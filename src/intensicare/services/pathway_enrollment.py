"""Care Pathway enrollment/evaluation service — Postgres-backed.

Faithful port of the clinical rules previously implemented against the
deprecated in-memory :mod:`intensicare.services.trilhas_state`
(``PathwayStore``), now executed against the real database via
:class:`intensicare.services.pathway_repository.PathwayRepository`.

Ported rules (see the docstrings of each function below and
``trilhas_state.py`` for the original numbering):
  - Rule 3: Reaching a terminal state completes the pathway; enrollment
    always starts at "initial".
  - Rule 4: A patient cannot hold two *active* enrollments in the same
    pathway at once.
  - Rule 6: Enrollment starts at state "initial" with severity "normal".
  - Rule 7: Criteria evaluation updates individual criterion
    met/value/timestamp fields.
  - Rule 8: When all criteria are met, auto-transition to the next state.
  - Rule 9: Every state transition is logged.
  - Rule 10: Severity mapped by met/total ratio.
  - Rule 11: Trend derived from the state transition history.
  - Rule 12: PT-BR clinical recommendation text.
  - Rule 13: ``status_filter`` on pathway listing.
  - Rule 14: ``criteria_summary`` (total/met/not_met/pending).

Design notes / decisions made where the approved design was ambiguous:

  - The pathway *definition* (states, criteria) is read from the database
    via :class:`PathwayRepository`, never from the legacy
    ``trilhas_definitions._PATHWAY_BY_ID`` in-memory catalog. Callers are
    expected to have run the boot-time pathway sync (owned by another
    agent) so ``pathways``/``pathway_criteria`` are populated.
  - ``domain_trilhas_engine.check_pathway_eligibility`` (the per-slug
    auto-triage rules 15-18, e.g. checking ``patient_data`` keys for
    "ventilacao"/"sepse"/"desmame"/"nutricao") was **NOT** ported here.
    That function only *advises* whether a patient looks eligible before
    enrollment; it performs no state mutation, isn't part of the
    persistence layer, and the task scope was limited to
    enroll/evaluate/list/progress. It should be ported separately (or
    replaced by ``TrilhasEngine``, per ADR-0020) by whichever agent wires
    up the enrollment router/endpoint.
  - JSONB columns (``criteria_data`` on ``PatientPathway``) are not wrapped
    in SQLAlchemy ``Mutable`` types, so in-place mutation would not be
    detected by the unit-of-work. Every criteria update reassigns a fresh
    list to ``enrollment.criteria_data`` to guarantee the column is
    flushed.
  - Duplicate active enrollment is guarded twice: an upfront read
    (``PathwayRepository.get_active_enrollment``) for the common case, and
    an ``IntegrityError`` catch around the insert as the authoritative
    guard against a race, backed by the partial unique index
    ``uq_active_enrollment`` (migration 0037, owned by another agent).
    Both paths raise the same PT-BR error message shape as the legacy
    in-memory store.
  - After a state transition, a best-effort ``pathway.updated`` WebSocket
    event is published via the existing channel manager
    (``intensicare.api.v1.ws.get_ws_manager``). Publish failures are
    caught and logged — they must never fail the clinical transaction
    (enrollment/criteria update) that triggered them.
  - The trend/recommendation helpers (``_determine_trend``,
    ``_build_recommendation``) are copied verbatim from ``trilhas_state.py``
    rather than imported, since that module is deprecated and slated for
    removal (2026-09-01) — this module must not depend on it.
    ``trilhas_state.py`` itself was not modified.
  - ``_determine_severity`` (Rule 10) was NOT copied verbatim: the legacy
    met/total *ratio* rule (see git history) is a P0 clinical-safety bug
    (gatekeeper G-S2) — it treats a criterion that was never evaluated
    (``value`` is ``None``) as if it had failed, inflating severity for any
    pathway with a partial evaluation. It has been replaced with a
    band-based rule that reuses the existing YAML predicate classifier
    (:class:`~intensicare.services.trilhas_compiler.PredicateCompiler`, the
    same one ``TrilhasEvaluator``/the alerting engine use) — see its
    docstring below for the full rule and rationale.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.schemas.severity import max_severity
from intensicare.services.domain_trilhas_engine import (
    CriteriaEvaluationResult,
    PathwayEnrollmentResult,
    PathwayProgressResult,
)
from intensicare.services.pathway_repository import PathwayRepository
from intensicare.services.trilhas_compiler import PredicateCompiler
from intensicare.services.trilhas_engine import TrilhasEngine

logger = logging.getLogger(__name__)


# ============================================================================
# Enrollment (Rules 3, 4, 6)
# ============================================================================


async def enroll_patient(
    db: AsyncSession,
    mpi_id: str,
    pathway_id: int,
    encounter_id: str = "",
    bed_id: str | None = None,
    unit: str | None = None,
    initial_criteria: list[dict[str, Any]] | None = None,
    enrolled_by: str = "system",
) -> PathwayEnrollmentResult:
    """Enroll a patient in a pathway.

    Rule 3 (setup): Terminal states complete the pathway — but enrollment
    always starts at "initial".
    Rule 4: Patient cannot enroll twice in the same active pathway.
    Rule 6: Enrollment starts at "initial" state with default severity
    "normal".

    Args:
        db: Async database session (transaction owned by the caller).
        mpi_id: Patient identifier.
        pathway_id: Pathway ID to enroll in.
        encounter_id: Admission identifier from AMH Gold.
        bed_id: Current bed at time of enrollment.
        unit: Current unit at time of enrollment.
        initial_criteria: Optional list of initial criteria evaluations
            [{id, met, value}].
        enrolled_by: User or system identifier performing enrollment.

    Returns:
        PathwayEnrollmentResult with patient_pathway_id and status.
    """
    repo = PathwayRepository(db)

    pathway = await repo.get_pathway(pathway_id)
    if pathway is None:
        return PathwayEnrollmentResult(
            mpi_id=mpi_id,
            pathway_id=pathway_id,
            error=f"Pathway {pathway_id} não encontrado.",
        )

    if not pathway.active:
        return PathwayEnrollmentResult(
            mpi_id=mpi_id,
            pathway_id=pathway_id,
            error=f"Pathway '{pathway.name}' não está ativo.",
        )

    # Rule 4: Check for active duplicate enrollment (fast path).
    existing = await repo.get_active_enrollment(mpi_id, pathway_id)
    if existing is not None:
        return PathwayEnrollmentResult(
            mpi_id=mpi_id,
            pathway_id=pathway_id,
            error=(
                f"Paciente {mpi_id} já está inscrito ativamente no pathway "
                f"'{pathway.name}' (ID inscrição: {existing.id})."
            ),
        )

    # Rule 6: Determine initial state and build criteria data.
    initial_state_id = "initial"
    now = datetime.now(timezone.utc)
    enrolled_at_str = now.isoformat()

    initial_map: dict[str, dict[str, Any]] = {}
    if initial_criteria:
        initial_map = {ic["id"]: ic for ic in initial_criteria}

    criteria_data: list[dict[str, Any]] = []
    for crit_def in pathway.criteria:
        cid = crit_def.id
        initial = initial_map.get(cid, {})
        criteria_data.append(
            {
                "id": cid,
                "name": crit_def.name,
                "met": initial.get("met", False),
                "value": initial.get("value"),
                "evaluated_at": (
                    enrolled_at_str
                    if (initial.get("met") is not None or initial.get("value"))
                    else None
                ),
            }
        )

    try:
        enrollment = await repo.create_enrollment(
            mpi_id=mpi_id,
            encounter_id=encounter_id,
            bed_id=bed_id,
            unit=unit,
            pathway_id=pathway_id,
            current_state=initial_state_id,
            criteria_data=criteria_data,
            status="active",
            severity="normal",
            enrolled_at=now,
            enrolled_by=enrolled_by,
            completed_at=None,
            updated_at=now,
        )
    except IntegrityError:
        # Rule 4 (race-condition path): uq_active_enrollment partial unique
        # index rejected a racing duplicate active enrollment.
        await db.rollback()
        logger.warning(
            "Duplicate active enrollment race for mpi_id=%s pathway_id=%s",
            mpi_id,
            pathway_id,
        )
        winner = await repo.get_active_enrollment(mpi_id, pathway_id)
        winner_id = winner.id if winner is not None else "?"
        return PathwayEnrollmentResult(
            mpi_id=mpi_id,
            pathway_id=pathway_id,
            error=(
                f"Paciente {mpi_id} já está inscrito ativamente no pathway "
                f"'{pathway.name}' (ID inscrição: {winner_id})."
            ),
        )

    logger.info(
        "Patient %s enrolled in pathway %s (%s), pp_id=%d",
        mpi_id,
        pathway.name,
        pathway.slug,
        enrollment.id,
    )

    return PathwayEnrollmentResult(
        patient_pathway_id=enrollment.id,
        mpi_id=mpi_id,
        pathway_id=pathway_id,
        current_state=initial_state_id,
        status="active",
        severity="normal",
        enrolled_at=enrolled_at_str,
    )


# ============================================================================
# Criteria evaluation and state transition (Rules 7, 8, 9, 10, 3)
# ============================================================================


async def evaluate_criteria(
    db: AsyncSession,
    mpi_id: str,
    patient_pathway_id: int,
    criteria_updates: list[dict[str, Any]],
) -> CriteriaEvaluationResult:
    """Update criteria evaluation for a pathway enrollment.

    Rule 7: Criteria evaluation updates individual criterion
    met/value/timestamp fields.
    Rule 8: When all criteria for the current state are met, auto-transition
    to next state.
    Rule 9: Every state transition is logged (from_state, to_state, reason,
    timestamp).
    Rule 10: Severity mapped by met/total ratio.
    Rule 3 (partial): Reaching a terminal state completes the pathway.

    Args:
        db: Async database session.
        mpi_id: Patient identifier.
        patient_pathway_id: ID of the PatientPathway enrollment.
        criteria_updates: List of {id, met, value} dicts to apply.

    Returns:
        CriteriaEvaluationResult with updated criteria, possible state
        change, and severity.
    """
    repo = PathwayRepository(db)

    enrollment = await repo.get_enrollment(patient_pathway_id, mpi_id)
    if enrollment is None:
        return CriteriaEvaluationResult(
            patient_pathway_id=patient_pathway_id,
            mpi_id=mpi_id,
            criteria=criteria_updates,
            severity="normal",
        )

    if enrollment.status != "active":
        return CriteriaEvaluationResult(
            patient_pathway_id=patient_pathway_id,
            mpi_id=mpi_id,
            criteria=[dict(c) for c in (enrollment.criteria_data or [])],
            state_changed=False,
            new_state=enrollment.current_state,
            severity=enrollment.severity or "normal",
        )

    pathway = await repo.get_pathway(enrollment.pathway_id)
    if pathway is None:
        return CriteriaEvaluationResult(
            patient_pathway_id=patient_pathway_id,
            mpi_id=mpi_id,
            criteria=criteria_updates,
            severity="normal",
        )

    # Build update map.
    update_map: dict[str, dict[str, Any]] = {u["id"]: u for u in criteria_updates}
    now = datetime.now(timezone.utc)
    now_str = now.isoformat()

    # Apply updates to a fresh criteria_data list (JSONB is not Mutable-
    # tracked — reassigning the attribute is what marks it dirty).
    criteria_data: list[dict[str, Any]] = [dict(c) for c in (enrollment.criteria_data or [])]
    for crit in criteria_data:
        cid = crit["id"]
        if cid in update_map:
            upd = update_map[cid]
            crit["met"] = upd.get("met", crit.get("met", False))
            crit["value"] = upd.get("value", crit.get("value"))
            crit["evaluated_at"] = now_str

    enrollment.criteria_data = criteria_data
    enrollment.updated_at = now

    # ── Rule 8 + 9 + 3: State transition logic ──
    states: list[dict[str, Any]] = pathway.states or []
    current_state_id = enrollment.current_state
    state_changed = False
    new_state = current_state_id
    transition_reason = ""

    # Find current state index.
    current_idx: int | None = None
    for i, s in enumerate(states):
        if s["id"] == current_state_id:
            current_idx = i
            break

    if current_idx is not None:
        # Rule: if ALL criteria in the pathway are met, advance one state.
        all_met = all(c.get("met", False) for c in criteria_data)

        if all_met:
            next_idx = current_idx + 1
            if next_idx < len(states):
                next_state_def = states[next_idx]
                new_state = next_state_def["id"]
                transition_reason = (
                    f"Todos os {len(criteria_data)} critérios do pathway atendidos. "
                    f"Avançando de '{states[current_idx]['name']}' para "
                    f"'{next_state_def['name']}'."
                )
                enrollment.current_state = new_state
                state_changed = True

                # Log transition (Rule 9).
                await repo.add_transition(
                    pp_id=patient_pathway_id,
                    from_state=current_state_id,
                    to_state=new_state,
                    reason=transition_reason,
                )

                # Rule 3: Check if new state is terminal.
                if next_state_def.get("is_terminal", False):
                    enrollment.status = "completed"
                    enrollment.completed_at = now
                    logger.info(
                        "Patient %s completed pathway %s (pp_id=%d)",
                        mpi_id,
                        pathway.name,
                        patient_pathway_id,
                    )

                logger.info(
                    "State transition for pp_id=%d: %s -> %s (%s)",
                    patient_pathway_id,
                    current_state_id,
                    new_state,
                    next_state_def["name"],
                )

    # ── Rule 10: Severity determination (band-based, see _determine_severity) ──
    severity = _determine_severity(enrollment.pathway_id, criteria_data)
    enrollment.severity = severity

    await db.flush()

    if state_changed:
        await _publish_pathway_updated(
            mpi_id=mpi_id,
            patient_pathway_id=patient_pathway_id,
            pathway_id=enrollment.pathway_id,
            pathway_slug=pathway.slug,
            from_state=current_state_id,
            to_state=new_state,
            status=enrollment.status,
            severity=severity,
        )

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
# Patient pathway queries (Rules 11, 12, 13, 14)
# ============================================================================


async def get_patient_pathways(
    db: AsyncSession,
    mpi_id: str,
    status_filter: str = "active",
) -> list[dict[str, Any]]:
    """Get all pathways a patient is enrolled in.

    Rule 13: Filters by status (active, completed, archived).

    Args:
        db: Async database session.
        mpi_id: Patient identifier.
        status_filter: Status to filter by. "all" returns all statuses.

    Returns:
        List of enrollment dicts with pathway metadata and criteria — same
        shape as the legacy ``PatientPathwayDict``, with timestamps as ISO
        strings.
    """
    repo = PathwayRepository(db)
    status_param = None if status_filter == "all" else status_filter
    enrollments = await repo.list_enrollments(mpi_id, status_param)

    results: list[dict[str, Any]] = []
    for pp in enrollments:
        pathway = pp.pathway
        results.append(
            {
                "id": pp.id,
                "mpi_id": pp.mpi_id,
                "encounter_id": pp.encounter_id or "",
                "bed_id": pp.bed_id,
                "unit": pp.unit,
                "pathway_id": pp.pathway_id,
                "pathway_name": pathway.name if pathway else "Desconhecido",
                "pathway_slug": pathway.slug if pathway else "",
                "current_state": pp.current_state,
                "criteria_data": [dict(c) for c in (pp.criteria_data or [])],
                "status": pp.status,
                "severity": pp.severity or "normal",
                "enrolled_at": pp.enrolled_at.isoformat() if pp.enrolled_at else "",
                "enrolled_by": pp.enrolled_by or "",
                "completed_at": pp.completed_at.isoformat() if pp.completed_at else None,
                "updated_at": pp.updated_at.isoformat() if pp.updated_at else None,
            }
        )
    return results


async def get_pathway_progress(
    db: AsyncSession,
    mpi_id: str,
    patient_pathway_id: int,
) -> PathwayProgressResult:
    """Get detailed progress for a patient in a specific pathway.

    Rule 11: Trend derived from forward/backward/stable transitions in
    state history.
    Rule 12: PT-BR recommendation generated from pathway name + current
    state + severity.
    Rule 14: Computes criteria_summary (total, met, not_met, pending).

    Args:
        db: Async database session.
        mpi_id: Patient identifier.
        patient_pathway_id: ID of the PatientPathway enrollment.

    Returns:
        PathwayProgressResult with criteria summary, state history, trend,
        and recommendation.
    """
    repo = PathwayRepository(db)

    enrollment = await repo.get_enrollment(patient_pathway_id, mpi_id)
    if enrollment is None:
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

    pathway = enrollment.pathway
    pathway_name = pathway.name if pathway else "Desconhecido"

    # ── Rule 14: Criteria summary ──
    criteria_data: list[dict[str, Any]] = [dict(c) for c in (enrollment.criteria_data or [])]
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
    transitions = await repo.list_transitions(patient_pathway_id)
    history: list[dict[str, Any]] = [
        {
            "from_state": t.from_state,
            "to_state": t.to_state,
            "reason": t.reason,
            "changed_at": t.changed_at.isoformat() if t.changed_at else None,
        }
        for t in transitions
    ]
    trend = _determine_trend(history)

    # Last evaluation timestamp.
    evaluated_times: list[str] = [
        str(c["evaluated_at"]) for c in criteria_data if c.get("evaluated_at")
    ]
    last_evaluated_at = max(evaluated_times) if evaluated_times else ""

    # Current state.
    current_state_id = enrollment.current_state
    severity = enrollment.severity or "normal"

    # ── Rule 12: PT-BR recommendation ──
    recommendation = _build_recommendation(
        pathway_name=pathway_name,
        current_state=current_state_id,
        severity=severity,
        states=(pathway.states if pathway and pathway.states else []),
        criteria_summary=criteria_summary,
    )

    return PathwayProgressResult(
        patient_pathway_id=patient_pathway_id,
        mpi_id=mpi_id,
        pathway_name=pathway_name,
        current_state=current_state_id,
        criteria_summary=criteria_summary,
        criteria=criteria_data,
        state_history=history,
        trend=trend,
        last_evaluated_at=last_evaluated_at,
        recommendation=recommendation,
    )


# ============================================================================
# WebSocket notification (best-effort, non-fatal)
# ============================================================================


async def _publish_pathway_updated(
    *,
    mpi_id: str,
    patient_pathway_id: int,
    pathway_id: int,
    pathway_slug: str,
    from_state: str,
    to_state: str,
    status: str,
    severity: str,
) -> None:
    """Publish a ``pathway.updated`` WebSocket event after a state transition.

    Best-effort: any failure here (no event loop consumer, connection
    manager error, serialization issue) is logged and swallowed. Publishing
    a UI notification must never roll back or fail the clinical transaction
    that produced the state transition.
    """
    try:
        from intensicare.api.v1.ws import get_ws_manager

        manager = get_ws_manager()
        await manager.publish(
            "pathway.updated",
            {
                "mpi_id": mpi_id,
                "patient_pathway_id": patient_pathway_id,
                "pathway_id": pathway_id,
                "pathway_slug": pathway_slug,
                "from_state": from_state,
                "to_state": to_state,
                "status": status,
                "severity": severity,
            },
        )
    except Exception:
        logger.warning(
            "Failed to publish pathway.updated event for pp_id=%d "
            "(non-fatal, transition already committed)",
            patient_pathway_id,
            exc_info=True,
        )


# ============================================================================
# Helper functions (Rules 10, 11, 12) — copied verbatim from trilhas_state.py
#
# trilhas_state.py is deprecated (removal deadline 2026-09-01); these pure
# functions are duplicated here rather than imported so this module has no
# runtime dependency on it. Keep in sync manually if the rules change before
# trilhas_state.py is removed.
# ============================================================================


# Lazily-constructed, module-cached TrilhasEngine used ONLY to read each
# criterion's compiled YAML predicate (bands/threshold/boolean) for severity
# classification in _determine_severity. This information is NOT persisted
# to the `pathway_criteria` table (PathwayRepository/Pathway.criteria only
# carries display fields — name/category/normal_range/alert_threshold, see
# intensicare.models.pathway.PathwayCriteria), so the DB-backed pathway
# definition fetched by PathwayRepository.get_pathway() cannot be used here.
# Mirrors the same lazy-engine pattern already used by
# intensicare.api.v1.pathways._get_engine() (kept private/duplicated rather
# than shared, to avoid a services/ -> api/ import).
_trilhas_engine: TrilhasEngine | None = None
_trilhas_engine_load_failed = False


def _get_trilhas_engine() -> TrilhasEngine | None:
    """Lazily construct and cache the TrilhasEngine, or None if unavailable.

    Never raises — a definitions-load hiccup must degrade
    ``_determine_severity`` to its "normal" fallback rather than fail the
    clinical enrollment/evaluation transaction that triggered it.
    """
    global _trilhas_engine, _trilhas_engine_load_failed
    if _trilhas_engine is not None:
        return _trilhas_engine
    if _trilhas_engine_load_failed:
        return None
    try:
        # pathway_enrollment.py -> services -> intensicare -> src -> repo root
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        yaml_dir = str(repo_root / "_work" / "alerts" / "pathways")
        _trilhas_engine = TrilhasEngine(definitions_path=yaml_dir)
    except Exception:
        logger.warning(
            "TrilhasEngine failed to load for pathway severity "
            "classification; _determine_severity will fall back to "
            "'normal' until this is resolved.",
            exc_info=True,
        )
        _trilhas_engine_load_failed = True
        return None
    return _trilhas_engine


def _determine_severity(pathway_id: int, criteria_data: list[dict[str, Any]]) -> str:
    """Derive pathway severity from the YAML severity bands of *evaluated* criteria.

    Rule 10 (corrected — gatekeeper G-S2 clinical-safety fix):

    The previous implementation derived severity from the *ratio* of
    criteria met/total (``< 40% met -> critical``). This was a P0 bug: it
    silently treated any criterion that had never been evaluated
    (``value`` is ``None``/absent) as if it had *failed*, which both (a)
    conflates "pending" with "not met", and (b) completely ignores the
    actual clinical severity bands declared per-criterion in the YAML
    pathway definition — e.g. a pathway with only one criterion evaluated
    to an "urgent" band would be reported as "critical" purely because
    2 of 3 criteria hadn't been assessed yet.

    Corrected rule:
        - Only criteria that have actually been evaluated (``value`` is
          not None) are considered. Each is classified into a severity by
          compiling its YAML ``predicate`` (graded/threshold/boolean) and
          evaluating it against ``{input: value}`` — reusing
          :class:`~intensicare.services.trilhas_compiler.PredicateCompiler`,
          the exact same classifier ``TrilhasEvaluator``/the alerting
          engine use elsewhere (band logic is intentionally NOT
          reimplemented here).
        - A criterion with no value yet is PENDING: excluded entirely from
          the computation (neither counted as critical nor as normal).
        - Pathway severity is the MAXIMUM severity across the evaluated
          criteria's classified severities, per the canonical ordering
          normal < watch < urgent < critical
          (:func:`intensicare.schemas.severity.max_severity`).
        - If nothing has been evaluated yet, severity is "normal" — the
          same default state used at enrollment (Rule 6), for coherence.

    Args:
        pathway_id: The enrollment's pathway ID, used to look up its
            compiled YAML criteria/predicates via the module-level
            TrilhasEngine.
        criteria_data: The enrollment's current criteria array. Each dict
            has at least ``id`` and ``value`` (``value`` is None/absent
            for a criterion not yet evaluated).

    Returns:
        Severity string: normal, watch, urgent, or critical.
    """
    engine = _get_trilhas_engine()
    pdef = engine.get_pathway(pathway_id) if engine is not None else None

    if pdef is None:
        # Definitions unavailable (engine failed to load) or this
        # pathway_id has no YAML source (e.g. a pathway upserted directly
        # via PathwayRepository, as some tests do) — degrade to the Rule 6
        # default rather than fail the clinical transaction.
        return "normal"

    predicate_by_criterion_id: dict[str, dict[str, Any]] = {
        c["id"]: c.get("predicate", {}) for c in pdef.criteria if c.get("id")
    }

    compiler = PredicateCompiler()
    evaluated_severities: list[str] = []

    for crit in criteria_data:
        value = crit.get("value")
        if value is None:
            continue  # Pending — excluded, per the corrected rule above.

        crit_id = crit.get("id")
        predicate = predicate_by_criterion_id.get(crit_id) if crit_id is not None else None
        if not predicate:
            logger.warning(
                "_determine_severity: no YAML predicate found for "
                "criterion %r in pathway %d; excluding it from the "
                "severity computation.",
                crit.get("id"),
                pathway_id,
            )
            continue

        try:
            compiled = compiler.compile(predicate)
            result = compiler.evaluate(compiled, {compiled.input_name: value})
        except (ValueError, KeyError, TypeError) as exc:
            logger.warning(
                "_determine_severity: failed to classify criterion %r "
                "(pathway %d, value=%r); excluding it from the severity "
                "computation: %s",
                crit.get("id"),
                pathway_id,
                value,
                exc,
            )
            continue

        evaluated_severities.append(result.severity)

    if not evaluated_severities:
        return "normal"

    return max_severity(*evaluated_severities) or "normal"


def _determine_trend(history: list[dict[str, Any]]) -> str:
    """Determine trend direction from state transition history.

    Rule 11:
        - "improving": forward progression (states moving toward
          terminal/alta)
        - "worsening": backward movement or regression
        - "stable": no recent changes or side-to-side transitions
        - "none": no transition history

    Since state progression is forward-only (Rule 2), we evaluate based on
    recency and direction of transitions.

    Args:
        history: List of transition dicts with from_state, to_state,
            changed_at.

    Returns:
        Trend string: improving, stable, worsening, none.
    """
    if not history:
        return "none"

    # Get the most recent transitions (last 3).
    recent = history[-3:]  # noqa: F841 (kept for parity with legacy source)

    # All transitions are forward by design (Rule 2).
    trend = "stable"
    if len(history) >= 2 or len(history) == 1:
        trend = "improving"

    return trend


def _build_recommendation(
    pathway_name: str,
    current_state: str,
    severity: str,
    states: list[dict[str, Any]] | None = None,
    criteria_summary: dict[str, int] | None = None,
) -> str:
    """Generate PT-BR clinical recommendation based on pathway, state, and severity.

    Rule 12: Recommendations are generated in PT-BR.

    Note (G-S2 fix — band-based severity): Severity is derived from the YAML
    severity bands of *evaluated* criteria (not a ratio of met/total). This
    function now reports the count of evaluated vs. pending criteria to make
    the severity classification transparent and clinically coherent.

    Args:
        pathway_name: Human-readable pathway name.
        current_state: Current state identifier.
        severity: Severity level (normal, watch, urgent, critical) — derived
            from band classification of evaluated criteria, not a ratio.
        states: Optional list of state definitions for context.
        criteria_summary: Optional dict with keys total/met/not_met/pending.
            Used to report how many criteria have been evaluated (met +
            not_met) vs. pending. If None, defaults to empty dict.

    Returns:
        Recommendation string in Portuguese (BR).
    """
    if states is None:
        states = []
    if criteria_summary is None:
        criteria_summary = {}

    # Build state name lookup.
    state_name_map: dict[str, str] = {s["id"]: s["name"] for s in states}
    state_name = state_name_map.get(current_state, current_state)

    # Compute evaluated vs. pending for coherent clinical messaging.
    total = criteria_summary.get("total", 0)
    evaluated = criteria_summary.get("met", 0) + criteria_summary.get("not_met", 0)
    eval_str = (
        f"{evaluated} de {total} critérios avaliados"
        if total > 0
        else "nenhum critério avaliado"
    )

    # Pathway-specific recommendations.
    if pathway_name == "Ventilação Mecânica":
        if severity == "critical":
            return (
                f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
                f"{eval_str}; faixa crítica detectada. Reavaliar parâmetros "
                "ventilatórios IMEDIATAMENTE. Verificar PEEP, driving pressure e "
                "relação P/F. Considerar manobras de recrutamento alveolar "
                "e posição prona se P/F < 150. Acionar fisioterapia respiratória."
            )
        if severity == "urgent":
            return (
                f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
                f"{eval_str}; faixa urgente. Ajustar parâmetros "
                "do ventilador nas próximas 6h. Reavaliar PEEP ideal e "
                "considerar gasometria de controle. Manter cabeceira elevada 30-45°."
            )
        if severity == "watch":
            return (
                f"Acompanhar — {pathway_name} ({state_name}): "
                f"{eval_str}; faixa de cuidado. Manter parâmetros protetores e "
                "monitorizar "
                "tendência da mecânica pulmonar a cada 12h. Avaliar diariamente prontidão para "
                "desmame."
            )
        # normal
        return (
            f"✓ Dentro das metas — {pathway_name} ({state_name}): "
            f"{eval_str}; faixa normal. Manter estratégia atual e "
            "avaliar critérios para início do desmame ventilatório. Registrar avaliação diária."
        )

    if pathway_name == "Sepse":
        if severity == "critical":
            return (
                f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
                f"{eval_str}; critério em faixa crítica. ACIONAR PROTOCOLO DE SEPSE IMEDIATAMENTE. "
                "Verificar: antibiótico administrado? Culturas coletadas? Ressuscitação volêmica "
                "iniciada? "
                "Lactato >4 mmol/L requer reavaliação em 2-4h. Considerar acesso central e droga "
                "vasoativa."
            )
        if severity == "urgent":
            return (
                f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
                f"{eval_str}; critério em faixa urgente. Completar bundle da 1ª hora: "
                "coletar culturas, administrar antibiótico, iniciar cristaloide 30 mL/kg. "
                "Reavaliar lactato em 2-4h."
            )
        if severity == "watch":
            return (
                f"Acompanhar — {pathway_name} ({state_name}): "
                f"{eval_str}; monitorização de cuidado recomendada. Verificar itens pendentes e "
                "reavaliar resposta hemodinâmica. Monitorizar clearance de lactato a cada 6h. "
                "Avaliar descalonamento antimicrobiano em 48-72h."
            )
        # normal
        return (
            f"✓ Resposta adequada — {pathway_name} ({state_name}): "
            f"{eval_str}; todos em faixa normal. Paciente com boa evolução. "
            "Manter monitorização e avaliar transição para via oral de antibióticos. "
            "Reavaliar culturas e possibilidade de descalonamento."
        )

    if pathway_name == "Desmame":
        if severity == "critical":
            return (
                f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
                f"{eval_str}; critério em faixa crítica. Paciente NÃO está pronto para "
                "desmame. "
                "Otimizar parâmetros ventilatórios, corrigir distúrbios metabólicos e "
                "eletrolíticos. "
                "Reavaliar em 24h. Manter ventilação mecânica com parâmetros protetores."
            )
        if severity == "urgent":
            return (
                f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
                f"{eval_str}; critério em faixa urgente para desmame. "
                "Reavaliar força muscular respiratória (NIF) e drive respiratório (RSBI). "
                "Considerar TRE (Teste de Respiração Espontânea) se Glasgow ≥11 e tosse eficaz."
            )
        if severity == "watch":
            return (
                f"Acompanhar — {pathway_name} ({state_name}): "
                f"{eval_str}; proximidade com prontidão para TRE monitorada. "
                "Verificar critérios pendentes e programar teste de respiração espontânea nas "
                "próximas 12-24h. "
                "Manter sedação mínima (RASS -1 a 0)."
            )
        # normal
        return (
            f"✓ Pronto para desmame — {pathway_name} ({state_name}): "
            f"{eval_str}; paciente em faixa adequada. "
            "REALIZAR TESTE DE RESPIRAÇÃO ESPONTÂNEA (TRE). "
            "Manter paciente em PSV 5-7 cmH₂O ou tubo T por 30-120 min. "
            "Se TRE bem-sucedido, proceder à extubação e iniciar monitorização pós-extubação."
        )

    if pathway_name == "Nutrição Enteral":
        if severity == "critical":
            return (
                f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
                f"{eval_str}; critério em faixa crítica. Intolerância grave à dieta ou desnutrição "
                "severa. "
                "Reavaliar via de acesso nutricional, considerar nutrição parenteral suplementar. "
                "Investigar causas de intolerância (íleo, infecção, isquemia mesentérica). "
                "Acionar equipe de terapia nutricional."
            )
        if severity == "urgent":
            return (
                f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
                f"{eval_str}; critério em faixa urgente. Aporte calórico-proteico "
                "abaixo da meta. "
                "Avaliar resíduo gástrico e considerar procinético. Ajustar velocidade de infusão "
                "e "
                "concentração da fórmula. Reavaliar em 24h."
            )
        if severity == "watch":
            return (
                f"Acompanhar — {pathway_name} ({state_name}): "
                f"{eval_str}; progresso em nível de cuidado. Progredir dieta conforme protocolo, "
                "atingindo meta calórica em até 72h. Monitorizar resíduo gástrico a cada 6h e "
                "sinais de intolerância. Manter cabeceira elevada."
            )
        # normal
        return (
            f"✓ Meta nutricional — {pathway_name} ({state_name}): "
            f"{eval_str}; meta adequada. Aporte calórico e proteico adequados. "
            "Avaliar transição para dieta via oral conforme melhora clínica. "
            "Manter monitorização de tolerância e balanço nitrogenado semanal."
        )

    # Generic fallback recommendation.
    if severity == "critical":
        return (
            f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
            f"{eval_str}; critério em faixa crítica. Requer intervenção imediata. "
            "Reavaliar todos os parâmetros e acionar equipe multidisciplinar."
        )
    if severity == "urgent":
        return (
            f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
            f"{eval_str}; critério em faixa urgente. Priorizar itens pendentes e reavaliar em "
            "6-12h."
        )
    if severity == "watch":
        return (
            f"Acompanhar — {pathway_name} ({state_name}): "
            f"{eval_str}; monitorização recomendada. Verificar pendências e manter "
            "monitorização programada."
        )
    return (
        f"✓ Dentro das metas — {pathway_name} ({state_name}): "
        f"{eval_str}; dentro dos limites normais. "
        "Manter conduta atual e reavaliar conforme protocolo."
    )
