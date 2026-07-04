# RULE-AUDITORIA-LOGS-007 — Top-4 most-accessed-routes limit

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | billing-administrative |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The 'most accessed routes' dashboard chart is limited to the top 4 paths by request count.

## Inputs

_None._

## Outputs

| name | type | unit |
|---|---|---|
| qtd_paths | dict | n/a |

## Logic

```text
qtd_paths = LogModel.objects.exclude(path=None).values("path")
              .annotate(qtd=Count("path")).values_list("path","qtd")
              .order_by("-qtd")[:4]
```

## Edge cases (as implemented)

This aggregation runs over ALL LogModel rows (not the currently filtered 'logs' queryset used for the list/table), so it is unaffected by the user's active filters.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/views/log.py` | 132-138 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-021`

**Related rules:**

- [RULE-AUDITORIA-LOGS-009](../data-validation/RULE-AUDITORIA-LOGS-009-undesirable-status-codes-chart-exclude-is-a-no-op-and-instea.md)
- [RULE-AUDITORIA-LOGS-008](RULE-AUDITORIA-LOGS-008-problematic-routes-selection-one-path-per-status-code-top-4.md)
- [RULE-AUDITORIA-LOGS-025](../data-validation/RULE-AUDITORIA-LOGS-025-uuid-in-path-anonymization-is-display-only-not-applied-to-ro.md)

## Notes

Same 'unfiltered aggregate' behavior applies to qtd_dispositivos, qtd_metodos, and qtd_status (lines 112-131) — all query LogModel.objects directly rather than the filtered 'logs' variable.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
