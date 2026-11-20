"""Source-level estimate of which declarations the RH proof actually uses.

Reads the .lean files as text (runs nothing). Resolves each identifier the way Lean roughly
does: as written, under every enclosing namespace, and under every `open`ed namespace; a
qualified name that is not a declaration falls back to its prefix (structure fields and
constructors). Generalized field notation (`h.foo`) matches every declaration ending in `.foo`
whose name occurs in the file. The goal is an over-approximation: keep too much rather than
too little, and let a compile settle the rest.

usage: reach.py SRC_DIR ROOT_DECL... [--keep-instances]
"""
import os, re, sys, collections, array
OUT = os.path.expanduser(os.environ.get('RH_TRIM_OUT', 'rh-trim-out'))
os.makedirs(OUT, exist_ok=True)

src = sys.argv[1]
roots = [a for a in sys.argv[2:] if not a.startswith('--')]
keep_inst = '--keep-instances' in sys.argv

KW = r'(?:theorem|lemma|def|abbrev|structure|class|instance|inductive|opaque|axiom)'
declre = re.compile(r'^(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable|partial|unsafe|nonrec)\s+)*'
                    r'(' + KW + r')\b\s*([^\s:({\[⦃]*)', re.M)
nsre = re.compile(r'^(namespace|end|section|open)\b(.*)$', re.M)
ident = re.compile(r"[A-Za-z_À-ɏͰ-Ͽᴀ-ᶿ℀-⅏\U0001d400-\U0001d7ff]"
                   r"[A-Za-z0-9_'!?.À-ɏͰ-Ͽᴀ-ᶿ₀-ₜ℀-⅏\U0001d400-\U0001d7ff]*")
PREFIX_IN = re.compile(r'^(?:open|set_option|variable|omit|include|attribute|local|scoped)\b.*\bin\s*$')
ctorre = re.compile(r'^\s*\|\s*([^\s:({\[]+)', re.M)
fieldre = re.compile(r'^\s+([^\s:({\[]+)\s*:', re.M)

files = []          # module names
decl_file = array.array('i')
decl_name = []
decl_inst = array.array('b')
name2id = {}
name2ids = collections.defaultdict(list)
last2ids = collections.defaultdict(list)
spans = []          # per file: list of (decl_id, start, end) offsets, and ns info

def add(full, fid, inst, attr=0, span=None):
    decl_attr.append(attr); decl_span.append(span); decl_cls.append(0)
    i = len(decl_name)
    decl_name.append(full); decl_file.append(fid); decl_inst.append(1 if inst else 0)
    name2id.setdefault(full, i)
    name2ids[full].append(i)
    last2ids[full.rsplit('.', 1)[-1]].append(i)
    return i

paths = []
for d, _, fs in os.walk(src):
    for f in fs:
        if f.endswith('.lean'):
            paths.append(os.path.join(d, f))
paths.sort()

import pickle
import hashlib
CACHE = os.path.join(OUT, 'reach-cache-%s%s.pkl' % (hashlib.sha1(os.path.abspath(src).encode()).hexdigest()[:8], '-v2' if '--v2' in sys.argv else ''))
cached = '--cached' in sys.argv and os.path.exists(CACHE)
if cached:
    deps = pickle.load(open(CACHE, 'rb'))[5]
