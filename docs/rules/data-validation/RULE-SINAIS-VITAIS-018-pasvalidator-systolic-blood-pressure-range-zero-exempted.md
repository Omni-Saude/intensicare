# RULE-SINAIS-VITAIS-018 — PASValidator — systolic blood pressure range, zero exempted

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
PAS (systolic blood pressure) must be between 50 and 250 inclusive, UNLESS exactly 0 (exempted, "not measured"). Applied on dados_prontuario.pas.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| pas | float | mmHg | 0 (exempt) or 50-250 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF pas != 0 AND NOT (50 <= pas <= 250): RAISE ValidationError(f"{pas} deve estar entre 50 e 250")
```

## Edge cases (as implemented)
0 allowed (sentinel); 255 -> error. Test test_limites_parametros.py:62-64.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 152-161 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 78-80 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-015, RULE-val-BE-10-080
- Related rules: RULE-SINAIS-VITAIS-001, RULE-SINAIS-VITAIS-005, RULE-SINAIS-VITAIS-019

## Notes
Frontend forms (movimentacao, physician) use min 50 with no zero-exemption, so the backend "0 = not measured" sentinel is not reachable via those number inputs (blank used instead). Numeric 50-250 bound matches the frontend.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
