"""Count `open … in`-style prefixes whose next non-blank line doesn't start a declaration."""
import os, re, sys
P = re.compile(r'^(open|set_option|variable|omit|include|attribute|local|scoped)\b.*\bin\s*$')
D = re.compile(r'^(@\[|(private |protected |noncomputable |partial |unsafe |nonrec )*(theorem|lemma|def|abbrev|structure|class|instance|inductive|opaque|example|axiom|macro|syntax|elab|notation|infix|instance)\b|(open|set_option|variable|omit|include|attribute|local|scoped)\b.*\bin\s*$|/--|#)')
for root in sys.argv[1:]:
    n = 0; ex = None
    for d, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith('.lean'): continue
            L = open(os.path.join(d, f), encoding='utf-8').read().split('\n')
            for i, l in enumerate(L):
                if P.match(l):
                    nxt = next((x for x in L[i + 1:] if x.strip()), '')
                    if not D.match(nxt): n += 1; ex = ex or (os.path.relpath(os.path.join(d, f), root), l, nxt)
    print(root.split('/')[-2] if root.endswith('src') else root, 'dangling prefixes:', n, ex)
