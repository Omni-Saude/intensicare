# RULE-EVOLUCOES-065 — String field disable condition (nullifier lookup)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
SubFormString computes its disabled state with an expression that references nullStatus.nullifiers[grupoKey] and INVERTS isAnnulled, which diverges from the disableAll semantics used by every other subform and can throw when the nullifier is missing.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| disableAll |  |  |  |
| grupoKey |  |  |  |
| nullStatus.nullifiers[grupoKey].isAnnulled |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| disabled |  |  |

## Logic
```text
disabled = disableAll
           || (grupoKey && !nullStatus.nullifiers[grupoKey].isAnnulled)
           || false
# Note: grupoKey is only passed when anulavel (SelectCampoType passes grupoKey={anulavel ? grupoKey : undefined}).
# When grupoKey set: field is disabled when the group is NOT annulled (isAnnulled false) -> inverse of
# every other field, which disables when the group IS annulled (nullCampo).
```

## Edge cases (as implemented)
If grupoKey is set but nullStatus.nullifiers[grupoKey] is undefined, `.isAnnulled` throws a TypeError. The inverted logic means an editable (non-annulled) annullable group would disable its string fields, contradicting SubFormNumber/Interval/etc. which use nullCampo (disable when annulled).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FormDadosProntuario/SubFormsDadosProntuario/SubFormString/SubFormString.tsx` | 44-54 | `f9656be2` | primary |
- Merged from: RULE-prontuario-FE-04-038
- Related rules: RULE-EVOLUCOES-064, RULE-EVOLUCOES-074

## Notes
Recorded verbatim, not corrected. Contrast RULE-prontuario-FE-04-018 (disableAll includes nullCampo = isAnnulled). This field's disable is `!isAnnulled` for annullable groups, the opposite direction, and lacks a null guard on the nullifier object.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
