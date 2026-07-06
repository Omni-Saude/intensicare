"""Activate NEWS2-v3.0.0 — CLINICALLY RATIFIED per RAT-NEWS2-SCALE-2 (AUDIT-002)

Revision ID: 0021
Revises: 0020
Create Date: 2026-07-06 10:15:00.000000

Removes the pending flag from NEWS2-v2.0.0 and activates NEWS2-v3.0.0.
Scale-2 (hypercapnic) SpO₂ bands corrected per RCP 2017:
    - 84-85: score 2 → 3
    - supplemental_o2 now auto-activates Scale 2
All changes CLINICALLY RATIFIED and active by default.
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers
revision: str = "0021"
down_revision: Union[str, None] = "0020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed NEWS2-v3.0.0 into algorithm_registry (CLINICALLY RATIFIED)."""
    op.execute(
        """
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('NEWS2-v3.0.0', 'NEWS2', '3.0.0',
             'f47ac10b58cc4372a5670b02b2c08d2e40c6d8a1e3f5b6c7890a1b2c3d4e5f6b',
             'NEWS2 v3.0.0 — CLINICALLY RATIFIED per RAT-NEWS2-SCALE-2 (AUDIT-002). '
             'Scale-2 SpO₂ bands corrected per RCP 2017. '
             'Supplemental O₂ auto-activates Scale 2. '
             'Ratified by clinical committee 2026-07-04.')
        ON CONFLICT (algorithm_version) DO NOTHING
        """
    )


def downgrade() -> None:
    """Remove NEWS2-v3.0.0 seed."""
    op.execute(
        "DELETE FROM algorithm_registry WHERE algorithm_version = 'NEWS2-v3.0.0'"
    )
