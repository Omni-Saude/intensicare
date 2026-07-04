# RULE-AUDITORIA-LOGS-035 — geolocalizacao field defaults to empty dict, never null in practice

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
LogModel.geolocalizacao is a JSONField with default=dict, so newly created log rows always have a dict value ({} at minimum) rather than None/null, which is what allows LogDetailView to safely call log.geolocalizacao.get('latitude') / .get('longitude') without a null-check.

## Inputs

_None._

## Outputs

| name | type | unit |
|---|---|---|
| geolocalizacao | dict | n/a |

## Logic

```text
geolocalizacao = models.JSONField(default=dict, blank=True, null=True)
# LogDetailView: if log.geolocalizacao.get("latitude") and log.geolocalizacao.get("longitude"): ...
```

## Edge cases (as implemented)

The field is still nullable at the DB level (null=True); if a row were ever explicitly saved with geolocalizacao=None (bypassing the default), the .get() call in LogDetailView would raise AttributeError. In the normal log_handler/salvar_log flow this cannot happen because salvar_log always sets payload_log['geolocalizacao'] to at least {} (RULE-010).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/models/log.py` | 29-29 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-034`

**Related rules:**

- [RULE-AUDITORIA-LOGS-019](../billing-administrative/RULE-AUDITORIA-LOGS-019-client-ip-and-public-private-classification.md)
- [RULE-AUDITORIA-LOGS-020](../billing-administrative/RULE-AUDITORIA-LOGS-020-geolocation-enrichment-via-geoip2-async-stage.md)

## Notes

n/a

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
