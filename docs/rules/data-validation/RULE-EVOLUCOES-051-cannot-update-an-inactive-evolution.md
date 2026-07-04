# RULE-EVOLUCOES-051 — Cannot update an inactive evolution

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | evolucoes |

## Rule
An evolution document whose status is "inativo" cannot be updated at all.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.status |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| ValidationError raised if invalid |  |  |

## Logic
```text
if instance.status == "inativo":
    raise ValidationError("Esta evolução já está inativa! Não é possível atualizá-la!")
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_base.py` | 303-311 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-007
- Related rules: RULE-EVOLUCOES-027, RULE-EVOLUCOES-052, RULE-EVOLUCOES-055

---
*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
