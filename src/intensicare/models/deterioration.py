"""Clinical Deterioration — SQLAlchemy model."""

from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


class DeteriorationAssessment(Base):
    __tablename__ = "deterioration_assessments"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    score: Mapped[str] = mapped_column(String(4), nullable=False, comment="0, 1+, 1-, 3+, 3-")
    trend: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="improving, stable, worsening, none"
    )
    criteria: Mapped[list[dict]] = mapped_column(
        JSONB, nullable=False, comment="DeteriorationCriteria dicts"
    )
    domains_affected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    recommendation: Mapped[str | None] = mapped_column(String(512), nullable=True)
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    assessed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
