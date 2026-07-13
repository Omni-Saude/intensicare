"""Hemodynamic Stability domain service — 27 criteria evaluator wrapping domain_hemo.py.

Architecture:
- Wraps domain_hemo.evaluate_all() (12 alerts) and adds 15 additional criteria
- 27 stability criteria across 6 categories:
    vasopressor(6), perfusion(5), cardiac_output(4), fluid_balance(5), lactate(4), combined(3)
- Score 0-27: count of criteria in warning/critical status
- Severity: 0-3=estavel, 4-9=atencao, 10+=critico
- Trend: 7-day history with direction (improving/stable/worsening)

CLINICAL RATIFICATION: rat-estabilidade-01 through rat-estabilidade-12 (P1 RATIFY).
"""

from __future__ import annotations

__version__ = "3.0.0"

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from typing import Any

from intensicare.services.domain_hemo import HemoAlertResult
from intensicare.services.domain_hemo import evaluate_all as evaluate_hemo_alerts

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 27 Stability criteria definitions
# ---------------------------------------------------------------------------

# Mapping from critério index → (name, category, threshold, alert_id or None)
STABILITY_CRITERIA: list[dict[str, str | None]] = [
    # ===== VASOPRESSOR (6 criteria) =====
    {
        "name": "Índice de choque > 0.9",
        "category": "vasopressor",
        "threshold": "SI > 0.9 ou MSI > 1.3 + corroborador de perfusão",
        "alert_id": "ALERT-HEMO-SHOCK-INDEX-01",
    },
    {
        "name": "Escalonamento de vasopressor > 50% em 2h",
        "category": "vasopressor",
        "threshold": "Dose atual > 1.5 × dose 2h atrás ou segundo agente iniciado",
        "alert_id": "ALERT-HEMO-VASO-ESCALATION-03",
    },
    {
        "name": "Vasopressor com balanço hídrico cumulativo negativo",
        "category": "vasopressor",
        "threshold": "Noradrenalina iniciada há < 6h + balanço < -2000 mL + sem bolus 500 mL 4h",
        "alert_id": "ALERT-HEMO-STABILITY-VASO-BALANCE-07",
    },
    {
        "name": "Noradrenalina em dose alta sem adjuntos",
        "category": "vasopressor",
        "threshold": "Dose > 0.5 mcg/kg/min sem vasopressina ou hidrocortisona",
        "alert_id": "ALERT-HEMO-STABILITY-HIGH-NORAD-09",
    },
    {
        "name": "Choque refratário — noradrenalina + vasopressina sem adrenalina",
        "category": "vasopressor",
        "threshold": "Noradrenalina > 0.5 + vasopressina ativa + adrenalina ausente",
        "alert_id": "ALERT-HEMO-STABILITY-REFRACTORY-10",
    },
    {
        "name": "Choque refratário — MAP < 65 com vasopressor máximo",
        "category": "vasopressor",
        "threshold": "MAP < 65 mmHg + noradrenalina > 1.0 mcg/kg/min",
        "alert_id": "ALERT-HEMO-REFRACTORY-SHOCK-04",
    },
    # ===== PERFUSION (5 criteria) =====
    {
        "name": "TEC > 3s em uso de noradrenalina",
        "category": "perfusion",
        "threshold": "TEC > 3 s (ANDROMEDA-SHOCK) + noradrenalina ativa",
        "alert_id": "ALERT-HEMO-STABILITY-CRT-NORAD-12",
    },
    {
        "name": "Lactato > 2 mmol/L (sem clearance)",
        "category": "perfusion",
        "threshold": "Lactato arterial > 2.0 mmol/L",
        "alert_id": None,  # Additional criterion beyond hemo alerts
    },
    {
        "name": "Lactato ≥ 4 mmol/L (choque tecidual)",
        "category": "perfusion",
        "threshold": "Lactato arterial ≥ 4.0 mmol/L",
        "alert_id": None,
    },
    {
        "name": "SvO2 < 65% (oferta/consumo O2)",
        "category": "perfusion",
        "threshold": "Saturação venosa mista < 65%",
        "alert_id": None,
    },
    {
        "name": "Delta PCO2 (gap) > 6 mmHg",
        "category": "perfusion",
        "threshold": "Gap PCO2 veno-arterial > 6 mmHg",
        "alert_id": None,
    },
    # ===== CARDIAC OUTPUT (4 criteria) =====
    {
        "name": "Índice cardíaco < 2.2 L/min/m²",
        "category": "cardiac_output",
        "threshold": "IC < 2.2 L/min/m²",
        "alert_id": None,
    },
    {
        "name": "Dobutamina com noradrenalina em dose alta",
        "category": "cardiac_output",
        "threshold": "Noradrenalina > 0.5 + dobutamina ativa (gate FC > 130)",
        "alert_id": "ALERT-HEMO-STABILITY-DOBUTAMINE-11",
    },
    {
        "name": "FC > 130 bpm sustentada",
        "category": "cardiac_output",
        "threshold": "Frequência cardíaca > 130 bpm",
        "alert_id": None,
    },
    {
        "name": "PAM < 65 mmHg (hipotensão)",
        "category": "cardiac_output",
        "threshold": "Pressão arterial média < 65 mmHg",
        "alert_id": None,
    },
    # ===== FLUID BALANCE (5 criteria) =====
    {
        "name": "Não responsivo a fluidos — risco de sobrecarga",
        "category": "fluid_balance",
        "threshold": "PPV/SVV < 10% + ΔSV < 10% + balanço > 3000 mL",
        "alert_id": "ALERT-HEMO-FLUID-NONRESPONSIVE-05",
    },
    {
        "name": "Balanço hídrico 24h > 3000 mL positivo",
        "category": "fluid_balance",
        "threshold": "Balanço acumulado 24h > +3000 mL",
        "alert_id": None,
    },
    {
        "name": "Balanço hídrico cumulativo < -2000 mL",
        "category": "fluid_balance",
        "threshold": "Balanço cumulativo < -2000 mL (desidratação)",
        "alert_id": None,
    },
    {
        "name": "Conflito anti-hipertensivo × PA / vasopressor",
        "category": "fluid_balance",
        "threshold": "Anti-hipertensivo ativo + hipotensão ou vasopressor",
        "alert_id": "ALERT-HEMO-ANTIHTN-CONFLICT-06",
    },
    {
        "name": "PPV > 13% ou SVV > 13% com resposta pobre a volume",
        "category": "fluid_balance",
        "threshold": "PPV > 13% ou SVV > 13% + ΔVS < 10% pós-volume",
        "alert_id": None,
    },
    # ===== LACTATE (4 criteria) =====
    {
        "name": "Clearance de lactato < 10% em 2h",
        "category": "lactate",
        "threshold": "Clearance < 10% em 2h durante ressuscitação ativa",
        "alert_id": "ALERT-HEMO-LACTATE-CLEARANCE-02",
    },
    {
        "name": "Lactato elevado com terapia de sepse — choque precoce",
        "category": "lactate",
        "threshold": "Lactato ≥ 2 + ATB prescrito + sem noradrenalina + sem VM 24h",
        "alert_id": "ALERT-HEMO-STABILITY-LACTATE-SEPSIS-08",
    },
    {
        "name": "Delta lactato > 0.5 mmol/L/h",
        "category": "lactate",
        "threshold": "Variação horária do lactato > 0.5 mmol/L/h",
        "alert_id": None,
    },
    {
        "name": "Lactato > 2 mmol/L após 6h de ressuscitação",
        "category": "lactate",
        "threshold": "Lactato > 2 mmol/L mantido após 6h de tratamento",
        "alert_id": None,
    },
    # ===== COMBINED (3 criteria) =====
    {
        "name": "Hipoperfusão global (≥ 2 domínios alterados)",
        "category": "combined",
        "threshold": "≥ 2 domínios (vasopressor, perfusão, débito, fluidos, lactato) alterados",
        "alert_id": None,
    },
    {
        "name": "Piora em ≥ 2 domínios nas últimas 6h",
        "category": "combined",
        "threshold": "≥ 2 domínios com piora nos critérios em 6h",
        "alert_id": None,
    },
    {
        "name": "Choque persistente (> 6h com critérios)",
        "category": "combined",
        "threshold": "Critérios de instabilidade mantidos por > 6h",
        "alert_id": None,
    },
]

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class StabilityCriterionResult:
    """Result of evaluating a single stability criterion."""

    name: str
    value: str
    threshold: str
    status: str  # normal, warning, critical
    category: str
    alert_id: str | None = None


