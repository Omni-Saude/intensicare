# RULE-EVOLUCOES-054 — CPF and PIN required to sign an evolution

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
A user must have both a registered CPF and a registered PIN before they can digitally sign an evolution document's PDF.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| usuario.cpf |  |  |  |
| usuario.pin |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| ValidationError raised if invalid |  |  |

## Logic
```text
validar_cpf(usuario)   # raises if no cpf
if not usuario.pin:
    raise ValidationError(
        "Você não possui PIN cadastrado. Consulte a administração para cadastrar seu PIN."
    )
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_base.py` | 322-330 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-010
- Related rules: RULE-EVOLUCOES-053, RULE-EVOLUCOES-025

## Notes
Same cpf+pin pairing is checked independently ad hoc in can_assinar computed fields (RULE-balanco-BE-07-007 etc.), duplicating this rule's intent.

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
