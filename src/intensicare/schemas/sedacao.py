"""Pydantic schemas for Sedation Monitoring API.

GET /patients/{mpi_id}/sedation (current assessment)
GET /patients/{mpi_id}/sedation/history (paginated history)
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CAMICUFeaturesSchema(BaseModel):
    """CAM-ICU feature details for delirium screening."""

    feature_1_acute_onset: bool | None = Field(
        None, description="Feature 1: Acute onset or fluctuating course"
    )
    feature_2_inattention: bool | None = Field(
        None, description="Feature 2: Inattention"
    )
    feature_3_altered_loc: bool | None = Field(
        None, description="Feature 3: Altered level of consciousness (current RASS != 0)"
    )
    feature_4_disorganized: bool | None = Field(
        None, description="Feature 4: Disorganized thinking"
    )
    rass_at_assessment: int | None = Field(
        None, ge=-5, le=4, description="RASS score at the time of CAM-ICU assessment"
    )


class SedationAssessmentSchema(BaseModel):
    """Individual sedation assessment record."""

    id: int = Field(..., description="Assessment unique identifier")
    mpi_id: str = Field(..., description="Patient MPI identifier")

    rass_score: int | None = Field(
        None, ge=-5, le=4, description="Richmond Agitation-Sedation Scale (-5 to +4)"
    )
    rass_label: str | None = Field(
        None, description="Human-readable RASS label (e.g. Sonolento, Agitado)"
    )

    bps_score: int | None = Field(
        None, ge=3, le=12, description="Behavioral Pain Scale (3–12)"
    )
    nrs_score: int | None = Field(
        None, ge=0, le=10, description="Numeric Rating Scale (0–10)"
    )

    cam_icu_positive: bool | None = Field(
        None, description="CAM-ICU positive for delirium"
    )
    cam_icu_features: dict[str, Any] | None = Field(
        None, description="CAM-ICU feature details"
    )

    current_sedation: str | None = Field(
        None, description="Current sedation infusion (e.g. Propofol 20mL/h)"
    )

    assessed_by: str = Field(..., description="Healthcare professional who performed the assessment")
    assessed_at: datetime = Field(..., description="Assessment timestamp (UTC)")
    notes: str | None = Field(None, max_length=512, description="Additional clinical notes")


class SedationAssessmentListResponse(BaseModel):
    """Paginated response for sedation history endpoint."""

    data: list[SedationAssessmentSchema] = Field(
        default_factory=list, description="List of sedation assessments"
    )
    total: int = Field(..., ge=0, description="Total records available")
    limit: int = Field(..., ge=1, le=500, description="Limit applied")
    offset: int = Field(..., ge=0, description="Offset applied")
