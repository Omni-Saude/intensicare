"""
Rotas da API v1 — consulta de status do paciente (DEPRECATED).

GET /api/v1/patients/{mpi_id}/status — Status do paciente (DEPRECATED).
Use GET /api/v1/patients/{mpi_id}/detail instead.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.core.database import get_db
from intensicare.schemas.dashboard import PatientDetailResponse
from intensicare.services.dashboard import get_patient_detail

router = APIRouter()


@router.get(
    "/patients/{mpi_id}/status",
    response_model=PatientDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="[DEPRECATED] Status do paciente",
    description=(
        "⚠️ DEPRECATED — use GET /api/v1/patients/{mpi_id}/detail instead. "
        "Retorna dados detalhados do paciente com histórico de sinais vitais "
        "(24h), scores (MEWS/NEWS2) e alertas ativos."
    ),
    responses={
        200: {"description": "Dados detalhados do paciente"},
        404: {"description": "Paciente não encontrado"},
    },
    deprecated=True,
)
async def patient_status(
    mpi_id: str,
    response: Response,  # FastAPI injects the response object
    db: AsyncSession = Depends(get_db),
    score_type: str = Query(
        "MEWS",
        description="[DEPRECATED] Ignorado — use /api/v1/patients/{mpi_id}/detail",
        deprecated=True,
        max_length=16,
    ),
    enrich: bool = Query(
        False,
        description="[DEPRECATED] Ignorado — use /api/v1/patients/{mpi_id}/detail",
        deprecated=True,
    ),
) -> PatientDetailResponse:
    """Retorna dados detalhados do paciente (endpoint deprecado).

    ⚠️ Este endpoint está deprecado e redireciona para o serviço de dashboard.
    Use GET /api/v1/patients/{mpi_id}/detail como substituto definitivo.
    """
    # Add deprecation headers (RFC 8594)
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "Sat, 01 Nov 2026 00:00:00 GMT"
    response.headers["Link"] = f'</api/v1/patients/{mpi_id}/detail>; rel="successor-version"'

    result = await get_patient_detail(db=db, mpi_id=mpi_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente não encontrado: {mpi_id}",
        )
    return result
