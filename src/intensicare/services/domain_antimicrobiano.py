"""
Antimicrobial Stewardship domain — criteria catalog + evaluation logic.

12 criteria (IDs from frontend-v2/lib/antimicrobial-types.ts):
  crit-001..crit-012 across 7 categories:
    duracao, espectro, dose, cvc, candidemia, culturas, cap_covid

Scoring:
  score = count(criteria where met == True)
  severity = NEUTRO (0-3), AMARELO (4-7), VERMELHO (8-12)

Recomendações geradas em PT-BR conforme faixa de severidade.
"""

from __future__ import annotations

__version__ = "3.0.0"

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Criteria catalog (source of truth — MUST match frontend IDs exactly)
# ---------------------------------------------------------------------------

ANTIMICROBIAL_CRITERIA: list[dict[str, str]] = [
    {
        "id": "crit-001",
        "name": "Duração > 7 dias",
        "category": "duracao",
        "description": "Antimicrobiano prescrito por mais de 7 dias sem justificativa documentada.",
    },
    {
        "id": "crit-002",
        "name": "Espectro muito amplo",
        "category": "espectro",
        "description": "Antimicrobiano de espectro excessivamente amplo para o sítio infeccioso identificado.",
    },
    {
        "id": "crit-003",
        "name": "Dose inadequada",
        "category": "dose",
        "description": "Dose prescrita fora da faixa terapêutica recomendada para peso/função renal.",
    },
    {
        "id": "crit-004",
        "name": "CVC > 7 dias",
        "category": "cvc",
        "description": "Cateter venoso central mantido por mais de 7 dias sem avaliação de necessidade.",
    },
    {
        "id": "crit-005",
        "name": "Candidemia sem descalonamento",
        "category": "candidemia",
        "description": "Candidemia identificada sem descalonamento para antifúngico dirigido em até 72h.",
    },
    {
        "id": "crit-006",
        "name": "Culturas pendentes > 72h",
        "category": "culturas",
        "description": "Culturas pendentes por mais de 72 horas sem revisão do esquema empírico.",
    },
    {
        "id": "crit-007",
        "name": "CAP sem critério de gravidade",
        "category": "cap_covid",
        "description": "Pneumonia adquirida na comunidade (CAP) sem critérios de gravidade que justifiquem antibioticoterapia venosa.",
    },
    {
        "id": "crit-008",
        "name": "Dupla cobertura gram-negativo",
        "category": "espectro",
        "description": "Dupla cobertura para gram-negativos sem indicação clínica documentada (ex: P. aeruginosa multirresistente confirmada).",
    },
    {
        "id": "crit-009",
        "name": "Vancomicina > 72h sem MRSA",
        "category": "espectro",
        "description": "Vancomicina mantida por mais de 72 horas sem isolamento de MRSA ou fator de risco documentado.",
    },
    {
        "id": "crit-010",
        "name": "Duração cirúrgica > 24h",
        "category": "duracao",
        "description": "Profilaxia cirúrgica mantida por mais de 24 horas, excedendo o recomendado pelas diretrizes vigentes.",
    },
    {
        "id": "crit-011",
        "name": "Sem nível sérico (vanco/aminog)",
        "category": "dose",
        "description": "Vancomicina ou aminoglicosídeo em uso há mais de 72h sem dosagem de nível sérico.",
    },
    {
        "id": "crit-012",
        "name": "CVC sem curativo documentado",
        "category": "cvc",
        "description": "Cateter venoso central sem registro de curativo/documentação do sítio de inserção nas últimas 24h.",
    },
]

CATEGORY_LABELS: dict[str, str] = {
    "duracao": "Duração",
    "espectro": "Espectro",
    "dose": "Dose / Nível Sérico",
    "cvc": "CVC",
    "candidemia": "Candidemia",
    "culturas": "Culturas",
    "cap_covid": "CAP / COVID",
}

# ---------------------------------------------------------------------------
# Domain model
# ---------------------------------------------------------------------------


@dataclass
class AntimicrobialCriterionResult:
    """Result of checking a single antimicrobial criterion."""

    id: str
    name: str
    category: str
    description: str
    met: bool


@dataclass
class AntimicrobialAssessmentResult:
    """Complete antimicrobial stewardship evaluation result.

    Fields match the OpenAPI contract (AntimicrobialAssessment).
    """

    id: int | None = None
    mpi_id: str = ""
    criteria: list[AntimicrobialCriterionResult] = field(default_factory=list)
    score: int = 0
    severity: str = "NEUTRO"
    recommendation: str = ""
    assessed_at: datetime | None = None
    assessed_by: str = ""

    def __post_init__(self) -> None:
        """Ensure assessed_at is timezone-aware when not explicitly set."""
        if self.assessed_at is None:
            self.assessed_at = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Evaluation logic
