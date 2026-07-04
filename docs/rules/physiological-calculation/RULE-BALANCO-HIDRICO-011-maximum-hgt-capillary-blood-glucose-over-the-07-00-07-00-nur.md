# RULE-BALANCO-HIDRICO-011 — Maximum HGT (capillary blood glucose) over the 07:00-07:00 nursing day

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: low |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Highest recorded capillary glucose (HGT = hemoglicoteste, SinaisVitais.hgt) for an attendance over the 07:00-07:00 nursing day. MAX of per-window maxima.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| horario_ref | — | — | — |
| nr_atendimento | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| hgt_max_24h | — | mg/dL |

## Logic
```text
windows built exactly as RULE-...-003 but on SinaisVitais.
valores = [ Max(qs1.hgt), Max(qs2.hgt) ]
remove None; valores.sort(); return valores[-1] if valores else None
```

## Edge cases (as implemented)
Same as RULE-...-004 (max, None-strip, month-agnostic __day, unsatisfiable else qs2).

## Divergence
Same window+Max defect as RULE-BALANCO-HIDRICO-010, on SinaisVitais.hgt (capillary glucose, mg/dL).

## Verification
- Verdict: DISCREPANCY (impact: low)
- Reference: No authoritative published clinical reference governs a "max capillary glucose over the 07:00-07:00 nursing day" aggregation helper — this is an internal data-rollup rule. Only the externally-referenced dimension (unit) is checkable: HGT (hemoglicoteste / point-of-care capillary blood glucose) is recorded in mg/dL in Brazilian ICUs. Reddy et al., "Accuracy of point-of-care capillary blood sugar measurements in critically ill patients" (POC glucose reported in mg/dL). (https://pmc.ncbi.nlm.nih.gov/articles/PMC11245140/)
- Test vectors: 1/3 match
- Extraction-flagged DISCREPANCY confirmed, but it is a TEMPORAL-WINDOW code defect, not a unit/coefficient/clinical-formula error. Two defects: (1) criado_em__day matches day-of-month only, so cross-month readings contaminate the max; (2) in the hour>=7 branch qs2's predicate `criado_em==horario_ref AND hour<7` is unsatisfiable, so the current day's 00:00-07:00 segment of the nursing day is silently dropped. Unit dimension (mg/dL, no conversion) is correct — no mg/dL-vs-mmol/L mismatch. Clinical impact rated LOW: this is a display/indicator rollup and clinicians still see the raw HGT readings; a missed or stale peak-glucose indicator is unlikely on its own to drive management. There is NO published reference for the 07:00-07:00 window shape itself (internal nursing-day convention) — flag the window construction for internal engineering review.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/utils.py | 177-209 | 8166c07e | primary |
- Merged from: RULE-balancohidrico-BE-09-005
- Related rules: RULE-BALANCO-HIDRICO-006, RULE-BALANCO-HIDRICO-010, RULE-BALANCO-HIDRICO-012, RULE-BALANCO-HIDRICO-028

## Notes
DISCREPANCY inherited from shared window helper. HGT (hemoglicoteste) is the Brazilian term for point-of-care capillary blood glucose.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
