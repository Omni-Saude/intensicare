"""
Respiratory domain — hybrid NRT+micro-batch evaluator.
5 alerts, 24 test vectors from docs/plan/_work/alerts/respiratory.yaml.

CRITICAL DESIGN RULE: CRIT severity never auto-resolves on stale data.
Unlike watch/urgent, a CRIT alert persists until explicitly acknowledged
and resolved by a clinician.

FiO2 is a FRACTION 0-1 at every computation boundary (mission law CON-SEED-12 / SYS-01).
SpO2/FiO2 bands per Berlin Definition (ARDS Task Force, JAMA 2012).
"""

from __future__ import annotations

__version__ = "3.0.0"

from dataclasses import dataclass, field
from typing import Any

from intensicare.schemas.severity import SeverityLevel


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


@dataclass
class RespiratoryAlertResult:
    """Result of evaluating one respiratory alert."""

    alert_id: str
    name: str
    fired: bool
    severity: SeverityLevel | None = None
    band: str | None = None  # "critical", "urgent", "watch", "normal"
    stage: str | None = None  # "leve", "moderada", "grave" for ARDS
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _band_severity(band: str | None) -> SeverityLevel | None:
    """Convert band label to SeverityLevel."""
    if band is None:
        return None
    return {
        "critical": SeverityLevel.CRITICAL,
        "urgent": SeverityLevel.URGENT,
        "watch": SeverityLevel.WATCH,
        "normal": SeverityLevel.NORMAL,
    }.get(band)


# ---------------------------------------------------------------------------
# FiO2 FRACTION enforcement (CANON_PINS from WO-009)
# ---------------------------------------------------------------------------


def _ensure_fio2_fraction(fio2_value: Any) -> float | None:
    """Enforce FiO2 as FRACTION 0-1.

    If value > 1.0, assume it's a percentage (e.g., 60 -> 0.60).
    Returns None for invalid values.
    """
    if fio2_value is None:
        return None
    try:
        v = float(fio2_value)
    except (ValueError, TypeError):
        return None

    # CANON_PINS: if > 1.0, treat as percentage and convert
    if v > 1.0:
        v = v / 100.0

    if v < 0.0 or v > 1.0:
        return None
    return v


def _compute_sf_ratio(spo2: Any, fio2: Any) -> float | None:
    """Compute SpO2/FiO2 ratio. FiO2 MUST be fraction 0-1.

    Returns None if either input is missing or FiO2 <= 0.
    """
    if spo2 is None or fio2 is None:
        return None
    try:
        s = float(spo2)
        f = _ensure_fio2_fraction(fio2)
        if f is None or f <= 0:
            return None
        return s / f
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def _compute_pf_ratio(pao2: Any, fio2: Any) -> float | None:
    """Compute PaO2/FiO2 ratio. FiO2 MUST be fraction 0-1."""
    if pao2 is None or fio2 is None:
        return None
    try:
        p = float(pao2)
        f = _ensure_fio2_fraction(fio2)
        if f is None or f <= 0:
            return None
        return p / f
    except (ValueError, TypeError, ZeroDivisionError):
        return None


# ---------------------------------------------------------------------------
# ALERT-RESP-ARDS-STAGING-01: SDRA — vigilância e estadiamento de Berlin
# ---------------------------------------------------------------------------