@dataclass
class StabilityEvaluationResult:
    """Result of evaluating all 27 stability criteria for a patient."""

    mpi_id: str
    score: int = 0  # 0-27: number of criteria in warning/critical
    severity: str = "estavel"  # estavel, atencao, critico
    criteria: list[StabilityCriterionResult] = field(default_factory=list)
    recommendation: str = ""
    assessed_at: str = ""


# ---------------------------------------------------------------------------
# Per-criterion evaluation helpers (additional criteria beyond hemo alerts)
# ---------------------------------------------------------------------------


def _num(v: Any) -> float | None:
    """Safely convert a value to float."""
    if v is None:
        return None
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _eval_lactate_gt_2(inputs: dict[str, Any]) -> tuple[bool, str]:
    """Lactato > 2 mmol/L (isolated criterion)."""
    lac = _num(inputs.get("lactato_arterial"))
    if lac is None:
        return False, "sem dados"
    if lac > 2.0:
        return True, f"Lactato={lac:.1f} mmol/L (> 2.0)"
    return False, f"Lactato={lac:.1f} mmol/L (normal)"


def _eval_lactate_ge_4(inputs: dict[str, Any]) -> tuple[bool, str]:
    """Lactato >= 4 mmol/L (tissue shock marker)."""
    lac = _num(inputs.get("lactato_arterial"))
    if lac is None:
        return False, "sem dados"
    if lac >= 4.0:
        return True, f"Lactato={lac:.1f} mmol/L (>= 4.0 — choque tecidual)"
    return False, f"Lactato={lac:.1f} mmol/L (< 4.0)"


