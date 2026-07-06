"""add audit_trail hypertable with immutable trigger (INV-1 / CON-0066)

Revision ID: 0003
Revises: 33909c9d8845
Create Date: 2026-07-05 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0003"
down_revision: Union[str, None] = "33909c9d8845"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # pgcrypto extension (needed for encrypted snapshots — INV-4 readiness)
    # ------------------------------------------------------------------
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto SCHEMA public")

    # ------------------------------------------------------------------
    # audit_trail (TimescaleDB hypertable on event_ts)
    # ------------------------------------------------------------------
    op.create_table(
        "audit_trail",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "event_ts",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("tenant_id", sa.String(32), nullable=True),
        sa.Column("actor", sa.String(255), nullable=False),
        sa.Column("action", sa.String(48), nullable=False),
        sa.Column("entity_table", sa.String(48), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("mpi_id", sa.String(64), nullable=True),
        sa.Column("before_state", sa.LargeBinary(), nullable=True),
        sa.Column("after_state", sa.LargeBinary(), nullable=True),
        sa.Column("request_id", sa.String(64), nullable=True),
        sa.PrimaryKeyConstraint("id", "event_ts"),
    )

    # TimescaleDB hypertable
    op.execute(
        "SELECT create_hypertable('audit_trail', 'event_ts', if_not_exists => true)"
    )

    # ------------------------------------------------------------------
    # Anti-mutation trigger — bloqueia UPDATE/DELETE (INV-1 / CON-0066)
    # ------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION audit_trail_no_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'audit_trail is append-only (INV-1 / CON-0066): % blocked', TG_OP;
        END;
        $$ LANGUAGE plpgsql
    """)

    op.execute("""
        CREATE TRIGGER trg_audit_trail_immutable
            BEFORE UPDATE OR DELETE ON audit_trail
            FOR EACH ROW EXECUTE FUNCTION audit_trail_no_mutation()
    """)

    # Revoke UPDATE, DELETE from public — defense in depth
    op.execute("REVOKE UPDATE, DELETE ON audit_trail FROM PUBLIC")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_trail_immutable ON audit_trail")
    op.execute("DROP FUNCTION IF EXISTS audit_trail_no_mutation()")
    op.drop_table("audit_trail")
