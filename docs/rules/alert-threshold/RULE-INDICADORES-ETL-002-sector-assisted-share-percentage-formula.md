# RULE-INDICADORES-ETL-002 — Sector assisted-share percentage formula

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
Computes what percentage of a sector's yellow+red alerted patients are currently marked as "assistido" (being actively assisted), used both to size the ASSISTIDO progress bar and, at 100%, to flip the whole card's status to ASSISTIDO (see RULE-dashboard-FE-06-005).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| assist | number | count |  |
| item.total_alertas.AMARELO | number | count |  |
| item.total_alertas.VERMELHO | number | count |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| assistPercent | number | % |

## Logic
```text
total = AMARELO + VERMELHO
assistPercent(assist) = total !== 0 ? (assist * 100) / total : 0
```

## Edge cases (as implemented)
Division-by-zero guarded, returns 0. Consequence: if a sector has total_assistidos > 0 but zero AMARELO/VERMELHO alerts, assistPercent returns 0 (not 100), so the ASSISTIDO override in RULE-dashboard-FE-06-005 will NOT trigger in that scenario.

## Verification
- Verdict: UNVERIFIABLE (clinical impact: n/a)
- Reference: No authoritative clinical/published reference. Proprietary UI display rule (assisted-share = assist/(AMARELO+VERMELHO)*100).

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ListDashboard/DashboardCard/DashboardCard.tsx` | 69-79 | `f9656be2` | primary |

- Merged from: RULE-dashboard-FE-06-004
- Related rules: RULE-INDICADORES-ETL-001, RULE-INDICADORES-ETL-006, RULE-INDICADORES-ETL-005, RULE-INDICADORES-ETL-009, RULE-INDICADORES-ETL-008, RULE-INDICADORES-ETL-022

## Notes
Used again at lines 375-388 for the ASSISTIDO progress bar (percent floor via Math.floor for display only).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
