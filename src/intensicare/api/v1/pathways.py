"""Care Pathways API Router — 6 endpoints for Trilhas Engine.

M4 (2026-07-09): Wired new stateless TrilhasEngine (YAML-based) for all
endpoints. GET endpoints use the engine as primary source with legacy
fallback. POST/PUT endpoints use the engine for validation and declarative
evaluation passes while delegating state mutation to the persistent
enrollment service.

Sprint 1 patient-safety (2026-07-12): Migrated all enrollment/state reads
and writes off the deprecated in-memory PathwayStore
(``intensicare.services.domain_trilhas_engine`` enroll/evaluate/list/
progress) onto ``intensicare.services.pathway_enrollment`` — an
async, Postgres-backed service built on ``PathwayRepository``. The only
remaining references to ``domain_trilhas_engine`` are the static YAML-seed
CATALOG readers (``get_pathway_catalog`` / ``get_pathway_by_id``), kept as a
defensive fallback for the two catalog endpoints when the TrilhasEngine
fails to load — these are pathway *definitions*, not patient *state*, and
are not part of the deprecated PathwayStore.
"""

from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user
from intensicare.core.database import get_db
from intensicare.models.pathway import Pathway
from intensicare.models.user import User
from intensicare.schemas.pathways import (
    EnrollPatientRequest,
    PathwayCriteriaSchema,
    PathwayListResponse,
    PathwayProgressSchema,
    PathwaySchema,
    PathwayStateSchema,
    PatientPathwayListResponse,
    PatientPathwaySchema,
    UpdateCriteriaRequest,
)

# NOTE: these two are the legacy *catalog* readers (static YAML-seed
# definitions), kept only as a defensive fallback for GET /pathways and
# GET /pathways/{id} when the TrilhasEngine fails to load. They are NOT the
# deprecated in-memory PathwayStore (enrollment/state) — that dependency
# has been fully removed from this router in favor of the Postgres-backed
# intensicare.services.pathway_enrollment service below.
# check_pathway_eligibility (auto-triage) is not used by this router and
# was intentionally left unimported.
from intensicare.services.domain_trilhas_engine import (
    get_pathway_by_id as _legacy_get_pathway_by_id,
)
from intensicare.services.domain_trilhas_engine import (
    get_pathway_catalog,
)
from intensicare.services.pathway_enrollment import (
    enroll_patient,
    evaluate_criteria,
    get_pathway_progress,
    get_patient_pathways,
)
from intensicare.services.pathway_repository import PathwayRepository
from intensicare.services.trilhas_engine import TrilhasEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["pathways"])

# ---------------------------------------------------------------------------
# New stateless engine (primary for reads); falls back to legacy
# ---------------------------------------------------------------------------
_engine: TrilhasEngine | None = None


def _get_engine() -> TrilhasEngine | None:
    """Lazily initialize the TrilhasEngine. Returns None if YAML not found."""
    global _engine
    if _engine is None:
        try:
            # Resolve the repo root for YAML definitions (4 levels up from
            # this file: pathways.py → v1 → api → intensicare → src → repo)
            repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
            yaml_dir = str(repo_root / "_work" / "alerts" / "pathways")
            _engine = TrilhasEngine(definitions_path=yaml_dir)
            if not _engine.get_pathways():
                logger.warning("TrilhasEngine loaded 0 pathways; will fall back to legacy catalog")
        except Exception as exc:
            logger.warning("TrilhasEngine init failed (%s); using legacy catalog", exc)
            _engine = None
    return _engine


