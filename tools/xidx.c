// xidx: one pass over a lean4export NDJSON file (format 3.x). Writes, into OUTDIR:
//   decls.tsv   idx  kind  name  type_expr  type_nodes  value_nodes  n_type_edges  n_value_edges
//   edges.bin   uint32 triples (src decl, dst decl, flag) flag 1 = used in the type, 2 = in the value
// type_nodes/value_nodes are distinct expression nodes reachable from the declaration's type and its
// value (proof term, definition body, recursor rules): a proxy for how much a kernel has to look at.
// Usage: xidx EXPORT.ndjson OUTDIR
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

enum { E_LEAF = 0, E_APP, E_BIND, E_LET, E_MDATA, E_PROJ, E_CONST };
enum { D_THM = 1, D_DEF, D_OPAQUE, D_AXIOM, D_QUOT, D_IND };
static const char *DKIND[] = {"", "thm", "def", "opaque", "axiom", "quot", "inductive"};

static uint8_t *ek; static uint32_t *ea, *eb, *ec; static uint64_t ecap;
static uint32_t *npre; static char **nstr; static uint64_t ncap;
static uint32_t *name2decl;
typedef struct { uint8_t kind; uint32_t name; uint32_t *roots; uint8_t *rflag; uint32_t nroots; } Decl;
static Decl *decls; static uint64_t ndecl, dcap;

static void *xrealloc(void *p, size_t n) { void *q = realloc(p, n); if (!q) { perror("realloc"); exit(1); } return q; }
static void grow_e(uint64_t id) {
  if (id < ecap) return;
  uint64_t nc = ecap ? ecap : 1 << 20; while (nc <= id) nc *= 2;
  ek = xrealloc(ek, nc); ea = xrealloc(ea, nc * 4); eb = xrealloc(eb, nc * 4); ec = xrealloc(ec, nc * 4);
  memset(ek + ecap, 0, nc - ecap); ecap = nc;
}
static void grow_n(uint64_t id) {
  if (id < ncap) return;
  uint64_t nc = ncap ? ncap : 1 << 16; while (nc <= id) nc *= 2;
  npre = xrealloc(npre, nc * 4); nstr = xrealloc(nstr, nc * sizeof(char *));
  memset(nstr + ncap, 0, (nc - ncap) * sizeof(char *)); ncap = nc;
}

// ---- a tiny JSON scanner: records "key":integer pairs at any depth, plus the string under "str"
#define MAXF 4096
static char fk[MAXF][12]; static long long fv[MAXF]; static int fd[MAXF]; static int nf;
static char topkey[16]; static char strval[4096];
static void scan(const char *s) {
  nf = 0; topkey[0] = 0; strval[0] = 0;
  int depth = 0; char key[32]; int havekey = 0; int expect_val = 0;
  for (const char *p = s; *p; p++) {
    char c = *p;
    if (c == '{' || c == '[') { depth++; expect_val = 0; havekey = 0; continue; }
    if (c == '}' || c == ']') { depth--; expect_val = 0; continue; }
    if (c == ',') { expect_val = 0; havekey = 0; continue; }
    if (c == ':') { expect_val = 1; continue; }
    if (c == '"') {
      const char *q = p + 1; int n = 0; char buf[4096];
      while (*q && *q != '"') { if (*q == '\\' && q[1]) { if (n < 4094) buf[n++] = *q; q++; } if (n < 4094) buf[n++] = *q; q++; }
      buf[n] = 0; p = q;
      if (expect_val) { if (havekey && strcmp(key, "str") == 0 && depth == 2) strcpy(strval, buf); expect_val = 0; havekey = 0; }
      else { strncpy(key, buf, 31); key[31] = 0; havekey = 1;
        if (depth == 1 && !topkey[0] && strcmp(key, "ie") && strcmp(key, "in") && strcmp(key, "il")) { strncpy(topkey, key, 15); topkey[15] = 0; } }
      continue;
    }
    if (expect_val && ((c >= '0' && c <= '9') || c == '-')) {
      char *end; long long v = strtoll(p, &end, 10);
      if (havekey && nf < MAXF) { strncpy(fk[nf], key, 11); fk[nf][11] = 0; fv[nf] = v; fd[nf] = depth; nf++; }
      p = end - 1; expect_val = 0; havekey = 0; continue;
    }
  }
}
static long long get(const char *k, int depth) { for (int i = 0; i < nf; i++) if (fd[i] == depth && !strcmp(fk[i], k)) return fv[i]; return -1; }

