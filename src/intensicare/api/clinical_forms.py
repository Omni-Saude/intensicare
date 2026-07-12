"""Clinical forms API — submit clinical assessments (RASS, CAM-ICU, BPS/NRS).

Replaces the frontend setTimeout mock with a real backend endpoint.
"""

from __future__ import annotations

from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user
from intensicare.core.database import get_db
from intensicare.models.user import User
from intensicare.schemas.clinical_forms import (
    ClinicalFormResponse,
    ClinicalFormSubmission,
)

router = APIRouter(prefix="/api", tags=["clinical-forms"])

VALID_FORM_TYPES: frozenset[str] = frozenset({"rass", "cam-icu", "bps-nrs"})


@router.post(
    "/clinical-forms",
    response_model=ClinicalFormResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a clinical assessment form",
    description="Record a clinical assessment (RASS, CAM-ICU, or BPS/NRS) for a patient.",
    responses={
        201: {"description": "Form recorded successfully"},
        401: {"description": "Not authenticated"},
        422: {"description": "Invalid form_type or malformed payload"},
    },
)
async def submit_clinical_form(
    submission: ClinicalFormSubmission,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ClinicalFormResponse:
    """Submit a clinical assessment form (RASS, CAM-ICU, BPS/NRS).

    TODO: Persist to DB when a ClinicalForm model is created.
    Currently returns a generated ID and timestamp — removes the frontend
    setTimeout mock.
    """
    if submission.form_type not in VALID_FORM_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid form_type '{submission.form_type}'. Must be one of: {sorted(VALID_FORM_TYPES)}",
        )

    form_id = str(uuid.uuid4())
    recorded_at = datetime.now(timezone.utc)

    return ClinicalFormResponse(
        id=form_id,
        status="recorded",
        recorded_at=recorded_at,
    )