def evaluate_ards_staging(inputs: dict[str, Any]) -> RespiratoryAlertResult:
    """Evaluate Berlin ARDS staging (S/F and P/F bands).

    ARDS gate: on mechanical ventilation/CPAP + PEEP >= 5 cmH2O
               + bilateral infiltrates + cardiogenic edema excluded.

    Staging:
      Leve (watch):     S/F <= 315 AND > 235  OR (P/F available AND P/F <= 300 AND > 200)
      Moderada (urgent): S/F <= 235 AND > 148  OR (P/F available AND P/F <= 200 AND > 100)
      Grave (critical):  S/F <= 148            OR (P/F available AND P/F <= 100)

    When ABG present, P/F is authoritative and overrides S/F band.
    FiO2 is a FRACTION throughout.

    Boundary: inclusive <= for upper, strict > for lower of each band.
    """
    result = RespiratoryAlertResult(
        alert_id="ALERT-RESP-ARDS-STAGING-01",
        name="SDRA — vigilância e estadiamento de Berlin (S/F e P/F)",
        fired=False,
    )

    peep = inputs.get("peep")
    infiltrado = inputs.get("infiltrado_bilateral", False)
    edema_excluido = inputs.get("edema_cardiogenico_excluido", False)
    spo2 = inputs.get("saturacao_o2")
    fio2 = inputs.get("fio2")
    pao2 = inputs.get("pao2")

    # --- ARDS gate ---
    gate_met = True
    if peep is None or float(peep) < 5:
        gate_met = False
    if infiltrado is not True:
        gate_met = False
    if edema_excluido is not True:
        gate_met = False

    if not gate_met:
        return result

    # Compute ratios
    sf = _compute_sf_ratio(spo2, fio2)
    pf = _compute_pf_ratio(pao2, fio2)

    if sf is None and pf is None:
        return result  # insufficient data

    # Determine stage from each ratio
    sf_stage = None  # "leve", "moderada", "grave"
    pf_stage = None

    if sf is not None:
        if sf <= 148:
            sf_stage = "grave"
        elif sf <= 235:
            sf_stage = "moderada"
        elif sf <= 315:
            sf_stage = "leve"

    if pf is not None:
        if pf <= 100:
            pf_stage = "grave"
        elif pf <= 200:
            pf_stage = "moderada"
        elif pf <= 300:
            pf_stage = "leve"

    # Authoritative: PF overrides SF when ABG available
    stage_order = {"grave": 3, "moderada": 2, "leve": 1}
    final_stage = None

    if pf_stage is not None:
        final_stage = pf_stage
    elif sf_stage is not None:
        final_stage = sf_stage

    if final_stage is None:
        return result

    # Map stage to band/severity
    band_map = {"leve": "watch", "moderada": "urgent", "grave": "critical"}

    result.fired = True
    result.stage = final_stage
    result.band = band_map[final_stage]
    result.severity = _band_severity(result.band)
    result.metadata = {
        "sf_ratio": sf,
        "pf_ratio": pf,
        "sf_stage": sf_stage,
        "pf_stage": pf_stage,
        "authoritative_stage": final_stage,
        "fio2_fraction": _ensure_fio2_fraction(fio2),
    }

    return result


# ---------------------------------------------------------------------------
# ALERT-RESP-DETERIORATION-02: Deterioração ventilatória
# ---------------------------------------------------------------------------


def evaluate_deterioration(inputs: dict[str, Any]) -> RespiratoryAlertResult:
    """Evaluate ventilatory deterioration — S/F trend and FiO2 demand.

    Fires when (persistence across >=2 samples):
      ΔS/F_6h <= -0.20 * previous_S/F      (>=20% drop)
      OR (FiO2_current > 1.30 * FiO2_6h_ago AND SpO2_current <= SpO2_6h_ago)

    FiO2 is a FRACTION throughout.

    Boundary: <= -20% inclusive (fires at exactly -20%).
    """
    result = RespiratoryAlertResult(
        alert_id="ALERT-RESP-DETERIORATION-02",
        name="Deterioração ventilatória — tendência S/F e demanda de FiO2",
        fired=False,
    )

    sf = inputs.get("relacao_spo2_fio2")
    sf_6h = inputs.get("relacao_spo2_fio2_6h_ago")
    fio2 = inputs.get("fio2")
    fio2_6h = inputs.get("fio2_6h_ago")
    spo2 = inputs.get("saturacao_o2")
    spo2_6h = inputs.get("saturacao_o2_6h_ago")

    deterioration = False

    # Branch 1: S/F drop >= 20%
    if sf is not None and sf_6h is not None:
        sf_f = float(sf)
        sf_6h_f = float(sf_6h)
        if sf_6h_f > 0:
            delta_pct = (sf_f - sf_6h_f) / sf_6h_f  # negative = drop
            if delta_pct <= -0.20:
                deterioration = True

    # Branch 2: FiO2 escalation without SpO2 improvement
    if not deterioration and fio2 is not None and fio2_6h is not None:
        fio2_f = _ensure_fio2_fraction(fio2)
        fio2_6h_f = _ensure_fio2_fraction(fio2_6h)
        if fio2_f is not None and fio2_6h_f is not None and fio2_6h_f > 0:
            if fio2_f > 1.30 * fio2_6h_f:
                if spo2 is not None and spo2_6h is not None:
                    if float(spo2) <= float(spo2_6h):
                        deterioration = True

    if deterioration:
        result.fired = True
        result.band = "urgent"
        result.severity = SeverityLevel.URGENT
        result.metadata = {
            "relacao_spo2_fio2": sf,
            "relacao_spo2_fio2_6h_ago": sf_6h,
            "fio2": fio2,
            "fio2_6h_ago": fio2_6h,
        }

    return result


