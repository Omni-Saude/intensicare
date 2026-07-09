"""Drug safety ranges, dose conversion utilities, and validation logic.

Extracted from domain_prescricao.py as part of F-CODE-004 component refactoring.

Contains:
- Drug safety range definitions (DRUG_SAFETY)
- Renal adjustment tables (RENAL_ADJUSTMENTS)
- Pediatric dose adjustments (PEDIATRIC_ADJUSTMENTS)
- Dose conversion functions (_mass_to_mg, _rate_to_mg, _to_mg)
- Dose validation logic (R27-R35)
- Weight-based and renal dose calculators
"""

from __future__ import annotations

from typing import Any, TypedDict

# =============================================================================
# Constants
# =============================================================================

VALID_ROUTES: list[str] = ["IV", "IM", "SC", "PO", "SN", "IT", "TOP", "INAL"]
VALID_STATUSES: list[str] = [
    "draft", "active", "completed", "discontinued", "suspended",
]
VALID_FREQUENCIES: list[str] = [
    "QID", "TID", "BID", "QD", "QOD", "PRN", "continuous",
    "8/8h", "6/6h", "12/12h", "24/24h", "4/4h", "1/1h", "48/48h",
]
VALID_UNITS: list[str] = [
    "mg", "g", "mcg", "ng", "mL", "L", "UI", "mEq", "mmol",
    "mg/kg", "mcg/kg", "mcg/kg/min", "mg/h", "mL/h",
]
VALID_SEVERITIES: list[str] = [
    "contraindicated", "severe", "moderate", "minor",
]
VALID_INTERACTION_TYPES: list[str] = [
    "drug-drug", "drug-allergy", "drug-food", "duplicate",
]

# Routes that support continuous infusion
INFUSION_ROUTES: set[str] = {"IV", "SC"}

# Terminal states — no further transitions allowed
TERMINAL_STATES: set[str] = {"completed", "discontinued"}


# =============================================================================
# DrugSafetyEntry TypedDict
# =============================================================================

class DrugSafetyEntry(TypedDict, total=False):
    """Typed representation of a drug safety range entry.

    Fields are optional (total=False) because each drug defines only a subset
    of dose fields depending on its unit system (mg, mcg, UI, mEq, mL, or
    weight-rate-based units like mcg/kg/min).
    """

    # Generic
    unit: str
    renal_adjust: bool
    weight_based: bool
    typical_routes: list[str]
    continuous_only: bool

    # Milligrams
    min_single_mg: float
    max_single_mg: float
    max_daily_mg: float
    weight_dose_mg_per_kg: float
    infusion_rate_max_mg_h: float

    # Micrograms
    min_single_mcg: float
    max_single_mcg: float
    max_daily_mcg: float
    weight_dose_mcg_per_kg: float
    continuous_mcg_kg_h_max: float
    continuous_mg_kg_h_max: float

    # International units
    min_single_ui: float
    max_single_ui: float
    weight_dose_ui_per_kg: float
    max_infusion_ui_h: float

    # Milliequivalents
    min_single_mEq: float
    max_single_mEq: float
    max_daily_mEq: float
    infusion_rate_max_mEq_h: float

    # Millilitres
    min_single_mL: float
    max_single_mL: float
    infusion_rate_max_mL_h: float

    # Micrograms per kg per minute
    min_single_mcg_kg_min: float
    max_single_mcg_kg_min: float

    # Elderly adjustment
    elderly_reduce_pct: float


# =============================================================================
# Drug safety ranges (dose, unit, route) — Rule base for dose validation
# =============================================================================

