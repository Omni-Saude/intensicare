"""Authentication and authorization dependencies for FastAPI.

Este é um stub de desenvolvimento. Em staging/production, ele é bloqueado
e o módulo real ``intensicare.auth`` (pacote) deve ser usado.
"""

from fastapi import Depends, HTTPException, Request, status

from intensicare.config import settings

# Ambientes onde o stub é permitido (apenas desenvolvimento e testes).
_STUB_ALLOWED_ENVIRONMENTS = frozenset({"development", "testing"})


def _block_if_production() -> None:
    """Levanta 403 se o ambiente não for de desenvolvimento/teste."""
    if settings.environment not in _STUB_ALLOWED_ENVIRONMENTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Auth stub is disabled in production — use real JWT auth module",
        )


async def get_current_user(request: Request) -> dict[str, str]:
    """Extract and validate the current user from the Authorization header.

    Expects: Authorization: Bearer ***
    Em desenvolvimento, qualquer token Bearer não vazio é aceito.
    Em produção, este stub é bloqueado (403).
    """
    _block_if_production()

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header[7:].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In production: decode and validate JWT here
    # For now, parse a simple format: "user_id:role" or just accept any token
    parts = token.split(":")
    return {
        "sub": parts[0] if len(parts) > 0 else token,
        "role": parts[1] if len(parts) > 1 else "user",
    }


async def require_admin(user: dict[str, str] = Depends(get_current_user)) -> dict[str, str]:
    """Ensure the current user has admin role.

    Em produção, este stub é bloqueado antes mesmo de chegar aqui (via
    get_current_user).
    """
    _block_if_production()

    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return user
