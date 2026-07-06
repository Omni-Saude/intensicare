"""Trilha de auditoria imutável — TimescaleDB hypertable em event_ts.

INV-1 / CON-0066: Tabela append-only com trigger anti-mutation. Snapshots
before/after são criptografados via pgcrypto.
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, LargeBinary, String, text
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


class AuditTrail(Base):
    """Registro imutável de auditoria para ações clínicas e administrativas.

    Hypertable em ``event_ts``. Protegida por ``trg_audit_trail_immutable``
    que bloqueia UPDATE/DELETE (INV-1).
    """

    __tablename__ = "audit_trail"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
        nullable=False,
        server_default=text("now()"),
    )
    tenant_id: Mapped[str | None] = mapped_column(String(32))
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(48), nullable=False)
    entity_table: Mapped[str] = mapped_column(String(48), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    mpi_id: Mapped[str | None] = mapped_column(String(64))
    before_state: Mapped[bytes | None] = mapped_column(LargeBinary)
    after_state: Mapped[bytes | None] = mapped_column(LargeBinary)
    request_id: Mapped[str | None] = mapped_column(String(64))
