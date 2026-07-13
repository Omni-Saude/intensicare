"""Testes para o serviço de dashboard (dashboard.py)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.services.dashboard import (
    NEWS2_HIGH_RISK_THRESHOLD,
    NEWS2_MEDIUM_RISK_THRESHOLD,
)


class TestNews2RiskThresholds:
    """Testa as constantes de threshold de risco NEWS2."""

    def test_high_risk_threshold(self):
        """NEWS2_HIGH_RISK_THRESHOLD deve ser 7."""
        assert NEWS2_HIGH_RISK_THRESHOLD == 7

    def test_medium_risk_threshold(self):
        """NEWS2_MEDIUM_RISK_THRESHOLD deve ser 5."""
        assert NEWS2_MEDIUM_RISK_THRESHOLD == 5

    def test_risk_categories_are_ordered(self):
        """Categorias devem estar em ordem crescente de severidade."""
        assert NEWS2_MEDIUM_RISK_THRESHOLD < NEWS2_HIGH_RISK_THRESHOLD


# ---------------------------------------------------------------------------
# Testes do get_dashboard (com mock de DB)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_dashboard_empty_patients():
    """Deve retornar resposta vazia quando não há pacientes ativos."""
    from intensicare.services.dashboard import get_dashboard

    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await get_dashboard(mock_db)
    assert response.total == 0
    assert response.patients == []
    assert response.active_alerts_total == 0


@pytest.mark.asyncio
async def test_get_dashboard_with_unit_filter():
    """Deve filtrar por unidade quando unit é fornecido."""
    from intensicare.services.dashboard import get_dashboard

    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await get_dashboard(mock_db, unit="UTI-A")
    assert response.total == 0


# ---------------------------------------------------------------------------
# Testes do get_patient_detail
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_dashboard_unit_counts_unfiltered_by_unit_param(
    db_session: AsyncSession,
) -> None:
    """BUG-F2-01: unit_counts must always list every unit with active
    patients, even when the bed grid itself is filtered by ?unit=X — the
    frontend derives its unit tabs from unit_counts (frontend-v3/app/
    page.tsx), so a filtered unit_counts made every other tab disappear
    and trapped users on whichever unit they filtered to."""
    from intensicare.models.patient_cache import PatientCache
    from intensicare.services.dashboard import get_dashboard
    from intensicare.services.patient_encryption import encrypt_phi

    tenant_id = "tenant-unit-counts-test"
    await _ensure_pgcrypto(db_session)
    await _set_dev_encryption_key(db_session, tenant_id)

    names = [
        await encrypt_phi(db_session, name)
        for name in ("Paciente UC 1", "Paciente UC 2", "Paciente UC 3")
    ]

    db_session.add_all(
        [
            PatientCache(
                mpi_id="MPI-UC-001",
                tenant_id=tenant_id,
                display_name=names[0],
                bed_id="B-UC-01",
                unit="UTI-DEMO",
                is_active=True,
            ),
            PatientCache(
                mpi_id="MPI-UC-002",
                tenant_id=tenant_id,
                display_name=names[1],
                bed_id="B-UC-02",
                unit="UTI-DEMO",
                is_active=True,
            ),
            PatientCache(
                mpi_id="MPI-UC-003",
                tenant_id=tenant_id,
                display_name=names[2],
                bed_id="B-UC-03",
                unit="UTI-B",
                is_active=True,
            ),
        ]
    )
    await db_session.flush()

    # Filtered by unit=UTI-DEMO: the bed grid narrows to that unit's 2
    # patients, but unit_counts must still report BOTH units so the
    # frontend can render a tab for UTI-B too.
    response = await get_dashboard(db_session, unit="UTI-DEMO")

    assert response.total == 2
    assert response.unit_counts == {"UTI-DEMO": 2, "UTI-B": 1}


@pytest.mark.asyncio
async def test_get_dashboard_last_vital_at_uses_latest_vital_not_synced_at(
    db_session: AsyncSession,
) -> None:
    """GK2-NEW-01: last_vital_at must track the patient's newest VitalSign
    row (the same single source of truth already used to populate `vitals`),
    not PatientCache.synced_at — vitals ingestion never touches synced_at,
    so using it froze the bed-card staleness indicator even as fresh vitals
    kept arriving. Seed synced_at far in the past and two VitalSign rows
    (older + newer); last_vital_at must equal the NEWER vital's recorded_at,
    proving both that synced_at is ignored and that the latest row wins."""
    from intensicare.models.patient_cache import PatientCache
    from intensicare.models.vital_sign import VitalSign
    from intensicare.services.dashboard import get_dashboard
    from intensicare.services.patient_encryption import encrypt_phi

    tenant_id = "tenant-last-vital-at-test"
    await _ensure_pgcrypto(db_session)
    await _set_dev_encryption_key(db_session, tenant_id)

    enc_name = await encrypt_phi(db_session, "Paciente Last Vital")

    stale_synced_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
    older_vital_at = datetime.now(timezone.utc) - timedelta(hours=1)
    newest_vital_at = datetime.now(timezone.utc) - timedelta(seconds=5)

    db_session.add(
        PatientCache(
            mpi_id="MPI-LASTVITAL-001",
            tenant_id=tenant_id,
            display_name=enc_name,
            bed_id="B-LV-01",
            unit="UTI-LASTVITAL",
            is_active=True,
            synced_at=stale_synced_at,
        )
    )
    db_session.add_all(
        [
            VitalSign(
                mpi_id="MPI-LASTVITAL-001",
                recorded_at=older_vital_at,
                ingested_at=older_vital_at,
                heart_rate=80,
                source_system="test",
            ),
            VitalSign(
                mpi_id="MPI-LASTVITAL-001",
                recorded_at=newest_vital_at,
                ingested_at=newest_vital_at,
                heart_rate=82,
                source_system="test",
            ),
        ]
    )
    await db_session.flush()

    response = await get_dashboard(db_session, unit="UTI-LASTVITAL")

    assert response.total == 1
    bed = response.patients[0]
    assert bed.last_updated == newest_vital_at.isoformat()
    assert bed.last_updated != stale_synced_at.isoformat()


@pytest.mark.asyncio
async def test_get_dashboard_last_vital_at_falls_back_to_synced_at_when_no_vitals(
    db_session: AsyncSession,
) -> None:
    """When a patient has no VitalSign rows at all, last_vital_at must fall
    back to PatientCache.synced_at rather than being left null — documented
    fallback for patients with a cache row but no ingested vitals yet."""
    from intensicare.models.patient_cache import PatientCache
    from intensicare.services.dashboard import get_dashboard
    from intensicare.services.patient_encryption import encrypt_phi

    tenant_id = "tenant-last-vital-fallback-test"
    await _ensure_pgcrypto(db_session)
    await _set_dev_encryption_key(db_session, tenant_id)

    enc_name = await encrypt_phi(db_session, "Paciente Sem Vitais")
    synced_at = datetime.now(timezone.utc) - timedelta(minutes=10)

    db_session.add(
        PatientCache(
            mpi_id="MPI-LASTVITAL-002",
            tenant_id=tenant_id,
            display_name=enc_name,
            bed_id="B-LV-02",
            unit="UTI-LASTVITAL-FALLBACK",
            is_active=True,
            synced_at=synced_at,
        )
    )
    await db_session.flush()

    response = await get_dashboard(db_session, unit="UTI-LASTVITAL-FALLBACK")

    assert response.total == 1
    bed = response.patients[0]
    assert bed.last_updated == synced_at.isoformat()


@pytest.mark.asyncio
async def test_get_patient_detail_not_found():
    """Deve retornar None quando o paciente não existe."""
    from intensicare.services.dashboard import get_patient_detail

    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await get_patient_detail(mock_db, "P-NOEXIST")
    assert response is None


# ---------------------------------------------------------------------------
# PHI dual-schema — end-to-end proof via real pgcrypto (encrypted path)
#
# Unit-level coverage of the dual-schema str/bytes fallback logic itself now
# lives in test_patient_encryption.py (TestResolveDisplayNameUnit), alongside
# resolve_display_name's other unit tests — the helper moved to
# patient_encryption.py so both dashboard.py and alerts.py can share it
# without importing from each other.
# ---------------------------------------------------------------------------

TENANT_PHI_DASH = "tenant-phi-dashboard-test"


async def _ensure_pgcrypto(db: AsyncSession) -> None:
    await db.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto SCHEMA public"))


async def _set_dev_encryption_key(db: AsyncSession, tenant_id: str) -> None:
    """Sets app.encryption_key using the same local DEK derivation dev/test
    uses when no real KMS is configured (KMSEngine._derive_dek_local) —
    the exact helper scripts/dev/seed_demo.py uses for the same reason."""
    from intensicare.services.kms_keys import KMSEngine

    dek = KMSEngine._derive_dek_local(tenant_id)
    await db.execute(
        text("SELECT set_config('app.encryption_key', :key, false)"),
        {"key": dek.plaintext.hex()},
    )


@pytest.fixture
async def phi_dashboard_session(db_session: AsyncSession) -> AsyncSession:
    """Real Postgres session with pgcrypto enabled and the dev-local DEK
    loaded into app.encryption_key for TENANT_PHI_DASH."""
    await _ensure_pgcrypto(db_session)
    await _set_dev_encryption_key(db_session, TENANT_PHI_DASH)
    return db_session


@pytest.mark.asyncio
async def test_get_dashboard_decrypts_encrypted_display_name(
    phi_dashboard_session: AsyncSession,
) -> None:
    """DRILL: patient_cache.display_name stored as real pgp_sym_encrypt
    BYTEA (post-migration-0004 schema) must come back decrypted through
    get_dashboard — not 500, not raw ciphertext bytes."""
    from intensicare.models.patient_cache import PatientCache
    from intensicare.services.dashboard import get_dashboard
    from intensicare.services.patient_encryption import encrypt_phi

    plaintext_name = "DEMO Sepse Crítica"
    enc_name = await encrypt_phi(phi_dashboard_session, plaintext_name)
    assert isinstance(enc_name, bytes)

    patient = PatientCache(
        mpi_id="MPI-PHI-DASH-001",
        tenant_id=TENANT_PHI_DASH,
        display_name=enc_name,
        bed_id="B-PHI-01",
        unit="UTI-PHI-TEST",
        is_active=True,
    )
    phi_dashboard_session.add(patient)
    await phi_dashboard_session.flush()

    response = await get_dashboard(phi_dashboard_session, unit="UTI-PHI-TEST")

    assert response.total == 1
    bed = response.patients[0]
    assert bed.mpi_id == "MPI-PHI-DASH-001"
    assert bed.display_name == plaintext_name


@pytest.mark.asyncio
async def test_get_patient_detail_decrypts_encrypted_display_name(
    phi_dashboard_session: AsyncSession,
) -> None:
    """Same DRILL as above, for get_patient_detail (PatientDetailResponse)."""
    from intensicare.models.patient_cache import PatientCache
    from intensicare.services.dashboard import get_patient_detail
    from intensicare.services.patient_encryption import encrypt_phi

    plaintext_name = "DEMO Choque Séptico"
    enc_name = await encrypt_phi(phi_dashboard_session, plaintext_name)

    patient = PatientCache(
        mpi_id="MPI-PHI-DASH-002",
        tenant_id=TENANT_PHI_DASH,
        display_name=enc_name,
        bed_id="B-PHI-02",
        unit="UTI-PHI-TEST",
        is_active=True,
        synced_at=datetime.now(timezone.utc),
    )
    phi_dashboard_session.add(patient)
    await phi_dashboard_session.flush()

    response = await get_patient_detail(phi_dashboard_session, "MPI-PHI-DASH-002")

    assert response is not None
    assert response.mpi_id == "MPI-PHI-DASH-002"
    assert response.display_name == plaintext_name
