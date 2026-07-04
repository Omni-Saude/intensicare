# RULE-AUDITORIA-LOGS-032 — is_html heuristic (broad false-positive risk)

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | data-validation |
| Type | validation |
| Status | AMBIGUOUS |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A string value is treated as 'HTML' for display purposes (routed to an iframe, see RULE-031) if it contains the literal substring '<html', OR if it simply contains BOTH a '<' and a '>' character anywhere in the string — a broad heuristic that is not real HTML detection.

## Inputs

| name | type | unit |
|---|---|---|
| val | n/a | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| is_html | boolean | n/a |

## Logic

```text
def is_html(val):
    if isinstance(val, str):
        return "<html" in val or bool("<" in val and ">" in val)
    return False
```

## Edge cases (as implemented)

A plain-text log value that happens to contain both '<' and '>' characters (e.g. a mathematical comparison string, an email header like 'Name <addr>', or a code snippet) would be misclassified as HTML and rendered inside an <iframe srcdoc> rather than as plain text.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/templatetags/logs.py` | 34-38 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-029`

**Related rules:**

- [RULE-AUDITORIA-LOGS-015](RULE-AUDITORIA-LOGS-015-log-detail-field-rendering-rules-skip-falsy-json-html-plain.md)

## Notes

AMBIGUOUS rather than DISCREPANCY: this may be an intentionally loose heuristic for a low-stakes internal admin tool rather than a bug; recorded as-is.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