def _eval_svo2_low(inputs: dict[str, Any]) -> tuple[bool, str]:
    """SvO2 < 65%."""
    svo2 = _num(inputs.get("saturacao_venosa_mista"))
    if svo2 is None:
        svo2 = _num(inputs.get("svo2"))
    if svo2 is None:
        return False, "sem dados"
    if svo2 < 65.0:
        return True, f"SvO2={svo2:.0f}% (< 65%)"
    return False, f"SvO2={svo2:.0f}%"


def _eval_delta_pco2_high(inputs: dict[str, Any]) -> tuple[bool, str]:
    """Delta PCO2 (gap veno-arterial) > 6 mmHg."""
    gap = _num(inputs.get("delta_pco2"))
    if gap is None:
        gap = _num(inputs.get("gap_pco2_veno_arterial"))
    if gap is None:
        return False, "sem dados"
    if gap > 6.0:
        return True, f"Delta PCO2={gap:.1f} mmHg (> 6)"
    return False, f"Delta PCO2={gap:.1f} mmHg"


def _eval_ci_low(inputs: dict[str, Any]) -> tuple[bool, str]:
    """Índice cardíaco < 2.2 L/min/m²."""
    ci = _num(inputs.get("indice_cardiaco"))
    if ci is None:
        ci = _num(inputs.get("ic"))
    if ci is None:
        return False, "sem dados"
    if ci < 2.2:
        return True, f"IC={ci:.1f} L/min/m² (< 2.2)"
    return False, f"IC={ci:.1f} L/min/m²"


def _eval_fc_gt_130(inputs: dict[str, Any]) -> tuple[bool, str]:
    """FC > 130 bpm sustained."""
    fc = _num(inputs.get("frequencia_cardiaca"))
    if fc is None:
        return False, "sem dados"
    if fc > 130.0:
        return True, f"FC={fc:.0f} bpm (> 130)"
    return False, f"FC={fc:.0f} bpm"


