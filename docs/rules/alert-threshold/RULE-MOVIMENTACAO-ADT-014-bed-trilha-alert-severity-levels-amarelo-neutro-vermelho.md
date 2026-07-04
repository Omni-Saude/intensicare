# RULE-MOVIMENTACAO-ADT-014 — Bed/trilha alert severity levels (AMARELO|NEUTRO|VERMELHO)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
A bed occupancy, its care-pathway (trilha), and any chat/feed message reference exactly three alert-severity levels - yellow (AMARELO), neutral/none (NEUTRO), and red (VERMELHO) - used as a traffic-light severity indicator throughout the UI.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| alerta | string enum: AMARELO \| NEUTRO \| VERMELHO |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| alerta | string enum |  |

## Logic
```text
Alerta = "AMARELO" | "NEUTRO" | "VERMELHO"
// used by: Models.Ocupacao.alerta, Models.Ocupacao.Trilha.alerta (typed as plain string there),
// Models.Feed.alerta, Models.Chat.Mensagem.alerta (all typed as Ocupacao.Alerta)
```

## Edge cases (as implemented)
Ocupacao.Trilha.alerta and Models.Criterio.alerta are typed as plain string, not the Alerta union - so at the type level a Trilha/Criterio could carry a value outside {AMARELO,NEUTRO,VERMELHO}, unlike Ocupacao.alerta itself.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/@types/models/Ocupacao.d.ts | 106-106 | f9656be2 | primary |
- Merged from: RULE-ocupacao-FE-07-001
- Related rules: RULE-MOVIMENTACAO-ADT-012

## Notes
A 4th level ("LARANJA") appears only in the dashboard aggregate type (RULE-dashboard-FE-07-001, out of this cluster), contradicting this 3-level definition.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
