#!/usr/bin/env python3
"""Lint a lecture notebook against the conventions used across the book.

    python3 tools/check_notebook.py "notebooks/Week 9/W09_L1_From_Transformers_to_Vision_Transformers.ipynb"

Checks the header cells (Colab badge, video, slides), the intro cell, the
required sections, that every code cell was executed without error, that no
local paths leaked into outputs, that the setup cell selects the device the
Colab-safe way, that the notebook is interactive enough (widgets) and that the
recorded execution time fits the budget. Prints FAIL / WARN lines and exits 1
on any FAIL.

Options:
    --min-words N     minimum markdown words (default 2000)
    --min-code N      minimum code lines (default 400)
    --min-widgets N   minimum number of interact() widgets (default 4)
    --budget S        maximum total execution time in seconds (default 300)
    --json            print a machine-readable summary at the end
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.parse


def cell_seconds(cell):
    e = cell.get('metadata', {}).get('execution', {})
    a, b = e.get('iopub.execute_input'), e.get('shell.execute_reply')
    if not (a and b):
        return None
    fa = dt.datetime.fromisoformat(a.replace('Z', '+00:00'))
    fb = dt.datetime.fromisoformat(b.replace('Z', '+00:00'))
    return (fb - fa).total_seconds()


def check(path, args):
    fails, warns, info = [], [], {}
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    rel = os.path.relpath(os.path.abspath(path), root)
    nb = json.load(open(path, encoding='utf-8'))
    cells = nb['cells']
    src = lambda c: ''.join(c['source'])

    m = re.search(r'Week (\d+)/', rel)
    week = int(m.group(1)) if m else None

    # ---- header cell 0 -------------------------------------------------
    c0 = src(cells[0]) if cells else ''
    if cells[0]['cell_type'] != 'markdown' or 'colab-badge.svg' not in c0:
        fails.append('cell 0 must be the markdown Colab-badge header')
    cm = re.search(r'colab\.research\.google\.com/github/DL4CV-NPTEL/2026/blob/main/([^"]+)"', c0)
    if not cm or urllib.parse.unquote(cm.group(1)) != rel:
        fails.append(f'cell 0 Colab link does not point at {rel}')
    vm = re.search(r'youtube\.com/watch\?v=([\w-]+)', c0)
    sm = re.search(r'\((https://github\.com/DL4CV-NPTEL/2026/blob/main/Slides/[^)]+)\)', c0)
    if not vm:
        fails.append('cell 0 has no lecture video link')
    if not sm:
        fails.append('cell 0 has no slides link')
    else:
        local = os.path.join(root, urllib.parse.unquote(sm.group(1).split('/blob/main/')[1]))
        if not os.path.exists(local):
            fails.append(f'cell 0 slides link points at a missing file: {local}')

    # ---- header cell 1 -------------------------------------------------
    c1 = cells[1] if len(cells) > 1 else {}
    c1s = src(c1)
    if c1.get('cell_type') != 'code' or 'remove-input' not in c1.get('metadata', {}).get('tags', []):
        fails.append('cell 1 must be the code video-embed cell tagged remove-input')
    idm = re.search(r'VIDEO_ID = "([\w-]+)"', c1s)
    if not idm or (vm and idm.group(1) != vm.group(1)):
        fails.append('cell 1 VIDEO_ID does not match the video link in cell 0')
    embed = ''.join(''.join(o.get('data', {}).get('text/html', '')) for o in c1.get('outputs', []))
    if 'youtube.com/embed/' not in embed:
        fails.append('cell 1 has no saved iframe output (execute the notebook)')

    # ---- intro cell 2 --------------------------------------------------
    c2 = src(cells[2]) if len(cells) > 2 else ''
    if not re.match(r'# Week \d+, Lecture \d+: \S', c2):
        fails.append('cell 2 must start with "# Week N, Lecture M: Title"')
    if 'Prof. Vineeth N Balasubramanian, IIT Hyderabad' not in c2:
        fails.append('cell 2 is missing the course/instructor line')
    if 'Companion notebook for **§' not in c2:
        fails.append('cell 2 is missing "Companion notebook for **§W.L Title**."')
    for needle in ('**What you will learn**', '**Contents**'):
        if needle not in c2:
            fails.append(f'cell 2 is missing {needle}')
    if '**How to run**' not in c2:
        warns.append('cell 2 has no **How to run** paragraph')

    # ---- sections ------------------------------------------------------
    md = [src(c) for c in cells if c['cell_type'] == 'markdown']
    heads = [l.strip() for m_ in md for l in m_.splitlines() if re.match(r'#{1,3} ', l)]
    h2 = [h for h in heads if h.startswith('## ')]
    def has(prefix):
        return any(h.lower().startswith(prefix.lower()) for h in h2)
    for req in ('## Review', '## Setup', '## Key takeaways', '## Exercises'):
        if not has(req):
            fails.append(f'missing section {req}')
    numbered = [h for h in h2 if re.match(r'## \d+\.', h)]
    info['numbered_sections'] = len(numbered)
    if len(numbered) < 5:
        fails.append(f'only {len(numbered)} numbered "## N." sections (need at least 5)')
    if has('## Setup') and has('## Review'):
        order = [h for h in h2 if h.lower().startswith(('## review', '## setup'))]
        if order and order[0].lower().startswith('## setup'):
            warns.append('Setup comes before Review (the rest of the book puts Review first)')
    # exercises count
    ex_idx = next((i for i, m_ in enumerate(md) if '## Exercises' in m_), None)
    if ex_idx is not None:
        ex = md[ex_idx].split('## Exercises', 1)[1]
        n_ex = len(re.findall(r'^\s*\d+\.\s', ex, re.M))
        info['exercises'] = n_ex
        if n_ex < 4:
            fails.append(f'only {n_ex} numbered exercises (need at least 4)')

    # ---- code cells ----------------------------------------------------
    code_cells = [c for c in cells[2:] if c['cell_type'] == 'code']
    code = '\n'.join(src(c) for c in code_cells)
    info['code_lines'] = sum(len(src(c).splitlines()) for c in code_cells)
    info['md_words'] = sum(len(m_.split()) for m_ in md)
    info['widgets'] = len(re.findall(r'\binteract\s*\(', code))
    info['asserts'] = len(re.findall(r'^\s*assert\b', code, re.M))
    info['figures'] = sum(1 for c in code_cells for o in c.get('outputs', []) if 'image/png' in o.get('data', {}))
    if info['md_words'] < args.min_words:
        fails.append(f"only {info['md_words']} markdown words (need at least {args.min_words})")
    if info['code_lines'] < args.min_code:
        fails.append(f"only {info['code_lines']} code lines (need at least {args.min_code})")
    if info['widgets'] < args.min_widgets:
        fails.append(f"only {info['widgets']} interact() widgets (need at least {args.min_widgets})")
    if info['asserts'] == 0:
        warns.append('no assert statements: the book verifies from-scratch code against a reference')
    if info['figures'] < 4:
        warns.append(f"only {info['figures']} figures in outputs")

    unexecuted = [i for i, c in enumerate(cells) if i > 1 and c['cell_type'] == 'code' and c.get('execution_count') is None]
    if unexecuted:
        fails.append(f'code cells not executed: {unexecuted}')
    errors = [i for i, c in enumerate(cells) if any(o.get('output_type') == 'error' for o in c.get('outputs', []))]
    if errors:
        fails.append(f'error outputs in cells {errors}')

    blob = json.dumps(nb)
    if re.search(r'/Users/[^/\s"]+/|/home/[^/\s"]+/', blob):
        fails.append('a local filesystem path leaked into the notebook (run tools/sanitize_outputs.py)')

    # setup conventions
    setup = ''
    for i, c in enumerate(cells):
        if c['cell_type'] == 'markdown' and src(c).strip().lower().startswith('## setup'):
            for c2_ in cells[i + 1:i + 3]:
                if c2_['cell_type'] == 'code':
                    setup = src(c2_); break
            break
    if 'torch' in code:
        if "torch.device('cuda' if torch.cuda.is_available() else 'cpu')" not in code and \
           'torch.device("cuda" if torch.cuda.is_available() else "cpu")' not in code:
            fails.append("setup must select the device with torch.device('cuda' if torch.cuda.is_available() else 'cpu')")
        if 'torch.manual_seed' not in code:
            fails.append('no torch.manual_seed call')
        if '.cuda()' in code:
            warns.append('uses .cuda() directly; prefer .to(device) so the CPU path works')
        if re.search(r"torch\.device\(['\"]mps", code):
            fails.append('do not select the mps device; the book uses cuda-or-cpu only')
    if '%matplotlib inline' not in code:
        fails.append('setup must contain %matplotlib inline (widgets need it)')
    if 'np.random.seed' not in code and 'default_rng' not in code and 'numpy' in code:
        warns.append('numpy is used but never seeded')

    # pip / shell / heavy downloads
    for i, c in enumerate(code_cells):
        s = src(c)
        if re.search(r'^\s*!', s, re.M):
            fails.append(f'shell escape (!) in a code cell: {s.splitlines()[0][:60]}')
        if 'pip install' in s and 'ImportError' not in s:
            fails.append('pip install outside a try/except ImportError guard')
        if 'tqdm' in s:
            warns.append('tqdm progress bars produce noisy static output; print every N steps instead')
    for m_ in re.finditer(r'datasets\.(\w+)\(([^)]*)\)', code):
        if "root='./data'" not in m_.group(2) and 'root="./data"' not in m_.group(2):
            fails.append(f"torchvision dataset {m_.group(1)} must use root='./data', download=True")
    if re.search(r'from transformers|import transformers|open_clip|timm\b|datasets\.load_dataset|hf_hub_download', code):
        warns.append('uses an external model hub; make sure the download is small and the import is guarded')
    if re.search(r'weights\s*=\s*(?!None)[A-Za-z_]+\.', code) or 'pretrained=True' in code:
        warns.append('downloads pretrained torchvision weights; keep it under ~100 MB')
    if 'num_workers' in code and re.search(r'num_workers\s*=\s*[1-9]', code):
        warns.append('num_workers > 0 can hang on Colab; use 0')

    # static figure paired with every widget
    for i, c in enumerate(cells):
        if c['cell_type'] == 'code' and re.search(r'\binteract\s*\(', src(c)):
            prev = cells[max(0, i - 6):i]
            if not any('image/png' in o.get('data', {}) for p in prev for o in p.get('outputs', [])):
                warns.append(f'widget in cell {i} has no static figure in the 6 cells before it (site readers cannot drag sliders)')
            if i == 0 or cells[i - 1]['cell_type'] != 'markdown':
                warns.append(f'widget in cell {i} is not introduced by a markdown cell saying what to drag')

    # execution time
    times = [cell_seconds(c) for c in cells if c['cell_type'] == 'code']
    times = [t for t in times if t is not None]
    info['exec_total_s'] = round(sum(times), 1)
    info['exec_slowest_s'] = round(max(times), 1) if times else None
    if times and sum(times) > args.budget:
        fails.append(f'total execution {sum(times):.0f}s exceeds the {args.budget:.0f}s budget')
    if times and max(times) > 90:
        warns.append(f'slowest cell takes {max(times):.0f}s; keep every cell under about a minute')

    # oversized outputs
    for i, c in enumerate(cells):
        for o in c.get('outputs', []):
            if o.get('output_type') == 'stream' and len(''.join(o.get('text', ''))) > 6000:
                warns.append(f'cell {i} prints more than 6000 characters')
    size = os.path.getsize(path)
    info['size_kb'] = size // 1024
    if size > 6_000_000:
        warns.append(f'notebook is {size // 1024} KB; keep figures small (dpi 100, figsize under 12x4)')

    return fails, warns, info


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--min-words', type=int, default=2000)
    ap.add_argument('--min-code', type=int, default=400)
    ap.add_argument('--min-widgets', type=int, default=4)
    ap.add_argument('--budget', type=float, default=300)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    ok = True
    summary = {}
    for p in args.paths:
        fails, warns, info = check(p, args)
        summary[p] = {'fails': fails, 'warns': warns, **info}
        print(f'{p}')
        print('  ' + ', '.join(f'{k}={v}' for k, v in info.items()))
        for f in fails:
            print(f'  FAIL: {f}')
        for w in warns:
            print(f'  WARN: {w}')
        print('  ' + ('PASS' if not fails else 'FAILED'))
        ok = ok and not fails
    if args.json:
        print(json.dumps(summary, indent=1))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
