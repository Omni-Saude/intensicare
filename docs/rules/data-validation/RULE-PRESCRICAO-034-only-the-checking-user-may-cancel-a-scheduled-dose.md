# RULE-PRESCRICAO-034 — Only the checking user may cancel a scheduled dose

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
A scheduled prescription dose can only be cancelled by the same user who originally checked/administered it (checado_por); any other user attempting cancellation is rejected.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.checado_por | user reference |  |  |
| requesting user | user reference |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| ValidationError raised if invalid | exception |  |

## Logic
```text
@staticmethod
def validar_cancelamento(instance, validated_data, user):
    if instance.checado_por != user:
        raise ValidationError("O cancelamento só pode ser feito pelo usuario que checou a prescrição!")
```

## Edge cases (as implemented)


## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/horario_prescricao.py` | 301-306 | `8166c07e` | primary |

- Merged from: RULE-prescricao-BE-07-009
- Related rules: RULE-PRESCRICAO-008, RULE-PRESCRICAO-026, RULE-PRESCRICAO-017

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
