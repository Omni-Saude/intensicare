"""Gate: RATIFICATION.md structure — every RATIFY disposition anchor resolves, all
12 P0 + 45 P1 rule IDs present, the FIVE audit asks answered, entries carry
question/options/recommendation.
"""
from __future__ import annotations

import json
import re
import sys

from _lib import ROOT, WORK, Gate, load_yaml

RAT = ROOT / "docs/plan/RATIFICATION.md"


def main() -> int:
    g = Gate("check_ratification")
    if not RAT.exists():
        g.add("RAT-EXISTS", False, "RATIFICATION.md exists", "MISSING")
        return g.finish()
    text = RAT.read_text(encoding="utf-8")
    anchors = set(re.findall(r'<a id="([^"]+)"></a>', text))

    merged = json.loads((WORK / "dispositions/merged.json").read_text())["records"]
    ratify = {rid: r for rid, r in merged.items() if r.get("disposition") == "RATIFY"}
    missing_anchor = []
    for rid, r in sorted(ratify.items()):
        tgt = str(r.get("target") or "")
        frag = tgt.split("#", 1)[1].lower() if "#" in tgt else ""
        ref = str(r.get("ratify_ref") or "").lower()
        if not ({frag, ref, re.sub(r"[^a-z0-9-]", "", ref)} & anchors) and rid.lower() not in text.lower():
            missing_anchor.append(f"{rid} (ref {r.get('ratify_ref')}, target #{frag})")
    g.add("RAT-ANCHORS", not missing_anchor,
          f"every RATIFY disposition ({len(ratify)}) anchored or named in RATIFICATION.md",
          f"{len(missing_anchor)} unanchored", missing_anchor)

    esc = load_yaml(WORK / "escalations/escalations.yaml")
    for band, expect in (("P0", 12), ("P1", 45)):
        ids = [it["rule_id"] for it in esc["items"] if it["band"] == band]
        absent = [rid for rid in ids if rid not in text]
        g.add(f"RAT-{band}-PRESENT", not absent, f"all {expect} {band} rule IDs named",
              f"{len(absent)} absent", absent)

    for ask in ("ask-1", "ask-2", "ask-3", "ask-4", "ask-5"):
        g.add(f"RAT-{ask.upper()}", ask in anchors or ask.upper() in text,
              f"{ask.upper()} section present", "present" if (ask in anchors or ask.upper() in text) else "ABSENT")

    n_q = len(re.findall(r"\*\*Question\.\*\*", text))
    n_rec = len(re.findall(r"\*\*Recommended default\.\*\*", text))
    g.add("RAT-CONTENT", n_q >= 57 and n_rec >= 40,
          ">=57 questions (P0+P1) and >=40 recommended defaults",
          f"questions={n_q}, recommended={n_rec}")
    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
