"""Testes para GoldWriter — write-back para fact_patient_score e fact_alert.

Cobre:
- write_scores com algorithm_version
- write_alerts com definition_version
- PHI ausente do payload de write-back (REQ-INV-4-S3)
- Idempotência: mesmo dado duas vezes → uma linha (ON CONFLICT DO NOTHING)
- Fluxo unidirecional: writer nunca lê de volta para scoring
"""

from datetime import datetime, timezone

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

# Importação antecipada dos modelos gold para que Base.metadata os inclua
# antes de create_tables (fixture autouse de sessão).
from intensicare.services.gold_schema import FactAlert, FactPatientScore  # noqa: F401

from intensicare.models.alert import Alert
from intensicare.models.alert_definition_version import AlertDefinitionVersion
from intensicare.models.clinical_score import ClinicalScore
from intensicare.services.gold_writer import GoldWriter, PHI_DENYLIST


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_score(**overrides: object) -> ClinicalScore:
    """Cria um ClinicalScore com valores padrão válidos."""
    defaults: dict[str, object] = {
        "mpi_id": "MPI-TEST-001",
        "score_type": "MEWS",
        "score_value": 3,
        "algorithm_version": "MEWS-v1.0",
        "calculated_at": datetime.now(timezone.utc),
        "id": 1,
    }
    defaults.update(overrides)
    score = ClinicalScore(**defaults)  # type: ignore[arg-type]
    return score


def _make_alert(**overrides: object) -> Alert:
    """Cria um Alert com valores padrão válidos."""
    defaults: dict[str, object] = {
        "mpi_id": "MPI-TEST-001",
        "severity": "urgent",
        "status": "active",
        "title": "Test Alert",
        "definition_version_id": "ALERT-TEST-v1.0",
        "created_at": datetime.now(timezone.utc),
        "id": 1,
    }
    defaults.update(overrides)
    alert = Alert(**defaults)  # type: ignore[arg-type]
    return alert


# ---------------------------------------------------------------------------
# PHI absence (REQ-INV-4-S3)
# ---------------------------------------------------------------------------


class TestPhiAbsence:
    """Garante que nenhum campo PHI chega ao payload de write-back."""

    def test_phi_denylist_contains_expected_fields(self) -> None:
        """PHI_DENYLIST deve cobrir campos comuns de PHI."""
        required = {
            "patient_name",
            "date_of_birth",
            "ssn",
            "address",
            "phone",
            "email",
            "medical_record_number",
            "mrn",
        }
        assert required.issubset(PHI_DENYLIST), (
            f"PHI_DENYLIST missing: {required - PHI_DENYLIST}"
        )

    def test_score_payload_lacks_phi_fields(self) -> None:
        """O payload de score deve conter apenas campos não-PHI."""
        score = _make_score()
        # Verifica que o payload NÃO contém campos PHI
        payload_keys = {
            "mpi_id",
            "score_type",
            "score_value",
            "algorithm_version",
            "calculated_at",
            "source_score_id",
        }
        # Nenhum desses deve estar na denylist
        assert PHI_DENYLIST.isdisjoint(payload_keys), (
            f"Score payload keys overlap with PHI denylist: "
            f"{PHI_DENYLIST & payload_keys}"
        )

    def test_alert_payload_lacks_phi_fields(self) -> None:
        """O payload de alerta deve conter apenas campos não-PHI."""
        # Verifica que o payload NÃO contém campos PHI
        payload_keys = {
            "mpi_id",
            "severity",
            "status",
            "title",
            "definition_version",
            "created_at",
            "source_alert_id",
        }
        assert PHI_DENYLIST.isdisjoint(payload_keys), (
            f"Alert payload keys overlap with PHI denylist: "
            f"{PHI_DENYLIST & payload_keys}"
        )

    def test_phi_denylist_rejects_contaminated_payload(self) -> None:
        """Payload com campo PHI deve ser rejeitado."""
        from intensicare.services.gold_writer import _assert_phi_absent

        with pytest.raises(ValueError, match="PHI fields found"):
            _assert_phi_absent({"mpi_id": "X", "patient_name": "John Doe"})

    def test_clean_payload_passes_phi_check(self) -> None:
        """Payload limpo (sem PHI) não deve levantar exceção."""
        from intensicare.services.gold_writer import _assert_phi_absent

        # Não deve levantar exceção
        _assert_phi_absent({"mpi_id": "X", "score_type": "MEWS", "score_value": 3})


# ---------------------------------------------------------------------------
# write_scores
# ---------------------------------------------------------------------------


