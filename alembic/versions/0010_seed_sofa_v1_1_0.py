"""Seed SOFA-v1.1.0 — Unified risk classification + renal=max(cr,uo) (WO-014 / AUDIT-003)

Revision ID: 0010
Revises: 0009
Create Date: 2026-07-05 20:00:00.000000

Seeds the SOFA-v1.1.0 algorithm version into algorithm_registry.
Changes from v1.0:
- Unified live vs replay risk classification (classify_sofa_mortality_risk)
- Renal score = max(creatinine_score, urine_output_score) per SOFA-C-03
- Vasopressor rate mcg/kg/min pending RAT-CLINICAL-SCORING-*/ASK-5
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers
revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed SOFA-v1.1.0 into algorithm_registry."""
    op.execute(
        """
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('SOFA-v1.1.0', 'SOFA', '1.1.0',
             'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2',
             'SOFA v1.1.0 — Unified live/replay risk classification via '
             'classify_sofa_mortality_risk. Renal = max(creatinine, urine_output) '
             'per SOFA-C-03. Vasopressor rate mcg/kg/min pending '
             'RAT-CLINICAL-SCORING-*/ASK-5 (AUDIT-003 / WO-014).')
        ON CONFLICT (algorithm_version) DO NOTHING
        """
    )


def downgrade() -> None:
    """Remove SOFA-v1.1.0 seed."""
    op.execute(
        "DELETE FROM algorithm_registry WHERE algorithm_version = 'SOFA-v1.1.0'"
    )
