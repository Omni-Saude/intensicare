"""
SOFA (Sequential Organ Failure Assessment) scoring engine.

Implements the SOFA score with 6 organ systems:
- Respiration (PaO2/FiO2 ratio)
- Coagulation (platelets)
- Liver (bilirubin)
- Cardiovascular (MAP + vasopressor use)
- Neurological (Glasgow Coma Scale)
- Renal (creatinine + urine output)

Each organ system scores 0-4; total SOFA score ranges 0-24.
Higher scores indicate more severe organ dysfunction.
"""

from __future__ import annotations

from dataclasses import dataclass, field

SOFA_VERSION = "SOFA-v2.0.0"  # CLINICALLY RATIFIED per RAT-CLINICAL-SCORING-01/02/03

# ─────────────────────────────────────────────────────────────────────────────
# Published SOFA thresholds (Vincent et al., Intensive Care Med 1996;22:707-710).
# The current implementation's values are authoritative and MUST NOT change;
# these named constants only replace inline literals with no behavior change.
# ─────────────────────────────────────────────────────────────────────────────

# Total-score mortality-risk bands (inclusive upper bound of each band)
SOFA_MORTALITY_RISK_LOW_MAX = 6
SOFA_MORTALITY_RISK_MODERATE_MAX = 9
SOFA_MORTALITY_RISK_HIGH_MAX = 12

# ─────────────────────────────────────────────────────────────────────────────
# Unified SOFA sepsis mortality risk classification (single source of truth)
# Used by both live scoring (SOFAResult.sepsis_mortality_risk) and replay
# (vitals._get_sofa_for_vital).
# ─────────────────────────────────────────────────────────────────────────────


def classify_sofa_mortality_risk(total_score: int) -> str:
    """Classify sepsis mortality risk from total SOFA score.

    SOFA ≥2 increase in mortality of ≈2-25%.
    SOFA 0-6: ~<10% mortality
    SOFA 7-9: ~15-20%
    SOFA 10-12: ~40-50%
    SOFA 13-14: ~50-60%
    SOFA 15-24: ~80-90%
    SOFA >15: ~>90%

    Returns 'low', 'moderate', 'high', or 'very_high'.
    """
    if total_score <= SOFA_MORTALITY_RISK_LOW_MAX:
        return "low"
    if total_score <= SOFA_MORTALITY_RISK_MODERATE_MAX:
        return "moderate"
    if total_score <= SOFA_MORTALITY_RISK_HIGH_MAX:
        return "high"
    return "very_high"

# Respiration — PaO2/FiO2 ratio (mmHg); inclusive lower bound of each score band
SOFA_RESP_PF_NORMAL = 400  # >= 400 -> 0
SOFA_RESP_PF_MILD = 300  # >= 300 -> 1
SOFA_RESP_PF_MODERATE = 200  # >= 200 -> 2
SOFA_RESP_PF_SEVERE = 100  # >= 100 (ventilated) -> 3, else -> 4

# Coagulation — platelets (x10^3/µL); inclusive lower bound of each score band
SOFA_PLATELETS_NORMAL = 150  # >= 150 -> 0
SOFA_PLATELETS_MILD = 100  # >= 100 -> 1
SOFA_PLATELETS_MODERATE = 50  # >= 50 -> 2
SOFA_PLATELETS_SEVERE = 20  # >= 20 -> 3, else -> 4

# Liver — bilirubin (mg/dL); exclusive upper bound of each score band
SOFA_BILIRUBIN_NORMAL = 1.2  # < 1.2 -> 0
SOFA_BILIRUBIN_MILD = 2.0  # < 2.0 -> 1
SOFA_BILIRUBIN_MODERATE = 6.0  # < 6.0 -> 2
SOFA_BILIRUBIN_SEVERE = 12.0  # < 12.0 -> 3, else -> 4

# Cardiovascular — MAP (mmHg) and vasopressor doses (µg/kg/min)
SOFA_MAP_NORMAL = 70  # MAP >= 70 (no pressors) -> 0, else -> 1
SOFA_DOPAMINE_LOW = 5  # dopamine <= 5 -> 2
SOFA_DOPAMINE_HIGH = 15  # dopamine <= 15 -> 3, else -> 4
SOFA_ADRENERGIC_LOW = 0.1  # epinephrine/norepinephrine <= 0.1 -> 3, else -> 4

# Neurological — Glasgow Coma Scale; inclusive lower bound of each score band
SOFA_GCS_NORMAL = 15  # == 15 -> 0
SOFA_GCS_MILD = 13  # >= 13 -> 1
SOFA_GCS_MODERATE = 10  # >= 10 -> 2
SOFA_GCS_SEVERE = 6  # >= 6 -> 3, else -> 4

