# RULE-SEPSE-058 — Sepse v3 automatica - trigger threshold table (20 criteria)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Sepsis screening pathway variant "v3" (payload_sepse_automatica_v3). Each of 20 criteria, when flagged by the model layer, surfaces an alert whose label encodes the exact clinical threshold that defines that criterion. This payload documents the full threshold set for the v3 sepsis trigger engine.

## Inputs

- TAX (axillary temperature) (float, degC)
- FR (respiratory rate) (float, ipm)
- VMI onset time (float, hours)
- DVA (vasoactive) onset time (float, hours)
- PAS / PAM (float, mmHg)
- TEC (capillary refill) (float, s)
- arterial lactate (float, mmol/L)
- diurese (float, ml/Kg/h)
- creatinina (trend) (float, mg/dl)
- GCS (int, points, 3-15)
- bilirrubinas (float, mg/dl)
- FC (float, bpm)
- PCO2 / P/F ratio (float)
- plaquetas (int, /mm3)
- CVC dwell time (central / femoral) (float, days)
- abdominal surgery recency (float, days)

## Outputs

- alerta text per criterion (string)

## Logic

```text
criterio_1  Febre:                  TAX >= 38.2 degC
criterio_2  Taquipnea:              FR > 20 ipm
criterio_3  Falencia respiratoria:  VMI started < 24h ago
criterio_4  Hipotensao refrataria:  DVA started < 6h ago
criterio_5  Hipotensao:             PAS < 90  OR  PAM < 60
criterio_6  Ma perfusao:            TEC > 3 s
criterio_7  Hiperlactatemia:        lactato >= 3 mmol/L
criterio_8  Oliguria:               diurese <= 0.5 ml/Kg/h over last 12h
criterio_9  Piora funcao renal:     creatinina rising (no numeric cutoff given)
criterio_10 Alt. nivel consciencia: GCS < 14
criterio_11 Ictericia:              bilirrubinas > 2 mg/dl
criterio_12 Hipotermia:             TAX < 36 degC
criterio_13 Taquicardia:            FC > 100 bpm
criterio_14 Disturbio respiratorio: PCO2 < 32  OR  P/F < 300
criterio_15 Piora infecciosa:       Leucocitos & PCR altered (no numeric cutoff)
criterio_16 Plaquetopenia:          plaquetas < 150000
criterio_17 Necessidade de SNE:     low oral diet acceptance (qualitative)
criterio_18 CVC:                    central venous catheter >= 7 days
criterio_19 CVC femoral:            femoral central venous catheter >= 5 days
criterio_20 Cirurgia abdominal:     recent abdominal surgery (< 20 days)
```

## Edge cases (as implemented)

recomendacoes list is empty for every criterion in v3 (only the alerta label carries content). Thresholds use mixed inclusive/exclusive operators exactly as written (>=, >, <=, <). No null handling in this payload (predicate lives out of scope).

## Divergence

Alert-label catalog (core/facade/trilha_sepse_v3.py, payload_sepse_automatica_v3) vs the v3 model predicates (trilhas_v3/trilha_sepse.py, RULE-SEPSE-007..026): (a) the catalog uses a DIFFERENT criterion numbering than the model (e.g. catalog criterio_6='Ma perfusao TEC>3s', criterio_16='Plaquetopenia'; model criterio_6=thrombocytopenia, criterio_16=capillary refill); (b) Plaquetopenia label '<150.000' but model predicate RULE-SEPSE-012 uses <100000; (c) Febre label 'TAX >= 38,2' but model RULE-SEPSE-007 uses temp > 38.2 (>= vs >); (d) Hipotensao label 'PAS<90 ou PAM<60' but model RULE-SEPSE-011 uses PAS<90 OR PAD<60 OR PAM<65; (e) Oliguria label 'diurese <= 0,5' but model RULE-SEPSE-014 uses <0.5; (f) 'Cateter venoso central >= 7 dias' / 'femoral >= 5 dias' labels vs model RULE-SEPSE-024/025 which use strictly > 7d / > 5d. Catalog carries display text only (all recomendacoes lists empty).

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** Sepsis-3 (Singer et al., The Third International Consensus Definitions, JAMA 2016;315:801-810) for SOFA/qSOFA cutoffs; ACCP/SCCM 1992 SIRS criteria (Bone et al., Chest 1992) for temp/RR/PaCO2; Vincent et al. 1996 SOFA (Intensive Care Med) for platelet & P/F organ-dysfunction bands. Cross-checked internally against v3 model predicates RULE-SEPSE-007..026. ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC4968574/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a (display-label threshold catalog, all recomendacoes lists empty; no computation performed here) |
| coefficients | n/a |
| units | ok — units internally consistent per label (degC, ipm, mmol/L, mg/dl, /mm3); lactate correctly in mmol/L (contrast variant B which mislabels mg/dl) |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff — (A) INTERNAL: display labels diverge from firing model predicates: Plaquetopenia label '<150.000' vs model RULE-SEPSE-012 fires at <100000; Febre label 'TAX>=38,2' vs model RULE-SEPSE-007 uses >38.2; Hipotensao label 'PAS<90 ou PAM<60' vs model RULE-SEPSE-011 adds PAD<60/PAM<65; Oliguria label '<=0,5' vs model <0.5; CVC labels '>=7d'/'>=5d' vs model >7d/>5d; criterion numbering differs from model. (B) EXTERNAL: Febre 38.2 vs SIRS 38.0; GCS<14 vs qSOFA altered-mentation GCS<15; lactato>=3 mmol/L vs Sepsis-3 septic-shock threshold >2 mmol/L; FR>20 and PaCO2<32 match SIRS; platelets<150k and P/F<300 match SOFA=1-2pt bands. |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| criterion=platelets; plaquetas=120000 | flag (label '<150.000' true; SOFA platelets<150=1pt supports <150k) | label predicate fires (plaquetas<150000 true) BUT model RULE-SEPSE-012 predicate does NOT fire (<100000); label/predicate mismatch at 100k-150k | no |
| criterion=lactato; lactato_mmol_L=2.5 | flag per Sepsis-3 hyperlactatemia >2 mmol/L | no flag (label '>=3 mmol/L' not met) | no |
| criterion=GCS; gcs=14 | flag per qSOFA altered mentation (GCS<15) | no flag (label 'GCS<14' not met) | no |
| criterion=TAX; tax_C=38.1 | flag per SIRS fever >38.0 degC | no flag (label '>=38,2' not met) | no |

