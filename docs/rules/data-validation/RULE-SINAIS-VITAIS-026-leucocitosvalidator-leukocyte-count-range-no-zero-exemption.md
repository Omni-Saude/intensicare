# RULE-SINAIS-VITAIS-026 — LeucocitosValidator — leukocyte count range, no zero exemption

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Leukocyte count must be between 0 and 40000 inclusive. Applied on dados_prontuario.leucocitos.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| leucocitos | float | /mm3 | 0-40000 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= leucocitos <= 40000): RAISE ValidationError(f"{leucocitos} deve estar entre 0 e 40000")
```

## Edge cases (as implemented)
No zero exemption; 41000 -> error. Test test_limites_parametros.py:94-96.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 264-276 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 106-108 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-023, RULE-val-BE-10-087
- Related rules: RULE-SINAIS-VITAIS-002

## Notes
Leukocytes is a SIRS input; range is plausibility-only. Frontend movimentacao input 0-40000 (matches).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
