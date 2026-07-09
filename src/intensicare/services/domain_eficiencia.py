"""Efficiency & Stewardship domain — 12 transfusion-appropriateness criteria
plus mechanical restraint, frailty scoring, and ICU LOS benchmarking.

4 groups of 12 criteria (aligned with OpenAPI contract eficiencia-openapi.yaml
and frontend-v2/lib/efficiency-types.ts):

  Transfusion appropriateness (TF-001..TF-012):
    - Hb threshold (TF-001, TF-002, TF-005)
    - Symptomatic anemia / active bleeding (TF-003, TF-004, TF-007)
    - Massive transfusion protocol (TF-006, TF-012)
    - Documentation / consent / compatibility (TF-008, TF-009, TF-010, TF-011)

  Mechanical restraint (2 criteria):
    - Duration > 4h
    - Daily reassessment

  Frailty scoring (Clinical Frailty Scale 1–9)

  ICU LOS benchmarking (expected vs actual, outlier detection)
"""

from __future__ import annotations

__version__ = "3.0.0"

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ============================================================================
# Enums (aligned with OpenAPI)
# ============================================================================


class RestraintStatus(str, Enum):
    """Current mechanical-restraint monitoring status."""

    NONE = "none"
    PLANNED = "planned"
    ACTIVE = "active"
    WEANING = "weaning"
    REMOVED = "removed"
    CONTRAINDICATED = "contraindicated"


class FrailtyScale(str, Enum):
    """Validated frailty instruments supported."""

    CFS = "CFS"
    MFI = "mFI"
    FRAIL = "FRAIL"


# ============================================================================
# 12 Transfusion Appropriateness Criteria catalog
# ============================================================================

TRANSFUSION_CRITERIA: list[dict[str, str]] = [
    {
        "code": "TF-001",
        "description": "Hb pré-transfusional documentada",
        "category": "hb_threshold",
        "detail": "Hemoglobina deve ser registrada antes de cada transfusão",
    },
    {
        "code": "TF-002",
        "description": "Hb ≥ 7 g/dL (gatilho restritivo)",
        "category": "hb_threshold",
        "detail": "Transfusão com Hb ≥ 7 g/dL requer justificativa clínica",
    },
    {
        "code": "TF-003",
        "description": "Transfusão em 1 unidade (single-unit)",
        "category": "symptomatic_anemia",
        "detail": "Estratégia single-unit reduz exposição e eventos adversos",
    },
    {
        "code": "TF-004",
        "description": "Reavaliação clínica pós-transfusional",
        "category": "symptomatic_anemia",
        "detail": "Registro de evolução clínica pós-transfusão em até 6h",
    },
    {
        "code": "TF-005",
        "description": "Hb pós-transfusional documentada",
        "category": "hb_threshold",
        "detail": "Controle laboratorial pós-transfusional em até 24h",
    },
    {
        "code": "TF-006",
        "description": "Ausência de reação transfusional",
        "category": "massive_transfusion",
        "detail": "Monitorização de sinais vitais durante e após transfusão",
    },
    {
        "code": "TF-007",
        "description": "Indicação clínica documentada",
        "category": "symptomatic_anemia",
        "detail": "Registro do motivo clínico da transfusão no prontuário",
    },
    {
        "code": "TF-008",
        "description": "Termo de consentimento assinado",
        "category": "documentation",
        "detail": "Consentimento informado documentado para transfusão",
    },
    {
        "code": "TF-009",
        "description": "Identificação correta do paciente",
        "category": "documentation",
        "detail": "Dupla checagem de identificação antes da administração",
    },
    {
        "code": "TF-010",
        "description": "Compatibilidade ABO/Rh confirmada",
        "category": "compatibility",
        "detail": "Prova cruzada ou confirmação de compatibilidade registrada",
    },
    {
        "code": "TF-011",
        "description": "Temperatura de armazenamento adequada",
        "category": "compatibility",
        "detail": "Registro da cadeia de frio até o momento da administração",
    },
    {
        "code": "TF-012",
        "description": "Tempo de infusão ≤ 4 horas",
        "category": "massive_transfusion",
        "detail": "Cada unidade deve ser infundida em até 4 horas",
    },
]


