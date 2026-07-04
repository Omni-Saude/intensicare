# RULE-OPERACIONAL-INFRA-008 — Minutes elapsed between two dates

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | operacional-infra |

## Rule

Computes whole minutes between two ISO/date strings as (date1 - date2), floored.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| date1 | string | date/datetime | - |
| date2 | string | date/datetime | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| diffMins | number | minutes |

## Logic

```text
d1 = new Date(date1); d2 = new Date(date2)
diffMs = (+d1) - (+d2)                 # date1 minus date2 (can be negative)
diffMins = Math.floor(diffMs / 1000 / 60)
return diffMins
```

## Edge cases (as implemented)

Sign convention is date1-date2 (negative if date1 earlier). Uses Math.floor, so negative differences round toward -Infinity (e.g. -0.5 min -> -1). No null/NaN guard; invalid date -> NaN result.

## Verification

- Verdict: UNVERIFIABLE
- Reference: No authoritative published reference. Whole-minutes-between-two-instants via floored millisecond difference is a generic time primitive.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/minutesBetweenDates.ts` | 1-9 | `f9656be2` | primary |

- Merged from: RULE-scheduling-FE-02-003

## Notes

Reusable time-window primitive (likely used for medication/observation timing). Sign and floor convention are load-bearing.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
