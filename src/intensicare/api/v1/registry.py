"""Registry API Router — REST endpoints for Empresa, Estabelecimento, Setor management.

6 endpoints conforme contrato cadastros-ui OpenAPI:
  GET    /registry/empresas              — List empresas
  POST   /registry/empresas              — Create empresa
  GET    /registry/empresas/{id}         — Get empresa by ID
  PUT    /registry/empresas/{id}         — Update empresa
  DELETE /registry/empresas/{id}         — Delete empresa
  GET    /registry/estabelecimentos      — List estabelecimentos (filter by empresa_id)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user
from intensicare.core.database import get_db
from intensicare.models.user import User
from intensicare.schemas.registry import (
    EmpresaCreate,
    EmpresaResponse,
    EmpresaUpdate,
    EstabelecimentoResponse,
    RegistryListResponse,
)
from intensicare.services.domain_tenancy import (
    create_empresa,
    delete_empresa,
    get_empresa,
    list_empresas,
    list_estabelecimentos,
    update_empresa,
)

router = APIRouter(prefix="/api/v1", tags=["registry"])


# ============================================================================
# Empresas
# ============================================================================


@router.get(
    "/registry/empresas",
    response_model=RegistryListResponse,
)
async def list_empresas_endpoint(
    search: str | None = Query(
        None, description="Termo de busca (nome fantasia, razão social ou CNPJ)"
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RegistryListResponse:
    """List empresas with optional search filter and pagination."""
    items, total = await list_empresas(db, search=search, limit=limit, offset=offset)
    return RegistryListResponse(
        items=[EmpresaResponse.model_validate(e) for e in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/registry/empresas",
    response_model=EmpresaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_empresa_endpoint(
    body: EmpresaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EmpresaResponse:
    """Create a new empresa (organization).

    Returns 409 if CNPJ already registered.
    """
    # Check CNPJ uniqueness
    existing_items, _ = await list_empresas(db, search=body.cnpj, limit=1)
    if existing_items:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CNPJ já cadastrado",
        )

    empresa = await create_empresa(db, data=body.model_dump())
    return EmpresaResponse.model_validate(empresa)


@router.get(
    "/registry/empresas/{empresa_id}",
    response_model=EmpresaResponse,
)
async def get_empresa_endpoint(
    empresa_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EmpresaResponse:
    """Get a single empresa by ID. Returns 404 if not found."""
    empresa = await get_empresa(db, empresa_id)
    if empresa is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada",
        )
    return EmpresaResponse.model_validate(empresa)


@router.put(
    "/registry/empresas/{empresa_id}",
    response_model=EmpresaResponse,
)
async def update_empresa_endpoint(
    empresa_id: str,
    body: EmpresaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EmpresaResponse:
    """Update an existing empresa. Returns 404 if not found."""
    update_data = body.model_dump(exclude_unset=True)

    # Check CNPJ uniqueness if changing CNPJ
    if update_data.get("cnpj"):
        existing_items, _ = await list_empresas(db, search=update_data["cnpj"], limit=2)
        conflicts = [e for e in existing_items if e.id != empresa_id]
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CNPJ já cadastrado",
            )

    empresa = await update_empresa(db, empresa_id, update_data)
    if empresa is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada",
        )
    return EmpresaResponse.model_validate(empresa)


@router.delete(
    "/registry/empresas/{empresa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_empresa_endpoint(
    empresa_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete an empresa by ID. Returns 204 on success, 404 if not found."""
    deleted = await delete_empresa(db, empresa_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada",
        )


# ============================================================================
# Estabelecimentos
# ============================================================================


@router.get(
    "/registry/estabelecimentos",
    response_model=RegistryListResponse,
)
async def list_estabelecimentos_endpoint(
    search: str | None = Query(None, description="Termo de busca (nome ou CNES)"),
    empresa_id: str | None = Query(None, description="Filtra por empresa proprietária"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RegistryListResponse:
    """List estabelecimentos with optional filters and pagination."""
    items, total = await list_estabelecimentos(
        db, empresa_id=empresa_id, search=search, limit=limit, offset=offset
    )
    return RegistryListResponse(
        items=[EstabelecimentoResponse.model_validate(e) for e in items],
        total=total,
        limit=limit,
        offset=offset,
    )