print('pass 1: declarations', file=sys.stderr)
file_ctx = []
file_imports = []
decl_attr = bytearray()
decl_cls = bytearray()
decl_span = []
inst_header = {}
for fid, p in enumerate(paths):
    files.append(os.path.relpath(p, src)[:-5].replace('/', '.'))
    t = open(p, encoding='utf-8').read()
    file_imports.append([w for l in re.findall(r'^import\s+(.+)$', t, re.M) for w in l.split()])
    events = sorted([(m.start(), 'ns', m) for m in nsre.finditer(t)] +
                    [(m.start(), 'd', m) for m in declre.finditer(t)], key=lambda e: e[0])
    stack, opens, decls = [], set(), []
    for pos, kind, m in events:
        if kind == 'ns':
            k, rest = m.group(1), m.group(2).strip()
            if k == 'namespace':
                stack.append(rest)
            elif k == 'section':
                stack.append(None)
            elif k == 'end':
                if stack: stack.pop()
            elif k == 'open':
                for w in rest.replace('in', ' ').split():
                    if w[0].isalpha() or w[0] == '_': opens.add(w)
        else:
            kw, nm = m.group(1), m.group(2)
            ns = '.'.join(x for x in stack if x)
            if kw == 'instance' and (not nm or nm.startswith('[') or nm in ('(', ':')):
                nm = f'_inst_{fid}_{pos}'
            if nm.startswith('_root_.'):
                full = nm[7:]
            else:
                full = (ns + '.' + nm) if ns and nm else (nm or f'_anon_{fid}_{pos}')
            ls = t.rfind('\n', 0, pos) + 1
            st0 = ls
            # attribute lines directly above belong to the declaration
            while st0 > 0:
                j = st0
                while j > 0:                      # look past blank lines
                    prev = t.rfind('\n', 0, j - 1) + 1
                    if t[prev:j - 1].strip() == '': j = prev
                    else: break
                if j == 0: break
                prev = t.rfind('\n', 0, j - 1) + 1
                ln = t[prev:j - 1]
                if ln.startswith('@[') or PREFIX_IN.match(ln): st0 = prev
                else: break
            attr = 1 if (st0 < ls or m.group(0).lstrip().startswith('@[')) else 0
            # the declaration runs until the next line that starts in column 0
            nxt = re.search(r'\n(?=\S)', t[pos:])
            en = pos + nxt.start() + 1 if nxt else len(t)
            i = add(full, fid, kw == 'instance', attr, (st0, en))
            if kw == 'class': decl_cls[i] = 1
            if kw == 'instance':
                body = t[pos:en]
                cut = min([k for k in (body.find(':='), body.find(' where'), body.find('\nwhere')) if k > 0] or [len(body)])
                inst_header[i] = (body[:cut], fid, ns)
            decls.append((i, pos, ns, kw))
    # end offsets
    out = []
    for j, (i, pos, ns, kw) in enumerate(decls):
        end = decls[j + 1][1] if j + 1 < len(decls) else len(t)
        out.append((i, pos, end, ns, kw))
        if kw in ('structure', 'class', 'inductive'):
            body = t[pos:end]
            base = decl_name[i]
            for c in ctorre.findall(body) + fieldre.findall(body):
                add(base + '.' + c, fid, False, 0, None)
            add(base + '.mk', fid, False, 0, None)
    file_ctx.append((out, frozenset(opens)))

print('declarations:', len(decl_name), file=sys.stderr)

V2 = '--v2' in sys.argv
mod2fid = {m: i for i, m in enumerate(files)}
dupnames = {k for k, v in name2ids.items() if len(set(decl_file[i] for i in v)) > 1}
dupfiles = sorted({decl_file[i] for k in dupnames for i in name2ids[k]})
dbit = {f: 1 << j for j, f in enumerate(dupfiles)}
anc = [None] * len(files)
if V2:
    sys.setrecursionlimit(10000)
    for f0 in range(len(files)):
        if anc[f0] is not None: continue
        stack = [(f0, iter(file_imports[f0]))]
        anc[f0] = -1
        while stack:
            f, it = stack[-1]
            nxt = None
            for imp in it:
                g = mod2fid.get(imp)
                if g is not None and anc[g] is None:
                    nxt = g; break
            if nxt is not None:
                anc[nxt] = -1
                stack.append((nxt, iter(file_imports[nxt])))
                continue
            stack.pop()
            b = 0
            for imp in file_imports[f]:
                g = mod2fid.get(imp)
                if g is not None and anc[g] not in (None, -1):
                    b |= anc[g] | dbit.get(g, 0)
            anc[f] = b
    print(f'import-aware: {len(dupnames)} duplicated names across {len(dupfiles)} files', file=sys.stderr)

def visible(i, fid):
    """Can file fid see declaration i? Only matters for duplicated names."""
    f = decl_file[i]
    return f == fid or (anc[fid] & dbit.get(f, 0)) != 0

