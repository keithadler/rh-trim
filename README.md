# rh-trim: the smallest version of the claimed Lean proof of RH

On 2026-11-20 Levent Alpöge announced a proof of the Riemann Hypothesis, and of GRH for
Dirichlet L-functions, found working with Claude and published as Lean 4 code
([announcement](https://alpo.ge/remark.pdf)): 175,188 files and 17.4 million lines.

**Our focus is the smallest proof:** the same five theorems, with everything they don't need
removed, rebuilt and checked by independent kernels, including three written from scratch (Tenet
in C#, tenet-hs in Haskell, tenet-jvm).

## Where it stands

| | Files | Lines | Status |
|---|---:|---:|---|
| The original | 175,188 | 17,374,242 | ✅ built on AWS: 0 errors, no `sorry` ([how](docs/BUILD-ORIGINAL.md)) |
| What the theorems use | 1,468,414 declarations (with Mathlib) | | ✅ exported; only Lean's 3 standard axioms |
| **The minified proof** | **161,543** (−7.8%) | **14,888,615** (−14.3%; −18.9% of content lines) | 🔵 source written, **not built yet** ([how](docs/MINIFY.md)) |

**Kernel checks so far:** Tenet accepts the whole original proof (1,468,414 declarations, 0 failed,
1 h). Live results and the research on the proof's structure: [BUILD-STATUS.md](BUILD-STATUS.md).

**How the minified proof is made** ([details](docs/MINIFY.md)):

1. **Exact cut.** The original's export is Lean's own record of what the five theorems use. Every
   source declaration not in it is cut, except instances and attributed declarations, which steer
   how Lean builds proofs.
2. **Merged repeats.** 64,046 theorems repeat another theorem's statement exactly; each now points to
   one copy instead of carrying its own proof, and what only those proofs used is cut too.
3. **Empty files dropped**, with their imports passed on.

**Next, to make it smaller still:**

- **Redundant imports removed**: an import another import already brings in (running now).
- **Small files merged** into modules of about 25 files each, folder by folder (the median file is
  59 lines).
- Then the **build**, the export of the minified proof, and **Tenet's check**, then the other kernels.

Later rounds: the 63,943 repeats that still can't point to a twin, near-identical statements,
lemmas used only once, and the 4,335 declarations that take half of the checking time.

The proof has no license, so this repository publishes the method, the tools and the cut lists,
never the proof's code. Anyone can regenerate the minified source from the public mirror
([command](docs/MINIFY.md#files)).

<details><summary><b>History: the first, source-level reduction was wrong</b></summary>

The first reduction came from reading source text, and building it on AWS showed it missed real
dependencies (dangling `open … in` prefixes, Mathlib-class instances, global theorems mistaken for
local names, dot notation). Fixed, that trace could only safely cut about 9%. So the original was
built instead, and its export now gives the exact list. `make-fork.sh` below reproduces that early
reduction byte for byte, but **it does not build**; don't spend machine time on it.

</details>

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

**To build the original proof yourself,** follow [docs/BUILD-ORIGINAL.md](docs/BUILD-ORIGINAL.md).
One script, `build-original.sh`, did it for us on one AWS Spot `m6a.48xlarge`: about 21 hours and
about $35, all 175,187 files, 0 errors. Build only on a throwaway machine, because compiling Lean
runs code. (The reduced version's guide, [docs/BUILD.md](docs/BUILD.md), builds a reduction we
know drops real dependencies; it is kept for the record.)

To help build the *original*, join the distributed replay at
[rohanarun/alpoge-rh-replay](https://github.com/rohanarun/alpoge-rh-replay).

## How much smaller, and why (superseded: see [docs/MINIFY.md](docs/MINIFY.md))

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
| `build-linux.sh` | builds it on a Linux cloud machine, network cut off, timestamped log |
| `tools/progress.sh`, `tools/missing.py` | build rate and time left; missing names mapped to the original |
| `data/kept-files.txt.gz` | the 137,019 modules the trace keeps |
| `data/cuts.json.gz` | the byte ranges of the 216,245 declarations cut from those modules |
| `data/expected-tree.txt` | the fingerprint (sha256 over every path and file) of the result |
| `data/replay-map.tsv.gz` | every module of the [distributed replay](https://github.com/rohanarun/alpoge-rh-replay), by its ID, with its status here: dropped, trimmed, changed, identical, and whether its compiled file is reusable |
| `tools/reach.py` | the dependency trace (about 17 minutes over the whole proof) |
| `tools/prune.py`, `check_fork.py`, `trim_main.py`, `add_docs.py` | the steps `make-fork.sh` runs |
| `tools/tree_hash.py`, `libstats.py`, `closure.py`, `org_stats.py` | fingerprint, counts, import closures, code statistics |
| `tools/sandbox-macos.sb` | a macOS sandbox profile for building safely |
| `docs/` | build guide, proof map, literature list, method, checking guide, numbers |
| `.github/ISSUE_TEMPLATE/build-report.yml` | the build-report form |

## License

The tools, data and documentation in this repository are Apache-2.0. That license covers this
repository's own files only, not the proof, whose author has not licensed it.
