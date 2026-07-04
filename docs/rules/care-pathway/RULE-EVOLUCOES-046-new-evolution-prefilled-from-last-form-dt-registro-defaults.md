# RULE-EVOLUCOES-046 — New evolution prefilled from last form; dt_registro defaults to now

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
When opening the "Adicionar" tab, the new evolution form is prefilled from the patient's last saved form (getLastForm), with the registration datetime reset to the current moment and horario_saida defaulted to "" when absent.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| lastForm data |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| initialValues |  |  |

## Logic
```text
initialValues = { ...data, dt_registro: moment(), horario_saida: data.horario_saida || "" }
adaptedData = adaptValues ? adaptValues(initialValues) : initialValues
# Default active tab: canAdd ? "adicionar" : "historico".
```

## Edge cases (as implemented)
form.resetFields() called after loading. On submit dt_registro is formatted "YYYY-MM-DD HH:mm" (only if present) and clearIds strips inherited ids (RULE-prontuario-FE-04-028).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/EvolucaoDefault/EvolucaoDefault.tsx` | 83-92 | `f9656be2` | primary |
- Merged from: RULE-evolucao-FE-04-036
- Related rules: RULE-EVOLUCOES-063, RULE-EVOLUCOES-059

## Notes
dt_registro submit format at lines 145-150; default tab at lines 62-72.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
