"""Wave 1C — RATIFY → Final Dispositions Ratification Record

Revision ID: 0024
Revises: 0022
Create Date: 2026-07-06 14:00:00.000000

Records the definitive ratification of all 204 RATIFY-disposition rules
converted to final dispositions (ADOPT/ADOPT-CORRECTED/ADAPT/RETIRE)
per the clinical committee decisions in RATIFICATION-DECISIONS.md.

Disposition changes:
  Before: 204 RATIFY, 194 ADOPT,  57 ADOPT-CORRECTED, 209 ADAPT,  66 SUPERSEDE, 229 RETIRE
  After:    0 RATIFY, 371 ADOPT,  57 ADOPT-CORRECTED, 223 ADAPT,  66 SUPERSEDE, 242 RETIRE

Breakdown by band:
  P0 (12):          RATIFY → ADOPT (reference-correct recommended defaults)
  P1 (45):          RATIFY → ADOPT (reference-correct recommended defaults)
  UNVERIFIABLE (101): RATIFY → ADOPT (owner-confirmed per ASK-2)
  AMBIGUOUS (14):   RATIFY → ADAPT (kept per drafter recommendation)
  AMBIGUOUS (13):   RATIFY → RETIRE (retired per drafter recommendation)
  P2/P3/ADDENDUM (19): RATIFY → ADOPT

Total: 177 ADOPT + 14 ADAPT + 13 RETIRE = 204 rules converted.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0024"
down_revision: Union[str, None] = "0022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Insert Wave 1C ratification event record.

    Records the completion of the RATIFY → final disposition conversion
    for all 204 rules, per RATIFICATION-DECISIONS.md (2026-07-04).
    """
    # Ensure ratification_event table exists (may be created by 0029)
    # Use IF NOT EXISTS to be safe
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS ratification_event (
            id SERIAL PRIMARY KEY,
            event_date TIMESTAMPTZ NOT NULL,
            ratified_by VARCHAR(128) NOT NULL,
            authority VARCHAR(256) NOT NULL,
            algorithm_versions TEXT NOT NULL,
            evidence_basis TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        INSERT INTO ratification_event
            (event_date, ratified_by, authority, algorithm_versions,
             evidence_basis, notes)
        VALUES
            ('2026-07-06 14:00:00+00:00',
             'Clinical Committee + Repository Owner Delegation',
             'RATIFICATION-DECISIONS.md (2026-07-04)',
             'WAVE-1C-RATIFY-CONVERSION',
             '204 RATIFY rules converted to final dispositions: '
             '177 ADOPT (P0/P1/UNVERIFIABLE/ADDENDUM/P2/P3), '
             '14 ADAPT (AMBIGUOUS kept), '
             '13 RETIRE (AMBIGUOUS retired). '
             'Per en-bloc adoption of reference-anchored recommended defaults. '
             'Decision rule: all P0/P1/UNVERIFIABLE rules confirmed; '
             'AMBIGUOUS rules kept (ADAPT) or retired per drafter recommendation.',
             'Wave 1C finalization. Traceability matrix updated: '
             '204 RATIFY → 0 RATIFY. '
             'New totals: 371 ADOPT, 57 ADOPT-CORRECTED, 223 ADAPT, '
             '66 SUPERSEDE, 242 RETIRE. '
             'See docs/plan/RATIFICATION-DECISIONS.md and '
             'docs/plan/traceability-matrix.md.')
        """
    )


def downgrade() -> None:
    """Remove Wave 1C ratification event."""
    op.execute(
        """
        DELETE FROM ratification_event
        WHERE algorithm_versions = 'WAVE-1C-RATIFY-CONVERSION'
        """
    )
