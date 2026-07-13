"""
Care Pathway Engine (Trilhas Engine) — **thin backward-compatibility wrapper.**

.. warning:: DEPRECATED THIN WRAPPER

    This module is a **thin re-export wrapper** around the following modules:

    - :mod:`intensicare.services.trilhas_engine` — new stateless YAML rule engine (ADR-0020)
    - :mod:`intensicare.services.trilhas_state` — legacy PathwayStore state machine (deprecated)
    - :mod:`intensicare.services.trilhas_definitions` — pathway catalog seeds

    It wires a module-level ``_default_store`` singleton so that existing
    callers of ``enroll_patient``, ``evaluate_criteria``, etc. continue to
    work without changes.  **This convenience layer exists only for
    backward compatibility and will be removed by 2026-09-01.**

    **Do NOT add new business logic here.**  New code must import directly
    from ``trilhas_engine`` (stateless engine) or, during migration,
    ``trilhas_state`` for the legacy store.  All new endpoint
    implementations should use TrilhasEngine.

Implements 18 clinical business rules across 4 pathway catalogs:
  - Ventilação Mecânica (ventilacao)
  - Sepse (sepse)
  - Desmame (desmame)
  - Nutrição Enteral (nutricao)

.. note:: M4 (2026-07-09)

    This module now re-exports the new stateless :class:`TrilhasEngine`
    and :class:`PathwayDefinition` from ``trilhas_engine.py`` alongside
    the legacy PathwayStore types for backward compatibility.

    The legacy PathwayStore state machine is **deprecated** — new code
    should use TrilhasEngine directly.  See ADR-0020 for the migration plan.

Architecture:
  - In-memory patient enrollment store (bridge to DB later via API router)
  - Dataclass return types matching OpenAPI contract (docs/contracts/pathways-openapi.yaml)
  - Seed pathways with realistic states + criteria definitions
  - State-transition engine triggered by criteria evaluation
  - PT-BR clinical recommendations

18 Rules (Regras):
  1. Only active pathways are returned when active_only=True
  2. Each pathway has ordered, forward-only state progression
  3. Reaching a terminal state completes the pathway (status=completed, completed_at set)
  4. A patient cannot enroll in the same active pathway twice (409 conflict)
  5. Eligibility check requires patient_data matching pathway criteria categories
  6. Enrollment always starts at the "initial" state with default severity "normal"
  7. Criteria evaluation updates individual criterion met/value/timestamp fields
  8. When all criteria for the current state are met, auto-transition to next state
  9. Every state transition is logged (from_state, to_state, reason, timestamp)
  10. Severity mapped by met/total ratio: normal(>=80%), watch(60-79%), urgent(40-59%), critical(<40%)
  11. Trend derived from forward/backward/stable transitions in state history
  12. PT-BR recommendation generated from pathway name + current state + severity
  13. get_patient_pathways filters by status (active/completed/archived)
  14. get_pathway_progress computes criteria_summary (total/met/not_met/pending)
  15. Eligibility for ventilacao requires ventilation/O₂ criteria data
  16. Eligibility for sepse requires qSOFA/lactate/culturas criteria data
  17. Eligibility for desmame requires weaning readiness criteria (NIF, FR/Vt, Glasgow)
  18. Eligibility for nutricao requires nutritional screening or intake criteria data
"""

from __future__ import annotations

__version__ = "3.0.0"

from dataclasses import dataclass, field
from typing import Any

# ── Import definitions (PATHWAY_SEEDS, catalog functions) ──────────────
from intensicare.services.trilhas_definitions import (
    PATHWAY_SEEDS,
    get_pathway_by_id,
    get_pathway_catalog,
)

# ── Re-exports from new stateless engine (M4) ───────────────────────────
from intensicare.services.trilhas_engine import (
    PathwayDefinition,
    TrilhasEngine,
)

