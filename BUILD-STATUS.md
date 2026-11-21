# Build status: the ORIGINAL proof, compiling on AWS

Updated **2026-11-21 01:20 UTC**, every 10 minutes while the build runs.

| | |
|---|---|
| Machine | AWS `m6a.48xlarge` Spot, Ohio: 192 vCPUs (96 cores), 739 GB RAM |
| Sandbox | bubblewrap, no network |
| Building | the original, byte-exact mirror at `8b83d5e7b` (175,187 proof files) |
| Compiling since | 2026-11-20 23:25 UTC |
| Cost so far | about $0.00 (machine at about $1.56/h) |
| Why the original | the source-level reduction kept dropping real dependencies; this build gives the exact dependency record to reduce from |
| Disk | ? |
| Error lines | ? (since the 00:49 restart) |
| Incident | 00:39 to 00:49 UTC: disk full. Lake's `.setup.json` files reached 92 GB (about 4.6 MB per module, each listing its whole import closure). They are now deleted as modules finish; nothing built was lost. |

```
waiting for the first files
```

Estimates come from the last 10 minutes of the timestamped log (`tools/progress.sh`).
How it's built: [docs/BUILD.md](docs/BUILD.md).
