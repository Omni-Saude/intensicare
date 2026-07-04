# RULE-TENANCY-ORGANIZACAO-021 — Sector queryset dual (non-exclusive) scoping by empresa and estabelecimento

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
SetorViewSet.get_queryset (and identically, SetorUsuarioViewSet.get_queryset) applies BOTH an empresa filter and an estabelecimento filter independently (if each is present on the request) rather than an either/or priority chain - unlike the setor>estabelecimento>empresa exclusive pattern used elsewhere (e.g. GrupoAcesso, permissions).

## Inputs

| Name | Type | Unit |
|---|---|---|
| request.empresa | object\|null |  |
| request.estabelecimento | object\|null |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| queryset | queryset of Setor |  |

## Logic

```text
queryset = Setor.objects.all()
if request.empresa:
    queryset = queryset.filter(estabelecimento__empresa=request.empresa)
if request.estabelecimento:
    queryset = queryset.filter(estabelecimento=request.estabelecimento)
return queryset
```

## Edge cases (as implemented)
Both conditions are plain 'if' (not 'elif'), so when both request.empresa and request.estabelecimento are present, both filters apply cumulatively (AND), which is consistent as long as estabelecimento actually belongs to empresa.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/setor.py` | 42-48, 191-197 | `8166c07e` | primary |

- Merged from: `RULE-setor-BE-05-017`
- Related rules: RULE-TENANCY-ORGANIZACAO-017, RULE-TENANCY-ORGANIZACAO-018, RULE-TENANCY-ORGANIZACAO-019, RULE-TENANCY-ORGANIZACAO-022

## Notes
Duplicated verbatim between SetorViewSet.get_queryset and SetorUsuarioViewSet.get_queryset. | Reconciliation: cross-referenced with the Empresa/Estabelecimento/Setor tenant-resolution middlewares (which populate request.empresa/request.estabelecimento consumed here) — not a duplicate, this is the queryset-filtering consumer of those middleware-attached objects.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
