# RULE-INDICADORES-ETL-022 — Macro-indicator tile display filter

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
Of the five macro indicators (vidas salvas, óbitos, taxa de mortalidade, admissões, tempo de permanência), a tile is rendered only if its resolved value is a string or a number; taxa de mortalidade is additionally pre-filtered to `undefined` unless its raw value is truthy and not null.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| item.macro_indicadores.vidas_salvas | number | count |  |
| item.macro_indicadores.obitos | number | count |  |
| item.macro_indicadores.tx_mortalidade | number | % |  |
| item.macro_indicadores.admissao | number | count |  |
| item.macro_indicadores.tempo_permanencia | number | days |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| IndicadoresArray[i].value | string \| number \| undefined |  |

## Logic
```text
tx_mortalidade_display = (tx_mortalidade && tx_mortalidade !== null) ? `${tx_mortalidade}%` : undefined
// render filter applied to every entry in IndicadoresArray:
show(indicador) = typeof indicador.value === "string" || typeof indicador.value === "number"
// if item.macro_indicadores is absent, IndicadoresArray = []
// if macro_indicadores is present but has zero own keys, shows Empty("Sem indicadores") instead
```

## Edge cases (as implemented)
tx_mortalidade of exactly 0 is falsy in JS, so a 0% mortality rate is treated the same as absent and hidden (not displayed as "0%") — this differs from the numeric fields elsewhere in the partition that use an explicit not-null/not-undefined check (compare RULE-indicadores-FE-06-018/019/020).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/ListDashboard/DashboardCard/DashboardCard.tsx` | 111-152 | `f9656be2` | primary |

- Merged from: RULE-dashboard-FE-06-008
- Related rules: RULE-INDICADORES-ETL-005, RULE-INDICADORES-ETL-001, RULE-INDICADORES-ETL-002, RULE-INDICADORES-ETL-006, RULE-INDICADORES-ETL-008, RULE-INDICADORES-ETL-009, RULE-INDICADORES-ETL-024, RULE-INDICADORES-ETL-025, RULE-INDICADORES-ETL-026

## Notes
Rendering site at lines 316-350 of the same file.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
