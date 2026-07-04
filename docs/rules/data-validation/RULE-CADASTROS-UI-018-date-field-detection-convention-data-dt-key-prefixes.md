# RULE-CADASTROS-UI-018 — Date-field detection convention (data_ / dt_ key prefixes)

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
Convention used to auto-detect which object fields are dates for serialization/parsing: any key whose name CONTAINS "data_" or "dt_" is treated as a date. Two variants convert such fields either to moment objects (inbound) or to formatted date strings (outbound).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| obj | object |  |  |
| keys | string[] |  | default ["data_","dt_"] |
| format | string |  | string variant only, default "YYYY-MM-DD" |

## Outputs

| name | type | unit |
|---|---|---|
| transformedObj | object \| null |  |

## Logic

```text
isDateKey(key) = keys.some(k => key.includes(k))
# moment variant (dateTreatmentMoment):
if obj is not Array:
  for [key,value] in entries(obj) WHERE value is truthy:   # falsy values dropped
    if isDateKey(key): out[key] = moment(value)
    elif typeof value == "object": out[key] = recurse(value)
    else: out[key] = value
  return out
else return obj
# string variant (dateTreatmentString):
if obj is not Array:
  for [key,value] in entries(obj):                          # no pre-filter
    if isDateKey(key): out[key] = value && moment(value).format(format)
    elif value && typeof value=="object": out[key]=recurse(value)
    else: out[key]=value
  return keys(out).length>0 ? out : null                    # empty -> null
else return obj
```

## Edge cases (as implemented)

Arrays are returned unchanged (not traversed element-wise). Moment variant drops all falsy-valued keys via .filter; string variant keeps them but guards format with `value &&`. String variant returns null when the resulting object is empty; moment variant returns {}. Recursion call omits the custom keys/format args, so nested objects always use the defaults.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dateTreatmentString.ts` | 3-29 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-validation-FE-02-006`

**Related rules:** _none_

## Notes

Two implementations of the same convention: dateTreatmentMoment.ts:3-26 (inbound, ->moment) and dateTreatmentString.ts:3-29 (outbound, ->string). Behavioral differences noted in edge_cases; treat as a paired rule.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
