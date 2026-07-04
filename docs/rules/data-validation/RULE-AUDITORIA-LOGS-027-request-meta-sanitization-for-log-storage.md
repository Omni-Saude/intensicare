# RULE-AUDITORIA-LOGS-027 — request.META sanitization for log storage

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Before storing request.META as the log's 'meta' JSON field, three WSGI-internal keys are dropped, and only values of type bytes/list/tuple/bool/dict/str are kept; bytes values are utf-8 decoded. Any other value type (e.g. file-like objects, callables) is silently discarded from 'meta'.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| request.META | dict | n/a | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| meta | dict | n/a |

## Logic

```text
buff = dict(request.META)
buff.pop("werkzeug.request", None); buff.pop("wsgi.input", None)
buff.pop("wsgi.errors", None); buff.pop("wsgi.file_wrapper", None)
for key, value in buff.items():
    if isinstance(value, bytes): meta[key] = value.decode("utf-8")
    elif isinstance(value, (list, tuple, bool, dict, str)): meta[key] = value
    # else: silently dropped
# on any exception: meta = {"meta_log_err": repr(e)}
```

## Edge cases (as implemented)

If decoding meta entirely fails, the whole meta dict is replaced by a single error marker key, losing all META data for that request.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/tasks/log_handler.py` | 19-33 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-002`

**Related rules:**

- [RULE-AUDITORIA-LOGS-016](../billing-administrative/RULE-AUDITORIA-LOGS-016-request-response-log-capture-payload.md)

## Notes

Pure predicate for what is retained in the audit trail's meta field.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
