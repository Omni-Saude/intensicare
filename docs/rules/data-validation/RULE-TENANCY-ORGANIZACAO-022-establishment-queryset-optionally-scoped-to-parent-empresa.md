# RULE-TENANCY-ORGANIZACAO-022 — Establishment queryset optionally scoped to parent empresa

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
EstabelecimentoViewSet.get_queryset filters to the empresa__pk URL kwarg when present (nested route), else returns all establishments.

## Inputs

| Name | Type | Unit |
|---|---|---|
| kwargs.empresa__pk | uuid \| null |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| queryset | queryset of Estabelecimento |  |

## Logic

```text
queryset = Estabelecimento.objects.all()
if kwargs.get("empresa__pk"):
    queryset = queryset.filter(empresa=kwargs["empresa__pk"])
return queryset
```

## Edge cases (as implemented)
No scoping by request.user at all (contrast with EstabelecimentoStatusSerializer's methods which do scope by setor__usuarios=user) - a non-nested request against this viewset returns ALL establishments across ALL companies.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/estabelecimento.py` | 34-39 | `8166c07e` | primary |

- Merged from: `RULE-estabelecimento-BE-05-008`
- Related rules: RULE-TENANCY-ORGANIZACAO-017, RULE-TENANCY-ORGANIZACAO-021

## Notes
Flagged for a verifier: whether this is intentional (e.g., permission_classes/TrilhasPermissaoMixin restricts access elsewhere) or a genuine multi-tenant gap depends on code outside this partition. | Reconciliation: cross-referenced with the tenant-resolution middleware chain and with setor-BE-05-017 (the analogous dual-scoping queryset for Setor); this establishment queryset only conditionally scopes by empresa (nested-route kwarg) and has no request.user scoping at all — flagged by Phase 1 as a possible multi-tenant gap depending on permission enforcement elsewhere.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
