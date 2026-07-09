"""
Electrolyte domain — expedited micro-batch evaluator (~1-2 min poll).
6 alerts, 39 test vectors from docs/plan/_work/alerts/electrolyte.yaml.

CRITICAL DESIGN RULE: CRIT severity never auto-resolves on stale data.
Unlike watch/urgent, a CRIT alert persists until explicitly acknowledged
and resolved by a clinician. The alert may escalate (worsening band) but
never downgrades or auto-clears due to data staleness.
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
class ElectrolyteAlertResult:
    """Result of evaluating one electrolyte alert."""

    alert_id: str
    name: str
    fired: bool
    severity: SeverityLevel | None = None
    direction: str | None = None  # "hyper", "hypo", or None
    band: str | None = None       # "critical", "urgent", "watch"
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
    }.get(band)


# ---------------------------------------------------------------------------
# ALERT-ELY-POTASSIUM-01: Distúrbio grave do potássio
# ---------------------------------------------------------------------------


def evaluate_potassium(inputs: dict[str, Any]) -> ElectrolyteAlertResult:
    """Evaluate potassium disturbance (hyperkalemia / hypokalemia).

    HYPER: critical if potassio > 6.5; urgent if > 6.0 (and <= 6.5);
           watch if > 5.5 AND delta_k_24h > 0.5 AND
           (ckd_moderada_grave OR medicamento_hipercalemiante_ativo OR digoxina_ativa).

    HYPO: critical if potassio < 2.5; urgent if < 3.0 (and >= 2.5);
          watch if < 3.5 AND (qtc > 500 OR furosemida_dose_alta OR digoxina_ativa OR magnesio < 0.7).

    DIGOXIN pairing: if digoxina_ativa AND (potassio > 6.0 OR potassio < 3.0),
    attach digoxin_toxicity_context=true.
    """
    result = ElectrolyteAlertResult(
        alert_id="ALERT-ELY-POTASSIUM-01",
        name="Distúrbio grave do potássio — hipercalemia/hipocalemia",
        fired=False,
    )

    potassio = inputs.get("potassio")
    if potassio is None:
        return result

    delta_k_24h = inputs.get("delta_k_24h")
    magnesio = inputs.get("magnesio")
    qtc = inputs.get("qtc")
    digoxina_ativa = inputs.get("digoxina_ativa", False)
    medicamento_hipercalemiante_ativo = inputs.get("medicamento_hipercalemiante_ativo", False)
    ckd_moderada_grave = inputs.get("ckd_moderada_grave", False)
    furosemida_dose_alta = inputs.get("furosemida_dose_alta", False)

    # Determine worst band across hyper and hypo axes
    hyper_band = None
    hypo_band = None

    # --- HYPER axis ---
    if potassio > 6.5:
        hyper_band = "critical"
    elif potassio > 6.0:
        hyper_band = "urgent"
    elif potassio > 5.5:
        if (delta_k_24h is not None and delta_k_24h > 0.5
                and (ckd_moderada_grave or medicamento_hipercalemiante_ativo or digoxina_ativa)):
            hyper_band = "watch"

    # --- HYPO axis ---
    if potassio < 2.5:
        hypo_band = "critical"
    elif potassio < 3.0:
        hypo_band = "urgent"
    elif potassio < 3.5:
        if (qtc is not None and qtc > 500) or furosemida_dose_alta or digoxina_ativa or (magnesio is not None and magnesio < 0.7):
            hypo_band = "watch"

    # Determine direction and worst band
    if hyper_band and hypo_band:
        # Both axes trigger — pick the more severe band
        band_order = {"critical": 3, "urgent": 2, "watch": 1}
        hy_order = band_order.get(hyper_band, 0)
        ho_order = band_order.get(hypo_band, 0)
        if hy_order >= ho_order:
            direction = "hyper"
            band = hyper_band
        else:
            direction = "hypo"
            band = hypo_band
    elif hyper_band:
        direction = "hyper"
        band = hyper_band
    elif hypo_band:
        direction = "hypo"
        band = hypo_band
    else:
        return result  # no-fire

    result.fired = True
    result.direction = direction
    result.band = band
    result.severity = _band_severity(band)

    # Digoxin pairing context
    digoxin_toxicity_context = False
    if digoxina_ativa and (potassio > 6.0 or potassio < 3.0):
        digoxin_toxicity_context = True

    result.metadata = {
        "potassio": potassio,
        "hyper_band": hyper_band,
        "hypo_band": hypo_band,
        "digoxin_toxicity_context": digoxin_toxicity_context,
    }
    return result


# ---------------------------------------------------------------------------
# ALERT-ELY-SODIUM-01: Distúrbio grave do sódio
# ---------------------------------------------------------------------------


def evaluate_sodium(inputs: dict[str, Any]) -> ElectrolyteAlertResult:
    """Evaluate sodium disturbance (hypernatremia / hyponatremia).

    Glucose correction: sodio_corrigido = sodio + 0.024*(glicemia - 100) when glicemia > 100.

    HYPER: critical if sodio > 160; urgent if > 155 (and <= 160);
           watch if > 150 AND delta_na_24h_trailing > 5.

    HYPO: critical if sodio < 120; urgent if < 125 (and >= 120);
          watch if < 130 AND delta_na_24h_trailing <= -5.
    """
    result = ElectrolyteAlertResult(
        alert_id="ALERT-ELY-SODIUM-01",
        name="Distúrbio grave do sódio — hipernatremia/hiponatremia",
        fired=False,
    )

    sodio = inputs.get("sodio")
    if sodio is None:
        return result

    glicemia = inputs.get("glicemia")
    delta_na_24h_trailing = inputs.get("delta_na_24h_trailing")

    # Glucose correction for pseudo-hyponatremia
    sodio_avaliado = sodio
    if glicemia is not None and glicemia > 100:
        sodio_avaliado = sodio + 0.024 * (glicemia - 100)

    hyper_band = None
    hypo_band = None

    # --- HYPER axis ---
    if sodio_avaliado > 160:
        hyper_band = "critical"
    elif sodio_avaliado > 155:
        hyper_band = "urgent"
    elif sodio_avaliado > 150:
        if delta_na_24h_trailing is not None and delta_na_24h_trailing > 5:
            hyper_band = "watch"

    # --- HYPO axis ---
    if sodio_avaliado < 120:
        hypo_band = "critical"
    elif sodio_avaliado < 125:
        hypo_band = "urgent"
    elif sodio_avaliado < 130:
        if delta_na_24h_trailing is not None and delta_na_24h_trailing <= -5:
            hypo_band = "watch"

    # Determine direction and worst band
    if hyper_band and hypo_band:
        band_order = {"critical": 3, "urgent": 2, "watch": 1}
        if band_order.get(hyper_band, 0) >= band_order.get(hypo_band, 0):
            direction = "hyper"
            band = hyper_band
        else:
            direction = "hypo"
            band = hypo_band
    elif hyper_band:
        direction = "hyper"
        band = hyper_band
    elif hypo_band:
        direction = "hypo"
        band = hypo_band
    else:
        return result

    result.fired = True
    result.direction = direction
    result.band = band
    result.severity = _band_severity(band)
    result.metadata = {
        "sodio": sodio,
        "sodio_corrigido": sodio_avaliado,
        "glicemia": glicemia,
    }
    return result


# ---------------------------------------------------------------------------
# ALERT-ELY-SODIUM-CORRECTION-02: Velocidade de correção do sódio perigosa
# ---------------------------------------------------------------------------


def evaluate_sodium_correction(inputs: dict[str, Any]) -> ElectrolyteAlertResult:
    """Evaluate sodium correction rate (osmotic demyelination risk).

    Uses correcao_na_24h_from_nadir (sodio_atual - sodio_nadir_24h),
    NOT the trailing delta_na_24h_trailing.

    critical if correcao_na_24h_from_nadir > 10 mmol/L/24h;
    urgent if > 8 mmol/L/24h (and <= 10).
    """
    result = ElectrolyteAlertResult(
        alert_id="ALERT-ELY-SODIUM-CORRECTION-02",
        name="Velocidade de correção do sódio perigosa — risco de desmielinização osmótica",
        fired=False,
    )

    correcao = inputs.get("correcao_na_24h_from_nadir")
    if correcao is None:
        return result

    band = None
    if correcao > 10:
        band = "critical"
    elif correcao > 8:
        band = "urgent"

    if band is None:
        return result

    result.fired = True
    result.band = band
    result.severity = _band_severity(band)
    result.metadata = {
        "correcao_na_24h_from_nadir": correcao,
        "sodio": inputs.get("sodio"),
        "sodio_nadir_24h": inputs.get("sodio_nadir_24h"),
    }
    return result


# ---------------------------------------------------------------------------
# ALERT-ELY-CALCIUM-01: Distúrbio grave do cálcio iônico
# ---------------------------------------------------------------------------


def evaluate_calcium(inputs: dict[str, Any]) -> ElectrolyteAlertResult:
    """Evaluate calcium disturbance (hypocalcemia / hypercalcemia).

    IONIZED calcium is primary; corrected TOTAL calcium is fallback.
    calcio_total_corrigido = calcio_total + 0.8*(4.0 - albumina), albumina in g/dL.

    HYPO critical: calcio_ionizado < 0.80 OR (unavailable AND calcio_total_corrigido < 7.0);
    HYPO urgent: calcio_ionizado < 0.90 (and >= 0.80).

    HYPER critical: calcio_ionizado > 1.60 OR (unavailable AND calcio_total_corrigido > 14.0);
    HYPER urgent: calcio_ionizado > 1.45 (and <= 1.60).
    """
    result = ElectrolyteAlertResult(
        alert_id="ALERT-ELY-CALCIUM-01",
        name="Distúrbio grave do cálcio iônico — hipocalcemia/hipercalcemia",
        fired=False,
    )

    calcio_ionizado = inputs.get("calcio_ionizado")
    calcio_total = inputs.get("calcio_total")
    albumina = inputs.get("albumina")
    qtc = inputs.get("qtc")

    # Compute corrected total calcium for fallback
    calcio_total_corrigido = None
    if calcio_total is not None and albumina is not None:
        calcio_total_corrigido = calcio_total + 0.8 * (4.0 - albumina)

    ionized_available = calcio_ionizado is not None

    hyper_band = None
    hypo_band = None

    # --- HYPO axis ---
    if ionized_available:
        if calcio_ionizado < 0.80:
            hypo_band = "critical"
        elif calcio_ionizado < 0.90:
            hypo_band = "urgent"
    elif calcio_total_corrigido is not None:
        # Fallback: corrected total calcium
        if calcio_total_corrigido < 7.0:
            hypo_band = "critical"

    # --- HYPER axis ---
    if ionized_available:
        if calcio_ionizado > 1.60:
            hyper_band = "critical"
        elif calcio_ionizado > 1.45:
            hyper_band = "urgent"
    elif calcio_total_corrigido is not None:
        if calcio_total_corrigido > 14.0:
            hyper_band = "critical"

    # Determine direction and worst band
    if hyper_band and hypo_band:
        band_order = {"critical": 3, "urgent": 2}
        if band_order.get(hyper_band, 0) >= band_order.get(hypo_band, 0):
            direction = "hyper"
            band = hyper_band
        else:
            direction = "hypo"
            band = hypo_band
    elif hyper_band:
        direction = "hyper"
        band = hyper_band
    elif hypo_band:
        direction = "hypo"
        band = hypo_band
    else:
        return result

    result.fired = True
    result.direction = direction
    result.band = band
    result.severity = _band_severity(band)
    result.metadata = {
        "calcio_ionizado": calcio_ionizado,
        "calcio_total": calcio_total,
        "albumina": albumina,
        "calcio_total_corrigido": calcio_total_corrigido,
        "ionized_available": ionized_available,
    }
    return result


# ---------------------------------------------------------------------------
# ALERT-ELY-MAGNESIUM-01: Hipomagnesemia grave
# ---------------------------------------------------------------------------


def evaluate_magnesium(inputs: dict[str, Any]) -> ElectrolyteAlertResult:
    """Evaluate hypomagnesemia.

    critical if magnesio < 0.5 mmol/L;
    urgent if magnesio < 0.7 mmol/L (and >= 0.5);
    watch if magnesio < 0.9 AND (potassio < 3.5 OR qtc > 500 ms).
    """
    result = ElectrolyteAlertResult(
        alert_id="ALERT-ELY-MAGNESIUM-01",
        name="Hipomagnesemia grave",
        fired=False,
    )

    magnesio = inputs.get("magnesio")
    if magnesio is None:
        return result

    potassio = inputs.get("potassio")
    qtc = inputs.get("qtc")

    band = None
    if magnesio < 0.5:
        band = "critical"
    elif magnesio < 0.7:
        band = "urgent"
    elif magnesio < 0.9:
        if (potassio is not None and potassio < 3.5) or (qtc is not None and qtc > 500):
            band = "watch"

    if band is None:
        return result

    result.fired = True
    result.band = band
    result.severity = _band_severity(band)
    result.metadata = {
        "magnesio": magnesio,
        "potassio": potassio,
        "qtc": qtc,
    }
    return result


# ---------------------------------------------------------------------------
# ALERT-ELY-PHOSPHATE-01: Distúrbio grave do fosfato
# ---------------------------------------------------------------------------
# CLINICALLY RATIFIED: RAT-ELY-01 — KDIGO phosphate management guidelines.
# Canonical unit mmol/L. Reference bands:
#   Hypophosphatemia:  < 0.8 mmol/L moderate (watch), < 0.3 mmol/L severe (urgent)
#   Hyperphosphatemia: > 1.5 mmol/L moderate (watch), > 2.5 mmol/L severe (critical)
# Reference: UpToDate / KDIGO phosphate management guidelines.


def evaluate_phosphate(inputs: dict[str, Any]) -> ElectrolyteAlertResult:
    """Evaluate phosphate disturbance (hypophosphatemia / hyperphosphatemia).

    CLINICALLY RATIFIED (RAT-ELY-01). KDIGO reference bands in mmol/L.

    HYPO: urgent if fosfato < 0.3 mmol/L (severe); watch if fosfato < 0.8 (moderate, >= 0.3).
    HYPER: critical if fosfato > 2.5 mmol/L (severe); watch if fosfato > 1.5 (moderate, <= 2.5).
    """
    result = ElectrolyteAlertResult(
        alert_id="ALERT-ELY-PHOSPHATE-01",
        name="Distúrbio grave do fosfato — hipofosfatemia/hiperfosfatemia",
        fired=False,
    )

    fosfato = inputs.get("fosfato")
    if fosfato is None:
        return result

    hyper_band = None
    hypo_band = None

    # --- HYPO axis ---
    if fosfato < 0.3:
        hypo_band = "urgent"      # severe hypophosphatemia
    elif fosfato < 0.8:
        hypo_band = "watch"       # moderate hypophosphatemia

    # --- HYPER axis ---
    if fosfato > 2.5:
        hyper_band = "critical"   # severe hyperphosphatemia
    elif fosfato > 1.5:
        hyper_band = "watch"      # moderate hyperphosphatemia

    # Determine direction and worst band
    if hyper_band and hypo_band:
        band_order = {"critical": 3, "urgent": 2, "watch": 1}
        if band_order.get(hyper_band, 0) >= band_order.get(hypo_band, 0):
            direction = "hyper"
            band = hyper_band
        else:
            direction = "hypo"
            band = hypo_band
    elif hyper_band:
        direction = "hyper"
        band = hyper_band
    elif hypo_band:
        direction = "hypo"
        band = hypo_band
    else:
        return result

    result.fired = True
    result.direction = direction
    result.band = band
    result.severity = _band_severity(band)
    result.metadata = {
        "fosfato": fosfato,
        "hyper_band": hyper_band,
        "hypo_band": hypo_band,
    }
    return result


# ---------------------------------------------------------------------------
# Unified evaluator: evaluate all 6 alerts
# ---------------------------------------------------------------------------


def evaluate_all(inputs: dict[str, Any]) -> dict[str, ElectrolyteAlertResult]:
    """Evaluate all 6 electrolyte alerts for a set of lab inputs.

    Returns a dict keyed by alert_id with results. Unfired alerts
    have fired=False.
    """
    evaluators = [
        evaluate_potassium,
        evaluate_sodium,
        evaluate_sodium_correction,
        evaluate_calcium,
        evaluate_magnesium,
        evaluate_phosphate,
    ]

    results: dict[str, ElectrolyteAlertResult] = {}
    for fn in evaluators:
        r = fn(inputs)
        results[r.alert_id] = r

    return results


# ---------------------------------------------------------------------------
# CRIT non-auto-resolve guard
# ---------------------------------------------------------------------------


def should_auto_resolve(
    alert_result: ElectrolyteAlertResult,
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
    # If stale, watch/urgent may auto-resolve (caller's choice).
    return is_stale


# ---------------------------------------------------------------------------
# Alert definitions for seeding
# ---------------------------------------------------------------------------

ELECTROLYTE_ALERT_DEFINITIONS = [
    {
        "definition_version": "ALERT-ELY-POTASSIUM-01-a1b2c3",
        "score_type": "POTASSIUM",
        "semver": "1.0.0",
        "spec_hash": "a1b2c3d4e5f6a7b8",
        "description": (
            "ALERT-ELY-POTASSIUM-01: Distúrbio grave do potássio — "
            "hipercalemia (>6.5 crit, >6.0 urg, >5.5+cofatores watch) / "
            "hipocalemia (<2.5 crit, <3.0 urg, <3.5+cofatores watch). "
            "Digoxin toxicity pairing. Per vision §3.6 VIS-3.6-02/03."
        ),
    },
    {
        "definition_version": "ALERT-ELY-SODIUM-01-b2c3d4",
        "score_type": "SODIUM",
        "semver": "1.0.0",
        "spec_hash": "b2c3d4e5f6a7b8c9",
        "description": (
            "ALERT-ELY-SODIUM-01: Distúrbio grave do sódio — "
            "hipernatremia (>160 crit, >155 urg, >150+delta>5 watch) / "
            "hiponatremia (<120 crit, <125 urg, <130+delta<=-5 watch). "
            "Glucose correction for pseudo-hyponatremia. Per vision §3.6 VIS-3.6-04/05."
        ),
    },
    {
        "definition_version": "ALERT-ELY-SODIUM-CORRECTION-02-c3d4e5",
        "score_type": "SODIUM_CORRECTION",
        "semver": "1.0.0",
        "spec_hash": "c3d4e5f6a7b8c9d0",
        "description": (
            "ALERT-ELY-SODIUM-CORRECTION-02: Velocidade de correção do sódio — "
            "risco de desmielinização osmótica. "
            "Usa correcao_na_24h_from_nadir (não trailing delta). "
            ">10 crit, >8 urg. HAZ-031 deterministic baseline. Per vision §3.6 VIS-3.6-06."
        ),
    },
    {
        "definition_version": "ALERT-ELY-CALCIUM-01-d4e5f6",
        "score_type": "CALCIUM",
        "semver": "1.0.0",
        "spec_hash": "d4e5f6a7b8c9d0e1",
        "description": (
            "ALERT-ELY-CALCIUM-01: Distúrbio grave do cálcio iônico — "
            "hipocalcemia (iCa<0.80 crit, <0.90 urg) / "
            "hipercalcemia (iCa>1.60 crit, >1.45 urg). "
            "Corrected total Ca fallback. Per vision §3.6 VIS-3.6-07/08."
        ),
    },
    {
        "definition_version": "ALERT-ELY-MAGNESIUM-01-e5f6a7",
        "score_type": "MAGNESIUM",
        "semver": "1.0.0",
        "spec_hash": "e5f6a7b8c9d0e1f2",
        "description": (
            "ALERT-ELY-MAGNESIUM-01: Hipomagnesemia grave — "
            "<0.5 crit, <0.7 urg, <0.9+K<3.5 ou QTc>500 watch. "
            "Per vision §3.6 VIS-3.6-09 (severity raised vs legacy ELY-006)."
        ),
    },
    {
        "definition_version": "ALERT-ELY-PHOSPHATE-01-g7h8i9",
        "score_type": "PHOSPHATE",
        "semver": "1.0.0",
        "spec_hash": "g7h8i9j0k1l2m3n4",
        "description": (
            "ALERT-ELY-PHOSPHATE-01: Distúrbio grave do fosfato — "
            "hipofosfatemia (<0.3 urg, <0.8 watch) / "
            "hiperfosfatemia (>2.5 crit, >1.5 watch). "
            "CLINICALLY RATIFIED: RAT-ELY-01 — KDIGO phosphate management guidelines. "
            "Canonical unit mmol/L. "
            "Reference: UpToDate / KDIGO phosphate management guidelines. "
            "Per vision §3.6 VIS-3.6-10."
        ),
    },
]
