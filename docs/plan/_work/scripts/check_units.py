"""Gate: units registry + cross-check of every declared input unit.

- _work/units/registry.yaml must exist, parse, and contain the mission-mandated
  canonicals (lactate mmol/L; FiO2 fraction; vasopressor mcg/kg/min; temperature
  Celsius; creatinine mg/dL).
- Every input unit in _work/alerts/*.yaml and in each domain doc's
  ```yaml domain-inputs``` block must resolve to a registry canonical or alias.
Usage: check_units.py [--mode draft|strict]
"""
from __future__ import annotations

import re
import sys

import yaml

from _lib import ROOT, WORK, Gate, load_yaml

DOMAINS = ["sepsis", "aki", "respiratory", "hemodynamics", "neuro-sedation",
           "electrolyte", "pharmaco-interaction", "early-warning-scores",
           "correlation-engine"]
CANON_PINS = [
    ("lactate", r"lactat", {"mmol/l"}),
    ("fio2", r"fio2|fio₂", {"fraction", "1", "fraction 0-1", "fraction (0-1)", "fração 0-1"}),
    ("vasopressor", r"vasopressor|noradrenal|norepinephrine|adrenalin", {"mcg/kg/min", "µg/kg/min"}),
    ("temperature", r"temperatur", {"°c", "celsius", "c", "degc"}),
    ("creatinine", r"creatinin", {"mg/dl"}),
]


def norm_unit(u) -> str:
    return re.sub(r"\s+", " ", str(u or "")).strip().lower()


def domain_inputs_block(md_text: str):
    m = re.search(r"```yaml\s+domain-inputs\s*\n(.*?)```", md_text, re.S)
    if not m:
        return None
    return yaml.safe_load(m.group(1))


def main() -> int:
    mode = "strict" if "strict" in " ".join(sys.argv[1:]) else "draft"
    g = Gate("check_units")
    rp = WORK / "units/registry.yaml"
    if not rp.exists():
        g.add("UNITS-REGISTRY", False, "registry.yaml exists", "MISSING")
        return g.finish()
    reg = load_yaml(rp)
    params = reg.get("parameters") or []
    g.add("UNITS-REGISTRY", len(params) >= 15, ">=15 parameters", str(len(params)))

    allowed: set[str] = set()
    for p in params:
        allowed.add(norm_unit(p.get("canonical_unit")))
        for a in p.get("aliases") or []:
            allowed.add(norm_unit(a))
    allowed.discard("")

    for name, pat, units in CANON_PINS:
        hits = [p for p in params if re.search(pat, str(p.get("parameter", "")), re.I)]
        ok = any(norm_unit(h.get("canonical_unit")) in units for h in hits)
        g.add(f"UNITS-CANON-{name}", ok, f"canonical in {sorted(units)}",
              "; ".join(f"{h.get('parameter')}={h.get('canonical_unit')}" for h in hits) or "no entry")

    for d in DOMAINS:
        bad = []
        ap = WORK / f"alerts/{d}.yaml"
        if ap.exists():
            try:
                for a in (load_yaml(ap).get("alerts") or []):
                    for i in a.get("inputs") or []:
                        u = norm_unit(i.get("unit"))
                        if u not in allowed:
                            bad.append(f"{a.get('alert_id')}: {i.get('name')} unit '{i.get('unit')}'")
            except Exception as e:  # noqa: BLE001
                bad.append(f"alerts yaml parse: {e}")
        dp = ROOT / f"docs/plan/clinical/domains/{d}.md"
        if dp.exists():
            try:
                block = domain_inputs_block(dp.read_text(encoding="utf-8"))
                if block is None:
                    bad.append("domain doc missing ```yaml domain-inputs``` block")
                else:
                    for i in block.get("inputs") or []:
                        u = norm_unit(i.get("unit"))
                        if u not in allowed:
                            bad.append(f"domain-inputs: {i.get('name')} unit '{i.get('unit')}'")
            except Exception as e:  # noqa: BLE001
                bad.append(f"domain doc block parse: {e}")
        else:
            bad.append("domain doc missing")
        g.add(f"UNITS-{d}", not bad, "all input units resolve in registry",
              f"{len(bad)} unresolved", bad, warn=(mode == "draft" and bad and
                                                   all("missing" in b for b in bad)))
    return g.finish()


if __name__ == "__main__":
    sys.exit(main())