binder_res = [
    re.compile(r'[(\{\[⦃]\s*([^():{}\[\]⦃⦄=]+?)\s*:'),                 # (x y : T)  {x : T}  [h : C]
    re.compile(r'(?:fun|λ)\s+([^=↦]+?)\s*(?:=>|↦)'),                   # fun x y =>
    re.compile(r'\b(?:intro|intros|rintro|introv|ext|funext)\b([^\n;]*)'),  # intro a b
    re.compile(r'\b(?:obtain|rcases|cases|induction|match|rcases)\b[^\n]*?\bwith\b([^\n]*)'),
    re.compile(r'\bobtain\s+([^:=\n]*)'),
    re.compile(r'\b(?:have|haveI|let|letI|set|replace|suffices|show_term|generalize)\s+([^\s:⟨(=]+)'),
    re.compile(r'\bwith\s+([^\s,\]\)⟩]+)'),
    re.compile(r'[∀∃∑∏⋃⋂]\s*([^,:]+?)\s*[,:∈]'),
    re.compile(r'^\s*\|\s*[^\s=]+\s+([^=\n]*?)\s*=>', re.M),               # | succ n ih =>
    re.compile(r'⟨([^⟨⟩]*)⟩'),                                             # ⟨a, b⟩ patterns
]
def locals_of(text):
    out = set()
    for rx in binder_res:
        for g in rx.findall(text):
            for w in ident.findall(g):
                if '.' not in w: out.add(w)
    return out

def resolve(tok, nsprefixes, opens, fid=None):
    hits = set()
    cands = [tok]
    for ns in nsprefixes:
        cands.append(ns + '.' + tok)
    for o in opens:
        cands.append(o + '.' + tok)
    for c in cands:
        while c:
            ids = name2ids.get(c)
            if ids:
                hits.update(ids); break
            if '.' not in c: break
            c = c.rsplit('.', 1)[0]
            if c in name2ids:
                hits.update(name2ids[c]); break
    if V2 and fid is not None and hits:
        vis = {i for i in hits if decl_name[i] not in dupnames or visible(i, fid)}
        if vis: hits = vis
    return hits

print('pass 2: references', file=sys.stderr, flush=True)
adj_start = array.array('q', [0]) ; adj = array.array('i')
if not cached: deps = [None] * len(decl_name)
for fid, p in enumerate([] if cached else paths):
    t = open(p, encoding='utf-8').read()
    out, opens = file_ctx[fid]
    for (i, pos, end, ns, kw) in out:
        parts = ns.split('.') if ns else []
        prefixes = ['.'.join(parts[:k]) for k in range(len(parts), 0, -1)]
        own = decl_name[i].split('.')
        prefixes += ['.'.join(own[:k]) for k in range(len(own) - 1, 0, -1)]
        hits = set()
        body = t[pos:end]
        loc = locals_of(body) if V2 else ()
        for tok in set(ident.findall(body)):
            tok = tok.rstrip('.')
            if tok.startswith('_root_.'): tok = tok[7:]
            if not tok: continue
            if V2 and tok.split('.', 1)[0] in loc and not tok.startswith('_root_'):
                continue
            hits |= resolve(tok, prefixes, opens, fid)
        hits.discard(i)
        deps[i] = array.array('i', sorted(hits))
    if fid % 10000 == 0: print(f'  {fid} files', file=sys.stderr, flush=True)

if not cached:
    pickle.dump((files, decl_file, decl_name, decl_inst, name2ids, deps), open(CACHE, 'wb'), protocol=5)
roots_ids = []
main_fid = files.index('Main')
for r in roots:
    ids = [i for i in name2ids.get(r, []) if decl_file[i] == main_fid]
    if ids: roots_ids += ids
    else: print('root not found in Main:', r, file=sys.stderr)
dups = sum(1 for k, v in name2ids.items() if len(set(decl_file[i] for i in v)) > 1)
print(f'names declared in more than one file: {dups}', flush=True)
if keep_inst:
    roots_ids += [i for i in range(len(decl_name)) if decl_inst[i]]

