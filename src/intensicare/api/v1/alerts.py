"""Alert endpoints — list, acknowledge, resolve, escalate, trace."""

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from intensicare.auth.abac import Action, ResourceType, require_abac
from intensicare.auth.dependencies import get_current_tenant_id, get_current_user
from intensicare.core.database import get_db
from intensicare.models.alert import Alert
from intensicare.models.clinical_score import ClinicalScore
from intensicare.models.user import User
from intensicare.schemas.alerts import (
    AlertGroupedListResponse,
    AlertGroupResponse,
    AlertListResponse,
    AlertResponse,
)
from intensicare.schemas.severity import SeverityLevel, max_severity
from intensicare.services.patient_encryption import resolve_display_name

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

# BUG-F5-01: GET /alerts only declared status/unit/mpi_id/limit/offset —
# the frontend's severity/type/acknowledged/resolved were silently dropped
# by FastAPI (unknown query params are ignored, not 422'd), so the Alerts
# page's filters were no-ops and processed alerts (status != "active", the
# default) were invisible forever. Target contract (orchestrator-adjudicated):
# expand `status` to cover the full lifecycle plus an explicit "all" escape
# hatch, and add `severity`. `type`/boolean acknowledged/resolved are
# explicitly OUT of contract — not added here.
#
# Both are typed as Literal so FastAPI/Pydantic validate them against the
# real enum (422 on bad input) instead of silently matching zero rows —
# matches Alert.status's documented lifecycle (models/alert.py WO-015:
# active, acting, escalated, acknowledged, resolved) and Alert.severity's
# documented canonical set (WO-011: normal, watch, urgent, critical).
# "acting" is intentionally excluded from the status filter — the target
# contract enumerates only active/acknowledged/escalated/resolved/all, and
# "all" already covers the case where a caller wants "acting" alerts too.
AlertStatusFilter = Literal["active", "acknowledged", "escalated", "resolved", "all"]
AlertSeverityFilter = Literal["normal", "watch", "urgent", "critical"]

# ADR-0039 §2: GET /alerts?group_by=signal aggregates members by
# (mpi_id, score_type) at READ time — additive, zero breaking (absent
# group_by keeps the exact pre-existing AlertListResponse shape).
AlertGroupByFilter = Literal["signal"]

# ABAC enforcement (fix RBAC audit Dim A/C — clinical guards had zero
# call-sites outside admin.py). Resolve/escalate are workflow transitions on
# an already-acknowledged alert, not a distinct "write" in the ABACPolicy
# matrix sense (only ADMIN has Action.WRITE for ResourceType.ALERTS). The
# matrix's Action.ACKNOWLEDGE is the one non-admin action clinical roles
# (physician/nurse/physiotherapist/nutritionist) hold for ALERTS beyond
# READ, so acknowledge/resolve/escalate are all mapped to ACKNOWLEDGE here —
# this preserves the exact set of roles the matrix already grants alert
# workflow actions to, without inventing a new policy.


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


async def _to_alert_response(db: AsyncSession, alert: Alert) -> AlertResponse:
    """Build an AlertResponse from an Alert ORM instance.

    ``alert.patient.display_name`` is PHI — on post-migration-0004 schemas
    it is pgcrypto ciphertext (BYTEA), so it must go through
    ``resolve_display_name`` (pgp_sym_decrypt), not a raw ``.decode("utf-8")``
    which produces mojibake/garbage or raises on encrypted bytes and never
    the real name. See ``patient_encryption.resolve_display_name`` for the
    dual-schema (str passthrough vs. encrypted bytes) handling this shares
    with the dashboard service.
    """
    # Derive type from definition_version_id or default
    alert_type = "clinical"
    if alert.definition_version_id:
        # e.g. "MEWS-v1.0.0" → "MEWS"
        alert_type = alert.definition_version_id.split("-")[0].lower()

    # Extract patient_name from eager-loaded relationship
    patient_name: str | None = None
    if alert.patient and alert.patient.display_name:
        patient_name = await resolve_display_name(db, alert.patient.display_name)

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


