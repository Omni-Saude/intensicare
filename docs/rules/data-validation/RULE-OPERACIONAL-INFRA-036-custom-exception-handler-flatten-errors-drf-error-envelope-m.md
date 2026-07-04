# RULE-OPERACIONAL-INFRA-036 — custom_exception_handler / flatten_errors — DRF error envelope mapping with a Python 3.10+ incompatible collections reference

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | data-validation |
| Type | decision-tree |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Maps Django/DRF exceptions to a standard response envelope: Http404 -> NotFound, PermissionDenied -> PermissionDenied, IntegrityError -> ValidationError('Erro de integridade! Verifique os dados enviados.'). Any resulting APIException response is rewrapped into {errors: <flattened>, status: <code>, exception: str(exc)}. flatten_errors recursively flattens one level of nested mapping values using `isinstance(v, collections.MutableMapping)` — this attribute was removed from the `collections` module in Python 3.10 (moved to collections.abc in 3.3, removed from `collections` entirely in 3.10), so this line raises AttributeError on Python 3.10+ despite functioning under the project's pinned Python 3.9 (per Dockerfile: python:3.9-slim-bullseye).

## Inputs

| name | type | unit |
|---|---|---|
| exc | Exception instance |  |
| context | DRF exception context dict |  |

## Outputs

| name | type | unit |
|---|---|---|
| response | DRF Response with {errors, status, exception} or None (falls through to 500) |  |

## Logic

```text
IF isinstance(exc, Http404): exc = exceptions.NotFound()
ELIF isinstance(exc, PermissionDenied): exc = exceptions.PermissionDenied()
ELIF isinstance(exc, IntegrityError): exc = exceptions.ValidationError("Erro de integridade! Verifique os dados enviados.")
IF isinstance(exc, exceptions.APIException):
  set_rollback()  # rolls back atomic DB transactions if in one
  response = Response(data, status=exc.status_code, headers=...)
response2 = custom_exception_handler(exc, context) wraps response.data into:
  {"errors": flatten_errors(data), "status": response.status_code, "exception": str(exc)}
flatten_errors(d, key=""):
  FOR k, v IN d.items():
    IF isinstance(v, collections.MutableMapping): items.extend(flatten_errors(v, k).items())   # AttributeError on Python >= 3.10
    ELSE: items.append((k, v))
  RETURN dict(items)
```

## Edge cases (as implemented)

flatten_errors only flattens ONE level of recursion correctly for dict values that are themselves plain dicts wrapped via the recursive call, but keys from nested dicts are not prefixed/namespaced — a naming collision between a nested key and a top-level key would silently overwrite one entry in the final flat dict (Python dict() from a list of tuples keeps the LAST occurrence of a repeated key).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/exceptions.py` | 17-83 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-err-BE-11-070`

**Related rules:** _none_

## Notes

DISCREPANCY/technical-debt flag for the rebuild: `collections.MutableMapping` must become `collections.abc.MutableMapping` (or an isinstance check against dict) on any Python >= 3.10 runtime, otherwise every API error response containing nested validation errors will 500 instead of returning the intended flattened error body.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
