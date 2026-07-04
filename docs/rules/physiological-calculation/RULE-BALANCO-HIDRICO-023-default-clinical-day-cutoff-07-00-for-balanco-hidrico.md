# RULE-BALANCO-HIDRICO-023 — Default clinical-day cutoff (07:00) for balanco hidrico

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | threshold |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
When no 'dia' query parameter is supplied, the fluid-balance day defaults to "today" if the current wall-clock hour is 07:00 or later, otherwise it defaults to "yesterday". This encodes a 24h clinical-day boundary starting at 07:00 rather than midnight.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| now.hour | hour (0-23, local/aware time) | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| dia_param | — | — |

## Logic
```text
now = datetime.now().astimezone()
if now.hour >= 7:
    dia_param = now.date()
else:
    dia_param = now.date() - timedelta(days=1)
```

## Edge cases (as implemented)
Boundary is inclusive at hour==7 (>=7 counts as "today"). Uses server/local timezone via astimezone() with no explicit timezone parameter - relies on system default tz.

## Verification
- Verdict: UNVERIFIABLE
- Reference: Nursing 07:00-to-07:00 (day/night 12h shift) clinical-day convention. This is a widely used institutional/operational nursing-shift convention (7-to-7), not a published clinical guideline with a mandated cutoff; the exact boundary is facility-configurable and not fixed by any authoritative standard. (n/a)
- Test vectors: 3/3 match
- Operational clinical-day boundary (07:00). Internally consistent with the same 7-to-7 window used across all balanco 24h aggregations. No authoritative published source fixes 07:00 as THE boundary (it is a nursing-shift convention; other sites use 06:00/08:00/midnight). Flag for internal review; not a clinical error. Uses system-default tz via astimezone() with no explicit tz (worth internal note).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/views/balanco_hidrico.py | 32-37 | 8166c07e | primary |
- Merged from: RULE-balanco-BE-08-005
- Related rules: RULE-BALANCO-HIDRICO-024, RULE-BALANCO-HIDRICO-027, RULE-BALANCO-HIDRICO-035

## Notes
Same 07:00 cutoff concept is reimplemented differently (and with a bug) in list() - see RULE-balanco-BE-08-007.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
