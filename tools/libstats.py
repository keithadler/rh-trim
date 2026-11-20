import os, re, sys, collections, json
declre = re.compile(r'^(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable|partial|unsafe|nonrec)\s+)*(?:theorem|lemma|def|abbrev|structure|class|instance|inductive|opaque)\b', re.M)
def stats(root):
    s = collections.defaultdict(lambda: [0, 0, 0])
    for d, _, fs in os.walk(root):
        for f in fs:
            if f.endswith('.lean'):
                p = os.path.join(d, f); rel = os.path.relpath(p, root)
                top = rel.split('/')[0] if '/' in rel else rel[:-5]
                t = open(p, encoding='utf-8').read()
                s[top][0] += 1; s[top][1] += t.count('\n') + 1; s[top][2] += len(declre.findall(t))
    return s
a, b = stats(sys.argv[1]), stats(sys.argv[2])
json.dump({'orig': a, 'fork': b}, open(sys.argv[3], 'w'), indent=1)
for k in sorted(a, key=lambda k: -a[k][1]):
    o, n = a[k], b.get(k, [0, 0, 0])
    print(f"{k:20s} files {o[0]:>7,} -> {n[0]:>7,}   lines {o[1]:>10,} -> {n[1]:>10,} ({100*n[1]/max(o[1],1):.0f}%)   decls {o[2]:>8,} -> {n[2]:>8,}")
