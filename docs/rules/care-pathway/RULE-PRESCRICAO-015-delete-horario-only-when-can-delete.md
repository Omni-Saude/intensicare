# RULE-PRESCRICAO-015 — Delete horario only when can_delete

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
The "Deletar Horario" button in the check modal is rendered only when horario.can_delete is true, and requires a confirmation popconfirm before issuing the delete.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| horario.can_delete | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| deleteAction | onOk({ horarioId }) -> DELETE |  |

## Logic

```text
if (horario.can_delete):
  render Popconfirm("Tem certeza que deseja remover este horario?")
    onConfirm: onOk({ horarioId: horario.id }); closeModal()
```

## Edge cases (as implemented)
Delete path sends horarioId with no body -> DELETE (RULE-presc-FE-04-005).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricao/HorarioCheck/CustomModalCheck/CustomModalCheck.tsx` | 57-78 | `f9656be2` | primary |

**Merged from:**

- RULE-presc-FE-04-011

**Related rules:**

- RULE-PRESCRICAO-014

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
