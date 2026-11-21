# Live: building the claimed Lean proof of the Riemann Hypothesis

🟢 **Compiling**: the original proof, all 175,187 files, on one AWS machine. Updated every 10 minutes; last update **2026-11-21 01:55 UTC**.

## 17.2% built

`██████▉░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░`  **30,138** of 175,187 proof files

| ⏱ Time left | 🏁 Finish (UTC) | ⚡ Rate | 💵 Spent | 💵 Projected total | ❌ Errors |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 11h 29m | 13:24 | 211 files/min | $5.08 | $23 | 0 |

![Proof files compiled over time](docs/status/chart-20261121-0155.svg)

## By library

| Library | Built | Progress |
|---|---:|---|
| `Development` | 13,494 / 141,928 | `█▉░░░░░░░░░░░░░░░░░░` 10% |
| `Formalism` | 11,961 / 18,254 | `█████████████ ░░░░░░` 66% |
| `GroundTheory` | 883 / 8,507 | `██ ░░░░░░░░░░░░░░░░░` 10% |
| `ReciprocityTheory` | 2,499 / 3,845 | `████████████▉░░░░░░░` 65% |
| `CompanionTheory` | 1,175 / 2,027 | `███████████▌░░░░░░░░` 58% |
| `PositivityTheory` | 0 / 449 | ` ░░░░░░░░░░░░░░░░░░░` 0% |
| `Lemmata` | 124 / 167 | `██████████████▊░░░░░` 74% |

## The machine

| | |
|---|---|
| Instance | AWS `m6a.48xlarge` Spot, Ohio, about $1.56/hour |
| CPUs | 192 vCPUs (96 cores), load 202, 28 Lean processes running |
| Memory | 32 GB used of 776 GB |
| Disk | 165 GB free of 207 GB |
| Sandbox | bubblewrap: no network, everything read-only except the build folder |
| Safety net | the disk survives termination, and is snapshotted every 2 hours |

## Just compiled

- `ReciprocityTheory.ReductiveGroups.ArithmeticGeometry.SquareIntegrability.SplitVC`
- `ReciprocityTheory.AnalyticForms.PotentialTheory.Degree`
- `Development.AbelianVarietyTheory.Proofs.ModuliProofs.IsLocallyNoetherianOfIsQProjOver`
- `Development.AbelianVarietyTheory.Proofs.DivisorProofs.TangentPhiSqZeroNaturalityStatement`
- `ReciprocityTheory.AnalyticForms.PotentialTheory.StokesA`
- `Development.AbelianVarietyTheory.Proofs.DivisorProofs.HodgeTateSandwichOfPrismaticDieudonne`

## What happens when it finishes

1. **Exact reduced form.** Export the five theorems with `lean4export`. The export holds exactly the declarations the proof uses, measured by Lean itself, not guessed.
2. **Kernel race.** Check that export with Lean's kernel, **tenet-hs** (Haskell), **Tenet** (C#) and **tenet-jvm**, all timed on this same machine.
3. **Publish** the times, the verdicts and the exact size here.

## Log

- **2026-11-20 23:29 UTC:** started compiling the original proof, after the source-level reduction turned out to drop real dependencies ([why](README.md)).
- **00:39 to 00:49:** disk full. Lake's per-module `.setup.json` files reached 92 GB (about 4.6 MB each, listing every import). They are now deleted as modules finish; nothing built was lost.
- **01:45:** status counter fixed. Lake re-prints warnings for modules already built, which the old counter counted twice.

Rate and finish come from the last hour of the timestamped build log. Build method: [docs/BUILD.md](docs/BUILD.md).