# Format: (min_single_dose, max_single_dose, unit, max_daily_dose, max_infusion_rate)
# Doses in the drug's native unit
DRUG_SAFETY: dict[str, DrugSafetyEntry] = {
    "meropenem": {
        "min_single_mg": 500,
        "max_single_mg": 2000,
        "max_daily_mg": 6000,
        "unit": "mg",
        "renal_adjust": True,
        "weight_based": False,
        "typical_routes": ["IV", "IM"],
    },
    "vancomicina": {
        "min_single_mg": 500,
        "max_single_mg": 2000,
        "max_daily_mg": 4000,
        "unit": "mg",
        "renal_adjust": True,
        "weight_based": True,
        "weight_dose_mg_per_kg": 15,
        "typical_routes": ["IV"],
        "infusion_rate_max_mg_h": 1000,  # max 1g/h (red man syndrome)
    },
    "noradrenalina": {
        "min_single_mcg_kg_min": 0.01,
        "max_single_mcg_kg_min": 3.0,
        "unit": "mcg/kg/min",
        "renal_adjust": False,
        "weight_based": True,
        "continuous_only": True,
        "typical_routes": ["IV"],
    },
    "dobutamina": {
        "min_single_mcg_kg_min": 2.5,
        "max_single_mcg_kg_min": 20.0,
        "unit": "mcg/kg/min",
        "renal_adjust": False,
        "weight_based": True,
        "continuous_only": True,
        "typical_routes": ["IV"],
    },
    "midazolam": {
        "min_single_mg": 1,
        "max_single_mg": 10,
        "max_daily_mg": 240,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV", "IM", "PO"],
        "elderly_reduce_pct": 50,  # 50% reduction for >65
    },
    "fentanil": {
        "min_single_mcg": 25,
        "max_single_mcg": 200,
        "max_daily_mcg": 1200,
        "unit": "mcg",
        "renal_adjust": False,
        "weight_based": True,
        "weight_dose_mcg_per_kg": 1,
        "typical_routes": ["IV"],
        "continuous_mcg_kg_h_max": 10,
    },
    "propofol": {
        "min_single_mg": 10,
        "max_single_mg": 200,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": True,
        "weight_dose_mg_per_kg": 2,
        "typical_routes": ["IV"],
        "continuous_mg_kg_h_max": 4,
        "max_daily_mg": 6000,
    },
    "insulina_regular": {
        "min_single_ui": 1,
        "max_single_ui": 50,
        "unit": "UI",
        "renal_adjust": True,
        "weight_based": False,
        "typical_routes": ["IV", "SC"],
        "max_infusion_ui_h": 10,
    },
    "heparina_nao_fracionada": {
        "min_single_ui": 5000,
        "max_single_ui": 25000,
        "unit": "UI",
        "renal_adjust": False,
        "weight_based": True,
        "weight_dose_ui_per_kg": 80,  # bolus
        "typical_routes": ["IV", "SC"],
        "max_infusion_ui_h": 1500,
    },
    "amiodarona": {
        "min_single_mg": 150,
        "max_single_mg": 450,
        "max_daily_mg": 1200,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV", "PO"],
    },
    "omeprazol": {
        "min_single_mg": 20,
        "max_single_mg": 80,
        "max_daily_mg": 80,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV", "PO"],
    },
    "dexametasona": {
        "min_single_mg": 4,
        "max_single_mg": 20,
        "max_daily_mg": 40,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV", "PO"],
    },
    "ceftriaxona": {
        "min_single_mg": 1000,
        "max_single_mg": 2000,
        "max_daily_mg": 4000,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV", "IM"],
    },
    "piperacilina_tazobactam": {
        "min_single_mg": 2250,
        "max_single_mg": 4500,
        "max_daily_mg": 18000,
        "unit": "mg",
        "renal_adjust": True,
        "weight_based": False,
        "typical_routes": ["IV"],
    },
    "metoclopramida": {
        "min_single_mg": 5,
        "max_single_mg": 20,
        "max_daily_mg": 60,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV", "PO"],
    },
    "dipirona": {
        "min_single_mg": 500,
        "max_single_mg": 2000,
        "max_daily_mg": 4000,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV", "PO"],
    },
    "morfina": {
        "min_single_mg": 2,
        "max_single_mg": 10,
        "max_daily_mg": 60,
        "unit": "mg",
        "renal_adjust": True,
        "weight_based": False,
        "typical_routes": ["IV", "SC", "PO"],
        "elderly_reduce_pct": 50,
    },
    "enoxaparina": {
        "min_single_mg": 20,
        "max_single_mg": 150,
        "unit": "mg",
        "renal_adjust": True,
        "weight_based": True,
        "weight_dose_mg_per_kg": 1.5,
        "typical_routes": ["SC"],
    },
    "cloreto_de_potassio": {
        "min_single_mEq": 10,
        "max_single_mEq": 40,
        "max_daily_mEq": 200,
        "unit": "mEq",
        "renal_adjust": True,
        "weight_based": False,
        "typical_routes": ["IV", "PO"],
        "infusion_rate_max_mEq_h": 20,
    },
    "cloreto_de_sodio_3%": {
        "min_single_mL": 50,
        "max_single_mL": 500,
        "unit": "mL",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV"],
        "infusion_rate_max_mL_h": 100,
    },
}

