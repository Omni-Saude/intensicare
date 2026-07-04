# RULE-EVOLUCOES-052 — Only the original author can edit an evolution

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
An evolution document can only be updated by the same user who created (preenchido_por) it; any other user attempting to edit it is rejected.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.preenchido_por |  |  |  |
| requesting usuario |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| ValidationError raised if invalid |  |  |

## Logic
```text
if instance.preenchido_por != usuario:
    raise ValidationError(
        "Você não é o usuário que criou esta evolução, apenas o criador pode "
        "editar as evoluções não liberadas."
    )
```

## Edge cases (as implemented)
The error message mentions "não liberadas" (not-yet-released) but the code check itself does not condition on status=="liberado" — it applies to ANY update attempt regardless of release state (beyond the separate inativo check).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_base.py` | 332-341 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-008
- Related rules: RULE-EVOLUCOES-027, RULE-EVOLUCOES-051, RULE-EVOLUCOES-019

## Notes
AMBIGUOUS whether the mismatch between the error message wording ("não liberadas") and the unconditional check is intentional (perhaps liberado records are expected to be blocked earlier by validar_status once transitioned to "inativo") — recorded as-is.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
