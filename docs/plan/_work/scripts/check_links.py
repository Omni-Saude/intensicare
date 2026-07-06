"""Gate: internal-link + anchor resolution across docs/plan/**/*.md (excluding _work),
unknown-RULE-token scan, and OpenAPI/AsyncAPI parse checks.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

from _lib import ROOT, WORK, Gate

PLAN = ROOT / "docs/plan"
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$", re.M)
RULE_RE = re.compile(r"RULE-[A-Z0-9][A-Z0-9-]*-\d{3}")


def slugify(heading: str) -> str:
    s = re.sub(r"[`*_~]|\{[^}]*\}", "", heading.strip().lower())
    s = re.sub(r"[^\w\- à-ÿ]", "", s, flags=re.UNICODE)
    return s.replace(" ", "-")


def anchors_of(path: Path) -> set[str]:
    seen: dict[str, int] = {}
    out = set()
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return out
    # Strip fenced blocks with a line-based state machine — robust to odd/unbalanced fences,
    # where a pair-matching regex would swallow real headings (root cause found in barrier C).
    kept, in_fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append(line)
    text = "\n".join(kept)
    for m in HEADING_RE.finditer(text):
        base = slugify(m.group(2))
        n = seen.get(base, 0)
        seen[base] = n + 1
        out.add(base if n == 0 else f"{base}-{n}")
    out.update(re.findall(r'<a\s+(?:name|id)="([^"]+)"', text))
    return out


def main() -> int:
    g = Gate("check_links")
    md_files = [p for p in PLAN.rglob("*.md") if "_work" not in p.parts]
    valid_ids = set(json.loads((WORK / "catalog/id-manifest.json").read_text())["shards"].keys())
    all_rule_ids: set[str] = set()
    for ids in json.loads((WORK / "catalog/id-manifest.json").read_text())["shards"].values():
        all_rule_ids.update(ids)

    broken, bad_rules = [], []
    for f in md_files:
        text = f.read_text(encoding="utf-8", errors="replace")
        rel = f.relative_to(PLAN)
        for rid in set(RULE_RE.findall(text)):
            if rid not in all_rule_ids:
                bad_rules.append(f"{rel}: unknown {rid}")
        for m in LINK_RE.finditer(text):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            frag = None
            if "#" in target:
                target, frag = target.split("#", 1)
            if not target:
                tgt_file = f
            else:
                tgt_file = (f.parent / target).resolve()
                try:
                    tgt_file.relative_to(ROOT)
                except ValueError:
                    broken.append(f"{rel}: escapes repo {m.group(1)}")
                    continue
                if not tgt_file.exists():
                    broken.append(f"{rel}: missing {m.group(1)}")
                    continue
            if frag and tgt_file.suffix == ".md":
                if slugify(frag) not in {slugify(a) for a in anchors_of(tgt_file)}:
                    broken.append(f"{rel}: anchor #{frag} not in {tgt_file.name}")
    g.add("LINKS-RESOLVE", not broken, "all internal links + anchors resolve",
          f"{len(broken)} broken", broken)
    g.add("LINKS-RULE-IDS", not bad_rules, "every RULE- token exists in the 959 catalog",
          f"{len(bad_rules)} unknown", bad_rules)

    oa = PLAN / "architecture/api/openapi.yaml"
    if oa.exists():
        try:
            doc = yaml.safe_load(oa.read_text())
            ok = str(doc.get("openapi", "")).startswith("3.1") and doc.get("paths")
            g.add("LINKS-OPENAPI", bool(ok), "openapi 3.1 with paths",
                  f"openapi={doc.get('openapi')}, paths={len(doc.get('paths') or {})}")
        except Exception as e:  # noqa: BLE001
            g.add("LINKS-OPENAPI", False, "parses", str(e)[:120])
    aa = PLAN / "architecture/api/asyncapi.yaml"
    if aa.exists():
        try:
            doc = yaml.safe_load(aa.read_text())
            g.add("LINKS-ASYNCAPI", bool(doc.get("asyncapi") and doc.get("channels")),
                  "asyncapi with channels",
                  f"asyncapi={doc.get('asyncapi')}, channels={len(doc.get('channels') or {})}")
        except Exception as e:  # noqa: BLE001
            g.add("LINKS-ASYNCAPI", False, "parses", str(e)[:120])
    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
