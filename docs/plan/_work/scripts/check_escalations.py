"""Gate: escalation resolution coverage — all 351 items resolved or RATIFY'd.

Reads _work/escalations/escalations.yaml (truth, 351 items) and
resolutions-{p0,p1a,p1b,unverifiable-a,unverifiable-b,ambiguous}.yaml.
Cross-checks against dispositions merged.json when available.
"""
from __future__ import annotations

import json
import sys

from _lib import WORK, Gate, load_yaml

RES_FILES = ["resolutions-p0.yaml", "resolutions-p1a.yaml", "resolutions-p1b.yaml",
             "resolutions-unverifiable-a.yaml", "resolutions-unverifiable-b.yaml",
             "resolutions-ambiguous.yaml", "resolutions-addendum.yaml"]
OUTCOMES = {"RATIFY", "RETIRE-RECOMMENDED", "RESOLVED-BY-DISPOSITION"}
DISPO_RESOLVED_BANDS = {"P2", "P3"}  # locked policy: decided by the disposition pass


def main() -> int:
    g = Gate("check_escalations")
    esc = load_yaml(WORK / "escalations/escalations.yaml")
    items = {it["item_id"]: it for it in esc["items"]}
    g.add("ESC-TRUTH-351", len(items) == 351, "351 items", str(len(items)))

    res: dict[str, dict] = {}
    dupes, parse_fails = [], []
    for f in RES_FILES:
        p = WORK / "escalations" / f
        if not p.exists():
            parse_fails.append(f"MISSING {f}")
            continue
        try:
            doc = load_yaml(p)
        except Exception as e:  # noqa: BLE001
            parse_fails.append(f"{f}: {e}")
            continue
        for r in doc.get("records") or []:
            iid = r.get("item_id")
            if iid in res:
                dupes.append(iid)
            r["_file"] = f
            res[iid] = r
    g.add("ESC-RES-FILES", not parse_fails, "all 6 resolution files parse",
          f"{len(parse_fails)}", parse_fails)

    merged_path = WORK / "dispositions/merged.json"
    merged_ids = set()
    if merged_path.exists():
        import json
        merged_ids = set(json.loads(merged_path.read_text())["records"])
    covered = set(res)
    for iid, it in items.items():
        if it["band"] in DISPO_RESOLVED_BANDS and it["rule_id"] in merged_ids:
            covered.add(iid)  # locked policy: P2/P3 resolved by the disposition pass
    missing = sorted(set(items) - covered)
    unknown = sorted(set(res) - set(items))
    g.add("ESC-COVERAGE", not missing,
          "every item resolved (P2/P3 via dispositions; others via drafter records)",
          f"{len(missing)} missing", missing)
    g.add("ESC-NO-UNKNOWN", not unknown, "no resolutions for unknown items",
          f"{len(unknown)}", unknown)
    g.add("ESC-NO-DUPES", not dupes, "one resolution per item", f"{len(dupes)}", dupes)

    bad_outcome, bad_content, band_mismatch = [], [], []
    for iid, r in res.items():
        it = items.get(iid)
        if not it:
            continue
        out = r.get("outcome")
        if out not in OUTCOMES:
            bad_outcome.append(f"{iid}: {out}")
            continue
        band = it["band"]
        if band in {"P0", "P1"}:
            if out != "RATIFY":
                band_mismatch.append(f"{iid} ({band}): outcome {out}")
            rat = r.get("ratify") or {}
            if not (rat.get("question") and rat.get("options") and rat.get("recommended")
                    and rat.get("rationale")):
                bad_content.append(f"{iid}: ratify content incomplete")
        if band in {"UNVERIFIABLE", "ADDENDUM"} and out != "RATIFY":
            band_mismatch.append(f"{iid} ({band}): outcome {out}")
        if str(r.get("rule_id")) != it["rule_id"]:
            bad_content.append(f"{iid}: rule_id {r.get('rule_id')} != {it['rule_id']}")
    g.add("ESC-OUTCOMES", not bad_outcome, "valid outcome enum", f"{len(bad_outcome)}", bad_outcome)
    g.add("ESC-BAND-POLICY", not band_mismatch, "P0/P1/UNVERIFIABLE => RATIFY",
          f"{len(band_mismatch)}", band_mismatch)
    g.add("ESC-CONTENT", not bad_content, "ratify entries complete (question/options/recommended/rationale)",
          f"{len(bad_content)}", bad_content)

    p0_items = [iid for iid, it in items.items() if it["band"] == "P0"]
    p0_ok = [iid for iid in p0_items if res.get(iid, {}).get("outcome") == "RATIFY"]
    g.add("ESC-P0-12", len(p0_ok) == 12, "all 12 P0 items RATIFY-drafted", f"{len(p0_ok)}/12")

    mp = WORK / "dispositions/merged.json"
    if mp.exists():
        merged = json.loads(mp.read_text())["records"]
        inconsistent = []
        for iid, it in items.items():
            d = (merged.get(it["rule_id"]) or {}).get("disposition")
            r = res.get(iid, {})
            if it["band"] in {"P0", "P1", "UNVERIFIABLE"} and d and d != "RATIFY":
                inconsistent.append(f"{iid}: rule {it['rule_id']} dispositioned {d}")
            if it["band"] == "AMBIGUOUS" and r.get("outcome") == "RETIRE-RECOMMENDED" \
                    and d and d not in {"RETIRE", "SUPERSEDE", "RATIFY"}:
                inconsistent.append(f"{iid}: drafter says retire, disposition {d}")
        g.add("ESC-DISPO-CONSISTENT", not inconsistent,
              "resolutions consistent with dispositions", f"{len(inconsistent)}",
              inconsistent, warn=True)
    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