# ── Import state management (PathwayStore, factory, transition functions) ──
from intensicare.services.trilhas_state import (  # noqa: F401
    PathwayStore,
    PatientPathwayDict,
    _build_recommendation,
    _determine_severity,
    _determine_trend,
    create_pathway_store,
)
from intensicare.services.trilhas_state import (
    enroll_patient as _enroll_patient,
)
from intensicare.services.trilhas_state import (
    evaluate_criteria as _evaluate_criteria,
)
from intensicare.services.trilhas_state import (
    get_pathway_progress as _get_pathway_progress,
)
from intensicare.services.trilhas_state import (
    get_patient_pathways as _get_patient_pathways,
)

# ============================================================================
# Default PathwayStore (backward-compatible module-level singleton)
# ============================================================================

_default_store: PathwayStore = create_pathway_store()


def _reset_stores() -> None:
    """Reset in-memory stores (useful for tests).

    Maintained for backward compatibility with existing test suites.
    """
    _default_store.reset()


# ============================================================================
# Dataclasses (match OpenAPI contract)
# ============================================================================


@dataclass
class PathwayEligibilityResult:
    """Result of checking whether a patient is eligible for a pathway."""

    eligible: bool
    reason: str = ""
    matching_criteria: list[str] = field(default_factory=list)


@dataclass
class PathwayEnrollmentResult:
    """Result of enrolling a patient in a pathway."""

    patient_pathway_id: int | None = None
    mpi_id: str = ""
    pathway_id: int = 0
    current_state: str = "initial"
    status: str = "active"
    severity: str = "normal"
    enrolled_at: str = ""
    error: str = ""


@dataclass
class CriteriaEvaluationResult:
    """Result of updating criteria evaluation for a pathway enrollment."""

    patient_pathway_id: int
    mpi_id: str
    criteria: list[dict[str, Any]]  # [{id, name, met, value, evaluated_at}]
    state_changed: bool = False
    new_state: str = ""
    transition_reason: str = ""
    severity: str = "normal"


@dataclass
class PathwayProgressResult:
    """Detailed progress for a patient in a specific pathway."""

    patient_pathway_id: int
    mpi_id: str
    pathway_name: str
    current_state: str
    criteria_summary: dict[str, int]  # {total, met, not_met, pending}
    criteria: list[dict[str, Any]]
    state_history: list[dict[str, Any]]
    trend: str = "none"
    last_evaluated_at: str = ""
    recommendation: str = ""


# ============================================================================
# Core functions — re-export with default store wired in
# ============================================================================


