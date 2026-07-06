"""Token bucket rate limiter using Redis.

Applies rate limits to:
- Auth endpoints: 5 attempts/minute for login (brute-force protection)
- API endpoints: 100 requests/minute default
- Critical endpoints (health, metrics): never rate-limited
"""

from __future__ import annotations

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from intensicare.core.redis import get_redis

# ---------------------------------------------------------------------------
# Rate limit buckets
# ---------------------------------------------------------------------------

# (max_tokens, refill_interval_seconds) — token bucket parameters
RATE_LIMITS: dict[str, tuple[int, float]] = {
    "auth": (5, 60.0),      # 5 attempts per minute (login brute-force)
    "api": (100, 60.0),      # 100 requests per minute default
}

# Endpoints that are NEVER rate-limited
CRITICAL_PATHS: set[str] = {
    "/health",
    "/api/v1/health",
    "/metrics",
}

# Map URL prefixes to bucket names
PATH_BUCKET_MAP: list[tuple[str, str]] = [
    ("/auth", "auth"),
    ("/api", "api"),
]


def _get_client_ip(request: Request) -> str:
    """Extract client IP, respecting X-Forwarded-For if present."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = request.client
    if client:
        return client.host or "unknown"
    return "unknown"


class TokenBucketRateLimiter:
    """Token bucket rate limiter backed by Redis.

    Uses a sliding-window approach: each key stores the current token count
    and last refill timestamp. Keys expire after idle window to prevent
    unbounded key accumulation.
    """

    KEY_PREFIX = "rate_limit"
    # Keys expire after 2x the refill window of idle time
    EXPIRE_SECONDS = 300

    def __init__(self) -> None:
        self._redis = None

    def _r(self):
        if self._redis is None:
            self._redis = get_redis()
        return self._redis

    def _key(self, client_ip: str, bucket: str) -> str:
        return f"{self.KEY_PREFIX}:{client_ip}:{bucket}"

    async def is_allowed(self, client_ip: str, bucket: str) -> bool:
        """Check if a request is allowed and consume a token.

        Returns True if allowed, False if rate-limited.
        """
        bucket_config = RATE_LIMITS.get(bucket)
        if bucket_config is None:
            return True  # unknown bucket → allow

        max_tokens, refill_interval = bucket_config
        redis_key = self._key(client_ip, bucket)
        now = time.monotonic()

        r = self._r()

        # Lua script for atomic check-and-consume
        lua_script = """
        local key = KEYS[1]
        local max_tokens = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])  -- tokens per second
        local now = tonumber(ARGV[3])
        local expire = tonumber(ARGV[4])

        local data = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(data[1])
        local last_refill = tonumber(data[2])

        if tokens == nil then
            -- First request — initialise bucket
            tokens = max_tokens - 1
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, expire)
            return 1
        end

        -- Refill tokens
        local elapsed = now - last_refill
        local new_tokens = math.min(max_tokens, tokens + elapsed * refill_rate)

        if new_tokens < 1 then
            -- Not enough tokens — rate limited
            redis.call('HSET', key, 'tokens', 0)
            redis.call('EXPIRE', key, expire)
            return 0
        end

        -- Consume one token
        new_tokens = new_tokens - 1
        redis.call('HMSET', key, 'tokens', new_tokens, 'last_refill', now)
        redis.call('EXPIRE', key, expire)
        return 1
        """

        refill_rate = max_tokens / refill_interval
        result = await r.eval(
            lua_script,
            1,
            redis_key,
            max_tokens,
            refill_rate,
            now,
            self.EXPIRE_SECONDS,
        )
        return bool(result)


# Singleton
_rate_limiter = TokenBucketRateLimiter()


def _resolve_bucket(path: str) -> str | None:
    """Determine which rate-limit bucket a path belongs to."""
    for prefix, bucket in PATH_BUCKET_MAP:
        if path.startswith(prefix):
            return bucket
    return None


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that enforces token-bucket rate limits.

    Critical endpoints (health, metrics) are exempt.
    Auth endpoints use a tighter limit to prevent brute-force attacks.
    All other API endpoints use the default limit.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        # Critical endpoints — never rate-limited
        if path.rstrip("/") in CRITICAL_PATHS:
            return await call_next(request)

        # Resolve bucket
        bucket = _resolve_bucket(path)
        if bucket is None:
            # Unknown path — allow (no rate limit defined)
            return await call_next(request)

        # Check rate limit
        client_ip = _get_client_ip(request)
        allowed = await _rate_limiter.is_allowed(client_ip, bucket)

        if not allowed:
            return Response(
                content='{"detail":"Too many requests. Please try again later."}',
                status_code=429,
                media_type="application/json",
                headers={
                    "Retry-After": str(int(RATE_LIMITS[bucket][1])),
                    "X-RateLimit-Limit": str(RATE_LIMITS[bucket][0]),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)

        # Add rate-limit headers
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMITS[bucket][0])
        return response
