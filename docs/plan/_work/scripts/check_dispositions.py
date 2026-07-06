"""Gate: disposition coverage + policy legality + anti-shallow-read for the 959 rules.

Reads _work/catalog/shards/*.yaml (truth: rule -> status/verdict/logic/escalations)
and _work/dispositions/<shard>.yaml (agent outputs; one file per shard).
Writes _work/dispositions/merged.json for downstream gates.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter

from _lib import ROOT, WORK, Gate, dump_json, load_yaml

DISPOSITIONS = {"ADOPT", "ADOPT-CORRECTED", "ADAPT", "SUPERSEDE", "RETIRE", "RATIFY"}
RATIFY_BANDS = {"P0", "P1", "UNVERIFIABLE", "ADDENDUM"}


def _strings(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from _strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from _strings(v)
    elif isinstance(o, str):
        yield o


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def verdict_of(rule: dict) -> str:
    v = rule.get("verification")
    if isinstance(v, dict):
        return str(v.get("verdict") or "NOT_APPLICABLE")
    if isinstance(v, str) and v.strip():
        return v
    return "NOT_APPLICABLE"


def main() -> int:
    g = Gate("check_dispositions")
    manifest = json.loads((WORK / "catalog/id-manifest.json").read_text())
    shards = manifest["shards"]

    truth: dict[str, dict] = {}
    for shard in shards:
        doc = load_yaml(WORK / f"catalog/shards/{shard}.yaml")
        for r in doc["rules"]:
            truth[r["id"]] = {
                "status": str(r.get("status") or ""),
                "verdict": verdict_of(r),
                "text": norm(" ".join(_strings(r))),
                "bands": {e["band"] for e in r.get("escalations", [])},
                "cluster": doc["cluster"],
            }
    all_ids = set(truth)
    g.add("DISP-TRUTH-959", len(all_ids) == 959, "959 truth IDs", str(len(all_ids)))

    records: dict[str, dict] = {}
    dupes, parse_fails = [], []
    for shard in shards:
        p = WORK / f"dispositions/{shard}.yaml"
        if not p.exists():
            parse_fails.append(f"MISSING {p.name}")
            continue
        try:
            doc = load_yaml(p)
            recs = doc.get("records") or []
        except Exception as e:  # noqa: BLE001
            parse_fails.append(f"{p.name}: {e}")
            continue
        for r in recs:
            rid = r.get("rule_id")
            if rid in records:
                dupes.append(rid)
            r["_shard"] = shard
            records[rid] = r
    g.add("DISP-FILES-PARSE", not parse_fails, "all 38 shard disposition files parse",
          f"{len(parse_fails)} problems", parse_fails)

    got = set(records)
    hallucinated = sorted(got - all_ids - {None})
    missing = sorted(all_ids - got)
    g.add("DISP-NO-HALLUCINATED", not hallucinated, "0 unknown rule IDs",
          f"{len(hallucinated)}", hallucinated)
    g.add("DISP-NO-MISSING", not missing, "all 959 covered", f"{len(missing)} missing", missing)
    g.add("DISP-NO-DUPES", not dupes, "no rule dispositioned twice", f"{len(dupes)}", dupes)

    bad_enum, bad_just, bad_evid, bad_echo, bad_quote = [], [], [], [], []
    bad_target, bad_band, bad_adopt, vacuity = [], [], [], []
    per_shard_grams: dict[str, Counter] = {}
    for rid, r in records.items():
        if rid not in truth:
            continue
        t = truth[rid]
        d = r.get("disposition")
        if d not in DISPOSITIONS:
            bad_enum.append(f"{rid}: {d}")
            continue
        just = str(r.get("justification") or "")
        if len(just) < 120:
            bad_just.append(f"{rid} ({len(just)} chars)")
        if not r.get("evidence"):
            bad_evid.append(rid)
        echo = r.get("catalog_echo") or {}
        if norm(echo.get("status")) != norm(t["status"]) or \
           norm(echo.get("verdict")) != norm(t["verdict"]):
            bad_echo.append(f"{rid}: echo {echo.get('status')}/{echo.get('verdict')} "
                            f"!= {t['status']}/{t['verdict']}")
        q = norm(r.get("source_quote"))
        if len(q) < 20 or q not in t["text"]:
            bad_quote.append(rid)
        target = r.get("target")
        if d in {"ADOPT", "ADOPT-CORRECTED", "ADAPT", "SUPERSEDE"} and not target:
            bad_target.append(f"{rid}: {d} without target")
        if d == "RATIFY" and not (r.get("ratify_ref") and target and "RATIFICATION" in str(target)):
            bad_target.append(f"{rid}: RATIFY without ratify_ref/RATIFICATION target")
        # Post-ratification: rules with RATIFY bands that have been ratified ([RATIFIED] marker)
        # are exempt from the pre-ratification policy check
        is_ratified = just.lower().startswith("[ratified")
        if t["bands"] & RATIFY_BANDS and d != "RATIFY" and not is_ratified:
            bad_band.append(f"{rid}: bands {sorted(t['bands'])} but {d}")
        if d == "ADOPT" and (norm(t["status"]) != "ok" or not norm(t["verdict"]).startswith("verified")):
            if not is_ratified:
                if norm(t["verdict"]) not in {"not_applicable", "not applicable", "n/a", "—", ""}:
                    bad_adopt.append(f"{rid}: ADOPT with status={t['status']} verdict={t['verdict']}")
                elif norm(t["status"]) != "ok":
                    bad_adopt.append(f"{rid}: ADOPT with status={t['status']}")
        toks = just.lower().split()
        grams = [" ".join(toks[i:i + 8]) for i in range(0, max(0, len(toks) - 7), 4)]
        per_shard_grams.setdefault(r["_shard"], Counter()).update(set(grams))
        ttoks = set(t["text"].split())
        jtoks = set(toks)
        if jtoks and len(jtoks & ttoks) / len(jtoks) > 0.85:
            vacuity.append(f"{rid}: justification ~pure echo of catalog text")

    g.add("DISP-ENUM", not bad_enum, "valid disposition enum", f"{len(bad_enum)}", bad_enum)
    g.add("DISP-JUSTIFICATION-LEN", not bad_just, ">=120 chars", f"{len(bad_just)} short", bad_just)
    g.add("DISP-EVIDENCE", not bad_evid, ">=1 evidence per record", f"{len(bad_evid)}", bad_evid)
    g.add("DISP-CATALOG-ECHO", not bad_echo, "echo == catalog status/verdict",
          f"{len(bad_echo)} mismatches", bad_echo)
    g.add("DISP-SOURCE-QUOTE", not bad_quote, "verbatim >=20-char substring of rule text",
          f"{len(bad_quote)} failed", bad_quote)
    g.add("DISP-TARGET", not bad_target, "target requiredness per disposition",
          f"{len(bad_target)}", bad_target)
    g.add("DISP-BAND-POLICY", not bad_band, "P0/P1/UNVERIFIABLE bands => RATIFY",
          f"{len(bad_band)} violations", bad_band)
    g.add("DISP-ADOPT-VERIFIED", not bad_adopt,
          "plain ADOPT only for status OK + verdict VERIFIED/N-A", f"{len(bad_adopt)}", bad_adopt)

    heavy_dupe = []
    for shard, ctr in per_shard_grams.items():
        n_recs = sum(1 for r in records.values() if r["_shard"] == shard)
        worst = ctr.most_common(1)
        if worst and n_recs >= 5 and worst[0][1] / n_recs > 0.5:
            heavy_dupe.append(f"{shard}: 8-gram '{worst[0][0][:50]}…' in {worst[0][1]}/{n_recs}")
    g.add("DISP-VACUITY", not (heavy_dupe or vacuity), "no template/echo justifications",
          f"{len(heavy_dupe)} shard-level, {len(vacuity)} echoes",
          heavy_dupe + vacuity, warn=True)

    if not missing and not hallucinated and not dupes:
        hist = Counter(r.get("disposition") for r in records.values())
        dump_json({"histogram": dict(hist),
                   "records": {rid: {k: v for k, v in r.items() if k != "_shard"}
                               for rid, r in sorted(records.items())}},
                  WORK / "dispositions/merged.json")
        print(f"[check_dispositions] merged.json written; histogram: {dict(hist)}")
    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
