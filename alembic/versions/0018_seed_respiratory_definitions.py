"""Seed respiratory alert definitions — WO-029 (Rollout 2b)

Revision ID: 0018
Revises: 0012
Create Date: 2026-07-06 10:30:00.000000

Seeds 5 alert_definition_version entries for the respiratory domain:
  ALERT-RESP-ARDS-STAGING-01, ALERT-RESP-DETERIORATION-02,
  ALERT-RESP-ASYNCHRONY-03, ALERT-RESP-WEANING-READY-04,
  ALERT-RESP-PROLONGED-INTUB-05

FiO2 FRACTION enforced at every computation boundary (CANON_PINS / CON-SEED-12).
SpO2/FiO2 bands per Berlin Definition (ARDS Task Force, JAMA 2012).
Hybrid NRT+micro-batch evaluator. CRIT severity never auto-resolves.
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers
revision: str = "0018"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed 5 respiratory alert definition versions."""
    op.execute(
        """
        INSERT INTO alert_definition_version
            (definition_version, score_type, semver, spec_hash, description)
        VALUES
            ('ALERT-RESP-ARDS-STAGING-01-a1b2c3', 'ARDS_STAGING', '1.0.0',
             're01a1b2c3d4e5f6',
             'ALERT-RESP-ARDS-STAGING-01: SDRA — vigilancia e estadiamento de Berlin (S/F e P/F). '
             'Stage(leve, WATCH): S/F<=315; moderada(urgent): S/F<=235; grave(critical): S/F<=148. '
             'PF authoritative override when ABG present. Berlin Definition (JAMA 2012). '
             'FiO2 FRACTION enforced (CANON_PINS).'),
            ('ALERT-RESP-DETERIORATION-02-b2c3d4', 'VENT_DETERIORATION', '1.0.0',
             're02b2c3d4e5f6a7',
             'ALERT-RESP-DETERIORATION-02: Deterioracao ventilatoria — tendencia S/F e demanda de FiO2. '
             'DeltaS/F <= -20% in 6h OR FiO2 escalation > 30% without SpO2 improvement. '
             '>=2 sample persistence. Rice 2017. FiO2 FRACTION. severity=urgent.'),
            ('ALERT-RESP-ASYNCHRONY-03-c3d4e5', 'ASYNCHRONY', '1.0.0',
             're03c3d4e5f6a7b8',
             'ALERT-RESP-ASYNCHRONY-03: Assincronia paciente-ventilador. '
             'Spontaneous RR > set RR AND plateau > 30 cmH2O. '
             'Thille 2016 + Amato 2015. Degrades on absent plateau. severity=watch.'),
            ('ALERT-RESP-WEANING-READY-04-d4e5f6', 'WEANING_READY', '1.0.0',
             're04d4e5f6a7b8c9',
             'ALERT-RESP-WEANING-READY-04: Prontidao para desmame / extubacao. '
             'S/F>315 + PEEP<=8 + FiO2<=0.40 + RSBI<105 + RASS>=-2 + GCS>8 + '
             'vasopressor<=0.2 + days>=1. Boles 2007 + Yang/Tobin 1991. severity=normal.'),
            ('ALERT-RESP-PROLONGED-INTUB-05-e5f6a7', 'PROLONGED_INTUB', '1.0.0',
             're05e5f6a7b8c9d0',
             'ALERT-RESP-PROLONGED-INTUB-05: Intubacao prolongada — avaliar traqueostomia. '
             'TOT + days>10 (non-COVID) or >=14 (COVID active). '
             'Young/JAMA 2013 (TracMan) + AAO-HNS 2020. severity=watch.')
        ON CONFLICT (definition_version) DO NOTHING
        """
    )


def downgrade() -> None:
    """Remove respiratory alert definition seeds."""
    op.execute(
        """
        DELETE FROM alert_definition_version
        WHERE definition_version IN (
            'ALERT-RESP-ARDS-STAGING-01-a1b2c3',
            'ALERT-RESP-DETERIORATION-02-b2c3d4',
            'ALERT-RESP-ASYNCHRONY-03-c3d4e5',
            'ALERT-RESP-WEANING-READY-04-d4e5f6',
            'ALERT-RESP-PROLONGED-INTUB-05-e5f6a7'
        )
        """
    )