CATEGORY_LABELS: dict[str, str] = {
    "hb_threshold": "Limiar de Hb",
    "symptomatic_anemia": "Anemia Sintomática / Sangramento",
    "massive_transfusion": "Protocolo Transfusional",
    "documentation": "Documentação / Consentimento",
    "compatibility": "Compatibilidade / Segurança",
}


# ============================================================================
# Domain model (dataclass per task specification)
# ============================================================================


@dataclass
class TransfusionCriterionResult:
    """Result of a single transfusion-appropriateness criterion evaluation."""

    code: str
    description: str
    met: bool
    detail: str | None = None


@dataclass
class EfficiencyAssessment:
    """Full resource-efficiency and stewardship assessment for a single ICU patient.

    Covers the 12 legacy rules across transfusion, restraint, frailty, and LOS.
    """

    mpi_id: str
    transfusion: dict = field(default_factory=dict)
    restraint: dict = field(default_factory=dict)
    frailty: dict = field(default_factory=dict)
    los: dict = field(default_factory=dict)
    recommendation: str = ""
    assessed_at: str = ""

    def __post_init__(self) -> None:
        if not self.assessed_at:
            self.assessed_at = datetime.now(timezone.utc).isoformat()


# ============================================================================
# Helpers
# ============================================================================


def _build_recommendation(
    transfusion_appropriate: bool,
    restraint_active: bool,
    restraint_duration_hours: float,
    cfs_score: int | None,
    los_is_outlier: bool,
) -> str:
    """Build PT-BR clinical recommendation based on efficiency evaluation.

    Args:
        transfusion_appropriate: Whether transfusions met appropriateness criteria.
        restraint_active: Whether mechanical restraint is currently active.
        restraint_duration_hours: Duration of current restraint episode.
        cfs_score: Clinical Frailty Scale score (1-9), or None if not assessed.
        los_is_outlier: Whether ICU LOS exceeds expected benchmark.

    Returns:
        Recommendation string in Portuguese (BR).
    """
    parts: list[str] = []

    if not transfusion_appropriate:
        parts.append(
            "Revisar protocolo transfusional — critérios de adequação não atendidos. "
            "Recomenda-se auditoria das transfusões recentes."
        )
    else:
        parts.append(
            "Transfusões dentro dos critérios de adequação. Manter monitorização."
        )

    if restraint_active and restraint_duration_hours > 4:
        parts.append(
            f"Contenção mecânica ativa há {restraint_duration_hours:.1f}h — "
            "reavaliar necessidade e documentar revisão diária."
        )
    elif restraint_active:
        parts.append(
            "Contenção mecânica ativa — programar reavaliação em 4h."
        )
    else:
        parts.append("Contenção mecânica sem intercorrências.")

    if cfs_score is not None and cfs_score >= 5:
        parts.append(
            f"CFS {cfs_score} — paciente frágil. Considerar abordagem multidimensional "
            "e metas de cuidado proporcionais."
        )
    elif cfs_score is not None:
        parts.append(f"CFS {cfs_score} — fragilidade dentro do esperado.")

    if los_is_outlier:
        parts.append(
            "Tempo de permanência na UTI acima do benchmark esperado. "
            "Revisar barreiras de alta e plano de cuidados."
        )
    else:
        parts.append("Tempo de permanência na UTI dentro do esperado.")

    return " ".join(parts)


# ============================================================================
# Criteria evaluation functions
# ============================================================================


