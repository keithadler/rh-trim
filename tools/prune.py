"""Write a pruned copy of the project: only the files in KEEP, with imports rewritten.

A kept file's import of a dropped file is replaced by the kept files that the dropped file
reached through its own imports, recursively. So every kept file can still see exactly the
kept files it could see before (new closure ∩ kept = old closure ∩ kept). Mathlib and other
package imports are left alone. Runs nothing from the project; reads and writes text only.

usage: prune.py SRC KEEP_LIST DEST
"""
import os, re, sys, functools

src, keep_list, dest = sys.argv[1:4]
keep = set(l.strip() for l in open(keep_list) if l.strip())
keep |= {'Main', 'Statements', 'Challenge'}

def path(m): return os.path.join(src, m.replace('.', '/') + '.lean')
def local(m): return os.path.exists(path(m))

impre = re.compile(r'^import\s+(.+)$', re.M)
_imports = {}
def imports(m):
    if m not in _imports:
        t = open(path(m), encoding='utf-8').read()
        _imports[m] = [w for line in impre.findall(t) for w in line.split()]
    return _imports[m]

sys.setrecursionlimit(1000000)
@functools.lru_cache(maxsize=None)
def frontier(m):
    """Kept files and package modules reachable from dropped module m, stopping at kept ones."""
    out = set()
    for i in imports(m):
        if not local(i) or i in keep:
            out.add(i)
        else:
            out |= frontier(i)
    return frozenset(out)

import json
cuts = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else {}
swaps = json.load(open(sys.argv[5])) if len(sys.argv) > 5 else {}
extra_imports = json.load(open(sys.argv[6])) if len(sys.argv) > 6 else {}
stats = dict(files=0, rewritten=0, max_imports=0, cut_decls=0, swapped=0)
for m in sorted(keep):
    if not local(m):
        print('missing source:', m, file=sys.stderr); continue
    t = open(path(m), encoding='utf-8').read()
    # cut the declarations the trace never reached (offsets are into the original text)
    spans = [(a, b, '') for a, b in cuts.get(m, [])] + [tuple(x) for x in swaps.get(m, [])]
    if spans:
        spans.sort(key=lambda x: (x[0], -x[1]))
        parts, last = [], 0
        for a, b, rep in spans:
            if a < last: continue          # inside a span already cut
            parts.append(t[last:a]); parts.append(rep); last = b
            stats['swapped' if rep else 'cut_decls'] += 1
        parts.append(t[last:])
        t = ''.join(parts)
    new = []
    for i in imports(m):
        if not local(i) or i in keep:
            new.append(i)
        else:
            new.extend(sorted(frontier(i)))
    new = new + [x for x in extra_imports.get(m, []) if x in keep or not local(x)]
    seen, ded = set(), []
    for i in new:
        if i not in seen and i != m:
            seen.add(i); ded.append(i)
    if ded != imports(m):
        stats['rewritten'] += 1
    stats['max_imports'] = max(stats['max_imports'], len(ded))
    # replace the header's import lines with the new list
    lines = t.split('\n')
    body_start = 0
    for k, line in enumerate(lines):
        s = line.strip()
        if s.startswith('import ') or s == '':
            body_start = k + 1
        else:
            break
    if ded == imports(m):
        out = t        # imports unchanged: keep the file's own header byte for byte
    else:
        out = '\n'.join('import ' + i for i in ded) + '\n\n' + '\n'.join(lines[body_start:])
    p = os.path.join(dest, 'src', m.replace('.', '/') + '.lean')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(out)
    stats['files'] += 1
print(stats)
