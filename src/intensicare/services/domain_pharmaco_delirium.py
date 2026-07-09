"""Domain runners for micro-batch alert evaluation from YAML catalogs.

WO-030 + WO-031: Drug Interactions + Delirium domain alert evaluation.
Each runner loads a YAML catalog, compiles alerts via alert_compiler,
and evaluates them against patient contexts in micro-batch mode.

Design:
- Micro-batch: evaluate all alerts for one patient context at a time
- Returns list of firing alert_ids with metadata
- Delegates expression evaluation to alert_compiler.evaluate_alert_definition()
"""

from __future__ import annotations

__version__ = "3.0.0"

import pathlib
from typing import Any

import yaml

from maezo.rules.alert_compiler import compile_all_alerts, evaluate_alert_definition

# ──────────────────────────────────────────────────────────────
# YAML catalog paths (relative to repository root)
# ──────────────────────────────────────────────────────────────

REPO_ROOT = pathlib.Path(__file__).parents[3]  # src/maezo/services -> maezo -> src -> repo root

PHARMACO_INTERACTION_CATALOG = REPO_ROOT / "docs" / "plan" / "_work" / "alerts" / "pharmaco-interaction.yaml"
NEURO_SEDATION_CATALOG = REPO_ROOT / "docs" / "plan" / "_work" / "alerts" / "neuro-sedation.yaml"


def _load_yaml(path: pathlib.Path) -> dict[str, Any]:
    """Load a YAML file and return parsed dict."""
    with path.open() as f:
        return yaml.safe_load(f)  # type: ignore[no-any-return]


def _build_context(vitals: dict[str, Any]) -> dict[str, Any]:
    """Normalize context keys for alert evaluation.

    All inputs are passed through directly — the alert compiler's
    _build_context handles scorer pre-computation.
    """
    return dict(vitals)


# ──────────────────────────────────────────────────────────────
# Pharmaco-Interaction Domain Runner
# ──────────────────────────────────────────────────────────────


def run_pharmaco_batch(
    patient_context: dict[str, Any],
    catalog_path: pathlib.Path | None = None,
) -> list[dict[str, Any]]:
    """Evaluate all drug interaction alerts for a given patient context.

    Micro-batch mode: all pharmaco-interaction alerts are evaluated
    against a single patient context and firing alerts are returned.

    Args:
        patient_context: Dict of clinical data for alert evaluation
            (e.g., on_warfarin, on_nsaid, inr, qtc_ms, medication_count, etc.)
        catalog_path: Optional override for the pharmaco-interaction YAML path.

    Returns:
        List of dicts with firing alert metadata:
        - alert_id: str
        - name: str
        - severity: str
        - condition: str
    """
    path = catalog_path or PHARMACO_INTERACTION_CATALOG
    catalog = _load_yaml(path)
    alerts = compile_all_alerts([catalog])
    ctx = _build_context(patient_context)

    firing: list[dict[str, Any]] = []
    for alert in alerts:
        try:
            if evaluate_alert_definition(alert, ctx):
                firing.append({
                    "alert_id": alert.get("alert_id", ""),
                    "name": alert.get("name", ""),
                    "severity": alert.get("severity", "unknown"),
                    "condition": alert.get("condition", ""),
                    "description": alert.get("description", ""),
                })
        except Exception:
            # Skip alerts that fail to evaluate (missing data, etc.)
            continue

    return firing


# ──────────────────────────────────────────────────────────────
# Delirium / Neuro-Sedation Domain Runner
# ──────────────────────────────────────────────────────────────


def run_delirium_batch(
    patient_context: dict[str, Any],
    catalog_path: pathlib.Path | None = None,
) -> list[dict[str, Any]]:
    """Evaluate all neuro-sedation/delirium alerts for a given patient context.

    Micro-batch mode: all delirium/neuro-sedation alerts are evaluated
    against a single patient context and firing alerts are returned.

    Args:
        patient_context: Dict of clinical data for alert evaluation
            (e.g., cam_icu_positive, rass_score, cpot_score, hours_since_last_sat, etc.)
        catalog_path: Optional override for the neuro-sedation YAML path.

    Returns:
        List of dicts with firing alert metadata:
        - alert_id: str
        - name: str
        - severity: str
        - condition: str
    """
    path = catalog_path or NEURO_SEDATION_CATALOG
    catalog = _load_yaml(path)
    alerts = compile_all_alerts([catalog])
    ctx = _build_context(patient_context)

    firing: list[dict[str, Any]] = []
    for alert in alerts:
        try:
            if evaluate_alert_definition(alert, ctx):
                firing.append({
                    "alert_id": alert.get("alert_id", ""),
                    "name": alert.get("name", ""),
                    "severity": alert.get("severity", "unknown"),
                    "condition": alert.get("condition", ""),
                    "description": alert.get("description", ""),
                })
        except Exception:
            # Skip alerts that fail to evaluate (missing data, etc.)
            continue

    return firing


