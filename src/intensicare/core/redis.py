"""Redis client initialization and utilities."""

import redis.asyncio as aioredis

from intensicare.config import settings


# Client stored as an attribute of a module-level container to avoid `global`.
class _RedisState:
    """Container for the lazily-initialised Redis client."""

    client: aioredis.Redis | None = None


_redis_state = _RedisState()


def get_redis() -> aioredis.Redis:
    """Get or create the Redis client (lazy init)."""
    if _redis_state.client is None:
        # from_url is untyped in redis 5.x (no annotations despite py.typed).
        _redis_state.client = aioredis.from_url(  # type: ignore[no-untyped-call]
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    client = _redis_state.client
    assert client is not None  # just initialised above when it was None
    return client


async def close_redis() -> None:
    """Close the Redis connection."""
    client = _redis_state.client
    if client is not None:
        await client.close()
        _redis_state.client = None


def get_redis_connection_kwargs() -> dict[str, object]:
    """Return Redis connection kwargs suitable for ARQ RedisSettings.

    Exposes host/port/database so that ARQ can build its own connection pool
    independently of the aioredis client managed by get_redis().
    """
    from intensicare.config import settings

    return {
        "host": settings.redis_host,
        "port": settings.redis_port,
        "database": settings.redis_db,
    }
