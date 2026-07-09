"""Prescription System — SQLAlchemy models.

Tables:
- prescricoes: Core prescription table (state machine per ADR-027)
- interacao_alertas: Drug interaction alerts (ADR-026)
- auditoria_prescricao: State transition audit log (ADR-027, INV-1)
- agenda_prescricao: Administration schedule (aprazamento)
"""

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from intensicare.core.database import Base


class Prescricao(Base):
    """Medical prescription for a patient in the ICU.

    Follows ADR-027 state machine with 5 states: draft, active, completed,
    discontinued, suspended. Uses optimistic locking (version column) to
    prevent concurrent modification races.
    """

    __tablename__ = "prescricoes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    medication: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="ex: '500mg', '1g', '20mg/mL'"
    )
    route: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="Administration route: IV, PO, SC, IM, SN, IT, TOP, INAL",
    )
    frequency: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="QID, TID, BID, QD, QOD, PRN, continuous, ou personalizada ex: 8/8h",
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(16),
        default="active",
        comment="State: draft, active, completed, discontinued, suspended (ADR-027)",
    )
    version: Mapped[int] = mapped_column(
        Integer, default=1, comment="Optimistic locking version"
    )
    prescribed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    interacao_alertas: Mapped[list["InteracaoAlerta"]] = relationship(
        back_populates="prescricao", cascade="all, delete-orphan"
    )
    auditoria: Mapped[list["AuditoriaPrescricao"]] = relationship(
        back_populates="prescricao", cascade="all, delete-orphan"
    )
    agenda: Mapped[list["AgendaPrescricao"]] = relationship(
        back_populates="prescricao", cascade="all, delete-orphan"
    )
    state_logs: Mapped[list["PrescriptionStateLog"]] = relationship(
        back_populates="prescricao", cascade="all, delete-orphan"
    )


class InteracaoAlerta(Base):
    """Drug interaction alert detected for a prescription (ADR-026).

    Severity levels (DMN versioned per ADR-0012):
    - contraindicated: absolute contraindication, hard stop
    - severe: serious risk, requires prescriber acknowledgment
    - moderate: caution, manageable with monitoring
    - minor: theoretical or low clinical relevance

    Interaction types:
    - drug-drug: between two co-prescribed medications
    - drug-allergy: medication vs patient allergy
    - drug-food: medication vs food/nutrient
    - duplicate: same therapeutic class duplicated
    """

    __tablename__ = "interacao_alertas"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    prescricao_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("prescricoes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    severity: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        comment="contraindicated, severe, moderate, minor",
    )
    interaction_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="drug-drug, drug-allergy, drug-food, duplicate",
    )
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    prescricao: Mapped["Prescricao"] = relationship(back_populates="interacao_alertas")


class AuditoriaPrescricao(Base):
    """Prescription state transition audit log (ADR-027, INV-1).

    Append-only table recording every state change with who, when,
    and what changed. Satisfies INV-1 full audit trail requirement.
    """

    __tablename__ = "auditoria_prescricao"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    prescricao_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("prescricoes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="created, updated, state_change, discontinued",
    )
    changed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    changes: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Snapshot of changed fields with old/new values",
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    prescricao: Mapped["Prescricao"] = relationship(back_populates="auditoria")


class AgendaPrescricao(Base):
    """Prescription administration schedule (aprazamento).

    Each row represents a scheduled administration time for a prescription.
    Tracks whether the dose was administered, by whom, and when.
    """

    __tablename__ = "agenda_prescricao"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    prescricao_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("prescricoes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scheduled_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(16),
        default="pending",
        comment="pending, administered, missed, refused",
    )
    administered_by: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    administered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    prescricao: Mapped["Prescricao"] = relationship(back_populates="agenda")


class PrescriptionStateLog(Base):
    """Append-only audit log for prescription state transitions.

    Records every state change with who performed it, when, and why.
    Never updated or deleted — strictly append-only per INV-1 requirements.
    Tracks the state machine version active at the time of transition.
    """

    __tablename__ = "prescription_state_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    prescription_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("prescricoes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_status: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="Previous state before transition"
    )
    to_status: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="New state after transition"
    )
    transitioned_by: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Clinician or system that performed the transition"
    )
    transition_reason: Mapped[str | None] = mapped_column(
        String(1024), nullable=True, comment="Clinical justification for the transition"
    )
    state_machine_version: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="1.0.0",
        comment="Version of the state machine active at transition time",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    prescricao: Mapped["Prescricao"] = relationship(back_populates="state_logs")
