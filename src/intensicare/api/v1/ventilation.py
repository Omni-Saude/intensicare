"""Ventilation Monitoring API Router.

2 endpoints conforme contrato OpenAPI (docs/contracts/ventilation-openapi.yaml):
  GET /patients/{mpi_id}/ventilation         — parâmetros atuais + tendência 24h
  GET /patients/{mpi_id}/ventilation/history  — histórico paginado
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from intensicare.auth.dependencies import get_current_user
from intensicare.models.user import User
from intensicare.services.domain_ventilacao import (
    evaluate_ventilation,
    VentilationResult,
)

router = APIRouter(prefix="/api/v1", tags=["ventilation"])


# ---------------------------------------------------------------------------
# Pydantic models (inline, matching OpenAPI contract)
# ---------------------------------------------------------------------------


class VentilationParametersSchema(BaseModel):
    """Current ventilation parameters (single reading)."""

    id: int | None = None
    mpi_id: str = ""
    mode: str | None = None
    FiO2: float | None = Field(None, ge=0.21, le=1.0)
    PEEP: float | None = Field(None, ge=0, le=40)
    VC: float | None = Field(None, ge=0)
    FR: int | None = Field(None, ge=0)
    Pplat: float | None = Field(None, ge=0, le=60)
    driving_pressure: float | None = Field(None, ge=0)
    PaO2_FiO2_ratio: float | None = Field(None, ge=0)
    SpO2: int | None = Field(None, ge=0, le=100)
    tidal_volume_per_kg_pbw: float | None = None
    spontaneous_rate: int | None = Field(None, ge=0)
    collected_at: str = ""
    source: str = "prontuario"


class SeriesPoint(BaseModel):
    """Single point in a parameter time series."""

    value: float
    collected_at: str


class ParameterTrendSchema(BaseModel):
    """Trend data for a single parameter."""

    current: float | None = None
    min: float | None = None
    max: float | None = None
    avg: float | None = None
    direction: str = "stable"
    change_pct: float | None = None
    series: list[SeriesPoint] = Field(default_factory=list)


class VentilationTrendSchema(BaseModel):
    """24-hour trend for all ventilation parameters."""

    period_hours: int = 24
    start_time: str = ""
    end_time: str = ""
    parameters: dict[str, ParameterTrendSchema] = Field(default_factory=dict)


class VentilationResponse(BaseModel):
    """GET /patients/{mpi_id}/ventilation response."""

    parameters: VentilationParametersSchema
    trend: VentilationTrendSchema
    collected_at: str


class VentilationHistoryResponse(BaseModel):
    """GET /patients/{mpi_id}/ventilation/history response."""

    items: list[VentilationParametersSchema]
    total: int


# ---------------------------------------------------------------------------
# Sample in-memory data (for testing — no database yet)
# ---------------------------------------------------------------------------

_SAMPLE_PATIENTS: dict[str, dict[str, Any]] = {
    "MPI-001": {
        "id": 3,
        "mpi_id": "MPI-001",
        "modo_ventilatorio": "PCV",
        "fio2": 0.35,
        "peep": 8.0,
        "volume_corrente": 450.0,
        "frequencia_respiratoria": 16,
        "pplat": 20.0,
        "pao2": 85.0,
        "saturacao_o2": 96,
        "vc_por_kg_pbw": 6.5,
        "fr_espontanea": 2,
        "collected_at": "2026-07-07T10:00:00+00:00",
        "source": "prontuario",
    },
    "LEITO-01": {
        "id": 4,
        "mpi_id": "LEITO-01",
        "modo_ventilatorio": "VCV",
        "fio2": 0.45,
        "peep": 10.0,
        "volume_corrente": 400.0,
        "frequencia_respiratoria": 20,
        "pplat": 24.0,
        "pao2": 70.0,
        "saturacao_o2": 92,
        "vc_por_kg_pbw": 6.0,
        "fr_espontanea": 3,
        "collected_at": "2026-07-07T09:45:00+00:00",
        "source": "prontuario",
    },
    "PAT-0042": {
        "id": 1,
        "mpi_id": "PAT-0042",
        "modo_ventilatorio": "PCV",
        "fio2": 0.40,
        "peep": 8.0,
        "volume_corrente": 420.0,
        "frequencia_respiratoria": 18,
        "pplat": 22.0,
        "pao2": 74.0,
        "saturacao_o2": 94,
        "vc_por_kg_pbw": 6.2,
        "fr_espontanea": 4,
        "collected_at": "2026-07-07T10:00:00+00:00",
        "source": "prontuario",
    },
    "PAT-0100": {
        "id": 2,
        "mpi_id": "PAT-0100",
        "modo_ventilatorio": "VCV",
        "fio2": 0.60,
        "peep": 12.0,
        "volume_corrente": 380.0,
        "frequencia_respiratoria": 22,
        "pplat": 28.0,
        "pao2": 65.0,
        "saturacao_o2": 88,
        "vc_por_kg_pbw": 5.8,
        "fr_espontanea": 0,
        "collected_at": "2026-07-07T09:30:00+00:00",
        "source": "ventilator",
    },
}


def _build_history(base_entry: dict[str, Any], num_entries: int = 30) -> list[dict[str, Any]]:
    """Generate simulated history entries for trend analysis.

    Creates entries going back from the current reading, with slight
    random-like variations to simulate real clinical fluctuations.
    """
    history: list[dict[str, Any]] = []
    base_time = datetime(2026, 7, 7, 10, 0, 0, tzinfo=timezone.utc)

    # Parameter ranges for variation
    fio2_base = float(base_entry.get("fio2", 0.40))
    peep_base = float(base_entry.get("peep", 8.0))
    vc_base = float(base_entry.get("volume_corrente", 420.0))
    fr_base = int(base_entry.get("frequencia_respiratoria", 18))
    pplat_base = float(base_entry.get("pplat", 22.0))
    pao2_base = float(base_entry.get("pao2", 74.0))

    for i in range(num_entries):
        offset_hours = (num_entries - 1 - i) * 1.5  # ~45 min between readings
        entry_time = base_time - timedelta(hours=offset_hours)

        # Small deterministic variation based on position
        # Use a simple pattern: slightly improving over time
        progress = i / max(num_entries - 1, 1)  # 0..1
        jitter_fio2 = (-0.02 + progress * 0.04)  # FiO2 weaning
        jitter_peep = (-1.0 + progress * 2.0)
        jitter_vc = (5.0 - progress * 10.0)
        jitter_fr = int(-2 + progress * 4)
        jitter_pplat = (-1.5 + progress * 3.0)
        jitter_pao2 = (3.0 - progress * 6.0)

        entry = {
            "id": base_entry.get("id", 0) + i + 1,
            "mpi_id": base_entry.get("mpi_id", ""),
            "modo_ventilatorio": base_entry.get("modo_ventilatorio", "PCV"),
            "fio2": round(fio2_base + jitter_fio2, 2),
            "peep": round(peep_base + jitter_peep, 1),
            "volume_corrente": round(vc_base + jitter_vc, 1),
            "frequencia_respiratoria": fr_base + jitter_fr,
            "pplat": round(pplat_base + jitter_pplat, 1),
            "pao2": round(pao2_base + jitter_pao2, 1),
            "saturacao_o2": base_entry.get("saturacao_o2", 94),
            "vc_por_kg_pbw": base_entry.get("vc_por_kg_pbw"),
            "fr_espontanea": base_entry.get("fr_espontanea"),
            "collected_at": entry_time.isoformat(),
            "source": base_entry.get("source", "prontuario"),
        }
        history.append(entry)

    return history


# Pre-built sample history for each sample patient
_SAMPLE_HISTORY: dict[str, list[dict[str, Any]]] = {
    mpi_id: _build_history(entry) for mpi_id, entry in _SAMPLE_PATIENTS.items()
}


# ---------------------------------------------------------------------------
# GET /patients/{mpi_id}/ventilation — Current parameters + trend
# ---------------------------------------------------------------------------


@router.get(
    "/patients/{mpi_id}/ventilation",
    response_model=VentilationResponse,
)
async def get_patient_ventilation(
    mpi_id: str,
    trend_hours: int = Query(24, ge=1, le=72),
    current_user: User = Depends(get_current_user),
) -> VentilationResponse:
    """Parâmetros ventilatórios atuais e tendência de 24 horas.

    Retorna os parâmetros atuais do ventilador mecânico do paciente
    (última leitura disponível) e a tendência das últimas N horas
    para cada parâmetro.
    """
    current_data = _SAMPLE_PATIENTS.get(mpi_id)
    if current_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {mpi_id} not found",
        )

    history = _SAMPLE_HISTORY.get(mpi_id, [])

    result: VentilationResult = evaluate_ventilation(
        mpi_id=mpi_id,
        current_data=current_data,
        history=history,
        trend_hours=trend_hours,
    )

    # Convert domain dataclasses → Pydantic schemas
    p = result.parameters
    t = result.trend

    params_schema = VentilationParametersSchema(
        id=p.id,
        mpi_id=p.mpi_id,
        mode=p.mode,
        FiO2=p.FiO2,
        PEEP=p.PEEP,
        VC=p.VC,
        FR=p.FR,
        Pplat=p.Pplat,
        driving_pressure=p.driving_pressure,
        PaO2_FiO2_ratio=p.PaO2_FiO2_ratio,
        SpO2=p.SpO2,
        tidal_volume_per_kg_pbw=p.tidal_volume_per_kg_pbw,
        spontaneous_rate=p.spontaneous_rate,
        collected_at=p.collected_at,
        source=p.source,
    )

    trend_params: dict[str, ParameterTrendSchema] = {}
    for key, pt in t.parameters.items():
        series_points = [
            SeriesPoint(value=s["value"], collected_at=s["collected_at"])
            for s in pt.series
        ]
        trend_params[key] = ParameterTrendSchema(
            current=pt.current,
            min=pt.min,
            max=pt.max,
            avg=pt.avg,
            direction=pt.direction,
            change_pct=pt.change_pct,
            series=series_points,
        )

    trend_schema = VentilationTrendSchema(
        period_hours=t.period_hours,
        start_time=t.start_time,
        end_time=t.end_time,
        parameters=trend_params,
    )

    return VentilationResponse(
        parameters=params_schema,
        trend=trend_schema,
        collected_at=result.collected_at,
    )


# ---------------------------------------------------------------------------
# GET /patients/{mpi_id}/ventilation/history — Paginated history
# ---------------------------------------------------------------------------


def _parse_history_datetime(val: str | None) -> datetime | None:
    """Parse an ISO-8601 datetime string for history filtering."""
    if not val:
        return None
    try:
        s = val.strip().replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


@router.get(
    "/patients/{mpi_id}/ventilation/history",
    response_model=VentilationHistoryResponse,
)
async def get_patient_ventilation_history(
    mpi_id: str,
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
) -> VentilationHistoryResponse:
    """Histórico de parâmetros ventilatórios.

    Retorna o histórico completo de parâmetros ventilatórios do paciente,
    ordenados por data de coleta (mais recente primeiro). Permite
    paginação e filtro por intervalo de datas.
    """
    current_data = _SAMPLE_PATIENTS.get(mpi_id)
    if current_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {mpi_id} not found",
        )

    history = _SAMPLE_HISTORY.get(mpi_id, [])

    # Parse date filters
    from_dt = _parse_history_datetime(from_date)
    to_dt = _parse_history_datetime(to_date)

    filtered: list[dict[str, Any]] = []
    for entry in history:
        collected_str = entry.get("collected_at", "")
        entry_dt = _parse_history_datetime(collected_str)
        if entry_dt is None:
            continue
        if from_dt is not None and entry_dt < from_dt:
            continue
        if to_dt is not None and entry_dt > to_dt:
            continue
        filtered.append(entry)

    # Sort newest first
    filtered.sort(
        key=lambda e: _parse_history_datetime(e.get("collected_at", ""))
        or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )

    total = len(filtered)

    # Apply pagination
    page = filtered[offset : offset + limit]

    # Convert to Pydantic schemas via domain service extraction
    # (reuse extract_ventilation_params logic via evaluate_ventilation with no trend)
    from intensicare.services.domain_ventilacao import extract_ventilation_params

    items: list[VentilationParametersSchema] = []
    for entry in page:
        vp = extract_ventilation_params(entry)
        items.append(
            VentilationParametersSchema(
                id=vp.id,
                mpi_id=vp.mpi_id,
                mode=vp.mode,
                FiO2=vp.FiO2,
                PEEP=vp.PEEP,
                VC=vp.VC,
                FR=vp.FR,
                Pplat=vp.Pplat,
                driving_pressure=vp.driving_pressure,
                PaO2_FiO2_ratio=vp.PaO2_FiO2_ratio,
                SpO2=vp.SpO2,
                tidal_volume_per_kg_pbw=vp.tidal_volume_per_kg_pbw,
                spontaneous_rate=vp.spontaneous_rate,
                collected_at=vp.collected_at,
                source=vp.source,
            )
        )

    return VentilationHistoryResponse(items=items, total=total)
