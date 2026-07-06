"""Testes para threshold_resolver — resolução 3-escopos + auditoria de mutações."""

import json

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.models.audit_trail import AuditTrail
from intensicare.models.threshold_config import ThresholdConfig
from intensicare.services.threshold_resolver import (
    resolve_threshold,
    write_threshold_audit,
)


# ── helpers ────────────────────────────────────────────────────────────────

async def _create_config(
    db: AsyncSession,
    *,
    tenant_id: str = "austa",
    unit: str | None = None,
    bed_id: str | None = None,
    score_type: str = "MEWS",
    watch: int = 3,
    urgent: int = 5,
    critical: int = 7,
) -> ThresholdConfig:
    """Cria um ThresholdConfig e retorna o objeto."""
    cfg = ThresholdConfig(
        tenant_id=tenant_id,
        unit=unit,
        bed_id=bed_id,
        score_type=score_type,
        watch_threshold=watch,
        urgent_threshold=urgent,
        critical_threshold=critical,
    )
    db.add(cfg)
    await db.flush()
    return cfg


# ── Resolução 3-escopos ────────────────────────────────────────────────────


class TestResolveThreshold:
    """Testes de resolução bed ≻ unit ≻ tenant."""

    @pytest.mark.asyncio
    async def test_bed_overrides_unit(self, db_session: AsyncSession):
        """Bed-level config deve ter precedência sobre unit-level."""
        await _create_config(db_session, unit=None, bed_id=None, watch=3)       # tenant
        await _create_config(db_session, unit="ICU", bed_id=None, watch=2)      # unit
        await _create_config(db_session, unit="ICU", bed_id="BED-01", watch=1)  # bed

        result = await resolve_threshold(
            db=db_session,
            tenant_id="austa",
            score_type="MEWS",
            unit="ICU",
            bed_id="BED-01",
        )
        assert result is not None
        assert result.watch_threshold == 1           # bed-level venceu
        assert result.bed_id == "BED-01"

    @pytest.mark.asyncio
    async def test_unit_overrides_tenant(self, db_session: AsyncSession):
        """Unit-level config deve ter precedência sobre tenant-level."""
        await _create_config(db_session, unit=None, bed_id=None, watch=3)   # tenant
        await _create_config(db_session, unit="ICU", bed_id=None, watch=2)  # unit

        result = await resolve_threshold(
            db=db_session,
            tenant_id="austa",
            score_type="MEWS",
            unit="ICU",
            bed_id="BED-01",  # bed não tem config → cai para unit
        )
        assert result is not None
        assert result.watch_threshold == 2           # unit-level venceu
        assert result.unit == "ICU"

    @pytest.mark.asyncio
    async def test_tenant_is_fallback(self, db_session: AsyncSession):
        """Tenant-level é usado quando não há config mais específica."""
        await _create_config(db_session, unit=None, bed_id=None, watch=3)  # tenant

        result = await resolve_threshold(
            db=db_session,
            tenant_id="austa",
            score_type="MEWS",
            unit="ER",
            bed_id="BED-99",
        )
        assert result is not None
        assert result.watch_threshold == 3           # tenant fallback
        assert result.unit is None
        assert result.bed_id is None

    @pytest.mark.asyncio
    async def test_no_config_returns_none(self, db_session: AsyncSession):
        """Sem nenhum config em qualquer escopo → None."""
        result = await resolve_threshold(
            db=db_session,
            tenant_id="unknown",
            score_type="NEWS2",
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_bed_without_unit_still_resolves(self, db_session: AsyncSession):
        """Bed-level config é encontrado mesmo se unit não for informada."""
        await _create_config(db_session, unit="ICU", bed_id="BED-01", watch=1)

        result = await resolve_threshold(
            db=db_session,
            tenant_id="austa",
            score_type="MEWS",
            bed_id="BED-01",
            unit=None,  # unit ausente, mas bed_id resolve
        )
        assert result is not None
        assert result.watch_threshold == 1
        assert result.bed_id == "BED-01"

    @pytest.mark.asyncio
    async def test_unit_without_bed_falls_back_to_tenant(self, db_session: AsyncSession):
        """Quando unit existe mas bed não, deve cair para unit se existir,
        senão tenant."""
        await _create_config(db_session, unit=None, bed_id=None, watch=5)  # tenant
        await _create_config(db_session, unit="ICU", bed_id=None, watch=2)  # unit

        result = await resolve_threshold(
            db=db_session,
            tenant_id="austa",
            score_type="MEWS",
            unit="ICU",
        )
        assert result is not None
        assert result.watch_threshold == 2           # unit-level

    @pytest.mark.asyncio
    async def test_different_score_types_isolated(self, db_session: AsyncSession):
        """Configs de score_type diferentes não interferem entre si."""
        await _create_config(db_session, score_type="MEWS", watch=3)
        await _create_config(db_session, score_type="NEWS2", watch=5)

        result_mews = await resolve_threshold(
            db=db_session,
            tenant_id="austa",
            score_type="MEWS",
        )
        result_news2 = await resolve_threshold(
            db=db_session,
            tenant_id="austa",
            score_type="NEWS2",
        )
        assert result_mews is not None
        assert result_mews.watch_threshold == 3
        assert result_news2 is not None
        assert result_news2.watch_threshold == 5


# ── Auditoria de mutações (REQ-INV-1-2) ────────────────────────────────────


class TestThresholdAuditTrail:
    """REQ-INV-1-2: toda mutação de threshold_config → audit_trail."""

    @pytest.mark.asyncio
    async def test_create_writes_audit_trail(self, db_session: AsyncSession):
        """Criação de threshold deve gerar entrada de auditoria (threshold.create)."""
        cfg = await _create_config(db_session, watch=3)

        entry = await write_threshold_audit(
            db=db_session,
            action="threshold.create",
            threshold_id=cfg.id,
            tenant_id=cfg.tenant_id,
            actor="dr-smith@hospital.com",
            after_state=json.dumps({"watch": 3, "urgent": 5, "critical": 7}).encode(),
            request_id="req-001",
        )
        assert entry is not None
        assert entry.action == "threshold.create"
        assert entry.entity_table == "threshold_config"
        assert entry.entity_id == str(cfg.id)
        assert entry.actor == "dr-smith@hospital.com"

    @pytest.mark.asyncio
    async def test_update_writes_audit_trail(self, db_session: AsyncSession):
        """Atualização de threshold deve gerar entrada de auditoria (threshold.update)."""
        cfg = await _create_config(db_session, watch=3)

        before = json.dumps({"watch": 3, "urgent": 5, "critical": 7}).encode()
        after = json.dumps({"watch": 2, "urgent": 4, "critical": 6}).encode()

        entry = await write_threshold_audit(
            db=db_session,
            action="threshold.update",
            threshold_id=cfg.id,
            tenant_id=cfg.tenant_id,
            actor="nurse-jones@hospital.com",
            before_state=before,
            after_state=after,
            request_id="req-002",
        )
        assert entry.action == "threshold.update"
        assert entry.before_state == before
        assert entry.after_state == after
        assert entry.actor == "nurse-jones@hospital.com"

    @pytest.mark.asyncio
    async def test_delete_writes_audit_trail(self, db_session: AsyncSession):
        """Exclusão de threshold deve gerar entrada de auditoria (threshold.delete)."""
        cfg = await _create_config(db_session, watch=3)

        before = json.dumps({"watch": 3, "urgent": 5, "critical": 7}).encode()

        entry = await write_threshold_audit(
            db=db_session,
            action="threshold.delete",
            threshold_id=cfg.id,
            tenant_id=cfg.tenant_id,
            actor="admin@hospital.com",
            before_state=before,
            after_state=None,  # após delete, sem estado
            request_id="req-003",
        )
        assert entry.action == "threshold.delete"
        assert entry.before_state == before
        assert entry.after_state is None

    @pytest.mark.asyncio
    async def test_audit_entry_persisted_in_db(self, db_session: AsyncSession):
        """Entrada de auditoria deve estar persistida no banco (round-trip)."""
        cfg = await _create_config(db_session, watch=3)

        await write_threshold_audit(
            db=db_session,
            action="threshold.create",
            threshold_id=cfg.id,
            tenant_id=cfg.tenant_id,
            actor="dr-smith@hospital.com",
            request_id="req-roundtrip",
        )

        # Reler do banco
        result = await db_session.execute(
            text(
                "SELECT * FROM audit_trail "
                "WHERE entity_table = 'threshold_config' AND entity_id = :eid"
            ),
            {"eid": str(cfg.id)},
        )
        rows = result.fetchall()
        assert len(rows) == 1
        assert rows[0].action == "threshold.create"
        assert rows[0].actor == "dr-smith@hospital.com"
        assert rows[0].request_id == "req-roundtrip"

    @pytest.mark.asyncio
    async def test_multiple_mutations_all_audited(self, db_session: AsyncSession):
        """Múltiplas mutações em threshold_config geram entradas distintas."""
        cfg = await _create_config(db_session, watch=3)

        # Create audit
        await write_threshold_audit(
            db=db_session,
            action="threshold.create",
            threshold_id=cfg.id,
            tenant_id=cfg.tenant_id,
            actor="dr-smith@hospital.com",
            request_id="req-multi-1",
        )

        # Update audit
        await write_threshold_audit(
            db=db_session,
            action="threshold.update",
            threshold_id=cfg.id,
            tenant_id=cfg.tenant_id,
            actor="nurse-jones@hospital.com",
            request_id="req-multi-2",
        )

        # Delete audit
        await write_threshold_audit(
            db=db_session,
            action="threshold.delete",
            threshold_id=cfg.id,
            tenant_id=cfg.tenant_id,
            actor="admin@hospital.com",
            request_id="req-multi-3",
        )

        result = await db_session.execute(
            text(
                "SELECT * FROM audit_trail "
                "WHERE entity_table = 'threshold_config' AND entity_id = :eid "
                "ORDER BY event_ts"
            ),
            {"eid": str(cfg.id)},
        )
        rows = result.fetchall()
        assert len(rows) == 3
        assert rows[0].action == "threshold.create"
        assert rows[1].action == "threshold.update"
        assert rows[2].action == "threshold.delete"

    @pytest.mark.asyncio
    async def test_resolution_with_audit_chain(self, db_session: AsyncSession):
        """Cenário completo: cria configs, resolve e audita."""
        # Cria configs em 3 níveis
        tenant_cfg = await _create_config(db_session, unit=None, bed_id=None, watch=3)
        unit_cfg = await _create_config(db_session, unit="ICU", bed_id=None, watch=2)
        bed_cfg = await _create_config(db_session, unit="ICU", bed_id="BED-01", watch=1)

        # Audita criações
        for cfg, action in [
            (tenant_cfg, "threshold.create"),
            (unit_cfg, "threshold.create"),
            (bed_cfg, "threshold.create"),
        ]:
            await write_threshold_audit(
                db=db_session,
                action=action,
                threshold_id=cfg.id,
                tenant_id=cfg.tenant_id,
                actor="admin@hospital.com",
            )

        # Resolve: bed-level deve vencer
        result = await resolve_threshold(
            db=db_session,
            tenant_id="austa",
            score_type="MEWS",
            unit="ICU",
            bed_id="BED-01",
        )
        assert result is not None
        assert result.watch_threshold == 1
        assert result.id == bed_cfg.id  # identidade correta

        # Verifica que todas as entradas de auditoria estão no banco
        audit_result = await db_session.execute(
            text(
                "SELECT count(*) as cnt FROM audit_trail "
                "WHERE entity_table = 'threshold_config'"
            )
        )
        assert audit_result.scalar() == 3
