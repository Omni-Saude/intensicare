"""IAM Identity Center — validação de tokens OIDC (Fase 3 / WO-037).

Substitui a validação JWT local (MVP) nos ambientes staging/production.
Usa o OIDC issuer do IAM Identity Center para validar assinaturas,
expiração e claims obrigatórios (iss, aud, sub, tenant_id).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from jose import JWTError, jwt  # type: ignore[import-untyped]
from jose.jwk import RSAKey  # type: ignore[import-untyped]

from intensicare.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------


class IAMIdentity:
    """Identidade extraída de um token IAM Identity Center válido."""

    def __init__(
        self,
        sub: str,
        username: str,
        tenant_id: str,
        role: str,
        email: str | None = None,
        groups: list[str] | None = None,
    ) -> None:
        self.sub = sub
        self.username = username
        self.tenant_id = tenant_id
        self.role = role
        self.email = email
        self.groups = groups or []

    def __repr__(self) -> str:
        return (
            f"IAMIdentity(sub={self.sub!r}, username={self.username!r}, "
            f"tenant={self.tenant_id!r}, role={self.role!r})"
        )


class IAMTokenError(Exception):
    """Token IAM IC inválido ou expirado."""


class IAMDisabledError(IAMTokenError):
    """IAM IC não está habilitado nas configurações."""


# ---------------------------------------------------------------------------
# Cache de JWKS (simplificado — em produção usar cache com TTL)
# ---------------------------------------------------------------------------

_jwks_cache: dict[str, Any] | None = None


async def _fetch_jwks() -> dict[str, Any]:
    """Obtém as chaves públicas do OIDC issuer via well-known endpoint.

    Em produção, substituir por um mecanismo com cache (ex: Redis, TTL 1h).
    """
    global _jwks_cache  # noqa: PLW0603

    if _jwks_cache is not None:
        return _jwks_cache

    try:
        import httpx

        issuer = settings.iam_oidc_issuer.rstrip("/")
        url = f"{issuer}/.well-known/openid-configuration"
        async with httpx.AsyncClient(timeout=10.0) as client:
            config_resp = await client.get(url)
            config_resp.raise_for_status()
            config = config_resp.json()
            jwks_uri = config["jwks_uri"]

            jwks_resp = await client.get(jwks_uri)
            jwks_resp.raise_for_status()
            _jwks_cache = jwks_resp.json()
        return _jwks_cache
    except Exception as exc:
        logger.error("Failed to fetch IAM JWKS: %s", exc)
        raise IAMTokenError(f"Cannot retrieve IAM signing keys: {exc}") from exc


# ---------------------------------------------------------------------------
# Validação
# ---------------------------------------------------------------------------


def _extract_claims(token: str, key: dict[str, Any]) -> dict[str, Any]:
    """Decodifica e valida assinatura + claims obrigatórios do token.

    Raises:
        IAMTokenError: se o token for inválido, expirado ou não passar
                       nas verificações de issuer/audience.
    """
    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.iam_client_id or None,
            options={
                "verify_exp": True,
                "verify_aud": bool(settings.iam_client_id),
            },
        )
    except JWTError as exc:
        raise IAMTokenError(f"IAM token validation failed: {exc}") from exc

    # Verificações adicionais
    expected_issuer = settings.iam_oidc_issuer.rstrip("/")
    actual_issuer = payload.get("iss", "")
    if not actual_issuer.startswith(expected_issuer):
        raise IAMTokenError(
            f"Invalid issuer: expected {expected_issuer}, got {actual_issuer}"
        )

    now = datetime.now(timezone.utc)
    exp = payload.get("exp")
    if exp is None:
        raise IAMTokenError("Token missing expiration claim")
    if datetime.fromtimestamp(exp, tz=timezone.utc) < now:
        raise IAMTokenError("Token expired")

    return payload


def _identity_from_claims(claims: dict[str, Any]) -> IAMIdentity:
    """Converte claims OIDC do IAM Identity Center em IAMIdentity."""
    sub = claims.get("sub")
    if not sub:
        raise IAMTokenError("Token missing 'sub' claim")

    # O IAM Identity Center injeta atributos customizados via claims.
    # Mapeamento esperado (configurável no IAM IC):
    #   sub            → identificador único do usuário
    #   preferred_username | username → nome de usuário
    #   custom:tenant_id → tenant ID (atributo customizado no IAM IC)
    #   custom:role      → role clínico (médico, enfermeiro, admin)
    #   groups          → grupos IAM IC (ex: "UTI-Alpha", "Pharma")
    username = claims.get("preferred_username") or claims.get("username") or sub
    tenant_id = (
        claims.get("custom:tenant_id")
        or claims.get("tenant_id")
        or "default"
    )
    role = (
        claims.get("custom:role")
        or claims.get("role")
        or "viewer"
    )
    email = claims.get("email")
    groups = claims.get("groups", [])
    if isinstance(groups, str):
        groups = [groups]

    return IAMIdentity(
        sub=sub,
        username=username,
        tenant_id=tenant_id,
        role=role,
        email=email,
        groups=groups,
    )


async def validate_iam_token(token: str) -> IAMIdentity:
    """Valida um token OIDC do IAM Identity Center e retorna a identidade.

    Fluxo:
        1. Confere se IAM está habilitado (settings.iam_enabled)
        2. Obtém JWKS do issuer OIDC
        3. Valida assinatura RS256 + claims (exp, aud, iss)
        4. Extrai IAMIdentity com tenant, role, groups

    Args:
        token: Token JWT no formato OIDC emitido pelo IAM Identity Center.

    Returns:
        IAMIdentity populada com sub, username, tenant_id, role, groups.

    Raises:
        IAMDisabledError: se settings.iam_enabled for False.
        IAMTokenError: se o token for inválido em qualquer etapa.
    """
    if not settings.iam_enabled:
        raise IAMDisabledError("IAM Identity Center SSO is not enabled")

    jwks = await _fetch_jwks()

    # Tenta cada chave do JWKS (o kid do header decide qual usar)
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
    except JWTError as exc:
        raise IAMTokenError(f"Cannot parse token header: {exc}") from exc

    matching_key = None
    for key_data in jwks.get("keys", []):
        if kid and key_data.get("kid") == kid:
            matching_key = key_data
            break

    if matching_key is None:
        # Fallback: tenta todas as chaves
        for key_data in jwks.get("keys", []):
            try:
                claims = _extract_claims(token, key_data)
                return _identity_from_claims(claims)
            except IAMTokenError:
                continue
        raise IAMTokenError(f"No matching key found for kid={kid!r}")

    claims = _extract_claims(token, matching_key)
    return _identity_from_claims(claims)
