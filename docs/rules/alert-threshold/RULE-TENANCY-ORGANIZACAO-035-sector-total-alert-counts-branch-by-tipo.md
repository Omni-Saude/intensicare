# RULE-TENANCY-ORGANIZACAO-035 — Sector total alert counts branch by tipo

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
get_total_alertas computes VERMELHO/AMARELO/NEUTRO counts from Movimentacao (manual) or from Leito.get_total_alertas_automaticos (automatica/homecare, scoped to setor__usuarios=request.user, ativo=True; ocupado filter commented out).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| instance.tipo | string enum |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| alertas | object {VERMELHO, AMARELO, NEUTRO} |  |

## Logic
```text
if instance.tipo == "manual":
    qs = context.get("movimentacoes", []).filter(leito__setor=instance)
    qs = Movimentacao.objects.filter(pk__in=qs.distinct("pk").values_list("pk"))
    return {"VERMELHO":0,"AMARELO":0,"NEUTRO":0, **dict(qs.values_list("alerta_movimentacao").annotate(Count("alerta_movimentacao")))}
else:
    leitos = Leito.objects.filter(setor=instance, setor__usuarios=request.user, ativo=True)
    return Leito.get_total_alertas_automaticos(leitos)
```

## Edge cases (as implemented)
Same commented-out ocupado=True filter as RULE-setor-BE-05-008 - all active leitos count, not just occupied ones, for automatica/homecare.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/setor.py | 208-236 | 8166c07e | primary |

- Merged from: RULE-setor-BE-05-010
- Related rules: RULE-TENANCY-ORGANIZACAO-016, RULE-TENANCY-ORGANIZACAO-011, RULE-TENANCY-ORGANIZACAO-029

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