# Renal — creatinine (mg/dL); exclusive upper bound of each score band
SOFA_CREATININE_NORMAL = 1.2  # < 1.2 -> 0
SOFA_CREATININE_MILD = 2.0  # < 2.0 -> 1
SOFA_CREATININE_MODERATE = 3.5  # < 3.5 -> 2
SOFA_CREATININE_SEVERE = 5.0  # < 5.0 -> 3, else -> 4

# Renal — 24h urine output (mL/day); upgrades the renal score
SOFA_URINE_OUTPUT_SEVERE = 200  # < 200 -> 4
SOFA_URINE_OUTPUT_MODERATE = 500  # < 500 -> 3


@dataclass
class SOFAComponents:
    """Individual organ system scores for SOFA."""

    respiration: int = 0
    coagulation: int = 0
    liver: int = 0
    cardiovascular: int = 0
    neurological: int = 0
    renal: int = 0


@dataclass
class SOFAResult:
    """Result of a SOFA calculation."""

    total_score: int
    components: SOFAComponents
    algorithm_version: str = SOFA_VERSION
    missing_components: list[str] = field(default_factory=list)

    @property
    def sepsis_mortality_risk(self) -> str:
        """Estimated mortality risk based on SOFA score.

        SOFA ≥2 increase in mortality of ≈2-25%.
        SOFA 0-6: ~<10% mortality
        SOFA 7-9: ~15-20%
        SOFA 10-12: ~40-50%
        SOFA 13-14: ~50-60%
        SOFA 15-24: ~80-90%
        SOFA >15: ~>90%

        Delegates to classify_sofa_mortality_risk (single source of truth).
        """
        return classify_sofa_mortality_risk(self.total_score)


# ═══════════════════════════════════════════════════════════════════════════
# Respiration — PaO2/FiO2 ratio
# ═══════════════════════════════════════════════════════════════════════════


def score_respiration(
    pao2_fio2: float | None = None,
    mechanical_ventilation: bool = False,
) -> tuple[int, str | None]:
    """Score respiration based on PaO2/FiO2 ratio.

    ≥400 mmHg = 0
    <400     = 1
    <300     = 2
    <200 AND mechanical ventilation = 3
    <100 AND mechanical ventilation = 4

    If not on mechanical ventilation, <200 and <100 still score 2
    (ventilation is required for scores 3-4).

    Args:
        pao2_fio2: PaO2/FiO2 ratio in mmHg, or None if unavailable.
        mechanical_ventilation: Whether patient is on mechanical ventilation.

    Returns:
        Tuple of (score, status_string_or_None).
    """
    if pao2_fio2 is None:
        return 0, "missing"

    if isinstance(pao2_fio2, bool):
        return 0, "invalid_type"

    if pao2_fio2 < 20:
        # FiO2 percent bug: P/F ratio should be ~200-500
        # If value is < 20, FiO2 was likely passed as percentage (e.g., 40%)
        # instead of fraction (0.4), causing ~100x error
        raise ValueError(
            f"PaO2/FiO2 ratio {pao2_fio2} appears to be invalid. "
            f"Expected ratio 200-500. If FiO2 was passed as percentage (e.g., 40), "
            f"divide by 100 to get fraction (0.4)."
        )

    if pao2_fio2 >= SOFA_RESP_PF_NORMAL:
        score = 0
    elif pao2_fio2 >= SOFA_RESP_PF_MILD:
        score = 1
    elif pao2_fio2 >= SOFA_RESP_PF_MODERATE:
        score = 2
    elif mechanical_ventilation:
        # pao2_fio2 < 200 and ventilated: 3 unless < 100
        score = 3 if pao2_fio2 >= SOFA_RESP_PF_SEVERE else 4
    else:
        # pao2_fio2 < 200 and not ventilated: cap at 2
        score = 2
    return score, None


# ═══════════════════════════════════════════════════════════════════════════
# Coagulation — Platelets
# ═══════════════════════════════════════════════════════════════════════════


def score_coagulation(platelets: float | None = None) -> tuple[int, str | None]:
    """Score coagulation based on platelet count (x10³/µL).

    ≥150 = 0
    <150 = 1
    <100 = 2
    <50  = 3
    <20  = 4

    Args:
        platelets: Platelet count in x10³/µL, or None if unavailable.

    Returns:
        Tuple of (score, status_string_or_None).
    """
    if platelets is None:
        return 0, "missing"

    if platelets >= SOFA_PLATELETS_NORMAL:
        return 0, None
    if platelets >= SOFA_PLATELETS_MILD:
        return 1, None
    if platelets >= SOFA_PLATELETS_MODERATE:
        return 2, None
    if platelets >= SOFA_PLATELETS_SEVERE:
        return 3, None
    return 4, None


# ═══════════════════════════════════════════════════════════════════════════
# Liver — Bilirubin
# ═══════════════════════════════════════════════════════════════════════════