# ---------------------------------------------------------------------------
# ALERT-RESP-ASYNCHRONY-03: Assincronia paciente-ventilador
# ---------------------------------------------------------------------------


def evaluate_asynchrony(inputs: dict[str, Any]) -> RespiratoryAlertResult:
    """Evaluate patient-ventilator asynchrony.

    Fires when:
      on_mechanical_ventilation
      AND spontaneous_RR > set_RR
      AND plateau_pressure > 30 cmH2O

    Boundary: strict > for both RR and plateau.
    Degrades to insufficient data when plateau absent.
    """
    result = RespiratoryAlertResult(
        alert_id="ALERT-RESP-ASYNCHRONY-03",
        name="Assincronia paciente-ventilador",
        fired=False,
    )

    rr = inputs.get("frequencia_respiratoria")
    rr_set = inputs.get("frequencia_respiratoria_programada")
    plateau = inputs.get("pressao_plato")

    # Plateau must be present AND > 30
    if plateau is None:
        return result  # insufficient data, no fire on RR alone
    if float(plateau) <= 30:
        return result

    # RR criterion: spontaneous > set (strict)
    if rr is None or rr_set is None:
        return result
    if float(rr) <= float(rr_set):
        return result

    result.fired = True
    result.band = "watch"
    result.severity = SeverityLevel.WATCH
    result.metadata = {
        "frequencia_respiratoria": rr,
        "frequencia_respiratoria_programada": rr_set,
        "pressao_plato": plateau,
    }

    return result


# ---------------------------------------------------------------------------
# ALERT-RESP-WEANING-READY-04: Prontidão para desmame / extubação
# ---------------------------------------------------------------------------


def evaluate_weaning_ready(inputs: dict[str, Any]) -> RespiratoryAlertResult:
    """Evaluate weaning/extubation readiness (RAT-CLINICAL-SCORING-06 RATIFIED).

    ALL criteria sustained >= 2h:
      S/F > 315 (strict >)
      AND PEEP <= 8 cmH2O (inclusive)
      AND FiO2 <= 0.40 (FRACTION, inclusive)
      AND RSBI < 105 if present (strict <)
      AND RASS >= -2 AND GCS >= 10
      AND dose_vasopressor <= 0.2 mcg/kg/min
      AND days_on_MV >= 1

    FiO2 is a FRACTION.

    Boundary: S/F strict > 315, FiO2 inclusive <= 0.40, RSBI strict < 105.
    """
    result = RespiratoryAlertResult(
        alert_id="ALERT-RESP-WEANING-READY-04",
        name="Prontidão para desmame / extubação",
        fired=False,
    )

    sf = inputs.get("relacao_spo2_fio2")
    peep = inputs.get("peep")
    fio2 = inputs.get("fio2")
    rsbi = inputs.get("indice_respiracao_rapida_superficial")
    rass = inputs.get("rass")
    gcs = inputs.get("glasgow")
    dose_vaso = inputs.get("dose_vasopressor")
    days_mv = inputs.get("dias_em_ventilacao_mecanica")

    # All criteria must be present and met
    # S/F > 315 (strict)
    if sf is None or float(sf) <= 315:
        return result

    # PEEP <= 8 (inclusive)
    if peep is None or float(peep) > 8:
        return result

    # FiO2 <= 0.40 FRACTION (inclusive)
    fio2_f = _ensure_fio2_fraction(fio2)
    if fio2_f is None or fio2_f > 0.40:
        return result

    # RSBI < 105 if present (strict)
    if rsbi is not None and float(rsbi) >= 105:
        return result

    # RASS >= -2
    if rass is None or float(rass) < -2:
        return result

    # GCS >= 10 (RATIFIED)
    if gcs is None or float(gcs) < 10:
        return result

    # Vasopressor <= 0.2 (inclusive)
    if dose_vaso is not None and float(dose_vaso) > 0.2:
        return result

    # Days on MV >= 1
    if days_mv is None or float(days_mv) < 1:
        return result

    result.fired = True
    result.band = "normal"
    result.severity = SeverityLevel.NORMAL
    result.metadata = {
        "relacao_spo2_fio2": sf,
        "peep": peep,
        "fio2": fio2,
        "rsbi": rsbi,
        "rass": rass,
        "glasgow": gcs,
        "dose_vasopressor": dose_vaso,
        "dias_em_ventilacao_mecanica": days_mv,
    }

    return result


