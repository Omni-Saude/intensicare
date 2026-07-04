# RULE-INDICADORES-ETL-005 — Bed-occupancy percentage color thresholds

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
The circular occupancy-percentage indicator on a sector's dashboard card is colored red above 70%, amber between 50% and 70%, and green at or below 50%.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| item.ocupacao | number (percent) | % | 0-100 (presumed) |

## Outputs

| Name | Type | Unit |
|---|---|---|
| strokeColor | css color hex string |  |

## Logic
```text
strokeColor = item.ocupacao > 70   ? "#FF1633"   // red
            : item.ocupacao > 50   ? "#FFAB00"   // amber
            :                        "#00DC50"   // green
```

## Edge cases (as implemented)
Boundaries are strict '>' (not >=): exactly 70 and exactly 50 fall into the lower/green-ward tier, i.e. 70.0 is amber (not red) and 50.0 is green (not amber).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ListDashboard/DashboardCard/DashboardCard.tsx` | 291-300 | `f9656be2` | primary |

- Merged from: RULE-dashboard-FE-06-002
- Related rules: RULE-INDICADORES-ETL-001, RULE-INDICADORES-ETL-002, RULE-INDICADORES-ETL-006, RULE-INDICADORES-ETL-008, RULE-INDICADORES-ETL-009, RULE-INDICADORES-ETL-022

## Notes
Percent value itself (item.ocupacao) is computed server-side; this is purely the client display threshold.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
