"""Pydantic schemas for Prescription System API.

OpenAPI contract — prescricao-openapi.yaml
Supports ADR-026 (drug interaction safety) and ADR-027 (lifecycle state machine).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Prescription core schemas
# ---------------------------------------------------------------------------


class PrescriptionSchema(BaseModel):
    """Full prescription response (maps to OpenAPI Prescription contract)."""

    id: int
    mpi_id: str
    medication: str = Field(..., description="Medication name (ex: 'Meropenem')")
    dosage: str = Field(..., description="Dosage string (ex: '500mg', '1g')")
    route: str = Field(
        ...,
        description="Administration route: IV, PO, SC, IM, SN, IT, TOP, INAL",
    )
    frequency: str = Field(
        ...,
        description="QID, TID, BID, QD, QOD, PRN, continuous, or custom (ex: 8/8h)",
    )
    start_time: datetime
    end_time: datetime | None = None
    status: str = Field(
        ...,
        description="Lifecycle state: draft, active, completed, discontinued, suspended (ADR-027)",
    )
    version: int = Field(default=1, description="Optimistic locking version")
    prescribed_by: str = Field(..., description="Prescribing physician")
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PrescriptionCreate(BaseModel):
    """Request body for creating a new prescription (POST /patients/{mpi_id}/prescriptions)."""

    mpi_id: str = Field(..., min_length=1, max_length=64)
    medication: str = Field(..., min_length=1, max_length=255)
    dosage: str = Field(
        ..., min_length=1, max_length=64, description="ex: '500mg', '1g'"
    )
    route: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="IV, PO, SC, IM, SN, IT, TOP, INAL",
    )
    frequency: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="QID, TID, BID, QD, QOD, PRN, continuous, or custom",
    )
    start_time: datetime | None = Field(
        None, description="Optional — defaults to now if not provided"
    )
    prescribed_by: str = Field(
        ..., min_length=1, max_length=255, description="Prescribing physician identifier"
    )
    notes: str | None = Field(None, max_length=1024)


class PrescriptionUpdate(BaseModel):
    """Request body for updating a prescription (PUT /prescriptions/{id}).

    All fields optional — only provided fields are updated.
    Status transitions follow ADR-027 state machine rules.
    """

    dosage: str | None = Field(None, max_length=64)
    route: str | None = Field(
        None,
        max_length=32,
        description="IV, PO, SC, IM, SN, IT, TOP, INAL",
    )
    frequency: str | None = Field(None, max_length=32)
    status: str | None = Field(
        None,
        description="Target state: active, completed, discontinued, suspended",
    )
    notes: str | None = Field(None, max_length=1024)
    version: int | None = Field(
        None, description="Optimistic locking — must match current version"
    )


# ---------------------------------------------------------------------------
# List response (AUDIT-007 pattern)
# ---------------------------------------------------------------------------


class PrescriptionListResponse(BaseModel):
    """Paginated list of prescriptions.

    Follows AUDIT-007 pattern: items list + total count.
    """

    prescriptions: list[PrescriptionSchema] = Field(default_factory=list)
    total: int = 0


# ---------------------------------------------------------------------------
# State transition (ADR-027)
# ---------------------------------------------------------------------------


class PrescriptionStateTransition(BaseModel):
    """State transition request for the prescription state machine.

    Follows ADR-027: validates transitions, requires clinical justification
    for sensitive transitions (discontinued, suspended). Uses optimistic
    locking via version to prevent concurrent modification races.
    """

    to_status: str = Field(
        ...,
        description="Target state: active, completed, discontinued, suspended",
    )
    reason: str | None = Field(
        None,
        description="Clinical justification (required for discontinued, suspended)",
    )
    changed_by: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Clinician executing the transition",
    )
    version: int = Field(
        ...,
        description="Optimistic locking — must match current version to prevent race conditions",
    )


# ---------------------------------------------------------------------------
# Drug interaction alert (ADR-026)
# ---------------------------------------------------------------------------


class InteracaoAlertaSchema(BaseModel):
    """Drug interaction alert detected for a prescription.

    Severity levels (DMN versioned per ADR-0012):
    - contraindicated: absolute contraindication, hard stop
    - severe: serious risk, requires prescriber acknowledgment
    - moderate: caution, manageable with monitoring
    - minor: theoretical or low clinical relevance
    """

    id: int
    prescricao_id: int
    severity: str = Field(
        ...,
        description="contraindicated, severe, moderate, minor",
    )
    interaction_type: str = Field(
        ...,
        description="drug-drug, drug-allergy, drug-food, duplicate",
    )
    description: str = Field(..., max_length=512)
    resolved: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}
