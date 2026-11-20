import os, re, sys
root = sys.argv[1]
imp = {}
for d, _, fs in os.walk(root):
    for f in fs:
        if f.endswith('.lean'):
            p = os.path.join(d, f)
            mod = os.path.relpath(p, root)[:-5].replace('/', '.')
            ims = []
            with open(p, encoding='utf-8') as h:
                for line in h:
                    m = re.match(r'\s*import\s+(.+)', line)
                    if m: ims += m.group(1).split()
                    elif line.strip() and not line.startswith(('import', '--', 'module', 'public', 'prelude')): break
            imp[mod] = [i for i in ims if not i.startswith(('Mathlib', 'Init', 'Std', 'Lean', 'Batteries', 'Aesop', 'Qq'))]
def closure(m):
    seen, st = set(), [m]
    while st:
        x = st.pop()
        if x in seen or x not in imp: continue
        seen.add(x); st += imp[x]
    return seen
print("modules", len(imp))
for m in sys.argv[2:]:
    print(len(closure(m)), m)
