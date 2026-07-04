# RULE-CLINICAL-SCORING-006 — SOFA CNS sub-score (Glasgow)

| Field | Value |
|---|---|
| Cluster | clinical-scoring |
| Category | clinical-scoring |
| Type | scoring |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
SOFA organ-5 (neurological) points from Glasgow Coma Scale.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| glasgow | int | GCS points | 0 or 3-15 |

## Outputs

| name | type | unit |
|---|---|---|
| pontos_criterio_5 | int | points 0-4 |

## Logic

```text
if glasgow == 15: 0
elif glasgow in [13,14]: 1
elif glasgow in [10,11,12]: 2
elif glasgow in [6,7,8,9]: 3
elif 0 < glasgow <= 6: 4     # only reaches for glasgow 1..5 (6 already caught above)
else: 0                       # glasgow 0 or >15 -> 0
```

## Edge cases (as implemented)

glasgow==6 -> 3 (caught by prior branch; the <=6 upper bound is partly dead). glasgow 0 or >15 -> 0. Test enumerates 1..16.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Vincent JL, Moreno R, Takala J, et al. The SOFA (Sepsis-related Organ Failure Assessment) score to describe organ dysfunction/failure. Intensive Care Med. 1996;22(7):707-710. Neurological component (Glasgow Coma Scale): GCS 15=0, 13-14=1, 10-12=2, 6-9=3, <6=4. Confirmed via MDCalc/Medscape SOFA calculator. ([source](https://reference.medscape.com/calculator/268/sequential-organ-failure-assessment-sofa))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| glasgow=15 | 0 | 0 | yes |
| glasgow=13 | 1 | 1 | yes |
| glasgow=11 | 2 | 2 | yes |
| glasgow=9 | 3 | 3 | yes |
| glasgow=6 | 3 | 3 | yes |
| glasgow=3 | 4 | 4 | yes |

**Verifier notes**

Legacy bands (15=0, 13-14=1, 10-12=2, 6-9=3, 1-5=4) map exactly onto the original SOFA CNS cutoffs across the valid GCS range 3-15. The `0 < glasgow <= 6` branch is partly dead (glasgow==6 is already captured by the prior [6,7,8,9] branch, correctly yielding 3), so only glasgow 1-5 reach it -> 4, which is correct. Out-of-range sentinels (glasgow==0 default / >15) fall to else -> 0 points, i.e. treated as "no data"; benign because valid GCS is 3-15 (RULE-013). No numeric discrepancy.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/sofa.py` | 128-140 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sofa-BE-10-008`

**Related rules:**

- [RULE-CLINICAL-SCORING-001](RULE-CLINICAL-SCORING-001-sofa-total-score-sum-of-six-organ-sub-scores.md)
- [RULE-CLINICAL-SCORING-013](RULE-CLINICAL-SCORING-013-glasgow-coma-scale-valid-range-3-15.md)

## Notes

Standard SOFA GCS 15=0, 13-14=1, 10-12=2, 6-9=3, <6=4. Matches (glasgow 1-5 -> 4). Test test_sofa.py:86-119.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
