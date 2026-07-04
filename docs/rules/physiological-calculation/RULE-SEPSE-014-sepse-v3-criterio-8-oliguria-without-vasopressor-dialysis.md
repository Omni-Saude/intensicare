# RULE-SEPSE-014 — SEPSE v3 criterio_8 - oliguria without vasopressor/dialysis

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | high |

## Rule
No noradrenaline (12h) AND no hemodialysis AND "DRC em TRS" present in diagnosis AND hourly urine output < 0.5 mL/kg/h computed over last 12h.

## Inputs

- balanco.qt_vol_espontanea, qt_vol_svd, qt_vol_cistostomia (float, mL)
- evolucao.peso (string parsed to float, kg)
- evolucao.diurna_terapia_hemo, diagnostico_1..4 (float / string)

## Outputs

- criterio_8 (boolean)

## Logic

```text
diurese_total = Sum(qt_vol_espontanea + qt_vol_svd + qt_vol_cistostomia) over balancos(dt>=now-12h)
peso = float("".join(re.findall(r"\d+", evolucao.peso.replace(",", ".")))) if evolucao.peso else 0
return all([
  not balanco_12h.filter(qt_vol_nora__gt=0).exists(),
  not get_number(evolucao.diurna_terapia_hemo),
  list(filter(lambda x: x == "DRC em TRS", vars(evolucao).fromkeys(("diagnostico_1".."diagnostico_4")))),  # always [] -> False
  ((diurese_total / 12) / peso) < 0.5 if (peso and diurese_total is not None) else False,
]) if balanco_12h and ultima_evolucao and diurese_balanco_12hrs else False
```

## Edge cases (as implemented)

peso parse strips decimal point (findall of \d+ then join) so "70.5"/"70,5" -> 705 kg (BUG - inflates weight, understates mL/kg/h). Division guarded by peso truthiness. diurese/12 assumes exactly 12h regardless of actual samples.

## Divergence

DISCREPANCY - (a) weight-parse strips the decimal separator inflating peso ~10x; (b) the "DRC em TRS" diagnosis gate is non-functional per RULE-systemic-BE-03-001 and also inverted (docstring wants ABSENCE of DRC, code has no `not`), so this whole all([]) is effectively always False. Same diurese formula appears (commented) in trilha_profilaxia.py c8.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** high
- **Reference:** KDIGO Clinical Practice Guideline for Acute Kidney Injury 2012 (Kidney Int Suppl 2012;2:1-138) - AKI urine criterion: urine output <0.5 mL/kg/h for 6-12 h (Stage 1). ([source](https://kdigo.org/guidelines/acute-kidney-injury/))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | /12 (12h window) reasonable vs KDIGO 6-12h; threshold 0.5 mL/kg/h correct |
| units | diff |
| ranges | ok |
| rounding | diff |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| qt_vol_nora_12h=0; diurna_terapia_hemo=; peso=70,5; diurese_total_12h=300; diagnostico_1_4=["none"] | rate=(300/12)/70.5=0.354 mL/kg/h <0.5 -> KDIGO oliguria -> positive | peso '70.5'->findall->['70','5']->'705'->705.0; ratio=(300/12)/705=0.035<0.5=True; BUT list(filter(=='DRC em TRS', fromkeys(diagnostico_1..4)))=[] -> falsy -> all([...,[],...])=False | no |
| qt_vol_nora_12h=0; diurna_terapia_hemo=; peso=80; diurese_total_12h=600 | rate=(600/12)/80=0.625 mL/kg/h >=0.5 -> not oliguric -> negative | 0.625<0.5=False AND DRC gate []=falsy -> all=False | yes |
| qt_vol_nora_12h=0; diurna_terapia_hemo=; peso=60; diurese_total_12h=120 | rate=(120/12)/60=0.167 mL/kg/h <0.5 -> KDIGO oliguria -> positive | DRC gate fromkeys->[]->falsy -> all=False (never fires) | no |

**Verifier notes**

Confirmed extraction DISCREPANCY. Two compounding defects vs KDIGO: (a) DRC gate list(filter(lambda x:x=='DRC em TRS', vars(evolucao).fromkeys((diagnostico_1..4)))) builds a dict keyed by field NAMES (never == 'DRC em TRS'), always yields [] -> falsy -> forces the whole all([]) to False, so the oliguria criterion NEVER fires (permanent false-negative); also logically inverted vs docstring (docstring wants ABSENCE of DRC, code has no `not`). (b) Weight parse float(''.join(re.findall(r'\d+', peso.replace(',','.')))) strips the decimal point, so '70,5'/'70.5'->705 kg, inflating weight ~10x and understating mL/kg/h ~10x (would over-flag oliguria if the gate were fixed). Core clinical target (<0.5 mL/kg/h) is correct; /12 assumes exactly 12h regardless of sample count. Impact high: a safety-relevant organ-dysfunction criterion is dead code.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 550-613 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-108`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](../alert-threshold/RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

DISCREPANCY - (a) weight-parse strips the decimal separator inflating peso ~10x; (b) the "DRC em TRS" diagnosis gate is non-functional per RULE-systemic-BE-03-001 and also inverted (docstring wants ABSENCE of DRC, code has no `not`), so this whole all([]) is effectively always False. Same diurese formula appears (commented) in trilha_profilaxia.py c8.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
