# The minified proof

Step 5 of the plan: cut the claimed Lean proof of the Riemann Hypothesis down to what its five main
theorems actually need, rebuild it, and check it again.

**Status: round 2 of the source is being written; round 1 failed in its first minute of building, for a reason now fixed** (see the [log](#log)). Nothing here is confirmed until it compiles and Tenet accepts its export. Nothing here is confirmed until it
compiles and Tenet accepts its export. The proof's own code is published without a license, so this
repository holds the method, the tools and the cut lists, not the minified source. Anyone can
regenerate it from the public mirror with the files in [`data/min`](../data/min).

## The numbers

| | Original | Minified | Change |
|---|---:|---:|---:|
| **Lines** (everything) | 17,374,242 | **13,850,849** | **−20.3%** |
| **Files** | 175,188 | **30,698** | **−82.5%** |
| Declarations in the source | 1,060,833 | **823,687** | −22.4% |
| Import lines | 909,823 | **71,440** | −92.1% |
| Declarations the kernel needs (from the export, with Mathlib) | 1,468,414 | **1,441,861** | −1.8% |
| Expression nodes the kernel checks | 100% | **97.2%** | −2.8% |

The minified source's other lines (12,189,756, not blank, not imports) include about 330,000 lines of
`section` / `end` wrappers added when files were merged (step 8); the proof content itself is
11.86 million lines, down from 14.62 million (−18.9%).

| Step | Lines after | Files after |
|---|---:|---:|
| Original | 17,374,242 | 175,188 |
| Exact cut, merged repeats, empty files dropped (steps 1 to 6) | 14,888,615 | 161,543 |
| Redundant imports removed (step 7) | 13,841,616 | 161,543 |
| Small files merged, then imports trimmed again (step 8) | **13,850,849** | **30,698** |

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
7. **Remove redundant imports.** An import is dropped when another import of the same file already brings
   it in, directly or not. Every file still sees exactly the same modules, so nothing about how the proof
   compiles changes. 935,081 import lines went.
8. **Merge small files** (the median file was 59 lines). Files in the same folder (so the same Lake library
   and its options) **and at the same depth in the import graph** are merged into bundle modules of at most
   25 files and 4,000 lines. Files at the same depth can't reach each other through any chain of imports,
   so no bundle can close an import cycle. Each file's text is wrapped in its own `section … end`, so its
   `open`, `variable`, `universe`, options and local notation stay with it; namespaces a file leaves open are
   closed first. Two files whose `private` names clash never share a bundle, and files using `#exit` are
   never merged. Every import of a merged file now points to its bundle. 146,388 files went into 15,543
   bundles; then redundant imports were trimmed again.

## What "minimal" means here, and what is left

- **No dead code:** every declaration that remains is needed by the five theorems, as far as the export
  can tell, apart from the instances and attributed declarations kept on purpose.
- **Not the shortest possible proof.** Proofs themselves weren't shortened. 4,335 declarations take half
  of the checking time (see [BUILD-STATUS.md](../BUILD-STATUS.md#research-on-the-export)); rewriting them
  is a different job.
- **Some repeats remain.** 63,943 copies had no usable twin (the chosen copy comes later in the build
  order, or the theorem's proof isn't a plain `:=`).
- **Wrappers:** merging files adds a `section … end` around each original file, about 330,000 lines in
  all. They keep each file's settings to itself; they are not proof content.

## What could still fail in the build

- A declaration that Lean needs only while building proofs, never in a finished one, and that isn't an
  instance or attributed. The build names it; it goes back and the build resumes.
- A merged proof where `apply … <;> assumption` doesn't close the goal (for example when Lean can't
  work out an argument by unification). Those proofs go back to their originals.
- An added import that changes how `simp` or instance search behaves in that file. Those imports go
  back too.
- A merged file that behaves differently inside a bundle (for example, a command that reads the module
  name). That file goes back out of its bundle.

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
| [`tools/trim_imports.py`](../tools/trim_imports.py) | removes imports another import already brings in |
| [`tools/merge_files.py`](../tools/merge_files.py) | merges same-folder, same-depth files into bundles |
| [`tools/xidx.c`](../tools/xidx.c), [`tools/xan.c`](../tools/xan.c) | index the export; `XSWAP=` recomputes what stays reachable after merges |

To regenerate the minified source from the public mirror at `8b83d5e` (Mathlib's import lists come from
`reach.py --dump-decls` run on its package; see the tools):

```bash
python3 tools/prune.py SRC <(gunzip -c data/min/kept-files.txt.gz) STEP1 <(gunzip -c data/min/cuts.json.gz) <(gunzip -c data/min/swaps.json.gz) <(gunzip -c data/min/imports.json.gz)
```

```bash
python3 tools/trim_imports.py STEP1/src LIB_DUMPS...
```

```bash
python3 tools/merge_files.py STEP1/src OUT/src && python3 tools/trim_imports.py OUT/src LIB_DUMPS...
```

## Log

All times UTC, 2026-11-22. Newest last.

- **06:19** Round 1 build started: 13,850,849 lines in 30,698 files.
- **06:20** First errors, in `Formalism/LocalToGlobal/NumberFieldFamilies/OwnStruct.lean`: `Unknown identifier copyAt`.
  The cause: instances and attributed declarations were kept on purpose, but what *they* depend on was not.
  An instance the proof never uses still referred to `copyAt`, which had been cut. Build stopped by hand.
- **06:30** Fix: keep the source-level dependencies of everything kept on purpose. That brings back about
  137,000 declarations (1,001,299 kept instead of 864,558), so this round will be bigger than round 1's
  numbers above. It's the safe version, built first so there is a version sure to compile. A later round will
  try cutting the instances the proof never uses, and their dependencies, and let the build say if any were needed.

