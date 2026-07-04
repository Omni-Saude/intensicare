# RULE-EVOLUCOES-049 — Annullable (anulavel) group nullification on submit

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Groups flagged anulavel expose a toggle (default ON = applicable). Turning it OFF marks the group isAnnulled; on submit, annulled group values are replaced by an empty object {} or empty array [] according to the nullifier type, effectively clearing that group.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| nullStatus.nullifiers[grupoKey].isAnnulled |  |  |  |
| nullStatus.nullifiers[grupoKey].type |  |  |  |
| form values |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| submittedValues |  |  |

## Logic
```text
Toggle (CollapsedFields): Switch defaultChecked; onChange(value) -> set nullifiers[grupoKey].isAnnulled = !value
On submit (nullifyFields, recursive):
  for each key in values:
    if (!isEmpty(object) && nullifiers[key]?.isAnnulled):
      if (nullifiers[key].type === "object") value[key] = {}
      if (nullifiers[key].type === "array")  value[key] = []
    else if (typeof value[key] === "object"): recurse into value[key]
# nullifyFields only applied when rawNullStatus prop was provided.
```

## Edge cases (as implemented)
isEmpty treats an object as empty if every own value is undefined or null. Nullification only runs if a nullStatus was passed in; otherwise raw values submit unchanged. Recursion re-assigns valuesToSub via spread on each nested object key.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormDadosProntuario/FormDadosProntuario.tsx` | 36-64 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-04-017
- Related rules: RULE-EVOLUCOES-074, RULE-EVOLUCOES-064, RULE-EVOLUCOES-065

## Notes
Toggle wiring in CollapsedFields.tsx lines 57-83 (only rendered when mode !== "in_page" && anulavel). Helpers isEmpty (src/utils/isEmpty.ts) and verifyNullKeys used across the form.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
