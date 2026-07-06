"""add vital_sign natural key (mpi_id, recorded_at, source_system)

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-05 10:00:00.000000

Gold-poll natural key: UNIQUE (mpi_id, recorded_at, source_system) garante
que um mesmo conjunto de sinais vitais da mesma origem no mesmo instante
não seja duplicado. Inclui recorded_at (partition key) para compatibilidade
com TimescaleDB hypertable constraints.

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers
revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_vital_sign_natural_key",
        "vital_sign",
        ["mpi_id", "recorded_at", "source_system"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_vital_sign_natural_key", "vital_sign", type_="unique")
