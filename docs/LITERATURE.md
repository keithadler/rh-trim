# Published results formalized in the proof

The literature bundle in
`src/Development/AutomorphicArithmetic/ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean`
derives 195 consequences that take the bundle `O` as an argument. Most conclude one of the 162
formal statements below, all in the namespace `GlobalTheory.Published`.

**These are proved in the project, not assumed.**

- 152 of the consequences are proved without `O`, by theorems elsewhere in the project.
- 30 pass `O` on to other consequences.
- 3 read one of `O`'s three fields.

The final theorem fills those three fields with theorems the project proves (see
[PROOF-MAP.md](PROOF-MAP.md)).

The second column only splits the Lean name into words. Whether each formal statement
matches the published theorem it is named after has not been checked. For soundness that
doesn't matter, because they are proved. For *understanding* the proof it does matter: it's
the first thing a reader would want to audit.

| Lean name | Name split into words |
|---|---|
| `AbMulNSt` | Ab Mul NSt |
| `AbelianDeRham` | Abelian De Rham |
| `AbelianLifting` | Abelian Lifting |
| `AlgebraicCharacterWD` | Algebraic Character WD |
| `ArCalc` | Ar Calc |
| `ArDegree` | Ar Degree |
| `ArithHilbertSamuel` | Arith Hilbert Samuel |
| `AutomorphicFormsFiniteGL` | Automorphic Forms Finite GL |
| `BaseChangeDefiniteUnitaryGroup` | Base Change Definite Unitary Group |
| `BaseChangeIsobaricTransfer` | Base Change Isobaric Transfer |
| `BernsteinUnitaryProductIrreducible` | Bernstein Unitary Product Irreducible |
| `BernsteinZelevinskyFiniteness` | Bernstein Zelevinsky Finiteness |
| `BhattScholzeCrystallineLattices` | Bhatt Scholze Crystalline Lattices |
| `BhattScholzeIntegral` | Bhatt Scholze Integral |
| `BlochKatoLocal` | Bloch Kato Local |
| `BorelCasselman` | Borel Casselman |
| `BrauerDegreeZero` | Brauer Degree Zero |
| `CMCurveGoodOutsidePrimeSt` | CMCurve Good Outside Prime St |
| `CasselmanWallach` | Casselman Wallach |
| `ChebotarevDegreeOne` | Chebotarev Degree One |
| `ChevalleyUnits` | Chevalley Units |
| `ChowFormExists` | Chow Form Exists |
| `ClozelCohomological` | Clozel Cohomological |
| `ClozelPurity` | Clozel Purity |
| `ComplexMultiplicationJSt` | Complex Multiplication JSt |
| `CuspBounded` | Cusp Bounded |
| `CuspDecayBound` | Cusp Decay Bound |
| `CuspDecaySobolev` | Cusp Decay Sobolev |
| `CuspFormsBoundedGL` | Cusp Forms Bounded GL |
| `CuspRapidDecay` | Cusp Rapid Decay |
| `CuspTraceClass` | Cusp Trace Class |
| `CuspidalMirabolic` | Cuspidal Mirabolic |
| `CuspidalMultiplicityOne` | Cuspidal Multiplicity One |
| `CuspidalSpectrumGL` | Cuspidal Spectrum GL |
| `CycleHeights` | Cycle Heights |
| `DeRhamPotSemistable` | De Rham Pot Semistable |
| `DeligneRibet` | Deligne Ribet |
| `DepthZeroInduction` | Depth Zero Induction |
| `DepthZeroJacquetInjective` | Depth Zero Jacquet Injective |
| `DepthZeroSupport` | Depth Zero Support |
| `DiscreteSeriesClassification` | Discrete Series Classification |
| `DiscreteSeriesCover` | Discrete Series Cover |
| `DiscreteSeriesCoverExists` | Discrete Series Cover Exists |
| `DiscreteSeriesExists` | Discrete Series Exists |
| `DiscreteSeriesHermitianUnique` | Discrete Series Hermitian Unique |
| `DiscreteSeriesLowestKType` | Discrete Series Lowest KType |
| `DiscreteSeriesUpqExists` | Discrete Series Upq Exists |
| `DixmierMalliavinFactorisation` | Dixmier Malliavin Factorisation |
| `DoublingMethodLocalZetaIntegrals` | Doubling Method Local Zeta Integrals |
| `DualAbelianScheme` | Dual Abelian Scheme |
| `EllipticMainTheoremCM` | Elliptic Main Theorem CM |
| `EssSquareIntegrableSegments` | Ess Square Integrable Segments |
| `FlathFactorisation` | Flath Factorisation |
| `FlathTensorProduct` | Flath Tensor Product |
| `FontaineBcris` | Fontaine Bcris |
| `FormalAlgebraisation` | Formal Algebraisation |
| `FormalDegreeCompactDual` | Formal Degree Compact Dual |
| `GKGlobalisation` | GKGlobalisation |
| `GLHoweDuality` | GLHowe Duality |
| `GelfandKazhdanDual` | Gelfand Kazhdan Dual |
| `GenericUnitaryDualGL` | Generic Unitary Dual GL |
| `GenericUnlinkedGL` | Generic Unlinked GL |
| `GeometricLemma` | Geometric Lemma |
| `GeometricLemmaFiltration` | Geometric Lemma Filtration |
| `GlobalArtinReciprocity` | Global Artin Reciprocity |
| `GoodChernWeil` | Good Chern Weil |
| `GreenCuspidal` | Green Cuspidal |
| `GreenRegularCharacters` | Green Regular Characters |
| `GreenSeriesSt` | Green Series St |
| `GrothendieckDeformation` | Grothendieck Deformation |
| `GrothendieckMessing` | Grothendieck Messing |
| `GrothendieckRingPolynomial` | Grothendieck Ring Polynomial |
| `HarishChandraAnalyticity` | Harish Chandra Analyticity |
| `HarishChandraFinite` | Harish Chandra Finite |
| `HarishChandraModules` | Harish Chandra Modules |
| `HasseNormSt` | Hasse Norm St |
| `HeckeLAdicCharacter` | Hecke LAdic Character |
| `HeckeLAdicCharacterAbove` | Hecke LAdic Character Above |
| `HeckeLAdicCharacterCrystalline` | Hecke LAdic Character Crystalline |
| `HeckeLAdicCharacterDeRham` | Hecke LAdic Character De Rham |
| `HeckeLAdicParameterAboveAlt` | Hecke LAdic Parameter Above Alt |
| `HeckeLEntireAndNonzeroAtOne` | Hecke LEntire And Nonzero At One |
| `HeckeLPartialContinuation` | Hecke LPartial Continuation |
| `HeckeTateFunctionalEquation` | Hecke Tate Functional Equation |
| `HermitianHassePrinciple` | Hermitian Hasse Principle |
| `HermitianLocalGlobal` | Hermitian Local Global |
| `HilbertClassFieldJ` | Hilbert Class Field J |
| `HolomorphicDiscreteSeries` | Holomorphic Discrete Series |
| `HoweDualityReal` | Howe Duality Real |
| `IdealInvariantsOneOrbitSt` | Ideal Invariants One Orbit St |
| `InducedSimpleLowestAlcove` | Induced Simple Lowest Alcove |
| `IrreducibleAdmissibleGL` | Irreducible Admissible GL |
| `JacquetShalika` | Jacquet Shalika |
| `JacquetShalikaRigidity` | Jacquet Shalika Rigidity |
| `KFiniteVectorsUnitary` | KFinite Vectors Unitary |
| `KawamataViehweg` | Kawamata Viehweg |
| `KudlaSplittingSplitUnitary` | Kudla Splitting Split Unitary |
| `L2ExtensionLogCanonical` | L2 Extension Log Canonical |
| `LandherrSt` | Landherr St |
| `LanglandsExhaustionGL` | Langlands Exhaustion GL |
| `LanglandsMultisegments` | Langlands Multisegments |
| `Linnik` | Linnik |
| `LocalConverseGL` | Local Converse GL |
| `MetaplecticRepresentation` | Metaplectic Representation |
| `MoyPrasadJacquetIso` | Moy Prasad Jacquet Iso |
| `NadelVanishingAndNonKltDivisor` | Nadel Vanishing And Non Klt Divisor |
| `NefNumerics` | Nef Numerics |
| `PartialZetaFunctionalEquation` | Partial Zeta Functional Equation |
| `PointSeparationPair` | Point Separation Pair |
| `PoitouTateNormalised` | Poitou Tate Normalised |
| `Principalisation` | Principalisation |
| `PrismaticDieudonneHodge` | Prismatic Dieudonne Hodge |
| `QuadraticClassFieldTheory` | Quadratic Class Field Theory |
| `RadfordShufflePolynomial` | Radford Shuffle Polynomial |
| `RallisInnerProductConvergent` | Rallis Inner Product Convergent |
| `RayCharacterArtin` | Ray Character Artin |
| `RayClassFieldSt` | Ray Class Field St |
| `RealMetaplecticRepresentation` | Real Metaplectic Representation |
| `RegularAlgebraicPurity` | Regular Algebraic Purity |
| `SchurOrthogonalitySquareIntegrable` | Schur Orthogonality Square Integrable |
| `SegmentRepresentation` | Segment Representation |
| `SemiAbelianHomExtension` | Semi Abelian Hom Extension |
| `SemiAbelianLieSeminegative` | Semi Abelian Lie Seminegative |
| `SemistableReductionSt` | Semistable Reduction St |
| `SerreHolomorphicSections` | Serre Holomorphic Sections |
| `SiegelEisensteinContinuation` | Siegel Eisenstein Continuation |
| `SiegelKlingenDeligneRibet` | Siegel Klingen Deligne Ribet |
| `SiegelSetUnitary` | Siegel Set Unitary |
| `SiegelToroidalIntegral` | Siegel Toroidal Integral |
| `SiegelWeilUnitaryConvergent` | Siegel Weil Unitary Convergent |
| `SiegelWeilUnitarySchrodinger` | Siegel Weil Unitary Schrodinger |
| `SquareIntegrableSegment` | Square Integrable Segment |
| `StandardCosocleGL` | Standard Cosocle GL |
| `StandardFunctorsFiniteLength` | Standard Functors Finite Length |
| `StoneVonNeumann` | Stone Von Neumann |
| `StrongApproxSU` | Strong Approx SU |
| `TemperedProductOfSquareIntegrable` | Tempered Product Of Square Integrable |
| `ThetaRationalInvariance` | Theta Rational Invariance |
| `ToroidalCompactification` | Toroidal Compactification |
| `ToroidalForFanKS` | Toroidal For Fan KS |
| `TotallyDisjointProductIrreducible` | Totally Disjoint Product Irreducible |
| `UnitaryIrreducibleAdmissible` | Unitary Irreducible Admissible |
| `UnlinkedProductIrreducible` | Unlinked Product Irreducible |
| `UnramifiedDoublingGL` | Unramified Doubling GL |
| `UnusedSlot72` | Unused Slot72 |
| `VolGe` | Vol Ge |
| `VolNef` | Vol Nef |
| `WeberRayFieldSt` | Weber Ray Field St |
| `WeilRepresentationExists` | Weil Representation Exists |
| `WeilRepresentationUnitaryPair` | Weil Representation Unitary Pair |
| `WeilSiegelFormulaUnitary` | Weil Siegel Formula Unitary |
| `WeilThetaConvergence` | Weil Theta Convergence |
| `WeylBranching` | Weyl Branching |
| `ZelevinskyPolynomialRing` | Zelevinsky Polynomial Ring |
| `cheb` | cheb |
| `chebotarevDegreeOne` | chebotarev Degree One |
| `chevalleyUnits` | chevalley Units |
| `chowFormExists` | chow Form Exists |
| `cmCurveGoodOutsidePrime` | cm Curve Good Outside Prime |
| `grothendieckDeformation` | grothendieck Deformation |
| `principalPolarisationOneSection` | principal Polarisation One Section |
| `serreHolomorphicSections` | serre Holomorphic Sections |