# ---------------------------------------------------------------------------
# ALERT-RESP-PROLONGED-INTUB-05: Intubação prolongada
# ---------------------------------------------------------------------------


def evaluate_prolonged_intubation(inputs: dict[str, Any]) -> RespiratoryAlertResult:
    """Evaluate prolonged intubation — tracheostomy consideration.

    Fires when:
      dispositivo_via_aerea == "TOT"
      AND days_on_MV > 10 (non-COVID) OR >= 14 (active COVID)

    Boundary: strict > for non-COVID threshold (day 10 no-fire, day 11 fires).
    COVID: inclusive >= 14.
    """
    result = RespiratoryAlertResult(
        alert_id="ALERT-RESP-PROLONGED-INTUB-05",
        name="Intubação prolongada — avaliar traqueostomia",
        fired=False,
    )

    dispositivo = inputs.get("dispositivo_via_aerea")
    days_mv = inputs.get("dias_em_ventilacao_mecanica")
    covid = inputs.get("covid19_ativo", False)

    # Must be orotracheally intubated
    if dispositivo != "TOT":
        return result

    if days_mv is None:
        return result

    days = float(days_mv)

    # COVID-adjusted threshold
    if covid is True:
        # >= 14 inclusive
        if days >= 14:
            result.fired = True
    else:
        # > 10 strict
        if days > 10:
            result.fired = True

    if result.fired:
        result.band = "watch"
        result.severity = SeverityLevel.WATCH
        result.metadata = {
            "dispositivo_via_aerea": dispositivo,
            "dias_em_ventilacao_mecanica": days,
            "covid19_ativo": covid,
            "threshold": 14 if covid else 10,
        }

    return result


# ---------------------------------------------------------------------------
# ALERT-RESP-HIGH-PPLAT-06: Pressão inspiratória ou volume corrente elevado
# (rat-ventilacao-02, RULE-VENTILACAO-003, P1 RATIFY)
# ---------------------------------------------------------------------------


def evaluate_high_pplat_tidal(
    inputs: dict[str, Any],
) -> RespiratoryAlertResult:
    """Evaluate high inspiratory pressure or excessive tidal volume.

    RATIFIED per rat-ventilacao-02: Lung-protective ventilation alert.
    Pplat > 30 cmH2O OR tidal volume > 8 mL/kg PBW.

    PBW (predicted body weight) formulas:
      Male: 50 + 0.91 * (height_cm - 152.4)
      Female: 45.5 + 0.91 * (height_cm - 152.4)

    Boundary: strict > for both thresholds.
    """
    result = RespiratoryAlertResult(
        alert_id="ALERT-RESP-HIGH-PPLAT-06",
        name="Pressão de platô elevada ou volume corrente excessivo",
        fired=False,
    )

    pplat = inputs.get("pressao_plato")
    vc = inputs.get("volume_corrente")  # mL
    altura = inputs.get("altura_cm")
    sexo = inputs.get("sexo", "").upper()

    # Branch A: Pplat > 30 cmH2O
    pplat_high = False
    if pplat is not None and float(pplat) > 30:
        pplat_high = True

    # Branch B: Tidal volume > 8 mL/kg PBW
    vc_high = False
    vc_ml_kg_pbw = None
    if vc is not None and altura is not None:
        try:
            altura_cm = float(altura)
            if sexo in ("F", "FEMININO"):
                pbw = 45.5 + 0.91 * (altura_cm - 152.4)
            else:
                pbw = 50 + 0.91 * (altura_cm - 152.4)
            if pbw > 0:
                vc_ml_kg_pbw = float(vc) / pbw
                if vc_ml_kg_pbw > 8:
                    vc_high = True
        except (ValueError, TypeError):
            pass

    if pplat_high or vc_high:
        result.fired = True
        result.band = "watch"
        result.severity = SeverityLevel.WATCH
        result.metadata = {
            "pressao_plato": pplat,
            "volume_corrente": vc,
            "vc_ml_kg_pbw": vc_ml_kg_pbw,
            "pplat_high": pplat_high,
            "vc_high": vc_high,
            "pbw": None if altura is None else (50 + 0.91 * (float(altura) - 152.4)
                   if sexo not in ("F", "FEMININO")
                   else 45.5 + 0.91 * (float(altura) - 152.4)),
            "recommendation": "Avaliar ventilação protetora (VC 4-6 mL/kg PBW, Pplat <= 30)",
        }

    return result


# ---------------------------------------------------------------------------
# ALERT-RESP-PEEP-FIO2-MODERATE-07: Dissociação FiO2×PEEP — hipoxemia moderada
# (rat-ventilacao-03, RULE-VENTILACAO-004, P1 RATIFY)
# ---------------------------------------------------------------------------


