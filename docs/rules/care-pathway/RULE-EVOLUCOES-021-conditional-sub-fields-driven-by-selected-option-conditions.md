# RULE-EVOLUCOES-021 — Conditional sub-fields driven by selected option (conditions map)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
For select, boolean, checkbox and multicheck fields, choosing an option value renders the additional fields listed under campo.conditions[value]. This is the schema-driven "show-if / required-if" branching of the clinical form (e.g. select a symptom -> reveal follow-up questions).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| selectedValue |  |  |  |
| campo.conditions |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| extraFields |  |  |

## Logic
```text
select/boolean/checkbox:
  currentCondition = (campo.conditions && currentOption) ? campo.conditions[currentOption] : undefined
  render each conditional campo via SelectCampoType (name prefixed with listName when inside a list)
multicheck:
  currentConditions = checkedOptions.flatMap(o => campo.conditions[o] || [])
# Conditional child fields carry their own required/min/max rules (recursive).
```

## Edge cases (as implemented)
Boolean uses the true/false radio value as the conditions key. Initial condition state is seeded from form.getFieldValue(campo.nome). Nested list conditions prefix names with listName.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormDadosProntuario/SubFormsDadosProntuario/SubFormSelect/SubFormSelect.tsx` | 29-96 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-04-025
- Related rules: RULE-EVOLUCOES-073, RULE-EVOLUCOES-022

## Notes
Same pattern in SubFormBoolean.tsx (29-96), SubFormCheckbox.tsx (29-88), SubFormMultiCheck.tsx (36-119, flattened). SubFormCheckbox reads e.target.value as the conditions key (see notes/discrepancy in RULE-prontuario-FE-04-030).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
