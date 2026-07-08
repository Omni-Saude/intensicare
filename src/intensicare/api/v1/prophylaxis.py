"""Prophylaxis Bundles API — 5 ICU bundles with scoring and criteria catalog.

Endpoints:
  GET  /prophylaxis/bundles                    — list all 5 bundles for a patient
  GET  /prophylaxis/bundles/{bundle_id}        — get a specific bundle assessment
  PUT  /prophylaxis/bundles/{bundle_id}        — update bundle criteria (upsert)
  GET  /prophylaxis/bundles/{bundle_id}/criteria — static criteria catalog
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user
from intensicare.core.database import get_db
from intensicare.models.prophylaxis import ProphylaxisAssessment
from intensicare.models.user import User
from intensicare.schemas.prophylaxis import (
    BundleCatalogResponse,
    BundleCriterionSchema,
    ProphylaxisBundleResponse,
    ProphylaxisBundlesListResponse,
    ProphylaxisBundleUpdateRequest,
)
from intensicare.services.domain_profilaxia import (
    BUNDLE_CATALOG,
    evaluate_all_bundles,
    evaluate_bundle,
    get_bundle_catalog,
)

router = APIRouter(prefix="/api/v1", tags=["prophylaxis"])

VALID_BUNDLE_IDS = frozenset(BUNDLE_CATALOG.keys())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _criteria_to_schema(criteria: list) -> list[BundleCriterionSchema]:
    """Convert service criteria (CriterionResult dataclass or dict) to pydantic schema."""
    result: list[BundleCriterionSchema] = []
    for c in criteria:
        if hasattr(c, "label"):
            # CriterionResult dataclass from domain service
            result.append(BundleCriterionSchema(
                id=c.id,
                label=c.label,
                met=c.met,
                na=c.na,
            ))
        else:
            # Plain dict (fallback)
            result.append(BundleCriterionSchema(
                id=c["id"],
                label=c["label"],
                met=c.get("met", False),
                na=c.get("na", False),
            ))
    return result


def _build_bundle_response(
    bundle_result,
    assessed_at: datetime | None = None,
    assessed_by: str | None = None,
) -> ProphylaxisBundleResponse:
    """Build a ProphylaxisBundleResponse from a service BundleResult."""
    return ProphylaxisBundleResponse(
        id=bundle_result.id,
        name=bundle_result.name,
        status=bundle_result.status,
        score=bundle_result.score,
        criteria=_criteria_to_schema(bundle_result.criteria),
        assessed_at=assessed_at,
        assessed_by=assessed_by,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/prophylaxis/bundles",
    response_model=ProphylaxisBundlesListResponse,
)
async def list_prophylaxis_bundles(
    mpi_id: str = Query(..., description="Patient MPI ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProphylaxisBundlesListResponse:
    """List all 5 prophylaxis bundle assessments for a patient.

    Returns existing assessments from the database, falling back to
    computed defaults (all pending, score 0) for bundles that have not
    been assessed yet.
    """
    # Query existing assessments for this patient
    result = await db.execute(
        select(ProphylaxisAssessment).where(
            ProphylaxisAssessment.mpi_id == mpi_id,
        ),
    )
    existing: dict[str, ProphylaxisAssessment] = {
        row.bundle_id: row for row in result.scalars().all()
    }

    # Build bundle inputs from existing rows for evaluate_all_bundles
    bundle_inputs: dict[str, list] = {}
    for bundle_id, row in existing.items():
        if row.criteria:
            # Model type-hint is dict[str, Any] but JSONB arrays are Python lists at runtime
            bundle_inputs[bundle_id] = row.criteria  # type: ignore[assignment]

    # Evaluate all 5 bundles (with overrides from DB where available)
    bundles_result = evaluate_all_bundles(bundle_inputs)

    # Build response list, merging timestamps from DB rows
    response_bundles: list[ProphylaxisBundleResponse] = []
    for br in bundles_result.bundles:
        db_row = existing.get(br.id)
        response_bundles.append(_build_bundle_response(
            br,
            assessed_at=db_row.assessed_at if db_row else None,
            assessed_by=db_row.assessed_by if db_row else None,
        ))

    return ProphylaxisBundlesListResponse(
        bundles=response_bundles,
        overall_status=bundles_result.overall_status,
        overall_score=bundles_result.overall_score,
    )


@router.get(
    "/prophylaxis/bundles/{bundle_id}",
    response_model=ProphylaxisBundleResponse,
)
async def get_prophylaxis_bundle(
    bundle_id: str,
    mpi_id: str = Query(..., description="Patient MPI ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProphylaxisBundleResponse:
    """Get a specific prophylaxis bundle assessment for a patient.

    Returns 404 if the bundle has not been assessed yet or if the
    bundle_id is invalid.
    """
    if bundle_id not in VALID_BUNDLE_IDS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Unknown bundle_id: {bundle_id}. "
                f"Valid: {', '.join(sorted(VALID_BUNDLE_IDS))}"
            ),
        )

    result = await db.execute(
        select(ProphylaxisAssessment).where(
            ProphylaxisAssessment.mpi_id == mpi_id,
            ProphylaxisAssessment.bundle_id == bundle_id,
        ),
    )
    row = result.scalar_one_or_none()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No assessment found for bundle '{bundle_id}' and patient '{mpi_id}'",
        )

    # Re-evaluate to get full criteria with labels from the catalog
    bundle_result = evaluate_bundle(bundle_id, row.criteria)  # type: ignore[arg-type]

    return _build_bundle_response(
        bundle_result,
        assessed_at=row.assessed_at,
        assessed_by=row.assessed_by,
    )


@router.put(
    "/prophylaxis/bundles/{bundle_id}",
    response_model=ProphylaxisBundleResponse,
)
async def update_prophylaxis_bundle(
    bundle_id: str,
    body: ProphylaxisBundleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProphylaxisBundleResponse:
    """Update a prophylaxis bundle assessment (upsert).

    Evaluates the provided criteria, computes score and status via the
    domain service, and persists the result to the database.  Creates a
    new assessment row if one does not already exist for this patient
    and bundle.
    """
    if bundle_id not in VALID_BUNDLE_IDS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Unknown bundle_id: {bundle_id}. "
                f"Valid: {', '.join(sorted(VALID_BUNDLE_IDS))}"
            ),
        )

    # Evaluate the bundle with the provided criteria inputs
    criteria_inputs = [{"id": c.id, "met": c.met} for c in body.criteria]
    bundle_result = evaluate_bundle(bundle_id, criteria_inputs)

    # Convert CriterionResult dataclasses to JSONB-compatible dicts
    criteria_jsonb = [
        {"id": c.id, "label": c.label, "met": c.met, "na": c.na}
        for c in bundle_result.criteria
    ]

    now = datetime.now(timezone.utc)

    # Upsert: try to find existing row
    result = await db.execute(
        select(ProphylaxisAssessment).where(
            ProphylaxisAssessment.mpi_id == body.mpi_id,
            ProphylaxisAssessment.bundle_id == bundle_id,
        ),
    )
    row = result.scalar_one_or_none()

    if row is None:
        # Create new assessment
        row = ProphylaxisAssessment(
            mpi_id=body.mpi_id,
            bundle_id=bundle_id,
            criteria=criteria_jsonb,
            status=bundle_result.status,
            score=bundle_result.score,
            assessed_at=now,
            assessed_by=current_user.username,
        )
        db.add(row)
    else:
        # Update existing
        row.criteria = criteria_jsonb  # type: ignore[assignment]
        row.status = bundle_result.status
        row.score = bundle_result.score
        row.assessed_at = now
        row.assessed_by = current_user.username

    await db.flush()
    await db.refresh(row)

    return _build_bundle_response(
        bundle_result,
        assessed_at=row.assessed_at,
        assessed_by=row.assessed_by,
    )


@router.get(
    "/prophylaxis/bundles/{bundle_id}/criteria",
    response_model=BundleCatalogResponse,
)
async def get_bundle_criteria_catalog(
    bundle_id: str,
) -> BundleCatalogResponse:
    """Return the static criteria catalog for a prophylaxis bundle.

    This endpoint is cacheable — the criteria definitions are immutable
    and do not depend on any patient data.
    """
    if bundle_id not in VALID_BUNDLE_IDS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Unknown bundle_id: {bundle_id}. "
                f"Valid: {', '.join(sorted(VALID_BUNDLE_IDS))}"
            ),
        )

    catalog = get_bundle_catalog(bundle_id)
    return BundleCatalogResponse(**catalog)
