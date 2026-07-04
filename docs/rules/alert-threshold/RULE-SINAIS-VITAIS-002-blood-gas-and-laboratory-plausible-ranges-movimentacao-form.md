# RULE-SINAIS-VITAIS-002 — Blood-gas and laboratory plausible ranges (movimentacao form)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Frontend min/max bounds for arterial blood-gas and lab values on the movimentacao form. These labs (PaO2->P/F, lactate, bilirubin, creatinine, platelets, leukocytes) feed downstream SOFA/sepsis-severity assessment, but these bounds are input-plausibility validation only, not scoring. Numeric bounds match the backend validators exactly.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| po2 | number | mmHg | 0-500 |
| paco2 | number | mmHg | 0-150 |
| lactato_arterial | number | mmol/L | 0-20 |
| leucocitos | number | /mm3 | 0-40000 |
| bilirrubinas | number | mg/dL | 0-30 |
| creatinina | number | mg/dL | 0-20 |
| plaquetas | number | /mm3 | 0-700000 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid labs | boolean |  |

## Logic
```text
po2 0-500; paco2 0-150; lactato_arterial 0-20; leucocitos 0-40000;
bilirrubinas 0-30; creatinina 0-20; plaquetas 0-700000
```

## Edge cases (as implemented)
Bilirubin/creatinine/platelets/PaO2(->P/F)/lactate are SOFA and sepsis-severity inputs; ranges are validation only, not scoring. The SOFA/sepsis score formula is not present in this cluster (collection surface only).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormMovimentacao.ts` | 145-198 | `f9656be2` | frontend-copy |

- Merged from: RULE-labs-FE-01-024
- Related rules: RULE-SINAIS-VITAIS-014, RULE-SINAIS-VITAIS-016, RULE-SINAIS-VITAIS-022, RULE-SINAIS-VITAIS-024, RULE-SINAIS-VITAIS-025, RULE-SINAIS-VITAIS-026, RULE-SINAIS-VITAIS-028

## Notes
This form is the collection surface for a downstream SOFA/sepsis score (score formula not captured in this cluster). All seven bounds reconcile exactly with backend validators (RULE-SINAIS-VITAIS-014/016/022/024/025/026/028).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
