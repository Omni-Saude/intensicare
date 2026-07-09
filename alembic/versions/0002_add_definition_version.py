"""add definition_version to clinical_form_submissions

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-09 10:00:00.000000

Adiciona coluna definition_version (String(32)) à tabela clinical_form_submissions
para suportar versionamento de schema de formulários clínicos (H9).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona coluna definition_version à tabela clinical_form_submissions."""
    op.add_column(
        "clinical_form_submissions",
        sa.Column(
            "definition_version",
            sa.String(32),
            nullable=True,
            comment="Form schema version (e.g., 'rass-v1.0')",
        ),
    )


def downgrade() -> None:
    """Remove coluna definition_version da tabela clinical_form_submissions."""
    op.drop_column("clinical_form_submissions", "definition_version")
