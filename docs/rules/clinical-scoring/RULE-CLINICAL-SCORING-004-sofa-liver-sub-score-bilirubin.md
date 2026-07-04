# RULE-CLINICAL-SCORING-004 — SOFA liver sub-score (bilirubin)

| Field | Value |
|---|---|
| Cluster | clinical-scoring |
| Category | clinical-scoring |
| Type | scoring |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
SOFA organ-3 (liver) points from total bilirubin (mg/dL).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| bilirrubinas | float | mg/dL | 0-30 |

## Outputs

| name | type | unit |
|---|---|---|
| pontos_criterio_3 | int | points 0-4 |

## Logic

```text
if bilirrubinas == 0: 0
elif bilirrubinas < 1.2: 0
elif 1.2 <= bilirrubinas < 1.9: 1
elif 2   <= bilirrubinas < 5.9: 2
elif 6   <= bilirrubinas < 11.9: 3
elif bilirrubinas >= 12: 4
```

## Edge cases (as implemented)

GAP/None-return: values in [1.9,2.0), [5.9,6.0), [11.9,12.0) match NO branch and return None (implicit), later summed as if 0 or may error. Test only uses 1, 1.5, 3, 7, 14.

## Divergence

DISCREPANCY vs standard SOFA (mg/dL): <1.2=0, 1.2-1.9=1, 2.0-5.9=2, 6.0-11.9=3, >=12=4. Implementation uses strict < at the upper bounds (1.9, 5.9, 11.9) instead of <=, creating dead gaps [1.9,2.0), [5.9,6.0), [11.9,12.0) that return None. Reimplement VERBATIM including the gaps.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** Vincent JL et al. 1996 (SOFA), liver component. Total bilirubin mg/dL: <1.2=0, 1.2-1.9=1, 2.0-5.9=2, 6.0-11.9=3, >=12.0=4 (mmol/L: <20 / 20-32 / 33-101 / 102-204 / >204). ([source](https://link.springer.com/article/10.1007/BF01709751))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok (mg/dL) |
| ranges | diff (dead gaps introduced) |
| rounding | n/a |
| cutoffs | diff (upper bounds use strict < at 1.9/5.9/11.9 instead of <2.0/<6.0/<12.0) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| bilirrubinas=1.5 | 1 | 1 | yes |
| bilirrubinas=3.0 | 2 | 2 | yes |
| bilirrubinas=7.0 | 3 | 3 | yes |
| bilirrubinas=14.0 | 4 | 4 | yes |
| bilirrubinas=1.95 | 1 | None (no branch) | no |
| bilirrubinas=5.95 | 2 | None | no |
| bilirrubinas=11.95 | 3 | None | no |

**Verifier notes**

Confirms extraction flag. Band upper bounds are strict-< at 1.9, 5.9 and 11.9, leaving dead intervals [1.9,2.0), [5.9,6.0), [11.9,12.0) that match no branch and return None. Bilirubin 1.95/5.95/11.95 mg/dL should score 1/2/3 but returns None, which makes calcular_escore_sofa (RULE-001) raise TypeError on sum() or mis-sum. Moderate impact: affected values are narrow (0.1 mg/dL) but land on clinically plausible results and can crash the SOFA computation for that patient. Reproduce verbatim including the gaps.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/sofa.py` | 100-112 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sofa-BE-10-006`

**Related rules:**

- [RULE-CLINICAL-SCORING-001](RULE-CLINICAL-SCORING-001-sofa-total-score-sum-of-six-organ-sub-scores.md)

## Notes

Test test_sofa.py:62-73.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
