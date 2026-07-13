"""Clinical Notes / Evolution API Router — SBAR-structured endpoints.

3 endpoints conforme contrato OpenAPI:
  GET    /patients/{mpi_id}/evolucoes  — List patient evolutions
  POST   /patients/{mpi_id}/evolucoes  — Create a new evolution
  GET    /evolucoes/{id}               — Get a single evolution
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from intensicare.auth.dependencies import get_current_user
from intensicare.models.user import User
from intensicare.schemas.evolucoes import (
    EvolucaoCreate,
    EvolucaoListResponse,
    EvolucaoSchema,
    EvolucaoSectionSchema,
    EvolucaoTemplateSchema,
)
from intensicare.services.domain_evolucoes import (
    EvolutionRecord,
    EvolutionSection,
    EvolutionTemplate,
    create_evolution,
    get_evolution,
    list_evolutions,
)

router = APIRouter(prefix="/api/v1", tags=["evolucoes"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_iso_to_datetime(iso_str: str | None) -> datetime | None:
    """Parse ISO-8601 string to datetime, returning None on empty/failure."""
    if not iso_str:
        return None
    try:
        return datetime.fromisoformat(iso_str)
    except (ValueError, TypeError):
        return None


def _section_to_dict(section: EvolutionSection) -> dict:
    """Serialize an EvolutionSection dataclass to a plain dict."""
    return {
        "section_key": section.section_key,
        "section_label": section.section_label,
        "content": section.content,
        "order": section.order,
    }


def _template_to_schema(template: EvolutionTemplate) -> EvolucaoTemplateSchema:
    """Map a domain EvolutionTemplate to an EvolucaoTemplateSchema."""
    return EvolucaoTemplateSchema(
        id=template.id,
        role=template.role,
        name=template.name,
        sections=template.sections,
        definition_version=template.definition_version,
        active=template.active,
        created_at=datetime.now(timezone.utc),
    )


def _to_evolution_response(
    record: EvolutionRecord,
    template: EvolutionTemplate | None = None,
) -> EvolucaoSchema:
    """Map a domain EvolutionRecord to an EvolucaoSchema."""
    sections_dict = [_section_to_dict(s) for s in record.sections]
    sections_schemas = [
        EvolucaoSectionSchema(
            section_key=s.section_key,
            section_label=s.section_label,
            content=s.content,
            order=s.order,
        )
        for s in record.sections
    ]

    return EvolucaoSchema(
        id=record.id,
        mpi_id=record.mpi_id,
        template_id=record.template_id,
        type=record.type,
        author=record.author,
        author_role=record.author_role,
        sections=sections_dict,
        content_hash=record.content_hash,
        previous_id=record.previous_id,
        status=record.status,
        created_at=_parse_iso_to_datetime(record.created_at),
        updated_at=_parse_iso_to_datetime(record.updated_at),
        template=_template_to_schema(template) if template else None,
        sections_rel=sections_schemas if sections_schemas else None,
    )


# ---------------------------------------------------------------------------
# GET /patients/{mpi_id}/evolucoes — List patient evolutions
# ---------------------------------------------------------------------------


@router.get(
    "/patients/{mpi_id}/evolucoes",
    response_model=EvolucaoListResponse,
)
async def list_patient_evolutions(
    mpi_id: str,
    type: str | None = Query(
        None,
        alias="type",
        description="Filter by evolution type: admissao, diaria, alta, obito, intercorrencia",
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
) -> EvolucaoListResponse:
    """List clinical evolutions for a patient.

    Returns {items, total} following the standard pattern.
    Supports optional type filter and pagination.
    """
    result = list_evolutions(
        mpi_id=mpi_id,
        type=type,
        limit=limit,
        offset=offset,
    )

    return EvolucaoListResponse(
        items=[_to_evolution_response(r) for r in result.items],
        total=result.total,
    )


# ---------------------------------------------------------------------------
# POST /patients/{mpi_id}/evolucoes — Create a new evolution
# ---------------------------------------------------------------------------


@router.post(
    "/patients/{mpi_id}/evolucoes",
    response_model=EvolucaoSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_patient_evolution(
    mpi_id: str,
    body: EvolucaoCreate,
    current_user: User = Depends(get_current_user),
) -> EvolucaoSchema:
    """Create a new clinical evolution (SBAR-structured note).

    Validates template existence, SBAR section completeness, and
    author role validity. Computes SHA-256 content hash for non-repudiation.

    Returns 409 on validation errors.
    """
    try:
        record = create_evolution(
            mpi_id=mpi_id,
            type=body.type,
            template_id=body.template_id,
            author=body.author or current_user.username,
            author_role=body.author_role,
            sections=body.sections,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return _to_evolution_response(record)


# ---------------------------------------------------------------------------
# GET /evolucoes/{evolution_id} — Get a single evolution
# ---------------------------------------------------------------------------


@router.get(
    "/evolucoes/{evolution_id}",
    response_model=EvolucaoSchema,
)
async def get_single_evolution(
    evolution_id: int,
    current_user: User = Depends(get_current_user),
) -> EvolucaoSchema:
    """Get a single clinical evolution by ID.

    Returns 404 if not found.
    """
    record = get_evolution(evolution_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evolution {evolution_id} not found",
        )

    return _to_evolution_response(record)
