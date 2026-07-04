# RULE-TENANCY-ORGANIZACAO-029 — Establishment gender/alert/assisted totals branch by tipo (manual vs. other)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
get_total_generos, get_total_alertas, and get_total_assistidos each branch on instance.tipo: 'manual' establishments compute from context-supplied Movimentacao records scoped to the establishment; any other tipo delegates to Leito-level aggregate helpers (get_total_generos_e_alertas_automaticos, get_total_alertas_automaticos) scoped to setor__usuarios=request.user.

## Inputs

| Name | Type | Unit |
|---|---|---|
| instance.tipo | string enum (manual\|automatica\|homecare) |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| generos | object {M, F, N, O} |  |
| alertas | object {VERMELHO, AMARELO, NEUTRO} |  |

## Logic

```text
# get_total_generos:
if instance.tipo == "manual":
    qs = context["movimentacoes"].filter(leito__setor__estabelecimento=instance)
    qs = Movimentacao.objects.filter(pk__in=qs.distinct("pk").values_list("pk"))
    return {"M":0,"F":0,"N":0,"O":0, **dict(qs.values_list("paciente__genero").annotate(Count("paciente__genero")))}
else:
    leitos = Leito.objects.filter(setor__estabelecimento=instance, setor__usuarios=request.user, ativo=True)
    generos, _ = Leito.get_total_generos_e_alertas_automaticos(leitos)
    return generos
# get_total_alertas mirrors this with alerta_movimentacao / get_total_alertas_automaticos
```

## Edge cases (as implemented)
The 'ocupado=True' filter is commented out in both branches for the non-manual case - all active leitos regardless of occupancy contribute.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/estabelecimento.py` | 114-146, 166-194 | `8166c07e` | primary |

- Merged from: `RULE-estabelecimento-BE-05-003`
- Related rules: RULE-TENANCY-ORGANIZACAO-016, RULE-TENANCY-ORGANIZACAO-034, RULE-TENANCY-ORGANIZACAO-035

## Notes
Same duplicated pattern as RULE-setor-BE-05-008/RULE-setor-BE-05-010, but at establishment scope.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