def _eval_map_lt_65(inputs: dict[str, Any]) -> tuple[bool, str]:
    """PAM < 65 mmHg."""
    pam = _num(inputs.get("pressao_arterial_media"))
    if pam is None:
        return False, "sem dados"
    if pam < 65.0:
        return True, f"PAM={pam:.0f} mmHg (< 65)"
    return False, f"PAM={pam:.0f} mmHg"


def _eval_balanco_24h_gt_3000(inputs: dict[str, Any]) -> tuple[bool, str]:
    """Balanço hídrico 24h > 3000 mL positivo."""
    bal = _num(inputs.get("balanco_hidrico_24h"))
    if bal is None:
        return False, "sem dados"
    if bal > 3000.0:
        return True, f"Balanço 24h=+{bal:.0f} mL (> +3000)"
    return False, f"Balanço 24h=+{bal:.0f} mL"


def _eval_balanco_cumulativo_lt_neg2000(inputs: dict[str, Any]) -> tuple[bool, str]:
    """Balanço hídrico cumulativo < -2000 mL."""
    bal = _num(inputs.get("balanco_hidrico_cumulativo"))
    if bal is None:
        return False, "sem dados"
    if bal < -2000.0:
        return True, f"Balanço cumulativo={bal:.0f} mL (< -2000)"
    return False, f"Balanço cumulativo={bal:.0f} mL"


def _eval_ppv_ou_svv_alto(inputs: dict[str, Any]) -> tuple[bool, str]:
    """PPV > 13% or SVV > 13% with poor volume response."""
    ppv = _num(inputs.get("ppv"))
    svv = _num(inputs.get("svv"))
    delta_sv = _num(inputs.get("delta_sv_pos_fluid"))
    if ppv is None and svv is None:
        return False, "sem dados"

    ppv_high = ppv is not None and ppv > 13.0
    svv_high = svv is not None and svv > 13.0
    poor_response = delta_sv is not None and delta_sv < 10.0

    if (ppv_high or svv_high) and poor_response:
        val = f"PPV={ppv}%, SVV={svv}%" if ppv is not None else f"SVV={svv}%"
        return True, f"{val} + ΔSV={delta_sv}% (resposta pobre)"
    return False, f"PPV={ppv}%, SVV={svv}% (sem critério)"


def _eval_delta_lactate_gt_05(inputs: dict[str, Any]) -> tuple[bool, str]:
    """Delta lactate > 0.5 mmol/L/h."""
    lac = _num(inputs.get("lactato_arterial"))
    lac_prev = _num(inputs.get("lactato_arterial_anterior"))
    if lac is None or lac_prev is None:
        return False, "sem dados"
    delta_raw = lac - lac_prev
    delta_hours = _num(inputs.get("lactate_delta_hours"))
    if delta_hours is None or delta_hours <= 0:
        delta_hours = 6.0
    delta_per_hour = delta_raw / delta_hours
    if delta_per_hour > 0.5:
        return True, f"Δlactato={delta_per_hour:.2f} mmol/L/h (> 0.5)"
    return False, f"Δlactato={delta_per_hour:.2f} mmol/L/h"


def _eval_lactate_6h_gt_2(inputs: dict[str, Any]) -> tuple[bool, str]:
    """Lactate > 2 mmol/L after 6h of resuscitation."""
    lac_6h = _num(inputs.get("lactato_6h"))
    if lac_6h is None:
        return False, "sem dados"
    if lac_6h > 2.0:
        return True, f"Lactato 6h={lac_6h:.1f} mmol/L (> 2.0)"
    return False, f"Lactato 6h={lac_6h:.1f} mmol/L"


