# RULE-PRESCRICAO-013 — Save vs Save-and-check vs Update-time decision when hour edited

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
In the check modal, if the administration time was changed (hasHourChanged), the primary button offers a two-way choice; otherwise it submits directly. This distinguishes "check the horario now" from "only reschedule its time".

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| asbutton | boolean |  |  |
| hasHourChanged | boolean |  |  |
| form.horario | moment |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| action | enum {submit-full, update-time-only} |  |

## Logic

```text
if (asbutton || !hasHourChanged):
  primary button submits the whole form (form.submit())
else:   # editing an existing horario AND time changed
  Popconfirm:
    okText "Salvar e checar"   onConfirm -> form.submit()   # full check + new time
    cancelText "Atualizar horario" onCancel -> onOk({ body:{ horario: form.getFieldValue("horario").format("HH:mm") }, horarioId }) # PATCH time only
```

## Edge cases (as implemented)
hasHourChanged is set true only when the changed field is `horario` (CheckModalContent onValuesChange). Cancel/close resets the form and hasHourChanged=false.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricao/HorarioCheck/CustomModalCheck/CustomModalCheck.tsx` | 108-151 | `f9656be2` | primary |

**Merged from:**

- RULE-presc-FE-04-012

**Related rules:**

- RULE-PRESCRICAO-025

## Notes
hasHourChanged wiring is in CheckModalContent.tsx (onValuesChange, lines 86-94) and HorarioCheck.tsx.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
