# RULE-OPERACIONAL-INFRA-034 — Shift-turnover (virada de turno) cutoff for date navigation

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | scheduling-operational |
| Type | threshold |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The generic date picker used across record-navigation screens disables selecting or advancing to any date beyond the current clinical shift-turnover boundary, computed via the shared dateTurn(now, "7:00", "7:00") utility (out of partition), effectively pinning the latest navigable "day" to the current shift.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| current (candidate date in the picker) | moment.Moment | date |  |
| date (currently selected date) | moment.Moment | date |  |
| dateTurnProps | { start: string; end: string } \| undefined |  |  |

## Outputs

| name | type |
|---|---|
| disabledDate (DatePicker) | boolean |
| disabled (next-day Button) | boolean |

## Logic

```text
cutoff = dateTurn(moment(), "7:00", "7:00")          // external util, out of partition
DatePicker.disabledDate(current) = current > cutoff
nextButton.disabled =
     !date
  OR date.isSame( dateTurnProps ? cutoff : moment(), "day" )
backButton.disabled = !date
onBack:  onBack(date - 1 day);  setDate(date - 1 day)
onNext:  onNext(date + 1 day);  setDate(date + 1 day)
```

## Edge cases (as implemented)

If dateTurnProps is not supplied, the "next" button's same-day check compares against plain moment() (now) instead of the shift-cutoff moment, so behavior differs depending on whether the caller passes dateTurnProps. No date is selected (date falsy) disables both back and next or renders the DatePicker unusable via allowClear={false} (no clearing once a date is chosen).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/CustomDatePicker/CustomDatePicker.tsx` | 20-65 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-turno-FE-05-001`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-029](RULE-OPERACIONAL-INFRA-029-shift-day-turno-calendar-date-assignment.md)
- [RULE-OPERACIONAL-INFRA-049](RULE-OPERACIONAL-INFRA-049-nursing-shift-day-window-07-00-07-00.md)
- [RULE-OPERACIONAL-INFRA-035](RULE-OPERACIONAL-INFRA-035-data-7-as-7-7am-to-7am-shift-reporting-day-boundary.md)

## Notes

dateTurn() itself is defined in src/utils/dateTurn.ts (out of this partition's scope), so the exact cutoff-time semantics (e.g. how "7:00","7:00" args resolve to a Moment) could not be verified here; behavior is inferred purely from this call site. Cross-reference for a verifier auditing utils/dateTurn.ts.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