def _apply_alert_filters(
    base_query: Select[tuple[Alert]],
    status_filter: AlertStatusFilter,
    severity: AlertSeverityFilter | None,
    mpi_id: str | None,
) -> Select[tuple[Alert]]:
    """Shared status/severity/mpi_id predicates for both the flat list and
    the grouped (group_by=signal) view — ADR-0039 §2: filters apply to
    MEMBERS before grouping, the group inherits whatever survives.

    `unit` is intentionally not applied here — it is already a reserved,
    accepted-but-unfiltered param on the ungrouped endpoint (Alert has no
    `unit` column); grouping preserves that exact no-op behavior rather
    than introducing new filtering semantics.
    """
    if status_filter != "all":
        base_query = base_query.where(Alert.status == status_filter)
    if severity:
        base_query = base_query.where(Alert.severity == severity)
    if mpi_id:
        base_query = base_query.where(Alert.mpi_id == mpi_id)
    return base_query


def _derive_score_type(alert: Alert, score_type_by_score_id: dict[int, str]) -> str:
    """Best-effort clinical signal for ADR-0039 grouping (mpi_id, score_type).

    ``Alert`` has no ``score_type`` column of its own. Priority order:

    1. ``score_id`` join to ``ClinicalScore.score_type`` — the single live
       creation path (``alert_engine.check_score_against_thresholds``)
       always sets ``score_id`` to the triggering ``ClinicalScore.id``, so
       this covers the authoritative source value for real alerts.
    2. ``definition_version_id`` prefix (e.g. ``"MEWS-v2.0.0"`` ->
       ``"MEWS"``) — the same derivation ``_to_alert_response()`` already
       uses for the `type` field; covers older/orphan alerts (dev-DB
       verified: 5/62 seed rows) that predate the live score_id path.
    3. ``"UNKNOWN"`` — no signal identifiable; still grouped, never dropped
       (zero information loss — see AlertGroupResponse docstring).
    """
    if alert.score_id is not None:
        score_type = score_type_by_score_id.get(alert.score_id)
        if score_type:
            return score_type
    if alert.definition_version_id:
        return alert.definition_version_id.split("-")[0].upper()
    return "UNKNOWN"


async def _list_alerts_grouped(
    db: AsyncSession,
    status_filter: AlertStatusFilter,
    severity: AlertSeverityFilter | None,
    mpi_id: str | None,
) -> AlertGroupedListResponse:
    """ADR-0039 §2: aggregate members by (mpi_id, score_type) at READ time.

    The source of truth (`alert` rows) is never fused or altered — every
    original alert stays queryable and is returned inside its group's
    `members` list. Pagination (limit/offset) does not apply here: a
    correct group (count, escalating, first/latest) requires seeing every
    filtered member, not a page of them.
    """
    query = _apply_alert_filters(
        select(Alert).options(joinedload(Alert.patient)), status_filter, severity, mpi_id
    )
    result = await db.execute(query.order_by(Alert.created_at.asc()))
    alerts = result.scalars().all()
    total_alerts = len(alerts)

    # Batch-resolve score_type via one ClinicalScore query instead of N+1.
    score_ids = {a.score_id for a in alerts if a.score_id is not None}
    score_type_by_score_id: dict[int, str] = {}
    if score_ids:
        score_rows = await db.execute(
            select(ClinicalScore.id, ClinicalScore.score_type).where(
                ClinicalScore.id.in_(score_ids)
            )
        )
        score_type_by_score_id = {row[0]: row[1] for row in score_rows.all()}

    groups: dict[tuple[str, str], list[Alert]] = {}
    for alert in alerts:
        key = (alert.mpi_id, _derive_score_type(alert, score_type_by_score_id))
        groups.setdefault(key, []).append(alert)

    group_responses: list[AlertGroupResponse] = []
    for (group_mpi_id, score_type), members in groups.items():
        # `members` preserves the query's created_at ASC order — members[0]
        # is the oldest, members[-1] the newest, for the group and for the
        # active-only subsequence used by `escalating` below.
        group_max_severity = max_severity(*(m.severity for m in members)) or members[0].severity

        active_members = [m for m in members if m.status == "active"]
        escalating = False
        if len(active_members) >= 2:
            oldest_active, newest_active = active_members[0], active_members[-1]
            escalating = SeverityLevel(newest_active.severity).is_more_severe_than(
                oldest_active.severity
            )

        patient_name: str | None = None
        if members[0].patient and members[0].patient.display_name:
            patient_name = await resolve_display_name(db, members[0].patient.display_name)

        member_responses = [await _to_alert_response(db, m) for m in members]

        group_responses.append(
            AlertGroupResponse(
                mpi_id=group_mpi_id,
                patient_name=patient_name,
                score_type=score_type,
                max_severity=group_max_severity,
                count=len(members),
                first_created_at=members[0].created_at.isoformat(),
                latest_created_at=members[-1].created_at.isoformat(),
                escalating=escalating,
                members=member_responses,
            )
        )

    # ADR-0039 ordering: max_severity desc, latest_created_at desc.
    group_responses.sort(
        key=lambda g: (SeverityLevel(g.max_severity).rank, g.latest_created_at),
        reverse=True,
    )

    return AlertGroupedListResponse(
        groups=group_responses,
        total_groups=len(group_responses),
        total_alerts=total_alerts,
    )


