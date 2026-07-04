# RULE-EVOLUCOES-050 — Checkable (checavel) subgroup toggle and null-on-disable

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
A subgroup flagged checavel shows a Switch; it starts ON only if the subgroup already has any non-null value. Its child fields are visible only while ON. Turning it OFF sets the whole subgroup value to null.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| form value at [grupoKey][subGrupoKey] |  |  |  |
| checavel |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| subgroupVisible / subgroupValue |  |  |

## Logic
```text
initialChecked = value && value[subGrupoKey] && !verifyNullKeys(value[subGrupoKey])   # has any non-null field
Switch disabled when mode === "in_page".
onChange(value):
  setChecked(value)
  if (!value): form.setFieldsValue({ [grupoKey]: { [subGrupoKey]: null } })
Child fields display: (!checavel || (checavel && checked===true)) ? "block" : "none"
verifyNullKeys(obj) = Object.values(obj).every(v => v === null)
```

## Edge cases (as implemented)
A subgroup whose values are all null renders unchecked. Non-checavel subgroups always show their fields. Setting null does not deep-clear nested arrays, only the subgroup key.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormDadosProntuario/SubGroupHandle/SubGroupHandle.tsx` | 32-91 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-04-026
- Related rules: none

## Notes
verifyNullKeys defined in src/utils/verifyNullKeys.ts (cross-partition).

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
