"""Sprint-1 Patient Safety — Anti-duplicate enrollment unique index.

Revision ID: 0037
Revises: 0036
Create Date: 2026-07-12

Adds a partial unique index on patient_pathways(mpi_id, pathway_id)
scoped to status = 'active'. Prevents a patient from being enrolled
more than once in the same active pathway (double-enrollment bug
that fans out duplicate alerts/tasks for the same clinical episode).

A patient may still be re-enrolled in the same pathway after the
previous enrollment is completed/discontinued, since the index only
covers rows where status = 'active'.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0037"
down_revision: Union[str, None] = "0036"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Idempotent partial unique index ────────────────────────────────────
    op.execute(
        sa.text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_active_enrollment
            ON patient_pathways (mpi_id, pathway_id)
            WHERE status = 'active';
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP INDEX IF EXISTS uq_active_enrollment;"))
