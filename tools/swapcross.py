#!/usr/bin/env python3
"""Plan proof swaps for theorems with identical statements, including twins in other files.

For each group of project theorems whose exported statements are identical, one copy is chosen
(the smallest proof among copies that stay in the build). Every other copy gets its proof replaced by
`by apply @_root_.<chosen> <;> assumption`. When the chosen copy is not already visible from the
other copy's file, that file gets one extra import of the chosen copy's file, but only when:
  * the chosen file comes earlier in a fixed topological order of the original import graph, so no
    added import can ever close a cycle, however many are added;
  * the import brings in no module that declares a name some other module also declares (the only
    way an extra import can cause a duplicate-declaration clash).
Library twins (Mathlib, Batteries, ...) are used when already visible.

usage: swapcross.py DUPS.tsv EXPORT_DECLS.tsv PROJECT_NAMES.txt KEEP_NAMES.txt SRC DUMP...
writes swaps.json, imports.json, pairs.tsv in the current directory; stats on stderr.
"""
import sys, json, collections

dups, edecls, pnames, keepn, src = sys.argv[1:6]
dumps = sys.argv[6:]
AUTO = ("._", "_proof_", ".eq_", "match_", "_simp", "_aux_", ".proof_", "_private")
proj = set(l.rstrip('\n') for l in open(pnames, encoding='utf-8'))
keep = set(l.rstrip('\n') for l in open(keepn, encoding='utf-8'))
vn = {}
for l in open(edecls, encoding='utf-8'):
    f = l.rstrip('\n').split('\t'); vn[f[2]] = int(f[5])

loc, imports, declared_in = {}, {}, collections.defaultdict(set)
project_mods = set()
for k, path in enumerate(dumps):
    for l in open(path, encoding='utf-8'):
        f = l.rstrip('\n').split('\t')
        if f[0] == 'D':
            loc.setdefault(f[1], (f[2], int(f[3]), int(f[4])))
            declared_in[f[1]].add(f[2])
        elif f[0] == 'I':
            imports.setdefault(f[1], f[2].split() if len(f) > 2 and f[2] else [])
            if k == 0: project_mods.add(f[1])
mods = list(imports); idx = {m: i for i, m in enumerate(mods)}

# topological order (dependencies first) and closure bitsets
topo, state = {}, {}
closure = {}
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
            closure[node] = b; topo[node] = len(topo)
        else:
            state[nxt] = 1; st.append((nxt, iter(imports.get(nxt, []))))
# modules that declare a name some other module also declares
clash = 0
for n, ms in declared_in.items():
    if len(ms) > 1:
        for m in ms:
            if m in idx: clash |= 1 << idx[m]
print(f'{len(mods)} modules; {bin(clash).count("1")} declare a name declared elsewhere', file=sys.stderr)

def visible(t, p):
    tm, ts, _ = loc[t]; pm, ps, _ = loc[p]
    if tm == pm: return ts < ps
    return tm in idx and pm in closure and (closure[pm] >> idx[tm]) & 1

def importable(t, p):
    tm, pm = loc[t][0], loc[p][0]
    if tm == pm or tm not in project_mods or pm not in project_mods: return False
    if topo[tm] >= topo[pm]: return False
    return True     # Main imports every module, so the original already shows no two of them clash

def body_span(text, start, end):
    depth = 0; i = start; n = end
    while i < n - 1:
        c = text[i]
        if c == '-' and text[i + 1] == '-':
            j = text.find('\n', i, n); i = n if j < 0 else j; continue
        if c == '/' and text[i + 1] == '-':
            j = text.find('-/', i + 2, n); i = n if j < 0 else j + 2; continue
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"': j += 2 if text[j] == '\\' else 1
            i = j + 1; continue
        if c in '([{⦃⟨': depth += 1
        elif c in ')]}⦄⟩': depth -= 1
        elif c == ':' and text[i + 1] == '=' and depth == 0: return i
        elif depth == 0 and text.startswith('where', i) and text[i - 1] in ' \n': return None
        i += 1
    return None

swaps = collections.defaultdict(list); extra = collections.defaultdict(set); texts = {}; pairs = []
stats = collections.Counter(); saved = 0
for l in open(dups, encoding='utf-8'):
    f = l.rstrip('\n').split('\t'); names = f[3:]
    libs = [n[6:] for n in names if n.startswith('[lib] ') and n[6:] in loc and not n[6:].startswith('_private')]
    prj = [n for n in names if not n.startswith('[lib] ') and n in proj and not any(a in n for a in AUTO) and n in loc and n in vn]
    if len(prj) + len(libs) < 2 or not prj: continue
    kept = sorted((q for q in prj if q in keep), key=lambda q: (topo.get(loc[q][0], 1 << 30), loc[q][1]))
    canon = kept[0] if kept else None                   # the copy earliest in build order
    for p in prj:
        if p not in keep: continue                      # a copy the build drops anyway
        t = next((c for c in libs if visible(c, p)), None)
        how = 'library'
        if t is None and canon and canon != p:
            if visible(canon, p): t, how = canon, 'visible'
            elif importable(canon, p): t, how = canon, 'import'
        if t is None: stats['no usable twin'] += 1; continue
        m, s, e = loc[p]
        if m not in texts: texts[m] = open(f'{src}/{m.replace(".", "/")}.lean', encoding='utf-8').read()
        b = body_span(texts[m], s, e)
        if b is None: stats['no := body'] += 1; continue
        new = f':= by apply @_root_.{t} <;> assumption\n'
        if len(texts[m][b:e]) <= len(new) + 4: stats['already short'] += 1; continue
        swaps[m].append([b, e, new]); pairs.append((p, t)); saved += vn[p]
        if how == 'import': extra[m].add(loc[t][0])
        stats['swap: ' + how] += 1
total = sum(v for n, v in vn.items() if n in proj)
print(dict(stats), file=sys.stderr)
print(f'proof nodes replaced: {saved} of {total} ({100 * saved / total:.2f}%), {len(pairs)} theorems in {len(swaps)} files; '
      f'{sum(len(v) for v in extra.values())} imports added to {len(extra)} files', file=sys.stderr)
json.dump(swaps, open('swaps.json', 'w'))
json.dump({m: sorted(v) for m, v in extra.items()}, open('imports.json', 'w'))
open('pairs.tsv', 'w').write(''.join(f'{a}\t{b}\n' for a, b in pairs))
