# RULE-INDICADORES-ETL-025 — 24h indicator numeric-type display filter

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
Each of the six 24h-window indicator tiles (Balanço, Diurese, HGT, Evacuações, Temperatura Máxima, Ganhos) is rendered only when its underlying value's JavaScript type is "number"; any other type (undefined, null, string) hides that tile entirely.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| item.balanco_24h | number \| undefined |  |  |
| item.diurese_24h | number \| undefined |  |  |
| item.hgt_24h | number \| undefined |  |  |
| item.evacuacoes_24h | number \| undefined |  |  |
| item.temperatura_max_24h | number \| undefined |  |  |
| item.ganhos_24h | number \| undefined |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| tileVisible | boolean |  |

## Logic
```text
for each field f: show(f) = typeof f === "number"
```

## Edge cases (as implemented)
A value of 0 for any of these six fields still satisfies typeof === 'number' and IS shown (contrast with plain-truthy checks used elsewhere in the partition).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ItemIndicadores24h/ItemIndicadores24h.tsx` | 18-58 | `f9656be2` | primary |

- Merged from: RULE-indicadores-FE-06-019
- Related rules: RULE-INDICADORES-ETL-024, RULE-INDICADORES-ETL-026, RULE-INDICADORES-ETL-022

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
