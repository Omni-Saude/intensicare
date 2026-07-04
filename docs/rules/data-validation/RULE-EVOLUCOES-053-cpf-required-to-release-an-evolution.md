# RULE-EVOLUCOES-053 — CPF required to release an evolution

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
A user without a registered CPF cannot release ("liberar") an evolution document.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| usuario.cpf |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| ValidationError raised if invalid |  |  |

## Logic
```text
if not usuario.cpf:
    raise ValidationError(
        "Você não possui CPF cadastrado. Cadastre seu CPF para poder liberar evoluções."
    )
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_base.py` | 313-320 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-009
- Related rules: RULE-EVOLUCOES-054, RULE-EVOLUCOES-009

## Notes
Reused inside validar_assinatura (RULE-evolucao-BE-07-010) and directly inside liberar() (RULE-evolucao-BE-07-004).

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
