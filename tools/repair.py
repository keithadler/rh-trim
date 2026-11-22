#!/usr/bin/env python3
"""Read the build's errors since the last round marker and grow the keep lists.
usage: repair.py BUILD_LOG DECLS_DUMP EXTRA_NAMES REVERT_FILES
* `Unknown identifier/constant X`, `environment does not contain X`: keep every source declaration whose
  name ends with the last two parts of X (the parser can misread outer namespaces, never the last parts);
  if none, the ones ending with its last part.
* Any other error: keep that file as it was."""
import re, sys, collections
log, dump, extra_p, revert_p = sys.argv[1:5]
lines = open(log, errors='replace').read().split('\n')
start = max(i for i, l in enumerate(lines) if l.startswith('== ') and ' source: ' in l)
errs = [l for l in lines[start:] if ' error: ' in l and 'Lean exited' not in l]
missing, files = set(), set(); where = collections.defaultdict(set)
for l in errs:
    m = re.search(r'error: src/(.+?)\.lean:\d+:\d+: (.*)', l)
    if not m: continue
    f, msg = m.group(1).replace('/', '.'), m.group(2)
    n = re.search(r'Unknown (?:identifier|constant) `([^`]+)`', msg) or re.search(r'does not contain `([^`]+)`', msg)
    if n: missing.add(n.group(1).replace('_root_.', '')); where[n.group(1).replace('_root_.', '')].add(f)
    else: files.add(f)
by2, by1 = collections.defaultdict(set), collections.defaultdict(set)
for l in open(dump, encoding='utf-8'):
    p = l.rstrip('\n').split('\t')
    if p[0] != 'D': continue
    parts = p[1].split('.'); by1[parts[-1]].add(p[1])
    if len(parts) > 1: by2['.'.join(parts[-2:])].add(p[1])
add = set(); unmatched = []
for x in missing:
    parts = x.split('.')
    hit = by2.get('.'.join(parts[-2:]), set()) if len(parts) > 1 else set()
    if not hit: hit = by1.get(parts[-1], set()) if len(by1.get(parts[-1], ())) <= 20 else set()
    if hit: add |= hit
    else: unmatched.append(x); files |= where[x]     # can't find it: keep the file that uses it as it was
old_x = set(l.strip() for l in open(extra_p)) if __import__('os').path.exists(extra_p) else set()
old_r = set(l.strip() for l in open(revert_p)) if __import__('os').path.exists(revert_p) else set()
open(extra_p, 'w').write(''.join(n + '\n' for n in sorted(old_x | add)))
open(revert_p, 'w').write(''.join(n + '\n' for n in sorted((old_r | files) - {''})))
print(f'{len(errs)} errors: {len(missing)} missing names -> {len(add)} declarations kept ({len(unmatched)} unmatched); '
      f'{len(files)} files kept as they were. Totals: {len(old_x | add)} extra names, {len(old_r | files)} reverted files')
for x in unmatched[:10]: print('  unmatched:', x)
