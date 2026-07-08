"""Regras de roteamento de alertas — condições e ações em JSONB.

Cada regra define condições (field, operator, value) que, quando satisfeitas,
disparam ações (notify, escalate, etc.) automaticamente.
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


class AlertRoutingRule(Base):
    """Regra de roteamento de alertas baseada em condições configuráveis.

    Conditions e actions são armazenados como JSONB para máxima flexibilidade.

    Exemplo de conditions:
        [
            {"field": "severity", "operator": "in", "value": ["urgent", "critical"]},
            {"field": "unit", "operator": "equals", "value": "UTI-A"}
        ]

    Exemplo de actions:
        [
            {"type": "notify", "channel": "push", "target": "team-uti-a"},
            {"type": "escalate", "delay_minutes": 15, "target": "supervisor"}
        ]
    """

    __tablename__ = "alert_routing_rule"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True,
        comment="Tenant proprietário da regra"
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="Nome descritivo da regra"
    )
    conditions: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list,
        comment="Lista de condições (field, operator, value) em JSONB"
    )
    actions: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list,
        comment="Lista de ações (type, channel, target, etc.) em JSONB"
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True,
        comment="Se a regra está ativa"
    )
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
        comment="Prioridade da regra (maior = mais prioritário)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="Timestamp de criação"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="Timestamp da última atualização"
    )
