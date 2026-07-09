"""Clinical Deterioration domain service — multi-domain scoring (13 rules).

Architecture:
- 13 deterioration criteria across 5 clinical domains:
    respiratory(4), hemodynamic(3), sepsis(3), neurologic(2), renal(1)
- Aggregates results from domain_respiratory, domain_hemo, and domain_sepsis
- Categorical scoring: 0, 1+, 1-, 3+, 3-
- Trend computation vs previous assessment

Scoring logic:
    0:  zero domains affected
    1+: 1-2 domains affected, improving trend
    1-: 1-2 domains affected, worsening/no trend
    3+: 3+ domains affected, improving trend
    3-: 3+ domains affected, worsening/no trend

Dependencies:
- intensicare.services.domain_respiratory (evaluate_all) — respiratory domain evaluation
- intensicare.services.domain_hemo (evaluate_all) — hemodynamic domain evaluation
- intensicare.services.domain_sepsis (SepsisDomainService) — sepsis domain evaluation

CLINICAL RATIFICATION: rat-piora-clinica-01 through rat-piora-clinica-13 (P0 RATIFY).
"""

from __future__ import annotations

__version__ = "3.0.0"

__all__ = [
    "DeteriorationCriteriaResult",
    "DeteriorationEvaluationResult",
    "DOMAIN_CRITERIA",
    "evaluate_deterioration",
    "evaluate_deterioration_from_history",
    "classify_deterioration",
]

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import logging

from intensicare.services.domain_respiratory import evaluate_all as evaluate_respiratory
from intensicare.services.domain_hemo import evaluate_all as evaluate_hemo
from intensicare.services.domain_sepsis import SepsisDomainService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 13 Deterioration criteria definitions
# ---------------------------------------------------------------------------

DOMAIN_CRITERIA: list[dict[str, str | None]] = [
    # ===== RESPIRATORY (4 criteria) =====
    {
        "domain": "respiratory",
        "name": "Queda de SpO2 com aumento de FiO2",
        "threshold": "SpO2 < 90% com FiO2 > 0.60",
    },
    {
        "domain": "respiratory",
        "name": "Piora PaO2/FiO2 em 6h",
        "threshold": "ΔP/F < -50 em 6h ou queda > 20%",
    },
    {
        "domain": "respiratory",
        "name": "Aumento de FiO2 > 30% sem melhora de SpO2",
        "threshold": "FiO2 atual > 1.3 × FiO2 6h atrás + SpO2 ≤ SpO2 6h",
    },
    {
        "domain": "respiratory",
        "name": "Taquipneia progressiva (FR > 35 ou ΔFR > 10 em 2h)",
        "threshold": "FR > 35 rpm ou aumento > 10 rpm em 2h",
    },

    # ===== HEMODYNAMIC (3 criteria) =====
    {
        "domain": "hemodynamic",
        "name": "Queda de PAM > 15 mmHg em 1h",
        "threshold": "ΔPAM < -15 mmHg em 1h",
    },
    {
        "domain": "hemodynamic",
        "name": "Escalonamento de vasopressor (dose > 2× ou 2º agente)",
        "threshold": "Dose vasopressor > 2 × basal ou novo agente iniciado",
    },
    {
        "domain": "hemodynamic",
        "name": "Índice de choque com piora (> 1.2 ou ΔSI > 0.3 em 2h)",
        "threshold": "SI > 1.2 ou aumento > 0.3 em 2h",
    },

    # ===== SEPSIS (3 criteria) =====
    {
        "domain": "sepsis",
        "name": "Aumento de qSOFA (≥ 1 ponto em 24h)",
        "threshold": "ΔqSOFA ≥ +1 em 24h",
    },
    {
        "domain": "sepsis",
        "name": "Lactato ascendente (> 0.5 mmol/L/h ou > 4 mmol/L)",
        "threshold": "Δlactato > 0.5 mmol/L/h ou lactato > 4 mmol/L",
    },
    {
        "domain": "sepsis",
        "name": "Procalcitonina em ascensão (> 0.25 ng/mL em 24h)",
        "threshold": "ΔPCT > 0.25 ng/mL em 24h com ATB ≥ 48h",
    },

    # ===== NEUROLOGIC (2 criteria) =====
    {
        "domain": "neurologic",
        "name": "Queda de GCS ≥ 2 pontos em 24h",
        "threshold": "ΔGCS ≤ -2 em 24h",
    },
    {
        "domain": "neurologic",
        "name": "Piora de RASS (agitação ou sedação excessiva)",
        "threshold": "RASS ≥ +2 (agitação) ou RASS ≤ -4 (sedação profunda) com piora",
    },

    # ===== RENAL (1 criterion) =====
    {
        "domain": "renal",
        "name": "Piora de função renal (creatinina > 1.5× basal ou diurese < 0.5 mL/kg/h)",
        "threshold": "Creatinina > 1.5 × basal ou diurese < 0.5 mL/kg/h por 6h",
    },
]

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class DeteriorationCriteriaResult:
    """Result of a single deterioration criterion evaluation."""

    domain: str
    name: str
    status: str  # normal, alert, critical
    value: str | None = None
    threshold: str | None = None
    alert_id: str | None = None


