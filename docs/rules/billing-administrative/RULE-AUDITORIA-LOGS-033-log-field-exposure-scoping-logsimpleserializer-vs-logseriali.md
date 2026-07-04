# RULE-AUDITORIA-LOGS-033 — Log field-exposure scoping (LogSimpleSerializer vs LogSerializer)

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | billing-administrative |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Two serializers expose different subsets of a log record. LogSimpleSerializer (used as the Celery task's return payload) exposes only: user, path, method, response_status_code, user_agent, dispositivo, error_request_log, error_response_log, ip, ip_publico, geolocalizacao, error_geolocalizacao — explicitly excluding meta, headers, request_body, and response_body. LogSerializer (fields='__all__', used for validation/save in salvar_log and for the detail-page context) exposes every field including the full request/response bodies and headers.

## Inputs

| name | type | unit |
|---|---|---|
| LogModel_instance | LogModel | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| serialized_data | dict | n/a |

## Logic

```text
class LogSimpleSerializer(ModelSerializer):
    user = UsuarioSerializer(read_only=True)
    fields = ['user','path','method','response_status_code','user_agent','dispositivo',
              'error_request_log','error_response_log','ip','ip_publico',
              'geolocalizacao','error_geolocalizacao']
class LogSerializer(ModelSerializer):
    fields = '__all__'
```

## Edge cases (as implemented)

Anywhere LogSimpleSerializer's output is consumed downstream (e.g. by a Celery result backend/consumer), request/response bodies and raw headers are never exposed there — only the detail-page path (LogSerializer, gated by RULE-014's access control) surfaces the full bodies/headers.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/api/v1/serializers/log.py` | 7-23 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-032`

**Related rules:**

- [RULE-AUDITORIA-LOGS-029](../data-validation/RULE-AUDITORIA-LOGS-029-log-persistence-validation-gate.md)
- [RULE-AUDITORIA-LOGS-022](RULE-AUDITORIA-LOGS-022-log-dashboard-access-control-authenticated-only-no-staff-own.md)

## Notes

n/a

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