def _pathway_def_to_flat_dict(pdef: Any) -> dict[str, Any]:
    """Convert a PathwayDefinition (YAML-based) to the flat dict format
    expected by _to_pathway_schema.

    The YAML format nests id/name/slug under ``pathway``, whereas the legacy
    PATHWAY_SEEDS format is flat.  This helper bridges the two.
    """
    raw = pdef.to_raw() if hasattr(pdef, "to_raw") else pdef

    # Top-level keys from raw YAML
    pathway_meta = raw.get("pathway", {}) if isinstance(raw, dict) else {}
    flat_id = pathway_meta.get("id", getattr(pdef, "id", 0))
    flat_name = pathway_meta.get("name", getattr(pdef, "name", ""))
    flat_slug = pathway_meta.get("slug", getattr(pdef, "slug", ""))
    flat_desc = pathway_meta.get("description", getattr(pdef, "description", ""))
    flat_active = pathway_meta.get("active", getattr(pdef, "active", True))
    flat_version = pathway_meta.get("version", getattr(pdef, "version", ""))

    # Flatten criteria: YAML nests unit inside predicate
    raw_criteria: list[dict[str, Any]] = raw.get("criteria", []) if isinstance(raw, dict) else []
    flat_criteria: list[dict[str, Any]] = []
    for c in raw_criteria:
        pred = c.get("predicate", {})
        flat_criteria.append(
            {
                "id": c.get("id", ""),
                "name": c.get("name", ""),
                "category": c.get("category", ""),
                "description": c.get("description", pred.get("rationale", "")),
                "unit": pred.get("unit"),
                "normal_range": c.get("normal_range"),
                "alert_threshold": c.get("alert_threshold"),
            }
        )

    # Flatten states: YAML states have id/name/order/is_terminal
    raw_states: list[dict[str, Any]] = raw.get("states", []) if isinstance(raw, dict) else []
    flat_states: list[dict[str, Any]] = []
    for s in raw_states:
        flat_states.append(
            {
                "id": s.get("id", ""),
                "name": s.get("name", ""),
                "order": s.get("order", 0),
                "description": s.get("description", ""),
                "is_terminal": s.get("is_terminal", False),
            }
        )

    return {
        "id": flat_id,
        "name": flat_name,
        "description": flat_desc,
        "slug": flat_slug,
        "active": flat_active,
        "version": flat_version,
        "states": flat_states,
        "criteria": flat_criteria,
    }


def _pathway_orm_to_flat_dict(pathway: Pathway) -> dict[str, Any]:
    """Convert a persisted ``Pathway`` row (criteria eager-loaded by the
    caller via ``PathwayRepository.get_pathway``) to the same flat dict
    shape as ``_pathway_def_to_flat_dict``/legacy catalog dicts, including
    ``created_at``/``updated_at`` — which the YAML engine cannot provide
    since it is stateless.
    """
    return {
        "id": pathway.id,
        "name": pathway.name,
        "description": pathway.description,
        "slug": pathway.slug,
        "active": pathway.active,
        "states": pathway.states or [],
        "criteria": [
            {
                "id": c.id,
                "name": c.name,
                "category": c.category,
                "description": c.description,
                "unit": c.unit,
                "normal_range": c.normal_range,
                "alert_threshold": c.alert_threshold,
            }
            for c in pathway.criteria
        ],
        "created_at": pathway.created_at,
        "updated_at": pathway.updated_at,
    }


# ===========================================================================
# Helpers
# ===========================================================================


def _to_pathway_schema(data: dict[str, Any]) -> PathwaySchema:
    """Convert a pathway dict from the domain service to a PathwaySchema."""
    return PathwaySchema(
        id=data["id"],
        name=data["name"],
        description=data.get("description"),
        slug=data["slug"],
        active=data.get("active", True),
        states=[PathwayStateSchema(**s) for s in data.get("states", [])],
        criteria=[PathwayCriteriaSchema(**c) for c in data.get("criteria", [])],
        created_at=data.get("created_at"),
        updated_at=data.get("updated_at"),
    )


