# RULE-PRESCRICAO-026 — Revert administration check requires justification

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Reverting a previously-checked horario requires a mandatory free-text cancellation justification and sets administrado=false on the horario.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| justificativa_cancelamento | string |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| patchBody | object { justificativa_cancelamento, administrado:false } |  |

## Logic

```text
ModalRevertCheck form: field justificativa_cancelamento required (defaultFormRules).
onOk(value): onOk({ body: { ...value, administrado:false }, horarioId: horario.id })
```

## Edge cases (as implemented)
The revert always forces administrado=false regardless of prior state.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricao/ModalRevertCheck/ModalRevertCheck.tsx` | 27-40 | `f9656be2` | primary |

**Merged from:**

- RULE-presc-FE-04-009

**Related rules:**

- RULE-PRESCRICAO-017
- RULE-PRESCRICAO-034

## Notes
onOk merge with administrado:false is in HorarioCheck.tsx lines 245-254.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
