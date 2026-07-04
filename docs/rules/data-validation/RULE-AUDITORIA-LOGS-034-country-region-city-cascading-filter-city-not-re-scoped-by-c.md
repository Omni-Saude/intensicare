# RULE-AUDITORIA-LOGS-034 — Country -> region -> city cascading filter (city not re-scoped by country)

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
The geolocation filter dropdowns cascade: regions are looked up filtered by an exact (case-insensitive) country name match; cities are looked up filtered ONLY by an exact (case-insensitive) region name match — with no additional country constraint — relying on the assumption that region names are globally unique across countries.

## Inputs

| name | type | unit |
|---|---|---|
| pais | string | n/a |
| estado | string | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| regioes | list[string] | n/a |
| cidades | list[string] | n/a |

## Logic

```text
# EstadoLogView.get(pais):
regioes = logs.distinct("geolocalizacao__region").order_by("geolocalizacao__region")
              .filter(geolocalizacao__country_name__iexact=pais).exclude(geolocalizacao__region=None)
# CityLogView.get(estado):
cidades = LogModel.objects.distinct("geolocalizacao__city").order_by("geolocalizacao__city")
              .filter(geolocalizacao__region__iexact=estado).exclude(geolocalizacao__city=None)
              # note: no geolocalizacao__country_name filter here
```

## Edge cases (as implemented)

If two different countries in the GeoIP data happen to share an identically-named region/state (a real possibility, e.g. common region names), the city dropdown would show cities from both countries merged together for that region name.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/views/log.py` | 233-271, 292-331 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-033`

**Related rules:**

- [RULE-AUDITORIA-LOGS-020](../billing-administrative/RULE-AUDITORIA-LOGS-020-geolocation-enrichment-via-geoip2-async-stage.md)
- [RULE-AUDITORIA-LOGS-024](RULE-AUDITORIA-LOGS-024-dead-nested-duplicate-of-estadologview.md)

## Notes

AMBIGUOUS: plausible by design (simplicity) for a mostly-domestic user base, but not verified against actual data distribution.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
