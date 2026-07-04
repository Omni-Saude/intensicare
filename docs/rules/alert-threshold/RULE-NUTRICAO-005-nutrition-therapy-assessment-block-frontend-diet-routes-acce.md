# RULE-NUTRICAO-005 — Nutrition-therapy assessment block (frontend) - diet routes, acceptance, ranges and prophylaxis enum

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | DISCREPANCY (impact: low) |
| Confidence | high |
| Cluster | nutricao |

## Rule
Frontend "Terapia Nutricional" form group with diet-route booleans, acceptance enum, vomit/gastric-residue/HGT numeric ranges, and the stress-ulcer/nutrition prophylaxis indication enum. Declared identically in the nursing form (dataFormEnfermagem) and the dietitian form (dataFormNutricionista).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dieta_zero / dieta_via_oral / enteral_sne_gtt / nutricao_parenteral | boolean |  |  |
| aceitacao | enum |  | total | parcial | recusado |
| vomitos | number | ml | 0-10000 |
| residuo_gastrico | number | ml | 0-10000 |
| hgt_max | number | mg/dL | 0-1000 |
| hgt_min | number | mg/dL | 0-1000 |
| indicacao_profilaxia | enum |  | see logic |

## Outputs
| Name | Type | Unit |
|---|---|---|
| nutrition assessment | object |  |

## Logic
```text
booleans: dieta_zero, dieta_via_oral, enteral_sne_gtt (label "Enteral (SNN/GTT)"), nutricao_parenteral
aceitacao (select): total | parcial | recusado
vomitos: number 0-10000 (ml)
residuo_gastrico: number 0-10000 (ml)
hgt_max: number 0-1000 (mg/dL)
hgt_min: number 0-1000 (mg/dL)
indicacao_profilaxia (select):
  dva | tce | avc | queimado | jejum_prolongado | nao_indicado | terapeutico | vm_mais_72h (VM > 72h)
```

## Edge cases (as implemented)
HGT max/min not cross-validated (max>=min not enforced). Ranges are UI input caps, not clinical decision thresholds. All fields optional.

## Verification
- Verdict: DISCREPANCY (impact: low)
- Reference: ASHP Therapeutic Guidelines on Stress Ulcer Prophylaxis (1999) - classic SUP indication is mechanical ventilation >48h or coagulopathy; SCCM/ASHP 2024 update de-emphasizes MV-alone. UI numeric ranges have no clinical-threshold anchor.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormEnfermagem.ts | 554-633 | f9656be2 | primary |
| trilhas-frontend | src/utils/dataForms/dataFormNutricionista.ts | 31-110 | f9656be2 | duplicate |

- Merged from: RULE-nutrition-FE-01-045, RULE-nutrition-FE-01-048
- Related rules: RULE-NUTRICAO-003, RULE-NUTRICAO-006

## Notes
MERGED RULE-nutrition-FE-01-045 (nursing) + RULE-nutrition-FE-01-048 (dietitian). Compared both source blocks line-by-line: byte-identical field set, bounds, option lists and enum -> status OK, no divergence. The aceitacao {total,parcial,recusado} and indicacao_profilaxia (8 values) enums are exact copies of backend TerapiaNutricionalChoices (terapia_nutricional.py) -> no backend/frontend divergence (see RULE-NUTRICAO-006). verify:true because the block carries the stress-ulcer prophylaxis eligibility enum (VM>72h) which has a published clinical anchor.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