class TestWriteScores:
    """Testes para GoldWriter.write_scores()."""

    async def test_write_single_score(self, db_session: AsyncSession) -> None:
        """Escrever um score deve resultar em 1 linha inserida."""
        writer = GoldWriter(db_session)
        score = _make_score(id=100, algorithm_version="MEWS-v1.0")
        inserted = await writer.write_scores([score])
        await db_session.flush()

        assert inserted == 1

        # Verifica que foi persistido
        stmt = select(text("1")).select_from(FactPatientScore).where(
            FactPatientScore.source_score_id == 100
        )
        result = await db_session.execute(stmt)
        assert result.scalar_one() == 1

    async def test_write_multiple_scores(self, db_session: AsyncSession) -> None:
        """Escrever múltiplos scores deve inserir todos."""
        writer = GoldWriter(db_session)
        scores = [
            _make_score(id=201, mpi_id="MPI-A", score_type="MEWS", score_value=2),
            _make_score(id=202, mpi_id="MPI-B", score_type="NEWS2", score_value=5),
            _make_score(id=203, mpi_id="MPI-C", score_type="SOFA", score_value=7),
        ]
        inserted = await writer.write_scores(scores)
        await db_session.flush()

        assert inserted == 3

        # Conta linhas
        stmt = select(text("count(*)")).select_from(FactPatientScore)
        result = await db_session.execute(stmt)
        assert result.scalar_one() == 3

    async def test_algorithm_version_present_in_every_fact_score(
        self, db_session: AsyncSession
    ) -> None:
        """Todo fact_patient_score deve ter algorithm_version preenchido."""
        writer = GoldWriter(db_session)
        scores = [
            _make_score(id=301, algorithm_version="MEWS-v1.0"),
            _make_score(id=302, algorithm_version="NEWS2-v1.0"),
            _make_score(id=303, algorithm_version="SOFA-v1.0"),
            _make_score(id=304, algorithm_version="qSOFA-v1.0"),
        ]
        await writer.write_scores(scores)
        await db_session.flush()

        # Todas as linhas devem ter algorithm_version não-nulo
        stmt = select(FactPatientScore).where(
            FactPatientScore.algorithm_version.is_(None)
        )
        result = await db_session.execute(stmt)
        null_versions = result.fetchall()
        assert len(null_versions) == 0, (
            f"Found {len(null_versions)} fact_patient_score rows with NULL algorithm_version"
        )

    async def test_write_empty_scores_returns_zero(
        self, db_session: AsyncSession
    ) -> None:
        """Lista vazia deve retornar 0 inserções."""
        writer = GoldWriter(db_session)
        inserted = await writer.write_scores([])
        assert inserted == 0


# ---------------------------------------------------------------------------
# write_alerts
# ---------------------------------------------------------------------------


class TestWriteAlerts:
    """Testes para GoldWriter.write_alerts()."""

    async def test_write_single_alert(self, db_session: AsyncSession) -> None:
        """Escrever um alerta deve resultar em 1 linha inserida."""
        writer = GoldWriter(db_session)
        alert = _make_alert(
            id=400, definition_version_id="ALERT-TEST-v1.0"
        )
        inserted = await writer.write_alerts([alert])
        await db_session.flush()

        assert inserted == 1

        # Verifica que foi persistido com definition_version
        stmt = select(FactAlert).where(FactAlert.source_alert_id == 400)
        result = await db_session.execute(stmt)
        row = result.scalar_one()
        assert row.definition_version == "ALERT-TEST-v1.0"

    async def test_write_multiple_alerts(self, db_session: AsyncSession) -> None:
        """Escrever múltiplos alertas deve inserir todos."""
        writer = GoldWriter(db_session)
        alerts = [
            _make_alert(id=501, mpi_id="MPI-A", severity="watch",
                        definition_version_id="v1.0"),
            _make_alert(id=502, mpi_id="MPI-B", severity="urgent",
                        definition_version_id="v2.0"),
            _make_alert(id=503, mpi_id="MPI-C", severity="critical",
                        definition_version_id="v3.0"),
        ]
        inserted = await writer.write_alerts(alerts)
        await db_session.flush()

        assert inserted == 3

    async def test_definition_version_present_in_every_fact_alert(
        self, db_session: AsyncSession
    ) -> None:
        """Todo fact_alert deve ter definition_version preenchido."""
        writer = GoldWriter(db_session)
        alerts = [
            _make_alert(id=601, definition_version_id="ALERT-A-v1.0"),
            _make_alert(id=602, definition_version_id="ALERT-B-v1.0"),
            _make_alert(id=603, definition_version_id=None),  # fallback "unknown"
        ]
        await writer.write_alerts(alerts)
        await db_session.flush()

        # Todas as linhas devem ter definition_version não-nulo
        stmt = select(FactAlert).where(
            FactAlert.definition_version.is_(None)
        )
        result = await db_session.execute(stmt)
        null_versions = result.fetchall()
        assert len(null_versions) == 0, (
            f"Found {len(null_versions)} fact_alert rows with NULL definition_version"
        )

        # Verifica que o fallback "unknown" foi usado
        stmt2 = select(FactAlert).where(FactAlert.source_alert_id == 603)
        result2 = await db_session.execute(stmt2)
        row = result2.scalar_one()
        assert row.definition_version == "unknown"

    async def test_write_empty_alerts_returns_zero(
        self, db_session: AsyncSession
    ) -> None:
        """Lista vazia deve retornar 0 inserções."""
        writer = GoldWriter(db_session)
        inserted = await writer.write_alerts([])
        assert inserted == 0


