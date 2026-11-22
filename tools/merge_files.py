#!/usr/bin/env python3
"""Merge small files into bundle modules, folder by folder, without changing how anything elaborates.

* Only files in the same folder (so the same Lake library and its options) are merged, in import order,
  at most MAX_FILES files and MAX_LINES lines per bundle.
* Each file's body is wrapped in its own `section ... end`, so its `open`, `variable`, `universe`,
  `set_option` and local notation stay with it. Namespaces, sections and `mutual` blocks a file leaves
  open are closed first.
* Two files whose `private` names clash never share a bundle; files using `#exit` are never merged.
* A bundle that would sit on an import cycle (it imports something that imports it back) is split into
  its files again, until the module graph is acyclic.
* Every import of a merged file is rewritten to its bundle.

usage: merge_files.py SRC OUT_SRC [MAX_FILES] [MAX_LINES]
"""
import os, re, sys, collections

src, out = sys.argv[1], sys.argv[2]
MAX_FILES = int(sys.argv[3]) if len(sys.argv) > 3 else 25
MAX_LINES = int(sys.argv[4]) if len(sys.argv) > 4 else 4000
NOMERGE = set(l.strip() for l in open(sys.argv[5]) if l.strip()) if len(sys.argv) > 5 else set()
KEEP_ALONE = {'Main', 'Statements', 'Challenge'}

texts, imports, header_end = {}, {}, {}
for d, _, fs in os.walk(src):
    for fn in fs:
        if fn.endswith('.lean'):
            p = os.path.join(d, fn); m = os.path.relpath(p, src)[:-5].replace('/', '.')
            t = open(p, encoding='utf-8').read(); texts[m] = t
            lines = t.split('\n'); imps = []; k = 0
            while k < len(lines) and (lines[k].strip().startswith('import ') or lines[k].strip() == ''):
                if lines[k].strip(): imps += lines[k].strip()[7:].split()
                k += 1
            imports[m] = imps; header_end[m] = k
mods = set(texts)

# topological order of project modules
order, state = [], {}
for m in sorted(mods):
    if m in state: continue
    st = [(m, iter(imports[m]))]; state[m] = 1
    while st:
        node, it = st[-1]
        nxt = next((x for x in it if x in mods and x not in state), None)
        if nxt is None: st.pop(); order.append(node)
        else: state[nxt] = 1; st.append((nxt, iter(imports[nxt])))
pos = {m: i for i, m in enumerate(order)}

privre = re.compile(r'^(?:@\[[^\]]*\]\s*)?(?:noncomputable\s+)?private\s+(?:noncomputable\s+)?(?:theorem|lemma|def|abbrev|instance|structure|inductive|class|opaque)\s+([^\s:({\[]+)', re.M)
privs = {m: set(privre.findall(t)) for m, t in texts.items()}

def eligible(m):
    return m not in KEEP_ALONE and m not in NOMERGE and m.count('.') >= 2 and '#exit' not in texts[m]   # never at a library's top level

# depth in the import graph: files at the same depth can't reach each other through any path,
# so a bundle of same-folder, same-depth files can never close an import cycle
level = {}
for m in order:
    level[m] = 1 + max((level[i] for i in imports[m] if i in mods), default=-1)
# bundles: per folder and depth, cut by size and private-name clashes
folder = collections.defaultdict(list)
for m in order:
    if eligible(m): folder[(m.rsplit('.', 1)[0], level[m])].append(m)
bundles = []
for f, ms in folder.items():
    if len(ms) < 2: continue
    cur, lines, names = [], 0, set()
    for m in ms:
        n = texts[m].count('\n') + 1
        if cur and (len(cur) >= MAX_FILES or lines + n > MAX_LINES or (privs[m] & names)):
            if len(cur) > 1: bundles.append((f, cur))
            cur, lines, names = [], 0, set()
        cur.append(m); lines += n; names |= privs[m]
    if len(cur) > 1: bundles.append((f, cur))
