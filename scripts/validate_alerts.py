#!/usr/bin/env python3
"""IntensiCare — Trilhas Engine Alert Validator (F-ARCH-001/002)

Validates pathway YAML definitions against three CI gates:

  Gate A — Unit Resolution:
    Every input.unit and criteria[n].predicate.unit must resolve in the
    canonical units registry (imported from scripts/verify_units.py).

  Gate B — Band Partition:
    For every graded (bands-based) predicate, the bands must partition the
    input domain with no gaps, no overlaps, and no unreachable bands.
    null upper-bound = positive infinity.
    In addition to the hand-rolled partition check above, Gate B also runs
    every predicate through the REAL production PredicateCompiler
    (intensicare.services.trilhas_compiler) — the same code path
    TrilhasEngine uses at runtime. This catches anything that could drift
    between this script's reimplementation and the actual compiler,
    including discontinuous bands and a last band that is closed (has a
    non-null upper bound) instead of covering to +∞.

  Gate C — Facade ≡ Predicate:
    If a predicate declares a `rationale` field, the validator renders the
    predicate AST to human-readable text and asserts it matches (normalized).
    This enforces that the rendered facade equals the actual predicate logic.

Usage:
    python scripts/validate_alerts.py --gate A --defs _work/alerts/pathways/
    python scripts/validate_alerts.py --gate B --defs _work/alerts/pathways/
    python scripts/validate_alerts.py --gate A|B|C  (all gates)

Per ADR-0020: build-time defect elimination.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Make the production compiler importable without requiring the caller to
# set PYTHONPATH — keeps this script standalone-executable exactly as
# before (`python scripts/validate_alerts.py ...`), per the existing CI
# workflow invocation (.github/workflows/validate-alerts.yml), while still
# letting Gate B exercise the REAL PredicateCompiler (see Gate B docstring
# above).
# ---------------------------------------------------------------------------
_REPO_ROOT_FOR_IMPORT = Path(__file__).resolve().parent.parent
_SRC_DIR = _REPO_ROOT_FOR_IMPORT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from intensicare.services.trilhas_compiler import PredicateCompiler  # noqa: E402

# ---------------------------------------------------------------------------
# Canonical unit registry (source: scripts/verify_units.py)
# ---------------------------------------------------------------------------
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
    "ratio": {"", "ratio", "ciclos/min/L", "dimensionless"},
    "nutrition": {"g/kg/dia", "kcal/kg/dia", "episódios/dia"},
    "events": {"episodios/dia", "episódios/dia"},
}

ALL_CANONICAL: set[str] = {u for units in CANONICAL_UNITS.values() for u in units}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_defs(defs_dir: Path) -> list[dict]:
    """Load all pathway YAML definitions from a directory.

    Each YAML file is expected to contain either a single pathway dict
    (with top-level keys: pathway, evaluation, criteria, states) or a
    list of such dicts.

    Returns:
        Flat list of pathway definition dicts.
    """
    definitions: list[dict] = []
    yaml_files = sorted(defs_dir.glob("*.yaml"))
    if not yaml_files:
        yaml_files = sorted(defs_dir.glob("*.yml"))
    if not yaml_files:
        print(f"[WARN] No YAML/YML files found in {defs_dir}")
        return definitions

    for yf in yaml_files:
        print(f"[LOAD] {yf.relative_to(defs_dir.parent.parent)}")
        with open(yf, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if data is None:
            continue
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item["_source_file"] = str(yf)
                    definitions.append(item)
        elif isinstance(data, dict):
            data["_source_file"] = str(yf)
            definitions.append(data)
    return definitions


def _collect_units(definition: dict) -> list[tuple[str, str, str]]:
    """Collect (source, field_path, unit) triples from a pathway definition.

    Returns list of (source_file, field_path, unit_string).
    """
    units: list[tuple[str, str, str]] = []
    src = definition.get("_source_file", "?")

    # Inputs
    evaluation = definition.get("evaluation", {})
    inputs = evaluation.get("inputs", [])
    for i, inp in enumerate(inputs):
        u = inp.get("unit")
        if u:
            units.append((src, f"evaluation.inputs[{i}].unit", u))

    # Criteria predicates
    criteria_list = definition.get("criteria", [])
    for ci, crit in enumerate(criteria_list):
        pred = crit.get("predicate", {})
        u = pred.get("unit")
        if u:
            units.append((src, f"criteria[{ci}].predicate.unit", u))
        # Recurse into composite sub-predicates
        sub_predicates = pred.get("sub_predicates", [])
        for si, sp in enumerate(sub_predicates):
            su = sp.get("unit")
            if su:
                units.append(
                    (src, f"criteria[{ci}].predicate.sub_predicates[{si}].unit", su)
                )

    return units


# ---------------------------------------------------------------------------
# Gate A: Unit Resolution
# ---------------------------------------------------------------------------

def gate_a_unit_resolution(defs: list[dict]) -> int:
    """Validate every unit string resolves in the canonical unit registry.

    Returns: 0 on pass, 1 on failure.
    """
    errors: list[str] = []
    for d in defs:
        for src, path, unit in _collect_units(d):
            if unit not in ALL_CANONICAL:
                errors.append(f"{src}: {path}='{unit}' — NOT CANONICAL")

    if errors:
        print(f"FAIL [Gate A]: {len(errors)} non-canonical unit(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    total = sum(len(_collect_units(d)) for d in defs)
    print(f"PASS [Gate A]: {total} unit(s) resolved in canonical registry.")
    return 0


# ---------------------------------------------------------------------------
# Gate B: Band Partition
# ---------------------------------------------------------------------------

def _validate_bands(
    bands: list[dict], src: str, path: str
) -> list[str]:
    """Validate that a list of bands partitions the domain without gaps/overlaps.

    Each band: {"range": [low, high], ...} where high=None means infinity.

    Returns list of error strings (empty = valid).
    """
    errors: list[str] = []

    if not bands:
        return errors

    # Extract and sort bands by lower bound
    parsed: list[tuple[float, float | None, dict]] = []
    for i, band in enumerate(bands):
        rng = band.get("range", [])
        if len(rng) != 2:
            errors.append(
                f"{src}: {path}[{i}].range must have exactly 2 elements, got {len(rng)}"
            )
            continue
        low, high = rng[0], rng[1]
        if not isinstance(low, (int, float)):
            errors.append(
                f"{src}: {path}[{i}].range[0] must be numeric, got {type(low).__name__}"
            )
            continue
        if high is not None and not isinstance(high, (int, float)):
            errors.append(
                f"{src}: {path}[{i}].range[1] must be numeric or null, got {type(high).__name__}"
            )
            continue
        if high is not None and high <= low:
            errors.append(
                f"{src}: {path}[{i}] range [{low}, {high}] has high <= low"
            )
            continue
        parsed.append((float(low), float(high) if high is not None else None, band))

    if errors:
        return errors  # can't validate further with broken ranges

    # Sort by lower bound
    parsed.sort(key=lambda x: x[0])

    # Check first band starts at negative infinity or 0 (allow 0-start)
    # Actually, clinical domains often start at 0, but could also start at
    # negative values (e.g., NIF). We just check continuity.

    # Check for gaps
    for i in range(len(parsed) - 1):
        curr_high = parsed[i][1]
        next_low = parsed[i + 1][0]
        if curr_high is None:
            errors.append(
                f"{src}: {path}[{i}] has infinite upper bound but is not the last band"
            )
        elif curr_high != next_low:
            # Allow small floating-point tolerance
            if abs(curr_high - next_low) > 1e-9:
                rng_curr = parsed[i][2].get("range", [])
                rng_next = parsed[i + 1][2].get("range", [])
                errors.append(
                    f"{src}: {path} — GAP between bands: "
                    f"{rng_curr} ends at {curr_high}, "
                    f"but next band starts at {next_low} ({rng_next})"
                )

    # Check last band's high is null (infinity) — coverage to +∞
    last_high = parsed[-1][1]
    if last_high is not None:
        errors.append(
            f"{src}: {path} — last band range {parsed[-1][2].get('range')} "
            f"does not cover to +∞ (must end with null upper bound)"
        )

    # Check no overlaps (already checked by gap detection since sorted
    # and contiguous; overlaps would manifest as curr_high > next_low)
    for i in range(len(parsed) - 1):
        curr_high = parsed[i][1]
        next_low = parsed[i + 1][0]
        if curr_high is not None and curr_high > next_low:
            rng_curr = parsed[i][2].get("range", [])
            rng_next = parsed[i + 1][2].get("range", [])
            errors.append(
                f"{src}: {path} — OVERLAP: {rng_curr} overlaps with {rng_next}"
            )

    # Check for unreachable bands: a band where low == high (zero width)
    for i, (low, high, band) in enumerate(parsed):
        if high is not None and abs(high - low) < 1e-9:
            errors.append(
                f"{src}: {path}[{i}] — unreachable band: range {band.get('range')} has zero width"
            )

    return errors


def gate_b_band_partition(defs: list[dict]) -> int:
    """Validate that every graded predicate's bands partition the domain.

    Returns: 0 on pass, 1 on failure.
    """
    errors: list[str] = []
    total_band_sets = 0

    for d in defs:
        src = d.get("_source_file", "?")
        criteria_list = d.get("criteria", [])
        for ci, crit in enumerate(criteria_list):
            pred = crit.get("predicate", {})
            bands = pred.get("bands")
            if bands and pred.get("type") in ("graded", "threshold"):
                total_band_sets += 1
                path = f"criteria[{ci}].predicate"
                errors.extend(_validate_bands(bands, src, path))

    if errors:
        print(f"FAIL [Gate B]: {len(errors)} band partition error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS [Gate B]: {total_band_sets} band set(s) partition their domains correctly.")
    return 0


def gate_b_real_compilation(defs: list[dict]) -> int:
    """Validate every predicate compiles for real via PredicateCompiler.

    This complements ``gate_b_band_partition`` (a hand-rolled reimplementation
    of the partition rules) by invoking the actual production compiler —
    the same code path TrilhasEngine uses at runtime — against every
    predicate (threshold, graded, boolean, composite). A discontinuous
    band, an overlapping band, or a last band that is closed instead of
    covering to +∞ raises ValueError in the real compiler and fails this
    gate, exactly as it would fail pathway loading in TrilhasEngine.

    Returns: 0 on pass, 1 on failure.
    """
    errors: list[str] = []
    total_compiled = 0
    compiler = PredicateCompiler()

    for d in defs:
        src = d.get("_source_file", "?")
        criteria_list = d.get("criteria", [])
        for ci, crit in enumerate(criteria_list):
            pred = crit.get("predicate", {})
            if not pred:
                continue
            crit_id = crit.get("id", f"criteria[{ci}]")
            try:
                compiler.compile(pred)
                total_compiled += 1
            except (ValueError, KeyError, TypeError) as exc:
                errors.append(
                    f"{src}: criteria[{ci}] ({crit_id}) — predicate failed "
                    f"REAL compilation via PredicateCompiler: {exc}"
                )

    if errors:
        print(f"FAIL [Gate B/compile]: {len(errors)} predicate(s) failed real compilation:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        f"PASS [Gate B/compile]: {total_compiled} predicate(s) compiled "
        "successfully via the real PredicateCompiler."
    )
    return 0


# ---------------------------------------------------------------------------
# Gate C: Facade ≡ Predicate
# ---------------------------------------------------------------------------

def _render_predicate_rationale(pred: dict) -> str:
    """Render a predicate AST to a deterministic, human-readable string.

    This is the canonical "facade" renderer. The declared rationale
    must match (after normalization) to pass Gate C.
    """
    ptype = pred.get("type", "threshold")

    if ptype == "threshold":
        op = pred.get("operator", ">=")
        val = pred.get("value", "?")
        unit = pred.get("unit", "")
        input_name = pred.get("input", "?")
        return f"{input_name} {op} {val} {unit}".strip()

    if ptype == "graded":
        input_name = pred.get("input", "?")
        unit = pred.get("unit", "")
        bands = pred.get("bands", [])
        band_strs = []
        for b in bands:
            rng = b.get("range", [])
            sev = b.get("severity", "?")
            score = b.get("score", "?")
            low = rng[0] if len(rng) > 0 else "?"
            high = rng[1] if len(rng) > 1 else "+∞"
            band_strs.append(
                f"[{low}, {high if high is not None else '+∞'})={sev}({score})"
            )
        parts = [f"graded({input_name}", *band_strs, f"unit={unit})"]
        return " ".join(parts).strip()

    if ptype == "boolean":
        input_name = pred.get("input", "?")
        return f"boolean({input_name})"

    if ptype == "composite":
        combinator = pred.get("combinator", "AND")
        subs = pred.get("sub_predicates", [])
        sub_render = " ".join(_render_predicate_rationale(sp) for sp in subs)
        return f"composite({combinator}: {sub_render})"

    return f"unknown({ptype})"


def _normalize(text: str) -> str:
    """Normalize text for comparison: strip extra whitespace, normalize unicode."""
    import unicodedata
    text = re.sub(r"\s+", " ", text).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    return text


def gate_c_facade_predicate(defs: list[dict]) -> int:
    """Validate that declared rationale matches rendered predicate facade.

    Returns: 0 on pass, 1 on failure.
    """
    errors: list[str] = []
    total_checked = 0

    for d in defs:
        src = d.get("_source_file", "?")
        criteria_list = d.get("criteria", [])
        for ci, crit in enumerate(criteria_list):
            pred = crit.get("predicate", {})
            declared = pred.get("rationale")
            if declared:
                total_checked += 1
                rendered = _render_predicate_rationale(pred)
                if _normalize(declared) != _normalize(rendered):
                    errors.append(
                        f"{src}: criteria[{ci}] ({crit.get('id', '?')}) "
                        f"— facade mismatch:\n"
                        f"    declared:  {declared}\n"
                        f"    rendered:  {rendered}"
                    )

    if errors:
        print(f"FAIL [Gate C]: {len(errors)} facade/predicate mismatch(es):")
        for e in errors:
            print(f"  - {e}")
        return 1

    if total_checked == 0:
        print(f"PASS [Gate C]: No criteria with rationale declared — nothing to check.")
    else:
        print(f"PASS [Gate C]: {total_checked} rationale(s) match rendered predicate.")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Trilhas Engine Alert Validator — CI Gates A, B, C",
    )
    parser.add_argument(
        "--gate",
        type=str,
        default="A|B|C",
        help="Gate(s) to run: A (unit resolution), B (band partition), C (facade==predicate). "
        "Use A|B|C for all gates (default).",
    )
    parser.add_argument(
        "--defs",
        type=str,
        default="_work/alerts/pathways/",
        help="Directory containing pathway YAML definitions.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    defs_dir = repo_root / args.defs

    if not defs_dir.is_dir():
        print(f"[WARN] Definitions directory not found: {defs_dir}")
        print("       Skipping validation — no pathway definitions to check.")
        return 0

    definitions = _load_defs(defs_dir)
    if not definitions:
        print("[WARN] No pathway definitions loaded — nothing to validate.")
        return 0

    print(f"\nLoaded {len(definitions)} pathway definition(s) from {defs_dir.relative_to(repo_root)}\n")

    gates = set(args.gate.split("|"))
    exit_code = 0

    if "A" in gates:
        rc = gate_a_unit_resolution(definitions)
        exit_code |= rc
        print()

    if "B" in gates:
        rc = gate_b_band_partition(definitions)
        exit_code |= rc
        print()
        rc = gate_b_real_compilation(definitions)
        exit_code |= rc
        print()

    if "C" in gates:
        rc = gate_c_facade_predicate(definitions)
        exit_code |= rc
        print()

    if exit_code == 0:
        print("=" * 50)
        print("  ALL GATES PASSED ✓")
        print("=" * 50)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
