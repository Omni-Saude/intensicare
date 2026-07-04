"""Gate: independent verification of the rendered traceability matrix.

Deliberately does NOT share parsing code with build_matrix.py: re-parses the
rendered markdown tables with its own parser and checks three-way equality:
matrix rows <-> disposition YAML records <-> the 959-ID catalog union, and
matrix escalation rows <-> the live ESCALATIONS parse (351 items).
"""
from __future__ import annotations

import json
import re
import sys

from _lib import ROOT, WORK, Gate, load_yaml

MATRIX = ROOT / "docs/plan/traceability-matrix.md"


def parse_table(text: str, section: str) -> list[list[str]]:
    m = re.search(rf"^## {re.escape(section)}.*?\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return []
    rows = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|[\s\-|:]+\|$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and not cells[0].startswith("**") and not cells[0] in ("Rule", "Item", "ADR", "Disposition", "Escalation band", "Vision item"):
            rows.append(cells)
    return rows


def main() -> int:
    g = Gate("check_matrix")
    if not MATRIX.exists():
        g.add("MATRIX-EXISTS", False, "traceability-matrix.md exists", "MISSING")
        return g.finish()
    text = MATRIX.read_text(encoding="utf-8")

    records = json.loads((WORK / "dispositions/merged.json").read_text())["records"]
    catalog_ids = set()
    for ids in json.loads((WORK / "catalog/id-manifest.json").read_text())["shards"].values():
        catalog_ids.update(ids)

    rule_rows = parse_table(text, "Rules (959)")
    row_ids = {r[0] for r in rule_rows}
    g.add("MATRIX-RULES-COUNT", len(rule_rows) == 959, "959 rule rows", str(len(rule_rows)))
    g.add("MATRIX-RULES-VS-CATALOG", row_ids == catalog_ids,
          "row IDs == catalog IDs",
          f"{len(catalog_ids - row_ids)} missing, {len(row_ids - catalog_ids)} extra",
          sorted(catalog_ids - row_ids)[:20] + sorted(row_ids - catalog_ids)[:20])
    mismatch = [f"{r[0]}: matrix {r[4]} != yaml {records.get(r[0], {}).get('disposition')}"
                for r in rule_rows
                if records.get(r[0], {}).get("disposition") != r[4]]
    g.add("MATRIX-RULES-VS-YAML", not mismatch, "matrix disposition == YAML disposition",
          f"{len(mismatch)} mismatches", mismatch)

    esc = load_yaml(WORK / "escalations/escalations.yaml")
    esc_rows = parse_table(text, "Escalations (351)")
    g.add("MATRIX-ESC-COUNT", len(esc_rows) == 351, "351 escalation rows", str(len(esc_rows)))
    live = {(it["item_id"], it["band"], it["rule_id"]) for it in esc["items"]}
    rendered = {(r[0], r[1], r[2]) for r in esc_rows}
    g.add("MATRIX-ESC-VS-LIVE", live == rendered, "escalation rows == live parse",
          f"{len(live - rendered)} missing, {len(rendered - live)} extra",
          [str(x) for x in sorted(live - rendered)[:10]])
    missing_outcome = [r[0] for r in esc_rows if r[3] in ("MISSING", "")]
    g.add("MATRIX-ESC-OUTCOMES", not missing_outcome, "every escalation row has an outcome",
          f"{len(missing_outcome)}", missing_outcome)

    adr_rows = parse_table(text, "Legacy design ADRs (18)")
    g.add("MATRIX-ADRS", len(adr_rows) == 18, "18 ADR rows", str(len(adr_rows)))
    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