def check_pathway_eligibility(
    mpi_id: str,
    pathway_id: int,
    patient_data: dict[str, Any] | None = None,
) -> PathwayEligibilityResult:
    """Check if a patient is eligible for a pathway.

    Rule 4 (partial): Also checks whether the patient is already enrolled.
    Rule 5: Eligibility check requires patient_data matching pathway criteria categories.
    Rule 15-18: Specific eligibility rules per pathway.

    For ventilacao: patient should have ventilation/O₂ data.
    For sepse: patient should have qSOFA/lactate/culturas indicators.
    For desmame: patient should have weaning readiness data (NIF, RSBI, Glasgow).
    For nutricao: patient should have nutritional screening or intake data.

    Args:
        mpi_id: Patient identifier.
        pathway_id: Pathway ID to check eligibility against.
        patient_data: Optional clinical data dict keyed by category or criterion ID.

    Returns:
        PathwayEligibilityResult with eligibility status and reason.
    """
    from intensicare.services.trilhas_definitions import _PATHWAY_BY_ID, _ensure_lookups

    _ensure_lookups()
    pathway = _PATHWAY_BY_ID.get(pathway_id)
    if pathway is None:
        return PathwayEligibilityResult(
            eligible=False,
            reason=f"Pathway {pathway_id} não encontrado.",
        )

    if not pathway.get("active", True):
        return PathwayEligibilityResult(
            eligible=False,
            reason=f"Pathway '{pathway['name']}' não está ativo.",
        )

    # Rule 4: Check if patient is already enrolled in this pathway (active)
    patient_pathways = _default_store._patient_pathway_store.get(mpi_id, {})
    if pathway_id in patient_pathways:
        existing = patient_pathways[pathway_id]
        if existing.get("status") == "active":
            return PathwayEligibilityResult(
                eligible=False,
                reason=f"Paciente {mpi_id} já está inscrito ativamente no pathway '{pathway['name']}'.",
            )

    # Rule 5 + 15-18: Eligibility based on patient_data
    if patient_data is None:
        # Without patient data, allow enrollment but flag as requiring manual data
        return PathwayEligibilityResult(
            eligible=True,
            reason="Verificação automática indisponível (sem dados do paciente). Elegibilidade presumida — requer avaliação clínica.",
        )

    # Collect pathway category and criterion IDs
    pathway_criteria_categories: set[str] = {c["category"] for c in pathway["criteria"]}
    pathway_criteria_ids: set[str] = {c["id"] for c in pathway["criteria"]}

    slug = pathway["slug"]

    if slug == "ventilacao":
        # Rule 15: Patient must have ventilation/O₂ data
        required_cats = {"oxigenacao", "parametros"}
        if patient_data:
            data_keys = set(patient_data.keys())
            has_oxigenacao = bool(
                data_keys & {"oxigenacao", "pf_ratio", "PaO2_FiO2", "crit-vent-pf"}
            )
            has_parametros = bool(data_keys & {"parametros", "peep", "vc", "plat", "drive"})
            if has_oxigenacao and has_parametros:
                matching_criteria = [
                    c["id"] for c in pathway["criteria"] if c["category"] in required_cats
                ]
                return PathwayEligibilityResult(
                    eligible=True,
                    reason="Paciente com dados de ventilação e oxigenação adequados para o pathway de Ventilação Mecânica.",
                    matching_criteria=matching_criteria,
                )
            return PathwayEligibilityResult(
                eligible=False,
                reason="Dados insuficientes de ventilação/oxigenação. Necessário: parâmetros ventilatórios (PEEP, VC, Pplat) e oxigenação (PaO₂/FiO₂).",
            )

    elif slug == "sepse":
        # Rule 16: Patient must have qSOFA/lactate/culturas indicators
        required_cats = {"triagem", "laboratorial"}
        if patient_data:
            data_keys = set(patient_data.keys())
            has_triagem = bool(data_keys & {"triagem", "qsofa", "crit-sep-qsofa"})
            has_labs = bool(data_keys & {"laboratorial", "lactato", "pct", "crit-sep-lactato"})
            if has_triagem or has_labs:
                matching_ids: list[str] = []
                for c in pathway["criteria"]:
                    if (
                        c["category"] in required_cats
                        or c["id"] in data_keys
                        or c["category"] in data_keys
                    ):
                        matching_ids.append(c["id"])
                return PathwayEligibilityResult(
                    eligible=True,
                    reason="Paciente com indicadores de triagem/laboratoriais compatíveis com pathway de Sepse.",
                    matching_criteria=matching_ids,
                )
            return PathwayEligibilityResult(
                eligible=False,
                reason="Dados insuficientes de triagem (qSOFA) ou laboratoriais (lactato) para pathway de Sepse.",
            )

    elif slug == "desmame":
        # Rule 17: Patient must have weaning readiness criteria
        required_cats = {"mecanica", "neurologico", "clinico"}
        if patient_data:
            data_keys = set(patient_data.keys())
            has_mec = bool(data_keys & {"mecanica", "rsbi", "nif", "crit-des-frvt", "crit-des-nif"})
            has_neuro = bool(data_keys & {"neurologico", "glasgow", "crit-des-glasgow"})
            if has_mec or has_neuro:
                matching_ids = [
                    c["id"] for c in pathway["criteria"] if c["category"] in required_cats
                ]
                return PathwayEligibilityResult(
                    eligible=True,
                    reason="Paciente com critérios de avaliação de prontidão para desmame presentes.",
                    matching_criteria=matching_ids,
                )
            return PathwayEligibilityResult(
                eligible=False,
                reason="Dados insuficientes para avaliação de desmame. Necessário: mecânica respiratória (NIF, RSBI) e nível de consciência (Glasgow).",
            )

    elif slug == "nutricao":
        # Rule 18: Patient must have nutritional screening or intake criteria
        required_cats = {"triagem", "nutricional"}
        if patient_data:
            data_keys = set(patient_data.keys())
            has_triagem = bool(data_keys & {"triagem", "nrs", "crit-nut-triagem"})
            has_nut = bool(
                data_keys & {"nutricional", "calorias", "proteinas", "crit-nut-calorias"}
            )
            if has_triagem or has_nut:
                matching_ids = [
                    c["id"] for c in pathway["criteria"] if c["category"] in required_cats
                ]
                return PathwayEligibilityResult(
                    eligible=True,
                    reason="Paciente com dados de triagem nutricional ou monitorização de dieta enteral.",
                    matching_criteria=matching_ids,
                )
            return PathwayEligibilityResult(
                eligible=False,
                reason="Dados insuficientes para pathway de Nutrição Enteral. Necessário: triagem NRS-2002 ou dados de aporte calórico/proteico.",
            )

    # Generic: check if any patient data keys overlap with pathway criteria
    if patient_data:
        data_keys = set(patient_data.keys())
        overlap = pathway_criteria_ids & data_keys
        if overlap:
            return PathwayEligibilityResult(
                eligible=True,
                reason=f"Dados do paciente compatíveis com critérios do pathway: {', '.join(sorted(overlap))}.",
                matching_criteria=sorted(overlap),
            )
        cat_overlap = pathway_criteria_categories & data_keys
        if cat_overlap:
            return PathwayEligibilityResult(
                eligible=True,
                reason=f"Categorias clínicas compatíveis: {', '.join(sorted(cat_overlap))}.",
                matching_criteria=[],
            )

    return PathwayEligibilityResult(
        eligible=True,
        reason="Sem contraindicações automáticas identificadas. Elegível mediante avaliação clínica.",
    )


