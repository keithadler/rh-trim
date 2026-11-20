# Build status: the reduced version, compiling on AWS

Updated **2026-11-20 23:17 UTC**, every 10 minutes while the build runs.

| | |
|---|---|
| Machine | AWS `m6a.48xlarge` Spot, Ohio: 192 vCPUs (96 cores), 739 GB RAM |
| Sandbox | bubblewrap, no network |
| Compiling since | 2026-11-20 22:46 UTC |
| Cost so far | about $0.98 (machine at about $1.56/h) |
| Proof files in the reduced version | 137,020 |
| Error lines | 7295 |

```
5765 proof files built, 7295 error lines
rate: 248 files/min over the last 10 min; about 8h 50m left at that rate
```

First errors:

```
22:59:05 error: src/Formalism/SatakeDualWeyl/AdelicIwasawaHecke/HeckeConvolutionMemHolds.lean:53:39: Unknown identifier `conv_finDosetSupp`
22:59:05 error: Lean exited with code 1
22:59:05 error: src/Formalism/LocalToGlobal/ProjectiveLattices/IntegrableOnIntegrand.lean:56:68: Invalid field `I`: The environment does not contain `Formalism.L2.Pj.FJ.CuspFD.I`, so it is not possible to project the fie
22:59:05 error: Lean exited with code 1
22:59:05 error: src/Formalism/GradedWeylDivisibility/FockSpaceTableaux/SSYTExists.lean:49:6: Unknown identifier `lcssyt_consI_strictMono`
```

Estimates come from the last 10 minutes of the timestamped log (`tools/progress.sh`).
How it's built: [docs/BUILD.md](docs/BUILD.md).
