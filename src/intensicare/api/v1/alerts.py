"""Alert endpoints — list, acknowledge, resolve, escalate, trace."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from intensicare.auth.abac import Action, ResourceType, require_abac
from intensicare.auth.dependencies import get_current_tenant_id, get_current_user
from intensicare.core.database import get_db
from intensicare.models.alert import Alert
from intensicare.models.user import User

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

# ABAC enforcement (fix RBAC audit Dim A/C — clinical guards had zero
# call-sites outside admin.py). Resolve/escalate are workflow transitions on
# an already-acknowledged alert, not a distinct "write" in the ABACPolicy
# matrix sense (only ADMIN has Action.WRITE for ResourceType.ALERTS). The
# matrix's Action.ACKNOWLEDGE is the one non-admin action clinical roles
# (physician/nurse/physiotherapist/nutritionist) hold for ALERTS beyond
# READ, so acknowledge/resolve/escalate are all mapped to ACKNOWLEDGE here —
# this preserves the exact set of roles the matrix already grants alert
# workflow actions to, without inventing a new policy.


class AlertResponse(BaseModel):
    """Alert response schema — shape matches frontend AlertInfo (api.ts:91-105)."""

    id: int
    type: str = "clinical"
    severity: str
    title: str
    message: str | None
    mpi_id: str | None = None
    patient_name: str | None = None
    pathway_name: str | None = None
    created_at: str
    acknowledged_at: str | None = None
    resolved_at: str | None = None
    resolved_by: str | None = None
    resolution: str | None = None

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    """Wrapped list response — frontend expects {items, total} (AUDIT-007)."""

    items: list[AlertResponse]
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
    # Derive type from definition_version_id or default
    alert_type = "clinical"
    if alert.definition_version_id:
        # e.g. "MEWS-v1.0.0" → "MEWS"
        alert_type = alert.definition_version_id.split("-")[0].lower()

    # Extract patient_name from eager-loaded relationship
    patient_name: str | None = None
    if alert.patient and alert.patient.display_name:
        try:
            patient_name = (
                alert.patient.display_name.decode("utf-8")
                if isinstance(alert.patient.display_name, bytes)
                else str(alert.patient.display_name)
            )
        except (UnicodeDecodeError, AttributeError):
            patient_name = None

    return AlertResponse(
        id=alert.id,
        type=alert_type,
        severity=alert.severity,
        title=alert.title,
        message=alert.body,
        mpi_id=alert.mpi_id,
        patient_name=patient_name,
        pathway_name=None,  # Not available on Alert model yet
        created_at=alert.created_at.isoformat(),
        acknowledged_at=alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
        resolved_at=alert.resolved_at.isoformat() if alert.resolved_at else None,
        resolved_by=None,  # Not tracked on Alert model yet
        resolution=alert.resolution,
    )


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    request: Request,
    status_filter: str = Query("active", alias="status"),
    unit: str | None = Query(
        None, alias="unit"
    ),  # reserved unit filter; accepted for API compatibility
    mpi_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertListResponse:
    """List alerts with optional filters. Returns {alerts, total} (AUDIT-007)."""
    tenant_id = await get_current_tenant_id(request)
    require_abac(
        role_str=current_user.role,
        resource=ResourceType.ALERTS,
        action=Action.READ,
        tenant_id=tenant_id,
        resource_tenant=tenant_id,
    )

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
        items=[_to_alert_response(a) for a in alerts],
        total=total,
    )


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: int,
    request: Request,
    request_body: AcknowledgeRequest | None = None,  # optional body accepted for API compatibility
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertResponse:
    """Acknowledge an alert (authenticated)."""
    tenant_id = await get_current_tenant_id(request)
    require_abac(
        role_str=current_user.role,
        resource=ResourceType.ALERTS,
        action=Action.ACKNOWLEDGE,
        tenant_id=tenant_id,
        resource_tenant=tenant_id,
    )

    result = await db.execute(
        select(Alert).options(joinedload(Alert.patient)).where(Alert.id == alert_id)
    )
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
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertResponse:
    """Resolve an alert — records the clinical outcome (authenticated)."""
    tenant_id = await get_current_tenant_id(request)
    require_abac(
        role_str=current_user.role,
        resource=ResourceType.ALERTS,
        action=Action.ACKNOWLEDGE,
        tenant_id=tenant_id,
        resource_tenant=tenant_id,
    )

    result = await db.execute(
        select(Alert).options(joinedload(Alert.patient)).where(Alert.id == alert_id)
    )
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
    request: Request,
    request_body: EscalateRequest | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertResponse:
    """Escalate an alert to the next response tier (authenticated)."""
    tenant_id = await get_current_tenant_id(request)
    require_abac(
        role_str=current_user.role,
        resource=ResourceType.ALERTS,
        action=Action.ACKNOWLEDGE,
        tenant_id=tenant_id,
        resource_tenant=tenant_id,
    )

    result = await db.execute(
        select(Alert).options(joinedload(Alert.patient)).where(Alert.id == alert_id)
    )
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
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertResponse:
    """Get detailed trace of a specific alert."""
    tenant_id = await get_current_tenant_id(request)
    require_abac(
        role_str=current_user.role,
        resource=ResourceType.ALERTS,
        action=Action.READ,
        tenant_id=tenant_id,
        resource_tenant=tenant_id,
    )

    result = await db.execute(
        select(Alert).options(joinedload(Alert.patient)).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    return _to_alert_response(alert)
