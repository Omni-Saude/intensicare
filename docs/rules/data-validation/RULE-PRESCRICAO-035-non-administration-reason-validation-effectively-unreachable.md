# RULE-PRESCRICAO-035 — Non-administration reason validation (effectively unreachable guard)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | prescricao |

## Rule
A validation intended to require either "administrado" or a "motivo_nao_administrado" is only ever invoked from a call site that has already guaranteed motivo_nao_administrado is truthy, making the check itself practically unable to raise.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| validated_data.administrado | boolean (nullable) |  |  |
| validated_data.motivo_nao_administrado | string (nullable) |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| ValidationError raised if invalid (in practice, never) | exception |  |

## Logic
```text
@staticmethod
def validar_motivo(validated_data):
    if not (validated_data.get("administrado", None) or validated_data.get("motivo_nao_administrado", None)):
        raise ValidationError("É necessário informar o motivo da prescrição não administrada")
# Call site (update(), RULE-prescricao-BE-07-006):
#   if administrado is False and motivo_nao_administrado:  <- already guarantees motivo truthy
#       validar_motivo(validated_data)
```

## Edge cases (as implemented)
Because the only call site already checked `validated_data.get("motivo_nao_administrado")` is truthy before calling this, the `or motivo_nao_administrado` half of the condition inside validar_motivo is always True at that point, so the ValidationError branch is unreachable via this call path.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/horario_prescricao.py` | 279-287 | `8166c07e` | primary |

- Merged from: RULE-prescricao-BE-07-007
- Related rules: RULE-PRESCRICAO-008, RULE-PRESCRICAO-030

## Notes
AMBIGUOUS whether validar_motivo is intended to also be called from other, out-of-scope call sites where the guarantee would not hold (which would make the check meaningful there); as implemented within this file it is dead validation.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
