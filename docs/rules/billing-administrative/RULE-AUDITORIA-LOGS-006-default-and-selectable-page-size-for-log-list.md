# RULE-AUDITORIA-LOGS-006 — Default and selectable page size for log list

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
The log list defaults to 50 results per page when no 'limit' query param is supplied (both server-side default and the client JS default), with selectable page sizes of 10/20/50/100/200/500.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| GET.limit | integer | records | 10\|20\|50\|100\|200\|500 |

## Outputs

| name | type | unit |
|---|---|---|
| page_size | integer | records |

## Logic

```text
limit = request.GET.get("limit", 50)   # server default
# client: if (!params.limit) limit_el.val(50)   # JS default mirrors server default
# <select id="limit"> options: 10, 20, 50, 100, 200, 500
```

## Edge cases (as implemented)

No server-side validation caps 'limit' to the listed choices; an arbitrary numeric (or non-numeric) limit value supplied directly via the URL query string is passed straight to Paginator().

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/views/log.py` | 48-49 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-016`

**Related rules:** _none_

## Notes

Companion UI evidence: log/templates/log.html lines 308-317 (option list) and 343-347 (JS default).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
