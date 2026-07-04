# RULE-AUDITORIA-LOGS-025 — UUID-in-path anonymization is display-only, not applied to route aggregation stats

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | data-validation |
| Type | workflow |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
cud_uuid replaces any path segment that parses as a valid UUID (version 4) with the literal string 'id', generalizing dynamic-resource routes for readability. This normalization is applied ONLY in the log-list table's path column ({{ obj.path|cud_uuid|truncatechars:40 }}); it is NOT applied when computing the 'most accessed routes' (qtd_paths) or 'problematic routes' (bad_paths) aggregate counts in the view, which group by the raw, un-normalized path string. As a result, requests to what a human would consider 'the same route' with different embedded UUIDs are counted as distinct paths in both dashboard charts.

## Inputs

| name | type | unit |
|---|---|---|
| path | string | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| normalized_path | string | n/a |

## Logic

```text
def cud_uuid(value):
    buff = []
    for path in value.split("/"):
        try:
            uuid.UUID(path, version=4); buff.append("id")
        except ValueError:
            buff.append(path)
    return "/".join(buff)
# used only in log.html's table row; qtd_paths/bad_paths (log/views/log.py) group by raw `path`
```

## Edge cases (as implemented)

A route pattern like /assistidos/<uuid>/observacoes/ visited for 1000 distinct assisted-persons would appear as up to 1000 separate rows in the raw path aggregation, likely never surfacing in the top-4 'most accessed routes' chart even though the underlying route pattern is extremely hot.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/templatetags/logs.py` | 50-60 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-030`

**Related rules:**

- [RULE-AUDITORIA-LOGS-007](../billing-administrative/RULE-AUDITORIA-LOGS-007-top-4-most-accessed-routes-limit.md)
- [RULE-AUDITORIA-LOGS-008](../billing-administrative/RULE-AUDITORIA-LOGS-008-problematic-routes-selection-one-path-per-status-code-top-4.md)

## Notes

AMBIGUOUS: could be an intentional scope limitation (display-only normalization) or an oversight where the stats should have used the normalized path too; cross-referenced against log/views/log.py lines 132-155 for the aggregation side.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
