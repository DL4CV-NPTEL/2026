#!/usr/bin/env python3
"""Execute notebooks in place and store their outputs.

The site is built with ``execute_notebooks: "off"``, so the outputs committed in
each notebook are what readers see. Run this after editing a notebook:

    python3 tools/execute_notebooks.py "notebooks/Week 9/W09_L1_From_Transformers_to_Vision_Transformers.ipynb"

Each notebook runs top to bottom in a fresh ``python3`` kernel, with the
notebook's own folder as the working directory (so ``root='./data'`` downloads
land next to it, and ``data/`` is git-ignored). Cell timings are recorded in the
cell metadata, and local filesystem paths are scrubbed from the outputs with
``tools/sanitize_outputs.py``.

Options:
    --threads N    cap OMP / MKL / torch threads in the kernel (default: all cores)
    --timeout S    per-cell timeout in seconds (default 600)
    --budget S     warn when a notebook's total execution time exceeds S (default 300)

GPU simulation (``--simulate-gpu``): the notebooks are written for Colab, where
``device`` is a CUDA GPU, but they are executed here on a CPU. Code that mixes a
CPU tensor into a GPU model, or calls ``.numpy()`` on a GPU tensor, passes on CPU
and crashes on Colab. This mode rewrites the device line to Apple's ``mps``
device, runs a *copy* of the notebook (the original is untouched) with errors
allowed, and reports every cell that failed with a device-mismatch error.
Failures that only exist on mps (float64, an unsupported op) are listed
separately and can be ignored.

Exit status is non-zero if any notebook raised. The notebook is still written
in that case, with outputs up to and including the failing cell, so the
traceback can be inspected in place.
"""

import argparse
import datetime as dt
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sanitize_outputs import scrub  # noqa: E402


def cell_seconds(cell):
    e = cell.get('metadata', {}).get('execution', {})
    a, b = e.get('iopub.execute_input'), e.get('shell.execute_reply')
    if not (a and b):
        return None
    fa = dt.datetime.fromisoformat(a.replace('Z', '+00:00'))
    fb = dt.datetime.fromisoformat(b.replace('Z', '+00:00'))
    return (fb - fa).total_seconds()


def sanitize(nb):
    hits = 0
    for cell in nb.cells:
        for out in (cell.get('outputs') or []):
            for key in ('text', 'traceback'):
                if key not in out:
                    continue
                val = out[key]
                if isinstance(val, list):
                    new = [scrub(v) for v in val]
                    hits += sum(a != b for a, b in zip(val, new))
                    out[key] = new
                else:
                    new = scrub(val)
                    hits += new != val
                    out[key] = new
    return hits


def run(path, timeout, budget):
    import nbformat
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError

    nb = nbformat.read(path, as_version=4)
    # Stale widget state from a previous run would otherwise be carried over.
    nb.metadata.pop('widgets', None)
    for cell in nb.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
            cell.metadata.pop('execution', None)

    client = NotebookClient(
        nb, timeout=timeout, kernel_name='python3', record_timing=True,
        allow_errors=False,
        resources={'metadata': {'path': os.path.dirname(os.path.abspath(path))}},
    )
    t0 = time.time()
    error = None
    try:
        client.execute()
    except CellExecutionError as exc:
        error = exc
    wall = time.time() - t0

    scrubbed = sanitize(nb)
    nbformat.write(nb, path)

    times = [(i, cell_seconds(c)) for i, c in enumerate(nb.cells) if c.cell_type == 'code']
    times = [(i, t) for i, t in times if t is not None]
    total = sum(t for _, t in times)
    slow = sorted(times, key=lambda x: -x[1])[:5]
    print(f'{path}')
    print(f'  wall {wall:6.1f}s | cells {total:6.1f}s | slowest: '
          + ', '.join(f'cell {i} {t:.1f}s' for i, t in slow))
    if scrubbed:
        print(f'  scrubbed {scrubbed} local path(s) from outputs')
    if total > budget:
        print(f'  WARNING: total execution {total:.0f}s exceeds the budget of {budget:.0f}s')
    if error is not None:
        # Find the failing cell index for a precise pointer.
        idx = next((i for i, c in enumerate(nb.cells)
                    if c.cell_type == 'code' and any(o.get('output_type') == 'error'
                                                    for o in c.get('outputs', []))), None)
        print(f'  ERROR in cell {idx}:')
        msg = str(error)
        print('    ' + '\n    '.join(msg.splitlines()[-25:]))
        return False
    print('  OK')
    return True


