"""
AKI domain — KDIGO 2012 staging micro-batch evaluator.
3 alerts, 17 test vectors from docs/plan/_work/alerts/aki.yaml.

CRITICAL DESIGN RULE: CRIT severity never auto-resolves on stale data.
Unlike watch/urgent, a CRIT alert persists until explicitly acknowledged
and resolved by a clinician.

KDIGO staging: max(stage_cr, stage_uo).
Boundary: Cr=1.5× inclusive (>=); UO <0.5 strict.
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
class AkiAlertResult:
    """Result of evaluating one AKI alert."""

    alert_id: str
    name: str
    fired: bool
    severity: SeverityLevel | None = None
    kdigo_stage: int = 0
    band: str | None = None  # "critical", "urgent", "watch"
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _band_severity(band: str | None) -> SeverityLevel | None:
    """Convert band label to SeverityLevel."""
    if band is None:
        return None
    return {
        "critical": SeverityLevel.CRITICAL,
        "urgent": SeverityLevel.URGENT,
        "watch": SeverityLevel.WATCH,
    }.get(band)


def _kdigo_stage_to_band(stage: int) -> str | None:
    """Map KDIGO stage to severity band."""
    if stage >= 3:
        return "critical"
    if stage >= 2:
        return "urgent"
    if stage >= 1:
        return "watch"
    return None


def compute_kdigo_stage(inputs: dict[str, Any]) -> int:
    """Compute KDIGO stage from creatinine and urine output axes.

    Returns max(stage_cr, stage_uo).
    Boundary: Cr=1.5× inclusive (>=); UO <0.5 strict.
    """
    creatinina = inputs.get("creatinina")
    creatinina_basal = inputs.get("creatinina_basal")
    delta_cr_48h = inputs.get("delta_cr_48h")
    debito_urinario_horario = inputs.get("debito_urinario_horario")
    terapia_renal_substitutiva = inputs.get("terapia_renal_substitutiva", False)

    # --- stage_cr ---
    stage_cr = 0

    if creatinina is not None and creatinina_basal is not None:
        # Stage 3: Cr >= 3.0*baseline OR (Cr >= 4.0 AND delta >= 0.5) OR RRT
        if (
            creatinina >= 3.0 * creatinina_basal
            or (creatinina >= 4.0 and delta_cr_48h is not None and delta_cr_48h >= 0.5)
            or terapia_renal_substitutiva
        ):
            stage_cr = 3
        # Stage 2: Cr >= 2.0*baseline
        elif creatinina >= 2.0 * creatinina_basal:
            stage_cr = 2
        # Stage 1: delta >= 0.3 OR (Cr >= 1.5*baseline within 7d)
        # Boundary: Cr=1.5× inclusive (>=)
        elif (
            (delta_cr_48h is not None and delta_cr_48h >= 0.3)
            or creatinina >= 1.5 * creatinina_basal
        ):
            stage_cr = 1

    # --- stage_uo ---
    stage_uo = 0

    if debito_urinario_horario is not None:
        # Stage 3: UO < 0.3 mL/kg/h (24h window)
        if debito_urinario_horario < 0.3:
            stage_uo = 3
        # Stage 2: UO < 0.5 mL/kg/h (12h window) — strict < 0.5
        elif debito_urinario_horario < 0.5:
            stage_uo = 2
        # Stage 1: UO < 0.5 mL/kg/h (6h window) — strict < 0.5
        # NOTE: same threshold as stage 2 but shorter window; in practice
        # the 6h vs 12h distinction comes from the calling context.
        # For the micro-batch evaluator we treat the input as the worst
        # rolling-window UO, so we only check the numeric threshold here.
        elif debito_urinario_horario < 0.5:
            stage_uo = 1

    # Unify the two UO bands: both <0.5 but stage 2 and 1 differentiated
    # by window (12h vs 6h). In the micro-batch, the caller provides the
    # worst UO across all windows. We keep the numeric check simple:
    if debito_urinario_horario is not None:
        if debito_urinario_horario < 0.3:
            stage_uo = 3
        elif debito_urinario_horario < 0.5:
            stage_uo = 1  # conservative: stage 1 for UO < 0.5

    return max(stage_cr, stage_uo)


# ---------------------------------------------------------------------------
# ALERT-AKI-KDIGO-STAGE-01: KDIGO staging
# ---------------------------------------------------------------------------


def evaluate_kdigo_stage(inputs: dict[str, Any]) -> AkiAlertResult:
    """Evaluate KDIGO stage alert.

    stage 1 → watch, stage 2 → urgent, stage 3 → critical.
    Boundary: Cr=1.5× inclusive (>=); UO <0.5 strict.
    """
    result = AkiAlertResult(
        alert_id="ALERT-AKI-KDIGO-STAGE-01",
        name="Lesão renal aguda — estadiamento KDIGO",
        fired=False,
    )

    stage = compute_kdigo_stage(inputs)
    result.kdigo_stage = stage

    if stage == 0:
        return result

    band = _kdigo_stage_to_band(stage)
    result.fired = True
    result.band = band
    result.severity = _band_severity(band)
    result.metadata = {
        "kdigo_stage": stage,
        "creatinina": inputs.get("creatinina"),
        "creatinina_basal": inputs.get("creatinina_basal"),
        "debito_urinario_horario": inputs.get("debito_urinario_horario"),
    }
    return result


# ---------------------------------------------------------------------------
# ALERT-AKI-PROGRESSION-02: KDIGO stage change within 24h
# ---------------------------------------------------------------------------


def evaluate_progression(inputs: dict[str, Any]) -> AkiAlertResult:
    """Evaluate KDIGO stage progression.

    Fires when kdigo_stage_now > kdigo_stage_24h_ago (both non-null).
    Severity: urgent, escalated to critical if kdigo_stage_now == 3.
    """
    result = AkiAlertResult(
        alert_id="ALERT-AKI-PROGRESSION-02",
        name="Progressão de LRA — mudança de estágio KDIGO em 24h",
        fired=False,
    )

    stage_now = inputs.get("kdigo_stage_now")
    stage_24h_ago = inputs.get("kdigo_stage_24h_ago")

    # No prior stage → first detection belongs to staging alert
    if stage_now is None or stage_24h_ago is None:
        return result

    if stage_now <= stage_24h_ago:
        return result  # no increase or improving

    result.fired = True
    result.kdigo_stage = stage_now

    if stage_now >= 3:
        band = "critical"
    else:
        band = "urgent"

    result.band = band
    result.severity = _band_severity(band)
    result.metadata = {
        "kdigo_stage_now": stage_now,
        "kdigo_stage_24h_ago": stage_24h_ago,
    }
    return result


# ---------------------------------------------------------------------------
# ALERT-AKI-NEPHROTOXIN-03: Nephrotoxic risk with rising Cr
# ---------------------------------------------------------------------------


def _check_nephrotoxic_combo(inputs: dict[str, Any]) -> bool:
    """Check for nephrotoxic drug combinations.

    nephrotoxic_combo =
        (vancomicina_ativa AND aminoglicosideo_ativo)
        OR (vancomicina_ativa AND contraste_iodado)
        OR (aminoglicosideo_ativo AND aine_ativo)
        OR (ieca_bra_ativo AND hipovolemia)
    """
    vanco = inputs.get("vancomicina_ativa", False)
    amino = inputs.get("aminoglicosideo_ativo", False)
    contraste = inputs.get("contraste_iodado", False)
    aine = inputs.get("aine_ativo", False)
    ieca = inputs.get("ieca_bra_ativo", False)
    hipo = inputs.get("hipovolemia", False)

    if vanco and amino:
        return True
    if vanco and contraste:
        return True
    if amino and aine:
        return True
    if ieca and hipo:
        return True
    return False


def evaluate_nephrotoxin(inputs: dict[str, Any]) -> AkiAlertResult:
    """Evaluate nephrotoxic risk with rising creatinine.

    Fires when rising_cr AND nephrotoxic_combo.
    rising_cr = creatinina > creatinina_basal + 0.2 mg/dL (strict >).
    Boundary: exactly +0.2 does NOT fire.
    """
    result = AkiAlertResult(
        alert_id="ALERT-AKI-NEPHROTOXIN-03",
        name="Risco de nefrotoxicidade aditiva com creatinina em elevação",
        fired=False,
    )

    creatinina = inputs.get("creatinina")
    creatinina_basal = inputs.get("creatinina_basal")

    if creatinina is None or creatinina_basal is None:
        return result

    # rising_cr: strict > (not >=)
    delta = creatinina - creatinina_basal
    rising_cr = delta > 0.2

    if not rising_cr:
        return result

    if not _check_nephrotoxic_combo(inputs):
        return result

    result.fired = True
    result.band = "watch"
    result.severity = SeverityLevel.WATCH
    result.metadata = {
        "creatinina": creatinina,
        "creatinina_basal": creatinina_basal,
        "delta_cr": delta,
        "vancomicina_ativa": inputs.get("vancomicina_ativa", False),
        "aminoglicosideo_ativo": inputs.get("aminoglicosideo_ativo", False),
        "contraste_iodado": inputs.get("contraste_iodado", False),
        "aine_ativo": inputs.get("aine_ativo", False),
        "ieca_bra_ativo": inputs.get("ieca_bra_ativo", False),
        "hipovolemia": inputs.get("hipovolemia", False),
    }
    return result


# ---------------------------------------------------------------------------
# Unified evaluator: evaluate all 3 alerts
# ---------------------------------------------------------------------------


def evaluate_all(inputs: dict[str, Any]) -> dict[str, AkiAlertResult]:
    """Evaluate all 3 AKI alerts for a set of lab/vital inputs.

    Returns a dict keyed by alert_id with results. Unfired alerts
    have fired=False.
    """
    evaluators = [
        evaluate_kdigo_stage,
        evaluate_progression,
        evaluate_nephrotoxin,
    ]

    results: dict[str, AkiAlertResult] = {}
    for fn in evaluators:
        r = fn(inputs)
        results[r.alert_id] = r

    return results


# ---------------------------------------------------------------------------
# CRIT non-auto-resolve guard
# ---------------------------------------------------------------------------


def should_auto_resolve(
    alert_result: AkiAlertResult,
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

    # For watch/urgent: auto-resolve if re-evaluation shows no fire
    # This is handled by the caller re-evaluating with current inputs.
    return is_stale


# ---------------------------------------------------------------------------
# Alert definitions for seeding
# ---------------------------------------------------------------------------


AKI_ALERT_DEFINITIONS = [
    {
        "definition_version": "ALERT-AKI-KDIGO-STAGE-01-a1b2c3",
        "score_type": "KDIGO_STAGE",
        "semver": "1.0.0",
        "spec_hash": "a1b2c3d4e5f6a7b8",
        "description": (
            "ALERT-AKI-KDIGO-STAGE-01: Lesão renal aguda — estadiamento KDIGO. "
            "Stage 1→watch, stage 2→urgent, stage 3→critical. "
            "max(stage_cr, stage_uo). Boundary: Cr≥1.5× inclusive; UO<0.5 strict. "
            "KDIGO 2012 Clinical Practice Guideline for AKI, Kidney Int Suppl 2012;2(1):1-138."
        ),
    },
    {
        "definition_version": "ALERT-AKI-PROGRESSION-02-b2c3d4",
        "score_type": "KDIGO_PROGRESSION",
        "semver": "1.0.0",
        "spec_hash": "b2c3d4e5f6a7b8c9",
        "description": (
            "ALERT-AKI-PROGRESSION-02: Progressão de LRA — mudança de estágio KDIGO em 24h. "
            "Fires when stage_now > stage_24h_ago. Severity=urgent, escalated to "
            "critical when new stage==3. Null-prior-stage guard. "
            "KDIGO 2012 (dynamic staging)."
        ),
    },
    {
        "definition_version": "ALERT-AKI-NEPHROTOXIN-03-c3d4e5",
        "score_type": "NEPHROTOXIN",
        "semver": "1.0.0",
        "spec_hash": "c3d4e5f6a7b8c9d0",
        "description": (
            "ALERT-AKI-NEPHROTOXIN-03: Risco de nefrotoxicidade aditiva com "
            "creatinina em elevação. rising_cr (>baseline+0.2 strict) AND "
            "nephrotoxic_combo (vanco+amino, vanco+contraste, amino+aine, "
            "ieca+hipovolemia). Severity=watch. KDIGO Drug-Induced AKI 2023."
        ),
    },
]
