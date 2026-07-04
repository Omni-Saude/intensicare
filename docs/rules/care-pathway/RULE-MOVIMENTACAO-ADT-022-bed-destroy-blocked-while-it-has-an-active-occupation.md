# RULE-MOVIMENTACAO-ADT-022 — Bed destroy() blocked while it has an active occupation

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
LeitoViewSet.destroy() prevents deletion of a bed that has a Movimentacao with atual=True.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| leito.movimentacoes.atual | boolean |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| eligible_for_deletion | boolean |  |

## Logic
```text
leito = Leito.objects.prefetch_related("movimentacoes").get(pk=kwargs["pk"])
if leito.movimentacoes.filter(atual=True):
    raise ValidationError({"erro": "Voce nao pode apagr um leito com ocupacoes!"})
return super().destroy(request, *args, **kwargs)
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/leito.py | 37-47 | 8166c07e | primary |
- Merged from: RULE-leito-BE-05-009
- Related rules: RULE-MOVIMENTACAO-ADT-031

## Notes
Error message contains a verbatim typo ('apagr' instead of 'apagar'), reproduced exactly as implemented. This message text is reused (copy-pasted) for the SetorViewSet.destroy() guard where it incorrectly refers to a leito while deleting a setor.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
