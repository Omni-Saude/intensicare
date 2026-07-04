# RULE-AUDITORIA-LOGS-012 — Device icon mapping (get_icon) missing branches for tablet/email/touch_capable

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
get_icon maps the 'dispositivo' value to a FontAwesome icon class for 'browser', 'mobile', 'bot', and 'other' only. It has no branch for 'tablet', 'email', or 'touch_capable' — all of which log_handler's device classification (RULE-007) can actually produce — so the filter implicitly returns None for those, rendering no icon in the log-list table.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| value | string | n/a | browser\|mobile\|bot\|tablet\|email\|touch_capable\|other |

## Outputs

| name | type | unit |
|---|---|---|
| icon_class | string\|None | n/a |

## Logic

```text
if value == 'browser': return "fas fa-desktop"
elif value == 'mobile': return "fas fa-mobile-alt"
elif value == 'bot': return "fas fa-robot"
elif value == 'other': return "fas fa-question-circle"
# no elif for 'tablet' / 'email' / 'touch_capable' -> implicit return None
```

## Edge cases (as implemented)

Any log entry classified as tablet/email/touch_capable device (see RULE-007) shows the device text with no icon in the log-list table (blank <i class="None">? actually template does {{ obj.dispositivo|get_icon }} inside class="", so a None renders as the literal string 'None' in the class attribute).

## Divergence

get_icon() branches only on dispositivo in {browser, mobile, bot, other}, but the classification producing 'dispositivo' (RULE-AUDITORIA-LOGS-004, old RULE-007) can also emit 'tablet', 'email', or 'touch_capable' -- for those three values get_icon() implicitly returns None, which the template then renders as the literal string 'None' in a class attribute. Single backend implementation gap, recorded verbatim.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/templatetags/logs.py` | 73-82 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-026`

**Related rules:**

- [RULE-AUDITORIA-LOGS-004](RULE-AUDITORIA-LOGS-004-device-classification-from-user-agent-dispositivo.md)

## Notes

DISCREPANCY: incomplete mapping relative to the value space produced elsewhere in the same app; recorded verbatim.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
