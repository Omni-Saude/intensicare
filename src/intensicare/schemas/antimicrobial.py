"""Pydantic schemas for Antimicrobial Stewardship API.

OpenAPI contract — antimicrobial assessment endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Criterion
# ---------------------------------------------------------------------------


class AntimicrobialCriterionSchema(BaseModel):
    """A single antimicrobial stewardship criterion evaluation."""

    id: str = Field(..., description="Criterion ID (ex: crit-001)")
    name: str = Field(..., description="Criterion name (ex: 'Duração > 7 dias')")
    category: str = Field(
        ..., description="Category: duracao, espectro, dose, cvc, candidemia, culturas, cap_covid"
    )
    description: str = Field(..., description="Criterion description")
    met: bool = Field(
        ..., description="True if this non-conformity criterion is met (identified as an issue)"
    )


# ---------------------------------------------------------------------------
# Assessment — request & response
# ---------------------------------------------------------------------------


class CreateAntimicrobialAssessmentSchema(BaseModel):
    """Request body for creating a new antimicrobial assessment."""

    mpi_id: str = Field(..., min_length=1, max_length=64)
    criteria_met: list[str] = Field(
        default_factory=list,
        description="List of criterion IDs that are met (non-conformities identified)",
    )
    assessed_by: str = Field(
        default="system",
        description="Identifier of the user or system performing the assessment",
    )


class AntimicrobialAssessmentResponse(BaseModel):
    """Single antimicrobial assessment response.

    Maps to the OpenAPI AntimicrobialAssessment contract.
    """

    id: int
    mpi_id: str
    criteria: list[AntimicrobialCriterionSchema]
    score: int = Field(..., ge=0, le=12, description="Total non-conformities (0-12)")
    severity: str = Field(
        ..., description="Severity band: NEUTRO, AMARELO, VERMELHO"
    )
    recommendation: str = Field(..., description="Clinical recommendation (PT-BR)")
    assessed_at: datetime
    assessed_by: str


# ---------------------------------------------------------------------------
# List response (AUDIT-007 pattern)
# ---------------------------------------------------------------------------


class AntimicrobialAssessmentListResponse(BaseModel):
    """Paginated list of antimicrobial assessments.

    Follows AUDIT-007 pattern: items list + total count.
    """

    items: list[AntimicrobialAssessmentResponse] = Field(default_factory=list)
    total: int = 0


# ---------------------------------------------------------------------------
# Criteria catalog
# ---------------------------------------------------------------------------


class CriterionCatalogItem(BaseModel):
    """A single item in the criteria catalog (no evaluation — definition only)."""

    id: str
    name: str
    category: str
    description: str


class AntimicrobialCriteriaCatalogResponse(BaseModel):
    """Response containing the full antimicrobial criteria catalog."""

    criteria: list[CriterionCatalogItem] = Field(default_factory=list)
    categories: dict[str, str] = Field(
        default_factory=dict,
        description="Category key → label map",
    )
    total: int = 0
