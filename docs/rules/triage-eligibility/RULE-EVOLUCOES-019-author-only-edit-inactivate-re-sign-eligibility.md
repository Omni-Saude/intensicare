# RULE-EVOLUCOES-019 — Author-only edit / inactivate / re-sign eligibility

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
Edit / inactivate / liberar-assinar controls on a past evolution are shown only when the viewer has add permission, is the original author (preenchido_por.id == user.usuario.id), and the form is not already inativo. Liberado forms expose Inativar + re-sign; non-liberado forms expose an Edit/Cancel toggle.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| permission (canAdd) |  |  |  |
| formulario.preenchido_por.id |  |  |  |
| user.usuario.id |  |  |  |
| formulario.status [salvo | liberado | inativo] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| availableActions |  |  |

## Logic
```text
showActions = permission && (formulario.preenchido_por.id === user.usuario.id) && (status !== "inativo")
if (showActions):
  if (status === "liberado"):
    show "Inativar" (confirm -> deleteEvolucao) and "Liberar/assinar novamente"
  else:
    show Edit/Cancel toggle (setEditing)
# Editing enables the past-evolution form in "modal" mode; otherwise "in_page" (read-only).
```

## Edge cases (as implemented)
Non-authors and inativo forms see no action buttons (view only). The drawer OK button is hidden unless editing (hideOk = !editing).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/HistoricoEvolucao/HistoricoEvolucao.tsx` | 230-296 | `f9656be2` | primary |
- Merged from: RULE-evolucao-FE-04-034
- Related rules: RULE-EVOLUCOES-043, RULE-EVOLUCOES-044, RULE-EVOLUCOES-052

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
