# Proof map

How the claimed proof is put together, from the five theorems in `Main.lean` down to the
inputs the deep part rests on. Every declaration named here gets a docstring in the fork that `make-fork.sh` builds
(marked "Added in this fork"), except where noted. Paths are relative to the fork's root.

Nothing on this page has been checked by a kernel in this fork. The fork has not been
compiled. Where a statement's meaning is read from its Lean text rather than checked, the
page says so.

## The shape in one picture

```
Main.lean: the five theorems
  │
  ├─ riemannHypothesis, riemannZeta_eq_zero_re ─── rhOfAll ─── Formalism.VW.rh_of_every ─── rh_of_right
  ├─ LFunction_ne_zero_of_half_lt_re ───────────── allChi   (this IS the key claim)
  ├─ LFunction_eq_zero_re ──────────────────────── claimAll ─── Claim.strip
  └─ LFunction_eq_zero_re_of_isPrimitive ───────── critAll  ─── Formalism.VW.critLine
                                                      │
                     every one of them uses ──────── allChi : UpperTheory.EveryCharacter
                                                      │
                                    UpperTheory.FinalTheorems.everyCharacter        ← no hypotheses
                                                      │
                                    everyCharacter_of_row (h : Row0b …)
                                         │                         │
            every_character_of_literature_of_vWin (O, hV)      vwin_of_row h : VWin
                                         │
            every_character_of_theta_integrals_local_matching (… many inputs …)
                                         │
            every_character_of_green_v_win (Green, VWin, Hyps …)

  and h := galoisLocalGlobalStrong_recParameter
             = galoisRepresentations_of_thetaLift tLiftK
```

**Read it as:** the whole proof is the key claim plus short classical arguments. The key claim
is assembled from one input, `Row0b` (Galois representations), which the project derives
from a theta-lift statement, `TLiftK`.

## Layer 1: the statements (checked by hand; small)

| File | Declarations | What they say |
|---|---|---|
| `src/Statements.lean` | `RiemannZetaZerosOnLine`, `DirichletLNonvanishingRightOfHalf`, `DirichletLZerosOnLine`, `PrimitiveDirichletLZerosOnLine` | RH and three GRH statements for Dirichlet L-functions, using only Mathlib's `riemannZeta`, `DirichletCharacter.LFunction` and `IsPrimitive`. Imports only Mathlib. |
| `src/Main.lean` | the five theorems | Each is one line, pointing at `rhOfAll`, `allChi`, `claimAll` or `critAll`. |
| `src/Challenge.lean` | the same five, with `sorry` | Added by the mirror for Comparator; not part of the submission and not imported by `Main`. |

In the original, `Claim.zeta_iff : Claim.Zeta ↔ RiemannHypothesis := Iff.rfl` shows the kernel
treats the written-out statement as Mathlib's. The final proof doesn't use it, so the trace
dropped it from this fork.

## Layer 2: the classical reduction (checked by hand; textbook)

All in Mathlib's language, a few files deep, importing only Mathlib.

| File | Declarations | Role |
|---|---|---|
| `src/Supplements/Kernels/MainTheorems.lean` | `allChi`, `rhOfAll`, `critAll`, `claimAll` | Glue: the key claim, and the three consequences. |
| `src/Formalism/GammaFactorNonvanishing/RhOfRight.lean` | `Formalism.VW.rh_of_right` | No zeros of `ζ` right of 1/2 implies RH, via the functional equation `riemannZeta_one_sub`. |
| `src/Formalism/GammaFactorNonvanishing/CritLine.lean` | `gammaFactor_ne_zero`, `critLine`, `rh_of_every` | The same for Dirichlet L-functions; RH as the modulus-1 case. |
| `src/Development/AutomorphicArithmetic/CharacterBoxes/HalfPlane.lean` | `Claim.HalfPlane`, `Claim.Strip`, `Claim.Zeta` | The three `Claim` statements. |
| `src/Development/AutomorphicArithmetic/CharacterBoxes/ClaimStrip.lean` | `Claim.strip`, `Claim.zeta`, helpers | Half-plane to strip (primitive characters, Euler factors) and to RH. |

In the original these files compiled cleanly on Lean 4.33.1, and lean-linter 0.5.4 found
nothing in them (18 checks, 15 declarations).

## Layer 3: the key claim (not checked anywhere yet)

`UpperTheory.EveryCharacter`, in
`src/Development/AutomorphicArithmetic/CharacterBoxes/EveryCharacter.lean`, says no
Dirichlet L-function vanishes right of `Re s = 1/2`. It is word for word the same statement as
`DirichletLNonvanishingRightOfHalf` and `Claim.HalfPlane`, defined three times under three
names.

### Theorems that conclude the key claim

The original has seven, plus `allChi`, which only re-exports one of them.

| Theorem | Hypotheses | Role | In this fork? |
|---|---|---|---|
| `UpperTheory.FinalTheorems.everyCharacter` | none | **the one the proof uses** | yes |
| `UpperTheory.FinalTheorems.everyCharacter_of_row` | `Row0b …` | step on the chain | yes |
| `UpperTheory.LiteratureTheorems.every_character_of_literature_of_vWin` | `O : OpenLiteratureStatements`, `hV : VWin` | step on the chain | yes |
| `every_character_of_theta_integrals_local_matching` | many | step on the chain: the heart of the argument | yes |
| `UpperTheory.Top.every_character_of_green_v_win` | `Green`, `VWin` | step on the chain: `every_character_of_theta_integrals_local_matching` calls it | yes |
| `UpperTheory.Top.plugAll` | `Green`, `VWin`, `Hyps …` | side route, unused | removed |
| `everyE₂` | several | side route, unused | removed |

Locations:

