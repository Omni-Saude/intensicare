"""Threshold configuration CRUD API — admin-only endpoints.

REQ-INV-1-2: toda mutação (create/update/delete) gera entrada em audit_trail.
"""

from datetime import datetime, timezone
import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth import require_admin
from intensicare.core.database import get_db
from intensicare.models.audit_trail import AuditTrail
from intensicare.models.threshold_config import ThresholdConfig
from intensicare.models.user import User
from intensicare.schemas import (
    ThresholdConfigCreate,
    ThresholdConfigResponse,
    ThresholdConfigUpdate,
)

router = APIRouter(
    prefix="/api/v1/thresholds",
    tags=["thresholds"],
    dependencies=[Depends(require_admin)],
)


async def _get_threshold_or_404(session: AsyncSession, threshold_id: int) -> ThresholdConfig:
    """Fetch a threshold config by ID or raise 404."""
    result = await session.execute(
        select(ThresholdConfig).where(ThresholdConfig.id == threshold_id)
    )
    threshold = result.scalar_one_or_none()
    if threshold is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Threshold configuration {threshold_id} not found",
        )
    return threshold


async def _write_audit(
    session: AsyncSession,
    *,
    action: str,
    threshold: ThresholdConfig,
    actor: str,
    before_state: bytes | None = None,
    after_state: bytes | None = None,
    request_id: str | None = None,
) -> None:
    """Cria entrada de auditoria para mutação de threshold_config (REQ-INV-1-2)."""
    entry = AuditTrail(
        event_ts=datetime.now(timezone.utc),
        tenant_id=threshold.tenant_id,
        actor=actor,
        action=action,
        entity_table="threshold_config",
        entity_id=str(threshold.id),
        before_state=before_state,
        after_state=after_state,
        request_id=request_id,
    )
    session.add(entry)


@router.get(
    "",
    response_model=list[ThresholdConfigResponse],
    summary="List all threshold configurations",
)
async def list_thresholds(
    tenant_id: str | None = None,
    session: AsyncSession = Depends(get_db),
) -> list[ThresholdConfig]:
    """List all threshold configurations, optionally filtered by tenant_id."""
    stmt = select(ThresholdConfig)
    if tenant_id:
        stmt = stmt.where(ThresholdConfig.tenant_id == tenant_id)
    stmt = stmt.order_by(ThresholdConfig.id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get(
    "/{threshold_id}",
    response_model=ThresholdConfigResponse,
    summary="Get a threshold configuration by ID",
)
async def get_threshold(
    threshold_id: int,
    session: AsyncSession = Depends(get_db),
) -> ThresholdConfig:
    """Retrieve a single threshold configuration by its ID."""
    return await _get_threshold_or_404(session, threshold_id)


@router.post(
    "",
    response_model=ThresholdConfigResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new threshold configuration",
)
async def create_threshold(
    body: ThresholdConfigCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
    request: Request = None,  # type: ignore[assignment]
) -> ThresholdConfig:
    """Create a new threshold configuration (admin-only)."""
    threshold = ThresholdConfig(
        tenant_id=body.tenant_id,
        unit=body.unit,
        score_type=body.score_type,
        watch_threshold=body.watch_threshold,
        urgent_threshold=body.urgent_threshold,
        critical_threshold=body.critical_threshold,
        rate_limit_per_hour=body.rate_limit_per_hour,
        cooldown_minutes=body.cooldown_minutes,
        updated_at=datetime.now(timezone.utc),
        updated_by=current_user.username,
    )
    session.add(threshold)
    await session.flush()  # flush para gerar o id antes do commit

    # REQ-INV-1-2: auditar criação
    after_state = json.dumps(body.model_dump(), default=str).encode()
    req_id = request.headers.get("x-request-id") if request else None
    await _write_audit(
        session,
        action="threshold.create",
        threshold=threshold,
        actor=current_user.username,
        after_state=after_state,
        request_id=req_id,
    )

    await session.commit()
    await session.refresh(threshold)
    return threshold


@router.put(
    "/{threshold_id}",
    response_model=ThresholdConfigResponse,
    summary="Update a threshold configuration",
)
async def update_threshold(
    threshold_id: int,
    body: ThresholdConfigUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
    request: Request = None,  # type: ignore[assignment]
) -> ThresholdConfig:
    """Update an existing threshold configuration (admin-only)."""
    threshold = await _get_threshold_or_404(session, threshold_id)

    # Serializa estado anterior para auditoria
    before_state = json.dumps(
        {
            "tenant_id": threshold.tenant_id,
            "unit": threshold.unit,
            "bed_id": threshold.bed_id,
            "score_type": threshold.score_type,
            "watch_threshold": threshold.watch_threshold,
            "urgent_threshold": threshold.urgent_threshold,
            "critical_threshold": threshold.critical_threshold,
            "rate_limit_per_hour": threshold.rate_limit_per_hour,
            "cooldown_minutes": threshold.cooldown_minutes,
        },
        default=str,
    ).encode()

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(threshold, field, value)

    threshold.updated_at = datetime.now(timezone.utc)
    threshold.updated_by = current_user.username

    # Serializa estado posterior para auditoria
    after_state = json.dumps(
        {
            "tenant_id": threshold.tenant_id,
            "unit": threshold.unit,
            "bed_id": threshold.bed_id,
            "score_type": threshold.score_type,
            "watch_threshold": threshold.watch_threshold,
            "urgent_threshold": threshold.urgent_threshold,
            "critical_threshold": threshold.critical_threshold,
            "rate_limit_per_hour": threshold.rate_limit_per_hour,
            "cooldown_minutes": threshold.cooldown_minutes,
        },
        default=str,
    ).encode()

    await session.flush()

    # REQ-INV-1-2: auditar atualização
    await _write_audit(
        session,
        action="threshold.update",
        threshold=threshold,
        actor=current_user.username,
        before_state=before_state,
        after_state=after_state,
        request_id=request.headers.get("x-request-id") if request else None,
    )

    await session.commit()
    await session.refresh(threshold)
    return threshold


@router.delete(
    "/{threshold_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a threshold configuration",
)
async def delete_threshold(
    threshold_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
    request: Request = None,  # type: ignore[assignment]
) -> None:
    """Delete a threshold configuration (admin-only)."""
    threshold = await _get_threshold_or_404(session, threshold_id)

    # Serializa estado antes da exclusão para auditoria
    before_state = json.dumps(
        {
            "tenant_id": threshold.tenant_id,
            "unit": threshold.unit,
            "bed_id": threshold.bed_id,
            "score_type": threshold.score_type,
            "watch_threshold": threshold.watch_threshold,
            "urgent_threshold": threshold.urgent_threshold,
            "critical_threshold": threshold.critical_threshold,
            "rate_limit_per_hour": threshold.rate_limit_per_hour,
            "cooldown_minutes": threshold.cooldown_minutes,
        },
        default=str,
    ).encode()

    # REQ-INV-1-2: auditar exclusão (antes do delete para ter o id)
    await _write_audit(
        session,
        action="threshold.delete",
        threshold=threshold,
        actor=current_user.username,
        before_state=before_state,
        after_state=None,
        request_id=request.headers.get("x-request-id") if request else None,
    )

    await session.delete(threshold)
    await session.commit()
