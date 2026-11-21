# Live: checking the claimed Lean proof of the Riemann Hypothesis

> **The goal:** find the exact, smallest form of the proof, then see whether **tenet-hs**, a Lean kernel written from scratch in Haskell, accepts it, and whether it is faster than Lean's own kernel.

**Next up: the Haskell run** (step 3) starts by itself as soon as the export is written.

🔵 **Step 2 of 6: exporting the exact reduced form** · updated every 10 minutes · last update **2026-11-21 22:24 UTC**

## The plan

```mermaid
flowchart LR
  build["1 Build the<br>original"] --> export["2 Exact<br>reduced form"] --> race["3 Haskell<br>vs Lean"] --> axioms["4 Axioms"] --> minify["5 Smallest<br>proof"] --> publish["6 Publish"]
  classDef done fill:#1f6f43,stroke:#8fe3b0,color:#fff
  classDef now fill:#2b3f8f,stroke:#8fa6ff,color:#fff,stroke-width:3px
  classDef next fill:#2a2f3d,stroke:#5b6378,color:#c9cfdc
  classDef stop fill:#7a2a2a,stroke:#ff9b9b,color:#fff
  class build done
  class export now
  class race next
  class axioms next
  class minify next
  class publish next
```

| | Step | What happens | Status |
|:---:|---|---|---|
| **1** | **Build the original** | Compile all 175,187 proof files, exactly as published. **100.0%** so far. | ✅ done |
| **2** | **Exact reduced form** | Export the five main theorems with `lean4export`. The export holds exactly what the proof uses, measured by Lean itself. | 🔵 **in progress** |
| **3** | **Haskell vs Lean** | Check that export with **tenet-hs** (Haskell) and with Lean's own kernel, timed, peak memory recorded. Tenet (C#), tenet-jvm, Lean's paranoid mode, nanoda, con-leche and con-ron run in the same race. | ⏳ waiting |
| **4** | **Axioms** | List exactly which axioms the five theorems rest on. | ⏳ waiting |
| **5** | **The smallest proof** | Cut the source down to only the declarations in the export, rebuild that, and check it again with every kernel. The result is the smallest version of the proof that still compiles. | ⏳ waiting |
| **6** | **Publish** | Post the times, the verdicts and the exact sizes here. | ⏳ waiting |

Steps 2 to 4 are queued on the machine and start by themselves when the build succeeds. Step 5 follows from their output.

## Step 1: the build ✅ done

`████████████████████████████████████████`  **175,187** of 175,187 proof files · `Build completed successfully (183893 jobs)`

| ⏱ Compiling time | 🏁 Finished (UTC) | 💵 Build cost | 💵 Spent so far | ❌ Errors | 🚫 sorry |
|:---:|:---:|:---:|:---:|:---:|:---:|
| about 21 h | 2026-11-21 20:52 | $33.43 | $35.84 | 0 | 0 |

Spent so far keeps counting while the machine runs steps 2 to 4.

![Proof files compiled over time](docs/status/chart-20261121-2224.svg)

<details><summary><b>By library</b></summary>

| Library | Built | Progress |
|---|---:|---|
| `Development` | 141,928 / 141,928 | `████████████████████` 100% |
| `Formalism` | 18,254 / 18,254 | `████████████████████` 100% |
| `GroundTheory` | 8,507 / 8,507 | `████████████████████` 100% |
| `ReciprocityTheory` | 3,845 / 3,845 | `████████████████████` 100% |
| `CompanionTheory` | 2,027 / 2,027 | `████████████████████` 100% |
| `PositivityTheory` | 449 / 449 | `████████████████████` 100% |
| `Lemmata` | 167 / 167 | `████████████████████` 100% |

</details>

<details><summary><b>The machine</b></summary>

| | |
|---|---|
| Instance | AWS `m6a.48xlarge` Spot, Ohio, about $1.56/hour |
| CPUs | 192 vCPUs (96 cores), load 1, 0 Lean processes running |
| Memory | 71 GB used of 776 GB |
| Disk | 447 GB free of 623 GB |
| Sandbox | bubblewrap: no network, everything read-only except the build folder |
| Safety net | the disk survives termination, and is snapshotted every 2 hours |

</details>

<details><summary><b>Just compiled</b></summary>

- `Main`
- `Supplements.Kernels.MainTheoremsAll`
- `Supplements.Kernels.MainTheoremsCritical`
- `Supplements.Kernels.MainTheorems`
- `Development.AutomorphicArithmetic.AutomorphicVarieties.SmallClassNumbers.CorGKOf`
- `Development.AutomorphicArithmetic.CharacterBoxes.MainConclusion`

</details>

<details><summary><b>Log: what went wrong and how it was handled</b></summary>

- **2026-11-20 23:29 UTC:** started compiling the original proof, after the source-level reduction turned out to drop real dependencies ([why](README.md)).
- **00:39 to 00:49:** disk full. Lake's per-module `.setup.json` files reached 92 GB (about 4.6 MB each, listing every import). They are now deleted as modules finish; nothing built was lost.
- **01:45:** status counter fixed. Lake re-prints warnings for modules already built, which the old counter counted twice.
- **02:06 to 02:12:** AWS reclaimed the Spot machine. It stopped with its disk kept, and came back on its own when capacity returned; the build resumed with nothing lost. Everything now restarts by itself after any interruption, and progress is counted from compiled files on disk.
- **2026-11-21 09:21 to 09:24:** a second Spot interruption. The machine resumed the build by itself within a minute of coming back.
- **10:25 to 10:34:** a third Spot interruption, with no capacity for 9 minutes. Resumed by itself again; nothing lost.
- **13:04 to 13:32:** a fourth Spot interruption, 28 minutes this time. Resumed by itself again; nothing lost.
- **20:52:38: build finished.** `Build completed successfully (183893 jobs)`: all 175,187 proof files, 0 errors, no `sorry`, 6 h 56 m of compiling since the last restart. The export (step 2) started at 20:53.

</details>

Rate and finish come from the last hour of the timestamped build log. Build method: [docs/BUILD.md](docs/BUILD.md).
