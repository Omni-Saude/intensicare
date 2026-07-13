"""Pydantic schemas for Documentation / Billing API.

OpenAPI contract — documentacao endpoints.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Documentacao — single record response
# ---------------------------------------------------------------------------


class DocumentacaoSchema(BaseModel):
    """Full documentation record returned by the API.

    Maps to the OpenAPI Documentacao schema.
    """

    id: int
    mpi_id: str
    type: str = Field(..., description="Document type: evolucao, prescricao, exame, procedimento")
    description: str = Field(..., description="Document description / content summary")
    glosa_status: str = Field(
        default="pendente",
        description="Glosa status: pendente, em_analise, glosado, liberado, recorrido",
    )
    glosa_motivo: str | None = Field(None, description="Reason for glosa (when glosado)")
    glosa_valor: float | None = Field(None, description="Glosa amount in BRL (R$)")
    data_documento: datetime = Field(..., description="Date/time of the clinical document")
    data_registro: datetime | None = Field(None, description="Date/time the record was registered")
    profissional: str | None = Field(None, description="Healthcare professional responsible")
    observacoes: str | None = Field(None, description="Additional observations")
    created_at: datetime | None = Field(None, description="Record creation timestamp")


# ---------------------------------------------------------------------------
# DocumentacaoCreate — request body for POST
# ---------------------------------------------------------------------------


class DocumentacaoCreate(BaseModel):
    """Request body for creating a new documentation record.

    glosa_status defaults to 'pendente' on creation.
    """

    type: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Document type: evolucao, prescricao, exame, procedimento",
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=512,
        description="Document description / content summary",
    )
    data_documento: datetime = Field(..., description="Date/time of the clinical document")
    profissional: str | None = Field(
        None, max_length=255, description="Healthcare professional responsible"
    )
    observacoes: str | None = Field(None, max_length=1024, description="Additional observations")


# ---------------------------------------------------------------------------
# DocumentacaoListResponse — paginated list (AUDIT-007 pattern)
# ---------------------------------------------------------------------------


class DocumentacaoListResponse(BaseModel):
    """Paginated list of documentation records.

    Follows AUDIT-007 pattern: items list + total count.
    """

    items: list[DocumentacaoSchema] = Field(default_factory=list)
    total: int = 0


# ---------------------------------------------------------------------------
# GlosaStatusUpdate — update glosa status + motivo
# ---------------------------------------------------------------------------


class GlosaStatusUpdate(BaseModel):
    """Request body for updating the glosa status of a documentation record.

    Used by auditors to transition glosa_status and record the reason.
    """

    status: str = Field(
        ...,
        description="New glosa status: pendente, em_analise, glosado, liberado, recorrido",
    )
    motivo: str | None = Field(
        None, max_length=512, description="Reason for the status change (especially for glosado)"
    )
