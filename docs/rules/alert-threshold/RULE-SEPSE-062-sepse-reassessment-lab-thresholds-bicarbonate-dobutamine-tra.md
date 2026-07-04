# RULE-SEPSE-062 — SEPSE reassessment lab thresholds (bicarbonate, dobutamine, transfusion)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Clinical decision-support text for the "exames" (labs reassessment) item: do not routinely replace bicarbonate in metabolic acidosis; consider dobutamine on rising lactate or poor perfusion signs; hemoglobin transfusion target > 7 mg/dl (do not transfuse above).

## Inputs

- lactato_arterial_tendencia (enum, {ascensao, estavel})
- TEC (number, segundos)
- SVcO2 (number, %)
- delta_PCO2 (number, mmHg)
- hemoglobina (number, mg/dl)

## Outputs

- acao (text)

## Logic

```text
IF acidose_metabolica: NAO repor bicarbonato de rotina (consultar protocolo institucional)
IF lactato em ascensao OR TEC > 3 s OR SVcO2 < 60 OR delta_PCO2 > 6:
    considerar iniciar dobutamina (otimizar inotropismo)
Alvo de hemoglobina > 7 mg/dl; NAO transfundir acima desse valor.
```

## Edge cases (as implemented)

Verbatim text. Units as written: SVcO2 "<60" (percent, no unit shown), delta PCO2 ">6" (mmHg implied), hemoglobin target ">7 mg/dl" (note: Hb is conventionally g/dL, source says mg/dl).

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Surviving Sepsis Campaign 2021 (Evans L, et al. Crit Care Med 2021;49:e1063): restrictive RBC transfusion, Hb trigger 7 g/dL (strong rec); bicarbonate not recommended for lactic acidosis pH>=7.15; dobutamine for persistent hypoperfusion/myocardial dysfunction. Perfusion-adequacy markers: ScvO2 and venoarterial PCO2 gap (Pcv-aCO2 >6 mmHg indicates inadequate flow; ScvO2 low <70%). ([source](https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-guidelines-2021))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | Hb target >7 matches SSC restrictive threshold (7.0 g/dL); dobutamine trigger set (rising lactate, TEC>3s, ScvO2<60, dPCO2>6) consistent with recognised perfusion-inadequacy markers. |
| units | diff (cosmetic) - hemoglobin written 'mg/dl'; Hb is conventionally g/dL. Value 7 is correct and unambiguous. SVcO2 in % (implied), delta PCO2 in mmHg (implied). |
| ranges | ScvO2 <60% is below normal (SSC/EGDT reference ~70%); dPCO2 >6 mmHg is the standard venoarterial-gap threshold. Both consistent with literature. |
| rounding | n/a |
| cutoffs | Hb >7 g/dL matches; do-not-transfuse-above-7 phrasing aligns with restrictive strategy. |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| Hb = 6.5 g/dL | below 7 g/dL -> transfuse (restrictive) | 6.5 < 7 -> transfuse; do not transfuse above 7 | yes |
| Hb = 8 g/dL, no active bleeding | above 7 -> do NOT transfuse (restrictive) | do not transfuse above 7 | yes |
| lactate rising + ScvO2 = 55% | poor perfusion / low ScvO2 -> consider inotrope (dobutamine) | lactato ascensao OR ScvO2<60 -> consider dobutamina | yes |
| metabolic acidosis pH 7.20 | do not give bicarbonate routinely (pH>=7.15) | nao repor bicarbonato de rotina | yes |

**Verifier notes**

All numeric targets match SSC-2021: restrictive Hb trigger 7 g/dL, no routine bicarbonate, dobutamine for hypoperfusion. Perfusion thresholds (ScvO2<60, dPCO2>6 mmHg) match established critical-care references. Only defect is a cosmetic unit-label typo 'mg/dl' for hemoglobin (should be g/dL); zero clinical impact because Hb is never expressed in mg/dL, so no dosing/decision error results. Verbatim guidance text; recorded, not corrected.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/api/v1/serializers/item_trilha_interativa_sepse.py` | 192-199 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-02-014`

**Related rules:**

- [RULE-SEPSE-063](../care-pathway/RULE-SEPSE-063-sepse-hemodynamic-status-decision-intubation-rass-2-fluid-ch.md)
- [RULE-SEPSE-064](../care-pathway/RULE-SEPSE-064-sepse-invasive-devices-decision-early-ne-central-access-cvc.md)
- [RULE-SEPSE-065](../drug-dosing/RULE-SEPSE-065-sepse-vasoactive-drug-escalation-thresholds-and-shock-index.md)
- [RULE-SEPSE-075](../care-pathway/RULE-SEPSE-075-sepse-item-check-uncheck-and-protocol-completion-state-machi.md)

## Notes

Hemoglobin unit written "mg/dl" (physiologically g/dL); recorded verbatim.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
