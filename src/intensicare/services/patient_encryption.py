"""
Serviço de criptografia/descriptografia de PHI via pgcrypto.

Usa pgp_sym_encrypt / pgp_sym_decrypt com chave por tenant
injetada via GUC ``app.encryption_key``.

Oferece:
  - encrypt_phi / decrypt_phi: round-trip string ↔ BYTEA
  - compute_mrn_bidx: blind-index HMAC para lookup sem descriptografia
  - age_derivation: idade calculada a partir da data de nascimento criptografada
"""

from __future__ import annotations

import logging
from datetime import date

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
        text(
            "SELECT pgp_sym_encrypt(:plaintext, current_setting(:guc)) AS enc"
        ),
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
            text(
                "SELECT pgp_sym_decrypt(:ciphertext, current_setting(:guc)) AS dec"
            ),
            {"ciphertext": ciphertext, "guc": _ENCRYPTION_KEY_GUC},
        )
    except DBAPIError as exc:
        # pgcrypto raises "Wrong key or corrupt data" as a PostgreSQL error,
        # which SQLAlchemy wraps in DBAPIError (orig = asyncpg ExternalRoutineInvocationError).
        raise ValueError(
            "Decryption failed — wrong key or corrupt ciphertext"
        ) from exc

    row = result.one()
    # pgp_sym_decrypt returns TEXT (or NULL if it couldn't decode).
    decrypted = row.dec
    if decrypted is None:
        raise ValueError(
            "Decryption returned NULL — possible wrong key or corrupted ciphertext"
        )
    return decrypted


async def _hmac_raw(db: AsyncSession, data: str) -> bytes:
    """Calcula HMAC-SHA256 do dado usando a chave GUC."""
    result = await db.execute(
        text(
            "SELECT hmac(:data, current_setting(:guc), 'sha256') AS idx"
        ),
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
    age = (
        today.year
        - birth.year
        - ((today.month, today.day) < (birth.month, birth.day))
    )
    return age
