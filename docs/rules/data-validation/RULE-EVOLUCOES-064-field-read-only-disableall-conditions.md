# RULE-EVOLUCOES-064 — Field read-only (disableAll) conditions

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Every dynamic prontuario field is disabled (read-only) when the form is in view mode (in_page), or the field is flagged disabledOnEdit, or its group is currently annulled.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| campo.disabledOnEdit |  |  |  |
| mode |  |  |  |
| nullCampo (group annulled) |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| disableAll |  |  |

## Logic
```text
disableAll = campo.disabledOnEdit || (mode === "in_page") || nullCampo
nullCampo = (anulavel && grupoKey && nullStatus.nullifiers[grupoKey]) ? nullStatus.nullifiers[grupoKey].isAnnulled : false
```

## Edge cases (as implemented)
mode defaults to in_page (view). Conditional sub-fields inherit mode = disableAll ? in_page : modal.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormDadosProntuario/SubFormsDadosProntuario/SelectCampoType/SelectCampoType.tsx` | 44-170 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-04-018
- Related rules: RULE-EVOLUCOES-065, RULE-EVOLUCOES-074

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
