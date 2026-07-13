"""
Rotas da API v1 — ingestão de sinais vitais.

POST /api/v1/vitals — Ingere sinais vitais com idempotência e scoring MEWS.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.abac import Action, ResourceType, require_abac
from intensicare.auth.dependencies import get_current_tenant_id, get_current_user
from intensicare.core.database import get_db
from intensicare.core.websocket import get_websocket_manager
from intensicare.models.user import User
from intensicare.schemas.vitals import VitalSignCreate, VitalSignResponse
from intensicare.services.vitals import ingest_vitals

router = APIRouter()


@router.post(
    "/vitals",
    response_model=VitalSignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingerir sinais vitais",
    description=(
        "Recebe sinais vitais de um paciente, persiste no banco, "
        "calcula MEWS sincronamente e retorna o resultado. "
        "Suporta idempotência via header `X-Idempotency-Key`."
    ),
    responses={
        201: {"description": "Sinais vitais ingeridos com sucesso"},
        200: {"description": "Requisição idempotente — dados já processados"},
        422: {"description": "Erro de validação nos dados enviados"},
    },
)
async def create_vitals(
    body: VitalSignCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    x_idempotency_key: str | None = Header(
        None,
        alias="X-Idempotency-Key",
        description="Chave de idempotência (MSH-10). Evita duplicação de registros.",
    ),
) -> VitalSignResponse:
    """Ingere sinais vitais com idempotência, scoring e alert engine."""
    # ABAC enforcement — usa o role real do usuário autenticado (fix RBAC
    # audit CRITICAL #6 / achado Dim A/C: guards clínicos não protegiam
    # dados clínicos fora de admin.py). Ingestão de vitals é WRITE em VITALS
    # (matriz não tem uma ação CREATE dedicada — WRITE cobre criação).
    tenant_id = await get_current_tenant_id(request)
    require_abac(
        role_str=current_user.role,
        resource=ResourceType.VITALS,
        action=Action.WRITE,
        tenant_id=tenant_id,
        resource_tenant=tenant_id,
    )

    try:
        result, alerts, is_replay = await ingest_vitals(
            db=db,
            data=body,
            idempotency_key=x_idempotency_key,
        )

        # Idempotent replay is a 200 (already processed), not a 201 (created).
        if is_replay:
            response.status_code = status.HTTP_200_OK

        # Broadcast any created alerts to WebSocket clients
        if alerts:
            manager = get_websocket_manager()
            for alert in alerts:
                alert_data = {
                    "type": "alert",
                    "id": alert.id,
                    "mpi_id": alert.mpi_id,
                    "severity": alert.severity,
                    "status": alert.status,
                    "title": alert.title,
                    "body": alert.body,
                    "created_at": alert.created_at.isoformat() if alert.created_at else None,
                }
                await manager.broadcast_alert(alert_data)

        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao processar sinais vitais: {exc}",
        ) from exc
