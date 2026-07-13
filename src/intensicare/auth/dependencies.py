"""FastAPI dependencies for authentication.

Fase 3 (WO-037): IAM Identity Center SSO é o mecanismo primário de
autenticação em staging/production. O JWT local (MVP) é mantido como
fallback para dev/test.

A dependência ``get_current_user`` detecta automaticamente o tipo de
token (IAM IC vs JWT local) pelo header e claims.
"""

import logging

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.jwt import decode_token, is_token_blacklisted
from intensicare.config import settings
from intensicare.core.database import get_db
from intensicare.core.redis import get_redis
from intensicare.models.user import User

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def _resolve_user_from_db(db: AsyncSession, username: str) -> User:
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
            logger.debug("IAM token validation failed, falling back to local JWT", exc_info=True)

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
# GAP C7 — Clinical roles para RBAC granular
# ---------------------------------------------------------------------------

CLINICAL_ROLES = [
    "admin",
    "medico",
    "enfermeiro",
    "fisioterapeuta",
    "farmacia",
    "nutricao",
    "readonly",
]


def _has_role(user: User, *roles: str) -> bool:
    """Verifica se o usuário possui um dos roles clínicos especificados.

    Fix RBAC (audit CRITICAL #6): ``is_admin`` NÃO é mais um bypass
    incondicional para guards clínicos (require_medico, require_enfermeiro,
    etc.). Um administrador de sistema não é implicitamente médico,
    enfermeiro, fisioterapeuta, farmacêutico ou nutricionista — essas
    permissões clínicas dependem do ``user.role`` real. Acesso
    administrativo (não-clínico) continua garantido por ``require_admin``.

    Levantamento prévio (grep no código): nenhum endpoint/router usa
    require_medico/require_enfermeiro/require_fisioterapeuta/
    require_farmacia/require_nutricao como dependência ativa, e nenhum
    teste existente exercitava o bypass de admin aqui — a remoção é
    comportamentalmente segura.
    """
    return user.role in roles


async def require_medico(
    current_user: User = Depends(get_current_user),
) -> User:
    """Requer admin ou role 'medico'."""
    if not _has_role(current_user, "medico"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Médico role required",
        )
    return current_user


async def require_enfermeiro(
    current_user: User = Depends(get_current_user),
) -> User:
    """Requer admin, médico ou role 'enfermeiro'."""
    if not _has_role(current_user, "medico", "enfermeiro"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Enfermeiro role required",
        )
    return current_user


async def require_fisioterapeuta(
    current_user: User = Depends(get_current_user),
) -> User:
    """Requer admin ou role 'fisioterapeuta'."""
    if not _has_role(current_user, "fisioterapeuta"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Fisioterapeuta role required",
        )
    return current_user


async def require_farmacia(
    current_user: User = Depends(get_current_user),
) -> User:
    """Requer admin ou role 'farmacia'."""
    if not _has_role(current_user, "farmacia"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Farmácia role required",
        )
    return current_user


async def require_nutricao(
    current_user: User = Depends(get_current_user),
) -> User:
    """Requer admin ou role 'nutricao'."""
    if not _has_role(current_user, "nutricao"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nutrição role required",
        )
    return current_user


# ---------------------------------------------------------------------------
# H15: Account lockout — Redis-based brute-force protection
# ---------------------------------------------------------------------------

_MAX_FAILED_ATTEMPTS = 5
_LOCKOUT_DURATION_SECONDS = 900  # 15 minutes


async def check_account_lockout(username: str) -> None:
    """Bloqueia autenticação se conta estiver em lockout.

    Levanta HTTPException 423 (Locked) se a conta excedeu o limite
    de tentativas de login malsucedidas.
    """
    redis_client = get_redis()
    lockout_key = f"lockout:{username}"
    locked = await redis_client.get(lockout_key)
    if locked:
        ttl = await redis_client.ttl(lockout_key)
        raise HTTPException(
            status_code=423,
            detail=f"Account locked. Try again in {ttl}s.",
        )


async def record_failed_login(username: str) -> None:
    """Registra tentativa de login malsucedida e aplica lockout se necessário."""
    redis_client = get_redis()
    attempts_key = f"login_attempts:{username}"
    lockout_key = f"lockout:{username}"

    attempts = await redis_client.incr(attempts_key)
    if attempts == 1:
        await redis_client.expire(attempts_key, _LOCKOUT_DURATION_SECONDS)
    if attempts >= _MAX_FAILED_ATTEMPTS:
        await redis_client.setex(lockout_key, _LOCKOUT_DURATION_SECONDS, "1")
        await redis_client.delete(attempts_key)


async def reset_login_attempts(username: str) -> None:
    """Limpa tentativas malsucedidas após login bem-sucedido."""
    redis_client = get_redis()
    await redis_client.delete(
        f"login_attempts:{username}",
        f"lockout:{username}",
    )


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
                logger.debug("IAM tenant resolution failed, using default tenant", exc_info=True)

    return "default"
