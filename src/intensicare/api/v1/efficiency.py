"""Efficiency & Stewardship API Router — REST endpoint for efficiency assessment.

1 endpoint conforme contrato OpenAPI (eficiencia-openapi.yaml):
  GET    /patients/{mpi_id}/efficiency    — Efficiency assessment (12 rules)

Covers 12 legacy clinical rules:
  - Transfusion appropriateness (12 criteria: TF-001..TF-012)
  - Mechanical restraint monitoring (duration >4h, daily reassessment)
  - Frailty scoring (Clinical Frailty Scale 1–9)
  - ICU LOS benchmarking (expected vs actual, outlier detection)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user
from intensicare.core.database import get_db
from intensicare.models.user import User
from intensicare.services.domain_eficiencia import (
    assess_efficiency,
)

router = APIRouter(prefix="/api/v1", tags=["efficiency"])


# ============================================================================
# Pydantic schemas (aligned with OpenAPI contract eficiencia-openapi.yaml)
# ============================================================================


class TransfusionCriterionSchema(BaseModel):
    """One of the 12 legacy transfusion-appropriateness criteria."""

    code: str = Field(..., description="Short code for the criterion", example="TF-001")
    description: str = Field(..., description="Human-readable description of the criterion")
    met: bool = Field(
        ..., description="Whether this criterion was satisfied for the current transfusion event"
    )
    detail: str | None = Field(
        None, description="Additional clinical context (e.g. actual lab value)"
    )


class RestraintDetailsSchema(BaseModel):
    """Additional mechanical-restraint context."""

    initiated_at: datetime | None = Field(None, description="When restraint was initiated")
    last_reviewed_at: datetime | None = Field(None, description="Last restraint-review timestamp")
    indication: str | None = Field(None, description="Clinical indication for restraint")


class EfficiencyAssessmentResponse(BaseModel):
    """Full resource-efficiency and stewardship assessment response.

    Maps to the OpenAPI EfficiencyAssessment contract.
    """

    id: str = Field(..., description="Unique assessment identifier")
    mpi_id: str = Field(..., description="Master Patient Index identifier")
    patient_name: str | None = Field(
        None, description="Patient display name (optional, for convenience)"
    )
    transfusion_criteria: list[TransfusionCriterionSchema] = Field(
        default_factory=list,
        description="Transfusion appropriateness evaluation (12 criteria)",
    )
    restraint_status: str = Field(..., description="Current mechanical-restraint monitoring status")
    restraint_details: RestraintDetailsSchema | None = Field(
        None, description="Additional mechanical-restraint context"
    )
    frailty_score: float | None = Field(
        None,
        description="Validated frailty score (CFS 1-9, mFI 0-1, or FRAIL 0-5)",
    )
    frailty_scale: str | None = Field(None, description="Frailty instrument used (CFS, mFI, FRAIL)")
    icu_los_days: float = Field(..., description="Current ICU length-of-stay in decimal days")
    icu_los_benchmark: float | None = Field(
        None,
        description="Expected/benchmark ICU LOS for this patient's DRG and severity, in days",
    )
    icu_admission_at: datetime | None = Field(None, description="ICU admission date-time")
    notes: str | None = Field(None, description="Free-text stewardship notes")
    assessed_at: datetime = Field(..., description="Timestamp of this assessment computation")
    assessed_by: str | None = Field(
        None, description="System or user that triggered the assessment"
    )


class EfficiencyErrorResponse(BaseModel):
    """Error response per OpenAPI contract."""

    error: dict[str, Any] = Field(..., description="Error object with code and message")


# ============================================================================
# Helper: build response from domain assessment
# ============================================================================


def _build_efficiency_response(
    mpi_id: str,
    patient_name: str | None = None,
    transfusion_inputs: dict[str, Any] | None = None,
    restraint_inputs: dict[str, Any] | None = None,
    frailty_inputs: dict[str, Any] | None = None,
    los_inputs: dict[str, Any] | None = None,
    assessed_by: str = "system",
) -> EfficiencyAssessmentResponse:
    """Build an EfficiencyAssessmentResponse from domain evaluation results.

    Args:
        mpi_id: Patient identifier.
        patient_name: Optional patient display name.
        transfusion_inputs: Clinical data for transfusion criteria.
        restraint_inputs: Clinical data for mechanical restraint.
        frailty_inputs: Clinical data for frailty scoring.
        los_inputs: Clinical data for LOS benchmarking.
        assessed_by: Identifier for the user/system.

    Returns:
        EfficiencyAssessmentResponse ready for JSON serialization.
    """
    result = assess_efficiency(
        mpi_id=mpi_id,
        transfusion_inputs=transfusion_inputs,
        restraint_inputs=restraint_inputs,
        frailty_inputs=frailty_inputs,
        los_inputs=los_inputs,
        assessed_by=assessed_by,
    )

    # Build transfusion criteria list
    transfusion_criteria = [
        TransfusionCriterionSchema(
            code=c["code"],
            description=c["description"],
            met=c["met"],
            detail=c.get("detail"),
        )
        for c in result.transfusion.get("criteria", [])
    ]

    # Build restraint details
    restraint = result.restraint
    restraint_status = restraint.get("status", "none")
    restraint_details = RestraintDetailsSchema(
        initiated_at=restraint_inputs.get("initiated_at") if restraint_inputs else None,
        last_reviewed_at=restraint_inputs.get("last_reviewed_at") if restraint_inputs else None,
        indication=restraint_inputs.get("indication") if restraint_inputs else None,
    )

    # Frailty
    frailty = result.frailty
    frailty_score = float(frailty["cfs_score"]) if frailty.get("cfs_score") is not None else None
    frailty_scale = frailty.get("scale")

    # LOS
    los = result.los
    icu_los_days = float(los.get("days", 0))
    icu_los_benchmark = (
        float(los["expected_days"]) if los.get("expected_days") is not None else None
    )
    icu_admission_at = los.get("admission_at")

    # Generate assessment ID
    assessment_id = f"EFF-{datetime.now().strftime('%Y%m%d')}-{hash(mpi_id) % 10000:04d}"

    return EfficiencyAssessmentResponse(
        id=assessment_id,
        mpi_id=mpi_id,
        patient_name=patient_name,
        transfusion_criteria=transfusion_criteria,
        restraint_status=restraint_status,
        restraint_details=restraint_details,
        frailty_score=frailty_score,
        frailty_scale=frailty_scale,
        icu_los_days=icu_los_days,
        icu_los_benchmark=icu_los_benchmark,
        icu_admission_at=icu_admission_at,
        notes=result.recommendation,
        assessed_at=result.assessed_at,  # type: ignore[arg-type]
        assessed_by=assessed_by,
    )


# ============================================================================
# GET /patients/{mpi_id}/efficiency — Efficiency assessment
# ============================================================================


@router.get(
    "/patients/{mpi_id}/efficiency",
    response_model=EfficiencyAssessmentResponse,
    responses={
        404: {
            "description": "Patient not found",
            "model": EfficiencyErrorResponse,
        },
        400: {
            "description": "Bad request",
            "model": EfficiencyErrorResponse,
        },
    },
)
async def get_efficiency_assessment(
    mpi_id: str,
    patient_name: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EfficiencyAssessmentResponse:
    """Return the full resource-efficiency and stewardship assessment for a patient.

    Covers 12 legacy rules:
      - Transfusion appropriateness (TF-001..TF-012)
      - Mechanical restraint monitoring
      - Frailty scoring (CFS 1-9)
      - ICU LOS benchmarking

    Args:
        mpi_id: Master Patient Index identifier.
        patient_name: Optional patient display name (query param).
        db: Database session (injected).
        current_user: Authenticated user (injected).

    Returns:
        EfficiencyAssessmentResponse with full evaluation.

    Raises:
        HTTPException 404: If no data is found for the given MPI ID.
        HTTPException 400: If the MPI ID format is invalid.
    """
    # Validate MPI ID format
    if not mpi_id or not mpi_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "Invalid MPI ID format",
                }
            },
        )

    # Build response with default inputs (real clinical data would come from DB)
    # For now, evaluates with empty inputs — criteria default to not met.
    # Future milestones will populate inputs from the data ingestion pipeline.
    try:
        response = _build_efficiency_response(
            mpi_id=mpi_id.strip(),
            patient_name=patient_name,
            assessed_by=current_user.username,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"An unexpected error occurred: {exc!s}",
                }
            },
        ) from exc

    return response
