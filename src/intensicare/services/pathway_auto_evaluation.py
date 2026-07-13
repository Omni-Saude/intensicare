"""Pathway auto-evaluation — the missing link between vitals ingestion and the
pathway evaluation engine.

Dim A re-audit finding: :func:`sepsis_input_provider.build_sepsis_inputs`
had ZERO callers in the live codebase — pathway criteria were only ever
evaluated through a manual PUT against :func:`pathway_enrollment.evaluate_criteria`.
This module wires the orphaned provider (and an equivalent generic builder
for non-sepse pathways) into the real ingestion loop:
:func:`vitals.ingest_vitals` calls :func:`evaluate_enrolled_pathways`
best-effort after every vitals ingestion.

Design contract:
- **No clinical logic is duplicated here.** Predicate compilation/evaluation
  reuses :class:`~intensicare.services.trilhas_compiler.PredicateCompiler`
  (the exact same compiler ``pathway_enrollment._determine_severity`` and
  the live alert engine use), the pathway YAML definitions are read through
  the same cached :class:`~intensicare.services.trilhas_engine.TrilhasEngine`
  singleton ``pathway_enrollment`` already maintains
  (``pathway_enrollment._get_trilhas_engine``), and once criteria are
  translated to ``{id, met, value}`` updates they are applied through
  :func:`pathway_enrollment.evaluate_criteria` itself — so state
  transitions, severity recomputation, and the ``pathway.updated``
  WebSocket publish all happen through the one real, already-tested path.
- **Missing input = pending criterion.** Exactly like
  ``sepsis_input_provider``'s contract: a criterion whose predicate
  references an input this function cannot source from persisted data is
  left untouched (no update emitted) rather than guessed/defaulted — the
  declarative evaluator's own "value is None -> pending" handling
  (``pathway_enrollment._determine_severity``,
  ``get_pathway_progress``'s ``criteria_summary``) is the correct,
  intentional behavior.
- **Failure isolation, two layers deep.** A failure evaluating ONE
  enrollment (missing pathway definition, provider exception, compiler
  error) is caught and recorded on that enrollment's outcome without
  aborting the patient's other enrollments. The vitals-ingestion hook
  wraps the *entire* call in its own try/except — this module's failure
  must never fail a vitals ingestion.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import logging
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.models.sedacao import SedationAssessment
from intensicare.services.pathway_enrollment import _get_trilhas_engine, evaluate_criteria
from intensicare.services.pathway_repository import PathwayRepository
from intensicare.services.sepsis_input_provider import (
    SEPSE_PATHWAY_SLUG,
    _compute_map,
    _fetch_latest_vital,
    build_sepsis_inputs,
)
from intensicare.services.trilhas_compiler import (
    CompiledPredicate,
    EvaluationResult,
    PredicateCompiler,
)

logger = logging.getLogger(__name__)

__all__ = ["AutoEvalReport", "PathwayEvalOutcome", "evaluate_enrolled_pathways"]


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class PathwayEvalOutcome:
    """Result of auto-evaluating a single active pathway enrollment."""

    patient_pathway_id: int
    pathway_id: int
    pathway_slug: str
    criteria_updated: int = 0
    state_changed: bool = False
    new_state: str | None = None
    severity: str | None = None
    error: str | None = None


@dataclass
class AutoEvalReport:
    """Result of auto-evaluating every active pathway enrollment for a patient."""

    mpi_id: str
    outcomes: list[PathwayEvalOutcome] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Generic (non-sepse) input builder — latest persisted VitalSign/SedationAssessment
# ---------------------------------------------------------------------------


async def _fetch_latest_sedation(db: AsyncSession, mpi_id: str) -> SedationAssessment | None:
    stmt = (
        select(SedationAssessment)
        .where(SedationAssessment.mpi_id == mpi_id)
        .order_by(desc(SedationAssessment.assessed_at))
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _build_generic_vitals_inputs(db: AsyncSession, mpi_id: str) -> dict[str, Any]:
    """Derive simple pathway inputs from the latest persisted VitalSign/SedationAssessment.

    Covers non-sepse pathway criteria whose YAML ``input`` names map 1:1 to
    a column this codebase actually ingests today (verified against every
    ``_work/alerts/pathways/*.yaml`` file, not guessed): PAM (``map_value``,
    else derived from SBP/DBP with the same formula
    ``sepsis_input_provider._compute_map`` uses for the sepse pathway), FC
    (``heart_rate``), FR (``respiratory_rate``), temperature, SpO2,
    vasopressor dose, creatinine, and urine output — all straight off the
    most recent ``VitalSign`` row — plus RASS, which is persisted on
    ``SedationAssessment`` rather than ``VitalSign``.

    Only keys with a real persisted value are included; an input with no
    source is correctly OMITTED (pending criterion), never guessed.
    """
    out: dict[str, Any] = {}

    vital = await _fetch_latest_vital(db, mpi_id)
    if vital is not None:
        if vital.map_value is not None:
            out["pam"] = float(vital.map_value)
        elif vital.systolic_bp is not None and vital.diastolic_bp is not None:
            mapv = _compute_map(float(vital.systolic_bp), float(vital.diastolic_bp))
            if mapv is not None:
                out["pam"] = mapv
        if vital.heart_rate is not None:
            out["fc"] = float(vital.heart_rate)
        if vital.respiratory_rate is not None:
            out["fr"] = float(vital.respiratory_rate)
        if vital.temperature is not None:
            out["temp"] = float(vital.temperature)
        if vital.spo2 is not None:
            out["spo2"] = float(vital.spo2)
        if vital.vasopressor_dose_mcg_kg_min is not None:
            out["vasopressor_dose"] = float(vital.vasopressor_dose_mcg_kg_min)
        if vital.creatinine is not None:
            out["creatinina"] = float(vital.creatinine)
        if vital.urine_output_ml_day is not None:
            out["debito_urinario"] = float(vital.urine_output_ml_day)

    sedation = await _fetch_latest_sedation(db, mpi_id)
    if sedation is not None and sedation.rass_score is not None:
        out["rass_score"] = float(sedation.rass_score)

    return out


# ---------------------------------------------------------------------------
# Criterion compile+evaluate -> {id, met, value}
# ---------------------------------------------------------------------------


def _criterion_met(compiled: CompiledPredicate, result: EvaluationResult) -> bool:
    """Translate a raw compiler :class:`EvaluationResult` into pathway-enrollment "met".

    For ``graded`` predicates, ``EvaluationResult.met`` means "severity is
    not normal" (alert-worthy) — the OPPOSITE of what a pathway
    enrollment's ``met`` means ("clinical target achieved", the flag
    ``pathway_enrollment.evaluate_criteria``'s "all criteria met -> advance
    state" rule reads). The one existing production caller that already
    feeds graded pathway criteria
    (``scripts/dev/seed_demo.py::_evaluate_pathway_input``) performs this
    exact inversion (``met = result.severity == "normal"``); mirrored here
    rather than duplicated with different logic.

    Every other predicate type shipped in ``_work/alerts/pathways/*.yaml``
    (boolean, threshold, composite, temporal) already reads naturally in
    the pathway-enrollment sense: e.g. ``culturas_status == true`` means
    cultures WERE collected (met=True=good), and the v4 sepse composites
    ported from ``domain_sepsis.py`` alerts (``crit-sep-organ``,
    ``crit-sep-shock``, ...) are themselves named after the condition they
    detect (e.g. "Choque Séptico") so ``met=True`` correctly means that
    condition IS present — those are passed through unchanged.
    """
    if compiled.predicate_type == "graded":
        return result.severity == "normal"
    return result.met


def _compile_and_evaluate_criteria(
    criteria: list[dict[str, Any]], patient_data: dict[str, Any]
) -> list[dict[str, Any]]:
    """Compile+evaluate every criterion's YAML predicate against patient_data.

    Mirrors the compile/evaluate pattern
    ``pathway_enrollment._determine_severity`` already uses for severity
    classification — reused here to additionally derive ``value``/``met``
    per criterion, in the exact ``{id, met, value}`` shape
    ``pathway_enrollment.evaluate_criteria`` expects.

    A criterion whose predicate references an input not present in
    ``patient_data`` raises ``KeyError`` inside the compiler's safe lookup
    and is silently skipped (no update emitted for it) — missing input =
    pending criterion, the correct, intentional behavior.
    """
    compiler = PredicateCompiler()
    updates: list[dict[str, Any]] = []

    for crit in criteria:
        predicate = crit.get("predicate")
        cid = crit.get("id")
        if not predicate or not cid:
            continue
        try:
            compiled = compiler.compile(predicate)
            result = compiler.evaluate(compiled, patient_data)
        except KeyError:
            continue  # Required input(s) not present yet — pending, not an error.
        except (ValueError, TypeError) as exc:
            logger.warning("Auto-evaluation: failed to evaluate criterion %r: %s", cid, exc)
            continue

        updates.append(
            {
                "id": cid,
                "met": _criterion_met(compiled, result),
                "value": result.actual_value,
            }
        )

    return updates


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def evaluate_enrolled_pathways(
    db: AsyncSession, mpi_id: str, now: datetime
) -> AutoEvalReport:
    """Auto-evaluate every ACTIVE pathway enrollment for a patient.

    This is the missing link the Dim A re-audit flagged: previously,
    ``build_sepsis_inputs`` was never called by anything, so declarative
    pathway criteria were only ever updated through a manual PUT. This
    function is meant to be called best-effort right after vitals
    ingestion persists new clinical data (see ``vitals.ingest_vitals``).

    For each active enrollment:
      - sepse (slug ``"sepse"``): ``patient_data`` comes from
        :func:`sepsis_input_provider.build_sepsis_inputs` — the previously
        orphaned provider; this is its missing caller.
      - every other pathway: ``patient_data`` comes from
        :func:`_build_generic_vitals_inputs` (latest VitalSign /
        SedationAssessment columns that map 1:1 to a YAML input name).

    Args:
        db: Active async session (transaction owned by the caller).
        mpi_id: Patient identifier.
        now: Reference instant for every relative/duration input fed to
            ``build_sepsis_inputs`` (injected, never ``datetime.now()``
            internally — keeps this deterministic and testable).

    Returns:
        AutoEvalReport with one PathwayEvalOutcome per active enrollment
        (empty ``outcomes`` when the patient has none — a clean no-op).
    """
    repo = PathwayRepository(db)
    enrollments = await repo.list_enrollments(mpi_id, "active")
    if not enrollments:
        return AutoEvalReport(mpi_id=mpi_id)

    engine = _get_trilhas_engine()

    # Computed lazily, at most once per patient, and shared across every
    # enrollment of the same kind (a patient may hold several active
    # non-sepse enrollments simultaneously).
    sepsis_inputs: dict[str, Any] | None = None
    generic_inputs: dict[str, Any] | None = None

    outcomes: list[PathwayEvalOutcome] = []
    for enrollment in enrollments:
        pathway = enrollment.pathway
        slug = pathway.slug if pathway else ""
        outcome = PathwayEvalOutcome(
            patient_pathway_id=enrollment.id,
            pathway_id=enrollment.pathway_id,
            pathway_slug=slug,
        )
        try:
            if slug == SEPSE_PATHWAY_SLUG:
                if sepsis_inputs is None:
                    sepsis_inputs = await build_sepsis_inputs(db, mpi_id, now)
                patient_data = sepsis_inputs
            else:
                if generic_inputs is None:
                    generic_inputs = await _build_generic_vitals_inputs(db, mpi_id)
                patient_data = generic_inputs

            pdef = engine.get_pathway(enrollment.pathway_id) if engine is not None else None
            if pdef is None:
                logger.debug(
                    "Pathway auto-evaluation: no TrilhasEngine definition for "
                    "pathway_id=%s (pp_id=%s, mpi_id=%s) — skipping.",
                    enrollment.pathway_id,
                    enrollment.id,
                    mpi_id,
                )
                outcomes.append(outcome)
                continue

            criteria_updates = _compile_and_evaluate_criteria(pdef.criteria, patient_data)
            if not criteria_updates:
                outcomes.append(outcome)
                continue

            result = await evaluate_criteria(
                db,
                mpi_id=mpi_id,
                patient_pathway_id=enrollment.id,
                criteria_updates=criteria_updates,
            )
            outcome.criteria_updated = len(criteria_updates)
            outcome.state_changed = result.state_changed
            outcome.new_state = result.new_state or None
            outcome.severity = result.severity
        except Exception as exc:
            logger.error(
                "Pathway auto-evaluation failed for pp_id=%s pathway=%s mpi_id=%s: %s",
                enrollment.id,
                slug,
                mpi_id,
                exc,
                exc_info=True,
            )
            outcome.error = str(exc)

        outcomes.append(outcome)

    return AutoEvalReport(mpi_id=mpi_id, outcomes=outcomes)