# ---------------------------------------------------------------------------


def evaluate_criterion(
    criterion_def: dict[str, str], inputs: dict[str, Any] | None = None
) -> AntimicrobialCriterionResult:
    """Evaluate a single antimicrobial criterion against provided inputs.

    By default (inputs=None), returns a criterion result with met=False.
    The caller is expected to supply real clinical data and override met
    accordingly. This function is a placeholder for the rule engine.

    Args:
        criterion_def: Dict with id, name, category, description.
        inputs: Optional dict of clinical data to evaluate against.

    Returns:
        AntimicrobialCriterionResult with met flag set.
    """
    result = AntimicrobialCriterionResult(
        id=criterion_def["id"],
        name=criterion_def["name"],
        category=criterion_def["category"],
        description=criterion_def["description"],
        met=False,
    )

    if inputs is None:
        return result

    # TODO: Rule-engine evaluation per criterion.
    # Each criterion will have a dedicated evaluator function in future
    # milestones; for now, met is determined by the caller (via API payload
    # or data ingestion pipeline) and stored directly.
    return result


def evaluate_assessment(
    mpi_id: str,
    criteria_met: list[str] | None = None,
    assessed_by: str = "system",
    inputs: dict[str, Any] | None = None,
) -> AntimicrobialAssessmentResult:
    """Evaluate a full antimicrobial stewardship assessment.

    Args:
        mpi_id: Patient identifier.
        criteria_met: List of criterion IDs that are met (non-conformities).
                      If None, evaluates from inputs (placeholder).
        assessed_by: Identifier for the user/system performing the assessment.
        inputs: Optional clinical data dict for rule-based evaluation.

    Returns:
        AntimicrobialAssessmentResult with criteria, score, severity, recommendation.
    """
    criteria_met_set: set[str] = set(criteria_met or [])

    # Build criteria results
    criteria_results: list[AntimicrobialCriterionResult] = []
    for crit_def in ANTIMICROBIAL_CRITERIA:
        is_met = crit_def["id"] in criteria_met_set or (
            inputs is not None
            and evaluate_criterion(crit_def, inputs.get(crit_def["id"])) is not None
        )
        criteria_results.append(
            AntimicrobialCriterionResult(
                id=crit_def["id"],
                name=crit_def["name"],
                category=crit_def["category"],
                description=crit_def["description"],
                met=is_met,
            )
        )

    # Scoring
    score = sum(1 for c in criteria_results if c.met)

    # Severity band
    if score <= 3:
        severity = "NEUTRO"
    elif score <= 7:
        severity = "AMARELO"
    else:
        severity = "VERMELHO"

    # Recommendation generation (PT-BR)
    recommendation = _build_recommendation(score, severity)

    return AntimicrobialAssessmentResult(
        mpi_id=mpi_id,
        criteria=criteria_results,
        score=score,
        severity=severity,
        recommendation=recommendation,
        assessed_by=assessed_by,
    )


def _build_recommendation(score: int, severity: str) -> str:
    """Build PT-BR clinical recommendation based on score and severity.

    Args:
        score: Number of non-conformities (0-12).
        severity: Severity band (NEUTRO, AMARELO, VERMELHO).

    Returns:
        Recommendation string in Portuguese (BR).
    """
    if severity == "NEUTRO":
        return (
            "Prescrição antimicrobiana dentro dos parâmetros adequados. "
            "Manter monitorização de rotina e reavaliar em 72h."
        )
    if severity == "AMARELO":
        return (
            f"Foram identificados {score} critério(s) que requerem atenção. "
            "Recomenda-se revisão estruturada e descalonamento nas próximas 24-48h."
        )
    # VERMELHO
    return (
        f"INTERVENÇÃO IMEDIATA necessária — {score} critérios críticos "
        "identificados. Acionar equipe de stewardship e reavaliar todos os "
        "antimicrobianos em até 12h."
    )


# ---------------------------------------------------------------------------
# Criteria catalog helpers
# ---------------------------------------------------------------------------


def get_criteria_catalog() -> list[dict[str, str]]:
    """Return the full antimicrobial criteria catalog.

    Returns:
        List of criterion dicts (id, name, category, description).
    """
    return [dict(c) for c in ANTIMICROBIAL_CRITERIA]


def get_criteria_by_category(category: str) -> list[dict[str, str]]:
    """Filter criteria catalog by category.

    Args:
        category: Category key (duracao, espectro, dose, cvc, candidemia,
                  culturas, cap_covid).

    Returns:
        List of criterion dicts matching the category.
    """
    return [dict(c) for c in ANTIMICROBIAL_CRITERIA if c["category"] == category]


def get_categories() -> dict[str, str]:
    """Return the category label map.

    Returns:
        Dict mapping category keys to human-readable labels.
    """
    return dict(CATEGORY_LABELS.items())
