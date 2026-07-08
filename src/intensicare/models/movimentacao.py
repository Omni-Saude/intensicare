"""Patient Movement / ADT — models for patient movements, beds, and admission episodes.

Based on ADR-025 (MovimentacaoStateStore projection) and the OpenAPI contract
docs/contracts/movimentacao-openapi.yaml.
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String
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
    notes: Mapped[str | None] = mapped_column(
        String(1024), nullable=True, comment="Clinical notes"
    )
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
