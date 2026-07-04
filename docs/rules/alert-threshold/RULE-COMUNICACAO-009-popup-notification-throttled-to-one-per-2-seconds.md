# RULE-COMUNICACAO-009 — Popup notification throttled to one per 2 seconds

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
Incoming popup notifications (from the popover websocket) are passed through a lodash debounce wrapping showNotification with a 2000ms wait, so rapid bursts of incoming messages collapse into at most one popup toast per 2-second window.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| notificacao (from wsPopover) | Models.Notificacao | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| antd notification.open(...) call | side effect | — |

## Logic
```text
trotthleNotification = debounce(showNotification, 2000)
```

## Edge cases (as implemented)
Because this is a plain debounce (not throttle, despite the variable name "trotthleNotification"), only the LAST notification in a rapid burst within the 2000ms window is ever shown - earlier ones in that window are silently discarded, not queued.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/DisplayNotificaoes/DisplayNotificaoes.tsx | 98,105 | f9656be2 | primary |
- Merged from: RULE-notificacao-FE-05-002
- Related rules: RULE-COMUNICACAO-020, RULE-COMUNICACAO-010, RULE-COMUNICACAO-011

## Notes
Misnamed variable ("trotthleNotification") suggests throttle was intended but debounce was used - recorded as implemented, not corrected.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
