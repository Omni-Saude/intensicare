# RULE-TENANCY-ORGANIZACAO-020 — LeitoMiddleware — path-based leito resolution (no cross-tenant check)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
Scans for a path segment literally 'ocupacoes'; takes the next segment as the leito pk and attaches the Leito instance to request.leito. Unlike Empresa/Estabelecimento/Setor middlewares, this one performs NO cross-tenant consistency check against request.empresa/estabelecimento/setor.

## Inputs

| Name | Type | Unit |
|---|---|---|
| request.path | string |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| request.leito | Leito instance or None |  |

## Logic

```text
request.leito = None
FOR index, name IN enumerate(path_splitted):
  IF name == "ocupacoes":
    TRY:
      pk = path_splitted[index + 1]
      request.leito = Leito.objects.get(pk=pk)
      BREAK
    EXCEPT Exception: pass
```

## Edge cases (as implemented)
No cross-check against request.empresa/estabelecimento/setor, and no prefetch_related (unlike the other three middlewares), suggesting this middleware may be less complete/mature than the others.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilhas/middleware.py` | 157-175 | `8166c07e` | primary |

- Merged from: `RULE-mw-BE-11-062`
- Related rules: RULE-TENANCY-ORGANIZACAO-017, RULE-TENANCY-ORGANIZACAO-018, RULE-TENANCY-ORGANIZACAO-019

## Notes
AMBIGUOUS whether the missing cross-tenant check is intentional (e.g. 'ocupacoes' routes are always nested under an already-validated setor path) or an inconsistency vs the other three middlewares; flag for verifier.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
