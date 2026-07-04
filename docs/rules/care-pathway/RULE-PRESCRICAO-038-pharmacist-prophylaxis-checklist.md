# RULE-PRESCRICAO-038 — Pharmacist prophylaxis checklist

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Free-text prophylaxis fields covering constipation/diarrhea, delirium, glycemic control, tube meds, VTE, stress-ulcer, analgesia and sedation.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| profilaxias.* | string |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| prophylaxis plan | object |  |

## Logic
```text
strings: profilaxia_constipacao_diarreia, profilaxia_delirium, profilaxia_controle_glicemico,
medicamento_sonda, profilaxia_tev(TEV/VTE), profilaxia_ulcera_estresse, analgesia, sedacao
```

## Edge cases (as implemented)
All optional free-text.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFarmaceutico.ts` | 415-461 | `f9656be2` | primary |

- Merged from: RULE-pharma-FE-01-059

## Notes
TEV = tromboembolismo venoso (VTE prophylaxis).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
