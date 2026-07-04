# RULE-EVOLUCOES-043 — Evolution status state machine (salvo / liberado / inativo)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
An evolution formulario has a status among salvo, liberado, inativo (plus empty). Status drives available actions and the displayed icon/color, and success messaging on update.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| formulario.status [salvo | liberado | inativo | '' ] |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| statusIcon/color, actions |  |  |

## Logic
```text
handleIconByStatus(status):
  "salvo"    -> { icon: mdiCheckCircleOutline, color:"#258a10" }
  "liberado" -> { icon: mdiCheckAll,           color:"#1890ff" }
  "inativo"  -> { icon: mdiCancel,             color:"#ff1633" }
  ""/default -> { icon: mdiInformation,        color:"#bababa" }
On patch: if (values.status === "liberado") msg "Formulario atualizado e liberado com sucesso!"
          else msg "Formulario atualizado com sucesso!"
```

## Edge cases (as implemented)
Delete/inactivate path shows "Formulario inativado com sucesso!" (soft-delete to inativo).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/HistoricoEvolucao/HistoricoEvolucao.tsx` | 92-96 | `f9656be2` | primary |
- Merged from: RULE-evolucao-FE-04-033
- Related rules: RULE-EVOLUCOES-042, RULE-EVOLUCOES-019, RULE-EVOLUCOES-044

## Notes
handleIconByStatus defined in src/utils/handleIconByStatus.ts (cross-partition).

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