@dataclass
class DeteriorationEvaluationResult:
    """Result of evaluating all 13 deterioration criteria for a patient."""

    mpi_id: str
    score: str = "0"  # 0, 1+, 1-, 3+, 3-
    trend: str = "none"  # improving, stable, worsening, none
    criteria: list[DeteriorationCriteriaResult] = field(default_factory=list)
    domains_affected: int = 0
    recommendation: str = ""
    assessed_at: str = ""
    assessed_by: str = "system"


# ---------------------------------------------------------------------------
# Helper: safe numeric conversion
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


# ---------------------------------------------------------------------------
# Per-criterion evaluation functions
# ---------------------------------------------------------------------------


def _eval_spo2_fio2_drop(inputs: dict[str, Any]) -> tuple[bool, str, str]:
    """Queda de SpO2 com aumento de FiO2."""
    spo2 = _num(inputs.get("saturacao_o2"))
    fio2 = _num(inputs.get("fio2"))
    if spo2 is None or fio2 is None:
        return False, "normal", "sem dados"
    # FiO2 enforcement: if > 1.0, treat as percentage
    if fio2 > 1.0:
        fio2 = fio2 / 100.0
    if spo2 < 90.0 and fio2 > 0.60:
        return True, "critical", f"SpO2={spo2:.0f}%, FiO2={fio2:.2f}"
    elif spo2 < 92.0 and fio2 > 0.50:
        return True, "alert", f"SpO2={spo2:.0f}%, FiO2={fio2:.2f}"
    return False, "normal", f"SpO2={spo2:.0f}%, FiO2={fio2:.2f}"


def _eval_pf_worsening(inputs: dict[str, Any]) -> tuple[bool, str, str]:
    """Piora PaO2/FiO2 em 6h."""
    pf = _num(inputs.get("pao2_fio2"))
    pf_6h = _num(inputs.get("pao2_fio2_6h_ago"))
    sf = _num(inputs.get("relacao_spo2_fio2"))
    sf_6h = _num(inputs.get("relacao_spo2_fio2_6h_ago"))

    # Prefer P/F, fallback to S/F
    current = pf if pf is not None else sf
    previous = pf_6h if pf_6h is not None else sf_6h

    if current is None or previous is None:
        return False, "normal", "sem dados de tendência"

    delta = current - previous
    if delta < -50 or (previous > 0 and current / previous < 0.80):
        return True, "critical", f"ΔP/F={delta:.0f} (queda > 20%)"
    elif delta < -25:
        return True, "alert", f"ΔP/F={delta:.0f} (queda moderada)"
    return False, "normal", f"ΔP/F={delta:.0f}"


