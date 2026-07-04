"""Parse docs/rules/ESCALATIONS.md into structured items, self-validating against
the file's own count-summary table.

Outputs:
  _work/escalations/escalations.yaml  — [{item_id, band, rule_id, title, excerpt}]
  _work/escalations/by-rule.json      — rule_id -> [{item_id, band, title, excerpt}]

Encoding (verified on disk):
  P0/P1/P2 sections + Addendum: items are '### RULE-… — title' (addendum also '#### RULE-…').
  P3 / UNVERIFIABLE / AMBIGUOUS: items are table rows whose first cell is a RULE id;
  UNVERIFIABLE rows are grouped under '### <cluster> (n)' subheads (not items).
  'Cross-cutting systemic issues' is NOT an item section.
"""
from __future__ import annotations

import re
import sys

from _lib import ROOT, WORK, Gate, dump_json, dump_yaml

SRC = ROOT / "docs/rules/ESCALATIONS.md"

BAND_SECTIONS = {
    "P0 — High clinical impact": ("P0", "headings"),
    "P1 — Moderate clinical impact": ("P1", "headings"),
    "P2 — Low clinical impact": ("P2", "rows"),
    "P3 — Discrepancies with no expected clinical impact": ("P3", "rows"),
    "Internal rules needing owner review (UNVERIFIABLE)": ("UNVERIFIABLE", "rows"),
    "AMBIGUOUS extractions": ("AMBIGUOUS", "rows"),
    "Addendum — Phase 6 coverage-sweep findings (gap remediation)": ("ADDENDUM", "headings"),
}

# summary-table row label -> band key
SUMMARY_LABELS = {
    "P0 — High clinical impact": "P0",
    "P1 — Moderate clinical impact": "P1",
    "P2 — Low clinical impact": "P2",
    "P3 — Discrepancies, no expected clinical impact": "P3",
    "Internal rules needing owner review (UNVERIFIABLE)": "UNVERIFIABLE",
    "AMBIGUOUS extractions": "AMBIGUOUS",
    "Addendum — Phase 6 gap findings": "ADDENDUM",
}

RULE_RE = re.compile(r"RULE-[A-Z0-9][A-Z0-9-]*-\d{3}")


def split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"^## (.+?)\s*$", line)
        if m:
            current = m.group(1)
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return sections


def parse_summary(lines: list[str]) -> dict[str, int]:
    counts = {}
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3:
            label = cells[0].strip("* ")
            if label in SUMMARY_LABELS:
                try:
                    counts[SUMMARY_LABELS[label]] = int(cells[-1].strip("* "))
                except ValueError:
                    pass
    return counts


def items_from_headings(band: str, lines: list[str]) -> list[dict]:
    items = []
    i = 0
    while i < len(lines):
        m = re.match(r"^#{3,4} (RULE-[A-Z0-9-]+-\d{3})\s*[—-]?\s*(.*)$", lines[i])
        if m:
            body = []
            j = i + 1
            while j < len(lines) and not re.match(r"^#{3,4} ", lines[j]):
                body.append(lines[j])
                j += 1
            text = "\n".join(body)
            dev = re.search(r"\*\*The exact deviation\.\*\*\s*(.+?)(?:\n\n|\Z)", text, re.S)
            excerpt = (dev.group(1) if dev else text.strip()).strip().replace("\n", " ")[:400]
            items.append({"band": band, "rule_id": m.group(1), "title": m.group(2).strip(),
                          "excerpt": excerpt})
            i = j
        else:
            i += 1
    return items


def items_from_rows(band: str, lines: list[str]) -> list[dict]:
    items = []
    for line in lines:
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        m = RULE_RE.search(cells[0])
        if not m:
            continue
        title = cells[1] if len(cells) > 1 else ""
        note = cells[2] if len(cells) > 2 else ""
        items.append({"band": band, "rule_id": m.group(0), "title": title.strip("`* "),
                      "excerpt": note[:400]})
    return items


def main() -> int:
    g = Gate("parse_escalations")
    text = SRC.read_text(encoding="utf-8")
    sections = split_sections(text)

    declared = parse_summary(sections.get("Count summary", []))
    g.add("ESC-SUMMARY-TABLE", len(declared) == 7, "7 band counts declared",
          f"{len(declared)} parsed: {declared}")

    all_items: list[dict] = []
    per_band: dict[str, int] = {}
    for title, (band, mode) in BAND_SECTIONS.items():
        lines = sections.get(title)
        if lines is None:
            g.add(f"ESC-SECTION-{band}", False, f"section '{title}' present", "MISSING")
            continue
        items = items_from_headings(band, lines) if mode == "headings" else items_from_rows(band, lines)
        per_band[band] = len(items)
        all_items.extend(items)
        exp = declared.get(band)
        g.add(f"ESC-COUNT-{band}", exp == len(items), f"{exp} items (per summary table)",
              f"{len(items)} parsed")

    total = len(all_items)
    g.add("ESC-TOTAL", total == 351, "351 items", str(total))

    dupes = {}
    for it in all_items:
        dupes.setdefault(it["rule_id"], []).append(it["band"])
    multi = {k: v for k, v in dupes.items() if len(v) > 1}
    g.add("ESC-UNIQUE", not multi, "each rule in exactly one band (per doc's own claim)",
          f"{len(multi)} rules in multiple bands", [f"{k}: {v}" for k, v in multi.items()],
          warn=True)

    for n, it in enumerate(all_items, 1):
        it["item_id"] = f"ESC-{it['band']}-{n:03d}"

    out = WORK / "escalations"
    out.mkdir(parents=True, exist_ok=True)
    dump_yaml({"source": str(SRC.relative_to(ROOT)), "total": total, "per_band": per_band,
               "items": all_items}, out / "escalations.yaml")
    by_rule: dict[str, list] = {}
    for it in all_items:
        by_rule.setdefault(it["rule_id"], []).append(
            {"item_id": it["item_id"], "band": it["band"], "title": it["title"],
             "excerpt": it["excerpt"]})
    dump_json(by_rule, out / "by-rule.json")
    print(f"[parse_escalations] {total} items, {len(by_rule)} distinct rule IDs -> "
          f"{out.relative_to(ROOT)}/")
    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
