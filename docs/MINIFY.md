# The minified proof

<!-- STATUS:BEGIN -->
<div align="center">

**The smallest proof, live** · round 6 · 🔁 REPAIRING · updated 08:21 UTC Nov 22

<table><tr>
<td align="center" width="20%"><sub><b>SMALLER</b></sub><h2>10.2%</h2><sub>in lines, so far</sub></td>
<td align="center" width="20%"><sub><b>LINES</b></sub><h2>15.60M</h2><sub>was 17.37M</sub></td>
<td align="center" width="20%"><sub><b>FILES</b></sub><h2>~32,000</h2><sub>was 175,188 · after merging. Building unmerged (172,271) first, so each error points at an original file</sub></td>
<td align="center" width="20%"><sub><b>THIS ROUND</b></sub><h2>2% built</h2><sub>3,252 of 172,271 files · 451 errors to repair</sub></td>
<td align="center" width="20%"><sub><b>TIME</b></sub><h2>2h 01m</h2><sub>and counting · since the first build, 06:19 UTC Nov 22 · 6 rounds</sub></td>
</tr></table>

<sub>Not confirmed until a round builds with 0 errors. Each round keeps what the last one's build said was missing, so the percentage can only go down from here. Updated every 2 minutes from the build machine. <a href="#log">Log of every round</a></sub>

</div>
<!-- STATUS:END -->

Step 5 of the plan: cut the claimed Lean proof of the Riemann Hypothesis down to what its five main
theorems actually need, rebuild it, and check it again.

