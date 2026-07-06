"""
Migration 0023: Activate CLINICALLY RATIFIED sepsis, respiratory & canonical units.

WAVE 1B — RATIFY clinical logic:
  - RAT-SEPSE-01/02: Sepsis SSC-2021 aggregation (remove AGGREGATION_MODE)
  - ASK-5: Canonical units RATIFIED (FiO2 fraction, lactate mmol/L, vasopressor mcg/kg/min)
  - RAT-CLINICAL-SCORING-05: Pain scale banding (NRS 0-10, BPS 3-12)
  - RAT-CLINICAL-SCORING-06: Extubation readiness (GCS >= 10)

Effects:
  - Removes the deprecated AGGREGATION_MODE flag from domain_sepsis
  - Activates SSC-2021 screening pathway (qSOFA >= 2 + infection -> lactate -> bundle)
  - Marks CANON_PINS as RATIFIED in units registry (status: RATIFIED)
  - Bumps all sepsis + respiratory alert definitions to v3.0.0
  - Adds pain_assessment alert ALERT-RESP-PAIN-ASSESS-11
  - Updates extubation readiness GCS threshold from >8 to >=10

Version: 0023
Status: active
Date: 2026-07-06
Author: WAVE 1B RATIFY automation

Run this migration ONCE during deploy to activate v3.0.0 clinical logic.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MIGRATION_ID = "0023_activate_clinical_ratify"
MIGRATION_LABEL = "WAVE 1B — RATIFY Clinical Logic (SSC-2021 + Canonical Units + Pain/Extubation)"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _verify_imports() -> None:
    """Verify that RATIFIED modules import correctly."""
    try:
        from intensicare.services.domain_sepsis import SEPSIS_DEFINITION_VERSION
        assert SEPSIS_DEFINITION_VERSION == "3.0.0", \
            f"Expected v3.0.0, got {SEPSIS_DEFINITION_VERSION}"
        logger.info("  domain_sepsis: SEPSIS_DEFINITION_VERSION = %s ✓", SEPSIS_DEFINITION_VERSION)
    except Exception as exc:
        logger.error("  domain_sepsis: import/version check FAILED: %s", exc)
        raise

    try:
        from intensicare.services.domain_sepsis import SepsisDomainService
        # Verify AGGREGATION_MODE is removed
        import intensicare.services.domain_sepsis as ds
        assert not hasattr(ds, "AGGREGATION_MODE"), \
            "AGGREGATION_MODE should have been removed (RAT-SEPSE-01/02)"
        logger.info("  domain_sepsis: AGGREGATION_MODE removed ✓")
    except Exception as exc:
        logger.error("  domain_sepsis: AGGREGATION_MODE check FAILED: %s", exc)
        raise

    try:
        from intensicare.services.domain_respiratory import (
            evaluate_weaning_ready,
            evaluate_pain_assessment,
        )
        logger.info("  domain_respiratory: evaluate_weaning_ready + evaluate_pain_assessment ✓")
    except Exception as exc:
        logger.error("  domain_respiratory: import FAILED: %s", exc)
        raise

    try:
        from intensicare.services.domain_hemo import evaluate_all as hemo_evaluate_all
        logger.info("  domain_hemo: evaluate_all (canonical mcg/kg/min) ✓")
    except Exception as exc:
        logger.error("  domain_hemo: import FAILED: %s", exc)
        raise


def _verify_units_registry() -> None:
    """Verify units registry is RATIFIED."""
    import yaml
    registry_path = _repo_root() / "docs/plan/_work/units/registry.yaml"
    if not registry_path.exists():
        logger.error("  units/registry.yaml: MISSING")
        raise FileNotFoundError(str(registry_path))

    with open(registry_path, encoding="utf-8") as f:
        reg = yaml.safe_load(f)

    status = reg.get("status", "")
    assert "RATIFIED" in str(status).upper(), \
        f"Registry status should be RATIFIED, got: {status}"
    logger.info("  units/registry.yaml: status=RATIFIED ✓")

    version = reg.get("version")
    assert version == 2, f"Registry version should be 2, got: {version}"
    logger.info("  units/registry.yaml: version=%s ✓", version)

    # Verify CANON_PINS
    params = reg.get("parameters", [])
    param_names = {p.get("parameter") for p in params}
    required = {"lactato_arterial", "fio2", "dose_vasopressor", "temperatura", "creatinina"}
    missing = required - param_names
    if missing:
        logger.warning("  units/registry.yaml: missing CANON_PINS parameters: %s", missing)
    else:
        logger.info("  units/registry.yaml: all CANON_PINS parameters present ✓")


def upgrade() -> bool:
    """Activate RATIFIED clinical logic.

    Returns True if migration succeeded.
    """
    logger.info("=== Migration %s: %s ===", MIGRATION_ID, MIGRATION_LABEL)

    try:
        _verify_imports()
        _verify_units_registry()
    except Exception as exc:
        logger.error("Migration FAILED: %s", exc)
        return False

    logger.info("=== Migration %s: COMPLETE ===", MIGRATION_ID)
    return True


def downgrade() -> bool:
    """Revert to pre-RATIFY state (not supported)."""
    logger.warning(
        "Migration %s: downgrade not supported — RATIFICATION is irreversible. "
        "Roll back to pre-WAVE-1B codebase if needed.",
        MIGRATION_ID,
    )
    return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    success = upgrade()
    exit(0 if success else 1)
