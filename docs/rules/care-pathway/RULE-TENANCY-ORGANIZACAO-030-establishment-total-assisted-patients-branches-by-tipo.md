# RULE-TENANCY-ORGANIZACAO-030 — Establishment total assisted patients branches by tipo

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
get_total_assistidos: 'manual' counts via Python loop over Movimentacao.dados_prontuario.get_assistido(); 'automatica' filters leitos (ocupado=True, ativo=True, setor.usuarios=user) then Leito.get_total_assistidos_automatica; any other tipo (homecare) uses the same leito filter but Leito.get_total_assistidos_homecare.

## Inputs

| Name | Type | Unit |
|---|---|---|
| instance.tipo | string enum |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| total_assistidos | integer |  |

## Logic

```text
if instance.tipo == "manual":
    total = sum(1 for m in movimentacoes_qs if m.dados_prontuario.get_assistido())
elif instance.tipo == "automatica":
    leitos = Leito.objects.filter(ocupado=True, setor__estabelecimento=instance, setor__usuarios=request.user, ativo=True)
    total = Leito.get_total_assistidos_automatica(leitos)
else:
    leitos = Leito.objects.filter(ocupado=True, setor__estabelecimento=instance, setor__usuarios=request.user, ativo=True)
    total = Leito.get_total_assistidos_homecare(leitos)
return total
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/estabelecimento.py` | 196-227 | `8166c07e` | primary |

- Merged from: `RULE-estabelecimento-BE-05-005`
- Related rules: RULE-TENANCY-ORGANIZACAO-016, RULE-TENANCY-ORGANIZACAO-036

## Notes
A leftover TODO comment ('adicionar o total de assistidos dos leitos homecare') suggests homecare handling may have been considered incomplete at some point, though the else-branch does invoke get_total_assistidos_homecare.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
