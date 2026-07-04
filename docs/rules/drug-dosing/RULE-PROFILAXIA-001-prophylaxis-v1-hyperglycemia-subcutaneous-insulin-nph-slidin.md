# RULE-PROFILAXIA-001 — Prophylaxis v1 - hyperglycemia subcutaneous insulin NPH sliding regimen

| Field | Value |
|---|---|
| Category | drug-dosing |
| Type | formula |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | profilaxia |

## Rule
Subcutaneous insulin regimen for recurrent hyperglycemia in the ICU (profilaxia v1 criterio_7), with an IV-insulin alternative (criterio_8).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| peso | float | kg | — |
| HGT (capillary glucose) | float | mg/dl | — |

## Outputs

| Name | Type | Unit |
|---|---|---|
| NPH total daily dose | float | U |
| regular insulin correction | float | U |

## Logic

```text
criterio_7 (hiperglicemia, insulina subcutanea):
  Insulin NPH: 0.3 to 0.5 U/kg/day, divided 3x/day (before meals).
  Correction (regular insulin): +1 U for each 50 mg/dl of HGT above
  150 mg/dl measured over the last 24h, divided 3x/day.
  Also: notify nutrition service for diet adjustment.
criterio_8 (hiperglicemia, insulina endovenosa) - alternative:
  recurrent hyperglycemia -> prescribe "Insulina em BIC - Protocolo de
  controle glicemico UTI" (IV insulin per institutional protocol)
  instead of NPH; notify nutrition service.
```

## Edge cases (as implemented)
Correction reference point is 150 mg/dl; increment step is 50 mg/dl. Coefficient range 0.3-0.5 U/kg/day inclusive.

## Verification
- Verdict: VERIFIED, impact: none
- Reference: ADA Standards of Care in Diabetes (Diabetes Care) inpatient glycemic management + Umpierrez et al. RABBIT-2 (Diabetes Care 2007) basal-bolus protocol: insulin-naive hospitalized T2DM starting total daily dose (TDD) 0.3-0.5 U/kg/day. The correction (supplemental) sliding-scale increment and the NPH-three-times-daily split are institutional protocol specifics, not a single published standard.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/facade/trilha_profilaxia.py` | 46-59 | `8166c07e` | primary |

- Merged from: RULE-profilaxia-BE-01-006
- Related rules: RULE-PROFILAXIA-002, RULE-PROFILAXIA-003, RULE-PROFILAXIA-007

## Notes
criterio_8 IV-insulin recommendation is duplicated in nutricao criterio_10 (cross-cluster, out of scope here). v1-only: criteria 7/8 are commented out of the v3 pathway (RULE-PROFILAXIA-008), so there is no v3 counterpart.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
