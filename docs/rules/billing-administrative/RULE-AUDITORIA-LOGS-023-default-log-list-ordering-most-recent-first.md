# RULE-AUDITORIA-LOGS-023 — Default log list ordering (most recent first)

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
The filtered log queryset is always ordered by -criado_em (most recently created first) before pagination, regardless of any other filter applied.

## Inputs

_None._

## Outputs

_None._

## Logic

```text
paginator = Paginator(logs.order_by("-criado_em"), limit)
```

## Edge cases (as implemented)

n/a

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/views/log.py` | 47-50 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-015`

**Related rules:** _none_

## Notes

n/a

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