def _coerce_value_to_string(value: Any) -> str | None:
    """Convert numeric or string values to string format compatible with frontend.

    Handles floats (3.2 → "3.2") and ints (3 → "3" not "3.0").
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        # Convert to string, stripping unnecessary ".0" for ints
        s = str(value)
        if isinstance(value, float) and value == int(value):
            return s.split(".", maxsplit=1)[0]  # "3.0" → "3"
        return s
    return str(value)


def _merge_criteria(
    criteria_defs: list[dict[str, Any]],
    evaluated: list[dict[str, Any]] | None = None,
) -> list[PathwayCriteriaSchema]:
    """Merge pathway criteria definitions with patient-evaluated values."""
    eval_map: dict[str, dict[str, Any]] = {}
    if evaluated:
        eval_map = {c["id"]: c for c in evaluated if c.get("id")}

    result: list[PathwayCriteriaSchema] = []
    for cd in criteria_defs:
        ev = eval_map.get(cd["id"], {})
        result.append(
            PathwayCriteriaSchema(
                id=cd["id"],
                name=cd["name"],
                category=cd.get("category", ""),
                description=cd.get("description"),
                unit=cd.get("unit"),
                normal_range=cd.get("normal_range"),
                alert_threshold=cd.get("alert_threshold"),
                met=ev.get("met"),
                value=_coerce_value_to_string(ev.get("value")),
                evaluated_at=_parse_dt(ev.get("evaluated_at")),
            )
        )
    return result


async def _to_patient_pathway_schema(db: AsyncSession, pp: dict[str, Any]) -> PatientPathwaySchema:
    """Convert a patient pathway dict (from the enrollment service) to a
    schema, resolving the owning pathway definition from the persistent
    store."""
    repo = PathwayRepository(db)
    pathway_orm = await repo.get_pathway(pp["pathway_id"])
    if pathway_orm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pathway {pp['pathway_id']} não encontrado",
        )
    pathway = _pathway_orm_to_flat_dict(pathway_orm)

    criteria_data: list[dict[str, Any]] = pp.get("criteria_data", [])
    criteria_schemas = _merge_criteria(
        pathway.get("criteria", []),
        criteria_data,
    )

    # Resolve current state definition from the pathway
    current_state_id = pp["current_state"]
    current_state_def: dict[str, Any] | None = None
    for s in pathway.get("states", []):
        if s["id"] == current_state_id:
            current_state_def = s
            break

    if current_state_def is None:
        current_state_def = {
            "id": current_state_id or "unknown",
            "name": current_state_id or "Desconhecido",
            "order": 0,
        }

    return PatientPathwaySchema(
        id=pp["id"],
        mpi_id=pp["mpi_id"],
        encounter_id=pp.get("encounter_id", ""),
        bed_id=pp.get("bed_id"),
        unit=pp.get("unit"),
        pathway=_to_pathway_schema(pathway),
        current_state=PathwayStateSchema(**current_state_def),
        criteria=criteria_schemas,
        status=pp.get("status", "active"),
        severity=pp.get("severity"),
        # enrolled_at is a required field on an enrollment record (set at
        # enrollment time); _parse_dt's Optional return type is for the
        # genuinely-optional fields below (completed_at, updated_at).
        enrolled_at=_parse_dt(pp["enrolled_at"]),  # type: ignore[arg-type]
        enrolled_by=pp.get("enrolled_by"),
        completed_at=_parse_dt(pp.get("completed_at")),
        updated_at=_parse_dt(pp.get("updated_at")),
    )


async def _find_enrollment(
    db: AsyncSession,
    mpi_id: str,
    patient_pathway_id: int,
) -> dict[str, Any] | None:
    """Fetch a single patient-pathway enrollment as a dict, scoped to the
    owning patient.

    Replaces the legacy linear scan over the in-memory PathwayStore with a
    single scoped query via ``PathwayRepository.get_enrollment``. Returns
    the same dict shape as
    ``intensicare.services.pathway_enrollment.get_patient_pathways`` so
    downstream helpers (``_to_patient_pathway_schema`` et al.) don't need to
    care which path produced the enrollment.
    """
    repo = PathwayRepository(db)
    pp = await repo.get_enrollment(patient_pathway_id, mpi_id)
    if pp is None:
        return None
    pathway = pp.pathway
    return {
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


def _criteria_to_patient_data(
    criteria: list[dict[str, Any]],
) -> dict[str, Any]:
    """Convert criteria update dicts to a flat patient_data dict for TrilhasEngine.

    Extracts ``id`` and ``value`` from each criteria dict, suitable for
    passing to ``TrilhasEngine.evaluate()``.
    """
    return {c["id"]: c["value"] for c in criteria if c.get("id") and c.get("value") is not None}


def _log_evaluation_pass_failure(exc: Exception, *, phase: str, **context: object) -> None:
    """Log a TrilhasEngine evaluation-pass failure with full stack trace.

    The declarative evaluation pass is enrichment-only (it produces
    alerts/log entries; it is never the source of truth for enrollment
    state, which lives in ``pathway_enrollment``). A failure here must not
    fail the request — but it must not be silently downgraded to an
    invisible one-line warning either: an ``AttributeError`` in particular
    usually means a programming bug (e.g. a missed ``await`` on the now-
    async ``TrilhasEngine.evaluate``), and must stay visible in the logs
    with a full stack trace rather than being swallowed.
    """
    ctx = ", ".join(f"{k}={v!r}" for k, v in context.items())
    kind = (
        "AttributeError (likely a programming bug — check async/await wiring)"
        if isinstance(exc, AttributeError)
        else type(exc).__name__
    )
    logger.exception(
        "TrilhasEngine evaluation pass failed on %s (%s) [%s]; continuing "
        "since evaluation is enrichment-only, not the enrollment source of truth",
        phase,
        ctx,
        kind,
    )


def _parse_dt(value: object) -> datetime | None:
    """Parse a datetime-ish value into a datetime or None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        if not value.strip():
            return None
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None
    return None


