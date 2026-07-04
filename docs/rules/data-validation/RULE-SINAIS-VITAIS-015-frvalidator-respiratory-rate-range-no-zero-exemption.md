# RULE-SINAIS-VITAIS-015 — FRValidator — respiratory rate range, no zero exemption

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
FR (respiratory rate) must be between 0 and 50 inclusive. Applied on dados_prontuario.fr.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| fr | int | breaths/min (ipm) | 0-50 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= fr <= 50): RAISE ValidationError(f"{fr} deve estar entre 0 e 50")
```

## Edge cases (as implemented)
No zero exemption (0 breaths/min = apnea is representable); 55 -> error. Test test_limites_parametros.py:50-52.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 108-117 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 66 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-012, RULE-val-BE-10-077
- Related rules: RULE-SINAIS-VITAIS-005

## Notes
Physician form leaves FR unbounded (RULE-SINAIS-VITAIS-005 divergence); movimentacao form bounds it 0-50 (matches).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
