"""Sedation Monitoring — SQLAlchemy model.

RASS, BPS/NRS, and CAM-ICU assessments for ICU patients.
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


class SedationAssessment(Base):
    """Sedation assessment including RASS, BPS/NRS pain scores, and CAM-ICU delirium screening."""

    __tablename__ = "sedation_assessments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    rass_score: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Richmond Agitation-Sedation Scale: -5 (unarousable) to +4 (combative)"
    )
    rass_label: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="e.g. Sonolento, Agitado, Calmo"
    )

    bps_score: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Behavioral Pain Scale: 3–12 (non-communicative patients)"
    )
    nrs_score: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Numeric Rating Scale: 0–10 (communicative patients)"
    )

    cam_icu_positive: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, comment="CAM-ICU delirium screening result (True=positive for delirium)"
    )
    cam_icu_features: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, comment="CAM-ICU feature details (Feature 1-4, RASS reference)"
    )

    current_sedation: Mapped[str | None] = mapped_column(
        String(128), nullable=True, comment="Current sedation infusion, e.g. Propofol 20mL/h"
    )

    assessed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)
