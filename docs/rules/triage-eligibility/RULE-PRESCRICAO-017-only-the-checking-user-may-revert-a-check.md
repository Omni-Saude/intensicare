# RULE-PRESCRICAO-017 — Only the checking user may revert a check

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
The "Reverter checagem" button is shown only to the user who originally checked the horario (checado_por.id equals the logged-in user id).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| horario.checado_por.id | string |  |  |
| user.usuario.id | string |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| showRevertButton | boolean |  |

## Logic

```text
showRevertButton = horario.checado_por && (user.usuario.id === horario.checado_por.id)
```

## Edge cases (as implemented)
Popover is only shown at all when administrado or motivo_nao_administrado is set.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricao/HorarioCheck/HorarioCheck.tsx` | 98-115 | `f9656be2` | primary |

**Merged from:**

- RULE-presc-FE-04-010

**Related rules:**

- RULE-PRESCRICAO-026
- RULE-PRESCRICAO-034

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
