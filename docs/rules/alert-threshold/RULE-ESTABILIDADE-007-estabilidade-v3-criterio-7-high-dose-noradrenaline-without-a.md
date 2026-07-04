# RULE-ESTABILIDADE-007 — Estabilidade v3 criterio_7 - high-dose noradrenaline without adjuncts (VERMELHO, wired)

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Noradrenaline > 20ml/h in last 4h AND (no vasopressin recorded in balanco OR no hydrocortisone prescribed). WIRED (contributes to VERMELHO alert).

## Inputs

| name | type | unit |
|---|---|---|
| balanco.qt_vol_nora | float | ml/h |
| balanco.qt_vol_vaso | float | ml/h |
| cpoe.hidrocortisona | float |  |

## Outputs

| name | type |
|---|---|
| criterio_7 | boolean |

## Logic

```text
return all([
  balanco_4h.filter(qt_vol_nora__gt=20).exists(),
  any([ not get_number(ultimo_balanco.qt_vol_vaso) > 0, not get_number(ultima_cpoe.hidrocortisona) > 0 ]),
]) if (balanco_4h and ultimo_balanco and ultima_cpoe) else False
```

## Edge cases (as implemented)

Refactored threshold: original docstring specified a 20-70 ml/h band; refactored code uses simply > 20 ml/h. Code matches the refactored docstring (no discrepancy).

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** Surviving Sepsis Campaign 2021 (Evans et al., Crit Care Med 2021): add vasopressin when norepinephrine is 0.25-0.5 mcg/kg/min instead of escalating; give IV hydrocortisone (50 mg q6h) when norepinephrine/epinephrine >=0.25 mcg/kg/min for >=4 h. ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486643/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | diff |
| units | diff |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| qt_vol_nora_mlh=25; qt_vol_vaso=0; hidrocortisona=0 | SSC: at ~0.38 mcg/kg/min (25 ml/h @64 mcg/mL,70 kg) adding vasopressin/hydrocortisone is reasonable, but the facade-displayed '>0.5 mcg/kg/min' is NOT met | nora>20 T, any([not vaso>0 T]) T -> True; alert text asserts >0.5 mcg/kg/min | no |
| qt_vol_nora_mlh=21; qt_vol_vaso=8; hidrocortisona=0 | SSC hydrocortisone anchor is >=0.25 mcg/kg/min sustained >=4 h; 21 ml/h ~0.32 mcg/kg/min but the >=4 h duration is never checked and units differ | nora>20 T (strict boundary just above 20), any([not hydro>0 T]) T -> True | no |
| qt_vol_nora_mlh=20; qt_vol_vaso=0; hidrocortisona=0 | 20 ml/h ~0.30 mcg/kg/min exceeds SSC 0.25 hydrocortisone anchor -> reference would prompt an adjunct | balanco_4h.filter(qt_vol_nora__gt=20) empty (strict >20) -> False -> criterion False (misses a case the mcg/kg/min anchor catches) | no |

**Verifier notes**

The CLINICAL CONCEPT (add vasopressin and/or hydrocortisone as adjuncts in high-dose vasopressor septic shock; flag when either adjunct is absent) is consistent with SSC-2021. The DISCREPANCY is a unit/threshold mismatch: the executed predicate fires on noradrenaline infusion volume >20 ml/h, while both the guideline anchor and the paired displayed facade text (RULE-016 criterio_7) are in mcg/kg/min (>0.5 displayed; 0.25-0.5 guideline). Under a plausible dilution the ml/h trigger fires at ~0.3-0.4 mcg/kg/min, below the 0.5 the clinician is shown. Moderate impact: the alert can fire at a materially different actual dose than the displayed threshold and misses the SSC 4-hour duration qualifier — a clinician may act on an unverified mcg/kg/min claim. WIRED (contributes to VERMELHO), so this is live. The ml/h cutoff itself is institution-specific/unverifiable.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_estabilidade.py` | 460-497 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-03-067`

**Related rules:**

- [RULE-ESTABILIDADE-014](RULE-ESTABILIDADE-014-estabilidade-v3-alert-level-calcular-alerta-calcular-alerta.md)
- [RULE-ESTABILIDADE-016](../drug-dosing/RULE-ESTABILIDADE-016-estabilidade-facade-alert-text-vasopressor-inotrope-escalati.md)
- [RULE-ESTABILIDADE-019](../care-pathway/RULE-ESTABILIDADE-019-estabilidade-manual-c3-high-noradrenaline-without-rescue-the.md)

## Notes

Displayed facade text (RULE-016 criterio_7) asserts "Noradrenalina >0,5mcg/kg/min" but this predicate fires on qt_vol_nora>20 ml/h — see divergence on RULE-016. Manual-pathway counterpart RULE-019 uses noradrenaline quantidade>21 (ml). SSC vasopressin/hydrocortisone adjunct anchor.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
