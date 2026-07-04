# RULE-MOVIMENTACAO-ADT-029 — Movimentacao queryset optionally scoped by setor, ordered by most recent update

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
MovimentacaoViewSet, MovimentacaoBaixaViewSet, and MovimentacaoNovaViewSet all share the same get_queryset pattern: if a setor__pk URL kwarg is present, filter to that sector's beds and order by data_atualizacao descending; otherwise return all Movimentacao records unfiltered.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| kwargs.setor__pk | uuid \| null |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| queryset | queryset of Movimentacao |  |

## Logic
```text
queryset = Movimentacao.objects.all()
if setor_pk:
    return queryset.filter(leito__setor=setor_pk).order_by("-data_atualizacao")
return queryset
```

## Edge cases (as implemented)
When setor_pk is absent, NO ordering is applied at all (falls back to default model ordering), unlike the setor-scoped branch which explicitly orders by -data_atualizacao.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/movimentacao.py | 36-41, 81-86, 126-131 | 8166c07e | primary |
- Merged from: RULE-movimentacao-BE-05-001
- Related rules: RULE-MOVIMENTACAO-ADT-019

## Notes
Identical code duplicated verbatim across all three Movimentacao viewsets (single rule, three call sites).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
