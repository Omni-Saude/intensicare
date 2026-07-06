"""
MPI (Master Patient Index) client — async HTTP client for AMH MPI API.

Returns raw patient demographics as dicts. Encryption of PHI fields happens
upstream in mpi_resolver, not here. Graceful degradation: any network error
returns None, never raises.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger(__name__)


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

    async def get_patient(self, mpi_id: str) -> MPIPatient | None:
        """Fetch patient demographics from the MPI.

        Returns None when MPI is not configured, unreachable, or the patient
        is not found.
        """
        if not self.is_configured:
            return None

        try:
            client = await self._get_client()
            response = await client.get(f"/api/v1/patients/{mpi_id}")
            response.raise_for_status()
            payload = response.json()
            return MPIPatient.from_api_payload(mpi_id, payload)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == httpx.codes.NOT_FOUND:
                logger.info("MPI patient not found: %s", mpi_id)
                return None
            logger.warning("MPI HTTP error for patient %s: %s", mpi_id, exc)
            return None
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            logger.warning("MPI request failed for patient %s: %s", mpi_id, exc)
            return None


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
