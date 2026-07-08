"""Sedation Monitoring API Router — RASS, BPS/NRS, CAM-ICU assessments.

2 endpoints conforme contrato OpenAPI (PASSO 2.2):
  GET    /patients/{mpi_id}/sedation              — Current assessment
  GET    /patients/{mpi_id}/sedation/history       — Paginated history
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user
from intensicare.core.database import get_db
from intensicare.models.user import User
from intensicare.schemas.sedacao import (
    SedationAssessmentListResponse,
    SedationAssessmentSchema,
)
from intensicare.services.domain_sedacao import (
    SedationRecord,
    get_current_sedation,
    list_sedation_history,
)

router = APIRouter(prefix="/api/v1", tags=["sedacao"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _record_to_schema(record: SedationRecord) -> SedationAssessmentSchema:
    """Convert a domain SedationRecord to a Pydantic SedationAssessmentSchema."""
    cam_features_dict = None
    if record.cam_icu_features is not None:
        cam_features_dict = record.cam_icu_features.to_dict()

    assessed_at_dt = datetime.now(timezone.utc)
    if record.assessed_at:
        try:
            assessed_at_dt = datetime.fromisoformat(record.assessed_at)
        except (ValueError, TypeError):
            assessed_at_dt = datetime.now(timezone.utc)

    return SedationAssessmentSchema(
        id=record.id or 0,
        mpi_id=record.mpi_id,
        rass_score=record.rass_score,
        rass_label=record.rass_label,
        bps_score=record.bps_score,
        nrs_score=record.nrs_score,
        cam_icu_positive=record.cam_icu_positive,
        cam_icu_features=cam_features_dict,
        current_sedation=record.current_sedation,
        assessed_by=record.assessed_by,
        assessed_at=assessed_at_dt,
        notes=record.notes,
    )


# ---------------------------------------------------------------------------
# GET /patients/{mpi_id}/sedation — Current assessment
# ---------------------------------------------------------------------------


@router.get(
    "/patients/{mpi_id}/sedation",
    response_model=SedationAssessmentSchema,
)
async def get_current_sedation_endpoint(
    mpi_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SedationAssessmentSchema:
    """Get the most recent sedation assessment for a patient.

    Returns 404 if no assessment exists for the patient.
    """
    record = await get_current_sedation(db=db, mpi_id=mpi_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No sedation assessment found for patient {mpi_id}",
        )

    return _record_to_schema(record)


# ---------------------------------------------------------------------------
# GET /patients/{mpi_id}/sedation/history — Paginated history
# ---------------------------------------------------------------------------


@router.get(
    "/patients/{mpi_id}/sedation/history",
    response_model=SedationAssessmentListResponse,
)
async def list_sedation_history_endpoint(
    mpi_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SedationAssessmentListResponse:
    """List sedation assessment history for a patient, paginated.

    Returns assessments ordered by date descending (most recent first).
    Follows AUDIT-007 pattern: {data, total}.
    """
    result = await list_sedation_history(
        db=db,
        mpi_id=mpi_id,
        limit=limit,
        offset=offset,
    )

    return SedationAssessmentListResponse(
        data=[_record_to_schema(r) for r in result.items],
        total=result.total,
        limit=limit,
        offset=offset,
    )
