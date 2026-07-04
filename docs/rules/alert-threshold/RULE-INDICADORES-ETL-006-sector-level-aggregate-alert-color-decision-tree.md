# RULE-INDICADORES-ETL-006 — Sector-level aggregate alert-color decision tree

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
Determines the single overall alert color badge for a sector's dashboard card, given its counts of red/amber/neutral alerts and its assisted-percentage. ASSISTIDO takes top priority; otherwise the highest-count color wins, with VERMELHO (red) preferred on ties over AMARELO, and AMARELO preferred on ties over NEUTRO.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| item.total_alertas.VERMELHO | number | count |  |
| item.total_alertas.AMARELO | number | count |  |
| item.total_alertas.NEUTRO | number | count |  |
| item.total_assistidos | number | count |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| alerta | string enum (ASSISTIDO\|VERMELHO\|AMARELO\|NEUTRO\|"") |  |

## Logic
```text
if (!item.total_alertas) return "NEUTRO"
if (assistPercent(item.total_assistidos) === 100) return "ASSISTIDO"
else if (VERMELHO >= AMARELO && VERMELHO >= NEUTRO && VERMELHO > 0) return "VERMELHO"
else if (AMARELO > VERMELHO && AMARELO >= NEUTRO && AMARELO > 0) return "AMARELO"
else if (NEUTRO > AMARELO && NEUTRO > VERMELHO && NEUTRO > 0) return "NEUTRO"
else return ""
```

## Edge cases (as implemented)
When all three counts are 0 (and total_alertas object is present but empty/zeroed), none of the branches match and the result is "" (falls through to no color, card gets the "empty" CSS class instead). If total_alertas is falsy/absent entirely, defaults straight to "NEUTRO" without evaluating assistPercent.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ListDashboard/DashboardCard/DashboardCard.tsx` | 81-109 | `f9656be2` | primary |

- Merged from: RULE-dashboard-FE-06-005
- Related rules: RULE-INDICADORES-ETL-001, RULE-INDICADORES-ETL-002, RULE-INDICADORES-ETL-007, RULE-INDICADORES-ETL-005

## Notes
Depends on RULE-dashboard-FE-06-004 (assistPercent) for the ASSISTIDO branch.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