static void add_decl(int kind) {
  if (ndecl == dcap) { dcap = dcap ? dcap * 2 : 1 << 16; decls = xrealloc(decls, dcap * sizeof(Decl)); }
  Decl *d = &decls[ndecl]; d->kind = kind; d->name = 0; d->nroots = 0;
  int nr = 0; for (int i = 0; i < nf; i++) if (!strcmp(fk[i], "type") || !strcmp(fk[i], "value") || !strcmp(fk[i], "rhs")) nr++;
  d->roots = malloc(nr * 4 + 4); d->rflag = malloc(nr + 1);
  int named = 0; long long lastname = -1;
  for (int i = 0; i < nf; i++) {
    if (kind == D_IND && !strcmp(fk[i], "numNested") && !named && lastname >= 0) { d->name = (uint32_t)lastname; named = 1; }
    if (!strcmp(fk[i], "name")) {
      uint32_t nm = (uint32_t)fv[i]; lastname = nm;
      if (!named && kind != D_IND) { d->name = nm; named = 1; }
      name2decl[nm] = (uint32_t)ndecl + 1;
    } else if (!strcmp(fk[i], "type")) { d->roots[d->nroots] = (uint32_t)fv[i]; d->rflag[d->nroots++] = 1; }
    else if (!strcmp(fk[i], "value") || !strcmp(fk[i], "rhs")) { d->roots[d->nroots] = (uint32_t)fv[i]; d->rflag[d->nroots++] = 2; }
  }
  ndecl++;
}

static void name_str(uint32_t n, char *out, size_t cap) {
  // build dotted name from the pre chain
  uint32_t chain[512]; int k = 0;
  while (n && k < 512) { chain[k++] = n; n = npre[n]; }
  size_t len = 0; out[0] = 0;
  for (int i = k - 1; i >= 0; i--) {
    const char *s = nstr[chain[i]] ? nstr[chain[i]] : "?";
    size_t l = strlen(s);
    if (len + l + 2 >= cap) break;
    if (len) out[len++] = '.';
    memcpy(out + len, s, l); len += l; out[len] = 0;
  }
}

