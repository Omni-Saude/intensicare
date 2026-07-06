"""Build-time SYS gates A/B/C for alert definitions.

Gate A (criterion-coverage): every declared input is referenced in logic.
Gate B (band-partition): bands cover admissible range without gaps/overlaps.
Gate C (facade==predicate): rendered thresholds match the parsed AST.

Usage: check_alert_definitions.py [--mode draft|strict]
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to path so we can import the compiler
_script_dir = Path(__file__).resolve().parent
_repo_root = _script_dir.parents[3]  # scripts -> _work -> plan -> docs -> repo root

sys.path.insert(0, str(_repo_root / "src"))

from intensicare.services.alert_compiler import (  # noqa: E402
    AlertCompiler,
    alert_catalog_paths,
)


def main() -> int:
    mode = "strict" if "strict" in " ".join(sys.argv[1:]) else "draft"
    strict = mode == "strict"

    compiler = AlertCompiler(_repo_root)
    definitions = compiler.load_all()

    n_pass = 0
    n_fail = 0
    all_failures: list[str] = []

    # --- Gate A: Criterion coverage ---
    gate_a_ok, gate_a_failures = compiler.gate_a_criterion_coverage()
    if gate_a_ok:
        n_pass += 1
        print(f"[PASS] Gate A (criterion-coverage): all {len(definitions)} alerts "
              f"have all inputs referenced in logic")
    else:
        n_fail += 1
        print(f"[FAIL] Gate A (criterion-coverage): {len(gate_a_failures)} alerts "
              f"have unreferenced inputs")
        for f in gate_a_failures:
            msg = (f"  {f['alert_id']}: {f['msg']}")
            print(msg)
            all_failures.append(msg)

    # --- Gate B: Band partition ---
    gate_b_ok, gate_b_failures = compiler.gate_b_band_partition()
    if gate_b_ok:
        n_pass += 1
        print(f"[PASS] Gate B (band-partition): no gaps/overlaps found "
              f"across {len(definitions)} alerts")
    else:
        n_fail += 1
        print(f"[FAIL] Gate B (band-partition): {len(gate_b_failures)} "
              f"band-partition issues found")
        for f in gate_b_failures:
            msg = (f"  {f['alert_id']} / {f.get('variable', '?')}: {f['msg']}")
            print(msg)
            all_failures.append(msg)

    # --- Gate C: Facade == predicate ---
    gate_c_ok, gate_c_failures = compiler.gate_c_facade_predicate()
    if gate_c_ok:
        n_pass += 1
        print(f"[PASS] Gate C (facade==predicate): no orphan facade thresholds "
              f"across {len(definitions)} alerts")
    else:
        n_fail += 1
        print(f"[FAIL] Gate C (facade==predicate): {len(gate_c_failures)} "
              f"facade/predicate mismatches")
        for f in gate_c_failures:
            msg = (f"  {f['alert_id']}: {f['msg']}")
            print(msg)
            all_failures.append(msg)

    # --- Load check ---
    catalog_count = len(list(alert_catalog_paths(_repo_root)))
    def_count = len(definitions)
    if catalog_count == 9 and def_count >= 20:
        n_pass += 1
        print(f"[PASS] Catalog load: all {catalog_count} YAMLs loaded, "
              f"{def_count} definitions compiled")
    else:
        n_fail += 1
        print(f"[FAIL] Catalog load: {catalog_count} YAMLs found, "
              f"{def_count} definitions expected >= 20")

    # --- Versioned registry check ---
    versioned = sum(1 for ad in definitions.values() if ad.content_hash)
    if versioned == def_count:
        n_pass += 1
        print(f"[PASS] Versioning: all {versioned} definitions have content hashes")
    else:
        n_fail += 1
        print(f"[FAIL] Versioning: only {versioned}/{def_count} have content hashes")

    print(f"\nSummary: {n_pass} gates passed, {n_fail} failed")

    if strict and n_fail > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
