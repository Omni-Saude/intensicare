"""Pydantic schemas for clinical form submissions (RASS, CAM-ICU, BPS/NRS)."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ClinicalFormSubmission(BaseModel):
    """Request body for submitting a clinical assessment form.

    Accepts frontend camelCase field names (formId, mpiId) via validation_alias,
    while keeping backend-native names (form_type, patient_mpi_id) internally.
    """

    form_type: str = Field(
        ...,
        validation_alias="formId",  # aceita "formId" do frontend
        description="Form type: rass | cam-icu | bps-nrs",
    )
    patient_mpi_id: str = Field(
        ...,
        min_length=1,
        validation_alias="mpiId",  # aceita "mpiId" do frontend
        description="Patient MPI identifier",
    )
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Form-specific data payload (e.g., score, note)",
    )


class ClinicalFormResponse(BaseModel):
    """Response returned after a clinical form is recorded."""

    id: str = Field(..., description="UUID of the recorded submission")
    status: str = Field(default="recorded", description="Submission status")
    recorded_at: datetime = Field(..., description="Timestamp of recording (UTC)")
