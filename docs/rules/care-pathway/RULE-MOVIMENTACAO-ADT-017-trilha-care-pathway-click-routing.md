# RULE-MOVIMENTACAO-ADT-017 — Trilha (care-pathway) click routing

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
Clicking a trilha chip on a bed card routes to a different destination depending on the trilha's tipo: prescription and fluid-balance trilhas navigate to dedicated pages; the evolucao trilha opens an in-drawer type-selection menu; any other trilha type opens the generic recommendations drawer at that trilha's index.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| trilha.tipo | enum prescricao\|balanco_hidrico\|evolucao\|other |  |  |
| trilhaIndex i | integer |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| navigationAction | enum route_prescricao\|route_balanco\|open_evolucao_menu\|open_recomendacoes_drawer |  |

## Logic
```text
switch (trilha.tipo) {
  case "prescricao":
    router.push(`${pathname}/leito/[id_leito]/ocupacao/[id_ocupacao]/prescricao/`)
    break
  case "balanco_hidrico":
    router.push(`${pathname}/leito/[id_leito]/ocupacao/[id_ocupacao]/balanco/`)
    break
  case "evolucao":
    setShowMenuEvolucao(true)
    break
  default:
    onTrilhaClick(ocupacao.id, ocupacao.leito.nome, i)   // opens recommendations drawer
}
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx | 104-134 | f9656be2 | primary |
- Merged from: RULE-leito-FE-06-010
- Related rules: RULE-MOVIMENTACAO-ADT-018

## Notes
The prescricao/balanco routes are consumed by out-of-partition pages/components (Prescricao*, BalancoHidrico*).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
