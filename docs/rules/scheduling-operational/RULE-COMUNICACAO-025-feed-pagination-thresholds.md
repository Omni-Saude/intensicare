# RULE-COMUNICACAO-025 — Feed pagination thresholds

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
The activity feed initially loads 20 items (offset 0, limit 20). Additional pages are loaded 20 at a time via a "Mais" (load more) button, which is only shown once at least 20 items are loaded and there are more items available (nextOffset <= total count).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| offset | number | items | >= 0, default 0 |
| limit | number | items | default 20 |
| count (total items available) | number | items | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| load-more button visibility | boolean | — |

## Logic
```text
initial fetch: _getFeed(offset=0, limit=20)
on success with offset===0 && limit===20:
  feed = data.results; count = data.count; nextOffset = 20
on success otherwise (subsequent pages):
  feed = [...feed, ...data.results]; nextOffset += 20

show "Mais" button IF (feed.length >= 20 AND nextOffset <= count)
onClick "Mais": _getFeed(nextOffset)   // limit defaults to 20
```

## Edge cases (as implemented)
If the backend returns fewer than 20 results on the very first page, feed.length < 20 so the load-more button is never shown even if count implies more exist elsewhere (feed.length gate, not count-based alone).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/pages/empresa/[id_empresa]/feed/index.tsx | 100-134, 230-242 | f9656be2 | primary |
- Merged from: RULE-feed-FE-08-002
- Related rules: RULE-COMUNICACAO-021, RULE-COMUNICACAO-024

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
