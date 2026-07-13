"""Testes para o módulo KMS keys — envelope encryption via AWS KMS."""

from __future__ import annotations

import pytest

from intensicare.services.kms_keys import (
    KMSEngine,
    KMSKeyError,
    KMSNotConfiguredError,
    TenantDEK,
    _hkdf_expand,
    _hmac_sha256,
)

# ---------------------------------------------------------------------------
# TenantDEK
# ---------------------------------------------------------------------------


class TestTenantDEK:
    def test_create_dek(self):
        dek = TenantDEK(
            tenant_id="tenant-1",
            plaintext=b"secret-key-32-bytes-xxxxxxxx",
            ciphertext=b"encrypted-key-blob",
            key_id="arn:aws:kms:us-east-1:123:key/abc",
        )
        assert dek.tenant_id == "tenant-1"
        assert dek.plaintext == b"secret-key-32-bytes-xxxxxxxx"
        assert dek.ciphertext == b"encrypted-key-blob"
        assert "arn:aws" in dek.key_id


# ---------------------------------------------------------------------------
# _hmac_sha256 e _hkdf_expand
# ---------------------------------------------------------------------------


class TestCryptoHelpers:
    def test_hmac_sha256_deterministic(self):
        """HMAC-SHA256 deve ser determinístico."""
        key = b"test-key"
        msg = b"test-message"
        h1 = _hmac_sha256(key, msg)
        h2 = _hmac_sha256(key, msg)
        assert h1 == h2
        assert len(h1) == 32  # SHA-256 digest = 32 bytes

    def test_hmac_sha256_different_inputs(self):
        """Entradas diferentes devem produzir HMACs diferentes."""
        h1 = _hmac_sha256(b"key", b"msg1")
        h2 = _hmac_sha256(b"key", b"msg2")
        assert h1 != h2

    def test_hkdf_expand_output_length(self):
        """HKDF-Expand deve retornar o comprimento solicitado."""
        prk = b"x" * 32
        info = b"test-info"
        result = _hkdf_expand(prk, info, 16)
        assert len(result) == 16

    def test_hkdf_expand_deterministic(self):
        """HKDF-Expand deve ser determinístico."""
        prk = b"x" * 32
        info = b"test"
        r1 = _hkdf_expand(prk, info, 32)
        r2 = _hkdf_expand(prk, info, 32)
        assert r1 == r2

    def test_hkdf_expand_too_large_raises(self):
        """HKDF-Expand não deve aceitar comprimentos > 255 * 32."""
        prk = b"x" * 32
        with pytest.raises(ValueError):
            _hkdf_expand(prk, b"info", 255 * 32 + 1)


# ---------------------------------------------------------------------------
# KMSEngine — local derivation (dev/test)
# ---------------------------------------------------------------------------


class TestKMSEngineLocal:
    """Testa o modo de derivação local (sem KMS real)."""

    @pytest.mark.asyncio
    async def test_derive_dek_local_deterministic(self):
        """A mesma tenant_id deve produzir a mesma DEK."""
        engine = KMSEngine()
        dek1 = engine._derive_dek_local("tenant-1")
        dek2 = engine._derive_dek_local("tenant-1")
        assert dek1.plaintext == dek2.plaintext
        assert dek1.ciphertext == dek2.ciphertext
        assert dek1.tenant_id == "tenant-1"

    @pytest.mark.asyncio
    async def test_derive_dek_local_different_tenants(self):
        """Tenants diferentes devem ter DEKs diferentes."""
        engine = KMSEngine()
        dek1 = engine._derive_dek_local("tenant-A")
        dek2 = engine._derive_dek_local("tenant-B")
        assert dek1.plaintext != dek2.plaintext

    @pytest.mark.asyncio
    async def test_derive_dek_local_key_id(self):
        """Modo local deve usar 'local-cmk-dev' como key_id."""
        engine = KMSEngine()
        dek = engine._derive_dek_local("tenant-1")
        assert dek.key_id == "local-cmk-dev"

    @pytest.mark.asyncio
    async def test_derive_dek_local_dek_size(self):
        """DEK local deve ter o tamanho configurado (32 bytes = AES-256)."""
        from intensicare.config import settings

        engine = KMSEngine()
        dek = engine._derive_dek_local("tenant-1")
        assert len(dek.plaintext) == settings.kms_dek_size_bytes


# ---------------------------------------------------------------------------
# KMSEngine — get_or_create_dek (modo local)
# ---------------------------------------------------------------------------


class TestKMSEngineGetOrCreateDek:
    """Testa get_or_create_dek no modo local (sem KMS configurado)."""

    @pytest.mark.asyncio
    async def test_get_or_create_dek_local(self):
        """Deve derivar DEK local quando KMS não está configurado."""
        from intensicare.config import settings

        # Garantir que KMS não está configurado
        assert not settings.kms_cmk_arn or settings.kms_cmk_arn == ""

        engine = KMSEngine()
        await engine.initialize()
        dek = await engine.get_or_create_dek("tenant-1")
        assert isinstance(dek, TenantDEK)
        assert dek.tenant_id == "tenant-1"
        assert len(dek.plaintext) > 0


# ---------------------------------------------------------------------------
# KMSEngine — unwrap_dek (modo local)
# ---------------------------------------------------------------------------


class TestKMSEngineUnwrapDek:
    """Testa unwrap_dek no modo local."""

    @pytest.mark.asyncio
    async def test_unwrap_dek_local(self):
        """No modo local, unwrap deve retornar o plaintext correto."""
        engine = KMSEngine()
        await engine.initialize()
        original = await engine.get_or_create_dek("tenant-1")
        unwrapped = await engine.unwrap_dek(original.ciphertext, "tenant-1")
        assert unwrapped == original.plaintext


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class TestExceptions:
    def test_kms_key_error_is_exception(self):
        with pytest.raises(KMSKeyError):
            raise KMSKeyError("test error")

    def test_kms_not_configured_error(self):
        err = KMSNotConfiguredError("no KMS")
        assert isinstance(err, KMSKeyError)
        assert "no KMS" in str(err)