**Status: building, with automatic repair rounds** (see the [log](#log)). Each round fixes what the previous one's build reported; it stops when a round builds with 0 errors. Nothing here is confirmed until it compiles and Tenet accepts its export. Nothing here is confirmed until it
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

## More ways to make it smaller, measured

Measured from the source's reference graph and the export's name lists (2026-11-22, during a Spot interruption),
against the round 4 baseline of 1,022,556 kept declarations. None of these is applied yet.

| Strategy | What it would remove | Size | Risk |
|---|---|---:|---|
| **Aggressive cut**: keep instances and attributed declarations only if the export uses them | 53,516 declarations | ~5% of declarations | medium: an unused instance can still steer `simp` or instance search; the build will say |
| **Inline single-use lemmas** into the one proof that uses them | 391,912 lemmas are used by exactly one other declaration (47% of those kept) | far fewer declarations, few lines (a lemma becomes a `have` with the same statement) | low per lemma, but a big mechanical rewrite |
| **`_alt` pairs** where the original also survives | 1,726 pairs (4,378 `_alt` declarations kept) | small | needs a look at each pair |
| **`…Statement` wrappers** (a named proposition and a theorem proving it) | 3,197 kept | small directly; unfolding them can expose more exact repeats to merge | low |
| **The 63,943 repeats with no usable twin** (the chosen copy comes later in the build order) | their proofs, plus what only those use | up to a few % of proof content | medium: means moving lemmas into shared files |

Order of play: finish the safe build first (it's the baseline every other round is checked against), then the
aggressive cut, then the repeats, then inlining.

## Next track: searching for a shorter route

Everything above removes what the proof doesn't need. The next question is whether the proof needs to go the
way it goes: is there a **shorter route to the same five theorems**, using pieces the proof already contains
or that Mathlib already has? Each step below can be measured from the export before anything is rewritten.

1. **Cheapest twin, not first twin.** Where several theorems prove the same statement, keep the one whose proof
   needs the least (smallest dependency closure), not just the earliest one. Its alternatives, and whatever only
   they use, can then go.
2. **Side routes to the key claim.** Seven theorems conclude `EveryCharacter`; the proof uses a chain of five, and
   two (`plugAll`, `everyE₂`) are side routes it doesn't take. Export them and measure what each needs: if a side
   route is cheaper than the chain, rewire the proof through it.
3. **Cheaper proofs of the heavy steps.** The dominator tree names the lemmas that own most of the proof
   (`everyCharacter_of_row` 77%, the literature step 67%, the theta-integral step 43%). For each, look for another
   lemma in the proof or in Mathlib that proves the same statement, or a stronger one, with less underneath.
4. **Generality the argument doesn't use.** p-adic Hodge theory takes about 19% of the checking time. Check whether
   the proof uses those results in full, or only a special case that has a much shorter proof.
5. **Compare with the paper.** Alpöge's outline names the new idea (Stepanov's method via theta lifts, positivity
   in the explicit formula) and the published theory it rests on. Where the formalization takes a longer road than
   the outline, that's a candidate for a shorter one.

Steps 1 to 3 are mechanical and measured; steps 4 and 5 need mathematical judgment and will say so.

**First measurement (step 2), 2026-11-22.** The side routes `plugAll` and `everyE₂` turn out to be conditional: like
the last link of the main chain, they need a `Green` property and the window bound `VWin` as inputs. So switching
routes alone saves nothing. What each link of the chain needs (share of the whole proof's expression nodes, to state
and prove that link, with its inputs taken as hypotheses):

| Link | Needs | Owns alone |
|---|---:|---:|
| `allChi`, `everyCharacter` (the key claim) | 100% | 99.35% |
| `everyCharacter_of_row` | 93.97% | 77.17% |
| `every_character_of_literature_of_vWin` | 84.17% | 66.98% |
| `every_character_of_theta_integrals_local_matching` | 62.26% | 43.21% |
| `vwin_of_row` (the window bound) | 22.87% | 7.98% |
| `every_character_of_green_v_win` (the last step) | **6.58%** | 1.25% |
| `green_of_regular` (the `Green` input) | **0.33%** | 0.00% |

The argument from `Green` and the window bound to every character is small (6.6%); nearly all the weight is in
supplying the inputs each link takes (the row, the literature results, theta integrals and local matching). That is
where a shorter route would have to come from: meeting one of those hypotheses more cheaply.

**Second measurement: where the inputs come from.** The key claim takes one unconditional input, a `Row0b` statement
about Galois representations (`galoisLocalGlobalStrong_recParameter`); the links above rebuild everything else from
that row plus a local Langlands existence result. Five pieces own about 60% of the proof outright (the rest is
shared foundations):

| Piece | What it supplies | Needs | Owns alone |
|---|---|---:|---:|
| `nonempty_hyps_definite_side_of_closed_bound` | hypotheses on the definite side, from a closed bound (theta correspondence) | 61.0% | **37.75%** |
| `vwin_of_row` | the window bound, from the Galois row | 22.9% | 7.98% |
| `topCovolSlim2_use_alt_alt` | a covolume bound, through resolution of singularities and principalisation in characteristic zero | 20.9% | 6.90% |
| `galoisLocalGlobalStrong_recParameter` | the Galois input `Row0b` | 22.8% | 6.03% |
| `every_character_of_green_v_win` | the final argument | 6.6% | 1.25% |

So the biggest target for a shorter route is the definite-side step (38% alone), and a clear "generality" question is
the covolume bound: it uses resolution of singularities (Hironaka-type results) in full generality, 7% alone; if the
argument needs only a special case, that part may have a much shorter proof. Both are mathematical questions, not
mechanical ones.

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
- **06:27** Round 2 source written and its build started: **15,445,263 lines (−11.1%) in 32,034 files (−81.7%)**.
  1,001,299 of 1,137,512 source declarations kept; 64,611 repeated theorems point to one copy; 527,297 redundant
  import lines removed, then 155,333 files merged into 16,315 bundles. (The table above still shows round 1's
  numbers, which didn't build; it will show the version that builds.)
- **06:30** Round 2 stopped after 52, then 322 errors. The lesson: Lean's export lists what a *finished* proof
  uses, but a tactic like `simp [foo]` must name `foo` even when the finished proof never uses it. So the cut
  must also keep everything the kept code **mentions** in its source.
- **06:36** Round 3: keeps the export's declarations plus everything their source mentions: 1,022,429 of
  1,137,512 declarations. Built **unmerged** (172,254 files, 15,565,484 lines) so each error points at an
  original file; small files get merged once a round builds clean.
- **06:41** Round 3's errors were in 14 files, nearly all `Unknown identifier` for names the source parser had
  misread (an outer namespace). Repair: keep every declaration whose name ends the same way; where nothing
  matches, keep the file that uses it as it was.
- **06:42** Round 4 started (15,567,987 lines). From here an automatic loop takes over: when a round's errors
  stop growing, it repairs them and starts the next round; Lake rebuilds only the files that changed.
- **06:50** Time is tracked from the first build (06:19): the counter at the top shows the clock, and
  [the status page](../BUILD-STATUS.md) lists every round with its start, size and error count. When a round builds
  with 0 errors, the clock stops there.
- **Then, automatically: step 2, merging small files.** The clean unmerged source is kept, merged into bundles
  (same folder, same import depth, at most 25 files), and built. A bundle that fails has its files taken back
  out of bundling and the build resumes, until the merged version builds clean too.
- **06:50 to 07:01** A sixth Spot interruption, 11 minutes. The machine came back by itself and the round 4 build
  resumed where it stopped. While it was down, the other strategies were measured (see
  [More ways to make it smaller](#more-ways-to-make-it-smaller-measured)).
- **07:15** The repair loop now also repairs every 20 minutes while a round has errors, not only when its errors
  stop growing: round 4 kept finding new errors as it built further, and each restart rebuilds only the files it
  changes.
- **07:1x to 07:22** A seventh Spot interruption. The build resumed by itself; round 4 had 5,462 files built at 07:23.