def evaluate_peep_fio2_moderate(
    inputs: dict[str, Any],
) -> RespiratoryAlertResult:
    """Evaluate FiO2×PEEP mismatch — moderate hypoxemia.

    RATIFIED per rat-ventilacao-03: FiO2 as FRACTION.
    P/F ratio 200-300 with inadequate PEEP for the FiO2 level.

    FiO2-as-fraction per CANON_PINS (ESC-P0-007).
    """
    result = RespiratoryAlertResult(
        alert_id="ALERT-RESP-PEEP-FIO2-MODERATE-07",
        name="Dissociação FiO2×PEEP — hipoxemia moderada",
        fired=False,
    )

    peep = inputs.get("peep")
    fio2 = _ensure_fio2_fraction(inputs.get("fio2"))
    pao2 = inputs.get("pao2")

    # Compute P/F ratio
    pf = _compute_pf_ratio(pao2, fio2)

    if pf is None:
        return result

    # Moderate: 200 < P/F <= 300 with low PEEP for FiO2
    if not (200 < pf <= 300):
        return result

    if peep is None:
        return result

    peep_f = float(peep)

    # FiO2×PEEP table (fraction FiO2, per Berlin):
    # FiO2 0.30 → PEEP 5; 0.40 → PEEP 5-8; 0.50 → PEEP 8-10;
    # 0.60 → PEEP 10; 0.70 → PEEP 10-14; 0.80 → PEEP 14;
    # 0.90 → PEEP 14-18; 1.0 → PEEP 18-24

    # Simplified: PEEP should be at least FiO2 * 10 (minimum)
    if fio2 is None or fio2 <= 0:
        return result

    min_peep_expected = fio2 * 15  # approx guideline minimum

    if peep_f < min_peep_expected - 2:  # tolerance of 2 cmH2O
        result.fired = True
        result.band = "watch"
        result.severity = SeverityLevel.WATCH
        result.metadata = {
            "peep": peep_f,
            "fio2_fraction": fio2,
            "pf_ratio": pf,
            "min_peep_expected": min_peep_expected,
            "recommendation": "Ajustar PEEP conforme tabela FiO2×PEEP (ARDSNet)",
        }

    return result


# ---------------------------------------------------------------------------
# ALERT-RESP-PEEP-FIO2-SEVERE-08: Dissociação FiO2×PEEP — hipoxemia grave
# (rat-ventilacao-04, RULE-VENTILACAO-005, P1 RATIFY)
# ---------------------------------------------------------------------------


def evaluate_peep_fio2_severe(
    inputs: dict[str, Any],
) -> RespiratoryAlertResult:
    """Evaluate FiO2×PEEP mismatch — severe hypoxemia.

    RATIFIED per rat-ventilacao-04: P/F <= 200 with inadequate PEEP.
    """
    result = RespiratoryAlertResult(
        alert_id="ALERT-RESP-PEEP-FIO2-SEVERE-08",
        name="Dissociação FiO2×PEEP — hipoxemia grave",
        fired=False,
    )

    peep = inputs.get("peep")
    fio2 = _ensure_fio2_fraction(inputs.get("fio2"))
    pao2 = inputs.get("pao2")

    pf = _compute_pf_ratio(pao2, fio2)

    if pf is None:
        return result

    # Severe: P/F <= 200
    if pf > 200:
        return result

    if peep is None or fio2 is None or fio2 <= 0:
        return result

    peep_f = float(peep)
    min_peep_expected = fio2 * 18  # Higher expectation for severe

    if peep_f < min_peep_expected - 2:
        result.fired = True
        result.band = "urgent"
        result.severity = SeverityLevel.URGENT
        result.metadata = {
            "peep": peep_f,
            "fio2_fraction": fio2,
            "pf_ratio": pf,
            "min_peep_expected": min_peep_expected,
            "recommendation": "Otimizar PEEP — considerar manobra de recrutamento (ART/SCCM)",
        }

    return result


# ---------------------------------------------------------------------------
# ALERT-RESP-PROLONGED-COVID-09: Intubação prolongada com COVID-19
# (rat-ventilacao-05, RULE-VENTILACAO-009, P1 RATIFY)
# ---------------------------------------------------------------------------


