# Numbers

All counts are from scripts over the source text, not from a build. Reproduce them with
`tools/libstats.py` and `tools/check_fork.py`.

## Overall

| | Original | This fork | Kept |
|---|---|---|---|
| Lean files | 175,188 | 137,020 | 78% |
| Lines (including the 38 docstrings this fork adds) | 17,549,430 | 11,953,342 | 68% |
| Declarations, counted by keyword | 1,060,833 | 629,722 | 59% |
| Declarations, as the trace counts them | 1,137,512 | 631,251 | 55% |
| Docstrings | 1 | 39 | |
| Comments | 0 | 0 | |

The two declaration counts measure different things:

- **By keyword:** lines that start with `theorem`, `lemma`, `def`, `abbrev`, `structure`,
  `class`, `instance`, `inductive` or `opaque`.
- **As the trace counts them:** also structure fields, constructors and unnamed instances,
  each a separate node. This is the count the pruning uses.

## By library

Columns: files, lines and declarations (by keyword), each as original → fork.

| Library | Files | → | Lines | → | Kept | Decls | → | Kept |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `Development` | 141,928 | 113,971 | 12,374,591 | 9,170,134 | 74% | 692,591 | 451,628 | 65% |
| `Formalism` | 18,254 | 12,120 | 3,219,002 | 1,647,545 | 51% | 240,003 | 109,793 | 46% |
| `GroundTheory` | 8,507 | 5,723 | 1,127,645 | 613,758 | 54% | 75,058 | 34,796 | 46% |
| `ReciprocityTheory` | 3,845 | 2,952 | 566,861 | 375,780 | 66% | 36,395 | 22,915 | 63% |
| `CompanionTheory` | 2,027 | 1,855 | 196,245 | 165,076 | 84% | 11,767 | 8,782 | 75% |
| `PositivityTheory` | 449 | 284 | 55,579 | 24,829 | 45% | 4,746 | 1,627 | 34% |
| `Lemmata` | 167 | 111 | 9,399 | 5,742 | 61% | 251 | 159 | 63% |
| `Challenge` | 1 | 1 | 28 | 28 | 100% | 9 | 9 | 100% |
| `Supplements` | 3 | 1 | 25 | 33 | 132% | 4 | 4 | 100% |
| `BuildAid` | 5 | 0 | 25 | 0 | 0% | 0 | 0 | n/a |
| `Statements` | 1 | 1 | 17 | 31 | 182% | 4 | 4 | 100% |
| `Main` | 1 | 1 | 13 | 34 | 262% | 5 | 5 | 100% |
| **Total** | **175,188** | **137,020** | **17,549,430** | **12,002,990** | **68%** | **1,060,833** | **629,722** | **59%** |

Notes:

- `Main.lean` and `Statements.lean` grew because of the docstrings. Their theorems and
  definitions are unchanged.
- `Supplements` lost `MainTheoremsAll.lean` and `MainTheoremsCritical.lean`, which the proof
  doesn't need.
- `BuildAid` is gone. Its five files only added namespaces to Lean's deny list for library
  suggestions.

## Versions of this fork

| Commit | Trace | Declarations | Files | Lines |
|---|---|---|---|---|
| `4d5b160` | first trace (`reach.py`) | 705,207 | 142,620 | 12.9M |
| `da6aa5a` | tighter trace (`reach.py --v2`) | 631,251 | 137,019 | 12.0M |
| this commit | same as `da6aa5a`, plus documentation | 631,251 | 137,020 | 12.0M |

`check_fork.py` counts 137,020 files where the trace counts 137,019; the difference is the
mirror's `Challenge.lean`, which the fork keeps but `Main` never imports.

## How these compare

| | Lines |
|---|---|
| Mathlib at the pinned version (v4.33.1) | 2.29M |
| This fork | 12.0M (about 5.2 times Mathlib) |
| The original | 17.5M (about 7.7 times Mathlib) |
