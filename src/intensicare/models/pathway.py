"""Care Pathways (Trilhas Engine) — SQLAlchemy models."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from intensicare.core.database import Base


class Pathway(Base):
    __tablename__ = "pathways"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    definition_hash: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="SHA-256 content hash of the compiled YAML pathway definition",
    )
    states: Mapped[list[dict] | None] = mapped_column(
        JSONB, nullable=True, comment="Array of PathwayState objects"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships (eager-load targets, F-CODE-001) ────────────────
    criteria: Mapped[list["PathwayCriteria"]] = relationship(
        "PathwayCriteria",
        back_populates="pathway",
        lazy="raise",
    )
    patient_pathways: Mapped[list["PatientPathway"]] = relationship(
        "PatientPathway",
        back_populates="pathway",
        lazy="raise",
    )


class PathwayCriteria(Base):
    __tablename__ = "pathway_criteria"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    normal_range: Mapped[str | None] = mapped_column(String(128), nullable=True)
    alert_threshold: Mapped[str | None] = mapped_column(String(128), nullable=True)
    pathway_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("pathways.id"), nullable=False)

    # ── Relationships (eager-load targets, F-CODE-001) ────────────────
    pathway: Mapped["Pathway"] = relationship("Pathway", back_populates="criteria")


class PatientPathway(Base):
    __tablename__ = "patient_pathways"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    encounter_id: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, comment="Admission identifier from AMH Gold"
    )
    bed_id: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="Current bed at time of enrollment"
    )
    unit: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="Current unit at time of enrollment"
    )
    pathway_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("pathways.id"), nullable=False)
    current_state: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="Current state ID (see ADR-021)"
    )
    criteria_data: Mapped[list[dict] | None] = mapped_column(
        JSONB, nullable=True, comment="Criteria evaluations array"
    )
    status: Mapped[str] = mapped_column(String(16), default="active")
    severity: Mapped[str | None] = mapped_column(String(16), nullable=True)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    enrolled_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships (eager-load targets, F-CODE-001) ────────────────
    pathway: Mapped["Pathway"] = relationship("Pathway", back_populates="patient_pathways")
    transitions: Mapped[list["PathwayStateTransition"]] = relationship(
        "PathwayStateTransition",
        lazy="raise",
    )


class PathwayStateTransition(Base):
    __tablename__ = "pathway_state_transitions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    patient_pathway_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("patient_pathways.id"), nullable=False
    )
    from_state: Mapped[str] = mapped_column(String(64), nullable=False)
    to_state: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
