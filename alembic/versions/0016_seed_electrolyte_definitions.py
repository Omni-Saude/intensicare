"""Seed electrolyte alert definitions — WO-026 (Rollout 2a)

Revision ID: 0016
Revises: 0012
Create Date: 2026-07-05 22:00:00.000000

Seeds 6 alert_definition_version entries for the electrolyte domain:
  ALERT-ELY-POTASSIUM-01, ALERT-ELY-SODIUM-01,
  ALERT-ELY-SODIUM-CORRECTION-02, ALERT-ELY-CALCIUM-01,
  ALERT-ELY-MAGNESIUM-01, ALERT-ELY-PHOSPHATE-01

CRITICAL: CRIT severity never auto-resolves on stale data.
Expedited ~1-2 min poll micro-batch.
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers
revision: str = "0016"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed 6 electrolyte alert definition versions."""
    op.execute(
        """
        INSERT INTO alert_definition_version
            (definition_version, score_type, semver, spec_hash, description)
        VALUES
            ('ALERT-ELY-POTASSIUM-01-a1b2c3', 'POTASSIUM', '1.0.0',
             'a1b2c3d4e5f6a7b8',
             'ALERT-ELY-POTASSIUM-01: Distúrbio grave do potássio — '
             'hipercalemia (>6.5 crit, >6.0 urg, >5.5+cofatores watch) / '
             'hipocalemia (<2.5 crit, <3.0 urg, <3.5+cofatores watch). '
             'Digoxin toxicity pairing. Per vision §3.6 VIS-3.6-02/03.'),
            ('ALERT-ELY-SODIUM-01-b2c3d4', 'SODIUM', '1.0.0',
             'b2c3d4e5f6a7b8c9',
             'ALERT-ELY-SODIUM-01: Distúrbio grave do sódio — '
             'hipernatremia (>160 crit, >155 urg, >150+delta>5 watch) / '
             'hiponatremia (<120 crit, <125 urg, <130+delta<=-5 watch). '
             'Glucose correction. Per vision §3.6 VIS-3.6-04/05.'),
            ('ALERT-ELY-SODIUM-CORRECTION-02-c3d4e5', 'SODIUM_CORRECTION', '1.0.0',
             'c3d4e5f6a7b8c9d0',
             'ALERT-ELY-SODIUM-CORRECTION-02: Velocidade de correção do sódio — '
             'risco de desmielinização osmótica. '
             'Usa correcao_na_24h_from_nadir. >10 crit, >8 urg. '
             'HAZ-031/032. Per vision §3.6 VIS-3.6-06.'),
            ('ALERT-ELY-CALCIUM-01-d4e5f6', 'CALCIUM', '1.0.0',
             'd4e5f6a7b8c9d0e1',
             'ALERT-ELY-CALCIUM-01: Distúrbio grave do cálcio iônico — '
             'hipocalcemia (iCa<0.80 crit, <0.90 urg) / '
             'hipercalcemia (iCa>1.60 crit, >1.45 urg). '
             'Corrected total Ca fallback. Per vision §3.6 VIS-3.6-07/08.'),
            ('ALERT-ELY-MAGNESIUM-01-e5f6a7', 'MAGNESIUM', '1.0.0',
             'e5f6a7b8c9d0e1f2',
             'ALERT-ELY-MAGNESIUM-01: Hipomagnesemia grave — '
             '<0.5 crit, <0.7 urg, <0.9+K<3.5 ou QTc>500 watch. '
             'Per vision §3.6 VIS-3.6-09.'),
            ('ALERT-ELY-PHOSPHATE-01-f6a7b8', 'PHOSPHATE', '1.0.0',
             'f6a7b8c9d0e1f2a3',
             'ALERT-ELY-PHOSPHATE-01: Distúrbio grave do fosfato — '
             'hipofosfatemia (<1.0 crit, <1.5 urg) / '
             'hiperfosfatemia (>7.0 watch, capped). '
             'Pending RAT-ELY-01. Per vision §3.6 VIS-3.6-10.')
        ON CONFLICT (definition_version) DO NOTHING
        """
    )


def downgrade() -> None:
    """Remove electrolyte alert definition seeds."""
    op.execute(
        """
        DELETE FROM alert_definition_version
        WHERE definition_version IN (
            'ALERT-ELY-POTASSIUM-01-a1b2c3',
            'ALERT-ELY-SODIUM-01-b2c3d4',
            'ALERT-ELY-SODIUM-CORRECTION-02-c3d4e5',
            'ALERT-ELY-CALCIUM-01-d4e5f6',
            'ALERT-ELY-MAGNESIUM-01-e5f6a7',
            'ALERT-ELY-PHOSPHATE-01-f6a7b8'
        )
        """
    )
