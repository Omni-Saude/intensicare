# RULE-OPERACIONAL-INFRA-035 — data_7_as_7 — 7am-to-7am shift/reporting-day boundary

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | scheduling-operational |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Computes the 'reporting day' used for shift-based aggregation: if the current local hour is 7 (07:00) or later, the reporting day is today's date; otherwise (before 07:00) it is yesterday's date.

## Inputs

_None._

## Outputs

| name | type | unit |
|---|---|---|
| data | date |  |

## Logic

```text
now = datetime.now().astimezone()
IF now.hour >= 7:
  RETURN now.date()
ELSE:
  RETURN now.date() - 1 day
```

## Edge cases (as implemented)

Uses the server/process local timezone via astimezone() with no explicit timezone parameter passed; Django project TIME_ZONE is 'America/Sao_Paulo' (trilhas/settings.py) but this function does not explicitly use Django's timezone-aware `django.utils.timezone.now()`, it uses the stdlib `datetime.now().astimezone()` — potential source of discrepancy if the OS/process timezone differs from the configured Django TIME_ZONE.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/handlers.py` | 226-229 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-util-BE-11-040`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-029](RULE-OPERACIONAL-INFRA-029-shift-day-turno-calendar-date-assignment.md)
- [RULE-OPERACIONAL-INFRA-049](RULE-OPERACIONAL-INFRA-049-nursing-shift-day-window-07-00-07-00.md)
- [RULE-OPERACIONAL-INFRA-034](RULE-OPERACIONAL-INFRA-034-shift-turnover-virada-de-turno-cutoff-for-date-navigation.md)

## Notes

Encodes a 7am-to-7am ICU shift/reporting-day convention, common in hospital operations (e.g. daily census counted at a fixed cutover hour rather than midnight).

See RULE-OPERACIONAL-INFRA-029 for the cross-implementation (BE vs FE) reconciliation of this exact 7am-to-7am boundary: confirmed behaviorally equivalent, no divergence found.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
