# RULE-SEDACAO-010 — Sedacao v3 criterio_6 - high-dose neuromuscular blockade (defined, unwired)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | drug-dosing |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Rocuronium>16 OR cisatracurium>10 ml/h in each of the last two consecutive balances.

## Inputs

| name | type | unit |
|---|---|---|
| balanco.qt_vol_roc, balanco.qt_vol_cis (latest and previous) | float | ml/h |

## Outputs

| name | type |
|---|---|
| criterio_6 | boolean |

## Logic

```text
return all([
  any([ get_number(ultimo.qt_vol_roc)   > 16, get_number(ultimo.qt_vol_cis)   > 10 ]),
  any([ get_number(anterior.qt_vol_roc) > 16, get_number(anterior.qt_vol_cis) > 10 ]),
]) if ultimo_balanco and balanco_anterior else False
```

## Edge cases (as implemented)

Needs two consecutive balances. Strict > thresholds (roc>16, cis>10). Unwired in calcular_criterios.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No published ml/h anchor. Standard NMBA maintenance dosing is expressed in mcg/kg/min (cisatracurium ~1-3 mcg/kg/min; rocuronium ~8-12 mcg/kg/min) with TOF monitoring (PADIS 2018 / Murray MJ et al. Clinical practice guidelines for sustained neuromuscular blockade, Crit Care Med 2016). ml/h thresholds depend on local drug concentration. ([source](https://pubmed.ncbi.nlm.nih.gov/27635478/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | unverifiable - roc>16 / cis>10 are ml/h, concentration-dependent; cannot be mapped to published mcg/kg/min without the institution's dilution and patient weight |
| units | unverifiable - ml/h (infusion volume) vs published mcg/kg/min; no concentration provided to reconcile |
| ranges | n/a |
| rounding | n/a |
| cutoffs | unverifiable - 16 and 10 ml/h have no published anchor (institutional/concentration-specific) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| ultimo={"qt_vol_roc": 18}; anterior={"qt_vol_roc": 17} | unverifiable ml/h threshold; LOGIC check only: high-dose roc in both consecutive balances -> flag TRUE | any([18>16])T and any([17>16])T -> criterio_6=True | yes |
| ultimo={"qt_vol_roc": 16, "qt_vol_cis": 0}; anterior={"qt_vol_roc": 18} | LOGIC check: roc exactly 16 (strict > required) -> ultimo clause False -> no flag FALSE | any([16>16=False, 0>10=False])=False -> criterio_6=False | yes |
| ultimo={"qt_vol_cis": 12}; anterior={"qt_vol_cis": 8} | LOGIC check: cis high only in latest, not in previous balance -> requires BOTH -> no flag FALSE | ultimo any([roc0>16,12>10=T])=T; anterior any([0>16,8>10=F])=F -> criterio_6=False | yes |

**Verifier notes**

The two-consecutive-balance structure and the strict-'>' boundary handling trace correctly (vectors above), but the core numeric thresholds (rocuronium >16 ml/h, cisatracurium >10 ml/h) are volumetric infusion rates whose clinical meaning depends on local drug concentration and patient weight; standard NMBA dosing references are in mcg/kg/min, so these ml/h cutoffs cannot be verified against an authoritative published source. Flag for internal clinical review to confirm the ml/h values correspond to the intended high-dose (overdose) mcg/kg/min range for the institution's standard dilutions. Method is DEFINED but UNWIRED (not in calcular_criterios), so any threshold mis-setting would currently be inert.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sedacao.py` | 539-579 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-03-047`

**Related rules:**

- [RULE-SEDACAO-007](RULE-SEDACAO-007-sedacao-v3-criterio-3-neuromuscular-blockade-with-p-f-150-de.md)
- [RULE-SEDACAO-014](../alert-threshold/RULE-SEDACAO-014-sedacao-v3-alert-calcular-alerta-v2-used-legacy-calcular-ale.md)

## Notes

Unwired.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
