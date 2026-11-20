import os, re, collections, statistics
root='.'
lines=[]; doc=0; comm=0; decls=0; files=0; ns_mismatch=0; ns_files=0; maxf=(0,'')
imports_per=[]; names=collections.Counter(); short_names=0; sorry=0
declre=re.compile(r'^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*(theorem|lemma|def|abbrev|structure|class|instance|inductive)\s+([^\s:({\[]+)')
for d,_,fs in os.walk(root):
    for f in fs:
        if not f.endswith('.lean'): continue
        p=os.path.join(d,f); files+=1
        t=open(p,encoding='utf-8').read(); L=t.count('\n')+1; lines.append(L)
        if L>maxf[0]: maxf=(L,p)
        doc+=t.count('/--'); comm+=len(re.findall(r'(^|\s)--',t))+t.count('/-!')
        imports_per.append(len(re.findall(r'^import ',t,re.M)))
        top=p.split('/')[1]
        m=re.search(r'^namespace\s+(\S+)',t,re.M)
        for line in t.splitlines():
            mm=declre.match(line)
            if mm:
                decls+=1; n=mm.group(2); last=n.split('.')[-1]; names[last]+=1
                if len(last)<=4: short_names+=1
        if m:
            ns_files+=1
            if not m.group(1).startswith(top) : ns_mismatch+=1
print('files',files,'lines',sum(lines))
print('lines/file median',statistics.median(lines),'p90',sorted(lines)[int(.9*len(lines))],'max',maxf)
print('docstrings',doc,'comments',comm)
print('imports/file median',statistics.median(imports_per),'max',max(imports_per))
print('decls',decls,'short names(<=4 chars)',short_names)
print('files w/ namespace',ns_files,'namespace not matching top dir',ns_mismatch)
print('most repeated short names',names.most_common(15))