# Map additional criterion names → evaluation functions
_ADDITIONAL_EVALUATORS: dict[str, callable] = {
    "Lactato > 2 mmol/L (sem clearance)": _eval_lactate_gt_2,
    "Lactato ≥ 4 mmol/L (choque tecidual)": _eval_lactate_ge_4,
    "SvO2 < 65% (oferta/consumo O2)": _eval_svo2_low,
    "Delta PCO2 (gap) > 6 mmHg": _eval_delta_pco2_high,
    "Índice cardíaco < 2.2 L/min/m²": _eval_ci_low,
    "FC > 130 bpm sustentada": _eval_fc_gt_130,
    "PAM < 65 mmHg (hipotensão)": _eval_map_lt_65,
    "Balanço hídrico 24h > 3000 mL positivo": _eval_balanco_24h_gt_3000,
    "Balanço hídrico cumulativo < -2000 mL": _eval_balanco_cumulativo_lt_neg2000,
    "PPV > 13% ou SVV > 13% com resposta pobre a volume": _eval_ppv_ou_svv_alto,
    "Delta lactato > 0.5 mmol/L/h": _eval_delta_lactate_gt_05,
    "Lactato > 2 mmol/L após 6h de ressuscitação": _eval_lactate_6h_gt_2,
}


# ---------------------------------------------------------------------------
# Combined criteria evaluators (use cross-domain results)
# ---------------------------------------------------------------------------


def _eval_hipoperfusao_global(
    category_results: dict[str, list[StabilityCriterionResult]],
) -> tuple[bool, str]:
    """Hipoperfusão global: ≥ 2 domains with any warning/critical criterion."""
    domains_altered = 0
    altered_domains: list[str] = []
    for cat, crits in category_results.items():
        if any(c.status in ("warning", "critical") for c in crits):
            domains_altered += 1
            altered_domains.append(cat)
    if domains_altered >= 2:
        return True, f"≥ 2 domínios alterados: {', '.join(altered_domains)}"
    return False, f"{domains_altered} domínio(s) alterado(s)"


def _eval_piora_multidominio(
    inputs: dict[str, Any],
) -> tuple[bool, str]:
    """Piora em ≥ 2 domínios nas últimas 6h (uses historical comparison flags)."""
    piora_flags = [
        inputs.get("piora_vasopressor_6h", False),
        inputs.get("piora_perfusao_6h", False),
        inputs.get("piora_debito_6h", False),
        inputs.get("piora_fluidos_6h", False),
        inputs.get("piora_lactato_6h", False),
    ]
    count = sum(1 for f in piora_flags if f)
    if count >= 2:
        return True, f"Piora em {count} domínios nas últimas 6h"
    return False, f"Piora em {count} domínio(s) nas últimas 6h"


def _eval_choque_persistente(
    inputs: dict[str, Any],
) -> tuple[bool, str]:
    """Choque persistente: stability criteria sustained > 6h."""
    horas_instabilidade = _num(inputs.get("horas_instabilidade_hemodinamica"))
    if horas_instabilidade is None:
        horas_instabilidade = _num(inputs.get("duracao_choque_horas"))
    if horas_instabilidade is None:
        return False, "sem dados de duração"
    if horas_instabilidade > 6.0:
        return True, f"Instabilidade mantida por {horas_instabilidade:.0f}h (> 6h)"
    return False, f"Instabilidade por {horas_instabilidade:.0f}h"


# ---------------------------------------------------------------------------
# Severity & recommendation helpers
# ---------------------------------------------------------------------------


def _determine_severity(score: int) -> str:
    """Map score to severity band.
    0-3: estavel (stable)
    4-9: atencao (attention)
    10+: critico (critical)
    """
    if score >= 10:
        return "critico"
    if score >= 4:
        return "atencao"
    return "estavel"


def _build_stability_recommendation(
    score: int,
    severity: str,
    triggered_criteria: list[str],
) -> str:
    """Build PT-BR clinical recommendation based on score and severity."""
    if severity == "critico":
        return (
            f"CRÍTICO: {score}/27 critérios de instabilidade ativos. "
            "Avaliação médica IMEDIATA. Considerar escalonamento de cuidados, "
            "monitorização invasiva e ajuste de vasopressores/fluidoterapia. "
            f"Critérios disparados: {', '.join(triggered_criteria[:5])}"
            + ("..." if len(triggered_criteria) > 5 else "")
        )
    if severity == "atencao":
        return (
            f"ATENÇÃO: {score}/27 critérios de instabilidade ativos. "
            "Reavaliar em 1-2h. Verificar tendência de lactato, balanço hídrico "
            "e dose de vasopressor. Notificar plantonista se piora. "
            f"Principais critérios: {', '.join(triggered_criteria[:3])}"
        )
    return (
        f"ESTÁVEL: {score}/27 critérios de instabilidade. "
        "Manter monitorização de rotina. "
        "Reavaliar a cada 4-6h ou conforme protocolo institucional."
    )