def evaluate_transfusion_criteria(
    inputs: dict[str, Any] | None = None,
) -> dict:
    """Evaluate all 12 transfusion-appropriateness criteria.

    Args:
        inputs: Optional dict with clinical data:
            - hb_pre (float): Pre-transfusion Hb in g/dL
            - hb_post (float): Post-transfusion Hb in g/dL
            - units (int): Number of units transfused
            - reassessed_6h (bool): Clinical reassessment within 6h post-transfusion
            - reaction (bool): Whether a transfusion reaction occurred
            - indication_documented (bool): Clinical indication documented
            - consent_signed (bool): Transfusion consent signed
            - patient_id_checked (bool): Double-check of patient ID performed
            - abo_rh_confirmed (bool): ABO/Rh compatibility confirmed
            - cold_chain_ok (bool): Cold chain maintained
            - infusion_time_min (float): Infusion time in minutes per unit

    Returns:
        Dict with keys:
            criteria: list[dict] — individual criterion results
            appropriate: bool — overall appropriateness
            met_count: int — number of criteria met
    """
    criteria_results: list[dict] = []
    met_count = 0
    inp = inputs or {}

    # TF-001: Hb pré-transfusional documentada
    hb_pre = inp.get("hb_pre")
    tf001_met = hb_pre is not None
    criteria_results.append({
        "code": "TF-001",
        "description": "Hb pré-transfusional documentada",
        "met": tf001_met,
        "detail": f"Hb = {hb_pre} g/dL" if tf001_met else "Hb pré-transfusional não registrada",
    })
    if tf001_met:
        met_count += 1

    # TF-002: Hb ≥ 7 g/dL (gatilho restritivo) — met means it's WITHIN threshold (appropriate)
    tf002_met = hb_pre is not None and hb_pre >= 7.0
    criteria_results.append({
        "code": "TF-002",
        "description": "Hb ≥ 7 g/dL (gatilho restritivo)",
        "met": tf002_met,
        "detail": (
            f"Gatilho restritivo respeitado — Hb {hb_pre} < 7.0"
            if not tf002_met and hb_pre is not None
            else f"Hb = {hb_pre} g/dL — requer justificativa"
            if tf002_met
            else "Hb não disponível para avaliação do gatilho"
        ),
    })
    if tf002_met:
        met_count += 1

    # TF-003: Transfusão em 1 unidade (single-unit strategy)
    units = inp.get("units", 0)
    tf003_met = units <= 1
    criteria_results.append({
        "code": "TF-003",
        "description": "Transfusão em 1 unidade (single-unit)",
        "met": tf003_met,
        "detail": f"{units} unidade(s) transfundida(s)",
    })
    if tf003_met:
        met_count += 1

    # TF-004: Reavaliação clínica pós-transfusional em até 6h
    reassessed = inp.get("reassessed_6h", False)
    tf004_met = bool(reassessed)
    criteria_results.append({
        "code": "TF-004",
        "description": "Reavaliação clínica pós-transfusional",
        "met": tf004_met,
        "detail": (
            "Reavaliação documentada em até 6h"
            if tf004_met
            else "Reavaliação pós-transfusional pendente"
        ),
    })
    if tf004_met:
        met_count += 1

    # TF-005: Hb pós-transfusional documentada
    hb_post = inp.get("hb_post")
    tf005_met = hb_post is not None
    criteria_results.append({
        "code": "TF-005",
        "description": "Hb pós-transfusional documentada",
        "met": tf005_met,
        "detail": f"Hb pós = {hb_post} g/dL" if tf005_met else "Hb pós-transfusional pendente",
    })
    if tf005_met:
        met_count += 1

    # TF-006: Ausência de reação transfusional
    reaction = inp.get("reaction", False)
    tf006_met = not bool(reaction)
    criteria_results.append({
        "code": "TF-006",
        "description": "Ausência de reação transfusional",
        "met": tf006_met,
        "detail": (
            "Sem sinais de reação transfusional"
            if tf006_met
            else "Reação transfusional registrada — verificar protocolo"
        ),
    })
    if tf006_met:
        met_count += 1

    # TF-007: Indicação clínica documentada
    indication_doc = inp.get("indication_documented", False)
    tf007_met = bool(indication_doc)
    criteria_results.append({
        "code": "TF-007",
        "description": "Indicação clínica documentada",
        "met": tf007_met,
        "detail": (
            "Indicação registrada no prontuário"
            if tf007_met
            else "Indicação clínica não documentada"
        ),
    })
    if tf007_met:
        met_count += 1

    # TF-008: Termo de consentimento assinado
    consent = inp.get("consent_signed", False)
    tf008_met = bool(consent)
    criteria_results.append({
        "code": "TF-008",
        "description": "Termo de consentimento assinado",
        "met": tf008_met,
        "detail": (
            "Consentimento informado documentado"
            if tf008_met
            else "Consentimento pendente"
        ),
    })
    if tf008_met:
        met_count += 1

    # TF-009: Identificação correta do paciente
    id_checked = inp.get("patient_id_checked", False)
    tf009_met = bool(id_checked)
    criteria_results.append({
        "code": "TF-009",
        "description": "Identificação correta do paciente",
        "met": tf009_met,
        "detail": (
            "Dupla checagem de identificação realizada"
            if tf009_met
            else "Dupla checagem pendente"
        ),
    })
    if tf009_met:
        met_count += 1

    # TF-010: Compatibilidade ABO/Rh confirmada
    abo_ok = inp.get("abo_rh_confirmed", False)
    tf010_met = bool(abo_ok)
    criteria_results.append({
        "code": "TF-010",
        "description": "Compatibilidade ABO/Rh confirmada",
        "met": tf010_met,
        "detail": (
            "Prova cruzada / compatibilidade confirmada"
            if tf010_met
            else "Confirmação de compatibilidade pendente"
        ),
    })
    if tf010_met:
        met_count += 1

    # TF-011: Temperatura de armazenamento adequada
    cold_ok = inp.get("cold_chain_ok", False)
    tf011_met = bool(cold_ok)
    criteria_results.append({
        "code": "TF-011",
        "description": "Temperatura de armazenamento adequada",
        "met": tf011_met,
        "detail": (
            "Cadeia de frio mantida"
            if tf011_met
            else "Registro de cadeia de frio pendente"
        ),
    })
    if tf011_met:
        met_count += 1

    # TF-012: Tempo de infusão ≤ 4 horas
    infusion_min = inp.get("infusion_time_min")
    if infusion_min is not None:
        tf012_met = float(infusion_min) <= 240  # 4 hours = 240 min
        detail = f"Infusão em {infusion_min} min"
    else:
        tf012_met = False
        detail = "Tempo de infusão não registrado"
    criteria_results.append({
        "code": "TF-012",
        "description": "Tempo de infusão ≤ 4 horas",
        "met": tf012_met,
        "detail": detail,
    })
    if tf012_met:
        met_count += 1

    # Overall appropriateness: appropriate if ≥ 8 of 12 criteria are met
    appropriate = met_count >= 8

    return {
        "criteria": criteria_results,
        "appropriate": appropriate,
        "met_count": met_count,
        "total": 12,
    }


