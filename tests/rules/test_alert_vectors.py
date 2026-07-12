"""L1 Rule-Vector Harness — YAML-driven alert validation.

Loads alert test vectors from docs/plan/_work/alerts/*.yaml and validates:
- Alert triggers correctly at specified thresholds
- Alert does NOT trigger below thresholds
- Severity assignment is correct
- Multi-parameter rules work (AND/OR logic)

The YAML files follow the IntensiCare v2 alert specification format:
  domain: <name>
  alerts:
    - alert_id: ALERT-...
      severity: watch|urgent|critical
      test_vectors:
        - {id: TV-1, kind: fire|no-fire|boundary, inputs: {...}, expected: fire|no-fire, note: "..."}

Full scorer integration requires wiring to actual MEWS/NEWS2/SOFA/qSOFA implementations
(deferred). For now, this harness validates vector structure, counts, and consistency.
"""

from pathlib import Path
from typing import Any

import pytest
import yaml

VECTORS_DIR = Path(__file__).parent.parent.parent / "docs" / "plan" / "_work" / "alerts"


def load_vectors() -> list[dict[str, Any]]:
    """Load all YAML alert vectors.

    Each YAML file has a top-level ``alerts:`` list. Each alert may contain
    a ``test_vectors:`` list.  We flatten all test vectors from all alerts
    into a single list, annotating each vector with its parent alert metadata
    so the parametrized test runner can skip misconfigured vectors individually.
    """
    vectors: list[dict[str, Any]] = []
    if not VECTORS_DIR.exists():
        return vectors

    for yaml_file in sorted(VECTORS_DIR.glob("*.yaml")):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            continue

        domain = data.get("domain", yaml_file.stem)
        alerts = data.get("alerts", [])

        for alert in alerts:
            if not isinstance(alert, dict):
                continue
            alert_id = alert.get("alert_id", "unknown")
            severity = alert.get("severity", "watch")
            # Some alerts have status via reconciliation; skip deferred ones
            reconciliation = alert.get("reconciliation", [])
            alert_status = None
            if reconciliation and isinstance(reconciliation, list):
                alert_status = reconciliation[0].get("status") if reconciliation else None
            if alert_status in ("deferred", "ratify"):
                continue

            tvs = alert.get("test_vectors", [])
            if not isinstance(tvs, list):
                continue

            for tv in tvs:
                if not isinstance(tv, dict):
                    continue
                # Annotate the vector with parent context
                tv["_domain"] = domain
                tv["_alert_id"] = alert_id
                tv["_alert_severity"] = severity
                vectors.append(tv)

    return vectors


# --- Parametrize fixture ---------------------------------------------------

ALL_VECTORS = load_vectors()


def _vector_id(vector: dict[str, Any]) -> str:
    """Build a stable, human-readable test ID from a vector."""
    vid = vector.get("id", "unknown")
    aid = vector.get("_alert_id", "?")
    return f"{aid}/{vid}"


VECTOR_IDS = [_vector_id(v) for v in ALL_VECTORS]


@pytest.mark.parametrize("vector", ALL_VECTORS, ids=VECTOR_IDS)
def test_alert_vector_structure(vector: dict[str, Any]) -> None:
    """Every YAML vector must have the required fields and valid values."""
    vector_id = _vector_id(vector)

    # Required top-level fields
    assert "id" in vector, f"Vector {vector_id} missing id"
    assert "kind" in vector, f"Vector {vector_id} missing kind"
    assert "expected" in vector, f"Vector {vector_id} missing expected"
    assert "inputs" in vector, f"Vector {vector_id} missing inputs"

    # Valid kind values
    assert vector["kind"] in (
        "fire",
        "no-fire",
        "boundary",
    ), f"Vector {vector_id}: invalid kind '{vector['kind']}'"

    # Valid expected values
    assert vector["expected"] in (
        "fire",
        "no-fire",
    ), f"Vector {vector_id}: invalid expected '{vector['expected']}'"

    # Consistency: kind="fire" implies expected="fire"
    if vector["kind"] == "fire":
        assert vector["expected"] == "fire", (
            f"Vector {vector_id}: kind=fire but expected={vector['expected']}"
        )

    # Consistency: kind="no-fire" implies expected="no-fire"
    if vector["kind"] == "no-fire":
        assert vector["expected"] == "no-fire", (
            f"Vector {vector_id}: kind=no-fire but expected={vector['expected']}"
        )

    # Inputs must be a dict
    assert isinstance(vector["inputs"], dict), (
        f"Vector {vector_id}: inputs must be a dict, got {type(vector['inputs']).__name__}"
    )
    assert len(vector["inputs"]) > 0, f"Vector {vector_id}: inputs must not be empty"

    # Parent alert metadata (set by load_vectors)
    assert "_domain" in vector, f"Vector {vector_id} missing _domain annotation"
    assert "_alert_id" in vector, f"Vector {vector_id} missing _alert_id annotation"
    assert "_alert_severity" in vector, f"Vector {vector_id} missing _alert_severity annotation"

    # Domain should match the file it came from
    assert vector["_domain"] in (
        "aki",
        "correlation-engine",
        "early-warning-scores",
        "electrolyte",
        "hemodynamics",
        "neuro-sedation",
        "pharmaco-interaction",
        "respiratory",
        "sepsis",
    ), f"Vector {vector_id}: unknown domain '{vector['_domain']}'"


def test_vectors_loaded() -> None:
    """Sanity: at least some vectors were loaded from the YAML corpus."""
    assert len(ALL_VECTORS) > 0, (
        "No vectors loaded — check docs/plan/_work/alerts/*.yaml exist and contain test_vectors"
    )
    # Log summary for visibility in test output
    domains = {v["_domain"] for v in ALL_VECTORS}
    print(f"\n  Loaded {len(ALL_VECTORS)} vectors across {len(domains)} domains: {sorted(domains)}")


def test_vectors_have_fire_and_nofire() -> None:
    """Every domain should have at least one fire and one no-fire vector."""
    from collections import defaultdict

    domain_kinds: dict[str, set[str]] = defaultdict(set)
    for v in ALL_VECTORS:
        domain_kinds[v["_domain"]].add(v["expected"])

    for domain, kinds in sorted(domain_kinds.items()):
        assert "fire" in kinds, f"Domain '{domain}' has no fire vectors"
        assert "no-fire" in kinds, f"Domain '{domain}' has no no-fire vectors"


@pytest.mark.parametrize("vector", ALL_VECTORS, ids=VECTOR_IDS)
def test_alert_vector_severity_consistent(vector: dict[str, Any]) -> None:
    """Alert severity must be one of the allowed values."""
    severity = vector["_alert_severity"]
    assert severity in ("normal", "watch", "urgent", "critical"), (
        f"Vector {_vector_id(vector)}: invalid severity '{severity}'"
    )
