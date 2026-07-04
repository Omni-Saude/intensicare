# RULE-AUDITORIA-LOGS-010 — Status-code badge color mapping (get_status_style) — 399 boundary bug

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
Response status codes are mapped to a bootstrap badge color: 'success' if the code is in range(100, 399) (i.e. 100-398 inclusive — 399 is EXCLUDED because Python's range() stop bound is exclusive), 'warning' if less than 500 (this catches 399 and any value <100, in addition to 400-499), else 'danger'.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| value | integer | HTTP status code | any |

## Outputs

| name | type | unit | range |
|---|---|---|---|
| badge_style | string | n/a | success\|warning\|danger |

## Logic

```text
if value in range(100, 399): return "success"   # 100..398 only; 399 NOT included
elif value < 500: return "warning"               # catches 399, and any value < 100
else: return "danger"
```

## Edge cases (as implemented)

Status code 399 (a 3xx-adjacent value) renders as 'warning' instead of 'success', inconsistent with the rest of the 300-398 block. A (non-real-world) value below 100 would also render as 'warning' rather than falling through to a distinct bucket.

## Divergence

range(100,399) excludes 399 (Python range() stop bound is exclusive), so status 399 falls through to the 'warning' branch (value < 500) instead of 'success', inconsistent with the rest of the 300-398 block and with RULE-AUDITORIA-LOGS-008's (old RULE-022) treatment of 399 as 'bad'/danger-range. Off-by-one, single backend implementation, recorded verbatim.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/templatetags/logs.py` | 85-92 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-024`

**Related rules:**

- [RULE-AUDITORIA-LOGS-008](../billing-administrative/RULE-AUDITORIA-LOGS-008-problematic-routes-selection-one-path-per-status-code-top-4.md)
- [RULE-AUDITORIA-LOGS-013](RULE-AUDITORIA-LOGS-013-is-status-code-validity-check-599-boundary-unused-dead-code.md)

## Notes

DISCREPANCY: off-by-one on the upper bound of the 'success' range, recorded verbatim (range(100,399) instead of range(100,400) or an inclusive check).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
