"""add_patient_location_current_and_discharge_summary

Revision ID: 35c5eebda2c7
Revises: 0035
Create Date: 2026-07-09 09:27:41.021098

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "35c5eebda2c7"
down_revision: Union[str, None] = "0035"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Add encounter_id to admission_episodes ──
    op.add_column(
        "admission_episodes",
        sa.Column(
            "encounter_id",
            sa.String(64),
            nullable=True,  # nullable initially for existing rows
            comment="External encounter identifier (e.g., from AMH Gold)",
        ),
    )
    op.create_unique_constraint(
        "uq_admission_episodes_encounter_id",
        "admission_episodes",
        ["encounter_id"],
    )
    # Make NOT NULL after unique constraint (existing rows may need backfill)
    op.alter_column(
        "admission_episodes",
        "encounter_id",
        existing_type=sa.String(64),
        nullable=False,
    )

    # ── 2. Create patient_location_current table ──
    op.create_table(
        "patient_location_current",
        sa.Column(
            "mpi_id",
            sa.String(64),
            primary_key=True,
            comment="One row per admitted patient",
        ),
        sa.Column(
            "encounter_id",
            sa.String(64),
            sa.ForeignKey("admission_episodes.encounter_id"),
            nullable=False,
            comment="Current admission episode",
        ),
        sa.Column(
            "unit",
            sa.String(64),
            nullable=False,
            comment="Current unit (e.g., UTI-1)",
        ),
        sa.Column(
            "bed_id",
            sa.String(32),
            nullable=True,
            comment="Current bed (e.g., L-101)",
        ),
        sa.Column(
            "specialty",
            sa.String(64),
            nullable=True,
            comment="Responsible clinical specialty",
        ),
        sa.Column(
            "admitted_to_unit_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="When patient arrived at current unit",
        ),
        sa.Column(
            "last_movement_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp of most recent movement",
        ),
        sa.Column(
            "source_cdc_offset",
            sa.BigInteger(),
            nullable=True,
            comment="CDC offset of the latest event applied",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            comment="Last update timestamp",
        ),
    )
    op.create_index(
        "ix_plc_unit_bed",
        "patient_location_current",
        ["unit", "bed_id"],
    )
    op.create_index(
        "ix_plc_unit",
        "patient_location_current",
        ["unit"],
    )
    op.create_index(
        "ix_plc_specialty",
        "patient_location_current",
        ["specialty"],
    )

    # ── 3. Create discharge_summaries table ──
    op.create_table(
        "discharge_summaries",
        sa.Column(
            "id",
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "encounter_id",
            sa.String(64),
            sa.ForeignKey("admission_episodes.encounter_id"),
            unique=True,
            nullable=False,
            comment="One row per discharge (unique encounter)",
        ),
        sa.Column(
            "mpi_id",
            sa.String(64),
            nullable=False,
            comment="Patient MPI identifier",
        ),
        sa.Column(
            "discharge_datetime",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Discharge date/time",
        ),
        sa.Column(
            "discharge_type",
            sa.String(32),
            nullable=False,
            comment="domiciliar, transferencia_hospitalar, obito, alta_pedido, evasao",
        ),
        sa.Column(
            "destination",
            sa.String(128),
            nullable=True,
            comment="Post-discharge destination",
        ),
        sa.Column(
            "discharge_diagnosis",
            sa.String(16),
            nullable=True,
            comment="CID-10 at discharge",
        ),
        sa.Column(
            "follow_up_scheduled",
            sa.Boolean(),
            server_default=sa.text("false"),
            comment="Whether follow-up was scheduled",
        ),
        sa.Column(
            "continuity_medication_prescribed",
            sa.Boolean(),
            server_default=sa.text("false"),
            comment="Medication continuity at discharge",
        ),
        sa.Column(
            "source_cdc_offset",
            sa.BigInteger(),
            nullable=True,
            comment="CDC offset of source event",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            comment="Record creation timestamp",
        ),
    )
    op.create_index(
        "ix_ds_mpi_dt",
        "discharge_summaries",
        ["mpi_id", "discharge_datetime"],
    )
    op.create_index(
        "ix_ds_discharge_dt",
        "discharge_summaries",
        ["discharge_datetime"],
    )
    op.create_index(
        "ix_ds_followup_dt",
        "discharge_summaries",
        ["follow_up_scheduled", "discharge_datetime"],
    )


def downgrade() -> None:
    # ── 3. Drop discharge_summaries ──
    op.drop_index("ix_ds_followup_dt", table_name="discharge_summaries")
    op.drop_index("ix_ds_discharge_dt", table_name="discharge_summaries")
    op.drop_index("ix_ds_mpi_dt", table_name="discharge_summaries")
    op.drop_table("discharge_summaries")

    # ── 2. Drop patient_location_current ──
    op.drop_index("ix_plc_specialty", table_name="patient_location_current")
    op.drop_index("ix_plc_unit", table_name="patient_location_current")
    op.drop_index("ix_plc_unit_bed", table_name="patient_location_current")
    op.drop_table("patient_location_current")

    # ── 1. Remove encounter_id from admission_episodes ──
    op.drop_constraint(
        "uq_admission_episodes_encounter_id",
        "admission_episodes",
        type_="unique",
    )
    op.drop_column("admission_episodes", "encounter_id")