# =============================================================================
# Renal adjustment table (GFR-based dose multipliers)
# =============================================================================

# GFR thresholds in mL/min
RENAL_ADJUSTMENTS: dict[str, Any] = {
    "meropenem": {
        "gfr_normal": 1.0,   # GFR 90-119: normal renal function
        "gfr_arc": 1.0,      # GFR >=120: ARC — standard dose (no increase)
        "gfr_50_90": 1.0,    # full dose
        "gfr_26_50": 1.0,    # full dose
        "gfr_10_25": 0.5,    # 50% dose
        "gfr_below_10": 0.25,  # 25% dose
    },
    "vancomicina": {
        "gfr_normal": 1.0,
        "gfr_arc": 1.2,      # ARC: higher doses may be needed
        "gfr_50_90": 1.0,
        "gfr_26_50": 0.5,
        "gfr_10_25": 0.25,
        "gfr_below_10": 0.15,
    },
    "piperacilina_tazobactam": {
        "gfr_normal": 1.0,
        "gfr_arc": 1.2,      # ARC: higher doses may be needed
        "gfr_50_90": 1.0,
        "gfr_26_50": 0.75,
        "gfr_10_25": 0.5,
        "gfr_below_10": 0.33,
    },
    "morfina": {
        "gfr_normal": 1.0,
        "gfr_arc": 1.0,
        "gfr_50_90": 1.0,
        "gfr_26_50": 0.75,
        "gfr_10_25": 0.5,
        "gfr_below_10": 0.5,
    },
    "insulina_regular": {
        "gfr_normal": 1.0,
        "gfr_arc": 1.0,
        "gfr_50_90": 1.0,
        "gfr_26_50": 0.75,
        "gfr_10_25": 0.5,
        "gfr_below_10": 0.25,
    },
    "enoxaparina": {
        "gfr_normal": 1.0,
        "gfr_arc": 1.0,
        "gfr_50_90": 1.0,
        "gfr_26_50": 0.75,
        "gfr_10_25": 0.5,
        "gfr_below_10": 0.5,
    },
    "cloreto_de_potassio": {
        "gfr_normal": 1.0,
        "gfr_arc": 1.0,
        "gfr_50_90": 1.0,
        "gfr_26_50": 0.5,
        "gfr_10_25": 0.25,
        "gfr_below_10": 0.1,
    },
}

# =============================================================================
# Pediatric and elderly adjustments
# =============================================================================

# Pediatric dose adjustment by age brackets (multiplier of adult dose)
PEDIATRIC_ADJUSTMENTS: dict[str, float] = {
    "neonate": 0.05,     # 0-28 days
    "infant": 0.15,      # 1-12 months
    "toddler": 0.25,     # 1-3 years
    "child": 0.5,        # 4-12 years
    "adolescent": 0.75,  # 13-17 years
}


# =============================================================================
# Dose conversion utilities
# =============================================================================

