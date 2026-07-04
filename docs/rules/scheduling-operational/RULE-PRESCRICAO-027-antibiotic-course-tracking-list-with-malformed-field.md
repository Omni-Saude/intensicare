# RULE-PRESCRICAO-027 — Antibiotic course tracking list (with malformed field)

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
List of antibiotics in use with start/end dates, renal/hepatic dose-adjustment note and adjustment date, and positive-culture note; one row-field is malformed (uses key "Data" instead of "label").

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| antibiotico | string |  |  |
| data_inicio / data_fim / data_reajuste | date |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| antibiotic course record | object |  |

## Logic

```text
formList: antibiotico(string, disabledOnEdit), data_inicio(date, disabledOnEdit), data_fim(date, disabledOnEdit),
  reajuste_funcao_renal_hepatica(string), data_reajuste(date) [defined as { Data:"Data reajuste", nome:["data_reajuste"], type:"date" } — has no `label` key],
  cura_positiva(string, disabledOnEdit)
```

## Edge cases (as implemented)
The data_reajuste field object omits `label` and instead has a stray `Data` property (line 401) -> renders without a proper label.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFarmaceutico.ts` | 367-414 | `f9656be2` | primary |

**Merged from:**

- RULE-pharma-FE-01-058

## Notes
DISCREPANCY = malformed field descriptor (key `Data` vs `label`).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