- `CharacterBoxes/MainConclusion.lean`: `everyCharacter`, `everyCharacter_of_row`
- `ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean`
- `ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/SiegelEisensteinSecondTermHypotheses.lean`
- `ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/TopPlug.lean`
- `CharacterBoxes/EveryCharacter.lean` (original only)
- `ThetaCorrespondence/FockModels/EveryCharacterE.lean` (original only)

All paths are under `src/Development/AutomorphicArithmetic/`.

## Layer 4: the inputs the key claim rests on

Meanings below are read from the Lean statements. They have not been checked against the
literature.

### `Row0b`: Galois representations

File: `Foundations/GaloisRepresentations/TypeConditions/WeightsConjBis.lean`.

The statement covers:

- every CM number field `E`, prime `l` and isomorphism `ι : Q̄_l ≃ ℂ`;
- every regular algebraic cuspidal representation `π` of `GL_a` over `E`, polarized by a Hecke
  character of the maximal real subfield.

For each such `π` it gives an `l`-adic Galois representation, with a weight and Hodge-Tate
data compatible with a local correspondence. In the literature, a statement of this kind is a
major theorem proved through the geometry of Shimura varieties. Here it is proved as
`galoisLocalGlobalStrong_recParameter`, from theta lifts:

- `Foundations/GaloisRepresentations/IntegralStructures/RowSrc.lean`:
  `galoisLocalGlobalStrong_recParameter`
- `Foundations/GaloisRepresentations/IntegralStructures/GaloisRepresentationsOfThetaLift.lean`:
  `galoisRepresentations_of_thetaLift`, from `TLiftK` and a geometric input `geoOne_holds`

### `TLiftK`: the theta-lift statement

- Statement: `Foundations/GaloisRepresentations/ThetaParseval/HalfIndexLattices/TLiftK.lean`
- Proof: `Foundations/GaloisRepresentations/ThetaParseval/ThetaKernels/TLiftK.lean`, by
  `UpperTheory.TP.tLift_holds_k`

`TLiftK` is about lifts between hermitian and skew-hermitian spaces over CM fields, for all
large dimensions. It is long; read it in full before relying on any summary.

### `RecTExists`: local Langlands existence

- Statement: `Foundations/LocalLanglands/IsRecTOfIsRec.lean`
- Proof: `Foundations/LocalLanglands/LocalCentralUnits/RecTExists.lean`

At every finite place of every number field, it gives a correspondence from irreducible
representations of `GL` to Weil-Deligne representations, satisfying `IsRecT`.

### `VWin`: the analytic window statement

- Statement: `CharacterBoxes/ExistsPageN.lean`
- Proof: `vwin_of_row` in
  `AutomorphicVarieties/ModularityArgument/ThresholdArguments/DenseThresholdCases/VwinOfRow.lean`

It says `VWinAt ψ 401` for every character `ψ`. That is a counting condition holding on a
window `[Y, Y²]`, for every `eps` in `(0, 1/52)`. It is proved from `Row0b`.

### `OpenLiteratureStatements`: the literature bundle

File: `ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean`.

The bundle has three fields:

- `caraianiLocalGlobalDual`
- `localLanglandsExists`
- `galoisRepOfPolarizedPairLit`

The final theorem does **not** assume them. `everyCharacter_of_row` fills all three with theorems proved in the project:
the Galois-representation theorem twice, and `recTExists` once.

The same file then derives 195 consequences of the form `… (O : OpenLiteratureStatements) : …`.
Most conclude a formal statement of a published result (`GlobalTheory.Published.*`, 162
distinct names; see [LITERATURE.md](LITERATURE.md)). They are proved like this (counted by a
script over the file):

| How it is proved | Count |
|---|---|
| A theorem elsewhere in the project, not using `O` (32 of them a `*_holds` theorem) | 152 |
| Other consequences, passing `O` along | 30 |
| A field of `O` directly (e.g. `O.localLanglandsExists`) | 3 |

So everything depends on `O` only through its three fields, and the final theorem fills those
with theorems proved in the project. The published results are proved, not assumed.

**This matters.** Formal statements of published theorems that were *assumed* would be the
classic place for a large formal proof to go wrong: a slightly misstated "known result" can
make anything provable. Here they are proved, so a misstatement can't introduce a false
assumption. Comparator's axiom check (only `propext`, `Quot.sound`, `Classical.choice`) is
the definitive test, once a full build exists.

## The libraries

What each top-level folder seems to hold, judged by folder and declaration names only.

| Library | Share of the fork | Main folders |
|---|---|---|
| `Development` | 76% of lines | `AutomorphicArithmetic` (the whole route to the key claim), `AbelianVarietyTheory`, `AutomorphicSpectrum`, `EtaleCohomology`, `ResolutionOfSingularities`, `WeilBound`, `DiscreteGroups` |
| `Formalism` | 14% | 96 topic folders: gamma factors, Hermitian lattices, formal groups, Frobenius orbits, Gauss sums, Galois cohomology… |
| `GroundTheory` | 5% | local and global fields, p-adic Hodge theory, Brauer groups, Tate and profinite cohomology, heights and theta |
| `ReciprocityTheory` | 3% | class field theory, Chebotarev, geometry of numbers, reductive groups, and `Hypotheses` (proved, like the rest) |
| `CompanionTheory` | 1% | real groups, Harish-Chandra modules, spectral geometry |
| `PositivityTheory` | < 1% | automorphic forms, `PublishedTheorems`, representations |
| `Lemmata` | < 1% | small numbered lemma families (`FirstBlockLemmaA`…, `GeneralBFact*`) |

The original's `BuildAid` (five files) is not in the fork. Each of its files only adds a
namespace to Lean's deny list for library suggestions, which doesn't affect the proof.
