# RULE-SINAIS-VITAIS-032 — PressaoInspiratoriaValidator — inspiratory pressure (PINS) range, no zero exemption

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Inspiratory pressure (PINS) must be between 0 and 30 inclusive. Applied on dados_prontuario.pressao_inspiratoria.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| pressao_inspiratoria | int | cmH2O | 0-30 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= pressao_inspiratoria <= 30): RAISE ValidationError(f"{pressao_inspiratoria} deve estar entre 0 e 30")
```

## Edge cases (as implemented)
No zero exemption. Ventilacao criterion C1 flags >16 (within valid 0-30); not directly boundary-tested.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 355-368 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 139-145 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-029, RULE-val-BE-10-092

## Notes
Frontend movimentacao PINS input 0-30 (matches).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
