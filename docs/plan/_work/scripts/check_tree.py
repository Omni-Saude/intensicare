"""Gate: deliverable-tree presence per phase. Usage: check_tree.py [--phase B|E]"""
from __future__ import annotations

import re
import sys

from _lib import ROOT, Gate

PLAN = ROOT / "docs/plan"
PHASE_B = [
    "clinical/units-registry.md",
    *[f"clinical/domains/{d}.md" for d in
      ["sepsis", "aki", "respiratory", "hemodynamics", "neuro-sedation", "electrolyte",
       "pharmaco-interaction", "early-warning-scores", "correlation-engine"]],
    "architecture/system-architecture.md", "architecture/data-model.md",
    "architecture/security-lgpd.md", "architecture/observability-slo.md",
    "architecture/alert-engine.md",
    "architecture/api/openapi.yaml", "architecture/api/asyncapi.yaml",
    "architecture/api/api-design.md",
    "design/design-language.md", "design/design-tokens.md", "design/component-library.md",
    "design/accessibility-standard.md",
    "design/screens/alert-triage.md", "design/screens/admin-config.md",
    "design/screens/clinical-forms.md",
    "delivery/regulatory-plan.md", "delivery/validation-plan.md", "delivery/test-strategy.md",
    "product/product-spec.md", "product/journey-maps.md",
]
PHASE_E_EXTRA = [
    "README.md", "executive-summary.md", "traceability-matrix.md", "RATIFICATION.md",
    "clinical/alert-catalog.md", "clinical/hazard-log.md",
    "design/screens/command-center.md", "design/screens/patient-timeline.md",
    "design/screens/handoff.md", "design/screens/alert-routing.md",
    "delivery/roadmap.md", "delivery/build-orchestrator-blueprint.md",
    "delivery/build-kickoff-prompt.md",
]
MIN_BYTES = {".md": 2000, ".yaml": 800}


def main() -> int:
    phase = "E" if "E" in sys.argv[1:] or "--phase E" in " ".join(sys.argv) else "B"
    g = Gate("check_tree")
    targets = PHASE_B + (PHASE_E_EXTRA if phase == "E" else [])
    problems = []
    for rel in targets:
        p = PLAN / rel
        if not p.exists():
            problems.append(f"MISSING {rel}")
            continue
        size = p.stat().st_size
        floor = MIN_BYTES.get(p.suffix, 1000)
        if size < floor:
            problems.append(f"TOO SMALL {rel} ({size}B < {floor})")
            continue
        if p.suffix == ".md":
            head = p.read_text(encoding="utf-8", errors="replace")[:4000]
            if not re.search(r"^# ", head, re.M):
                problems.append(f"NO H1 {rel}")
    g.add(f"TREE-PHASE-{phase}", not problems, f"all {len(targets)} deliverables present",
          f"{len(problems)} problems", problems)

    if phase == "E":
        stray = []
        allowed = set(targets) | {"architecture/adr"}
        for p in PLAN.rglob("*"):
            if p.is_dir() or "_work" in p.parts:
                continue
            rel = str(p.relative_to(PLAN))
            if rel not in allowed and not rel.startswith("architecture/adr/"):
                stray.append(rel)
        g.add("TREE-NO-STRAYS", not stray, "no files outside the mission tree",
              f"{len(stray)}", stray)
    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
