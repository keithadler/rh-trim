# Live: checking the claimed Lean proof of the Riemann Hypothesis

> **The goal:** find the exact, smallest form of the proof, then see whether **tenet-hs**, a Lean kernel written from scratch in Haskell, accepts it, and whether it is faster than Lean's own kernel.

🔵 **Step 1 of 6: compiling** · updated every 10 minutes · last update **2026-11-21 18:15 UTC**

## The plan

```mermaid
flowchart LR
  build["1 Build the<br>original"] --> export["2 Exact<br>reduced form"] --> race["3 Haskell<br>vs Lean"] --> axioms["4 Axioms"] --> minify["5 Smallest<br>proof"] --> publish["6 Publish"]
  classDef done fill:#1f6f43,stroke:#8fe3b0,color:#fff
  classDef now fill:#2b3f8f,stroke:#8fa6ff,color:#fff,stroke-width:3px
  classDef next fill:#2a2f3d,stroke:#5b6378,color:#c9cfdc
  classDef stop fill:#7a2a2a,stroke:#ff9b9b,color:#fff
  class build now
  class export next
  class race next
  class axioms next
  class minify next
  class publish next
```

| | Step | What happens | Status |
|:---:|---|---|---|
| **1** | **Build the original** | Compile all 175,187 proof files, exactly as published. **90.5%** so far. | 🔵 **in progress** |
| **2** | **Exact reduced form** | Export the five main theorems with `lean4export`. The export holds exactly what the proof uses, measured by Lean itself. | ⏳ waiting |
| **3** | **Haskell vs Lean** | Check that export with **tenet-hs** (Haskell) and with Lean's own kernel, timed, peak memory recorded. Tenet (C#), tenet-jvm, Lean's paranoid mode, nanoda, con-leche and con-ron run in the same race. | ⏳ waiting |
| **4** | **Axioms** | List exactly which axioms the five theorems rest on. | ⏳ waiting |
| **5** | **The smallest proof** | Cut the source down to only the declarations in the export, rebuild that, and check it again with every kernel. The result is the smallest version of the proof that still compiles. | ⏳ waiting |
| **6** | **Publish** | Post the times, the verdicts and the exact sizes here. | ⏳ waiting |

Steps 2 to 4 are queued on the machine and start by themselves when the build succeeds. Step 5 follows from their output.

## Step 1: the build, 90.5%

`████████████████████████████████████▏░░░`  **158,500** of 175,187 proof files

| ⏱ Time left | 🏁 Finish (UTC) | ⚡ Rate | 💵 Spent | 💵 Projected total | ❌ Errors |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 2h 25m | 20:40 | 115 files/min | $29.35 | $33 | 0 |

![Proof files compiled over time](docs/status/chart-20261121-1815.svg)

<details><summary><b>By library</b></summary>

| Library | Built | Progress |
|---|---:|---|
| `Development` | 125,422 / 141,928 | `█████████████████▋░░` 88% |
| `Formalism` | 18,244 / 18,254 | `███████████████████▉` 100% |
| `GroundTheory` | 8,367 / 8,507 | `███████████████████▋` 98% |
| `ReciprocityTheory` | 3,841 / 3,845 | `███████████████████▉` 100% |
| `CompanionTheory` | 2,013 / 2,027 | `███████████████████▊` 99% |
| `PositivityTheory` | 441 / 449 | `███████████████████▋` 98% |
| `Lemmata` | 167 / 167 | `████████████████████` 100% |

</details>

<details><summary><b>The machine</b></summary>

| | |
|---|---|
| Instance | AWS `m6a.48xlarge` Spot, Ohio, about $1.56/hour |
| CPUs | 192 vCPUs (96 cores), load 194, 15 Lean processes running |
| Memory | 21 GB used of 776 GB |
| Disk | 83 GB free of 207 GB |
| Sandbox | bubblewrap: no network, everything read-only except the build folder |
| Safety net | the disk survives termination, and is snapshotted every 2 hours |

</details>

<details><summary><b>Just compiled</b></summary>

- `Development.AutomorphicArithmetic.WhittakerHecke.LocalArtinInertiaValuationOfUniformizerPrime`
- `Development.AutomorphicArithmetic.Foundations.Convolution.PowerSumTraces.TwistFactor`
- `Development.AutomorphicSpectrum.Proofs.BlockDecomposition.UnramifiedSatake`
- `Development.AbelianVarietyTheory.Proofs.InertiaEigenvalues.ConjLMemWeil`
- `Development.AutomorphicSpectrum.Proofs.BlockDecomposition.GluePlaces`
- `Development.AutomorphicArithmetic.WhittakerHecke.ExistsUnitResidueLogarithmOfRootsOfUnity`

</details>

<details><summary><b>Log: what went wrong and how it was handled</b></summary>

- **2026-11-20 23:29 UTC:** started compiling the original proof, after the source-level reduction turned out to drop real dependencies ([why](README.md)).
- **00:39 to 00:49:** disk full. Lake's per-module `.setup.json` files reached 92 GB (about 4.6 MB each, listing every import). They are now deleted as modules finish; nothing built was lost.
- **01:45:** status counter fixed. Lake re-prints warnings for modules already built, which the old counter counted twice.
- **02:06 to 02:12:** AWS reclaimed the Spot machine. It stopped with its disk kept, and came back on its own when capacity returned; the build resumed with nothing lost. Everything now restarts by itself after any interruption, and progress is counted from compiled files on disk.
- **2026-11-21 09:21 to 09:24:** a second Spot interruption. The machine resumed the build by itself within a minute of coming back.
- **10:25 to 10:34:** a third Spot interruption, with no capacity for 9 minutes. Resumed by itself again; nothing lost.
- **13:04 to 13:32:** a fourth Spot interruption, 28 minutes this time. Resumed by itself again; nothing lost.

</details>

Rate and finish come from the last hour of the timestamped build log. Build method: [docs/BUILD.md](docs/BUILD.md).
