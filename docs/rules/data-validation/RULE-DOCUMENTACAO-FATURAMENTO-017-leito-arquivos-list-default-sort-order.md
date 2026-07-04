# RULE-DOCUMENTACAO-FATURAMENTO-017 — Leito arquivos list default sort order

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | documentacao-faturamento |

## Rule
The paginated list of a leito's uploaded arquivos (files) applies a static default ordering of "data_arquivo" with no leading minus sign, which - for the typical Django-REST-Framework "ordering" query-param convention this codebase otherwise follows - sorts ascending (oldest file first) by default.

## Outputs
| Name | Type | Unit |
|---|---|---|
| staticFilters.ordering | string |  |

## Logic
```text
PaginationProvider(staticFilters = { ordering: "data_arquivo" })
```

## Edge cases (as implemented)
No leading "-" is present, so if the backend follows the common DRF convention (bare field name = ascending, "-field" = descending), the default view would list the oldest uploaded file first rather than the most recent - unusual for a document/attachment list, where most-recent-first is the typical expectation.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/ArquivosContent/ArquivosContent.tsx | 239-262 | f9656be2 | primary |
- Merged from: RULE-arquivo-FE-05-001
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-011, RULE-DOCUMENTACAO-FATURAMENTO-016

## Notes
Recorded verbatim per audit ground rules; flagged AMBIGUOUS because it is plausible this ascending default is intentional (e.g. chronological reading order) or an oversight (missing "-" prefix) - a verifier should confirm the intended default sort direction against product requirements or the equivalent backend endpoint.


No corresponding backend DRF `ordering`/default-sort configuration for this endpoint was found in the backend repo to resolve the ambiguity one way or the other; recorded as-is per audit ground rules.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
