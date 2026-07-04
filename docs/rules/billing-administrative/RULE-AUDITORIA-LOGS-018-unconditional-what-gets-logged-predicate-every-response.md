# RULE-AUDITORIA-LOGS-018 — Unconditional what-gets-logged predicate (every response)

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
There is no filtering predicate anywhere in the log app (no exclusion by path, method, status code, or content type) that determines whether a request gets logged. log_handler(request, response) is invoked for literally every HTTP response processed by the application.

## Inputs

_None._

## Outputs

_None._

## Logic

```text
class LogMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        log_handler(request, response)   # unconditional, no predicate
        return response
```

## Edge cases (as implemented)

Static assets, health checks, admin pages, and error responses (4xx/5xx) are all logged identically to normal API calls; nothing is exempted.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilhas/middleware.py` | 9-15 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-004`

**Related rules:**

- [RULE-AUDITORIA-LOGS-016](RULE-AUDITORIA-LOGS-016-request-response-log-capture-payload.md)

## Notes

trilhas/middleware.py is OUTSIDE this partition's enumerated log/* file list (it is the invocation site, likely owned by another partition covering the trilhas/ project package), but it is the only place that answers the task brief's explicit 'what-gets-logged predicate' question for the log app, so it is included here for completeness. No other file in log/* contains a call to log_handler.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
