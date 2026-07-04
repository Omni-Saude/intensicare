# RULE-TENANCY-ORGANIZACAO-037 — Sector destroy() blocked while any bed has an active occupation

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | eligibility |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
SetorViewSet.destroy() prevents deletion if ANY of the sector's beds has a Movimentacao with atual=True; the error message text refers to 'leito' (bed) rather than 'setor' (sector), a wording mismatch for the entity actually being deleted.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| setor.leitos.movimentacoes.atual | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| eligible_for_deletion | boolean |  |

## Logic
```text
setor = Setor.objects.prefetch_related("leitos", "leitos__movimentacoes").get(pk=kwargs["pk"])
if setor.leitos.filter(movimentacoes__atual=True):
    raise ValidationError({"erro": "Você não pode apagar um leito com ocupações!"})
return super().destroy(request, *args, **kwargs)
```

## Edge cases (as implemented)
Uses queryset truthiness (implicit .exists()-like check via __bool__) rather than an explicit .exists() call - functionally equivalent but less idiomatic.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/setor.py | 50-61 | 8166c07e | primary |

- Merged from: RULE-setor-BE-05-014
- Related rules: RULE-TENANCY-ORGANIZACAO-032

## Notes
Identical (copy-pasted) error message text 'apagar um leito com ocupações' is used verbatim in LeitoViewSet.destroy() (RULE-leito-BE-05-002) - here it is reused for a Setor deletion, which is the wording mismatch. | Reconciliation: cross-referenced with estabelecimento-BE-05-009, the analogous deletion guard at establishment scope, whose error message correctly names 'estabelecimento'; this sector-level guard's error message incorrectly says 'leito' (bed) instead of 'setor', which is the basis for this rule's DISCREPANCY status. Not merged (different entity/endpoint), but the wording mismatch is preserved verbatim per clinical-safety instructions (never correct legacy logic/text).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
