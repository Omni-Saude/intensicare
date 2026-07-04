# RULE-AUDITORIA-LOGS-013 — is_status_code validity check — 599 boundary, unused (dead code)

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
is_status_code(value) returns True only for value in range(100, 599) — i.e. 100-598 inclusive, excluding 599 due to range()'s exclusive stop bound — and returns None (falsy) otherwise. This filter is defined but never referenced by any template in the repository.

## Inputs

| name | type | unit |
|---|---|---|
| value | integer | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| is_valid | boolean\|None | n/a |

## Logic

```text
def is_status_code(value):
    if value in range(100, 599):   # excludes 599
        return True
    # implicit return None otherwise
```

## Edge cases (as implemented)

n/a — dead code, no runtime callers found via repo-wide grep.

## Divergence

range(100,599) excludes 599 (exclusive stop bound), same off-by-one pattern as RULE-AUDITORIA-LOGS-010 (old RULE-024); however this filter has zero call sites in any template (dead code), so the bug has no observable runtime effect today. Recorded verbatim.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/templatetags/logs.py` | 105-108 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-027`

**Related rules:**

- [RULE-AUDITORIA-LOGS-010](RULE-AUDITORIA-LOGS-010-status-code-badge-color-mapping-get-status-style-399-boundar.md)

## Notes

DISCREPANCY (low impact — dead code): same off-by-one pattern as RULE-024. Grep across the repo for 'is_status_code' finds only this definition, no usage in any .html template.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