# ---------------------------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------------------------


def evaluate_stability(
    mpi_id: str,
    clinical_data: dict[str, Any],
) -> StabilityEvaluationResult:
    """Evaluate all 27 stability criteria for a patient.

    Wraps domain_hemo.evaluate_all() for the 12 alert-backed criteria and
    adds 15 additional criteria evaluated directly from clinical_data.
    Three combined criteria use cross-domain aggregation.

    Args:
        mpi_id: Patient MPI identifier.
        clinical_data: Dict of clinical data (vitals, labs, flags).

    Returns:
        StabilityEvaluationResult with score, severity, and all 27 criteria.
    """
    now = datetime.now(timezone.utc).isoformat()

    # Step 1: Evaluate all 12 hemo alerts
    hemo_results: dict[str, HemoAlertResult] = evaluate_hemo_alerts(clinical_data)

    # Step 2: Build 27 criteria results
    criteria_results: list[StabilityCriterionResult] = []

    for crit_def in STABILITY_CRITERIA:
        name: str = crit_def["name"]  # type: ignore[assignment]
        category: str = crit_def["category"]  # type: ignore[assignment]
        threshold: str = crit_def["threshold"] or ""  # type: ignore[assignment]
        alert_id: str | None = crit_def.get("alert_id")

        status = "normal"
        value = ""

        if alert_id is not None and alert_id in hemo_results:
            # Criterion backed by a hemo alert
            hemo_result = hemo_results[alert_id]
            if hemo_result.fired:
                band = hemo_result.band or "watch"
                if band == "critical":
                    status = "critical"
                elif band in ("urgent", "watch"):
                    status = "warning"
                else:
                    status = "normal"
                # Build value string from alert metadata
                meta = hemo_result.metadata
                if meta:
                    value = ", ".join(f"{k}={v}" for k, v in list(meta.items())[:3])
                else:
                    value = "critério atingido"
            else:
                status = "normal"
                value = "critério não atingido"
        elif name in _ADDITIONAL_EVALUATORS:
            # Additional criterion evaluated directly
            eval_fn = _ADDITIONAL_EVALUATORS[name]
            try:
                fired, reason = eval_fn(clinical_data)
            except Exception as exc:
                logger.warning("Error evaluating criterion '%s': %s", name, exc)
                fired, reason = False, f"erro: {exc}"
            if fired:
                status = "warning"
                value = reason
            else:
                status = "normal"
                value = reason
        elif name == "Hipoperfusão global (≥ 2 domínios alterados)":
            # Combined: evaluated after building category breakdown
            # Placeholder — will be filled after initial criteria_results
            criteria_results.append(
                StabilityCriterionResult(
                    name=name,
                    value="pendente",
                    threshold=threshold,
                    status="normal",
                    category=category,
                    alert_id=alert_id,
                )
            )
            continue
        elif name == "Piora em ≥ 2 domínios nas últimas 6h":
            try:
                fired, reason = _eval_piora_multidominio(clinical_data)
            except Exception as exc:
                logger.warning("Error evaluating piora multidominio: %s", exc)
                fired, reason = False, f"erro: {exc}"
            status = "warning" if fired else "normal"
            value = reason
        elif name == "Choque persistente (> 6h com critérios)":
            try:
                fired, reason = _eval_choque_persistente(clinical_data)
            except Exception as exc:
                logger.warning("Error evaluating choque persistente: %s", exc)
                fired, reason = False, f"erro: {exc}"
            status = "warning" if fired else "normal"
            value = reason
        else:
            status = "normal"
            value = "sem avaliador definido"

        criteria_results.append(
            StabilityCriterionResult(
                name=name,
                value=value,
                threshold=threshold,
                status=status,
                category=category,
                alert_id=alert_id,
            )
        )

    # Step 3: Fill in the combined criteria
    # Build category_results dict
    category_results: dict[str, list[StabilityCriterionResult]] = {}
    for c in criteria_results:
        category_results.setdefault(c.category, []).append(c)

    # Evaluate hipoperfusão global
    hipo_fired, hipo_reason = _eval_hipoperfusao_global(category_results)
    for i, c in enumerate(criteria_results):
        if c.name == "Hipoperfusão global (≥ 2 domínios alterados)":
            criteria_results[i] = StabilityCriterionResult(
                name=c.name,
                value=hipo_reason,
                threshold=c.threshold,
                status="warning" if hipo_fired else "normal",
                category=c.category,
                alert_id=c.alert_id,
            )
            break

    # Step 4: Compute score, severity, and recommendation
    triggered = [c for c in criteria_results if c.status in ("warning", "critical")]
    score = len(triggered)
    severity = _determine_severity(score)
    triggered_names = [c.name for c in triggered]
    recommendation = _build_stability_recommendation(score, severity, triggered_names)

    return StabilityEvaluationResult(
        mpi_id=mpi_id,
        score=score,
        severity=severity,
        criteria=criteria_results,
        recommendation=recommendation,
        assessed_at=now,
    )


