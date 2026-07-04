# RULE-EVOLUCOES-070 — Repeatable list maximum item cap

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
A list field lets the user add repeated sub-item groups; the "Add" button is only available while the item count is below campo.max (or unbounded if campo.max is undefined), and only when the form is editable.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| fields.length |  |  |  |
| campo.max |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| showAddButton |  |  |

## Logic
```text
showAddButton = (!disableAll && campo.max === undefined) ||
                (!disableAll && campo.max && fields.length < campo.max)
# cap: at most campo.max items; unlimited when campo.max undefined
```

## Edge cases (as implemented)
When disableAll and no items, renders "Nenhum item informado". Each item exposes a delete button only when !disableAll. Strict `<` means max is an exclusive upper bound on adds (i.e. list can hold exactly campo.max items).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormDadosProntuario/SubFormsDadosProntuario/SubFormList/SubFormList.tsx` | 42-104 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-04-024
- Related rules: RULE-EVOLUCOES-023

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
