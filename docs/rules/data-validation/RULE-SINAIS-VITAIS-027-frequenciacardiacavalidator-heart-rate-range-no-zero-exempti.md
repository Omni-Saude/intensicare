# RULE-SINAIS-VITAIS-027 — FrequenciaCardiacaValidator — heart rate range, no zero exemption

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Heart rate must be between 0 and 200 inclusive. Applied on dados_prontuario.frequencia_cardiaca.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| frequencia_cardiaca | int | bpm | 0-200 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF NOT (0 <= frequencia_cardiaca <= 200): RAISE ValidationError(f"{frequencia_cardiaca} deve estar entre 0 e 200")
```

## Edge cases (as implemented)
No zero exemption (0 bpm = asystole/arrest is representable); 201 -> error. Test test_limites_parametros.py:106-108.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 279-292 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 112-114 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-024, RULE-val-BE-10-089
- Related rules: RULE-SINAIS-VITAIS-001, RULE-SINAIS-VITAIS-005

## Notes
Movimentacao form bounds HR 0-200 (matches); physician form leaves HR unbounded (RULE-SINAIS-VITAIS-005 divergence).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
