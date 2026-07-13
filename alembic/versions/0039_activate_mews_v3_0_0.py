"""Activate MEWS-v3.0.0 — RAT-MEWS-SUBBE-2001-R2 (temperature band realignment)

Revision ID: 0039
Revises: 0038
Create Date: 2026-07-12

AUDIT-001 follow-up: the MEWS-v2.0.0 ratification recorded in 0020/0029
(RAT-MEWS-SUBBE-2001) only ever covered the HR/RR/hypothermia band
corrections. The intermediate temperature bands were never checked
against the classic Subbe et al. (QJM 2001;94:521-526) table, and shipped
with 5 unratified bands that under-score fever at the escalation
threshold (38.5°C scored 1 instead of 2, masking clinical deterioration).

This migration seeds MEWS-v3.0.0, which realigns temperature to the
classic Subbe 2001 3-band table (<35.0:2, 35.0-38.4:0, >=38.5:2) and
corrects the HR 40 bpm boundary (40 -> 1, not 2, per Subbe 2001's
40-50 bpm band). MEWS-v2.0.0 is retired (superseded) accordingly.

RAT-MEWS-SUBBE-2001-R2 is PENDING CLINICAL SIGN-OFF — MEWS-v3.0.0 must
not be treated as clinically ratified until the committee confirms the
corrected bands.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0039"
down_revision: Union[str, None] = "0038"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed MEWS-v3.0.0 into algorithm_registry and retire MEWS-v2.0.0."""
    op.execute(
        """
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('MEWS-v3.0.0', 'MEWS', '3.0.0',
             'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
             'MEWS v3.0.0 — Temp bands realigned to Subbe 2001 (<35:2, 35-38.4:0, '
             '>=38.5:2); HR 40 boundary corrected to 1. '
             'RAT-MEWS-SUBBE-2001-R2 — requires clinical sign-off before production.')
        ON CONFLICT (algorithm_version) DO NOTHING
        """
    )

    # algorithm_registry has no boolean "active" flag; deactivation is modeled
    # via retired_at (see 0005_algorithm_registry.py). Retire MEWS-v2.0.0 now
    # that its temperature bands are superseded by MEWS-v3.0.0.
    op.execute(
        """
        UPDATE algorithm_registry
        SET retired_at = now()
        WHERE algorithm_version = 'MEWS-v2.0.0'
          AND retired_at IS NULL
        """
    )


def downgrade() -> None:
    """Un-retire MEWS-v2.0.0 and remove the MEWS-v3.0.0 seed."""
    op.execute(
        """
        UPDATE algorithm_registry
        SET retired_at = NULL
        WHERE algorithm_version = 'MEWS-v2.0.0'
        """
    )
    op.execute(
        "DELETE FROM algorithm_registry WHERE algorithm_version = 'MEWS-v3.0.0'"
    )
