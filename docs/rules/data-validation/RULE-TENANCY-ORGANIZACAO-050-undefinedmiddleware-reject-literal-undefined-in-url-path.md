# RULE-TENANCY-ORGANIZACAO-050 — UndefinedMiddleware — reject literal 'undefined' in URL path

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
If any path segment of the request literally equals the string 'undefined' (a classic symptom of a frontend bug sending a JS undefined value into a URL), the request is rejected with HTTP 400.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request.path | string |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| HTTP 400 response | returned when triggered |  |

## Logic
```text
IF "undefined" IN request.path.split("/"):
  RETURN JsonResponse({"errors": {"detail": "Undefined enviado na rota. Verifique seus parâmetros!"}, "status": 400, ...}, status=400)
```

## Edge cases (as implemented)
None documented.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilhas/middleware.py | 178-195 | 8166c07e | primary |

- Merged from: RULE-mw-BE-11-063
- Related rules: RULE-TENANCY-ORGANIZACAO-017, RULE-TENANCY-ORGANIZACAO-018, RULE-TENANCY-ORGANIZACAO-019, RULE-TENANCY-ORGANIZACAO-020

## Notes
Reconciliation: sibling of the Empresa/Estabelecimento/Setor/Leito tenant-resolution middlewares in the same file (trilhas/middleware.py); this one is a generic URL-hygiene guard (rejects literal 'undefined' segments) rather than a tenant-hierarchy resolver, cross-referenced via related.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
