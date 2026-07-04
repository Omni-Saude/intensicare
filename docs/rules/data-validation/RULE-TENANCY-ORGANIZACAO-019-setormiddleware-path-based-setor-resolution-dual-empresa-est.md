# RULE-TENANCY-ORGANIZACAO-019 — SetorMiddleware — path-based setor resolution + dual empresa/estabelecimento cross-check

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
Same URL-segment convention for 'setores'; validates the resolved setor's estabelecimento against BOTH request.empresa (if set) and request.estabelecimento (if set); rejects with HTTP 400 if either mismatches.

## Inputs

| Name | Type | Unit |
|---|---|---|
| request.path | string |  |
| request.empresa, request.estabelecimento | instances or None |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| request.setor | Setor instance or None |  |
| HTTP 400 response | returned early on tenant mismatch |  |

## Logic

```text
request.setor = None
FOR index, name IN enumerate(path_splitted):
  IF name == "setores":
    TRY:
      pk = path_splitted[index + 1]
      setor = Setor.objects.select_related("estabelecimento","estabelecimento__empresa").prefetch_related(...).get(pk=pk)
      request.setor = setor
      IF (request.empresa AND request.empresa != setor.estabelecimento.empresa) OR \
         (request.estabelecimento AND request.estabelecimento != setor.estabelecimento):
        RETURN JsonResponse({"errors": {"detail": "Este setor não pertence à este estabelecimento ou empresa"}, ...}, status=400)
      BREAK
    EXCEPT Exception: pass
```

## Edge cases (as implemented)
Same MIDDLEWARE-ordering caveat as EstabelecimentoMiddleware: cross-checks are only as strong as whichever of empresa/estabelecimento happened to be resolved earlier from the same URL.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilhas/middleware.py` | 97-154 | `8166c07e` | primary |

- Merged from: `RULE-mw-BE-11-061`
- Related rules: RULE-TENANCY-ORGANIZACAO-017, RULE-TENANCY-ORGANIZACAO-018, RULE-TENANCY-ORGANIZACAO-021

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
