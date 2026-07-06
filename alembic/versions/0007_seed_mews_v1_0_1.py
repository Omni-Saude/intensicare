"""Seed MEWS-v1.0.1 with Subbe 2001 corrected bands (AUDIT-001 / WO-012)

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-05 16:00:00.000000

Seeds the corrected MEWS-v1.0.1 algorithm version into algorithm_registry.
Pending RAT-MEWS-SUBBE-2001 (AUDIT-001) — clinical sign-off required.
Bands corrected: HR ≤40:3→2, HR 41-50:2→1, RR ≤8:3→2, Temp ≤35.0:3→2.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# pending RAT-MEWS-SUBBE-2001 (AUDIT-001) — clinical sign-off required
MEWS_V1_0_1 = {
    "algorithm_version": "MEWS-v1.0.1",
    "score_type": "MEWS",
    "semver": "1.0.1",
    "spec_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "description": (
        "MEWS (Modified Early Warning Score) v1.0.1 — Subbe et al., QJM 2001;94:521-526 "
        "[CORRECTED per AUDIT-001: HR ≤40:2, 41-50:1, RR ≤8:2, Temp ≤35.0:2] "
        "PENDING clinical sign-off (RAT-MEWS-SUBBE-2001)"
    ),
}


def upgrade() -> None:
    """Seed MEWS-v1.0.1 into algorithm_registry."""
    v = MEWS_V1_0_1
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


def downgrade() -> None:
    """Remove MEWS-v1.0.1 seed."""
    op.execute(
        "DELETE FROM algorithm_registry WHERE algorithm_version = 'MEWS-v1.0.1'"
    )
