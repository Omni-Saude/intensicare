"""add role column to users for granular RBAC

Revision ID: 0035
Revises: 0034
Create Date: 2026-07-09

GAP C7 — Adds role column to users table with clinical role options:
admin, medico, enfermeiro, fisioterapeuta, farmacia, nutricao, readonly.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0035"
down_revision: Union[str, None] = "0034"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(32),
            nullable=False,
            server_default="readonly",
            comment=(
                "Clinical role: admin, medico, enfermeiro, "
                "fisioterapeuta, farmacia, nutricao, readonly"
            ),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