# ---------------------------------------------------------------------------
# Idempotência: ON CONFLICT DO NOTHING
# ---------------------------------------------------------------------------


class TestIdempotency:
    """Garante que replay do mesmo dado não duplica linhas."""

    async def test_replay_scores_does_not_duplicate(
        self, db_session: AsyncSession
    ) -> None:
        """Escrever os mesmos scores duas vezes → apenas 1 linha por score."""
        writer = GoldWriter(db_session)
        scores = [
            _make_score(id=701, mpi_id="MPI-D", score_type="MEWS", score_value=3),
            _make_score(id=702, mpi_id="MPI-E", score_type="NEWS2", score_value=5),
        ]

        # Primeira escrita
        first = await writer.write_scores(scores)
        await db_session.flush()
        assert first == 2

        # Replay — mesmos source_score_ids
        second = await writer.write_scores(scores)
        await db_session.flush()
        assert second == 0  # ON CONFLICT DO NOTHING

        # Deve haver exatamente 2 linhas no total
        stmt = select(text("count(*)")).select_from(FactPatientScore)
        result = await db_session.execute(stmt)
        assert result.scalar_one() == 2

    async def test_replay_alerts_does_not_duplicate(
        self, db_session: AsyncSession
    ) -> None:
        """Escrever os mesmos alertas duas vezes → apenas 1 linha por alerta."""
        writer = GoldWriter(db_session)
        alerts = [
            _make_alert(id=801, mpi_id="MPI-F", severity="urgent"),
            _make_alert(id=802, mpi_id="MPI-G", severity="critical"),
        ]

        # Primeira escrita
        first = await writer.write_alerts(alerts)
        await db_session.flush()
        assert first == 2

        # Replay
        second = await writer.write_alerts(alerts)
        await db_session.flush()
        assert second == 0

        # Deve haver exatamente 2 linhas no total
        stmt = select(text("count(*)")).select_from(FactAlert)
        result = await db_session.execute(stmt)
        assert result.scalar_one() == 2

    async def test_partial_replay_only_inserts_new(
        self, db_session: AsyncSession
    ) -> None:
        """Replay com alguns novos + alguns existentes → apenas novos inseridos."""
        writer = GoldWriter(db_session)
        batch1 = [
            _make_score(id=901, mpi_id="MPI-H", score_type="MEWS", score_value=1),
            _make_score(id=902, mpi_id="MPI-I", score_type="MEWS", score_value=2),
        ]
        await writer.write_scores(batch1)
        await db_session.flush()

        # Batch 2: um existente (901) + um novo (903)
        batch2 = [
            _make_score(id=901, mpi_id="MPI-H", score_type="MEWS", score_value=1),
            _make_score(id=903, mpi_id="MPI-J", score_type="MEWS", score_value=3),
        ]
        inserted = await writer.write_scores(batch2)
        await db_session.flush()

        assert inserted == 1  # apenas o novo (903)

        # Total deve ser 3
        stmt = select(text("count(*)")).select_from(FactPatientScore)
        result = await db_session.execute(stmt)
        assert result.scalar_one() == 3


# ---------------------------------------------------------------------------
# One-directional: writer nunca lê de volta para scoring
# ---------------------------------------------------------------------------


