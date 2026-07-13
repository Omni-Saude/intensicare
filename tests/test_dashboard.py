"""Testes para o serviço de dashboard (dashboard.py)."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.services.dashboard import (
    NEWS2_HIGH_RISK_THRESHOLD,
    NEWS2_MEDIUM_RISK_THRESHOLD,
    _resolve_patient_display_name,
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
# _resolve_patient_display_name — dual-schema PHI decrypt (unit-level)
# ---------------------------------------------------------------------------


class TestResolvePatientDisplayNameUnit:
    """Unit coverage of the dual-schema fallback logic in isolation
    (mocked db/decrypt_phi — no real Postgres needed for these branches)."""

    @pytest.mark.asyncio
    async def test_legacy_plaintext_str_passthrough(self):
        """Schema pre-migration-0004: driver returns str — used as-is,
        decrypt_phi must NOT be called."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(side_effect=AssertionError("must not query DB for str input"))

        result = await _resolve_patient_display_name(mock_db, "DEMO Sepse Crítica")
        assert result == "DEMO Sepse Crítica"

    @pytest.mark.asyncio
    async def test_encrypted_bytes_calls_decrypt_phi(self, monkeypatch):
        """Schema post-migration-0004: bytes go through decrypt_phi."""
        import intensicare.services.dashboard as dashboard_module

        async def _fake_decrypt(db, ciphertext):
            assert ciphertext == b"fake-ciphertext"
            return "Maria Oliveira"

        monkeypatch.setattr(dashboard_module, "decrypt_phi", _fake_decrypt)

        mock_db = MagicMock()
        result = await _resolve_patient_display_name(mock_db, b"fake-ciphertext")
        assert result == "Maria Oliveira"

    @pytest.mark.asyncio
    async def test_decrypt_failure_falls_back_to_utf8_decode(self, monkeypatch):
        """decrypt_phi raising ValueError (wrong key/corrupt/unset GUC) falls
        back to a best-effort UTF-8 decode instead of raising/500ing."""
        import intensicare.services.dashboard as dashboard_module

        async def _failing_decrypt(db, ciphertext):
            raise ValueError("Decryption failed — wrong key or corrupt ciphertext")

        monkeypatch.setattr(dashboard_module, "decrypt_phi", _failing_decrypt)

        mock_db = MagicMock()
        result = await _resolve_patient_display_name(mock_db, "plain-ascii-bytes".encode())
        assert result == "plain-ascii-bytes"

    @pytest.mark.asyncio
    async def test_decrypt_failure_and_undecodable_bytes_returns_placeholder(self, monkeypatch):
        """Neither decrypt_phi nor a raw UTF-8 decode works — never 500s,
        returns a safe placeholder instead."""
        import intensicare.services.dashboard as dashboard_module

        async def _failing_decrypt(db, ciphertext):
            raise ValueError("Decryption failed — wrong key or corrupt ciphertext")

        monkeypatch.setattr(dashboard_module, "decrypt_phi", _failing_decrypt)

        mock_db = MagicMock()
        result = await _resolve_patient_display_name(mock_db, b"\xff\xfe\x00\x01not-utf8")
        assert result == "—"


# ---------------------------------------------------------------------------
# PHI dual-schema — end-to-end proof via real pgcrypto (encrypted path)
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
