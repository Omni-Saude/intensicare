"""Sprint-1 Patient Safety — Backfill role='admin' for legacy admin users.

Revision ID: 0040
Revises: 0039
Create Date: 2026-07-12

Context: the RBAC fix made ABAC validate the user's REAL clinical role
(`User.role`) instead of trusting a fixed/derived value. `User.role`
defaults to 'readonly' (models/user.py:24), and prior to this sprint the
admin API (`UserCreate`) never exposed a `role` field — every user ever
created through it was persisted with role='readonly' regardless of
`is_admin`. Combined with the ABAC fix, that leaves existing operators
who have `is_admin = TRUE` but `role = 'readonly'` locked out of the
very admin endpoints they're supposed to manage.

This migration is a one-time data backfill: any user flagged
`is_admin = TRUE` whose `role` is still the default `'readonly'` is
promoted to `role = 'admin'`. Users who already have a non-default
clinical role (e.g. an `is_admin` medico) are left untouched — we only
correct rows that are unambiguously still sitting on the schema default.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0040"
down_revision: Union[str, None] = "0039"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Backfill admin role for legacy admin users stuck on the default
    #    'readonly' role ─────────────────────────────────────────────────
    op.execute(
        sa.text(
            "UPDATE users SET role = 'admin' "
            "WHERE is_admin = TRUE AND role = 'readonly';"
        )
    )


def downgrade() -> None:
    # No-op by design. Reverting this backfill is unsafe: we cannot
    # distinguish rows that were 'readonly' because of the pre-fix bug
    # (which we intentionally corrected) from rows that were genuinely,
    # deliberately set to 'readonly' by an operator before this migration
    # ran. Setting them back to 'readonly' could silently re-lock admins
    # out of admin endpoints, which is the exact patient-safety bug this
    # migration exists to fix. If a rollback is truly required, restore
    # role values from a pre-migration backup instead.
    pass
