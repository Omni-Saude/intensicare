# RULE-AUDITORIA-LOGS-019 — Client IP and public/private classification

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
The client IP address and whether it is publicly routable are captured via django-ipware's get_client_ip(request), which returns (ip, is_routable); is_routable is stored verbatim as 'ip_publico'.

## Inputs

| name | type | unit |
|---|---|---|
| request | HttpRequest | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| ip | string | n/a |
| ip_publico | boolean | n/a |

## Logic

```text
ip, ip_publico = get_client_ip(request)
payload_log["ip"] = ip
payload_log["ip_publico"] = ip_publico
```

## Edge cases (as implemented)

If no IP can be determined, ipware conventionally returns (None, False); LogModel.ip_publico default=False aligns with this, but ip_publico=False is ambiguous between 'confirmed private IP' and 'IP undetermined'.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/tasks/log_handler.py` | 39, 51-53 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-009`

**Related rules:**

- [RULE-AUDITORIA-LOGS-035](../data-validation/RULE-AUDITORIA-LOGS-035-geolocalizacao-field-defaults-to-empty-dict-never-null-in-pr.md)
- [RULE-AUDITORIA-LOGS-016](RULE-AUDITORIA-LOGS-016-request-response-log-capture-payload.md)

## Notes

Field model default is documented separately as RULE-log-BE-13-034.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