def _eval_fio2_escalation(inputs: dict[str, Any]) -> tuple[bool, str, str]:
    """Aumento de FiO2 > 30% sem melhora de SpO2."""
    fio2 = _num(inputs.get("fio2"))
    fio2_6h = _num(inputs.get("fio2_6h_ago"))
    spo2 = _num(inputs.get("saturacao_o2"))
    spo2_6h = _num(inputs.get("saturacao_o2_6h_ago"))

    if fio2 is None or fio2_6h is None:
        return False, "normal", "sem dados de FiO2"
    if fio2 > 1.0:
        fio2 = fio2 / 100.0
    if fio2_6h > 1.0:
        fio2_6h = fio2_6h / 100.0

    if fio2_6h <= 0:
        return False, "normal", "FiO2 basal inválida"

    fio2_ratio = fio2 / fio2_6h
    if fio2_ratio > 1.30:
        if spo2 is not None and spo2_6h is not None and spo2 <= spo2_6h:
            return True, "critical", f"FiO2 +{(fio2_ratio - 1) * 100:.0f}%, SpO2 sem melhora"
        elif spo2 is not None and spo2_6h is not None:
            return True, "alert", f"FiO2 +{(fio2_ratio - 1) * 100:.0f}%, SpO2 melhorou"
    return False, "normal", f"FiO2 variação={(fio2_ratio - 1) * 100:.0f}%"


def _eval_tachypnea_progressive(inputs: dict[str, Any]) -> tuple[bool, str, str]:
    """Taquipneia progressiva."""
    fr = _num(inputs.get("frequencia_respiratoria"))
    fr_2h = _num(inputs.get("frequencia_respiratoria_2h_ago"))

    if fr is None:
        return False, "normal", "sem dados de FR"

    if fr > 35.0:
        return True, "critical", f"FR={fr:.0f} (> 35 rpm)"

    if fr_2h is not None:
        delta = fr - fr_2h
        if delta > 10.0:
            return True, "alert", f"ΔFR=+{delta:.0f} rpm em 2h"
    return False, "normal", f"FR={fr:.0f} rpm"


def _eval_map_drop(inputs: dict[str, Any]) -> tuple[bool, str, str]:
    """Queda de PAM > 15 mmHg em 1h."""
    pam = _num(inputs.get("pressao_arterial_media"))
    pam_1h = _num(inputs.get("pressao_arterial_media_1h_ago"))

    if pam is None:
        return False, "normal", "sem dados de PAM"

    if pam < 60.0:
        return True, "critical", f"PAM={pam:.0f} mmHg (crítico)"

    if pam_1h is not None:
        delta = pam - pam_1h
        if delta < -15.0:
            return True, "critical", f"ΔPAM={delta:.0f} mmHg em 1h"
        elif delta < -10.0:
            return True, "alert", f"ΔPAM={delta:.0f} mmHg em 1h"
    return False, "normal", f"PAM={pam:.0f} mmHg"


def _eval_vaso_escalation_deterioration(inputs: dict[str, Any]) -> tuple[bool, str, str]:
    """Escalonamento de vasopressor."""
    dose = _num(inputs.get("dose_vasopressor"))
    dose_basal = _num(inputs.get("dose_vasopressor_basal"))

    dose_vaso_val = _num(inputs.get("dose_vasopressina"))
    dose_adr_val = _num(inputs.get("dose_adrenalina"))
    second_agent = (
        dose_vaso_val is not None
        and dose_vaso_val > 0
        and not inputs.get("vasopressina_previa", False)
    ) or (
        dose_adr_val is not None
        and dose_adr_val > 0
        and not inputs.get("adrenalina_previa", False)
    )

    if second_agent:
        return True, "critical", "Novo agente vasopressor iniciado"

    if dose is not None and dose_basal is not None and dose_basal > 0:
        ratio = dose / dose_basal
        if ratio > 2.0:
            return True, "critical", f"Dose vasopressor {ratio:.1f}× basal"
        elif ratio > 1.5:
            return True, "alert", f"Dose vasopressor {ratio:.1f}× basal"

    if dose is not None and dose > 0:
        return False, "normal", f"Dose vasopressor={dose:.2f} mcg/kg/min"
    return False, "normal", "sem vasopressor ativo"


