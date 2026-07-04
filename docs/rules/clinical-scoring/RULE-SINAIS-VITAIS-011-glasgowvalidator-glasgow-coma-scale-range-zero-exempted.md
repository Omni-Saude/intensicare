# RULE-SINAIS-VITAIS-011 — GlasgowValidator — Glasgow Coma Scale range, zero exempted

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | validation |
| Status | OK |
| Verification | VERIFIED |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Glasgow Coma Scale total must be between 3 and 15 inclusive (standard GCS range), UNLESS exactly 0 (exempted, treated as not measured). Applied on dados_prontuario.glasgow.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| glasgow | int | GCS points | 0 (exempt) or 3-15 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF glasgow != 0 AND NOT (3 <= glasgow <= 15): RAISE ValidationError(f"{glasgow} deve estar entre 3 e 15")
```

## Edge cases (as implemented)
0 allowed (sentinel/"not measured"); 1, 2, 16 -> error. Test test_limites_parametros.py:98-104.

## Verification
- Verdict: VERIFIED
- Reference: Glasgow Coma Scale (Teasdale & Jennett, Lancet 1974). Total = eye (1-4) + verbal (1-5) + motor (1-6); range 3 (no response) to 15 (fully alert). Severe 3-8, moderate 9-12, mild 13-15. Confirmed by StatPearls NBK513298 and glasgowcomascale.org.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 58-69 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 109-111 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-008, RULE-val-BE-10-088

## Notes
3-15 is the standard published GCS range (verify against Glasgow Coma Scale). Category taken from the validators.py capture (clinical-scoring); the model-field capture labelled it data-validation.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