bundles = [(f[0], ms) for f, ms in bundles]

def assign(bundles):
    owner = {}
    used = set(mods)
    named = []
    for f, ms in bundles:
        k = 0
        while f'{f}.Bundle{k}' in used: k += 1
        name = f'{f}.Bundle{k}'; used.add(name); named.append((name, ms))
        for m in ms: owner[m] = name
    return owner, named

# split bundles that sit on cycles until the condensed graph is acyclic
for rnd in range(50):
    owner, named = assign(bundles)
    node = lambda m: owner.get(m, m)
    g = collections.defaultdict(set)
    for m in mods:
        a = node(m)
        for i in imports[m]:
            if i in mods and node(i) != a: g[a].add(node(i))
    # Tarjan SCC, iterative
    index, low, onst, stack, sccs, counter = {}, {}, set(), [], [], [0]
    nodes = set(node(m) for m in mods)
    for v in nodes:
        if v in index: continue
        work = [(v, iter(g[v]))]; index[v] = low[v] = counter[0]; counter[0] += 1; stack.append(v); onst.add(v)
        while work:
            x, it = work[-1]; y = next(it, None)
            if y is None:
                work.pop()
                if work: low[work[-1][0]] = min(low[work[-1][0]], low[x])
                if low[x] == index[x]:
                    comp = []
                    while True:
                        z = stack.pop(); onst.discard(z); comp.append(z)
                        if z == x: break
                    if len(comp) > 1: sccs.append(comp)
            elif y not in index:
                index[y] = low[y] = counter[0]; counter[0] += 1; stack.append(y); onst.add(y); work.append((y, iter(g[y])))
            elif y in onst:
                low[x] = min(low[x], index[y])
    bad = {b for comp in sccs for b in comp if b.rsplit('.', 1)[-1].startswith('Bundle')}
    print(f'round {rnd}: {len(named)} bundles, {len(sccs)} cycles, splitting {len(bad)}', file=sys.stderr)
    if not bad: break
    bundles = [(f, ms) for (name, ms), (f, _) in zip(named, bundles) if name not in bad]

owner, named = assign(bundles)
OPEN = re.compile(r'^(namespace|section|noncomputable section|mutual|end)\b\s*(\S*)')
def closers(body):
    st = []
    for line in body.split('\n'):
        mm = OPEN.match(line)
        if not mm: continue
        kw, nm = mm.group(1), mm.group(2)
        if kw == 'end':
            if st: st.pop()
        elif kw == 'mutual': st.append('')
        else: st.append(nm)
    return ['end ' + n if n else 'end' for n in reversed(st)]

def new_imports(ms):
    seen, res = set(), []
    for m in ms:
        for i in imports[m]:
            j = owner.get(i, i)
            if j in seen or (i in ms): continue
            seen.add(j); res.append(j)
    return res

os.makedirs(out, exist_ok=True)
def write(mod, text):
    p = os.path.join(out, mod.replace('.', '/') + '.lean'); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(text)
merged = set(owner)
for name, ms in named:
    parts = ['import ' + i for i in new_imports(ms) if i != name] + ['']
    for m in ms:
        body = '\n'.join(texts[m].split('\n')[header_end[m]:]).rstrip('\n')
        parts += ['section', body] + closers(body) + ['end', '']
    write(name, '\n'.join(parts))
for m in mods:
    if m in merged: continue
    imps = []
    for i in imports[m]:
        j = owner.get(i, i)
        if j not in imps: imps.append(j)
    body = '\n'.join(texts[m].split('\n')[header_end[m]:])
    write(m, '\n'.join('import ' + i for i in imps) + '\n\n' + body)
open(out.rstrip('/') + '.bundles.tsv', 'w').write(''.join(f'{n}\t{m}\n' for n, ms in named for m in ms))
print(f'files {len(mods)} -> {len(mods) - len(merged) + len(named)} ({len(named)} bundles hold {len(merged)} files)', file=sys.stderr)
