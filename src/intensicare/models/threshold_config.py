"""Configuração de thresholds de alerta por tenant, unidade e leito."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


class ThresholdConfig(Base):
    """Configuração de thresholds de alerta.

    Escopo de resolução (bed ≻ unit ≻ tenant):
    - Se bed_id + unit informados, aplica ao leito específico.
    - Se apenas unit informado (bed_id NULL), aplica a toda unidade.
    - Se ambos NULL, fallback global do tenant.
    """

    __tablename__ = "threshold_config"
    __table_args__ = (
        UniqueConstraint("tenant_id", "unit", "bed_id", "score_type", name="uq_threshold_scope"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(32), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(64))
    bed_id: Mapped[str | None] = mapped_column(String(32))
    score_type: Mapped[str] = mapped_column(String(16), nullable=False)
    watch_threshold: Mapped[int] = mapped_column(Integer, nullable=False)
    urgent_threshold: Mapped[int] = mapped_column(Integer, nullable=False)
    critical_threshold: Mapped[int] = mapped_column(Integer, nullable=False)
    rate_limit_per_hour: Mapped[int | None] = mapped_column(Integer)
    cooldown_minutes: Mapped[int | None] = mapped_column(Integer)
    guideline_source: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_doi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    evidence_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_by: Mapped[str | None] = mapped_column(String(255))
