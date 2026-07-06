"""Seed NEWS2-v2.0.0 — Scale-2 SpO₂ boundary correction (WO-013 / AUDIT-002)

Revision ID: 0008
Revises: 0007
Create Date: 2026-07-05 18:00:00.000000

Seeds the corrected NEWS2-v2.0.0 algorithm version into algorithm_registry.
Scale-2 (hypercapnic) SpO₂ bands corrected per RCP 2017:
    - 84-85: score 2 → 3
    - supplemental_o2 now auto-activates Scale 2

Pending: RAT-NEWS2-SCALE-2 (AUDIT-002) — clinical sign-off required
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers
revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('NEWS2-v2.0.0', 'NEWS2', '2.0.0',
             'f47ac10b58cc4372a5670b02b2c08d2e40c6d8a1e3f5b6c7890a1b2c3d4e5f6a',
             'NEWS2 v2.0.0 — Scale-2 SpO₂ bands corrected per RCP 2017 (AUDIT-002). '
             'Supplemental O₂ auto-activates Scale 2. '
             'Pending RAT-NEWS2-SCALE-2 clinical sign-off.')
        ON CONFLICT (algorithm_version) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM algorithm_registry WHERE algorithm_version = 'NEWS2-v2.0.0'"
    )
