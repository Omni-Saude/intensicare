"""Pydantic schemas para Alert Routing Rules."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Condition / Action item validators (opcionais, mantidos aqui para documentar o schema)
# ---------------------------------------------------------------------------

class ConditionItem(BaseModel):
    """Uma única condição de roteamento."""

    field: str = Field(..., description="Campo a ser avaliado (ex.: severity, unit, mpi_id)")
    operator: str = Field(..., description="Operador: equals, in, not_in, gt, lt, gte, lte, contains")
    value: Any = Field(..., description="Valor(es) de comparação (scalar ou lista)")


class ActionItem(BaseModel):
    """Uma única ação a ser disparada quando as condições são satisfeitas."""

    type: str = Field(..., description="Tipo da ação: notify, escalate, webhook, assign")
    channel: str | None = Field(None, description="Canal: push, email, sms, webhook")
    target: str = Field(..., description="Alvo da ação (team id, endpoint, etc.)")
    delay_minutes: int | None = Field(None, ge=0, description="Delay em minutos antes de executar a ação")


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class AlertRoutingRuleCreate(BaseModel):
    """Schema para criação de uma regra de roteamento."""

    tenant_id: str = Field(..., min_length=1, max_length=64, description="Tenant proprietário")
    name: str = Field(..., min_length=1, max_length=255, description="Nome descritivo da regra")
    conditions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de condições (field, operator, value)",
    )
    actions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de ações (type, target, etc.)",
    )
    enabled: bool = Field(True, description="Se a regra deve ser ativada imediatamente")
    priority: int = Field(0, ge=0, description="Prioridade (maior = mais prioritário)")


class AlertRoutingRuleUpdate(BaseModel):
    """Schema para atualização parcial de uma regra de roteamento."""

    tenant_id: str | None = Field(None, min_length=1, max_length=64)
    name: str | None = Field(None, min_length=1, max_length=255)
    conditions: list[dict[str, Any]] | None = Field(None)
    actions: list[dict[str, Any]] | None = Field(None)
    enabled: bool | None = Field(None)
    priority: int | None = Field(None, ge=0)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class AlertRoutingRuleResponse(BaseModel):
    """Resposta individual de uma regra de roteamento."""

    id: int
    tenant_id: str
    name: str
    conditions: list[dict[str, Any]]
    actions: list[dict[str, Any]]
    enabled: bool
    priority: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlertRoutingRulesListResponse(BaseModel):
    """Resposta paginada da listagem de regras."""

    rules: list[AlertRoutingRuleResponse]
    total: int
