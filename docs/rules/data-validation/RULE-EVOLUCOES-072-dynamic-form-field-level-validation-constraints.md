# RULE-EVOLUCOES-072 — Dynamic-form field-level validation constraints

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
The dynamic-form engine (used to render clinical evolution forms) supports declaring, per field (Campo), a "required" flag, numeric "min"/"max" bounds, and a "regex" pattern constraint, in addition to an input mask string.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| required |  |  |  |
| min / max |  |  |  |
| regex |  |  |  |
| mask |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| Campo |  |  |

## Logic
```text
Campo = {
  label: string, nome: string | string[], type: CampoType, options?: Option[],
  conditions?: Condition, required?: boolean, min?: number, max?: number,
  mask?: string, regex?: RegExp, showTime?: boolean, formList: Campo[],
  disabledOnEdit?: boolean
}
```

## Edge cases (as implemented)
min/max/regex/required are declared at the type level only in this partition; the actual per-instance constraint values live in the (out-of-scope) utils/dataForms/* form-definition files, and the validator that enforces them at submit time is also out of scope.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/DadosFormDinamico.d.ts` | 14-31 | `f9656be2` | primary |
- Merged from: RULE-formdinamico-FE-07-001
- Related rules: RULE-EVOLUCOES-066, RULE-EVOLUCOES-068, RULE-EVOLUCOES-069, RULE-EVOLUCOES-023

## Notes
This is the declarative "engine" capability; concrete field configurations (e.g. actual min/max values for a given clinical field) are defined in utils/dataForms/*, outside this partition's scope.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
