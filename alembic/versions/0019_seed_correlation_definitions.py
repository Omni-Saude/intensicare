"""Seed correlation alert definitions — WO-032 (Rollout 2d)

Revision ID: 0019
Revises: 0016
Create Date: 2026-07-06 00:00:00.000000

Seeds 4 alert_definition_version entries for the correlation engine:
  ALERT-CORR-SEPSIS-AKI-01  — Sepsis + AKI (SA-AKI)
  ALERT-CORR-RESP-HEMO-02   — Respiratory + Hemodynamic (SDRA+choque)
  ALERT-CORR-QTC-ELEC-03    — Drug + Electrolyte (QTc + K+/Mg2+)
  ALERT-CORR-EXAM-REDUND-04 — Redundant diagnostic ordering (efficiency)

Clinical chains (1)(2)(3): fold member alerts (net reduction in pushes).
Chain (3) AMPLIFIES: two WARN members -> one CRITICAL.
Chain (4): standalone efficiency/stewardship; excluded from suppression
accounting per B3-004.

PPV budget: fleet floor >= 0.60; per-correlation targets: 0.80/0.85/0.70/0.60.
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers
revision: str = "0019"
down_revision: Union[str, None] = "0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed 4 correlation alert definition versions."""
    op.execute(
        """
        INSERT INTO alert_definition_version
            (definition_version, score_type, semver, spec_hash, description)
        VALUES
            ('ALERT-CORR-SEPSIS-AKI-01-v1-0-0', 'CORRELATION_SEPSIS_AKI', '1.0.0',
             'corr_sepsis_aki_sha256_001',
             'ALERT-CORR-SEPSIS-AKI-01: Sepse com lesao renal aguda associada (SA-AKI) — '
             'sepsis organ-dysfunction/shock + KDIGO>=1 joined within PT72H, sepsis-first '
             'causal ordering. Critical severity. Folds member sepsis (ORGAN-02/SHOCK-03) + '
             'AKI (KDIGO stage) alerts. '
             'Evidence: Zarbock/ADQI 2023, Bagshaw 2007, KDIGO 2012, SSC 2021. '
             'PPV target: 0.80, est volume: 2/100 beds/day.'),
            ('ALERT-CORR-RESP-HEMO-02-v1-0-0', 'CORRELATION_RESP_HEMO', '1.0.0',
             'corr_resp_hemo_sha256_001',
             'ALERT-CORR-RESP-HEMO-02: Falencia cardiopulmonar combinada (SDRA moderada/grave + '
             'choque) — moderate/severe ARDS (P/F<=200 or S/F<=235) + shock event joined within '
             'PT6H. Critical severity. Folds member respiratory (RESP-002) + hemodynamic '
             '(HEMO-003/HEMO-001) alerts. '
             'Evidence: Berlin Definition 2012, SEPSISPAM 2014, Vieillard-Baron 2016. '
             'PPV target: 0.85, est volume: 1/100 beds/day.'),
            ('ALERT-CORR-QTC-ELEC-03-v1-0-0', 'CORRELATION_QTC_ELEC', '1.0.0',
             'corr_qtc_elec_sha256_001',
             'ALERT-CORR-QTC-ELEC-03: Substrato de Torsades amplificado — QTc prolongado + '
             'hipocalemia/hipomagnesemia — QTc>500ms + >=1 CredibleMeds Known-Risk drug + '
             '(K<3.5 or Mg<0.7) joined within PT24H. AMPLIFIED from WARN to CRITICAL. '
             'Folds member drug (DDX-001) + electrolyte (ELY-002/ELY-006) alerts. '
             'Evidence: Drew/AHA/ACCF 2010, Tisdale 2013, CredibleMeds. '
             'PPV target: 0.70, est volume: 1/100 beds/day.'),
            ('ALERT-CORR-EXAM-REDUND-04-v1-0-0', 'CORRELATION_EXAM_REDUND', '1.0.0',
             'corr_exam_redund_sha256_001',
             'ALERT-CORR-EXAM-REDUND-04: Solicitacao redundante de exame (mesma classe dentro '
             'da janela de reavaliacao) — per-class window test (corrected from legacy '
             'RULE-EFICIENCIA-007 summed-across-classes bug). Normal severity. STANDALONE '
             '(no member alerts suppressed; net-additive +2 volume). '
             'Category: efficiency-stewardship (B3-004). '
             'Evidence: RULE-EFICIENCIA-007 (ADAPT), Choosing Wisely 2014. '
             'PPV target: 0.60, est volume: 2/100 beds/day.')
        ON CONFLICT (definition_version) DO NOTHING
        """
    )


def downgrade() -> None:
    """Remove correlation alert definition seeds."""
    op.execute(
        """
        DELETE FROM alert_definition_version
        WHERE definition_version IN (
            'ALERT-CORR-SEPSIS-AKI-01-v1-0-0',
            'ALERT-CORR-RESP-HEMO-02-v1-0-0',
            'ALERT-CORR-QTC-ELEC-03-v1-0-0',
            'ALERT-CORR-EXAM-REDUND-04-v1-0-0'
        )
        """
    )
