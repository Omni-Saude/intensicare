# RULE-BALANCO-HIDRICO-010 — Maximum temperature over the 07:00-07:00 nursing day

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Highest recorded body temperature (SinaisVitais.temperatura) for an attendance over the 07:00-07:00 nursing day. Takes the MAX of the per-window maxima.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| horario_ref | — | — | — |
| nr_atendimento | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| temperatura_max_24h | — | degrees Celsius |

## Logic
```text
windows built exactly as RULE-...-003 but on SinaisVitais.
valores = [ Max(qs1.temperatura), Max(qs2.temperatura) ]
remove all None from valores
valores.sort()
return valores[-1] if valores else None   # the largest of the two window maxima
```

## Edge cases (as implemented)
Same window defects as RULE-...-001. Aggregate is Max not Sum. Removes None entries then sorts ascending and returns last element (the maximum). Returns None if no readings.

## Divergence
Same window defect as RULE-BALANCO-HIDRICO-006, but aggregate is Max not Sum: valores=[Max(qs1.temperatura),Max(qs2.temperatura)], strip None, sort ascending, return last (the maximum); None if no readings.

## Verification
- Verdict: DISCREPANCY (impact: moderate)
- Reference: Maximum recorded body temperature over the 24h nursing day (Tmax) - a simple MAX aggregation. Fever thresholds (e.g. >=38.3 C) are applied downstream, not in this helper (O'Grady NP et al., Guidelines for evaluation of new fever in critically ill adult patients, SCCM/IDSA, Crit Care Med 2008;36:1330). No scored calculator here. (https://pubmed.ncbi.nlm.nih.gov/18379262/)
- Test vectors: 1/3 match
- Aggregation is MAX (not Sum) and 0->None does not apply. Discrepancy is the window: D2 drops the 00:00-07:00 night tail so a nocturnal fever spike (a key sepsis/infection trigger) can be missed, and D1 can import a spurious high temperature from the same day-number in another month. Missing or fabricating a fever peak on a clinical evolution display -> moderate.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/utils.py | 141-174 | 8166c07e | primary |
- Merged from: RULE-balancohidrico-BE-09-004
- Related rules: RULE-BALANCO-HIDRICO-006, RULE-BALANCO-HIDRICO-011, RULE-BALANCO-HIDRICO-012, RULE-BALANCO-HIDRICO-028

## Notes
DISCREPANCY inherited from shared window helper.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
