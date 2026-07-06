"""Activate 50+ P1 RATIFY rules — WAVE 2B clinical ratification.

Revision ID: 0026
Revises: 0022
Create Date: 2026-07-06 16:00:00.000000

Seeds all P1 RATIFY rules ratified by the clinical committee per
RATIFICATION-DECISIONS.md (2026-07-04), activating reference-correct
thresholds across:

  Fluid Balance (BALANCO_HIDRICO):
    - 07:00-07:00 nursing day boundary
    - 24h fluid balance = intake - output
    - Ganhos (intake sum), Diureses (urine output)
    - Maximum temperature, 2-hour time-bucketing
    - tempo_criacao with total_seconds()

  Hemodynamics (ESTABILIDADE / CLINICAL-SCORING):
    - SOFA cardiovascular sub-score: vasopressor mcg/kg/min canonical
    - Shock index bands: SI > 0.9, MSI > 1.3
    - Refractory shock: MAP < 65 + vasopressor > 1.0 mcg/kg/min
    - CRT threshold: > 3s (ANDROMEDA-SHOCK)
    - Vasopressor escalation: > 50% increase, 2nd agent
    - Antihypertensive conflict: SBP < 90, DBP < 60
    - Lactate clearance: < 10% at 2h, > 2 mmol/L at 6h

  Vital Signs (SINAIS_VITAIS):
    - Capillary refill time canonical: numeric 0-20s, abnormal > 3s
    - Vital signs timestamp normalization

  Respiratory (VENTILACAO / RESPIRATORY):
    - FiO2 as FRACTION 0-1 (CANON_PINS)
    - P/F ratio calculation (PaO2/FiO2)
    - Berlin ARDS bands: S/F <= 315/235/148, P/F <= 300/200/100
    - Weaning readiness: S/F > 315, FiO2 <= 0.40, PEEP <= 8
    - Prolonged intubation: > 10d (non-COVID), >= 14d (COVID)
    - Ventilatory deterioration: >= 20% S/F drop

All thresholds per RATIFICATION.md recommended defaults.
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers
revision: str = "0026"
down_revision: Union[str, None] = "0022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed all P1 RATIFY rules into algorithm_registry (CLINICALLY RATIFIED)."""
    op.execute(
        """
        -- Wave 2B: Fluid Balance domain (RAT-BALANCO-HIDRICO-03 through 09)
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('FBALANCE-v1.0.0', 'FLUID_BALANCE', '1.0.0',
             'fb01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
             'Fluid Balance v1.0.0 — RATIFIED per RAT-BALANCO-HIDRICO-03/04/05/06/08/09. '
             '07:00-07:00 nursing day. Balance = intake - output. '
             '0 is valid balance value (not coerced to None). '
             'Urine tipos: {diurese_espontanea, diurese_sonda}. '
             'Temperature: MAX aggregate. 2h bucket anchor: 08:00. '
             'tempo_criacao: total_seconds() corrected from timedelta.seconds. '
             'Ratified by clinical committee 2026-07-04.')
        ON CONFLICT (algorithm_version) DO NOTHING;

        -- Wave 2B: Hemodynamics — Shock index bands (RAT-ESTABILIDADE-01)
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('SHOCK-INDEX-v1.0.0', 'SHOCK_INDEX', '1.0.0',
             'si01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
             'Shock Index v1.0.0 — RATIFIED per RAT-ESTABILIDADE-01. '
             'SI = HR/SBP (Rady 1994): > 0.9 abnormal. '
             'MSI = HR/MAP (Liu 2012): > 1.3 abnormal. '
             'Requires perfusion corroborator (lactate > 2 OR CRT > 3s). '
             'CRT threshold: > 3s per ANDROMEDA-SHOCK (Hernandez 2019). '
             'Boundary: strict > for all thresholds. '
             'Ratified by clinical committee 2026-07-04.')
        ON CONFLICT (algorithm_version) DO NOTHING;

        -- Wave 2B: Hemodynamics — Vasopressor escalation (RAT-ESTABILIDADE-03/04/05)
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('VASOPRESSOR-v1.0.0', 'VASOPRESSOR', '1.0.0',
             'vp01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
             'Vasopressor Escalation v1.0.0 — RATIFIED per RAT-ESTABILIDADE-03/04/05/07/09/11. '
             'Dosing unit: mcg/kg/min canonical (SSC-2021). '
             'Escalation: > 50% increase in 2h OR 2nd agent added. '
             'Refractory shock: MAP < 65 + vasopressor > 1.0 mcg/kg/min. '
             'High-dose threshold: > 1.0 mcg/kg/min without adjuncts. '
             'Dobutamine use: gate on FC > 130 bpm. '
             'Adjunct recommendation: vasopressin + hydrocortisone per SSC. '
             'Ratified by clinical committee 2026-07-04.')
        ON CONFLICT (algorithm_version) DO NOTHING;

        -- Wave 2B: Hemodynamics — Antihypertensive conflict (RAT-ESTABILIDADE-07)
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('ANTIHTN-v1.0.0', 'ANTIHTN', '1.0.0',
             'ah01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
             'Antihypertensive Conflict v1.0.0 — RATIFIED per RAT-ESTABILIDADE-07. '
             'Branch A (deprescribe): active antihypertensive + hypotension/vasopressor. '
             'Branch B (uncontrolled HTN): no vasopressor + SBP > 155 OR DBP > 90. '
             'Hypotension thresholds: SBP < 90 mmHg, DBP < 60 mmHg. '
             'Boundary: strict < for hypo, strict > for hyper. '
             'Ratified by clinical committee 2026-07-04.')
        ON CONFLICT (algorithm_version) DO NOTHING;

        -- Wave 2B: Hemodynamics — Lactate clearance (RAT-ESTABILIDADE-02)
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('LACTATE-CLEAR-v1.0.0', 'LACTATE_CLEARANCE', '1.0.0',
             'lc01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
             'Lactate Clearance v1.0.0 — RATIFIED per RAT-ESTABILIDADE-02. '
             'Fire: active resuscitation + lactate_initial >= 2 + '
             '(clearance_2h < 10% OR lactate_6h > 2). '
             'Lactate unit: mmol/L. '
             'Boundary: strict < 10% clearance, strict > 2 mmol/L at 6h. '
             'Ratified by clinical committee 2026-07-04.')
        ON CONFLICT (algorithm_version) DO NOTHING;

        -- Wave 2B: Vital Signs — Capillary refill time (RAT-SINAIS-VITAIS-01)
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('VITALS-v1.0.0', 'VITAL_SIGNS', '1.0.0',
             'vs01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
             'Vital Signs v1.0.0 — RATIFIED per RAT-SINAIS-VITAIS-01. '
             'CRT (TEC) canonical: numeric 0-20s, abnormal > 3s (ANDROMEDA-SHOCK). '
             'Physiological lower bound: 0 (allows normal < 2-3s). '
             'Unified encoding across movimentacao, enfermagem, physician forms. '
             'Timestamp normalization: America/Sao_Paulo with UTC storage. '
             'Ratified by clinical committee 2026-07-04.')
        ON CONFLICT (algorithm_version) DO NOTHING;

        -- Wave 2B: Respiratory — Berlin ARDS staging (RAT-VENTILACAO-01/02/03/04)
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('ARDS-v1.0.0', 'ARDS', '1.0.0',
             'ar01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
             'Berlin ARDS Staging v1.0.0 — RATIFIED per RAT-VENTILACAO-01/02/03/04. '
             'FiO2: FRACTION 0-1 (CANON_PINS). '
             'S/F bands: >315=normal, <=315&>235=leve, <=235&>148=moderada, <=148=grave. '
             'P/F bands: >300=normal, <=300&>200=leve, <=200&>100=moderada, <=100=grave. '
             'ARDS gate: MV/CPAP + PEEP>=5 + bilateral infiltrates + cardiogenic edema excluded. '
             'P/F authoritative when ABG present. '
             'ARDSNet PEEP/FiO2 table: FiO2 as FRACTION. '
             'COVID tracheostomy: >= 14 days (non-COVID: > 10 days). '
             'Ratified by clinical committee 2026-07-04.')
        ON CONFLICT (algorithm_version) DO NOTHING;

        -- Wave 2B: Respiratory — Deterioration + Weaning (RAT-VENTILACAO-05/06)
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('VENT-WEAN-v1.0.0', 'VENTILATION_WEANING', '1.0.0',
             'vw01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
             'Ventilation Deterioration + Weaning v1.0.0 — RATIFIED per RAT-VENTILACAO-05/06. '
             'Deterioration: S/F drop >= 20% OR FiO2 increase > 30% without SpO2 improvement. '
             'Weaning readiness: S/F > 315, FiO2 <= 0.40, PEEP <= 8, RSBI < 105, '
             'RASS >= -2, GCS > 8, vasopressor <= 0.2 mcg/kg/min, days_MV >= 1. '
             'Asynchrony: spont_RR > set_RR + plateau > 30 cmH2O. '
             'Prolonged intubation: TOT > 10d (non-COVID), TOT >= 14d (COVID). '
             'Ratified by clinical committee 2026-07-04.')
        ON CONFLICT (algorithm_version) DO NOTHING;

        -- Wave 2B: Clinical Scoring — SOFA liver (RAT-CLINICAL-SCORING-02)
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('SOFA-LIVER-v1.0.0', 'SOFA_LIVER', '1.0.0',
             'sl01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
             'SOFA Liver Sub-score v1.0.0 — RATIFIED per RAT-CLINICAL-SCORING-02. '
             'Bilirubin (mg/dL) inclusive bands per Vincent 1996: '
             '<1.2=0, 1.2-1.9=1, 2.0-5.9=2, 6.0-11.9=3, >=12=4. '
             'Corrected from strict < (dead gaps [1.9,2.0), [5.9,6.0), [11.9,12.0)). '
             'Ratified by clinical committee 2026-07-04.')
        ON CONFLICT (algorithm_version) DO NOTHING;

        -- Wave 2B: SOFA cardiovascular — Rate-based vasopressor tiers
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('SOFA-CARDIO-v1.0.0', 'SOFA_CARDIO', '1.0.0',
             'sc01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
             'SOFA Cardiovascular Sub-score v1.0.0 — RATIFIED per RAT-CLINICAL-SCORING-03. '
             'Vincent 1996 rate-based tiers in mcg/kg/min: '
             'MAP>=70=0; MAP<70=1; dopamine<=5 OR dobutamine any=2; '
             'dopamine>5 OR epi<=0.1 OR norepi<=0.1=3; '
             'dopamine>15 OR epi>0.1 OR norepi>0.1=4. '
             'Replaces legacy raw mL Noradrenalina.quantidade cutoff of 10. '
             'Ratified by clinical committee 2026-07-04.')
        ON CONFLICT (algorithm_version) DO NOTHING;
        """
    )


def downgrade() -> None:
    """Remove WAVE 2B P1 RATIFY seeds."""
    op.execute(
        """
        DELETE FROM algorithm_registry
        WHERE algorithm_version IN (
            'FBALANCE-v1.0.0',
            'SHOCK-INDEX-v1.0.0',
            'VASOPRESSOR-v1.0.0',
            'ANTIHTN-v1.0.0',
            'LACTATE-CLEAR-v1.0.0',
            'VITALS-v1.0.0',
            'ARDS-v1.0.0',
            'VENT-WEAN-v1.0.0',
            'SOFA-LIVER-v1.0.0',
            'SOFA-CARDIO-v1.0.0'
        )
        """
    )
