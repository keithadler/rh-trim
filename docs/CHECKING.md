# Checking the fork

Run `make-fork.sh` first; it builds the fork as plain text, without compiling anything.

**This fork has never been compiled.** This page is the plan for compiling it, and for
judging what a successful compile would and would not show.

## Why compiling it is unsafe without a sandbox

Compiling Lean runs code: tactics, macros, and initializers when files are loaded.

- **In the original,** the mirror's own text scan found no `unsafe`, `extern`,
  `implemented_by` or `opaque`, and two uses of metaprogramming: `BuildAid` (`run_cmd`) and
  `CutCptCopy.lean` (`addDecl`).
- **In this fork,** neither of those is present. What remains is 20 local tactic `macro`s,
  which are shorthand for tactic sequences.

Even so, treat the code as untrusted.

- **On macOS:** use `tools/sandbox-macos.sb` with `sandbox-exec`, after replacing `HOME_DIR` and `FORK_DIR` in it. It blocks the network,
  every read under the home folder except the project and the Lean toolchain, and writes
  outside the project. Edit its paths for your machine first.
- **On Linux:** use a container with no network and a read-only root, as the mirror's own
  `verification/NOTES.md` does with podman.

## What it costs

These figures were measured on the original, not the fork.

| Machine | Rate | Full build |
|---|---|---|
| M2 Mac, 16 GB | about 85 s per file, memory-starved (each Lean process at about 14% CPU) | about 17 days: not practical |
| 32 vCPU, 256 GB (RunPod cpu3m, $1.76/h) | estimated | about 22 to 34 hours |
| 128 vCPU, 256 GB (AWS c7a.32xlarge) | estimated | about 6 to 8 hours |

The fork has 78% of the original's files and 68% of its lines, so expect it to take roughly
20 to 30% less time. Disk: about 100 GB for the original's build.

## Steps

1. **Fetch Mathlib's cache.** Run `lake exe cache get` outside the sandbox (it needs network).
   It only touches the pinned, verified Mathlib.
2. **Build.** Run `lake build Main` inside the sandbox. For the proof alone, building each
   file with `lake env lean -o` skips the C code that `lake build` also writes.
3. **On failure:** each error names what the trace dropped (see [PRUNING.md](PRUNING.md)).
   Put the declaration back from the original at the same path, then rebuild. Most failures
   should be missing `simp` lemmas, notation or instances.
4. **Judge with Comparator,** exactly as the mirror's README describes. The checkers are Lean
   4.36.0's kernel, `leanchecker-paranoid`, nanoda, con-leche and con-ron, using the fork's
   `comparator.json`. It checks that the five statements match `Challenge.lean`, which
   imports only Mathlib, and that the axioms used are only `propext`, `Quot.sound` and
   `Classical.choice`.
5. **Independent kernels.** Tenet (C#), tenet-hs (Haskell) and tenet-jvm read the compiled
   `.olean` files directly, and all three are correct on the Lean Kernel Arena. They would be
   checkers six to eight.
6. **The exact minimum.** After one full build, every compiled file records the constants each
   proof uses. Tracing from the five theorems through that record gives the true minimum, with
   no guessing. That would show how far the source trace still over-approximates.
7. **Lint.** Run lean-linter 0.5.4, built on Lean 4.33.1, with its `duplicate` and `trust`
   checks.

## What a passing check would and would not show

- **It would show** that the five theorems, stated over Mathlib's definitions, have proofs the
  kernels accept, using only the three standard axioms.
- **It would not show that the original is sound.** This fork is a trimmed copy; the original
  needs its own check. A passing fork is strong evidence for the mathematics all the same,
  because it is a subset of the original's own proof text.
- **Kernel bugs.** Lean 4.33.1 lacks some later runtime fixes (see the mirror's `NOTES.md`).
  That is why the judging uses Lean 4.36.0 and outside checkers.
