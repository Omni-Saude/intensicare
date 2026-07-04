# RULE-BALANCO-HIDRICO-061 — Required HH:MM 24h event-time (fluid balance)

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Fluid-balance "Horario" field masked 00:00 and validated as strict 24h HH:MM; unlike RULE-003 the regex does NOT permit an empty value.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| horario | string (masked) | HH:MM | 00:00-23:59 |

## Outputs

| name | type | unit |
|---|---|---|
| valid | boolean |  |

## Logic

```text
mask = "00:00"
regex = /^([01][0-9]|2[0-3]):([0-5][0-9])$/   // no empty-string alternative
```

## Edge cases (as implemented)

Empty value FAILS here (no `|` empty branch), whereas the discipline-form exit-time regex (RULE-003) allows empty.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormBalancoHidrico.ts` | 293-299 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-time-FE-01-004`

**Related rules:** _none_

## Notes

Same regex repeated at dataFormBalancoHidrico.ts:459-465 (saida) and 638-644 (sinais vitais). DISCREPANCY = two divergent time regexes coexist in the codebase (empty allowed vs not). Referenced as "RULE-004" by the intake/output decision-tree rules RULE-BALANCO-HIDRICO-029 and RULE-BALANCO-HIDRICO-031, which span these source lines but do not themselves capture this time-mask validation.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