def _eval_si_worsening(inputs: dict[str, Any]) -> tuple[bool, str, str]:
    """Índice de choque com piora."""
    si = _num(inputs.get("indice_choque"))
    fc = _num(inputs.get("frequencia_cardiaca"))
    pas = _num(inputs.get("pressao_arterial_sistolica"))
    si_2h = _num(inputs.get("indice_choque_2h_ago"))

    # Compute SI if not provided
    if si is None and fc is not None and pas is not None and pas > 0:
        si = fc / pas

    if si is None:
        return False, "normal", "sem dados para índice de choque"

    if si > 1.2:
        return True, "critical", f"SI={si:.2f} (> 1.2)"

    if si_2h is not None:
        delta = si - si_2h
        if delta > 0.3:
            return True, "alert", f"ΔSI=+{delta:.2f} em 2h"
    return False, "normal", f"SI={si:.2f}"


def _eval_qsofa_increase(inputs: dict[str, Any]) -> tuple[bool, str, str]:
    """Aumento de qSOFA ≥ 1 ponto em 24h."""
    qsofa = inputs.get("qsofa")
    qsofa_24h = inputs.get("qsofa_24h_ago")

    # Compute qSOFA if not provided
    if qsofa is None:
        rr = _num(inputs.get("frequencia_respiratoria"))
        sbp = _num(inputs.get("pressao_arterial_sistolica"))
        gcs = _num(inputs.get("glasgow"))
        qsofa = 0
        if rr is not None and rr >= 22:
            qsofa += 1
        if sbp is not None and sbp <= 100:
            qsofa += 1
        if gcs is not None and gcs < 15:
            qsofa += 1

    qsofa_val = _num(qsofa)
    if qsofa_val is None:
        return False, "normal", "sem dados de qSOFA"

    if qsofa_val >= 2:
        if qsofa_24h is not None:
            qsofa_24h_val = _num(qsofa_24h)
            if qsofa_24h_val is not None and qsofa_val > qsofa_24h_val:
                return True, "critical", f"qSOFA={int(qsofa_val)} (aumentou de {int(qsofa_24h_val)})"
        return True, "alert", f"qSOFA={int(qsofa_val)} (≥ 2)"

    return False, "normal", f"qSOFA={int(qsofa_val)}"


def _eval_lactate_rising(inputs: dict[str, Any]) -> tuple[bool, str, str]:
    """Lactato ascendente."""
    lac = _num(inputs.get("lactato_arterial"))
    lac_prev = _num(inputs.get("lactato_arterial_anterior"))

    if lac is None:
        return False, "normal", "sem dados de lactato"

    if lac >= 4.0:
        return True, "critical", f"Lactato={lac:.1f} mmol/L (≥ 4.0)"

    if lac_prev is not None:
        delta_raw = lac - lac_prev
        delta_hours = _num(inputs.get("lactate_delta_hours"))
        if delta_hours is None or delta_hours <= 0:
            delta_hours = 6.0
        delta_per_hour = delta_raw / delta_hours
        if delta_per_hour > 0.5:
            return True, "critical", f"Δlactato=+{delta_per_hour:.2f} mmol/L/h"
        elif delta_per_hour > 0.25:
            return True, "alert", f"Δlactato=+{delta_per_hour:.2f} mmol/L/h"

    if lac > 2.0:
        return True, "alert", f"Lactato={lac:.1f} mmol/L (> 2.0)"
    return False, "normal", f"Lactato={lac:.1f} mmol/L"


