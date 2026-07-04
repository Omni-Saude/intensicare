# RULE-OPERACIONAL-INFRA-043 — Breadcrumb hides UUID-shaped route segments

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | data-validation |
| Type | workflow |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
When building the breadcrumb trail from the current route path, any path segment whose string length is exactly 36 characters (the length of a canonical UUID) is dropped from the displayed trail, so entity IDs embedded in the URL never appear as breadcrumb labels.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| router.asPath segments | string[] |  |  |

## Outputs

| name | type |
|---|---|
| breadcrumbs | { breadcrumbName: string; path: string }[] |

## Logic

```text
linkPath = router.asPath.split("/"); linkPath.shift()   // drop leading empty segment
for each (path, i) in linkPath:
  if path.length !== 36:
    emit { breadcrumbName: capitalize(path), path: "/" + linkPath.slice(0,i).join("/") }
  else:
    emit undefined   // filtered out at render time (falsy Bread entries are skipped)
```

## Edge cases (as implemented)

Uses a raw length check (===36) rather than a UUID regex, so any non-UUID path segment that happens to be exactly 36 characters long would also be hidden, and a UUID rendered without dashes or with different formatting would not be hidden. Breadcrumbs accumulate onto previous state across router changes ([...prevState, ...pathArray]) rather than being replaced, relying on route decomposition being consistent.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Breadcrumbs/Breadcrumbs.tsx` | 20-35 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-breadcrumb-FE-05-001`

**Related rules:** _none_

## Notes

Minor routing-convention rule; included because it encodes an assumption about the URL structure (bare UUIDs as path segments) that a rebuild must preserve to avoid breadcrumbs showing raw entity IDs.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
