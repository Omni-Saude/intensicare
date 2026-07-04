# RULE-COMUNICACAO-043 — Observation reply field rename

| Field | Value |
|---|---|
| Cluster | comunicacao |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
manage_data renames incoming 'resposta' to 'resposta_id' when present.

## Inputs

| name | type | unit |
|---|---|---|
| resposta | uuid |  |

## Outputs

| name | type | unit |
|---|---|---|
| resposta_id | uuid |  |

## Logic

```text
if data.get("resposta"):
    data["resposta_id"] = data.pop("resposta")
```

## Edge cases (as implemented)

Falsy resposta (None/0/'') is left un-renamed.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/observacao.py` | 16-20 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-observacao-BE-05-008`

**Related rules:**

- [RULE-COMUNICACAO-007](../alert-threshold/RULE-COMUNICACAO-007-firebase-message-count-notification-suppressed-for-reply-mes.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
