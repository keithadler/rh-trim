#!/usr/bin/env python3
"""Plant single faults in a small lean4export file, for differential kernel testing.

usage: mutate.py SLICE.ndjson OUTDIR N [SEED] [TARGET_NAME]

Each mutant is the slice with exactly one line changed. Faults go into the target theorem's proof
term, in expression nodes that nothing else uses (so the statement and every other declaration are
untouched): a correct kernel must reject the file unless the change happens to leave a valid proof.
A few mutants instead swap the theorem's statement for another theorem's. Writes OUTDIR/mNNNN.ndjson
and OUTDIR/mutants.tsv (id, operator, line number, before, after).
"""
import json, random, sys, os

src, out, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
target = sys.argv[5] if len(sys.argv) > 5 else None
rng = random.Random(seed)
os.makedirs(out, exist_ok=True)
lines = open(src, encoding='utf-8').read().split('\n')
if lines and lines[-1] == '':
    lines.pop()

names, exprs, expr_line, decls = {0: ''}, {}, {}, []
levels = []
for i, l in enumerate(lines):
    o = json.loads(l)
    if 'in' in o:
        if 'str' in o:
            names[o['in']] = (names[o['str']['pre']] + '.' if names.get(o['str']['pre']) else '') + o['str']['str']
        else:
            names[o['in']] = names[o['num']['pre']] + '.' + str(o['num']['i'])
    elif 'il' in o:
        levels.append(o['il'])
    elif 'ie' in o:
        exprs[o['ie']] = o
        expr_line[o['ie']] = i
    elif any(k in o for k in ('thm', 'def', 'opaque', 'axiom', 'quot', 'inductive')):
        decls.append((i, o))

def children(o):
    k = next(k for k in o if k != 'ie')
    v = o[k]
    if k == 'app': return [v['fn'], v['arg']]
    if k in ('forallE', 'lam'): return [v['type'], v['body']]
    if k == 'letE': return [v['type'], v['value'], v['body']]
    if k == 'mdata': return [v['expr']]
    if k == 'proj': return [v['struct']]
    return []

def reach(roots):
    seen, st = set(), list(roots)
    while st:
        e = st.pop()
        if e in seen or e not in exprs: continue
        seen.add(e); st.extend(children(exprs[e]))
    return seen

thms = [(i, o) for i, o in decls if 'thm' in o]
if target:
    ti, to = next((i, o) for i, o in thms if names[o['thm']['name']] == target)
else:
    ti, to = thms[-1]
tname = names[to['thm']['name']]
val_nodes = reach([to['thm']['value']])
other_roots = [to['thm']['type']]
for i, o in decls:
    if i == ti: continue
    for k, v in o.items():
        for key in ('type', 'value'):
            if isinstance(v, dict) and key in v: other_roots.append(v[key])
        if k == 'inductive':
            for grp in ('types', 'ctors', 'recs'):
                for ent in v.get(grp, []):
                    other_roots.append(ent['type'])
                    for r in ent.get('rules', []): other_roots.append(r['rhs'])
shared = reach(other_roots)
excl = sorted(e for e in val_nodes if e not in shared)
const_names = sorted({o['const']['name'] for o in exprs.values() if 'const' in o})
thm_types = [o['thm']['type'] for i, o in thms if i != ti]
print(f'target {tname}: proof term {len(val_nodes)} nodes, {len(excl)} used only by the proof', file=sys.stderr)

def mutate_once():
    e = rng.choice(excl)
    o = json.loads(json.dumps(exprs[e]))
    k = next(k for k in o if k != 'ie')
    v = o[k]
    earlier = [x for x in range(max(0, e - 5000), e) if x in exprs]
    ops = []
    if k == 'const' and len(const_names) > 1: ops.append('const-swap')
    if k == 'bvar': ops.append('bvar-shift')
    if k == 'app': ops += ['app-swap', 'app-arg-replace']
    if k in ('forallE', 'lam'): ops += ['binder-type-replace', 'binder-body-replace']
    if k == 'letE': ops.append('let-value-replace')
    if k == 'natVal': ops.append('nat-bump')
    if k == 'sort' and len(levels) > 1: ops.append('sort-change')
    if k == 'proj': ops.append('proj-index')
    if not ops: return None
    op = rng.choice(ops)
    if op == 'const-swap':
        v['name'] = rng.choice([c for c in const_names if c != v['name']])
    elif op == 'bvar-shift':
        o['bvar'] = max(0, o['bvar'] + rng.choice([-1, 1])) if o['bvar'] > 0 else o['bvar'] + 1
    elif op == 'app-swap':
        v['fn'], v['arg'] = v['arg'], v['fn']
    elif op == 'app-arg-replace' and earlier:
        v['arg'] = rng.choice(earlier)
    elif op == 'binder-type-replace' and earlier:
        v['type'] = rng.choice(earlier)
    elif op == 'binder-body-replace' and earlier:
        v['body'] = rng.choice(earlier)
    elif op == 'let-value-replace' and earlier:
        v['value'] = rng.choice(earlier)
    elif op == 'nat-bump':
        o['natVal'] = str(int(o['natVal']) + 1)
    elif op == 'sort-change':
        o['sort'] = rng.choice([l for l in levels if l != o['sort']])
    elif op == 'proj-index':
        v['idx'] = v['idx'] + 1
    else:
        return None
    new = json.dumps(o, separators=(',', ':'), ensure_ascii=False, sort_keys=True)
    if new == lines[expr_line[e]]:
        return None
    return op, expr_line[e], new

with open(os.path.join(out, 'mutants.tsv'), 'w') as tsv:
    made = 0; tries = 0
    while made < n and tries < n * 50:
        tries += 1
        if made % 10 == 9 and thm_types:      # every tenth: swap the statement
            o = json.loads(lines[ti]); o['thm']['type'] = rng.choice(thm_types)
            m = ('statement-swap', ti, json.dumps(o, separators=(',', ':'), ensure_ascii=False, sort_keys=True))
        else:
            m = mutate_once()
        if not m: continue
        op, li, new = m
        mid = f'm{made:04d}'
        mutated = list(lines); before = mutated[li]; mutated[li] = new
        with open(os.path.join(out, mid + '.ndjson'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(mutated) + '\n')
        tsv.write(f'{mid}\t{op}\t{li + 1}\t{before}\t{new}\n')
        made += 1
print(f'{made} mutants of {tname} in {out}', file=sys.stderr)
