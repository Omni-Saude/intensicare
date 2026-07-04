# RULE-TENANCY-ORGANIZACAO-034 — Sector patient/gender totals branch by tipo (manual vs. automatic/homecare)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
get_total_generos computes gender counts differently depending on instance.tipo: for 'manual' sectors, it counts genders from Movimentacao records supplied via context['movimentacoes'] (already scoped upstream) filtered to this setor; for any other tipo ('automatica'/'homecare'), it queries Leito directly (ativo=True, setor=instance, setor__usuarios=request.user) and delegates to Leito.get_total_generos_e_alertas_automaticos.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| instance.tipo | string enum (manual\|automatica\|homecare) |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| generos | object {M, F, N, O} |  |

## Logic
```text
if instance.tipo == "manual":
    qs = context.get("movimentacoes", []).filter(leito__setor=instance)
    qs = Movimentacao.objects.filter(pk__in=qs.distinct("pk").values_list("pk"))
    return {"M":0,"F":0,"N":0,"O":0, **dict(qs.values_list("paciente__genero").annotate(Count("paciente__genero")))}
else:
    leitos = Leito.objects.filter(setor=instance, setor__usuarios=request.user, ativo=True)  # ocupado filter commented out
    generos, _ = Leito.get_total_generos_e_alertas_automaticos(leitos)
    return generos
```

## Edge cases (as implemented)
The 'ocupado=True' filter is present in source but commented out for the non-manual branch, so ALL active leitos (occupied or not) in the sector contribute to the gender count for automatica/homecare sectors.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/serializers/setor.py | 158-185 | 8166c07e | primary |

- Merged from: RULE-setor-BE-05-008
- Related rules: RULE-TENANCY-ORGANIZACAO-016, RULE-TENANCY-ORGANIZACAO-013, RULE-TENANCY-ORGANIZACAO-029

## Notes
Structurally identical to EstabelecimentoStatusSerializer.get_total_generos (RULE-estabelecimento-BE-05-003), duplicated code across the two files.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
