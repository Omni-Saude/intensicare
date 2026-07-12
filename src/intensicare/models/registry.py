"""Registry models — Empresa, Estabelecimento, Setor.

Maps to the OpenAPI cadastros-ui contract (docs/contracts/cadastros-ui-openapi.yaml).
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Empresa (Organization / Company)
# ---------------------------------------------------------------------------


class Empresa(Base):
    """Tenant organization — top-level company/org in the registry."""

    __tablename__ = "empresas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    razao_social: Mapped[str] = mapped_column(String(200), nullable=False)
    nome_fantasia: Mapped[str] = mapped_column(String(150), nullable=False)
    cnpj: Mapped[str] = mapped_column(
        String(14), nullable=False, unique=True, comment="CNPJ apenas dígitos"
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=_utcnow
    )


# ---------------------------------------------------------------------------
# Estabelecimento (Establishment / Facility)
# ---------------------------------------------------------------------------


class Estabelecimento(Base):
    """Health establishment — hospital, clinic, etc., owned by an Empresa."""

    __tablename__ = "estabelecimentos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    empresa_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True, comment="FK → empresas.id"
    )
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cnes: Mapped[str | None] = mapped_column(
        String(7), nullable=True, unique=True, comment="CNES 7 dígitos"
    )
    logradouro: Mapped[str | None] = mapped_column(String(200), nullable=True)
    numero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    complemento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bairro: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cidade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True)
    cep: Mapped[str | None] = mapped_column(String(8), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=_utcnow
    )


# ---------------------------------------------------------------------------
# Setor (Sector / Care Unit)
# ---------------------------------------------------------------------------


class Setor(Base):
    """Care unit / sector within an establishment."""

    __tablename__ = "setores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    estabelecimento_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True, comment="FK → estabelecimentos.id"
    )
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    sigla: Mapped[str | None] = mapped_column(String(20), nullable=True)
    tipo: Mapped[str | None] = mapped_column(String(30), nullable=True)
    leitos_operacionais: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=_utcnow
    )
