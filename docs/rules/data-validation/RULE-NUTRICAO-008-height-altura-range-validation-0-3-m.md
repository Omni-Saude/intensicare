# RULE-NUTRICAO-008 — Height (altura) range validation 0-3 m

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | nutricao |

## Rule
Nutrition altura field is constrained to the numeric range [0, 3] meters.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| altura | number | m | 0-3 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid | boolean |  |

## Logic
```text
rules = [{ max: 3, min: 0, type: "number" }]
```

## Edge cases (as implemented)
No required rule (optional field). peso and imc have no range validation; imc is disabled.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/FieldsetAvGlobalNutricionista/FieldsetAvGlobalNutricionista.tsx | 43-47 | f9656be2 | primary |

- Merged from: RULE-nutricao-FE-04-030
- Related rules: RULE-NUTRICAO-001

## Notes
Verified against source lines 43-47. Feeds RULE-NUTRICAO-001 (BMI) altura input.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
