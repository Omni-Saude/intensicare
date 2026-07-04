# RULE-AUDITORIA-LOGS-011 — HTTP method badge color mapping (get_method_style)

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
HTTP methods are mapped to a badge color: GET is 'success'; POST/PUT/PATCH are 'warning'; any other method (DELETE, HEAD, OPTIONS, etc.) is 'danger'.

## Inputs

| name | type | unit |
|---|---|---|
| value | string | HTTP method |

## Outputs

| name | type | unit | range |
|---|---|---|---|
| badge_style | string | n/a | success\|warning\|danger |

## Logic

```text
if value == "GET": return "success"
elif value in ("POST", "PUT", "PATCH"): return "warning"
else: return "danger"
```

## Edge cases (as implemented)

DELETE is classified as 'danger' along with any unrecognized/malformed method string.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/templatetags/logs.py` | 95-102 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-025`

**Related rules:**

- [RULE-AUDITORIA-LOGS-010](RULE-AUDITORIA-LOGS-010-status-code-badge-color-mapping-get-status-style-399-boundar.md)
- [RULE-AUDITORIA-LOGS-012](RULE-AUDITORIA-LOGS-012-device-icon-mapping-get-icon-missing-branches-for-tablet-ema.md)

## Notes

n/a

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
