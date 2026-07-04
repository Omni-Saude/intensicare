# RULE-CLINICAL-SCORING-002 — SOFA respiratory sub-score (PaO2/FiO2)

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
SOFA organ-1 (respiration) points from the PaO2/FiO2 ratio, computed inline in sofa.py.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| po2 | float | mmHg | 0-500 |
| fio2 | float | fraction (per thresholds) |  |

## Outputs

| name | type | unit |
|---|---|---|
| pontos_criterio_1 | int | points 0-4 |

## Logic

```text
if not (po2 > 0 and fio2 > 0): return 0
ratio = po2 / fio2
if ratio >= 400: 0
elif 300 <= ratio < 400: 1
elif 200 <= ratio < 300: 2
elif 100 <= ratio < 200: 3
elif ratio < 100: 4
```

## Edge cases (as implemented)

Missing po2/fio2 -> 0 points. Boundaries [lo,hi) inclusive-low. Test confirms po2=500->0, 350->1, 250->2, 150->3, 50->4 (with fio2=1).

## Divergence

UNIT DISCREPANCY: thresholds are the standard P/F cutoffs which require FiO2 as a fraction (0.21-1.0), but the DadosProntuario FiO2Validator stores 21-100 (percentage). With a percentage FiO2 the ratio is ~100x too small vs standard P/F. Tests set attributes directly (fio2=1) bypassing the validator. See RULE-008. Same bilirubin-style strict-upper-bound convention is NOT present here (all bands contiguous).

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** high
- **Reference:** Vincent JL et al. 1996 (SOFA), respiration component. PaO2/FiO2 in mmHg with FiO2 as a FRACTION (0.21-1.0): >=400=0, 300-399=1, 200-299=2, 100-199=3 (requires respiratory support), <100=4 (requires respiratory support). ([source](https://www.ebmedicine.net/media_library/files/Calculated%20Decisions%20E1018%20Sepsis.pdf))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok (ratio = PaO2/FiO2) |
| coefficients | n/a |
| units | diff (FiO2 must be a fraction 0.21-1.0; DadosProntuario FiO2Validator stores 21-100 percent -> ratio ~100x too small) |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok (400/300/200/100 boundaries match; inclusive-low [lo,hi) reproduces reference bands) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| po2=350; fio2=1.0 | 1 | 1 | yes |
| po2=250; fio2=1.0 | 2 | 2 | yes |
| po2=50; fio2=1.0 | 4 | 4 | yes |
| po2=350; fio2=100; note=FiO2 stored as percent per validator | 1 | 4 | no |
| po2=0; fio2=1.0 | 0 (no data) | 0 | yes |

**Verifier notes**

Two issues. (1) UNIT: cutoffs are correct P/F thresholds but presume FiO2 as a fraction; the model's FiO2Validator stores 21-100 (percent), so with real persisted data the ratio is ~100x too small and nearly every ventilated patient scores 4 (worst) instead of the true band, inflating total SOFA. Tests set fio2=1 directly, masking this. (2) Reference gates the 3- and 4-point bands on respiratory support (mechanical ventilation); legacy applies them unconditionally, over-scoring a spontaneously breathing patient with a low ratio. High impact: both errors push the respiratory sub-score upward and can change sepsis-driven escalation.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/sofa.py` | 69-84 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sofa-BE-10-004`

**Related rules:**

- [RULE-CLINICAL-SCORING-001](RULE-CLINICAL-SCORING-001-sofa-total-score-sum-of-six-organ-sub-scores.md)
- [RULE-CLINICAL-SCORING-008](../physiological-calculation/RULE-CLINICAL-SCORING-008-pao2-fio2-ratio-relacao-po2-fio2.md)

## Notes

Test trilha_manual/tests/test_sofa.py:35-47. FiO2 unit inconsistency detailed in RULE-008.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
