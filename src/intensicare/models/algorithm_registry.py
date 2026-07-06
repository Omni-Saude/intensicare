"""Registry de versões de algoritmos — imutável, referência FK para clinical_score."""

from datetime import datetime

from sqlalchemy import DateTime, String, Text, UniqueConstraint
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


class AlgorithmRegistry(Base):
    """Registro imutável de versões de algoritmos de scoring clínico.

    Cada linha representa uma versão específica de um score_type (MEWS, NEWS2, SOFA, qSOFA).
    A coluna algorithm_version é a PK e é referenciada por clinical_score.algorithm_version.

    O registro é imutável: uma vez inserido, os campos versionados não devem ser alterados.
    """

    __tablename__ = "algorithm_registry"
    __table_args__ = (
        UniqueConstraint("score_type", "semver"),
    )

    algorithm_version: Mapped[str] = mapped_column(String(32), primary_key=True)
    score_type: Mapped[str] = mapped_column(String(16), nullable=False)
    semver: Mapped[str] = mapped_column(String(16), nullable=False)
    spec_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
    retired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
