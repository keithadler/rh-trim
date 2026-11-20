"""Turn a failed build log into a list of what the reduction cut but the proof needs.

Reads Lean's errors ("Unknown identifier `X`", "unknown constant 'X'") and, for each name,
finds where the original (the mirror) declares it. Put each listed declaration back into the
reduced file at the same path, or report the list in a build-report issue.

usage: missing.py BUILD_LOG MIRROR_SRC
"""
import collections, os, re, sys

log, orig = sys.argv[1:3]
errre = re.compile(r"error: (src/\S+?\.lean):\d+:\d+: (?:Unknown identifier|unknown identifier|Unknown constant|unknown constant) [`'‘]([^`'’]+)[`'’]")
names = collections.defaultdict(set)
for line in open(log, encoding='utf-8', errors='replace'):
    for m in errre.finditer(line):
        n = m.group(2)
        if n.startswith('_root_.'): n = n[7:]
        names[n].add(m.group(1))
if not names:
    print('no unknown-identifier errors found'); sys.exit(0)

lasts = {n.split('.')[-1] for n in names}
declre = re.compile(r'^(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable|partial|unsafe|nonrec)\s+)*'
                    r'(?:theorem|lemma|def|abbrev|structure|class|instance|inductive|opaque)\s+([^\s:({\[⦃]+)', re.M)
found = collections.defaultdict(list)
for d, _, fs in os.walk(orig):
    for f in fs:
        if not f.endswith('.lean'): continue
        p = os.path.join(d, f)
        t = open(p, encoding='utf-8').read()
        for m in declre.finditer(t):
            full = m.group(1)
            if full.split('.')[-1] in lasts:
                found[full.split('.')[-1]].append((full, os.path.relpath(p, os.path.dirname(orig.rstrip('/'))), t.count('\n', 0, m.start()) + 1))

print(f'{len(names)} missing names\n')
for n in sorted(names):
    last = n.split('.')[-1]
    cands = [c for c in found.get(last, []) if c[0] == n or c[0].endswith('.' + n) or n.endswith('.' + c[0].split('.', 1)[-1]) or c[0].split('.')[-1] == last]
    exact = [c for c in cands if c[0] == n or c[0].endswith('.' + n)]
    show = exact or cands
    print(f'{n}   (needed by {len(names[n])} file(s), e.g. {sorted(names[n])[0]})')
    for full, path, line in show[:5]:
        print(f'    declared as {full}  in {path}:{line}')
    if not show:
        print('    not found by name: may be notation, a field, or a macro')
    print()
