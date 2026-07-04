# RULE-PRESCRICAO-018 — can_manage_prescricao gates all administration controls

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Without can_manage_prescricao permission, the horario check/dots buttons are hidden and the horario is rendered view-only (only the time and checker name shown); the add-new button is also hidden.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| can_manage_prescricao | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| controlsVisible | boolean |  |

## Logic

```text
horario-wrapper gets class "only-view" when !can_manage_prescricao.
Left dots/info button rendered only if can_manage_prescricao.
Right check button rendered only if can_manage_prescricao.
Add-new HorarioCheck rendered only if (!prescricao.suspenso && can_manage_prescricao).
```

## Edge cases (as implemented)
Permission is read from useEffectivePermissions() hook (out of partition).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricao/HorarioCheck/HorarioCheck.tsx` | 171-237 | `f9656be2` | primary |

**Merged from:**

- RULE-presc-FE-04-014

**Related rules:**

- RULE-PRESCRICAO-016
- RULE-PRESCRICAO-023

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