file_decls = collections.defaultdict(list)
for i in range(len(decl_name)): file_decls[decl_file[i]].append(i)
file_closure = '--file-closure' in sys.argv
class_gated = '--class-gated' in sys.argv
KEEP_ATTR = "--no-attr" not in sys.argv
fseen = bytearray(len(files))
seen = bytearray(len(decl_name))
parent = {}
BLOCK = set()
for a in sys.argv:
    if a.startswith('--block='):
        for nm in a[8:].split(','):
            BLOCK.update(name2ids.get(nm, []))
def run(st):
    while st:
        x = st.pop()
        if seen[x] or x in BLOCK: continue
        seen[x] = 1
        if not fseen[decl_file[x]]:
            fseen[decl_file[x]] = 1
            if file_closure:
                st.extend(y for y in file_decls[decl_file[x]] if not seen[y])
            elif not class_gated:
                st.extend(y for y in file_decls[decl_file[x]] if not seen[y] and (decl_inst[y] or (decl_attr[y] and KEEP_ATTR)))
        d = deps[x]
        if d is not None:
            for y in d:
                if not seen[y]:
                    parent.setdefault(y, x); st.append(y)
run(list(roots_ids))
print(f"  named references only: {sum(seen)} declarations in {sum(fseen)} files", file=sys.stderr, flush=True)
if class_gated:
    insts = [i for i in range(len(decl_name)) if decl_inst[i] and deps[i] is not None]
    hdr_deps = {}
    for i, (h, fid_, ns_) in inst_header.items():
        parts = ns_.split('.') if ns_ else []
        prefixes = ['.'.join(parts[:k]) for k in range(len(parts), 0, -1)]
        hs = set()
        for tok in set(ident.findall(h)):
            tok = tok.rstrip('.')
            if tok.startswith('_root_.'): tok = tok[7:]
            if tok: hs |= resolve(tok, prefixes, file_ctx[fid_][1], fid_)
        hs.discard(i); hdr_deps[i] = hs
    print(f'  instance headers resolved: {len(hdr_deps)}', file=sys.stderr, flush=True)
    rnd = 0
    while True:
        add_ = []
        for i in insts:
            if seen[i] or i not in hdr_deps: continue
            hd = hdr_deps[i]
            proj_cls = [d for d in hd if decl_cls[d]]
            cls_ok = (not proj_cls) or any(seen[d] for d in proj_cls)
            if cls_ok and any(seen[d] for d in hd if not decl_cls[d]):
                add_.append(i)
        rnd += 1
        print(f'  instance round {rnd}: +{len(add_)}', file=sys.stderr, flush=True)
        if not add_: break
        run(add_)
for a in sys.argv:
    if a.startswith('--why='):
        for nm in a[6:].split(','):
            for i in name2ids.get(nm, []):
                if not seen[i]: print(f'why {nm}: not reached'); continue
                path = [i]
                while path[-1] in parent and len(path) < 60: path.append(parent[path[-1]])
                print(f'why {nm}:'); [print('   ', decl_name[j], '  [', files[decl_file[j]], ']') for j in reversed(path)]
if '--no-write' in sys.argv:
    print(f'reachable: {sum(seen)} declarations in {sum(fseen)} files'); sys.exit(0)
reach = [i for i in range(len(decl_name)) if seen[i]]
rf = set(decl_file[i] for i in reach)
print(f'reachable declarations: {len(reach)} of {len(decl_name)}')
print(f'files holding them: {len(rf)} of {len(files)}')
with open(os.path.join(OUT, 'reach-files' + ('-inst' if keep_inst else '') + ('-fc' if '--file-closure' in sys.argv else '') + '.txt'), 'w') as h:
    for f in sorted(files[i] for i in rf): h.write(f + '\n')

import json
cuts = {}
for f in rf:
    sp = []
    for i in file_decls[f]:
        if not seen[i] and decl_span[i] is not None:
            sp.append(decl_span[i])
    cuts[files[f]] = sorted(sp)
json.dump(cuts, open(os.path.join(OUT, 'reach-cuts.json'), 'w'))
kept_decl_lines = 0
print('declarations cut from kept files:', sum(len(v) for v in cuts.values()))
