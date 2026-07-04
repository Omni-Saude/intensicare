# RULE-INDICADORES-ETL-007 — Dashboard alert-count 4th severity level inconsistent with 3-level Alerta elsewhere

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
Models.DashboardItem.TotalAlerta defines four alert-count buckets — VERMELHO, AMARELO, NEUTRO, and LARANJA (orange) — whereas every other alert type/count in the codebase (Ocupacao.Alerta, Estatisticas.Alertas) defines only three levels (VERMELHO, AMARELO, NEUTRO) and never includes LARANJA.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| alert severity | string enum / count-bucket key |  | 3 levels (Ocupacao.Alerta, Estatisticas.Alertas) vs 4 levels (DashboardItem.TotalAlerta) |

## Outputs

| Name | Type | Unit |
|---|---|---|
| total_alertas | { VERMELHO: number, AMARELO: number, NEUTRO: number, LARANJA: number } |  |

## Logic
```text
DashboardItem.TotalAlerta = { VERMELHO: number, AMARELO: number, NEUTRO: number, LARANJA: number }
Estatisticas.Alertas       = { VERMELHO: number, AMARELO: number, NEUTRO: number }              // no LARANJA
Ocupacao.Alerta (type)     = "AMARELO" | "NEUTRO" | "VERMELHO"                                    // no LARANJA
```

## Edge cases (as implemented)
Recorded verbatim; not reconciled. If a bed/trilha's alerta value can in fact be "LARANJA" server-side (contradicting the 3-value Ocupacao.Alerta union), the frontend type for that field would be unsound.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/DashboardItem.d.ts` | 26-31 | `f9656be2` | primary |

- Merged from: RULE-dashboard-FE-07-001
- Related rules: RULE-INDICADORES-ETL-006, RULE-INDICADORES-ETL-023, RULE-INDICADORES-ETL-018

## Notes
Cross-reference src/@types/models/Ocupacao.d.ts line 106 and src/@types/models/Estatisticas.d.ts lines 18-22.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
