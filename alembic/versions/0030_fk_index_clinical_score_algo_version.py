"""Add FK index on clinical_score.algorithm_version

Revision ID: 0030
Revises: 0029
Create Date: 2026-07-06 20:00:00.000000

Adds an explicit index on clinical_score.algorithm_version to improve
join performance with algorithm_registry and foreign-key lookups.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers
revision: str = "0030"
down_revision: Union[str, None] = "0029"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create index on clinical_score.algorithm_version."""
    op.create_index(
        "ix_clinical_score_algorithm_version",
        "clinical_score",
        ["algorithm_version"],
    )


def downgrade() -> None:
    """Drop the index."""
    op.drop_index(
        "ix_clinical_score_algorithm_version",
        table_name="clinical_score",
    )
