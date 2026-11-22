// xan: analyses over xidx's output. Usage:
//   xan DIR PROJECT_NAMES.txt ROOT1 [ROOT2 ...]
// Reads DIR/decls.tsv and DIR/edges.bin, writes DIR/report.txt and a few TSVs:
//   trusted-base.tsv  declarations the theorem STATEMENTS rest on (definitions unfolded, proofs not)
//   dups.tsv          theorems with identical statements (same exported type expression)
//   hubs.tsv          project declarations used directly by the most other declarations
//   dominators.tsv    declarations that every dependency path to some part of the proof runs through,
//                     with the share of the proof (declarations, expression nodes) only reachable via them
//   spine.tsv         from the roots down: at each step the child dominating the most of the proof
//   biggest.tsv       project declarations with the largest proof terms (expression nodes)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct { char *name; char kind; uint32_t type_expr; uint64_t tn, vn; int project; } D;
static D *d; static uint32_t nd;

// ---- string hash set for project names
static char **hs; static uint64_t hcap;
static uint64_t hh(const char *s) { uint64_t h = 1469598103934665603ULL; while (*s) { h ^= (unsigned char)*s++; h *= 1099511628211ULL; } return h; }
static void hadd(char *s) { uint64_t i = hh(s) & (hcap - 1); while (hs[i]) { if (!strcmp(hs[i], s)) return; i = (i + 1) & (hcap - 1); } hs[i] = s; }
static int hhas(const char *s) { uint64_t i = hh(s) & (hcap - 1); while (hs[i]) { if (!strcmp(hs[i], s)) return 1; i = (i + 1) & (hcap - 1); } return 0; }
// name -> decl index
static uint32_t *nh; static uint64_t ncap2;
static void nadd(uint32_t idx) { uint64_t i = hh(d[idx].name) & (ncap2 - 1); while (nh[i]) i = (i + 1) & (ncap2 - 1); nh[i] = idx + 1; }
static int64_t nfind(const char *s) { uint64_t i = hh(s) & (ncap2 - 1); while (nh[i]) { if (!strcmp(d[nh[i] - 1].name, s)) return nh[i] - 1; i = (i + 1) & (ncap2 - 1); } return -1; }

static int autogen(const char *n) {
  return strstr(n, "._") || strstr(n, ".eq_") || strstr(n, ".match_") || strstr(n, "_proof_") || strstr(n, "_simp_")
      || strstr(n, ".proof_") || strstr(n, "_sunfold") || strstr(n, ".eq_def") || strstr(n, "_cstage") || strstr(n, ".injEq")
      || strstr(n, ".inj") || strstr(n, ".sizeOf_spec") || strstr(n, ".ext_iff") || strstr(n, "_aux_");
}

static uint32_t *fo, *fa, *ro, *ra, *to_, *ta; // forward CSR (all), reverse CSR (all), type-only forward CSR
static int cmp_u64(const void *a, const void *b) { uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b; return x < y ? -1 : x > y; }