def score_liver(bilirubin: float | None = None) -> tuple[int, str | None]:
    """Score liver function based on bilirubin (mg/dL or µmol/L).

    Thresholds in mg/dL:
    <1.2    = 0
    1.2-1.9 = 1
    2.0-5.9 = 2
    6.0-11.9 = 3
    ≥12.0   = 4

    Args:
        bilirubin: Total bilirubin in mg/dL, or None if unavailable.

    Returns:
        Tuple of (score, status_string_or_None).
    """
    if bilirubin is None:
        return 0, "missing"

    if bilirubin < SOFA_BILIRUBIN_NORMAL:
        return 0, None
    if bilirubin < SOFA_BILIRUBIN_MILD:
        return 1, None
    if bilirubin < SOFA_BILIRUBIN_MODERATE:
        return 2, None
    if bilirubin < SOFA_BILIRUBIN_SEVERE:
        return 3, None
    return 4, None


# ═══════════════════════════════════════════════════════════════════════════
# Cardiovascular — MAP + vasopressors
# ═══════════════════════════════════════════════════════════════════════════


def score_cardiovascular(
    map_value: float | None = None,
    vasopressor_type: str | None = None,
    vasopressor_dose_mcg_kg_min: float | None = None,
) -> tuple[int, str | None]:
    """Score cardiovascular system based on MAP and vasopressor support.

    MAP ≥70 mmHg, no vasopressors = 0
    MAP <70 mmHg, no vasopressors = 1
    Dopamine ≤5 µg/kg/min OR dobutamine (any) = 2
    Dopamine >5 µg/kg/min OR epinephrine ≤0.1 µg/kg/min OR norepinephrine ≤0.1 µg/kg/min = 3
    Dopamine >15 µg/kg/min OR epinephrine >0.1 µg/kg/min OR norepinephrine >0.1 µg/kg/min = 4

    Simplified scoring when vasopressor_type is just a boolean/string:
    - vasopressor_type=None or "" or False: no vasopressors → score based on MAP
    - vasopressor_type="dobutamine" or dose unknown: score 2
    - vasopressor_type="dopamine" with dose ≤5: score 2; dose >5 and ≤15: score 3; dose >15: score 4
    - vasopressor_type="epinephrine" or "norepinephrine" with dose ≤0.1: score 3; dose >0.1: score 4

    Args:
        map_value: Mean Arterial Pressure in mmHg, or None if unavailable.
        vasopressor_type: Type of vasopressor ('dopamine', 'dobutamine',
            'epinephrine', 'norepinephrine'), or None.
        vasopressor_dose_mcg_kg_min: Dose in µg/kg/min, or None.

    Returns:
        Tuple of (score, status_string_or_None).
    """
    if map_value is None:
        return 0, "missing"

    if not vasopressor_type or vasopressor_type.lower() in ("none", ""):
        # Score based on MAP alone
        return (0 if map_value >= SOFA_MAP_NORMAL else 1), None

    # Has vasopressor — determine level
    # NOTE: vasopressor dose is assumed in mcg/kg/min (canonical unit, CLINICALLY RATIFIED per RAT-CLINICAL-SCORING-03).
    vtype = vasopressor_type.lower().strip()
    dose = vasopressor_dose_mcg_kg_min

    if vtype == "dopamine":
        if dose is None:
            # Unknown dose, default to moderate (2-3 range)
            score = 2
        elif dose <= SOFA_DOPAMINE_LOW:
            score = 2
        elif dose <= SOFA_DOPAMINE_HIGH:
            score = 3
        else:
            score = 4
    elif vtype in ("epinephrine", "norepinephrine", "noradrenaline"):
        if dose is None:
            # Unknown dose, default to moderate-high
            score = 3
        elif dose <= SOFA_ADRENERGIC_LOW:
            score = 3
        else:
            score = 4
    else:
        # Dobutamine or unknown vasopressor type — default to mid-range
        score = 2

    return score, None


# ═══════════════════════════════════════════════════════════════════════════
# Neurological — Glasgow Coma Scale
# ═══════════════════════════════════════════════════════════════════════════


def score_neurological(gcs: int | None = None) -> tuple[int, str | None]:
    """Score neurological function based on Glasgow Coma Scale.

    15     = 0
    13-14  = 1
    10-12  = 2
    6-9    = 3
    <6     = 4

    Args:
        gcs: Glasgow Coma Scale score (3-15), or None if unavailable.

    Returns:
        Tuple of (score, status_string_or_None).
    """
    if gcs is None:
        return 0, "missing"

    if gcs == SOFA_GCS_NORMAL:
        return 0, None
    if gcs >= SOFA_GCS_MILD:
        return 1, None
    if gcs >= SOFA_GCS_MODERATE:
        return 2, None
    if gcs >= SOFA_GCS_SEVERE:
        return 3, None
    return 4, None


