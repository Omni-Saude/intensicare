"""Schema deltas — alert/definition_version_id, correlation_event_id,
status acting/escalated, threshold_config.bed_id + unique scope (WO-015)

Revision ID: 0011
Revises: 0009
Create Date: 2026-07-05 23:00:00.000000

- Creates alert_definition_version (immutable version registry for alert definitions).
- Creates correlation_event (clusters of correlated alerts).
- Adds alert.definition_version_id FK → alert_definition_version.
- Adds alert.correlation_event_id FK → correlation_event.
- Adds CHECK constraint on alert.status: active, acting, escalated, acknowledged, resolved.
- Adds threshold_config.bed_id column.
- Adds UNIQUE (tenant_id, unit, bed_id, score_type) on threshold_config.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0011"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Status values accepted by alert.status after WO-015
ALERT_STATUS_VALUES = ("active", "acting", "escalated", "acknowledged", "resolved")


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Create alert_definition_version table
    # ------------------------------------------------------------------
    op.create_table(
        "alert_definition_version",
        sa.Column("definition_version", sa.String(32), nullable=False),
        sa.Column("score_type", sa.String(16), nullable=False),
        sa.Column("semver", sa.String(16), nullable=False),
        sa.Column("spec_hash", sa.String(64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "effective_from",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("retired_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("definition_version"),
    )

    # ------------------------------------------------------------------
    # 2. Create correlation_event table
    # ------------------------------------------------------------------
    op.create_table(
        "correlation_event",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mpi_id", sa.String(64), nullable=False, index=True),
        sa.Column(
            "correlation_key",
            sa.String(64),
            nullable=False,
            comment="Chave determinística de correlação (hash de scores + janela)",
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # ------------------------------------------------------------------
    # 3. Add alert.definition_version_id (nullable FK)
    # ------------------------------------------------------------------
    op.add_column(
        "alert",
        sa.Column(
            "definition_version_id",
            sa.String(32),
            nullable=True,
            comment="Versão da definição que gerou este alerta",
        ),
    )
    op.create_foreign_key(
        "fk_alert_definition_version",
        "alert",
        "alert_definition_version",
        ["definition_version_id"],
        ["definition_version"],
    )

    # ------------------------------------------------------------------
    # 4. Add alert.correlation_event_id (nullable FK)
    # ------------------------------------------------------------------
    op.add_column(
        "alert",
        sa.Column(
            "correlation_event_id",
            sa.BigInteger(),
            nullable=True,
            comment="Evento de correlação ao qual este alerta pertence",
        ),
    )
    op.create_foreign_key(
        "fk_alert_correlation_event",
        "alert",
        "correlation_event",
        ["correlation_event_id"],
        ["id"],
    )

    # ------------------------------------------------------------------
    # 5. Add CHECK constraint on alert.status for extended enum
    # ------------------------------------------------------------------
    op.create_check_constraint(
        "ck_alert_status_values",
        "alert",
        sa.text(
            f"status = ANY(ARRAY[{', '.join(repr(s) for s in ALERT_STATUS_VALUES)}])"
        ),
    )

    # ------------------------------------------------------------------
    # 6. Add threshold_config.bed_id column
    # ------------------------------------------------------------------
    op.add_column(
        "threshold_config",
        sa.Column("bed_id", sa.String(32), nullable=True),
    )

    # ------------------------------------------------------------------
    # 7. Add UNIQUE constraint (tenant_id, unit, bed_id, score_type)
    # ------------------------------------------------------------------
    op.create_unique_constraint(
        "uq_threshold_scope",
        "threshold_config",
        ["tenant_id", "unit", "bed_id", "score_type"],
    )


def downgrade() -> None:
    # 1. Drop unique constraint
    op.drop_constraint("uq_threshold_scope", "threshold_config", type_="unique")

    # 2. Drop bed_id column
    op.drop_column("threshold_config", "bed_id")

    # 3. Drop alert.status CHECK constraint
    op.drop_constraint("ck_alert_status_values", "alert", type_="check")

    # 4. Drop FK + column: correlation_event_id
    op.drop_constraint("fk_alert_correlation_event", "alert", type_="foreignkey")
    op.drop_column("alert", "correlation_event_id")

    # 5. Drop FK + column: definition_version_id
    op.drop_constraint("fk_alert_definition_version", "alert", type_="foreignkey")
    op.drop_column("alert", "definition_version_id")

    # 6. Drop correlation_event table
    op.drop_table("correlation_event")

    # 7. Drop alert_definition_version table
    op.drop_table("alert_definition_version")
