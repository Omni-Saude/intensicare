"""JWT token creation and verification using python-jose."""

from datetime import datetime, timedelta, timezone
from typing import Any, cast
from uuid import uuid4

from jose import JWTError, jwt  # type: ignore[import-untyped]  # python-jose ships no type stubs
import redis.asyncio as aioredis

from intensicare.config import settings


def create_access_token(data: dict[str, Any]) -> str:
    """Create a JWT access token with expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire, "type": "access", "jti": str(uuid4())})
    secret = settings.secret_key.get_secret_value()
    return cast("str", jwt.encode(to_encode, secret, algorithm=settings.jwt_algorithm))


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a JWT refresh token with longer expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_expire_days)
    to_encode.update({"exp": expire, "type": "refresh", "jti": str(uuid4())})
    secret = settings.secret_key.get_secret_value()
    return cast("str", jwt.encode(to_encode, secret, algorithm=settings.jwt_algorithm))


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and verify a JWT token. Returns payload or None if invalid."""
    try:
        secret = settings.secret_key.get_secret_value()
        return cast(
            "dict[str, Any]",
            jwt.decode(token, secret, algorithms=[settings.jwt_algorithm]),
        )
    except JWTError:
        return None


async def is_token_blacklisted(token: str, redis_client: aioredis.Redis) -> bool:
    """Check if a token is in the Redis blacklist."""
    token_hash = jwt.get_unverified_claims(token).get("jti", "")
    if not token_hash:
        return False
    return bool(await redis_client.exists(f"blacklist:{token_hash}") > 0)


async def blacklist_token(token: str, redis_client: aioredis.Redis) -> None:
    """Blacklist a token by storing its JTI in Redis with remaining TTL.

    Extracts the JTI and exp claims from the token without verification,
    then stores a blacklist entry in Redis that expires when the token
    would have naturally expired.
    """
    claims: dict[str, Any] = jwt.get_unverified_claims(token)
    jti: str = claims.get("jti", "")
    exp: float | None = claims.get("exp")
    if not jti:
        return
    now = datetime.now(timezone.utc).timestamp()
    if exp and exp > now:
        ttl = int(exp - now)
    else:
        ttl = 3600  # Default 1 hour for tokens without a valid exp
    await redis_client.setex(f"blacklist:{jti}", ttl, "1")


def verify_token(token: str) -> dict[str, Any] | None:
    """Verify a JWT token (alias for decode_token)."""
    return decode_token(token)
