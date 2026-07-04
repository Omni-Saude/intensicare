# RULE-SEDACAO-007 — Sedacao v3 criterio_3 - neuromuscular blockade with P/F>150 (defined, unwired)

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
P/F>150 AND (rocuronium OR cisatracurium) recorded in the last two consecutive balances.

## Inputs

| name | type | unit |
|---|---|---|
| evolucao.diurna_pf | float | ratio |
| balanco.qt_vol_roc, balanco.qt_vol_cis | float | ml/h |

## Outputs

| name | type |
|---|---|
| criterio_3 | boolean |

## Logic

```text
return all([
  get_number(evolucao.diurna_pf) > 150,
  any([ ultimo_balanco.qt_vol_roc,   ultimo_balanco.qt_vol_cis ]),
  any([ balanco_anterior.qt_vol_roc, balanco_anterior.qt_vol_cis ]),
]) if ultimo_balanco and ultima_evolucao and balanco_anterior else False
```

## Edge cases (as implemented)

Two consecutive balances = balancos[0] and balancos[1] (needs >=2 records). Unwired.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Papazian L et al. Early Neuromuscular Blockade in ARDS (ACURASYS). NEJM 2010;363:1107-1116 (cisatracurium benefit shown only in severe ARDS PaO2/FiO2 <150). Moss M et al. ROSE trial, NEJM 2019 (no benefit in moderate-severe). ([source](https://pubmed.ncbi.nlm.nih.gov/20843245/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | ok |
| units | ok - P/F in mmHg; NMBA presence flags (qt_vol_roc/cis, ml/h) used only as boolean presence here |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok - P/F>150 threshold to reconsider stopping continuous NMBA is the exact complement of the ACURASYS severe-ARDS entry cutoff (<150), where NMBA benefit is established |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| diurna_pf=200; ultimo={"qt_vol_roc": 5}; anterior={"qt_vol_roc": 5} | P/F 200 >150 -> above severe-ARDS threshold, NMBA benefit questionable -> flag TRUE | 200>150 True, any([roc])True, any([roc])True -> criterio_3=True | yes |
| diurna_pf=140; ultimo={"qt_vol_roc": 5}; anterior={"qt_vol_roc": 5} | P/F 140 <150 = severe ARDS -> NMBA justified (ACURASYS) -> no flag FALSE | 140>150 False -> criterio_3=False | yes |
| diurna_pf=150; ultimo={"qt_vol_roc": 5}; anterior={"qt_vol_roc": 5} | P/F=150 = ACURASYS boundary (severe is <150); at 150 NMBA still reasonable -> no flag FALSE | strict 150>150 False -> criterio_3=False | yes |
| diurna_pf=200; ultimo={"qt_vol_roc": 5}; anterior={"qt_vol_roc": 0, "qt_vol_cis": 0} | NMBA not present in BOTH of last 2 balances -> criterion requires 2 consecutive -> no flag FALSE | any([anterior roc0,cis0])=False -> criterio_3=False | yes |

**Verifier notes**

Cutoff P/F>150 matches ACURASYS/ROSE evidence that continuous NMBA benefit is confined to severe ARDS (<150). Consistent with the facade recommendation text (RULE-SEDACAO-024 crit3: 'beneficio questionavel sem PRONA e P/F>150'). Method DEFINED but UNWIRED; inert. No discrepancy.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 353-385 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-044`

**Related rules:**

- [RULE-SEDACAO-010](RULE-SEDACAO-010-sedacao-v3-criterio-6-high-dose-neuromuscular-blockade-defin.md)
- [RULE-SEDACAO-014](../alert-threshold/RULE-SEDACAO-014-sedacao-v3-alert-calcular-alerta-v2-used-legacy-calcular-ale.md)

## Notes

Unwired.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