def evaluate_prolonged_covid_intubation(
    inputs: dict[str, Any],
) -> RespiratoryAlertResult:
    """Evaluate prolonged intubation in COVID-19 patients.

    RATIFIED per rat-ventilacao-05: Different thresholds for COVID vs non-COVID.
    COVID: >= 14 days, Non-COVID: > 10 days.

    Already covered in evaluate_prolonged_intubation (ALERT-RESP-PROLONGED-INTUB-05).
    This is an explicit COVID-dedicated variant.
    """
    result = RespiratoryAlertResult(
        alert_id="ALERT-RESP-PROLONGED-COVID-09",
        name="Intubação prolongada em COVID-19 — avaliar traqueostomia",
        fired=False,
    )

    dispositivo = inputs.get("dispositivo_via_aerea")
    dias_vm = inputs.get("dias_em_ventilacao_mecanica")
    covid = inputs.get("covid19_ativo", False)

    if dispositivo != "TOT":
        return result

    if not covid:
        return result  # Use non-COVID variant instead

    if dias_vm is None:
        return result

    dias = float(dias_vm)

    # >= 14 days inclusive for COVID
    if dias >= 14:
        result.fired = True
        result.band = "watch"
        result.severity = SeverityLevel.WATCH
        result.metadata = {
            "dispositivo_via_aerea": dispositivo,
            "dias_em_ventilacao_mecanica": dias,
            "covid19_ativo": True,
            "threshold_days": 14,
        }

    return result


# ---------------------------------------------------------------------------
# ALERT-RESP-EXTUBATION-BUNDLE-10: Bundle de prontidão para extubação
# (rat-ventilacao-06, RULE-VENTILACAO-011, P0 RATIFY)
# ---------------------------------------------------------------------------


def evaluate_extubation_readiness_bundle(
    inputs: dict[str, Any],
) -> RespiratoryAlertResult:
    """Evaluate extubation-readiness bundle — all criteria sustained.

    RATIFIED per rat-ventilacao-06 (recommended default B):
    FiO2 <= 0.40 (FRACTION), PEEP <= 8 cmH2O, adequate oxygenation (P/F >= 150),
    RR criterion, no/minimal vasopressors, adequate consciousness.

    International Consensus Conference on weaning (Boles, ERJ 2007).
    FiO2 as FRACTION throughout.
    """
    result = RespiratoryAlertResult(
        alert_id="ALERT-RESP-EXTUBATION-BUNDLE-10",
        name="Bundle de prontidão para extubação (ERS/ATS 2007)",
        fired=False,
    )

    fio2 = _ensure_fio2_fraction(inputs.get("fio2"))
    peep = inputs.get("peep")
    pf = _compute_pf_ratio(inputs.get("pao2"), inputs.get("fio2"))
    rr = inputs.get("frequencia_respiratoria")
    dose_vaso = inputs.get("dose_vasopressor")
    gcs = inputs.get("glasgow")
    rass = inputs.get("rass")

    # All criteria must be met
    criteria_met = 0
    total_needed = 5

    # Criterion 1: FiO2 <= 0.40
    if fio2 is not None and fio2 <= 0.40:
        criteria_met += 1

    # Criterion 2: PEEP <= 8
    if peep is not None and float(peep) <= 8:
        criteria_met += 1

    # Criterion 3: Adequate oxygenation (P/F >= 150)
    if pf is not None and pf >= 150:
        criteria_met += 1

    # Criterion 4: Adequate consciousness (GCS > 8 OR RASS >= -2)
    consciousness_ok = False
    if gcs is not None and float(gcs) > 8:
        consciousness_ok = True
    if rass is not None and float(rass) >= -2:
        consciousness_ok = True
    if consciousness_ok:
        criteria_met += 1

    # Criterion 5: No/minimal vasopressors (<= 0.2 mcg/kg/min or absent)
    vaso_ok = False
    if dose_vaso is None or float(dose_vaso) <= 0.2:
        vaso_ok = True
    if vaso_ok:
        criteria_met += 1

    if criteria_met >= total_needed:
        result.fired = True
        result.band = "normal"
        result.severity = SeverityLevel.NORMAL
        result.metadata = {
            "fio2_fraction": fio2,
            "peep": peep,
            "pf_ratio": pf,
            "frequencia_respiratoria": rr,
            "dose_vasopressor": dose_vaso,
            "glasgow": gcs,
            "rass": rass,
            "criteria_met": criteria_met,
            "total_needed": total_needed,
            "recommendation": "Paciente preenche critérios para teste de respiração espontânea (TRE)",
        }

    return result


