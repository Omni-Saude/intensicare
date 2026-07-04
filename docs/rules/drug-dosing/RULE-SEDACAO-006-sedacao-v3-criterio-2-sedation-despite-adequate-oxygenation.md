# RULE-SEDACAO-006 — Sedacao v3 criterio_2 - sedation despite adequate oxygenation (defined, unwired)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | drug-dosing |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Midazolam/Propofol/Cetamina present in last 4h AND P/F>200 AND FiO2<50 AND PEEP<=10 AND sedoanalgesia justification in {outros, SDRA moderada ou grave}.

## Inputs

| name | type | unit |
|---|---|---|
| evolucao.diurna_pf/diurna_fio2/diurna_peep/diurna_sedoanalgesia | float / string | ratio / % / cmH2O |
| balanco.qt_vol_mid/pro/cet | float | ml/h |

## Outputs

| name | type |
|---|---|
| criterio_2 | boolean |

## Logic

```text
presenca_sedativos = any(balanco.qt_vol_mid / qt_vol_pro / qt_vol_cet) over balanco_4h
return all([
  presenca_sedativos,
  get_number(diurna_pf)   > 200,
  get_number(diurna_fio2) < 50,
  get_number(diurna_peep) <= 10,
  diurna_sedoanalgesia in ["outros", "SDRA moderada ou grave"],
]) if balanco_4h and ultima_evolucao else False
```

## Edge cases (as implemented)

Defined but NOT called by calcular_criterios (criterio_2 stays null). Justification match is case/label-sensitive ('outros' lowercase).

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** ARDS Definition Task Force. Acute Respiratory Distress Syndrome: The Berlin Definition. JAMA 2012;307(23):2526-2533. (moderate ARDS PaO2/FiO2 100-200, severe <=100, on PEEP>=5). Devlin JW et al. PADIS Guidelines. Crit Care Med 2018 (light sedation). ([source](https://pubmed.ncbi.nlm.nih.gov/22797452/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | ok |
| units | ok - P/F in mmHg, FiO2 as percent (<50), PEEP in cmH2O (<=10); all internally consistent, no unit mismatch |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok - P/F>200 threshold matches Berlin moderate/severe upper boundary (moderate is 100-200); FiO2<50% and PEEP<=10 are consistent low-support cutoffs |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| sedative_mid=5; diurna_pf=250; diurna_fio2=40; diurna_peep=8; diurna_sedoanalgesia=SDRA moderada ou grave | P/F 250 = mild/resolved ARDS (no longer moderate/severe per Berlin) while sedated for ARDS -> reconsider sedation -> flag TRUE | presenca_sedativos=True, 250>200 True, 40<50 True, 8<=10 True, justification match True -> criterio_2=True | yes |
| sedative_mid=5; diurna_pf=180; diurna_fio2=40; diurna_peep=8; diurna_sedoanalgesia=SDRA moderada ou grave | P/F 180 = moderate ARDS still present -> sedation justified -> no flag FALSE | 180>200 False -> all() False -> criterio_2=False | yes |
| sedative_mid=5; diurna_pf=200; diurna_fio2=40; diurna_peep=8; diurna_sedoanalgesia=outros | P/F=200 boundary is still moderate ARDS (Berlin moderate 100-200 inclusive) -> sedation reasonable -> no flag FALSE | strict 200>200 False -> criterio_2=False | yes |
| sedative_mid=5; diurna_pf=250; diurna_fio2=55; diurna_peep=8; diurna_sedoanalgesia=outros | FiO2 55% -> still meaningful support -> no flag FALSE | 55<50 False -> criterio_2=False | yes |

**Verifier notes**

Composite institutional decision rule; numeric cutoffs align with the Berlin ARDS definition (moderate/severe boundary at P/F 200) and PADIS light-sedation principle. Units are internally consistent (FiO2 percent, not the fraction/percent confusion seen in criterio_12). Method is DEFINED but UNWIRED (not called by calcular_criterios), so any issue would be inert; none found.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 311-351 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-043`

**Related rules:**

- [RULE-SEDACAO-005](RULE-SEDACAO-005-sedacao-v3-criterio-1-excessive-continuous-sedation-infusion.md)
- [RULE-SEDACAO-014](../alert-threshold/RULE-SEDACAO-014-sedacao-v3-alert-calcular-alerta-v2-used-legacy-calcular-ale.md)

## Notes

Unwired method retained for completeness.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
