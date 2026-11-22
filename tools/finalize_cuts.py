#!/usr/bin/env python3
"""Make a cut list safe and pick droppable files.
usage: finalize_cuts.py CUTS.json KEEP_NAMES.txt DECLS_DUMP FILES.txt ORIG_SRC OUT_CUTS.json OUT_FILES.txt
1. Restore any cut declaration whose name, with an outer namespace added or removed, is a kept name
   (the source parser can misread a namespace; Lean's export is the authority).
2. Drop a file when every declaration in it is cut and it has no notation, syntax, tactic,
   attribute, instance or export command."""
import json, collections, re, sys
cuts_p, keep_p, dump_p, files_p, src, out_c, out_f = sys.argv[1:8]
cuts = json.load(open(cuts_p))
keep = set()
for l in open(keep_p, encoding='utf-8'):
    n = l.rstrip('\n')
    if n.startswith('_private.') and '.0.' in n: n = n.split('.0.', 1)[1]
    keep.add(n)
suf = collections.defaultdict(set)
for n in keep:
    p = n.split('.')
    for k in range(1, len(p) - 1): suf['.'.join(p[k:])].add(n)
cutset = {(m, a, b) for m, v in cuts.items() for a, b in v}
back = collections.defaultdict(set); decls = collections.defaultdict(list); nb = 0
for l in open(dump_p, encoding='utf-8'):
    f = l.rstrip('\n').split('\t')
    if f[0] != 'D': continue
    m, a, b = f[2], int(f[3]), int(f[4]); decls[m].append((a, b))
    if (m, a, b) not in cutset: continue
    n = f[1]; p = n.split('.')
    if n in suf or any('.'.join(p[k:]) in keep for k in range(1, len(p) - 1 if len(p) > 2 else 1)):
        back[m].add((a, b)); nb += 1
new = {m: [s for s in v if tuple(s) not in back.get(m, set())] for m, v in cuts.items()}
json.dump(new, open(out_c, 'w'))
cutset = {(m, a, b) for m, v in new.items() for a, b in v}
META = re.compile(r'^\s*(?:@\[[^\]]*\]\s*)?(?:(?:scoped|local)\s+)?(syntax|macro|macro_rules|notation|infix|infixl|infixr|prefix|postfix|elab|elab_rules|declare_syntax_cat|attribute|instance|initialize|register_\w+|export)\b', re.M)
mods = [l.strip() for l in open(files_p)]
drop = set()
for m in mods:
    v = decls.get(m, [])
    if v and all((m, a, b) in cutset for a, b in v):
        if not META.search(open(f'{src}/{m.replace(".", "/")}.lean', encoding='utf-8').read()): drop.add(m)
drop -= {'Main', 'Statements', 'Challenge'}
open(out_f, 'w').write(''.join(m + '\n' for m in mods if m not in drop))
print(f'restored {nb} cuts (name spelled differently in the source); cuts {sum(len(v) for v in new.values())}; '
      f'files {len(mods)} -> {len(mods) - len(drop)}')
