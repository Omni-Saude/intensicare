# RULE-SINAIS-VITAIS-013 — TecValidator — capillary refill time range, zero exempted

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
TEC (tempo de enchimento capilar / capillary refill time) must be between 3 and 20 inclusive, UNLESS exactly 0 (exempted). Applied on dados_prontuario.tec.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| tec | int | seconds | 0 (exempt) or 3-20 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid/ValidationError | bool |  |

## Logic
```text
IF tec != 0 AND NOT (3 <= tec <= 20): RAISE ValidationError(f"{tec} deve estar entre 3 e 20")
```

## Edge cases (as implemented)
0 allowed (sentinel/"not measured"); 25 -> error. Test test_limites_parametros.py:42-44. Criteria treat tec>5 as abnormal (within the valid 3-20 range).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/validators.py` | 84-93 | `8166c07e` | primary |
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 62-64 | `8166c07e` | duplicate |

- Merged from: RULE-vitais-BE-11-010, RULE-val-BE-10-076
- Related rules: RULE-SINAIS-VITAIS-004

## Notes
The 3-20 permissible-entry range is wider than the classic clinical normal cutoff (<2-3s); recorded verbatim, no correction. The frontend encodes the same field three ways (RULE-SINAIS-VITAIS-004), which carries the capillary-refill discrepancy/verify.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
