#!/usr/bin/env python3
"""Strip local filesystem paths out of notebook outputs before committing.

Executing a notebook captures stderr, and library warnings quote the full path of
the file that raised them:

    /Users/<your-name>/Library/Python/3.9/lib/python/site-packages/skimage/...

That puts your username and local Python layout into a public repository and onto
the published site. This rewrites such paths to ".../site-packages/...", keeping
the warning readable while removing anything identifying.

Run it after re-executing notebooks:

    python3 tools/sanitize_outputs.py
"""

import glob
import json
import re
import sys

PATTERNS = [
    (re.compile(r'/Users/[^/\s"\',:]+/(?:Library/Python/[0-9.]+/lib/python/)?site-packages/'),
     '.../site-packages/'),
    (re.compile(r'/home/[^/\s"\',:]+/(?:\.local/lib/python[0-9.]+/)?site-packages/'),
     '.../site-packages/'),
    (re.compile(r'/Users/[^/\s"\',:]+/'), '.../'),
    (re.compile(r'/home/[^/\s"\',:]+/'), '.../'),
]


def scrub(text):
    for pat, rep in PATTERNS:
        text = pat.sub(rep, text)
    return text


def main():
    files, lines = 0, 0
    for path in sorted(glob.glob('notebooks/Week */*.ipynb')):
        nb = json.load(open(path))
        hits = 0
        for cell in nb['cells']:
            for out in (cell.get('outputs') or []):
                for key in ('text', 'traceback'):
                    if key not in out:
                        continue
                    val = out[key]
                    seq = val if isinstance(val, list) else [val]
                    new = []
                    for item in seq:
                        cleaned = scrub(item)
                        hits += cleaned != item
                        new.append(cleaned)
                    out[key] = new if isinstance(val, list) else new[0]
        if hits:
            with open(path, 'w', encoding='utf-8') as fh:
                json.dump(nb, fh, indent=1, ensure_ascii=False)
                fh.write('\n')
            files += 1
            lines += hits
            print(f'  cleaned {hits:3d} line(s) in {path}')

    print(f'{files} notebook(s) cleaned, {lines} line(s) rewritten'
          if files else 'nothing to clean')
    return 0


if __name__ == '__main__':
    sys.exit(main())
