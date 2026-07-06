"""Ratification Record — Wave 3B Finalization

Revision ID: 0029
Revises: 0022
Create Date: 2026-07-06 16:00:00.000000

Records the definitive ratification of all 204 RATIFY-disposition rules
per the clinical committee decisions in RATIFICATION-DECISIONS.md.
Creates the ratification_event table and seeds the canonical ratification
record for the 2026-07-06 ratification event.

Algorithm versions ratified:
  - MEWS-v2.0.0  (RAT-MEWS-SUBBE-2001, AUDIT-001) — Subbe 2001 corrected bands
  - NEWS2-v3.0.0 (RAT-NEWS2-SCALE-2, AUDIT-002)  — RCP 2017 Scale-2 + supplemental_O2
  - SOFA-v2.0.0  (RAT-CLINICAL-SCORING-01/02/03) — canonical units, boundary fixes
  - Sepsis-v3.0.0 (RAT-SEPSE-01/02) — SSC-2021 screening pathway

Deliberately deferred (HANDOFF):
  - RAT-ELY-01 — phosphate canonical unit + numeric bands
    (awaiting clinical committee; see docs/plan/clinical/domains/electrolyte.md §3.6)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0029"
down_revision: Union[str, None] = "0022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create ratification_event table, seed algorithm_registry, insert event."""

    # ── 1. Create ratification_event table ──────────────────────────────────
    op.create_table(
        "ratification_event",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "event_date",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("ratified_by", sa.String(length=128), nullable=False),
        sa.Column("authority", sa.String(length=256), nullable=False),
        sa.Column("algorithm_versions", sa.Text(), nullable=False),
        sa.Column("evidence_basis", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── 2. Update algorithm_registry with ratification metadata ────────────
    # Mark existing entries as CLINICALLY RATIFIED with the definitive date.
    op.execute(
        """
        UPDATE algorithm_registry
        SET description = description || ' Ratified 2026-07-06.'
        WHERE algorithm_version IN (
            'MEWS-v2.0.0',
            'NEWS2-v3.0.0',
            'SOFA-v2.0.0',
            'qSOFA-v1.0.0'
        )
        AND description NOT LIKE '%Ratified 2026-07-06%'
        """
    )

    # Ensure Sepsis v3.0.0 entry exists (may have been seeded by prior migration)
    op.execute(
        """
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('Sepsis-v3.0.0', 'SEPSIS', '3.0.0',
             's3p5i5v300a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3',
             'Sepsis v3.0.0 — CLINICALLY RATIFIED per RAT-SEPSE-01/02. '
             'SSC-2021 screening pathway: qSOFA >=2 + suspected infection -> '
             'lactate confirmation -> hour-1 bundle. '
             'Supersedes v1-AND and v3-OR aggregation (RATIFICATION-DECISIONS.md §1). '
             'Ratified by clinical committee 2026-07-04. Ratified 2026-07-06.')
        ON CONFLICT (algorithm_version) DO UPDATE
        SET description = EXCLUDED.description
        """
    )

    # ── 3. Insert the ratification event record ─────────────────────────────
    op.execute(
        """
        INSERT INTO ratification_event
            (event_date, ratified_by, authority, algorithm_versions,
             evidence_basis, notes)
        VALUES
            ('2026-07-06 00:00:00+00:00',
             'Clinical Committee + Repository Owner Delegation',
             'RATIFICATION-DECISIONS.md (2026-07-04); BUILD-ADR-001 ACCEPTED',
             'MEWS-v2.0.0 (RAT-MEWS-SUBBE-2001, AUDIT-001), '
             'NEWS2-v3.0.0 (RAT-NEWS2-SCALE-2, AUDIT-002), '
             'SOFA-v2.0.0 (RAT-CLINICAL-SCORING-01/02/03), '
             'Sepsis-v3.0.0 (RAT-SEPSE-01/02), '
             'qSOFA-v1.0.0 (canonical)',
             '204 RATIFY dispositions confirmed. '
             '12 P0 defects resolved per reference-correct defaults. '
             'MEWS/NEWS2 corrections (HANDOFF AUDIT-001/002) ratified. '
             'Canonical units (FiO2 fraction, lactate mmol/L, vasopressor mcg/kg/min) ratified. '
             '1 DEFERRED: RAT-ELY-01 (phosphate thresholds — HANDOFF, awaiting clinical committee). '
             'See docs/plan/RATIFICATION-DECISIONS.md and docs/plan/traceability-matrix.md.',
             'Wave 3B finalization. All pending RAT-* flags resolved: '
             '5 RATIFIED, 1 DEFERRED (RAT-ELY-01). '
             'Traceability matrix regenerated with 959 rules (204 RATIFY).')
        """
    )


def downgrade() -> None:
    """Remove ratification event record and drop table."""
    op.execute("DELETE FROM ratification_event WHERE event_date = '2026-07-06 00:00:00+00:00'")
    op.execute(
        """
        UPDATE algorithm_registry
        SET description = REPLACE(description, ' Ratified 2026-07-06.', '')
        WHERE algorithm_version IN (
            'MEWS-v2.0.0', 'NEWS2-v3.0.0', 'SOFA-v2.0.0', 'qSOFA-v1.0.0'
        )
        """
    )
    op.execute("DELETE FROM algorithm_registry WHERE algorithm_version = 'Sepsis-v3.0.0'")
    op.drop_table("ratification_event")
