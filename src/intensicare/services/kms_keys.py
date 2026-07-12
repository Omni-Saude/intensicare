"""KMS per-tenant key hierarchy for pgcrypto DEKs (Fase 3 / WO-037).

Implementa envelope encryption:
    1. CMK raiz (Customer Master Key) no AWS KMS — nunca sai do HSM.
    2. DEK (Data Encryption Key) por tenant — gerada via KMS GenerateDataKey,
       criptografada com a CMK, armazenada na tabela ``tenant_keys``.
    3. A DEK descriptografada é injetada na sessão PostgreSQL via
       GUC ``app.encryption_key`` para uso com pgcrypto.

Fluxo:
    KMS GenerateDataKey(CMK) → (DEK_plain, DEK_cipher)
    DEK_cipher → tenant_keys.encrypted_dek (PostgreSQL)
    DEK_plain  → SET app.encryption_key = :dek (sessão PostgreSQL)
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import logging
from typing import Any, Protocol

from intensicare.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------


@dataclass
class TenantDEK:
    """Chave de criptografia de dados (DEK) de um tenant."""

    tenant_id: str
    plaintext: bytes  # DEK em texto plano (uso imediato, nunca logado)
    ciphertext: bytes  # DEK criptografada pela CMK (armazenada)
    key_id: str  # ARN da CMK usada para gerar esta DEK


class KMSClient(Protocol):
    """Interface para o cliente AWS KMS (produção: boto3)."""

    async def generate_data_key(
        self,
        KeyId: str,
        KeySpec: str,
    ) -> dict[str, Any]: ...

    async def decrypt(self, CiphertextBlob: bytes) -> dict[str, Any]: ...


class KMSKeyError(Exception):
    """Erro ao interagir com o KMS para operações de chave."""


class KMSNotConfiguredError(KMSKeyError):
    """KMS não está configurado (produção requer KMS)."""


# ---------------------------------------------------------------------------
# Engine KMS
# ---------------------------------------------------------------------------


class KMSEngine:
    """Motor de envelope encryption via AWS KMS.

    Em produção, usa boto3. Em dev/test, deriva chaves determinísticas
    via HKDF (SHA-256) usando o secret_key da aplicação como seed.
    """

    def __init__(self) -> None:
        self._kms_client: KMSClient | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Inicializa o cliente KMS (lazy)."""
        if self._initialized:
            return
        if settings.kms_cmk_arn:
            try:
                import boto3  # type: ignore[import-untyped]

                self._kms_client = boto3.client(
                    "kms",
                    region_name=settings.kms_region,
                )
                logger.info("KMS client initialized (CMK: %s)", settings.kms_cmk_arn)
            except Exception as exc:
                logger.warning(
                    "Failed to initialize KMS client: %s. Falling back to local key derivation.",
                    exc,
                )
                self._kms_client = None
        else:
            logger.info("KMS CMK not configured — using local key derivation for dev/test")
        self._initialized = True

    # ------------------------------------------------------------------
    # Derivação local (dev/test) — HKDF-SHA256 determinístico
    # ------------------------------------------------------------------

    @staticmethod
    def _derive_dek_local(tenant_id: str) -> TenantDEK:
        """Deriva uma DEK determinística usando HKDF-SHA256.

        Usa o ``secret_key`` da aplicação como IKM (input keying material)
        e ``tenant_id`` como salt + info. Produz sempre a mesma DEK para
        o mesmo tenant (útil para dev/test sem KMS real).

        ⚠️ NÃO use em produção — a chave nunca toca um HSM.
        """
        secret = settings.secret_key.get_secret_value()
        ikm = secret.encode("utf-8")
        salt = hashlib.sha256(f"intensicare-dek-salt:{tenant_id}".encode()).digest()
        info = f"intensicare-tenant-dek-v1:{tenant_id}".encode()

        # HKDF-SHA256 (RFC 5869) implementado manualmente
        # HKDF-Extract
        prk = _hmac_sha256(salt, ikm)
        # HKDF-Expand
        dek = _hkdf_expand(prk, info, settings.kms_dek_size_bytes)

        return TenantDEK(
            tenant_id=tenant_id,
            plaintext=dek,
            ciphertext=_hmac_sha256(prk, b"intensicare-dek-wrapper"),
            key_id="local-cmk-dev",
        )

    # ------------------------------------------------------------------
    # Geração via KMS (produção)
    # ------------------------------------------------------------------

    async def _generate_dek_kms(self, tenant_id: str) -> TenantDEK:
        """Gera uma DEK via AWS KMS GenerateDataKey.

        Args:
            tenant_id: ID do tenant para rastreabilidade.

        Returns:
            TenantDEK com plaintext (não logado) e ciphertext (para armazenar).

        Raises:
            KMSNotConfiguredError: se o cliente KMS não estiver disponível.
            KMSKeyError: se a chamada KMS falhar.
        """
        if self._kms_client is None:
            raise KMSNotConfiguredError("KMS client is not available — cannot generate DEK")

        try:
            response = await self._kms_client.generate_data_key(
                KeyId=settings.kms_cmk_arn,
                KeySpec="AES_256",
            )
            plaintext_b64 = response.get("Plaintext", "")
            ciphertext_blob = response.get("CiphertextBlob", b"")

            plaintext = base64.b64decode(plaintext_b64)
            return TenantDEK(
                tenant_id=tenant_id,
                plaintext=plaintext,
                ciphertext=ciphertext_blob,
                key_id=settings.kms_cmk_arn,
            )
        except Exception as exc:
            raise KMSKeyError(
                f"KMS GenerateDataKey failed for tenant {tenant_id!r}: {exc}"
            ) from exc

    async def _decrypt_dek_kms(self, ciphertext: bytes, tenant_id: str) -> bytes:
        """Descriptografa uma DEK via AWS KMS Decrypt.

        Args:
            ciphertext: DEK criptografada pela CMK (CiphertextBlob).
            tenant_id: ID do tenant (para logging).

        Returns:
            DEK em texto plano.

        Raises:
            KMSNotConfiguredError: se o cliente KMS não estiver disponível.
            KMSKeyError: se a descriptografia falhar.
        """
        if self._kms_client is None:
            raise KMSNotConfiguredError("KMS client is not available — cannot decrypt DEK")

        try:
            response = await self._kms_client.decrypt(
                CiphertextBlob=ciphertext,
            )
            plaintext_b64 = response.get("Plaintext", "")
            return base64.b64decode(plaintext_b64)
        except Exception as exc:
            raise KMSKeyError(f"KMS Decrypt failed for tenant {tenant_id!r}: {exc}") from exc

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    async def get_or_create_dek(self, tenant_id: str) -> TenantDEK:
        """Obtém ou cria a DEK de um tenant.

        Em produção: chama KMS GenerateDataKey.
        Em dev/test: deriva deterministicamente via HKDF.

        Args:
            tenant_id: ID do tenant.

        Returns:
            TenantDEK com plaintext pronto para injetar na sessão PG.

        Raises:
            KMSKeyError: se a geração falhar.
        """
        await self.initialize()

        # Tentar KMS primeiro
        if settings.kms_cmk_arn and self._kms_client is not None:
            return await self._generate_dek_kms(tenant_id)

        # Fallback local (dev/test)
        logger.debug("Deriving DEK locally for tenant %r (dev/test mode)", tenant_id)
        return self._derive_dek_local(tenant_id)

    async def unwrap_dek(self, encrypted_dek: bytes, tenant_id: str) -> bytes:
        """Descriptografa uma DEK armazenada (ciphertext) de volta para plaintext.

        Em produção: chama KMS Decrypt.
        Em dev/test: devolve a própria ``encrypted_dek`` como plaintext
                      (não há dois níveis de wrapping no modo local).

        Args:
            encrypted_dek: DEK criptografada armazenada no banco.
            tenant_id: ID do tenant.

        Returns:
            DEK em texto plano.
        """
        await self.initialize()

        if settings.kms_cmk_arn and self._kms_client is not None:
            return await self._decrypt_dek_kms(encrypted_dek, tenant_id)

        # No modo local, a "ciphertext" é o HMAC — rederivamos do zero
        logger.debug("Unwrapping DEK locally for tenant %r (dev/test mode)", tenant_id)
        dek = self._derive_dek_local(tenant_id)
        return dek.plaintext