# ---------------------------------------------------------------------------
# ALERT-RESP-PAIN-ASSESS-11: Avaliação de dor — escala numérica 0-10
# (RAT-CLINICAL-SCORING-05 RATIFIED)
# ---------------------------------------------------------------------------


def evaluate_pain_assessment(
    inputs: dict[str, Any],
) -> RespiratoryAlertResult:
    """Evaluate pain scale with band thresholds (NRS 0-10, RATIFIED).

    RATIFIED per RAT-CLINICAL-SCORING-05 (recommended defaults):
      - Severe pain:  NRS 7-10 (critical/urgent)
      - Moderate pain: NRS 4-6 (watch)
      - Mild pain:     NRS 1-3 (normal)
      - No pain:       NRS 0

    Behavioral Pain Scale (BPS 3-12) as fallback for non-communicative patients:
      - Severe:  BPS 10-12
      - Moderate: BPS 7-9
      - Mild:     BPS 3-6

    Boundary: inclusive for both ends of each band.
    NRS (Numeric Rating Scale) is primary; BPS is used when NRS unavailable.
    """
    result = RespiratoryAlertResult(
        alert_id="ALERT-RESP-PAIN-ASSESS-11",
        name="Avaliação de dor — escala numérica (NRS 0-10) / comportamental (BPS 3-12)",
        fired=False,
    )

    nrs = inputs.get("escala_dor_numerica")
    bps = inputs.get("escala_dor_comportamental")
    sedated = inputs.get("rass")
    is_sedated = sedated is not None and float(sedated) <= -3

    band = None
    pain_score = None

    # Primary: NRS (for communicative patients)
    if nrs is not None and not is_sedated:
        try:
            score = float(nrs)
            pain_score = score
            if score >= 7:
                band = "critical" if score >= 9 else "urgent"
            elif score >= 4:
                band = "watch"
            elif score >= 1:
                band = "normal"
            # score == 0: no fire
        except (ValueError, TypeError):
            pass

    # Fallback: BPS (for non-communicative/sedated patients)
    if band is None and bps is not None:
        try:
            score = float(bps)
            pain_score = score
            if score >= 10:
                band = "critical"
            elif score >= 7:
                band = "urgent"
            elif score >= 4:
                band = "watch"
            elif score >= 3:
                band = "normal"
        except (ValueError, TypeError):
            pass

    if band is None:
        return result

    result.fired = True
    result.band = band
    result.severity = _band_severity(band)
    result.metadata = {
        "escala_dor_numerica": nrs,
        "escala_dor_comportamental": bps,
        "pain_score": pain_score,
        "scale_used": "NRS" if nrs is not None else "BPS",
        "is_sedated": is_sedated,
        "band_thresholds": {
            "NRS_severe": "7-10",
            "NRS_moderate": "4-6",
            "NRS_mild": "1-3",
            "BPS_severe": "10-12",
            "BPS_moderate": "7-9",
            "BPS_mild": "3-6",
        },
    }

    return result


# ---------------------------------------------------------------------------
# Unified evaluator: evaluate all 11 alerts
# ---------------------------------------------------------------------------


def evaluate_all(inputs: dict[str, Any]) -> dict[str, RespiratoryAlertResult]:
    """Evaluate all 11 respiratory alerts for a set of clinical inputs.

    Returns a dict keyed by alert_id with results. Unfired alerts
    have fired=False.
    """
    evaluators = [
        evaluate_ards_staging,
        evaluate_deterioration,
        evaluate_asynchrony,
        evaluate_weaning_ready,
        evaluate_prolonged_intubation,
        # WAVE 3A ventilation RATIFY alerts (P1 + P0 extubation)
        evaluate_high_pplat_tidal,
        evaluate_peep_fio2_moderate,
        evaluate_peep_fio2_severe,
        evaluate_prolonged_covid_intubation,
        evaluate_extubation_readiness_bundle,
        # WAVE 1B: Pain assessment RATIFIED (RAT-CLINICAL-SCORING-05)
        evaluate_pain_assessment,
    ]

    results: dict[str, RespiratoryAlertResult] = {}
    for fn in evaluators:
        r = fn(inputs)
        results[r.alert_id] = r

    return results


# ---------------------------------------------------------------------------
# CRIT non-auto-resolve guard
# ---------------------------------------------------------------------------


