# RULE-OPERACIONAL-INFRA-049 — Nursing-shift day window 07:00-07:00

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The prescription screen operates on a nursing shift running 07:00 to 07:00 (24h window starting at 7am). The selected "day" of prescriptions is derived by mapping the current moment into the shift-day: times before 07:00 belong to the previous calendar day. The UI label reads "Turno vigente: 7:00 as 7:00".

## Inputs

| name | type | unit | range |
|---|---|---|---|
| currentMoment | moment (now) |  |  |
| startHour | string | HH:mm |  |
| endHour | string | HH:mm |  |

## Outputs

| name | type | unit |
|---|---|---|
| shiftDay | moment (date used as dia=YYYY-MM-DD filter) |  |

## Logic

```text
date = dateTurn(moment(), "7:00", "7:00")   # start == end
dateTurn(currentMoment, startHour, endHour):
  start = moment(startHour,"HH:mm"); end = moment(endHour,"HH:mm")
  if (end.isBefore(start) || end.isSame(start)) end.add(1,"day")   # 7:00==7:00 -> end pushed +1 day
  currentHour = moment(now.format("HH:mm"),"HH:mm")
  if (currentHour.isBetween(start,end)) return currentMoment
  else if (currentHour.isBefore(start))  return currentMoment.subtract(1,"day")
  else if (currentHour.isAfter(end))     return currentMoment.add(1,"day")
  else return currentMoment
# Prescriptions fetched with { dia: date.format("YYYY-MM-DD") }.
```

## Edge cases (as implemented)

Because start==end=="7:00", end is bumped to next day so the window is [07:00, 07:00+1d]. isBetween is exclusive of endpoints: exactly 07:00 is neither before start nor between, and not after end (end is 07:00 next day), so the final else returns currentMoment unchanged. Comparisons use HH:mm only (date component stripped for the hour test).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/Prescricoes/Prescricoes.tsx` | 49-49 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-turno-FE-04-015`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-029](RULE-OPERACIONAL-INFRA-029-shift-day-turno-calendar-date-assignment.md)
- [RULE-OPERACIONAL-INFRA-034](RULE-OPERACIONAL-INFRA-034-shift-turnover-virada-de-turno-cutoff-for-date-navigation.md)
- [RULE-OPERACIONAL-INFRA-035](RULE-OPERACIONAL-INFRA-035-data-7-as-7-7am-to-7am-shift-reporting-day-boundary.md)

## Notes

dateTurn algorithm defined in src/utils/dateTurn.ts (cross-partition). Also passed to CustomDatePicker dateTurnProps {start:"7:00", end:"7:00"} (lines 282-285). Label at line 287-289.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
