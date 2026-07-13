"""Tests for neuro-sedation (delirium) domain alerts (WO-031).

Verifies:
1. All test vectors from neuro-sedation.yaml pass (fire/no-fire/boundary).
2. run_delirium_batch() micro-batch mode evaluates all alerts correctly.
3. Alert compiler integration: evaluate_alert_definition works with delirium context.
"""

from __future__ import annotations

import pathlib
from typing import Any

from maezo.rules.alert_compiler import evaluate_alert_definition
from maezo.services.domain_runners import run_delirium_batch
import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).parents[2]
NEURO_SEDATION_YAML = REPO_ROOT / "docs" / "plan" / "_work" / "alerts" / "neuro-sedation.yaml"


def _load_catalog() -> dict[str, Any]:
    with open(NEURO_SEDATION_YAML) as f:
        return yaml.safe_load(f)  # type: ignore[no-any-return]


def _flatten_alerts(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten all alerts from all groups."""
    alerts: list[dict[str, Any]] = []
    for group in catalog.get("alert_groups", []):
        alerts.extend(group.get("alerts", []))
    return alerts


# ──────────────────────────────────────────────────────────────
# Test vectors from YAML (fire/no-fire)
# ──────────────────────────────────────────────────────────────


class TestDeliriumAlertVectors:
    """Test each alert definition's test vectors from the YAML catalog."""

    @pytest.mark.parametrize(
        "alert",
        _flatten_alerts(_load_catalog()),
        ids=lambda a: a.get("alert_id", "?"),
    )
    def test_alert_vectors(self, alert: dict[str, Any]) -> None:
        alert_id = alert.get("alert_id", "?")
        test_vectors = alert.get("test_vectors", [])
        assert test_vectors, f"Alert {alert_id} has no test vectors"

        for i, tv in enumerate(test_vectors):
            inp = tv.get("input", {})
            expected = tv.get("expect")

            result = evaluate_alert_definition(alert, inp)
            fires = result is True

            if expected == "fire":
                assert fires, (
                    f"[{alert_id}] vector #{i}: expected FIRE, got NO-FIRE\n"
                    f"  condition: {alert.get('condition')}\n"
                    f"  input: {inp}"
                )
            elif expected == "no-fire":
                assert not fires, (
                    f"[{alert_id}] vector #{i}: expected NO-FIRE, got FIRE\n"
                    f"  condition: {alert.get('condition')}\n"
                    f"  input: {inp}"
                )
            elif expected == "boundary":
                # Boundary: fires on either side is acceptable
                pass
            else:
                pytest.fail(f"[{alert_id}] vector #{i}: unknown expect='{expected}'")


# ──────────────────────────────────────────────────────────────
# Micro-batch mode tests
# ──────────────────────────────────────────────────────────────


class TestDeliriumMicroBatch:
    """Test micro-batch evaluation via run_delirium_batch()."""

    def test_micro_batch_cam_icu_hyperactive(self) -> None:
        """Patient with CAM-ICU positive + hyperactive delirium (RASS >= 2)."""
        ctx = {
            "cam_icu_positive": True,
            "rass_score": 3,
        }
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "DELIR-CAM-001" in alert_ids
        assert "DELIR-CAM-002" in alert_ids  # hyperactive
        assert "DELIR-CAM-003" not in alert_ids  # not hypoactive

    def test_micro_batch_cam_icu_hypoactive(self) -> None:
        """Patient with CAM-ICU positive + hypoactive delirium (RASS <= -2)."""
        ctx = {
            "cam_icu_positive": True,
            "rass_score": -3,
        }
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "DELIR-CAM-001" in alert_ids
        assert "DELIR-CAM-002" not in alert_ids  # not hyperactive
        assert "DELIR-CAM-003" in alert_ids  # hypoactive

    def test_micro_batch_cam_icu_no_delirium(self) -> None:
        """Patient without delirium."""
        ctx = {
            "cam_icu_positive": False,
            "rass_score": 0,
        }
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "DELIR-CAM-001" not in alert_ids
        assert "DELIR-CAM-002" not in alert_ids
        assert "DELIR-CAM-003" not in alert_ids

    def test_micro_batch_deep_sedation(self) -> None:
        """Patient with RASS -5 (deep sedation)."""
        ctx = {"rass_score": -5}
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "SED-RASS-001" in alert_ids  # RASS <= -4

    def test_micro_batch_moderate_sedation(self) -> None:
        """Patient with RASS -3 (moderate sedation)."""
        ctx = {"rass_score": -3}
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "SED-RASS-002" in alert_ids  # RASS == -3

    def test_micro_batch_agitation(self) -> None:
        """Patient with RASS 4 (severe agitation)."""
        ctx = {"rass_score": 4}
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "SED-RASS-003" in alert_ids  # RASS >= 3
        assert "SED-RASS-001" not in alert_ids  # not deeply sedated

    def test_micro_batch_rass_target_out_of_range(self) -> None:
        """Patient with RASS outside prescribed target range."""
        ctx = {
            "rass_score": -4,
            "rass_target_min": -2,
            "rass_target_max": 0,
        }
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "SED-RASS-004" in alert_ids  # out of range
        assert "SED-RASS-001" in alert_ids  # also RASS <= -4

    def test_micro_batch_rass_target_in_range(self) -> None:
        """Patient with RASS within prescribed target range."""
        ctx = {
            "rass_score": -1,
            "rass_target_min": -2,
            "rass_target_max": 0,
        }
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "SED-RASS-004" not in alert_ids  # in range

    def test_micro_batch_sat_overdue(self) -> None:
        """Patient overdue for SAT (> 24h)."""
        ctx = {"hours_since_last_sat": 48}
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "SED-SAT-001" in alert_ids

    def test_micro_batch_sat_not_overdue(self) -> None:
        """Patient with SAT performed within 24h."""
        ctx = {"hours_since_last_sat": 12}
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "SED-SAT-001" not in alert_ids

    def test_micro_batch_sat_no_documented_contraindication(self) -> None:
        """SAT not performed and no documented contraindication."""
        ctx = {
            "sat_performed": False,
            "sat_contraindication_documented": False,
        }
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "SED-SAT-002" in alert_ids

    def test_micro_batch_sat_contraindicated(self) -> None:
        """SAT not performed but contraindication documented — no alert."""
        ctx = {
            "sat_performed": False,
            "sat_contraindication_documented": True,
        }
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "SED-SAT-002" not in alert_ids

    def test_micro_batch_analgesia_gap(self) -> None:
        """High pain with sedation increase but no analgesia bolus."""
        ctx = {
            "sedation_dose_increased": True,
            "cpot_score": 5,
            "analgesia_bolus_count": 0,
        }
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "SED-ANALG-001" in alert_ids
        assert "SED-ANALG-002" in alert_ids  # CPOT >= 4

    def test_micro_batch_delirium_risk_elderly_benzo(self) -> None:
        """Elderly patient on benzodiazepine."""
        ctx = {
            "on_benzodiazepine": True,
            "age": 75,
        }
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "DELIR-RISK-002" in alert_ids

    def test_micro_batch_delirium_with_restraints(self) -> None:
        """Patient delirious AND physically restrained — emergency."""
        ctx = {
            "delirious": True,
            "restrained": True,
        }
        firing = run_delirium_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "DELIR-RISK-003" in alert_ids

    def test_micro_batch_empty_context(self) -> None:
        """Empty context should not fire any alerts."""
        firing = run_delirium_batch({})
        assert len(firing) == 0, f"Expected no alerts, got: {firing}"

    def test_micro_batch_returns_metadata(self) -> None:
        """Verify firing alerts include all required metadata."""
        ctx = {
            "cam_icu_positive": True,
            "rass_score": 3,
        }
        firing = run_delirium_batch(ctx)
        for alert in firing:
            assert "alert_id" in alert
            assert "name" in alert
            assert "severity" in alert
            assert "condition" in alert
            assert "description" in alert
            assert alert["alert_id"]
            assert alert["severity"] in ("info", "warning", "critical", "emergency", "unknown")
