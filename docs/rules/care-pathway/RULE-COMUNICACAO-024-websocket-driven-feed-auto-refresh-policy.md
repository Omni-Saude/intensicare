# RULE-COMUNICACAO-024 — WebSocket-driven feed auto-refresh policy

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
The homecare activity feed listens on a WebSocket for update notifications. When a message with update === true arrives, the feed is only auto-refreshed and scrolled to top if the user has NOT scrolled away from the top of the feed (scrollTop === 0); if the user has scrolled down, no auto-refresh happens (a manual "Novas Atualizações" button is shown instead, per the surrounding UI).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| ws message payload .update | boolean | — | — |
| feed scroll position (element#feed.scrollTop) | number | pixels | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| feed refreshed / scrolled | boolean | — |

## Logic
```text
ws.onmessage = ({ data }) => {
  parsed = JSON.parse(data)
  checkScroll()                 // updates feedRolled state
  if (parsed.update === true) {
    rolled = checkScroll()      // rolled = (scrollTop !== 0)
    if (!rolled) {
      _getFeed()
      scrollToTop()
    }
  }
}
```

## Edge cases (as implemented)
checkScroll returns undefined if the #feed DOM element is not present (e.g. before first render); the `!rolled` check would then be `!undefined` = true, causing a refresh attempt.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/pages/empresa/[id_empresa]/feed/index.tsx | 66-149 | f9656be2 | primary |
- Merged from: RULE-feed-FE-08-001
- Related rules: RULE-COMUNICACAO-025, RULE-COMUNICACAO-026

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
