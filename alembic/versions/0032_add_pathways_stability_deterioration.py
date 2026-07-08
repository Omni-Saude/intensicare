"""add pathways + stability_assessments + deterioration_assessments tables

Revision ID: 0032
Revises: 0031
Create Date: 2026-07-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "0032"
down_revision: Union[str, None] = "0031"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── pathways ───────────────────────────────────────────────────────────
    op.create_table(
        "pathways",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=True),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("states", postgresql.JSONB(), nullable=True,
                  comment="Array of PathwayState objects"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    # ── pathway_criteria ───────────────────────────────────────────────────
    op.create_table(
        "pathway_criteria",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=True),
        sa.Column("unit", sa.String(length=32), nullable=True),
        sa.Column("normal_range", sa.String(length=128), nullable=True),
        sa.Column("alert_threshold", sa.String(length=128), nullable=True),
        sa.Column("pathway_id", sa.BigInteger(),
                  sa.ForeignKey("pathways.id"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── patient_pathways ───────────────────────────────────────────────────
    op.create_table(
        "patient_pathways",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mpi_id", sa.String(length=64), nullable=False),
        sa.Column("pathway_id", sa.BigInteger(),
                  sa.ForeignKey("pathways.id"), nullable=False),
        sa.Column("current_state", sa.String(length=64), nullable=False),
        sa.Column("criteria_data", postgresql.JSONB(), nullable=True,
                  comment="Criteria evaluations array"),
        sa.Column("status", sa.String(length=16), nullable=False,
                  server_default="active"),
        sa.Column("severity", sa.String(length=16), nullable=True),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("enrolled_by", sa.String(length=255), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_patient_pathways_mpi_id"),
        "patient_pathways",
        ["mpi_id"],
        unique=False,
    )

    # ── pathway_state_transitions ──────────────────────────────────────────
    op.create_table(
        "pathway_state_transitions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("patient_pathway_id", sa.BigInteger(),
                  sa.ForeignKey("patient_pathways.id"), nullable=False),
        sa.Column("from_state", sa.String(length=64), nullable=False),
        sa.Column("to_state", sa.String(length=64), nullable=False),
        sa.Column("reason", sa.String(length=512), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── stability_assessments ──────────────────────────────────────────────
    op.create_table(
        "stability_assessments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mpi_id", sa.String(length=64), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False,
                  comment="0-27 criteria in warning/critical"),
        sa.Column("severity", sa.String(length=16), nullable=False,
                  comment="estavel, atencao, critico"),
        sa.Column("criteria", postgresql.JSONB(), nullable=False,
                  comment="27 StabilityCriterion dicts"),
        sa.Column("recommendation", sa.String(length=512), nullable=True),
        sa.Column("assessed_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_stability_assessments_mpi_id"),
        "stability_assessments",
        ["mpi_id"],
        unique=False,
    )

    # ── deterioration_assessments ──────────────────────────────────────────
    op.create_table(
        "deterioration_assessments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mpi_id", sa.String(length=64), nullable=False),
        sa.Column("score", sa.String(length=4), nullable=False,
                  comment="0, 1+, 1-, 3+, 3-"),
        sa.Column("trend", sa.String(length=16), nullable=False,
                  comment="improving, stable, worsening, none"),
        sa.Column("criteria", postgresql.JSONB(), nullable=False,
                  comment="DeteriorationCriteria dicts"),
        sa.Column("domains_affected", sa.Integer(), nullable=False,
                  server_default="0"),
        sa.Column("recommendation", sa.String(length=512), nullable=True),
        sa.Column("assessed_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("assessed_by", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_deterioration_assessments_mpi_id"),
        "deterioration_assessments",
        ["mpi_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("deterioration_assessments")
    op.drop_index(
        op.f("ix_stability_assessments_mpi_id"),
        table_name="stability_assessments",
    )
    op.drop_table("stability_assessments")
    op.drop_table("pathway_state_transitions")
    op.drop_index(
        op.f("ix_patient_pathways_mpi_id"),
        table_name="patient_pathways",
    )
    op.drop_table("patient_pathways")
    op.drop_table("pathway_criteria")
    op.drop_table("pathways")
