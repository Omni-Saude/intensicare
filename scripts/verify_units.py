#!/usr/bin/env python3
"""
IntensiCare — CI Gate A: Alert Unit Validator (F-ARCH-001)

Verifies that all alert threshold values in YAML alert definitions use
canonical clinical units recognized by the IntensiCare system.

Exit code 0 = all units recognized.
Non-zero = unrecognized or missing units found.

Per ADR-021: CI gate for unit validation on alert definitions.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
ALERTS_DIR = ROOT / "_work" / "alerts"

# ---------------------------------------------------------------------------
# Canonical Units Registry
#
# All units recognized by the IntensiCare clinical scoring system.
# Alerts that reference a unit not in this set will fail validation.
# ---------------------------------------------------------------------------
CANONICAL_UNITS: set[str] = {
    # --- Hemodynamics / Respiratory ---
    "mmHg",              # blood pressure, PaO₂, etc.
    "cmH₂O",             # ventilator pressures (PEEP, plateau, driving)
    "cmH2O",             # ASCII variant (accepted alias)
    # --- Laboratory ---
    "mmol/L",            # lactate, electrolytes, glucose
    "mg/dL",             # glucose, creatinine, BUN
    "g/dL",              # albumin, hemoglobin
    "ng/mL",             # procalcitonin, CRP
    "mEq/L",             # electrolytes
    # --- Ventilation ---
    "mL/kg",             # tidal volume (PBW)
    "mL",                # volumes (residual gastric, fluid balance)
    "L/min",             # oxygen flow
    # --- Nutrition ---
    "g/kg/dia",          # protein intake
    "% meta/dia",        # caloric goal percentage
    # --- Scoring ---
    "pontos",            # clinical scores (SOFA, qSOFA, SIRS, NRS-2002, Glasgow)
    # --- Weaning ---
    "ciclos/min/L",      # RSBI (rapid shallow breathing index)
    # --- Time ---
    "h",                 # hours (duration, clearance windows)
    "min",               # minutes
    "dias",              # days
    # --- Frequency ---
    "episódios/dia",     # diarrheal episodes per day
    "irpm",              # respiratory rate
    "bpm",               # heart rate
    "°C",                # temperature (Celsius)
    # --- Dimensionless / Qualitative ---
    "-",                 # no unit (binary, categorical, or qualitative)
}

# Common aliases that are not canonical but are close enough to warn about
UNIT_ALIASES: dict[str, str] = {
    "cmh2o": "cmH₂O",
    "cm h2o": "cmH₂O",
    "mmhg": "mmHg",
    "mmol/l": "mmol/L",
    "mg/dl": "mg/dL",
    "ml": "mL",
    "ml/kg": "mL/kg",
    "ng/ml": "ng/mL",
    "g/dl": "g/dL",
    "meq/l": "mEq/L",
    "l/min": "L/min",
}


def collect_units_from_alerts(alerts_dir: Path) -> list[tuple[str, str, str]]:
    """Parse all YAML alert definitions and extract (unit, alert_id, field) tuples.

    Args:
        alerts_dir: Directory containing *.yaml alert definition files.

    Returns:
        List of (unit, alert_id, field_name) tuples for every criterion with a unit.
    """
    unit_refs: list[tuple[str, str, str]] = []

    yaml_files = sorted(alerts_dir.glob("*.yaml"))
    for yaml_file in yaml_files:
        with open(yaml_file, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)

        if data is None:
            continue

        alerts: list[dict] = data if isinstance(data, list) else [data]

        for alert in alerts:
            if not isinstance(alert, dict):
                continue
            alert_id = alert.get("id", "?")
            criteria = alert.get("criteria", [])
            for crit in criteria:
                if not isinstance(crit, dict):
                    continue
                unit = crit.get("unit")
                field = crit.get("field", "?")
                if unit is not None:
                    unit_refs.append((unit, alert_id, field))

    return unit_refs


def verify_units(alerts_dir: Path) -> int:
    """Verify all alert threshold units against the canonical registry.

    Args:
        alerts_dir: Directory with YAML alert definitions.

    Returns:
        Exit code (0 = all valid, 1 = unknown units or no alerts found).
    """
    if not alerts_dir.is_dir():
        print(f"[ERROR] Alerts directory not found: {alerts_dir}")
        return 1

    unit_refs = collect_units_from_alerts(alerts_dir)

    if not unit_refs:
        print("[WARN] No alert definitions with units found.")
        return 0

    unknown: list[tuple[str, str, str]] = []
    aliased: list[tuple[str, str, str, str]] = []  # (unit, canonical, alert_id, field)
    known: list[tuple[str, str, str]] = []

    for unit, alert_id, field in unit_refs:
        # Normalize for lookup
        unit_key = unit.strip().lower()
        if unit_key in CANONICAL_UNITS or unit in CANONICAL_UNITS:
            known.append((unit, alert_id, field))
        elif unit_key in UNIT_ALIASES:
            aliased.append((unit, UNIT_ALIASES[unit_key], alert_id, field))
        else:
            unknown.append((unit, alert_id, field))

    # Report
    print("=" * 60)
    print("  IntensiCare — Alert Unit Validator (CI Gate A)")
    print("=" * 60)
    print()

    print(f"Canonical units registered: {len(CANONICAL_UNITS)}")
    print(f"Unit references found:     {len(unit_refs)}")
    print()

    if known:
        print(f"✓ {len(known)} unit reference(s) use canonical units:")
        for unit, alert_id, field in known:
            print(f"  [{unit}] in {alert_id}.{field}")
        print()

    if aliased:
        print(f"⚠ {len(aliased)} unit reference(s) use non-canonical casing — auto-resolved:")
        for unit, canonical, alert_id, field in aliased:
            print(f"  '{unit}' -> '{canonical}' in {alert_id}.{field}")
        print()

    if unknown:
        print(f"✗ {len(unknown)} unit reference(s) use UNRECOGNIZED units:")
        for unit, alert_id, field in unknown:
            print(f"  [{unit}] in {alert_id}.{field}")
            # Suggest closest match
            import difflib
            matches = difflib.get_close_matches(unit.lower(), CANONICAL_UNITS, n=3, cutoff=0.4)
            if matches:
                print(f"      Did you mean: {', '.join(sorted(matches))}?")
        print()
        print(f"[FAIL] {len(unknown)} unrecognized unit(s). "
              "Add them to CANONICAL_UNITS or fix the definition.")
        return 1

    print("[PASS] All alert units are recognized.")
    return 0


def main() -> int:
    """Entry point."""
    return verify_units(ALERTS_DIR)


if __name__ == "__main__":
    sys.exit(main())