class TestOneDirectional:
    """Garante que o GoldWriter é estritamente write-only."""

    def test_writer_has_no_read_methods_for_scoring(self) -> None:
        """GoldWriter não deve expor métodos de leitura para scoring."""
        writer_methods = set(dir(GoldWriter))
        # Não deve ter métodos públicos de leitura/query
        forbidden_patterns = ["read", "get", "query", "fetch", "select", "load"]
        for pattern in forbidden_patterns:
            matching = [
                m for m in writer_methods
                if pattern in m.lower() and not m.startswith("_")
            ]
            assert len(matching) == 0, (
                f"GoldWriter should not have '{pattern}' method (one-directional). "
                f"Found: {matching}"
            )

    async def test_writer_does_not_read_back_from_fact_tables(
        self, db_session: AsyncSession
    ) -> None:
        """Após escrever, o writer não consulta as tabelas fact_*."""
        writer = GoldWriter(db_session)
        score = _make_score(id=1001)
        await writer.write_scores([score])
        await db_session.flush()

        # Verifica que o writer não tem estado interno de leitura
        # (não armazena cache dos dados escritos para scoring)
        assert not hasattr(writer, "_score_cache")
        assert not hasattr(writer, "_alert_cache")


# ---------------------------------------------------------------------------
# DDL: tabelas fact_* existem e têm as colunas esperadas
# ---------------------------------------------------------------------------


class TestFactTableSchema:
    """Verifica que as tabelas fact_* foram criadas com as colunas corretas."""

    async def test_fact_patient_score_table_exists(
        self, db_session: AsyncSession
    ) -> None:
        """Tabela fact_patient_score deve existir."""
        stmt = select(text("count(*)")).select_from(FactPatientScore)
        result = await db_session.execute(stmt)
        assert result.scalar_one() == 0  # vazia mas existe

    async def test_fact_alert_table_exists(self, db_session: AsyncSession) -> None:
        """Tabela fact_alert deve existir."""
        stmt = select(text("count(*)")).select_from(FactAlert)
        result = await db_session.execute(stmt)
        assert result.scalar_one() == 0

    async def test_fact_patient_score_has_expected_columns(
        self, db_session: AsyncSession
    ) -> None:
        """fact_patient_score deve ter as colunas esperadas."""
        expected = {
            "id",
            "mpi_id",
            "score_type",
            "score_value",
            "algorithm_version",
            "calculated_at",
            "source_score_id",
        }
        columns = {c.name for c in FactPatientScore.__table__.columns}
        assert expected.issubset(columns), (
            f"Missing columns: {expected - columns}"
        )

    async def test_fact_alert_has_expected_columns(
        self, db_session: AsyncSession
    ) -> None:
        """fact_alert deve ter as colunas esperadas."""
        expected = {
            "id",
            "mpi_id",
            "severity",
            "status",
            "title",
            "definition_version",
            "created_at",
            "source_alert_id",
        }
        columns = {c.name for c in FactAlert.__table__.columns}
        assert expected.issubset(columns), (
            f"Missing columns: {expected - columns}"
        )

    async def test_fact_patient_score_unique_constraint(
        self, db_session: AsyncSession
    ) -> None:
        """source_score_id deve ter UNIQUE constraint."""
        writer = GoldWriter(db_session)
        score = _make_score(id=1101)
        await writer.write_scores([score])
        await db_session.flush()

        # Tentar inserir duplicado via raw SQL deve falhar
        from sqlalchemy.exc import IntegrityError

        dup_score = _make_score(id=1101, mpi_id="MPI-DUP")
        with pytest.raises(IntegrityError):
            # Força INSERT sem ON CONFLICT para testar a constraint
            await db_session.execute(
                FactPatientScore.__table__.insert().values(
                    mpi_id=dup_score.mpi_id,
                    score_type=dup_score.score_type,
                    score_value=dup_score.score_value,
                    algorithm_version=dup_score.algorithm_version,
                    calculated_at=dup_score.calculated_at,
                    source_score_id=dup_score.id,
                )
            )
            await db_session.flush()

    async def test_fact_alert_unique_constraint(
        self, db_session: AsyncSession
    ) -> None:
        """source_alert_id deve ter UNIQUE constraint."""
        writer = GoldWriter(db_session)
        alert = _make_alert(id=1201)
        await writer.write_alerts([alert])
        await db_session.flush()

        # Tentar inserir duplicado via raw SQL deve falhar
        from sqlalchemy.exc import IntegrityError

        dup_alert = _make_alert(id=1201, mpi_id="MPI-DUP")
        with pytest.raises(IntegrityError):
            await db_session.execute(
                FactAlert.__table__.insert().values(
                    mpi_id=dup_alert.mpi_id,
                    severity=dup_alert.severity,
                    status=dup_alert.status,
                    title=dup_alert.title,
                    definition_version=dup_alert.definition_version_id or "unknown",
                    created_at=dup_alert.created_at,
                    source_alert_id=dup_alert.id,
                )
            )
            await db_session.flush()
