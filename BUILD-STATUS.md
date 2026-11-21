# Live: building the claimed Lean proof of the Riemann Hypothesis

🟢 **Compiling**: the original proof, all 175,187 files, on one AWS machine. Updated every 10 minutes; last update **2026-11-21 02:16 UTC**.

## 18.3% built

`███████▎░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░`  **32,119** of 175,187 proof files

| ⏱ Time left | 🏁 Finish (UTC) | ⚡ Rate | 💵 Spent | 💵 Projected total | ❌ Errors |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 14h 38m | 16:55 | 163 files/min | $5.48 | $28 | 0 |

![Proof files compiled over time](docs/status/chart-20261121-0216.svg)

## By library

| Library | Built | Progress |
|---|---:|---|
| `Development` | 15,131 / 141,928 | `██▏░░░░░░░░░░░░░░░░░` 11% |
| `Formalism` | 11,988 / 18,254 | `█████████████▏░░░░░░` 66% |
| `GroundTheory` | 887 / 8,507 | `██ ░░░░░░░░░░░░░░░░░` 10% |
| `ReciprocityTheory` | 2,807 / 3,845 | `██████████████▌░░░░░` 73% |
| `CompanionTheory` | 1,179 / 2,027 | `███████████▋░░░░░░░░` 58% |
| `PositivityTheory` | 0 / 449 | ` ░░░░░░░░░░░░░░░░░░░` 0% |
| `Lemmata` | 125 / 167 | `██████████████▉░░░░░` 75% |

## The machine

| | |
|---|---|
| Instance | AWS `m6a.48xlarge` Spot, Ohio, about $1.56/hour |
| CPUs | 192 vCPUs (96 cores), load 137, 192 Lean processes running |
| Memory | 83 GB used of 776 GB |
| Disk | 157 GB free of 207 GB |
| Sandbox | bubblewrap: no network, everything read-only except the build folder |
| Safety net | the disk survives termination, and is snapshotted every 2 hours |

## Just compiled


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
