"""Dashboard API endpoints — patient list, patient detail."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.abac import Action, ResourceType, require_abac
from intensicare.auth.dependencies import get_current_tenant_id, get_current_user
from intensicare.core.database import get_db
from intensicare.models.user import User
from intensicare.schemas.dashboard import DashboardResponse, PatientDetailResponse
from intensicare.services.dashboard import get_dashboard, get_patient_detail

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Clinical dashboard — bed grid",
    description=(
        "Returns summary for all active patients with latest MEWS, NEWS2, and alert status."
    ),
)
async def dashboard(
    request: Request,
    unit: str | None = Query(None, description="Filter by unit"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardResponse:
    """Get the clinical dashboard bed grid data."""
    # ABAC enforcement (fix RBAC audit Dim A/C). The aggregate bed-grid is the
    # "telão" (big-screen) resource — ResourceType.DASHBOARD/READ is granted
    # broadly in the matrix (all clinical roles + VIEWER + AUDITOR), which is
    # intentional: this endpoint carries no single-patient drill-down.
    tenant_id = await get_current_tenant_id(request)
    require_abac(
        role_str=current_user.role,
        resource=ResourceType.DASHBOARD,
        action=Action.READ,
        tenant_id=tenant_id,
        resource_tenant=tenant_id,
    )

    try:
        return await get_dashboard(db=db, unit=unit)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load dashboard: {exc}",
        ) from exc


@router.get(
    "/patients/{mpi_id}/detail",
    response_model=PatientDetailResponse,
    summary="Patient detail view",
    description=(
        "Returns detailed patient data with vitals history (24h), score history, and active alerts."
    ),
)
async def patient_detail(
    mpi_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PatientDetailResponse:
    """Get detailed patient information for the detail view."""
    # ABAC enforcement — unlike the aggregate /dashboard bed grid, this
    # endpoint drills into a single patient's identified vitals/score/alert
    # history (PHI), so it is scoped to ResourceType.PATIENT_DEMOGRAPHICS
    # rather than DASHBOARD. This is a deliberate, documented decision (no
    # more specific ResourceType exists in the matrix for "single-patient
    # clinical detail view"): it keeps VIEWER (telão) able to read the
    # bed-grid dashboard while NOT granting it per-patient PHI drill-down,
    # matching the matrix's existing PATIENT_DEMOGRAPHICS grants
    # (physician/nurse/physiotherapist/nutritionist/admin only).
    tenant_id = await get_current_tenant_id(request)
    require_abac(
        role_str=current_user.role,
        resource=ResourceType.PATIENT_DEMOGRAPHICS,
        action=Action.READ,
        tenant_id=tenant_id,
        resource_tenant=tenant_id,
    )

    result = await get_patient_detail(db=db, mpi_id=mpi_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient not found: {mpi_id}",
        )
    return result


@router.get(
    "/patients/{mpi_id}",
    response_model=PatientDetailResponse,
    summary="Patient detail (alias without /detail suffix)",
    description=(
        "Alias for /patients/{mpi_id}/detail. "
        "Returns detailed patient data with vitals history (24h), score history, and active alerts."
    ),
)
async def patient_detail_alias(
    mpi_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PatientDetailResponse:
    """Get detailed patient information — alias for frontend compatibility."""
    # ABAC enforcement — same rationale as patient_detail() above (this is a
    # frontend-compatibility alias for the same resource).
    tenant_id = await get_current_tenant_id(request)
    require_abac(
        role_str=current_user.role,
        resource=ResourceType.PATIENT_DEMOGRAPHICS,
        action=Action.READ,
        tenant_id=tenant_id,
        resource_tenant=tenant_id,
    )

    result = await get_patient_detail(db=db, mpi_id=mpi_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient not found: {mpi_id}",
        )
    return result