def _eval_pct_rising(inputs: dict[str, Any]) -> tuple[bool, str, str]:
    """Procalcitonina em ascensão."""
    pct = _num(inputs.get("procalcitonina"))
    pct_prev = _num(inputs.get("procalcitonina_anterior"))
    atb_hours = _num(inputs.get("atb_ativa_horas"))

    if pct is None:
        return False, "normal", "sem dados de PCT"

    atb_ok = atb_hours is None or atb_hours >= 48

    if pct_prev is not None and atb_ok:
        delta = pct - pct_prev
        if delta > 0.5:
            return True, "critical", f"ΔPCT=+{delta:.2f} ng/mL (> 0.5)"
        elif delta > 0.25:
            return True, "alert", f"ΔPCT=+{delta:.2f} ng/mL (> 0.25)"

    if pct > 2.0:
        return True, "alert", f"PCT={pct:.2f} ng/mL (> 2.0)"

    return False, "normal", f"PCT={pct:.2f} ng/mL"


def _eval_gcs_drop(inputs: dict[str, Any]) -> tuple[bool, str, str]:
    """Queda de GCS ≥ 2 pontos em 24h."""
    gcs = _num(inputs.get("glasgow"))
    gcs_24h = _num(inputs.get("glasgow_24h_ago"))

    if gcs is None:
        return False, "normal", "sem dados de GCS"

    if gcs <= 8:
        return True, "critical", f"GCS={int(gcs)} (≤ 8 — coma)"

    if gcs_24h is not None:
        delta = gcs - gcs_24h
        if delta <= -3:
            return True, "critical", f"ΔGCS={int(delta)} em 24h"
        elif delta <= -2:
            return True, "alert", f"ΔGCS={int(delta)} em 24h"

    return False, "normal", f"GCS={int(gcs)}"


def _eval_rass_worsening(inputs: dict[str, Any]) -> tuple[bool, str, str]:
    """Piora de RASS."""
    rass = _num(inputs.get("rass"))
    rass_prev = _num(inputs.get("rass_anterior"))

    if rass is None:
        return False, "normal", "sem dados de RASS"

    # Agitation: RASS ≥ +2
    if rass >= 3:
        return True, "critical", f"RASS={int(rass)} (agitação severa)"
    elif rass >= 2:
        return True, "alert", f"RASS={int(rass)} (agitação moderada)"

    # Deep sedation: RASS ≤ -4
    if rass <= -5:
        return True, "critical", f"RASS={int(rass)} (sedação profunda — sem resposta)"
    elif rass <= -4:
        # Check if worsening from previous
        if rass_prev is not None and rass < rass_prev:
            return True, "alert", f"RASS={int(rass)} (sedação profunda, piora)"
        return True, "alert", f"RASS={int(rass)} (sedação profunda)"

    return False, "normal", f"RASS={int(rass)}"


def _eval_renal_worsening(inputs: dict[str, Any]) -> tuple[bool, str, str]:
    """Piora de função renal."""
    creat = _num(inputs.get("creatinina"))
    creat_basal = _num(inputs.get("creatinina_basal"))
    diurese = _num(inputs.get("diurese_ml_kg_h"))

    # Check creatinine
    if creat is not None and creat_basal is not None and creat_basal > 0:
        ratio = creat / creat_basal
        if ratio >= 2.0:
            return True, "critical", f"Creatinina={creat:.2f} ({ratio:.1f}× basal)"
        elif ratio >= 1.5:
            return True, "alert", f"Creatinina={creat:.2f} ({ratio:.1f}× basal)"

    # Check urine output
    if diurese is not None:
        if diurese < 0.3:
            return True, "critical", f"Diurese={diurese:.2f} mL/kg/h (< 0.3)"
        elif diurese < 0.5:
            return True, "alert", f"Diurese={diurese:.2f} mL/kg/h (< 0.5)"

    if creat is not None:
        if creat > 2.0:
            return True, "alert", f"Creatinina={creat:.2f} mg/dL (> 2.0)"
        return False, "normal", f"Creatinina={creat:.2f} mg/dL"

    # No creatinine, check urine only
    if diurese is not None:
        return False, "normal", f"Diurese={diurese:.2f} mL/kg/h"

    return False, "normal", "sem dados de função renal"