def evaluate_restraint(
    inputs: dict[str, Any] | None = None,
) -> dict:
    """Evaluate mechanical restraint monitoring (2 criteria: duration, reassessment).

    Args:
        inputs: Optional dict with:
            - active (bool): Whether restraint is currently active
            - duration_hours (float): Duration in hours
            - reassessed_today (bool): Whether daily reassessment was performed

    Returns:
        Dict with: active, duration_hours, reassessed_today, status
    """
    inp = inputs or {}
    active = bool(inp.get("active", False))
    duration = float(inp.get("duration_hours", 0))
    reassessed = bool(inp.get("reassessed_today", False))

    # Determine status
    if not active:
        status = RestraintStatus.NONE.value
    elif reassessed:
        status = RestraintStatus.ACTIVE.value
    else:
        status = RestraintStatus.ACTIVE.value

    return {
        "active": active,
        "duration_hours": duration,
        "reassessed_today": reassessed,
        "status": status,
        "criteria_met": {
            "duration_within_limit": duration <= 4,
            "daily_reassessment": reassessed,
        },
    }


def evaluate_frailty(
    inputs: dict[str, Any] | None = None,
) -> dict:
    """Evaluate frailty scoring (Clinical Frailty Scale 1-9).

    Args:
        inputs: Optional dict with:
            - cfs_score (int): CFS score 1-9
            - scale (str): Frailty scale used (CFS, mFI, FRAIL)

    Returns:
        Dict with: cfs_score, scale, category, assessed
    """
    inp = inputs or {}
    cfs_score = inp.get("cfs_score")
    scale = inp.get("scale", "CFS")

    if cfs_score is None:
        return {
            "cfs_score": None,
            "scale": scale,
            "category": "não avaliada",
            "assessed": False,
        }

    score = int(cfs_score)
    if score <= 3:
        category = "Robusto"
    elif score == 4:
        category = "Vulnerável"
    elif score <= 6:
        category = "Frágil"
    elif score <= 8:
        category = "Muito frágil"
    else:
        category = "Terminal"

    return {
        "cfs_score": score,
        "scale": scale,
        "category": category,
        "assessed": True,
    }