@router.get("", response_model=AlertListResponse | AlertGroupedListResponse)
async def list_alerts(
    request: Request,
    status_filter: AlertStatusFilter = Query("active", alias="status"),
    severity: AlertSeverityFilter | None = Query(
        None, description="Filter by alert severity: normal, watch, urgent, critical"
    ),
    unit: str | None = Query(
        None, alias="unit"
    ),  # reserved unit filter; accepted for API compatibility
    mpi_id: str | None = Query(None),
    group_by: AlertGroupByFilter | None = Query(
        None,
        description=(
            "Optional read-time aggregation (ADR-0039). group_by=signal groups "
            "members by (mpi_id, score_type); omitted, the response is the "
            "unchanged flat {items, total} shape."
        ),
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertListResponse | AlertGroupedListResponse:
    """List alerts with optional filters. Returns {alerts, total} (AUDIT-007).

    BUG-F5-01: `status` now covers the full lifecycle (active/acknowledged/
    escalated/resolved) plus `all` (no status predicate applied), and
    `severity` filters by Alert.severity. See the module-level comment above
    for why these are Literal-typed and why `all` subsumes `acting`.

    ADR-0039: `group_by=signal` switches the response to
    `AlertGroupedListResponse` ({groups, total_groups, total_alerts}) —
    additive and opt-in; without it the response is byte-for-byte the
    pre-existing `AlertListResponse` shape.
    """
    tenant_id = await get_current_tenant_id(request)
    require_abac(
        role_str=current_user.role,
        resource=ResourceType.ALERTS,
        action=Action.READ,
        tenant_id=tenant_id,
        resource_tenant=tenant_id,
    )

    if group_by == "signal":
        return await _list_alerts_grouped(db, status_filter, severity, mpi_id)

    base_query = _apply_alert_filters(
        select(Alert).options(joinedload(Alert.patient)), status_filter, severity, mpi_id
    )

    # Count query: same filters, no pagination
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Data query with pagination
    data_query = base_query.order_by(Alert.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(data_query)
    alerts = result.scalars().all()

    items = [await _to_alert_response(db, a) for a in alerts]
    return AlertListResponse(
        items=items,
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
    # Scope the refresh to the columns just mutated. A bare db.refresh(alert)
    # expires *every* attribute — including the eager-loaded `patient`
    # relationship (lazy="raise", F-CODE-001) — so the subsequent
    # _to_alert_response() access to alert.patient blows up with
    # InvalidRequestError. attribute_names limits expiry to the named
    # columns, leaving the joinedload'd relationship intact.
    await db.refresh(alert, attribute_names=["status", "acknowledged_at", "acknowledged_by"])

    return await _to_alert_response(db, alert)


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
    # See acknowledge_alert() above — scope the refresh to the mutated
    # columns so the eager-loaded `patient` relationship (lazy="raise")
    # survives for _to_alert_response().
    await db.refresh(alert, attribute_names=["status", "resolved_at", "resolution"])

    return await _to_alert_response(db, alert)


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
    # See acknowledge_alert() above — scope the refresh to the mutated
    # column so the eager-loaded `patient` relationship (lazy="raise")
    # survives for _to_alert_response().
    await db.refresh(alert, attribute_names=["status"])

    return await _to_alert_response(db, alert)


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

    return await _to_alert_response(db, alert)