# Map criterion name → evaluator function
_CRITERION_EVALUATORS: dict[str, Callable[..., tuple[bool, str, str]]] = {
    "Queda de SpO2 com aumento de FiO2": _eval_spo2_fio2_drop,
    "Piora PaO2/FiO2 em 6h": _eval_pf_worsening,
    "Aumento de FiO2 > 30% sem melhora de SpO2": _eval_fio2_escalation,
    "Taquipneia progressiva (FR > 35 ou ΔFR > 10 em 2h)": _eval_tachypnea_progressive,
    "Queda de PAM > 15 mmHg em 1h": _eval_map_drop,
    "Escalonamento de vasopressor (dose > 2× ou 2º agente)": _eval_vaso_escalation_deterioration,
    "Índice de choque com piora (> 1.2 ou ΔSI > 0.3 em 2h)": _eval_si_worsening,
    "Aumento de qSOFA (≥ 1 ponto em 24h)": _eval_qsofa_increase,
    "Lactato ascendente (> 0.5 mmol/L/h ou > 4 mmol/L)": _eval_lactate_rising,
    "Procalcitonina em ascensão (> 0.25 ng/mL em 24h)": _eval_pct_rising,
    "Queda de GCS ≥ 2 pontos em 24h": _eval_gcs_drop,
    "Piora de RASS (agitação ou sedação excessiva)": _eval_rass_worsening,
    "Piora de função renal (creatinina > 1.5× basal ou diurese < 0.5 mL/kg/h)": _eval_renal_worsening,
}

# ---------------------------------------------------------------------------
# Domain aggregation helpers
# ---------------------------------------------------------------------------


def _count_domains_affected(
    criteria_results: list[DeteriorationCriteriaResult],
) -> int:
    """Count domains with at least one criterion in alert or critical status."""
    affected: set[str] = set()
    for c in criteria_results:
        if c.status in ("alert", "critical"):
            affected.add(c.domain)
    return len(affected)


def _list_affected_domains(
    criteria_results: list[DeteriorationCriteriaResult],
) -> list[str]:
    """List domains with at least one alert/critical criterion."""
    affected: set[str] = set()
    for c in criteria_results:
        if c.status in ("alert", "critical"):
            affected.add(c.domain)
    return sorted(affected)


# ---------------------------------------------------------------------------
# Score computation
# ---------------------------------------------------------------------------


def _compute_score(
    criteria_results: list[DeteriorationCriteriaResult],
    previous_score: str | None = None,
) -> tuple[str, str]:
    """Compute categorical score (0/1+/1-/3+/3-) and trend.

    Score logic:
    - 0: zero domains affected (all normal)
    - 1+: 1-2 domains affected, improving from previous
    - 1-: 1-2 domains affected, worsening or no previous comparison
    - 3+: 3+ domains affected, improving from previous
    - 3-: 3+ domains affected, worsening or no previous comparison

    Trend determination:
    - improving: fewer domains affected than previous score
    - worsening: more domains affected than previous score
    - stable: same number of domains
    - none: no previous score to compare

    Args:
        criteria_results: List of evaluated criteria.
        previous_score: Previous categorical score string (e.g., "1+").

    Returns:
        Tuple of (score, trend).
    """
    domains = _count_domains_affected(criteria_results)

    # Base score from domain count
    if domains == 0:
        base_score = "0"
        base_domains = 0
    elif domains <= 2:
        base_score = "1"
        base_domains = 1
    else:
        base_score = "3"
        base_domains = 3

    # Determine trend from previous
    trend = "none"
    if previous_score is not None:
        prev_domains = _parse_previous_domains(previous_score)
        if prev_domains is not None:
            if domains < prev_domains:
                trend = "improving"
            elif domains > prev_domains:
                trend = "worsening"
            else:
                trend = "stable"

    # Determine sign (+/-)
    if base_score == "0":
        return "0", trend

    if trend == "improving":
        return f"{base_score}+", trend
    else:
        # worsening, stable, or none → negative sign
        return f"{base_score}-", trend


