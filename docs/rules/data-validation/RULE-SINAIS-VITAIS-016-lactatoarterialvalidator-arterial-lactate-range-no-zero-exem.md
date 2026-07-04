# RULE-SINAIS-VITAIS-016 — LactatoArterialValidator — arterial lactate range, no zero exemption

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Arterial lactate must be between 0 and 20 inclusive. Applied on dados_prontuario.lactato_arterial.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| lactato_arterial | float | mmol/L (mg/dl per some texts) | 0-20 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= lactato_arterial <= 20): RAISE ValidationError(f"{lactato_arterial} deve estar entre 0 e 20")
```

## Edge cases (as implemented)
No zero exemption; 25 -> error. Test test_limites_parametros.py:54-56.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 120-133 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 69-71 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-013, RULE-val-BE-10-078
- Related rules: RULE-SINAIS-VITAIS-002

## Notes
Lactate is a sepsis-severity input; range is plausibility-only. Frontend movimentacao lactate input 0-20 (matches).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
