# RULE-MOVIMENTACAO-ADT-016 — Invasive-procedures alert indicator

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
A bed card shows an amber alert-box icon (with a popover listing each procedure) whenever the occupation has one or more recorded invasive procedures.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| ocupacao.procedimentos_invasivos | array |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| showInvasiveIcon | boolean |  |

## Logic
```text
showInvasiveIcon = ocupacao.procedimentos_invasivos?.length > 0
```

## Edge cases (as implemented)
Uses optional chaining; if procedimentos_invasivos is undefined, the comparison is undefined > 0 which is false, so the icon is safely hidden rather than throwing.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx | 423-454 | f9656be2 | primary |
- Merged from: RULE-leito-FE-06-031
- Related rules: RULE-MOVIMENTACAO-ADT-005, RULE-MOVIMENTACAO-ADT-053

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
