# RULE-SEPSE-015 — SEPSE v3 criterio_9 - acute kidney injury without vasopressor/dialysis

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
No noradrenaline (12h) AND no hemodialysis AND no "DRC em TRS" AND (creatinine>2 OR creatinine rise >0.5 over last 2 evolutions).

## Inputs

- evolucao.diurna_creatinina (last & penultimate) (float, mg/dL)
- balanco.qt_vol_nora, evolucao.diurna_terapia_hemo, diag_inter_1..4 (float / string)

## Outputs

- criterio_9 (boolean)

## Logic

```text
return all([
  not balanco_12h.filter(qt_vol_nora__gt=0).exists(),
  not get_number(ultima_evolucao.diurna_terapia_hemo),
  any([ get_number(ultima.diurna_creatinina) > 2,
        get_number(ultima.diurna_creatinina) - get_number(penultima.diurna_creatinina) > 0.5 ]),
  not list(filter(lambda x: x == "DRC em TRS", vars(ultima).fromkeys(("diag_inter_1".."diag_inter_4")))),  # always True
]) if balanco_12h and penultima_evolucao and ultima_evolucao else False
```

## Edge cases (as implemented)

Requires at least 2 evolutions (penultima). The DRC absence gate is vacuously True (fromkeys bug).

## Divergence

DISCREPANCY - DRC exclusion always-true due to fromkeys bug (RULE-systemic-BE-03-001); remaining creatinine logic is sound.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** KDIGO AKI 2012 - AKI = SCr increase >=0.3 mg/dL within 48h OR >=1.5x baseline; SOFA renal subscore (Vincent 1996): creatinine 2.0-3.4 mg/dL = 2 points. ([source](https://kdigo.org/guidelines/acute-kidney-injury/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | creatinine >2 mg/dL (SOFA 2-pt boundary) OR delta >0.5 mg/dL over last 2 evolutions |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| qt_vol_nora_12h=0; diurna_terapia_hemo=; ultima_creat=2.5; penultima_creat=2.0; diag_inter_1_4=["none"] | Cr 2.5 > 2 -> SOFA renal 2pt / AKI -> positive (if acute) | not(nora)=T; not hemo=T; any([2.5>2 T,...])=T; not list(filter fromkeys)=not[]=T; all=True | yes |
| qt_vol_nora_12h=0; diurna_terapia_hemo=; ultima_creat=1.8; penultima_creat=1.4 | rise 0.4 mg/dL >=0.3 -> KDIGO Stage 1 AKI -> should flag | 1.8>2 F; 1.8-1.4=0.4 >0.5 F -> any=False -> all=False (NOT flagged) | no |
| qt_vol_nora_12h=0; diurna_terapia_hemo=; ultima_creat=6.0; penultima_creat=6.0; diag_inter_1=DRC em TRS | chronic ESRD on RRT, stable Cr -> should be EXCLUDED (not acute sepsis-AKI) -> negative | 6>2 T; DRC gate not list(filter(=='DRC em TRS', fromkeys(diag_inter_1..4)))=not[]=True (vacuous) -> exclusion never applies -> all=True (FALSE POSITIVE) | no |

**Verifier notes**

Confirmed extraction DISCREPANCY. (a) DRC-on-RRT exclusion gate `not list(filter(lambda x:x=='DRC em TRS', vars(ultima).fromkeys((diag_inter_1..4))))` is vacuously True (fromkeys keys are field NAMES, never 'DRC em TRS', so filter->[]->not[]->True): chronic dialysis/CKD patients with chronically elevated creatinine are NOT excluded and can falsely trigger the AKI criterion (false positive). (b) creatinine-rise threshold >0.5 mg/dL exceeds KDIGO's >=0.3 mg/dL/48h, missing Stage-1 AKI rises of 0.3-0.5 mg/dL (false negative), and no 48h window is enforced (compares only the last two evolutions whatever their spacing). The Cr>2 mg/dL absolute cutoff aligns with the SOFA renal 2-point boundary (SOFA uses >=2.0; legacy strict >2 excludes exactly 2.0 - minor boundary difference). Impact moderate: opposing sensitivity/specificity errors on a single OR-ed organ criterion.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 615-671 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-109`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

DISCREPANCY - DRC exclusion always-true due to fromkeys bug (RULE-systemic-BE-03-001); remaining creatinine logic is sound.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
