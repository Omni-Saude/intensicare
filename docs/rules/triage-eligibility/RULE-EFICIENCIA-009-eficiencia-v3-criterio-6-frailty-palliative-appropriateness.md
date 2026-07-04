# RULE-EFICIENCIA-009 — Eficiencia v3 criterio_6 - frailty / palliative-appropriateness (defined, unwired)

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | decision-tree |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | eficiencia |

## Rule
Three OR-combined frailty patterns using age, length of stay (LOS), SAPS3, SOFA, antecedents, gastrostomy, dialysis, ventilation and noradrenaline to flag patients for whom palliative care should be considered.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| evolucao.idade, dt_entrada, admissao_saps3, diurna_sofa, ant_pessoal_1..5, enf_gastrostomia, diurna_ventilacao | | | |
| cpoe.hemodialise | | | |
| balanco.qt_vol_nora | | | |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_6 | boolean | |

## Logic
```text
return any([
  all([ idade >= 80, any([ LOS >= 7,  SAPS3 > 50, SOFA >= 3 ]) ]),
  all([ idade > 70,  any([ LOS > 15,  SAPS3 > 70, SOFA >= 5 ]) ]),
  all([ any([
          idade > 70,
          antecedente in {"Acamado previamente", "Demencia de Alzheimer",
                          "Demencia senil", "Cancer"},   # via fromkeys -> inert
          gastrostomia,
          cpoe.hemodialise,
          ventilacao in <mecanica>,
          qt_vol_nora > 20,
          SOFA >= 5,
       ]) ]),
]) if (ultima_evolucao and ultima_cpoe) else False
# LOS = handlers.diferenca_dias(dt_entrada)
```

## Edge cases (as implemented)
The antecedent membership uses vars().fromkeys().values() (all None), so the antecedent-list check is non-functional; however the third OR branch still fires via age/gastrostomy/dialysis/ventilation/noradrenaline>20/SOFA>=5. Age tiers 80/70, SAPS3 50/70, SOFA 3/5, LOS 7/15 captured verbatim. Unwired.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published guideline defines a palliative/frailty-appropriateness trigger with these exact composite cutoffs (age 80/70, LOS 7/15 d, SAPS3 50/70, SOFA 3/5). Component severity scores are validated (SAPS 3: Moreno et al., Intensive Care Med 2005; SOFA: Vincent et al., Intensive Care Med 1996) but the trigger thresholds and OR-combination are an internal institutional triage rule. (https://link.springer.com/article/10.1007/s00134-005-2763-5)
- Test vectors: 3/3 match
- Thresholds are clinically plausible and internally consistent but not traceable to a single authoritative source -> internal business rule, flagged for internal clinical review (do NOT treat as wrong). Extraction status OK. The antecedent-list membership check is inert (vars().fromkeys().values() are all None) so 'Acamado/Cancer/Demencia' never contribute, but the third OR branch still fires via age>70 / gastrostomy / dialysis / mechanical ventilation / noradrenaline>20 ml/h / SOFA>=5. Unwired.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/models/trilhas_v3/trilha_eficiencia.py | 619-740 | 8166c07e | primary |
| ahlabs-trilhas | core/facade/trilha_eficiencia.py | 135-138 | 8166c07e | duplicate |
- Merged from: RULE-eficiencia-BE-03-086
- Related rules: RULE-EFICIENCIA-012

## Notes
Status OK (thresholds sound); antecedent-list sub-check is inert but does not block the other predicates. Unwired.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
