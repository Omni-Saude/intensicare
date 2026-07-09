"""Alertas clínicos — TimescaleDB hypertable em created_at."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from intensicare.core.database import Base
from intensicare.models.patient_cache import PatientCache


class Alert(Base):
    """Alertas gerados a partir de scores que excedem thresholds. Hypertable em created_at.

    Severity model (WO-011): canonical normal < watch < urgent < critical.
    Status lifecycle (WO-015): active → acting → acknowledged → resolved |
                               active → escalated → acknowledged → resolved.
    P0-10 highest-severity-wins — never last-writer-wins.
    Resolves AUDIT-008 enum mismatch.
    """

    __tablename__ = "alert"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    score_id: Mapped[int | None] = mapped_column(BigInteger)
    severity: Mapped[str] = mapped_column(
        String(16), nullable=False,
        comment="Canonical severity: normal, watch, urgent, critical"
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="active",
        comment="Status lifecycle: active, acting, escalated, acknowledged, resolved"
    )
    definition_version_id: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("alert_definition_version.definition_version"),
        comment="Versão da definição que gerou este alerta"
    )
    correlation_event_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("correlation_event.id"),
        comment="Evento de correlação ao qual este alerta pertence"
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    acknowledged_by: Mapped[str | None] = mapped_column(String(255))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution: Mapped[str | None] = mapped_column(String(32))

    # ── Relationships (eager-load targets, F-CODE-001) ────────────────
    patient: Mapped["PatientCache"] = relationship(
        "PatientCache",
        primaryjoin="foreign(Alert.mpi_id) == PatientCache.mpi_id",
        lazy="raise",
        viewonly=True,
    )
