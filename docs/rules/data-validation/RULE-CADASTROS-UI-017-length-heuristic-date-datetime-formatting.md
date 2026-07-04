# RULE-CADASTROS-UI-017 — Length-heuristic date/datetime formatting

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Formats a raw value as datetime, date, or plain text based purely on the input string length (proxy for ISO datetime vs ISO date vs other).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| value | string |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| formatted | string |  |

## Logic

```text
if value.length >= 25:  return moment(value).format("DD/MM/YYYY HH:mm")   # ISO datetime w/ tz offset
elif value.length >= 10: return moment(value).format("DD/MM/YYYY")        # ISO date
else:                    return value.toString()                          # leave as-is
```

## Edge cases (as implemented)

Threshold 25 targets ISO strings with timezone offset (e.g. 2020-01-01T00:00:00+00:00); threshold 10 targets YYYY-MM-DD. A 10-24 char value is rendered date-only (time dropped). No validity check; a non-date >=10 chars still runs through moment.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/formatDataItem.ts` | 3-11 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-validation-FE-02-005`

**Related rules:** _none_

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
