"""Hemodynamic Stability API Router — REST endpoints for stability assessment.

2 endpoints conforme contrato OpenAPI (docs/contracts/stability-openapi.yaml):
  GET /patients/{mpi_id}/stability       — Status atual (27 critérios)
  GET /patients/{mpi_id}/stability/trend — Tendência 7 dias

Dados de demonstração disponíveis via ?demo=true.
Por padrão (?demo=false), consulta VitalSign hypertable + LabResult para
dados reais do paciente.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user
from intensicare.core.database import get_db
from intensicare.models.lab_result import LabResult
from intensicare.models.user import User
from intensicare.models.vital_sign import VitalSign
from intensicare.schemas.stability import (
    StabilityCriterionSchema,
    StabilityStatusSchema,
    StabilityTrendPointSchema,
    StabilityTrendSchema,
)
from intensicare.services.domain_estabilidade import (
    StabilityCriterionResult,
    StabilityEvaluationResult,
    compute_stability_trend,
    evaluate_stability,
)

router = APIRouter(prefix="/api/v1", tags=["stability"])


# ---------------------------------------------------------------------------
# Demo clinical data — realistic ICU patient snapshot
# ---------------------------------------------------------------------------

# MPI_IDs válidos para demonstração (qualquer outro retorna 404)
_DEMO_MPI_IDS: set[str] = {"PAT-0042", "PAT-0077", "PAT-0101", "PAT-0001"}


def _demo_clinical_data(mpi_id: str) -> dict[str, Any]:
    """Retorna dados clínicos de demonstração para um MPI_ID.

    Cada paciente tem um perfil hemodinâmico distinto para exercitar
    diferentes critérios dos 27 avaliadores.
    """
    base: dict[str, Any] = {
        "lactato_arterial": 3.2,
        "lactato_arterial_anterior": 4.1,
        "lactate_delta_hours": 6.0,
        "lactato_6h": 3.8,
        "saturacao_venosa_mista": 58.0,
        "delta_pco2": 7.2,
        "indice_cardiaco": 1.9,
        "frequencia_cardiaca": 112.0,
        "pressao_arterial_media": 58.0,
        "balanco_hidrico_24h": 3200.0,
        "balanco_hidrico_cumulativo": 4500.0,
        "ppv": 15.0,
        "svv": 14.0,
        "delta_sv_pos_fluid": 6.0,
        "horas_instabilidade_hemodinamica": 8.5,
        "piora_vasopressor_6h": True,
        "piora_perfusao_6h": True,
        "piora_debito_6h": False,
        "piora_fluidos_6h": False,
        "piora_lactato_6h": False,
    }

    # Per-patient overrides for variety
    overrides: dict[str, dict[str, Any]] = {
        "PAT-0077": {
            # Patient improving — fewer criteria triggered
            "lactato_arterial": 1.6,
            "lactato_6h": 1.8,
            "saturacao_venosa_mista": 72.0,
            "delta_pco2": 4.5,
            "indice_cardiaco": 2.8,
            "frequencia_cardiaca": 88.0,
            "pressao_arterial_media": 78.0,
            "balanco_hidrico_24h": 800.0,
            "ppv": 9.0,
            "svv": 8.0,
            "horas_instabilidade_hemodinamica": 2.0,
            "piora_vasopressor_6h": False,
            "piora_perfusao_6h": False,
        },
        "PAT-0101": {
            # Critical patient — many criteria triggered
            "lactato_arterial": 5.8,
            "lactato_6h": 5.2,
            "saturacao_venosa_mista": 48.0,
            "delta_pco2": 9.8,
            "indice_cardiaco": 1.5,
            "frequencia_cardiaca": 138.0,
            "pressao_arterial_media": 49.0,
            "balanco_hidrico_24h": 5200.0,
            "balanco_hidrico_cumulativo": 7800.0,
            "ppv": 18.0,
            "svv": 19.0,
            "delta_sv_pos_fluid": 4.0,
            "horas_instabilidade_hemodinamica": 18.0,
            "piora_vasopressor_6h": True,
            "piora_perfusao_6h": True,
            "piora_debito_6h": True,
            "piora_fluidos_6h": True,
            "piora_lactato_6h": True,
        },
    }

    if mpi_id in overrides:
        base.update(overrides[mpi_id])

    return base


# ---------------------------------------------------------------------------
# Real data pipeline: VitalSign hypertable + LabResult queries
# ---------------------------------------------------------------------------


async def _fetch_real_clinical_data(db: AsyncSession, mpi_id: str) -> dict[str, Any]:
    """Fetch real clinical data from VitalSign hypertable and LabResult table.

    Queries the most recent vital signs and lab results for the patient
    and builds a clinical data dict compatible with evaluate_stability().

    Args:
        db: Async SQLAlchemy session.
        mpi_id: Patient MPI identifier.

    Returns:
        Dict of clinical data suitable for stability evaluation.
    """
    clinical_data: dict[str, Any] = {}

    # ── Fetch most recent vital signs ─────────────────────────────────
    vital_stmt = (
        select(VitalSign)
        .where(VitalSign.mpi_id == mpi_id)
        .order_by(desc(VitalSign.recorded_at))
        .limit(1)
    )
    vital_result = await db.execute(vital_stmt)
    vital = vital_result.scalar_one_or_none()

    if vital is not None:
        clinical_data.update(
            {
                "frequencia_cardiaca": vital.heart_rate,
                "pressao_arterial_media": (
                    _compute_map(vital.systolic_bp, vital.diastolic_bp)
                    if vital.systolic_bp is not None and vital.diastolic_bp is not None
                    else vital.map_value
                ),
                "pressao_arterial_sistolica": vital.systolic_bp,
            }
        )

    # ── Fetch most recent lab results ─────────────────────────────────
    lab_stmt = (
        select(LabResult)
        .where(LabResult.mpi_id == mpi_id)
        .order_by(desc(LabResult.collected_at))
        .limit(20)
    )
    lab_result = await db.execute(lab_stmt)
    labs = lab_result.scalars().all()

    # Map lab analytes to clinical data keys
    _ANALYTE_MAP: dict[str, str] = {
        "lactate": "lactato_arterial",
        "lactato": "lactato_arterial",
        "sv02": "saturacao_venosa_mista",
        "pco2_gap": "delta_pco2",
        "cardiac_index": "indice_cardiaco",
        "creatinine": "creatinina",
        "bilirubin": "bilirrubina",
        "platelets": "plaquetas",
    }

    for lab in labs:
        analyte_lower = (lab.analyte or "").lower().replace(" ", "_").replace("-", "_")
        key = _ANALYTE_MAP.get(analyte_lower)
        if key is not None and lab.value_num is not None:
            clinical_data[key] = lab.value_num

    return clinical_data


def _compute_map(systolic: int | float | None, diastolic: int | float | None) -> float | None:
    """Compute Mean Arterial Pressure (MAP) from systolic and diastolic.

    MAP = DBP + (SBP - DBP) / 3
    """
    if systolic is None or diastolic is None:
        return None
    return diastolic + (systolic - diastolic) / 3.0


# ---------------------------------------------------------------------------
# Conversion helpers: domain dataclass → Pydantic schema
# ---------------------------------------------------------------------------


def _criterion_to_schema(c: StabilityCriterionResult) -> StabilityCriterionSchema:
    """Converte StabilityCriterionResult (dataclass) → StabilityCriterionSchema (Pydantic)."""
    return StabilityCriterionSchema(
        name=c.name,
        value=c.value,
        threshold=c.threshold,
        status=c.status,
        category=c.category,
        alert_id=c.alert_id,
    )


def _result_to_status(result: StabilityEvaluationResult) -> StabilityStatusSchema:
    """Converte StabilityEvaluationResult → StabilityStatusSchema."""
    return StabilityStatusSchema(
        mpi_id=result.mpi_id,
        score=result.score,
        severity=result.severity,
        criteria=[_criterion_to_schema(c) for c in result.criteria],
        recommendation=result.recommendation,
        assessed_at=datetime.fromisoformat(result.assessed_at),
    )


# ---------------------------------------------------------------------------
# Demo history generator — 7 days of trend data
# ---------------------------------------------------------------------------


def _demo_history(mpi_id: str, current_score: int, current_severity: str) -> list[dict[str, Any]]:
    """Gera 7 dias de histórico sintético para demonstração de tendência."""
    today = date.today()
    history: list[dict[str, Any]] = []

    # Build a plausible trajectory
    if current_severity == "critico":
        trajectory = [3, 5, 8, 10, 12, 13, current_score]  # worsening
    elif current_severity == "atencao":
        trajectory = [8, 7, 9, 5, 4, 6, current_score]  # fluctuating
    else:
        trajectory = [2, 1, 3, 1, 0, 1, current_score]  # stable/improving

    for i, score in enumerate(trajectory):
        day = today - timedelta(days=6 - i)
        sev = "estavel" if score <= 3 else "atencao" if score <= 9 else "critico"
        history.append(
            {
                "score": score,
                "severity": sev,
                "assessed_at": day.isoformat(),
            }
        )

    return history


# ============================================================================
# API Endpoints
# ============================================================================


@router.get(
    "/patients/{mpi_id}/stability",
    response_model=StabilityStatusSchema,
    responses={404: {"description": "Paciente não encontrado"}},
)
async def get_patient_stability(
    mpi_id: str,
    demo: bool = Query(
        False,
        description="Use dados de demonstração (true) ou dados reais do banco (false).",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StabilityStatusSchema:
    """Estabilidade hemodinâmica atual do paciente.

    Retorna o score de estabilidade atual com os 27 critérios avaliados,
    severidade e recomendações clínicas.

    Por padrão, consulta VitalSign hypertable + LabResult para dados reais.
    Passe ?demo=true para usar dados sintéticos de demonstração.

    - **mpi_id**: Identificador MPI do paciente (ex: PAT-0042)
    - **demo**: Se true, usa dados de demonstração pré-definidos
    """
    if demo:
        # ── Demo mode: use synthetic data ──────────────────────────
        if mpi_id not in _DEMO_MPI_IDS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente demo {mpi_id} não encontrado. Disponíveis: {sorted(_DEMO_MPI_IDS)}",
            )
        clinical_data = _demo_clinical_data(mpi_id)
    else:
        # ── Real mode: query VitalSign hypertable + LabResult ──────
        clinical_data = await _fetch_real_clinical_data(db, mpi_id)
        if not clinical_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente {mpi_id} não encontrado ou sem dados clínicos recentes.",
            )

    result: StabilityEvaluationResult = evaluate_stability(mpi_id, clinical_data)
    return _result_to_status(result)


@router.get(
    "/patients/{mpi_id}/stability/trend",
    response_model=StabilityTrendSchema,
    responses={404: {"description": "Paciente não encontrado"}},
)
async def get_patient_stability_trend(
    mpi_id: str,
    demo: bool = Query(
        False,
        description="Use dados de demonstração (true) ou dados reais do banco (false).",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StabilityTrendSchema:
    """Tendência de estabilidade hemodinâmica (7 dias).

    Retorna a evolução do score de estabilidade nos últimos 7 dias,
    permitindo identificar deterioração ou melhora ao longo do tempo.

    Por padrão, consulta VitalSign hypertable para dados reais.
    Passe ?demo=true para usar dados sintéticos de demonstração.

    - **mpi_id**: Identificador MPI do paciente (ex: PAT-0042)
    - **demo**: Se true, usa dados de demonstração pré-definidos
    """
    if demo:
        # ── Demo mode ──────────────────────────────────────────────
        if mpi_id not in _DEMO_MPI_IDS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente demo {mpi_id} não encontrado. Disponíveis: {sorted(_DEMO_MPI_IDS)}",
            )
        clinical_data = _demo_clinical_data(mpi_id)
        current_result: StabilityEvaluationResult = evaluate_stability(mpi_id, clinical_data)
        current_status = _result_to_status(current_result)
        history = _demo_history(mpi_id, current_result.score, current_result.severity)
    else:
        # ── Real mode: query VitalSign for trend data ──────────────
        clinical_data = await _fetch_real_clinical_data(db, mpi_id)
        if not clinical_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente {mpi_id} não encontrado ou sem dados clínicos recentes.",
            )
        current_result = evaluate_stability(mpi_id, clinical_data)
        current_status = _result_to_status(current_result)

        # Build trend history from last 7 days of vital signs
        history = await _fetch_real_trend_history(db, mpi_id)

    # Tendência via domain service
    trend_data = compute_stability_trend(mpi_id, history)

    # Converte pontos de tendência para schemas Pydantic
    trend_points = [
        StabilityTrendPointSchema(
            date=date.fromisoformat(tp["date"]) if isinstance(tp["date"], str) else tp["date"],
            score=tp["score"],
            severity=tp["severity"],
            criteria_triggered=tp.get("criteria_triggered", tp["score"]),
        )
        for tp in trend_data.get("trend_points", [])
    ]

    return StabilityTrendSchema(
        mpi_id=mpi_id,
        current=current_status,
        trend=trend_points,
        direction=trend_data.get("direction", "stable"),
        delta_7d=trend_data.get("delta_7d", 0),
    )


# ---------------------------------------------------------------------------
# Real trend history — 7 days of VitalSign snapshots
# ---------------------------------------------------------------------------


async def _fetch_real_trend_history(db: AsyncSession, mpi_id: str) -> list[dict[str, Any]]:
    """Build 7-day trend history from real VitalSign records.

    Queries one vital sign snapshot per day for the last 7 days,
    evaluates stability for each, and returns a history list.

    Args:
        db: Async SQLAlchemy session.
        mpi_id: Patient MPI identifier.

    Returns:
        List of dicts with 'score', 'severity', 'assessed_at' keys.
    """
    today = date.today()
    history: list[dict[str, Any]] = []

    for day_offset in range(6, -1, -1):
        target_date = today - timedelta(days=day_offset)
        day_start = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
        day_end = datetime.combine(target_date, datetime.max.time(), tzinfo=timezone.utc)

        # Get the most recent vital sign for this day
        vital_stmt = (
            select(VitalSign)
            .where(
                VitalSign.mpi_id == mpi_id,
                VitalSign.recorded_at >= day_start,
                VitalSign.recorded_at <= day_end,
            )
            .order_by(desc(VitalSign.recorded_at))
            .limit(1)
        )
        vital_result = await db.execute(vital_stmt)
        vital = vital_result.scalar_one_or_none()

        if vital is not None:
            clinical_data = {
                "frequencia_cardiaca": vital.heart_rate,
                "pressao_arterial_media": (
                    _compute_map(vital.systolic_bp, vital.diastolic_bp)
                    if vital.systolic_bp is not None and vital.diastolic_bp is not None
                    else vital.map_value
                ),
                "pressao_arterial_sistolica": vital.systolic_bp,
            }
            result = evaluate_stability(mpi_id, clinical_data)
            history.append(
                {
                    "score": result.score,
                    "severity": result.severity,
                    "assessed_at": target_date.isoformat(),
                }
            )
        else:
            # No data for this day — use neutral placeholder
            history.append(
                {
                    "score": 0,
                    "severity": "estavel",
                    "assessed_at": target_date.isoformat(),
                }
            )

    return history
