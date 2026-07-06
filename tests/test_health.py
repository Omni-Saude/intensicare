"""
Tests for the /api/v1/health endpoint and health check logic.

Covers:
  - GET /api/v1/health returns 200 with correct response structure
  - Component checks: postgresql, redis, arq, athena
  - Staleness matrix computed correctly
  - Aggregate status determination (healthy / degraded / unhealthy)
  - Watchdog ping tracking
  - ComponentCheck and HealthResponse model serialization
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from intensicare.api.v1.health import (
    ComponentCheck,
    HealthResponse,
    StalenessEntry,
    _check_arq,
    _check_athena,
    _check_postgresql,
    _check_redis,
    _compute_staleness_matrix,
    _get_watchdog_last_seen,
    _record_watchdog_ping,
    health_check,
)


# ─── ComponentCheck model tests ──────────────────────────────────────────────


class TestComponentCheckModel:
    """Tests for ComponentCheck Pydantic model."""

    def test_defaults(self):
        c = ComponentCheck()
        assert c.status == "skipped"
        assert c.latency_ms is None
        assert c.detail is None

    def test_ok_check(self):
        c = ComponentCheck(status="ok", latency_ms=12.5)
        assert c.status == "ok"
        assert c.latency_ms == 12.5

    def test_error_check(self):
        c = ComponentCheck(status="error", latency_ms=150.0, detail="Connection refused")
        assert c.status == "error"
        assert c.detail == "Connection refused"


# ─── HealthResponse model tests ──────────────────────────────────────────────


class TestHealthResponseModel:
    """Tests for HealthResponse Pydantic model."""

    def test_defaults(self):
        h = HealthResponse()
        assert h.status == "healthy"
        assert h.version == "0.1.0"
        assert h.environment == "development"
        assert h.checks == {}
        assert h.staleness == {}
        assert h.watchdog_last_seen is None

    def test_full_response(self):
        h = HealthResponse(
            status="healthy",
            version="1.0.0",
            environment="production",
            checks={
                "postgresql": ComponentCheck(status="ok", latency_ms=5.0),
                "redis": ComponentCheck(status="ok", latency_ms=2.0),
            },
            staleness={
                "ICU-1": {
                    "mews": StalenessEntry(last_score_at="2026-01-01T00:00:00Z", minutes_stale=5.0),
                },
            },
            watchdog_last_seen="2026-01-01T00:00:00Z",
        )
        assert h.status == "healthy"
        assert len(h.checks) == 2
        assert "ICU-1" in h.staleness
        assert h.watchdog_last_seen is not None


# ─── Component check functions (with mocked dependencies) ────────────────────


class TestPostgresqlCheck:
    """Tests for _check_postgresql."""

    @pytest.mark.asyncio
    async def test_successful_check(self):
        """Should return ok when DB connection works."""
        mock_conn = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_conn.execute.return_value = mock_result

        mock_engine = MagicMock()
        mock_engine.connect.return_value.__aenter__.return_value = mock_conn

        with patch(
            "intensicare.api.v1.health.get_engine", return_value=mock_engine
        ):
            result = await _check_postgresql()
            assert result.status == "ok"
            assert result.latency_ms is not None
            assert result.latency_ms >= 0

    @pytest.mark.asyncio
    async def test_failed_check(self):
        """Should return error when DB connection fails."""
        with patch(
            "intensicare.api.v1.health.get_engine",
            side_effect=Exception("Connection refused"),
        ):
            result = await _check_postgresql()
            assert result.status == "error"
            assert "Connection refused" in (result.detail or "")


class TestRedisCheck:
    """Tests for _check_redis."""

    @pytest.mark.asyncio
    async def test_successful_check(self):
        """Should return ok when Redis PING succeeds."""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True

        with patch(
            "intensicare.api.v1.health.get_redis", return_value=mock_redis
        ):
            result = await _check_redis()
            assert result.status == "ok"

    @pytest.mark.asyncio
    async def test_failed_check(self):
        """Should return error when Redis is unreachable."""
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = Exception("Connection refused")

        with patch(
            "intensicare.api.v1.health.get_redis", return_value=mock_redis
        ):
            result = await _check_redis()
            assert result.status == "error"


class TestArqCheck:
    """Tests for _check_arq."""

    @pytest.mark.asyncio
    async def test_keys_found(self):
        """When ARQ keys exist in Redis, return ok."""
        mock_redis = AsyncMock()
        mock_redis.keys.return_value = [b"arq:queue", b"arq:worker:abc"]

        with patch(
            "intensicare.api.v1.health.get_redis", return_value=mock_redis
        ):
            result = await _check_arq()
            assert result.status == "ok"
            assert "2 ARQ key" in (result.detail or "")

    @pytest.mark.asyncio
    async def test_no_keys_found(self):
        """When no ARQ keys exist, still return ok but note it."""
        mock_redis = AsyncMock()
        mock_redis.keys.return_value = []

        with patch(
            "intensicare.api.v1.health.get_redis", return_value=mock_redis
        ):
            result = await _check_arq()
            assert result.status == "ok"
            assert "No ARQ keys" in (result.detail or "")

    @pytest.mark.asyncio
    async def test_redis_error(self):
        """Should return error when Redis fails."""
        mock_redis = AsyncMock()
        mock_redis.keys.side_effect = Exception("Redis down")

        with patch(
            "intensicare.api.v1.health.get_redis", return_value=mock_redis
        ):
            result = await _check_arq()
            assert result.status == "error"


class TestAthenaCheck:
    """Tests for _check_athena."""

    @pytest.mark.asyncio
    async def test_skipped_when_not_configured(self):
        """Should return skipped when Athena is not enabled."""
        with patch(
            "intensicare.api.v1.health.settings.athena_enabled", False
        ):
            result = await _check_athena()
            assert result.status == "skipped"
            assert "not configured" in (result.detail or "").lower()

    @pytest.mark.asyncio
    async def test_ok_when_configured(self):
        """Should return ok when Athena is enabled and configured."""
        with patch(
            "intensicare.api.v1.health.settings.athena_enabled", True
        ), patch(
            "intensicare.api.v1.health.settings.athena_output_location", "s3://bucket/"
        ):
            result = await _check_athena()
            assert result.status == "ok"


# ─── Staleness matrix tests ──────────────────────────────────────────────────


class TestStalenessMatrix:
    """Tests for _compute_staleness_matrix."""

    @pytest.mark.asyncio
    async def test_returns_dict_structure(self):
        """Should return a dict of units -> domains -> StalenessEntry."""
        mock_conn = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_conn.execute.return_value = mock_result

        mock_engine = MagicMock()
        mock_engine.connect.return_value.__aenter__.return_value = mock_conn

        with patch(
            "intensicare.api.v1.health.get_engine", return_value=mock_engine
        ):
            result = await _compute_staleness_matrix()
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_populates_entries(self):
        """Should populate staleness entries from rows."""
        now = datetime.now(timezone.utc)
        row = MagicMock()
        row.unit = "ICU-1"
        row.score_type = "mews"
        row.last_calculated_at = now

        mock_conn = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [row]
        mock_conn.execute.return_value = mock_result

        mock_engine = MagicMock()
        mock_engine.connect.return_value.__aenter__.return_value = mock_conn

        with patch(
            "intensicare.api.v1.health.get_engine", return_value=mock_engine
        ):
            result = await _compute_staleness_matrix()
            assert "ICU-1" in result
            assert "mews" in result["ICU-1"]
            entry = result["ICU-1"]["mews"]
            assert entry.last_score_at is not None
            assert entry.minutes_stale is not None

    @pytest.mark.asyncio
    async def test_handles_db_error_gracefully(self):
        """When DB query fails, return empty matrix."""
        with patch(
            "intensicare.api.v1.health.get_engine",
            side_effect=Exception("DB unreachable"),
        ):
            result = await _compute_staleness_matrix()
            assert result == {}


# ─── Watchdog tests ──────────────────────────────────────────────────────────


class TestWatchdog:
    """Tests for watchdog ping tracking."""

    @pytest.mark.asyncio
    async def test_record_ping(self):
        """Should set Redis key with ISO timestamp."""
        mock_redis = AsyncMock()
        with patch(
            "intensicare.api.v1.health.get_redis", return_value=mock_redis
        ):
            await _record_watchdog_ping()
            mock_redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_last_seen(self):
        """Should return the stored timestamp."""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = "2026-07-06T12:00:00Z"
        with patch(
            "intensicare.api.v1.health.get_redis", return_value=mock_redis
        ):
            result = await _get_watchdog_last_seen()
            assert result == "2026-07-06T12:00:00Z"

    @pytest.mark.asyncio
    async def test_get_last_seen_redis_unavailable(self):
        """Should return None when Redis is down."""
        with patch(
            "intensicare.api.v1.health.get_redis",
            side_effect=Exception("Redis down"),
        ):
            result = await _get_watchdog_last_seen()
            assert result is None


# ─── Aggregate status tests ──────────────────────────────────────────────────


class TestAggregateStatus:
    """Tests for overall health status determination."""

    @pytest.mark.asyncio
    async def test_all_healthy(self):
        """All components ok → healthy."""
        with patch(
            "intensicare.api.v1.health._check_postgresql",
            return_value=ComponentCheck(status="ok", latency_ms=5.0),
        ), patch(
            "intensicare.api.v1.health._check_redis",
            return_value=ComponentCheck(status="ok", latency_ms=2.0),
        ), patch(
            "intensicare.api.v1.health._check_arq",
            return_value=ComponentCheck(status="ok", latency_ms=3.0),
        ), patch(
            "intensicare.api.v1.health._check_athena",
            return_value=ComponentCheck(status="skipped", detail="Not configured"),
        ), patch(
            "intensicare.api.v1.health._compute_staleness_matrix",
            return_value={},
        ), patch(
            "intensicare.api.v1.health._record_watchdog_ping",
            new_callable=AsyncMock,
        ), patch(
            "intensicare.api.v1.health._get_watchdog_last_seen",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await health_check()
            assert response.status == "healthy"

    @pytest.mark.asyncio
    async def test_one_degraded_component(self):
        """One component in error → degraded."""
        with patch(
            "intensicare.api.v1.health._check_postgresql",
            return_value=ComponentCheck(status="ok", latency_ms=5.0),
        ), patch(
            "intensicare.api.v1.health._check_redis",
            return_value=ComponentCheck(status="error", latency_ms=100.0, detail="Timeout"),
        ), patch(
            "intensicare.api.v1.health._check_arq",
            return_value=ComponentCheck(status="ok", latency_ms=3.0),
        ), patch(
            "intensicare.api.v1.health._check_athena",
            return_value=ComponentCheck(status="skipped"),
        ), patch(
            "intensicare.api.v1.health._compute_staleness_matrix",
            return_value={},
        ), patch(
            "intensicare.api.v1.health._record_watchdog_ping",
            new_callable=AsyncMock,
        ), patch(
            "intensicare.api.v1.health._get_watchdog_last_seen",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await health_check()
            assert response.status == "degraded"

    @pytest.mark.asyncio
    async def test_both_critical_components_fail(self):
        """PostgreSQL AND Redis both in error → unhealthy."""
        with patch(
            "intensicare.api.v1.health._check_postgresql",
            return_value=ComponentCheck(status="error", latency_ms=100.0, detail="Down"),
        ), patch(
            "intensicare.api.v1.health._check_redis",
            return_value=ComponentCheck(status="error", latency_ms=100.0, detail="Down"),
        ), patch(
            "intensicare.api.v1.health._check_arq",
            return_value=ComponentCheck(status="error", latency_ms=100.0),
        ), patch(
            "intensicare.api.v1.health._check_athena",
            return_value=ComponentCheck(status="skipped"),
        ), patch(
            "intensicare.api.v1.health._compute_staleness_matrix",
            return_value={},
        ), patch(
            "intensicare.api.v1.health._record_watchdog_ping",
            new_callable=AsyncMock,
        ), patch(
            "intensicare.api.v1.health._get_watchdog_last_seen",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await health_check()
            assert response.status == "unhealthy"


# ─── HTTP API integration tests ──────────────────────────────────────────────


class TestHealthEndpoint:
    """Integration tests hitting the actual /api/v1/health endpoint."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self, client: AsyncClient):
        """The health endpoint should return 200 OK."""
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_health_response_structure(self, client: AsyncClient):
        """The response should contain the correct structure."""
        resp = await client.get("/api/v1/health")
        data = resp.json()
        assert "status" in data
        assert "version" in data
        assert "environment" in data
        assert "checks" in data
        assert "staleness" in data
        assert "watchdog_last_seen" in data

    @pytest.mark.asyncio
    async def test_health_checks_contain_required_components(self, client: AsyncClient):
        """Checks should include postgresql, redis, arq, athena."""
        resp = await client.get("/api/v1/health")
        data = resp.json()
        checks = data.get("checks", {})
        assert "postgresql" in checks
        assert "redis" in checks
        assert "arq" in checks
        assert "athena" in checks

    @pytest.mark.asyncio
    async def test_health_status_is_valid(self, client: AsyncClient):
        """Status should be one of: healthy, degraded, unhealthy."""
        resp = await client.get("/api/v1/health")
        data = resp.json()
        assert data["status"] in ("healthy", "degraded", "unhealthy")

    @pytest.mark.asyncio
    async def test_staleness_is_present(self, client: AsyncClient):
        """Staleness matrix should be present (dict, possibly empty)."""
        resp = await client.get("/api/v1/health")
        data = resp.json()
        assert isinstance(data["staleness"], dict)
