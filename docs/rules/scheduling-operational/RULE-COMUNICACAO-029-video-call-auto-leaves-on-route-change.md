# RULE-COMUNICACAO-029 — Video call auto-leaves on route change

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
While in an active video call, if the user starts navigating to a different Next.js route, the call-leave handler is invoked automatically so the user does not remain connected to the call after leaving the page.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| Next.js Router "routeChangeStart" event |  | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| onLeave() invocation | side effect | — |

## Logic
```text
Router.events.on("routeChangeStart", () => { onLeave(); })   // registered on every render of Controls
```

## Edge cases (as implemented)
The listener is registered unconditionally on every render (not inside a useEffect and not cleaned up/removed), so repeated renders of Controls attach additional "routeChangeStart" listeners, each of which will independently call onLeave() on the next route change.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/BuildVideoChat/VideoCall/Controls/Controls.tsx | 59-61 | f9656be2 | primary |
- Merged from: RULE-video-FE-05-003
- Related rules: RULE-COMUNICACAO-028, RULE-COMUNICACAO-030, RULE-COMUNICACAO-031

## Notes
Flagged for a verifier as a likely resource/listener leak (missing useEffect + cleanup / Router.events.off), recorded as implemented rather than corrected.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
