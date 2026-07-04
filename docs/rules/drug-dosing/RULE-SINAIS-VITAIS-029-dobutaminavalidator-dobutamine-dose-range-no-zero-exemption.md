# RULE-SINAIS-VITAIS-029 — DobutaminaValidator — dobutamine dose range, no zero exemption

| Field | Value |
|---|---|
| Category | drug-dosing |
| Type | validation |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | sinais-vitais |

## Rule
Dobutamine dosing value must be between 0 and 30 inclusive. Applied on dados_prontuario.dobutamina.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dobutamina | float | ml/h (mcg/kg/min per some captures; unit not stated in code) | 0-30 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= dobutamina <= 30): RAISE ValidationError(f"{dobutamina} deve estar entre 0 e 30")
```

## Edge cases (as implemented)
No zero exemption (0 = drug not running is valid); 35 -> error. Test test_limites_parametros.py:114-116.

## Verification
- Verdict: UNVERIFIABLE
- Reference: Dobutamine IV infusion (Pfizer/USP label; Drugs.com dosage monograph). Maintenance 2-20 mcg/kg/min; usual effective 2.5-15 mcg/kg/min; maximum 40 mcg/kg/min (rarely required). SOFA cardiovascular uses "dobutamine any dose".

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 310-322 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 132-138 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-026, RULE-val-BE-10-091

## Notes
Unit is not documented in code (model-field capture said ml/h, validators.py capture inferred mcg/kg/min). SOFA/estabilidade criteria compare dobutamina>0 or >10 (both within 0-30).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
