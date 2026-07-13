"""
Rotas da API v1 — consulta de status do paciente (DEPRECATED).

GET /api/v1/patients/{mpi_id}/status — Status agregado do paciente (DEPRECATED).
Use GET /api/v1/patients/{mpi_id}/detail instead.

Contrato legado (docs/contracts/patients-base-openapi.yaml): sempre 200,
com campos nulos quando o paciente ainda não possui dados processados
(ex.: sinais vitais recém-ingeridos, sem PatientCache populado ainda).
NÃO delega para get_patient_detail (services/dashboard.py) — aquele serviço
depende de PatientCache e retorna None/404 quando o cache não existe, o que
quebra o contrato null-safe deste endpoint legado. Consulta diretamente
VitalSign/ClinicalScore via get_patient_status (services/patients.py).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.core.database import get_db
from intensicare.schemas.patients import PatientStatusResponse
from intensicare.services.patients import get_patient_status

router = APIRouter()


@router.get(
    "/patients/{mpi_id}/status",
    response_model=PatientStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="[DEPRECATED] Status do paciente",
    description=(
        "⚠️ DEPRECATED — prefira GET /api/v1/patients/{mpi_id}/detail. "
        "Retorna o status agregado do paciente: sinais vitais mais recentes, "
        "último score e tendência dos últimos 5 scores. "
        "Quando enrich=true e FHIR_BASE_URL está configurado, inclui dados "
        "demográficos e clínicos do FHIR (HAPI FHIR / AMH Data Platform). "
        "Sempre retorna 200 — campos nulos quando o paciente não possui "
        "dados processados ainda."
    ),
    responses={
        200: {"description": "Status do paciente (campos nulos quando não há dados)"},
    },
    deprecated=True,
)
async def patient_status(
    mpi_id: str,
    response: Response,  # FastAPI injects the response object
    db: AsyncSession = Depends(get_db),
    score_type: str = Query(
        "MEWS",
        description="Tipo de score a consultar (MEWS, NEWS2, SOFA, qSOFA)",
        max_length=16,
    ),
    enrich: bool = Query(
        False,
        description="Enriquecer com dados do FHIR (requer FHIR_BASE_URL configurado)",
    ),
) -> PatientStatusResponse:
    """Retorna status agregado do paciente com enriquecimento FHIR opcional.

    ⚠️ Este endpoint está deprecado — use GET /api/v1/patients/{mpi_id}/detail
    para o contrato completo (vitals/scores history, alertas, pathways).
    Mantido por compatibilidade retroativa: nunca 404, campos nulos quando
    não há dados (comportamento null-safe original, ver
    docs/contracts/patients-base-openapi.yaml).
    """
    # Add deprecation headers (RFC 8594)
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "Sat, 01 Nov 2026 00:00:00 GMT"
    response.headers["Link"] = f'</api/v1/patients/{mpi_id}/detail>; rel="successor-version"'

    try:
        # Retorna 200 mesmo sem dados — o frontend decide como tratar
        return await get_patient_status(
            db=db,
            mpi_id=mpi_id,
            score_type=score_type,
            enrich=enrich,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao consultar status do paciente: {exc}",
        ) from exc
