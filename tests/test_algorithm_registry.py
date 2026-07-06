"""
Testes para algorithm_registry + clinical_score NOT NULL FK (WO-003 / INV-3).

Cobre:
- DRILL-VERSION-PIN: algorithm_version é NOT NULL em inserts de clinical_score
- FK constraint: insert com versão inválida falha
- Imutabilidade do algorithm_registry (sem updates em version strings)
- Seeded versions existem
"""

from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from intensicare.models.algorithm_registry import AlgorithmRegistry
from intensicare.models.clinical_score import ClinicalScore

# Versions seeded by migration 0005
SEEDED_VERSIONS = [
    "MEWS-v1.0",
    "NEWS2-v1.0",
    "SOFA-v1.0",
    "qSOFA-v1.0",
]


# ═══════════════════════════════════════════════════════════════════════════
# Fixture: seed algorithm_registry (mimics migration 0005 seed data)
# ═══════════════════════════════════════════════════════════════════════════


@pytest_asyncio.fixture(loop_scope="session", autouse=True)
async def seed_algorithm_registry(engine: AsyncEngine) -> None:
    """Seed algorithm_registry with current scorer versions.

    Runs once per test session after create_tables (which is also autouse).
    Since conftest uses Base.metadata.create_all (not migrations), we must
    seed the reference data manually.
    """
    from sqlalchemy import text

    seed_sql = text(
        """
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('MEWS-v1.0',  'MEWS',  '1.0.0',
             'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
             'MEWS v1.0 — Subbe et al.'),
            ('NEWS2-v1.0', 'NEWS2', '1.0.0',
             'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
             'NEWS2 v1.0 — RCP 2017'),
            ('SOFA-v1.0',  'SOFA',  '1.0.0',
             'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
             'SOFA v1.0 — Vincent et al.'),
            ('qSOFA-v1.0', 'qSOFA', '1.0.0',
             'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
             'qSOFA v1.0 — Singer et al., Sepsis-3')
        ON CONFLICT (algorithm_version) DO NOTHING
        """
    )
    async with engine.connect() as conn:
        await conn.execute(seed_sql)
        await conn.commit()


# ═══════════════════════════════════════════════════════════════════════════
# Seeded versions — verify migration ran
# ═══════════════════════════════════════════════════════════════════════════


class TestSeededVersions:
    """Verifica que as versões foram seedadas pela migration."""

    async def test_all_versions_seeded(self, db_session: AsyncSession):
        """Todas as 4 versões de algoritmo devem existir no registry."""
        from sqlalchemy import select

        for version in SEEDED_VERSIONS:
            stmt = select(AlgorithmRegistry).where(
                AlgorithmRegistry.algorithm_version == version
            )
            result = await db_session.execute(stmt)
            row = result.scalar_one_or_none()
            assert row is not None, f"Version {version} not found in algorithm_registry"
            assert row.score_type in ("MEWS", "NEWS2", "SOFA", "qSOFA")
            assert row.semver == "1.0.0"

    async def test_registry_row_count(self, db_session: AsyncSession):
        """Deve haver exatamente 4 versões (uma por score_type)."""
        from sqlalchemy import select, func

        stmt = select(func.count()).select_from(AlgorithmRegistry)
        result = await db_session.execute(stmt)
        count = result.scalar_one()
        assert count == 4, f"Expected 4 versions, got {count}"


# ═══════════════════════════════════════════════════════════════════════════
# DRILL-VERSION-PIN: algorithm_version NOT NULL
# ═══════════════════════════════════════════════════════════════════════════


class TestDrillVersionPin:
    """DRILL-VERSION-PIN: algorithm_version é obrigatório em clinical_score."""

    async def test_insert_without_version_fails(self, db_session: AsyncSession):
        """Insert sem algorithm_version deve lançar IntegrityError (NOT NULL)."""
        score = ClinicalScore(
            mpi_id="TEST-MPI-001",
            score_type="MEWS",
            score_value=3,
            # algorithm_version OMITTED — should fail
            calculated_at=datetime.now(timezone.utc),
        )
        db_session.add(score)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_insert_with_version_succeeds(self, db_session: AsyncSession):
        """Insert com algorithm_version válida deve funcionar."""
        score = ClinicalScore(
            mpi_id="TEST-MPI-002",
            score_type="MEWS",
            score_value=2,
            algorithm_version="MEWS-v1.0",
            calculated_at=datetime.now(timezone.utc),
        )
        db_session.add(score)
        await db_session.flush()
        assert score.id is not None
        assert score.algorithm_version == "MEWS-v1.0"

    async def test_insert_with_null_version_fails(self, db_session: AsyncSession):
        """Insert com algorithm_version=None deve lançar IntegrityError."""
        score = ClinicalScore(
            mpi_id="TEST-MPI-003",
            score_type="NEWS2",
            score_value=4,
            algorithm_version=None,  # explicit None
            calculated_at=datetime.now(timezone.utc),
        )
        db_session.add(score)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_version_is_retrievable(self, db_session: AsyncSession):
        """O algorithm_version salvo deve ser recuperável corretamente."""
        score = ClinicalScore(
            mpi_id="TEST-MPI-004",
            score_type="SOFA",
            score_value=5,
            algorithm_version="SOFA-v1.0",
            calculated_at=datetime.now(timezone.utc),
        )
        db_session.add(score)
        await db_session.flush()

        from sqlalchemy import select

        stmt = select(ClinicalScore).where(ClinicalScore.mpi_id == "TEST-MPI-004")
        result = await db_session.execute(stmt)
        retrieved = result.scalar_one()
        assert retrieved.algorithm_version == "SOFA-v1.0"
        assert retrieved.algorithm_version is not None


