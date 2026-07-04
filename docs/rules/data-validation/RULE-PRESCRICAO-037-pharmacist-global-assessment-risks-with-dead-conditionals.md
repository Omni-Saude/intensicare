# RULE-PRESCRICAO-037 — Pharmacist global assessment (risks with dead conditionals)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Pharmacist global assessment reuses the assistance-risk multicheck but all conditional reveals (allergy note, LPP list, other-lesion list) are commented out, so no fields open on selection.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| avaliacao_global.riscos_assistenciais | enum[] (multicheck) |  | see logic |
| presenca_de_delirium | boolean |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| global assessment | object |  |

## Logic
```text
idade(number, disabledOnEdit), peso(number), estado_geral {grave,regular}
riscos_assistenciais multicheck {queda,alergia,sangramento,trombose_venosa,delirium,broncoaspiracao,
  flebite,alteracao_glicemica,lpp,outras_lesoes}
conditions: {} // alergia/lpp/outras_lesoes blocks all commented out
presenca_de_delirium(boolean)
```

## Edge cases (as implemented)
Selecting alergia/lpp/outras_lesoes opens NO detail field (unlike nursing RULE-038).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFarmaceutico.ts` | 22-275 | `f9656be2` | primary |

- Merged from: RULE-pharma-FE-01-057

## Notes
DISCREPANCY = risk categories present but their required-detail logic is disabled vs the nurse form.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
