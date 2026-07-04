# RULE-OPERACIONAL-INFRA-028 — Pagination control disabled when everything fits on one page

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

The shared footer pagination control is disabled whenever the total record count is less than or equal to the current page size, since there would be no additional pages to page through.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| page.count (total records) | number | - | - |
| paginator.limit (page size) | number | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| Pagination disabled prop | boolean | - |

## Logic

```text
disabled = page.count <= paginator.limit
onChange(page, limit): paginate({ limit, offset: (page-1)*limit }); setCurrentPage(page)
```

## Edge cases (as implemented)

Uses "<=" so a result set exactly equal to one page's worth of records also disables the control (correct, since a second page would be empty); does not account for limit being 0 or negative.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FooterPaginator/FooterPaginator.tsx` | 11-31 | `f9656be2` | primary |

- Merged from: RULE-paginacao-FE-05-001
- Related rules: RULE-OPERACIONAL-INFRA-007

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