int main(int argc, char **argv) {
  if (argc < 3) { fprintf(stderr, "usage: xidx EXPORT.ndjson OUTDIR\n"); return 2; }
  FILE *f = fopen(argv[1], "r"); if (!f) { perror(argv[1]); return 2; }
  grow_n(1 << 24); name2decl = calloc(1ull << 25, 4); uint64_t n2dcap = 1ull << 25;
  char *line = NULL; size_t cap = 0; ssize_t len; uint64_t lines = 0;
  while ((len = getline(&line, &cap, f)) > 0) {
    lines++;
    if ((lines & ((1 << 26) - 1)) == 0) fprintf(stderr, "  %llu lines, %llu decls\n", (unsigned long long)lines, (unsigned long long)ndecl);
    scan(line);
    long long ie = get("ie", 1), in = get("in", 1);
    if (in >= 0) {
      grow_n(in); if ((uint64_t)in >= n2dcap) { uint64_t nc = n2dcap; while (nc <= (uint64_t)in) nc *= 2; name2decl = xrealloc(name2decl, nc * 4); memset(name2decl + n2dcap, 0, (nc - n2dcap) * 4); n2dcap = nc; }
      long long pre = get("pre", 2); npre[in] = pre < 0 ? 0 : (uint32_t)pre;
      if (!strcmp(topkey, "str")) nstr[in] = strdup(strval);
      else { long long i = get("i", 2); char b[32]; snprintf(b, 32, "%lld", i); nstr[in] = strdup(b); }
      continue;
    }
    if (ie >= 0) {
      grow_e(ie);
      if (!strcmp(topkey, "app")) { ek[ie] = E_APP; ea[ie] = get("fn", 2); eb[ie] = get("arg", 2); }
      else if (!strcmp(topkey, "forallE") || !strcmp(topkey, "lam")) { ek[ie] = E_BIND; ea[ie] = get("type", 2); eb[ie] = get("body", 2); }
      else if (!strcmp(topkey, "letE")) { ek[ie] = E_LET; ea[ie] = get("type", 2); eb[ie] = get("value", 2); ec[ie] = get("body", 2); }
      else if (!strcmp(topkey, "mdata")) { ek[ie] = E_MDATA; ea[ie] = get("expr", 2); }
      else if (!strcmp(topkey, "proj")) { ek[ie] = E_PROJ; ea[ie] = get("struct", 2); }
      else if (!strcmp(topkey, "const")) { ek[ie] = E_CONST; ea[ie] = get("name", 2); }
      else ek[ie] = E_LEAF;
      continue;
    }
    if (get("il", 1) >= 0) continue;
    if (!strcmp(topkey, "thm")) add_decl(D_THM);
    else if (!strcmp(topkey, "def")) add_decl(D_DEF);
    else if (!strcmp(topkey, "opaque")) add_decl(D_OPAQUE);
    else if (!strcmp(topkey, "axiom")) add_decl(D_AXIOM);
    else if (!strcmp(topkey, "quot")) add_decl(D_QUOT);
    else if (!strcmp(topkey, "inductive")) add_decl(D_IND);
  }
  fprintf(stderr, "parsed %llu lines: %llu decls, %llu exprs (cap), names cap %llu\n",
          (unsigned long long)lines, (unsigned long long)ndecl, (unsigned long long)ecap, (unsigned long long)ncap);

  // ---- walk every declaration
  char path[4096];
  snprintf(path, sizeof path, "%s/decls.tsv", argv[2]); FILE *dt = fopen(path, "w");
  snprintf(path, sizeof path, "%s/edges.bin", argv[2]); FILE *eo = fopen(path, "wb");
  uint32_t *stamp = calloc(ecap, 4); uint32_t *dseen = calloc(ndecl + 1, 4); uint32_t st = 0;
  uint32_t *stack = malloc(sizeof(uint32_t) * (1 << 26)); uint64_t scap = 1 << 26;
  char nm[8192]; uint64_t total_edges = 0;
  for (uint64_t d = 0; d < ndecl; d++) {
    Decl *D = &decls[d]; uint64_t nodes[3] = {0, 0, 0}; uint64_t nedge[3] = {0, 0, 0};
    for (int flag = 1; flag <= 2; flag++) {
      st++; if (st == 0) { memset(stamp, 0, ecap * 4); memset(dseen, 0, (ndecl + 1) * 4); st = 1; }
      uint64_t sp = 0;
      for (uint32_t r = 0; r < D->nroots; r++) if (D->rflag[r] == flag) stack[sp++] = D->roots[r];
      while (sp) {
        uint32_t e = stack[--sp];
        if (e >= ecap || stamp[e] == st) continue;
        stamp[e] = st; nodes[flag]++;
        if (sp + 4 >= scap) { scap *= 2; stack = xrealloc(stack, scap * 4); }
        switch (ek[e]) {
          case E_APP: case E_BIND: stack[sp++] = ea[e]; stack[sp++] = eb[e]; break;
          case E_LET: stack[sp++] = ea[e]; stack[sp++] = eb[e]; stack[sp++] = ec[e]; break;
          case E_MDATA: case E_PROJ: stack[sp++] = ea[e]; break;
          case E_CONST: {
            uint32_t nmid = ea[e]; uint32_t t = nmid < n2dcap ? name2decl[nmid] : 0;
            if (t && t - 1 != d && dseen[t] != st) {
              dseen[t] = st; uint32_t rec[3] = {(uint32_t)d, t - 1, (uint32_t)flag};
              fwrite(rec, 4, 3, eo); nedge[flag]++; total_edges++;
            }
            break; }
          default: break;
        }
      }
    }
    name_str(D->name, nm, sizeof nm);
    fprintf(dt, "%llu\t%s\t%s\t%u\t%llu\t%llu\t%llu\t%llu\n", (unsigned long long)d, DKIND[D->kind], nm,
            D->nroots ? D->roots[0] : 0, (unsigned long long)nodes[1], (unsigned long long)nodes[2],
            (unsigned long long)nedge[1], (unsigned long long)nedge[2]);
    if ((d & ((1 << 17) - 1)) == 0) fprintf(stderr, "  walked %llu / %llu decls, %llu edges\n", (unsigned long long)d, (unsigned long long)ndecl, (unsigned long long)total_edges);
  }
  fclose(dt); fclose(eo);
  fprintf(stderr, "done: %llu decls, %llu edges\n", (unsigned long long)ndecl, (unsigned long long)total_edges);
  return 0;
}
