# RULE-MOVIMENTACAO-ADT-026 — Bed (leito) default type is manual

| Field | Value |
|---|---|
| Category | billing-administrative |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | movimentacao-adt |

## Rule
A newly created Leito defaults to tipo 'manual'; tipo may be set to 'automatica' (also 'homecare' referenced elsewhere).

## Outputs
| Name | Type | Unit |
|---|---|---|
| leito.tipo | string |  |

## Logic
```text
Leito.objects.create(setor=...).tipo == "manual"   # default
leito.tipo = "automatica"; leito.save() -> "automatica"
```

## Edge cases (as implemented)
Default applied when tipo not provided at creation.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/tests/test_leito.py | 51-55 | 8166c07e | primary |
- Merged from: RULE-ADMIN-BE-12-031
- Related rules: RULE-MOVIMENTACAO-ADT-052, RULE-MOVIMENTACAO-ADT-021

## Notes
tipo values in play across partition - 'manual', 'automatica', 'homecare' (enviar_observacao_leito branches on automatica/homecare, core/utils.py:165-168). Model definition outside partition.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
