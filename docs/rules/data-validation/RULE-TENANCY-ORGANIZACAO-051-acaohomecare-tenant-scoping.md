# RULE-TENANCY-ORGANIZACAO-051 — AcaoHomecare tenant scoping

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
The AcoesHomecare (homecare action/audit log) list is restricted to records whose sector's establishment belongs to the requesting user's company (empresa) - multi-tenant isolation.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request.empresa | Empresa (FK) |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| filtered queryset | queryset |  |

## Logic
```text
AcaoHomecare.objects.filter(setor__estabelecimento__empresa == request.empresa)
```

## Edge cases (as implemented)
Assumes request.empresa is always set (populated by out-of-partition middleware); no fallback.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/views/acao_homecare.py | 17-20 | 8166c07e | primary |

- Merged from: RULE-tenant-BE-08-004
- Related rules: RULE-TENANCY-ORGANIZACAO-017

## Notes
Only List is exposed (GenericViewSet + ListModelMixin); no create/update/destroy from this endpoint. | Reconciliation: depends on request.empresa having been populated by EmpresaMiddleware (mw-BE-11-059, cross-referenced); this rule is the tenant-isolation filter applied at a specific endpoint (AcaoHomecare list) rather than the resolution mechanism itself.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