def should_auto_resolve(
    alert_result: RespiratoryAlertResult,
    current_inputs: dict[str, Any],
    is_stale: bool = False,
) -> bool:
    """Determine whether a fired alert should auto-resolve.

    CRITICAL RULE: CRIT severity NEVER auto-resolves, even on stale data.
    The alert persists until a clinician explicitly acknowledges and resolves it.
    Watch/urgent alerts may auto-resolve when inputs return to normal range.

    Returns True if the alert should auto-resolve, False otherwise.
    """
    if alert_result.severity == SeverityLevel.CRITICAL:
        return False  # NEVER auto-resolve CRIT

    # For watch/urgent: auto-resolve if stale
    return is_stale


# ---------------------------------------------------------------------------
# Alert definitions for seeding
# ---------------------------------------------------------------------------


RESPIRATORY_ALERT_DEFINITIONS = [
    {
        "definition_version": "ALERT-RESP-ARDS-STAGING-01-a1b2c3",
        "score_type": "ARDS_STAGING",
        "semver": "3.0.0",
        "spec_hash": "re01a1b2c3d4e5f6",
        "description": (
            "ALERT-RESP-ARDS-STAGING-01: SDRA — vigilância e estadiamento de Berlin (S/F e P/F). "
            "Stage(leve, WATCH): S/F<=315; moderate(urgent): S/F<=235; severe(critical): S/F<=148. "
            "PF authoritative override when ABG present. Berlin Definition (JAMA 2012). "
            "FiO2 FRACTION enforced (CANON_PINS RATIFIED). v3.0.0 CLINICALLY RATIFIED."
        ),
    },
    {
        "definition_version": "ALERT-RESP-DETERIORATION-02-b2c3d4",
        "score_type": "VENT_DETERIORATION",
        "semver": "3.0.0",
        "spec_hash": "re02b2c3d4e5f6a7",
        "description": (
            "ALERT-RESP-DETERIORATION-02: Deterioração ventilatória — tendência S/F e demanda de FiO2. "
            "ΔS/F <= -20% in 6h OR FiO2 escalation > 30% without SpO2 improvement. "
            ">=2 sample persistence. Rice 2017. FiO2 FRACTION. severity=urgent."
        ),
    },
    {
        "definition_version": "ALERT-RESP-ASYNCHRONY-03-c3d4e5",
        "score_type": "ASYNCHRONY",
        "semver": "3.0.0",
        "spec_hash": "re03c3d4e5f6a7b8",
        "description": (
            "ALERT-RESP-ASYNCHRONY-03: Assincronia paciente-ventilador. "
            "Spontaneous RR > set RR AND plateau > 30 cmH2O. "
            "Thille 2016 + Amato 2015. Degrades on absent plateau. severity=watch. v3.0.0 RATIFIED."
        ),
    },
    {
        "definition_version": "ALERT-RESP-WEANING-READY-04-d4e5f6",
        "score_type": "WEANING_READY",
        "semver": "3.0.0",
        "spec_hash": "re04d4e5f6a7b8c9",
        "description": (
            "ALERT-RESP-WEANING-READY-04: Prontidão para desmame / extubação. "
            "S/F>315 + PEEP<=8 + FiO2<=0.40 + RSBI<105 + RASS>=-2 + GCS>=10 + "
            "vasopressor<=0.2 + days>=1. Boles 2007 + Yang/Tobin 1991. "
            "severity=normal. v3.0.0 RATIFIED (RAT-CLINICAL-SCORING-06)."
        ),
    },
    {
        "definition_version": "ALERT-RESP-PROLONGED-INTUB-05-e5f6a7",
        "score_type": "PROLONGED_INTUB",
        "semver": "3.0.0",
        "spec_hash": "re05e5f6a7b8c9d0",
        "description": (
            "ALERT-RESP-PROLONGED-INTUB-05: Intubação prolongada — avaliar traqueostomia. "
            "TOT + days>10 (non-COVID) or >=14 (COVID active). "
            "Young/JAMA 2013 (TracMan) + AAO-HNS 2020. severity=watch."
        ),
    },
    {
        "definition_version": "ALERT-RESP-PAIN-ASSESS-11-f6a7b8",
        "score_type": "PAIN_ASSESSMENT",
        "semver": "3.0.0",
        "spec_hash": "re11f6a7b8c9d0e1",
        "description": (
            "ALERT-RESP-PAIN-ASSESS-11: Avaliação de dor — NRS 0-10 / BPS 3-12. "
            "RAT-CLINICAL-SCORING-05 RATIFIED. NRS severe 7-10 (critical/urgent), "
            "moderate 4-6 (watch), mild 1-3 (normal). BPS fallback for sedated. "
            "PADIS 2018 + Chanques CCM 2006. severity varies by band."
        ),
    },
]
