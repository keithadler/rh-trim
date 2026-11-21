# Build status: the ORIGINAL proof, compiling on AWS

Updated **2026-11-21 00:50 UTC**, every 10 minutes while the build runs.

| | |
|---|---|
| Machine | AWS `m6a.48xlarge` Spot, Ohio: 192 vCPUs (96 cores), 739 GB RAM |
| Sandbox | bubblewrap, no network |
| Building | the original, byte-exact mirror at `8b83d5e7b` (175,187 proof files) |
| Compiling since | 2026-11-20 23:25 UTC |
| Cost so far | about $3.38 (machine at about $1.56/h) |
| Why the original | the source-level reduction kept dropping real dependencies; this build gives the exact dependency record to reduce from |
| Error lines | 0 |

```
725 proof files built, 0 error lines
rate: 944 files/min over the last 0 min; about 3h 04m left at that rate
```

Estimates come from the last 10 minutes of the timestamped log (`tools/progress.sh`).
How it's built: [docs/BUILD.md](docs/BUILD.md).
