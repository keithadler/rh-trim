Measured weights for the 41 sub-roadmaps, from the kernel export of the formal proof (lean4export of the five main theorems: 1,468,414 declarations). For each sub-roadmap, the declarations its README names were looked up in the export.

- **Reaches**: the largest dependency closure among its named declarations, as a share of the whole proof (expression nodes) and in declarations.
- **Owns**: the largest share of the proof that can only be reached through one of its named declarations (dominator tree).

Together, the 2,023 declarations the roadmap names reach 699,515 declarations: **38.4% of the formal proof** (36.5% of the project's own part).

| Sub-roadmap | Names found | Reaches | Declarations | Via | Owns |
|---|---:|---:|---:|---|---:|
| UniformWildKernelBounds | 214 | 7.73% | 229,107 | `UpperTheory.V.Z.Sym.W.unitary_three_automorphy_dense_of_prints` | 0.60% |
| ArithmeticVolumesAndIntegralFormsOnUnitaryShimuraVarieties | 53 | 7.34% | 205,680 | `GlobalTheory.FlatRootTwist.flat_root_twist` | 0.17% |
| HeightsForLogSingularMetrics | 35 | 7.29% | 202,511 | `GlobalTheory.T.slope_bound_of_line_large_degree` | 0.14% |
| ProjectiveModelsAndPeriodBoundsOnShimuraVarieties | 34 | 5.67% | 177,086 | `GlobalTheory.CompanionTheory.Ar.Top.partI_holds` | 0.14% |
| HeckeIdealsAndTaylorWilesRelations | 50 | 5.64% | 196,128 | `UpperTheory.V.Hi.hecke_ideal_point_properties` | 0.04% |
| GluedTargetAndDivisionInequality | 118 | 4.30% | 167,176 | `GlobalTheory.RunJoin.exists_genOK` | 0.38% |
| RowTowerAndRallisIdentities | 85 | 3.93% | 147,152 | `GlobalTheory.T.tower_stage_successor_coefficients_alt` | 0.43% |
| HodgeTateLatticesAndLubinTateLogarithms | 36 | 3.27% | 142,610 | `GlobalTheory.ChF.colength_bound_split_place_chart` | 0.02% |
| DiscreteSeriesCoefficientsAndAutomorphicMetrics | 39 | 3.11% | 145,353 | `GlobalTheory.T.toroidalFlagProportionality_of_goodChernWeil` | 0.18% |
| SeesawForThetaChains | 72 | 2.76% | 121,364 | `GlobalTheory.T.seeSawTwistPlaceLaws_of_rootOfUnityRescaling` | 0.19% |
| SelmerLengthBoundsAndLocalLifting | 95 | 2.67% | 94,702 | `GlobalTheory.T.localLiftingTheoremB_of_blochKato_tateDuality_eulerChar` | 0.53% |
| LocalGainOfThetaChains | 124 | 2.65% | 128,691 | `GlobalTheory.T.fivePointLaws_trueChains` | 0.24% |
| BesselPoincareSeriesAndGramBounds | 102 | 2.31% | 115,875 | `GlobalTheory.wuDecayOfGap` | 0.01% |
| MultiplierIdealsOfPairsAndPointSeparation | 33 | 2.28% | 121,721 | `NadelVanishingSeparation.NSI.isolatedNonKltDivisor` | 0.01% |
| ThetaKernelsForUnitaryDualPairs | 92 | 2.09% | 110,208 | `GlobalTheory.TwBound.tw_bound` | 0.08% |
| BernoulliBoundsForClassGroupEigenspaces | 90 | 2.07% | 121,730 | `UpperTheory.V.ZK.bOdd` | 0.15% |
| BaseChangeAndGaloisRepresentationsForUnitaryGroups | 23 | 1.75% | 96,515 | `UpperTheory.Gal.Int.Row.dz_of_cusp` | 0.01% |
| ThetaChainsOnDefiniteUnitaryGroups | 70 | 1.71% | 105,763 | `GlobalTheory.T.exists_thetaVectorFamily_of_curveDatum` | 0.00% |
| FiniteReductiveGroups | 41 | 1.63% | 89,485 | `UpperTheory.Gal.InertialTypesAlt.lblOf_holds` | 0.02% |
| LocalFactorsOfTwistsAndTypes | 27 | 1.59% | 86,295 | `PositivityTheory.Gud.Fin.genericUnitaryDualGL_holds` | 0.01% |
| CongruenceModulesOfThetaLifts | 91 | 1.50% | 95,360 | `GlobalTheory.T.doubling_integrals_vanish_of_all_lifts_vanish` | 0.05% |
| ChowFormsAndHeightsOfSubvarieties | 26 | 1.11% | 79,828 | `GlobalTheory.CompanionTheory.Ar.Short.mahlerSection` | 0.01% |
| GeneralizedRiemannHypothesisFromWindowBounds | 44 | 1.09% | 86,273 | `UpperTheory.Top.zeroFreeAll_of_topG` | 0.03% |
| ThetaChainsAndFrobeniusPrimeSums | 51 | 1.05% | 84,123 | `GlobalTheory.T.goodPrimeWeightHypotheses_of_depthParameters` | 0.02% |
| OrbitMeasuresOnAdelicGroups | 14 | 1.03% | 77,584 | `GlobalTheory.T.genLin_tamagawa_volume` | 0.00% |
| SlopesOfHermitianVectorBundles | 28 | 1.02% | 78,397 | `GlobalTheory.HSShort.SlopeTop.slopeBound` | 0.02% |
| FrobeniusRestrictedRieszSums | 45 | 0.88% | 71,606 | `IsCyclotomicExtension.Rat.inertiaDegIn_eq` | 0.02% |
| SingularHermitianMetricsAndL2Methods | 19 | 0.83% | 64,534 | `GlobalTheory.l2ExtensionLogCanonical'` | 0.05% |
| ThetaLiftsForDefiniteUnitaryGroups | 66 | 0.82% | 67,953 | `GlobalTheory.ThK.Dbl.nu_pow_ne_one` | 0.00% |
| PositivityOfDirichletSeriesWithKernels | 61 | 0.82% | 65,399 | `Formalism.FourierDecayAlt.P.stationary_phase_holomorphic` | 0.02% |
| LengthBoundsInPadicFamilies | 30 | 0.75% | 66,132 | `GlobalTheory.Cut.ccOff` | 0.02% |
| TensorInductionAndFiniteGroupInputs | 36 | 0.72% | 61,612 | `GlobalTheory.Shin.kills_of_norm_one_of_pairing_prime` | 0.01% |
| RiemannHypothesisStatementsAndConsequences | 62 | 0.66% | 59,168 | `Deduction.poleData_char` | 0.00% |
| RieszSumsOverPrimesAndExceptionalZeros | 13 | 0.65% | 59,331 | `NumberField.exists_ideal_in_class_of_norm_le` | 0.00% |
| WachLatticesOverTheCyclotomicTower | 52 | 0.64% | 50,708 | `GlobalTheory.ResidueBound.resBound_dsum` | 0.02% |
| AdelicHeightsAndSuccessiveMinima | 10 | 0.61% | 56,868 | `NumberField.prod_abs_eq_one` | 0.00% |
| QuadraticTwistSelectionOverPrimes | 10 | 0.60% | 56,534 | `DirichletCharacter.LFunction_apply_one_ne_zero` | 0.00% |
| ReducibilityIdealsAndUltrafilterPatching | 40 | 0.59% | 45,445 | `UpperTheory.V.Alg.M.main_holds` | 0.07% |
| HermitianFormsAndLattices | 28 | 0.55% | 53,081 | `NumberField.dedekindZeta_residue` | 0.00% |
| IntegralWeylModulesOfGeneralLinearGroups | 14 | 0.31% | 35,337 | `Formalism.HN.muMaxDef` | 0.00% |
| TaylorBoundsAndDepthsOnHeightTwoFormalGroups | 4 | 0.04% | 7,723 | `Formalism.L2.FormalSeriesBounds.RawChart.AxesSt` | 0.00% |

Method and tools: https://github.com/keithadler/rh-trim (an export indexer and a dominator-tree analysis; no proof code). Sizes count distinct expression nodes in each declaration's statement and proof, a rough stand-in for the work a kernel does.
