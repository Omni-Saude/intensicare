# RULE-AUDITORIA-LOGS-002 — request_body capture (GET vs write methods, JSON fallback)

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The logged request_body is the GET querydict for GET requests, or the POST querydict otherwise; if reading either raises, it falls back to parsing request.body as JSON; if that also fails, the parse error is recorded instead of the body.

## Inputs

| name | type | unit |
|---|---|---|
| request | HttpRequest | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| request_body | dict\|json | n/a |

## Logic

```text
try:
    request_body = request.GET if request.method == "GET" else request.POST
except (SyntaxError, KeyError, Exception):   # redundant tuple, effectively "except Exception"
    try:
        request_body = json.loads(request.body.decode("UTF-8")) if request.body else {}
    except Exception as e:
        error_request_body = repr(e)
```

## Edge cases (as implemented)

Multipart/binary bodies that are neither a QueryDict-compatible method nor valid JSON end up recorded only as an error string in error_request_body, with no request_body value at all.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/tasks/log_handler.py` | 59-70 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-005`

**Related rules:**

- [RULE-AUDITORIA-LOGS-016](../billing-administrative/RULE-AUDITORIA-LOGS-016-request-response-log-capture-payload.md)
- [RULE-AUDITORIA-LOGS-003](RULE-AUDITORIA-LOGS-003-response-body-capture-json-then-raw-text-fallback.md)

## Notes

DISCREPANCY (cosmetic): 'except (SyntaxError, KeyError, Exception):' is redundant — Exception already subsumes SyntaxError and KeyError, so this is functionally identical to a bare 'except Exception:'. Recorded verbatim; does not change runtime behavior.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
