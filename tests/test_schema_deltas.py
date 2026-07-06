"""Tests for WO-015 schema deltas — alert status extension, threshold_config.bed_id scope."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.models.alert import Alert
from intensicare.models.alert_definition_version import AlertDefinitionVersion
from intensicare.models.correlation_event import CorrelationEvent
from intensicare.models.threshold_config import ThresholdConfig


# ═══════════════════════════════════════════════════════════════════════════
# Alert status — acting / escalated
# ═══════════════════════════════════════════════════════════════════════════


class TestAlertStatusExtended:
    """WO-015: alert.status deve aceitar 'acting' e 'escalated'."""

    async def test_status_acting_is_persisted(self, db_session: AsyncSession):
        """Cria alerta com status='acting' e verifica persistência."""
        alert = Alert(
            mpi_id="MPI-2001",
            severity="watch",
            status="acting",
            title="Paciente sob intervenção",
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(alert)
        await db_session.flush()
        await db_session.refresh(alert)

        assert alert.status == "acting"
        assert alert.id is not None

    async def test_status_escalated_is_persisted(self, db_session: AsyncSession):
        """Cria alerta com status='escalated' e verifica persistência."""
        alert = Alert(
            mpi_id="MPI-2002",
            severity="urgent",
            status="escalated",
            title="Alerta escalado para time de resposta rápida",
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(alert)
        await db_session.flush()
        await db_session.refresh(alert)

        assert alert.status == "escalated"
        assert alert.id is not None

    async def test_status_lifecycle_transitions(self, db_session: AsyncSession):
        """Simula transições de status: active → acting → acknowledged → resolved."""
        alert = Alert(
            mpi_id="MPI-2003",
            severity="critical",
            status="active",
            title="Transição de status",
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(alert)
        await db_session.flush()

        # active → acting
        alert.status = "acting"
        await db_session.flush()
        assert alert.status == "acting"

        # acting → acknowledged
        alert.status = "acknowledged"
        alert.acknowledged_at = datetime.now(timezone.utc)
        alert.acknowledged_by = "enfermeiro-1"
        await db_session.flush()
        assert alert.status == "acknowledged"

        # acknowledged → resolved
        alert.status = "resolved"
        alert.resolved_at = datetime.now(timezone.utc)
        alert.resolution = "resolved_normally"
        await db_session.flush()
        assert alert.status == "resolved"

    async def test_status_escalated_lifecycle(self, db_session: AsyncSession):
        """Simula transição: active → escalated → acknowledged → resolved."""
        alert = Alert(
            mpi_id="MPI-2004",
            severity="urgent",
            status="active",
            title="Escalação de status",
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(alert)
        await db_session.flush()

        # active → escalated
        alert.status = "escalated"
        await db_session.flush()
        assert alert.status == "escalated"

        # escalated → acknowledged
        alert.status = "acknowledged"
        alert.acknowledged_at = datetime.now(timezone.utc)
        await db_session.flush()
        assert alert.status == "acknowledged"


# ═══════════════════════════════════════════════════════════════════════════
# Alert FK columns — definition_version_id, correlation_event_id
# ═══════════════════════════════════════════════════════════════════════════


class TestAlertForeignKeyColumns:
    """WO-015: alert.definition_version_id e correlation_event_id devem ser
    aceitos como valores nulos (FKs opcionais)."""

    async def test_definition_version_id_nullable(self, db_session: AsyncSession):
        """Alert pode ser criado sem definition_version_id."""
        alert = Alert(
            mpi_id="MPI-3001",
            severity="watch",
            status="active",
            title="Alerta sem versão de definição",
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(alert)
        await db_session.flush()

        assert alert.definition_version_id is None

    async def test_definition_version_id_with_fk(self, db_session: AsyncSession):
        """Alert referencia uma definition_version existente."""
        # Seed a definition version
        adv = AlertDefinitionVersion(
            definition_version="ALERT-DEFAULT-v1.0",
            score_type="MEWS",
            semver="1.0.0",
            spec_hash="abc123",
            effective_from=datetime.now(timezone.utc),
        )
        db_session.add(adv)
        await db_session.flush()

        alert = Alert(
            mpi_id="MPI-3002",
            severity="urgent",
            status="active",
            definition_version_id="ALERT-DEFAULT-v1.0",
            title="Alerta com versão de definição",
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(alert)
        await db_session.flush()

        assert alert.definition_version_id == "ALERT-DEFAULT-v1.0"

    async def test_correlation_event_id_nullable(self, db_session: AsyncSession):
        """Alert pode ser criado sem correlation_event_id."""
        alert = Alert(
            mpi_id="MPI-3003",
            severity="critical",
            status="active",
            title="Alerta sem evento de correlação",
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(alert)
        await db_session.flush()

        assert alert.correlation_event_id is None

    async def test_correlation_event_id_with_fk(self, db_session: AsyncSession):
        """Alert referencia um correlation_event existente."""
        ce = CorrelationEvent(
            mpi_id="MPI-3004",
            correlation_key="hash-deterministico-001",
            title="Cluster de deterioração multi-sistema",
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(ce)
        await db_session.flush()

        alert = Alert(
            mpi_id="MPI-3004",
            severity="critical",
            status="active",
            correlation_event_id=ce.id,
            title="Alerta correlacionado",
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(alert)
        await db_session.flush()

        assert alert.correlation_event_id == ce.id


# ═══════════════════════════════════════════════════════════════════════════
# ThresholdConfig bed_id + unique scope (bed ≻ unit ≻ tenant)
# ═══════════════════════════════════════════════════════════════════════════


class TestThresholdConfigBedScope:
    """WO-015: threshold_config.bed_id com UNIQUE (tenant_id, unit, bed_id, score_type).

    Escopo de resolução: bed ≻ unit ≻ tenant.
    """

    async def test_bed_id_column_present(self, db_session: AsyncSession):
        """Verifica que bed_id é aceito e persistido."""
        config = ThresholdConfig(
            tenant_id="tenant-1",
            unit="ICU-A",
            bed_id="BED-01",
            score_type="MEWS",
            watch_threshold=3,
            urgent_threshold=5,
            critical_threshold=7,
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(config)
        await db_session.flush()
        await db_session.refresh(config)

        assert config.bed_id == "BED-01"
        assert config.unit == "ICU-A"
        assert config.tenant_id == "tenant-1"

    async def test_bed_id_nullable_fallback_to_unit(self, db_session: AsyncSession):
        """ThresholdConfig sem bed_id (NULL) funciona como escopo de unidade."""
        config = ThresholdConfig(
            tenant_id="tenant-1",
            unit="ICU-B",
            bed_id=None,
            score_type="NEWS2",
            watch_threshold=4,
            urgent_threshold=6,
            critical_threshold=8,
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(config)
        await db_session.flush()
        await db_session.refresh(config)

        assert config.bed_id is None
        assert config.unit == "ICU-B"

    async def test_unique_scope_bed_level(self, db_session: AsyncSession):
        """Dois leitos diferentes na mesma unidade podem ter thresholds distintos."""
        config_a = ThresholdConfig(
            tenant_id="tenant-1",
            unit="ICU-A",
            bed_id="BED-01",
            score_type="MEWS",
            watch_threshold=3,
            urgent_threshold=5,
            critical_threshold=7,
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(config_a)
        await db_session.flush()

        config_b = ThresholdConfig(
            tenant_id="tenant-1",
            unit="ICU-A",
            bed_id="BED-02",
            score_type="MEWS",
            watch_threshold=4,
            urgent_threshold=6,
            critical_threshold=8,
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(config_b)
        await db_session.flush()

        assert config_a.id != config_b.id
        assert config_a.bed_id == "BED-01"
        assert config_b.bed_id == "BED-02"

    async def test_unique_scope_unit_fallback(self, db_session: AsyncSession):
        """Thresholds com mesmo tenant+unit+score_type sem bed (ambos NULL)
        podem coexistir com thresholds com bed definido."""
        # Unidade sem bed
        config_unit = ThresholdConfig(
            tenant_id="tenant-1",
            unit="ICU-C",
            bed_id=None,
            score_type="MEWS",
            watch_threshold=2,
            urgent_threshold=4,
            critical_threshold=6,
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(config_unit)
        await db_session.flush()

        # Leito específico na mesma unidade
        config_bed = ThresholdConfig(
            tenant_id="tenant-1",
            unit="ICU-C",
            bed_id="BED-03",
            score_type="MEWS",
            watch_threshold=5,
            urgent_threshold=7,
            critical_threshold=9,
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(config_bed)
        await db_session.flush()

        assert config_unit.bed_id is None
        assert config_bed.bed_id == "BED-03"
        # Ambos coexistem — scopes diferentes na unique constraint
        assert config_unit.id != config_bed.id

    async def test_unique_scope_tenant_fallback(self, db_session: AsyncSession):
        """Threshold global do tenant (unit + bed_id ambos NULL)."""
        config = ThresholdConfig(
            tenant_id="tenant-1",
            unit=None,
            bed_id=None,
            score_type="MEWS",
            watch_threshold=3,
            urgent_threshold=5,
            critical_threshold=7,
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(config)
        await db_session.flush()
        await db_session.refresh(config)

        assert config.unit is None
        assert config.bed_id is None
        assert config.tenant_id == "tenant-1"

    async def test_unique_scope_duplicate_rejected(self, db_session: AsyncSession):
        """Tentar inserir (tenant_id, unit, bed_id, score_type) duplicado
        deve lançar IntegrityError."""
        from sqlalchemy.exc import IntegrityError

        config1 = ThresholdConfig(
            tenant_id="tenant-1",
            unit="ICU-D",
            bed_id="BED-10",
            score_type="MEWS",
            watch_threshold=3,
            urgent_threshold=5,
            critical_threshold=7,
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(config1)
        await db_session.flush()

        config2 = ThresholdConfig(
            tenant_id="tenant-1",
            unit="ICU-D",
            bed_id="BED-10",
            score_type="MEWS",
            watch_threshold=4,
            urgent_threshold=6,
            critical_threshold=8,
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(config2)

        with pytest.raises(IntegrityError):
            await db_session.flush()


# ═══════════════════════════════════════════════════════════════════════════
# Severity model — normal já deve existir (WO-011)
# ═══════════════════════════════════════════════════════════════════════════


class TestSeverityNormalPresent:
    """WO-011: severidade 'normal' já deve ser aceita (verificação)."""

    async def test_severity_normal_accepted(self, db_session: AsyncSession):
        """Alerta com severity='normal' deve ser persistido sem erro."""
        alert = Alert(
            mpi_id="MPI-4001",
            severity="normal",
            status="active",
            title="Alerta de severidade normal",
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(alert)
        await db_session.flush()
        await db_session.refresh(alert)

        assert alert.severity == "normal"
