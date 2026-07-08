"""Hemodynamic Stability — SQLAlchemy model."""
from datetime import datetime, timezone
from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from intensicare.core.database import Base

class StabilityAssessment(Base):
    __tablename__ = "stability_assessments"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False, comment="0-27 criteria in warning/critical")
    severity: Mapped[str] = mapped_column(String(16), nullable=False, comment="estavel, atencao, critico")
    criteria: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, comment="27 StabilityCriterion dicts")
    recommendation: Mapped[str | None] = mapped_column(String(512), nullable=True)
    assessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
