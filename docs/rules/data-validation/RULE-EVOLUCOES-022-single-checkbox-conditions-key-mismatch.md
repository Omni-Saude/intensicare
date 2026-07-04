# RULE-EVOLUCOES-022 — Single-checkbox conditions key mismatch

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
SubFormCheckbox drives its conditional sub-fields from e.target.value on change, but an antd Checkbox onChange event carries e.target.checked (boolean), not a value. The conditions lookup key is therefore likely always undefined/incorrect.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| checkbox change event |  |  |  |
| campo.conditions |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| currentCondition |  |  |

## Logic
```text
onChange(e): setCurrentOptionCondition(e.target.value as string)   # antd checkbox: value is the prop, checked is state
currentCondition = (campo.conditions && currentOption) ? campo.conditions[currentOption] : undefined
```

## Edge cases (as implemented)
e.target.value is the Checkbox's `value` prop (undefined here since none is set), so currentOptionCondition is likely undefined and conditional fields never render. Best interpretation: intended to key conditions off checked state (true/false) as SubFormBoolean does.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormDadosProntuario/SubFormsDadosProntuario/SubFormCheckbox/SubFormCheckbox.tsx` | 55-88 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-04-039
- Related rules: RULE-EVOLUCOES-021

## Notes
Recorded verbatim. Compare SubFormBoolean (RULE-prontuario-FE-04-025) which correctly uses e.target.value from a Radio.Group. Marked AMBIGUOUS because intended conditions key is unclear.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
