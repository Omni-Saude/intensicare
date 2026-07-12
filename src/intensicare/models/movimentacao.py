"""Patient Movement / ADT — models for patient movements, beds, and admission episodes.

Based on ADR-025 (MovimentacaoStateStore projection) and the OpenAPI contract
docs/contracts/movimentacao-openapi.yaml.
"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base

# ---------------------------------------------------------------------------
# PatientMovement — registro de admissão, transferência e alta
# ---------------------------------------------------------------------------


class PatientMovement(Base):
    """A single patient movement event: admission, transfer, or discharge.

    Maps to the OpenAPI PatientMovement schema. This is the canonical log
    of every patient location change. Queried by domain_movimentacao.py.
    """

    __tablename__ = "patient_movements"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, comment="Patient MPI identifier"
    )
    type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        comment="Movement type: admission, transfer, discharge",
    )
    from_unit: Mapped[str | None] = mapped_column(
        String(128), nullable=True, comment="Origin unit (null on admission)"
    )
    to_unit: Mapped[str | None] = mapped_column(
        String(128), nullable=True, comment="Destination unit (null on discharge)"
    )
    from_bed: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="Origin bed (null on admission)"
    )
    to_bed: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="Destination bed (null on discharge)"
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Date/time the movement occurred",
    )
    notes: Mapped[str | None] = mapped_column(String(1024), nullable=True, comment="Clinical notes")
    registered_by: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Professional who registered the movement"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        comment="Record creation timestamp",
    )


# ---------------------------------------------------------------------------
# Bed — leito da UTI
# ---------------------------------------------------------------------------


class Bed(Base):
    """ICU bed with current status and occupant tracking.

    Maps to the OpenAPI BedStatus schema. The bed grid is queried by
    the GET /beds endpoint and updated by movement registration logic.
    """

    __tablename__ = "beds"

    id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
        comment="Bed identifier (ex: 'UTI-A-01')",
    )
    unit: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="Unit this bed belongs to"
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="free",
        comment="Bed status: free, occupied, blocked, cleaning",
    )
    current_patient_mpi_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="MPI ID of occupying patient (null if free)"
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        comment="Last status update timestamp",
    )


# ---------------------------------------------------------------------------
# AdmissionEpisode — episódio de internação
# ---------------------------------------------------------------------------


class AdmissionEpisode(Base):
    """A complete admission episode from admission to discharge.

    Maps to the ADR-025 admission_episode projection. Tracks the entire
    hospital stay lifecycle.
    """

    __tablename__ = "admission_episodes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, comment="Patient MPI identifier"
    )
    encounter_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        comment="External encounter identifier (e.g., from AMH Gold)",
    )
    admission_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Admission date/time",
    )
    discharge_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Discharge date/time (null if active)"
    )
    admission_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="Admission type: eletiva, urgencia, emergencia, transferencia",
    )
    status: Mapped[str] = mapped_column(
        String(16),
        default="active",
        comment="Episode status: active, discharged",
    )


# ---------------------------------------------------------------------------
# PatientLocationCurrent — localização atual do paciente (uma linha por paciente)
# ---------------------------------------------------------------------------


class PatientLocationCurrent(Base):
    """Current patient location (one row per admitted patient).

    Maps to the patient_location_current projection defined in ADR-025.
    Updated by every movement event via the movement domain logic.
    """

    __tablename__ = "patient_location_current"

    mpi_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        comment="One row per admitted patient",
    )
    encounter_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("admission_episodes.encounter_id"),
        nullable=False,
        comment="Current admission episode",
    )
    unit: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="Current unit (e.g., UTI-1)"
    )
    bed_id: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="Current bed (e.g., L-101)"
    )
    specialty: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="Responsible clinical specialty"
    )
    admitted_to_unit_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When patient arrived at current unit",
    )
    last_movement_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of most recent movement",
    )
    source_cdc_offset: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, comment="CDC offset of the latest event applied"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        comment="Last update timestamp",
    )

    __table_args__ = (
        Index("ix_plc_unit_bed", "unit", "bed_id"),
        Index("ix_plc_unit", "unit"),
        Index("ix_plc_specialty", "specialty"),
    )


# ---------------------------------------------------------------------------
# DischargeSummary — resumo de alta
# ---------------------------------------------------------------------------


class DischargeSummary(Base):
    """Discharge summary — one row per discharged encounter.

    Maps to the discharge_summary table defined in ADR-025.
    Contains clinical and operational data about the discharge.
    """

    __tablename__ = "discharge_summaries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    encounter_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("admission_episodes.encounter_id"),
        unique=True,
        nullable=False,
        comment="One row per discharge (unique encounter)",
    )
    mpi_id: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="Patient MPI identifier"
    )
    discharge_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Discharge date/time",
    )
    discharge_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="domiciliar, transferencia_hospitalar, obito, alta_pedido, evasao",
    )
    destination: Mapped[str | None] = mapped_column(
        String(128), nullable=True, comment="Post-discharge destination"
    )
    discharge_diagnosis: Mapped[str | None] = mapped_column(
        String(16), nullable=True, comment="CID-10 at discharge"
    )
    follow_up_scheduled: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Whether follow-up was scheduled"
    )
    continuity_medication_prescribed: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Medication continuity at discharge"
    )
    source_cdc_offset: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, comment="CDC offset of source event"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        comment="Record creation timestamp",
    )

    __table_args__ = (
        Index("ix_ds_mpi_dt", "mpi_id", "discharge_datetime"),
        Index("ix_ds_discharge_dt", "discharge_datetime"),
        Index("ix_ds_followup_dt", "follow_up_scheduled", "discharge_datetime"),
    )