# ═══════════════════════════════════════════════════════════════════════════
# Renal — Creatinine + urine output
# ═══════════════════════════════════════════════════════════════════════════


def score_renal(
    creatinine: float | None = None,
    urine_output_ml_day: float | None = None,
) -> tuple[int, str | None]:
    """Score renal function based on creatinine and urine output.

    Creatinine thresholds (mg/dL):
    <1.2 = 0  (1.2-1.9=1, 2.0-3.4=2, 3.5-4.9=3, ≥5.0=4)

    Urine output can upgrade the score:
    <500 mL/day → minimum score 3
    <200 mL/day → minimum score 4

    The final score is the maximum of the creatinine-based score and the
    urine-output-based score.

    Args:
        creatinine: Serum creatinine in mg/dL, or None if unavailable.
        urine_output_ml_day: 24-hour urine output in mL, or None if unavailable.

    Returns:
        Tuple of (score, status_string_or_None).
    """
    both_missing = creatinine is None and urine_output_ml_day is None
    if both_missing:
        return 0, "missing"

    # Creatinine-based score
    if creatinine is None or creatinine < SOFA_CREATININE_NORMAL:
        cr_score = 0
    elif creatinine < SOFA_CREATININE_MILD:
        cr_score = 1
    elif creatinine < SOFA_CREATININE_MODERATE:
        cr_score = 2
    elif creatinine < SOFA_CREATININE_SEVERE:
        cr_score = 3
    else:
        cr_score = 4

    # Urine output-based score
    if urine_output_ml_day is None:
        uo_score = 0
    elif urine_output_ml_day < SOFA_URINE_OUTPUT_SEVERE:
        uo_score = 4
    elif urine_output_ml_day < SOFA_URINE_OUTPUT_MODERATE:
        uo_score = 3
    else:
        uo_score = 0

    # Per SOFA-C-03: renal_score = max(creatinine_score, urine_output_score)
    return max(cr_score, uo_score), None


# ═══════════════════════════════════════════════════════════════════════════
# Full SOFA Calculation
# ═══════════════════════════════════════════════════════════════════════════


def calculate_sofa(
    pao2_fio2: float | None = None,
    mechanical_ventilation: bool = False,
    platelets: float | None = None,
    bilirubin: float | None = None,
    map_value: float | None = None,
    vasopressor_type: str | None = None,
    vasopressor_dose_mcg_kg_min: float | None = None,
    gcs: int | None = None,
    creatinine: float | None = None,
    urine_output_ml_day: float | None = None,
) -> SOFAResult:
    """Calculate the full SOFA score from all 6 organ system parameters.

    Args:
        pao2_fio2: PaO2/FiO2 ratio in mmHg.
        mechanical_ventilation: Whether the patient is on mechanical ventilation.
        platelets: Platelet count in x10³/µL.
        bilirubin: Total bilirubin in mg/dL.
        map_value: Mean Arterial Pressure in mmHg.
        vasopressor_type: Type of vasopressor ('dopamine', 'dobutamine',
            'epinephrine', 'norepinephrine'), or None.
        vasopressor_dose_mcg_kg_min: Vasopressor dose in µg/kg/min.
        gcs: Glasgow Coma Scale score (3-15).
        creatinine: Serum creatinine in mg/dL.
        urine_output_ml_day: 24-hour urine output in mL.

    Returns:
        SOFAResult with total score, component breakdown, and missing list.
    """
    missing: list[str] = []

    resp_score, resp_status = score_respiration(pao2_fio2, mechanical_ventilation)
    if resp_status == "missing":
        missing.append("pao2_fio2")

    coag_score, coag_status = score_coagulation(platelets)
    if coag_status == "missing":
        missing.append("platelets")

    liver_score, liver_status = score_liver(bilirubin)
    if liver_status == "missing":
        missing.append("bilirubin")

    cv_score, cv_status = score_cardiovascular(
        map_value,
        vasopressor_type,
        vasopressor_dose_mcg_kg_min,
    )
    if cv_status == "missing":
        missing.append("map_value")

    neuro_score, neuro_status = score_neurological(gcs)
    if neuro_status == "missing":
        missing.append("gcs")

    renal_score, renal_status = score_renal(creatinine, urine_output_ml_day)
    if renal_status == "missing":
        missing.append("creatinine_and_urine_output")

    components = SOFAComponents(
        respiration=resp_score,
        coagulation=coag_score,
        liver=liver_score,
        cardiovascular=cv_score,
        neurological=neuro_score,
        renal=renal_score,
    )

    total = resp_score + coag_score + liver_score + cv_score + neuro_score + renal_score

    return SOFAResult(
        total_score=total,
        components=components,
        missing_components=missing,
    )
