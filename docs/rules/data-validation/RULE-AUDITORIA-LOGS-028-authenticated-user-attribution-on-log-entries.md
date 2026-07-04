# RULE-AUDITORIA-LOGS-028 — Authenticated-user attribution on log entries

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | data-validation |
| Type | validation |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The log's 'user' FK value and 'nome' display name are only populated when the request is authenticated as a core.Usuario instance; otherwise 'nome' is an empty string and 'user' is coerced to the empty string "" (not None/null).

## Inputs

| name | type | unit |
|---|---|---|
| request.user | Usuario\|AnonymousUser | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| user | string | n/a |
| nome | string | n/a |

## Logic

```text
payload_log["user"] = str(request.user.pk) if request.user.pk else ""
payload_log["nome"] = request.user.nome if isinstance(request.user, Usuario) else ""
```

## Edge cases (as implemented)

For anonymous requests, 'user' is the literal string '' rather than None, even though LogModel.user is a nullable ForeignKey. Whether DRF's LogSerializer (PrimaryKeyRelatedField, fields='__all__') accepts '' and maps it to NULL, or raises a validation error that would fail the whole task (see RULE-011), could not be confirmed from the code alone (depends on DRF version's empty-value handling for FK fields with blank=True/null=True) — best interpretation: intent was 'no user' but the literal value produced is not the FK's null value.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/tasks/log_handler.py` | 35-48 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-008`

**Related rules:**

- [RULE-AUDITORIA-LOGS-016](../billing-administrative/RULE-AUDITORIA-LOGS-016-request-response-log-capture-payload.md)
- [RULE-AUDITORIA-LOGS-029](RULE-AUDITORIA-LOGS-029-log-persistence-validation-gate.md)

## Notes

AMBIGUOUS: recorded verbatim; downstream serializer behavior for the '' sentinel on an unauthenticated request was not verifiable statically.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
