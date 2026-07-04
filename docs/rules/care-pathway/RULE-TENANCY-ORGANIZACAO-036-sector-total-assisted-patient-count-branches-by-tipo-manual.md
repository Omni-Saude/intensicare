# RULE-TENANCY-ORGANIZACAO-036 — Sector total assisted-patient count branches by tipo (manual/automatica/homecare)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
get_total_assistidos counts patients considered 'assistido' (attended-to) differently per sector tipo: 'manual' iterates Movimentacao records in Python calling dados_prontuario.get_assistido() per row; 'automatica' and the else-branch (homecare) both filter Leito (ocupado=True, ativo=True, setor__usuarios=request.user) then delegate to Leito.get_total_assistidos_automatica or Leito.get_total_assistidos_homecare respectively.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| instance.tipo | string enum |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| total_assistidos | integer |  |

## Logic
```text
if instance.tipo == "manual":
    qs = context.get("movimentacoes", []).filter(leito__setor=instance)
    qs = Movimentacao.objects.filter(pk__in=qs.distinct("pk").values_list("pk"))
    total = sum(1 for m in qs if m.dados_prontuario.get_assistido())
elif instance.tipo == "automatica":
    leitos = Leito.objects.filter(ocupado=True, setor=instance, setor__usuarios=request.user, ativo=True)
    total = Leito.get_total_assistidos_automatica(leitos)
else:
    leitos = Leito.objects.filter(ocupado=True, setor=instance, setor__usuarios=request.user, ativo=True)
    total = Leito.get_total_assistidos_homecare(leitos)
return total
```

## Edge cases (as implemented)
The manual branch does a Python-level loop/count (not a DB aggregate), which could be slow for large querysets but is functionally straightforward.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/setor.py | 238-268 | 8166c07e | primary |

- Merged from: RULE-setor-BE-05-011
- Related rules: RULE-TENANCY-ORGANIZACAO-016, RULE-TENANCY-ORGANIZACAO-030

## Notes
Structurally identical to EstabelecimentoStatusSerializer.get_total_assistidos (RULE-estabelecimento-BE-05-006).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
