"""Versões de definição de alertas — referência imutável versionada."""

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


class AlertDefinitionVersion(Base):
    """Registro de versões de definições de alertas.

    Cada linha representa uma versão de uma definição de alerta (thresholds,
    lógica de correlação, etc.). A coluna definition_version é a PK e é
    referenciada por alert.definition_version_id.
    """

    __tablename__ = "alert_definition_version"

    definition_version: Mapped[str] = mapped_column(String(32), primary_key=True)
    score_type: Mapped[str] = mapped_column(String(16), nullable=False)
    semver: Mapped[str] = mapped_column(String(16), nullable=False)
    spec_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
    retired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
