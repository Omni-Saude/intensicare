"""
MPI (Master Patient Index) client — async HTTP client for AMH MPI API.

Returns raw patient demographics as dicts. Encryption of PHI fields happens
upstream in mpi_resolver, not here. Graceful degradation: any network error
returns None, never raises.

F-INT-005: retry with tenacity (3 attempts, exponential backoff 1s→2s→4s),
circuit breaker via Redis (3 consecutive failures → open 30s).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

# ── Circuit breaker constants ──────────────────────────────────────────

CIRCUIT_FAILURE_KEY = "circuit:mpi:failure_count"
CIRCUIT_OPEN_KEY = "circuit:mpi:open_until"
CIRCUIT_FAILURE_THRESHOLD = 3
CIRCUIT_OPEN_TIMEOUT = 30  # seconds


# ── Retry predicate ────────────────────────────────────────────────────


def _should_retry_mpi(exception: BaseException) -> bool:
    """Only retry on 5xx HTTP errors, timeouts, and connection errors.

    404 (NOT_FOUND) is a normal response — do not retry.
    """
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code >= 500
    return isinstance(exception, (httpx.RequestError, httpx.TimeoutException))


@dataclass
class MPIPatient:
    """Structured patient data returned by the MPI API."""

    mpi_id: str
    tenant_id: str | None = None
    display_name: str | None = None
    mrn: str | None = None
    birth_date: str | None = None  # ISO date
    cpf: str | None = None
    cns: str | None = None
    gender: str | None = None
    admission_dt: str | None = None  # ISO datetime
    discharge_dt: str | None = None  # ISO datetime
    bed_id: str | None = None
    unit: str | None = None
    is_active: bool = True
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_payload(cls, mpi_id: str, payload: dict[str, Any]) -> MPIPatient:
        """Parse a JSON payload from the MPI API into a MPIPatient."""
        return cls(
            mpi_id=mpi_id,
            tenant_id=payload.get("tenant_id"),
            display_name=payload.get("display_name"),
            mrn=payload.get("mrn"),
            birth_date=payload.get("birth_date"),
            cpf=payload.get("cpf"),
            cns=payload.get("cns"),
            gender=payload.get("gender"),
            admission_dt=payload.get("admission_dt"),
            discharge_dt=payload.get("discharge_dt"),
            bed_id=payload.get("bed_id"),
            unit=payload.get("unit"),
            is_active=not payload.get("discharge_dt"),
            raw=payload,
        )


class MPIClient:
    """Async HTTP client for the MPI REST API.

    Gracefully degrades when MPI is unreachable or not configured.
    """

    def __init__(
        self,
        base_url: str | None = None,
        auth_token: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self._base_url = (base_url or "").rstrip("/")
        self._auth_token = auth_token
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        """True when an MPI base URL has been set."""
        return bool(self._base_url)

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers: dict[str, str] = {"Accept": "application/json"}
            if self._auth_token:
                headers["Authorization"] = f"Bearer {self._auth_token}"
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=headers,
                timeout=httpx.Timeout(self._timeout),
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # ── Circuit breaker helpers ──────────────────────────────────────

    async def _circuit_allows(self) -> bool:
        """Check if the circuit breaker allows requests.

        Returns False when the circuit is open (consecutive failures exceeded
        threshold within the timeout window).  Gracefully allows requests when
        Redis is unavailable.
        """
        try:
            from intensicare.core.redis import get_redis  # noqa: PLC0415

            redis = get_redis()
            open_until = await redis.get(CIRCUIT_OPEN_KEY)
            if open_until is not None:
                if float(open_until) > time.time():
                    return False
                # Circuit timeout expired — reset
                await redis.delete(CIRCUIT_FAILURE_KEY, CIRCUIT_OPEN_KEY)
        except Exception:
            pass  # Redis unavailable → allow requests
        return True

    async def _record_failure(self) -> None:
        """Record a failure for circuit breaker tracking.

        After CIRCUIT_FAILURE_THRESHOLD consecutive failures the circuit opens
        for CIRCUIT_OPEN_TIMEOUT seconds.
        """
        try:
            from intensicare.core.redis import get_redis  # noqa: PLC0415

            redis = get_redis()
            count: int = await redis.incr(CIRCUIT_FAILURE_KEY)  # type: ignore[assignment]
            if count >= CIRCUIT_FAILURE_THRESHOLD:
                await redis.set(
                    CIRCUIT_OPEN_KEY, str(time.time() + CIRCUIT_OPEN_TIMEOUT)
                )
                logger.warning(
                    "MPI circuit breaker OPEN — %d consecutive failures", count
                )
        except Exception:
            pass

    async def _record_success(self) -> None:
        """Reset circuit breaker on successful MPI call."""
        try:
            from intensicare.core.redis import get_redis  # noqa: PLC0415

            redis = get_redis()
            await redis.delete(CIRCUIT_FAILURE_KEY, CIRCUIT_OPEN_KEY)
        except Exception:
            pass

    # ── Retry-capable inner call ──────────────────────────────────────

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception(_should_retry_mpi),
    )
    async def _call_mpi_with_retry(self, mpi_id: str) -> MPIPatient:
        """Execute the MPI HTTP request with retry on 5xx / timeout.

        Raises httpx.HTTPStatusError (404) immediately — NOT retried.
        Raises httpx.HTTPStatusError (5xx), RequestError, or TimeoutException
        to trigger tenacity retry.
        """
        client = await self._get_client()
        response = await client.get(f"/api/v1/patients/{mpi_id}")
        response.raise_for_status()
        payload = response.json()
        return MPIPatient.from_api_payload(mpi_id, payload)

    # ── Public API ────────────────────────────────────────────────────

    async def get_patient(self, mpi_id: str) -> MPIPatient | None:
        """Fetch patient demographics from the MPI with retry + circuit breaker.

        Returns None when MPI is not configured, the circuit breaker is open,
        the patient is not found (404), or the request fails after all retries.
        """
        if not self.is_configured:
            return None

        # Circuit breaker: if open, return degraded response immediately.
        if not await self._circuit_allows():
            logger.warning(
                "MPI circuit breaker open — returning degraded response for %s",
                mpi_id,
            )
            return None

        try:
            result = await self._call_mpi_with_retry(mpi_id)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                logger.info("MPI patient not found: %s", mpi_id)
                return None
            # 5xx — all retries exhausted
            logger.error(
                "MPI HTTP %d for patient %s after %d retries",
                exc.response.status_code,
                mpi_id,
                3,
            )
            await self._record_failure()
            return None
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            logger.error(
                "MPI request failed for patient %s after %d retries: %s",
                mpi_id,
                3,
                exc,
            )
            await self._record_failure()
            return None
        except Exception as exc:
            logger.warning("MPI unexpected error for patient %s: %s", mpi_id, exc)
            await self._record_failure()
            return None

        # Success — reset circuit breaker
        await self._record_success()
        return result


# Module-level singleton (lazy, cached).
_mpi_client: MPIClient | None = None


def get_mpi_client() -> MPIClient:
    """Return the module-level MPI client, creating it on first call."""
    global _mpi_client
    if _mpi_client is None:
        from intensicare.config import settings  # noqa: PLC0415 — avoid circular import

        base = settings.mpi_base_url or None
        token = (
            settings.mpi_auth_token.get_secret_value()
            if settings.mpi_auth_token
            else None
        )
        _mpi_client = MPIClient(base_url=base, auth_token=token)
    return _mpi_client


async def resolve_mpi(mpi_id: str) -> MPIPatient | None:
    """Convenience function: resolve an MPI patient with retry + circuit breaker.

    Returns the parsed MPIPatient, or None when the patient is not found,
    MPI is unreachable, or the circuit breaker is open.
    """
    client = get_mpi_client()
    return await client.get_patient(mpi_id)
