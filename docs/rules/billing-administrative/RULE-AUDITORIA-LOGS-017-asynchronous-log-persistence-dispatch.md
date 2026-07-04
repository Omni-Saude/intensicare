# RULE-AUDITORIA-LOGS-017 — Asynchronous log persistence dispatch

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
Log persistence is never done inline in the request/response cycle; log_handler always dispatches the assembled payload to the salvar_log Celery task via apply_async, routed on exchange 'trilhas' with routing key '{ENVIRONMENT}.trilhas.log' (empty-string environment prefix if ENVIRONMENT is unset).

## Inputs

| name | type | unit |
|---|---|---|
| payload_log | dict | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| celery_task_dispatch | n/a | n/a |

## Logic

```text
salvar_log.apply_async(args=(payload_log,))
# salvar_log is @shared_task(exchange="trilhas",
#   routing_key=os.environ.get("ENVIRONMENT", "") + ".trilhas.log")
```

## Edge cases (as implemented)

If the broker is unreachable or the task silently fails, log_handler itself has no feedback loop / no fallback synchronous write; requests are not blocked or retried by this code path.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/tasks/log_handler.py` | 113-118 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-003`

**Related rules:**

- [RULE-AUDITORIA-LOGS-016](RULE-AUDITORIA-LOGS-016-request-response-log-capture-payload.md)

## Notes

Consistent with the same routing-key convention used by other domains (core.tasks, utils.firebase).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
