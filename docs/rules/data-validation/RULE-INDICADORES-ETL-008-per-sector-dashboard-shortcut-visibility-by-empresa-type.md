# RULE-INDICADORES-ETL-008 — Per-sector dashboard shortcut visibility by empresa type

| Field | Value |
|---|---|
| Category | data-validation |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | indicadores-etl |

## Rule
An info button that deep-links to a sector-specific dashboard page is shown on a sector's dashboard card only when the parent company (empresa) is configured with tipo "automatica" and the card is being rendered in sector (isSetor) context.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| empresaData.tipo | string |  | observed value: 'automatica' (others unspecified) |
| isSetor | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| showInfoButton | boolean |  |

## Logic
```text
showInfoButton = (empresaData.tipo === "automatica") && isSetor
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ListDashboard/DashboardCard/DashboardCard.tsx` | 224-249 | `f9656be2` | primary |

- Merged from: RULE-dashboard-FE-06-006
- Related rules: RULE-INDICADORES-ETL-005, RULE-INDICADORES-ETL-001, RULE-INDICADORES-ETL-002, RULE-INDICADORES-ETL-006, RULE-INDICADORES-ETL-009, RULE-INDICADORES-ETL-022

## Notes
The full enum of empresa.tipo values is not visible in this partition; only the "automatica" branch condition is confirmed from this file.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
