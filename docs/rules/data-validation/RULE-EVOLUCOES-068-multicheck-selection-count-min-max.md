# RULE-EVOLUCOES-068 — Multicheck selection-count min/max

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
A multicheck field validates the number of selected options as an array within [campo.min, campo.max]; required when campo.required. Checked options can trigger conditional sub-fields (flattened across all checked values).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| selected [length in [campo.min, campo.max]] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid |  |  |

## Logic
```text
rules = [
  { type:"array", max: campo.max, min: campo.min, message: `Selecione ate ${campo.max} opcoes.` },
  ...(campo.required ? requiredRule : [])
]
currentConditions = checkedOptions.map(o => campo.conditions?.[o] || []).flat()
```

## Edge cases (as implemented)
Message only mentions max; array min still enforced. Layout is 2 columns desktop, 1 collapsed.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormDadosProntuario/SubFormsDadosProntuario/SubFormMultiCheck/SubFormMultiCheck.tsx` | 36-96 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-04-022
- Related rules: RULE-EVOLUCOES-072, RULE-EVOLUCOES-023

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
