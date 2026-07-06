"""Resolvedor de thresholds em 3 escopos: bed ≻ unit ≻ tenant (mais específico vence).

Também fornece helpers para escrever entradas de audit_trail em toda mutação
de threshold_config (REQ-INV-1-2).
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.models.audit_trail import AuditTrail
from intensicare.models.threshold_config import ThresholdConfig


async def resolve_threshold(
    db: AsyncSession,
    tenant_id: str,
    score_type: str,
    unit: str | None = None,
    bed_id: str | None = None,
) -> ThresholdConfig | None:
    """Resolve the most specific threshold config for a given scope.

    Resolution order: **bed ≻ unit ≻ tenant** (most specific wins).

    Parameters
    ----------
    db:
        Async database session.
    tenant_id:
        Tenant identifier (required — tenant-wide is the fallback).
    score_type:
        Clinical score type (e.g. "MEWS", "NEWS2", "SOFA").
    unit:
        Optional unit (e.g. "ICU", "ER"). When provided, unit-level configs
        are checked *before* tenant-level.
    bed_id:
        Optional bed identifier. When provided, bed-level configs are checked
        *first* (highest priority).

    Returns
    -------
    ThresholdConfig | None
        The resolved config, or ``None`` if no threshold exists at any scope.
    """
    # 1. Bed-level (most specific)
    if bed_id is not None:
        result = await db.execute(
            select(ThresholdConfig).where(
                ThresholdConfig.tenant_id == tenant_id,
                ThresholdConfig.score_type == score_type,
                ThresholdConfig.bed_id == bed_id,
            )
        )
        config = result.scalar_one_or_none()
        if config is not None:
            return config

    # 2. Unit-level
    if unit is not None:
        result = await db.execute(
            select(ThresholdConfig).where(
                ThresholdConfig.tenant_id == tenant_id,
                ThresholdConfig.score_type == score_type,
                ThresholdConfig.unit == unit,
                ThresholdConfig.bed_id.is_(None),  # exclui configs de leito
            )
        )
        config = result.scalar_one_or_none()
        if config is not None:
            return config

    # 3. Tenant-level (fallback — unit + bed_id ambos NULL)
    result = await db.execute(
        select(ThresholdConfig).where(
            ThresholdConfig.tenant_id == tenant_id,
            ThresholdConfig.score_type == score_type,
            ThresholdConfig.unit.is_(None),
            ThresholdConfig.bed_id.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def write_threshold_audit(
    db: AsyncSession,
    *,
    action: str,
    threshold_id: int,
    tenant_id: str,
    actor: str,
    before_state: bytes | None = None,
    after_state: bytes | None = None,
    request_id: str | None = None,
) -> AuditTrail:
    """Cria uma entrada imutável de auditoria para mutação de threshold_config.

    Ações válidas: ``threshold.create``, ``threshold.update``, ``threshold.delete``.

    Requisito REQ-INV-1-2: toda mutação de threshold deve ser auditada.
    """
    entry = AuditTrail(
        event_ts=datetime.now(timezone.utc),
        tenant_id=tenant_id,
        actor=actor,
        action=action,
        entity_table="threshold_config",
        entity_id=str(threshold_id),
        before_state=before_state,
        after_state=after_state,
        request_id=request_id,
    )
    db.add(entry)
    await db.flush()
    return entry
