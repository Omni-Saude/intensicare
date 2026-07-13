"""
Serviço de criptografia/descriptografia de PHI via pgcrypto.

Usa pgp_sym_encrypt / pgp_sym_decrypt com chave por tenant
injetada via GUC ``app.encryption_key``.

Oferece:
  - encrypt_phi / decrypt_phi: round-trip string ↔ BYTEA
  - compute_mrn_bidx: blind-index HMAC para lookup sem descriptografia
  - age_derivation: idade calculada a partir da data de nascimento criptografada
  - resolve_display_name: dual-schema safe resolution de display_name
    (str passthrough ou bytes → decrypt_phi), com fallback não-fatal
"""

from __future__ import annotations

from datetime import date
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# GUC que carrega a chave de criptografia por tenant.
# Deve estar definida na sessão PostgreSQL antes de qualquer operação.
_ENCRYPTION_KEY_GUC = "app.encryption_key"

# ---------------------------------------------------------------------------
# Helpers de baixo nível (raw SQL via session)
# ---------------------------------------------------------------------------


async def _pgp_sym_encrypt_raw(db: AsyncSession, plaintext: str) -> bytes:
    """Executa pgp_sym_encrypt no banco e retorna o BYTEA resultante."""
    result = await db.execute(
        text("SELECT pgp_sym_encrypt(:plaintext, current_setting(:guc)) AS enc"),
        {"plaintext": plaintext, "guc": _ENCRYPTION_KEY_GUC},
    )
    row = result.one()
    return bytes(row.enc)


async def _pgp_sym_decrypt_raw(db: AsyncSession, ciphertext: bytes) -> str:
    """Executa pgp_sym_decrypt no banco e retorna o texto original.

    Raises:
        ValueError: se a descriptografia falhar (chave errada, dado corrompido).
    """
    from sqlalchemy.exc import DBAPIError

    try:
        result = await db.execute(
            text("SELECT pgp_sym_decrypt(:ciphertext, current_setting(:guc)) AS dec"),
            {"ciphertext": ciphertext, "guc": _ENCRYPTION_KEY_GUC},
        )
    except DBAPIError as exc:
        # pgcrypto raises "Wrong key or corrupt data" as a PostgreSQL error,
        # which SQLAlchemy wraps in DBAPIError (orig = asyncpg ExternalRoutineInvocationError).
        raise ValueError("Decryption failed — wrong key or corrupt ciphertext") from exc

    row = result.one()
    # pgp_sym_decrypt returns TEXT (or NULL if it couldn't decode).
    decrypted = row.dec
    if decrypted is None:
        raise ValueError("Decryption returned NULL — possible wrong key or corrupted ciphertext")
    return decrypted


async def _hmac_raw(db: AsyncSession, data: str) -> bytes:
    """Calcula HMAC-SHA256 do dado usando a chave GUC."""
    result = await db.execute(
        text("SELECT hmac(:data, current_setting(:guc), 'sha256') AS idx"),
        {"data": data, "guc": _ENCRYPTION_KEY_GUC},
    )
    row = result.one()
    return bytes(row.idx)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------


async def encrypt_phi(db: AsyncSession, plaintext: str) -> bytes:
    """Criptografa uma string PHI usando pgp_sym_encrypt.

    Args:
        db: Sessão assíncrona ativa.
        plaintext: Texto a ser criptografado.

    Returns:
        BYTEA criptografado.
    """
    return await _pgp_sym_encrypt_raw(db, plaintext)


async def decrypt_phi(db: AsyncSession, ciphertext: bytes) -> str:
    """Descriptografa um valor PHI usando pgp_sym_decrypt.

    Args:
        db: Sessão assíncrona ativa.
        ciphertext: BYTEA criptografado.

    Returns:
        Texto original.

    Raises:
        ValueError: Se a descriptografia falhar (chave errada, dado corrompido).
    """
    return await _pgp_sym_decrypt_raw(db, ciphertext)


async def compute_mrn_bidx(db: AsyncSession, mrn: str) -> bytes:
    """Calcula o blind-index (HMAC-SHA256) para um MRN.

    Permite busca por MRN sem descriptografar os dados armazenados.
    O mesmo MRN sempre produz o mesmo blind-index sob a mesma chave.

    Args:
        db: Sessão assíncrona ativa.
        mrn: Número de prontuário em texto plano.

    Returns:
        BYTEA com o HMAC (32 bytes).
    """
    return await _hmac_raw(db, mrn)


async def age_derivation(db: AsyncSession, birth_date_encrypted: bytes) -> int | None:
    """Calcula a idade a partir da data de nascimento criptografada.

    Descriptografa internamente, calcula a idade e NÃO armazena
    o texto plano em nenhum log ou retorno auxiliar.

    Args:
        db: Sessão assíncrona ativa.
        birth_date_encrypted: BYTEA com a data de nascimento criptografada.

    Returns:
        Idade em anos, ou None se o valor for NULL / inválido.
    """
    if birth_date_encrypted is None:
        return None

    try:
        plain = await decrypt_phi(db, birth_date_encrypted)
        birth = date.fromisoformat(plain)
    except (ValueError, TypeError) as exc:
        logger.warning("age_derivation: cannot decrypt/parse birth_date: %s", exc)
        return None

    today = date.today()
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


async def resolve_display_name(db: AsyncSession, display_name: bytes | str) -> str:
    """Resolve a PHI display-name column to plaintext, dual-schema safe.

    Several ``display_name``-carrying columns (e.g. ``patient_cache.
    display_name``) are typed ``Mapped[bytes]`` (LargeBinary) —
    post-migration-0004 databases store pgcrypto ciphertext
    (``pgp_sym_encrypt``), and the driver returns ``bytes``. A database
    that predates migration 0004 still has a plaintext VARCHAR column,
    so the driver returns ``str`` directly (see ``scripts/dev/seed_demo.
    py``'s ``_patient_cache_schema_supports_encrypted_phi``, which
    detects this same drift via ``information_schema`` at seed time, and
    its ``_upsert_patient_legacy_schema`` fallback, which is the reason a
    pre-migration dev DB can hold a plain ``str`` here). This handles
    both shapes on the read side, using ``decrypt_phi`` (pgp_sym_decrypt)
    — no new crypto.

    A naive ``isinstance(..., bytes)`` guard that falls through to a raw
    ``.decode("utf-8")`` (rather than routing through ``decrypt_phi``)
    is the exact PHI-decoding defect this helper exists to prevent:
    against a pgcrypto-encrypted column that produces mojibake/garbage
    or an outright ``UnicodeDecodeError`` — never the real name.

    Never logs the decrypted value.
    """
    if isinstance(display_name, str):
        return display_name

    try:
        return await decrypt_phi(db, display_name)
    except ValueError:
        # BYTEA holding bytes pgp_sym_decrypt rejects — wrong/unset
        # app.encryption_key GUC, or a row that was never actually
        # pgp-encrypted. Best-effort UTF-8 fallback instead of a 500;
        # the exception message (never the payload) is logged only.
        try:
            return display_name.decode("utf-8")
        except UnicodeDecodeError:
            logger.warning(
                "Could not resolve PHI display_name: decrypt_phi failed and "
                "value is not valid UTF-8 plaintext either (identifier/value "
                "omitted from log)."
            )
            return "—"
