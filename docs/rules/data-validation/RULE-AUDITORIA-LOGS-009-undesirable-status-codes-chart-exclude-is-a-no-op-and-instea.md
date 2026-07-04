# RULE-AUDITORIA-LOGS-009 — 'Undesirable status codes' chart exclude is a no-op (AND instead of OR)

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | data-validation |
| Type | decision-tree |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The 'qtd_status' aggregate (used for the chart titled 'Status de resposta indesejáveis' / undesirable response statuses) is built by excluding rows that match BOTH response_status_code__isnull=True AND response_status_code__range= (200, 399) in a single .exclude() call. Because a single .exclude(A=x, B=y) call combines conditions with AND, and a value can never be simultaneously NULL and within a numeric range, no row ever satisfies both conditions at once — so this exclude() removes ZERO rows. The chart therefore includes every status code, including nulls and 2xx/3xx 'successful' codes, despite the intent implied by its title and by the analogous-but-correctly-chained exclude used elsewhere (RULE-022 uses .exclude(...).filter(...) as two separate calls).

## Inputs

_None._

## Outputs

| name | type | unit |
|---|---|---|
| qtd_status | dict | n/a |

## Logic

```text
qtd_status = LogModel.objects.exclude(
        response_status_code__isnull=True, response_status_code__range=(200, 399)
    ).values("response_status_code").annotate(qtd=Count("response_status_code"))
     .values_list("response_status_code", "qtd")
# NOTE: exclude(A=x, B=y) == NOT(A AND B). Since isnull=True and range(200,399) are
# mutually exclusive on the same field, NOT(A AND B) is always True => nothing excluded.
```

## Edge cases (as implemented)

n/a — the bug manifests on every request, unconditionally, not just an edge case.

## Divergence

Intent (implied by chart title 'Status de resposta indesejáveis' and by the correctly-chained exclude()+filter() pattern used in RULE-AUDITORIA-LOGS-008/old RULE-022) vs actual: the single .exclude(response_status_code__isnull=True, response_status_code__range=(200,399)) call ANDs the two conditions, which are mutually exclusive on one field, so the exclude removes zero rows. Should have been two chained .exclude() calls. No frontend counterpart; this is a single-backend ORM-semantics bug, recorded verbatim.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/views/log.py` | 124-131 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-023`

**Related rules:**

- [RULE-AUDITORIA-LOGS-008](../billing-administrative/RULE-AUDITORIA-LOGS-008-problematic-routes-selection-one-path-per-status-code-top-4.md)

## Notes

DISCREPANCY, high confidence: this is a Django ORM semantics bug (should have been two chained .exclude() calls, e.g. .exclude(response_status_code__isnull=True).exclude(response_status_code__range=(200,399))). Recorded exactly as implemented, not corrected.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
