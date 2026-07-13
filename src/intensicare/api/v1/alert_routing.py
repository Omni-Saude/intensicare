"""Alert Routing Rules — CRUD endpoints para regras de roteamento de alertas."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user
from intensicare.core.database import get_db
from intensicare.models.alert_routing import AlertRoutingRule
from intensicare.models.user import User
from intensicare.schemas.alert_routing import (
    AlertRoutingRuleCreate,
    AlertRoutingRuleResponse,
    AlertRoutingRulesListResponse,
    AlertRoutingRuleUpdate,
)

router = APIRouter(prefix="/api/v1", tags=["alert-routing"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _rule_to_response(rule: AlertRoutingRule) -> AlertRoutingRuleResponse:
    """Converte uma instância ORM AlertRoutingRule para o schema de resposta."""
    return AlertRoutingRuleResponse(
        id=rule.id,
        tenant_id=rule.tenant_id,
        name=rule.name,
        conditions=rule.conditions or [],
        actions=rule.actions or [],
        enabled=rule.enabled,
        priority=rule.priority,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/alert-routing", response_model=AlertRoutingRulesListResponse)
async def list_alert_routing_rules(
    enabled: bool | None = Query(None, description="Filtrar por status enabled/disabled"),
    tenant_id: str | None = Query(None, description="Filtrar por tenant"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertRoutingRulesListResponse:
    """Lista regras de roteamento com filtros opcionais e paginação."""
    base_query = select(AlertRoutingRule)

    if enabled is not None:
        base_query = base_query.where(AlertRoutingRule.enabled == enabled)
    if tenant_id:
        base_query = base_query.where(AlertRoutingRule.tenant_id == tenant_id)

    # Count
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Data
    data_query = (
        base_query.order_by(
            AlertRoutingRule.priority.desc(),
            AlertRoutingRule.created_at.desc(),
        )
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(data_query)
    rules = result.scalars().all()

    return AlertRoutingRulesListResponse(
        rules=[_rule_to_response(r) for r in rules],
        total=total,
    )


@router.post(
    "/alert-routing", response_model=AlertRoutingRuleResponse, status_code=status.HTTP_201_CREATED
)
async def create_alert_routing_rule(
    body: AlertRoutingRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertRoutingRuleResponse:
    """Cria uma nova regra de roteamento de alertas."""
    now = datetime.now(timezone.utc)
    rule = AlertRoutingRule(
        tenant_id=body.tenant_id,
        name=body.name,
        conditions=body.conditions,
        actions=body.actions,
        enabled=body.enabled,
        priority=body.priority,
        created_at=now,
        updated_at=now,
    )
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return _rule_to_response(rule)


@router.get("/alert-routing/{rule_id}", response_model=AlertRoutingRuleResponse)
async def get_alert_routing_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertRoutingRuleResponse:
    """Obtém uma regra de roteamento específica pelo ID."""
    result = await db.execute(select(AlertRoutingRule).where(AlertRoutingRule.id == rule_id))
    rule = result.scalar_one_or_none()

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert routing rule not found",
        )

    return _rule_to_response(rule)


@router.put("/alert-routing/{rule_id}", response_model=AlertRoutingRuleResponse)
async def update_alert_routing_rule(
    rule_id: int,
    body: AlertRoutingRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertRoutingRuleResponse:
    """Atualiza uma regra de roteamento (partial update)."""
    result = await db.execute(select(AlertRoutingRule).where(AlertRoutingRule.id == rule_id))
    rule = result.scalar_one_or_none()

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert routing rule not found",
        )

    # Aplica apenas os campos enviados (partial update)
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    rule.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(rule)
    return _rule_to_response(rule)


@router.delete("/alert-routing/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_routing_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Remove uma regra de roteamento de alertas."""
    result = await db.execute(select(AlertRoutingRule).where(AlertRoutingRule.id == rule_id))
    rule = result.scalar_one_or_none()

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert routing rule not found",
        )

    await db.delete(rule)
    await db.flush()
