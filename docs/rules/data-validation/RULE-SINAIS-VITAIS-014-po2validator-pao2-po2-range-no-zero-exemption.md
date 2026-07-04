# RULE-SINAIS-VITAIS-014 — Po2Validator — PaO2/PO2 range, no zero exemption

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
PO2 must be between 0 and 500 inclusive. Applied on dados_prontuario.po2.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| po2 | float | mmHg | 0-500 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= po2 <= 500): RAISE ValidationError(f"{po2} deve estar entre 0 e 500")
```

## Edge cases (as implemented)
No zero exemption; 505 -> error. Test test_limites_parametros.py:46-48.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 96-105 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 50-52 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-011, RULE-val-BE-10-075
- Related rules: RULE-SINAIS-VITAIS-002

## Notes
PaO2 feeds P/F ratio (cross-cluster RULE-pfratio-BE-10-001). Frontend movimentacao PO2 input 0-500 (matches).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
