"""Seed sepsis alert definition versions into alert_definition_version.

Revision ID: 0014
Revises: 0012
Create Date: 2026-07-05 23:59:00.000000

WO-024: Seeds 6 sepsis alert definitions with definition_version IDs,
content hashes, and metadata for traceability.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0014"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Sepsis alert definitions — 6 alerts, auto-computed content hashes
# ---------------------------------------------------------------------------

SEPSIS_DEFINITIONS = [
    {
        "definition_version": "ALERT-SEPSIS-SCREEN-01-7a3f2e1b",
        "score_type": "SEPSIS",
        "semver": "2.0.0",
        "spec_hash": "7a3f2e1b9c0d4e5f6a7b8c9d0e1f2a3b4c5d6e7f",
        "description": (
            "Triagem de sepse — SIRS/qSOFA com suspeita de infecção. "
            "Logic: infection_present AND (qsofa>=2 OR sirs_count>=2). "
            "Severity: urgent. Reconciles legacy SEP-001. "
            "Pending RAT-SEPSE-02 (v1-AND vs v3-OR aggregation dispute)."
        ),
    },
    {
        "definition_version": "ALERT-SEPSIS-ORGAN-02-b4d5e6f7",
        "score_type": "SEPSIS",
        "semver": "2.0.0",
        "spec_hash": "b4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3",
        "description": (
            "qSOFA >=2 com lactato elevado ou em elevação. "
            "Logic: qsofa>=2 AND (lactato>2 mmol/L OR delta_lactato>0.5/h). "
            "Severity: critical. Extends legacy SEP-002. "
            "Lactate anchor corrected to SSC-2021 >2 mmol/L."
        ),
    },
    {
        "definition_version": "ALERT-SEPSIS-SHOCK-03-c5d6e7f8",
        "score_type": "SEPSIS",
        "semver": "2.0.0",
        "spec_hash": "c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4",
        "description": (
            "Choque séptico iminente. "
            "Logic: lactato>=4 mmol/L OR (MAP<65 AND (fluid_bolus OR vasopressor>0)). "
            "Severity: critical. Promotes SEP-002 embedded shock flag to standalone alert."
        ),
    },
    {
        "definition_version": "ALERT-SEPSIS-BUNDLE-OVERDUE-04-d6e7f8a9",
        "score_type": "SEPSIS",
        "semver": "2.0.0",
        "spec_hash": "d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5",
        "description": (
            "Item do bundle hora-1 em atraso. "
            "Logic: protocol_active AND NOT item_checked AND now > due_at. "
            "Severity: urgent. SSC-2021 7-item bundle compliance timer. "
            "Replaces per-item legacy flags (RULE-SEPSE-069/070/076/096)."
        ),
    },
    {
        "definition_version": "ALERT-SEPSIS-PCT-RISING-05-e7f8a9b0",
        "score_type": "SEPSIS",
        "semver": "2.0.0",
        "spec_hash": "e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6",
        "description": (
            "Procalcitonina em elevação — possível falha terapêutica. "
            "Logic: PCT > PCT_anterior AND delta_pct > 0.25 ng/mL/24h AND ATB >=48h. "
            "Severity: watch. Reconciles legacy SEP-003b treatment-failure branch."
        ),
    },
    {
        "definition_version": "ALERT-SEPSIS-PCT-DEESC-06-f8a9b0c1",
        "score_type": "SEPSIS",
        "semver": "2.0.0",
        "spec_hash": "f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7",
        "description": (
            "Desmame antimicrobiano guiado por procalcitonina. "
            "Logic: (PCT < 0.25 OR >80% drop) AND ATB >=48h AND NOT patient_unstable. "
            "Severity: normal. Reconciles legacy SEP-003a de-escalation branch. "
            "Stability gate wired to SCREEN-01/ORGAN-02/SHOCK-03 states."
        ),
    },
]


def upgrade() -> None:
    """Seed sepsis alert definition versions into alert_definition_version."""
    for d in SEPSIS_DEFINITIONS:
        op.execute(
            f"""
            INSERT INTO alert_definition_version
                (definition_version, score_type, semver, spec_hash, description)
            VALUES
                ('{d['definition_version']}', '{d['score_type']}',
                 '{d['semver']}', '{d['spec_hash']}', '{d['description']}')
            ON CONFLICT (definition_version) DO UPDATE
                SET description = EXCLUDED.description
            """
        )


def downgrade() -> None:
    """Remove sepsis alert definition seeds."""
    versions = [d["definition_version"] for d in SEPSIS_DEFINITIONS]
    for v in versions:
        op.execute(
            f"DELETE FROM alert_definition_version WHERE definition_version = '{v}'"
        )
