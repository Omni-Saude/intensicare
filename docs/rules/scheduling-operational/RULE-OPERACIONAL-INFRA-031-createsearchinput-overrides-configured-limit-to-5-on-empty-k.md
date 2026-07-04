# RULE-OPERACIONAL-INFRA-031 — CreateSearchInput overrides configured limit to 5 on empty keyword

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Unlike its sibling widgets (CreateAutoComplete, CreateSearchTags), CreateSearchInput always requests exactly 5 results when the search keyword is empty (e.g. on initial focus/load), regardless of a caller-configured `limit` prop, and only honors the configured `limit` once the keyword is non-empty.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| keyword | string | - | - |
| limit (prop) | number | results | default 5 |

## Outputs

| Name | Type | Unit |
|---|---|---|
| effective request limit | number | results |

## Logic

```text
// CreateSearchInput only:
effective_limit = (keyword.length == 0) ? 5 : limit
// CreateAutoComplete and CreateSearchTags, by contrast, always use `limit` unconditionally:
effective_limit = limit   // (these two do NOT special-case empty keyword)
```

## Edge cases (as implemented)

A caller who configures CreateSearchInput with limit=20 would still only receive 5 initial options on focus (before typing), then up to 20 once a keyword is entered — an inconsistency with the other two search widgets that would return 20 initial options in the same scenario.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/hooks/Search/CreateSearchInput.tsx` | 43-59 | `f9656be2` | primary |

- Merged from: RULE-search-FE-07-002
- Related rules: RULE-OPERACIONAL-INFRA-030

## Notes

Compare src/hooks/Search/CreateAutoComplete.tsx lines 45-61 and src/hooks/Search/CreateSearchTags.tsx lines 51-66, neither of which conditions the limit on keyword length.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
