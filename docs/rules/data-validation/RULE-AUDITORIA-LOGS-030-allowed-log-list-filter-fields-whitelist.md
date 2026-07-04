# RULE-AUDITORIA-LOGS-030 — Allowed log-list filter fields whitelist

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Only whitelisted GET parameters with a truthy value are turned into ORM filter kwargs for LogModel.objects.filter(**filtros); everything else is silently ignored. The whitelist includes 'origem' and 'cpf', but LogModel has no such fields, and no UI control ever emits them (both are commented out in the template and in the surrounding view code).

## Inputs

| name | type | unit |
|---|---|---|
| request.GET | dict | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| filtros | dict | n/a |

## Logic

```text
filtros_permitidos = ["nome","origem","cpf","response_status_code","method","dispositivo",
                       "geolocalizacao__country_name","geolocalizacao__region","geolocalizacao__city",
                       "criado_em__gte","criado_em__lte","path"]
filtros = {}
for chave, valor in request.GET.items():
    if valor and chave in filtros_permitidos:
        # date-specific handling, see RULE-018
        filtros[chave] = valor
logs = LogModel.objects.filter(**filtros)
```

## Edge cases (as implemented)

If a client ever sends ?origem=x or ?cpf=y directly (bypassing the UI, which has no such inputs), filtros would include a key with no matching model field, and LogModel.objects.filter(**filtros) would raise a Django FieldError (500 error) since 'origem' and 'cpf' are not attributes of LogModel.

## Divergence

filtros_permitidos includes 'origem' and 'cpf', but LogModel has no such fields and no UI control ever emits them (both commented out in log.html and in the view's commented qs_origem block). If either param is ever supplied directly via query string, LogModel.objects.filter(**filtros) raises a Django FieldError (500). Single backend implementation, recorded verbatim.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/views/log.py` | 25-46 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-017`

**Related rules:**

- [RULE-AUDITORIA-LOGS-031](RULE-AUDITORIA-LOGS-031-geo-cascade-endpoints-use-a-narrower-filter-whitelist-than-t.md)
- [RULE-AUDITORIA-LOGS-001](RULE-AUDITORIA-LOGS-001-date-range-filter-boundary-formula-start-of-day-end-of-day.md)

## Notes

DISCREPANCY recorded verbatim: 'origem'/'cpf' are dead whitelist entries (commented out in log.html at lines 170/335-336/362 and in the view's commented qs_origem block at lines 96-101) that would crash the view if ever supplied as query params. Left exactly as coded.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