def _mass_to_mg(dose: float, unit: str) -> float:
    """Convert a mass or volume dose to mg equivalent for comparison.

    Handles mass/volume units only (mg, g, mcg, ng, mL, L, UI, mEq, mmol).
    For rate or weight-based units, use ``_rate_to_mg()`` instead.

    Parameters
    ----------
    dose:
        The numeric dose value.
    unit:
        Unit string (e.g. "mg", "g", "mcg", "mL").

    Returns
    -------
    float
        Dose expressed in mg equivalent.
    """
    conversion: dict[str, float] = {
        "mg": 1.0,
        "g": 1000.0,
        "mcg": 0.001,
        "ng": 1e-6,
        "mL": 1.0,   # context-dependent, assume 1 mg/mL
        "L": 1000.0,
        "UI": 1.0,   # cannot directly convert to mg
        "mEq": 1.0,  # context-dependent
        "mmol": 1.0,  # context-dependent
    }
    return dose * conversion.get(unit, 1.0)


def _rate_to_mg(
    rate: float,
    unit: str,
    weight_kg: float | None = None,
    duration_h: float = 1.0,
) -> float:
    """Convert a rate or weight-based dose to total mg equivalent.

    Unlike ``_mass_to_mg()``, this function correctly incorporates patient
    weight and infusion duration for clinically meaningful dose comparisons.

    Parameters
    ----------
    rate:
        The numeric rate (or weight-adjusted dose) value.
    unit:
        Unit string — must be a rate or weight-based unit:
        ``mg/kg``, ``mcg/kg``, ``mcg/kg/min``, ``mg/h``, ``mL/h``.
    weight_kg:
        Patient weight in kg. Required for ``mg/kg``, ``mcg/kg``,
        and ``mcg/kg/min``.
    duration_h:
        Duration in hours for the administration (default 1.0).

    Returns
    -------
    float
        Total mg equivalent over the given duration.

    Raises
    ------
    ValueError
        If ``weight_kg`` is missing for weight-dependent units.
    """
    known_rate_units = {"mg/kg", "mcg/kg", "mcg/kg/min", "mg/h", "mL/h"}

    if unit not in known_rate_units:
        # Not a rate unit — fall back to mass conversion
        return _mass_to_mg(rate, unit)

    # Weight-based units require weight
    weight_dependent = {"mg/kg", "mcg/kg", "mcg/kg/min"}
    if unit in weight_dependent and (weight_kg is None or weight_kg <= 0):
        raise ValueError(
            f"Unit '{unit}' requires patient weight_kg (got {weight_kg!r}). "
            "Cannot compute clinically meaningful mg equivalent without weight."
        )

    if unit == "mg/kg":
        return rate * weight_kg  # type: ignore[operator]
    elif unit == "mcg/kg":
        return rate * weight_kg * 0.001  # type: ignore[operator]
    elif unit == "mcg/kg/min":
        return rate * weight_kg * duration_h * 60.0 * 0.001  # type: ignore[operator]
    elif unit == "mg/h":
        return rate * duration_h
    elif unit == "mL/h":
        # Assume 1 mg/mL concentration
        return rate * duration_h

    # Should not reach here; fallback
    return rate


def _to_mg(
    dose: float,
    unit: str,
    weight_kg: float | None = None,
    duration_h: float = 1.0,
) -> float:
    """Convert dose to mg equivalent, delegating to the correct converter.

    Dispatches to :func:`_rate_to_mg` for rate/weight-based units
    (mg/kg, mcg/kg, mcg/kg/min, mg/h, mL/h) and to :func:`_mass_to_mg`
    for mass/volume units.
    """
    rate_units = {"mg/kg", "mcg/kg", "mcg/kg/min", "mg/h", "mL/h"}

    if unit in rate_units:
        return _rate_to_mg(dose, unit, weight_kg=weight_kg, duration_h=duration_h)
    return _mass_to_mg(dose, unit)


