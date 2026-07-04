# RULE-NUTRICAO-001 — BMI (IMC) auto-calculation

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | VERIFIED (impact: none) |
| Confidence | high |
| Cluster | nutricao |

## Rule
Body Mass Index is computed live as weight divided by height squared whenever height (altura, meters) or weight (peso, Kg) changes in the nutritionist Global Assessment fieldset, and written read-only to the imc field rounded to 2 decimals.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| altura | number | m | 0-3 |
| peso | number | kg |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| imc | string (fixed 2 decimals) | kg/m^2 |

## Logic
```text
on altura change (value = new altura):
  imc = (peso / (value * value)) || 0
  setFieldsValue(avaliacao_global.imc = imc.toFixed(2))
on peso change (value = new peso):
  imc = (value / Math.pow(altura, 2)) || 0
  setFieldsValue(avaliacao_global.imc = imc.toFixed(2))
# IMC = peso / altura^2   (standard BMI, altura in meters, peso in kg)
```

## Edge cases (as implemented)
Division-by-zero / missing inputs handled by `|| 0`: if numerator is 0 or result is NaN (e.g. altura undefined -> Math.pow(undefined,2)=NaN), imc falls back to 0 -> "0.00". However if peso>0 and altura==0, peso/0 = Infinity, and Infinity||0 = Infinity -> imc.toFixed(2) = "Infinity" (not guarded). imc stored as a STRING via toFixed. altura constrained to [0,3] by field rules (RULE-NUTRICAO-008); peso has no range rule; imc field is disabled (read-only).

## Verification
- Verdict: VERIFIED (impact: none)
- Reference: WHO / standard Body Mass Index (Quetelet index): BMI = weight(kg) / height(m)^2

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/FieldsetAvGlobalNutricionista/FieldsetAvGlobalNutricionista.tsx | 43-90 | f9656be2 | primary |

- Merged from: RULE-nutricao-FE-04-029
- Related rules: RULE-NUTRICAO-008

## Notes
Verified against source lines 43-90. Formula matches standard BMI. The "Infinity" string when altura=0 & peso>0 is a minor unguarded edge but the formula itself is correct, so status OK. Frontend-only; no backend IMC counterpart in this cluster.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
