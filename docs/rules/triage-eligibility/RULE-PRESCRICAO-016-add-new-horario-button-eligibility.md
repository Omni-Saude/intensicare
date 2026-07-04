# RULE-PRESCRICAO-016 — Add-new-horario button eligibility

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
The "Adicionar" (add new administration time) placeholder is rendered only when the prescription is not suspended AND the user has can_manage_prescricao permission.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| prescricao.suspenso | boolean |  |  |
| can_manage_prescricao | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| showAddButton | boolean |  |

## Logic

```text
showAddButton = (!prescricao.suspenso) && can_manage_prescricao
```

## Edge cases (as implemented)
Existing horarios always render regardless of permission (view-only when no permission).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricao/Prescricao.tsx` | 137-144 | `f9656be2` | primary |

**Merged from:**

- RULE-presc-FE-04-003

**Related rules:**

- RULE-PRESCRICAO-018

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
