# Building the original proof yourself

How we built the claimed Lean proof of the Riemann Hypothesis, exactly as published, on one cloud
machine, and how to do the same. Live record of our run: [BUILD-STATUS.md](../BUILD-STATUS.md).

## What it took us

| | |
|---|---|
| Result | `Build completed successfully (183893 jobs)`: all 175,187 proof files, **0 errors, no `sorry`** |
| Machine | AWS `m6a.48xlarge` **Spot**, Ohio (us-east-2): 192 vCPUs, 768 GB RAM, 200 GB gp3 disk |
| Price | about $1.56/hour (Spot; on-demand is about $8.29/hour) |
| Time | started compiling 2026-11-20 23:29 UTC, finished 2026-11-21 20:52 UTC: **about 21 hours**, including four Spot interruptions (46 minutes in all) and one disk-full stop (10 minutes) |
| Cost | **about $35** for the machine, plus well under $2 for the disk and its snapshots |
| Lean | 4.33.1, Mathlib from its official cache, mirror commit `8b83d5e7b319ebc7b3be6e59ce3411ba2b09d116` |

We wanted a `c7a` (newer, faster per core) but AWS had no Spot capacity for it that night;
`m6a.48xlarge` is an older generation. A faster machine should do better. Near the end the build
can only use a few cores at a time, because the last files depend on each other in a chain.

## 1. Start a throwaway machine

**Compiling Lean runs the proof's code.** Use a fresh machine with no credentials on it: no SSH
keys you care about, no cloud roles. Delete it afterward.

On AWS:

- AMI: **Ubuntu Server 24.04**, x86_64
- Instance type: `m6a.48xlarge`, `c7a.48xlarge` or similar (lots of cores, at least 256 GB RAM)
- Under **Advanced details**: request a **Spot** instance, type **persistent**, interruption
  behavior **stop**. Then an interruption pauses the machine instead of deleting it.
- Storage: **200 GB gp3**, with **Delete on termination: No**, so the build survives anything
- IAM role: **none**
- Security group: SSH from your IP only

Optional but worth it: an Elastic IP (the address stays the same after a Spot stop), and a Data
Lifecycle Manager policy that snapshots the disk every 2 hours.

## 2. Run the build

```bash
git clone https://github.com/keithadler/rh-trim && cd rh-trim
```

```bash
tmux new -s rh
```

```bash
./build-original.sh ~/rh-build
```

It installs the tools, clones the proof at the pinned commit, fetches Lean 4.33.1 and Mathlib's
cache, and compiles `Main` inside bubblewrap **with the network cut off**. Everything else is
read-only. The log is timestamped in `~/rh-build/build-original.log`.

Detach with `Ctrl-b` then `d`; reattach with `tmux attach -t rh`.

## 3. Watch it

```bash
TOTAL=175187 tools/progress.sh ~/rh-build/build-original.log
```

Or count compiled files directly: `find ~/rh-build/original/.lake/build/lib/lean -name '*.olean' | wc -l`
(this includes Mathlib's, so subtract the count right after the cache step).

## 4. If the Spot machine is interrupted

Start it again (a persistent request does this by itself when capacity returns) and rerun
`./build-original.sh ~/rh-build`. Lake skips everything already built. To make this automatic, add
a line to `crontab -e`:

```
@reboot sleep 30 && tmux new -d -s rh "cd ~/rh-trim && ./build-original.sh ~/rh-build"
```

## 5. After it finishes

Check the result line at the end of the script's output, then check the proof itself. A clean
build is only Lean 4.33.1's kernel accepting it. We go on to export the five main theorems with
`lean4export` and check that export with eight independent kernels, including three written from
scratch: **Tenet** (C#), **tenet-hs** (Haskell) and **tenet-jvm**. See [CHECKING.md](CHECKING.md)
and the plan in [BUILD-STATUS.md](../BUILD-STATUS.md).

## 6. Clean up

Terminate the instance, **cancel the Spot request** (a persistent request otherwise starts a new
machine), then delete the volume, snapshots and Elastic IP once you have what you need.
