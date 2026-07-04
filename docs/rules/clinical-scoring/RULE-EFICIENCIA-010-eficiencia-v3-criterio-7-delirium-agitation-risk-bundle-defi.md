# RULE-EFICIENCIA-010 — Eficiencia v3 criterio_7 - delirium/agitation risk bundle (defined, unwired, crashes)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: none |
| Confidence | high |
| Cluster | eficiencia |

## Rule
OR of many delirium risk factors (SOFA>=5, age>75, dementia/AVC antecedent, antibiotic, bicarbonate<22, no evacuation in 48h, Na>150 or Na<130, mechanical restraint, GCS 13-14, RASS +1..+4, high pain scores).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| evolucao.idade, diurna_sofa, diurna_bicabornato, diurna_sodio, diurna_glasgow, rass, contencao | | | |
| cpoe.antibiotico, cpoe.contencao_mecanica | | | |
| balanco pain fields | | | VISUAL / COMPORTAMENTAL |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_7 | boolean | |

## Logic
```text
return any([
  get_number(diurna_sofa) >= 5,
  get_number(idade) > 75,
  antecedente in ["Demencia, AVC"],                 # via fromkeys -> inert
  get_number(cpoe.antibiotico),
  get_number(diurna_bicabornato) < 22,
  not evolucao_48h.filter(enf_eliminacoes_intestinais__isnull=False),
  get_number(diurna_sodio) > 150,
  get_number(diurna_sodio) < 130,
  get_number(cpoe.contencao_mecanica),
  get_number(diurna_glasgow) in [13, 14],
  int(rass) in range[1, 5] if rass else False,      # range[1,5] -> TypeError (range not subscriptable)
  all([ <mutually exclusive VISUAL and COMPORTAMENTAL pain equalities> ]),
]) if (ultima_evolucao and ultima_cpoe and ultimo_balanco and balanco_anterior) else False
```

## Edge cases (as implemented)
`int(rass) in range[1, 5]` raises TypeError when rass is truthy (a range object is not subscriptable) - the RASS branch crashes rather than testing +1..+4. The pain sub-block uses all([...]) over mutually exclusive VISUAL / COMPORTAMENTAL equalities, so it is always False. Antecedent check inert (fromkeys). Na>150 and Na<130 are separate OR terms. Unwired (would raise if wired and rass present).

## Divergence
`int(rass) in range[1, 5]` is a runtime bug (subscripting a range) instead of a membership test against range(1,5); the pain all([]) block is unsatisfiable; the antecedent membership is inert.

## Verification
- Verdict: DISCREPANCY (impact: none)
- Reference: Qualitatively maps to established ICU delirium risk factors. PRE-DELIRIC model (van den Boogaard et al., BMJ 2012;344:e420) predicts delirium from age, APACHE-II, coma, admission category, infection, metabolic acidosis, morphine/sedatives, urea, urgent admission. The rule's bicarbonate<22 (metabolic acidosis), antibiotic (infection), age>75, sedation/coma and agitation (RASS +1..+4) terms align with these validated predictors, but the rule is an ad-hoc OR-bundle, not the PRE-DELIRIC logistic equation. (https://www.bmj.com/content/344/bmj.e420)
- Test vectors: 1/3 match (1 ambiguous)
- Individual risk factors are clinically reasonable and consistent with PRE-DELIRIC, but implementation has hard bugs: (1) `int(rass) in range[1, 5]` subscripts a range object -> TypeError whenever rass is truthy (the intended membership test is `in range(1,5)` i.e. RASS +1..+4); the entire any([...]) list is built eagerly so a truthy RASS crashes the method. (2) the pain sub-block uses all([...]) over mutually exclusive VISUAL and COMPORTAMENTAL equalities on the same record -> unsatisfiable (always False). (3) antecedent 'Demencia, AVC' membership inert (fromkeys None values). Vector 3 match is ambiguous because the `not evolucao_48h.filter(...)` (absence-of-evacuation) term can independently fire. Unwired (calcular_criterio_7 commented out) so no production impact; would crash if wired and a RASS value is present.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/models/trilhas_v3/trilha_eficiencia.py | 742-828 | 8166c07e | primary |
| ahlabs-trilhas | core/facade/trilha_eficiencia.py | 139-142 | 8166c07e | duplicate |
- Merged from: RULE-eficiencia-BE-03-087
- Related rules: RULE-EFICIENCIA-012

## Notes
Unwired (calcular_criterio_7 commented out in calcular_criterios).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
