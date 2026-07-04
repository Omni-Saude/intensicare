# RULE-SINAIS-VITAIS-017 — VolumeCorrenteValidator — tidal volume range, no zero exemption

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Tidal volume must be between 0 and 1500 inclusive. Applied on dados_prontuario.volume_corrente.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| volume_corrente | float | mL | 0-1500 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= volume_corrente <= 1500): RAISE ValidationError(f"{volume_corrente} deve estar entre 0 e 1500")
```

## Edge cases (as implemented)
No zero exemption; 1550 -> error. Test test_limites_parametros.py:58-60.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 136-149 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 75-77 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-014, RULE-val-BE-10-079

## Notes
Ventilacao criterion C1 flags volume_corrente >500 (within valid 0-1500). Frontend movimentacao input 0-1500 (matches).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
