"""Cut the 27 phase-2 catalog YAMLs into 38 shard files for disposition agents,
embedding each rule's escalation refs (from by-rule.json). Asserts every one of
the 959 rule IDs lands in exactly one shard.

Outputs:
  _work/catalog/shards/<cluster>[-pN].yaml   (38 files)
  _work/catalog/id-manifest.json             shard -> [ids] + global set stats
"""
from __future__ import annotations

import json
import sys

from _lib import ROOT, WORK, Gate, dump_json, dump_yaml, load_yaml

CATALOG = ROOT / "docs/rules/extraction/phase2/catalog"
SPLITS = {  # cluster -> number of parts
    "sepse": 3, "evolucoes": 2, "movimentacao-adt": 2, "auth-usuarios": 2,
    "balanco-hidrico": 2, "operacional-infra": 2, "tenancy-organizacao": 2,
    "comunicacao": 2, "formularios-clinicos": 2, "prescricao": 2,
}
EXPECTED_TOTAL = 959
EXPECTED_STALE_INDEX_DELTA = 12  # catalog-index.json is missing the 12 Phase-6 gap rules


def main() -> int:
    g = Gate("shard_catalog")
    by_rule = json.loads((WORK / "escalations/by-rule.json").read_text())

    files = sorted(CATALOG.glob("*.yaml"))
    g.add("SHARD-27-FILES", len(files) == 27, "27 catalog files", str(len(files)))

    all_ids: list[str] = []
    shards: dict[str, list[dict]] = {}
    for f in files:
        doc = load_yaml(f)
        cluster = doc.get("cluster") or f.stem
        rules = doc.get("rules") or []
        for r in rules:
            r["escalations"] = by_rule.get(r.get("id"), [])
            all_ids.append(r.get("id"))
        parts = SPLITS.get(f.stem, 1)
        if parts == 1:
            shards[f.stem] = rules
        else:
            size = -(-len(rules) // parts)  # ceil
            for i in range(parts):
                shards[f"{f.stem}-p{i + 1}"] = rules[i * size:(i + 1) * size]

    g.add("SHARD-TOTAL", len(all_ids) == EXPECTED_TOTAL, f"{EXPECTED_TOTAL} rules",
          str(len(all_ids)))
    g.add("SHARD-UNIQUE", len(set(all_ids)) == len(all_ids), "no duplicate IDs",
          f"{len(all_ids) - len(set(all_ids))} dupes")
    g.add("SHARD-38", len(shards) == 38, "38 shards", str(len(shards)))
    empty = [k for k, v in shards.items() if not v]
    g.add("SHARD-NONEMPTY", not empty, "no empty shard", str(empty))

    # stale-index integrity pin
    idx = {e["id"] for e in json.loads((ROOT / "docs/rules/catalog-index.json").read_text())}
    delta = sorted(set(all_ids) - idx)
    g.add("SHARD-INDEX-DELTA", len(delta) == EXPECTED_STALE_INDEX_DELTA and not (idx - set(all_ids)),
          f"catalog-index.json stale by exactly the {EXPECTED_STALE_INDEX_DELTA} gap rules",
          f"{len(delta)} missing from index, {len(idx - set(all_ids))} extra in index", delta,
          warn=(len(delta) == EXPECTED_STALE_INDEX_DELTA))

    out = WORK / "catalog/shards"
    out.mkdir(parents=True, exist_ok=True)
    manifest = {}
    sharded_ids: list[str] = []
    for name, rules in sorted(shards.items()):
        cluster = name.split("-p")[0] if "-p" in name and name.split("-p")[-1].isdigit() else name
        n_esc = sum(1 for r in rules if r["escalations"])
        dump_yaml({"shard": name, "cluster": cluster, "rule_count": len(rules),
                   "rules_with_escalations": n_esc, "rules": rules}, out / f"{name}.yaml")
        ids = [r["id"] for r in rules]
        manifest[name] = ids
        sharded_ids.extend(ids)

    g.add("SHARD-EXACTLY-ONCE",
          sorted(sharded_ids) == sorted(all_ids) and len(sharded_ids) == len(set(sharded_ids)),
          "every ID in exactly one shard", f"{len(sharded_ids)} sharded / {len(all_ids)} total")

    esc_rules = sum(1 for i in all_ids if i in by_rule)
    dump_json({"total_rules": len(all_ids), "shards": manifest,
               "rules_with_escalations": esc_rules,
               "escalation_rule_ids_missing_from_catalog":
                   sorted(set(by_rule) - set(all_ids))},
              WORK / "catalog/id-manifest.json")
    orphans = sorted(set(by_rule) - set(all_ids))
    g.add("SHARD-ESC-ORPHANS", not orphans, "every escalated rule ID exists in catalog",
          f"{len(orphans)} orphans", orphans)

    sizes = sorted(((len(v), k) for k, v in shards.items()), reverse=True)[:5]
    print(f"[shard_catalog] 38 shards written; largest: "
          + ", ".join(f"{k}={n}" for n, k in sizes)
          + f"; {esc_rules}/{len(all_ids)} rules carry escalation refs")
    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