def _estimate_daily_doses(frequency: str) -> int:
    """Estimate number of doses per 24h from frequency string."""
    freq_map: dict[str, int] = {
        "QID": 4,
        "TID": 3,
        "BID": 2,
        "QD": 1,
        "QOD": 1,  # every other day ~0.5, but use 1 for estimation
        "PRN": 1,  # as needed, assume max 1
        "continuous": 24,  # hourly rate
        "8/8h": 3,
        "6/6h": 4,
        "12/12h": 2,
        "24/24h": 1,
        "4/4h": 6,
        "1/1h": 24,
        "48/48h": 1,
    }
    return freq_map.get(frequency, 1)


def _pediatric_age_bracket(age_years: float) -> str:
    """Determine pediatric age bracket."""
    age_days = age_years * 365.25
    if age_days <= 28:
        return "neonate"
    if age_days <= 365:
        return "infant"
    if age_years <= 3:
        return "toddler"
    if age_years <= 12:
        return "child"
    return "adolescent"


# =============================================================================
# Dose validation (R27-R35)
# =============================================================================

def _validate_dose(
    drug: str,
    dose: float,
    unit: str,
    route: str,
    frequency: str,
    weight_kg: float | None = None,
    gfr: float | None = None,
    age_years: float | None = None,
) -> tuple[bool, list[str]]:
    """R27-R35: Validate dose against known safety ranges.

    Returns (valid, warnings). A dose may be flagged with warnings but still
    considered technically valid (clinician override possible).
    """
    warnings: list[str] = []
    drug_key = drug.lower().replace(" ", "_")
    safety = DRUG_SAFETY.get(drug_key)

    if not safety:
        # Drug not in our safety database — can't validate, assume valid
        return True, warnings

    # R27: Convert dose to mg equivalent for comparison
    dose_mg = _to_mg(dose, unit, weight_kg=weight_kg)

    # R28: Max single dose check
    max_single = safety.get("max_single_mg")
    min_single = safety.get("min_single_mg")
    if max_single is not None and dose_mg > max_single:
        warnings.append(
            f"R28: Dose única de {dose} {unit} ({dose_mg} mg equiv.) excede "
            f"o limite máximo de {max_single} mg para {drug}."
        )
    if min_single is not None and dose_mg < min_single:
        warnings.append(
            f"R28: Dose única de {dose} {unit} ({dose_mg} mg equiv.) abaixo "
            f"do limite mínimo de {min_single} mg para {drug}."
        )

    # R29: Max daily dose estimation
    max_daily = safety.get("max_daily_mg")
    if max_daily is not None:
        doses_per_day = _estimate_daily_doses(frequency)
        daily_mg = dose_mg * doses_per_day
        if daily_mg > max_daily:
            warnings.append(
                f"R29: Dose diária estimada ({daily_mg} mg) excede o limite "
                f"máximo diário de {max_daily} mg para {drug}."
            )

    # R30: Weight-based dose validation
    if safety.get("weight_based") and weight_kg and weight_kg > 0:
        expected = _calculate_dose_weight_based(weight_kg, drug_key)
        if expected > 0:
            ratio = dose_mg / expected
            if ratio < 0.5:
                warnings.append(
                    f"R30: Dose ({dose_mg} mg) é {ratio:.0%} da dose calculada "
                    f"por peso ({expected:.0f} mg para {weight_kg} kg). Possível subdose."
                )
            elif ratio > 2.0:
                warnings.append(
                    f"R30: Dose ({dose_mg} mg) é {ratio:.0%} da dose calculada "
                    f"por peso ({expected:.0f} mg para {weight_kg} kg). Possível sobredose."
                )

    # R31: Renal-adjusted dose check
    if safety.get("renal_adjust") and gfr is not None and gfr > 0:
        adjusted = _calculate_dose_renal_adjusted(gfr, drug_key, dose_mg)
        if adjusted != dose_mg:
            ratio = adjusted / dose_mg
            warnings.append(
                f"R31: Dose ajustada para função renal (GFR={gfr} mL/min): "
                f"{adjusted:.0f} mg (fator {ratio:.0%}). Dose atual: {dose_mg} mg."
            )

    # R32: Elderly dose reduction alert
    if age_years and age_years >= 65 and safety.get("elderly_reduce_pct"):
        reduce_pct: float = safety.get("elderly_reduce_pct", 0)
        recommended = dose_mg * (1 - reduce_pct / 100)
        warnings.append(
            f"R32: Paciente idoso ({age_years:.0f} anos). Considerar redução de "
            f"{reduce_pct}% na dose de {drug} → dose recomendada: ~{recommended:.0f} mg."
        )

    # R33: Pediatric dose adjustment
    if age_years is not None and age_years < 18:
        bracket = _pediatric_age_bracket(age_years)
        factor = PEDIATRIC_ADJUSTMENTS.get(bracket, 1.0)
        if factor < 1.0:
            pediatric_dose = dose_mg * factor
            warnings.append(
                f"R33: Paciente pediátrico ({bracket}, {age_years:.1f} anos). "
                f"Dose pediátrica estimada: ~{pediatric_dose:.0f} mg "
                f"(fator {factor:.0%} da dose adulta)."
            )

    # R34: Infusion rate limit for IV drugs
    if route == "IV" and frequency == "continuous":
        max_rate = safety.get("infusion_rate_max_mg_h")
        if max_rate and dose_mg > max_rate:
            warnings.append(
                f"R34: Taxa de infusão ({dose_mg} mg/h) excede o limite "
                f"de segurança de {max_rate} mg/h para {drug}."
            )

    # R35: Concentration limit check for specific routes
    if drug_key == "cloreto_de_potassio" and route == "IV":
        max_rate = safety.get("infusion_rate_max_mEq_h", 20)
        if dose > max_rate:
            warnings.append(
                f"R35: Infusão de K+ ({dose} mEq/h) excede {max_rate} mEq/h. "
                "Risco de arritmia por hipercalemia aguda."
            )

    # Dose is valid if no warnings are critical (all are advisory)
    valid = True
    return valid, warnings


