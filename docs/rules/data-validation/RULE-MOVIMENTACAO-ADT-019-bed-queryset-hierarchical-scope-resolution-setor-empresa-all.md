# RULE-MOVIMENTACAO-ADT-019 — Bed queryset hierarchical scope resolution (setor > empresa > all)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
LeitoViewSet.get_queryset resolves scope in priority order: setor (if setor__pk present) > empresa (if empresa__pk present, via setor__estabelecimento__empresa) > all beds.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| kwargs.setor__pk | uuid \| null |  |  |
| kwargs.empresa__pk | uuid \| null |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| queryset | queryset of Leito |  |

## Logic
```text
queryset = Leito.objects.all()
if setor_pk:
    return queryset.filter(setor=setor_pk)
elif empresa_pk:
    return queryset.filter(setor__estabelecimento__empresa=empresa_pk)
return queryset
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/leito.py | 27-35 | 8166c07e | primary |
- Merged from: RULE-leito-BE-05-008
- Related rules: RULE-MOVIMENTACAO-ADT-029

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
