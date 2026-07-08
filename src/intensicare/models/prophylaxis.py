"""Prophylaxis bundle assessments — one row per patient per bundle."""

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


class ProphylaxisAssessment(Base):
    """Persisted state of a prophylaxis bundle assessment for a patient.

    Each (mpi_id, bundle_id) pair has exactly one row. The criteria column
    stores the current met/na state as a JSONB array. Status and score are
    recomputed on every update via the domain service.
    """

    __tablename__ = "prophylaxis_assessment"
    __table_args__ = (
        UniqueConstraint(
            "mpi_id",
            "bundle_id",
            name="uq_prophylaxis_assessment_patient_bundle",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    bundle_id: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="Bundle identifier: lamgd, tev, hiperglicemia, mobilizacao, dispositivos"
    )

    # JSONB array of {id, met, na} criterion states
    criteria: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        comment="Array of {id, met, na} objects for each criterion"
    )

    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="pending",
        comment="Bundle status: complete, partial, pending, na"
    )
    score: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
        comment="Bundle score 0-100"
    )

    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        comment="Timestamp of the last assessment"
    )
    assessed_by: Mapped[str | None] = mapped_column(
        String(255),
        comment="User who performed the assessment"
    )
