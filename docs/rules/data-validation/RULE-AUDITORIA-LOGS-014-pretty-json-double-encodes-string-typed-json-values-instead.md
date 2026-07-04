# RULE-AUDITORIA-LOGS-014 — pretty_json double-encodes string-typed JSON values instead of formatting them

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | data-validation |
| Type | decision-tree |
| Status | DISCREPANCY |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
pretty_json is meant to indent/format a JSON-classified value for display. For non-string values (dict/list) it correctly does json.dumps(value, indent=4). For STRING values that pass is_json (i.e. valid JSON text stored as a string), it first re-serializes the raw string itself via json.dumps (wrapping/escaping it as a JSON string literal), then json.dumps's that already-serialized string again for the 'indent=4' pass — producing a garbled, escaped single-line string rather than a parsed-and-reformatted JSON structure. The code never calls json.loads on the string branch.

## Inputs

| name | type | unit |
|---|---|---|
| value | str\|dict\|list | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| formatted | string | n/a |

## Logic

```text
def pretty_json(value):
    res = value
    if is_json(value):
        if isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False)   # BUG: re-serializes the raw string,
                                                              # does not parse it (should be json.loads)
        res = json.dumps(value, indent=4, ensure_ascii=False)  # dumps a string -> no real indentation
    return res
```

## Edge cases (as implemented)

Only manifests when the underlying log_data value is itself a JSON-formatted STRING (rather than an already-decoded dict/list); most JSONField values from LogSerializer come through as native dicts/lists (where the bug does not trigger), but any header/meta/body value that ended up stored as a raw JSON string text would be rendered garbled in log-detail.html's <pre>{{ value|pretty_json }}</pre> block.

## Divergence

Intended behavior: parse a JSON-formatted string then pretty-print it with indent=4. Actual: for string-typed JSON values the code re-serializes the raw string via json.dumps (escaping it as a JSON string literal) instead of json.loads-ing it, then dumps the already-serialized string again -- producing a garbled single-line escaped string instead of an indented structure. Only manifests when a log_data value is itself a JSON-formatted string rather than an already-decoded dict/list. Single backend implementation, recorded verbatim.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/templatetags/logs.py` | 63-70 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-028`

**Related rules:**

- [RULE-AUDITORIA-LOGS-015](RULE-AUDITORIA-LOGS-015-log-detail-field-rendering-rules-skip-falsy-json-html-plain.md)

## Notes

DISCREPANCY recorded verbatim. Confidence is medium because whether string-typed JSON values actually reach this template filter in practice (vs. always-already-decoded dicts) depends on runtime data shapes not fully determinable from static code alone.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
