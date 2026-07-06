"""Testes para audit_trail — verifica imutabilidade e append-only (INV-1).

DRILL-AUDIT-TAMPER: UPDATE/DELETE bloqueados com exceção.
DRILL-AUDIT-COMPLETENESS: INSERT bem-sucedido, bytes preservados no round-trip.
"""

from datetime import datetime, timezone

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.models.audit_trail import AuditTrail


@pytest.mark.integration
class TestAuditTrailHypertable:
    """Verifica que a tabela audit_trail é uma hypertable do TimescaleDB."""

    async def test_hypertable_created(self, db_session: AsyncSession) -> None:
        """Confirma que create_hypertable foi aplicado com sucesso."""
        result = await db_session.execute(
            text(
                "SELECT * FROM timescaledb_information.hypertables "
                "WHERE hypertable_name = 'audit_trail'"
            )
        )
        row = result.fetchone()
        assert row is not None, "audit_trail deve ser uma hypertable do TimescaleDB"


@pytest.mark.integration
class TestAuditTrailInsert:
    """DRILL-AUDIT-COMPLETENESS: INSERT bem-sucedido, dados preservados."""

    async def test_insert_succeeds(self, db_session: AsyncSession) -> None:
        """Insere um registro e verifica que os dados são preservados."""
        before = b'{"status": "active", "severity": "watch"}'
        after = b'{"status": "acknowledged", "severity": "watch"}'

        entry = AuditTrail(
            event_ts=datetime(2026, 7, 5, 12, 0, 0, tzinfo=timezone.utc),
            tenant_id="tenant-01",
            actor="dr-smith@hospital.com",
            action="alert.acknowledge",
            entity_table="alert",
            entity_id="42",
            mpi_id="MPI-000001",
            before_state=before,
            after_state=after,
            request_id="trace-abc123",
        )
        db_session.add(entry)
        await db_session.flush()

        # Reler do banco
        result = await db_session.execute(
            text("SELECT * FROM audit_trail WHERE id = :id AND event_ts = :ts"),
            {"id": entry.id, "ts": entry.event_ts},
        )
        row = result.fetchone()
        assert row is not None
        assert row.actor == "dr-smith@hospital.com"
        assert row.action == "alert.acknowledge"
        assert row.entity_table == "alert"
        assert row.entity_id == "42"
        assert row.mpi_id == "MPI-000001"
        assert bytes(row.before_state) == before
        assert bytes(row.after_state) == after
        assert row.request_id == "trace-abc123"

    async def test_insert_multiple_appends(self, db_session: AsyncSession) -> None:
        """Verifica que múltiplos INSERTs funcionam (append-only)."""
        ids = []
        for i in range(3):
            entry = AuditTrail(
                event_ts=datetime(2026, 7, 5, 13, i, 0, tzinfo=timezone.utc),
                tenant_id="tenant-01",
                actor="nurse-jones@hospital.com",
                action="threshold.update",
                entity_table="threshold_config",
                entity_id=str(100 + i),
                mpi_id=None,
                before_state=None,
                after_state=None,
                request_id=f"trace-{i:03d}",
            )
            db_session.add(entry)
            await db_session.flush()
            ids.append(entry.id)

        result = await db_session.execute(
            text("SELECT count(*) as cnt FROM audit_trail")
        )
        count = result.scalar()
        assert count == 3, f"Esperava 3 registros, encontrou {count}"


@pytest.mark.integration
class TestAuditTrailImmutable:
    """DRILL-AUDIT-TAMPER: UPDATE e DELETE são bloqueados pelo trigger."""

    async def _create_entry(self, db_session: AsyncSession) -> AuditTrail:
        """Helper: cria uma entrada de auditoria para testes de mutação."""
        entry = AuditTrail(
            event_ts=datetime(2026, 7, 5, 14, 0, 0, tzinfo=timezone.utc),
            tenant_id="tenant-01",
            actor="test@hospital.com",
            action="phi.read",
            entity_table="patient_cache",
            entity_id="MPI-000099",
            mpi_id="MPI-000099",
            request_id="trace-mutation",
        )
        db_session.add(entry)
        await db_session.flush()
        return entry

    async def test_update_blocked(self, db_session: AsyncSession) -> None:
        """DRILL-AUDIT-TAMPER: UPDATE dispara exceção do trigger."""
        entry = await self._create_entry(db_session)

        # Tentar UPDATE via SQL bruto (contorna o ORM que poderia não emitir UPDATE)
        with pytest.raises(Exception) as exc_info:
            await db_session.execute(
                text("UPDATE audit_trail SET actor = 'hacker' WHERE id = :id"),
                {"id": entry.id},
            )
            await db_session.flush()

        error_msg = str(exc_info.value).lower()
        assert "audit_trail is append-only" in error_msg or "blocked" in error_msg, (
            f"Mensagem de erro esperada não encontrada: {error_msg}"
        )

    async def test_delete_blocked(self, db_session: AsyncSession) -> None:
        """DRILL-AUDIT-TAMPER: DELETE dispara exceção do trigger."""
        entry = await self._create_entry(db_session)

        # Tentar DELETE via SQL bruto
        with pytest.raises(Exception) as exc_info:
            await db_session.execute(
                text("DELETE FROM audit_trail WHERE id = :id"),
                {"id": entry.id},
            )
            await db_session.flush()

        error_msg = str(exc_info.value).lower()
        assert "audit_trail is append-only" in error_msg or "blocked" in error_msg, (
            f"Mensagem de erro esperada não encontrada: {error_msg}"
        )

    async def test_row_preserved_after_blocked_mutation(
        self, db_session: AsyncSession
    ) -> None:
        """Verifica que após tentativa de mutação bloqueada, o registro original
        permanece intacto (DRILL-AUDIT-COMPLETENESS / row bytes unchanged)."""
        entry = await self._create_entry(db_session)
        original_actor = entry.actor

        # Tenta UPDATE (deve falhar)
        try:
            await db_session.execute(
                text("UPDATE audit_trail SET actor = 'hacker' WHERE id = :id"),
                {"id": entry.id},
            )
            await db_session.flush()
        except Exception:
            pass

        # O registro original deve permanecer inalterado
        await db_session.refresh(entry)
        assert entry.actor == original_actor, (
            f"Registro foi alterado! Esperado '{original_actor}', obtido '{entry.actor}'"
        )

    async def test_trigger_exists(self, db_session: AsyncSession) -> None:
        """Verifica que o trigger de imutabilidade está instalado."""
        result = await db_session.execute(
            text(
                "SELECT tgname FROM pg_trigger "
                "WHERE tgname = 'trg_audit_trail_immutable'"
            )
        )
        row = result.fetchone()
        assert row is not None, "Trigger trg_audit_trail_immutable não encontrado"
