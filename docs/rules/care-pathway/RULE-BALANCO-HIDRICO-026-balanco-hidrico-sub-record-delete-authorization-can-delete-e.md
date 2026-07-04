# RULE-BALANCO-HIDRICO-026 — Balanco-hidrico sub-record delete authorization (can_delete) - Entrada/Saida/SinaisVitais

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
A fluid-intake record can be deleted only if the requesting user holds the "can_delete_balanco_hidrico" company-scoped permission OR is the original author, AND the record has not already been soft-deleted.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| user permissions | get_permissoes_empresa | — | — |
| instance.preenchido_por | — | — | — |
| instance.deletado_em | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| can_delete | — | — |

## Logic
```text
can_delete = (
    "can_delete_balanco_hidrico" in get_permissoes_empresa(user, request.empresa)
    OR instance.preenchido_por == user
) AND NOT bool(instance.deletado_em)
```

## Edge cases (as implemented)
Raises a ValidationError({"empresa_obrigatoria": ...}) if request.empresa is missing, via an explicit try/except — this graceful handling is NOT present in the equivalent methods on Saida/SinaisVitais (see RULE-balanco-BE-07-012 / RULE-balanco-BE-07-014 notes), where a missing empresa would instead raise an unhandled AttributeError.

## Divergence
Core predicate is identical across all three serializers: ('can_delete_balanco_hidrico' in get_permissoes_empresa(user, request.empresa) OR instance.preenchido_por == user) AND NOT bool(instance.deletado_em). They DIVERGE on missing-empresa handling: Entrada.get_can_delete (entradas.py:144-157) wraps the request.empresa access in try/except and raises ValidationError({'empresa_obrigatoria': ...}); Saida.get_can_delete (saidas.py:152-158) and SinaisVitais.get_can_delete (sinais_vitais.py:181-187) access request.empresa directly with no guard, so a missing/None empresa surfaces an unhandled AttributeError instead of the clear validation error.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/serializers/entradas.py | 144-157 | 8166c07e | primary |
| ahlabs-trilhas | trilha_homecare/api/v1/serializers/saidas.py | 152-158 | 8166c07e | duplicate |
| ahlabs-trilhas | trilha_homecare/api/v1/serializers/sinais_vitais.py | 181-187 | 8166c07e | duplicate |
- Merged from: RULE-balanco-BE-07-006, RULE-balanco-BE-07-013, RULE-balanco-BE-07-014
- Related rules: RULE-BALANCO-HIDRICO-033, RULE-BALANCO-HIDRICO-034, RULE-BALANCO-HIDRICO-051

## Notes
Permission string "can_delete_balanco_hidrico" is shared with Saida and SinaisVitais delete checks.
Permission string 'can_delete_balanco_hidrico' is shared across all three record types (and consumed by the frontend as record.can_delete, RULE-BALANCO-HIDRICO-034/045).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