def evaluate_los(
    inputs: dict[str, Any] | None = None,
) -> dict:
    """Evaluate ICU length-of-stay benchmarking.

    Args:
        inputs: Optional dict with:
            - days (int): Current ICU LOS in decimal days
            - expected_days (int): Expected/benchmark LOS for the DRG/severity
            - admission_at (str): ICU admission timestamp (ISO 8601)

    Returns:
        Dict with: days, expected_days, is_outlier, admission_at
    """
    inp = inputs or {}
    days = float(inp.get("days", 0))
    expected_days = float(inp.get("expected_days", 0)) if inp.get("expected_days") is not None else None
    admission_at = inp.get("admission_at")

    # Outlier detection: actual > 1.5× expected (or > 14 days if no benchmark)
    if expected_days is not None and expected_days > 0:
        is_outlier = days > expected_days * 1.5
    else:
        is_outlier = days > 14

    return {
        "days": days,
        "expected_days": expected_days,
        "is_outlier": is_outlier,
        "admission_at": admission_at,
    }


# ============================================================================
# Main assessment function (public API)
# ============================================================================


def assess_efficiency(
    mpi_id: str,
    transfusion_inputs: dict[str, Any] | None = None,
    restraint_inputs: dict[str, Any] | None = None,
    frailty_inputs: dict[str, Any] | None = None,
    los_inputs: dict[str, Any] | None = None,
    assessed_by: str = "system",
) -> EfficiencyAssessment:
    """Evaluate a full efficiency/stewardship assessment for a patient.

    Covers all 12 legacy rules across 4 domains:
      - Transfusion appropriateness (12 criteria)
      - Mechanical restraint (2 criteria)
      - Frailty scoring (CFS 1-9)
      - ICU LOS benchmarking

    Args:
        mpi_id: Master Patient Index identifier.
        transfusion_inputs: Clinical data for transfusion criteria evaluation.
        restraint_inputs: Clinical data for mechanical restraint evaluation.
        frailty_inputs: Clinical data for frailty scoring.
        los_inputs: Clinical data for LOS benchmarking.
        assessed_by: Identifier for the user/system performing the assessment.

    Returns:
        EfficiencyAssessment dataclass with full evaluation results.
    """
    transfusion = evaluate_transfusion_criteria(transfusion_inputs)
    restraint = evaluate_restraint(restraint_inputs)
    frailty = evaluate_frailty(frailty_inputs)
    los = evaluate_los(los_inputs)

    recommendation = _build_recommendation(
        transfusion_appropriate=transfusion["appropriate"],
        restraint_active=restraint["active"],
        restraint_duration_hours=restraint["duration_hours"],
        cfs_score=frailty["cfs_score"],
        los_is_outlier=los["is_outlier"],
    )

    return EfficiencyAssessment(
        mpi_id=mpi_id,
        transfusion=transfusion,
        restraint=restraint,
        frailty=frailty,
        los=los,
        recommendation=recommendation,
        assessed_at=datetime.now(timezone.utc).isoformat(),
    )


# ============================================================================
# Catalog helpers
# ============================================================================


def get_transfusion_criteria_catalog() -> list[dict[str, str]]:
    """Return the full 12-item transfusion criteria catalog.

    Returns:
        List of criterion dicts (code, description, category, detail).
    """
    return [dict(c) for c in TRANSFUSION_CRITERIA]


def get_transfusion_categories() -> dict[str, str]:
    """Return the category label map for transfusion criteria.

    Returns:
        Dict mapping category keys to human-readable labels.
    """
    return {k: v for k, v in CATEGORY_LABELS.items()}
