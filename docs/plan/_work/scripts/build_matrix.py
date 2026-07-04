"""Tool: render docs/plan/traceability-matrix.md deterministically from _work data.

Sections: curated header (from _work/traceability/header.md if present) + generated
summary stats + 959-row rule table + 351-row escalation table + 18 design-ADR rows
+ vision-item coverage (from _work/coverage/vision-map.yaml if present).
Humans never hand-edit the generated block.
"""
from __future__ import annotations

import json
import sys
from collections import Counter

from _lib import ROOT, WORK, load_yaml

OUT = ROOT / "docs/plan/traceability-matrix.md"


def esc_md(s) -> str:
    return str(s or "").replace("|", "\\|").replace("\n", " ")


def main() -> int:
    merged = json.loads((WORK / "dispositions/merged.json").read_text())
    records = merged["records"]
    esc = load_yaml(WORK / "escalations/escalations.yaml")
    res: dict[str, dict] = {}
    for f in sorted((WORK / "escalations").glob("resolutions-*.yaml")):
        for r in load_yaml(f).get("records") or []:
            res[r["item_id"]] = r
    adrs = load_yaml(WORK / "dispositions/design-adrs.yaml").get("records") or []

    manifest = json.loads((WORK / "catalog/id-manifest.json").read_text())
    cluster_of, name_of, verdict_of = {}, {}, {}
    for shard in manifest["shards"]:
        doc = load_yaml(WORK / f"catalog/shards/{shard}.yaml")
        for r in doc["rules"]:
            cluster_of[r["id"]] = doc["cluster"]
            name_of[r["id"]] = r.get("name", "")
            v = r.get("verification")
            verdict_of[r["id"]] = (v.get("verdict") if isinstance(v, dict) else v) or "NOT_APPLICABLE"

    bands_of: dict[str, list[str]] = {}
    for it in esc["items"]:
        bands_of.setdefault(it["rule_id"], []).append(it["band"])

    hp = WORK / "traceability/header.md"
    header = hp.read_text(encoding="utf-8") if hp.exists() else (
        "# Traceability Matrix — IntensiCare v2 Build Plan\n\n"
        "Generated mechanically from `docs/plan/_work/dispositions/` and "
        "`docs/plan/_work/escalations/`. Do not hand-edit below the marker; regenerate with "
        "`python3 docs/plan/_work/scripts/build_matrix.py`.\n")

    lines = [header.rstrip(), "", "<!-- BEGIN GENERATED -->", ""]

    hist = Counter(r["disposition"] for r in records.values())
    lines += ["## Summary", "", "| Disposition | Count |", "|---|---:|"]
    for d in ["ADOPT", "ADOPT-CORRECTED", "ADAPT", "SUPERSEDE", "RETIRE", "RATIFY"]:
        lines.append(f"| {d} | {hist.get(d, 0)} |")
    lines.append(f"| **Total** | **{sum(hist.values())}** |")
    band_hist = Counter(it["band"] for it in esc["items"])
    lines += ["", "| Escalation band | Items |", "|---|---:|"]
    for b in ["P0", "P1", "P2", "P3", "UNVERIFIABLE", "AMBIGUOUS", "ADDENDUM"]:
        lines.append(f"| {b} | {band_hist.get(b, 0)} |")

    lines += ["", "## Rules (959)", "",
              "| Rule | Name | Cluster | Verdict | Disposition | Target | Bands |",
              "|---|---|---|---|---|---|---|"]
    for rid in sorted(records):
        r = records[rid]
        tgt = r.get("target") or "—"
        if tgt != "—":
            tgt = f"[{tgt.split('#')[0].split('/')[-1]}#{tgt.split('#')[1] if '#' in tgt else ''}]({tgt})"
        lines.append(
            f"| {rid} | {esc_md(name_of.get(rid, ''))[:60]} | {cluster_of.get(rid, '?')} "
            f"| {esc_md(verdict_of.get(rid, ''))} | {r['disposition']} | {tgt} "
            f"| {','.join(bands_of.get(rid, [])) or '—'} |")

    lines += ["", "## Escalations (351)", "",
              "| Item | Band | Rule | Outcome | Where |", "|---|---|---|---|---|"]
    for it in sorted(esc["items"], key=lambda x: x["item_id"]):
        r = res.get(it["item_id"], {})
        out = r.get("outcome", "MISSING")
        where = "RATIFICATION.md" if out == "RATIFY" else "traceability (disposition)"
        lines.append(f"| {it['item_id']} | {it['band']} | {it['rule_id']} | {out} | {where} |")

    lines += ["", "## Legacy design ADRs (18)", "",
              "| ADR | Title | Disposition | Target |", "|---|---|---|---|"]
    for a in sorted(adrs, key=lambda x: str(x.get("adr_id"))):
        lines.append(f"| {a.get('adr_id')} | {esc_md(a.get('title'))[:70]} "
                     f"| {a.get('disposition')} | {a.get('target') or '—'} |")

    vm = WORK / "coverage/vision-map.yaml"
    if vm.exists():
        vmap = load_yaml(vm)
        lines += ["", "## Vision-item coverage", "",
                  "| Vision item | Covered by |", "|---|---|"]
        for e in vmap.get("items", []):
            lines.append(f"| {esc_md(e.get('item'))} | {esc_md(', '.join(e.get('covered_by') or []))} |")

    lines += ["", "<!-- END GENERATED -->", ""]
    tmp = OUT.with_suffix(".md.tmp")
    tmp.write_text("\n".join(lines), encoding="utf-8")
    tmp.rename(OUT)
    print(f"[build_matrix] wrote {OUT.relative_to(ROOT)}: {len(records)} rules, "
          f"{len(esc['items'])} escalations, {len(adrs)} ADRs, {sum(hist.values())} dispositions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
