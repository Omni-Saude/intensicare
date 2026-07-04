# RULE-SINAIS-VITAIS-031 — SedativoValidator — sedative dose range, no zero exemption

| Field | Value |
|---|---|
| Category | drug-dosing |
| Type | validation |
| Status | DISCREPANCY |
| Verification | DISCREPANCY |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Sedative dosing value/quantity must be between 0 and 30 inclusive. Defined in validators.py and applied on the Sedativo model.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| sedativo/quantidade | int | ml (unit not stated in validator) | 0-30 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= sedativo <= 30): RAISE ValidationError(f"{sedativo} deve estar entre 0 e 30")
```

## Edge cases (as implemented)
No zero exemption; 31 -> error. Test test_limites_parametros.py:127-134 asserts quantidade=31 raises.

## Divergence
Test-vs-name discrepancy (backend-internal): the test method is named test_sedativo_entre_0_e_200 but the SedativoValidator max is 30 (and the test asserts 31 raises). The "0 e 200" in the test name is wrong; the actual enforced bound is 0-30. The two captures (validators.py definition and sedativo.py application) agree on 0-30.

## Verification
- Verdict: DISCREPANCY
- Reference: No single authoritative reference: "sedativo" is a drug CLASS (midazolam, propofol, dexmedetomidine, fentanyl, etc.), each with distinct units and dose ranges, so a generic 0-30 bound has no external clinical anchor. The flagged discrepancy is backend-internal (test naming vs enforced bound).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 341-352 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/sedativo.py` | 18-20 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-028, RULE-val-BE-10-095

## Notes
DISCREPANCY preserved from the model-field capture (misnamed test). Sedation overdose criterion flags a single dose >15 (cross-cluster RULE-sedacao-BE-10-011), within 0-30.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
