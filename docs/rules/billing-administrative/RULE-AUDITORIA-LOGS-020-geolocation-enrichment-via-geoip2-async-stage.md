# RULE-AUDITORIA-LOGS-020 — Geolocation enrichment via GeoIP2 (async stage)

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
In the async persistence task, if an IP was captured, a GeoIP2 city lookup is performed and its result stored as 'geolocalizacao'; on any failure the error is recorded in 'error_geolocalizacao' and geolocalizacao remains an empty dict; if no IP was captured, geolocalizacao is also an empty dict.

## Inputs

| name | type | unit |
|---|---|---|
| payload_log.ip | string | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| geolocalizacao | dict | n/a |

## Logic

```text
ip = payload_log.get("ip", None)
geo_data = {}
if ip:
    try:
        geo_data = GeoIP2().city(ip)
    except Exception as e:
        payload_log["error_geolocalizacao"] = repr(e)
payload_log["geolocalizacao"] = geo_data
```

## Edge cases (as implemented)

Private/non-routable IPs (ip_publico=False) are still passed to GeoIP2().city(ip) with no guard, and will raise/be caught the same as any other lookup failure (recorded, not distinguished from a genuine GeoIP database miss).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/tasks/log_handler.py` | 119-128 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-010`

**Related rules:**

- [RULE-AUDITORIA-LOGS-034](../data-validation/RULE-AUDITORIA-LOGS-034-country-region-city-cascading-filter-city-not-re-scoped-by-c.md)

## Notes

Feeds the country/region/city filter dropdowns and the map shown on the log-detail page (RULE-033).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
