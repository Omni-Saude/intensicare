"""Clinical Deterioration API Router.

GET /patients/{mpi_id}/deterioration      — score atual
GET /patients/{mpi_id}/deterioration/history — histórico paginado
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user
from intensicare.core.database import get_db
from intensicare.models.deterioration import DeteriorationAssessment
from intensicare.models.user import User
from intensicare.models.vital_sign import VitalSign
from intensicare.schemas.deterioration import (
    DeteriorationCriteriaSchema,
    DeteriorationHistoryResponse,
    DeteriorationScoreSchema,
)
from intensicare.services.domain_piora_clinica import evaluate_deterioration

router = APIRouter(prefix="/api/v1", tags=["deterioration"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_clinical_data(vital: VitalSign) -> dict:
    """Convert a VitalSign ORM row into the clinical_data dict expected by the
    deterioration domain service.

    Maps VitalSign columns → domain keys used by the 13 criteria evaluators.
    """
    return {
        # ── Respiratory ──────────────────────────────────────────
        "saturacao_o2": vital.spo2,
        "fio2": None,  # not in VitalSign — evaluate_respiratory may provide
        "pao2_fio2": vital.pao2_fio2,
        "relacao_spo2_fio2": None,  # derived by domain if needed
        "frequencia_respiratoria": vital.respiratory_rate,
        # ── Hemodynamic ──────────────────────────────────────────
        "pressao_arterial_media": vital.map_value,
        "pressao_arterial_sistolica": vital.systolic_bp,
        "frequencia_cardiaca": vital.heart_rate,
        "dose_vasopressor": vital.vasopressor_dose_mcg_kg_min,
        "dose_vasopressor_basal": None,
        "indice_choque": None,  # computed by evaluator
        "indice_choque_2h_ago": None,
        # ── Sepsis / labs ────────────────────────────────────────
        "glasgow": vital.gcs,
        "lactato_arterial": None,  # not in VitalSign — from LabResult
        "procalcitonina": None,
        "creatinina": vital.creatinine,
        "creatinina_basal": None,
        "diurese_ml_kg_h": None,  # derived from urine_output
        "rass": None,
        "rass_anterior": None,
        # ── Trend keys (previous values for delta criteria) ──────
        "pao2_fio2_6h_ago": None,
        "relacao_spo2_fio2_6h_ago": None,
        "fio2_6h_ago": None,
        "saturacao_o2_6h_ago": None,
        "frequencia_respiratoria_2h_ago": None,
        "pressao_arterial_media_1h_ago": None,
        "glasgow_24h_ago": None,
        "qsofa": None,
        "qsofa_24h_ago": None,
        "lactato_arterial_anterior": None,
        "lactate_delta_hours": None,
        "procalcitonina_anterior": None,
        "atb_ativa_horas": None,
    }


def _to_score_schema(asmnt: DeteriorationAssessment) -> DeteriorationScoreSchema:
    """Map a DeteriorationAssessment ORM row → DeteriorationScoreSchema."""
    criteria_schemas = [
        DeteriorationCriteriaSchema(
            domain=c.get("domain", ""),
            name=c.get("name", ""),
            status=c.get("status", "normal"),
            value=c.get("value"),
            threshold=c.get("threshold"),
            alert_id=c.get("alert_id"),
        )
        for c in (asmnt.criteria or [])
    ]
    return DeteriorationScoreSchema(
        id=asmnt.id,
        mpi_id=asmnt.mpi_id,
        score=asmnt.score,
        trend=asmnt.trend,
        criteria=criteria_schemas,
        domains_affected=asmnt.domains_affected,
        recommendation=asmnt.recommendation,
        assessed_at=asmnt.assessed_at,
        assessed_by=asmnt.assessed_by,
    )


def _result_to_score_schema(
    result, mpi_id: str
) -> DeteriorationScoreSchema:
    """Map a DeteriorationEvaluationResult (domain service) → DeteriorationScoreSchema."""
    criteria_schemas = [
        DeteriorationCriteriaSchema(
            domain=c.domain,
            name=c.name,
            status=c.status,
            value=c.value,
            threshold=c.threshold,
            alert_id=c.alert_id,
        )
        for c in (result.criteria or [])
    ]
    assessed_at = result.assessed_at
    if isinstance(assessed_at, str):
        assessed_at = datetime.fromisoformat(assessed_at)
    return DeteriorationScoreSchema(
        id=0,  # computed on-the-fly — not yet persisted
        mpi_id=mpi_id,
        score=result.score,
        trend=result.trend,
        criteria=criteria_schemas,
        domains_affected=result.domains_affected,
        recommendation=result.recommendation,
        assessed_at=assessed_at,
        assessed_by=result.assessed_by,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/patients/{mpi_id}/deterioration",
    response_model=DeteriorationScoreSchema,
    summary="Score de deterioração clínica atual",
)
async def get_patient_deterioration(
    mpi_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DeteriorationScoreSchema:
    """Retorna o score de deterioração clínica atual do paciente.

    Calculado a partir de múltiplos domínios (respiratório, hemodinâmico,
    sepse, neurológico, renal) usando 13 critérios de deterioração.

    Se nenhuma avaliação persistida existir, calcula sob demanda a partir
    dos sinais vitais mais recentes.
    """
    # 1. Try latest persisted assessment
    stmt = (
        select(DeteriorationAssessment)
        .where(DeteriorationAssessment.mpi_id == mpi_id)
        .order_by(DeteriorationAssessment.assessed_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    assessment = result.scalar_one_or_none()

    if assessment is not None:
        return _to_score_schema(assessment)

    # 2. No persisted assessment — compute from latest vitals
    vital_stmt = (
        select(VitalSign)
        .where(VitalSign.mpi_id == mpi_id)
        .order_by(VitalSign.recorded_at.desc())
        .limit(1)
    )
    vital_result = await db.execute(vital_stmt)
    vital = vital_result.scalar_one_or_none()

    if vital is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente '{mpi_id}' não encontrado ou sem sinais vitais.",
        )

    clinical_data = _build_clinical_data(vital)
    evaluation = evaluate_deterioration(mpi_id, clinical_data)
    return _result_to_score_schema(evaluation, mpi_id)


@router.get(
    "/patients/{mpi_id}/deterioration/history",
    response_model=DeteriorationHistoryResponse,
    summary="Histórico de scores de deterioração",
)
async def get_patient_deterioration_history(
    mpi_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DeteriorationHistoryResponse:
    """Retorna histórico paginado de avaliações de deterioração clínica.

    Ordenado por data de avaliação (mais recente primeiro).
    """
    # Check patient has at least one assessment
    base_stmt = (
        select(DeteriorationAssessment)
        .where(DeteriorationAssessment.mpi_id == mpi_id)
    )

    # Count
    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    if total == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhuma avaliação de deterioração encontrada para '{mpi_id}'.",
        )

    # Fetch page
    data_stmt = (
        base_stmt
        .order_by(DeteriorationAssessment.assessed_at.desc())
        .offset(offset)
        .limit(limit)
    )
    data_result = await db.execute(data_stmt)
    assessments = data_result.scalars().all()

    return DeteriorationHistoryResponse(
        items=[_to_score_schema(a) for a in assessments],
        total=total,
    )
