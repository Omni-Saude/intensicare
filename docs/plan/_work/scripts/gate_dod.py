"""Aggregator: run the phase's gate suite, map results onto the mission DoD lines,
emit _work/gates/dod-report.json. Usage: gate_dod.py [--phase B|C|D|E]
Exit: 0 PASS, 1 FAIL, 2 PASS-WITH-ESCALATIONS/WARN.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from _lib import GATES, ROOT, WORK, dump_json

SUITES = {
    "B": ["check_env", "check_schema", "check_dispositions", "check_escalations",
          ("check_alert_catalog", ["--mode", "draft"]), ("check_units", ["--mode", "draft"]),
          "check_tree"],
    "C": ["check_env", ("check_units", ["--mode", "strict"]),
          ("check_alert_catalog", ["--mode", "strict"]), "check_links"],
    "D": ["check_env", "check_dispositions", "check_escalations",
          ("check_alert_catalog", ["--mode", "strict"]), ("check_units", ["--mode", "strict"]),
          "check_links", "check_coverage_maps", "check_matrix"],
    "E": ["check_env", "check_schema", "check_dispositions", "check_escalations",
          ("check_alert_catalog", ["--mode", "strict"]), ("check_units", ["--mode", "strict"]),
          ("check_tree", ["--phase", "E"]), "check_links", "check_coverage_maps",
          "check_matrix", "check_ratification"],
}

DOD_MAP = {
    "DoD-1 100% of 959 rules + 351 escalations dispositioned, zero silent drops":
        ["check_dispositions", "check_escalations", "check_matrix"],
    "DoD-2 every alert: typed unit-checked inputs, evidence, severity, suppression, PPV budget, >=3 vectors":
        ["check_alert_catalog"],
    "DoD-3 units registry exists; every domain input validates against it": ["check_units"],
    "DoD-4 all 12 P0 resolved-or-RATIFIED; all FIVE audit asks answered/escalated":
        ["check_escalations", "check_ratification"],
    "DoD-5 every persona criterion -> >=1 screen/flow + >=1 metric": ["check_coverage_maps"],
    "DoD-6 six invariants as testable requirements with owning components": ["check_coverage_maps"],
    "DoD-7 every ADR-001 constraint honored or counter-ADR'd": ["check_coverage_maps"],
    "DoD-8 red team: two consecutive rounds, zero unresolved CONFIRMED critical": ["redteam-ledger"],
    "DoD-9 all internal links resolve; deliverable tree complete": ["check_links", "check_tree"],
}


def run(name: str, args: list[str]) -> dict:
    script = ROOT / f"docs/plan/_work/scripts/{name}.py"
    p = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)
    jf = GATES / f"{name}.json"
    status = "MISSING"
    if jf.exists():
        status = json.loads(jf.read_text()).get("status", "?")
    return {"gate": name, "exit": p.returncode, "status": status,
            "summary": (p.stdout.splitlines() or [""])[0][:200]}


def main() -> int:
    phase = "E"
    if "--phase" in sys.argv:
        phase = sys.argv[sys.argv.index("--phase") + 1]
    results = []
    for entry in SUITES[phase]:
        name, args = entry if isinstance(entry, tuple) else (entry, [])
        results.append(run(name, args))
        print(results[-1]["summary"])

    rt = WORK / "redteam/ledger.json"
    if phase in ("D", "E"):
        if rt.exists():
            led = json.loads(rt.read_text())
            ok = led.get("consecutive_clean", 0) >= 2 and led.get("unresolved_confirmed_critical", 1) == 0
            results.append({"gate": "redteam-ledger", "exit": 0 if ok else 1,
                            "status": "PASS" if ok else "FAIL",
                            "summary": f"clean_rounds={led.get('consecutive_clean')}, "
                                       f"unresolved_critical={led.get('unresolved_confirmed_critical')}"})
        else:
            results.append({"gate": "redteam-ledger", "exit": 1, "status": "MISSING",
                            "summary": "no red-team ledger yet"})

    by_gate = {r["gate"]: r for r in results}
    dod = []
    for line, gates in DOD_MAP.items():
        rel = [by_gate.get(g) for g in gates if by_gate.get(g)]
        if not rel:
            verdict = "NOT-RUN-THIS-PHASE"
        elif any(r["status"] == "FAIL" or r["exit"] == 1 for r in rel):
            verdict = "FAIL"
        elif any(r["status"] in ("WARN",) or r["exit"] == 2 for r in rel):
            verdict = "PASS-WITH-WARNINGS"
        else:
            verdict = "PASS"
        dod.append({"dod": line, "verdict": verdict, "gates": [r["gate"] for r in rel]})

    hard_fail = any(r["exit"] == 1 for r in results)
    warn = any(r["exit"] == 2 for r in results)
    overall = "FAIL" if hard_fail else ("PASS-WITH-WARNINGS" if warn else "PASS")
    dump_json({"phase": phase, "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "overall": overall, "gates": results, "dod": dod},
              GATES / "dod-report.json")
    print(f"\n[gate_dod --phase {phase}] OVERALL: {overall}")
    for d in dod:
        print(f"  {d['verdict']:20s} {d['dod'][:95]}")
    return 1 if hard_fail else (2 if warn else 0)


if __name__ == "__main__":
    sys.exit(main())