# ──────────────────────────────────────────────────────────────
# Sedation RATIFY alerts (WAVE 3A)
# ──────────────────────────────────────────────────────────────


# ---------------------------------------------------------------------------
# SEDATION REDUCTION — Daily awakening / spontaneous awakening trial
# (rat-sedacao-02, RULE-SEDACAO-009, P1 RATIFY)
# ---------------------------------------------------------------------------


def evaluate_sedation_morning_reduction(
    patient_context: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate daily sedation reduction (>=50% morning reduction).

    RATIFIED per rat-sedacao-02 (recommended default B):
    Generalize to daily sedation-interruption check, PADIS-aligned.
    Evaluates whether sedative dose was reduced by >=50% between
    the last two assessments (morning window).

    Returns a dict with:
      - fired: bool
      - reduction_pct: float (positive = reduction, negative = increase)
      - sedation_active: bool
      - recommendation: str
    """
    reduction_pct = None
    sedation_active = False

    dose_atual = patient_context.get("dose_sedativo_atual")
    dose_anterior = patient_context.get("dose_sedativo_anterior")
    sedativo_em_uso = patient_context.get("sedativo_em_uso", False)

    if not sedativo_em_uso:
        return {
            "alert_id": "SED-REDUCTION-01",
            "fired": False,
            "reduction_pct": reduction_pct,
            "sedation_active": sedation_active,
            "recommendation": "Sem sedativo ativo — critério não aplicável",
        }

    sedation_active = True

    if dose_atual is None or dose_anterior is None:
        return {
            "alert_id": "SED-REDUCTION-01",
            "fired": False,
            "reduction_pct": reduction_pct,
            "sedation_active": True,
            "recommendation": "Dados insuficientes para avaliar redução",
        }

    try:
        d_atual = float(dose_atual)
        d_anterior = float(dose_anterior)
    except (ValueError, TypeError):
        return {
            "alert_id": "SED-REDUCTION-01",
            "fired": False,
            "reduction_pct": None,
            "sedation_active": True,
            "recommendation": "Dose inválida",
        }

    if d_anterior <= 0:
        return {
            "alert_id": "SED-REDUCTION-01",
            "fired": False,
            "reduction_pct": 0.0,
            "sedation_active": True,
            "recommendation": "Dose anterior zero — sem referência para redução",
        }

    reduction_pct = round(((d_anterior - d_atual) / d_anterior) * 100, 1)

    # >= 50% reduction = good (no alert)
    # < 50% reduction = fires (need more reduction)
    if reduction_pct >= 50:
        return {
            "alert_id": "SED-REDUCTION-01",
            "fired": False,
            "reduction_pct": reduction_pct,
            "sedation_active": True,
            "recommendation": "Redução matinal >= 50% alcançada — manter despertar diário",
        }
    else:
        return {
            "alert_id": "SED-REDUCTION-01",
            "fired": True,
            "reduction_pct": reduction_pct,
            "sedation_active": True,
            "recommendation": (
                f"Redução matinal de apenas {reduction_pct}% (< 50%). "
                "Avaliar interrupção diária da sedação (SAT) conforme PADIS 2018"
            ),
        }


# ---------------------------------------------------------------------------
# SEDATION ASSESSMENT — RASS / CAM-ICU integrated evaluation
# ---------------------------------------------------------------------------


def evaluate_sedation_rass_camicu(
    patient_context: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate RASS + CAM-ICU for sedation depth and delirium.

    RATIFIED: RASS range -5 to +4, CAM-ICU positive means delirium.
    Flags:
      - Deep sedation: RASS <= -3
      - Undersedation: RASS >= +2
      - Delirium: CAM-ICU positive
      - Target RASS: -2 to 0 for most ICU patients (PADIS 2018)

    Returns evaluation with severity and recommendations.
    """
    rass = patient_context.get("rass_score")
    cam_icu = patient_context.get("cam_icu_positive", False)
    target_rass_min = patient_context.get("target_rass_min", -2)
    target_rass_max = patient_context.get("target_rass_max", 0)
    on_ventilator = patient_context.get("on_mechanical_ventilation", False)

    result = {
        "alert_id": "SED-RASS-01",
        "fired": False,
        "rass": rass,
        "cam_icu_positive": cam_icu,
        "deep_sedation": False,
        "undersedation": False,
        "outside_target": False,
        "delirium_detected": cam_icu,
        "severity": "normal",
        "recommendations": [],
    }

    if rass is None:
        result["recommendations"].append("RASS não registrado — avaliar nível de sedação")
        return result

    try:
        rass_val = int(rass)
    except (ValueError, TypeError):
        result["recommendations"].append("Valor RASS inválido")
        return result

    # Boundary checks
    if rass_val < -5 or rass_val > 4:
        result["recommendations"].append(f"RASS {rass_val} fora do intervalo válido [-5, +4]")
        return result

    # Deep sedation: RASS -3 to -5
    if rass_val <= -3:
        result["deep_sedation"] = True
        result["fired"] = True
        result["severity"] = "urgent" if rass_val <= -4 else "watch"
        result["recommendations"].append(
            f"Sedação profunda (RASS {rass_val}). "
            "Avaliar redução se não houver indicação específica "
            "(ex.: SDRA grave, hipertensão intracraniana, BNM)"
        )

    # Target range evaluation
    if rass_val < target_rass_min or rass_val > target_rass_max:
        result["outside_target"] = True
        if not result["fired"]:
            result["fired"] = True
            result["severity"] = "watch"

    # Undersedation: RASS >= +2
    if rass_val >= 2:
        result["undersedation"] = True
        result["fired"] = True
        result["severity"] = "urgent" if rass_val >= 3 else "watch"
        result["recommendations"].append(
            f"Agitação (RASS {rass_val}). Avaliar dor, delirium e "
            "necessidade de ajuste de sedação"
        )

    # CAM-ICU delirium
    if cam_icu:
        if rass_val >= 0:
            result["recommendations"].append(
                "Delirium hiperativo (CAM-ICU + com RASS >= 0). "
                "Avaliar farmacoterapia (dexmedetomidina/haloperidol) e medidas não farmacológicas"
            )
        else:
            result["recommendations"].append(
                "Delirium hipoativo (CAM-ICU + com RASS < 0). "
                "Avaliar suspensão de benzodiazepínicos, mobilização precoce"
            )
        if not result["fired"]:
            result["fired"] = True
            result["severity"] = "watch"

    # Ventilator-specific PADIS guidance
    if on_ventilator and result["deep_sedation"]:
        result["recommendations"].append(
            "Ventilado com sedação profunda — SAT (spontaneous awakening trial) "
            "diariamente se critérios de segurança presentes (PADIS 2018)"
        )

    return result


# ──────────────────────────────────────────────────────────────
# WAVE 3A: Enhanced domain evaluation including sedation RATIFY
# ──────────────────────────────────────────────────────────────


def evaluate_all_domains(
    patient_context: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    """Evaluate all domain alerts for a patient context.

    This is the integration point for the Gold Reader poll cycle.
    Runs pharmaco, delirium, and sedation+stability micro-batches
    and returns all firing alerts grouped by domain.

    Args:
        patient_context: Dict of clinical data.

    Returns:
        Dict mapping domain name to list of firing alerts.
    """
    # Core pharmaco-interaction and delirium evaluation
    pharmaco_alerts = run_pharmaco_batch(patient_context)
    delirium_alerts = run_delirium_batch(patient_context)

    # WAVE 3A: Sedation RATIFY evaluation
    sedation_reduction = evaluate_sedation_morning_reduction(patient_context)
    sedation_rass = evaluate_sedation_rass_camicu(patient_context)

    sedation_alerts = []
    if sedation_reduction.get("fired"):
        sedation_alerts.append(sedation_reduction)
    if sedation_rass.get("fired"):
        sedation_alerts.append(sedation_rass)

    return {
        "pharmaco": pharmaco_alerts,
        "delirium": delirium_alerts,
        "sedation_ratify": sedation_alerts,
    }
