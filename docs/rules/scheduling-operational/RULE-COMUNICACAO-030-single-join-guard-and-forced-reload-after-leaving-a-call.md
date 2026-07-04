# RULE-COMUNICACAO-030 — Single-join guard and forced reload after leaving a call

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
The Agora video-call session only calls client.join(...) once per "canJoin" cycle (guarded by a canJoin flag flipped to false immediately after joining), and forces a full browser page reload immediately after a user leaves the call/closes tracks.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| canJoin (state, initial true) |  | — | — |
| ready, tracks (Agora hook state) |  | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| client.join(appId, channelName, token, null) invocation | side effect | — |
| window.location.reload() | side effect | — |

## Logic
```text
effect on [channelName, client, ready, tracks]:
  if ready && tracks: init(channelName)
init(name):
  register user-published/unpublished/left handlers
  if canJoin:
    await client.join(appId, name, token, null)
    if tracks: await client.publish([tracks[0], tracks[1]])
    canJoin = false
    start = true
leaveChannel():
  await client.leave(); await offlineUser(); client.removeAllListeners()
  if tracks: tracks[0].close(); tracks[1].close()
  setInCall(false); canJoin = true
  window.location.reload()      // unconditional full page reload after leaving
```

## Edge cases (as implemented)
Because window.location.reload() runs unconditionally at the end of leaveChannel, any further in-memory app state is discarded and the whole SPA reloads from scratch every time a user leaves a video call, not just on error paths.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/BuildVideoChat/VideoCall/VideoCall.tsx | 27,32-77,79-90 | f9656be2 | primary |
- Merged from: RULE-video-FE-05-004
- Related rules: RULE-COMUNICACAO-028, RULE-COMUNICACAO-029

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
