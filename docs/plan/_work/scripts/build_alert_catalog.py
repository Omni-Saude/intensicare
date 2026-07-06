"""Tool: render docs/plan/clinical/alert-catalog.md from _work/alerts/*.yaml.

Per domain H2; per alert H3 with prose summary + one fenced ```yaml alert-spec block
(the raw entry, machine-checkable); final reconciliation table covering all existing
catalog IDs. Curated header from _work/editorial/alert-catalog-header.md if present.
"""
from __future__ import annotations

import json
import re
import sys

import yaml

from _lib import ROOT, WORK, load_yaml

OUT = ROOT / "docs/plan/clinical/alert-catalog.md"
DOMAINS = ["sepsis", "aki", "respiratory", "hemodynamics", "neuro-sedation",
           "electrolyte", "pharmaco-interaction", "early-warning-scores",
           "correlation-engine"]


def main() -> int:
    hp = WORK / "editorial/alert-catalog-header.md"
    header = hp.read_text(encoding="utf-8") if hp.exists() else (
        "# Alert Catalog — IntensiCare v2\n\n"
        "Every alert: typed unit-checked inputs, evidence citation, severity "
        "(`normal|watch|urgent|critical`), suppression spec, PPV budget, required response, "
        "and ≥3 test vectors. Machine source: `docs/plan/_work/alerts/<domain>.yaml` — this file "
        "is generated (`build_alert_catalog.py`); edit the YAML, not this file.\n")
    L = [header.rstrip(), ""]

    recon_rows = []
    n_alerts = 0
    for d in DOMAINS:
        p = WORK / f"alerts/{d}.yaml"
        if not p.exists():
            continue
        doc = load_yaml(p)
        alerts = doc.get("alerts") or []
        L += [f"## {d} ({len(alerts)} alerts)", ""]
        for a in alerts:
            n_alerts += 1
            aid = a.get("alert_id")
            L += [f'<a id="{str(aid).lower()}"></a>', f"### {aid} — {a.get('name', '')}", ""]
            ev = "; ".join(e.get("citation", "") for e in a.get("evidence") or [])
            rules = ", ".join(sorted({r for e in a.get("evidence") or []
                                      for r in e.get("rule_refs") or []})) or "—"
            L += [f"**Severity** {a.get('severity')} · **Evidence** {ev} · **Rules** {rules} · "
                  f"**PPV target** {(a.get('ppv_budget') or {}).get('target_ppv')} · "
                  f"**Est. volume** {(a.get('ppv_budget') or {}).get('est_volume_per_100_beds_day')}"
                  f"/100 beds/day", "",
                  "```yaml alert-spec",
                  yaml.safe_dump(a, allow_unicode=True, sort_keys=False, width=100).rstrip(),
                  "```", ""]
            recs = a.get("reconciliation") or {}
            for rec in (recs if isinstance(recs, list) else [recs]):
                if isinstance(rec, dict) and rec.get("existing_id"):
                    recon_rows.append((rec["existing_id"], aid, rec.get("status"), rec.get("note", "")))

    cat_ids = set()
    bp = WORK / "briefs/existing-alert-catalog.json"
    if bp.exists():
        for f in json.loads(bp.read_text()).get("facts", []):
            m = re.match(r"CAT-([A-Z]+-\d+)", str(f.get("id", "")))
            if m:
                cat_ids.add(m.group(1))
    covered = {r[0] for r in recon_rows}
    L += ["## Reconciliation vs docs/clinical/alert-catalog.md (v1.0.0)", "",
          "| Existing | New alert | Status | Note |", "|---|---|---|---|"]
    for row in sorted(recon_rows):
        L.append(f"| {row[0]} | {row[1]} | {row[2]} | {str(row[3])[:100]} |")
    for missing in sorted(cat_ids - covered):
        L.append(f"| {missing} | — | **UNRECONCILED** | gate failure |")
    L.append("")

    tmp = OUT.with_suffix(".md.tmp")
    tmp.write_text("\n".join(L), encoding="utf-8")
    tmp.rename(OUT)
    print(f"[build_alert_catalog] wrote {OUT.relative_to(ROOT)}: {n_alerts} alerts, "
          f"{len(recon_rows)} reconciliations, {len(cat_ids - covered)} unreconciled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
