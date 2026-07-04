# RULE-COMUNICACAO-031 — Video-call room exit confirmation guard

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
While a video-call room has unsaved-changes state active (defaulting to true), both browser tab-close/refresh and in-app route navigation are intercepted with a confirmation prompt asking "Deseja sair da sala de video chamada?" (Do you want to leave the video call room?); confirming an in-app navigation additionally invokes an onLeaveConfirm callback.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| unsavedChanges | boolean | — | default true |

## Outputs
| Name | Type | Unit |
|---|---|---|
| navigation/unload block or allow | boolean (route change aborted or allowed) | — |

## Logic
```text
message = "Deseja sair da sala de video chamada?"
on beforeunload: if unsavedChanges: preventDefault(); returnValue = message
on routeChangeStart(url):
  if Router.asPath != url AND unsavedChanges AND NOT confirm(message):
    emit "routeChangeError"; Router.replace(Router, Router.asPath); throw (abort navigation)
  if confirm(message):
    onLeaveConfirm()
```

## Edge cases (as implemented)
confirm(message) is called up to twice in the same routeChangeStart handler (once inside the abort-condition check, once again unconditionally afterward) — meaning the user could see the native confirm dialog twice for a single navigation attempt if the first confirm() returns true (the abort branch's `!confirm(...)` short-circuits to false, so the code falls through to the second unconditional `if (confirm(message))`, prompting again).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/hooks/useWarnIfUnsavedChanges.ts | 4-38 | f9656be2 | primary |
- Merged from: RULE-video-FE-07-002
- Related rules: RULE-COMUNICACAO-029, RULE-COMUNICACAO-030

## Notes
Recorded verbatim; the double-confirm() behavior looks unintentional but is reproduced exactly as implemented, per ground rules.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
