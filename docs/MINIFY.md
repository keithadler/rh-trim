# The smallest proof

<!-- STATUS:BEGIN -->
<div align="center">

**The smallest proof, live** · round 60 · 🔁 REPAIRING · updated 08:14 UTC Nov 23

<table><tr>
<td align="center" width="20%"><sub><b>SMALLER</b></sub><h2>8.2%</h2><sub>in lines, so far</sub></td>
<td align="center" width="20%"><sub><b>LINES</b></sub><h2>15.95M</h2><sub>was 17.37M</sub></td>
<td align="center" width="20%"><sub><b>FILES</b></sub><h2>~32,000</h2><sub>was 175,188 · after small files are merged</sub></td>
<td align="center" width="20%"><sub><b>THIS ROUND</b></sub><h2>2% built</h2><sub>3,214 of 172,489 files · 49 errors to repair</sub></td>
<td align="center" width="20%"><sub><b>TIME</b></sub><h2>25h 55m</h2><sub>and counting · since the first build, 06:19 UTC Nov 22 · 61 rounds</sub></td>
</tr></table>

<sub>Not confirmed until a round builds with 0 errors. Each round keeps what the last one's build said was missing, so the percentage can only go down from here. Updated every 2 minutes from the build machine. <a href="#log">Log of every round</a></sub>

</div>
<!-- STATUS:END -->

The goal: the same five theorems as the claimed Lean proof of the Riemann Hypothesis, with everything they
don't need removed, rebuilt with 0 errors, and checked by independent kernels (Tenet first, then the others).

**Status:** the minified source is building in automatic repair rounds (round 25 as of 16:38 UTC, 2026-11-22).
Nothing below is confirmed until a round builds with 0 errors. The proof has no license, so this repository
publishes the method, the tools and the cut lists, never the proof's code.

## Where it stands

| | Original | Now | Change |
|---|---:|---:|---:|
| **Lines** | 17,374,242 | **15,879,883** | **−8.6%** |
| Lines of proof content (not imports, not blank) | 14,621,954 | 13,675,749 | −6.5% |
| Import lines | 909,823 | 387,727 | −57% |
| Files | 175,188 | 172,315 (about 32,000 after merging, once it builds) | −1.7% |

**What the 8.6% is**, all of it dead code; no mathematics was simplified:

| Removed | Lines (approx.) |
|---|---:|
| ~90,700 unused declarations: 59,712 theorems and lemmas, 29,806 definitions, 610 abbreviations, 553 structures, 9 inductive types, 3 classes | 951,000 |
| 2,873 files that held nothing the proof needs | 183,000 |
| Redundant imports (another import already brings them in) | 522,000 |
| 43,070 repeated theorems now point to an identical twin instead of carrying their own proof | small |

The categories overlap slightly (dropped files had imports too).

## What it means

- **It's still about 7 times the size of Mathlib**: 15.9M lines against Mathlib's 2,293,877 lines in 8,311 files
  (the version this proof builds on).
- **For kernels, almost nothing changes.** A kernel checks only what the five theorems use, 1,468,414 declarations
  in the export, and dead code was never in that set. After the merges, 99.7% of the same expression nodes still
  need checking. Tenet checks the original in 1 hour; Lean's own kernel is single-threaded and takes many hours.
  What minifying saves is build time and reading, not kernel time.
- **The proof isn't big because of waste; it's big because of what it uses.** A real reduction needs a shorter
  route through the mathematics (below).

## How it's cut

1. **What the theorems use.** The original was built and its five main theorems exported with `lean4export`: Lean's
   own record of every declaration their finished proofs use.
2. **What the kept code mentions.** Tactics name lemmas a finished proof may never use (`simp [foo]` needs `foo` to
   exist). So everything the kept code mentions in its source is kept too, and every instance and attributed
   declaration with its dependencies.
3. **Repeated theorems.** When several theorems have identical statements and one is already visible from another's
   file, the second's proof becomes `by apply @_root_.<twin> <;> assumption`. Name and statement stay, so nothing that
   uses it changes.
4. **Empty files dropped**, and **redundant imports removed** (every file still sees exactly the same modules).
5. **Build and repair, automatically.** Each round's errors are fed back: names the build reports missing are kept;
   files that fail for other reasons go back to their original text. Lake rebuilds only what changed.
6. **Merge small files** once a round builds clean: same folder, same depth in the import graph (so no import cycle
   can form), each file wrapped in its own `section … end`.

## What didn't work

