# RULE-OPERACIONAL-INFRA-007 — Pagination page-count and default page size

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | operacional-infra |

## Rule

Page model computes total page count as ceil(count/page_size); default list requests use offset 0 and limit (page size) 20.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| count | number | records | - |
| page_size | number | records/page | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| page_count | number | pages |

## Logic

```text
page_count = (count && page_size) ? Math.ceil(count / page_size) : 0
# default paginator: { offset: 0, limit: 20 }
```

## Edge cases (as implemented)

Returns 0 page_count when count or page_size is falsy (0/undefined). Default page size 20 (initialPaginator.ts).

## Verification

- Verdict: UNVERIFIABLE
- Reference: No authoritative published reference. ceil(count/page_size) is standard pagination arithmetic; default page size 20 is an arbitrary internal UI constant.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/Page.ts` | 16-20 | `f9656be2` | primary |

- Merged from: RULE-ops-FE-02-002
- Related rules: RULE-OPERACIONAL-INFRA-028

## Notes

Default limit=20 defined in src/utils/initialPaginator.ts:1. Operational pagination default.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
