"""Tool: compute judge-panel decisions from scorecards.

Reads _work/panels/<topic>/score-*.yaml (schema in RUBRIC.md), applies fixed weights,
disqualifies safety-vetoed concepts, writes _work/panels/<topic>/decision.yaml.
"""
from __future__ import annotations

import sys
from collections import defaultdict

from _lib import WORK, Gate, dump_yaml, load_yaml

WEIGHTS = {"safety": 0.30, "persona_fit": 0.25, "feasibility": 0.20,
           "alarm_fatigue_a11y": 0.15, "innovation": 0.10}
TOPICS = ["home-surface", "timeline-model", "alert-routing"]


def main() -> int:
    g = Gate("panel_decide")
    for topic in TOPICS:
        tdir = WORK / "panels" / topic
        cards = []
        for f in sorted(tdir.glob("score-*.yaml")):
            try:
                doc = load_yaml(f)
                cards.extend(doc if isinstance(doc, list) else [doc])
            except Exception as e:  # noqa: BLE001
                g.add(f"PANEL-{topic}-PARSE", False, "scorecards parse", f"{f.name}: {e}")
        by_concept: dict[str, list[dict]] = defaultdict(list)
        for c in cards:
            by_concept[str(c.get("concept"))].append(c)
        g.add(f"PANEL-{topic}-CARDS", len(cards) >= 6 and all(len(v) >= 2 for v in by_concept.values()),
              ">=6 scorecards, >=2 per concept (economy mode: 2 scorers)",
              f"{len(cards)} cards over concepts {sorted(by_concept)}")

        totals, vetoes = {}, {}
        for concept, cs in sorted(by_concept.items()):
            per_scorer = []
            for c in cs:
                s = c.get("scores") or {}
                if set(WEIGHTS) - set(s):
                    g.add(f"PANEL-{topic}-{concept}-DIMS", False, "all 5 dimensions scored",
                          f"{c.get('scorer')}: missing {sorted(set(WEIGHTS) - set(s))}")
                    continue
                per_scorer.append(sum(WEIGHTS[k] * float(s[k]) for k in WEIGHTS))
                if c.get("veto") and c.get("scorer") == "clinical-safety-officer":
                    vetoes[concept] = c.get("rationale", "vetoed")
            totals[concept] = round(sum(per_scorer) / len(per_scorer), 3) if per_scorer else 0.0

        eligible = {k: v for k, v in totals.items() if k not in vetoes}
        if not eligible:
            g.add(f"PANEL-{topic}-WINNER", False, "an eligible concept", "ALL VETOED")
            continue
        winner = max(eligible, key=lambda k: eligible[k])
        must_fix = sorted({m for c in by_concept[winner] for m in c.get("must_fix") or []})
        salvage = sorted({s for k, cs in by_concept.items() if k != winner
                          for c in cs for s in c.get("salvage") or []})
        dump_yaml({"topic": topic, "winner": winner, "totals": totals, "vetoes": vetoes,
                   "must_fix": must_fix, "salvage": salvage,
                   "scorers": sorted({c.get("scorer") for c in cards}),
                   "signoffs": []},
                  tdir / "decision.yaml")
        g.add(f"PANEL-{topic}-WINNER", True, "decision computed",
              f"winner={winner} totals={totals} vetoes={sorted(vetoes)}")
    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
