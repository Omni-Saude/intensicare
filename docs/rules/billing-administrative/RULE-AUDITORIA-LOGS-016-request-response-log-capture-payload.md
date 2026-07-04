# RULE-AUDITORIA-LOGS-016 — Request/response log-capture payload

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | billing-administrative |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
On every HTTP response, an audit-log payload is assembled from the request/response (user, path, content_type, method, display name, sanitized meta, headers, response status code, client IP and public/private flag) and handed off asynchronously for persistence. Each enrichment step is independently wrapped in try/except so a failure in one field does not prevent the others from being logged.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| request | HttpRequest | n/a | n/a |
| response | HttpResponse | n/a | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| payload_log | dict | n/a |

## Logic

```text
payload_log = {"user": str(request.user.pk) if request.user.pk else ""}
try:
    payload_log += {path, content_type, method,
                     nome = request.user.nome if isinstance(request.user, Usuario) else "",
                     meta, headers=dict(request.headers),
                     response_status_code=int(response.status_code),
                     ip, ip_publico}
except Exception as e:
    payload_log["error_request_log"] = repr(e)
... (see RULE-005/006/007/009 for the sub-steps)
salvar_log.apply_async(args=(payload_log,))   # async persistence, see RULE-003
```

## Edge cases (as implemented)

Any exception during the main enrichment block is swallowed and recorded as payload_log['error_request_log'] instead of aborting the log; the log is still dispatched with whatever partial payload was built.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/tasks/log_handler.py` | 18-113 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-001`

**Related rules:**

- [RULE-AUDITORIA-LOGS-017](RULE-AUDITORIA-LOGS-017-asynchronous-log-persistence-dispatch.md)
- [RULE-AUDITORIA-LOGS-018](RULE-AUDITORIA-LOGS-018-unconditional-what-gets-logged-predicate-every-response.md)
- [RULE-AUDITORIA-LOGS-002](../data-validation/RULE-AUDITORIA-LOGS-002-request-body-capture-get-vs-write-methods-json-fallback.md)
- [RULE-AUDITORIA-LOGS-003](../data-validation/RULE-AUDITORIA-LOGS-003-response-body-capture-json-then-raw-text-fallback.md)
- [RULE-AUDITORIA-LOGS-004](../data-validation/RULE-AUDITORIA-LOGS-004-device-classification-from-user-agent-dispositivo.md)
- [RULE-AUDITORIA-LOGS-019](RULE-AUDITORIA-LOGS-019-client-ip-and-public-private-classification.md)

## Notes

This is the central audit-logging capture rule for the whole platform (every request/response, see RULE-004 for the unconditional trigger).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
