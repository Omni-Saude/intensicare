"""Activate MEWS-v2.0.0 — CLINICALLY RATIFIED per RAT-MEWS-SUBBE-2001 (AUDIT-001)

Revision ID: 0020
Revises: 0019
Create Date: 2026-07-06 10:00:00.000000

Removes the pending flag from MEWS-v1.0.1 and activates MEWS-v2.0.0.
All Subbe 2001 corrected bands (HR ≤40:2, 41-50:1, RR ≤8:2, Temp ≤35.0:2)
are now CLINICALLY RATIFIED and active by default.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0020"
down_revision: Union[str, None] = "0019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed MEWS-v2.0.0 into algorithm_registry (CLINICALLY RATIFIED)."""
    op.execute(
        """
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('MEWS-v2.0.0', 'MEWS', '2.0.0',
             'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
             'MEWS v2.0.0 — CLINICALLY RATIFIED per RAT-MEWS-SUBBE-2001 (AUDIT-001). '
             'Subbe et al., QJM 2001;94:521-526 with corrected bands: '
             'HR ≤40:2, 41-50:1, RR ≤8:2, Temp ≤35.0:2.')
        ON CONFLICT (algorithm_version) DO NOTHING
        """
    )


def downgrade() -> None:
    """Remove MEWS-v2.0.0 seed."""
    op.execute(
        "DELETE FROM algorithm_registry WHERE algorithm_version = 'MEWS-v2.0.0'"
    )
