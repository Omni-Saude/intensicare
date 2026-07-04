# RULE-SINAIS-VITAIS-028 — PlaquetasValidator — platelet count range, no zero exemption

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Platelet count must be between 0 and 700000 inclusive. Applied on dados_prontuario.plaquetas.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| plaquetas | int | /mm3 | 0-700000 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= plaquetas <= 700000): RAISE ValidationError(f"{plaquetas} deve estar entre 0 e 700000")
```

## Edge cases (as implemented)
No zero exemption; 701000 -> error. Test test_limites_parametros.py:110-112.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 295-307 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 115-117 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-025, RULE-val-BE-10-090
- Related rules: RULE-SINAIS-VITAIS-002

## Notes
Platelets is a SOFA input; range is plausibility-only. Frontend movimentacao input 0-700000 (matches).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
