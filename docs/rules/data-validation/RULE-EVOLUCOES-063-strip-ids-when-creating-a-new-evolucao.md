# RULE-EVOLUCOES-063 — Strip ids when creating a new evolucao

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
When submitting a NEW evolution, every nested object has its `id` key set to undefined (clearIds) before POST, so a new record does not inherit ids copied from the prefilled "last form".

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| values |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| cleanedValues |  |  |

## Logic
```text
onFinish(clearIds(values))
clearIds(values): for each [key,value] in values -> newObj[key] = removeIds(value)
removeIds(obj): if obj is a non-array object -> copy keys, set key "id" to undefined; else return obj as-is
```

## Edge cases (as implemented)
Only one level deep: removeIds strips "id" on each direct child object; arrays are returned unchanged (their element ids are NOT stripped). Non-object children pass through.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/EvolucaoDefault/EvolucaoDefault.tsx` | 229-240 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-04-028
- Related rules: RULE-EVOLUCOES-046

## Notes
clearIds defined in src/utils/clearIds.ts (cross-partition); shallow id-stripping may be intentional or a limitation.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
