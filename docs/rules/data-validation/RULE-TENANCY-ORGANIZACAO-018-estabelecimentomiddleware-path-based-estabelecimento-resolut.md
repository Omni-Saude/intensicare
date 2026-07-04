# RULE-TENANCY-ORGANIZACAO-018 — EstabelecimentoMiddleware — path-based estabelecimento resolution + empresa cross-check

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
Same URL-segment convention as EmpresaMiddleware but for 'estabelecimentos'; additionally validates that if request.empresa is already set (from EmpresaMiddleware running earlier in MIDDLEWARE order), it must equal the resolved estabelecimento.empresa, otherwise the request is rejected with HTTP 400.

## Inputs

| Name | Type | Unit |
|---|---|---|
| request.path | string |  |
| request.empresa | Empresa instance or None (set by EmpresaMiddleware) |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| request.estabelecimento | Estabelecimento instance or None |  |
| HTTP 400 response | returned early on tenant mismatch |  |

## Logic

```text
request.estabelecimento = None
FOR index, name IN enumerate(path_splitted):
  IF name == "estabelecimentos":
    TRY:
      pk = path_splitted[index + 1]
      estabelecimento = Estabelecimento.objects.select_related("empresa").prefetch_related(...).get(pk=pk)
      request.estabelecimento = estabelecimento
      IF request.empresa AND request.empresa != estabelecimento.empresa:
        RETURN JsonResponse({"errors": {"detail": "Este estabelecimento não pertence à esta empresa"}, ...}, status=400)
      BREAK
    EXCEPT Exception: pass
```

## Edge cases (as implemented)
Cross-check only applies if request.empresa was already resolved (depends on MIDDLEWARE ordering: EmpresaMiddleware runs before EstabelecimentoMiddleware per settings.py MIDDLEWARE list) — a request path containing only '/estabelecimentos/<pk>/' without an '/empresas/<pk>/' segment performs no cross-tenant validation at all.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilhas/middleware.py` | 49-94 | `8166c07e` | primary |

- Merged from: `RULE-mw-BE-11-060`
- Related rules: RULE-TENANCY-ORGANIZACAO-017, RULE-TENANCY-ORGANIZACAO-019, RULE-TENANCY-ORGANIZACAO-020

## Notes
Duplicates the business intent of verificar_setor_da_empresa (RULE-util-BE-11-044) at the establishment level rather than the setor level.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
