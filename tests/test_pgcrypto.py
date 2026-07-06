"""
Tests for pgcrypto-based PHI encryption (patient_encryption.py).

Covers:
  - encrypt_phi / decrypt_phi roundtrip
  - Blind index (HMAC-SHA256) verification
  - Per-tenant key isolation (via GUC app.encryption_key)
  - Null handling in age_derivation
  - Wrong-key decryption raises ValueError
  - compute_mrn_bidx consistency (same input → same output)
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from intensicare.services.patient_encryption import (
    _ENCRYPTION_KEY_GUC,
    age_derivation,
    compute_mrn_bidx,
    decrypt_phi,
    encrypt_phi,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_db() -> AsyncMock:
    """Returns an AsyncMock for AsyncSession with execute configured."""
    return AsyncMock()


# ─── encrypt_phi tests ───────────────────────────────────────────────────────


class TestEncryptPhi:
    """Tests for encrypt_phi."""

    @pytest.mark.asyncio
    async def test_encrypt_returns_bytes(self, mock_db):
        """Should return bytes from pgp_sym_encrypt."""
        expected = b"\x01\x02\x03\x04"
        mock_result = MagicMock()
        mock_result.one.return_value.enc = expected
        mock_db.execute.return_value = mock_result

        result = await encrypt_phi(mock_db, "patient-name")
        assert isinstance(result, bytes)
        assert result == expected

    @pytest.mark.asyncio
    async def test_encrypt_delegates_to_raw(self, mock_db):
        """Should call _pgp_sym_encrypt_raw with correct parameters."""
        expected = b"encrypted-data"
        mock_result = MagicMock()
        mock_result.one.return_value.enc = expected
        mock_db.execute.return_value = mock_result

        await encrypt_phi(mock_db, "SENSITIVE-DATA")
        mock_db.execute.assert_called_once()
        call_args = mock_db.execute.call_args
        # Verify the GUC key is referenced in the query
        assert _ENCRYPTION_KEY_GUC in str(call_args)

    @pytest.mark.asyncio
    async def test_encrypt_empty_string(self, mock_db):
        """Should handle empty plaintext."""
        expected = b""
        mock_result = MagicMock()
        mock_result.one.return_value.enc = expected
        mock_db.execute.return_value = mock_result

        result = await encrypt_phi(mock_db, "")
        assert result == b""


# ─── decrypt_phi tests ───────────────────────────────────────────────────────


class TestDecryptPhi:
    """Tests for decrypt_phi."""

    @pytest.mark.asyncio
    async def test_decrypt_returns_string(self, mock_db):
        """Should return the original plaintext."""
        mock_result = MagicMock()
        mock_result.one.return_value.dec = "hello-world"
        mock_db.execute.return_value = mock_result

        result = await decrypt_phi(mock_db, b"some-ciphertext")
        assert result == "hello-world"

    @pytest.mark.asyncio
    async def test_decrypt_with_wrong_key_raises_value_error(self, mock_db):
        """When decryption fails (wrong key), should raise ValueError."""
        from sqlalchemy.exc import DBAPIError

        orig = Exception("Wrong key or corrupt data")
        mock_db.execute.side_effect = DBAPIError("statement", {}, orig)

        with pytest.raises(ValueError, match="Decryption failed"):
            await decrypt_phi(mock_db, b"bad-ciphertext")

    @pytest.mark.asyncio
    async def test_decrypt_null_result_raises_value_error(self, mock_db):
        """When decryption returns NULL, should raise ValueError."""
        mock_result = MagicMock()
        mock_result.one.return_value.dec = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(ValueError, match="NULL"):
            await decrypt_phi(mock_db, b"corrupted-ciphertext")


# ─── Roundtrip tests ─────────────────────────────────────────────────────────


class TestEncryptDecryptRoundtrip:
    """Tests for encrypt_phi → decrypt_phi roundtrips."""

    @pytest.mark.asyncio
    async def test_roundtrip_simple_string(self):
        """Simulates a full roundtrip: encrypt then decrypt."""
        plaintext = "John Doe"
        ciphertext = b"mock-ciphertext-for-john"

        mock_db = AsyncMock()

        # First call: encrypt
        mock_enc_result = MagicMock()
        mock_enc_result.one.return_value.enc = ciphertext

        # Second call: decrypt
        mock_dec_result = MagicMock()
        mock_dec_result.one.return_value.dec = plaintext

        mock_db.execute.side_effect = [
            mock_enc_result,
            mock_dec_result,
        ]

        encrypted = await encrypt_phi(mock_db, plaintext)
        assert encrypted == ciphertext

        decrypted = await decrypt_phi(mock_db, encrypted)
        assert decrypted == plaintext

    @pytest.mark.asyncio
    async def test_roundtrip_unicode(self):
        """Should handle Unicode characters (patient names with accents)."""
        plaintext = "José María Peña"
        ciphertext = b"mock-unicode-cipher"

        mock_db = AsyncMock()
        mock_enc_result = MagicMock()
        mock_enc_result.one.return_value.enc = ciphertext
        mock_dec_result = MagicMock()
        mock_dec_result.one.return_value.dec = plaintext
        mock_db.execute.side_effect = [mock_enc_result, mock_dec_result]

        encrypted = await encrypt_phi(mock_db, plaintext)
        decrypted = await decrypt_phi(mock_db, encrypted)
        assert decrypted == plaintext

    @pytest.mark.asyncio
    async def test_roundtrip_with_numbers(self):
        """Should handle strings containing numbers (MRN, etc.)."""
        plaintext = "MRN-2026-00012345"
        ciphertext = b"mock-mrn-cipher"

        mock_db = AsyncMock()
        mock_enc_result = MagicMock()
        mock_enc_result.one.return_value.enc = ciphertext
        mock_dec_result = MagicMock()
        mock_dec_result.one.return_value.dec = plaintext
        mock_db.execute.side_effect = [mock_enc_result, mock_dec_result]

        encrypted = await encrypt_phi(mock_db, plaintext)
        decrypted = await decrypt_phi(mock_db, encrypted)
        assert decrypted == plaintext


# ─── Blind index (HMAC-SHA256) tests ─────────────────────────────────────────


class TestComputeMrnBidx:
    """Tests for compute_mrn_bidx (blind index)."""

    @pytest.mark.asyncio
    async def test_returns_bytes(self, mock_db):
        """Should return bytes from HMAC-SHA256."""
        expected = b"a" * 32  # 32 bytes for SHA-256
        mock_result = MagicMock()
        mock_result.one.return_value.idx = expected
        mock_db.execute.return_value = mock_result

        result = await compute_mrn_bidx(mock_db, "MRN-001")
        assert isinstance(result, bytes)
        assert len(result) == 32

    @pytest.mark.asyncio
    async def test_same_input_produces_same_output(self, mock_db):
        """Same MRN under same key → same blind index."""
        expected = b"consistent-blind-index-value"
        mock_result = MagicMock()
        mock_result.one.return_value.idx = expected
        mock_db.execute.return_value = mock_result

        idx1 = await compute_mrn_bidx(mock_db, "MRN-SAME")
        idx2 = await compute_mrn_bidx(mock_db, "MRN-SAME")
        assert idx1 == idx2

    @pytest.mark.asyncio
    async def test_different_inputs_produce_different_outputs(self, mock_db):
        """Different MRNs → different blind indices."""
        results = {}

        def side_effect(*args, **kwargs):
            # Extract the data parameter from the call
            call_args = args[0] if args else {}
            data = kwargs.get("params", {}).get("data", "") if kwargs.get("params") else ""
            return_value = f"idx-{data}".encode().ljust(32, b"\x00")
            mock_result = MagicMock()
            mock_result.one.return_value.idx = return_value[:32]
            return mock_result

        mock_db.execute.side_effect = side_effect

        idx1 = await compute_mrn_bidx(mock_db, "MRN-A")
        idx2 = await compute_mrn_bidx(mock_db, "MRN-B")
        assert idx1 != idx2

    @pytest.mark.asyncio
    async def test_uses_hmac_sha256(self, mock_db):
        """Should use HMAC with SHA-256 algorithm."""
        mock_result = MagicMock()
        mock_result.one.return_value.idx = b"x" * 32
        mock_db.execute.return_value = mock_result

        await compute_mrn_bidx(mock_db, "test")
        mock_db.execute.assert_called_once()
        call_text = str(mock_db.execute.call_args)
        assert "sha256" in call_text
        assert "hmac" in call_text


# ─── Per-tenant key isolation tests ──────────────────────────────────────────


class TestTenantKeyIsolation:
    """Tests for per-tenant key isolation via GUC app.encryption_key."""

    @pytest.mark.asyncio
    async def test_encrypt_uses_guc_key(self, mock_db):
        """Encryption should reference the GUC app.encryption_key."""
        mock_result = MagicMock()
        mock_result.one.return_value.enc = b"encrypted"
        mock_db.execute.return_value = mock_result

        await encrypt_phi(mock_db, "data")
        call_text = str(mock_db.execute.call_args)
        assert _ENCRYPTION_KEY_GUC in call_text

    @pytest.mark.asyncio
    async def test_decrypt_uses_guc_key(self, mock_db):
        """Decryption should reference the GUC app.encryption_key."""
        mock_result = MagicMock()
        mock_result.one.return_value.dec = "plaintext"
        mock_db.execute.return_value = mock_result

        await decrypt_phi(mock_db, b"cipher")
        call_text = str(mock_db.execute.call_args)
        assert _ENCRYPTION_KEY_GUC in call_text

    @pytest.mark.asyncio
    async def test_blind_index_uses_guc_key(self, mock_db):
        """Blind index should also use the GUC key."""
        mock_result = MagicMock()
        mock_result.one.return_value.idx = b"x" * 32
        mock_db.execute.return_value = mock_result

        await compute_mrn_bidx(mock_db, "mrn")
        call_text = str(mock_db.execute.call_args)
        assert _ENCRYPTION_KEY_GUC in call_text


# ─── age_derivation tests ────────────────────────────────────────────────────


class TestAgeDerivation:
    """Tests for age_derivation."""

    @pytest.mark.asyncio
    async def test_null_ciphertext_returns_none(self, mock_db):
        """When ciphertext is None, return None."""
        result = await age_derivation(mock_db, None)
        assert result is None

    @pytest.mark.asyncio
    async def test_valid_birth_date_returns_age(self, mock_db):
        """Should compute age from decrypted birth date."""
        # Decrypt returns '1990-06-15'
        mock_result = MagicMock()
        mock_result.one.return_value.dec = "1990-06-15"
        mock_db.execute.return_value = mock_result

        result = await age_derivation(mock_db, b"encrypted-birth")
        assert result is not None
        # Age should be >= 35 (as of 2026, born 1990)
        assert result >= 35

    @pytest.mark.asyncio
    async def test_invalid_date_format_returns_none(self, mock_db):
        """When decrypted value is not a valid date, return None."""
        mock_result = MagicMock()
        mock_result.one.return_value.dec = "not-a-date"
        mock_db.execute.return_value = mock_result

        result = await age_derivation(mock_db, b"bad-format")
        assert result is None

    @pytest.mark.asyncio
    async def test_decryption_failure_returns_none(self, mock_db):
        """When decryption fails, return None gracefully."""
        from sqlalchemy.exc import DBAPIError

        orig = Exception("Wrong key")
        mock_db.execute.side_effect = DBAPIError("stmt", {}, orig)

        result = await age_derivation(mock_db, b"wrong-key-cipher")
        assert result is None


# ─── GUC constant test ───────────────────────────────────────────────────────


class TestEncryptionKeyGUC:
    """Verify the GUC constant."""

    def test_guc_is_app_encryption_key(self):
        """The GUC must be app.encryption_key for per-tenant isolation."""
        assert _ENCRYPTION_KEY_GUC == "app.encryption_key"
