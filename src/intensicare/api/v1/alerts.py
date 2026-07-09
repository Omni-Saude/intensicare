"""Alert endpoints — list, acknowledge, resolve, escalate, trace."""

from datetime import datetime, timezone
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from intensicare.auth.dependencies import get_current_user
from intensicare.core.database import get_db
from intensicare.models.alert import Alert
from intensicare.models.user import User

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


class AlertResponse(BaseModel):
    """Alert response schema."""

    id: int
    mpi_id: str
    score_id: int | None
    severity: str
    status: str
    title: str
    body: str | None
    created_at: str
    acknowledged_at: str | None
    acknowledged_by: str | None
    resolved_at: str | None
    resolution: str | None

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    """Wrapped list response (AUDIT-007)."""

    alerts: list[AlertResponse]
    total: int


class AcknowledgeRequest(BaseModel):
    """Acknowledge an alert."""

    notes: str | None = None


class ResolveRequest(BaseModel):
    """Resolve an alert with clinical outcome."""

    resolution: str  # true_positive | false_positive | intervention_done
    note: str | None = None


class EscalateRequest(BaseModel):
    """Escalate an alert."""

    reason: str | None = None


def _to_alert_response(alert: Alert) -> AlertResponse:
    """Build an AlertResponse from an Alert ORM instance."""
    return AlertResponse(
        id=alert.id,
        mpi_id=alert.mpi_id,
        score_id=alert.score_id,
        severity=alert.severity,
        status=alert.status,
        title=alert.title,
        body=alert.body,
        created_at=alert.created_at.isoformat(),
        acknowledged_at=alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
        acknowledged_by=alert.acknowledged_by,
        resolved_at=alert.resolved_at.isoformat() if alert.resolved_at else None,
        resolution=alert.resolution,
    )


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    status_filter: str = Query("active", alias="status"),
    unit: str | None = Query(None, alias="unit"),  # noqa: ARG001  # reserved unit filter; accepted for API compatibility
    mpi_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertListResponse:
    """List alerts with optional filters. Returns {alerts, total} (AUDIT-007)."""
    base_query = select(Alert).options(joinedload(Alert.patient))

    if status_filter:
        base_query = base_query.where(Alert.status == status_filter)
    if mpi_id:
        base_query = base_query.where(Alert.mpi_id == mpi_id)

    # Count query: same filters, no pagination
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Data query with pagination
    data_query = base_query.order_by(Alert.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(data_query)
    alerts = result.scalars().all()

    return AlertListResponse(
        alerts=[_to_alert_response(a) for a in alerts],
        total=total,
    )


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: int,
    request_body: AcknowledgeRequest | None = None,  # noqa: ARG001  # optional body accepted for API compatibility
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertResponse:
    """Acknowledge an alert (authenticated)."""
    result = await db.execute(select(Alert).options(joinedload(Alert.patient)).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    if alert.status not in ("active", "escalated"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Alert is already {alert.status}",
        )

    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.now(timezone.utc)
    alert.acknowledged_by = current_user.username

    await db.flush()
    await db.refresh(alert)

    return _to_alert_response(alert)


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: int,
    request_body: ResolveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertResponse:
    """Resolve an alert — records the clinical outcome (authenticated)."""
    result = await db.execute(select(Alert).options(joinedload(Alert.patient)).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    if alert.status in ("resolved",):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Alert is already {alert.status}",
        )

    # Valid transitions: acknowledged → resolved, acting → resolved
    if alert.status not in ("acknowledged", "acting"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot resolve alert in status '{alert.status}'; "
                   "valid from 'acknowledged' or 'acting'",
        )

    valid_resolutions = {"true_positive", "false_positive", "intervention_done"}
    if request_body.resolution not in valid_resolutions:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid resolution '{request_body.resolution}'. "
                   f"Must be one of: {', '.join(sorted(valid_resolutions))}",
        )

    alert.status = "resolved"
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolution = request_body.resolution

    await db.flush()
    await db.refresh(alert)

    return _to_alert_response(alert)


@router.post("/{alert_id}/escalate", response_model=AlertResponse)
async def escalate_alert(
    alert_id: int,
    request_body: EscalateRequest | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertResponse:
    """Escalate an alert to the next response tier (authenticated)."""
    result = await db.execute(select(Alert).options(joinedload(Alert.patient)).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    if alert.status in ("resolved",):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Alert is already {alert.status}",
        )

    # Valid from: raised (active), acknowledged
    if alert.status not in ("active", "acknowledged"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot escalate alert in status '{alert.status}'; "
                   "valid from 'active' or 'acknowledged'",
        )

    alert.status = "escalated"

    await db.flush()
    await db.refresh(alert)

    return _to_alert_response(alert)


@router.get("/{alert_id}/trace", response_model=AlertResponse)
async def trace_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertResponse:
    """Get detailed trace of a specific alert."""
    result = await db.execute(select(Alert).options(joinedload(Alert.patient)).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    return _to_alert_response(alert)
