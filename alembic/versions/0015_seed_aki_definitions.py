"""Seed AKI alert definitions — WO-025 (Rollout 2a)

Revision ID: 0015
Revises: 0012
Create Date: 2026-07-05 21:30:00.000000

Seeds 3 alert_definition_version entries for the AKI domain:
  ALERT-AKI-KDIGO-STAGE-01, ALERT-AKI-PROGRESSION-02,
  ALERT-AKI-NEPHROTOXIN-03

KDIGO 2012 staging engine. CRIT severity never auto-resolves.
Micro-batch evaluator (~1-2 min poll).
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers
revision: str = "0015"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed 3 AKI alert definition versions."""
    op.execute(
        """
        INSERT INTO alert_definition_version
            (definition_version, score_type, semver, spec_hash, description)
        VALUES
            ('ALERT-AKI-KDIGO-STAGE-01-a1b2c3', 'KDIGO_STAGE', '1.0.0',
             'a1b2c3d4e5f6a7b8',
             'ALERT-AKI-KDIGO-STAGE-01: Lesao renal aguda — estadiamento KDIGO. '
             'Stage 1→watch, stage 2→urgent, stage 3→critical. '
             'max(stage_cr, stage_uo). Boundary: Cr≥1.5× inclusive; UO<0.5 strict. '
             'KDIGO 2012 Clinical Practice Guideline for AKI, '
             'Kidney Int Suppl 2012;2(1):1-138.'),
            ('ALERT-AKI-PROGRESSION-02-b2c3d4', 'KDIGO_PROGRESSION', '1.0.0',
             'b2c3d4e5f6a7b8c9',
             'ALERT-AKI-PROGRESSION-02: Progressao de LRA — mudanca de estagio KDIGO em 24h. '
             'Fires when stage_now > stage_24h_ago. Severity=urgent, escalated to '
             'critical when new stage==3. Null-prior-stage guard. '
             'KDIGO 2012 (dynamic staging).'),
            ('ALERT-AKI-NEPHROTOXIN-03-c3d4e5', 'NEPHROTOXIN', '1.0.0',
             'c3d4e5f6a7b8c9d0',
             'ALERT-AKI-NEPHROTOXIN-03: Risco de nefrotoxicidade aditiva com '
             'creatinina em elevacao. rising_cr (>baseline+0.2 strict) AND '
             'nephrotoxic_combo (vanco+amino, vanco+contraste, amino+aine, '
             'ieca+hipovolemia). Severity=watch. KDIGO Drug-Induced AKI 2023.')
        ON CONFLICT (definition_version) DO NOTHING
        """
    )


def downgrade() -> None:
    """Remove AKI alert definition seeds."""
    op.execute(
        """
        DELETE FROM alert_definition_version
        WHERE definition_version IN (
            'ALERT-AKI-KDIGO-STAGE-01-a1b2c3',
            'ALERT-AKI-PROGRESSION-02-b2c3d4',
            'ALERT-AKI-NEPHROTOXIN-03-c3d4e5'
        )
        """
    )
