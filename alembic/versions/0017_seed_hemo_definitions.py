"""Seed hemodynamics alert definitions — WO-028 (Rollout 2b)

Revision ID: 0017
Revises: 0012
Create Date: 2026-07-06 10:00:00.000000

Seeds 6 alert_definition_version entries for the hemodynamics domain:
  ALERT-HEMO-SHOCK-INDEX-01, ALERT-HEMO-LACTATE-CLEARANCE-02,
  ALERT-HEMO-VASO-ESCALATION-03, ALERT-HEMO-REFRACTORY-SHOCK-04,
  ALERT-HEMO-FLUID-NONRESPONSIVE-05, ALERT-HEMO-ANTIHTN-CONFLICT-06

Hybrid NRT+micro-batch evaluator. CRIT severity never auto-resolves.
Vasopressor dosing ALL canonical mcg/kg/min (SYS-02/CON-0060).
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers
revision: str = "0017"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed 6 hemodynamics alert definition versions."""
    op.execute(
        """
        INSERT INTO alert_definition_version
            (definition_version, score_type, semver, spec_hash, description)
        VALUES
            ('ALERT-HEMO-SHOCK-INDEX-01-a1b2c3', 'SHOCK_INDEX', '1.0.0',
             'he01a1b2c3d4e5f6',
             'ALERT-HEMO-SHOCK-INDEX-01: Indice de choque elevado — hipoperfusao oculta. '
             'SI > 0.9 OR MSI > 1.3 sustained > PT15M + perfusion corroborator (lactate > 2 mmol/L '
             'OR TEC > 3 s). Rady 1994 + Liu 2012 + ANDROMEDA-SHOCK 2019. severity=watch.'),
            ('ALERT-HEMO-LACTATE-CLEARANCE-02-b2c3d4', 'LACTATE_CLEARANCE', '1.0.0',
             'he02b2c3d4e5f6a7',
             'ALERT-HEMO-LACTATE-CLEARANCE-02: Clearance de lactato inadequado. '
             'Active resuscitation gate + baseline >= 2 mmol/L + (2h clearance < 10% OR '
             '6h lactate > 2 mmol/L). Jones 2010 JAMA + SSC 2021. severity=critical.'),
            ('ALERT-HEMO-VASO-ESCALATION-03-c3d4e5', 'VASO_ESCALATION', '1.0.0',
             'he03c3d4e5f6a7b8',
             'ALERT-HEMO-VASO-ESCALATION-03: Escalonamento de vasopressor. '
             'NE > 0 mcg/kg/min + (>50% dose increase in 2h OR second vasopressor added). '
             'SCCM 2024 + SSC 2021. All dosing canonical mcg/kg/min. severity=urgent.'),
            ('ALERT-HEMO-REFRACTORY-SHOCK-04-d4e5f6', 'REFRACTORY_SHOCK', '1.0.0',
             'he04d4e5f6a7b8c9',
             'ALERT-HEMO-REFRACTORY-SHOCK-04: Choque refratario — hipotensao sob vasopressor maximo. '
             'MAP < 65 mmHg sustained > PT30M AND NE > 1.0 mcg/kg/min. '
             'SEPSISPAM 2014 + SCCM 2024. Adjunct-absence enrichment. severity=critical.'),
            ('ALERT-HEMO-FLUID-NONRESPONSIVE-05-e5f6a7', 'FLUID_NONRESPONSIVE', '1.0.0',
             'he05e5f6a7b8c9d0',
             'ALERT-HEMO-FLUID-NONRESPONSIVE-05: Nao responsivo a fluidos — risco de sobrecarga. '
             'Primary (PPV/SVV < 10% + deltaSV < 10% + balance > 3000 mL) OR '
             'Fallback (fluid challenge + deltaMAP < 5 mmHg + deltalactato < 5%). '
             'Marik 2013 + Monnet 2016. severity=watch.'),
            ('ALERT-HEMO-ANTIHTN-CONFLICT-06-f6a7b8', 'ANTIHTN_CONFLICT', '1.0.0',
             'he06f6a7b8c9d0e1',
             'ALERT-HEMO-ANTIHTN-CONFLICT-06: Conflito anti-hipertensivo x PA / vasopressor. '
             'Branch A (deprescribe): active antihypertensive + hypotension/vasopressor. '
             'Branch B: uncontrolled HTN off pressor, no permissive indication. '
             'Institutional medication-safety pathway. severity=watch.')
        ON CONFLICT (definition_version) DO NOTHING
        """
    )


def downgrade() -> None:
    """Remove hemodynamics alert definition seeds."""
    op.execute(
        """
        DELETE FROM alert_definition_version
        WHERE definition_version IN (
            'ALERT-HEMO-SHOCK-INDEX-01-a1b2c3',
            'ALERT-HEMO-LACTATE-CLEARANCE-02-b2c3d4',
            'ALERT-HEMO-VASO-ESCALATION-03-c3d4e5',
            'ALERT-HEMO-REFRACTORY-SHOCK-04-d4e5f6',
            'ALERT-HEMO-FLUID-NONRESPONSIVE-05-e5f6a7',
            'ALERT-HEMO-ANTIHTN-CONFLICT-06-f6a7b8'
        )
        """
    )
