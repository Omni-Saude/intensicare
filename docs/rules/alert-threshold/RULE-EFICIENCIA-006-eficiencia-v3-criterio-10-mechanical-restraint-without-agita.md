# RULE-EFICIENCIA-006 — Eficiencia v3 criterio_10 - mechanical restraint without agitation (AMARELO, wired)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | AMBIGUOUS |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | medium |
| Cluster | eficiencia |

## Rule
Mechanical restraint prescribed AND GCS>12 AND (per docstring) absence of RASS>+1 AND absence of delirium. Code requires delirium PRESENT (truthy) and RASS not > 1. Feeds the AMARELO alert.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| cpoe.contencao_mecanica | | | |
| evolucao.diurna_glasgow, evolucao.diurna_delirium, evolucao.rass | | | |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_10 | boolean | |

## Logic
```text
return all([
  handlers.get_number(getattr(ultima_evolucao, "diurna_glasgow")) > 12,
  handlers.get_number(getattr(ultima_cpoe, "contencao_mecanica")),
  handlers.get_number(getattr(ultima_evolucao, "diurna_delirium")),   # docstring: ABSENCE of delirium
  not int(getattr(ultima_evolucao, "rass")) > 1
      if getattr(ultima_evolucao, "rass", False) else False,
]) if (ultima_evolucao and ultima_cpoe) else False
```

## Edge cases (as implemented)
The delirium clause checks PRESENCE (truthy diurna_delirium) whereas the docstring/facade intent is "ausencia de delirium". RASS clause `not int(rass) > 1` -> True when rass <= 1; when rass is falsy the whole criterion is False.

## Divergence
Delirium clause checks presence of delirium, opposite of the documented "ausencia de delirium" intent (facade RULE-EFICIENCIA-012). GCS>12 and RASS<=1 gates match intent.

## Verification
- Verdict: DISCREPANCY (impact: moderate)
- Reference: Devlin JW, Skrobik Y, Gelinas C, et al. PADIS Guidelines (SCCM) for Prevention and Management of Pain, Agitation/sedation, Delirium, Immobility, and Sleep Disruption in Adult ICU Patients. Crit Care Med 2018;46(9):e825-e873 (minimize physical restraint; treat underlying delirium/agitation rather than restrain). Sessler CN, et al. Richmond Agitation-Sedation Scale (RASS), Am J Respir Crit Care Med 2002;166:1338-1344 (scale -5..+4; +1 = restless, >=+2 = agitated). (https://www.mdcalc.com/calc/1872/richmond-agitation-sedation-scale-rass)
- Test vectors: 2/4 match
- The GCS>12 and RASS<=+1 (not RASS>+1) gates correctly match the documented intent and RASS/PADIS framing of a non-agitated patient. The DISCREPANCY (carried as AMBIGUOUS from extraction, here characterized) is the delirium clause: `get_number(diurna_delirium)` requires delirium to be PRESENT (truthy), the exact opposite of the facade/docstring intent "ausencia de delirium". Consequently the wired AMARELO alert fires for delirious restrained patients (whose restraint is more likely justified) and stays silent for the calm, non-delirious restrained patients who are precisely the intended restraint-reassessment target - inverting the alert population. Additional edge: when rass is stored as 0/falsy the whole criterion short-circuits to False via the `if getattr(...,"rass",False) else False` guard. Advisory nudge -> moderate.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/models/trilhas_v3/trilha_eficiencia.py | 914-937 | 8166c07e | primary |
| ahlabs-trilhas | core/facade/trilha_eficiencia.py | 151-154 | 8166c07e | duplicate |
- Merged from: RULE-eficiencia-BE-03-090
- Related rules: RULE-EFICIENCIA-001, RULE-EFICIENCIA-012

## Notes
Wired (AMARELO via calcular_alerta_v2). AMBIGUOUS - presence-vs-absence of delirium ambiguity preserved as implemented.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
