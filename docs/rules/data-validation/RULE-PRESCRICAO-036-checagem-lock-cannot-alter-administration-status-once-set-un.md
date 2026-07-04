# RULE-PRESCRICAO-036 — Checagem lock — cannot alter administration status once set (unused in this scope)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | prescricao |

## Rule
A static validator exists asserting that once a scheduled dose's "administrado" field has been set to any non-null value, it cannot be altered again — but this method is not called anywhere within the files examined in this partition.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.administrado | boolean (nullable) |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| ValidationError raised if invalid | exception |  |

## Logic
```text
@staticmethod
def validar_alteracao_dado(instance, validated_data):
    if instance.administrado is not None:
        raise ValidationError("Você não pode alterar a checagem da prescrição!")
```

## Edge cases (as implemented)
Unused within this partition's update() flow (RULE-prescricao-BE-07-006 does not call it).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/horario_prescricao.py` | 289-292 | `8166c07e` | primary |

- Merged from: RULE-prescricao-BE-07-008
- Related rules: RULE-PRESCRICAO-008

## Notes
Recorded because it encodes a real business rule even if apparently dead code here; may be invoked from a view or another serializer outside trilha_homecare/api/v1/serializers/.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
