# RULE-AUDITORIA-LOGS-015 — Log-detail field rendering rules (skip falsy, JSON/HTML/plain branching)

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
On the single-log detail page, every field of the serialized log (LogSerializer, all fields) is iterated; fields with a falsy value are skipped entirely (no placeholder shown, unlike the list view's '-' placeholder). For each rendered field: JSON-classified values are pretty-printed in a <pre> block; else HTML-classified values are rendered inside a sandboxed <iframe srcdoc>; else the raw value is shown as plain text.

## Inputs

| name | type | unit |
|---|---|---|
| log_data | dict | n/a |

## Outputs

_None._

## Logic

```text
for name, value in log_data.items():
    if not value: continue
    if is_json(value) is True: render <pre>{{ value|pretty_json }}</pre>
    elif is_html(value) is True: render <iframe srcdoc="{{ value|clean_html }}">
    else: render <p>{{ value }}</p>
```

## Edge cases (as implemented)

Falsy-but-meaningful values (0, False, empty list/dict) are indistinguishable from 'absent' on this page since they are hidden entirely — e.g. a response_status_code of 0, or an empty geolocalizacao {}, would not be shown at all.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/templates/log-detail.html` | 62-80 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-031`

**Related rules:**

- [RULE-AUDITORIA-LOGS-014](RULE-AUDITORIA-LOGS-014-pretty-json-double-encodes-string-typed-json-values-instead.md)
- [RULE-AUDITORIA-LOGS-032](RULE-AUDITORIA-LOGS-032-is-html-heuristic-broad-false-positive-risk.md)

## Notes

n/a

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
