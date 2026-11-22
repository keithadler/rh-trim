# The minified proof

Step 5 of the plan: cut the claimed Lean proof of the Riemann Hypothesis down to what its five main
theorems actually need, rebuild it, and check it again.

**Status: the minified source is written but not built yet.** Nothing here is confirmed until it
compiles and Tenet accepts its export. The proof's own code is published without a license, so this
repository holds the method, the tools and the cut lists, not the minified source. Anyone can
regenerate it from the public mirror with the files in [`data/min`](../data/min).

## The numbers

| | Original | Minified | Change |
|---|---:|---:|---:|
| Files | 175,188 | **161,543** | −13,645 (−7.8%) |
| Declarations in the source | 1,060,833 | **823,687** | −237,146 (−22.4%) |
| Lines of content (no blank lines, no imports) | 14,621,954 | **11,858,344** | −2,763,610 (**−18.9%**) |
| Declarations the kernel needs (from the export) | 1,468,414 | **1,441,861** | −26,553 (−1.8%) |
| Expression nodes the kernel checks | 100% | **97.2%** | −2.8% |

The last two rows count Mathlib and Lean's core library too, which can't be minified here; the first
three count only the project's own source.

## How it was cut

1. **The exact list of what the proof uses.** The original was built and its five main theorems
   exported with `lean4export`. The export is Lean's own record of every declaration the theorems
   depend on, so nothing in it is guessed. The earlier source-level trace overestimated what could be
   cut (it missed real dependencies); this replaces it.
2. **Cut every source declaration that isn't in that list**, except instances and declarations with
   attributes (`@[simp]` and the like). Those steer how Lean builds proofs even when they never appear
   in a finished proof, so they all stay.
3. **Name check.** The source parser sometimes misreads a namespace. Any cut whose name, with an
   outer namespace added or removed, is a used name was restored (343 of them).
4. **Merge repeated theorems.** 96,661 project theorems repeat another theorem's statement exactly
   (equal up to the names of bound variables). For each group, one copy is chosen (the one earliest in
   the build order) and every other copy's proof is replaced by `by apply @_root_.<chosen> <;> assumption`.
   The theorem keeps its name and statement, so nothing that uses it changes. When the chosen copy isn't
   visible from a file, that file gets one import of the chosen copy's file, only ever pointing earlier
   in a fixed build order, so no import cycle can form. 64,046 proofs were replaced this way.
5. **Cut again.** Once those proofs are gone, whatever only they used is dead too: 26,553 more
   declarations.
6. **Drop empty files.** A file whose every declaration is cut, and which defines no notation, syntax,
   tactic, attribute, instance or export, is dropped; files that imported it import what it imported.

## What "minimal" means here, and what is left

- **No dead code:** every declaration that remains is needed by the five theorems, as far as the export
  can tell, apart from the instances and attributed declarations kept on purpose.
- **Not the shortest possible proof.** Proofs themselves weren't shortened. 4,335 declarations take half
  of the checking time (see [BUILD-STATUS.md](../BUILD-STATUS.md#research-on-the-export)); rewriting them
  is a different job.
- **Some repeats remain.** 63,943 copies had no usable twin (the chosen copy comes later in the build
  order, or the theorem's proof isn't a plain `:=`).
- **Import lines went up**, from 0.91 million to 1.33 million, because files that imported a dropped
  file now import what it imported. These are not proof content.

## What could still fail in the build

- A declaration that Lean needs only while building proofs, never in a finished one, and that isn't an
  instance or attributed. The build names it; it goes back and the build resumes.
- A merged proof where `apply … <;> assumption` doesn't close the goal (for example when Lean can't
  work out an argument by unification). Those proofs go back to their originals.
- An added import that changes how `simp` or instance search behaves in that file. Those imports go
  back too.

## Files

| File | What it is |
|---|---|
| [`data/min/kept-files.txt.gz`](../data/min/kept-files.txt.gz) | the 161,543 modules kept |
| [`data/min/cuts.json.gz`](../data/min/cuts.json.gz) | per module, the character ranges of the original source to cut |
| [`data/min/swaps.json.gz`](../data/min/swaps.json.gz) | per module, the proof ranges replaced and the one-line replacement |
| [`data/min/imports.json.gz`](../data/min/imports.json.gz) | per module, the imports added for merged theorems |
| [`data/min/merged-theorems.tsv.gz`](../data/min/merged-theorems.tsv.gz) | each merged theorem and the copy it now points to |
| [`tools/reach.py`](../tools/reach.py) `--keep-names` | turns the export's names into the cut list |
| [`tools/swapcross.py`](../tools/swapcross.py) | plans the merges |
| [`tools/finalize_cuts.py`](../tools/finalize_cuts.py) | the name check and the file drops |
| [`tools/prune.py`](../tools/prune.py) | writes the minified source from the original |
| [`tools/xidx.c`](../tools/xidx.c), [`tools/xan.c`](../tools/xan.c) | index the export; `XSWAP=` recomputes what stays reachable after merges |

To regenerate the minified source from the public mirror at `8b83d5e`:

```bash
python3 tools/prune.py SRC <(gunzip -c data/min/kept-files.txt.gz) OUT <(gunzip -c data/min/cuts.json.gz) <(gunzip -c data/min/swaps.json.gz) <(gunzip -c data/min/imports.json.gz)
```
