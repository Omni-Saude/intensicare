# RULE-EFICIENCIA-005 — Eficiencia v3 criterio_9 - coma without sedation (defined, unwired)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | high |
| Cluster | eficiencia |

## Rule
Intended - GCS<6 AND absence of any sedative (cetamina/dexmedetomidina/ propofol/tiopental/midazolam via balanco, fenitoina/fenobarbital via adep) in the last 6h -> suspected brain death, initiate donor-potential maintenance. Facade criterio_9 = "Suspeita de ME". Code uses GCS<13 and an AND-combined sedative filter.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| evolucao.diurna_glasgow | GCS | | |
| balanco.qt_vol_cet/dex/pro/tiop/mid | | ml/h | last 6h |
| adep.fenitoina/fenobarbital | | | last 6h |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_9 | boolean | |

## Logic
```text
return all([
  handlers.get_number(getattr(evolucao, "diurna_glasgow")) < 13,   # docstring/intent: < 6
  not (
    balanco_6h.filter(qt_vol_cet__gt=0, qt_vol_dex__gt=0, qt_vol_pro__gt=0,
                      qt_vol_tiop__gt=0, qt_vol_mid__gt=0).exists()
    or adep_6h.filter(fenitoina__gt=0, fenobarbital__gt=0).exists()
  ),
]) if (ultima_evolucao and adep_6h and balanco_6h) else False
```

## Edge cases (as implemented)
GCS threshold is 13 in code, not 6 as documented. The sedative-absence clause uses a single .filter() with comma-separated (AND) conditions, so it only matches a balance record where ALL five infusion sedatives are simultaneously >0 (and, separately, both adep drugs >0) - effectively never, making the "absence" clause almost always True. Unwired.

## Divergence
GCS<13 implemented vs GCS<6 intended; sedative-absence uses an AND-combined filter (requires all sedatives present at once) rather than the intended OR/any across sedatives, so it almost never excludes.

## Verification
- Verdict: DISCREPANCY (impact: moderate)
- Reference: Clinical triggers for organ-donation referral - ventilated patient with severe neurological injury and GCS <=5 (or GCS <=4 not explained by sedation) prompts referral to the organ procurement organization / brain-death evaluation. NICE CG135 Organ donation for transplantation (clinical trigger: GCS <=4 not explained by sedation, or intention to test brainstem death). GCS: Teasdale & Jennett, Lancet 1974;2:81-84 (range 3-15). (https://www.ncbi.nlm.nih.gov/books/NBK550813/)
- Test vectors: 2/4 match
- Intended docstring GCS<6 (GCS<=5) matches the published OPO/NICE clinical-trigger literature. Code diverges on two dimensions: (1) threshold is GCS<13, far broader than GCS<=5, so it would label many merely obtunded patients as brain-death suspects; (2) the sedative-absence clause uses a single .filter() with comma-separated (logical AND) conditions, so it only detects sedation when ALL FIVE infusion sedatives (and, in the adep arm, BOTH fenitoina and fenobarbital) are simultaneously >0 - so a patient on a single agent (e.g. propofol alone) is wrongly treated as unsedated. Intent was OR/any sedative. Directionally dangerous (initiating donor-potential maintenance on a merely sedated/obtunded patient), but the rule is UNWIRED (calcular_criterio_9 commented out), so no live production impact -> moderate (would be high if enabled).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/models/trilhas_v3/trilha_eficiencia.py | 878-912 | 8166c07e | primary |
| ahlabs-trilhas | core/facade/trilha_eficiencia.py | 147-150 | 8166c07e | duplicate |
- Merged from: RULE-eficiencia-BE-03-089
- Related rules: RULE-EFICIENCIA-012

## Notes
Unwired (calcular_criterio_9 commented out in calcular_criterios).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
