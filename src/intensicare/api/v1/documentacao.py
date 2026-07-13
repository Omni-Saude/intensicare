"""Documentation / Billing API Router — Glosa Zero endpoints.

2 endpoints conforme contrato OpenAPI (PASSO 2.2):
  GET    /patients/{mpi_id}/documentacao            — List (filter glosa_status)
  POST   /patients/{mpi_id}/documentacao            — Create
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, status

from intensicare.auth.dependencies import get_current_user
from intensicare.models.user import User
from intensicare.schemas.documentacao import (
    DocumentacaoCreate,
    DocumentacaoListResponse,
    DocumentacaoSchema,
)
from intensicare.services.domain_documentacao import (
    DocumentacaoRecord,
    create_documentacao,
    list_documentacao,
)

router = APIRouter(prefix="/api/v1", tags=["documentacao"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _record_to_schema(record: DocumentacaoRecord) -> DocumentacaoSchema:
    """Convert a domain DocumentacaoRecord to a Pydantic DocumentacaoSchema."""
    return DocumentacaoSchema(
        id=record.id or 0,
        mpi_id=record.mpi_id,
        type=record.type,
        description=record.description,
        glosa_status=record.glosa_status,
        glosa_motivo=record.glosa_motivo,
        glosa_valor=float(record.glosa_valor) if record.glosa_valor else None,
        data_documento=datetime.fromisoformat(record.data_documento)
        if record.data_documento
        else datetime.now(timezone.utc),
        data_registro=datetime.fromisoformat(record.data_registro)
        if record.data_registro
        else None,
        profissional=record.profissional,
        observacoes=record.observacoes,
        created_at=None,
    )


# ---------------------------------------------------------------------------
# GET /patients/{mpi_id}/documentacao — List documentation
# ---------------------------------------------------------------------------


@router.get(
    "/patients/{mpi_id}/documentacao",
    response_model=DocumentacaoListResponse,
)
async def list_documentacao_endpoint(
    mpi_id: str,
    glosa_status: str | None = Query(
        None,
        description="Filter by glosa status: pendente, em_analise, glosado, liberado, recorrido",
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
) -> DocumentacaoListResponse:
    """List documentation records for a patient.

    Supports optional filter by glosa_status and pagination.
    Follows AUDIT-007 pattern: {items, total}.
    """
    result = list_documentacao(
        mpi_id=mpi_id,
        glosa_status=glosa_status,
        limit=limit,
        offset=offset,
    )

    return DocumentacaoListResponse(
        items=[_record_to_schema(r) for r in result.items],
        total=result.total,
    )


# ---------------------------------------------------------------------------
# POST /patients/{mpi_id}/documentacao — Create documentation
# ---------------------------------------------------------------------------


@router.post(
    "/patients/{mpi_id}/documentacao",
    response_model=DocumentacaoSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_documentacao_endpoint(
    mpi_id: str,
    body: DocumentacaoCreate,
    current_user: User = Depends(get_current_user),
) -> DocumentacaoSchema:
    """Create a new documentation record for a patient.

    The glosa_status is initialized as 'pendente'.
    """
    record = create_documentacao(
        mpi_id=mpi_id,
        type=body.type,
        description=body.description,
        data_documento=body.data_documento.isoformat() if body.data_documento else "",
        profissional=body.profissional or current_user.username,
        observacoes=body.observacoes,
    )

    return _record_to_schema(record)
