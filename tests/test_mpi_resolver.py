"""
Tests for MPI resolver + patient_cache sync with discharge flush.

Covers:
  - Cache hit: returns cached patient without MPI call
  - Cache miss: queries MPI, caches result
  - Discharge flush: old discharged patients removed
  - MPI unreachable: returns None, alert proceeds (graceful degradation)
  - Demographics never leak to scorers (PHI remains encrypted)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.clients.mpi_client import MPIClient, MPIPatient
from intensicare.models.patient_cache import PatientCache
from intensicare.services.mpi_resolver import (
    DISCHARGE_FLUSH_DAYS,
    flush_discharged_patients,
    resolve_patient,
    sync_patient_cache,
)
from intensicare.services.patient_encryption import decrypt_phi, encrypt_phi

# ── Test constants ────────────────────────────────────────────────────
MPI_ID_HIT = "MPI-CACHED-001"
MPI_ID_MISS = "MPI-UNCACHED-001"
MPI_ID_FLUSH = "MPI-FLUSH-001"
MPI_ID_ACTIVE = "MPI-ACTIVE-001"
TENANT_A_KEY = "tenant-a-secret-key-32bytes!!"
TENANT_A = "tenant-a"


# ── Helpers ────────────────────────────────────────────────────────────


async def _set_encryption_key(db: AsyncSession, key: str) -> None:
    sanitized = key.replace("'", "''")
    await db.execute(text(f"SET app.encryption_key = '{sanitized}'"))


async def _ensure_pgcrypto(db: AsyncSession) -> None:
    await db.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto SCHEMA public"))


def _make_mpi_patient(
    mpi_id: str,
    *,
    display_name: str = "Test Patient",
    tenant_id: str = TENANT_A,
    mrn: str = "MRN-12345",
    gender: str = "M",
    unit: str = "ICU-1",
    discharged: bool = False,
) -> MPIPatient:
    return MPIPatient(
        mpi_id=mpi_id,
        tenant_id=tenant_id,
        display_name=display_name,
        mrn=mrn,
        birth_date="1980-01-15",
        cpf="123.456.789-00",
        cns="898001100000001",
        gender=gender,
        admission_dt="2025-12-01T08:00:00+00:00",
        discharge_dt="2025-12-15T10:00:00+00:00" if discharged else None,
        bed_id="BED-01",
        unit=unit,
        is_active=not discharged,
    )


# ── Fixtures ───────────────────────────────────────────────────────────


@pytest.fixture
async def crypto_session(db_session: AsyncSession) -> AsyncSession:
    """Session with pgcrypto enabled and tenant A encryption key set."""
    await _ensure_pgcrypto(db_session)
    await _set_encryption_key(db_session, TENANT_A_KEY)
    return db_session


# ── Test: Cache hit — no MPI call ──────────────────────────────────────


@pytest.mark.asyncio
async def test_cache_hit_avoids_mpi_call(crypto_session: AsyncSession) -> None:
    """A cached patient is returned immediately without querying MPI."""
    # Pre-populate the cache
    mpi_patient = _make_mpi_patient(MPI_ID_HIT, display_name="Cache Hit Patient")
    with patch.object(
        MPIClient, "get_patient", AsyncMock(return_value=mpi_patient)
    ):
        synced = await sync_patient_cache(crypto_session, MPI_ID_HIT)
    assert synced is not None

    # Now resolve — should hit cache, not MPI
    with patch.object(
        MPIClient, "get_patient", AsyncMock()
    ) as mock_mpi:
        result = await resolve_patient(crypto_session, MPI_ID_HIT)
        mock_mpi.assert_not_called()

    assert result is not None
    assert result.mpi_id == MPI_ID_HIT
    assert result.gender == "M"
    assert result.unit == "ICU-1"


# ── Test: Cache miss — queries MPI, caches result ─────────────────────


@pytest.mark.asyncio
async def test_cache_miss_queries_mpi_and_caches(crypto_session: AsyncSession) -> None:
    """A cache miss queries MPI and upserts the result into patient_cache."""
    mpi_patient = _make_mpi_patient(MPI_ID_MISS, display_name="Maria Cache Miss")

    # Mock the MPI client to return our synthetic patient
    with patch.object(
        MPIClient, "get_patient", AsyncMock(return_value=mpi_patient)
    ) as mock_mpi:
        result = await resolve_patient(crypto_session, MPI_ID_MISS)
        mock_mpi.assert_called_once_with(MPI_ID_MISS)

    assert result is not None
    assert result.mpi_id == MPI_ID_MISS
    assert result.gender == "M"
    assert result.unit == "ICU-1"
    assert result.synced_at is not None

    # Verify PHI was encrypted (not stored as plaintext)
    # display_name should be binary (BYTEA), not a plain string
    assert isinstance(result.display_name, bytes)
    assert len(result.display_name) > 0

    # Decrypt and verify
    decrypted_name = await decrypt_phi(crypto_session, result.display_name)
    assert decrypted_name == "Maria Cache Miss"

    # Verify mrn was encrypted too
    assert result.mrn is not None
    assert isinstance(result.mrn, bytes)
    decrypted_mrn = await decrypt_phi(crypto_session, result.mrn)
    assert decrypted_mrn == "MRN-12345"


# ── Test: PHI remains encrypted on cache hit ───────────────────────────


@pytest.mark.asyncio
async def test_demographics_never_leak_plaintext(crypto_session: AsyncSession) -> None:
    """Resolve returns encrypted PHI — scorers never see plaintext."""
    mpi_patient = _make_mpi_patient("MPI-SECRET-001", display_name="João Secreto")

    with patch.object(
        MPIClient, "get_patient", AsyncMock(return_value=mpi_patient)
    ):
        result = await resolve_patient(crypto_session, "MPI-SECRET-001")

    assert result is not None

    # PHI fields must be bytes (encrypted), not strings
    assert isinstance(result.display_name, bytes)
    assert isinstance(result.mrn, bytes)
    assert isinstance(result.birth_date, bytes)
    assert isinstance(result.cpf, bytes)
    assert isinstance(result.cns, bytes)

    # Plaintext must NOT appear in the binary fields
    assert b"Jo\xc3\xa3o Secreto" not in result.display_name  # utf-8 bytes
    assert b"MRN-" not in (result.mrn or b"")

    # Non-PHI fields remain accessible without decryption
    assert result.gender == "M"
    assert result.tenant_id == TENANT_A


# ── Test: MPI unreachable — graceful degradation ───────────────────────


@pytest.mark.asyncio
async def test_mpi_unreachable_returns_none(crypto_session: AsyncSession) -> None:
    """When MPI is unreachable, resolve returns None — alerts proceed."""
    with patch.object(
        MPIClient,
        "get_patient",
        AsyncMock(side_effect=ConnectionError("MPI unreachable")),
    ) as mock_mpi:
        result = await resolve_patient(crypto_session, "MPI-DOWN-001")
        mock_mpi.assert_called_once_with("MPI-DOWN-001")

    # Graceful degradation: None, not an exception
    assert result is None

    # Alert engine can proceed with None (no crash)
    # This mimics: if patient is None → skip alert evaluation


@pytest.mark.asyncio
async def test_mpi_timeout_returns_none(crypto_session: AsyncSession) -> None:
    """MPI timeout also returns None, never blocks."""
    import httpx

    with patch.object(
        MPIClient,
        "get_patient",
        AsyncMock(side_effect=httpx.TimeoutException("timeout")),
    ):
        result = await resolve_patient(crypto_session, "MPI-TIMEOUT-001")

    assert result is None


@pytest.mark.asyncio
async def test_sync_patient_cache_mpi_unreachable_returns_none(
    crypto_session: AsyncSession,
) -> None:
    """sync_patient_cache also handles MPI failure gracefully."""
    with patch.object(
        MPIClient,
        "get_patient",
        AsyncMock(return_value=None),  # MPI returns no data
    ):
        result = await sync_patient_cache(crypto_session, "MPI-NODATA-001")

    assert result is None


# ── Test: Discharge flush — old patients removed ──────────────────────


@pytest.mark.asyncio
async def test_flush_discharged_patients_removes_old(crypto_session: AsyncSession) -> None:
    """Patients discharged >30 days ago are removed by flush."""
    # Sync a discharged patient
    mpi_patient = _make_mpi_patient(
        MPI_ID_FLUSH,
        display_name="Old Discharged",
        discharged=True,
    )
    with patch.object(
        MPIClient, "get_patient", AsyncMock(return_value=mpi_patient)
    ):
        result = await sync_patient_cache(crypto_session, MPI_ID_FLUSH)

    assert result is not None
    assert result.is_active is False

    # Backdate synced_at to simulate old discharge (31 days ago)
    result.synced_at = datetime.now(timezone.utc) - timedelta(days=DISCHARGE_FLUSH_DAYS + 1)
    await crypto_session.flush()

    # Verify the patient exists before flush
    from sqlalchemy import select

    before = await crypto_session.execute(
        select(PatientCache).where(PatientCache.mpi_id == MPI_ID_FLUSH)
    )
    assert before.scalar_one_or_none() is not None

    # Flush
    deleted = await flush_discharged_patients(crypto_session)
    assert deleted >= 1

    # Verify the patient is gone
    after = await crypto_session.execute(
        select(PatientCache).where(PatientCache.mpi_id == MPI_ID_FLUSH)
    )
    assert after.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_flush_does_not_remove_active_patients(crypto_session: AsyncSession) -> None:
    """Active patients are never removed by flush, regardless of age."""
    mpi_patient = _make_mpi_patient(MPI_ID_ACTIVE, display_name="Still Active")
    with patch.object(
        MPIClient, "get_patient", AsyncMock(return_value=mpi_patient)
    ):
        result = await sync_patient_cache(crypto_session, MPI_ID_ACTIVE)

    assert result is not None
    assert result.is_active is True

    # Backdate synced_at
    result.synced_at = datetime.now(timezone.utc) - timedelta(days=DISCHARGE_FLUSH_DAYS + 10)
    await crypto_session.flush()

    # Flush
    deleted = await flush_discharged_patients(crypto_session)

    # Active patients should not be counted
    from sqlalchemy import select

    after = await crypto_session.execute(
        select(PatientCache).where(PatientCache.mpi_id == MPI_ID_ACTIVE)
    )
    assert after.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_flush_recent_discharge_not_removed(crypto_session: AsyncSession) -> None:
    """Recently discharged patients (<30 days) are not removed."""
    mpi_id = "MPI-RECENT-DC-001"
    mpi_patient = _make_mpi_patient(mpi_id, display_name="Recent DC", discharged=True)

    with patch.object(
        MPIClient, "get_patient", AsyncMock(return_value=mpi_patient)
    ):
        result = await sync_patient_cache(crypto_session, mpi_id)

    assert result is not None
    assert result.is_active is False

    # synced_at is recent (just now), so should NOT be flushed
    deleted = await flush_discharged_patients(crypto_session)

    from sqlalchemy import select

    after = await crypto_session.execute(
        select(PatientCache).where(PatientCache.mpi_id == mpi_id)
    )
    assert after.scalar_one_or_none() is not None


# ── Test: force_sync bypasses cache ────────────────────────────────────


@pytest.mark.asyncio
async def test_force_sync_bypasses_cache(crypto_session: AsyncSession) -> None:
    """force_sync=True always queries MPI even when cache exists."""
    # Pre-populate cache
    mpi_patient_v1 = _make_mpi_patient("MPI-FORCE-001", display_name="V1")
    with patch.object(
        MPIClient, "get_patient", AsyncMock(return_value=mpi_patient_v1)
    ):
        await sync_patient_cache(crypto_session, "MPI-FORCE-001")

    # Now force_sync with updated data
    mpi_patient_v2 = _make_mpi_patient(
        "MPI-FORCE-001", display_name="V2 Updated", unit="ICU-2"
    )
    with patch.object(
        MPIClient, "get_patient", AsyncMock(return_value=mpi_patient_v2)
    ) as mock_mpi:
        result = await resolve_patient(
            crypto_session, "MPI-FORCE-001", force_sync=True
        )
        mock_mpi.assert_called_once_with("MPI-FORCE-001")

    assert result is not None
    assert result.unit == "ICU-2"
    decrypted = await decrypt_phi(crypto_session, result.display_name)
    assert decrypted == "V2 Updated"
