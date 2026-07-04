# RULE-SINAIS-VITAIS-012 — PeepValidator — PEEP range, no zero exemption

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
PEEP (positive end-expiratory pressure) must be between 0 and 40 inclusive. Applied on dados_prontuario.peep.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| peep | float | cmH2O | 0-40 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= peep <= 40): RAISE ValidationError(f"{peep} deve estar entre 0 e 40")
```

## Edge cases (as implemented)
0 is a valid PEEP (no positive pressure); 45 -> error. Test test_limites_parametros.py:38-40.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 72-81 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 47-49 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-009, RULE-val-BE-10-074

## Notes
Cross-file discrepancy noted at seed time: utils/popular_banco.py valores_maximos_atributos uses an upper bound of 41 for peep (not 40) — tracked separately as RULE-seed-BE-11-031 (out of this cluster). Frontend movimentacao PEEP input is 0-40 (matches).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
