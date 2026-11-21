# Building the reduced version

Step-by-step instructions for one cloud machine, from nothing to a build report.

**Want to help build the *original*, as published?** Join the distributed replay at
[rohanarun/alpoge-rh-replay](https://github.com/rohanarun/alpoge-rh-replay). Volunteers there
claim and build chunks of the 175,187 modules. This page builds the reduced version (137,020
files) on a single machine, as a complement.

> **These instructions are new and haven't been run end to end yet.** If a step fails, the
> failure itself is a useful report.

## Cost and time

The estimates are scaled from measurements on an M2 Mac (about 12 CPU-seconds per file). The
real rate shows in the first 10 minutes; see [step 5](#5-watch-the-rate).

| Machine | Cores / RAM | Price | Time (estimate) | Cost (estimate) |
|---|---|---|---|---|
| **AWS `c7a.32xlarge`, spot** (recommended) | 128 / 256 GB | about $2.15/h | 4 to 6 h | **about $9 to $13** |
| AWS `c7a.32xlarge`, on-demand | 128 / 256 GB | $6.57/h | 4 to 6 h | about $26 to $40 |
| Hetzner `CCX63` | 48 / 192 GB | about €1.37/h | 8 to 12 h | about €11 to €17 |
| RunPod `cpu3m`, 32 vCPU | 32 / 256 GB | $1.76/h | 14 to 26 h | about $25 to $45 |

- **Disk:** about 150 GB. `build-linux.sh` deletes Lake's per-module `.setup.json` files as it goes. Without that, they reach about 4.6 MB per module, which would mean hundreds of GB for this proof. On AWS add a 200 GB gp3 volume; it costs well under $1 for a day.
- **Spot interruptions:** a spot machine can be taken back. Lake skips everything already built,
  so rerunning `build-linux.sh` on the same disk resumes. Keep the volume when the instance stops.
- **Memory:** 256 GB is the safe choice. The mirror's own build allowed up to 440 GB, and how much
  the last files really need is unknown.

## 1. Start a throwaway machine

Use Ubuntu 22.04 or 24.04.

**Compiling Lean runs the proof's code.** Use a fresh machine with no credentials on it: no SSH
keys you care about, no cloud roles. Delete it afterward.

On AWS:

- AMI: Ubuntu Server 24.04, x86_64
- Instance type: `c7a.32xlarge`; under **Advanced details**, request a **Spot** instance
- Storage: 200 GB gp3
- IAM role: **none**
- Security group: SSH from your IP only

## 2. Get the scripts

```bash
git clone https://github.com/keithadler/rh-trim && cd rh-trim
```

## 3. Run the build

Use `tmux`, so the build survives a dropped connection:

```bash
tmux new -s rh
```

```bash
./build-linux.sh ~/rh-build
```

The script:

1. installs `git`, `python3`, `bubblewrap` and elan (Lean's installer);
2. runs `make-fork.sh`, which rebuilds the reduced version from the public mirror and checks its
   fingerprint (about 2 minutes);
3. fetches Lean 4.33.1 and Mathlib's official build cache (needs network);
4. compiles `Main` **with the network cut off**, inside bubblewrap. Everything is read-only except
   the build folder and `/tmp`, and the log is timestamped in `~/rh-build/build.log`;
5. prints the result, and on failure lists what the reduction cut but the proof needs.

**Inside a container** (a RunPod pod, Docker), bubblewrap usually can't make a sandbox. The script
stops and says so. On a throwaway machine with nothing to protect, you can continue without the
sandbox:

```bash
ALLOW_NO_SANDBOX=1 ./build-linux.sh ~/rh-build
```

## 4. Detach and come back

Press `Ctrl-b`, then `d`, to detach. Reattach later:

```bash
tmux attach -t rh
```

## 5. Watch the rate

```bash
tools/progress.sh ~/rh-build/build.log
```

It prints the files built, the rate over the last 10 minutes and the time left at that rate.
After 10 to 15 minutes this is the real estimate. If it says days instead of hours, the machine
is too small; stop and report the rate.

## 6. If it fails

Most failures should be names the trace couldn't see: lemmas `simp` uses without naming them,
notation, instances. The script runs `tools/missing.py` and writes `~/rh-build/missing.txt`. That
file lists each missing name and where the original declares it.

Report that list as it is; you don't need to fix anything. If you want to go on:

1. copy each listed declaration from the original file into the reduced file at the same path;
2. rerun `./build-linux.sh ~/rh-build`. It resumes where it stopped.

## 7. Report

Open a [build report](https://github.com/keithadler/rh-trim/issues/new?template=build-report.yml)
with:

- your machine, the time and the result;
- every error;
- `missing.txt`;
- the compressed log:

```bash
zstd -19 ~/rh-build/build.log
```

## 8. After a clean build: judge it

A clean build is only Lean 4.33.1's kernel accepting it. The real verdict comes from the
mirror's Comparator route, with Lean 4.36.0 and four independent checkers. Run it from
`~/rh-build/reduced`, following
[the mirror's README](https://github.com/Deicyde/riemann-hypothesis#checking-it):

1. export the challenge from a clean clone;
2. export `Main` from this build;
3. run `lake comparator` with the fork's `comparator.json`.

See [CHECKING.md](CHECKING.md) for what a pass would and would not show.

## 9. Clean up

Terminate the instance and delete the volume. On AWS, check **EC2 → Volumes** for leftovers.
