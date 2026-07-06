"""
MPI Resolver — patient_cache sync with discharge flush.

Responsibilities:
  - resolve_patient: check local cache, fall back to MPI (graceful degradation)
  - sync_patient_cache: upsert from MPI, stamp synced_at
  - flush_discharged_patients: remove patients discharged >30 days ago

Demographics (PHI) are NEVER exposed to the scoring engine.
The resolver only returns the PatientCache ORM object; PHI columns remain
encrypted (BYTEA). Callers that need plaintext must use the dedicated
decryption service (patient_encryption) with proper authorization.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.clients.mpi_client import get_mpi_client
from intensicare.models.patient_cache import PatientCache
from intensicare.services.patient_encryption import compute_mrn_bidx, encrypt_phi

logger = logging.getLogger(__name__)

# ── Discharge flush threshold ──────────────────────────────────────────
DISCHARGE_FLUSH_DAYS = 30


# ── Resolve ────────────────────────────────────────────────────────────


async def resolve_patient(
    db: AsyncSession,
    mpi_id: str,
    *,
    force_sync: bool = False,
) -> PatientCache | None:
    """Resolve a patient, checking the local cache first.

    Cache-hit path (fast): returns the cached PatientCache without any
    external API call.

    Cache-miss path:
        1. Queries MPI for patient demographics.
        2. If MPI is unreachable, returns ``None`` — the caller (e.g. alert
           engine) proceeds without blocking.  Graceful degradation.
        3. If MPI returns data, upserts it into patient_cache with
           ``synced_at`` set to now, then returns the cached row.

    Parameters
    ----------
    db : AsyncSession
        Active database session.
    mpi_id : str
        MPI identifier of the patient.
    force_sync : bool
        If True, skip the cache-hit check and always re-sync from MPI.

    Returns
    -------
    PatientCache | None
        The cached patient record, or None if the patient cannot be resolved.
    """
    # ── Cache hit ──────────────────────────────────────────────────
    if not force_sync:
        cached = await _get_cached(db, mpi_id)
        if cached is not None:
            return cached

    # ── Cache miss — query MPI ─────────────────────────────────────
    return await sync_patient_cache(db, mpi_id)


# ── Sync ───────────────────────────────────────────────────────────────


async def sync_patient_cache(
    db: AsyncSession,
    mpi_id: str,
) -> PatientCache | None:
    """Fetch patient demographics from MPI and upsert into patient_cache.

    PHI fields (display_name, mrn, birth_date, cpf, cns) are encrypted
    via pgcrypto before storage.  The ``synced_at`` column is stamped
    with the current UTC time.

    Returns the upserted PatientCache row, or None if MPI is unreachable
    or returns no data.
    """
    # ── Query MPI ──────────────────────────────────────────────────
    mpi_client = get_mpi_client()
    try:
        mpi_patient = await mpi_client.get_patient(mpi_id)
    except Exception:
        logger.exception("MPI client error for patient %s — graceful degradation", mpi_id)
        return None

    if mpi_patient is None:
        logger.warning("MPI returned no data for %s — patient unresolved", mpi_id)
        return None

    # ── Encrypt PHI fields ─────────────────────────────────────────
    enc_display_name = (
        await encrypt_phi(db, mpi_patient.display_name)
        if mpi_patient.display_name
        else await encrypt_phi(db, "")
    )
    enc_mrn = (
        await encrypt_phi(db, mpi_patient.mrn)
        if mpi_patient.mrn
        else None
    )
    enc_birth_date = (
        await encrypt_phi(db, mpi_patient.birth_date)
        if mpi_patient.birth_date
        else None
    )
    enc_cpf = (
        await encrypt_phi(db, mpi_patient.cpf)
        if mpi_patient.cpf
        else None
    )
    enc_cns = (
        await encrypt_phi(db, mpi_patient.cns)
        if mpi_patient.cns
        else None
    )
    mrn_bidx = (
        await compute_mrn_bidx(db, mpi_patient.mrn)
        if mpi_patient.mrn
        else None
    )

    # ── Parse datetimes ────────────────────────────────────────────
    admission_dt = _parse_iso(mpi_patient.admission_dt)
    discharge_dt = _parse_iso(mpi_patient.discharge_dt)
    is_active = discharge_dt is None

    # ── Upsert into patient_cache ──────────────────────────────────
    synced_at = datetime.now(timezone.utc)

    existing = await _get_cached(db, mpi_id)
    if existing is not None:
        # Update existing row
        existing.tenant_id = mpi_patient.tenant_id or existing.tenant_id
        existing.display_name = enc_display_name
        existing.mrn = enc_mrn
        existing.birth_date = enc_birth_date
        existing.cpf = enc_cpf
        existing.cns = enc_cns
        existing.mrn_bidx = mrn_bidx
        existing.gender = mpi_patient.gender
        existing.admission_dt = admission_dt
        existing.bed_id = mpi_patient.bed_id
        existing.unit = mpi_patient.unit
        existing.synced_at = synced_at
        existing.is_active = is_active
        await db.flush()
        await db.refresh(existing)
        return existing

    # Insert new row
    patient = PatientCache(
        mpi_id=mpi_id,
        tenant_id=mpi_patient.tenant_id or "default",
        display_name=enc_display_name,
        mrn=enc_mrn,
        birth_date=enc_birth_date,
        cpf=enc_cpf,
        cns=enc_cns,
        mrn_bidx=mrn_bidx,
        gender=mpi_patient.gender,
        admission_dt=admission_dt,
        bed_id=mpi_patient.bed_id,
        unit=mpi_patient.unit,
        synced_at=synced_at,
        is_active=is_active,
    )
    db.add(patient)
    await db.flush()
    await db.refresh(patient)

    logger.info("Patient %s synced from MPI (active=%s)", mpi_id, is_active)
    return patient


# ── Flush ──────────────────────────────────────────────────────────────


async def flush_discharged_patients(db: AsyncSession) -> int:
    """Remove patients discharged more than 30 days ago.

    Only removes rows where ``is_active`` is False **and** ``synced_at``
    (proxy for last-known-discharge) is older than DISCHARGE_FLUSH_DAYS.

    Returns the number of rows deleted.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=DISCHARGE_FLUSH_DAYS)

    stmt = (
        delete(PatientCache)
        .where(
            PatientCache.is_active.is_(False),
            PatientCache.synced_at.is_not(None),
            PatientCache.synced_at < cutoff,
        )
    )
    result = await db.execute(stmt)
    deleted = result.rowcount
    if deleted:
        logger.info(
            "Flushed %d discharged patient(s) older than %d days",
            deleted,
            DISCHARGE_FLUSH_DAYS,
        )
    return deleted


# ── Internal helpers ──────────────────────────────────────────────────


async def _get_cached(db: AsyncSession, mpi_id: str) -> PatientCache | None:
    """Return the cached PatientCache row, or None."""
    result = await db.execute(
        select(PatientCache).where(PatientCache.mpi_id == mpi_id)
    )
    return result.scalar_one_or_none()


def _parse_iso(value: str | None) -> datetime | None:
    """Parse an ISO-8601 string to a timezone-aware datetime, or None."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        logger.debug("Could not parse datetime: %s", value)
        return None
