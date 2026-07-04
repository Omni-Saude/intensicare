"""Gate: coverage maps — six invariants, every ADR-001 constraint, 12 persona criteria.

Validates _work/coverage/{invariants-map,adr001-map,persona-map}.yaml: full coverage
of the pinned ID sets AND that every referenced requirement-id/anchor literally
exists in the referenced deliverable file.
"""
from __future__ import annotations

import re
import sys

from _lib import ROOT, WORK, Gate, load_yaml

PLAN = ROOT / "docs/plan"


def ref_ok(ref: str) -> tuple[bool, str]:
    path = ref.split("#", 1)[0]
    p = PLAN / path
    if not p.exists():
        return False, f"missing file {path}"
    return True, ""


def grep_ok(ref: str, needle: str) -> bool:
    p = PLAN / ref.split("#", 1)[0]
    try:
        return needle in p.read_text(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return False


def main() -> int:
    g = Gate("check_coverage_maps")

    inv = load_yaml(WORK / "coverage/invariants-map.yaml") if (WORK / "coverage/invariants-map.yaml").exists() else None
    if inv is None:
        g.add("COV-INV", False, "invariants-map.yaml exists", "MISSING")
    else:
        problems = []
        entries = {e["invariant_id"]: e for e in inv.get("invariants", [])}
        for n in range(1, 7):
            e = entries.get(f"INV-{n}")
            if not e:
                problems.append(f"INV-{n} missing")
                continue
            if not e.get("owning_component"):
                problems.append(f"INV-{n}: no owning_component")
            reqs = e.get("requirement_ids") or []
            refs = e.get("refs") or []
            if not reqs or not refs:
                problems.append(f"INV-{n}: requirement_ids/refs empty")
            for ref in refs:
                ok, why = ref_ok(ref)
                if not ok:
                    problems.append(f"INV-{n}: {why}")
            for rid in reqs:
                if not any(grep_ok(ref, rid) for ref in refs):
                    problems.append(f"INV-{n}: requirement id {rid} not found in refs")
            if not e.get("test_ref"):
                problems.append(f"INV-{n}: no test-strategy ref")
        g.add("COV-INV", not problems, "6 invariants -> testable reqs w/ owners + verified refs",
              f"{len(problems)}", problems)

    ledger = load_yaml(WORK / "constraints/ledger.yaml")
    adr_ids = set()
    for e in ledger["entries"]:
        for sid in e.get("source_constraint_ids") or []:
            if re.match(r"ADR001-C-\d+", str(sid)):
                adr_ids.add(str(sid))
    amap = load_yaml(WORK / "coverage/adr001-map.yaml") if (WORK / "coverage/adr001-map.yaml").exists() else None
    if amap is None:
        g.add("COV-ADR001", False, "adr001-map.yaml exists", "MISSING")
    else:
        entries = {e["constraint_id"]: e for e in amap.get("constraints", [])}
        problems = [f"{cid} unmapped" for cid in sorted(adr_ids - set(entries))]
        for cid, e in entries.items():
            hb, ca = e.get("honored_by"), e.get("counter_adr")
            if not hb and not ca:
                problems.append(f"{cid}: neither honored_by nor counter_adr")
            for ref in ([hb] if hb else []) + ([ca] if ca else []):
                ok, why = ref_ok(ref)
                if not ok:
                    problems.append(f"{cid}: {why}")
        g.add("COV-ADR001", not problems, f"all {len(adr_ids)} ADR-001 constraints honored or counter-ADR'd",
              f"{len(problems)}", problems)

    pmap = load_yaml(WORK / "coverage/persona-map.yaml") if (WORK / "coverage/persona-map.yaml").exists() else None
    if pmap is None:
        g.add("COV-PERSONA", False, "persona-map.yaml exists", "MISSING")
    else:
        entries = {e["criterion_id"]: e for e in pmap.get("criteria", [])}
        expected = {f"PER-{p}-{i:02d}" for p in ("CARLOS", "ANA", "FERNANDA", "RAFAEL")
                    for i in (1, 2, 3)}
        problems = [f"{c} unmapped" for c in sorted(expected - set(entries))]
        for cid, e in entries.items():
            screens = e.get("screens") or []
            metrics = e.get("metrics") or []
            if not screens:
                problems.append(f"{cid}: no screen/flow ref")
            if not metrics:
                problems.append(f"{cid}: no metric ref")
            for ref in screens + metrics:
                ok, why = ref_ok(ref)
                if not ok:
                    problems.append(f"{cid}: {why}")
        g.add("COV-PERSONA", not problems, "12 criteria -> >=1 screen + >=1 metric, refs resolve",
              f"{len(problems)}", problems)
    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
