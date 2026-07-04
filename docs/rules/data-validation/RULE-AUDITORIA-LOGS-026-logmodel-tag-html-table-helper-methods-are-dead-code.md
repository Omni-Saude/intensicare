# RULE-AUDITORIA-LOGS-026 — LogModel *_tag() HTML-table helper methods are dead code

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | data-validation |
| Type | workflow |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
LogModel defines headers_tag(), meta_tag(), request_body_tag(), and response_body_tag(), each building an HTML <table> (via utils.html_template. table_template) of the corresponding JSON field's key/value pairs. None of these methods are referenced anywhere in the repository (no admin.py registers list_display/readonly_fields using them, no template calls them) — the log app has no admin.py at all in this partition.

## Inputs

_None._

## Outputs

| name | type | unit |
|---|---|---|
| html_table | string | n/a |

## Logic

```text
def headers_tag(self): return table_template(self.headers)
def meta_tag(self): return table_template(self.meta)
def request_body_tag(self): return table_template(self.request_body)
def response_body_tag(self): return table_template(self.response_body)
# grep across repo for these method names: only these 4 definitions, zero call sites
```

## Edge cases (as implemented)

n/a — dead code, no runtime effect.

## Divergence

headers_tag()/meta_tag()/request_body_tag()/response_body_tag() build HTML <table> markup but have zero call sites repo-wide (no admin.py exists for the log app in this snapshot) -- dead code, likely intended for a Django admin change-list/detail display that was never wired up. Recorded verbatim.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/models/log.py` | 49-59 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-035`

**Related rules:**

- [RULE-AUDITORIA-LOGS-019](../billing-administrative/RULE-AUDITORIA-LOGS-019-client-ip-and-public-private-classification.md)

## Notes

DISCREPANCY (dead code): likely intended for a Django admin change-list/detail display that was never wired up (no log/admin.py exists in this repo snapshot).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
