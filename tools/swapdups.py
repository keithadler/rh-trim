#!/usr/bin/env python3
"""Plan proof swaps: a project theorem whose statement is identical to another theorem's (same exported
type, so equal up to bound-variable names) gets its proof replaced by a one-line use of that twin,
when the twin is visible from the theorem's file (same file and earlier, or in a module the file
imports, directly or not). Mathlib twins are preferred; among project twins, the one with the
smallest proof. Callers are untouched: the theorem keeps its name and statement.

usage: swapdups.py DUPS.tsv EXPORT_DECLS.tsv PROJECT_NAMES.txt SRC DECLS_DUMP... > swaps.json
  DUPS.tsv          from xan (group size, statement nodes, touches-project, names; library names "[lib] ")
  EXPORT_DECLS.tsv  from xidx (idx kind name type_expr type_nodes value_nodes ...)
  DECLS_DUMP        from reach.py --dump-decls (project dump first, then libraries)
Writes {module: [[start, end, new_text], ...]} with offsets into the original source, plus stats on stderr.
"""
import sys, json, collections

dups, edecls, pnames, src = sys.argv[1:5]
dumps = sys.argv[5:]
AUTO = ("._", "_proof_", ".eq_", "match_", "_simp", "_aux_", ".proof_", "_private")
proj = set(l.rstrip('\n') for l in open(pnames, encoding='utf-8'))
vn = {}
for l in open(edecls, encoding='utf-8'):
    f = l.rstrip('\n').split('\t'); vn[f[2]] = int(f[5])

loc = {}                 # name -> (module, start, end)
imports = {}             # module -> [imported modules]
for path in dumps:
    for l in open(path, encoding='utf-8'):
        f = l.rstrip('\n').split('\t')
        if f[0] == 'D':
            loc.setdefault(f[1], (f[2], int(f[3]), int(f[4])))
        elif f[0] == 'I':
            imports.setdefault(f[1], f[2].split() if len(f) > 2 and f[2] else [])

# transitive import closure as bitsets (Python ints), in dependency order
mods = list(imports); idx = {m: i for i, m in enumerate(mods)}
sys.setrecursionlimit(1000000)
closure = {}
def clo(m):
    if m in closure: return closure[m]
    b = 0
    for i in imports.get(m, []):
        if i in idx: b |= (1 << idx[i]) | clo(i)
    closure[m] = b
    return b
order = []
state = {}
for m in mods:                         # iterative post-order so deep chains don't recurse
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

def visible(target, frm):
    tm, ts, _ = loc[target]; fm, fs, _ = loc[frm]
    if tm == fm: return ts < fs
    return tm in idx and fm in closure and (closure[fm] >> idx[tm]) & 1

def body_span(text, start, end):
    """offset of the first top-level ':=' in a declaration, or None"""
    depth = 0; i = start; n = end
    while i < n - 1:
        c = text[i]
        if c == '-' and text[i + 1] == '-':
            j = text.find('\n', i, n); i = n if j < 0 else j; continue
        if c == '/' and text[i + 1] == '-':
            j = text.find('-/', i + 2, n); i = n if j < 0 else j + 2; continue
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == '\\' else 1
            i = j + 1; continue
        if c in '([{⦃⟨': depth += 1
        elif c in ')]}⦄⟩': depth -= 1
        elif c == ':' and text[i + 1] == '=' and depth == 0: return i
        elif depth == 0 and text.startswith('where', i) and text[i - 1] in ' \n': return None
        i += 1
    return None

swaps = collections.defaultdict(list); texts = {}; pairs = []
stats = collections.Counter(); saved = 0
for l in open(dups, encoding='utf-8'):
    f = l.rstrip('\n').split('\t'); names = f[3:]
    libs = [n[6:] for n in names if n.startswith('[lib] ')]
    prj = [n for n in names if not n.startswith('[lib] ') and n in proj and not any(a in n for a in AUTO) and n in loc and n in vn]
    if not prj: continue
    libs = [n for n in libs if n in loc and not n.startswith('_private')]
    # candidate targets, best first: library twins, then project twins by proof size
    for p in prj:
        cands = libs + sorted((q for q in prj if q != p and vn[q] < vn[p]), key=lambda q: vn[q])
        t = next((c for c in cands if visible(c, p)), None)
        if t is None: stats['no visible twin'] += 1; continue
        m, s, e = loc[p]
        if m not in texts:
            texts[m] = open(f'{src}/{m.replace(".", "/")}.lean', encoding='utf-8').read()
        b = body_span(texts[m], s, e)
        if b is None: stats['no := body'] += 1; continue
        tail = texts[m][b:e]
        new = f':= by apply @_root_.{t} <;> assumption\n'
        if len(tail) <= len(new) + 4: stats['already short'] += 1; continue
        swaps[m].append([b, e, new]); saved += vn[p]; pairs.append((p, t))
        stats['swap to library' if t in libs else 'swap to project twin'] += 1
total = sum(v for n, v in vn.items() if n in proj)
print(dict(stats), file=sys.stderr)
print(f'proof nodes removed: {saved} of {total} ({100 * saved / total:.2f}%) in {sum(len(v) for v in swaps.values())} theorems, {len(swaps)} files', file=sys.stderr)
json.dump(swaps, sys.stdout)
import os
if os.environ.get('PAIRS'):
    open(os.environ['PAIRS'], 'w').write(''.join(f'{a}\t{b}\n' for a, b in pairs))
