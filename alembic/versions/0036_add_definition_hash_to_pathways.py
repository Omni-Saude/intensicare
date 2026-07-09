"""GAP C5 — Add definition_hash column to pathways table.

Revision ID: 0036
Revises: 0035
Create Date: 2026-07-09

Adds a SHA-256 content hash column for content-addressed pathway
definitions per ADR-020/ADR-021. The hash is computed from the
canonical JSON form of the YAML pathway definition and provides
immutable traceability for compiled definitions.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0036"
down_revision: Union[str, None] = "0035"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Idempotent column addition ────────────────────────────────────────
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'pathways'
                      AND column_name = 'definition_hash'
                ) THEN
                    ALTER TABLE pathways
                    ADD COLUMN definition_hash VARCHAR(128);
                END IF;
            END $$;
            """
        )
    )

    # ── Column comment ────────────────────────────────────────────────────
    op.execute(
        sa.text(
            "COMMENT ON COLUMN pathways.definition_hash IS "
            "'SHA-256 content hash of the compiled YAML pathway definition';"
        )
    )


def downgrade() -> None:
    op.drop_column("pathways", "definition_hash")
