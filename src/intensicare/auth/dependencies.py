"""FastAPI dependencies for authentication.

Fase 3 (WO-037): IAM Identity Center SSO é o mecanismo primário de
autenticação em staging/production. O JWT local (MVP) é mantido como
fallback para dev/test.

A dependência ``get_current_user`` detecta automaticamente o tipo de
token (IAM IC vs JWT local) pelo header e claims.
"""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.jwt import decode_token, is_token_blacklisted
from intensicare.config import settings
from intensicare.core.database import get_db
from intensicare.core.redis import get_redis
from intensicare.models.user import User

security = HTTPBearer()


async def _resolve_user_from_db(
    db: AsyncSession, username: str
) -> User:
    """Busca usuário no banco local (compatibilidade com MVP)."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extrai e valida o usuário autenticado.

    Fase 3 — detecção automática do tipo de token:
        1. Se ``settings.iam_enabled``, tenta validar como token IAM IC.
        2. Caso contrário (ou fallback), valida como JWT local (MVP).

    O IAM Identity Center emite tokens OIDC com claims específicos
    (iss no domínio identitycenter.amazonaws.com). O validador IAM
    extrai tenant_id, role e groups dos claims customizados.
    """
    token = credentials.credentials

    # Tenta IAM Identity Center primeiro (Fase 3)
    if settings.iam_enabled:
        try:
            from intensicare.auth.iam import validate_iam_token
            identity = await validate_iam_token(token)
            # Mapeia IAMIdentity → User local (ou cria virtual)
            return await _resolve_user_from_db(db, identity.username)
        except Exception:
            # Fallback: tenta JWT local
            pass

    # JWT local (MVP / dev / fallback)
    redis_client = get_redis()

    if await is_token_blacklisted(token, redis_client):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    username: str | None = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return await _resolve_user_from_db(db, username)


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Requer que o usuário autenticado tenha privilégios de administrador."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


# ---------------------------------------------------------------------------
# ABAC dependencies (Fase 3 / WO-037)
# ---------------------------------------------------------------------------


async def get_current_tenant_id(
    request: Request,
) -> str:
    """Extrai o tenant_id do request (header X-Tenant-ID ou token IAM IC).

    Em produção, o tenant_id vem do claim ``custom:tenant_id`` no token
    IAM Identity Center. Em dev/test, usa o header ``X-Tenant-ID``.
    """
    # Header explícito tem precedência (útil para dev/test e operadores admin)
    tenant_header = request.headers.get("X-Tenant-ID")
    if tenant_header:
        return tenant_header

    # Tenta extrair do token IAM IC
    if settings.iam_enabled:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            try:
                from intensicare.auth.iam import validate_iam_token
                identity = await validate_iam_token(token)
                return identity.tenant_id
            except Exception:
                pass

    return "default"
