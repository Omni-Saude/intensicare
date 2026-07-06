"""Eventos de correlação — associação de alertas correlacionados."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


class CorrelationEvent(Base):
    """Evento de correlação que agrupa alertas relacionados.

    Representa um "cluster" de alertas correlacionados (ex.: deterioração
    multi-sistema detectada em scores simultâneos). Cada alerta pode
    referenciar um correlation_event via correlation_event_id.
    """

    __tablename__ = "correlation_event"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    correlation_key: Mapped[str] = mapped_column(
        String(64), nullable=False,
        comment="Chave determinística de correlação (hash de scores + janela)"
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
