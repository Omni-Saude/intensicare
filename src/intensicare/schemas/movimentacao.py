"""Pydantic schemas for Patient Movement / ADT API.

OpenAPI contract — docs/contracts/movimentacao-openapi.yaml.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# PatientMovement — request & response
# ---------------------------------------------------------------------------


class RegisterMovementRequest(BaseModel):
    """Request body for POST /patients/{mpi_id}/movements."""

    mpi_id: str = Field(..., min_length=1, max_length=64, description="Patient MPI identifier")
    type: str = Field(..., description="Movement type: admission, transfer, discharge")
    from_unit: str | None = Field(
        None, max_length=128, description="Origin unit (null on admission)"
    )
    to_unit: str | None = Field(
        None, max_length=128, description="Destination unit (null on discharge)"
    )
    from_bed: str | None = Field(None, max_length=32, description="Origin bed (null on admission)")
    to_bed: str | None = Field(
        None, max_length=32, description="Destination bed (null on discharge)"
    )
    timestamp: datetime = Field(..., description="Date/time the movement occurred")
    notes: str | None = Field(None, max_length=1024, description="Clinical notes")
    registered_by: str | None = Field(
        None, max_length=255, description="Professional who registered the movement"
    )


class PatientMovementSchema(BaseModel):
    """Single patient movement record — maps to OpenAPI PatientMovement."""

    id: int = Field(..., description="Unique movement identifier")
    mpi_id: str = Field(..., description="Patient MPI identifier")
    type: str = Field(..., description="Movement type: admission, transfer, discharge")
    from_unit: str | None = Field(None, description="Origin unit")
    to_unit: str | None = Field(None, description="Destination unit")
    from_bed: str | None = Field(None, description="Origin bed")
    to_bed: str | None = Field(None, description="Destination bed")
    timestamp: datetime = Field(..., description="Date/time the movement occurred")
    notes: str | None = Field(None, description="Clinical notes")
    registered_by: str | None = Field(None, description="Professional who registered")
    created_at: datetime = Field(..., description="Record creation timestamp")


class PatientMovementListResponse(BaseModel):
    """Paginated list of patient movements (follows AUDIT-007 pattern)."""

    movements: list[PatientMovementSchema] = Field(default_factory=list)
    total: int = 0


# ---------------------------------------------------------------------------
# Bed — grade de leitos
# ---------------------------------------------------------------------------


class BedSchema(BaseModel):
    """Single bed status record — maps to OpenAPI BedStatus."""

    id: str = Field(..., description="Bed identifier (ex: 'UTI-A-01')")
    unit: str = Field(..., description="Unit this bed belongs to")
    status: str = Field(..., description="Bed status: free, occupied, blocked, cleaning")
    current_patient_mpi_id: str | None = Field(None, description="MPI ID of occupying patient")
    last_updated: datetime = Field(..., description="Last status update timestamp")


class BedGridSummary(BaseModel):
    """Aggregated bed counts by status."""

    total: int = 0
    free: int = 0
    occupied: int = 0
    blocked: int = 0
    cleaning: int = 0


class BedGridResponse(BaseModel):
    """Full bed grid with status summary — maps to OpenAPI GET /beds response."""

    beds: list[BedSchema] = Field(default_factory=list)
    summary: BedGridSummary = Field(default_factory=BedGridSummary)


# ---------------------------------------------------------------------------
# AdmissionEpisode
# ---------------------------------------------------------------------------


class AdmissionEpisodeSchema(BaseModel):
    """A complete admission episode — maps to ADR-025 admission_episode projection."""

    id: int = Field(..., description="Unique episode identifier")
    mpi_id: str = Field(..., description="Patient MPI identifier")
    encounter_id: str = Field(
        ..., description="External encounter identifier (e.g., from AMH Gold)"
    )
    admission_date: datetime = Field(..., description="Admission date/time")
    discharge_date: datetime | None = Field(
        None, description="Discharge date/time (null if active)"
    )
    admission_type: str = Field(
        ..., description="Admission type: eletiva, urgencia, emergencia, transferencia"
    )
    status: str = Field(..., description="Episode status: active, discharged")


# ---------------------------------------------------------------------------
# PatientLocationCurrent
# ---------------------------------------------------------------------------


class PatientLocationCurrentSchema(BaseModel):
    """Current patient location — one row per admitted patient."""

    mpi_id: str = Field(..., description="Patient MPI identifier (primary key)")
    encounter_id: str = Field(..., description="Current admission episode identifier")
    unit: str = Field(..., description="Current unit (e.g., UTI-1)")
    bed_id: str | None = Field(None, description="Current bed (e.g., L-101)")
    specialty: str | None = Field(None, description="Responsible clinical specialty")
    admitted_to_unit_at: datetime | None = Field(
        None, description="When patient arrived at current unit"
    )
    last_movement_at: datetime | None = Field(None, description="Timestamp of most recent movement")
    source_cdc_offset: int | None = Field(
        None, description="CDC offset of the latest event applied"
    )
    updated_at: datetime = Field(..., description="Last update timestamp")


# ---------------------------------------------------------------------------
# DischargeSummary
# ---------------------------------------------------------------------------


class DischargeSummarySchema(BaseModel):
    """Discharge summary — one row per discharged encounter."""

    id: int = Field(..., description="Unique discharge summary identifier")
    encounter_id: str = Field(..., description="Admission episode identifier (unique)")
    mpi_id: str = Field(..., description="Patient MPI identifier")
    discharge_datetime: datetime = Field(..., description="Discharge date/time")
    discharge_type: str = Field(
        ...,
        description="domiciliar, transferencia_hospitalar, obito, alta_pedido, evasao",
    )
    destination: str | None = Field(None, description="Post-discharge destination")
    discharge_diagnosis: str | None = Field(None, description="CID-10 at discharge")
    follow_up_scheduled: bool = Field(default=False, description="Whether follow-up was scheduled")
    continuity_medication_prescribed: bool = Field(
        default=False, description="Medication continuity at discharge"
    )
    source_cdc_offset: int | None = Field(None, description="CDC offset of source event")
    created_at: datetime = Field(..., description="Record creation timestamp")
