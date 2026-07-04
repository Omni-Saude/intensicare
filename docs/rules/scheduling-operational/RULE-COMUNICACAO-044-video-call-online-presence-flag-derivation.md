# RULE-COMUNICACAO-044 — Video-call online-presence flag derivation

| Field | Value |
|---|---|
| Cluster | comunicacao |
| Category | scheduling-operational |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A user's real-time video-call presence status for a given sector/chat is written to Firestore as online_call=true when the triggering action is "in", and false for any other action (in practice "out").

## Inputs

| name | type | unit | range |
|---|---|---|---|
| action | string enum |  | in \| out |

## Outputs

| name | type | unit |
|---|---|---|
| online_call | boolean |  |

## Logic

```text
online_call = (action == "in") ? true : false
// written via Firestore document update at path /chats/{setor}/usuarios/{usuario}/
```

## Edge cases (as implemented)

Any action value other than the literal "in" (the type only allows "in"|"out", but the ternary itself would treat any non-"in" value as false) results in online_call=false.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hooks/useUpdateStatus.ts` | 3-17 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-video-FE-07-001`

**Related rules:**

- [RULE-COMUNICACAO-028](../care-pathway/RULE-COMUNICACAO-028-online-call-roster-filtered-to-users-currently-in-call.md)
- [RULE-COMUNICACAO-016](../triage-eligibility/RULE-COMUNICACAO-016-video-call-join-gated-on-detected-video-input-device.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
