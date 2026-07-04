# RULE-CLINICAL-SCORING-005 — SOFA cardiovascular sub-score (vasopressors/MAP)

| Field | Value |
|---|---|
| Cluster | clinical-scoring |
| Category | clinical-scoring |
| Type | scoring |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | high |

## Rule
SOFA organ-4 (cardiovascular) points from noradrenaline dose, dobutamine presence, and MAP.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| noradrenalina | float | ml (Noradrenalina.quantidade), NOT mcg/kg/min | 0-200 |
| dobutamina | float | ml/h | 0-30 |
| pam | float | mmHg |  |

## Outputs

| name | type | unit |
|---|---|---|
| pontos_criterio_4 | int | points 0-4 |

## Logic

```text
if noradrenalina > 10: 4
elif 0 < noradrenalina <= 10: 3
elif dobutamina > 0: 2
elif 0 < pam < 70: 1
elif pam >= 70: 0
else: 0
```

## Edge cases (as implemented)

Priority order noradrenaline > dobutamine > MAP. pam==0 with no drugs -> else 0. Test pam=50->1, +dobutamina5->2, +noradrenalina5->3, noradrenalina20->4.

## Divergence

DISCREPANCY: standard SOFA cardiovascular uses vasopressor RATES in mcg/kg/min (norepi >0.1=4, <=0.1=3; dopamine/epinephrine tiers; dobutamine any=2; MAP<70=1). Here noradrenaline is a raw ml volume (Noradrenalina.quantidade) with cutoff 10, and dobutamine is any>0=2. MAP<70=1 matches standard. Non-standard dosing units.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** high
- **Reference:** Vincent JL et al. 1996 (SOFA), cardiovascular component. Vasopressor doses in mcg/kg/min sustained >=1h: MAP>=70=0; MAP<70=1; dopamine<=5 OR dobutamine (any dose)=2; dopamine>5 OR epinephrine<=0.1 OR norepinephrine<=0.1=3; dopamine>15 OR epinephrine>0.1 OR norepinephrine>0.1=4. ([source](https://www.ebmedicine.net/media_library/files/Calculated%20Decisions%20E1018%20Sepsis.pdf))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | diff (norepinephrine split at 10 raw ml vs reference 0.1 mcg/kg/min for the 3-vs-4 band) |
| units | diff (noradrenalina = Noradrenalina.quantidade in ml volume, NOT a mcg/kg/min rate) |
| ranges | diff (norepi any >0 -> min 3 pts; dopamine/epinephrine tiers absent) |
| rounding | n/a |
| cutoffs | partial (MAP<70=1 and MAP>=70=0 match; dobutamine any>0=2 matches) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| pam=80; noradrenalina=0; dobutamina=0 | 0 | 0 | yes |
| pam=50; noradrenalina=0; dobutamina=0 | 1 | 1 | yes |
| pam=50; noradrenalina=0; dobutamina=5 | 2 | 2 | yes |
| pam=50; noradrenalina=5; dobutamina=5; note=norepi 5 mcg/kg/min is a very high rate | 4 | 3 | no |
| pam=50; noradrenalina=20; dobutamina=0 | 4 | 4 | no |

**Verifier notes**

Confirms extraction flag. MAP bands (>=70=0, <70=1) and dobutamine-any=2 match the reference. Norepinephrine handling does not: legacy reads a raw ml VOLUME (Noradrenalina.quantidade) and splits 3 vs 4 points at >10 ml, whereas the reference uses an infusion RATE (mcg/kg/min) with the 3/4 split at 0.1. The mapping is incoherent (10 ml is not comparable to 0.1 mcg/kg/min), so any patient on norepinephrine can be mis-tiered in either direction depending on how the ml value was recorded. Legacy also omits dopamine and epinephrine entirely. High impact: cardiovascular is a frequent SOFA driver and this can materially mis-score shock severity. Reproduce verbatim.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/sofa.py` | 114-126 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sofa-BE-10-007`

**Related rules:**

- [RULE-CLINICAL-SCORING-001](RULE-CLINICAL-SCORING-001-sofa-total-score-sum-of-six-organ-sub-scores.md)
- [RULE-CLINICAL-SCORING-009](../physiological-calculation/RULE-CLINICAL-SCORING-009-mean-arterial-pressure-pam-from-pas-pad.md)

## Notes

Test test_sofa.py:75-84. pam feeds from RULE-009 (MAP formula).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