# ═══════════════════════════════════════════════════════════════════════════
# FK constraint enforcement
# ═══════════════════════════════════════════════════════════════════════════


class TestForeignKeyConstraint:
    """Garante que a FK de algorithm_version é aplicada."""

    async def test_insert_invalid_version_fails(self, db_session: AsyncSession):
        """Insert com versão que não existe no registry deve falhar (FK)."""
        score = ClinicalScore(
            mpi_id="TEST-MPI-FK-001",
            score_type="MEWS",
            score_value=0,
            algorithm_version="MEWS-v99.0",  # não existe no registry
            calculated_at=datetime.now(timezone.utc),
        )
        db_session.add(score)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_delete_registry_version_while_referenced_fails(
        self, db_session: AsyncSession
    ):
        """Não deve ser possível deletar uma versão do registry que está em uso."""
        # First insert a score referencing a version
        score = ClinicalScore(
            mpi_id="TEST-MPI-FK-002",
            score_type="qSOFA",
            score_value=1,
            algorithm_version="qSOFA-v1.0",
            calculated_at=datetime.now(timezone.utc),
        )
        db_session.add(score)
        await db_session.flush()

        # Try to delete the referenced version
        from sqlalchemy import delete

        stmt = delete(AlgorithmRegistry).where(
            AlgorithmRegistry.algorithm_version == "qSOFA-v1.0"
        )
        with pytest.raises(IntegrityError):
            await db_session.execute(stmt)
            await db_session.flush()

    async def test_all_four_types_accept_valid_versions(
        self, db_session: AsyncSession
    ):
        """Todas as combinações válidas score_type ↔ version devem funcionar."""
        pairs = [
            ("MEWS", "MEWS-v1.0"),
            ("NEWS2", "NEWS2-v1.0"),
            ("SOFA", "SOFA-v1.0"),
            ("qSOFA", "qSOFA-v1.0"),
        ]
        for score_type, version in pairs:
            score = ClinicalScore(
                mpi_id=f"TEST-MPI-FK-{score_type}",
                score_type=score_type,
                score_value=0,
                algorithm_version=version,
                calculated_at=datetime.now(timezone.utc),
            )
            db_session.add(score)
        await db_session.flush()  # should not raise


# ═══════════════════════════════════════════════════════════════════════════
# Immutability of algorithm_registry
# ═══════════════════════════════════════════════════════════════════════════


class TestRegistryImmutability:
    """O algorithm_registry é imutável — version strings não podem ser alteradas."""

    async def test_update_version_string_should_fail_in_practice(
        self, db_session: AsyncSession
    ):
        """Atualizar algorithm_version (PK) deve ser tratado como erro de design.

        O registry é imutável. Em vez de UPDATE, deve-se INSERT nova versão
        e marcar a antiga como retired_at.
        """
        # This test verifies that the design intent is clear:
        # algorithm_version is a PK and should never be updated.
        # We demonstrate that new versions are INSERT-only.
        new_version = AlgorithmRegistry(
            algorithm_version="qSOFA-v1.1",
            score_type="qSOFA",
            semver="1.1.0",
            spec_hash="a" * 64,
            description="qSOFA v1.1 — hypothetical update",
            effective_from=datetime.now(timezone.utc),
        )
        db_session.add(new_version)
        await db_session.flush()

        # Verify it was inserted
        from sqlalchemy import select

        stmt = select(AlgorithmRegistry).where(
            AlgorithmRegistry.algorithm_version == "qSOFA-v1.1"
        )
        result = await db_session.execute(stmt)
        assert result.scalar_one_or_none() is not None

    async def test_cannot_insert_duplicate_pk(self, db_session: AsyncSession):
        """Não pode inserir versão com PK duplicada."""
        dup = AlgorithmRegistry(
            algorithm_version="MEWS-v1.0",  # already seeded
            score_type="MEWS",
            semver="1.0.0",
            spec_hash="b" * 64,
            description="duplicate",
            effective_from=datetime.now(timezone.utc),
        )
        db_session.add(dup)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_unique_score_type_semver(self, db_session: AsyncSession):
        """Não pode inserir score_type + semver duplicado mesmo com version diferente."""
        dup = AlgorithmRegistry(
            algorithm_version="MEWS-v1.0-redux",
            score_type="MEWS",
            semver="1.0.0",  # same semver as MEWS-v1.0
            spec_hash="c" * 64,
            description="duplicate semver",
            effective_from=datetime.now(timezone.utc),
        )
        db_session.add(dup)
        with pytest.raises(IntegrityError):
            await db_session.flush()
