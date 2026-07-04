# RULE-MOVIMENTACAO-ADT-015 — Overdue-protocol-item indicator on trilha chip

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
A trilha chip on a bed card shows a clock-alert icon with the tooltip "Ha itens do protocolo em atraso." whenever the trilha's has_item_em_atraso flag is true, signalling overdue protocol items to the care team.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| trilha.has_item_em_atraso | boolean |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| showOverdueIcon | boolean |  |

## Logic
```text
showOverdueIcon = !!trilha.has_item_em_atraso
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx | 570-578 | f9656be2 | primary |
- Merged from: RULE-leito-FE-06-030
- Related rules: RULE-MOVIMENTACAO-ADT-017

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
