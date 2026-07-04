# RULE-INDICADORES-ETL-009 — Unread-message badge display and cap

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
A sector's dashboard card shows an unread-message count badge only when the count is greater than zero, and displays "+99" instead of the exact number once it exceeds 99.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| item.qtd_mensagens | integer | count | >=0 |

## Outputs

| Name | Type | Unit |
|---|---|---|
| badgeVisible | boolean |  |
| badgeText | string |  |

## Logic
```text
badgeVisible = item.qtd_mensagens > 0
badgeText = item.qtd_mensagens > 99 ? "+99" : String(item.qtd_mensagens)
```

## Edge cases (as implemented)
Boundary exactly 99 shows literal '99', not '+99'; 100+ shows '+99'.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ListDashboard/DashboardCard/DashboardCard.tsx` | 250-259 | `f9656be2` | primary |

- Merged from: RULE-dashboard-FE-06-007
- Related rules: RULE-INDICADORES-ETL-005, RULE-INDICADORES-ETL-001, RULE-INDICADORES-ETL-002, RULE-INDICADORES-ETL-006, RULE-INDICADORES-ETL-008, RULE-INDICADORES-ETL-022

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
