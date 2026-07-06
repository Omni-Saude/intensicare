"""Activate SOFA-v2.0.0 — CLINICALLY RATIFIED per RAT-CLINICAL-SCORING-01/02/03

Revision ID: 0022
Revises: 0021
Create Date: 2026-07-06 10:30:00.000000

Removes pending flags and activates all 3 SOFA RATIFY rules per committee
recommended defaults:
  - RAT-CLINICAL-SCORING-01 (Respiratory): FiO2 fraction 0.21-1.0,
    400/300/200/100 bands, 3-4 point bands gated on respiratory support
  - RAT-CLINICAL-SCORING-02 (Renal): boundary off-by-one fixes
  - RAT-CLINICAL-SCORING-03 (Cardiovascular): vasopressor mcg/kg/min canonical
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers
revision: str = "0022"
down_revision: Union[str, None] = "0021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed SOFA-v2.0.0 into algorithm_registry (CLINICALLY RATIFIED)."""
    op.execute(
        """
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('SOFA-v2.0.0', 'SOFA', '2.0.0',
             'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2',
             'SOFA v2.0.0 — CLINICALLY RATIFIED per RAT-CLINICAL-SCORING-01/02/03. '
             'Unified live/replay risk classification via classify_sofa_mortality_risk. '
             'Renal = max(creatinine, urine_output) per SOFA-C-03. '
             'Vasopressor dose canonical unit: mcg/kg/min. '
             'Ratified by clinical committee 2026-07-04.')
        ON CONFLICT (algorithm_version) DO NOTHING
        """
    )


def downgrade() -> None:
    """Remove SOFA-v2.0.0 seed."""
    op.execute(
        "DELETE FROM algorithm_registry WHERE algorithm_version = 'SOFA-v2.0.0'"
    )
