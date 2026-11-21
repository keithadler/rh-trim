# Live: building the claimed Lean proof of the Riemann Hypothesis

🟢 **Compiling**: the original proof, all 175,187 files, on one AWS machine. Updated every 10 minutes; last update **2026-11-21 02:37 UTC**.

## 20.3% built

`████████ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░`  **35,538** of 175,187 proof files

| ⏱ Time left | 🏁 Finish (UTC) | ⚡ Rate | 💵 Spent | 💵 Projected total | ❌ Errors |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 15h 58m | 18:35 | 146 files/min | $6.02 | $31 | 0 |

![Proof files compiled over time](docs/status/chart-20261121-0237.svg)

## By library

| Library | Built | Progress |
|---|---:|---|
| `Development` | 18,312 / 141,928 | `██▌░░░░░░░░░░░░░░░░░` 13% |
| `Formalism` | 12,010 / 18,254 | `█████████████▏░░░░░░` 66% |
| `GroundTheory` | 1,028 / 8,507 | `██▍░░░░░░░░░░░░░░░░░` 12% |
| `ReciprocityTheory` | 2,851 / 3,845 | `██████████████▊░░░░░` 74% |
| `CompanionTheory` | 1,210 / 2,027 | `███████████▉░░░░░░░░` 60% |
| `PositivityTheory` | 0 / 449 | ` ░░░░░░░░░░░░░░░░░░░` 0% |
| `Lemmata` | 125 / 167 | `██████████████▉░░░░░` 75% |

## The machine

| | |
|---|---|
| Instance | AWS `m6a.48xlarge` Spot, Ohio, about $1.56/hour |
| CPUs | 192 vCPUs (96 cores), load 195, 24 Lean processes running |
| Memory | 26 GB used of 776 GB |
| Disk | 153 GB free of 207 GB |
| Sandbox | bubblewrap: no network, everything read-only except the build folder |
| Safety net | the disk survives termination, and is snapshotted every 2 hours |

## Just compiled

- `Development.AbelianVarietyTheory.Proofs.DivisorProofs.CurvatureSumWedgeWellDefinedAndDeRhamLiftStatement`
- `Development.AbelianVarietyTheory.Proofs.DivisorProofs.PlaceRingFractionEmbedding`
- `Development.AbelianVarietyTheory.Proofs.DivisorProofs.CmTypeConjugateInField`
- `Development.AbelianVarietyTheory.Proofs.DivisorProofs.DeRhamCorrespondencePolynomialStatement`
- `Development.AbelianVarietyTheory.Proofs.DivisorProofs.WeierstrassModularTransformationLevelStatement`
- `Development.AbelianVarietyTheory.Proofs.DivisorProofs.ExistsPrimeAboveValuationEq`

## What happens when it finishes

**Queued on the machine; it starts by itself when the build succeeds:**

1. **Exact reduced form.** Export the five theorems with `lean4export`. The export holds exactly the declarations the proof uses, measured by Lean itself, not guessed.
2. **Kernel race.** Check that one export, one checker at a time, each timed with peak memory recorded: Lean's kernel, its paranoid mode, nanoda, con-leche, con-ron, and the three clean-room kernels **Tenet** (C#), **tenet-hs** (Haskell) and **tenet-jvm**. All eight accepted a test export of the same format.
3. **Axioms.** List exactly which axioms the five theorems depend on.
4. **Publish** the times, the verdicts and the exact size here.

## Log

- **2026-11-20 23:29 UTC:** started compiling the original proof, after the source-level reduction turned out to drop real dependencies ([why](README.md)).
- **00:39 to 00:49:** disk full. Lake's per-module `.setup.json` files reached 92 GB (about 4.6 MB each, listing every import). They are now deleted as modules finish; nothing built was lost.
- **01:45:** status counter fixed. Lake re-prints warnings for modules already built, which the old counter counted twice.
- **02:06 to 02:12:** AWS reclaimed the Spot machine. It stopped with its disk kept, and came back on its own when capacity returned; the build resumed with nothing lost. Everything now restarts by itself after any interruption, and progress is counted from compiled files on disk.

Rate and finish come from the last hour of the timestamped build log. Build method: [docs/BUILD.md](docs/BUILD.md).
