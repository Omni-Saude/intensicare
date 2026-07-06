#!/usr/bin/env python3
"""check_vector_coverage.py — Verify alert vector coverage completeness.

Scans all YAML alert catalogs in docs/plan/_work/alerts/ and checks:
1. Every alert_id has >= 1 test vector
2. Every alert with test_vectors has a compiled definition (condition)
3. Reports stats: total alerts, total vectors, alerts without vectors

Exit codes:
  0 — All alerts have vectors, all vectors valid
  1 — At least one alert lacks vectors, or vectors fail validation
"""

from __future__ import annotations

import pathlib
import sys
from typing import Any

import yaml


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
ALERTS_DIR = REPO_ROOT / "docs" / "plan" / "_work" / "alerts"


def load_all_catalogs() -> list[dict[str, Any]]:
    """Load all YAML catalogs."""
    catalogs = []
    if not ALERTS_DIR.exists():
        print(f"ERROR: Alerts directory not found: {ALERTS_DIR}", file=sys.stderr)
        sys.exit(1)

    yaml_files = sorted(ALERTS_DIR.glob("*.yaml"))
    if not yaml_files:
        print(f"ERROR: No YAML files found in {ALERTS_DIR}", file=sys.stderr)
        sys.exit(1)

    for yaml_file in yaml_files:
        try:
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            if data is None:
                print(f"WARNING: Empty YAML file: {yaml_file.name}", file=sys.stderr)
                continue
            if "alert_groups" not in data:
                print(f"WARNING: {yaml_file.name} missing 'alert_groups' key", file=sys.stderr)
                continue
            catalogs.append(data)
        except yaml.YAMLError as e:
            print(f"ERROR: Failed to parse {yaml_file.name}: {e}", file=sys.stderr)
            sys.exit(1)

    return catalogs


def check_coverage() -> tuple[int, int, list[str], list[str], int]:
    """Check coverage and return (total, with_vectors, missing, no_condition).

    Returns:
        total: Total number of alerts
        with_vectors: Number of alerts with >= 1 test vector
        missing: List of alert_ids without vectors
        no_condition: List of alert_ids without a condition string
    """
    catalogs = load_all_catalogs()
    seen_ids: set[str] = set()
    total = 0
    with_vectors = 0
    missing: list[str] = []
    no_condition: list[str] = []
    total_vectors = 0

    for catalog in catalogs:
        for group in catalog.get("alert_groups", []):
            for alert in group.get("alerts", []):
                alert_id = alert.get("alert_id", "UNKNOWN")

                # Check duplicate
                if alert_id in seen_ids:
                    print(f"WARNING: Duplicate alert_id: {alert_id}", file=sys.stderr)
                seen_ids.add(alert_id)
                total += 1

                # Check condition
                condition = alert.get("condition", "")
                if not condition or not condition.strip():
                    no_condition.append(alert_id)

                # Check vectors
                vectors = alert.get("test_vectors", [])
                if len(vectors) >= 1:
                    with_vectors += 1
                    total_vectors += len(vectors)
                else:
                    missing.append(alert_id)

    return total, with_vectors, missing, no_condition, total_vectors


def main() -> int:
    """Run coverage check. Exit 0 on success, 1 on failure."""
    print("=== Alert Vector Coverage Check ===\n")

    total, with_vectors, missing, no_condition, total_vectors = check_coverage()

    print(f"Total alerts:          {total}")
    print(f"Total test vectors:    {total_vectors}")
    print(f"Alerts with vectors:   {with_vectors}")
    print(f"Alerts without vectors: {len(missing)}")
    print(f"Alerts without condition: {len(no_condition)}")
    print()

    # Check 1: Minimum expected coverage
    if total < 50:
        print(f"WARNING: Expected >= 50 alerts, found {total}")
    if total_vectors < 266:
        print(f"WARNING: Expected >= 266 vectors, found {total_vectors}")

    # Check 2: Missing vectors
    if missing:
        print("ERROR: The following alerts have NO test vectors:")
        for aid in missing:
            print(f"  - {aid}")
        print()

    # Check 3: Missing conditions
    if no_condition:
        print("ERROR: The following alerts have NO condition:")
        for aid in no_condition:
            print(f"  - {aid}")
        print()

    # Coverage percentage
    coverage = (with_vectors / total * 100) if total > 0 else 0
    print(f"Coverage: {with_vectors}/{total} ({coverage:.1f}%)")

    if missing or no_condition:
        print("\n❌ FAILED: Some alerts lack vectors or conditions.")
        print("Run 'make check-vectors' to verify after fixing.")
        return 1

    print(f"\n✅ PASSED: All {total} alerts have test vectors and conditions.")
    print(f"   Total test vectors: {total_vectors}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
