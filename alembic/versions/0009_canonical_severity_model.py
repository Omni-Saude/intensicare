"""canonical severity model + algorithm_registry seed (WO-011 / AUDIT-008)

Revision ID: 0009
Revises: 0008
Create Date: 2026-07-05 18:00:00.000000

- Adiciona CHECK constraint em alert.severity para garantir valores canônicos
  (normal, watch, urgent, critical).
- Seed algorithm_registry com a entrada "severity-model-v1.0" para
  rastreabilidade da versão do modelo de severidade.
- Resolve AUDIT-008: backend watch/urgent/critical vs frontend info/warning/critical.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Canonical severity values (normal < watch < urgent < critical)
CANONICAL_SEVERITIES = ("normal", "watch", "urgent", "critical")

SEVERITY_MODEL_SEED = {
    "algorithm_version": "severity-model-v1.0",
    "score_type": "SEVERITY",
    "semver": "1.0.0",
    "spec_hash": "c4f8e9a21d0b67e3f51982a4d6c01e57b3f2a8904d761c9e82f3a45b6c01d789",
    "description": (
        "Canonical Severity Model v1.0 — normal < watch < urgent < critical. "
        "P0-10 highest-severity-wins. Triple-encoded (color+icon+shape). "
        "Resolves AUDIT-008 enum mismatch."
    ),
}


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Add CHECK constraint on alert.severity column
    # ------------------------------------------------------------------
    op.create_check_constraint(
        "ck_alert_severity_canonical",
        "alert",
        sa.text(
            f"severity = ANY(ARRAY[{', '.join(repr(s) for s in CANONICAL_SEVERITIES)}])"
        ),
    )

    # ------------------------------------------------------------------
    # 2. Seed algorithm_registry with severity model version
    # ------------------------------------------------------------------
    op.execute(
        f"""
        INSERT INTO algorithm_registry
            (algorithm_version, score_type, semver, spec_hash, description)
        VALUES
            ('{SEVERITY_MODEL_SEED['algorithm_version']}',
             '{SEVERITY_MODEL_SEED['score_type']}',
             '{SEVERITY_MODEL_SEED['semver']}',
             '{SEVERITY_MODEL_SEED['spec_hash']}',
             '{SEVERITY_MODEL_SEED['description']}')
        ON CONFLICT (algorithm_version) DO NOTHING
        """
    )


def downgrade() -> None:
    # 1. Remove the seed entry
    op.execute(
        f"""
        DELETE FROM algorithm_registry
        WHERE algorithm_version = '{SEVERITY_MODEL_SEED['algorithm_version']}'
        """
    )

    # 2. Drop the CHECK constraint
    op.drop_constraint("ck_alert_severity_canonical", "alert", type_="check")
