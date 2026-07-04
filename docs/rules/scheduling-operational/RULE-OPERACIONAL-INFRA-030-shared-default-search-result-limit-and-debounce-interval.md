# RULE-OPERACIONAL-INFRA-030 — Shared default search-result limit and debounce interval

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

The three reusable search-input widget factories (autocomplete, single-select search, multi-tag search) each default to fetching a maximum of 5 results per request and debounce the user's keystroke-triggered search request by 700 milliseconds before firing it.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| limit (prop, optional) | number | results | default 5 |
| keystroke debounce | number | milliseconds | fixed at 700ms, not configurable via props |

## Outputs

| Name | Type | Unit |
|---|---|---|
| search request | HTTP GET (via injected request function) | - |

## Logic

```text
limit = props.limit ?? 5   // default across CreateAutoComplete, CreateSearchInput, CreateSearchTags
onSearchThrottle = debounce((key) => _request(key), 700)   // 700ms fixed debounce, all three widgets
```

## Edge cases (as implemented)

The debounce function is re-created on every render (`debounce(...)` called inline, not memoized), meaning the debounce timer's internal closure is a new instance each render — potentially causing multiple pending timers rather than one continuously-reset timer, across all three widgets identically.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hooks/Search/CreateAutoComplete.tsx` | 16-16,63-63 | `f9656be2` | primary |

- Merged from: RULE-search-FE-07-001
- Related rules: RULE-OPERACIONAL-INFRA-031

## Notes

Same pattern duplicated at src/hooks/Search/CreateSearchInput.tsx lines 16,61 and src/hooks/Search/CreateSearchTags.tsx lines 19,68. Debounce/limit counted as an API-layer request-transformation rule per scope instructions.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
