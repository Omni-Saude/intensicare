# RULE-SINAIS-VITAIS-001 — Blood-pressure and heart-rate plausible ranges (movimentacao form)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | sinais-vitais |

## Rule
Frontend antd number-input min/max bounds for systolic/diastolic BP and heart rate on the movimentacao (nurse handoff) form. Re-expresses the backend field validators; numeric bounds match the backend exactly.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| pas | number | mmHg | 50-250 |
| pad | number | mmHg | 0-150 |
| frequencia_cardiaca | number | bpm | 0-200 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valid vitals | boolean |  |

## Logic
```text
pas: min 50, max 250
pad: min 0,  max 150
frequencia_cardiaca: min 0, max 200
```

## Edge cases (as implemented)
Inclusive bounds; no cross-field check (PAS>PAD not enforced). Unlike the backend PASValidator, the FE min of 50 has NO zero-exemption sentinel, so a literal 0 ("not measured" on the backend) would be blocked by this input; on the FE the "not measured" case is expressed by leaving the field blank instead.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormMovimentacao.ts` | 72-92 | `f9656be2` | frontend-copy |

- Merged from: RULE-vitals-FE-01-021
- Related rules: RULE-SINAIS-VITAIS-018, RULE-SINAIS-VITAIS-019, RULE-SINAIS-VITAIS-027, RULE-SINAIS-VITAIS-005

## Notes
PAS 50-250 / PAD 0-150 identical in dataFormFormularioMedico.ts:283-296 (see RULE-SINAIS-VITAIS-005). Bounds reconciled against backend validators RULE-SINAIS-VITAIS-018/019/027 — numeric ranges agree exactly.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
