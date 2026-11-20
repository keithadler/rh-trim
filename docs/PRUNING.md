# How the fork was pruned

The goal: keep only what the five theorems in `Main.lean` need, without compiling anything.
Everything here works on the source text. No code from the project was run, and the scripts
are in `tools/`.

## Step 1: a dependency trace (`tools/reach.py`)

**Pass 1, declarations.** Every `theorem`, `lemma`, `def`, `abbrev`, `structure`, `class`,
`instance`, `inductive`, `opaque` and `axiom` in all 175,188 files gets a full name. The
name is built from the enclosing `namespace` blocks, with `_root_.` prefixes honored.

- Structure fields, constructors and `.mk` also become names.
- Unnamed instances get a synthetic name.
- Each declaration's text span runs from its first attribute line to the next line that
  starts in column 0.

**Pass 2, references.** Every identifier in a declaration's text is resolved roughly the way
Lean does it. The candidates are:

- the name as written;
- the name under each enclosing namespace, and under each prefix of the declaration's own
  name;
- the name under each `open`ed namespace;
- for a qualified name that isn't a declaration, its prefix, which covers fields and
  constructors.

Two refinements (`--v2`):

- **Local names are skipped.** Names bound inside the declaration don't count, so a variable
  `h` or `key` doesn't drag in a global `key`. That covers binders `(x : T)`, `fun x =>`,
  `intro`, `rintro`, `obtain`, `rcases … with`, `have`, `let`, `set`, `∀`/`∃`, match arms and
  `⟨a, b⟩` patterns.
- **Duplicated names resolve through imports.** 4,157 names are declared in more than one file;
  Lean allows that when no file imports both. For those, only the copies the current file can
  see through its imports count. A bitset over the 3,373 files involved records this.

**Reachability.** The trace starts at the five theorems *in `Main.lean`*. Starting by name
alone found the wrong `riemannHypothesis` in the first attempt, because the name is
duplicated. From there it follows references. An instance in a reached file is added once its
class is reached, since type-class search can only use instances of classes that appear.
Repeat until nothing changes.

**Result:** 631,251 of 1,137,512 declarations, in 137,019 files.

Pass 2 takes about 17 minutes on an M2 with 16 GB. Its result is cached in
`$RH_TRIM_OUT/reach-cache-<hash>-v2.pkl`, so `--cached` reruns take about 90 seconds.

## Step 2: writing the fork (`tools/prune.py`)

- **Files with nothing reached are dropped.**
- **Imports are rewired.** A kept file's import of a dropped file is replaced by the kept files
  the dropped file reached through its own imports, recursively. So each kept file can still
  see exactly the kept files it saw before.
- **Unneeded declarations are cut** from kept files: 216,245 spans, using the spans from pass 1.
- **No surviving line of proof is changed.**

## Step 3: cleanup and checks (`tools/check_fork.py`)

- **Dangling attributes removed.** 174 `attribute [...] name` commands named a cut declaration.
  Those commands are removed.
- **Imports checked.** Every import resolves, either to a file in the fork or to Mathlib or
  another package.
- **Reachability checked.** `Main` reaches every proof file through imports.

## Step 4: Main's imports and documentation (`tools/trim_main.py`, `tools/add_docs.py`)

`Main.lean` keeps only the two imports its theorems need.

38 docstrings on the key chain, each ending "(Added in this fork; not in the original.)".
Comments only; no proof text changes. See [PROOF-MAP.md](PROOF-MAP.md).

## What this method cannot see

Everything here is a reading of text. The trace can still be wrong in both directions.

### It may keep too much

- **Dot notation.** `h.foo` matches by prefix rules, not by `h`'s type.
- **Local-name detection is pattern-based**, so some local names are still matched as globals.

### It may keep too little (a build would report these)

- **Lemmas `simp` uses without naming them** (`@[simp]` in a dropped place).
- **Notation, macros and elaborators** defined in a dropped declaration.
- **Instances found through a class the trace didn't reach** by name.
- **Shadowing.** A local name that shadows a global only partway through a proof can hide a
  real use of the global.

Building the fork turns these into concrete errors. Each error names the missing piece; put it
back, then rerun the build. The exact minimum comes from Lean itself after one full build: the
compiled files record which constants each proof uses. See [CHECKING.md](CHECKING.md).

## Reproducing

`make-fork.sh` rebuilds the fork from the public mirror, using the trace results in `data/`.
It then checks that the result matches `data/expected-tree.txt` byte for byte.

To redo the trace itself (about 17 minutes), run this from a clone of the mirror at the pinned
commit:

```bash
RH_TRIM_OUT=out python3 tools/reach.py MIRROR/src riemannHypothesis riemannZeta_eq_zero_re LFunction_ne_zero_of_half_lt_re LFunction_eq_zero_re LFunction_eq_zero_re_of_isPrimitive --class-gated --v2
```

It writes `out/reach-files.txt` and `out/reach-cuts.json`. These are the uncompressed forms of
`data/kept-files.txt.gz` and `data/cuts.json.gz`.

## Mistakes made along the way

These are recorded so nobody repeats them.

1. **Duplicated names, first attempt.** The first trace kept one declaration per name and
   started from the wrong `riemannHypothesis`. It reported 9 declarations.
2. **`_root_.` references.** The second trace didn't strip `_root_.` from references, which
   this code uses everywhere. It reported 23% of declarations, and the fork built from it
   failed a smoke test with "Unknown identifier `_root_.…`". The real figure after the fix
   was 62%.
3. **Whole files as the unit.** Keeping every declaration of a kept file pulls in 90% of the
   project. Cutting at declaration level is what makes the fork smaller.
4. **A helper named `org.py`.** Python's `pickle` imports `org` on startup, so the helper ran
   on every trace. It's now `org_stats.py`.
