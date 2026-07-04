# RULE-EVOLUCOES-073 — Dynamic-form conditional field visibility

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
A dynamic-form field's "conditions" map allows additional Campo[] to be shown only when the field's own value equals one of the map's keys — implementing conditional/dependent field visibility within the form engine used for clinical evolution forms.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| conditions |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| additional visible Campo[] |  |  |

## Logic
```text
Condition = { [key: string]: Campo[] }
// when the governing field's value === key, render the associated Campo[] additionally
```

## Edge cases (as implemented)
The actual value-matching/rendering logic that consumes this "conditions" map is implemented in the (out-of-scope) form-rendering component, not in this partition's type-only file.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/DadosFormDinamico.d.ts` | 22-37 | `f9656be2` | primary |
- Merged from: RULE-formdinamico-FE-07-002
- Related rules: RULE-EVOLUCOES-021

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
