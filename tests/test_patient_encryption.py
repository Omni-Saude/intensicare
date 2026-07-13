"""
Testes para criptografia PHI via pgcrypto (INV-4 / WO-002).

Cobre:
  - DRILL-CROSS-TENANT-DECRYPT: chave de tenant errada não descriptografa
  - DRILL-PHI-EGRESS-SCRUB: dados criptografados não contêm texto plano
  - Round-trip encrypt/decrypt
  - Blind-index (MRN lookup sem descriptografia)
  - age_derivation (idade a partir de birth_date criptografado)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.services.patient_encryption import (
    age_derivation,
    compute_mrn_bidx,
    decrypt_phi,
    encrypt_phi,
    resolve_display_name,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TENANT_A_KEY = "tenant-a-secret-key-32bytes!!"  # 32 bytes
TENANT_B_KEY = "tenant-b-secret-key-32bytes!!"  # 32 bytes


async def _set_encryption_key(db: AsyncSession, key: str) -> None:
    """Define a GUC app.encryption_key para a sessão corrente.

    PostgreSQL SET does NOT support bind parameters — the value must
    be a literal. Keys are trusted test constants; safe to interpolate.
    """
    # SET only accepts literals, not $1 placeholders.
    sanitized = key.replace("'", "''")  # escape single quotes defensively
    await db.execute(text(f"SET app.encryption_key = '{sanitized}'"))


async def _ensure_pgcrypto(db: AsyncSession) -> None:
    """Garante que a extensão pgcrypto está disponível."""
    await db.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto SCHEMA public"))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def pgcrypto_session(db_session: AsyncSession) -> AsyncSession:
    """Sessão com pgcrypto habilitada e chave de tenant A definida."""
    await _ensure_pgcrypto(db_session)
    await _set_encryption_key(db_session, TENANT_A_KEY)
    return db_session


# ---------------------------------------------------------------------------
# DRILL: Round-trip encrypt/decrypt
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_encrypt_decrypt_round_trip(pgcrypto_session: AsyncSession) -> None:
    """DRILL: encrypt_phi seguido de decrypt_phi retorna o texto original."""
    plaintext = "Maria Silva Oliveira"

    ciphertext = await encrypt_phi(pgcrypto_session, plaintext)
    assert isinstance(ciphertext, bytes)
    assert len(ciphertext) > 0

    decrypted = await decrypt_phi(pgcrypto_session, ciphertext)
    assert decrypted == plaintext


@pytest.mark.asyncio
async def test_encrypt_produces_different_output_for_different_inputs(
    pgcrypto_session: AsyncSession,
) -> None:
    """Entradas diferentes produzem ciphertexts diferentes."""
    ct1 = await encrypt_phi(pgcrypto_session, "Paciente A")
    ct2 = await encrypt_phi(pgcrypto_session, "Paciente B")
    assert ct1 != ct2


@pytest.mark.asyncio
async def test_encrypt_null_handling(pgcrypto_session: AsyncSession) -> None:
    """Encrypt/decrypt de strings vazias funciona (não quebra)."""
    ct = await encrypt_phi(pgcrypto_session, "")
    decrypted = await decrypt_phi(pgcrypto_session, ct)
    assert decrypted == ""


# ---------------------------------------------------------------------------
# DRILL-CROSS-TENANT-DECRYPT: wrong tenant key cannot decrypt
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cross_tenant_decrypt_fails(
    pgcrypto_session: AsyncSession,
) -> None:
    """DRILL-CROSS-TENANT-DECRYPT: dado criptografado com chave A
    NÃO pode ser descriptografado com chave B."""
    plaintext = "Dado sensível do tenant A"

    # Criptografa com chave A (já definida no fixture)
    ciphertext = await encrypt_phi(pgcrypto_session, plaintext)

    # Troca para chave B
    await _set_encryption_key(pgcrypto_session, TENANT_B_KEY)

    # Tentativa de descriptografar com chave B deve falhar
    with pytest.raises(ValueError, match=r"wrong key|corrupted|NULL"):
        await decrypt_phi(pgcrypto_session, ciphertext)

    # A transação PostgreSQL fica em estado abortado após erro de decrypt.
    # Precisamos de rollback antes de continuar.
    await pgcrypto_session.rollback()

    # Restaura chave A para não contaminar outros testes
    await _set_encryption_key(pgcrypto_session, TENANT_A_KEY)


@pytest.mark.asyncio
async def test_cross_tenant_own_key_works(
    pgcrypto_session: AsyncSession,
) -> None:
    """Cada tenant consegue ler seus próprios dados."""
    # Tenant A
    ct_a = await encrypt_phi(pgcrypto_session, "Dado A")
    assert await decrypt_phi(pgcrypto_session, ct_a) == "Dado A"

    # Tenant B
    await _set_encryption_key(pgcrypto_session, TENANT_B_KEY)
    ct_b = await encrypt_phi(pgcrypto_session, "Dado B")
    assert await decrypt_phi(pgcrypto_session, ct_b) == "Dado B"

    # Tenant A não consegue ler dados de B
    await _set_encryption_key(pgcrypto_session, TENANT_A_KEY)
    with pytest.raises(ValueError, match=r"wrong key|corrupted|NULL"):
        await decrypt_phi(pgcrypto_session, ct_b)
    await pgcrypto_session.rollback()

    # Tenant B não consegue ler dados de A
    await _set_encryption_key(pgcrypto_session, TENANT_B_KEY)
    with pytest.raises(ValueError, match=r"wrong key|corrupted|NULL"):
        await decrypt_phi(pgcrypto_session, ct_a)
    await pgcrypto_session.rollback()

    # Restaura chave A
    await _set_encryption_key(pgcrypto_session, TENANT_A_KEY)


# ---------------------------------------------------------------------------
# DRILL-PHI-EGRESS-SCRUB: no plaintext in encrypted output
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_encrypted_data_does_not_contain_plaintext(
    pgcrypto_session: AsyncSession,
) -> None:
    """DRILL-PHI-EGRESS-SCRUB: o ciphertext NÃO contém o texto plano
    legível como substring. Simula verificação de pg_dump."""
    plaintext = "1985-03-22"  # data de nascimento

    ciphertext = await encrypt_phi(pgcrypto_session, plaintext)

    # O ciphertext é binário. Convertendo para representação hex
    # ou tentando decodificar como UTF-8 não deve revelar o plaintext.
    hex_repr = ciphertext.hex()
    assert plaintext.encode() not in ciphertext
    assert plaintext not in hex_repr

    # Tenta interpretar como string — mesmo que funcione, não deve conter plaintext
    try:
        as_str = ciphertext.decode("utf-8", errors="replace")
        assert plaintext not in as_str
    except UnicodeDecodeError:
        pass  # binário puro, ainda melhor


@pytest.mark.asyncio
async def test_encrypted_birth_date_no_plaintext(
    pgcrypto_session: AsyncSession,
) -> None:
    """DRILL-PHI-EGRESS-SCRUB: data de nascimento não aparece em plaintext."""
    birth_date_str = "2000-01-15"

    ciphertext = await encrypt_phi(pgcrypto_session, birth_date_str)

    # Nem a data original nem fragmentos devem aparecer
    assert b"2000" not in ciphertext
    assert b"01" not in ciphertext  # pode colidir com bytes aleatórios, mas é improvável
    assert b"2000-01-15" not in ciphertext


@pytest.mark.asyncio
async def test_multiple_phi_fields_all_encrypted(
    pgcrypto_session: AsyncSession,
) -> None:
    """Todos os campos PHI produzem ciphertexts distintos e sem plaintext."""
    fields = {
        "display_name": "João Pedro dos Santos",
        "mrn": "MRN-987654321",
        "birth_date": "1970-06-30",
        "cpf": "123.456.789-00",
        "cns": "8980011 0000 0001",
    }

    ciphertexts: dict[str, bytes] = {}
    for field_name, value in fields.items():
        ct = await encrypt_phi(pgcrypto_session, value)
        ciphertexts[field_name] = ct
        # Nenhum ciphertext contém o plaintext
        assert value.encode() not in ct, f"{field_name}: plaintext found in ciphertext"

    # Todos os ciphertexts são distintos entre si
    ct_values = list(ciphertexts.values())
    for i in range(len(ct_values)):
        for j in range(i + 1, len(ct_values)):
            assert ct_values[i] != ct_values[j], (
                f"Ciphertexts for different fields should differ: {i} vs {j}"
            )


# ---------------------------------------------------------------------------
# Blind-index (mrn_bidx)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mrn_bidx_same_input_same_output(
    pgcrypto_session: AsyncSession,
) -> None:
    """O mesmo MRN produz sempre o mesmo blind-index."""
    mrn = "MRN-12345"
    bidx1 = await compute_mrn_bidx(pgcrypto_session, mrn)
    bidx2 = await compute_mrn_bidx(pgcrypto_session, mrn)
    assert bidx1 == bidx2
    assert len(bidx1) == 32  # SHA256 = 32 bytes


@pytest.mark.asyncio
async def test_mrn_bidx_different_inputs_different_outputs(
    pgcrypto_session: AsyncSession,
) -> None:
    """MRNs diferentes produzem blind-indexes diferentes."""
    bidx1 = await compute_mrn_bidx(pgcrypto_session, "MRN-AAAA")
    bidx2 = await compute_mrn_bidx(pgcrypto_session, "MRN-BBBB")
    assert bidx1 != bidx2


@pytest.mark.asyncio
async def test_mrn_bidx_cross_tenant_different(
    pgcrypto_session: AsyncSession,
) -> None:
    """Blind-index com chaves diferentes produz valores diferentes
    para o mesmo MRN (isolamento cross-tenant)."""
    mrn = "MRN-SHARED"

    bidx_a = await compute_mrn_bidx(pgcrypto_session, mrn)

    await _set_encryption_key(pgcrypto_session, TENANT_B_KEY)
    bidx_b = await compute_mrn_bidx(pgcrypto_session, mrn)

    # Blind indexes devem diferir (chaves diferentes)
    assert bidx_a != bidx_b, (
        "Cross-tenant blind-index isolation failed: same MRN produced same bidx"
    )

    await _set_encryption_key(pgcrypto_session, TENANT_A_KEY)


@pytest.mark.asyncio
async def test_mrn_bidx_does_not_reveal_plaintext(
    pgcrypto_session: AsyncSession,
) -> None:
    """Blind-index não revela o MRN original em plaintext."""
    mrn = "MRN-SECRET-999"
    bidx = await compute_mrn_bidx(pgcrypto_session, mrn)
    assert mrn.encode() not in bidx
    # O blind-index é um hash, não deve ser possível recuperar o original


# ---------------------------------------------------------------------------
# age_derivation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_age_derivation_known_birth_date(
    pgcrypto_session: AsyncSession,
) -> None:
    """age_derivation calcula idade correta a partir de data criptografada."""
    from datetime import date as date_type

    birth_str = "1990-06-15"
    encrypted = await encrypt_phi(pgcrypto_session, birth_str)

    age = await age_derivation(pgcrypto_session, encrypted)

    expected_age = (
        date_type.today().year - 1990 - ((date_type.today().month, date_type.today().day) < (6, 15))
    )
    assert age == expected_age, f"Expected age {expected_age}, got {age}"


@pytest.mark.asyncio
async def test_age_derivation_none_input(pgcrypto_session: AsyncSession) -> None:
    """age_derivation com input None retorna None."""
    # Precisamos de bytes None-like. Usamos None diretamente.
    result = await age_derivation(pgcrypto_session, None)  # type: ignore[arg-type]
    assert result is None


@pytest.mark.asyncio
async def test_age_derivation_invalid_ciphertext(
    pgcrypto_session: AsyncSession,
) -> None:
    """age_derivation com ciphertext inválido retorna None (não quebra)."""
    garbage = b"\x00\x01\x02\x03invalid-ciphertext"
    result = await age_derivation(pgcrypto_session, garbage)
    assert result is None


@pytest.mark.asyncio
async def test_age_derivation_cross_tenant(
    pgcrypto_session: AsyncSession,
) -> None:
    """age_derivation com chave errada retorna None (não vaza idade)."""
    birth_str = "1980-01-01"
    encrypted = await encrypt_phi(pgcrypto_session, birth_str)

    # Troca para chave errada
    await _set_encryption_key(pgcrypto_session, TENANT_B_KEY)
    result = await age_derivation(pgcrypto_session, encrypted)
    # Deve retornar None (não consegue descriptografar)
    assert result is None, "Cross-tenant age derivation should return None, not leak data"

    await pgcrypto_session.rollback()
    await _set_encryption_key(pgcrypto_session, TENANT_A_KEY)


# ---------------------------------------------------------------------------
# Integração: escrever e ler PatientCache real com PHI criptografado
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_patient_cache_write_encrypted_read_decrypted(
    pgcrypto_session: AsyncSession,
) -> None:
    """Grava um registro no patient_cache com PHI criptografado e
    verifica que a leitura descriptografa corretamente."""
    from intensicare.models.patient_cache import PatientCache

    # -- Setup: criptografar campos --
    enc_name = await encrypt_phi(pgcrypto_session, "Ana Beatriz Costa")
    enc_mrn = await encrypt_phi(pgcrypto_session, "MRN-555666")
    enc_birth = await encrypt_phi(pgcrypto_session, "1995-08-20")
    enc_cpf = await encrypt_phi(pgcrypto_session, "111.222.333-44")
    enc_cns = await encrypt_phi(pgcrypto_session, "123456789012345")
    bidx = await compute_mrn_bidx(pgcrypto_session, "MRN-555666")

    patient = PatientCache(
        mpi_id="MPI-ENC-TEST-001",
        tenant_id="tenant-a",
        display_name=enc_name,
        mrn=enc_mrn,
        birth_date=enc_birth,
        cpf=enc_cpf,
        cns=enc_cns,
        mrn_bidx=bidx,
        gender="F",
        is_active=True,
    )
    pgcrypto_session.add(patient)
    await pgcrypto_session.flush()

    # -- Leitura: descriptografar --
    from sqlalchemy import select

    stmt = select(PatientCache).where(PatientCache.mpi_id == "MPI-ENC-TEST-001")
    result = await pgcrypto_session.execute(stmt)
    loaded = result.scalar_one()

    # Descriptografa e verifica
    assert loaded.display_name is not None
    assert await decrypt_phi(pgcrypto_session, loaded.display_name) == "Ana Beatriz Costa"
    assert loaded.mrn is not None
    assert await decrypt_phi(pgcrypto_session, loaded.mrn) == "MRN-555666"
    assert loaded.birth_date is not None
    assert await decrypt_phi(pgcrypto_session, loaded.birth_date) == "1995-08-20"
    assert loaded.cpf is not None
    assert await decrypt_phi(pgcrypto_session, loaded.cpf) == "111.222.333-44"
    assert loaded.cns is not None
    assert await decrypt_phi(pgcrypto_session, loaded.cns) == "123456789012345"

    # Blind-index lookup
    stmt_bidx = select(PatientCache).where(PatientCache.mrn_bidx == bidx)
    result_bidx = await pgcrypto_session.execute(stmt_bidx)
    found = result_bidx.scalar_one()
    assert found.mpi_id == "MPI-ENC-TEST-001"


@pytest.mark.asyncio
async def test_patient_cache_no_plaintext_phi_in_db(
    pgcrypto_session: AsyncSession,
) -> None:
    """DRILL-PHI-EGRESS-SCRUB: verifica que as colunas no banco
    NÃO contêm os valores em texto plano (simula pg_dump)."""
    from intensicare.models.patient_cache import PatientCache

    enc_name = await encrypt_phi(pgcrypto_session, "Carlos Drummond")
    enc_cpf = await encrypt_phi(pgcrypto_session, "999.888.777-66")

    patient = PatientCache(
        mpi_id="MPI-EGRESS-TEST-001",
        tenant_id="tenant-a",
        display_name=enc_name,
        cpf=enc_cpf,
        is_active=True,
    )
    pgcrypto_session.add(patient)
    await pgcrypto_session.flush()

    # Agora fazemos uma query raw para obter os bytes EXATOS do banco
    row = await pgcrypto_session.execute(
        text("SELECT display_name, cpf FROM patient_cache WHERE mpi_id = :mpi"),
        {"mpi": "MPI-EGRESS-TEST-001"},
    )
    db_display_name, db_cpf = row.one()

    # Os bytes no banco NÃO devem conter os plaintexts
    plaintext_name = b"Carlos Drummond"
    plaintext_cpf = b"999.888.777-66"

    assert plaintext_name not in bytes(db_display_name), (
        "DRILL-PHI-EGRESS-SCRUB FAIL: display_name plaintext found in DB column"
    )
    assert plaintext_cpf not in bytes(db_cpf), (
        "DRILL-PHI-EGRESS-SCRUB FAIL: cpf plaintext found in DB column"
    )


# ---------------------------------------------------------------------------
# resolve_display_name — dual-schema PHI decrypt (unit-level)
#
# Shared by dashboard.py and alerts.py (both build a patient display name
# from a column that is plaintext str pre-migration-0004 or pgcrypto BYTEA
# post-migration-0004). Moved here from test_dashboard.py when the helper
# itself moved out of dashboard.py to avoid alerts.py importing from the
# dashboard service module.
# ---------------------------------------------------------------------------


class TestResolveDisplayNameUnit:
    """Unit coverage of the dual-schema fallback logic in isolation
    (mocked db/decrypt_phi — no real Postgres needed for these branches)."""

    @pytest.mark.asyncio
    async def test_legacy_plaintext_str_passthrough(self):
        """Schema pre-migration-0004: driver returns str — used as-is,
        decrypt_phi must NOT be called."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(side_effect=AssertionError("must not query DB for str input"))

        result = await resolve_display_name(mock_db, "DEMO Sepse Crítica")
        assert result == "DEMO Sepse Crítica"

    @pytest.mark.asyncio
    async def test_encrypted_bytes_calls_decrypt_phi(self, monkeypatch):
        """Schema post-migration-0004: bytes go through decrypt_phi."""
        import intensicare.services.patient_encryption as patient_encryption_module

        async def _fake_decrypt(db, ciphertext):
            assert ciphertext == b"fake-ciphertext"
            return "Maria Oliveira"

        monkeypatch.setattr(patient_encryption_module, "decrypt_phi", _fake_decrypt)

        mock_db = MagicMock()
        result = await resolve_display_name(mock_db, b"fake-ciphertext")
        assert result == "Maria Oliveira"

    @pytest.mark.asyncio
    async def test_decrypt_failure_falls_back_to_utf8_decode(self, monkeypatch):
        """decrypt_phi raising ValueError (wrong key/corrupt/unset GUC) falls
        back to a best-effort UTF-8 decode instead of raising/500ing."""
        import intensicare.services.patient_encryption as patient_encryption_module

        async def _failing_decrypt(db, ciphertext):
            raise ValueError("Decryption failed — wrong key or corrupt ciphertext")

        monkeypatch.setattr(patient_encryption_module, "decrypt_phi", _failing_decrypt)

        mock_db = MagicMock()
        result = await resolve_display_name(mock_db, "plain-ascii-bytes".encode())
        assert result == "plain-ascii-bytes"

    @pytest.mark.asyncio
    async def test_decrypt_failure_and_undecodable_bytes_returns_placeholder(self, monkeypatch):
        """Neither decrypt_phi nor a raw UTF-8 decode works — never 500s,
        returns a safe placeholder instead."""
        import intensicare.services.patient_encryption as patient_encryption_module

        async def _failing_decrypt(db, ciphertext):
            raise ValueError("Decryption failed — wrong key or corrupt ciphertext")

        monkeypatch.setattr(patient_encryption_module, "decrypt_phi", _failing_decrypt)

        mock_db = MagicMock()
        result = await resolve_display_name(mock_db, b"\xff\xfe\x00\x01not-utf8")
        assert result == "—"
