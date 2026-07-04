# RULE-PRESCRICAO-025 — Administration-check form value construction

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
When submitting the administration-check modal, the payload is transformed: reason is set only when not administered; exported quantity defaults to the prescribed quantity; the free-text "outros" reason overrides the select; the changed time is only sent when the hour was edited.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| rawValues.administrado | boolean |  |  |
| motivoNaoAdministrado | string (enum value or "outros") |  |  |
| rawValues.qtd_exportada | number | ml |  |
| quantidade | number | ml |  |
| editHour | boolean |  |  |
| rawValues.horario | moment |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| SendValue | object |  |

## Logic

```text
values.motivo_nao_administrado =
  rawValues.administrado ? undefined
  : motivoNaoAdministrado === "outros" ? form.getFieldValue("outros_motivos")
  : form.getFieldValue("motivo_nao_administrado")
values.qtd_exportada =
  rawValues.administrado ? (rawValues.qtd_exportada ? rawValues.qtd_exportada : quantidade)
  : undefined
values.outros_motivos = undefined            # stripped from payload
values.horario = editHour ? rawValues.horario.format("HH:mm") : undefined
```

## Edge cases (as implemented)
qtd_exportada falls back to the prescribed `quantidade` when the field is empty AND administrado is true. When not administered, qtd_exportada is cleared. horario is omitted unless the clock-edit toggle was used.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricao/CheckModalContent/CheckModalContent.tsx` | 39-59 | `f9656be2` | primary |

**Merged from:**

- RULE-presc-FE-04-006

**Related rules:**

- RULE-PRESCRICAO-001
- RULE-PRESCRICAO-030
- RULE-PRESCRICAO-013

## Notes
initialValues seed administrado=true and qtd_exportada=quantidade (lines 61-64).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
