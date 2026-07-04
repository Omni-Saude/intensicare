# RULE-PRESCRICAO-032 — Horario de prescricao - autor padrao 'sistema'

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
On save, if a prescription time-slot has no creator, it is assigned to the user with username "sistema"; if that user is missing a ValidationError is raised.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| self.criado_por | FK Usuario |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| criado_por (defaulted) or ValidationError | FK Usuario |  |

## Logic

```text
if not self.criado_por:
    try:
        self.criado_por = Usuario.objects.get(username="sistema")
    except Usuario.DoesNotExist:
        raise ValidationError("Usuario sistema nao encontrado")
return super().save(...)
```

## Edge cases (as implemented)
Only defaults when criado_por is unset. Hard dependency on a seed "sistema" user.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/horarios_prescricao.py` | 62-70 | `8166c07e` | primary |

**Merged from:**

- RULE-prescricao-BE-06-003

**Related rules:**

- RULE-PRESCRICAO-020

## Notes
Auto-generated slots (RULE-prescricao-BE-06-001) rely on this to attribute authorship to the system.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
