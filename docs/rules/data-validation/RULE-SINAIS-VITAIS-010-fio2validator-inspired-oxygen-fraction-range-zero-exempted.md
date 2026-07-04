# RULE-SINAIS-VITAIS-010 — FiO2Validator — inspired oxygen fraction range, zero exempted

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
FiO2 (%) must be between 21 and 100 inclusive, UNLESS exactly 0 (treated as not-applicable/not-measured and exempted). Applied on the dados_prontuario.fio2 field.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| fio2 | float | percent | 0 (exempt) or 21-100 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF fio2 != 0 AND NOT (21 <= fio2 <= 100): RAISE ValidationError(f"{fio2} deve estar entre 21 e 100")
```

## Edge cases (as implemented)
0 explicitly allowed (means "not informed"); 5 -> error; non-numeric -> "deve ser um numero". Confirmed by test_limites_parametros.py:30-36 (fio2=5 raises, fio2=0 ok).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 46-55 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 44-46 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-007, RULE-val-BE-10-073
- Related rules: RULE-SINAIS-VITAIS-033, RULE-SINAIS-VITAIS-002

## Notes
21% approximates room-air FiO2 (physiological floor). The percentage range here (21-100) contrasts with fraction usage in P/F-ratio math (cross-cluster RULE-pfratio-BE-10-001). Structurally identical to SatO2Validator (RULE-SINAIS-VITAIS-033) but SatO2 has NO zero exemption AND is disabled. Frontend movimentacao FiO2 input is 21-100 (matches).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
