"""pgcrypto PHI encryption for patient_cache (INV-4 / WO-002)

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-05 12:00:00.000000

Encrypts PHI columns (display_name, mrn, birth_date) using pgcrypto pgp_sym_encrypt.
Adds cpf (BYTEA) / cns (BYTEA) columns.
Adds mrn_bidx blind index (HMAC-SHA256) for lookups without decryption.

Per-tenant key isolation via GUC ``app.encryption_key`` (must be set before migration).

DRILL gates:
  - REQ-INV-4-1: display_name / mrn / birth_date encrypted at rest
  - REQ-INV-4-2: mrn_bidx blind index for lookups
  - REQ-INV-4-3: cpf / cns columns added
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# GUC that holds the per-tenant Data Encryption Key.
# Must be set (e.g. via SET app.encryption_key = '...' or ALTER DATABASE … SET).
ENCRYPTION_KEY_GUC = "app.encryption_key"


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. pgcrypto extension (idempotent — also created by 0003 for safety)
    # ------------------------------------------------------------------
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto SCHEMA public")

    # ------------------------------------------------------------------
    # 2. Add new BYTEA columns: cpf, cns, mrn_bidx
    #    (nullable initially; we may tighten constraints later)
    # ------------------------------------------------------------------
    op.add_column("patient_cache", sa.Column("cpf", sa.LargeBinary(), nullable=True))
    op.add_column("patient_cache", sa.Column("cns", sa.LargeBinary(), nullable=True))
    op.add_column("patient_cache", sa.Column("mrn_bidx", sa.LargeBinary(), nullable=True))

    # ------------------------------------------------------------------
    # 3. Populate mrn_bidx blind index from existing plaintext MRN
    #    Uses HMAC-SHA256 so the same MRN always produces the same
    #    blind-index value (lookup without decryption).
    # ------------------------------------------------------------------
    op.execute(
        f"""
        UPDATE patient_cache
           SET mrn_bidx = hmac(mrn, current_setting('{ENCRYPTION_KEY_GUC}'), 'sha256')
         WHERE mrn IS NOT NULL
           AND mrn_bidx IS NULL
        """
    )

    # ------------------------------------------------------------------
    # 4. Encrypt existing plaintext PHI columns in-place via ALTER TYPE.
    #    USING pgp_sym_encrypt(<col>::text, …) handles the conversion.
    #    Handles NULLs gracefully (pgp_sym_encrypt of NULL → NULL).
    # ------------------------------------------------------------------
    op.execute(
        f"""
        ALTER TABLE patient_cache
          ALTER COLUMN display_name TYPE BYTEA
          USING pgp_sym_encrypt(display_name,
                                current_setting('{ENCRYPTION_KEY_GUC}'))
        """
    )
    op.execute(
        f"""
        ALTER TABLE patient_cache
          ALTER COLUMN mrn TYPE BYTEA
          USING pgp_sym_encrypt(mrn,
                                current_setting('{ENCRYPTION_KEY_GUC}'))
        """
    )
    op.execute(
        f"""
        ALTER TABLE patient_cache
          ALTER COLUMN birth_date TYPE BYTEA
          USING pgp_sym_encrypt(birth_date::text,
                                current_setting('{ENCRYPTION_KEY_GUC}'))
        """
    )

    # ------------------------------------------------------------------
    # 5. Make PHI columns NOT NULL where the domain demands it
    #    display_name stays NOT NULL (was NOT NULL before)
    # ------------------------------------------------------------------


def downgrade() -> None:
    # Reverse: decrypt BYTEA back to plaintext, drop new columns.

    # 1. Decrypt PHI columns back to their original types
    op.execute(
        f"""
        ALTER TABLE patient_cache
          ALTER COLUMN display_name TYPE VARCHAR(255)
          USING pgp_sym_decrypt(display_name,
                                current_setting('{ENCRYPTION_KEY_GUC}'))
        """
    )
    op.execute(
        f"""
        ALTER TABLE patient_cache
          ALTER COLUMN mrn TYPE VARCHAR(64)
          USING pgp_sym_decrypt(mrn,
                                current_setting('{ENCRYPTION_KEY_GUC}'))
        """
    )
    op.execute(
        f"""
        ALTER TABLE patient_cache
          ALTER COLUMN birth_date TYPE DATE
          USING pgp_sym_decrypt(birth_date,
                                current_setting('{ENCRYPTION_KEY_GUC}'))::date
        """
    )

    # 2. Drop new columns
    op.drop_column("patient_cache", "mrn_bidx")
    op.drop_column("patient_cache", "cns")
    op.drop_column("patient_cache", "cpf")
