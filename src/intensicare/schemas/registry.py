"""Pydantic schemas for Registry/Admin UI API.

Maps to OpenAPI contract: docs/contracts/cadastros-ui-openapi.yaml
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Empresa
# ---------------------------------------------------------------------------


class EmpresaResponse(BaseModel):
    """Full Empresa response (read model)."""

    id: str = Field(..., description="UUID da empresa")
    razao_social: str = Field(..., max_length=200)
    nome_fantasia: str = Field(..., max_length=150)
    cnpj: str = Field(..., min_length=14, max_length=14, pattern=r"^\d{14}$")
    ativo: bool = True
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class EmpresaCreate(BaseModel):
    """Request body for creating an Empresa."""

    razao_social: str = Field(..., max_length=200)
    nome_fantasia: str = Field(..., max_length=150)
    cnpj: str = Field(..., min_length=14, max_length=14, pattern=r"^\d{14}$")


class EmpresaUpdate(BaseModel):
    """Request body for updating an Empresa (all fields optional)."""

    razao_social: str | None = Field(None, max_length=200)
    nome_fantasia: str | None = Field(None, max_length=150)
    cnpj: str | None = Field(None, min_length=14, max_length=14, pattern=r"^\d{14}$")
    ativo: bool | None = None


# ---------------------------------------------------------------------------
# Estabelecimento
# ---------------------------------------------------------------------------


class EstabelecimentoResponse(BaseModel):
    """Full Estabelecimento response (read model)."""

    id: str = Field(..., description="UUID do estabelecimento")
    empresa_id: str = Field(..., description="UUID da empresa proprietária")
    nome: str = Field(..., max_length=200)
    cnes: str | None = Field(None, min_length=7, max_length=7, pattern=r"^\d{7}$")
    logradouro: str | None = Field(None, max_length=200)
    numero: str | None = Field(None, max_length=20)
    complemento: str | None = Field(None, max_length=100)
    bairro: str | None = Field(None, max_length=100)
    cidade: str | None = Field(None, max_length=100)
    uf: str | None = Field(None, min_length=2, max_length=2, pattern=r"^[A-Z]{2}$")
    cep: str | None = Field(None, min_length=8, max_length=8, pattern=r"^\d{8}$")
    ativo: bool = True
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class EstabelecimentoCreate(BaseModel):
    """Request body for creating an Estabelecimento."""

    empresa_id: str = Field(..., description="UUID da empresa proprietária")
    nome: str = Field(..., max_length=200)
    cnes: str | None = Field(None, min_length=7, max_length=7, pattern=r"^\d{7}$")
    logradouro: str | None = Field(None, max_length=200)
    numero: str | None = Field(None, max_length=20)
    complemento: str | None = Field(None, max_length=100)
    bairro: str | None = Field(None, max_length=100)
    cidade: str | None = Field(None, max_length=100)
    uf: str | None = Field(None, min_length=2, max_length=2, pattern=r"^[A-Z]{2}$")
    cep: str | None = Field(None, min_length=8, max_length=8, pattern=r"^\d{8}$")


# ---------------------------------------------------------------------------
# Setor
# ---------------------------------------------------------------------------


class SetorResponse(BaseModel):
    """Full Setor response (read model)."""

    id: str = Field(..., description="UUID do setor")
    estabelecimento_id: str = Field(..., description="UUID do estabelecimento")
    nome: str = Field(..., max_length=150)
    sigla: str | None = Field(None, max_length=20)
    tipo: str | None = None
    leitos_operacionais: int | None = Field(None, ge=0)
    ativo: bool = True
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class SetorCreate(BaseModel):
    """Request body for creating a Setor."""

    estabelecimento_id: str = Field(..., description="UUID do estabelecimento")
    nome: str = Field(..., max_length=150)
    sigla: str | None = Field(None, max_length=20)
    tipo: str | None = None
    leitos_operacionais: int | None = Field(None, ge=0)


# ---------------------------------------------------------------------------
# List responses (AUDIT-007 pattern: items + total)
# ---------------------------------------------------------------------------


class RegistryListResponse(BaseModel):
    """Generic paginated list response (AUDIT-007 pattern)."""

    items: list[Any] = Field(default_factory=list)
    total: int = 0
    limit: int = 50
    offset: int = 0
