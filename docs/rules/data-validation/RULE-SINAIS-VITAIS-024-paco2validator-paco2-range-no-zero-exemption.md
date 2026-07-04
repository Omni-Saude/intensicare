# RULE-SINAIS-VITAIS-024 — PaCO2Validator — PaCO2 range, no zero exemption

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
PaCO2 must be between 0 and 150 inclusive. Applied on dados_prontuario.paco2.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| paco2 | float | mmHg | 0-150 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= paco2 <= 150): RAISE ValidationError(f"{paco2} deve estar entre 0 e 150")
```

## Edge cases (as implemented)
No zero exemption; 155 -> error. Test test_limites_parametros.py:86-88.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 235-246 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 100-102 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-021, RULE-val-BE-10-085
- Related rules: RULE-SINAIS-VITAIS-002

## Notes
Frontend movimentacao PaCO2 input 0-150 (matches).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
