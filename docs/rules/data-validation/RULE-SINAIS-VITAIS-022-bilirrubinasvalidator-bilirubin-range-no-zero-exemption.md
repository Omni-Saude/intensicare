# RULE-SINAIS-VITAIS-022 — BilirrubinasValidator — bilirubin range, no zero exemption

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Bilirubin must be between 0 and 30 inclusive. Applied on dados_prontuario.bilirrubinas.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| bilirrubinas | float | mg/dL | 0-30 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= bilirrubinas <= 30): RAISE ValidationError(f"{bilirrubinas} deve estar entre 0 e 30")
```

## Edge cases (as implemented)
No zero exemption; 35 -> error. Test test_limites_parametros.py:78-80.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 204-217 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 94-96 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-019, RULE-val-BE-10-083
- Related rules: RULE-SINAIS-VITAIS-002

## Notes
Bilirubin is a SOFA input; range is plausibility-only. Frontend movimentacao input 0-30 (matches).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
