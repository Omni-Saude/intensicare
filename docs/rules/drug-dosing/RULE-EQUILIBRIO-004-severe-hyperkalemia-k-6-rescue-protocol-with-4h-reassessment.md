# RULE-EQUILIBRIO-004 — Severe hyperkalemia (K>6) rescue protocol with 4h reassessment (criterio 9)

| Field | Value |
|---|---|
| Category | drug-dosing |
| Type | workflow |
| Status | OK |
| Verification | DISCREPANCY, impact: low |
| Confidence | high |
| Cluster | equilibrio |

## Rule
Emergency treatment protocol for severe hyperkalemia (equilibrio criterio_9), with a timed reassessment and escalation branch at +4h.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| potassio serico | float | mEq/L (labelled mg/dl in source) | — |
| peso | float | kg | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| medication protocol | string | — |

## Logic
```text
IF K > 6 (hipercalemia grave):
  Gluconato de Calcio 1 ampola EV;
  Furosemida 20 mg, 3 ampolas EV em bolus;
  solucao polarizante (insulina + soro glicofisiologico);
  3 doses inalatorias de 10 gotas de fenoterol OU salbutamol, de 15 em 15 min.
Reavaliar potassio serico apos 4h:
  IF K > 5.5 (source writes "5,5mg/dl") ->
    repetir o esquema anterior
    + Bicarbonato de sodio 8,4%, 1 ml/kg de peso
    + Sorcal (via oral apenas), 1 envelope de 15 g, 8/8h.
```

## Edge cases (as implemented)
Initial trigger K > 6; reassessment/escalation threshold K > 5.5 at +4h. Source writes the potassium unit as "mg/dl" (should be mEq/L or mmol/L) - reproduced verbatim, NOT corrected. Bicarbonate dose is 1 ml/kg of 8.4% solution. Sorcal restricted to oral route.

## Verification
- Verdict: DISCREPANCY (impact: low)
- Reference: KDIGO conference summary "Acute hyperkalemia in the emergency department" (Eur J Emerg Med 2020;27(5):329-337, PMC7448835); Mount DB, Sterns RH. Treatment of hyperkalemia (UpToDate); Medscape Hyperkalemia Treatment (emedicine.medscape.com/article/240903-treatment). Standard emergency bundle: calcium (membrane stabilization), insulin+glucose and nebulized beta-agonist and bicarbonate (intracellular shift), loop diuretic + cation-exchange resin (removal). (https://pmc.ncbi.nlm.nih.gov/articles/PMC7448835/)
- Test vectors: 4/5 match
- Protocol content matches the reference emergency-hyperkalemia bundle on all dimensions: calcium gluconate (membrane stabilization), insulin+glycophysiologic polarizing solution and nebulized fenoterol/salbutamol and sodium bicarbonate 8.4% at 1 ml/kg (= 1 mEq/kg, standard) for intracellular shift, furosemide for renal excretion, and Sorcal (calcium polystyrene sulfonate, oral cation-exchange resin) for gut removal. The single discrepancy is a UNIT MISLABEL: the source writes the potassium unit as "mg/dl" ("5,5mg/dl") whereas the correct unit is mEq/L (mmol/L). Clinical impact LOW: the numeric thresholds 6 and 5.5 are the correct values in mEq/L and the predicate fires on the upstream mEq/L value, so the mislabel is cosmetic/display-only with no downstream conversion - but it is a genuine unit error versus the reference and is exactly the class of defect this audit targets, so it is characterized rather than dismissed. Threshold nuance (some references define "severe" as K>6.5 or >7.0 with ECG changes rather than >6) is source-dependent and not scored as a discrepancy. Extraction already flagged the mg/dl label in edge_cases; this verification confirms it against the reference.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/facade/trilha_equilibrio.py | 64-73 | 8166c07e | primary |
| ahlabs-trilhas | trilha_automatica/facade/equilibrio.py | 1-4 | 8166c07e | duplicate |

- Merged from: RULE-equilibrio-BE-01-010
- Related rules: RULE-EQUILIBRIO-001, RULE-EQUILIBRIO-002, RULE-EQUILIBRIO-003

## Notes
verify=true: category drug-dosing + hyperkalemia emergency management is a well-published protocol (calcium gluconate, insulin+glucose, beta-agonist, furosemide, bicarbonate, cation exchange resin). criterio_9 (which drives the "vermelho" color in RULE-EQUILIBRIO-003) bundles both the initial K>6 measures and the +4h K>5.5 escalation into one recommendation string. Doses/units preserved verbatim.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
