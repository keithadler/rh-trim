# rh-trim: the claimed Lean proof of RH, reduced to what it needs

On 2026-11-20 Levent Alpöge announced a proof of the Riemann Hypothesis, and of GRH for
Dirichlet L-functions. He found it working with Claude, and published it only as Lean 4 code
([announcement](https://alpo.ge/remark.pdf)): 175,188 files and 17.5 million lines.

This repository builds a **reduced version**: the same proof with everything it never uses
cut out. It is **about a third smaller**, and it documents how the proof fits together.

> **If you are building the original, please build this too and
> [share your results](../../issues/new?template=build-report.yml).** Machine, time, errors in
> full, checker verdicts. The reduced version has **not been compiled yet**, so every report helps.

## Get it

```bash
git clone https://github.com/keithadler/rh-trim && cd rh-trim
```

```bash
./make-fork.sh ../rh-reduced
```

This clones the public byte-exact mirror
[Deicyde/riemann-hypothesis](https://github.com/Deicyde/riemann-hypothesis) at a pinned
commit. It applies the reduction (text edits only), and checks the result byte for byte
against a published fingerprint. That takes about 2 minutes plus the 1.7 GB clone. Nothing
is compiled or run.

**Then build it only inside a sandbox: compiling Lean runs code.** See
[docs/CHECKING.md](docs/CHECKING.md).

## How much smaller, and why

| | Original | Reduced | Kept |
|---|---|---|---|
| Lean files | 175,188 | 137,020 | 78% |
| Lines | 17.5 million | 12.0 million | 68% |
| Declarations | 1,137,512 | 631,251 | 55% |

- **A dependency trace** follows every name the five main theorems use, starting from
  `Main.lean`. 45% of declarations are never reached by anything the proof needs, and they
  are cut.
- **Empty files are dropped.** Files left with nothing needed go away, and imports are rewired
  so every remaining file still sees every remaining file it saw before.
- **No surviving line of proof is changed.** The only additions are 38 docstrings on the key
  chain, each marked "(Added in this fork; not in the original.)".

**Caveat:** the trace reads source text. It can't see lemmas `simp` uses without naming them,
or notation, so the first build may report a few missing pieces. Each error names the piece.
Method, limits and mistakes made along the way: [docs/PRUNING.md](docs/PRUNING.md).
Per-library numbers: [docs/NUMBERS.md](docs/NUMBERS.md).

## What the proof looks like inside

```
five theorems ← short textbook arguments over Mathlib ← ONE KEY CLAIM ← Galois representations ← theta lifts
```

- **The key claim:** no Dirichlet L-function vanishes right of `Re s = 1/2`. RH and the GRH
  statements follow from it by the functional equation, in a few short files.
- **The front end is clean.** In the original, those front-end files compile on Lean 4.33.1,
  and lean-linter 0.5.4 finds nothing in them (18 checks).
- **Where the key claim comes from:** it is assembled from Galois representations attached to
  polarized cuspidal representations. The project derives those from **theta lifts**, rather
  than from the geometry of Shimura varieties.
- **Nothing from the literature is assumed:** the 162 formal statements of published results
  are proved inside the project. See [docs/LITERATURE.md](docs/LITERATURE.md).
- **Seven theorems conclude the key claim.** Five form the one chain the proof uses; two are
  unused side routes.

Layer by layer, with files: [docs/PROOF-MAP.md](docs/PROOF-MAP.md).

## What this repository is not

- **It is not the proof's code.** The original was published without a license, so no Lean
  source from it is redistributed here. `make-fork.sh` makes your copy locally, from the public
  mirror.
- **It is not a verification.** Nothing here says whether the mathematics is right. The
  mirror's team is judging the original with Lean's kernel and four outside checkers.

## Contents

| Path | What it is |
|---|---|
| `make-fork.sh` | rebuilds the reduced version from the mirror and checks its fingerprint |
| `data/kept-files.txt.gz` | the 137,019 modules the trace keeps |
| `data/cuts.json.gz` | the byte ranges of the 216,245 declarations cut from those modules |
| `data/expected-tree.txt` | the fingerprint (sha256 over every path and file) of the result |
| `tools/reach.py` | the dependency trace (about 17 minutes over the whole proof) |
| `tools/prune.py`, `check_fork.py`, `trim_main.py`, `add_docs.py` | the steps `make-fork.sh` runs |
| `tools/tree_hash.py`, `libstats.py`, `closure.py`, `org_stats.py` | fingerprint, counts, import closures, code statistics |
| `tools/sandbox-macos.sb` | a macOS sandbox profile for building safely |
| `docs/` | proof map, literature list, method, checking guide, numbers |
| `.github/ISSUE_TEMPLATE/build-report.yml` | the build-report form |

## License

The tools, data and documentation in this repository are Apache-2.0. That license covers this
repository's own files only, not the proof, whose author has not licensed it.
