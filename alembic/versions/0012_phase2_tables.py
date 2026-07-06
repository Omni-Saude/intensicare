"""Phase-2 hot-cache tables: lab_result hypertable + medication_order/administration.

Revision ID: 0012
Revises: 0011
Create Date: 2026-07-05 23:30:00.000000

- lab_result: TimescaleDB hypertable on collected_at
  UNIQUE (fhir_id, collected_at) for idempotency
- medication_order: FK → patient_cache.mpi_id
- medication_administration: FK → patient_cache.mpi_id + FK → medication_order.id
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. lab_result (TimescaleDB hypertable on collected_at)
    # ------------------------------------------------------------------
    op.create_table(
        "lab_result",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mpi_id", sa.String(64), nullable=False),
        sa.Column("fhir_id", sa.String(128), nullable=False),
        sa.Column("loinc_code", sa.String(32), nullable=True),
        sa.Column("analyte", sa.String(255), nullable=True),
        sa.Column("value_num", sa.Float(), nullable=True),
        sa.Column("value_unit", sa.String(32), nullable=True),
        sa.Column("reference_low", sa.Float(), nullable=True),
        sa.Column("reference_high", sa.Float(), nullable=True),
        sa.Column("abnormal_flag", sa.String(16), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resulted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_system", sa.String(32), nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", "collected_at"),
        sa.UniqueConstraint("fhir_id", "collected_at", name="uq_lab_result_fhir_id_collected"),
    )
    op.create_index("ix_lab_result_mpi_id", "lab_result", ["mpi_id"])
    # TimescaleDB hypertable
    op.execute(
        "SELECT create_hypertable('lab_result', 'collected_at', if_not_exists => true)"
    )

    # ------------------------------------------------------------------
    # 2. medication_order
    # ------------------------------------------------------------------
    op.create_table(
        "medication_order",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mpi_id", sa.String(64), nullable=False),
        sa.Column("fhir_id", sa.String(128), nullable=False),
        sa.Column("medication_name", sa.String(255), nullable=True),
        sa.Column("dose", sa.String(64), nullable=True),
        sa.Column("route", sa.String(64), nullable=True),
        sa.Column("frequency", sa.String(64), nullable=True),
        sa.Column("ordered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_medication_order_mpi_id", "medication_order", ["mpi_id"])
    op.create_foreign_key(
        "fk_medication_order_patient_cache",
        "medication_order",
        "patient_cache",
        ["mpi_id"],
        ["mpi_id"],
        ondelete="CASCADE",
    )

    # ------------------------------------------------------------------
    # 3. medication_administration
    # ------------------------------------------------------------------
    op.create_table(
        "medication_administration",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mpi_id", sa.String(64), nullable=False),
        sa.Column("fhir_id", sa.String(128), nullable=False),
        sa.Column("order_id", sa.BigInteger(), nullable=True),
        sa.Column("administered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dose_given", sa.String(64), nullable=True),
        sa.Column("route", sa.String(64), nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_medication_administration_mpi_id", "medication_administration", ["mpi_id"])
    op.create_index(
        "ix_medication_administration_order_id",
        "medication_administration",
        ["order_id"],
    )
    op.create_foreign_key(
        "fk_medication_administration_patient_cache",
        "medication_administration",
        "patient_cache",
        ["mpi_id"],
        ["mpi_id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_medication_administration_order",
        "medication_administration",
        "medication_order",
        ["order_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_medication_administration_order",
        "medication_administration",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_medication_administration_patient_cache",
        "medication_administration",
        type_="foreignkey",
    )
    op.drop_index("ix_medication_administration_order_id", "medication_administration")
    op.drop_index("ix_medication_administration_mpi_id", "medication_administration")
    op.drop_table("medication_administration")

    op.drop_constraint(
        "fk_medication_order_patient_cache",
        "medication_order",
        type_="foreignkey",
    )
    op.drop_index("ix_medication_order_mpi_id", "medication_order")
    op.drop_table("medication_order")

    op.drop_index("ix_lab_result_mpi_id", "lab_result")
    op.drop_table("lab_result")
