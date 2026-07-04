# RULE-PRESCRICAO-023 — Suspended horario blocks all administration actions

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
A suspended horario cannot be checked, edited, or acted upon. Clicking a suspended tag shows a warning and no modal/action opens; all check handlers are guarded by !suspenso.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| horario.suspenso | boolean |  |  |
| horario.id | string |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| action | enum {warning, open-modal, quick-check, none} |  |

## Logic

```text
onClick(tag):
  if (horario.suspenso) message.warning("Horario suspenso, nao e possivel realizar acoes")
  else if (asbutton && !horario.id) openCheckModal()
onClick(dots/info btn):
  if (!horario.administrado && !horario.motivo_nao_administrado && !horario.suspenso) openCheckModal()
onClick(check btn):
  if (!horario.checado_por && !horario.suspenso) onOk({ body:{administrado:true}, horarioId:horario.id })
```

## Edge cases (as implemented)
The dots/info button opens the modal ONLY when the horario is pending (not administered, not refused, not suspended). The right-side check button fires ONLY when nobody has checked it yet (checado_por falsy) and it is not suspended.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricao/HorarioCheck/HorarioCheck.tsx` | 150-236 | `f9656be2` | primary |

**Merged from:**

- RULE-presc-FE-04-002

**Related rules:**

- RULE-PRESCRICAO-011
- RULE-PRESCRICAO-018

## Notes
All action controls also require can_manage_prescricao (see RULE-presc-FE-04-015).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
