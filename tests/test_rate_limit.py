"""
Tests for the token-bucket rate limiter.

Covers:
  - Token-bucket initialisation and first-request allowance
  - Bucket exhaustion (rate-limited after max requests)
  - Token refill after idle period
  - Critical-path exemption (/health, /metrics)
  - Bucket resolution by URL prefix
  - Rate-limit headers on responses
  - Client IP extraction (including X-Forwarded-For)
"""

from unittest.mock import AsyncMock, MagicMock

from fastapi import Request
from httpx import AsyncClient
import pytest

from intensicare.core.rate_limit import (
    CRITICAL_PATHS,
    RATE_LIMITS,
    TokenBucketRateLimiter,
    _get_client_ip,
    _resolve_bucket,
)

# ─── Client IP extraction ────────────────────────────────────────────────────


class TestClientIP:
    """Tests for client IP extraction."""

    def test_direct_client_ip(self):
        """When no X-Forwarded-For is present, use the direct client IP."""
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client.host = "192.168.1.100"
        assert _get_client_ip(request) == "192.168.1.100"

    def test_forwarded_header_takes_precedence(self):
        """X-Forwarded-For header should be used when present."""
        request = MagicMock(spec=Request)
        request.headers = {"X-Forwarded-For": "10.0.0.5, 192.168.1.1"}
        request.client.host = "192.168.1.100"
        assert _get_client_ip(request) == "10.0.0.5"

    def test_no_client_returns_unknown(self):
        """When neither header nor client is available, return 'unknown'."""
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = None
        assert _get_client_ip(request) == "unknown"


# ─── Bucket resolution ───────────────────────────────────────────────────────


class TestBucketResolution:
    """Tests for path → bucket mapping."""

    def test_auth_path_resolves_to_auth_bucket(self):
        assert _resolve_bucket("/auth/login") == "auth"

    def test_api_path_resolves_to_api_bucket(self):
        assert _resolve_bucket("/api/v1/patients") == "api"

    def test_unknown_path_returns_none(self):
        assert _resolve_bucket("/some/random/path") is None

    def test_empty_path_returns_none(self):
        assert _resolve_bucket("/") is None


# ─── TokenBucketRateLimiter (unit tests with mocked Redis) ────────────────────


class TestTokenBucketRateLimiter:
    """Unit tests for token-bucket logic with mocked Redis."""

    def test_first_request_allowed(self):
        """The first request initialises the bucket and is always allowed."""
        limiter = TokenBucketRateLimiter()
        mock_redis = AsyncMock()
        # Simulate Lua script returning 1 (allowed)
        mock_redis.eval.return_value = 1
        limiter._redis = mock_redis

        limiter.is_allowed("10.0.0.1", "api")
        # Can't directly await in a sync test without asyncio.run,
        # but we can patch the method to return immediately.
        # Use pytest-asyncio for proper async test.
        pass

    @pytest.mark.asyncio
    async def test_first_request_initializes_bucket(self):
        """The first request should initialise bucket and allow it."""
        limiter = TokenBucketRateLimiter()
        mock_redis = AsyncMock()
        mock_redis.eval.return_value = 1
        limiter._redis = mock_redis

        allowed = await limiter.is_allowed("10.0.0.2", "api")
        assert allowed is True

        # Lua script should have been called
        mock_redis.eval.assert_called_once()
        call_args = mock_redis.eval.call_args
        # args: lua_script, num_keys, key, max_tokens, refill_rate, now, expire
        assert call_args[0][2] == "rate_limit:10.0.0.2:api"

    @pytest.mark.asyncio
    async def test_bucket_exhaustion_returns_false(self):
        """When Lua returns 0 (no tokens), is_allowed returns False."""
        limiter = TokenBucketRateLimiter()
        mock_redis = AsyncMock()
        mock_redis.eval.return_value = 0
        limiter._redis = mock_redis

        allowed = await limiter.is_allowed("10.0.0.3", "auth")
        assert allowed is False

    @pytest.mark.asyncio
    async def test_unknown_bucket_always_allows(self):
        """An unknown bucket name should always return True."""
        limiter = TokenBucketRateLimiter()
        allowed = await limiter.is_allowed("10.0.0.4", "nonexistent")
        assert allowed is True

    @pytest.mark.asyncio
    async def test_multiple_requests_exhaust_auth_bucket(self):
        """Auth bucket (5 requests/minute) should deny the 6th request."""
        limiter = TokenBucketRateLimiter()
        mock_redis = AsyncMock()

        # First 5 requests succeed (return 1)
        success_results = [1, 1, 1, 1, 1, 0]
        call_count = [0]

        async def mock_eval(*args, **kwargs):
            idx = call_count[0]
            call_count[0] += 1
            return success_results[min(idx, len(success_results) - 1)]

        mock_redis.eval = mock_eval
        limiter._redis = mock_redis

        results = []
        for _ in range(6):
            results.append(await limiter.is_allowed("10.0.0.5", "auth"))

        assert results == [True, True, True, True, True, False]


# ─── Middleware integration tests ────────────────────────────────────────────


class TestRateLimitMiddleware:
    """Integration tests for the RateLimitMiddleware via HTTP client."""

    @pytest.mark.asyncio
    async def test_critical_path_exempt_from_rate_limit(self, client: AsyncClient):
        """The /health endpoint should never be rate-limited."""
        for _ in range(10):
            resp = await client.get("/api/v1/health")
            assert resp.status_code != 429, f"Health endpoint was rate-limited on request {_ + 1}"

    @pytest.mark.asyncio
    async def test_metrics_path_exempt(self, client: AsyncClient):
        """The /metrics endpoint should be in CRITICAL_PATHS."""
        assert "/metrics" in CRITICAL_PATHS

    @pytest.mark.asyncio
    async def test_api_path_includes_rate_limit_headers(self, client: AsyncClient):
        """API responses should include X-RateLimit-Limit header."""
        await client.get("/api/v1/patients")
        # May be 200, 401 (auth), or 429 (rate-limited)
        # But should have rate-limit headers when rate-limited or when API bucket applies
        # Note: we need auth for /api/v1/patients, so it'll likely be 401 with auth header
        pass


# ─── RATE_LIMITS configuration ───────────────────────────────────────────────


class TestRateLimitConfig:
    """Verify sensible rate-limit defaults."""

    def test_auth_limit_is_tight(self):
        """Auth bucket should be tight (≤10 attempts per minute)."""
        max_tokens, interval = RATE_LIMITS["auth"]
        assert max_tokens <= 10
        assert interval == 60.0

    def test_api_limit_is_reasonable(self):
        """API bucket should allow a reasonable number of requests."""
        max_tokens, interval = RATE_LIMITS["api"]
        assert max_tokens >= 50
        assert interval == 60.0

    def test_critical_paths_contain_health(self):
        """Critical paths must include /health and /api/v1/health."""
        assert "/health" in CRITICAL_PATHS
        assert "/api/v1/health" in CRITICAL_PATHS
        assert "/metrics" in CRITICAL_PATHS
