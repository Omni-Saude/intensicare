"""Care Pathway state machine and transition logic.

Extracted from domain_trilhas_engine.py as part of F-CODE-013 component refactoring.

Removes mutable global state — converted to factory functions.

.. deprecated:: M4 (2026-07-09)
    This module is **deprecated** in favor of the new stateless
    :class:`intensicare.services.trilhas_engine.TrilhasEngine` (YAML-based,
    declarative rule engine per ADR-0020).

    The PathwayStore state machine is still used by enrollment, criteria
    update, and progress endpoints — but all read endpoints now use the new
    engine.  New code should use TrilhasEngine instead of PathwayStore.

    **Migration deadline: 2026-09-01.**  After this date, this module will
    be removed and all references must be migrated to TrilhasEngine.

    **Do NOT add new imports or new code that depends on this module.**
    The only allowed consumer is
    :mod:`intensicare.services.domain_trilhas_engine`, which re-exports
    symbols for backward compatibility.  All other modules must import from
    ``domain_trilhas_engine`` or ``trilhas_engine`` directly.

Contains:
- PatientPathwayDict: typed enrollment record
- PathwayStore: encapsulated in-memory store (factory via create_pathway_store)
- enroll_patient, evaluate_criteria, get_patient_pathways, get_pathway_progress
- Helper functions: _determine_severity, _determine_trend, _build_recommendation
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import TYPE_CHECKING, Any, TypedDict
import warnings

from intensicare.services.trilhas_definitions import _PATHWAY_BY_ID, _ensure_lookups

if TYPE_CHECKING:
    # domain_trilhas_engine imports from this module at runtime (see module
    # docstring), so this back-reference must stay TYPE_CHECKING-only to
    # avoid a circular import. The functions below import these lazily at
    # call time for the same reason; this satisfies static analysis of the
    # quoted return-type annotations.
    from intensicare.services.domain_trilhas_engine import (
        CriteriaEvaluationResult,
        PathwayEnrollmentResult,
        PathwayProgressResult,
    )

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level deprecation flag — scanned by tooling, linters, and CI
# ---------------------------------------------------------------------------
__deprecated__ = True

# ---------------------------------------------------------------------------
# Deprecation warning (M4: 2026-07-09)
# ---------------------------------------------------------------------------
warnings.warn(
    "trilhas_state.PathwayStore is deprecated. "
    "Use TrilhasEngine (intensicare.services.trilhas_engine) for new code. "
    "See ADR-0020 for migration plan.",
    DeprecationWarning,
    stacklevel=2,
)


# ============================================================================
# TypedDict for enrollment records
# ============================================================================


class PatientPathwayDict(TypedDict):
    """Typed representation of a patient pathway enrollment record.

    Mirrors the in-memory store structure used throughout the trilhas engine.
    """

    id: int
    mpi_id: str
    encounter_id: str
    bed_id: str | None
    unit: str | None
    pathway_id: int
    pathway_name: str
    pathway_slug: str
    current_state: str
    criteria_data: list[dict[str, Any]]
    status: str
    severity: str
    enrolled_at: str
    enrolled_by: str
    completed_at: str | None
    updated_at: str


# ============================================================================
# PathwayStore — factory-based state management (replaces global dicts)
# ============================================================================


class PathwayStore:
    """Encapsulated in-memory store for patient pathway enrollments.

    Replaces the previous mutable global dicts (_patient_pathway_store,
    _transition_store, _next_pp_id) with a self-contained instance.
    Use :func:`create_pathway_store` to obtain a new instance.
    """

    def __init__(self) -> None:
        warnings.warn(
            "PathwayStore is deprecated. Use TrilhasEngine instead. See ADR-0020.",
            DeprecationWarning,
            stacklevel=2,
        )
        # {mpi_id: {pathway_id: PatientPathwayDict}}
        self._patient_pathway_store: dict[str, dict[int, PatientPathwayDict]] = {}
        # {patient_pathway_id: list[transition dicts]}
        self._transition_store: dict[int, list[dict[str, Any]]] = {}
        # Auto-increment counter for patient_pathway IDs
        self._next_pp_id: int = 1

    def reset(self) -> None:
        """Reset all in-memory stores (useful for tests)."""
        self._patient_pathway_store = {}
        self._transition_store = {}
        self._next_pp_id = 1


def create_pathway_store() -> PathwayStore:
    """Factory function for creating a new PathwayStore instance.

    Use this instead of the deprecated global dicts for new code.
    For backward compatibility, a module-level default store is maintained
    in domain_trilhas_engine.py.
    """
    return PathwayStore()


# ============================================================================
# Enrollment
# ============================================================================


def enroll_patient(
    mpi_id: str,
    pathway_id: int,
    encounter_id: str = "",
    bed_id: str | None = None,
    unit: str | None = None,
    initial_criteria: list[dict[str, Any]] | None = None,
    enrolled_by: str = "system",
    store: PathwayStore | None = None,
) -> "PathwayEnrollmentResult":
    """Enroll a patient in a pathway.

    Rule 3 (setup): Terminal states complete the pathway — but enrollment always starts at "initial".
    Rule 4: Patient cannot enroll twice in the same active pathway.
    Rule 6: Enrollment starts at "initial" state with default severity "normal".

    Args:
        mpi_id: Patient identifier.
        pathway_id: Pathway ID to enroll in.
        encounter_id: Admission identifier from AMH Gold.
        bed_id: Current bed at time of enrollment.
        unit: Current unit at time of enrollment.
        initial_criteria: Optional list of initial criteria evaluations [{id, met, value}].
        enrolled_by: User or system identifier performing enrollment.
        store: PathwayStore instance. Uses default if None.

    Returns:
        PathwayEnrollmentResult with patient_pathway_id and status.
    """
    # Lazy import to avoid circular dependency
    from intensicare.services.domain_trilhas_engine import PathwayEnrollmentResult

    if store is None:
        from intensicare.services.domain_trilhas_engine import _default_store

        store = _default_store

    _ensure_lookups()
    pathway = _PATHWAY_BY_ID.get(pathway_id)
    if pathway is None:
        return PathwayEnrollmentResult(
            mpi_id=mpi_id,
            pathway_id=pathway_id,
            error=f"Pathway {pathway_id} não encontrado.",
        )

    if not pathway.get("active", True):
        return PathwayEnrollmentResult(
            mpi_id=mpi_id,
            pathway_id=pathway_id,
            error=f"Pathway '{pathway['name']}' não está ativo.",
        )

    # Rule 4: Check for active duplicate enrollment
    patient_pathways = store._patient_pathway_store.setdefault(mpi_id, {})
    if pathway_id in patient_pathways:
        existing = patient_pathways[pathway_id]
        if existing.get("status") == "active":
            return PathwayEnrollmentResult(
                mpi_id=mpi_id,
                pathway_id=pathway_id,
                error=f"Paciente {mpi_id} já está inscrito ativamente no pathway '{pathway['name']}' (ID inscrição: {existing['id']}).",
            )

    # RULE 6: Determine initial state and build criteria data
    initial_state_id = "initial"
    now = datetime.now(timezone.utc)
    enrolled_at_str = now.isoformat()

    # Build criteria_data from pathway criteria definitions + optional initial_criteria
    criteria_data: list[dict[str, Any]] = []
    initial_map: dict[str, dict[str, Any]] = {}
    if initial_criteria:
        initial_map = {ic["id"]: ic for ic in initial_criteria}

    for crit_def in pathway["criteria"]:
        cid = crit_def["id"]
        initial = initial_map.get(cid, {})
        criteria_data.append(
            {
                "id": cid,
                "name": crit_def["name"],
                "met": initial.get("met", False),
                "value": initial.get("value"),
                "evaluated_at": enrolled_at_str
                if (initial.get("met") is not None or initial.get("value"))
                else None,
            }
        )

    # Assign auto-increment ID
    pp_id = store._next_pp_id
    store._next_pp_id += 1

    enrollment: PatientPathwayDict = {
        "id": pp_id,
        "mpi_id": mpi_id,
        "encounter_id": encounter_id,
        "bed_id": bed_id,
        "unit": unit,
        "pathway_id": pathway_id,
        "pathway_name": pathway["name"],
        "pathway_slug": pathway["slug"],
        "current_state": initial_state_id,
        "criteria_data": criteria_data,
        "status": "active",
        "severity": "normal",
        "enrolled_at": enrolled_at_str,
        "enrolled_by": enrolled_by,
        "completed_at": None,
        "updated_at": enrolled_at_str,
    }
    patient_pathways[pathway_id] = enrollment

    # Initialize empty transition history
    store._transition_store[pp_id] = []

    logger.info(
        "Patient %s enrolled in pathway %s (%s), pp_id=%d",
        mpi_id,
        pathway["name"],
        pathway["slug"],
        pp_id,
    )

    return PathwayEnrollmentResult(
        patient_pathway_id=pp_id,
        mpi_id=mpi_id,
        pathway_id=pathway_id,
        current_state=initial_state_id,
        status="active",
        severity="normal",
        enrolled_at=enrolled_at_str,
    )


# ============================================================================
# Criteria evaluation and state transition
# ============================================================================


def evaluate_criteria(
    mpi_id: str,
    patient_pathway_id: int,
    criteria_updates: list[dict[str, Any]],
    store: PathwayStore | None = None,
) -> "CriteriaEvaluationResult":
    """Update criteria evaluation for a pathway enrollment.

    Rule 7: Criteria evaluation updates individual criterion met/value/timestamp fields.
    Rule 8: When all criteria for the current state are met, auto-transition to next state.
    Rule 9: Every state transition is logged (from_state, to_state, reason, timestamp).
    Rule 10: Severity mapped by met/total ratio.
    Rule 3 (partial): Reaching a terminal state completes the pathway.

    Args:
        mpi_id: Patient identifier.
        patient_pathway_id: ID of the PatientPathway enrollment.
        criteria_updates: List of {id, met, value} dicts to apply.
        store: PathwayStore instance. Uses default if None.

    Returns:
        CriteriaEvaluationResult with updated criteria, possible state change, and severity.
    """
    # Lazy import to avoid circular dependency
    from intensicare.services.domain_trilhas_engine import CriteriaEvaluationResult

    if store is None:
        from intensicare.services.domain_trilhas_engine import _default_store

        store = _default_store

    _ensure_lookups()

    # Find the enrollment
    enrollment: PatientPathwayDict | None = None
    for _pid, pathways in store._patient_pathway_store.items():
        for _pw_id, pp in pathways.items():
            if pp["id"] == patient_pathway_id:
                if pp["mpi_id"] != mpi_id:
                    # This shouldn't happen but guard
                    continue
                enrollment = pp
                break
        if enrollment is not None:
            break

    if enrollment is None:
        return CriteriaEvaluationResult(
            patient_pathway_id=patient_pathway_id,
            mpi_id=mpi_id,
            criteria=criteria_updates,
            severity="normal",
        )

    if enrollment["status"] != "active":
        return CriteriaEvaluationResult(
            patient_pathway_id=patient_pathway_id,
            mpi_id=mpi_id,
            criteria=enrollment.get("criteria_data", []),
            state_changed=False,
            new_state=enrollment["current_state"],
            severity=enrollment.get("severity", "normal"),
        )

    pathway = _PATHWAY_BY_ID.get(enrollment["pathway_id"])
    if pathway is None:
        return CriteriaEvaluationResult(
            patient_pathway_id=patient_pathway_id,
            mpi_id=mpi_id,
            criteria=criteria_updates,
            severity="normal",
        )

    # Build update map
    update_map: dict[str, dict[str, Any]] = {u["id"]: u for u in criteria_updates}
    now = datetime.now(timezone.utc)
    now_str = now.isoformat()

    # Apply updates to criteria_data
    criteria_data = enrollment.get("criteria_data", [])
    for crit in criteria_data:
        cid = crit["id"]
        if cid in update_map:
            upd = update_map[cid]
            crit["met"] = upd.get("met", crit.get("met", False))
            crit["value"] = upd.get("value", crit.get("value"))
            crit["evaluated_at"] = now_str

    enrollment["criteria_data"] = criteria_data
    enrollment["updated_at"] = now_str

    # ── Rule 8 + 9 + 3: State transition logic ──
    states: list[dict[str, Any]] = pathway.get("states", [])
    current_state_id = enrollment["current_state"]
    state_changed = False
    new_state = current_state_id
    transition_reason = ""

    # Find current state index
    current_idx: int | None = None
    for i, s in enumerate(states):
        if s["id"] == current_state_id:
            current_idx = i
            break

    if current_idx is not None:
        # Check if all criteria are met for this state
        # The rule: if ALL criteria in the pathway are met, advance one state
        all_met = all(c.get("met", False) for c in criteria_data)

        if all_met:
            # Advance to next state if not already at terminal
            next_idx = current_idx + 1
            if next_idx < len(states):
                next_state_def = states[next_idx]
                new_state = next_state_def["id"]
                transition_reason = (
                    f"Todos os {len(criteria_data)} critérios do pathway atendidos. "
                    f"Avançando de '{states[current_idx]['name']}' para '{next_state_def['name']}'."
                )
                enrollment["current_state"] = new_state
                state_changed = True

                # Log transition (Rule 9)
                transition = {
                    "from_state": current_state_id,
                    "to_state": new_state,
                    "reason": transition_reason,
                    "changed_at": now_str,
                }
                store._transition_store.setdefault(patient_pathway_id, []).append(transition)

                # Rule 3: Check if new state is terminal
                if next_state_def.get("is_terminal", False):
                    enrollment["status"] = "completed"
                    enrollment["completed_at"] = now_str
                    logger.info(
                        "Patient %s completed pathway %s (pp_id=%d)",
                        mpi_id,
                        pathway["name"],
                        patient_pathway_id,
                    )

                logger.info(
                    "State transition for pp_id=%d: %s -> %s (%s)",
                    patient_pathway_id,
                    current_state_id,
                    new_state,
                    next_state_def["name"],
                )

    # ── Rule 10: Severity determination ──
    met_count = sum(1 for c in criteria_data if c.get("met", False))
    total_count = len(criteria_data)
    severity = _determine_severity(met_count, total_count)
    enrollment["severity"] = severity

    return CriteriaEvaluationResult(
        patient_pathway_id=patient_pathway_id,
        mpi_id=mpi_id,
        criteria=[dict(c) for c in criteria_data],
        state_changed=state_changed,
        new_state=new_state,
        transition_reason=transition_reason,
        severity=severity,
    )


# ============================================================================
# Patient pathway queries
# ============================================================================


def get_patient_pathways(
    mpi_id: str,
    status_filter: str = "active",
    store: PathwayStore | None = None,
) -> list[dict[str, Any]]:
    """Get all pathways a patient is enrolled in.

    Rule 13: Filters by status (active, completed, archived).

    Args:
        mpi_id: Patient identifier.
        status_filter: Status to filter by. "all" returns all statuses.
        store: PathwayStore instance. Uses default if None.

    Returns:
        List of enrollment dicts with pathway metadata and criteria.
    """
    if store is None:
        from intensicare.services.domain_trilhas_engine import _default_store

        store = _default_store

    _ensure_lookups()
    patient_pathways = store._patient_pathway_store.get(mpi_id, {})

    results: list[dict[str, Any]] = []
    for pathway_id, pp in patient_pathways.items():
        if status_filter != "all" and pp.get("status") != status_filter:
            continue
        pathway = _PATHWAY_BY_ID.get(pathway_id)
        results.append(
            {
                "id": pp["id"],
                "mpi_id": pp["mpi_id"],
                "encounter_id": pp.get("encounter_id", ""),
                "bed_id": pp.get("bed_id"),
                "unit": pp.get("unit"),
                "pathway_id": pp["pathway_id"],
                "pathway_name": pp.get(
                    "pathway_name", pathway["name"] if pathway else "Desconhecido"
                ),
                "pathway_slug": pp.get("pathway_slug", pathway["slug"] if pathway else ""),
                "current_state": pp["current_state"],
                "criteria_data": [dict(c) for c in pp.get("criteria_data", [])],
                "status": pp["status"],
                "severity": pp.get("severity", "normal"),
                "enrolled_at": pp["enrolled_at"],
                "enrolled_by": pp.get("enrolled_by", ""),
                "completed_at": pp.get("completed_at"),
                "updated_at": pp.get("updated_at"),
            }
        )
    return results


def get_pathway_progress(
    mpi_id: str,
    patient_pathway_id: int,
    store: PathwayStore | None = None,
) -> "PathwayProgressResult":
    """Get detailed progress for a patient in a specific pathway.

    Rule 11: Trend derived from forward/backward/stable transitions in state history.
    Rule 12: PT-BR recommendation generated from pathway name + current state + severity.
    Rule 14: Computes criteria_summary (total, met, not_met, pending).

    Args:
        mpi_id: Patient identifier.
        patient_pathway_id: ID of the PatientPathway enrollment.
        store: PathwayStore instance. Uses default if None.

    Returns:
        PathwayProgressResult with criteria summary, state history, trend, and recommendation.
    """
    # Lazy import to avoid circular dependency
    from intensicare.services.domain_trilhas_engine import PathwayProgressResult

    if store is None:
        from intensicare.services.domain_trilhas_engine import _default_store

        store = _default_store

    _ensure_lookups()

    # Find the enrollment
    enrollment: PatientPathwayDict | None = None
    pathway: dict[str, Any] | None = None
    for _pid, pathways in store._patient_pathway_store.items():
        for pw_id, pp in pathways.items():
            if pp["id"] == patient_pathway_id and pp["mpi_id"] == mpi_id:
                enrollment = pp
                pathway = _PATHWAY_BY_ID.get(pw_id)
                break
        if enrollment is not None:
            break

    if enrollment is None:
        # Return empty progress
        return PathwayProgressResult(
            patient_pathway_id=patient_pathway_id,
            mpi_id=mpi_id,
            pathway_name="Desconhecido",
            current_state="",
            criteria_summary={"total": 0, "met": 0, "not_met": 0, "pending": 0},
            criteria=[],
            state_history=[],
            trend="none",
            last_evaluated_at="",
            recommendation="Inscrição não localizada. Verifique o ID do pathway.",
        )

    pathway_name = enrollment.get(
        "pathway_name", pathway.get("name", "Desconhecido") if pathway else "Desconhecido"
    )

    # ── Rule 14: Criteria summary ──
    criteria_data: list[dict[str, Any]] = enrollment.get("criteria_data", [])
    total = len(criteria_data)
    met = sum(1 for c in criteria_data if c.get("met", False))
    not_met = sum(1 for c in criteria_data if c.get("met") is False)
    pending = total - met - not_met

    criteria_summary: dict[str, int] = {
        "total": total,
        "met": met,
        "not_met": not_met,
        "pending": pending,
    }

    # ── Rule 11: Trend from state history ──
    history = store._transition_store.get(patient_pathway_id, [])
    trend = _determine_trend(history)

    # Last evaluation timestamp
    evaluated_times: list[str] = [
        str(c["evaluated_at"]) for c in criteria_data if c.get("evaluated_at")
    ]
    last_evaluated_at = max(evaluated_times) if evaluated_times else ""

    # Current state
    current_state_id = enrollment["current_state"]
    severity = enrollment.get("severity", "normal")

    # ── Rule 12: PT-BR recommendation ──
    recommendation = _build_recommendation(
        pathway_name=pathway_name,
        current_state=current_state_id,
        severity=severity,
        states=pathway.get("states", []) if pathway else [],
    )

    return PathwayProgressResult(
        patient_pathway_id=patient_pathway_id,
        mpi_id=mpi_id,
        pathway_name=pathway_name,
        current_state=current_state_id,
        criteria_summary=criteria_summary,
        criteria=[dict(c) for c in criteria_data],
        state_history=[dict(h) for h in history],
        trend=trend,
        last_evaluated_at=last_evaluated_at,
        recommendation=recommendation,
    )


# ============================================================================
# Helper functions (Rules 10, 11, 12)
# ============================================================================


def _determine_severity(met_count: int, total_count: int) -> str:
    """Map criteria met ratio to severity.

    Rule 10:
        - normal: >= 80% of criteria met
        - watch: 60-79% of criteria met
        - urgent: 40-59% of criteria met
        - critical: < 40% of criteria met

    Args:
        met_count: Number of criteria met.
        total_count: Total number of criteria.

    Returns:
        Severity string: normal, watch, urgent, or critical.
    """
    if total_count == 0:
        return "normal"
    ratio = met_count / total_count
    if ratio >= 0.80:
        return "normal"
    if ratio >= 0.60:
        return "watch"
    if ratio >= 0.40:
        return "urgent"
    return "critical"


def _determine_trend(history: list[dict[str, Any]]) -> str:
    """Determine trend direction from state transition history.

    Rule 11:
        - "improving": forward progression (states moving toward terminal/alta)
        - "worsening": backward movement or regression
        - "stable": no recent changes or side-to-side transitions
        - "none": no transition history

    Since state progression is forward-only (Rule 2), we evaluate based on
    recency and direction of transitions.

    Args:
        history: List of transition dicts with from_state, to_state, changed_at.

    Returns:
        Trend string: improving, stable, worsening, none.
    """
    if not history:
        return "none"

    # Count forward vs backward transitions
    # In this engine, all transitions are forward (Rule 2), but we check by
    # looking at the state order in the pathway definition.
    # For simplicity: if there's at least one transition and the latest was
    # toward a higher-order state, it's improving.
    # If no transitions in last period → stable.
    # Worsening would be handled if we allowed regression.

    # Check if the most recent transition happened recently
    # For now, any transition history = improving (since all transitions are forward)
    # Stable = no recent transitions in last evaluation window
    # We use a simple heuristic: if last transition was within reasonable timeframe

    # If there are transitions, at minimum it's "stable"
    # If the last transition moved toward a terminal/higher state, "improving"
    trend = "stable"

    # All transitions are forward by design (Rule 2)
    if len(history) >= 2:
        # Multiple forward transitions → improving
        trend = "improving"
    elif len(history) == 1:
        trend = "improving"

    return trend


def _build_recommendation(
    pathway_name: str,
    current_state: str,
    severity: str,
    states: list[dict[str, Any]] | None = None,
) -> str:
    """Generate PT-BR clinical recommendation based on pathway, state, and severity.

    Rule 12: Recommendations are generated in PT-BR.

    Args:
        pathway_name: Human-readable pathway name.
        current_state: Current state identifier.
        severity: Severity level (normal, watch, urgent, critical).
        states: Optional list of state definitions for context.

    Returns:
        Recommendation string in Portuguese (BR).
    """
    if states is None:
        states = []

    # Build state name lookup
    state_name_map: dict[str, str] = {s["id"]: s["name"] for s in states}
    state_name = state_name_map.get(current_state, current_state)

    # Pathway-specific recommendations
    if pathway_name == "Ventilação Mecânica":
        if severity == "critical":
            return (
                f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
                "Menos de 40% dos critérios atendidos. Reavaliar parâmetros ventilatórios IMEDIATAMENTE. "
                "Verificar PEEP, driving pressure e relação P/F. Considerar manobras de recrutamento alveolar "
                "e posição prona se P/F < 150. Acionar fisioterapia respiratória."
            )
        if severity == "urgent":
            return (
                f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
                "Critérios parcialmente atendidos (40-59%). Ajustar parâmetros do ventilador nas próximas 6h. "
                "Reavaliar PEEP ideal e considerar gasometria de controle. Manter cabeceira elevada 30-45°."
            )
        if severity == "watch":
            return (
                f"Acompanhar — {pathway_name} ({state_name}): "
                "Maioria dos critérios atendidos (60-79%). Manter parâmetros protetores e monitorizar "
                "tendência da mecânica pulmonar a cada 12h. Avaliar diariamente prontidão para desmame."
            )
        # normal
        return (
            f"✓ Dentro das metas — {pathway_name} ({state_name}): "
            "≥80% dos critérios de ventilação protetora atendidos. Manter estratégia atual e "
            "avaliar critérios para início do desmame ventilatório. Registrar avaliação diária."
        )

    if pathway_name == "Sepse":
        if severity == "critical":
            return (
                f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
                "Menos de 40% dos critérios atendidos. ACIONAR PROTOCOLO DE SEPSE IMEDIATAMENTE. "
                "Verificar: antibiótico administrado? Culturas coletadas? Ressuscitação volêmica iniciada? "
                "Lactato >4 mmol/L requer reavaliação em 2-4h. Considerar acesso central e droga vasoativa."
            )
        if severity == "urgent":
            return (
                f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
                "Critérios do bundle de sepse incompletos (40-59%). Completar bundle da 1ª hora: "
                "coletar culturas, administrar antibiótico, iniciar cristaloide 30 mL/kg. "
                "Reavaliar lactato em 2-4h."
            )
        if severity == "watch":
            return (
                f"Acompanhar — {pathway_name} ({state_name}): "
                "Bundle de sepse parcialmente completo (60-79%). Verificar itens pendentes e "
                "reavaliar resposta hemodinâmica. Monitorizar clearance de lactato a cada 6h. "
                "Avaliar descalonamento antimicrobiano em 48-72h."
            )
        # normal
        return (
            f"✓ Resposta adequada — {pathway_name} ({state_name}): "
            "≥80% dos critérios do bundle atendidos. Paciente com boa evolução. "
            "Manter monitorização e avaliar transição para via oral de antibióticos. "
            "Reavaliar culturas e possibilidade de descalonamento."
        )

    if pathway_name == "Desmame":
        if severity == "critical":
            return (
                f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
                "Menos de 40% dos critérios de desmame atendidos. Paciente NÃO está pronto para desmame. "
                "Otimizar parâmetros ventilatórios, corrigir distúrbios metabólicos e eletrolíticos. "
                "Reavaliar em 24h. Manter ventilação mecânica com parâmetros protetores."
            )
        if severity == "urgent":
            return (
                f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
                "Critérios de prontidão para desmame parcialmente atendidos (40-59%). "
                "Reavaliar força muscular respiratória (NIF) e drive respiratório (RSBI). "
                "Considerar TRE (Teste de Respiração Espontânea) se Glasgow ≥11 e tosse eficaz."
            )
        if severity == "watch":
            return (
                f"Acompanhar — {pathway_name} ({state_name}): "
                "Maioria dos critérios atendidos (60-79%). Paciente próximo da prontidão para TRE. "
                "Verificar critérios pendentes e programar teste de respiração espontânea nas próximas 12-24h. "
                "Manter sedação mínima (RASS -1 a 0)."
            )
        # normal
        return (
            f"✓ Pronto para desmame — {pathway_name} ({state_name}): "
            "≥80% dos critérios atendidos. REALIZAR TESTE DE RESPIRAÇÃO ESPONTÂNEA (TRE). "
            "Manter paciente em PSV 5-7 cmH₂O ou tubo T por 30-120 min. "
            "Se TRE bem-sucedido, proceder à extubação e iniciar monitorização pós-extubação."
        )

    if pathway_name == "Nutrição Enteral":
        if severity == "critical":
            return (
                f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
                "Menos de 40% dos critérios atendidos. Intolerância grave à dieta ou desnutrição severa. "
                "Reavaliar via de acesso nutricional, considerar nutrição parenteral suplementar. "
                "Investigar causas de intolerância (íleo, infecção, isquemia mesentérica). "
                "Acionar equipe de terapia nutricional."
            )
        if severity == "urgent":
            return (
                f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
                "Critérios nutricionais parcialmente atendidos (40-59%). Aporte calórico-proteico abaixo da meta. "
                "Avaliar resíduo gástrico e considerar procinético. Ajustar velocidade de infusão e "
                "concentração da fórmula. Reavaliar em 24h."
            )
        if severity == "watch":
            return (
                f"Acompanhar — {pathway_name} ({state_name}): "
                "Maioria dos critérios atendidos (60-79%). Progredir dieta conforme protocolo, "
                "atingindo meta calórica em até 72h. Monitorizar resíduo gástrico a cada 6h e "
                "sinais de intolerância. Manter cabeceira elevada."
            )
        # normal
        return (
            f"✓ Meta nutricional — {pathway_name} ({state_name}): "
            "≥80% dos critérios atendidos. Aporte calórico e proteico adequados. "
            "Avaliar transição para dieta via oral conforme melhora clínica. "
            "Manter monitorização de tolerância e balanço nitrogenado semanal."
        )

    # Generic fallback recommendation
    if severity == "critical":
        return (
            f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
            "Menos de 40% dos critérios clínicos atendidos. Requer intervenção imediata. "
            "Reavaliar todos os parâmetros e acionar equipe multidisciplinar."
        )
    if severity == "urgent":
        return (
            f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
            "Critérios parcialmente atendidos (40-59%). Priorizar itens pendentes e reavaliar em 6-12h."
        )
    if severity == "watch":
        return (
            f"Acompanhar — {pathway_name} ({state_name}): "
            "Maioria dos critérios atendidos (60-79%). Verificar pendências e manter monitorização programada."
        )
    return (
        f"✓ Dentro das metas — {pathway_name} ({state_name}): "
        "≥80% dos critérios atendidos. Manter conduta atual e reavaliar conforme protocolo."
    )
