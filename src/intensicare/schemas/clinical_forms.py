"""Pydantic schemas for clinical form submissions (RASS, CAM-ICU, BPS/NRS)."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ClinicalFormSubmission(BaseModel):
    """Request body for submitting a clinical assessment form."""

    form_type: str = Field(
        ...,
        description="Form type: rass | cam-icu | bps-nrs",
    )
    patient_mpi_id: str = Field(..., min_length=1, description="Patient MPI identifier")
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Form-specific data payload (e.g., score, note)",
    )


class ClinicalFormResponse(BaseModel):
    """Response returned after a clinical form is recorded."""

    id: str = Field(..., description="UUID of the recorded submission")
    status: str = Field(default="recorded", description="Submission status")
    recorded_at: datetime = Field(..., description="Timestamp of recording (UTC)")
