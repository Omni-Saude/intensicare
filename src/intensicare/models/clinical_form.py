"""Formulários clínicos — definição de formulários e submissões."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from intensicare.core.database import Base


class FormDefinition(Base):
    """Tipos de formulários clínicos disponíveis no sistema."""

    __tablename__ = "form_definitions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512))
    version: Mapped[str] = mapped_column(String(16), default="1.0.0")
    fields: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    scoring: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relacionamento reverso para submissões
    submissions: Mapped[list["ClinicalFormSubmission"]] = relationship(
        "ClinicalFormSubmission", back_populates="form_definition"
    )

    def __repr__(self) -> str:
        return f"<FormDefinition(id={self.id!r}, name={self.name!r})>"


class ClinicalFormSubmission(Base):
    """Submissões de formulários clínicos preenchidos por paciente."""

    __tablename__ = "clinical_form_submissions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    form_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("form_definitions.id"),
        nullable=False,
    )
    form_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="Cópia desnormalizada de form_definitions.id para compatibilidade com schema legado",
    )
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    score: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    severity: Mapped[str | None] = mapped_column(String(16))
    submitted_by: Mapped[str] = mapped_column(String(255), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    version: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="Versão da definição de formulário usada"
    )

    # Relacionamento com a definição do formulário
    form_definition: Mapped["FormDefinition"] = relationship(
        "FormDefinition", back_populates="submissions"
    )

    def __repr__(self) -> str:
        return (
            f"<ClinicalFormSubmission(id={self.id!r}, mpi_id={self.mpi_id!r}, "
            f"form_type={self.form_type!r})>"
        )
