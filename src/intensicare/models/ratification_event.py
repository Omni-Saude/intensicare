"""Ratification event — single-row history table for clinical algorithm ratification.

Each row records a ratification decision: which algorithm versions were ratified,
by whom, on what date, and the evidence basis.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


class RatificationEvent(Base):
    """Immutable record of a clinical ratification decision.

    This is a single-row-per-event log — once inserted, rows should never
    be updated. The table serves as the definitive record that a set of
    algorithm versions passed clinical committee review.
    """

    __tablename__ = "ratification_event"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    ratified_by: Mapped[str] = mapped_column(String(128), nullable=False)
    authority: Mapped[str] = mapped_column(String(256), nullable=False)
    algorithm_versions: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_basis: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
