"""Antimicrobial Stewardship API Router — REST endpoints for antimicrobial assessment.

4 endpoints conforme contrato OpenAPI (Milestone A2):
  GET    /antimicrobial/assessments            — List (AUDIT-007)
  POST   /antimicrobial/assessments            — Create (auth required)
  GET    /antimicrobial/assessments/{id}       — Get by ID
  GET    /antimicrobial/criteria               — Criteria catalog (cacheable)
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user
from intensicare.core.database import get_db
from intensicare.models.antimicrobial import AntimicrobialAssessment
from intensicare.models.user import User
from intensicare.schemas.antimicrobial import (
    AntimicrobialAssessmentListResponse,
    AntimicrobialAssessmentResponse,
    AntimicrobialCriteriaCatalogResponse,
    AntimicrobialCriterionSchema,
    CreateAntimicrobialAssessmentSchema,
    CriterionCatalogItem,
)
from intensicare.services.domain_antimicrobiano import (
    evaluate_assessment,
    get_categories,
    get_criteria_catalog,
)

router = APIRouter(prefix="/api/v1", tags=["antimicrobial"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_assessment_response(
    assessment: AntimicrobialAssessment,
) -> AntimicrobialAssessmentResponse:
    """Build an AntimicrobialAssessmentResponse from an ORM instance."""
    criteria_data: list[dict] = assessment.criteria or []
    criteria_schemas = [AntimicrobialCriterionSchema(**c) for c in criteria_data]
    return AntimicrobialAssessmentResponse(
        id=assessment.id,
        mpi_id=assessment.mpi_id,
        criteria=criteria_schemas,
        score=assessment.score,
        severity=assessment.severity,
        recommendation=assessment.recommendation,
        assessed_at=assessment.assessed_at,
        assessed_by=assessment.assessed_by,
    )


# ---------------------------------------------------------------------------
# GET /antimicrobial/assessments — List assessments
# ---------------------------------------------------------------------------


@router.get(
    "/antimicrobial/assessments",
    response_model=AntimicrobialAssessmentListResponse,
)
async def list_assessments(
    mpi_id: str | None = Query(None),
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filter by severity band: NEUTRO, AMARELO, VERMELHO",
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AntimicrobialAssessmentListResponse:
    """List antimicrobial assessments with optional filters.

    Follows AUDIT-007 pattern: {items, total}.
    Query params: mpi_id, status (severity), limit, offset.
    """
    base_query = select(AntimicrobialAssessment)

    if mpi_id:
        base_query = base_query.where(AntimicrobialAssessment.mpi_id == mpi_id)
    if status_filter:
        base_query = base_query.where(AntimicrobialAssessment.severity == status_filter)

    # Count query — same filters, no pagination
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total: int = total_result.scalar() or 0

    # Data query with pagination
    data_query = (
        base_query.order_by(AntimicrobialAssessment.assessed_at.desc()).offset(offset).limit(limit)
    )
    result = await db.execute(data_query)
    assessments = result.scalars().all()

    return AntimicrobialAssessmentListResponse(
        items=[_to_assessment_response(a) for a in assessments],
        total=total,
    )


# ---------------------------------------------------------------------------
# POST /antimicrobial/assessments — Create assessment
# ---------------------------------------------------------------------------


@router.post(
    "/antimicrobial/assessments",
    response_model=AntimicrobialAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_assessment(
    body: CreateAntimicrobialAssessmentSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AntimicrobialAssessmentResponse:
    """Create a new antimicrobial stewardship assessment (authenticated).

    Evaluates criteria via the domain service (score + severity + recommendation),
    persists the result in the database, and returns the assessment.
    """
    # Evaluate using domain service
    result = evaluate_assessment(
        mpi_id=body.mpi_id,
        criteria_met=body.criteria_met,
        assessed_by=body.assessed_by or current_user.username,
    )

    # Serialize criteria results as plain dicts for JSONB storage
    criteria_dicts: list[dict] = [
        {
            "id": c.id,
            "name": c.name,
            "category": c.category,
            "description": c.description,
            "met": c.met,
        }
        for c in result.criteria
    ]

    assessment = AntimicrobialAssessment(
        mpi_id=result.mpi_id,
        criteria=criteria_dicts,
        score=result.score,
        severity=result.severity,
        recommendation=result.recommendation,
        assessed_at=result.assessed_at or datetime.now(timezone.utc),
        assessed_by=result.assessed_by,
    )

    db.add(assessment)
    await db.flush()
    await db.refresh(assessment)

    return _to_assessment_response(assessment)


# ---------------------------------------------------------------------------
# GET /antimicrobial/assessments/{assessment_id} — Get single assessment
# ---------------------------------------------------------------------------


@router.get(
    "/antimicrobial/assessments/{assessment_id}",
    response_model=AntimicrobialAssessmentResponse,
)
async def get_assessment(
    assessment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AntimicrobialAssessmentResponse:
    """Get a single antimicrobial assessment by ID.

    Returns 404 if not found.
    """
    result = await db.execute(
        select(AntimicrobialAssessment).where(AntimicrobialAssessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()

    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    return _to_assessment_response(assessment)


# ---------------------------------------------------------------------------
# GET /antimicrobial/criteria — Criteria catalog
# ---------------------------------------------------------------------------


@router.get(
    "/antimicrobial/criteria",
    response_model=AntimicrobialCriteriaCatalogResponse,
)
async def get_criteria_catalog_endpoint() -> AntimicrobialCriteriaCatalogResponse:
    """Return the full antimicrobial criteria catalog (12 criteria).

    Cacheable — criteria definitions are static and do not change per request.
    """
    criteria_raw = get_criteria_catalog()
    categories = get_categories()

    criteria_items = [
        CriterionCatalogItem(
            id=c["id"],
            name=c["name"],
            category=c["category"],
            description=c["description"],
        )
        for c in criteria_raw
    ]

    return AntimicrobialCriteriaCatalogResponse(
        criteria=criteria_items,
        categories=categories,
        total=len(criteria_items),
    )