DEVICE_LINE = re.compile(r"torch\.device\(\s*['\"]cuda['\"]\s+if\s+torch\.cuda\.is_available\(\)\s+else\s+['\"]cpu['\"]\s*\)")
MISMATCH = re.compile(r"same device|two devices|found at least two|Expected all tensors|"
                      r"can't convert mps|Cannot convert a MPS|to numpy|use Tensor\.cpu|"
                      r"is on mps|on device mps|Placeholder storage|not on the same device|"
                      r"must be on the same device|device mismatch|expected device|got cpu|got mps", re.I)
MPS_ONLY = re.compile(r"float64|Double|MPS does not support|not currently implemented for the MPS|"
                      r"NotImplementedError|not supported on MPS|mps.*not.*support", re.I)


def simulate_gpu(path, timeout):
    """Run a copy of the notebook on the mps device with errors allowed."""
    import tempfile
    import nbformat
    from nbclient import NotebookClient

    nb = nbformat.read(path, as_version=4)
    nb.metadata.pop('widgets', None)
    n_dev = 0
    for cell in nb.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
            new, k = DEVICE_LINE.subn("torch.device('mps')", cell.source)
            n_dev += k
            cell.source = new
    print(f'{path}')
    if not n_dev:
        print("  SIMULATE-GPU: no device line found to rewrite; nothing to check")
        return True
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
    client = NotebookClient(
        nb, timeout=timeout, kernel_name='python3', allow_errors=True,
        resources={'metadata': {'path': os.path.dirname(os.path.abspath(path))}},
    )
    t0 = time.time()
    client.execute()
    out = os.path.join(tempfile.gettempdir(), os.path.basename(path).replace('.ipynb', '.gpu-sim.ipynb'))
    nbformat.write(nb, out)
    mismatches, mps_only, other = [], [], []
    for i, cell in enumerate(nb.cells):
        for o in cell.get('outputs', []):
            if o.get('output_type') != 'error':
                continue
            msg = f"{o.get('ename')}: {o.get('evalue')}"
            first = msg.splitlines()[0][:160]
            if MISMATCH.search(msg):
                mismatches.append((i, first))
            elif MPS_ONLY.search(msg):
                mps_only.append((i, first))
            else:
                other.append((i, first))
    print(f'  SIMULATE-GPU on mps: {time.time() - t0:.0f}s, copy written to {out}')
    for i, m in mismatches:
        print(f'  DEVICE MISMATCH in cell {i}: {m}')
    for i, m in mps_only:
        print(f'  mps-only (ignore) in cell {i}: {m}')
    for i, m in other:
        print(f'  other error in cell {i} (check it): {m}')
    if not (mismatches or mps_only or other):
        print('  OK: no errors on the simulated GPU device')
    return not mismatches and not other


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--threads', type=int, default=None)
    ap.add_argument('--timeout', type=int, default=600)
    ap.add_argument('--budget', type=float, default=300)
    ap.add_argument('--simulate-gpu', action='store_true',
                    help='run a copy on the mps device to catch Colab GPU device bugs')
    args = ap.parse_args()

    if args.threads:
        for var in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
                    'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
            os.environ[var] = str(args.threads)

    ok = True
    for p in args.paths:
        if args.simulate_gpu:
            ok = simulate_gpu(p, args.timeout) and ok
        else:
            ok = run(p, args.timeout, args.budget) and ok
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
