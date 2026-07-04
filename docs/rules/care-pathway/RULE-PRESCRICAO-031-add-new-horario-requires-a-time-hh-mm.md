# RULE-PRESCRICAO-031 — Add-new-horario requires a time (HH:mm)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Creating a new administration horario requires a mandatory time picker; the value is serialized as HH:mm and posted as a new horario.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| horario | moment |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| postBody | object { horario:"HH:mm" } |  |

## Logic

```text
field "horario" required (defaultFormRules).
onFinish: values.horario = rawValues.horario.format("HH:mm"); onOk({ body: values })  # no horarioId -> POST
```

## Edge cases (as implemented)
rawValues.horario.format is called unconditionally; a missing time is prevented by the required rule.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricao/AsButtonModalContent/AsButtonModalContent.tsx` | 11-32 | `f9656be2` | primary |

**Merged from:**

- RULE-presc-FE-04-013

**Related rules:**

- RULE-PRESCRICAO-016

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
