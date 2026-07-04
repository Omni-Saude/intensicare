# RULE-INDICADORES-ETL-023 — Macro-indicator KPI shape

| Field | Value |
|---|---|
| Category | billing-administrative |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | indicadores-etl |

## Rule
Each dashboard item (company/establishment/sector) reports six macro-level KPIs — lives saved (vidas_salvas), deaths (obitos), length of stay (tempo_permanencia), mortality rate (tx_mortalidade), occupancy rate (tx_ocupacao), and admissions (admissao).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| vidas_salvas, obitos, tempo_permanencia, tx_mortalidade, tx_ocupacao, admissao | number | not stated (rates presumed 0-1 or 0-100; tempo_permanencia presumed days) |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| MacroIndicadores | object |  |

## Logic
```text
MacroIndicadores = { vidas_salvas: number, obitos: number, tempo_permanencia: number,
                      tx_mortalidade: number, tx_ocupacao: number, admissao: number }
```

## Edge cases (as implemented)
No units or valid ranges given in this partition for any of the six fields.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/DashboardItem.d.ts` | 17-24 | `f9656be2` | primary |

- Merged from: RULE-dashboard-FE-07-002
- Related rules: RULE-INDICADORES-ETL-018, RULE-INDICADORES-ETL-007, RULE-INDICADORES-ETL-010

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
