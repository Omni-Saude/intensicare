# RULE-CLINICAL-SCORING-010 — Patient age from birthdate (integer days // 365)

| Field | Value |
|---|---|
| Cluster | clinical-scoring |
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
Computes patient age in whole years as the number of days elapsed since birth divided (floor) by 365.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| data_nascimento | date | calendar date | any past date, or falsy/None |

## Outputs

| name | type | unit |
|---|---|---|
| idade | integer\|null | years |

## Logic

```text
if not data_nascimento:
    return None            # no explicit return -> function returns None
idade = (timezone.now().date() - data_nascimento).days // 365
return idade if idade else 0   # if idade == 0 (falsy) return 0, else return idade
```

## Edge cases (as implemented)

Uses a fixed 365-day year (leap years ignored). Floor division truncates. Falsy birthdate (None/empty) returns None (not 0). Computed age of 0 (infants < ~1yr, or a future/same date giving 0) returns integer 0. A future birthdate yields a negative day-count // 365 (Python floor toward -inf) -> negative age is possible and returned as-is (only exact 0 is coerced). Uses server timezone via timezone.now().date().

## Divergence

DISCREPANCY vs standard age = calendar-year difference with leap-year/birthday adjustment. //365 slowly overcounts (real year 365.2425 days). Return type inconsistent (None vs int). No rounding to nearest; always floors.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Standard chronological age = completed calendar years between birthdate and the current date, i.e. (current_year - birth_year) minus 1 if the birthday has not yet occurred this year; the mean Gregorian year is 365.2425 days (leap-year rule). No single primary paper; this is the universal calendar-age definition (ISO 8601 / dateutil.relativedelta convention). ([source](https://en.wikipedia.org/wiki/Age_of_a_person))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | diff |
| units | ok |
| ranges | diff |
| rounding | diff |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| data_nascimento=1986-07-03; today=2026-07-03 | 40 | 40 | yes |
| data_nascimento=1986-07-04; today=2026-07-03 | 39 | 40 | no |
| data_nascimento=; today=2026-07-03 | undefined/error |  | no |
| data_nascimento=2027-07-03; today=2026-07-03 | 0/invalid | -1 | no |

**Verifier notes**

Dividing elapsed days by a fixed 365 (vs the true 365.2425-day mean year) makes each birthday register early: the code reaches the next integer age roughly 0.2425 days per year-of-age BEFORE the true anniversary, so within a narrow pre-birthday window the computed age is 1 year higher than the true completed-years age (e.g. reported 40 the day before the 40th birthday). It does not accumulate to a full extra year within a human lifespan (real elapsed days already include leap days, so ~1460 years would be needed to overcount by one). Additional deviations: (a) return-type inconsistency - falsy birthdate returns None while a computed age of 0 returns int 0; (b) a future birthdate yields a negative age (Python floor division toward -inf) returned as-is, with no guard. Clinical impact low: age used for scoring thresholds rarely changes management on a one-year, narrow-window boundary, but the None/negative return paths could break downstream numeric consumers.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/utils.py` | 51-54 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-PHYSIO-BE-12-001`

**Related rules:** _none_

## Notes

Single-source formula; no frontend/second-backend copy found in this cluster.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