# =============================================================================
# Weight-based and renal dose calculators
# =============================================================================


def _calculate_dose_weight_based(weight_kg: float, drug: str) -> float:
    """Calculate weight-based dose for a given drug.

    Returns dose in mg (or native unit as defined in DRUG_SAFETY).
    """
    drug_key = drug.lower().replace(" ", "_")
    safety = DRUG_SAFETY.get(drug_key)
    if not safety or not safety.get("weight_based"):
        return 0.0

    if "weight_dose_mg_per_kg" in safety:
        return weight_kg * safety["weight_dose_mg_per_kg"]
    if "weight_dose_mcg_per_kg" in safety:
        return weight_kg * safety["weight_dose_mcg_per_kg"] / 1000.0
    if "weight_dose_ui_per_kg" in safety:
        return weight_kg * safety["weight_dose_ui_per_kg"]

    return 0.0


def _calculate_dose_renal_adjusted(gfr: float, drug: str, base_dose: float) -> float:
    """Adjust dose for renal function based on GFR.

    Returns adjusted dose in same unit as base_dose.
    """
    drug_key = drug.lower().replace(" ", "_")
    adjustments = RENAL_ADJUSTMENTS.get(drug_key)
    if not adjustments:
        return base_dose

    if gfr >= 120:
        factor = adjustments.get("gfr_arc", adjustments.get("gfr_normal", 1.0))
    elif gfr >= 90:
        factor = adjustments.get("gfr_normal", 1.0)
    elif gfr >= 50:
        factor = adjustments.get("gfr_50_90", 1.0)
    elif gfr >= 26:
        factor = adjustments.get("gfr_26_50", 1.0)
    elif gfr >= 10:
        factor = adjustments.get("gfr_10_25", 1.0)
    else:
        factor = adjustments.get("gfr_below_10", 1.0)

    return base_dose * factor
