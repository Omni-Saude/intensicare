# RULE-SINAIS-VITAIS-023 — TemperaturaValidator — body temperature range, zero exempted

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Temperature must be between 20 and 43 (Celsius) inclusive, UNLESS exactly 0 (exempted). Applied on dados_prontuario.temperatura.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| temperatura | float | Celsius | 0 (exempt) or 20-43 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF temperatura != 0 AND NOT (20 <= temperatura <= 43): RAISE ValidationError(f"{temperatura} deve estar entre 20 e 43")
```

## Edge cases (as implemented)
0 allowed (sentinel/"not measured"), even though 0C is not physiologically plausible; 45 -> error. Test test_limites_parametros.py:82-84.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 220-232 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 97-99 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-020, RULE-val-BE-10-084
- Related rules: RULE-SINAIS-VITAIS-003, RULE-SINAIS-VITAIS-005

## Notes
Movimentacao form temperature input is 20-43 (matches, no zero-exemption on FE); physician form leaves temperature unbounded (RULE-SINAIS-VITAIS-005 divergence).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
