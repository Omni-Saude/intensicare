# RULE-OPERACIONAL-INFRA-001 — Round timestamp to whole hour (get_hora_cheia / justOclock)

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | formula |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: low |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Cross-implementation copy of the same 'round a timestamp to a whole hour' rule: the backend (get_hora_cheia, used to label homecare balanco-hidrico/sinais-vitais records with an 'hora_cheia' field) and the frontend (justOclock, a standalone utility with no confirmed call site in this checkout) both round minute>30 up to the next hour and otherwise truncate down, formatting the result as 'H:00'. The two thresholds are written differently (BE: minute>=31 rounds up; FE: minute>30 rounds up) but are mathematically identical over integer minutes (both select exactly minutes 31-59) — reconciliation found NO behavioral divergence between the two sides on the rounding threshold itself.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| data (BE) / time (FE) | datetime \| string \| moment.Moment | - | any |

## Outputs

| Name | Type | Unit |
|---|---|---|
| hora_cheia (BE) / hourString (FE) | string | H:00 / HH:mm |

## Logic

```text
# BE: core/utils.py get_hora_cheia(data)
data = data.astimezone()             # convert to server local tz
if data.minute >= 31:
    hora_cheia = data.hour + 1
else:
    hora_cheia = data.hour
return f"{hora_cheia}:00"

# FE: src/utils/justOclock.ts justOclock(time)
hour   = moment(time).format("HH")     # "00".."23"
minute = moment(time).format("mm")     # "00".."59"
if (+minute > 30):
    return moment(`${(+hour) + 1}:00`, "HH:mm").format("HH:mm")
else:
    return moment(`${hour}:00`, "HH:mm").format("HH:mm")
```

## Edge cases (as implemented)

Both sides share the SAME unguarded overflow bug at the top of the day: when hour==23 and minute is in the rounds-up range, the computed hour becomes 24. BE returns the literal invalid string "24:00" (no day rollover / no modulo 24). FE constructs "24:00" via string interpolation then re-parses it with moment("24:00","HH:mm"), which moment parses leniently and rolls over to "00:00", silently dropping the date instead of raising or carrying the day forward. So the two sides even DIVERGE in how the shared bug manifests (BE: invalid string "24:00"; FE: silently wrong "00:00") even though the rounding threshold itself is identical. BE additionally applies data.astimezone() (server local tz) before rounding; FE has no explicit tz conversion and assumes the Moment is already in local time. No confirmed call site for justOclock exists anywhere in the frontend checkout (grep found only its own definition), so the FE side may be dead/unused code carried over from an earlier feature.

## Divergence

Both sides implement the same round-to-whole-hour rule with an equivalent minute>30/minute>=31 threshold (no behavioral difference there). However the shared 23:xx overflow bug resolves DIFFERENTLY per side: BE emits the literal out-of-range string "24:00"; FE's re-parse of the same string silently rolls over to "00:00" (day dropped). Neither side guards against the overflow.

## Verification

- Verdict: DISCREPANCY (clinical impact: low)
- Reference: ISO 8601-1:2019 time-of-day representation (hour range 00-23; 24:00 permitted ONLY as an end-of-day midnight marker, never as a labeled hour-of-day). Cross-checked against standard 'round half up' arithmetic convention (IEEE 754 roundTiesToAway / common commercial rounding).

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/utils.py` | 149-156 | `8166c07e` | primary |
| trilhas-frontend | `src/utils/justOclock.ts` | 3-11 | `f9656be2` | frontend-copy |

- Merged from: RULE-SCHED-BE-12-012, RULE-scheduling-FE-02-002
- Related rules: RULE-OPERACIONAL-INFRA-009

## Notes

MERGED: backend/frontend copies of the same 'round to whole hour' utility (Phase-1 IDs RULE-SCHED-BE-12-012 + RULE-scheduling-FE-02-002). BE notes (verbatim): DISCREPANCY - "24:00" overflow at 23:31-23:59 and non-standard :31 threshold (half-hour would round at :30).
FE notes (verbatim): Marked DISCREPANCY for two verbatim behaviors a reimplementer must preserve or consciously fix: (1) :30 rounds down (not standard "round half up"), (2) the 23:31-23:59 -> "24:00" -> "00:00" wraparound that silently drops the date.

Status DISCREPANCY is preserved (never downgraded) because each side independently carries an unguarded 23:xx-hour overflow; reconciliation additionally found the two sides' overflow OUTCOMES differ (see divergence field) even though the rounding threshold does not.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
