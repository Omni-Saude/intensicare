# RULE-INDICADORES-ETL-001 — Sector alert-share percentage formula

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
Computes what percentage of a sector's total alert count (across NEUTRO+AMARELO+VERMELHO) a given alert-color bucket represents, used to size each segment of the sector's alert progress bars.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| alert | number | count | >=0 |
| item.total_alertas.NEUTRO | number | count |  |
| item.total_alertas.AMARELO | number | count |  |
| item.total_alertas.VERMELHO | number | count |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| alertPercent | number | % |

## Logic
```text
total = NEUTRO + AMARELO + VERMELHO
alertPercent(alert) = total !== 0 ? (alert * 100) / total : 0
```

## Edge cases (as implemented)
Division-by-zero guarded explicitly; returns 0 when total is 0.

## Verification
- Verdict: UNVERIFIABLE (clinical impact: n/a)
- Reference: No authoritative clinical/published reference. Proprietary UI display rule (percent-of-total = part/whole*100, the universal arithmetic definition of a percentage).

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ListDashboard/DashboardCard/DashboardCard.tsx` | 54-67 | `f9656be2` | primary |

- Merged from: RULE-dashboard-FE-06-003
- Related rules: RULE-INDICADORES-ETL-002, RULE-INDICADORES-ETL-006, RULE-INDICADORES-ETL-005, RULE-INDICADORES-ETL-009, RULE-INDICADORES-ETL-008, RULE-INDICADORES-ETL-022

## Notes
Feeds the per-color Progress bars rendered at lines 356-390 of the same file.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
