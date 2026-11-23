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
    elif 'unknown namespace' in msg: pass          # handled below by keeping one declaration of it
    else: files.add(f)
namespaces = set(); ns_where = collections.defaultdict(set)
for l in errs:
    m = re.search(r'unknown namespace `([^`]+)`', l)
    if m:
        namespaces.add(m.group(1).replace('_root_.', ''))
        fm = re.search(r'error: src/(.+?)\.lean', l)
        if fm: ns_where[m.group(1).replace('_root_.', '')].add(fm.group(1).replace('/', '.'))
by2, by1 = collections.defaultdict(set), collections.defaultdict(set)
size = {}; modof = {}; impg = {}
for l in open(dump, encoding='utf-8'):
    p = l.rstrip('\n').split('\t')
    if p[0] == 'I': impg[p[1]] = p[2].split() if len(p) > 2 and p[2] else []
    if p[0] != 'D': continue
    parts = p[1].split('.'); by1[parts[-1]].add(p[1]); size[p[1]] = int(p[4]) - int(p[3]); modof[p[1]] = p[2]
    if len(parts) > 1: by2['.'.join(parts[-2:])].add(p[1])

_clo = {}
def closure(m):
    """modules a file sees in the original: itself plus everything it imports, directly or not"""
    if m in _clo: return _clo[m]
    seen, st = {m}, [m]
    while st:
        x = st.pop()
        for i in impg.get(x, []):
            if i not in seen: seen.add(i); st.append(i)
    _clo[m] = seen; return seen
def visible_to(cands, files_):
    """keep the candidates a failing file can actually see; if none can, fall back to all"""
    vis = set()
    for f in files_: vis |= closure(f)
    v = {c for c in cands if modof.get(c) in vis}
    return v or cands

add = set(); unmatched = []
for x in missing:
    parts = x.split('.')
    hit = by2.get('.'.join(parts[-2:]), set()) if len(parts) > 1 else set()
    if not hit: hit = by1.get(parts[-1], set()) if len(by1.get(parts[-1], ())) <= 20 else set()
    # `foo.mpr`, `cpCutoff.choose`, `Struct.field`: the missing thing is the stem, the last part is how it's used
    if not hit and len(parts) > 1:
        stem = parts[:-1]
        hit = by2.get('.'.join(stem[-2:]), set()) if len(stem) > 1 else set()
        if not hit: hit = by1.get(stem[-1], set()) if len(by1.get(stem[-1], ())) <= 20 else set()
    # `h.mul` on a type that unfolds to a core one (And, Function, ...): keep the `.mul` lemmas the file can see
    if not hit and len(parts) == 2 and parts[0] in ('And', 'Or', 'Function', 'Exists', 'Iff', 'Eq', 'Not', 'Prod', 'Subtype', 'Set', 'Nat', 'Int'):
        vis = visible_to(by1.get(parts[1], set()), where[x])
        if 0 < len(vis) <= 60 and vis != by1.get(parts[1], set()) or 0 < len(vis) <= 12: hit = vis
    if hit: add |= visible_to(hit, where[x])
    else: unmatched.append(x); files |= where[x]     # can't find it: keep the file that uses it as it was
# an `open` of a namespace whose every declaration was cut fails, and takes every other name on that line with it:
# keep the smallest declaration in each such namespace (written relative to the file, so match it anywhere)
ns_kept = 0
for ns in namespaces:
    cands = {n for n in size if n.startswith(ns + '.') or ('.' + ns + '.') in n}
    if cands:
        vis = visible_to(cands, ns_where[ns])
        add.add(min(vis, key=lambda n: size[n])); ns_kept += 1
    else: unmatched.append('namespace ' + ns)
old_x = set(l.strip() for l in open(extra_p)) if __import__('os').path.exists(extra_p) else set()
old_r = set(l.strip() for l in open(revert_p)) if __import__('os').path.exists(revert_p) else set()
open(extra_p, 'w').write(''.join(n + '\n' for n in sorted(old_x | add)))
open(revert_p, 'w').write(''.join(n + '\n' for n in sorted((old_r | files) - {''})))
print(f'{len(errs)} errors: {len(namespaces)} unknown namespaces ({ns_kept} kept), {len(missing)} missing names -> {len(add)} declarations kept ({len(unmatched)} unmatched); '
      f'{len(files)} files kept as they were. Totals: {len(old_x | add)} extra names, {len(old_r | files)} reverted files')
for x in unmatched[:10]: print('  unmatched:', x)
if not ((old_x | add) - old_x) and not ((old_r | files) - old_r):
    print('NO PROGRESS: this round reported nothing new to keep'); sys.exit(3)