- **Cutting by the export alone** (round 1, 13.85M lines, −20.3%): the export lists what finished proofs use, not
  what tactics name, and kept instances lost their dependencies. Rounds 1 and 2 failed in minutes.
- **Adding imports to merge more repeats** (24,021 more merges): the extra names in scope made short names in
  untouched files ambiguous, and the repair loop stalled on the same errors for three rounds. Removed in round 25.
  They can come back one shared module at a time, each checked for ambiguity.
- **The very first, source-level reduction** in this repository (12.0M lines) missed real dependencies and doesn't
  build; it's kept only as history.

## More ways to make it smaller, measured

None applied yet. Measured from the source's reference graph and the export:

| Strategy | Size | Risk |
|---|---|---|
| **Aggressive cut**: keep instances and attributed declarations only if the export uses them | 53,516 declarations, ~5% | medium: an unused instance can still steer `simp` or instance search |
| **Merges through a shared module** instead of extra imports | the 24,021 merges dropped above, plus 98,375 with no visible twin | medium |
| **Inline single-use lemmas** | 391,912 lemmas (47% of those kept) are used by exactly one other declaration | low per lemma; far fewer declarations, few lines |
| **`…Statement` wrappers** | 3,197 kept; unfolding them exposes more exact repeats | low |
| **`_alt` pairs** where the original also survives | 1,726 pairs | needs a look at each |

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

All times UTC, 2026-11-22.

- **06:19** Round 1 (exact cut from the export, 13.85M lines) fails in its first minute: a kept instance needs
  `copyAt`, which was cut. Instances must keep their dependencies.
- **06:27 to 06:36** Round 2 fails with hundreds of errors: tactics name lemmas that finished proofs never use. From
  round 3 on, everything the kept code mentions is kept, and the build runs **unmerged** so each error points at an
  original file.
- **06:42 onward** The automatic repair loop takes over (every 20 minutes, or sooner when errors settle).
- **07:41 to 16:28** Rounds 5 to 24. Errors per round fall from 2,585 toward a few hundred. Two bugs fixed on the way:
  Lean diagnostics containing `source:` confused my round detection (12:28), and rounds 22 to 24 stalled on
  ambiguity caused by added imports (16:30).
- **16:38** Round 25: merges only to already-visible twins, no imports added. 15,879,883 lines (−8.6%). After 10
  minutes it had 34 errors, against hundreds in the stalled rounds.
- Spot interruptions at about 06:50, 07:15, 11:06 and 15:50, each recovered automatically.

## Files

| File | What it is |
|---|---|
| [`data/min/`](../data/min) | cut lists, merged theorems (updated as rounds progress) |
| [`tools/reach.py`](../tools/reach.py) `--keep-names --extra-names --revert-files` | the cut list from the export, the build's reports and reverted files |
| [`tools/swapcross.py`](../tools/swapcross.py) | plans the merges of repeated theorems (`NOIMPORT=1`: never add an import) |
| [`tools/finalize_cuts.py`](../tools/finalize_cuts.py), [`tools/prune.py`](../tools/prune.py), [`tools/trim_imports.py`](../tools/trim_imports.py) | name check, file drops, writing the source, import trimming |
| [`tools/repair.py`](../tools/repair.py), [`tools/auto-repair.sh`](../tools/auto-repair.sh), [`tools/min-round.sh`](../tools/min-round.sh) | the automatic repair loop |
| [`tools/merge_files.py`](../tools/merge_files.py), [`tools/merge-phase.sh`](../tools/merge-phase.sh) | merging small files, with its own repair loop |
| [`tools/xidx.c`](../tools/xidx.c), [`tools/xan.c`](../tools/xan.c) | index the export; dominator tree, closures, `XSWAP=` reachability after merges |
- **23:16 to 00:52** Rounds 39 to 44. Two more causes found and fixed, each of which made rounds repeat the same
  errors: (1) cutting every declaration of a namespace breaks any `open` of it, and the failed `open` takes every
  other name on that line down too; the repair now keeps one declaration of such a namespace, chosen from what the
  failing file actually imports. (2) A parser bug: declarations written with universe parameters on the name
  (`theorem foo.{u, v} : …`, 558 of them) were recorded as `foo.` and so looked unused. Fixed; the source's reference
  graph is being rebuilt from scratch so references to them connect again.
- The repair loop now stops by itself when a round has nothing new to keep, instead of repeating; and it copies only
  the current round's part of the build log (the full log passed 1.5 GB).