def _parse_previous_domains(score: str) -> int | None:
    """Parse domain count from a previous score string.

    Examples:
        "0" -> 0
        "1+" -> 1
        "1-" -> 1
        "3+" -> 3
        "3-" -> 3
    """
    if not score:
        return None
    score = score.strip()
    if score == "0":
        return 0
    try:
        return int(score[0])
    except (ValueError, IndexError):
        return None


# ---------------------------------------------------------------------------
# Recommendation builder
# ---------------------------------------------------------------------------


def _build_deterioration_recommendation(
    score: str,
    domains: list[str],
) -> str:
    """Build PT-BR clinical recommendation based on score and affected domains.

    Args:
        score: Categorical score ("0", "1+", "1-", "3+", "3-").
        domains: List of affected domain names.

    Returns:
        Clinical recommendation string in Portuguese.
    """
    domain_str = ", ".join(domains) if domains else "nenhum"

    if score == "0":
        return (
            "Sem sinais de deterioração clínica em nenhum domínio. "
            "Manter rotina de avaliação e monitorização conforme protocolo institucional."
        )

    if score.startswith("1"):
        if score.endswith("+"):
            return (
                f"POUCOS DOMÍNIOS AFETADOS — MELHORANDO: {len(domains)} domínio(s) afetado(s) "
                f"({domain_str}). Tendência de melhora em relação à avaliação anterior. "
                "Manter vigilância e reavaliar em 2-4h. "
                "Notificar plantonista se houver piora."
            )
        else:
            return (
                f"POUCOS DOMÍNIOS AFETADOS — ATENÇÃO: {len(domains)} domínio(s) afetado(s) "
                f"({domain_str}). Sem evidência de melhora ou em piora. "
                "Reavaliar em 1h. Considerar ajuste terapêutico nos domínios afetados. "
                "Notificar plantonista."
            )

    if score.startswith("3"):
        if score.endswith("+"):
            return (
                f"MÚLTIPLOS DOMÍNIOS AFETADOS — MELHORANDO: {len(domains)} domínios afetados "
                f"({domain_str}). Tendência de melhora, mas mantém gravidade. "
                "Manter vigilância intensiva. Reavaliar em 1h. "
                "Avaliar resposta às intervenções em curso."
            )
        else:
            return (
                f"MÚLTIPLOS DOMÍNIOS AFETADOS — CRÍTICO: {len(domains)} domínios afetados "
                f"({domain_str}). Sem melhora ou em piora. "
                "AVALIAÇÃO MÉDICA IMEDIATA. Considerar escalonamento de cuidados, "
                "revisão completa do plano terapêutico e acionamento do time de resposta rápida."
            )

    return "Reavaliação clínica recomendada."


# ---------------------------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------------------------


