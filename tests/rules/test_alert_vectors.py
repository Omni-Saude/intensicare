"""L1 Rule-Vector Harness — YAML-driven alert evaluation tests.

Loads all alert catalog YAMLs from docs/plan/_work/alerts/*.yaml,
parametrizes test vectors, and evaluates via alert_compiler.evaluate_alert_definition().

Verifies:
- Fire vectors actually fire (expect='fire')
- No-fire vectors don't fire (expect='no-fire')
- Boundary vectors correct

Target: 50 alerts / 266 vectors across 9 catalogs.
"""

from __future__ import annotations

import pathlib
import sys
from typing import Any

import pytest
import yaml

# Ensure src/ is on path
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from intensicare.services.alert_compiler import AlertCompiler  # noqa: E402


# ──────────────────────────────────────────────────────────────
# Load all alert catalogs
# ──────────────────────────────────────────────────────────────

ALERTS_DIR = REPO_ROOT / "docs" / "plan" / "_work" / "alerts"


def _load_all_catalogs() -> list[dict[str, Any]]:
    """Load all YAML files from the alerts directory."""
    catalogs = []
    for yaml_file in sorted(ALERTS_DIR.glob("*.yaml")):
        with open(yaml_file) as f:
            catalogs.append(yaml.safe_load(f))
    return catalogs


def _collect_all_alerts() -> list[dict[str, Any]]:
    """Flatten all alerts from all catalogs (top-level 'alerts' key in YAMLs)."""
    alerts = []
    for catalog in _load_all_catalogs():
        for alert in catalog.get("alerts", []):
            alerts.append(alert)
    return alerts


def _collect_test_vectors() -> list[tuple[str, str, dict[str, Any], str]]:
    """Collect all test vectors as (alert_id, alert_name, inputs, expected) tuples."""
    vectors = []
    for catalog in _load_all_catalogs():
        for alert in catalog.get("alerts", []):
            alert_id = alert["alert_id"]
            alert_name = alert.get("name", alert_id)
            for tv in alert.get("test_vectors", []):
                vectors.append((
                    alert_id,
                    alert_name,
                    tv.get("inputs", {}),
                    tv.get("expected", "no-fire"),
                ))
    return vectors


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

ALL_ALERTS = _collect_all_alerts()
ALL_VECTORS = _collect_test_vectors()


@pytest.fixture(scope="session")
def all_alerts() -> list[dict[str, Any]]:
    return ALL_ALERTS


@pytest.fixture(scope="session")
def alert_by_id() -> dict[str, dict[str, Any]]:
    return {a["alert_id"]: a for a in ALL_ALERTS}


@pytest.fixture(scope="session")
def compiler() -> AlertCompiler:
    """Session-scoped AlertCompiler with all catalogs loaded."""
    c = AlertCompiler()
    c.load_all()
    return c


# ──────────────────────────────────────────────────────────────
# Tests: Structural
# ──────────────────────────────────────────────────────────────


class TestAlertCatalogStructure:
    """Verify the alert catalog YAMLs are well-formed."""

    def test_at_least_50_alerts(self, all_alerts: list[dict[str, Any]]) -> None:
        """We have at least 50 alerts defined across all catalogs."""
        assert len(all_alerts) >= 50, (
            f"Expected >= 50 alerts, found {len(all_alerts)}. "
            "WO-022 requires 50 alerts with test vectors."
        )

    def test_at_least_266_vectors(self) -> None:
        """We have at least 266 test vectors across all alerts."""
        assert len(ALL_VECTORS) >= 266, (
            f"Expected >= 266 test vectors, found {len(ALL_VECTORS)}. "
            "WO-022 requires 266 vectors across all alerts."
        )

    def test_every_alert_has_alert_id(self, all_alerts: list[dict[str, Any]]) -> None:
        for alert in all_alerts:
            assert "alert_id" in alert, f"Alert missing alert_id: {alert.get('name', 'unknown')}"
            assert alert["alert_id"], f"Alert has empty alert_id"

    def test_every_alert_has_condition(self, all_alerts: list[dict[str, Any]]) -> None:
        for alert in all_alerts:
            trigger = alert.get("trigger", {})
            logic = trigger.get("logic", "") if isinstance(trigger, dict) else ""
            assert logic.strip(), (
                f"Alert {alert.get('alert_id', 'unknown')} missing trigger.logic"
            )

    def test_every_alert_has_test_vectors(self, all_alerts: list[dict[str, Any]]) -> None:
        for alert in all_alerts:
            vectors = alert.get("test_vectors", [])
            assert len(vectors) >= 1, (
                f"Alert {alert.get('alert_id', 'unknown')} has no test vectors"
            )

    def test_every_alert_has_severity(self, all_alerts: list[dict[str, Any]]) -> None:
        valid_severities = {"normal", "watch", "urgent", "critical"}
        for alert in all_alerts:
            sev = alert.get("severity", "")
            assert sev in valid_severities, (
                f"Alert {alert.get('alert_id')} has invalid severity: {sev}"
            )

    def test_unique_alert_ids(self, all_alerts: list[dict[str, Any]]) -> None:
        seen: set[str] = set()
        for alert in all_alerts:
            aid = alert["alert_id"]
            assert aid not in seen, f"Duplicate alert_id: {aid}"
            seen.add(aid)

    def test_all_catalogs_loadable(self) -> None:
        """All 9 YAML catalogs are valid and loadable."""
        catalogs = list(ALERTS_DIR.glob("*.yaml"))
        assert len(catalogs) >= 9, f"Expected >= 9 catalogs, found {len(catalogs)}"
        for yaml_file in catalogs:
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            assert data is not None, f"Failed to parse: {yaml_file.name}"
            assert "alerts" in data, f"{yaml_file.name} missing 'alerts'"


