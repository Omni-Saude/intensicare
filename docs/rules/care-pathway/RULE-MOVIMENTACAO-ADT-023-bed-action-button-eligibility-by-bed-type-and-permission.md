# RULE-MOVIMENTACAO-ADT-023 — Bed action-button eligibility by bed type and permission

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
The action buttons available on an occupied/empty bed card are gated jointly by leito.tipo ("manual" vs "homecare") and role-based permission flags. Manual beds expose Movimentacao/Remover-paciente/Adicionar-paciente buttons subject to permission; homecare beds expose only a "Gerenciar arquivos" button (no permission check) and only while occupied.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| ocupacao.leito.tipo | enum manual\|homecare |  |  |
| ocupacao.leito.ocupado | boolean |  |  |
| can_add_movimentacao / can_remove_paciente / can_create_paciente | permission booleans |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| showMovimentacaoButton / showRemoverPacienteButton / showGerenciarArquivosButton / showAdicionarPacienteButton | boolean |  |

## Logic
```text
if (leito.ocupado) {
  showMovimentacaoButton    = (leito.tipo === "manual") && can_add_movimentacao
  showRemoverPacienteButton = (leito.tipo === "manual") && can_remove_paciente
  showGerenciarArquivosButton = (leito.tipo === "homecare")   // no permission gate
} else {
  showAdicionarPacienteButton = (leito.tipo === "manual") && can_create_paciente
  // note: no button of any kind is rendered for an empty "homecare" bed
}
// camera button (always rendered when leito.ocupado) is separately disabled via:
cameraButtonDisabled = !ocupacao.leito.has_camera
```

## Edge cases (as implemented)
An unoccupied ("vazio") homecare bed exposes no action button at all - as implemented, patients cannot be added to an empty homecare bed from this card.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx | 605-681 | f9656be2 | primary |
- Merged from: RULE-leito-FE-06-009
- Related rules: RULE-MOVIMENTACAO-ADT-025, RULE-MOVIMENTACAO-ADT-027, RULE-MOVIMENTACAO-ADT-052

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
