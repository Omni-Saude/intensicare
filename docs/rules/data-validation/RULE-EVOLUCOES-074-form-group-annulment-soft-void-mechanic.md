# RULE-EVOLUCOES-074 — Form-group annulment (soft-void) mechanic

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | low |
| Cluster | evolucoes |

## Rule
A dynamic-form group can be marked "anulavel" (annullable); combined with the Utils.NullStatus "nullifiers" map (keyed per field, each carrying a data-shape type of "object"|"array" and an "isAnnulled" boolean), this implies clinical-record groups can be marked as void/annulled rather than physically deleted, presumably to preserve an audit trail for medical-legal recordkeeping.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| anulavel |  |  |  |
| nullifiers[key].isAnnulled |  |  |  |
| nullifiers[key].type [object \| array] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| annulment state per form-group key |  |  |

## Logic
```text
DadosFormDinamico.anulavel?: boolean   // marks a form group/subgroup as eligible for annulment
Utils.NullStatus.nullifiers = { [key: string]: { type: "object" | "array", isAnnulled: boolean } }
// presumed: when a group's data is annulled, isAnnulled=true is set for its key rather than
// deleting the underlying record, and "type" records whether the annulled value was an
// object or an array (for correct re-hydration/display).
```

## Edge cases (as implemented)
No code in this partition actually sets isAnnulled or reads anulavel to drive UI behavior — this is a shape-only inference.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/DadosFormDinamico.d.ts` | 1-11 | `f9656be2` | primary |
- Merged from: RULE-formdinamico-FE-07-004
- Related rules: RULE-EVOLUCOES-049, RULE-EVOLUCOES-064, RULE-EVOLUCOES-065

## Notes
Cross-reference Utils.NullStatus at src/@types/models/Utils.d.ts lines 100-107.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
