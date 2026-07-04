# RULE-AUDITORIA-LOGS-029 — Log persistence validation gate

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
The assembled payload is validated through LogSerializer before saving; an invalid payload raises (raise_exception=True), meaning a malformed log entry is never partially/silently saved — the whole task fails instead.

## Inputs

| name | type | unit |
|---|---|---|
| payload_log | dict | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| log_instance | LogModel | n/a |

## Logic

```text
log = LogSerializer(data=payload_log)
log.is_valid(raise_exception=True)   # raises on failure -> task fails, nothing saved
log_instance = log.save()
return LogSimpleSerializer(instance=log_instance).data
```

## Edge cases (as implemented)

A single malformed field (e.g. an unexpected type for response_status_code) discards the entire log entry for that request/response, with no retry/dead-letter handling visible in this code.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/tasks/log_handler.py` | 129-135 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-011`

**Related rules:**

- [RULE-AUDITORIA-LOGS-028](RULE-AUDITORIA-LOGS-028-authenticated-user-attribution-on-log-entries.md)
- [RULE-AUDITORIA-LOGS-033](../billing-administrative/RULE-AUDITORIA-LOGS-033-log-field-exposure-scoping-logsimpleserializer-vs-logseriali.md)

## Notes

n/a

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
