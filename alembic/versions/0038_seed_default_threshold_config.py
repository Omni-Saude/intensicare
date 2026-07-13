"""Sprint-1 Patient Safety — Seed default (tenant-global) threshold_config.

Revision ID: 0038
Revises: 0037
Create Date: 2026-07-12

Seeds the fallback (tenant-global: unit=NULL, bed_id=NULL) threshold_config
rows for MEWS and NEWS2 so every tenant has a safe default alert
configuration even before an operator sets unit/bed-specific overrides.

Thresholds and rationale are evidence-anchored (guideline_source /
evidence_doi columns) rather than arbitrary:

- MEWS  watch=3, urgent=4, critical=5
  Subbe CP et al. QJM 2001;94:521-6 — MEWS >=5 associated with increased
  mortality / ICU admission; >=4 is the response-trigger threshold.
  DOI: 10.1093/qjmed/94.10.521

- NEWS2 watch=3, urgent=5, critical=7
  Royal College of Physicians. NEWS2, 2017 — aggregate score 5-6 = medium
  clinical risk, >=7 = high clinical risk.

Uses tenant_id = 'default', which is the existing house convention for
the tenant-global/system scope (see src/intensicare/api/v1/admin.py and
src/intensicare/services/mpi_resolver.py).

The threshold_config.guideline_source / evidence_doi / evidence_level
columns are added idempotently here because no prior migration created
them, even though the ORM model (threshold_config.py) already declares
them.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0038"
down_revision: Union[str, None] = "0037"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_TENANT = "default"

SEED_ROWS = [
    {
        "score_type": "MEWS",
        "watch_threshold": 3,
        "urgent_threshold": 4,
        "critical_threshold": 5,
        "guideline_source": (
            "Subbe CP et al. QJM 2001;94:521-6 (MEWS ≥5 associado a "
            "↑mortalidade/admissão UTI; ≥4 gatilho de resposta)"
        ),
        "evidence_doi": "10.1093/qjmed/94.10.521",
    },
    {
        "score_type": "NEWS2",
        "watch_threshold": 3,
        "urgent_threshold": 5,
        "critical_threshold": 7,
        "guideline_source": (
            "Royal College of Physicians. NEWS2, 2017 (agregado 5-6 = "
            "medium, ≥7 = high)"
        ),
        "evidence_doi": None,
    },
]


def upgrade() -> None:
    # ── Idempotent column additions (model declares these, no prior
    #    migration created them) ─────────────────────────────────────────
    for col_name, col_type in [
        ("guideline_source", "TEXT"),
        ("evidence_doi", "VARCHAR(255)"),
        ("evidence_level", "VARCHAR(50)"),
    ]:
        op.execute(
            sa.text(
                f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'threshold_config'
                          AND column_name = '{col_name}'
                    ) THEN
                        ALTER TABLE threshold_config
                        ADD COLUMN {col_name} {col_type};
                    END IF;
                END $$;
                """
            )
        )

    # ── Idempotent seed of tenant-global default thresholds ────────────────
    # NB: threshold_config's unique constraint (tenant_id, unit, bed_id,
    # score_type) does not by itself dedupe rows where unit/bed_id are both
    # NULL (standard SQL treats NULL <> NULL), so we gate the insert with a
    # NOT EXISTS check. We intentionally do NOT also use ON CONFLICT here:
    # it requires a unique/exclusion constraint or index exactly matching
    # (tenant_id, unit, bed_id, score_type) to exist on the target table,
    # which is not guaranteed on every DB this migration runs against (e.g.
    # a dev DB created via metadata.create_all without that constraint) —
    # ON CONFLICT would then raise InvalidColumnReferenceError. The
    # WHERE NOT EXISTS guard alone is sufficient and portable.
    for row in SEED_ROWS:
        guideline_source = row["guideline_source"].replace("'", "''")
        evidence_doi_sql = (
            f"'{row['evidence_doi']}'" if row["evidence_doi"] else "NULL"
        )
        op.execute(
            sa.text(
                f"""
                INSERT INTO threshold_config (
                    tenant_id, unit, bed_id, score_type,
                    watch_threshold, urgent_threshold, critical_threshold,
                    guideline_source, evidence_doi,
                    updated_at, updated_by
                )
                SELECT
                    '{DEFAULT_TENANT}', NULL, NULL, '{row["score_type"]}',
                    {row["watch_threshold"]}, {row["urgent_threshold"]},
                    {row["critical_threshold"]},
                    '{guideline_source}', {evidence_doi_sql},
                    now(), 'migration:0038'
                WHERE NOT EXISTS (
                    SELECT 1 FROM threshold_config
                    WHERE tenant_id = '{DEFAULT_TENANT}'
                      AND unit IS NULL
                      AND bed_id IS NULL
                      AND score_type = '{row["score_type"]}'
                );
                """
            )
        )


def downgrade() -> None:
    op.execute(
        sa.text(
            f"""
            DELETE FROM threshold_config
            WHERE tenant_id = '{DEFAULT_TENANT}'
              AND unit IS NULL
              AND bed_id IS NULL
              AND score_type IN ('MEWS', 'NEWS2');
            """
        )
    )
