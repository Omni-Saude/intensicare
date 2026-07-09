"""Clinical Forms API Router — RASS, SOFA, CAM-ICU, Glasgow, BPS/NRS.

3 endpoints conforme contrato OpenAPI (PASSO 2.2):
  GET    /clinical-forms                             — List form types
  GET    /patients/{mpi_id}/clinical-forms           — List submissions
  POST   /patients/{mpi_id}/clinical-forms            — Submit a form
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status

from intensicare.auth.dependencies import get_current_user
from intensicare.models.user import User
from intensicare.schemas.clinical_forms_extended import (
    ClinicalFormSubmissionListResponse,
    ClinicalFormSubmissionSchema,
    ClinicalFormSubmitRequest,
    ClinicalFormTypeListResponse,
    ClinicalFormTypeSchema,
)
from intensicare.services.domain_formularios import (
    CrossFieldValidationError,
    FormSubmissionResult,
    FormTypeInfo,
    get_form_types,
    list_submissions,
    submit_form,
)

router = APIRouter(prefix="/api/v1", tags=["formularios"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _form_type_to_schema(ft: FormTypeInfo) -> ClinicalFormTypeSchema:
    """Convert a domain FormTypeInfo to a Pydantic ClinicalFormTypeSchema."""
    return ClinicalFormTypeSchema(
        id=ft.id,
        name=ft.name,
        description=ft.description,
        version=ft.version,
        active=ft.active,
        score_range=None,
        fields=[],
    )


def _submission_to_schema(sub: FormSubmissionResult) -> ClinicalFormSubmissionSchema:
    """Convert a domain FormSubmissionResult to a Pydantic ClinicalFormSubmissionSchema."""
    return ClinicalFormSubmissionSchema(
        id=sub.id or 0,
        mpi_id=sub.mpi_id,
        form_id=sub.form_id,
        form_type=sub.form_type,
        data=sub.data,
        score=Decimal(str(sub.score)) if sub.score is not None else None,
        severity=sub.severity,
        submitted_by=sub.submitted_by,
        submitted_at=datetime.fromisoformat(sub.submitted_at)
        if sub.submitted_at
        else datetime.now(timezone.utc),
        version=sub.version,
        definition_version=sub.definition_version,
    )


# ---------------------------------------------------------------------------
# GET /clinical-forms — List form types
# ---------------------------------------------------------------------------


@router.get(
    "/clinical-forms",
    response_model=ClinicalFormTypeListResponse,
)
async def list_form_types_endpoint(
    current_user: User = Depends(get_current_user),
) -> ClinicalFormTypeListResponse:
    """List all available clinical form types (RASS, CAM-ICU, BPS/NRS, Glasgow, SOFA).

    Returns form definitions with metadata.
    Follows AUDIT-007 pattern: {items, total}.
    """
    result = get_form_types()

    return ClinicalFormTypeListResponse(
        items=[_form_type_to_schema(ft) for ft in result.items],
        total=result.total,
    )


# ---------------------------------------------------------------------------
# GET /patients/{mpi_id}/clinical-forms — List submissions
# ---------------------------------------------------------------------------


@router.get(
    "/patients/{mpi_id}/clinical-forms",
    response_model=ClinicalFormSubmissionListResponse,
)
async def list_submissions_endpoint(
    mpi_id: str,
    form_id: str | None = Query(
        None,
        description="Filter by form type: rass, cam-icu, bps-nrs, glasgow, sofa",
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
) -> ClinicalFormSubmissionListResponse:
    """List clinical form submissions for a patient.

    Supports optional filter by form_id (form type) and pagination.
    Follows AUDIT-007 pattern: {items, total}.
    """
    result = list_submissions(
        mpi_id=mpi_id,
        form_id=form_id,
        limit=limit,
        offset=offset,
    )

    return ClinicalFormSubmissionListResponse(
        items=[_submission_to_schema(s) for s in result.items],
        total=result.total,
    )


# ---------------------------------------------------------------------------
# POST /patients/{mpi_id}/clinical-forms — Submit a form
# ---------------------------------------------------------------------------


@router.post(
    "/patients/{mpi_id}/clinical-forms",
    response_model=ClinicalFormSubmissionSchema,
    status_code=status.HTTP_201_CREATED,
)
async def submit_form_endpoint(
    mpi_id: str,
    body: ClinicalFormSubmitRequest,
    current_user: User = Depends(get_current_user),
) -> ClinicalFormSubmissionSchema:
    """Submit a new clinical form for a patient.

    The form_type determines which scoring engine is used
    (RASS, CAM-ICU, BPS/NRS, Glasgow, SOFA).

    Returns 400 if the form_type is unknown.
    """
    try:
        result = submit_form(
            mpi_id=mpi_id,
            form_id=body.form_type,  # form_type serves as both type and id
            form_type=body.form_type,
            data=body.data,
            submitted_by=current_user.username,
            definition_version=body.definition_version,
        )
    except CrossFieldValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return _submission_to_schema(result)