# ──────────────────────────────────────────────────────────────
# Tests: Vector Evaluation
# ──────────────────────────────────────────────────────────────


def _make_test_id(alert_id: str, idx: object, input_data: dict[str, Any], expect: str) -> str:
    """Create a human-readable test ID."""
    # Truncate input for display
    input_str = ", ".join(f"{k}={v}" for k, v in sorted(input_data.items())[:4])
    if len(input_data) > 4:
        input_str += ", ..."
    return f"{alert_id}[{idx}]:{expect}"


@pytest.mark.parametrize(
    "alert_id, alert_name, input_data, expect",
    ALL_VECTORS,
    ids=[_make_test_id(*v) for v in ALL_VECTORS],
)
def test_vector_evaluation(
    alert_id: str,
    alert_name: str,
    input_data: dict[str, Any],
    expect: str,
    alert_by_id: dict[str, dict[str, Any]],
    compiler: AlertCompiler,
) -> None:
    """Each test vector evaluates correctly against its alert definition."""
    alert_def = alert_by_id[alert_id]
    assert alert_def is not None, f"Alert {alert_id} not found in catalog"

    result = compiler.evaluate_alert_definition(alert_id, input_data)

    if expect == "fire":
        assert result is True, (
            f"Alert '{alert_name}' ({alert_id}) should FIRE with input {input_data}, "
            f"but it did NOT fire. Condition: {alert_def.get('condition')}"
        )
    elif expect == "no-fire":
        assert result is False, (
            f"Alert '{alert_name}' ({alert_id}) should NOT FIRE with input {input_data}, "
            f"but it FIRED. Condition: {alert_def.get('condition')}"
        )
    elif expect == "boundary":
        # Boundary vectors should be exactly at threshold — they fire
        assert result is True, (
            f"Alert '{alert_name}' ({alert_id}) boundary should FIRE with input {input_data}, "
            f"but it did NOT fire. Condition: {alert_def.get('condition')}"
        )
    elif expect == "member-delivers":
        # member-delivers is a fire variant (domain-to-domain delivery)
        assert result is True, (
            f"Alert '{alert_name}' ({alert_id}) member-delivers should FIRE with input {input_data}, "
            f"but it did NOT fire. Condition: {alert_def.get('condition')}"
        )
    else:
        pytest.fail(f"Unknown expect value: {expect}")


# ──────────────────────────────────────────────────────────────
# Tests: Alert compilation
# ──────────────────────────────────────────────────────────────


class TestAlertCompilation:
    """Verify alert definitions compile correctly."""

    def test_all_alerts_compile_without_error(
        self, all_alerts: list[dict[str, Any]], compiler: AlertCompiler
    ) -> None:
        """Every alert definition should evaluate without throwing exceptions."""
        for alert in all_alerts:
            alert_id = alert["alert_id"]
            trigger = alert.get("trigger", {})
            logic = trigger.get("logic", "") if isinstance(trigger, dict) else ""
            # Try with minimal context — should not raise
            try:
                compiler.evaluate_alert_definition(alert_id, {})
            except Exception as e:
                pytest.fail(
                    f"Alert {alert_id} raised {type(e).__name__}: {e}\n"
                    f"Logic: {logic}"
                )

    def test_alerts_dont_fire_with_empty_context(
        self, all_alerts: list[dict[str, Any]], compiler: AlertCompiler
    ) -> None:
        """Alerts should not fire with empty context (missing→default behavior)."""
        for alert in all_alerts:
            result = compiler.evaluate_alert_definition(alert["alert_id"], {})
            # With empty context, most alerts should NOT fire
            # (they need data to trigger)
            assert result is False, (
                f"Alert {alert['alert_id']} fired with empty context. "
                f"Logic: {alert.get('trigger', {}).get('logic', '') if isinstance(alert.get('trigger'), dict) else ''}\n"
                "This may indicate the alert is too sensitive (always-on)."
            )
