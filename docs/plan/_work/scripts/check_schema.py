"""Gate: Phase-A brief + ledger validation (--phase A). Structural schema checks
for _work artifacts; content pins for the load-bearing briefs.
"""
from __future__ import annotations

import json
import re
import sys

from _lib import ROOT, WORK, Gate, load_yaml

DOC_BRIEFS = [
    "vision", "adr-001", "implementation-plan", "audit-report", "design-adrs",
    "design-inventory", "escalations-systemic", "existing-alert-catalog",
    "personas", "data-model", "review-queue", "scorers",
]
CLUSTERS = [
    "alertas", "antimicrobiano", "auditoria-logs", "auth-usuarios", "balanco-hidrico",
    "cadastros-ui", "clinical-scoring", "comunicacao", "documentacao-faturamento",
    "eficiencia", "equilibrio", "estabilidade", "evolucoes", "formularios-clinicos",
    "indicadores-etl", "movimentacao-adt", "nutricao", "operacional-infra",
    "piora-clinica", "prescricao", "profilaxia", "sedacao", "sepse", "sinais-vitais",
    "tenancy-organizacao", "trilhas-engine", "ventilacao",
]
# brief -> (fact-id prefix, minimum count)
FACT_PINS = {
    "personas": [("PER-", 12)],
    "existing-alert-catalog": [("CAT-", 32)],
    "audit-report": [("ASK-", 5)],
    "design-adrs": [("ADR-00", 18)],
    "escalations-systemic": [("SYS-", 10), ("P0-", 12)],
}
LEDGER_PINS = [
    ("INV-invariants", r"INV-[1-6]", 6),
    ("ADR001-constraints", r"ADR001-C-\d+", 8),
    ("CON-SEED", r"CON-SEED-\d+", 12),
]


def check_brief(g: Gate, path, name: str):
    if not path.exists():
        g.add(f"BRIEF-{name}", False, "file exists", "MISSING")
        return
    try:
        b = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        g.add(f"BRIEF-{name}", False, "valid JSON", f"parse error: {e}")
        return
    problems = []
    if not b.get("brief_id"):
        problems.append("no brief_id")
    if b.get("authority") not in {"adr-001", "vision", "directive", "audit"}:
        problems.append(f"bad authority {b.get('authority')}")
    src = b.get("source") or {}
    if not (isinstance(src, dict) and src.get("read_complete") is True) and not any(
        isinstance(s, dict) and s.get("read_complete") is True for s in (b.get("source_files") or [])
    ):
        if not src.get("read_complete"):
            problems.append("read_complete not true")
    facts = b.get("facts") or []
    if not facts:
        problems.append("no facts")
    for f in facts[:500]:
        if not (f.get("id") and f.get("claim") and f.get("source_ref")):
            problems.append(f"fact missing id/claim/source_ref: {str(f)[:80]}")
            break
    size = path.stat().st_size
    if size > 64_000:
        problems.append(f"oversize {size}B > 64KB")
    g.add(f"BRIEF-{name}", not problems, "schema-valid brief", "; ".join(problems) or "ok",
          problems)
    if size > 26_000:
        g.add(f"BRIEF-{name}-SIZE", False, "<=26KB", f"{size}B", warn=True)
    for prefix, minimum in FACT_PINS.get(name, []):
        n = sum(1 for f in facts if str(f.get("id", "")).startswith(prefix))
        g.add(f"BRIEF-{name}-PIN-{prefix.rstrip('-')}", n >= minimum,
              f">={minimum} facts with id prefix {prefix}", str(n))


def main() -> int:
    g = Gate("check_schema")
    for name in DOC_BRIEFS:
        check_brief(g, WORK / f"briefs/{name}.json", name)
    for c in CLUSTERS:
        check_brief(g, WORK / f"briefs/clusters/{c}.json", f"cluster-{c}")

    lp = WORK / "constraints/ledger.yaml"
    if not lp.exists():
        g.add("LEDGER", False, "ledger.yaml exists", "MISSING")
        return g.finish()
    try:
        ledger = load_yaml(lp)
        entries = ledger.get("entries") or []
    except Exception as e:  # noqa: BLE001
        g.add("LEDGER", False, "valid YAML", f"parse error: {e}")
        return g.finish()
    g.add("LEDGER", len(entries) >= 30, ">=30 merged entries", str(len(entries)))
    blob = json.dumps(ledger, ensure_ascii=False)
    for label, pat, minimum in LEDGER_PINS:
        n = len(set(re.findall(pat, blob)))
        g.add(f"LEDGER-{label}", n >= minimum, f">={minimum} distinct {pat}", str(n))
    for label, needle in [
        ("PPV60", "60"), ("IGNORED10", "10"), ("P95-30S", "30"),
        ("UNITS", "mcg/kg/min"), ("LACTATE", "mmol/L"),
    ]:
        g.add(f"LEDGER-METRIC-{label}", needle in blob, f"mentions {needle!r}", "present" if needle in blob else "ABSENT")
    bad = [e.get("id") for e in entries
           if not (e.get("id") and e.get("text") and e.get("source_ref") and e.get("authority"))]
    g.add("LEDGER-ENTRIES-COMPLETE", not bad, "every entry has id/text/source_ref/authority",
          f"{len(bad)} incomplete", bad)
    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
