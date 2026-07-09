#!/usr/bin/env python3
"""Verify threshold units are canonical against known unit lists.

Reads YAML alert/threshold definitions and validates that unit strings
match the canonical registry. Currently a skeleton — extend as the
canonical unit registry grows.
"""
from __future__ import annotations

import sys
from pathlib import Path

# ── Canonical unit registry ──────────────────────────────────────────────
# Maps category -> set of accepted unit strings.
CANONICAL_UNITS: dict[str, set[str]] = {
    "vasopressor": {"mcg/kg/min", "mL/h"},
    "temperature": {"°C", "°F"},
    "respiratory_rate": {"rpm"},
    "oxygen": {"%", "L/min", "FiO2"},
    "pressure": {"mmHg", "cmH2O", "kPa"},
    "heart_rate": {"bpm"},
    "weight": {"kg", "g", "lb"},
    "lab": {"mg/dL", "mmol/L", "mEq/L", "g/dL", "U/L", "ng/mL", "pg/mL"},
    "volume": {"mL", "L", "mL/kg"},
    "time": {"h", "min", "s", "days"},
    "scoring": {"points", "score"},
    "ratio": {"", "ratio"},
}


def _find_yaml_files(root: Path) -> list[Path]:
    """Collect YAML files that might define threshold units."""
    candidates = []
    for pattern in ["**/*alerts*.yaml", "**/*thresholds*.yaml", "**/*units*.yaml"]:
        candidates.extend(root.glob(pattern))
    return sorted(set(candidates))


def _extract_units_from_yaml(path: Path) -> list[tuple[str, str]]:
    """Naive extraction of `unit:` keys from a YAML file.

    Returns [(file_stem, unit_string), ...].
    """
    import re
    results: list[tuple[str, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return results
    # Match lines like:  unit: "mmHg"  or  unit: mcg/kg/min
    for m in re.finditer(r'^\s*unit\s*:\s*["\']?([^"\'#\n]+)["\']?', text, re.MULTILINE):
        unit = m.group(1).strip().strip('"\'')
        results.append((path.stem, unit))
    return results


def main() -> int:
    repo_root = Path(__file__).parent.parent
    yaml_files = _find_yaml_files(repo_root)

    if not yaml_files:
        print("SKIP: No YAML threshold/alert files found — nothing to verify.")
        return 0

    all_canonical = {u for units in CANONICAL_UNITS.values() for u in units}
    errors: list[str] = []

    for yf in yaml_files:
        for stem, unit in _extract_units_from_yaml(yf):
            if unit not in all_canonical:
                errors.append(f"{stem}.yaml: unit='{unit}' not canonical")

    if errors:
        print(f"FAIL: {len(errors)} non-canonical unit(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("PASS: All threshold units canonical.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
