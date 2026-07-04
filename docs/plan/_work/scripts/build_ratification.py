"""Tool: render the RATIFICATION.md skeleton from _work data.

Content order: preamble (policy interpretation) -> the FIVE audit ratification asks
-> 12 P0 items (full question/options/recommended) -> P1 -> UNVERIFIABLE groups ->
AMBIGUOUS -> cluster RATIFY dispositions not covered by an escalation -> barrier
residuals -> accepted-risk red-team findings. Every item gets an explicit
<a id="..."></a> anchor matching disposition targets (rat-<cluster>-<nn>) or item ids.
The ratification-assembler agent polishes prose afterwards WITHOUT changing anchors.
"""
from __future__ import annotations

import json
import re
import sys

from _lib import ROOT, WORK, load_yaml

OUT = ROOT / "docs/plan/RATIFICATION.md"


def anchor(s: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", str(s).lower().replace(" ", "-"))


def render_ratify(r: dict) -> list[str]:
    rat = r.get("ratify") or {}
    lines = [f"**Question.** {rat.get('question', 'TBD')}", ""]
    opts = rat.get("options") or []
    if opts:
        lines += ["**Options.**", ""]
        for o in opts:
            oid = o.get("id", "?")
            risk = o.get("clinical_risk") or o.get("risk") or ""
            lines.append(f"- **{oid}** — {o.get('text', '')}" + (f" *(risk: {risk})*" if risk else ""))
        lines.append("")
    if rat.get("recommended"):
        lines.append(f"**Recommended default.** {rat['recommended']} — {rat.get('rationale', '')}")
        lines.append("")
    if r.get("disposition_note"):
        lines += [f"**Disposition note.** {r['disposition_note']}", ""]
    return lines


def main() -> int:
    merged = json.loads((WORK / "dispositions/merged.json").read_text())["records"]
    esc = load_yaml(WORK / "escalations/escalations.yaml")
    items = {it["item_id"]: it for it in esc["items"]}
    res: dict[str, dict] = {}
    groups: dict[str, dict] = {}
    for f in sorted((WORK / "escalations").glob("resolutions-*.yaml")):
        doc = load_yaml(f)
        for r in doc.get("records") or []:
            res[r["item_id"]] = r
        for gr in doc.get("groups") or []:
            groups[gr["group_id"]] = gr

    audit_brief = json.loads((WORK / "briefs/audit-report.json").read_text())
    asks = [f for f in audit_brief.get("facts", []) if str(f.get("id", "")).startswith("ASK-")]

    L = ["# RATIFICATION — Open Human Decisions, IntensiCare v2 Build Plan", "",
         "Every item below requires a decision by the clinical committee, product owner, or legal",
         "counsel. Each carries a concrete question, options, and the plan's recommended default —",
         "the design proceeds on the recommended default and marks the affected specs `pending RAT-*`.",
         "", "**Standing policy (locked at Phase 0, ratify or amend):** rules escalated at bands",
         "P0, P1, or UNVERIFIABLE-owner-review are never silently adopted — each is dispositioned",
         "`RATIFY` and listed here. P2/P3 were decided by the disposition pass citing the escalation;",
         "AMBIGUOUS rules were kept (RATIFY) or retired per clinical value.", ""]

    L += ["## The five audit ratification asks", ""]
    for f in sorted(asks, key=lambda x: x["id"]):
        aid = f["id"].lower()
        L += [f'<a id="{aid}"></a>', f"### {f['id']} — {f.get('claim', '')[:110]}", "",
              f"{f.get('claim', '')}", "", f"*Source: {f.get('source_ref', '')}*", "",
              "**Answered by this plan:** see the corresponding sections below (P0/P1 committee "
              "queue, UNVERIFIABLE owner queue, e-signature items, sepsis aggregation item, and the "
              "canonical units registry `clinical/units-registry.md`).", ""]

    def section(title: str, band: str):
        nonlocal L
        band_items = [it for it in esc["items"] if it["band"] == band]
        L += [f"## {title} ({len(band_items)} items)", ""]
        for it in sorted(band_items, key=lambda x: x["item_id"]):
            r = res.get(it["item_id"], {})
            rid = it["rule_id"]
            rec = merged.get(rid, {})
            aid = (rec.get("ratify_ref") or it["item_id"]).lower()
            L.append(f'<a id="{anchor(aid)}"></a>')
            L.append(f"### {rec.get('ratify_ref') or it['item_id']} — {rid}: {it.get('title', '')[:90]}")
            L.append("")
            if it.get("excerpt"):
                L += [f"> {it['excerpt'][:350]}", ""]
            if r.get("group") and r["group"] in groups:
                gr = groups[r["group"]]
                L += [f"*Grouped under* **{r['group']}** — {gr.get('question', '')}", ""]
            else:
                L += render_ratify(r)
        L.append("")

    section("P0 — high clinical impact (committee review first)", "P0")
    section("P1 — moderate clinical impact", "P1")

    L += ["## UNVERIFIABLE — proprietary rules requiring owner confirmation (grouped)", ""]
    for gid in sorted(groups):
        gr = groups[gid]
        L += [f'<a id="{anchor(gid)}"></a>', f"### {gid} — {gr.get('question', '')[:110]}", ""]
        member = gr.get("member_rule_ids") or []
        L += [f"**Member rules ({len(member)}):** " + ", ".join(member), ""]
        for o in gr.get("options") or []:
            L.append(f"- **{o.get('id')}** — {o.get('text', '')}")
        L += ["", f"**Recommended default.** {gr.get('recommended', 'TBD')}", ""]
    section("ADDENDUM — Phase-6 security/compliance findings", "ADDENDUM")

    L += ["## AMBIGUOUS extractions — keep-vs-retire recommendations", "",
          "| Item | Rule | Drafter recommendation | Disposition |", "|---|---|---|---|"]
    for it in sorted((i for i in esc["items"] if i["band"] == "AMBIGUOUS"), key=lambda x: x["item_id"]):
        r = res.get(it["item_id"], {})
        d = merged.get(it["rule_id"], {}).get("disposition", "?")
        L.append(f"| {it['item_id']} | {it['rule_id']} | {r.get('outcome', '?')}: "
                 f"{str(r.get('recommendation', ''))[:90]} | {d} |")
    L.append("")

    # rules already anchored above: P0/P1/ADDENDUM sections + UNVERIFIABLE groups
    anchored_rules = {it["rule_id"] for it in esc["items"]
                      if it["band"] in {"P0", "P1", "UNVERIFIABLE", "ADDENDUM"}}
    extra = [(rid, r) for rid, r in sorted(merged.items())
             if r.get("disposition") == "RATIFY" and rid not in anchored_rules]
    if extra:
        L += [f"## Additional RATIFY dispositions (not escalation-driven) ({len(extra)})", "",
              "| Ref | Rule | Why |", "|---|---|---|"]
        for rid, r in extra:
            L.append(f'| <a id="{anchor(r.get("ratify_ref") or rid)}"></a>{r.get("ratify_ref")} '
                     f"| {rid} | {str(r.get('justification', ''))[:110]} |")
        L.append("")

    for bdir, title in [("barriers", "Barrier residuals"), ("redteam", "Accepted-risk red-team findings")]:
        rows = []
        for f in sorted((WORK / bdir).rglob("*.yaml")):
            try:
                doc = load_yaml(f)
            except Exception:  # noqa: BLE001
                continue
            for c in (doc.get("conflicts") or doc.get("findings") or []):
                st = ((c.get("resolution") or {}).get("status") or c.get("status") or "").lower()
                if st in ("ratified", "accepted-risk"):
                    rows.append(c)
        if rows:
            L += [f"## {title} ({len(rows)})", ""]
            for c in rows:
                cid = c.get("conflict_id") or c.get("finding_id")
                L += [f'<a id="{anchor(cid)}"></a>', f"### {cid}", "",
                      c.get("description") or c.get("claim") or "", ""]

    tmp = OUT.with_suffix(".md.tmp")
    tmp.write_text("\n".join(L), encoding="utf-8")
    tmp.rename(OUT)
    print(f"[build_ratification] wrote {OUT.relative_to(ROOT)} — asks={len(asks)}, "
          f"groups={len(groups)}, extra_ratify={len(extra)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
