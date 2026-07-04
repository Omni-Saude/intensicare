# RULE-EVOLUCOES-020 — Evolução drawer OK-button gating

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
The Save/OK button on the evolução-type drawer is hidden whenever a component type is selected and that type does not both allow adding (canAdd) and represent the "add" variant (isAddKey); i.e., only evolução types flagged canAdd && isAddKey expose the generic save-and-release workflow via this drawer's OK button.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| currentEvolucaoComponent.component |  |  |  |
| evolucaoComponents[component].canAdd |  |  |  |
| evolucaoComponents[component].isAddKey |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| hideOk |  |  |

## Logic
```text
hideOk = currentEvolucaoComponent.component &&
         (!evolucaoComponents[component].canAdd || !evolucaoComponents[component].isAddKey)
```

## Edge cases (as implemented)
If no component is currently selected, `hideOk` evaluates to a falsy value (undefined), so the OK button is shown by default before any evolução type has been chosen.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx` | 195-199 | `f9656be2` | primary |
- Merged from: RULE-evolucao-FE-06-012
- Related rules: RULE-EVOLUCOES-045

## Notes
canAdd/isAddKey are defined in the out-of-partition hooks/useEvolucaoMenu hook; only the gating expression itself is in scope here.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
