# Build status: the reduced version, compiling on AWS

Updated **2026-11-20 22:57 UTC**, every 10 minutes while the build runs.

| | |
|---|---|
| Machine | AWS `m6a.48xlarge` Spot, Ohio: 192 vCPUs (96 cores), 739 GB RAM |
| Sandbox | bubblewrap, no network |
| Compiling since | 2026-11-20 22:46 UTC |
| Cost so far | about $0.45 (machine at about $1.56/h) |
| Proof files in the reduced version | 137,020 |
| Error lines | 3947 |

```
2229 proof files built, 3947 error lines
rate: 223 files/min over the last 10 min; about 10h 04m left at that rate
```

First errors:

```
22:46:35 error: src/ReciprocityTheory/ReductiveGroups/ArithmeticGeometry/SemiabelianSchemes/AbelianSchemeQuotients/IsAbelianScheme.lean:37:10: failed to synthesize instance of type class
22:46:35 error: Lean exited with code 1
22:46:41 error: src/Formalism/CyclotomicNorms/StatementI.lean:65:0: Unexpected name `Formalism.CyclotomicNorms` after `end`: The current section is unnamed
22:46:41 error: Lean exited with code 1
22:46:42 error: src/Formalism/IncomingBounds/IncomingBound.lean:38:0: Unexpected name `TopData` after `end`: The current section is unnamed
```

Estimates come from the last 10 minutes of the timestamped log (`tools/progress.sh`).
How it's built: [docs/BUILD.md](docs/BUILD.md).
