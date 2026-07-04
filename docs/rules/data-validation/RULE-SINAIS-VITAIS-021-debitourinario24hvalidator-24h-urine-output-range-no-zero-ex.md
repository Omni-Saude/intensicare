# RULE-SINAIS-VITAIS-021 — DebitoUrinario24hValidator — 24h urine output range, no zero exemption

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
24-hour urine output must be between 0 and 10000 inclusive. Applied on dados_prontuario.debito_urinario_24h.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| debito_urinario | float | mL/24h | 0-10000 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= debito_urinario <= 10000): RAISE ValidationError(f"{debito_urinario} deve estar entre 0 e 10000")
```

## Edge cases (as implemented)
No zero exemption (0 mL/24h = anuria is representable); 100005 -> error. Test test_limites_parametros.py:74-76.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 188-201 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 90-92 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-018, RULE-val-BE-10-082
- Related rules: RULE-SINAIS-VITAIS-003

## Notes
Frontend movimentacao urine input 0-10000 (matches).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
