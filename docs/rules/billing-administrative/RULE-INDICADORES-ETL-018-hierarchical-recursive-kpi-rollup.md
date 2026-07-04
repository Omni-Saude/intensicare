# RULE-INDICADORES-ETL-018 — Hierarchical recursive KPI rollup

| Field | Value |
|---|---|
| Category | billing-administrative |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | indicadores-etl |

## Rule
A DashboardItem (representing a company, establishment, or sector) can recursively contain child DashboardItem entries under "setores" and/or a flat list of Leito entries under "leitos", allowing the same KPI shape (total_leitos, total_assistidos, total_leitos_ocupados, macro_indicadores, qtd_mensagens, total_alertas, ocupacao) to be reported at every level of the empresa > estabelecimento > setor hierarchy.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| setores | Models.DashboardItem[], optional |  |  |
| leitos | Models.Leito[], optional |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| DashboardItem (nested) | object (recursive) |  |

## Logic
```text
DashboardItem = {
  id, nome, total_leitos: number, total_assistidos: number, total_leitos_ocupados: number,
  macro_indicadores: MacroIndicadores, qtd_mensagens: number, total_alertas: TotalAlerta,
  ocupacao: number, setores?: DashboardItem[], leitos?: Leito[]
}
```

## Edge cases (as implemented)
setores and leitos are both optional and can, in principle, coexist on the same node (no mutual-exclusivity constraint enforced in this partition).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/@types/models/DashboardItem.d.ts` | 3-15 | `f9656be2` | primary |

- Merged from: RULE-dashboard-FE-07-003
- Related rules: RULE-INDICADORES-ETL-023, RULE-INDICADORES-ETL-007

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
