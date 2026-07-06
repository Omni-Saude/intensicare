"""algorithm_registry + clinical_score.algorithm_version NOT NULL + FK (INV-3 / WO-003)

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-05 15:00:00.000000

Creates immutable algorithm_registry table, seeds current scorer versions,
backfills legacy clinical_score rows, and enforces NOT NULL + FK constraint.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Current scorer versions (must match the constants in services/*.py)
SEED_VERSIONS = [
    {
        "algorithm_version": "MEWS-v1.0",
        "score_type": "MEWS",
        "semver": "1.0.0",
        "spec_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "description": "MEWS (Modified Early Warning Score) v1.0 — Subbe et al., QJM 2001;94:521-526",
    },
    {
        "algorithm_version": "NEWS2-v1.0",
        "score_type": "NEWS2",
        "semver": "1.0.0",
        "spec_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "description": "NEWS2 (National Early Warning Score 2) v1.0 — RCP 2017",
    },
    {
        "algorithm_version": "SOFA-v1.0",
        "score_type": "SOFA",
        "semver": "1.0.0",
        "spec_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "description": "SOFA (Sequential Organ Failure Assessment) v1.0 — Vincent et al., ICM 1996;22:707-710",
    },
    {
        "algorithm_version": "qSOFA-v1.0",
        "score_type": "qSOFA",
        "semver": "1.0.0",
        "spec_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "description": "qSOFA (Quick SOFA) v1.0 — Singer et al., Sepsis-3, JAMA 2016;315:801-810",
    },
]


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Create algorithm_registry table (immutable reference table)
    # ------------------------------------------------------------------
    op.create_table(
        "algorithm_registry",
        sa.Column("algorithm_version", sa.String(32), nullable=False),
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
        sa.PrimaryKeyConstraint("algorithm_version"),
        sa.UniqueConstraint("score_type", "semver"),
    )

    # ------------------------------------------------------------------
    # 2. Seed current scorer versions
    # ------------------------------------------------------------------
    for v in SEED_VERSIONS:
        op.execute(
            f"""
            INSERT INTO algorithm_registry
                (algorithm_version, score_type, semver, spec_hash, description)
            VALUES
                ('{v['algorithm_version']}', '{v['score_type']}', '{v['semver']}',
                 '{v['spec_hash']}', '{v['description']}')
            ON CONFLICT (algorithm_version) DO NOTHING
            """
        )

    # ------------------------------------------------------------------
    # 3. Backfill legacy clinical_score rows
    #    Derive algorithm_version from score_type: "{score_type}@0.0.0"
    # ------------------------------------------------------------------
    op.execute(
        """
        UPDATE clinical_score
           SET algorithm_version = score_type || '@0.0.0'
         WHERE algorithm_version IS NULL
        """
    )

    # ------------------------------------------------------------------
    # 4. Make algorithm_version NOT NULL
    # ------------------------------------------------------------------
    op.alter_column(
        "clinical_score",
        "algorithm_version",
        existing_type=sa.String(32),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # 5. Add FK constraint
    # ------------------------------------------------------------------
    op.create_foreign_key(
        "fk_score_algorithm",
        "clinical_score",
        "algorithm_registry",
        ["algorithm_version"],
        ["algorithm_version"],
    )


def downgrade() -> None:
    # 1. Drop FK
    op.drop_constraint("fk_score_algorithm", "clinical_score", type_="foreignkey")

    # 2. Make algorithm_version nullable again
    op.alter_column(
        "clinical_score",
        "algorithm_version",
        existing_type=sa.String(32),
        nullable=True,
    )

    # 3. Revert backfill (set legacy back to NULL)
    op.execute(
        """
        UPDATE clinical_score
           SET algorithm_version = NULL
         WHERE algorithm_version LIKE '%@0.0.0'
        """
    )

    # 4. Drop algorithm_registry table
    op.drop_table("algorithm_registry")
