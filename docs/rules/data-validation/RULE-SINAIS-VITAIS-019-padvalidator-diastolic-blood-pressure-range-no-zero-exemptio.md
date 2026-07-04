# RULE-SINAIS-VITAIS-019 — PADValidator — diastolic blood pressure range, no zero exemption

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
PAD (diastolic blood pressure) must be between 0 and 150 inclusive. Applied on dados_prontuario.pad.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| pad | float | mmHg | 0-150 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= pad <= 150): RAISE ValidationError(f"{pad} deve estar entre 0 e 150")
```

## Edge cases (as implemented)
No zero exemption, unlike PASValidator for the paired systolic reading; 155 -> error. Test test_limites_parametros.py:66-68.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 164-173 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 81-83 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-016, RULE-val-BE-10-081
- Related rules: RULE-SINAIS-VITAIS-001, RULE-SINAIS-VITAIS-005, RULE-SINAIS-VITAIS-018

## Notes
Internally inconsistent with PASValidator (systolic exempts 0, diastolic does not); recorded verbatim, not corrected. Frontend PAD input 0-150 (matches).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
