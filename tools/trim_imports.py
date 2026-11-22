#!/usr/bin/env python3
"""Remove redundant imports: an import is dropped when another import of the same file already brings
it in, directly or not. Every file still sees exactly the same modules, so nothing about how the
proof compiles changes; only the import lists get shorter. Rewrites files in place.

usage: trim_imports.py SRC LIB_DUMP...    (LIB_DUMP: reach.py --dump-decls output, for package imports)
"""
import os, sys, re

src = sys.argv[1]
imports = {}
for path in sys.argv[2:]:
    for l in open(path, encoding='utf-8'):
        if l.startswith('I\t'):
            f = l.rstrip('\n').split('\t')
            imports.setdefault(f[1], f[2].split() if len(f) > 2 and f[2] else [])
impre = re.compile(r'^import\s+(.+)$')
texts = {}
for d, _, fs in os.walk(src):
    for fn in fs:
        if not fn.endswith('.lean'): continue
        p = os.path.join(d, fn); m = os.path.relpath(p, src)[:-5].replace('/', '.')
        t = open(p, encoding='utf-8').read(); texts[m] = (p, t)
        imps = []
        for line in t.split('\n'):
            s = line.strip()
            if s.startswith('import '): imps += s[7:].split()
            elif s == '': continue
            else: break
        imports[m] = imps
mods = list(imports); idx = {m: i for i, m in enumerate(mods)}
closure, state = {}, {}
for m in mods:
    if m in state: continue
    st = [(m, iter(imports.get(m, [])))]; state[m] = 1
    while st:
        node, it = st[-1]
        nxt = next((x for x in it if x in idx and x not in state), None)
        if nxt is None:
            st.pop(); b = 0
            for i in imports.get(node, []):
                if i in idx: b |= (1 << idx[i]) | closure.get(i, 0)
            closure[node] = b
        else:
            state[nxt] = 1; st.append((nxt, iter(imports.get(nxt, []))))
print(f'closures for {len(mods)} modules', file=sys.stderr)
before = after = changed = 0
for m, (p, t) in texts.items():
    imps = imports[m]; before += len(imps)
    keep = []
    for i in imps:
        if i not in idx: keep.append(i); continue
        bit = 1 << idx[i]
        if any(j != i and j in idx and (closure[j] & bit) for j in imps): continue
        if i in keep: continue
        keep.append(i)
    after += len(keep)
    if keep != imps:
        lines = t.split('\n'); k = 0
        while k < len(lines) and (lines[k].strip().startswith('import ') or lines[k].strip() == ''): k += 1
        new = '\n'.join('import ' + i for i in keep) + '\n\n' + '\n'.join(lines[k:])
        open(p, 'w', encoding='utf-8').write(new); changed += 1
print(f'imports {before} -> {after} ({before - after} removed) in {changed} files', file=sys.stderr)
