"""
Cross-validation script for IntensiCare audit agent outputs.
Run after all 6 agents complete to verify consistency across batches.
Usage: python /Users/familia/intensicare/audit-results/verify.py
"""
import json, csv, os, sys
from pathlib import Path
from collections import defaultdict

AUDIT_DIR = Path("/Users/familia/intensicare/audit-results")

def check_file_exists(filename: str) -> bool:
    path = AUDIT_DIR / filename
    exists = path.exists()
    print(f"  {'✅' if exists else '❌'} {filename} {'found' if exists else 'MISSING'}")
    return exists

def count_csv_rows(filename: str) -> int:
    path = AUDIT_DIR / filename
    if not path.exists():
        return 0
    with open(path) as f:
        return sum(1 for _ in csv.reader(f)) - 1  # minus header

def main():
    print("=" * 60)
    print("IntensiCare Audit — Cross-Validation Report")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # ── Gate 1: All expected outputs exist ──
    print("\n📋 Gate 1: Output Completeness")
    expected = [
        "CANONICAL_AUDIT.md", "CONFORMITY_MATRIX.csv",
        "HEURISTIC_SCORECARD.csv", "ACCESSIBILITY_REPORT.csv",
        "UX_ACCESSIBILITY_AUDIT.md", "DS_GOVERNANCE_REPORT.md",
        "TOKEN_COMPLIANCE.csv", "COMPONENT_INVENTORY.csv",
        "BENCHMARK_GAP_ANALYSIS.md", "CONTRAST_AUDIT.csv",
        "COMPONENT_STATE_MATRIX.csv", "STATE_COVERAGE_REPORT.md",
        "RUNBOOK.md"
    ]
    missing = [f for f in expected if not check_file_exists(f)]
    if missing:
        warnings.append(f"Missing outputs: {', '.join(missing)}")
    
    # ── Gate 2: Matrix has ADR coverage ──
    print("\n📋 Gate 2: ADR Coverage")
    matrix_path = AUDIT_DIR / "CONFORMITY_MATRIX.csv"
    if matrix_path.exists():
        with open(matrix_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            adrs_found = {r.get("ADR", "") for r in rows}
            expected_adrs = {f"{i:04d}" for i in range(1, 19)}
            missing_adrs = expected_adrs - adrs_found
            if missing_adrs:
                errors.append(f"ADRs missing from matrix: {sorted(missing_adrs)}")
            else:
                print(f"  ✅ All 18 ADRs covered ({len(rows)} rows)")
            
            # Check for required columns
            required_cols = {"ADR", "Title", "Status", "Severity", "Evidence", "Recommendation"}
            actual_cols = set(rows[0].keys()) if rows else set()
            missing_cols = required_cols - actual_cols
            if missing_cols:
                errors.append(f"Matrix missing columns: {missing_cols}")
            
            # Check status values
            valid_statuses = {"COMPLIANT", "PARTIAL", "VIOLATED", "NOT_IMPLEMENTED", "NOT_APPLICABLE"}
            for r in rows:
                status = r.get("Status", "")
                if status not in valid_statuses:
                    errors.append(f"ADR {r.get('ADR')}: invalid status '{status}'")
    
    # ── Gate 3: Evidence citations ──
    print("\n📋 Gate 3: Evidence Quality")
    if matrix_path.exists():
        with open(matrix_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            no_evidence = [r["ADR"] for r in rows if not r.get("Evidence", "").strip()]
            if no_evidence:
                errors.append(f"ADRs without evidence: {no_evidence}")
            else:
                print(f"  ✅ All {len(rows)} rows have evidence citations")
    
    # ── Gate 4: Cross-batch consistency (when both TOKEN_COMPLIANCE.csv exist) ──
    print("\n📋 Gate 4: Cross-Batch Consistency")
    tc1 = AUDIT_DIR / "TOKEN_COMPLIANCE.csv"  # From Batch 1 (governance)
    # Batch 2 produces same filename — check if they agree
    if tc1.exists():
        count = count_csv_rows("TOKEN_COMPLIANCE.csv")
        print(f"  Token compliance rows: {count}")
        if count == 0:
            warnings.append("TOKEN_COMPLIANCE.csv is empty — possible scan failure")
    
    # ── Gate 5: Contrast ratios are numeric ──
    print("\n📋 Gate 5: Contrast Audit Quality")
    ca = AUDIT_DIR / "CONTRAST_AUDIT.csv"
    if ca.exists():
        with open(ca) as f:
            reader = csv.DictReader(f)
            rows = [r for r in reader if r.get("status") is not None]
            fails = [r for r in rows if (r.get("status") or "").upper() == "FAIL"]
            if fails:
                errors.append(f"FAILING contrast ratios: {[r.get('token_name','?') for r in fails]}")
            else:
                print(f"  ✅ All {len(rows)} token pairs pass or are borderline")
    
    # ── Summary ──
    print("\n" + "=" * 60)
    print(f"RESULTS: {len(errors)} errors, {len(warnings)} warnings")
    if errors:
        print("\n❌ ERRORS (must fix before consolidation):")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print("\n⚠️ WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    if not errors and not warnings:
        print("\n✅ All gates passed — ready for consolidation")
    
    return 0 if not errors else 1

if __name__ == "__main__":
    sys.exit(main())