# ---------------------------------------------------------------------------
# Singleton e API de conveniência
# ---------------------------------------------------------------------------

_kms_engine = KMSEngine()


async def get_kms_engine() -> KMSEngine:
    """Retorna o singleton do motor KMS."""
    await _kms_engine.initialize()
    return _kms_engine


async def set_session_encryption_key(
    db_session: Any,
    tenant_id: str,
) -> None:
    """Injeta a DEK do tenant na sessão PostgreSQL via GUC.

    Deve ser chamada no início de cada request autenticado, ANTES de
    qualquer operação que use pgcrypto (encrypt_phi, decrypt_phi, etc.).

    Args:
        db_session: Sessão assíncrona SQLAlchemy.
        tenant_id: ID do tenant para o qual carregar a chave.

    Raises:
        KMSKeyError: se a geração/derivação da DEK falhar.
    """
    from sqlalchemy import text

    engine = await get_kms_engine()
    dek = await engine.get_or_create_dek(tenant_id)

    # Codifica a DEK como hex para o GUC (evita problemas com null bytes)
    dek_hex = dek.plaintext.hex()
    await db_session.execute(
        text("SELECT set_config('app.encryption_key', :key, false)"),
        {"key": dek_hex},
    )
    logger.debug("Encryption key set for tenant %r (key_id=%r)", tenant_id, dek.key_id)


# ---------------------------------------------------------------------------
# Helpers criptográficos (HKDF manual — evitar dependência extra em dev)
# ---------------------------------------------------------------------------


def _hmac_sha256(key: bytes, msg: bytes) -> bytes:
    """HMAC-SHA256 usando hashlib."""
    import hmac as _hmac_mod

    return _hmac_mod.new(key, msg, hashlib.sha256).digest()


def _hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    """HKDF-Expand (RFC 5869, seção 2.3)."""
    if length > 255 * 32:  # hash_len = 32 (SHA-256)
        raise ValueError("Cannot expand to more than 255 * HashLen bytes")

    n = (length + 31) // 32  # ceil(length / hash_len)
    t = b""
    okm = b""
    for i in range(1, n + 1):
        t = _hmac_sha256(prk, t + info + bytes([i]))
        okm += t
    return okm[:length]
