"""After prune.py: drop `attribute [...]` commands that name cut declarations, then check that
every import resolves and that Main reaches every proof file. Reads and writes text only.

usage: check_fork.py FORK_SRC ORIGINAL_SRC
"""
import os, re, sys
fork, orig = sys.argv[1:3]
declre = re.compile(r'^(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable|partial|unsafe|nonrec)\s+)*'
                    r'(?:theorem|lemma|def|abbrev|structure|class|instance|inductive|opaque)\b\s*([^\s:({\[⦃]*)', re.M)
attre = re.compile(r'^attribute \[[^\]]*\]\s+(.+)$', re.M)
last = lambda n: n.split('.')[-1]
imp = {}; removed = 0; lines = 0
for d, _, fs in os.walk(fork):
    for f in fs:
        if not f.endswith('.lean'): continue
        p = os.path.join(d, f); rel = os.path.relpath(p, fork)
        t = open(p, encoding='utf-8').read()
        if 'attribute [' in t:
            o = open(os.path.join(orig, rel), encoding='utf-8').read()
            gone = {last(n) for n in declre.findall(o) if n} - {last(n) for n in declre.findall(t) if n}
            if gone:
                out = []
                for line in t.split('\n'):
                    m = attre.match(line)
                    if m and any(last(x) in gone for x in m.group(1).split()):
                        removed += 1; continue
                    out.append(line)
                if len(out) != t.count('\n') + 1:
                    t = '\n'.join(out); open(p, 'w', encoding='utf-8').write(t)
        lines += t.count('\n') + 1
        imp[rel[:-5].replace('/', '.')] = [w for l in re.findall(r'^import\s+(.+)$', t, re.M) for w in l.split()]
pk = ('Mathlib', 'Init', 'Std', 'Lean', 'Batteries', 'Aesop', 'Qq', 'Plausible', 'ProofWidgets', 'ImportGraph', 'LeanSearchClient')
miss = {i for L in imp.values() for i in L if i not in imp and not i.startswith(pk)}
seen, st = set(), ['Main']
while st:
    x = st.pop()
    if x in seen or x not in imp: continue
    seen.add(x); st += imp[x]
print(f'files {len(imp)}, lines {lines}, attribute commands removed {removed}, '
      f'unresolved imports {len(miss)}, unreached from Main {sorted(set(imp) - seen)}')
