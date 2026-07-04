# RULE-PRESCRICAO-024 — Quick "administered" check without reason

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
Clicking the right-hand circle button on a pending horario marks it administered directly (administrado:true) with no modal, provided it is not yet checked and not suspended.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| horario.checado_por | object\|null |  |  |
| horario.suspenso | boolean |  |  |
| horario.id | string |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| patchBody | object { administrado:true } |  |

## Logic

```text
if (!horario.checado_por && !horario.suspenso):
  onOk({ body: { administrado: true }, horarioId: horario.id })
# onOk with horarioId + body -> PATCH (see RULE-presc-FE-04-006)
```

## Edge cases (as implemented)
Only rendered when can_manage_prescricao is true. Does not capture qtd_exportada; the ml-based fluid-balance quantity is captured only via the full CheckModalContent path.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricao/HorarioCheck/HorarioCheck.tsx` | 212-236 | `f9656be2` | primary |

**Merged from:**

- RULE-presc-FE-04-004

**Related rules:**

- RULE-PRESCRICAO-025
- RULE-PRESCRICAO-012

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
