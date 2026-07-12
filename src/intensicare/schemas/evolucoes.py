"""Pydantic schemas for Clinical Notes / Evolution API.

OpenAPI contract — evoluções clínicas (admissão, diária, alta, óbito,
intercorrência) with SBAR-structured sections.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# EvolucaoSection — individual SBAR section
# ---------------------------------------------------------------------------


class EvolucaoSectionSchema(BaseModel):
    """A single SBAR section within a clinical evolution."""

    id: int | None = Field(None, description="Section ID (auto-generated)")
    section_key: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Section key: situation, background, assessment, recommendation",
    )
    section_label: str = Field(
        ..., min_length=1, max_length=64, description="Human-readable section label"
    )
    content: str = Field(..., min_length=1, max_length=4096, description="Section text content")
    order: int = Field(..., ge=0, description="Display order within the evolution")

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# EvolucaoTemplate — template definition
# ---------------------------------------------------------------------------


class EvolucaoTemplateSchema(BaseModel):
    """Pre-defined template for SBAR-structured evolution notes."""

    id: str = Field(
        ..., min_length=1, max_length=32, description="Template key (ex: 'medico_diaria')"
    )
    role: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Clinical role: medico, enfermeiro, fisioterapeuta, etc.",
    )
    name: str = Field(..., min_length=1, max_length=128, description="Human-readable template name")
    sections: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Array of SBAR section definitions with field definitions",
    )
    definition_version: str = Field(
        ..., min_length=1, max_length=16, description="Template version (ex: '1.0.0')"
    )
    active: bool = Field(True, description="Whether this template is active")
    created_at: datetime | None = Field(None, description="Template creation timestamp")

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Evolucao — full evolution response
# ---------------------------------------------------------------------------


class EvolucaoSchema(BaseModel):
    """Complete clinical evolution note (response)."""

    id: int | None = Field(None, description="Evolution ID (auto-generated)")
    mpi_id: str = Field(
        ..., min_length=1, max_length=64, description="Master Patient Index identifier"
    )
    template_id: str = Field(
        ..., min_length=1, max_length=32, description="FK to evolucao_templates.id"
    )
    type: str = Field(
        ...,
        min_length=1,
        max_length=16,
        description="Evolution type: admissao, diaria, alta, obito, intercorrencia",
    )
    author: str = Field(
        ..., min_length=1, max_length=255, description="Professional who authored the note"
    )
    author_role: str = Field(
        ..., min_length=1, max_length=32, description="Clinical role of the author"
    )
    sections: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Filled SBAR sections",
    )
    content_hash: str | None = Field(
        None, min_length=1, max_length=64, description="SHA-256 hash for non-repudiation"
    )
    previous_id: int | None = Field(None, description="FK to previous version (amendment chain)")
    status: str = Field(
        "final", min_length=1, max_length=16, description="Status: draft, final, amended"
    )
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")

    # Optional nested resources
    template: EvolucaoTemplateSchema | None = Field(
        None, description="Associated template (when expanded)"
    )
    sections_rel: list[EvolucaoSectionSchema] | None = Field(
        None, description="Normalized sections (when expanded)"
    )

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# EvolucaoCreate — request body for creating an evolution
# ---------------------------------------------------------------------------


class EvolucaoCreate(BaseModel):
    """Request body for creating a new clinical evolution note."""

    template_id: str = Field(..., min_length=1, max_length=32, description="Template key to use")
    type: str = Field(
        ...,
        min_length=1,
        max_length=16,
        description="Evolution type: admissao, diaria, alta, obito, intercorrencia",
        examples=["diaria"],
    )
    author: str = Field(
        ..., min_length=1, max_length=255, description="Professional who authored the note"
    )
    author_role: str = Field(
        ..., min_length=1, max_length=32, description="Clinical role of the author"
    )
    sections: list[dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="Filled SBAR sections (Situation, Background, Assessment, Recommendation)",
    )
    status: str = Field(
        "final",
        min_length=1,
        max_length=16,
        description="Status: draft, final",
        examples=["final"],
    )

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# EvolucaoListResponse — paginated list
# ---------------------------------------------------------------------------


class EvolucaoListResponse(BaseModel):
    """Paginated list of clinical evolution notes.

    Follows the standard pattern: items list + total count.
    """

    items: list[EvolucaoSchema] = Field(default_factory=list)
    total: int = Field(0, ge=0, description="Total number of records available")
