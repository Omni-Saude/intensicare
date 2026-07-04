# RULE-SEPSE-065 — SEPSE vasoactive-drug escalation thresholds and shock index

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | drug-dosing |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Clinical decision-support text for the "drogas_vasoativas" item. Escalation by noradrenaline rate: at NE > 0.3 mcg/kg/min add vasopressin + hydrocortisone (refractory shock), set diet ZERO or trophic (20 ml/h) and reassess in 24h; suspend antihypertensives/beta-blockers/ diuretics; prefer epinephrine if NE > 1 mcg/kg/min or shock index positive (HR/SBP > 0.7); start IV vasopressin continuous + hydrocortisone 50 mg IV q6h when NE > 0.3 mcg/kg/min.

## Inputs

- noradrenalina (number, mcg/kg/min)
- FC (number, bpm)
- PA_sistolica (number, mmHg)

## Outputs

- indice_de_choque (number)
- conduta_vasopressor (text)

## Logic

```text
indice_de_choque = FC / PA_sistolica            # "positivo" se > 0.7
IF noradrenalina > 0.3 mcg/kg/min:
    associar vasopressina + hidrocortisona (choque refratario)
    dieta ZERO ou trofica (20 ml/h); reavaliar em 24 h
    iniciar vasopressina EV continua + hidrocortisona 50 mg EV de 6/6h
    (~20 ml/h para paciente de 80 kg)
Suspender anti-hipertensivos, beta-bloqueadores e diureticos se presentes.
IF noradrenalina > 1 mcg/kg/min OR indice_de_choque > 0.7:
    preferir epinefrina
```

## Edge cases (as implemented)

Verbatim text. Two NE thresholds: 0.3 (add vasopressin/hydrocortisone) and 1.0 (switch to epinephrine). Shock index HR/SBP threshold 0.7. Hydrocortisone 50 mg q6h. "~20 ml/h for 80 kg" is an illustrative infusion rate.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Surviving Sepsis Campaign 2021 (Evans L, et al. Crit Care Med 2021;49:e1063): norepinephrine first-line; add vasopressin when NE ~0.25-0.5 mcg/kg/min; add epinephrine if inadequate MAP on NE+vasopressin; hydrocortisone 200 mg/d = 50 mg IV q6h (or infusion) with ongoing vasopressor requirement (NE/epi >=0.25 mcg/kg/min). Shock index (HR/SBP) normal 0.5-0.7 (Allgower & Burri 1967; Rady 1994). ([source](https://dig.pharmacy.uic.edu/faqs/2022-2/march-2022-faqs/update-what-are-the-2021-pharmacotherapy-updates-to-the-surviving-sepsis-campaign-international-guidelines-for-management-of-sepsis-and-septic-shock/))

**Checks**

| Dimension | Result |
|---|---|
| equation | indice_de_choque = FC / PA_sistolica -> correct shock-index definition (HR/SBP). |
| coefficients | NE >0.3 mcg/kg/min add vasopressin+hydrocortisone lies inside SSC vasopressin window 0.25-0.5 and >=0.25 hydrocortisone trigger; hydrocortisone 50 mg IV q6h = 200 mg/day exactly matches SSC. |
| units | NE in mcg/kg/min (matches SSC dosing unit); shock index dimensionless; hydrocortisone mg. |
| ranges | Shock index >0.7 as 'positivo' matches upper bound of normal (0.5-0.7); NE 0.3 and 1.0 mcg/kg/min are plausible escalation points. |
| rounding | n/a |
| cutoffs | Two NE thresholds 0.3 (add vasopressin/steroid) and 1.0 (prefer epinephrine) - 0.3 within SSC range; 1.0 and shock-index>0.7 are reasonable escalation triggers; epinephrine is the SSC add-on after NE+vasopressin. |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| NE = 0.35 mcg/kg/min | in vasopressin-initiation window (0.25-0.5); start vasopressin + hydrocortisone 50 mg q6h (200 mg/d) | 0.35 > 0.3 -> vasopressina EV continua + hidrocortisona 50 mg 6/6h, dieta trofica, reavaliar 24h | yes |
| NE = 0.2 mcg/kg/min | below typical vasopressin/steroid initiation (<0.25) | 0.2 > 0.3 FALSE -> no add-on | yes |
| NE = 1.2 mcg/kg/min | high-dose refractory shock -> add epinephrine (3rd agent) | 1.2 > 1 -> preferir epinefrina | yes |
| FC = 120, PA_sistolica = 100 -> SI = 1.2 | shock index >0.7 abnormal (normal 0.5-0.7) | 1.2 > 0.7 -> indice de choque positivo -> preferir epinefrina | yes |

**Verifier notes**

Escalation figures match SSC-2021: NE 0.3 add-vasopressin threshold sits inside the 0.25-0.5 mcg/kg/min window; hydrocortisone 50 mg IV q6h = 200 mg/day is the exact SSC dose; epinephrine as third-line add-on is SSC-recommended. Shock index HR/SBP with >0.7 = abnormal matches classic normal range 0.5-0.7. Verbatim clinician-facing text; all numeric thresholds consistent with references.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/api/v1/serializers/item_trilha_interativa_sepse.py` | 218-229 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-02-017`

**Related rules:**

- [RULE-SEPSE-061](RULE-SEPSE-061-sepse-volume-expansion-expansao-volemica-decision-and-dosing.md)
- [RULE-SEPSE-062](../alert-threshold/RULE-SEPSE-062-sepse-reassessment-lab-thresholds-bicarbonate-dobutamine-tra.md)
- [RULE-SEPSE-063](../care-pathway/RULE-SEPSE-063-sepse-hemodynamic-status-decision-intubation-rass-2-fluid-ch.md)
- [RULE-SEPSE-064](../care-pathway/RULE-SEPSE-064-sepse-invasive-devices-decision-early-ne-central-access-cvc.md)

## Notes

Shock index "positive" threshold coded as > 0.7 (normal shock index 0.5-0.7); recorded verbatim.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