# ---------------------------------------------------------------------------
# Trend computation
# ---------------------------------------------------------------------------


def compute_stability_trend(
    mpi_id: str,
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compute 7-day stability trend from assessment history.

    Args:
        mpi_id: Patient MPI identifier.
        history: List of assessment dicts with 'score', 'severity', 'assessed_at'.

    Returns:
        Dict with trend data: direction, delta_7d, trend_points.
    """
    if not history:
        return {
            "mpi_id": mpi_id,
            "direction": "stable",
            "delta_7d": 0,
            "trend_points": [],
        }

    # Sort by assessed_at ascending
    sorted_history = sorted(history, key=lambda h: h.get("assessed_at", ""))

    # Extract trend points
    trend_points: list[dict] = []
    for h in sorted_history:
        assessed = h.get("assessed_at", "")
        if isinstance(assessed, str) and "T" in assessed:
            date_str = assessed[:10]  # YYYY-MM-DD
        elif hasattr(assessed, "strftime"):
            date_str = assessed.strftime("%Y-%m-%d")
        else:
            date_str = str(assessed)[:10]
        trend_points.append(
            {
                "date": date_str,
                "score": h.get("score", 0),
                "severity": h.get("severity", "estavel"),
                "criteria_triggered": h.get("score", 0),
            }
        )

    # Determine direction: compare first vs last
    first_score = sorted_history[0].get("score", 0)
    last_score = sorted_history[-1].get("score", 0)
    delta_7d = last_score - first_score

    if delta_7d > 1:
        direction = "worsening"
    elif delta_7d < -1:
        direction = "improving"
    else:
        direction = "stable"

    # Deduplicate trend points by date (keep latest per day)
    seen_dates: set[str] = set()
    deduped_points: list[dict] = []
    for tp in reversed(trend_points):
        if tp["date"] not in seen_dates:
            seen_dates.add(tp["date"])
            deduped_points.append(tp)
    deduped_points.reverse()

    return {
        "mpi_id": mpi_id,
        "direction": direction,
        "delta_7d": delta_7d,
        "trend_points": deduped_points,
    }


# ---------------------------------------------------------------------------
# Convenience: quick classification from score only
# ---------------------------------------------------------------------------


def classify_stability(score: int) -> dict[str, str]:
    """Quick severity classification from score without full evaluation.

    Args:
        score: Number of criteria triggered (0-27).

    Returns:
        Dict with 'severity' and 'recommendation' keys.
    """
    severity = _determine_severity(score)
    rec = _build_stability_recommendation(score, severity, [])
    return {"severity": severity, "recommendation": rec}
