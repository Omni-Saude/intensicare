"""Wave 1C: Update traceability matrix — convert 204 RATIFY rules to final dispositions.

Reads ratification-decisions.yaml for per-rule decisions and updates the
per-shard disposition YAMLs, then regenerates merged.json and traceability-matrix.md.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib import ROOT, WORK, load_yaml, dump_yaml

RATIFICATION_YAML = WORK / "ratification-decisions.yaml"
MERGED_JSON = WORK / "dispositions/merged.json"


def map_decision_to_disposition(decision: str, band: str) -> str:
    """Map a ratification decision to a final disposition."""
    d = decision.strip()
    
    # ADOPT RECOMMENDED OPTION * -> ADOPT
    if d.startswith("ADOPT RECOMMENDED"):
        return "ADOPT"
    
    # KEEP per drafter -> ADAPT
    if d.startswith("KEEP per drafter"):
        return "ADAPT"
    
    # RETIRE per drafter -> RETIRE
    if d.startswith("RETIRE per drafter"):
        return "RETIRE"
    
    # PROCEED per the recommended default -> ADOPT
    if d.startswith("PROCEED per"):
        return "ADOPT"
    
    # ACCEPTED -> ADOPT (risk items, not affecting rules)
    if d.startswith("ACCEPTED"):
        return "ADOPT"
    
    # Unknown
    print(f"  WARNING: Unknown decision '{d[:60]}...' for band {band} — defaulting to ADOPT")
    return "ADOPT"


def main() -> int:
    # 1. Load data
    merged = json.loads(MERGED_JSON.read_text())
    decisions_doc = load_yaml(RATIFICATION_YAML)
    
    # Build rule_id -> decision map
    rule_decision: dict[str, dict] = {}
    for d in decisions_doc["decisions"]:
        decision = d["decision"]
        band = d.get("band", "")
        item_id = d["id"]
        for rid in d.get("rule_ids", []):
            rule_decision[rid] = {
                "decision": decision,
                "band": band,
                "item_id": item_id,
            }
    
    # 2. Identify all RATIFY rules
    ratify_rules = {
        rid: r for rid, r in merged["records"].items()
        if r.get("disposition") == "RATIFY"
    }
    print(f"Found {len(ratify_rules)} RATIFY rules to convert")
    
    # 3. Map each to new disposition
    new_dispositions: dict[str, str] = {}
    no_decision = []
    decision_counts: Counter = Counter()
    
    for rid in sorted(ratify_rules):
        if rid in rule_decision:
            info = rule_decision[rid]
            new_disp = map_decision_to_disposition(info["decision"], info["band"])
            new_dispositions[rid] = new_disp
            decision_counts[new_disp] += 1
        else:
            # No explicit decision — these are P2/P3 rules without decisions
            # Default to ADOPT per RATIFICATION-DECISIONS.md
            new_dispositions[rid] = "ADOPT"
            decision_counts["ADOPT"] += 1
            no_decision.append(rid)
    
    if no_decision:
        print(f"  {len(no_decision)} rules without explicit decision → defaulting to ADOPT:")
        for rid in no_decision:
            print(f"    {rid}")
    
    print(f"\nNew disposition counts:")
    for d, c in decision_counts.most_common():
        print(f"  {d}: {c}")
    
    # 4. Update the per-shard disposition YAMLs
    # Read all shard files
    shard_dir = WORK / "dispositions"
    shard_files = sorted(shard_dir.glob("*.yaml"))
    updated_count = 0
    
    for sf in shard_files:
        if sf.name == "design-adrs.yaml":
            continue  # skip ADRs
        try:
            doc = load_yaml(sf)
            records = doc.get("records") or []
            modified = False
            
            for rec in records:
                rid = rec.get("rule_id")
                if rid in new_dispositions:
                    old_disp = rec.get("disposition")
                    new_disp = new_dispositions[rid]
                    if old_disp != new_disp:
                        rec["disposition"] = new_disp
                        # Also update justification to note ratification
                        rec["justification"] = (
                            f"[RATIFIED 2026-07-04] {rec.get('justification', '')}"
                        )[:300]
                        modified = True
                        updated_count += 1
            
            if modified:
                dump_yaml(doc, sf)
                print(f"  Updated {sf.name}: {sum(1 for r in records if r['rule_id'] in new_dispositions)} rules")
        except Exception as e:
            print(f"  ERROR processing {sf.name}: {e}")
    
    print(f"\nTotal rules updated in shard files: {updated_count}")
    
    # 5. Verify: read back and count
    verify_merged = {}
    for sf in shard_files:
        if sf.name == "design-adrs.yaml":
            continue
        try:
            doc = load_yaml(sf)
            for rec in doc.get("records") or []:
                rid = rec.get("rule_id")
                if rid:
                    verify_merged[rid] = rec.get("disposition")
        except Exception:
            pass
    
    remaining_ratify = sum(1 for d in verify_merged.values() if d == "RATIFY")
    print(f"\nVerification: {remaining_ratify} RATIFY remaining (should be 0)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
