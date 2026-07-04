# RULE-EVOLUCOES-059 — Registration datetime immutable when editing a past evolution

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
When editing a past evolution, the dt_registro field is force-disabled (disabledOnEdit=true) so the original registration datetime cannot be changed; it is still reformatted on submit.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dataForm campos |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| editedDataForm (dt_registro disabledOnEdit=true) |  |  |

## Logic
```text
disableField(["dt_registro"]): for each group, for each campo:
  if (campo.nome.toString() === "dt_registro".toString()) -> { ...campo, disabledOnEdit:true }
On submit: values.dt_registro = values.dt_registro.format("YYYY-MM-DD HH:mm")
```

## Edge cases (as implemented)
Comparison uses .toString() so array-named fields compare by joined string. On submit, dt_registro.format is called unconditionally (assumes a moment present).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/EvolucaoDefaultPassada/EvolucaoDefaultPassada.tsx` | 93-124 | `f9656be2` | primary |
- Merged from: RULE-evolucao-FE-04-037
- Related rules: RULE-EVOLUCOES-046

## Notes
dt_registro initialized from moment(data.dt_registro) at line 66.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
