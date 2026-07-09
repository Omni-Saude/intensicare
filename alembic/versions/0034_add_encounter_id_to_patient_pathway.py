"""GAP C4 — Add encounter_id, bed_id, unit to patient_pathways table.

Revision ID: 0034
Revises: 0033
Create Date: 2026-07-09

Creates the patient_pathways table (if it does not yet exist) with all
columns including the new encounter_id, bed_id, and unit fields.
Uses idempotent SQL so it is safe to run on environments where the table
already exists (only adds missing columns).

FK to pathways.id is omitted here because the pathways table may not
exist yet in all environments; the application manages the relationship
at the ORM level.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers
revision: str = "0034"
down_revision: Union[str, None] = "0033"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Create patient_pathways if it doesn't exist ────────────────────────
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS patient_pathways (
                id BIGSERIAL NOT NULL,
                mpi_id VARCHAR(64) NOT NULL,
                encounter_id VARCHAR(64) NOT NULL DEFAULT '',
                bed_id VARCHAR(32),
                unit VARCHAR(64),
                pathway_id BIGINT NOT NULL,
                current_state VARCHAR(64) NOT NULL,
                criteria_data JSONB,
                status VARCHAR(16) NOT NULL DEFAULT 'active',
                severity VARCHAR(16),
                enrolled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                enrolled_by VARCHAR(255),
                completed_at TIMESTAMPTZ,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                PRIMARY KEY (id)
            );
            """
        )
    )

    # ── Idempotent column additions (for envs where table existed from 0032) ─
    for col_name, col_type, col_default, col_null, col_comment in [
        ("encounter_id", "VARCHAR(64)", "''", "NOT NULL",
         "Admission identifier from AMH Gold"),
        ("bed_id", "VARCHAR(32)", None, "NULL",
         "Current bed at time of enrollment"),
        ("unit", "VARCHAR(64)", None, "NULL",
         "Current unit at time of enrollment"),
    ]:
        default_clause = f" DEFAULT {col_default}" if col_default else ""
        op.execute(
            sa.text(
                f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'patient_pathways'
                          AND column_name = '{col_name}'
                    ) THEN
                        ALTER TABLE patient_pathways
                        ADD COLUMN {col_name} {col_type} {col_null}{default_clause};
                    END IF;
                END $$;
                """
            )
        )
        if col_comment:
            op.execute(
                sa.text(
                    f"COMMENT ON COLUMN patient_pathways.{col_name} "
                    f"IS '{col_comment}';"
                )
            )

    # ── Idempotent index creation ──────────────────────────────────────────
    for idx_name, col in [
        ("ix_patient_pathways_mpi_id", "mpi_id"),
        ("ix_patient_pathways_encounter_id", "encounter_id"),
    ]:
        op.execute(
            sa.text(
                f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes
                        WHERE indexname = '{idx_name}'
                    ) THEN
                        CREATE INDEX {idx_name}
                        ON patient_pathways ({col});
                    END IF;
                END $$;
                """
            )
        )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_patient_pathways_encounter_id"),
        table_name="patient_pathways",
    )
    op.drop_index(
        op.f("ix_patient_pathways_mpi_id"),
        table_name="patient_pathways",
    )
    op.drop_column("patient_pathways", "unit")
    op.drop_column("patient_pathways", "bed_id")
    op.drop_column("patient_pathways", "encounter_id")
    op.drop_table("patient_pathways")
