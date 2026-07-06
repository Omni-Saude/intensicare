"""seed domain alert definitions — tabela alert_definition_version (WO-030+WO-031)

Revision ID: 0013_seed_domain_definitions
Revises: 0012
Create Date: 2026-07-05

Forward-only (ADR-0011): NUNCA editar uma migracao ja aplicada; sempre adicione uma nova.

Cria a tabela `alert_definition_version` no schema do tenant para versionamento de definicoes de
alertas de dominio (pharmaco-interaction e neuro-sedation). Cada alerta tem um identificador,
versao semantica e o caminho do YAML de origem.

Tambem faz o seed inicial com os alertas dos catalogos pharmaco-interaction.yaml e
neuro-sedation.yaml, ambos na versao 1.0.0.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Tabela UNQUALIFIED — o search_path (env.py) resolve no schema do tenant (schema-por-tenant).
    op.create_table(
        "alert_definition_version",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tenant", sa.Text(), nullable=False),
        sa.Column("alert_id", sa.Text(), nullable=False),
        sa.Column("domain", sa.Text(), nullable=False),
        sa.Column("version", sa.Text(), nullable=False, server_default="1.0.0"),
        sa.Column("yaml_path", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index(
        "ix_alert_definition_version_alert_id",
        "alert_definition_version",
        ["alert_id"],
    )
    op.create_index(
        "ix_alert_definition_version_domain",
        "alert_definition_version",
        ["domain"],
    )
    op.create_unique_constraint(
        "uq_alert_definition_version_tenant_alert_id",
        "alert_definition_version",
        ["tenant", "alert_id", "version"],
    )

    # ── Seed: pharmaco-interaction domain ──
    pharmaco_alerts = [
        ("PHARMA-WARF-NSAID-001", "pharmaco-interaction", "1.0.0"),
        ("PHARMA-WARF-NSAID-002", "pharmaco-interaction", "1.0.0"),
        ("PHARMA-ACEI-K-001", "pharmaco-interaction", "1.0.0"),
        ("PHARMA-ACEI-K-002", "pharmaco-interaction", "1.0.0"),
        ("PHARMA-QT-001", "pharmaco-interaction", "1.0.0"),
        ("PHARMA-QT-002", "pharmaco-interaction", "1.0.0"),
        ("PHARMA-QT-003", "pharmaco-interaction", "1.0.0"),
        ("PHARMA-SEROT-001", "pharmaco-interaction", "1.0.0"),
        ("PHARMA-SEROT-002", "pharmaco-interaction", "1.0.0"),
        ("PHARMA-POLY-001", "pharmaco-interaction", "1.0.0"),
        ("PHARMA-POLY-002", "pharmaco-interaction", "1.0.0"),
        ("PHARMA-ANTICOAG-001", "pharmaco-interaction", "1.0.0"),
        ("PHARMA-ANTICOAG-002", "pharmaco-interaction", "1.0.0"),
        ("PHARMA-NEPHRO-001", "pharmaco-interaction", "1.0.0"),
        ("PHARMA-NEPHRO-002", "pharmaco-interaction", "1.0.0"),
    ]

    neuro_alerts = [
        ("DELIR-CAM-001", "neuro-sedation", "1.0.0"),
        ("DELIR-CAM-002", "neuro-sedation", "1.0.0"),
        ("DELIR-CAM-003", "neuro-sedation", "1.0.0"),
        ("SED-RASS-001", "neuro-sedation", "1.0.0"),
        ("SED-RASS-002", "neuro-sedation", "1.0.0"),
        ("SED-RASS-003", "neuro-sedation", "1.0.0"),
        ("SED-RASS-004", "neuro-sedation", "1.0.0"),
        ("SED-SAT-001", "neuro-sedation", "1.0.0"),
        ("SED-SAT-002", "neuro-sedation", "1.0.0"),
        ("SED-ANALG-001", "neuro-sedation", "1.0.0"),
        ("SED-ANALG-002", "neuro-sedation", "1.0.0"),
        ("DELIR-RISK-001", "neuro-sedation", "1.0.0"),
        ("DELIR-RISK-002", "neuro-sedation", "1.0.0"),
        ("DELIR-RISK-003", "neuro-sedation", "1.0.0"),
    ]

    yaml_base = "docs/plan/_work/alerts"

    # Seed pharmaco alerts
    for alert_id, domain, version in pharmaco_alerts:
        op.execute(
            sa.text(
                "INSERT INTO alert_definition_version "
                "(tenant, alert_id, domain, version, yaml_path) "
                "VALUES (:tenant, :alert_id, :domain, :version, :yaml_path) "
                "ON CONFLICT (tenant, alert_id, version) DO NOTHING"
            ).bindparams(
                tenant="amh",
                alert_id=alert_id,
                domain=domain,
                version=version,
                yaml_path=f"{yaml_base}/pharmaco-interaction.yaml",
            )
        )

    # Seed neuro-sedation alerts
    for alert_id, domain, version in neuro_alerts:
        op.execute(
            sa.text(
                "INSERT INTO alert_definition_version "
                "(tenant, alert_id, domain, version, yaml_path) "
                "VALUES (:tenant, :alert_id, :domain, :version, :yaml_path) "
                "ON CONFLICT (tenant, alert_id, version) DO NOTHING"
            ).bindparams(
                tenant="amh",
                alert_id=alert_id,
                domain=domain,
                version=version,
                yaml_path=f"{yaml_base}/neuro-sedation.yaml",
            )
        )


def downgrade() -> None:
    # Forward-only: downgrade nao suportado nesta plataforma.
    raise NotImplementedError("migracoes sao forward-only (ADR-0011)")