def _resolve_current_state(pathway: dict[str, Any] | None, current_state_id: str) -> dict[str, Any]:
    """Look up state definition from the pathway the patient is enrolled in."""
    if pathway:
        for s in pathway.get("states", []):
            if s["id"] == current_state_id:
                return dict(s)
    return {
        "id": current_state_id or "unknown",
        "name": current_state_id or "Desconhecido",
        "order": 0,
    }


def _resolve_progress_criteria(
    pathway: dict[str, Any] | None,
    evaluated: list[dict[str, Any]],
) -> list[PathwayCriteriaSchema]:
    """Merge progress criteria with pathway definitions for full metadata."""
    criteria_defs: list[dict[str, Any]] = pathway.get("criteria", []) if pathway else []

    # Build def map; if no pathway found, use evaluated data as-is
    if not criteria_defs:
        return [
            PathwayCriteriaSchema(
                id=c.get("id", ""),
                name=c.get("name", ""),
                category=c.get("category", ""),
                description=c.get("description"),
                unit=c.get("unit"),
                normal_range=c.get("normal_range"),
                alert_threshold=c.get("alert_threshold"),
                met=c.get("met"),
                value=_coerce_value_to_string(c.get("value")),
                evaluated_at=_parse_dt(c.get("evaluated_at")),
            )
            for c in evaluated
        ]

    return _merge_criteria(criteria_defs, evaluated)


# ===========================================================================
# GET /pathways — Catalog listing
# ===========================================================================


