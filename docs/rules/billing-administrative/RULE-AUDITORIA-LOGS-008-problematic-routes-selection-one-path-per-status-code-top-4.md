# RULE-AUDITORIA-LOGS-008 — 'Problematic routes' selection: one path per status code, top 4

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | billing-administrative |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Candidate rows for the 'most problematic routes' chart are non-favicon paths with response_status_code in [399, 600), grouped by (path, status) and ordered by count descending. The loop then keeps only the FIRST row encountered for each distinct status code (i.e., the highest-count path for that code, since the queryset is pre-sorted by -qtd), discarding any other path sharing that status code, and the resulting list is capped to 4 entries.

## Inputs

_None._

## Outputs

| name | type | unit |
|---|---|---|
| bad_paths | list[dict] | n/a |

## Logic

```text
paths = LogModel.objects.exclude(path="/favicon.ico")
          .filter(path__isnull=False, response_status_code__range=(399, 600))
          .values_list("path","response_status_code").annotate(qtd=Count("path"))
          .order_by("-qtd")
lis, stats_diff = [], []
for path, status, qtd in paths:
    if status in stats_diff: continue        # only first (highest-qtd) path per status kept
    lis.append({"path": path, "status": status, "qtd": qtd})
    stats_diff.append(status)
bad_paths = lis[:4]
```

## Edge cases (as implemented)

If two different paths tie for the highest count under the same status code, only the one that sorts first in the DB's tie-break order is shown, silently dropping the other path with that same status entirely from the chart (not just deduped, but never revisited even in a lower position).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/views/log.py` | 139-155 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-022`

**Related rules:**

- [RULE-AUDITORIA-LOGS-010](../data-validation/RULE-AUDITORIA-LOGS-010-status-code-badge-color-mapping-get-status-style-399-boundar.md)
- [RULE-AUDITORIA-LOGS-007](RULE-AUDITORIA-LOGS-007-top-4-most-accessed-routes-limit.md)
- [RULE-AUDITORIA-LOGS-025](../data-validation/RULE-AUDITORIA-LOGS-025-uuid-in-path-anonymization-is-display-only-not-applied-to-ro.md)

## Notes

Range (399, 600) here treats status 399 as 'bad' (unlike RULE-024's get_status_style, which treats 399 as neither success nor clearly danger, folding it into 'warning').

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
