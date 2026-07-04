# RULE-AUDITORIA-LOGS-001 — Date-range filter boundary formula (start-of-day / end-of-day)

| Field | Value |
|---|---|
| Cluster | auditoria-logs |
| Category | data-validation |
| Type | formula |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
When the 'criado_em__gte'/'criado_em__lte' filters are supplied, the parsed date is combined with time.min (00:00:00) for the lower bound and time.max (23:59:59.999999) for the upper bound, so the range is inclusive of the entire day on both ends.

## Inputs

| name | type | unit |
|---|---|---|
| criado_em__gte / criado_em__lte (date string) | string | n/a |

## Outputs

| name | type | unit |
|---|---|---|
| criado_em__gte / criado_em__lte (datetime) | datetime | n/a |

## Logic

```text
if chave == "criado_em__gte":
    valor = datetime.combine(parse_date_to_iso(valor), time.min)
elif chave == "criado_em__lte":
    valor = datetime.combine(parse_date_to_iso(valor), time.max)
```

## Edge cases (as implemented)

parse_date_to_iso (utils/handlers.py) accepts multiple date formats (MM/YYYY, YYYY-MM, DD/MM/YYYY, YYYY-MM-DD, or a generic dateutil.parse fallback); an ambiguous/garbled date string falls through to dateutil's best-effort parse.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative clinical/published reference applies. This is an internal software date-range-filter boundary convention (inclusive start-of-day / end-of-day). Only cross-checkable against the Python standard library datetime documentation (datetime.time.min = 00:00:00, datetime.time.max = 23:59:59.999999, datetime.combine(date, time)). ([source](https://docs.python.org/3/library/datetime.html#datetime.time.max))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | ok — lower bound combined with time.min (00:00:00.000000), upper bound with time.max (23:59:59.999999); inclusive of the entire day on both ends, consistent with the rule description. Verified against legacy source log/views/log.py lines 41-45 and utils/handlers.py parse_date_to_iso. |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| criado_em__gte=2026-07-03 (YYYY-MM-DD) | start-of-day inclusive -> 2026-07-03 00:00:00.000000 | datetime.combine(2026-07-03, time.min) = 2026-07-03 00:00:00.000000 | yes |
| criado_em__lte=2026-07-03 (YYYY-MM-DD) | end-of-day inclusive -> 2026-07-03 23:59:59.999999 | datetime.combine(2026-07-03, time.max) = 2026-07-03 23:59:59.999999 | yes |
| criado_em__lte=03/07/2026 (DD/MM/YYYY) | parsed to 2026-07-03, end-of-day inclusive 2026-07-03 23:59:59.999999 | parse_date_to_iso('03/07/2026')=2026-07-03; combine time.max = 2026-07-03 23:59:59.999999 | yes |
| boundary=log row at exactly 2026-07-03 23:59:59.999999, filter criado_em__lte=2026-07-03 | included (<= end-of-day) | included; a row at 2026-07-04 00:00:00 would be excluded | yes |
| edge_quirk=criado_em__gte='07/2026' (MM/YYYY) | n/a — no reference defines month-only semantics | strptime('%m/%Y') yields day=1 -> 2026-07-01 00:00:00; a month filter resolves to only the FIRST day of the month, not the whole month (documented quirk, no reference to violate) | yes |

**Verifier notes**

Internal business rule (audit-log date-range filter), not a clinical scale or calculator — no authoritative published clinical reference exists, so flagged for internal review rather than treated as wrong. Legacy behavior confirmed verbatim against log/views/log.py (lines 41-45) and utils/handlers.py parse_date_to_iso. Technically consistent with documented Python datetime semantics: inclusive of the full day on both bounds. One non-clinical quirk worth internal note: because parse_date_to_iso maps MM/YYYY and YYYY-MM to the first day of the month (day=1), a month-granularity filter collapses to a single day rather than the whole month; and dateutil.parse fallback on a garbled string is best-effort. Neither affects any clinical computation.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `log/views/log.py` | 40-46 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-log-BE-13-018`

**Related rules:**

- [RULE-AUDITORIA-LOGS-030](RULE-AUDITORIA-LOGS-030-allowed-log-list-filter-fields-whitelist.md)

## Notes

parse_date_to_iso itself lives in utils/handlers.py (outside log/*), cited only as supporting evidence.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
