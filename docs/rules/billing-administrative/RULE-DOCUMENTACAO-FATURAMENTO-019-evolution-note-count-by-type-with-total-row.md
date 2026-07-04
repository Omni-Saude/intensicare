# RULE-DOCUMENTACAO-FATURAMENTO-019 — Evolution-note count-by-type with Total row

| Field | Value |
|---|---|
| Category | billing-administrative |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
Aggregates a list of evolution/progress-note records into counts per type, then returns a list whose FIRST element is a "Total" row equal to the overall record count, followed by one row per distinct type.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| itens | RelatorioEvolucao[] |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| resultado | {tipo:string, qtd:number}[] |  |

## Logic
```text
contagemTipos = {}
for registro in itens: contagemTipos[registro.tipo] = (contagemTipos[registro.tipo] || 0) + 1
total = { tipo: "Total", qtd: itens.length }
resultado = [ {tipo, qtd} for each tipo in contagemTipos ]
return [ total, ...resultado ]
```

## Edge cases (as implemented)
Total is itens.length (total record count), always first. Empty input -> [{tipo:"Total",qtd:0}]. Type key order follows insertion order of first occurrence.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/contarTiposEvolucao.ts | 6-28 | f9656be2 | primary |
- Merged from: RULE-reporting-FE-02-001
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-014

## Notes
Reporting aggregation for evolution-note dashboards.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
