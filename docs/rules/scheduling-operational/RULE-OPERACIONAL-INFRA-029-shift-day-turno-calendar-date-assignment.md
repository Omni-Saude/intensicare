# RULE-OPERACIONAL-INFRA-029 — Shift-day (turno) calendar-date assignment

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Given a timestamp and a work-shift defined by a start hour and end hour, returns the same timestamp shifted to the calendar day the shift belongs to. Handles overnight shifts (end <= start means the shift crosses midnight, so the end is on the next day). If the timestamp's time-of-day is inside the shift window it is left unchanged; if it is before the shift start it is moved back one day; if after the shift end it is moved forward one day.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| currentMoment | moment.Moment | - | - |
| startHour | string | HH:mm | - |
| endHour | string | HH:mm | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| adjustedMoment | moment.Moment | - |

## Logic

```text
start = moment(startHour, "HH:mm")
end   = moment(endHour, "HH:mm")
if end.isBefore(start) OR end.isSame(start):
    end = end.add(1 day)                      # overnight or full-24h shift
currentHour = moment(currentMoment.format("HH:mm"), "HH:mm")   # today's date @ current time-of-day
if currentHour.isBetween(start, end):         # moment isBetween is EXCLUSIVE of both bounds
    return currentMoment                       # unchanged
elif currentHour.isBefore(start):
    return currentMoment.subtract(1 day)
elif currentHour.isAfter(end):
    return currentMoment.add(1 day)
else:
    return currentMoment
```

## Edge cases (as implemented)

isBetween is exclusive: a time exactly equal to start or end is NOT "between" and falls to the else branch (returned unchanged) since it is neither strictly before start nor strictly after end. When end<=start the end is pushed to +1 day, so "isAfter(end)" can essentially never trigger for an overnight shift (end is tomorrow), meaning only same-day / previous-day mapping occurs. Mutates currentMoment in place (moment .add/.subtract are mutating).

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dateTurn.ts` | 3-25 | `f9656be2` | primary |

- Merged from: RULE-scheduling-FE-02-001
- Related rules: RULE-OPERACIONAL-INFRA-035, RULE-OPERACIONAL-INFRA-049, RULE-OPERACIONAL-INFRA-034

## Notes

Core shift/turno logic used to bucket clinical records into the correct shift day. Boundary semantics (exclusive isBetween) are non-obvious; reproduce exactly.


RECONCILIATION FINDING (no divergence, no merge performed — distinct call sites preserved): traced the generic dateTurn(currentMoment,startHour,endHour) utility against the backend's data_7_as_7 (RULE-OPERACIONAL-INFRA-035) for the specific case startHour=endHour="7:00" used at RULE-OPERACIONAL-INFRA-034/049. Both independently resolve to: hour>=07:00 -> current calendar day; hour<07:00 -> previous calendar day. No behavioral difference was found between the BE simple-threshold implementation and the FE moment.isBetween-based implementation for this boundary case.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