int main(int argc, char **argv) {
  if (argc < 4) { fprintf(stderr, "usage: xan DIR PROJECT_NAMES ROOT...\n"); return 2; }
  char p[4096]; char *line = NULL; size_t cap = 0;
  // decls
  snprintf(p, sizeof p, "%s/decls.tsv", argv[1]); FILE *f = fopen(p, "r"); if (!f) { perror(p); return 2; }
  uint32_t dcap = 1 << 20; d = malloc(sizeof(D) * dcap);
  while (getline(&line, &cap, f) > 0) {
    if (nd == dcap) { dcap *= 2; d = realloc(d, sizeof(D) * dcap); }
    char *f0 = strtok(line, "\t"), *k = strtok(NULL, "\t"), *nm = strtok(NULL, "\t"), *te = strtok(NULL, "\t"),
         *tn = strtok(NULL, "\t"), *vn = strtok(NULL, "\t");
    (void)f0;
    d[nd].name = strdup(nm); d[nd].kind = k[0] == 't' ? 'T' : k[0] == 'd' ? 'D' : k[0] == 'i' ? 'I' : k[0] == 'o' ? 'O' : k[0] == 'a' ? 'A' : 'Q';
    d[nd].type_expr = strtoul(te, 0, 10); d[nd].tn = strtoull(tn, 0, 10); d[nd].vn = strtoull(vn, 0, 10); nd++;
  }
  fclose(f);
  ncap2 = 1; while (ncap2 < (uint64_t)nd * 3) ncap2 <<= 1; nh = calloc(ncap2, 4);
  for (uint32_t i = 0; i < nd; i++) nadd(i);
  // project names
  f = fopen(argv[2], "r"); if (!f) { perror(argv[2]); return 2; }
  hcap = 1 << 23; hs = calloc(hcap, sizeof(char *));
  while (getline(&line, &cap, f) > 0) { line[strcspn(line, "\n")] = 0; hadd(strdup(line)); }
  fclose(f);
  for (uint32_t i = 0; i < nd; i++) d[i].project = hhas(d[i].name);
  // edges
  snprintf(p, sizeof p, "%s/edges.bin", argv[1]); f = fopen(p, "rb");
  fseek(f, 0, SEEK_END); uint64_t ne = ftell(f) / 12; fseek(f, 0, SEEK_SET);
  uint32_t *E = malloc(ne * 12); if (fread(E, 12, ne, f) != ne) { fprintf(stderr, "short read\n"); return 2; } fclose(f);
  fo = calloc(nd + 1, 4); ro = calloc(nd + 1, 4); to_ = calloc(nd + 1, 4);
  // merge type and value edges into one (src,dst) set for the all-graph
  for (uint64_t i = 0; i < ne; i++) { fo[E[3 * i] + 1]++; ro[E[3 * i + 1] + 1]++; if (E[3 * i + 2] == 1) to_[E[3 * i] + 1]++; }
  for (uint32_t i = 0; i < nd; i++) { fo[i + 1] += fo[i]; ro[i + 1] += ro[i]; to_[i + 1] += to_[i]; }
  fa = malloc(4 * (uint64_t)fo[nd]); ra = malloc(4 * (uint64_t)ro[nd]); ta = malloc(4 * (uint64_t)to_[nd]);
  uint32_t *fc = calloc(nd, 4), *rc = calloc(nd, 4), *tc = calloc(nd, 4);
  for (uint64_t i = 0; i < ne; i++) {
    uint32_t s = E[3 * i], t = E[3 * i + 1];
    fa[fo[s] + fc[s]++] = t; ra[ro[t] + rc[t]++] = s; if (E[3 * i + 2] == 1) ta[to_[s] + tc[s]++] = t;
  }
  free(E);
  // in-degree in distinct sources (a decl may appear twice: once from its type, once from its value)
  uint32_t *indeg = calloc(nd, 4);
  { uint32_t *mark = calloc(nd, 4);
    for (uint32_t t = 0; t < nd; t++) for (uint32_t j = ro[t]; j < ro[t + 1]; j++) { uint32_t s = ra[j]; if (mark[s] != t + 1) { mark[s] = t + 1; indeg[t]++; } }
    free(mark); }
  // roots
  int nr = argc - 3; uint32_t roots[64];
  for (int i = 0; i < nr; i++) { int64_t r = nfind(argv[3 + i]); if (r < 0) { fprintf(stderr, "root not found: %s\n", argv[3 + i]); return 2; } roots[i] = r; }

  snprintf(p, sizeof p, "%s/report.txt", argv[1]); FILE *R = fopen(p, "w");
  // ---------- totals
  uint64_t cnt[2][128] = {{0}}, nodes[2] = {0, 0};
  for (uint32_t i = 0; i < nd; i++) { cnt[d[i].project][(int)d[i].kind]++; nodes[d[i].project] += d[i].tn + d[i].vn; }
  fprintf(R, "== totals\n%u declarations, %llu dependency edges\n", nd, (unsigned long long)ne);
  for (int pj = 1; pj >= 0; pj--)
    fprintf(R, "%-9s thm %llu, def %llu, inductive %llu, opaque %llu, axiom %llu, quot %llu, total %llu, expression nodes %llu\n",
            pj ? "project" : "library", (unsigned long long)cnt[pj]['T'], (unsigned long long)cnt[pj]['D'], (unsigned long long)cnt[pj]['I'],
            (unsigned long long)cnt[pj]['O'], (unsigned long long)cnt[pj]['A'], (unsigned long long)cnt[pj]['Q'],
            (unsigned long long)(cnt[pj]['T'] + cnt[pj]['D'] + cnt[pj]['I'] + cnt[pj]['O'] + cnt[pj]['A'] + cnt[pj]['Q']), (unsigned long long)nodes[pj]);

  // ---------- trusted base of the statements
  { uint8_t *seen = calloc(nd, 1); uint32_t *q = malloc(4 * nd); uint64_t h = 0, t = 0;
    for (int i = 0; i < nr; i++) for (uint32_t j = to_[roots[i]]; j < to_[roots[i] + 1]; j++) { uint32_t x = ta[j]; if (!seen[x]) { seen[x] = 1; q[t++] = x; } }
    while (h < t) {
      uint32_t x = q[h++];
      uint32_t *o = d[x].kind == 'T' ? to_ : fo, *a = d[x].kind == 'T' ? ta : fa;
      for (uint32_t j = o[x]; j < o[x + 1]; j++) { uint32_t y = a[j]; if (!seen[y]) { seen[y] = 1; q[t++] = y; } }
    }
    uint64_t tp = 0, tl = 0, tk[128] = {0};
    snprintf(p, sizeof p, "%s/trusted-base.tsv", argv[1]); FILE *T = fopen(p, "w");
    for (uint64_t i = 0; i < t; i++) { uint32_t x = q[i]; if (d[x].project) tp++; else tl++; tk[(int)d[x].kind]++;
      fprintf(T, "%s\t%c\t%s\n", d[x].project ? "project" : "library", d[x].kind, d[x].name); }
    fclose(T);
    fprintf(R, "\n== trusted base of the %d statements (what the statements mean: definitions unfolded, proofs not)\n", nr);
    fprintf(R, "%llu declarations: %llu from the project, %llu from Mathlib/Lean; defs %llu, inductives %llu, theorems %llu, other %llu\n",
            (unsigned long long)t, (unsigned long long)tp, (unsigned long long)tl, (unsigned long long)tk['D'], (unsigned long long)tk['I'],
            (unsigned long long)tk['T'], (unsigned long long)(tk['O'] + tk['A'] + tk['Q']));
    fprintf(R, "project declarations in it:\n");
    for (uint64_t i = 0; i < t; i++) if (d[q[i]].project) fprintf(R, "  %c %s\n", d[q[i]].kind, d[q[i]].name);
    free(seen); free(q); }

  // ---------- duplicate theorem statements
  { uint64_t *key = malloc(8 * nd); uint32_t m = 0;
    for (uint32_t i = 0; i < nd; i++) if (d[i].kind == 'T') key[m++] = ((uint64_t)d[i].type_expr << 32) | i;
    qsort(key, m, 8, cmp_u64);
    snprintf(p, sizeof p, "%s/dups.tsv", argv[1]); FILE *T = fopen(p, "w");
    uint64_t groups = 0, extra = 0, pgroups = 0, pextra = 0, ngroups = 0, nextra = 0;
    for (uint32_t i = 0; i < m;) {
      uint32_t j = i; while (j < m && (key[j] >> 32) == (key[i] >> 32)) j++;
      if (j - i > 1) {
        int anyp = 0, named = 0;
        for (uint32_t k = i; k < j; k++) { uint32_t x = key[k] & 0xffffffff; if (d[x].project) anyp = 1; if (!autogen(d[x].name)) named++; }
        groups++; extra += j - i - 1; if (anyp) { pgroups++; pextra += j - i - 1; }
        if (anyp && named >= 2) { ngroups++; nextra += named - 1; }
        uint32_t x0 = key[i] & 0xffffffff;
        fprintf(T, "%u\t%llu\t%d", j - i, (unsigned long long)d[x0].tn, anyp);
        for (uint32_t k = i; k < j; k++) { uint32_t x = key[k] & 0xffffffff; fprintf(T, "\t%s%s", d[x].project ? "" : "[lib] ", d[x].name); }
        fprintf(T, "\n");
      }
      i = j;
    }
    fclose(T);
    fprintf(R, "\n== theorems with identical statements (same exported type, so equal up to bound-variable names)\n");
    fprintf(R, "%llu groups, %llu redundant copies overall; %llu groups touching the project (%llu copies); "
               "%llu groups with two or more hand-named project-side theorems (%llu redundant named copies)\n",
            (unsigned long long)groups, (unsigned long long)extra, (unsigned long long)pgroups, (unsigned long long)pextra,
            (unsigned long long)ngroups, (unsigned long long)nextra);
    free(key); }

  // ---------- hubs
  { uint32_t *ord = malloc(4 * nd); uint32_t m = 0; for (uint32_t i = 0; i < nd; i++) if (d[i].project) ord[m++] = i;
    // partial sort: top 200 by indeg
    snprintf(p, sizeof p, "%s/hubs.tsv", argv[1]); FILE *T = fopen(p, "w");
    for (int k = 0; k < 200 && k < (int)m; k++) {
      uint32_t best = k; for (uint32_t j = k + 1; j < m; j++) if (indeg[ord[j]] > indeg[ord[best]]) best = j;
      uint32_t tmp = ord[k]; ord[k] = ord[best]; ord[best] = tmp;
      fprintf(T, "%u\t%c\t%s\n", indeg[ord[k]], d[ord[k]].kind, d[ord[k]].name);
    }
    fclose(T); free(ord); }

  // ---------- dominator tree (Cooper, Harvey, Kennedy) from a virtual root over the whole graph
  uint32_t N = nd + 1, VR = nd; // virtual root index nd
  uint32_t *po = malloc(4 * N), *rpo_num = malloc(4 * N); uint32_t np = 0;
  { // iterative DFS postorder
    uint8_t *vis = calloc(N, 1); uint32_t *st = malloc(4 * N), *it = malloc(4 * N); uint32_t sp = 0;
    vis[VR] = 1; st[sp] = VR; it[sp] = 0; sp++;
    while (sp) {
      uint32_t x = st[sp - 1];
      uint32_t deg = x == VR ? (uint32_t)nr : fo[x + 1] - fo[x];
      if (it[sp - 1] < deg) {
        uint32_t y = x == VR ? roots[it[sp - 1]] : fa[fo[x] + it[sp - 1]]; it[sp - 1]++;
        if (!vis[y]) { vis[y] = 1; st[sp] = y; it[sp] = 0; sp++; }
      } else { po[np++] = x; sp--; }
    }
    free(vis); free(st); free(it);
  }
  for (uint32_t i = 0; i < N; i++) rpo_num[i] = UINT32_MAX;
  for (uint32_t i = 0; i < np; i++) rpo_num[po[i]] = i; // postorder number; root has the largest
  uint32_t *idom = malloc(4 * N); for (uint32_t i = 0; i < N; i++) idom[i] = UINT32_MAX; idom[VR] = VR;
  int changed = 1, rounds = 0;
  while (changed) {
    changed = 0; rounds++;
    for (int64_t k = (int64_t)np - 2; k >= 0; k--) { // reverse postorder, skipping the root
      uint32_t b = po[k], nid = UINT32_MAX;
      // predecessors: reverse edges, plus the virtual root for root decls
      int isroot = 0; for (int i = 0; i < nr; i++) if (roots[i] == b) isroot = 1;
      if (isroot) nid = VR;
      for (uint32_t j = ro[b]; j < ro[b + 1]; j++) {
        uint32_t pp = ra[j]; if (idom[pp] == UINT32_MAX) continue;
        if (nid == UINT32_MAX) { nid = pp; continue; }
        uint32_t f1 = pp, f2 = nid;
        while (f1 != f2) { while (rpo_num[f1] < rpo_num[f2]) f1 = idom[f1]; while (rpo_num[f2] < rpo_num[f1]) f2 = idom[f2]; }
        nid = f1;
      }
      if (idom[b] != nid) { idom[b] = nid; changed = 1; }
    }
  }
  // subtree sizes (decls and nodes): process in postorder (children before parents)
  uint64_t *sz = calloc(N, 8), *szn = calloc(N, 8);
  for (uint32_t i = 0; i < np; i++) { uint32_t x = po[i]; if (x != VR) { sz[x] += 1; szn[x] += d[x].tn + d[x].vn; } if (x != VR) { sz[idom[x]] += sz[x]; szn[idom[x]] += szn[x]; } }
  { // the dominator tree itself, for drawing: every node owning at least 0.005% of the proof
    snprintf(p, sizeof p, "%s/domtree.tsv", argv[1]); FILE *T = fopen(p, "w");
    fprintf(T, "%u\t%u\t%llu\t%llu\t%s\t%c\t%s\n", VR, VR, (unsigned long long)szn[VR], (unsigned long long)(np - 1), "root", 'R', "(the five theorems)");
    for (uint32_t i = 0; i < np; i++) { uint32_t x = po[i]; if (x == VR || szn[x] * 20000 < szn[VR]) continue;
      fprintf(T, "%u\t%u\t%llu\t%llu\t%s\t%c\t%s\n", x, idom[x], (unsigned long long)szn[x], (unsigned long long)sz[x],
              d[x].project ? "project" : "library", d[x].kind, d[x].name); }
    fclose(T); }
  if (getenv("XQ")) { // query: for each "group<TAB>name" line, the declaration's dominated share and its full closure
    FILE *Q = fopen(getenv("XQ"), "r"); snprintf(p, sizeof p, "%s/query.tsv", argv[1]); FILE *T = fopen(p, "w");
    uint32_t *stamp = calloc(nd, 4), *q = malloc(4 * nd); uint32_t st = 0;
    while (getline(&line, &cap, Q) > 0) {
      line[strcspn(line, "\n")] = 0; char *tab = strchr(line, '\t'); if (!tab) continue; *tab = 0; char *nm = tab + 1;
      int64_t x = nfind(nm); if (x < 0) continue;
      st++; uint64_t h = 0, t = 0, cn = 0, cp = 0; stamp[x] = st; q[t++] = x;
      while (h < t) { uint32_t y = q[h++]; cn += d[y].tn + d[y].vn; if (d[y].project) cp++;
        for (uint32_t j = fo[y]; j < fo[y + 1]; j++) { uint32_t z = fa[j]; if (stamp[z] != st) { stamp[z] = st; q[t++] = z; } } }
      fprintf(T, "%s\t%s\t%c\t%d\t%.4f\t%llu\t%llu\t%llu\t%.4f\n", line, nm, d[x].kind, d[x].project,
              rpo_num[x] == UINT32_MAX ? 0.0 : 100.0 * szn[x] / szn[VR], (unsigned long long)(rpo_num[x] == UINT32_MAX ? 0 : sz[x]),
              (unsigned long long)t, (unsigned long long)cp, 100.0 * cn / szn[VR]);
    }
    fclose(T); fclose(Q); }
  if (getenv("XQU")) { // union closure of every name in the file (second column)
    FILE *Q = fopen(getenv("XQU"), "r"); uint8_t *seen = calloc(nd, 1); uint32_t *q = malloc(4 * nd); uint64_t h = 0, t = 0, found = 0;
    while (getline(&line, &cap, Q) > 0) { line[strcspn(line, "\n")] = 0; char *tab = strchr(line, '\t'); char *nm = tab ? tab + 1 : line;
      int64_t x = nfind(nm); if (x < 0 || seen[x]) continue; seen[x] = 1; q[t++] = x; found++; }
    while (h < t) { uint32_t y = q[h++]; for (uint32_t j = fo[y]; j < fo[y + 1]; j++) { uint32_t z = fa[j]; if (!seen[z]) { seen[z] = 1; q[t++] = z; } } }
    uint64_t cn = 0, cp = 0, pn = 0, pall = 0; for (uint64_t i = 0; i < t; i++) { cn += d[q[i]].tn + d[q[i]].vn; if (d[q[i]].project) { cp++; pn += d[q[i]].tn + d[q[i]].vn; } }
    for (uint32_t i = 0; i < nd; i++) if (d[i].project) pall += d[i].tn + d[i].vn;
    fprintf(stderr, "union: %llu names found, closure %llu decls (%llu project), %.2f%% of all expression nodes, %.2f%% of the project's\n",
            (unsigned long long)found, (unsigned long long)t, (unsigned long long)cp, 100.0 * cn / szn[VR], 100.0 * pn / pall);
    fclose(Q); }
  fprintf(R, "\n== dominator tree (%d rounds): %u declarations reachable from the %d roots, %llu expression nodes\n",
          rounds, np - 1, nr, (unsigned long long)szn[VR]);
  { // top dominators among project decls (excluding the roots themselves)
    snprintf(p, sizeof p, "%s/dominators.tsv", argv[1]); FILE *T = fopen(p, "w");
    uint32_t *ord = malloc(4 * nd); uint32_t m = 0; for (uint32_t i = 0; i < nd; i++) if (d[i].project && rpo_num[i] != UINT32_MAX) ord[m++] = i;
    for (int k = 0; k < 300 && k < (int)m; k++) {
      uint32_t best = k; for (uint32_t j = k + 1; j < m; j++) if (szn[ord[j]] > szn[ord[best]]) best = j;
      uint32_t tmp = ord[k]; ord[k] = ord[best]; ord[best] = tmp; uint32_t x = ord[k];
      fprintf(T, "%.2f%%\t%.2f%%\t%llu\t%c\t%s\n", 100.0 * szn[x] / szn[VR], 100.0 * sz[x] / (np - 1), (unsigned long long)sz[x], d[x].kind, d[x].name);
    }
    fclose(T); free(ord); }
  { // spine: from the virtual root, follow the child with the most dominated expression nodes
    snprintf(p, sizeof p, "%s/spine.tsv", argv[1]); FILE *T = fopen(p, "w");
    // children lists via counting
    uint32_t *co = calloc(N + 1, 4); for (uint32_t i = 0; i < np; i++) { uint32_t x = po[i]; if (x != VR) co[idom[x] + 1]++; }
    for (uint32_t i = 0; i < N; i++) co[i + 1] += co[i];
    uint32_t *ca = malloc(4 * (uint64_t)co[N]), *cc = calloc(N, 4);
    for (uint32_t i = 0; i < np; i++) { uint32_t x = po[i]; if (x != VR) ca[co[idom[x]] + cc[idom[x]]++] = x; }
    uint32_t x = VR; int depth = 0;
    while (1) {
      uint32_t best = UINT32_MAX; for (uint32_t j = co[x]; j < co[x + 1]; j++) if (best == UINT32_MAX || szn[ca[j]] > szn[best]) best = ca[j];
      if (best == UINT32_MAX || szn[best] * 1000 < szn[VR]) break;
      fprintf(T, "%d\t%.2f%%\t%.2f%%\t%u\t%s\t%c\t%s\n", depth++, 100.0 * szn[best] / szn[VR], 100.0 * sz[best] / (np - 1),
              co[x + 1] - co[x], d[best].project ? "project" : "library", d[best].kind, d[best].name);
      x = best;
    }
    fclose(T); }
  // ---------- biggest proof terms in the project
  { snprintf(p, sizeof p, "%s/biggest.tsv", argv[1]); FILE *T = fopen(p, "w");
    uint32_t *ord = malloc(4 * nd); uint32_t m = 0; for (uint32_t i = 0; i < nd; i++) if (d[i].project) ord[m++] = i;
    for (int k = 0; k < 200 && k < (int)m; k++) {
      uint32_t best = k; for (uint32_t j = k + 1; j < m; j++) if (d[ord[j]].vn > d[ord[best]].vn) best = j;
      uint32_t tmp = ord[k]; ord[k] = ord[best]; ord[best] = tmp;
      fprintf(T, "%llu\t%llu\t%c\t%s\n", (unsigned long long)d[ord[k]].vn, (unsigned long long)d[ord[k]].tn, d[ord[k]].kind, d[ord[k]].name);
    }
    fclose(T); free(ord); }
  fclose(R);
  fprintf(stderr, "done\n");
  return 0;
}
