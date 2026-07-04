"""Gate: alert-catalog completeness over _work/alerts/<domain>.yaml (9 domains).

Checks schema completeness, >=3 test vectors incl. boundary, severity enum,
globally-unique alert IDs, rule_refs validity + disposition legality (needs
_work/dispositions/merged.json), and reconciliation coverage of all 32 existing
catalog alert IDs (from the existing-alert-catalog brief).
Usage: check_alert_catalog.py [--mode draft|strict]
"""
from __future__ import annotations

import json
import re
import sys

from _lib import WORK, Gate, load_yaml

DOMAINS = ["sepsis", "aki", "respiratory", "hemodynamics", "neuro-sedation",
           "electrolyte", "pharmaco-interaction", "early-warning-scores",
           "correlation-engine"]
SEVERITIES = {"normal", "watch", "urgent", "critical"}
OK_DISPO = {"ADOPT", "ADOPT-CORRECTED", "ADAPT"}
RECON_STATUS = {"aligned", "extended", "changed", "new", "dropped"}


def main() -> int:
    mode = "strict" if "strict" in " ".join(sys.argv[1:]) else "draft"
    g = Gate("check_alert_catalog")

    merged = {}
    mp = WORK / "dispositions/merged.json"
    if mp.exists():
        merged = json.loads(mp.read_text())["records"]
    g.add("AC-DISPOSITIONS-AVAILABLE", bool(merged), "merged.json present for legality checks",
          "present" if merged else "absent", warn=not merged)

    cat_ids = set()
    bp = WORK / "briefs/existing-alert-catalog.json"
    if bp.exists():
        brief = json.loads(bp.read_text())
        for f in brief.get("facts", []):
            m = re.match(r"CAT-([A-Z]+-\d+)", str(f.get("id", "")))
            if m:
                cat_ids.add(m.group(1))
    g.add("AC-EXISTING-32", len(cat_ids) >= 32, ">=32 existing alert IDs from brief",
          str(len(cat_ids)), sorted(cat_ids) if len(cat_ids) < 32 else [])

    seen_ids: dict[str, str] = {}
    recon_seen: dict[str, str] = {}
    n_alerts = 0
    for d in DOMAINS:
        p = WORK / f"alerts/{d}.yaml"
        if not p.exists():
            g.add(f"AC-{d}", False, "domain alert file exists", "MISSING")
            continue
        try:
            doc = load_yaml(p)
            alerts = doc.get("alerts") or []
        except Exception as e:  # noqa: BLE001
            g.add(f"AC-{d}", False, "valid YAML", f"parse error: {e}")
            continue
        problems = []
        for a in alerts:
            n_alerts += 1
            aid = a.get("alert_id") or "?"
            if aid in seen_ids:
                problems.append(f"{aid}: duplicate (also in {seen_ids[aid]})")
            seen_ids[aid] = d
            if not str(aid).startswith("ALERT-"):
                problems.append(f"{aid}: id must start ALERT-")
            if a.get("severity") not in SEVERITIES:
                problems.append(f"{aid}: severity {a.get('severity')}")
            trig = a.get("trigger") or {}
            if not (trig.get("logic") and trig.get("window")):
                problems.append(f"{aid}: trigger.logic/window missing")
            inputs = a.get("inputs") or []
            if not inputs:
                problems.append(f"{aid}: no inputs")
            for i in inputs:
                if not (i.get("name") and i.get("unit") and i.get("source")):
                    problems.append(f"{aid}: input incomplete {str(i)[:60]}")
                    break
            ev = a.get("evidence") or []
            if not any(e.get("citation") for e in ev):
                problems.append(f"{aid}: no evidence citation")
            for e in ev:
                for rid in e.get("rule_refs") or []:
                    rec = merged.get(rid)
                    if merged and rec is None:
                        problems.append(f"{aid}: rule_ref {rid} not in catalog/dispositions")
                    elif rec and rec.get("disposition") in {"RETIRE", "SUPERSEDE"}:
                        problems.append(f"{aid}: cites {rid} dispositioned {rec['disposition']}")
                    elif rec and rec.get("disposition") == "RATIFY":
                        g.add(f"AC-{aid}-RATIFY-REF", False,
                              "alert cites decided rule", f"{rid} is RATIFY-pending", warn=True)
            sup = a.get("suppression") or {}
            if not (sup.get("dedup_key") and sup.get("cooldown") and sup.get("rate_limit")):
                problems.append(f"{aid}: suppression incomplete")
            ppv = a.get("ppv_budget") or {}
            if not (isinstance(ppv.get("target_ppv"), (int, float))
                    and ppv.get("est_volume_per_100_beds_day") is not None
                    and ppv.get("rationale")):
                problems.append(f"{aid}: ppv_budget incomplete")
            tv = a.get("test_vectors") or []
            if len(tv) < 3:
                problems.append(f"{aid}: only {len(tv)} test vectors")
            elif not any(v.get("kind") == "boundary" for v in tv):
                problems.append(f"{aid}: no boundary vector")
            if not (a.get("response") or {}).get("required"):
                problems.append(f"{aid}: response.required missing")
            rec = a.get("reconciliation") or {}
            if rec.get("status") not in RECON_STATUS:
                problems.append(f"{aid}: reconciliation.status {rec.get('status')}")
            if rec.get("existing_id"):
                recon_seen[str(rec["existing_id"])] = aid
        g.add(f"AC-{d}", not problems, f"all {len(alerts)} alerts complete",
              f"{len(problems)} problems", problems)

    uncovered = sorted(cat_ids - set(recon_seen))
    g.add("AC-RECONCILE-32", not uncovered,
          "every existing catalog alert reconciled by some new alert entry",
          f"{len(uncovered)} unreconciled", uncovered, warn=(mode == "draft"))
    g.add("AC-TOTAL", n_alerts >= 25, ">=25 alerts fleet-wide", str(n_alerts))
    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