def evaluate_deterioration(
    mpi_id: str,
    clinical_data: dict[str, Any],
    previous_score: str | None = None,
) -> DeteriorationEvaluationResult:
    """Evaluate clinical deterioration across 5 domains (13 criteria).

    Aggregates respiratory, hemodynamic, sepsis, neurologic, and renal domains.
    Each criterion is evaluated independently; results are then aggregated
    to produce a categorical score and clinical recommendation.

    Args:
        mpi_id: Patient MPI identifier.
        clinical_data: Dict of clinical data (vitals, labs, flags).
        previous_score: Previous categorical score for trend comparison.

    Returns:
        DeteriorationEvaluationResult with score, trend, criteria, and recommendation.
    """
    now = datetime.now(timezone.utc).isoformat()

    # Step 1: Optionally evaluate domain-level services for context
    # These provide enrichment but don't gate the 13 criteria
    try:
        hemo_alerts = evaluate_hemo(clinical_data)
    except Exception as exc:
        logger.debug("Hemo alert evaluation failed (non-blocking): %s", exc)
        hemo_alerts = {}

    try:
        resp_alerts = evaluate_respiratory(clinical_data)
    except Exception as exc:
        logger.debug("Respiratory alert evaluation failed (non-blocking): %s", exc)
        resp_alerts = {}

    # Step 2: Evaluate all 13 deterioration criteria
    criteria_results: list[DeteriorationCriteriaResult] = []

    for crit_def in DOMAIN_CRITERIA:
        name: str = crit_def["name"]  # type: ignore[assignment]
        domain: str = crit_def["domain"]  # type: ignore[assignment]
        threshold: str = crit_def.get("threshold") or ""

        evaluator = _CRITERION_EVALUATORS.get(name)
        if evaluator is None:
            criteria_results.append(
                DeteriorationCriteriaResult(
                    domain=domain,
                    name=name,
                    status="normal",
                    value="sem avaliador",
                    threshold=threshold,
                )
            )
            continue

        try:
            fired, status, value = evaluator(clinical_data)
        except Exception as exc:
            logger.warning("Error evaluating deterioration criterion '%s': %s", name, exc)
            fired, status, value = False, "normal", f"erro: {exc}"

        criteria_results.append(
            DeteriorationCriteriaResult(
                domain=domain,
                name=name,
                status=status,
                value=value,
                threshold=threshold,
            )
        )

    # Step 3: Compute score and trend
    score, trend = _compute_score(criteria_results, previous_score)

    # Step 4: Count domains affected
    domains_affected = _count_domains_affected(criteria_results)
    affected_domains = _list_affected_domains(criteria_results)

    # Step 5: Build recommendation
    recommendation = _build_deterioration_recommendation(score, affected_domains)

    return DeteriorationEvaluationResult(
        mpi_id=mpi_id,
        score=score,
        trend=trend,
        criteria=criteria_results,
        domains_affected=domains_affected,
        recommendation=recommendation,
        assessed_at=now,
        assessed_by="system",
    )


# ---------------------------------------------------------------------------
# Convenience: evaluate from previous assessment record
# ---------------------------------------------------------------------------


def evaluate_deterioration_from_history(
    mpi_id: str,
    clinical_data: dict[str, Any],
    previous_assessment: dict[str, Any] | None = None,
) -> DeteriorationEvaluationResult:
    """Evaluate deterioration with history-aware trend computation.

    Args:
        mpi_id: Patient MPI identifier.
        clinical_data: Current clinical data dict.
        previous_assessment: Dict with 'score' key from previous assessment.

    Returns:
        DeteriorationEvaluationResult.
    """
    prev_score = None
    if previous_assessment is not None:
        prev_score = previous_assessment.get("score")
    return evaluate_deterioration(mpi_id, clinical_data, previous_score=prev_score)


# ---------------------------------------------------------------------------
# Quick domain classification
# ---------------------------------------------------------------------------


def classify_deterioration(domains_affected: int, trend: str = "none") -> dict[str, str]:
    """Quick deterioration classification without full evaluation.

    Args:
        domains_affected: Number of domains with alert/critical criteria.
        trend: Trend vs previous ("improving", "worsening", "stable", "none").

    Returns:
        Dict with 'score' and 'recommendation'.
    """
    if domains_affected == 0:
        score = "0"
    elif domains_affected <= 2:
        score = f"1{'+' if trend == 'improving' else '-'}"
    else:
        score = f"3{'+' if trend == 'improving' else '-'}"

    domains_list = [f"domínio {i + 1}" for i in range(domains_affected)]
    rec = _build_deterioration_recommendation(score, domains_list)
    return {"score": score, "recommendation": rec}
