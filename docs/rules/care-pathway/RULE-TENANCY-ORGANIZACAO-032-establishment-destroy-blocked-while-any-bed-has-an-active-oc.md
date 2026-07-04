# RULE-TENANCY-ORGANIZACAO-032 — Establishment destroy() blocked while any bed has an active occupation

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
EstabelecimentoViewSet.destroy() prevents deletion if any of the establishment's sectors has a bed with an active (atual=True) Movimentacao.

## Inputs

| Name | Type | Unit |
|---|---|---|
| estabelecimento.setores.leitos.movimentacoes.atual | boolean |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| eligible_for_deletion | boolean |  |

## Logic

```text
estabelecimento = Estabelecimento.objects.prefetch_related("setores","setores__leitos","setores__leitos__movimentacoes").get(pk=kwargs["pk"])
if estabelecimento.setores.filter(leitos__movimentacoes__atual=True):
    raise ValidationError({"erro": "Você não pode apagar um estabelecimento com leitos ocupados!"})
return super().destroy(request, *args, **kwargs)
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/estabelecimento.py` | 41-53 | `8166c07e` | primary |

- Merged from: `RULE-estabelecimento-BE-05-009`
- Related rules: RULE-TENANCY-ORGANIZACAO-037

## Notes
Unlike the Setor/Leito deletion guards (RULE-setor-BE-05-014, RULE-leito-BE-05-002), this error message correctly names 'estabelecimento' rather than 'leito'. | Reconciliation: cross-referenced with setor-BE-05-014, the analogous deletion guard at sector scope, which has a DISCREPANCY status due to an incorrect ('leito') error message; this establishment-level guard's error message correctly names the entity being deleted.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
