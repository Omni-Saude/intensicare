"""Tool: draw the seeded qualitative sample of disposition records for strong-model review.

Selection: per cluster max(3, ceil(5% of n)) seeded by sha256(inputs-manifest.json),
PLUS every disposition whose rule appears in a P0 escalation. Emits review batches
(~5 clusters per batch) under _work/reviews/samples/batch-N.yaml with full catalog
rule text + the disposition record, for reviewer agents.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from collections import defaultdict

from _lib import WORK, dump_yaml, load_yaml


def main() -> int:
    seed = hashlib.sha256((WORK / "gates/inputs-manifest.json").read_bytes()).hexdigest()
    rng = random.Random(seed)
    merged = json.loads((WORK / "dispositions/merged.json").read_text())["records"]
    esc = load_yaml(WORK / "escalations/escalations.yaml")
    p0_rules = {it["rule_id"] for it in esc["items"] if it["band"] == "P0"}

    manifest = json.loads((WORK / "catalog/id-manifest.json").read_text())
    rule_text: dict[str, dict] = {}
    cluster_of: dict[str, str] = {}
    for shard in manifest["shards"]:
        doc = load_yaml(WORK / f"catalog/shards/{shard}.yaml")
        for r in doc["rules"]:
            rule_text[r["id"]] = r
            cluster_of[r["id"]] = doc["cluster"]

    by_cluster: dict[str, list[str]] = defaultdict(list)
    for rid in sorted(merged):
        by_cluster[cluster_of.get(rid, "?")].append(rid)

    picked: dict[str, list[str]] = {}
    for cluster, rids in sorted(by_cluster.items()):
        n = max(3, math.ceil(0.05 * len(rids)))
        sample = set(rng.sample(rids, min(n, len(rids))))
        sample |= {r for r in rids if r in p0_rules}
        picked[cluster] = sorted(sample)

    clusters = sorted(picked)
    batches = [clusters[i::6] for i in range(6)]
    out = WORK / "reviews/samples"
    out.mkdir(parents=True, exist_ok=True)
    total = 0
    for i, batch in enumerate(batches, 1):
        items = []
        for cluster in batch:
            for rid in picked[cluster]:
                items.append({
                    "rule_id": rid, "cluster": cluster,
                    "catalog_rule": {k: rule_text[rid].get(k) for k in
                                     ("id", "name", "category", "type", "status", "description",
                                      "logic", "edge_cases", "verification", "escalations")},
                    "disposition_record": merged[rid],
                })
        total += len(items)
        dump_yaml({"batch": i, "clusters": batch, "n_items": len(items), "items": items},
                  out / f"batch-{i}.yaml")
    print(f"[make_samples] seed={seed[:12]} total_sampled={total} "
          f"(incl. {len(p0_rules)} P0-touching) across 6 batches -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