# ============================================================================
# Public API — wiring default store
# ============================================================================


def enroll_patient(
    mpi_id: str,
    pathway_id: int,
    encounter_id: str = "",
    bed_id: str | None = None,
    unit: str | None = None,
    initial_criteria: list[dict[str, Any]] | None = None,
    enrolled_by: str = "system",
) -> PathwayEnrollmentResult:
    """Enroll a patient in a pathway (uses default store)."""
    return _enroll_patient(
        mpi_id=mpi_id,
        pathway_id=pathway_id,
        encounter_id=encounter_id,
        bed_id=bed_id,
        unit=unit,
        initial_criteria=initial_criteria,
        enrolled_by=enrolled_by,
        store=_default_store,
    )


def evaluate_criteria(
    mpi_id: str,
    patient_pathway_id: int,
    criteria_updates: list[dict[str, Any]],
) -> CriteriaEvaluationResult:
    """Update criteria evaluation for a pathway enrollment (uses default store)."""
    return _evaluate_criteria(
        mpi_id=mpi_id,
        patient_pathway_id=patient_pathway_id,
        criteria_updates=criteria_updates,
        store=_default_store,
    )


def get_patient_pathways(
    mpi_id: str,
    status_filter: str = "active",
) -> list[dict[str, Any]]:
    """Get all pathways a patient is enrolled in (uses default store)."""
    return _get_patient_pathways(
        mpi_id=mpi_id,
        status_filter=status_filter,
        store=_default_store,
    )


def get_pathway_progress(
    mpi_id: str,
    patient_pathway_id: int,
) -> PathwayProgressResult:
    """Get detailed progress for a patient in a specific pathway (uses default store)."""
    return _get_pathway_progress(
        mpi_id=mpi_id,
        patient_pathway_id=patient_pathway_id,
        store=_default_store,
    )


# ============================================================================
# Export
# ============================================================================

__all__ = [
    # Definitions / catalog
    "PATHWAY_SEEDS",
    "CriteriaEvaluationResult",
    "PathwayDefinition",
    # Dataclasses
    "PathwayEligibilityResult",
    "PathwayEnrollmentResult",
    "PathwayProgressResult",
    # Store
    "PathwayStore",
    # TypedDicts
    "PatientPathwayDict",
    # New engine (M4)
    "TrilhasEngine",
    "_reset_stores",
    # Core engine
    "check_pathway_eligibility",
    "create_pathway_store",
    "enroll_patient",
    "evaluate_criteria",
    "get_pathway_by_id",
    "get_pathway_catalog",
    "get_pathway_progress",
    "get_patient_pathways",
]
