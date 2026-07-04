# RULE-AUDITORIA-LOGS-004 — Device classification from user agent (dispositivo)

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
The 'dispositivo' (device type) field is derived from the parsed user agent using a fixed priority order of boolean flags; the first matching flag wins. Default is 'other' when there is no user agent or none of the flags match.

## Inputs

| name | type | unit |
|---|---|---|
| request.user_agent | object | n/a |

## Outputs

| name | type | unit | range |
|---|---|---|---|
| dispositivo | string | n/a | browser\|mobile\|bot\|tablet\|email\|touch_capable\|other |

## Logic

```text
user_agent_str = "other"
if request.user_agent:
    agent = request.user_agent
    if agent.is_pc: user_agent_str = "browser"
    elif agent.is_mobile: user_agent_str = "mobile"
    elif agent.is_bot: user_agent_str = "bot"
    elif agent.is_tablet: user_agent_str = "tablet"
    elif agent.is_email_client: user_agent_str = "email"
    elif agent.is_touch_capable: user_agent_str = "touch_capable"
dispositivo = user_agent_str
```

## Edge cases (as implemented)

A device that is both touch-capable and a tablet is classified as 'tablet' (tablet checked before touch_capable); a PC-flagged bot would be classified as 'browser' not 'bot' since is_pc is checked first.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/tasks/log_handler.py` | 78-99 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-007`

**Related rules:**

- [RULE-AUDITORIA-LOGS-012](RULE-AUDITORIA-LOGS-012-device-icon-mapping-get-icon-missing-branches-for-tablet-ema.md)
- [RULE-AUDITORIA-LOGS-016](../billing-administrative/RULE-AUDITORIA-LOGS-016-request-response-log-capture-payload.md)

## Notes

Feeds directly into RULE-log-BE-13-026 (get_icon), which does not have branches for tablet/email/touch_capable.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
