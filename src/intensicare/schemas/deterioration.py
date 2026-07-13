"""Pydantic schemas for Clinical Deterioration API.

OpenAPI contract — deterioration assessment endpoints.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# DeteriorationCriteria
# ---------------------------------------------------------------------------


class DeteriorationCriteriaSchema(BaseModel):
    """A single clinical deterioration criterion evaluation."""

    domain: str = Field(
        ...,
        description="Clinical domain: respiratory, hemodynamic, sepsis, neurologic, renal",
    )
    name: str = Field(..., description="Criterion name (ex: 'Queda de SpO2 com aumento de FiO2')")
    status: str = Field(
        ...,
        description="Status: normal, alert (attention), critical (immediate intervention)",
    )
    value: str | None = Field(None, description="Current observed value")
    threshold: str | None = Field(None, description="Trigger threshold")
    alert_id: str | None = Field(
        None, description="Associated alert ID (ex: ALERT-RESP-DETERIORATION-02)"
    )


# ---------------------------------------------------------------------------
# DeteriorationScore — single assessment response
# ---------------------------------------------------------------------------


class DeteriorationScoreSchema(BaseModel):
    """Single deterioration assessment response.

    Maps to the OpenAPI DeteriorationScore contract.
    """

    id: int
    mpi_id: str
    score: str = Field(
        ...,
        description="Categorical score: 0, 1+, 1-, 3+, 3-",
    )
    trend: str = Field(
        ...,
        description="Trend vs previous assessment: improving, stable, worsening, none",
    )
    criteria: list[DeteriorationCriteriaSchema] = Field(
        default_factory=list,
        description="Evaluated criteria across all domains",
    )
    domains_affected: int = Field(
        default=0,
        ge=0,
        description="Number of domains with at least 1 criterion in alert or critical",
    )
    recommendation: str | None = Field(
        None,
        description="Clinical recommendation (PT-BR)",
    )
    assessed_at: datetime
    assessed_by: str | None = Field(
        None, description="User or system that generated the assessment"
    )


# ---------------------------------------------------------------------------
# History list response (AUDIT-007 pattern)
# ---------------------------------------------------------------------------


class DeteriorationHistoryResponse(BaseModel):
    """Paginated list of deterioration assessments.

    Follows AUDIT-007 pattern: items list + total count.
    """

    items: list[DeteriorationScoreSchema] = Field(default_factory=list)
    total: int = 0
