# RULE-AUDITORIA-LOGS-003 — response_body capture (JSON then raw-text fallback)

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
The logged response_body is the JSON-decoded response content if parseable; otherwise the raw utf-8-decoded content string; otherwise a recorded parse error. Empty response content yields an empty dict in both success branches.

## Inputs

| name | type | unit |
|---|---|---|
| response | HttpResponse | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| response_body | dict\|str | n/a |

## Logic

```text
try:
    response_body = json.loads(response.content.decode("UTF-8")) if response.content else {}
except (SyntaxError, KeyError, Exception):
    try:
        response_body = response.content.decode("UTF-8") if response.content else {}
    except Exception as e:
        error_response_log = repr(e)
```

## Edge cases (as implemented)

Binary (non-utf-8) response bodies (e.g. PDFs, images) fail both branches and are logged only as an error string, never storing the actual bytes.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/tasks/log_handler.py` | 101-111 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-006`

**Related rules:**

- [RULE-AUDITORIA-LOGS-016](../billing-administrative/RULE-AUDITORIA-LOGS-016-request-response-log-capture-payload.md)
- [RULE-AUDITORIA-LOGS-002](RULE-AUDITORIA-LOGS-002-request-body-capture-get-vs-write-methods-json-fallback.md)

## Notes

Same redundant except-tuple pattern as RULE-005; noted once, applies here too.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