@router.get("/pathways", response_model=PathwayListResponse)
async def list_pathways(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PathwayListResponse:
    """Listar todas as vias de cuidado (pathways) disponíveis no catálogo.

    Retorna o catálogo de pathways clínicos configurados no sistema.
    Cada pathway define um conjunto de critérios e estados que guiam
    o acompanhamento do paciente.

    M4: Primary source is the new YAML-based TrilhasEngine.
    Falls back to legacy PATHWAY_SEEDS if the engine is unavailable.
    Sprint 1: ``created_at``/``updated_at`` are enriched from the
    persistent ``pathways`` table (populated by the boot-time sync job)
    when the engine path is used.
    """
    engine = _get_engine()
    if engine is not None and engine.get_pathways():
        # Use new engine (YAML-driven), enriched with DB timestamps.
        repo = PathwayRepository(db)
        all_defs = engine.get_pathways()
        if active_only:
            all_defs = [p for p in all_defs if p.active]
        items = []
        for p in all_defs:
            flat = _pathway_def_to_flat_dict(p)
            db_pathway = await repo.get_pathway(flat["id"])
            if db_pathway is not None:
                flat["created_at"] = db_pathway.created_at
                flat["updated_at"] = db_pathway.updated_at
            items.append(_to_pathway_schema(flat))
    else:
        # Fallback to legacy static catalog (engine unavailable).
        catalog = get_pathway_catalog(active_only=active_only)
        items = [_to_pathway_schema(p) for p in catalog]
    return PathwayListResponse(items=items, total=len(items))


# ===========================================================================
# GET /pathways/{pathway_id} — Pathway detail with criteria
# ===========================================================================


@router.get("/pathways/{pathway_id}", response_model=PathwaySchema)
async def get_pathway(
    pathway_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PathwaySchema:
    """Obter detalhes de um pathway com seus critérios e estados.

    Retorna o pathway completo incluindo a definição de estados
    possíveis e os critérios de avaliação associados.

    M4: Uses new TrilhasEngine with legacy fallback.
    Sprint 1: enriches ``created_at``/``updated_at`` from the persistent
    ``pathways`` table when the engine path is used.
    """
    engine = _get_engine()
    pathway: dict[str, Any] | None = None
    if engine is not None:
        pdef = engine.get_pathway(pathway_id)
        if pdef is not None:
            pathway = _pathway_def_to_flat_dict(pdef)
            repo = PathwayRepository(db)
            db_pathway = await repo.get_pathway(pathway_id)
            if db_pathway is not None:
                pathway["created_at"] = db_pathway.created_at
                pathway["updated_at"] = db_pathway.updated_at
    if pathway is None:
        # Fallback to legacy static catalog
        pathway = _legacy_get_pathway_by_id(pathway_id)
    if pathway is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pathway {pathway_id} não encontrado.",
        )
    return _to_pathway_schema(pathway)


# ===========================================================================
# GET /patients/{mpi_id}/pathways — Patient's active pathways
# ===========================================================================


@router.get(
    "/patients/{mpi_id}/pathways",
    response_model=PatientPathwayListResponse,
)
async def list_patient_pathways(
    mpi_id: str,
    status_filter: str = Query("active", alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PatientPathwayListResponse:
    """Listar pathways nos quais o paciente está atualmente inscrito.

    Retorna todos os pathways do paciente incluindo estado atual
    e último progresso registrado.

    Sprint 1: reads enrollments from the persistent
    ``pathway_enrollment.get_patient_pathways`` service (Postgres-backed).
    """
    all_pathways = await get_patient_pathways(db, mpi_id, status_filter=status_filter)
    total = len(all_pathways)
    paginated = all_pathways[offset : offset + limit]
    items = [await _to_patient_pathway_schema(db, pp) for pp in paginated]
    return PatientPathwayListResponse(items=items, total=total)


# ===========================================================================
# POST /patients/{mpi_id}/pathways — Enroll patient
# ===========================================================================


@router.post(
    "/patients/{mpi_id}/pathways",
    response_model=PatientPathwaySchema,
    status_code=status.HTTP_201_CREATED,
)
async def enroll_patient_in_pathway(
    mpi_id: str,
    body: EnrollPatientRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PatientPathwaySchema:
    """Inscrever paciente em um pathway clínico.

    Dispara a avaliação inicial dos critérios e posiciona o paciente
    no estado inicial do pathway.

    M4: Validates pathway existence via new TrilhasEngine (YAML-based)
    before enrolling.
    Sprint 1: enrollment is persisted via
    ``intensicare.services.pathway_enrollment.enroll_patient``
    (Postgres-backed, replaces the deprecated in-memory PathwayStore).
    """
    engine = _get_engine()

    # ── Try new TrilhasEngine for pathway validation ──
    if engine is not None:
        pdef = engine.get_pathway(body.pathway_id)
        if pdef is not None:
            logger.info(
                "TrilhasEngine validated pathway %d (%s); enrolling via persistent service",
                body.pathway_id,
                pdef.name,
            )
        else:
            logger.warning(
                "Pathway %d not found in TrilhasEngine; enrolling via persistent "
                "service catalog (pathways table) anyway",
                body.pathway_id,
            )
    else:
        logger.warning(
            "TrilhasEngine unavailable; enrolling via persistent service "
            "catalog (pathways table) only"
        )

    # ── Actual enrollment always goes through the persistent service ──
    result = await enroll_patient(
        db,
        mpi_id=mpi_id,
        pathway_id=body.pathway_id,
        encounter_id=body.encounter_id,
        bed_id=body.bed_id,
        unit=body.unit,
        initial_criteria=body.initial_criteria,
        enrolled_by=current_user.username,
    )

    if result.error:
        if "não encontrado" in result.error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.error,
            )
        if "já está inscrito" in result.error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=result.error,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error,
        )

    # ── Run new engine evaluation as a validation pass (non-blocking) ──
    if engine is not None and body.initial_criteria:
        try:
            patient_data = _criteria_to_patient_data(body.initial_criteria)
            if patient_data:
                alerts = await engine.evaluate(mpi_id, patient_data)
                if alerts:
                    logger.info(
                        "TrilhasEngine produced %d alert(s) on enrollment for mpi=%s pathway=%d",
                        len(alerts),
                        mpi_id,
                        body.pathway_id,
                    )
        except Exception as exc:
            _log_evaluation_pass_failure(
                exc,
                phase="enrollment",
                mpi_id=mpi_id,
                pathway_id=body.pathway_id,
            )

    # Fetch the created enrollment to build the full response.
    # result.error was checked above (and raises on any failure), so on this
    # path enroll_patient's success branch always set patient_pathway_id.
    enrollment = await _find_enrollment(db, mpi_id, result.patient_pathway_id)  # type: ignore[arg-type]
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao recuperar inscrição recém-criada.",
        )
    return await _to_patient_pathway_schema(db, enrollment)


# ===========================================================================
# PUT /patients/{mpi_id}/pathways/{patient_pathway_id}/criteria
# ===========================================================================


@router.put(
    "/patients/{mpi_id}/pathways/{patient_pathway_id}/criteria",
    response_model=PatientPathwaySchema,
)
async def update_pathway_criteria(
    mpi_id: str,
    patient_pathway_id: int,
    body: UpdateCriteriaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PatientPathwaySchema:
    """Atualizar avaliação dos critérios de um pathway.

    Atualiza a avaliação dos critérios para uma inscrição de pathway
    específica. Pode disparar transição de estado se todos os critérios
    forem atendidos.

    M4: Runs new TrilhasEngine declarative evaluation as a validation pass
    before applying criteria.
    Sprint 1: criteria application/state transition is persisted via
    ``intensicare.services.pathway_enrollment.evaluate_criteria``
    (Postgres-backed, replaces the deprecated in-memory PathwayStore).
    """
    # Verify enrollment exists before evaluating
    enrollment = await _find_enrollment(db, mpi_id, patient_pathway_id)
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inscrição de pathway {patient_pathway_id} não encontrada "
            f"para o paciente {mpi_id}.",
        )

    if enrollment.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Inscrição de pathway não está ativa "
            f"(status: {enrollment.get('status')}). "
            f"Apenas pathways ativos podem ter critérios atualizados.",
        )

    engine = _get_engine()

    # ── Run new TrilhasEngine evaluation as a validation pass (non-blocking) ──
    if engine is not None:
        try:
            patient_data = _criteria_to_patient_data(body.criteria)
            if patient_data:
                alerts = await engine.evaluate(mpi_id, patient_data)
                if alerts:
                    logger.info(
                        "TrilhasEngine produced %d alert(s) on criteria update for mpi=%s pp_id=%d",
                        len(alerts),
                        mpi_id,
                        patient_pathway_id,
                    )
                else:
                    logger.debug(
                        "TrilhasEngine evaluation pass: 0 alerts for mpi=%s pp_id=%d",
                        mpi_id,
                        patient_pathway_id,
                    )
        except Exception as exc:
            _log_evaluation_pass_failure(
                exc,
                phase="criteria update",
                mpi_id=mpi_id,
                patient_pathway_id=patient_pathway_id,
            )
    else:
        logger.warning(
            "TrilhasEngine unavailable; evaluating criteria via persistent "
            "service only (no declarative validation pass)"
        )

    # ── Actual criteria update always goes through the persistent service ──
    await evaluate_criteria(
        db,
        mpi_id=mpi_id,
        patient_pathway_id=patient_pathway_id,
        criteria_updates=body.criteria,
    )

    # Fetch updated enrollment after criteria evaluation
    enrollment = await _find_enrollment(db, mpi_id, patient_pathway_id)
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao recuperar inscrição após atualização.",
        )
    return await _to_patient_pathway_schema(db, enrollment)


