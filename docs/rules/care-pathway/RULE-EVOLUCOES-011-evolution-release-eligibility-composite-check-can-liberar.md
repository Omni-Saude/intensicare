# RULE-EVOLUCOES-011 — Evolution release eligibility composite check (can_liberar)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
A helper predicate that determines whether an evolution can be released, requiring simultaneously that the tipo is registered, the liberar flag is set, the user has a cpf, and an nr_atendimento (encounter number) is present.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| liberar |  |  |  |
| tipo |  |  |  |
| cpf |  |  |  |
| nr_atendimento |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| can_liberar |  |  |

## Logic
```text
def can_liberar(liberar, tipo, cpf, nr_atendimento):
    return all([
        tipo in get_evolucoes_para_liberar().keys(),
        liberar,
        cpf,
        nr_atendimento,
    ])
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/formulario_base.py` | 379-387 | `8166c07e` | primary |
- Merged from: RULE-evolucao-BE-07-012
- Related rules: RULE-EVOLUCOES-009, RULE-EVOLUCOES-010

## Notes
This method is not invoked anywhere else within this partition's files; it may be consumed by a view/serializer outside the serializers/ directory (out of scope). Marked AMBIGUOUS only regarding call-site usage, not the logic itself.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
