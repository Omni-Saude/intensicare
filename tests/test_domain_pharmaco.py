"""Tests for pharmaco-interaction domain alerts (WO-030).

Verifies:
1. All test vectors from pharmaco-interaction.yaml pass (fire/no-fire/boundary).
2. run_pharmaco_batch() micro-batch mode evaluates all alerts correctly.
3. Alert compiler integration: evaluate_alert_definition works with drug context.
"""

from __future__ import annotations

import pathlib
from typing import Any

import pytest
import yaml

from maezo.rules.alert_compiler import evaluate_alert_definition
from maezo.services.domain_runners import run_pharmaco_batch

REPO_ROOT = pathlib.Path(__file__).parents[2]
PHARMACO_YAML = REPO_ROOT / "docs" / "plan" / "_work" / "alerts" / "pharmaco-interaction.yaml"


def _load_catalog() -> dict[str, Any]:
    with open(PHARMACO_YAML) as f:
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


class TestPharmacoAlertVectors:
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
                # (documented for edge-case awareness)
                pass
            else:
                pytest.fail(f"[{alert_id}] vector #{i}: unknown expect='{expected}'")


# ──────────────────────────────────────────────────────────────
# Micro-batch mode tests
# ──────────────────────────────────────────────────────────────


class TestPharmacoMicroBatch:
    """Test micro-batch evaluation via run_pharmaco_batch()."""

    def test_micro_batch_warfarin_nsaid_context(self) -> None:
        """Patient on both warfarin and NSAID with elevated INR."""
        ctx = {
            "on_warfarin": True,
            "on_nsaid": True,
            "inr": 4.5,
        }
        firing = run_pharmaco_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "PHARMA-WARF-NSAID-001" in alert_ids, (
            f"Expected WARF-NSAID-001 to fire. Firing: {alert_ids}"
        )
        assert "PHARMA-WARF-NSAID-002" in alert_ids, (
            f"Expected WARF-NSAID-002 to fire (INR 4.5). Firing: {alert_ids}"
        )

    def test_micro_batch_warfarin_only_no_fire(self) -> None:
        """Patient on warfarin only — no NSAID interaction."""
        ctx = {
            "on_warfarin": True,
            "on_nsaid": False,
            "inr": 3.0,
        }
        firing = run_pharmaco_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "PHARMA-WARF-NSAID-001" not in alert_ids
        assert "PHARMA-WARF-NSAID-002" not in alert_ids

    def test_micro_batch_polypharmacy_severe(self) -> None:
        """Patient with severe polypharmacy (15+ medications)."""
        ctx = {"medication_count": 16}
        firing = run_pharmaco_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "PHARMA-POLY-001" in alert_ids
        assert "PHARMA-POLY-002" in alert_ids

    def test_micro_batch_polypharmacy_moderate_only(self) -> None:
        """Patient with moderate polypharmacy (10-14 medications)."""
        ctx = {"medication_count": 12}
        firing = run_pharmaco_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "PHARMA-POLY-001" in alert_ids
        assert "PHARMA-POLY-002" not in alert_ids

    def test_micro_batch_qt_prolongation_critical(self) -> None:
        """Patient with QTc > 500 and QT-prolonging drug."""
        ctx = {
            "qt_drug_count": 2,
            "qtc_ms": 520,
        }
        firing = run_pharmaco_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "PHARMA-QT-001" in alert_ids  # >= 2 QT drugs
        assert "PHARMA-QT-002" in alert_ids  # QTc > 500 + drug
        assert "PHARMA-QT-003" in alert_ids  # QTc > 480

    def test_micro_batch_serotonin_maoi_ssri(self) -> None:
        """Patient on MAOI + SSRI — contraindicated."""
        ctx = {
            "on_maoi": True,
            "on_ssri": True,
            "serotonergic_drug_count": 3,
        }
        firing = run_pharmaco_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "PHARMA-SEROT-001" in alert_ids
        assert "PHARMA-SEROT-002" in alert_ids

    def test_micro_batch_triple_antithrombotic(self) -> None:
        """Patient on anticoagulant + dual antiplatelet."""
        ctx = {
            "on_anticoagulant": True,
            "antiplatelet_count": 2,
        }
        firing = run_pharmaco_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "PHARMA-ANTICOAG-001" in alert_ids  # triple therapy
        assert "PHARMA-ANTICOAG-002" in alert_ids  # any combo

    def test_micro_batch_nephrotoxic_critical(self) -> None:
        """Patient on nephrotoxic drug with elevated creatinine."""
        ctx = {
            "nephrotoxic_drug_count": 2,
            "creatinine": 3.0,
        }
        firing = run_pharmaco_batch(ctx)

        alert_ids = {a["alert_id"] for a in firing}
        assert "PHARMA-NEPHRO-001" in alert_ids  # >= 2 nephrotoxic
        assert "PHARMA-NEPHRO-002" in alert_ids  # + creatinine > 2

    def test_micro_batch_empty_context(self) -> None:
        """Empty context should not fire any alerts."""
        firing = run_pharmaco_batch({})
        # No alert should fire with empty context (all conditions use guards like is not None)
        assert len(firing) == 0, f"Expected no alerts, got: {firing}"

    def test_micro_batch_returns_metadata(self) -> None:
        """Verify firing alerts include all required metadata."""
        ctx = {
            "on_warfarin": True,
            "on_nsaid": True,
        }
        firing = run_pharmaco_batch(ctx)
        for alert in firing:
            assert "alert_id" in alert
            assert "name" in alert
            assert "severity" in alert
            assert "condition" in alert
            assert "description" in alert
            assert alert["alert_id"]  # non-empty
            assert alert["severity"] in ("info", "warning", "critical", "emergency", "unknown")
