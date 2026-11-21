# Live: building the claimed Lean proof of the Riemann Hypothesis

🟢 **Compiling**: the original proof, all 175,187 files, on one AWS machine. Updated every 10 minutes; last update **2026-11-21 07:18 UTC**.

## 45.4% built

`██████████████████▏░░░░░░░░░░░░░░░░░░░░░`  **79,534** of 175,187 proof files

| ⏱ Time left | 🏁 Finish (UTC) | ⚡ Rate | 💵 Spent | 💵 Projected total | ❌ Errors |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 10h 08m | 17:27 | 157 files/min | $13.33 | $29 | 0 |

![Proof files compiled over time](docs/status/chart-20261121-0718.svg)

## By library

| Library | Built | Progress |
|---|---:|---|
| `Development` | 54,714 / 141,928 | `███████▋░░░░░░░░░░░░` 39% |
| `Formalism` | 12,618 / 18,254 | `█████████████▊░░░░░░` 69% |
| `GroundTheory` | 7,213 / 8,507 | `████████████████▉░░░` 85% |
| `ReciprocityTheory` | 3,400 / 3,845 | `█████████████████▋░░` 88% |
| `CompanionTheory` | 1,440 / 2,027 | `██████████████▏░░░░░` 71% |
| `PositivityTheory` | 6 / 449 | `▎░░░░░░░░░░░░░░░░░░░` 1% |
| `Lemmata` | 140 / 167 | `████████████████▊░░░` 84% |

## The machine

| | |
|---|---|
| Instance | AWS `m6a.48xlarge` Spot, Ohio, about $1.56/hour |
| CPUs | 192 vCPUs (96 cores), load 197, 25 Lean processes running |
| Memory | 29 GB used of 776 GB |
| Disk | 132 GB free of 207 GB |
| Sandbox | bubblewrap: no network, everything read-only except the build folder |
| Safety net | the disk survives termination, and is snapshotted every 2 hours |

## Just compiled

- `Development.AbelianVarietyTheory.Proofs.TwistedOperators.WeilActionVacuumEqResidueDetCharOfFrameStabilizeStatement`
- `Development.AbelianVarietyTheory.Proofs.DivisorProofs.SchwartzBoxTensorLeftFixedLinearApply`
- `Development.AbelianVarietyTheory.Proofs.DivisorProofs.IsNatDatumSquareFlip`
- `Development.AbelianVarietyTheory.Proofs.TwistedOperators.CutIsometry`
- `Development.AbelianVarietyTheory.Proofs.UnitaryExistence.LinearIndependentSingleAdd`
- `Development.AbelianVarietyTheory.Proofs.TwistedOperators.DatumLevelHyperspecialOffFinitePlaces`

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