# ===========================================================================
# GET /patients/{mpi_id}/pathways/{patient_pathway_id}/progress
# ===========================================================================


@router.get(
    "/patients/{mpi_id}/pathways/{patient_pathway_id}/progress",
    response_model=PathwayProgressSchema,
)
async def get_pathway_progress_endpoint(
    mpi_id: str,
    patient_pathway_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PathwayProgressSchema:
    """Consultar progresso do paciente em um pathway específico.

    Retorna o progresso detalhado incluindo estado atual,
    histórico de transições, critérios avaliados e tendência.

    Sprint 1: reads from
    ``intensicare.services.pathway_enrollment.get_pathway_progress``
    (Postgres-backed, replaces the deprecated in-memory PathwayStore).
    """
    progress = await get_pathway_progress(db, mpi_id, patient_pathway_id)

    # Fetch the enrollment once — used both for the not-found check and to
    # resolve the pathway definition (state/criteria metadata) below.
    enrollment = await _find_enrollment(db, mpi_id, patient_pathway_id)

    # Detect not-found: the service returns a stub with Unknown name
    if not progress.current_state or progress.pathway_name == "Desconhecido":
        # Double-check: only raise 404 if enrollment truly doesn't exist
        if enrollment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inscrição de pathway {patient_pathway_id} não encontrada "
                f"para o paciente {mpi_id}.",
            )

    pathway_flat: dict[str, Any] | None = None
    if enrollment is not None:
        repo = PathwayRepository(db)
        pathway_orm = await repo.get_pathway(enrollment["pathway_id"])
        if pathway_orm is not None:
            pathway_flat = _pathway_orm_to_flat_dict(pathway_orm)

    # Resolve current state by ID from the enrollment's pathway
    current_state_def = _resolve_current_state(pathway_flat, progress.current_state)

    # Merge criteria with pathway definitions for category/unit/normal_range
    criteria_schemas = _resolve_progress_criteria(pathway_flat, progress.criteria)

    return PathwayProgressSchema(
        patient_pathway_id=progress.patient_pathway_id,
        mpi_id=progress.mpi_id,
        pathway_name=progress.pathway_name,
        current_state=PathwayStateSchema(**current_state_def),
        criteria_summary=progress.criteria_summary,
        criteria=criteria_schemas,
        state_history=progress.state_history,
        trend=progress.trend,
        last_evaluated_at=_parse_dt(progress.last_evaluated_at),
        recommendation=progress.recommendation,
    )
