"""Hemodynamic Stability API Router — REST endpoints for stability assessment.

2 endpoints conforme contrato OpenAPI (docs/contracts/stability-openapi.yaml):
  GET /patients/{mpi_id}/stability       — Status atual (27 critérios)
  GET /patients/{mpi_id}/stability/trend — Tendência 7 dias

Dados de demonstração injetados diretamente no domain service
(avaliação sintética, sem persistência em banco).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from intensicare.auth.dependencies import get_current_user
from intensicare.models.user import User
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


def _demo_history(
    mpi_id: str, current_score: int, current_severity: str
) -> list[dict[str, Any]]:
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
        sev = (
            "estavel" if score <= 3 else "atencao" if score <= 9 else "critico"
        )
        history.append({
            "score": score,
            "severity": sev,
            "assessed_at": day.isoformat(),
        })

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
    current_user: User = Depends(get_current_user),
) -> StabilityStatusSchema:
    """Estabilidade hemodinâmica atual do paciente.

    Retorna o score de estabilidade atual com os 27 critérios avaliados,
    severidade e recomendações clínicas. Dados calculados com base nos
    sinais vitais e parâmetros hemodinâmicos mais recentes.

    - **mpi_id**: Identificador MPI do paciente (ex: PAT-0042)
    """
    if mpi_id not in _DEMO_MPI_IDS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente {mpi_id} não encontrado",
        )

    clinical_data = _demo_clinical_data(mpi_id)
    result: StabilityEvaluationResult = evaluate_stability(mpi_id, clinical_data)
    return _result_to_status(result)


@router.get(
    "/patients/{mpi_id}/stability/trend",
    response_model=StabilityTrendSchema,
    responses={404: {"description": "Paciente não encontrado"}},
)
async def get_patient_stability_trend(
    mpi_id: str,
    current_user: User = Depends(get_current_user),
) -> StabilityTrendSchema:
    """Tendência de estabilidade hemodinâmica (7 dias).

    Retorna a evolução do score de estabilidade nos últimos 7 dias,
    permitindo identificar deterioração ou melhora ao longo do tempo.

    - **mpi_id**: Identificador MPI do paciente (ex: PAT-0042)
    """
    if mpi_id not in _DEMO_MPI_IDS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente {mpi_id} não encontrado",
        )

    # Avaliação atual
    clinical_data = _demo_clinical_data(mpi_id)
    current_result: StabilityEvaluationResult = evaluate_stability(
        mpi_id, clinical_data
    )
    current_status = _result_to_status(current_result)

    # Histórico sintético 7 dias
    history = _demo_history(
        mpi_id, current_result.score, current_result.severity
    )

    # Tendência via domain service
    trend_data = compute_stability_trend(mpi_id, history)

    # Converte pontos de tendência para schemas Pydantic
    trend_points = [
        StabilityTrendPointSchema(
            date=date.fromisoformat(tp["date"])
            if isinstance(tp["date"], str)
            else tp["date"],
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