**Verifier notes**

Rationale for moderate: this is a display/alert-label catalog (get_payload_trilha_sepse, trilha_sepse_v3.py:1-85) so it drives what clinicians SEE, not the firing decision. Two distinct issues: (1) internal label-vs-predicate mismatch — the Plaquetopenia alert reads '<150.000' but only fires when the model detects <100.000, so a displayed threshold does not describe the condition that triggered it (mislabels severity); (2) external divergences (lactate >=3 vs Sepsis-3 >2 mmol/L; GCS<14 vs qSOFA<15; fever 38.2 vs SIRS 38.0) are stricter institutional variants that could delay recognition of the 2-3 mmol/L lactate / GCS-14 / 38.0-38.1 zones. Impact capped at moderate because these are screening prompts within a multi-criterion pathway, not automated dosing. Carries DISCREPANCY from extraction — confirmed and characterized, not dismissed.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/facade/trilha_sepse_v3.py` | 1-85 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-01-001`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-007](RULE-SEPSE-007-sepse-v3-criterio-1-fever-without-vasopressor.md)
- [RULE-SEPSE-008](RULE-SEPSE-008-sepse-v3-criterio-2-tachypnea-hypoxemia-without-vasopressor.md)
- [RULE-SEPSE-009](RULE-SEPSE-009-sepse-v3-criterio-3-respiratory-failure-prescription.md)
- [RULE-SEPSE-010](RULE-SEPSE-010-sepse-v3-criterio-4-newly-started-vasopressor.md)
- [RULE-SEPSE-011](RULE-SEPSE-011-sepse-v3-criterio-5-hypotension-without-vasopressor.md)
- [RULE-SEPSE-012](RULE-SEPSE-012-sepse-v3-criterio-6-thrombocytopenia-without-vasopressor.md)
- [RULE-SEPSE-013](RULE-SEPSE-013-sepse-v3-criterio-7-hyperlactatemia-without-vasopressor.md)
- [RULE-SEPSE-014](../physiological-calculation/RULE-SEPSE-014-sepse-v3-criterio-8-oliguria-without-vasopressor-dialysis.md)
- [RULE-SEPSE-015](RULE-SEPSE-015-sepse-v3-criterio-9-acute-kidney-injury-without-vasopressor.md)
- [RULE-SEPSE-016](RULE-SEPSE-016-sepse-v3-criterio-10-acute-encephalopathy-delirium.md)
- [RULE-SEPSE-017](RULE-SEPSE-017-sepse-v3-criterio-11-hyperbilirubinemia-jaundice-incomplete.md)
- [RULE-SEPSE-018](RULE-SEPSE-018-sepse-v3-criterio-12-hypothermia-minor.md)
- [RULE-SEPSE-019](RULE-SEPSE-019-sepse-v3-criterio-13-tachycardia-minor-wrong-column.md)
- [RULE-SEPSE-020](RULE-SEPSE-020-sepse-v3-criterio-14-respiratory-alkalosis-hypoxemia-spontan.md)
- [RULE-SEPSE-021](RULE-SEPSE-021-sepse-v3-criterio-15-leukocytosis-leukopenia-bandemia-crp-mi.md)
- [RULE-SEPSE-022](RULE-SEPSE-022-sepse-v3-criterio-16-prolonged-capillary-refill-minor-new-on.md)
- [RULE-SEPSE-023](RULE-SEPSE-023-sepse-v3-criterio-17-enteral-tube-with-adequate-gcs-minor.md)
- [RULE-SEPSE-024](RULE-SEPSE-024-sepse-v3-criterio-18-central-line-7-days-minor.md)
- [RULE-SEPSE-025](RULE-SEPSE-025-sepse-v3-criterio-19-femoral-central-line-5-days-minor.md)
- [RULE-SEPSE-026](RULE-SEPSE-026-sepse-v3-criterio-20-recent-abdominal-surgery-minor.md)

## Notes

Wired via trilha_automatica/facade/sepse_v3.py -> payload_sepse_automatica_v3. DISCREPANCY vs variant B (RULE-sepse-BE-01-002): femoral CVC threshold is 5 days here vs "femoral >7 dias" text elsewhere; CVC threshold >=7d here vs >10d in variant B criterio_22; hipotermia <36 here. Cross-ref RULE-sepse-BE-01-002/003.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
