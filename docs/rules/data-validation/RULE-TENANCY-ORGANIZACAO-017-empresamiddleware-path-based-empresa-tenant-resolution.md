# RULE-TENANCY-ORGANIZACAO-017 — EmpresaMiddleware — path-based empresa (tenant) resolution

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
Scans the request path's segments; when a segment literally equals 'empresas', treats the NEXT segment as the empresa pk, looks it up (with related prefetching) and attaches it to request.empresa. Any lookup failure (bad pk, does-not-exist, etc.) is silently swallowed (bare except: pass), leaving request.empresa as None.

## Inputs

| Name | Type | Unit |
|---|---|---|
| request.path | string |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| request.empresa | Empresa instance or None |  |

## Logic

```text
request.empresa = None
FOR index, name IN enumerate(request.path.split("/")):
  IF name == "empresas":
    TRY:
      pk = path_splitted[index + 1]
      request.empresa = Empresa.objects.prefetch_related(
        "grupos_acessos","usuarios","grupos_acessos__grupo","grupos_acessos__grupo__permissions"
      ).get(pk=pk)
      BREAK
    EXCEPT Exception: pass
```

## Edge cases (as implemented)
Any exception (malformed UUID, DoesNotExist, IndexError if 'empresas' is the last path segment) is caught by a bare `except Exception: pass`, silently leaving request.empresa unset with no error surfaced.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilhas/middleware.py` | 18-46 | `8166c07e` | primary |

- Merged from: `RULE-mw-BE-11-059`
- Related rules: RULE-TENANCY-ORGANIZACAO-018, RULE-TENANCY-ORGANIZACAO-019, RULE-TENANCY-ORGANIZACAO-020, RULE-TENANCY-ORGANIZACAO-051

## Notes
First of a chain of 4 tenant-hierarchy-resolving middlewares (Empresa -> Estabelecimento -> Setor -> Leito) that all rely on this exact URL-segment-name-then-next-segment convention. | Reconciliation: first of a 4-middleware tenant-resolution chain (Empresa->Estabelecimento->Setor->Leito/ocupacoes) plus the sibling UndefinedMiddleware (mw-BE-11-063) in the same file; kept as 5 separate rules (each resolves a different path segment / entity and has distinct cross-check behavior) rather than merged, cross-referenced via related.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
