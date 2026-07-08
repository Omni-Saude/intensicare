"""Care Pathways API Router — 6 endpoints for Trilhas Engine."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from intensicare.auth.dependencies import get_current_user
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
from intensicare.services.domain_trilhas_engine import (
    enroll_patient,
    evaluate_criteria,
    get_pathway_by_id,
    get_pathway_catalog,
    get_patient_pathways,
    get_pathway_progress,
)

router = APIRouter(prefix="/api/v1", tags=["pathways"])


# ===========================================================================
# Helpers
# ===========================================================================

def _to_pathway_schema(data: dict) -> PathwaySchema:
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


def _merge_criteria(
    criteria_defs: list[dict],
    evaluated: list[dict] | None = None,
) -> list[PathwayCriteriaSchema]:
    """Merge pathway criteria definitions with patient-evaluated values."""
    eval_map: dict[str, dict] = {}
    if evaluated:
        eval_map = {
            c["id"]: c
            for c in evaluated
            if c.get("id")
        }

    result: list[PathwayCriteriaSchema] = []
    for cd in criteria_defs:
        ev = eval_map.get(cd["id"], {})
        result.append(PathwayCriteriaSchema(
            id=cd["id"],
            name=cd["name"],
            category=cd.get("category", ""),
            description=cd.get("description"),
            unit=cd.get("unit"),
            normal_range=cd.get("normal_range"),
            alert_threshold=cd.get("alert_threshold"),
            met=ev.get("met"),
            value=ev.get("value"),
            evaluated_at=_parse_dt(ev.get("evaluated_at")),
        ))
    return result


def _to_patient_pathway_schema(pp: dict) -> PatientPathwaySchema:
    """Convert a patient pathway dict from the domain service to a schema."""
    pathway = get_pathway_by_id(pp["pathway_id"])
    if pathway is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pathway {pp['pathway_id']} não encontrado",
        )

    criteria_data: list[dict] = pp.get("criteria_data", [])
    criteria_schemas = _merge_criteria(
        pathway.get("criteria", []), criteria_data,
    )

    # Resolve current state definition from the pathway
    current_state_id = pp["current_state"]
    current_state_def: dict | None = None
    for s in pathway.get("states", []):
        if s["id"] == current_state_id:
            current_state_def = s
            break

    if current_state_def is None:
        current_state_def = {
            "id": current_state_id,
            "name": current_state_id,
            "order": 0,
        }

    return PatientPathwaySchema(
        id=pp["id"],
        mpi_id=pp["mpi_id"],
        pathway=_to_pathway_schema(pathway),
        current_state=PathwayStateSchema(**current_state_def),
        criteria=criteria_schemas,
        status=pp.get("status", "active"),
        severity=pp.get("severity"),
        enrolled_at=_parse_dt(pp["enrolled_at"]),
        enrolled_by=pp.get("enrolled_by"),
        completed_at=_parse_dt(pp.get("completed_at")),
        updated_at=_parse_dt(pp.get("updated_at")),
    )


def _find_enrollment(mpi_id: str, patient_pathway_id: int) -> dict | None:
    """Find a specific patient-pathway enrollment by its ID."""
    pathways = get_patient_pathways(mpi_id, status_filter="all")
    for pp in pathways:
        if pp["id"] == patient_pathway_id:
            return pp
    return None


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


# ===========================================================================
# GET /pathways — Catalog listing
# ===========================================================================

@router.get("/pathways", response_model=PathwayListResponse)
async def list_pathways(
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_user),
) -> PathwayListResponse:
    """Listar todas as vias de cuidado (pathways) disponíveis no catálogo.

    Retorna o catálogo de pathways clínicos configurados no sistema.
    Cada pathway define um conjunto de critérios e estados que guiam
    o acompanhamento do paciente.
    """
    catalog = get_pathway_catalog(active_only=active_only)
    items = [_to_pathway_schema(p) for p in catalog]
    return PathwayListResponse(items=items, total=len(items))


# ===========================================================================
# GET /pathways/{pathway_id} — Pathway detail with criteria
# ===========================================================================

@router.get("/pathways/{pathway_id}", response_model=PathwaySchema)
async def get_pathway(
    pathway_id: int,
    current_user: User = Depends(get_current_user),
) -> PathwaySchema:
    """Obter detalhes de um pathway com seus critérios e estados.

    Retorna o pathway completo incluindo a definição de estados
    possíveis e os critérios de avaliação associados.
    """
    pathway = get_pathway_by_id(pathway_id)
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
    current_user: User = Depends(get_current_user),
) -> PatientPathwayListResponse:
    """Listar pathways nos quais o paciente está atualmente inscrito.

    Retorna todos os pathways do paciente incluindo estado atual
    e último progresso registrado.
    """
    all_pathways = get_patient_pathways(mpi_id, status_filter=status_filter)
    total = len(all_pathways)
    paginated = all_pathways[offset : offset + limit]
    items = [_to_patient_pathway_schema(pp) for pp in paginated]
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
    current_user: User = Depends(get_current_user),
) -> PatientPathwaySchema:
    """Inscrever paciente em um pathway clínico.

    Dispara a avaliação inicial dos critérios e posiciona o paciente
    no estado inicial do pathway.
    """
    result = enroll_patient(
        mpi_id=mpi_id,
        pathway_id=body.pathway_id,
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

    # Fetch the created enrollment to build the full response
    enrollment = _find_enrollment(mpi_id, result.patient_pathway_id)
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao recuperar inscrição recém-criada.",
        )
    return _to_patient_pathway_schema(enrollment)


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
    current_user: User = Depends(get_current_user),
) -> PatientPathwaySchema:
    """Atualizar avaliação dos critérios de um pathway.

    Atualiza a avaliação dos critérios para uma inscrição de pathway
    específica. Pode disparar transição de estado se todos os critérios
    forem atendidos.
    """
    # Verify enrollment exists before evaluating
    enrollment = _find_enrollment(mpi_id, patient_pathway_id)
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

    evaluate_criteria(
        mpi_id=mpi_id,
        patient_pathway_id=patient_pathway_id,
        criteria_updates=body.criteria,
    )

    # Fetch updated enrollment after criteria evaluation
    enrollment = _find_enrollment(mpi_id, patient_pathway_id)
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao recuperar inscrição após atualização.",
        )
    return _to_patient_pathway_schema(enrollment)


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
    current_user: User = Depends(get_current_user),
) -> PathwayProgressSchema:
    """Consultar progresso do paciente em um pathway específico.

    Retorna o progresso detalhado incluindo estado atual,
    histórico de transições, critérios avaliados e tendência.
    """
    progress = get_pathway_progress(mpi_id, patient_pathway_id)

    # Detect not-found: the service returns a stub with Unknown name
    if not progress.current_state or progress.pathway_name == "Desconhecido":
        # Double-check: only raise 404 if enrollment truly doesn't exist
        enrollment = _find_enrollment(mpi_id, patient_pathway_id)
        if enrollment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inscrição de pathway {patient_pathway_id} não encontrada "
                       f"para o paciente {mpi_id}.",
            )

    # Resolve current state by ID from the enrollment's pathway
    current_state_def = _resolve_current_state(
        mpi_id, patient_pathway_id, progress.current_state,
    )

    # Merge criteria with pathway definitions for category/unit/normal_range
    criteria_schemas = _resolve_progress_criteria(
        mpi_id, patient_pathway_id, progress.criteria,
    )

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


def _resolve_current_state(
    mpi_id: str,
    patient_pathway_id: int,
    current_state_id: str,
) -> dict:
    """Look up state definition from the pathway the patient is enrolled in."""
    enrollment = _find_enrollment(mpi_id, patient_pathway_id)
    if enrollment:
        pathway = get_pathway_by_id(enrollment["pathway_id"])
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
    mpi_id: str,
    patient_pathway_id: int,
    evaluated: list[dict],
) -> list[PathwayCriteriaSchema]:
    """Merge progress criteria with pathway definitions for full metadata."""
    enrollment = _find_enrollment(mpi_id, patient_pathway_id)
    criteria_defs: list[dict] = []
    if enrollment:
        pathway = get_pathway_by_id(enrollment["pathway_id"])
        if pathway:
            criteria_defs = pathway.get("criteria", [])

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
                value=c.get("value"),
                evaluated_at=_parse_dt(c.get("evaluated_at")),
            )
            for c in evaluated
        ]

    return _merge_criteria(criteria_defs, evaluated)
