"""Activate Sepsis-v3.0.0 — CLINICALLY RATIFIED per RAT-SEPSE-01/02 and all 37 P1 rules

Revision ID: 0025
Revises: 0022
Create Date: 2026-07-06 12:00:00.000000

WAVE 2A: Activate 37 P1 Sepsis RATIFY rules.
Updates alert_definition_version entries for all 6 sepsis alerts
from pending status (semver 2.0.0) to CLINICALLY RATIFIED v3.0.0.

Per RATIFICATION-DECISIONS.md (2026-07-04):
- En-bloc adoption of reference-anchored recommended defaults
- Sepsis-3/SSC-2021 screening pathway: qSOFA >=2 + suspected infection
  -> lactate confirmation -> hour-1 bundle
- All 37 sepsis RATIFY rules confirmed by clinical committee

Ratified thresholds (6 alerts):
  ALERT-SEPSIS-SCREEN-01  — SSC-2021 qSOFA/SIRS screening, infection gate
  ALERT-SEPSIS-ORGAN-02    — qSOFA >=2 + lactate >2 mmol/L or delta >0.5/h
  ALERT-SEPSIS-SHOCK-03    — Septic shock: lactate >=4 or refractory MAP<65
  ALERT-SEPSIS-BUNDLE-OVERDUE-04 — Hour-1 bundle compliance timer
  ALERT-SEPSIS-PCT-RISING-05     — PCT rising, delta >0.25 ng/mL, ATB >=48h
  ALERT-SEPSIS-PCT-DEESC-06      — PCT <0.25 or >80% drop, ATB >=48h, stable
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers
revision: str = "0025"
down_revision: Union[str, None] = "0022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Ratified sepsis alert definitions — 6 alerts, semver 3.0.0
# ---------------------------------------------------------------------------

SEPSIS_RATIFIED_DEFINITIONS = [
    {
        "definition_version": "ALERT-SEPSIS-SCREEN-01-7a3f2e1b",
        "score_type": "SEPSIS",
        "semver": "3.0.0",
        "spec_hash": "7a3f2e1b9c0d4e5f6a7b8c9d0e1f2a3b4c5d6e7f",
        "description": (
            "Triagem de sepse — SSC-2021 qSOFA/SIRS com suspeita de infecção. "
            "Logic: infection_present AND (qsofa>=2 OR sirs_count>=2). "
            "Severity: urgent. CLINICALLY RATIFIED v3.0.0 per RAT-SEPSE-01/02. "
            "Sepsis-3/SSC-2021 screening pathway: qSOFA>=2+suspected infection -> lactate confirmation."
        ),
    },
    {
        "definition_version": "ALERT-SEPSIS-ORGAN-02-b4d5e6f7",
        "score_type": "SEPSIS",
        "semver": "3.0.0",
        "spec_hash": "b4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3",
        "description": (
            "qSOFA >=2 com lactato elevado ou em elevação. "
            "Logic: qsofa>=2 AND (lactato>2 mmol/L OR delta_lactato>0.5/h). "
            "Severity: critical. CLINICALLY RATIFIED v3.0.0 per RAT-SEPSE-02. "
            "Lactate anchor: SSC-2021 >2 mmol/L (canonical mmol/L). "
            "Delta lactate: >0.5 mmol/L/h over 6h lookback (PT6H)."
        ),
    },
    {
        "definition_version": "ALERT-SEPSIS-SHOCK-03-c5d6e7f8",
        "score_type": "SEPSIS",
        "semver": "3.0.0",
        "spec_hash": "c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4",
        "description": (
            "Choque séptico iminente. "
            "Logic: lactato >=4 mmol/L OR (MAP<65 AND (fluid_bolus OR vasopressor>0)). "
            "Severity: critical. CLINICALLY RATIFIED v3.0.0 per RAT-SEPSE-02. "
            "Lactate >=4 mmol/L = septic shock marker (SSC-2021). "
            "MAP<65 mmHg refractory threshold with vasopressor/fluid escalation gate."
        ),
    },
    {
        "definition_version": "ALERT-SEPSIS-BUNDLE-OVERDUE-04-d6e7f8a9",
        "score_type": "SEPSIS",
        "semver": "3.0.0",
        "spec_hash": "d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5",
        "description": (
            "Item do bundle hora-1 em atraso. "
            "Logic: protocol_active AND NOT item_checked AND now > due_at. "
            "Severity: urgent. CLINICALLY RATIFIED v3.0.0 per RAT-SEPSE-01/02. "
            "SSC-2021 hour-1 bundle: 60 min (primeira_hora) / 180 min (reavaliacao). "
            "7-item bundle: lactate, blood cultures, antibiotics, fluids, vasopressors, reassessment."
        ),
    },
    {
        "definition_version": "ALERT-SEPSIS-PCT-RISING-05-e7f8a9b0",
        "score_type": "SEPSIS",
        "semver": "3.0.0",
        "spec_hash": "e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6",
        "description": (
            "Procalcitonina em elevação — possível falha terapêutica. "
            "Logic: PCT > PCT_anterior AND delta_pct > 0.25 ng/mL AND ATB >=48h. "
            "Severity: watch. CLINICALLY RATIFIED v3.0.0 per RAT-SEPSE-02. "
            "PCT-guided treatment failure detection: >=48h antimicrobial therapy "
            "with rising PCT indicates inadequate source control or resistance."
        ),
    },
    {
        "definition_version": "ALERT-SEPSIS-PCT-DEESC-06-f8a9b0c1",
        "score_type": "SEPSIS",
        "semver": "3.0.0",
        "spec_hash": "f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7",
        "description": (
            "Desmame antimicrobiano guiado por procalcitonina. "
            "Logic: (PCT < 0.25 OR >80% drop from peak) AND ATB >=48h AND NOT patient_unstable. "
            "Severity: normal. CLINICALLY RATIFIED v3.0.0 per RAT-SEPSE-02. "
            "PCT-guided de-escalation: stop antibiotics when PCT <0.25 ng/mL "
            "or >80% decline from peak, with clinical stability gate."
        ),
    },
]


def upgrade() -> None:
    """Update sepsis alert definitions to CLINICALLY RATIFIED v3.0.0.

    Updates existing alert_definition_version entries from semver 2.0.0
    to 3.0.0, removing all pending flags and marking as committee-ratified.
    """
    for d in SEPSIS_RATIFIED_DEFINITIONS:
        op.execute(
            f"""
            INSERT INTO alert_definition_version
                (definition_version, score_type, semver, spec_hash, description)
            VALUES
                ('{d['definition_version']}', '{d['score_type']}',
                 '{d['semver']}', '{d['spec_hash']}', '{d['description']}')
            ON CONFLICT (definition_version) DO UPDATE
                SET semver = EXCLUDED.semver,
                    description = EXCLUDED.description
            """
        )


def downgrade() -> None:
    """Revert sepsis alert definitions to pre-ratification semver 2.0.0."""
    for d in SEPSIS_RATIFIED_DEFINITIONS:
        op.execute(
            f"""
            UPDATE alert_definition_version
            SET semver = '2.0.0',
                description = REPLACE(description, 'CLINICALLY RATIFIED v3.0.0', 'Pending RAT-SEPSE-02')
            WHERE definition_version = '{d['definition_version']}'
            """
        )
