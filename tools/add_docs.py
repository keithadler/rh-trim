"""Insert docstrings before the key-chain declarations of the fork. Comments only: no proof text
changes. Each docstring ends with a marker so they can be told apart from the original's one
docstring. Refuses to insert twice.

usage: add_docs.py FORK_SRC
"""
import os, re, sys
root = sys.argv[1]
MARK = '(Added in this fork; not in the original.)'

D = 'Development/AutomorphicArithmetic/'
DOCS = [
 # ---- the five theorems -------------------------------------------------------------------------
 ('Main.lean', 'riemannHypothesis',
  "The Riemann Hypothesis, exactly as Mathlib states it (`RiemannHypothesis`): every zero `s` of\n"
  "`riemannZeta` that is not a trivial zero `-2(n+1)` and is not `s = 1` has `s.re = 1/2`.\n"
  "Proved by `rhOfAll`, which reduces it to the key claim `allChi`."),
 ('Main.lean', 'riemannZeta_eq_zero_re',
  "The same statement, written out as `RiemannZetaZerosOnLine` in `Statements.lean`; it is\n"
  "definitionally Mathlib's `RiemannHypothesis`."),
 ('Main.lean', 'LFunction_ne_zero_of_half_lt_re',
  "GRH for Dirichlet L-functions in half-plane form: `L(χ, s) ≠ 0` whenever `Re s > 1/2`, for every\n"
  "modulus `N` and every Dirichlet character `χ` mod `N`, imprimitive ones included, except the\n"
  "trivial character at `s = 1`. This *is* the key claim (`allChi`); everything deep is behind it."),
 ('Main.lean', 'LFunction_eq_zero_re',
  "Every zero of `L(χ, s)` in the critical strip `0 < Re s < 1` lies on `Re s = 1/2`, for every\n"
  "modulus and every character. The second component of `claimAll`, from `Claim.strip`."),
 ('Main.lean', 'LFunction_eq_zero_re_of_isPrimitive',
  "The critical-line statement for primitive characters, from `critAll` (`Formalism.VW.critLine`)."),
 # ---- the statements --------------------------------------------------------------------------
 ('Statements.lean', 'RiemannZetaZerosOnLine',
  "RH written out with Mathlib's `riemannZeta`: nontrivial zeros other than `s = 1` lie on\n"
  "`Re s = 1/2`. Imports only Mathlib."),
 ('Statements.lean', 'DirichletLNonvanishingRightOfHalf',
  "No Dirichlet L-function vanishes right of `Re s = 1/2` (trivial character at `s = 1` excepted).\n"
  "Textually identical to `UpperTheory.EveryCharacter` and `Claim.HalfPlane`."),
 ('Statements.lean', 'DirichletLZerosOnLine',
  "Zeros of Dirichlet L-functions in the critical strip lie on `Re s = 1/2`; all characters."),
 ('Statements.lean', 'PrimitiveDirichletLZerosOnLine',
  "Zeros of primitive Dirichlet L-functions in the critical strip lie on `Re s = 1/2`."),
 # ---- the top of the proof ----------------------------------------------------------------------
 ('Supplements/Kernels/MainTheorems.lean', 'allChi',
  "THE KEY CLAIM: no Dirichlet L-function vanishes right of `Re s = 1/2`. Proved by\n"
  "`UpperTheory.FinalTheorems.everyCharacter` in `CharacterBoxes/MainConclusion.lean`, whose import\n"
  "closure is almost the whole project. Everything else in `Main` follows from this by short\n"
  "textbook arguments over Mathlib."),
 ('Supplements/Kernels/MainTheorems.lean', 'rhOfAll',
  "RH from the key claim, via `Formalism.VW.rh_of_every` (modulus 1, where `L = ζ`)."),
 ('Supplements/Kernels/MainTheorems.lean', 'critAll',
  "The critical line for primitive characters from the key claim, via `Formalism.VW.critLine`\n"
  "(the functional equation reflects a zero left of 1/2 to one right of 1/2)."),
 ('Supplements/Kernels/MainTheorems.lean', 'claimAll',
  "The three `Claim` forms (half-plane, strip, zeta) from the key claim; see `ClaimStrip.lean`."),
 (D + 'CharacterBoxes/EveryCharacter.lean', r'UpperTheory\.EveryCharacter',
  "The key claim as the deep part states it. Textually identical to\n"
  "`DirichletLNonvanishingRightOfHalf` in `Statements.lean`."),
 # ---- the classical reduction -------------------------------------------------------------------
 ('Formalism/GammaFactorNonvanishing/RhOfRight.lean', r'Formalism\.VW\.rh_of_right',
  "If `ζ` has no zero with `Re s > 1/2` (other than at `s = 1`), then RH holds. A zero left of 1/2\n"
  "is reflected by Mathlib's functional equation `riemannZeta_one_sub`; `Γ`, the power of `2π` and\n"
  "the cosine factor are shown nonzero, and trivial zeros are excluded by hypothesis."),
 ('Formalism/GammaFactorNonvanishing/CritLine.lean', r'Formalism\.VW\.gammaFactor_ne_zero',
  "The gamma factor of a Dirichlet L-function does not vanish for `Re s > 0`."),
 ('Formalism/GammaFactorNonvanishing/CritLine.lean', r'Formalism\.VW\.critLine',
  "Critical line for a primitive character from the key claim: a zero with `Re s < 1/2` gives, by\n"
  "the functional equation of the completed L-function, a zero of `L(χ⁻¹, 1 - s)` with\n"
  "`Re(1 - s) > 1/2`, which the key claim forbids."),
 ('Formalism/GammaFactorNonvanishing/CritLine.lean', r'Formalism\.VW\.rh_of_every',
  "RH from the key claim: take the modulus-1 character, whose L-function is `ζ`, then apply\n"
  "`rh_of_right`."),
 (D + 'CharacterBoxes/HalfPlane.lean', r'Claim\.HalfPlane',
  "The key claim once more, in the `Claim` namespace (textually identical)."),
 (D + 'CharacterBoxes/HalfPlane.lean', r'Claim\.Strip',
  "Critical-strip zeros of every Dirichlet L-function lie on `Re s = 1/2`."),
 (D + 'CharacterBoxes/HalfPlane.lean', r'Claim\.Zeta',
  "RH, written so that `Claim.zeta_iff` can prove it equals Mathlib's `RiemannHypothesis` by `Iff.rfl`."),
 (D + 'CharacterBoxes/ClaimStrip.lean', 'strip',
  "Half-plane to strip: pass to the primitive character (Euler factors do not vanish for `Re s > 0`),\n"
  "reflect with the functional equation, and apply the half-plane claim."),
 (D + 'CharacterBoxes/ClaimStrip.lean', 'zeta',
  "Half-plane to RH: zeros with `0 < Re s < 1` via `strip` at modulus 1; `Re s ≥ 1` has no zeros\n"
  "(Mathlib); `Re s ≤ 0` reflects through `completedRiemannZeta_one_sub`."),
 # ---- the deep part: how the key claim is assembled ---------------------------------------------
 (D + 'CharacterBoxes/MainConclusion.lean', r'UpperTheory\.FinalTheorems\.everyCharacter_of_row',
  "The key claim from one input, `Row0b` (Galois representations attached to polarized regular\n"
  "algebraic cuspidal representations, matched with local Langlands `IsRecT`). It feeds that input\n"
  "into `every_character_of_literature_of_vWin` three ways: as the literature bundle\n"
  "`OpenLiteratureStatements` (with `recTExists`), and through `vwin_of_row` for the analytic\n"
  "window statement `VWin`."),
 (D + 'CharacterBoxes/MainConclusion.lean', r'UpperTheory\.FinalTheorems\.everyCharacter',
  "The key claim, unconditionally: `everyCharacter_of_row` applied to\n"
  "`galoisLocalGlobalStrong_recParameter`, which the project proves from theta lifts. Of the five\n"
  "theorems in the original that conclude `EveryCharacter`, this is the only one with no hypotheses."),
 (D + 'ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean',
  r'UpperTheory\.LiteratureTheorems\.OpenLiteratureStatements',
  "Three results from the research literature, bundled. In the final theorem they are not assumed:\n"
  "`everyCharacter_of_row` supplies them from theorems proved in the project.\n"
  "- `caraianiLocalGlobalDual`, `galoisRepOfPolarizedPairLit`: both `UpperTheory.One.M.Row`, i.e.\n"
  "  `Row0b` with local Langlands `IsRecT` (Galois representations with local-global compatibility).\n"
  "- `localLanglandsExists`: `RecTExists` (a local correspondence exists at every finite place).\n"
  "195 consequences taking `O` follow in this file. 152 are proved without `O`, by theorems\n"
  "elsewhere in the project; 30 pass `O` to other consequences; 3 read a field of `O`. So\n"
  "everything depends on `O` only through these three fields."),
 (D + 'ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean',
  r'UpperTheory\.LiteratureTheorems\.every_character_of_literature_of_vWin',
  "The key claim from the literature bundle and the analytic window statement `VWin`. The heart of\n"
  "the argument is `UpperTheory.Lit.every_character_of_theta_integrals_local_matching`, fed with\n"
  "theta-integral, covolume and local-Langlands inputs derived from `O`."),
 (D + 'AutomorphicVarieties/ModularityArgument/ThresholdArguments/DenseThresholdCases/VwinOfRow.lean',
  r'UpperTheory\.One\.vwin_of_row',
  "The analytic window statement `VWin` from `Row0b`, via\n"
  "`UpperTheory.One.Join.automorphic_window_of_inputs` and base change `baseChangeN`."),
 (D + 'CharacterBoxes/ExistsPageN.lean', 'VWinAt',
  "The window condition for one character `ψ` with constant `Ct`: for every `eps` in `(0, 1/52)` and\n"
  "every page-count function `e`, there are `J ≥ 1` and `X0` such that for all `X ≥ X0` and every\n"
  "admissible pair `(q, d)` some `Y` in `[X^(1/J), √X]` makes `VAt` hold on all of `[Y, Y²]`."),
 (D + 'CharacterBoxes/ExistsPageN.lean', 'VWin',
  "`VWinAt ψ 401` for every character `ψ`: the analytic input with the constant 401."),
 (D + 'Foundations/GaloisRepresentations/IntegralStructures/RowSrc.lean',
  r'galoisLocalGlobalStrong_recParameter',
  "`Row0b` for the local correspondence `recT`, proved from the theta-lift statement `tLiftK` by\n"
  "`galoisRepresentations_of_thetaLift`. This is where the existence of Galois representations,\n"
  "normally taken from the geometry of Shimura varieties, enters the proof."),
 (D + 'Foundations/GaloisRepresentations/IntegralStructures/GaloisRepresentationsOfThetaLift.lean',
  r'galoisRepresentations_of_thetaLift',
  "Galois representations (`Row0b recT`) from theta lifts (`TLiftK`), through\n"
  "`galoisLocalGlobalStrong_of_geometry_lift` and the geometric input `geoOne_holds`."),
 (D + 'Foundations/GaloisRepresentations/TypeConditions/WeightsConjBis.lean', 'Row0b',
  "For every CM number field `E`, prime `l`, isomorphism `ι : Q̄_l ≃ ℂ` and `a ≥ 1`, and every\n"
  "regular algebraic cuspidal representation `π` of `GL_a` over `E` that is polarized by a Hecke\n"
  "character `χ` of the maximal real subfield, there is a Galois representation\n"
  "`r : Gal(Ω/E) → GL_a(Q̄_l)` with a weight and Hodge-Tate multisets satisfying `PropsB Rc`\n"
  "(compatibility with the local correspondence `Rc`). The standard statement of this kind is a\n"
  "major theorem in the literature."),
 (D + 'Foundations/UnitarySphericalFixing/SatakeParameters/RecT.lean', r'UpperTheory\.One\.M\.Row',
  "`Row0b` for the local correspondence `IsRecT`."),
 (D + 'Foundations/LocalLanglands/IsRecTOfIsRec.lean', 'RecTExists',
  "Local Langlands existence: at every finite place `w` of every number field `E`, there is a\n"
  "correspondence `rc` from irreducible representations of `GL` over the completion to\n"
  "Weil-Deligne representations satisfying `IsRecT`."),
 (D + 'Foundations/LocalLanglands/LocalCentralUnits/RecTExists.lean', r'UpperTheory\.Zero\.LLC\.recTExists',
  "`RecTExists`, proved in the project."),
 (D + 'Foundations/GaloisRepresentations/ThetaParseval/HalfIndexLattices/TLiftK.lean', 'TLiftK',
  "The theta-lift statement behind the Galois representations: for every CM field `E` with good\n"
  "base data and every hermitian space `X` of dimension `n ≥ 1`, there is `d₀` such that for all\n"
  "skew-hermitian `W` of dimension `d ≥ d₀` and Hecke characters satisfying the stated conditions,\n"
  "the lift exists with the stated properties. Read the full statement before relying on this\n"
  "summary; it is long."),
 (D + 'Foundations/GaloisRepresentations/ThetaParseval/ThetaKernels/TLiftK.lean', r'UpperTheory\.TP\.K\.tLiftK',
  "`TLiftK`, proved in the project (`UpperTheory.TP.tLift_holds_k`)."),
]

declre_t = r'^(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable|partial|unsafe|nonrec)\s+)*(?:theorem|lemma|def|abbrev|structure|class|inductive)\s+{}(?=[\s:({{\[]|$)'
added = missing = 0
for rel, name, text in DOCS:
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        print('MISSING FILE', rel); missing += 1; continue
    t = open(p, encoding='utf-8').read()
    m = re.search(declre_t.format(name), t, re.M)
    if not m:
        print('MISSING DECL', name, 'in', rel); missing += 1; continue
    start = m.start()
    while start > 0:                       # attribute lines above belong to the declaration
        prev = t.rfind('\n', 0, start - 1) + 1
        if t.startswith('@[', prev): start = prev
        else: break
    if t[:start].rstrip().endswith('-/'):
        continue                           # already documented
    doc = '/-- ' + text.replace('\n', '\n    ') + '\n\n    ' + MARK + ' -/\n'
    t = t[:start] + doc + t[start:]
    open(p, 'w', encoding='utf-8').write(t); added += 1
print(f'docstrings added: {added}, not found: {missing}')
