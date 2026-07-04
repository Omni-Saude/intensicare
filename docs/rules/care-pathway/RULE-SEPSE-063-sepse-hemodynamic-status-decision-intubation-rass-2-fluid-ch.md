# RULE-SEPSE-063 — SEPSE hemodynamic-status decision (intubation RASS-2, fluid challenge)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Clinical decision-support text for the "status_hemodinamico" item: consider orotracheal intubation with sedoanalgesia targeting RASS -2 when poor perfusion + tachydyspnea + confusion/somnolence, to reduce VO2 and optimize DO2; if ultrasound available assess fluid-responsiveness and consider a 250 ml Ringer Lactate volume challenge.

## Inputs

- sinais_mal_perfusao (boolean)
- taquidispneia (boolean)
- confusao_ou_sonolencia (boolean)
- usg_disponivel (boolean)

## Outputs

- alvo_RASS (integer)
- desafio_volemico (number, ml)

## Logic

```text
IF sinais_mal_perfusao AND taquidispneia AND (confusao OR sonolencia):
    considerar intubacao orotraqueal + sedoanalgesia com alvo RASS -2 (reduzir VO2, otimizar DO2)
IF usg_disponivel:
    checar fluido-responsividade; considerar desafio volemico com aliquotas de 250 ml de Ringer Lactato
```

## Edge cases (as implemented)

Verbatim text; RASS target is the sedation scale value -2. Volume-challenge aliquot 250 ml (vs 500 ml initial bolus in RULE-sepse-BE-02-013).

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Surviving Sepsis Campaign 2021 (dynamic fluid-responsiveness assessment; fluid challenge technique) + Sessler CN, et al. The Richmond Agitation-Sedation Scale (RASS). Am J Respir Crit Care Med 2002;166:1338 (RASS -2 = light sedation). Intubation to reduce work of breathing / VO2 in shock with respiratory distress is standard ICU practice. ([source](https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-guidelines-2021))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | RASS target -2 is a valid point on the -5..+4 RASS scale (light sedation, briefly awakens to voice). |
| units | Fluid-challenge aliquot 250 mL (volume); RASS -2 dimensionless scale value. |
| ranges | 250 mL fluid-challenge aliquot is within the accepted 250-500 mL range; SSC endorses fluid-responsiveness assessment (ultrasound/passive leg raise) to guide additional fluids. |
| rounding | n/a |
| cutoffs | Intubation gated on mal-perfusao AND taquidispneia AND (confusao OR sonolencia) - clinical composite, no guideline-defined numeric cutoff. |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| mal-perfusao=T, taquidispneia=T, sonolencia=T | reasonable to consider intubation + light sedation to reduce VO2 | considerar IOT + sedoanalgesia alvo RASS -2 | yes |
| usg_disponivel=T, fluid-responsive | give guided fluid challenge (250-500 mL crystalloid) | desafio volemico 250 mL Ringer Lactato | yes |
| mal-perfusao=T, taquidispneia=F | intubation composite not met -> no forced intubation on this criterion | AND not satisfied -> no intubation prompt | yes |

**Verifier notes**

RASS -2 is a valid light-sedation target (Sessler 2002 RASS scale); 250 mL fluid-challenge aliquots are within accepted practice and consistent with SSC-2021 dynamic-assessment guidance. Intubation to reduce VO2/optimize DO2 in perfusion failure with tachydyspnea is standard. Verbatim clinician-facing text; no numeric conflict with references.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/api/v1/serializers/item_trilha_interativa_sepse.py` | 200-207 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-02-015`

**Related rules:**

- [RULE-SEPSE-061](../drug-dosing/RULE-SEPSE-061-sepse-volume-expansion-expansao-volemica-decision-and-dosing.md)
- [RULE-SEPSE-062](../alert-threshold/RULE-SEPSE-062-sepse-reassessment-lab-thresholds-bicarbonate-dobutamine-tra.md)
- [RULE-SEPSE-064](RULE-SEPSE-064-sepse-invasive-devices-decision-early-ne-central-access-cvc.md)
- [RULE-SEPSE-065](../drug-dosing/RULE-SEPSE-065-sepse-vasoactive-drug-escalation-thresholds-and-shock-index.md)

## Notes

References RASS (Richmond Agitation-Sedation Scale) target -2.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
