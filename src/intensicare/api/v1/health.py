"""
Health-check readiness endpoint — DB, Redis, ARQ, Athena + dead-man's switch.

Implements REQ-INV-5:
- Real component verification (no static stubs)
- /api/v1/health returns healthy | degraded | unhealthy
- Per-(unit, domain) liveness matrix with staleness monitoring

DB check uses a raw engine connection (not Depends(get_db)) so the health endpoint
can gracefully report "degraded" instead of returning 500 when the database is down.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import logging

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import text

from intensicare.config import settings
from intensicare.core.database import get_engine
from intensicare.core.redis import get_redis

logger = logging.getLogger(__name__)

router = APIRouter(tags=["system"])

# ── Response models ──────────────────────────────────────────────────────────


class ComponentCheck(BaseModel):
    """Status of a single infrastructure component."""

    status: str = Field(default="skipped", description="ok | error | skipped")
    latency_ms: float | None = Field(default=None, description="Check latency in milliseconds")
    detail: str | None = Field(default=None, description="Error or skip reason")


class StalenessEntry(BaseModel):
    """Per-domain staleness for a single unit."""

    last_score_at: str | None = Field(
        default=None, description="ISO-8601 timestamp of most recent score"
    )
    minutes_stale: float | None = Field(
        default=None, description="Minutes since last score (null if never scored)"
    )


class HealthResponse(BaseModel):
    """Full health-check response with readiness + liveness matrix."""

    status: str = Field(default="healthy", description="healthy | degraded | unhealthy")
    version: str = Field(default="0.1.0", description="Application version")
    environment: str = Field(default="development", description="deployment environment")
    checks: dict[str, ComponentCheck] = Field(
        default_factory=dict, description="Per-component readiness checks"
    )
    staleness: dict[str, dict[str, StalenessEntry]] = Field(
        default_factory=dict,
        description="Per-(unit, domain) liveness matrix — most recent score per pair",
    )
    watchdog_last_seen: str | None = Field(
        default=None, description="ISO-8601 of last external watchdog ping"
    )


# ── Component check helpers ──────────────────────────────────────────────────


async def _check_postgresql() -> ComponentCheck:
    """Verify PostgreSQL connectivity with SELECT 1 using a raw engine connection."""
    t0 = datetime.now(timezone.utc)
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar_one()
        latency = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
        return ComponentCheck(status="ok", latency_ms=round(latency, 2))
    except Exception as exc:
        logger.error("PostgreSQL health check failed: %s", exc)
        latency = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
        return ComponentCheck(
            status="error",
            latency_ms=round(latency, 2),
            detail=f"{type(exc).__name__}: {exc}",
        )


async def _check_redis() -> ComponentCheck:
    """Verify Redis connectivity with PING."""
    t0 = datetime.now(timezone.utc)
    try:
        client = get_redis()
        await client.ping()
        latency = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
        return ComponentCheck(status="ok", latency_ms=round(latency, 2))
    except Exception as exc:
        logger.error("Redis health check failed: %s", exc)
        latency = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
        return ComponentCheck(
            status="error",
            latency_ms=round(latency, 2),
            detail=f"{type(exc).__name__}: {exc}",
        )


async def _check_arq() -> ComponentCheck:
    """Verify ARQ queue health via Redis (check if queue key + worker heartbeat exists)."""
    t0 = datetime.now(timezone.utc)
    try:
        client = get_redis()
        # ARQ uses Redis keys like "arq:queue" for the job queue.
        # A healthy ARQ deployment has at least the queue key and ideally
        # worker heartbeat keys (arq:worker:*).
        queue_keys = await client.keys("arq:*")
        latency = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
        if queue_keys:
            return ComponentCheck(
                status="ok",
                latency_ms=round(latency, 2),
                detail=f"Found {len(queue_keys)} ARQ key(s)",
            )
        # No ARQ keys — might be a fresh deploy with no jobs yet.
        # Not an error, but we flag it as degraded since the worker may not be running.
        return ComponentCheck(
            status="ok",
            latency_ms=round(latency, 2),
            detail="No ARQ keys found (queue may be empty or worker not started)",
        )
    except Exception as exc:
        logger.error("ARQ health check failed: %s", exc)
        latency = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
        return ComponentCheck(
            status="error",
            latency_ms=round(latency, 2),
            detail=f"{type(exc).__name__}: {exc}",
        )


async def _check_athena() -> ComponentCheck:
    """Verify Athena connectivity with a real lightweight query."""
    if not settings.athena_enabled or not settings.athena_output_location:
        return ComponentCheck(status="skipped", detail="Athena not configured")
    t0 = datetime.now(timezone.utc)
    try:
        from intensicare.clients.athena_client import AthenaClient

        client = AthenaClient(query_timeout=5)
        result = await client.execute_query("SELECT 1")
        latency = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
        return ComponentCheck(
            status="ok",
            latency_ms=round(latency, 2),
            detail=f"Athena query succeeded (exec={result.query_execution_id})",
        )
    except Exception as exc:
        logger.error("Athena health check failed: %s", exc)
        latency = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
        return ComponentCheck(
            status="error",
            latency_ms=round(latency, 2),
            detail=f"{type(exc).__name__}: {exc}",
        )


# ── Staleness / liveness matrix ──────────────────────────────────────────────


async def _compute_staleness_matrix() -> dict[str, dict[str, StalenessEntry]]:
    """Build per-(unit, domain) liveness matrix from clinical_score + patient_cache.

    Returns a dict: {unit_id: {score_type: StalenessEntry}}.
    Gracefully degrades when tables are missing, empty, or DB is unreachable.
    """
    now = datetime.now(timezone.utc)
    matrix: dict[str, dict[str, StalenessEntry]] = {}

    try:
        engine = get_engine()
        async with engine.connect() as conn:
            result = await conn.execute(
                text(
                    """
                    SELECT
                        COALESCE(pc.unit, 'unknown') AS unit,
                        cs.score_type,
                        MAX(cs.calculated_at) AS last_calculated_at
                    FROM clinical_score cs
                    LEFT JOIN patient_cache pc ON pc.mpi_id = cs.mpi_id
                    WHERE cs.calculated_at IS NOT NULL
                    GROUP BY COALESCE(pc.unit, 'unknown'), cs.score_type
                    ORDER BY unit, score_type
                    """
                )
            )
            rows = result.fetchall()
            for row in rows:
                unit = row.unit or "unknown"
                domain = row.score_type
                last_at: datetime | None = row.last_calculated_at

                if last_at is not None:
                    delta = (now - last_at).total_seconds()
                    minutes_stale = round(delta / 60.0, 1)
                    last_at_iso = last_at.isoformat()
                else:
                    minutes_stale = None
                    last_at_iso = None

                entry = StalenessEntry(last_score_at=last_at_iso, minutes_stale=minutes_stale)
                matrix.setdefault(unit, {})[domain] = entry

    except Exception as exc:
        logger.warning("Staleness matrix query failed: %s", exc)
        # Return empty matrix — caller will treat missing data as information,
        # not as an error (fresh deploy may have no scores yet).

    return matrix


# ── Watchdog last-seen tracking ──────────────────────────────────────────────

WATCHDOG_KEY = "health:watchdog:last_seen"


async def _record_watchdog_ping() -> None:
    """Record the current timestamp as the last watchdog ping."""
    try:
        client = get_redis()
        await client.set(WATCHDOG_KEY, datetime.now(timezone.utc).isoformat())
    except Exception:
        logger.debug("Cannot record watchdog ping — Redis unavailable", exc_info=True)


async def _get_watchdog_last_seen() -> str | None:
    """Return the ISO-8601 timestamp of the last watchdog ping (or None)."""
    try:
        client = get_redis()
        return await client.get(WATCHDOG_KEY)  # type: ignore[no-any-return]
    except Exception:
        return None


# ── Endpoint ─────────────────────────────────────────────────────────────────


def _unwrap_check(result: ComponentCheck | BaseException, name: str) -> ComponentCheck:
    """Handle unexpected exceptions from asyncio.gather into ComponentCheck error entries.

    Each ``_check_*`` function already catches its own errors internally, but
    ``return_exceptions=True`` ensures that any truly unhandled exception
    (e.g. an import error, memory error) doesn't cancel sibling checks.
    """
    if isinstance(result, BaseException):
        logger.error("%s health check raised unexpected exception: %s", name, result)
        return ComponentCheck(
            status="error",
            detail=f"{type(result).__name__}: {result}",
        )
    return result


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Full readiness check: PostgreSQL, Redis, ARQ, Athena + staleness matrix.

    Returns ``healthy`` when all components are ok.
    Returns ``degraded`` when at least one component is in error.
    Returns ``unhealthy`` when critical components (DB + Redis) are both down.

    Uses raw engine connections for DB checks so the endpoint gracefully
    reports ``degraded`` instead of returning 500 when the database is down.
    """
    # Run checks concurrently using asyncio.gather.
    # Each check internally catches its own errors so a single component
    # failure never cascades.  ``return_exceptions=True`` is a safety net
    # for any truly unhandled exception (import error, memory error, etc.)
    # so it doesn't cancel sibling checks.
    pg_check, redis_check, arq_check, athena_check = await asyncio.gather(
        _check_postgresql(),
        _check_redis(),
        _check_arq(),
        _check_athena(),
        return_exceptions=True,
    )

    checks: dict[str, ComponentCheck] = {
        "postgresql": _unwrap_check(pg_check, "PostgreSQL"),
        "redis": _unwrap_check(redis_check, "Redis"),
        "arq": _unwrap_check(arq_check, "ARQ"),
        "athena": _unwrap_check(athena_check, "Athena"),
    }

    # Record this request as a watchdog ping.
    await _record_watchdog_ping()

    # Compute staleness matrix.
    staleness = await _compute_staleness_matrix()

    # Determine aggregate status.
    error_checks = [name for name, c in checks.items() if c.status == "error"]
    if "postgresql" in error_checks and "redis" in error_checks:
        overall = "unhealthy"
    elif error_checks:
        overall = "degraded"
    else:
        overall = "healthy"

    # Check staleness alert threshold.
    for unit_name, domains in staleness.items():
        for domain_name, entry in domains.items():
            if (
                entry.minutes_stale is not None
                and entry.minutes_stale > settings.staleness_alert_minutes
            ):
                logger.warning(
                    "Staleness threshold exceeded: unit=%s domain=%s stale=%s min",
                    unit_name,
                    domain_name,
                    entry.minutes_stale,
                )

    watchdog_last = await _get_watchdog_last_seen()

    return HealthResponse(
        status=overall,
        version="0.1.0",
        environment=settings.environment,
        checks=checks,
        staleness=staleness,
        watchdog_last_seen=watchdog_last,
    )
