# RULE-PRESCRICAO-012 — Horario persistence routing (POST / PATCH / DELETE)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
The onOk dispatcher decides the backend operation for a horario from the presence of horarioId and body.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| horarioId | string\|undefined |  |  |
| body | object\|undefined |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| operation | enum {POST, PATCH, DELETE} |  |

## Logic

```text
if (!horarioId)            -> postHorario(prescricao.id, body)        # create new horario
else if (body)             -> patchHorario(prescricao.id, horarioId, body)  # update/check
else                       -> deleteHorario(prescricao.id, horarioId) # delete (no body, has id)
```

## Edge cases (as implemented)
A call with horarioId set but body undefined is interpreted as a delete. A call with no horarioId requires body (non-null assertion body!).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricao/Prescricao.tsx` | 41-52 | `f9656be2` | primary |

**Merged from:**

- RULE-presc-FE-04-005

**Related rules:**

- RULE-PRESCRICAO-023
- RULE-PRESCRICAO-024
- RULE-PRESCRICAO-025
- RULE-PRESCRICAO-015

## Notes
Network layer (hooks/networking/prescricao) is in another partition; the day filter { dia: date } and refresh-after-write are in Prescricoes.tsx.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
