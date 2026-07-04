# RULE-COMUNICACAO-021 — Chat message list pagination

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
The sector chat loads messages in fixed pages of 20, newest-first from the API but reversed for display (oldest-at-top of each page); a "load more" control is shown only while at least 20 messages are currently loaded and the next offset has not yet reached the total count, and each additional load advances the offset by 20.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| offset | integer | message count | >=0, default 0 |
| limit | integer | message count | default 20 (fixed) |
| count (total messages) | integer | count | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| showLoadMore | boolean | — |
| nextOffset | integer | — |

## Logic
```text
// initial/refresh fetch: offset=0, limit=20
if (offset === 0 && limit === 20) {
  mensagens = data.results.reverse()
  count = data.count
  nextOffset = 20
} else {
  mensagens = [...data.results.reverse(), ...mensagens]   // prepend older page
  nextOffset += 20
}
showLoadMore = mensagens.length >= 20 && nextOffset <= count
```

## Edge cases (as implemented)
Page size (20) is hardcoded, not configurable from the UI; reaction/checagem actions re-fetch using the *current* nextOffset as the limit (so the whole loaded window is refreshed, not just the new page).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/MessagesList/MessagesList.tsx | 111-160 | f9656be2 | primary |
- Merged from: RULE-chat-FE-06-017
- Related rules: RULE-COMUNICACAO-025, RULE-COMUNICACAO-008

## Notes
Load-more UI condition rendered at lines 456-466 of the same file.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
