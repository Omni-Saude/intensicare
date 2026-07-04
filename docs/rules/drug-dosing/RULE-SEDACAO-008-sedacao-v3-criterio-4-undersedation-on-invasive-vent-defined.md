# RULE-SEDACAO-008 — Sedacao v3 criterio_4 - undersedation on invasive vent (defined, unwired)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | drug-dosing |
| Type | threshold |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
RASS>=-2 AND invasive VM AND (P/F<200 OR PINS>=20 OR FiO2>=60) AND absence of midazolam/propofol/cetamina in the last two consecutive balances.

## Inputs

| name | type | unit |
|---|---|---|
| evolucao.rass, diurna_ventilacao, diurna_pf, diurna_pins, diurna_fio2 | int / string / float |  |
| balanco.qt_vol_mid/pro/cet | float | ml/h |

## Outputs

| name | type |
|---|---|
| criterio_4 | boolean |

## Logic

```text
return all([
  int(evolucao.rass) >= -2 if evolucao.rass else False,
  evolucao.diurna_ventilacao == "VM invasiva",
  any([ get_number(diurna_pf) < 200, get_number(diurna_pins) >= 20, get_number(diurna_fio2) >= 60 ]),
  any([ not ultimo_balanco.qt_vol_mid,   not ultimo_balanco.qt_vol_pro,   not ultimo_balanco.qt_vol_cet ]),
  any([ not balanco_anterior.qt_vol_mid, not balanco_anterior.qt_vol_pro, not balanco_anterior.qt_vol_cet ]),
]) if ultimo_balanco and ultima_evolucao and balanco_anterior else False
```

## Edge cases (as implemented)

The "absence of sedatives" clauses use any([not a, not b, not c]) - True if ANY ONE sedative is absent, not requiring all absent; weaker than the intended "ausencia de midazolam OU propofol OU cetamina". diurna_ventilacao requires exact string "VM invasiva".

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Devlin JW et al. PADIS Guidelines. Crit Care Med 2018;46(9):e825-e873 (light sedation defined RASS +1 to -2). Berlin Definition, JAMA 2012 (moderate ARDS P/F 100-200). ([source](https://pubmed.ncbi.nlm.nih.gov/30113379/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | ok |
| units | ok - RASS integer, P/F mmHg, PINS cmH2O, FiO2 percent (>=60); units internally consistent |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok - RASS>=-2 is exactly the PADIS light-sedation upper boundary; P/F<200 = moderate/severe ARDS (Berlin); FiO2>=60% and PINS>=20 are high-support cutoffs |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| rass=0; diurna_ventilacao=VM invasiva; diurna_pf=180; ultimo={"qt_vol_mid": 0, "qt_vol_pro": 0, "qt_vol_cet": 0}; anterior={"qt_vol_mid": 0, "qt_vol_pro": 0, "qt_vol_cet": 0} | Lightly sedated (RASS0), invasive VM, moderate ARDS (P/F180), NO sedatives -> undersedated with high needs -> flag TRUE | rass0>=-2 T; vent T; any([180<200,..]) T; any([not0,not0,not0])=T both -> criterio_4=True | yes |
| rass=0; diurna_ventilacao=VM invasiva; diurna_pf=180; ultimo={"qt_vol_mid": 10, "qt_vol_pro": 0, "qt_vol_cet": 0}; anterior={"qt_vol_mid": 10, "qt_vol_pro": 0, "qt_vol_cet": 0} | Midazolam IS running (10 ml/h) -> patient IS receiving sedation -> 'absence of midazolam OU propofol OU cetamina' not satisfied -> no flag FALSE | any([not 10, not 0, not 0])=any([False,True,True])=True (propofol/cetamina absent) -> criterio_4=True (FLAGS despite active midazolam) | no |
| rass=-3; diurna_ventilacao=VM invasiva; diurna_pf=180; ultimo={"qt_vol_mid": 0, "qt_vol_pro": 0, "qt_vol_cet": 0}; anterior={"qt_vol_mid": 0} | RASS -3 = deep sedation, below the >=-2 light threshold -> not undersedated -> no flag FALSE | int(-3)>=-2 False -> criterio_4=False | yes |

**Verifier notes**

Clinical THRESHOLDS verify against reference (RASS>=-2 = PADIS light-sedation boundary; P/F<200 = Berlin moderate; FiO2>=60, PINS>=20 high-support). The discrepancy is an internal code-vs-intent boolean-logic defect, NOT a reference-numeric mismatch: the 'absence of sedatives' clauses use any([not mid, not pro, not cet]), which is TRUE whenever ANY ONE of the three sedatives is absent, so the criterion fires even while another sedative is actively infusing (see vector 2). Intended semantics ('ausencia de midazolam OU propofol OU cetamina' -> none present) would require all([not mid, not pro, not cet]). Impact low: method is UNWIRED (not called by calcular_criterios), and even if wired it is an advisory over-trigger (false positives), not an automated dosing action.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 387-445 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-045`

**Related rules:**

- [RULE-SEDACAO-014](../alert-threshold/RULE-SEDACAO-014-sedacao-v3-alert-calcular-alerta-v2-used-legacy-calcular-ale.md)

## Notes

AMBIGUOUS - any([not ...]) semantics likely unintended (should be none/all absent). Unwired. Preserved verbatim.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
