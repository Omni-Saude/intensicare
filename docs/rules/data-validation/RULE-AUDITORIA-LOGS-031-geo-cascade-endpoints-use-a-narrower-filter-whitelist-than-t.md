# RULE-AUDITORIA-LOGS-031 — Geo cascade endpoints use a narrower filter whitelist than the main list (missing 'path')

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
EstadoLogView (region-by-country) and CityLogView (city-by-region) each define their own filtros_permitidos list, identical to LogView's except that 'path' is omitted. The client JS forwards the full current query string (including any selected 'path'/route filter) to these endpoints, but the server silently drops the 'path' param since it is not in these views' whitelist — so the region/city suggestion lists never actually reflect a currently-applied route filter, even though the country/status/method/device/date filters do apply.

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
# EstadoLogView / CityLogView filtros_permitidos (both instances):
["nome","origem","cpf","response_status_code","method","dispositivo",
 "geolocalizacao__country_name","geolocalizacao__region","geolocalizacao__city",
 "criado_em__gte","criado_em__lte"]   # <-- no "path", unlike LogView's list (line 37)
```

## Edge cases (as implemented)

n/a

## Divergence

LogView's filtros_permitidos includes 'path'; EstadoLogView's and CityLogView's own copies of the same list omit 'path'. The client JS forwards the full current query string (including any 'path' filter) to these endpoints regardless, but the server silently drops it since it's not in the whitelist -- so region/city suggestion lists never reflect a currently-applied route filter, unlike the country/status/method/device/date filters which do apply. Inconsistency across three sibling endpoints in a single backend, recorded verbatim.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/views/log.py` | 200-212, 241-253, 301-313 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-019`

**Related rules:**

- [RULE-AUDITORIA-LOGS-030](RULE-AUDITORIA-LOGS-030-allowed-log-list-filter-fields-whitelist.md)
- [RULE-AUDITORIA-LOGS-001](RULE-AUDITORIA-LOGS-001-date-range-filter-boundary-formula-start-of-day-end-of-day.md)

## Notes

DISCREPANCY: inconsistent filter propagation across the three sibling endpoints, recorded verbatim.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
