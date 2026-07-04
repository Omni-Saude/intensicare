# RULE-CLINICAL-SCORING-007 — SOFA renal sub-score (creatinine/urine output)

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
SOFA organ-6 (renal) points from serum creatinine OR 24h urine output.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| creatinina | float | mg/dL | 0-20 |
| debito_urinario_24h | float | mL/24h | 0-10000 |

## Outputs

| name | type | unit |
|---|---|---|
| pontos_criterio_6 | int | points 0-4 |

## Logic

```text
if any([creatinina > 5, 0 < debito < 200]): 4
elif any([3.5 <= creatinina <= 4.9, 0 < debito < 500]): 3
elif 2   <= creatinina <= 4:   2
elif 1.2 <= creatinina <= 1.9: 1
elif 0 < creatinina < 1.2:     0
else: 0
```

## Edge cases (as implemented)

GAP: creatinina == 5.0 and creatinina in (4.9,5.0] match NO creatinine branch (not >5, not 3.5-4.9, not 2-4, not 1.2-1.9, not <1.2); fall to else -> 0 unless urine output triggers. debito uses OPEN-low bound (0 < debito): debito==0 ignored. Urine <200 -> 4, <500 -> 3. Overlap creatinina 3.5-4.0 resolves to 3 (checked before the 2..4 branch via any()).

## Divergence

DISCREPANCY vs standard SOFA renal (Cr mg/dL): <1.2=0, 1.2-1.9=1, 2.0-3.4=2, 3.5-4.9=3, >=5.0=4; urine <500=3, <200=4. Here the '2 points' band is 2.0-4.0 (standard 2.0-3.4) and '>5' is strict leaving a dead gap at (4.9,5.0]. Reproduce VERBATIM.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** high
- **Reference:** Vincent JL, et al. SOFA score, Intensive Care Med. 1996;22(7):707-710. Renal component (serum creatinine, mg/dL, OR urine output): <1.2=0, 1.2-1.9=1, 2.0-3.4=2, 3.5-4.9=3, >=5.0 (>440 umol/L)=4; urine <500 mL/day=3, <200 mL/day=4. Confirmed via MDCalc/Medscape SOFA calculator. ([source](https://reference.medscape.com/calculator/268/sequential-organ-failure-assessment-sofa))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok |
| ranges | diff |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| creatinina=6.0; debito_urinario_24h=0 | 4 | 4 | yes |
| creatinina=5.0; debito_urinario_24h=0 | 4 | 0 | no |
| creatinina=4.95; debito_urinario_24h=0 | 4 | 0 | no |
| creatinina=3.7; debito_urinario_24h=0 | 3 | 3 | yes |
| creatinina=2.5; debito_urinario_24h=0 | 2 | 2 | yes |
| creatinina=0; debito_urinario_24h=450 | 3 | 3 | yes |
| creatinina=0; debito_urinario_24h=50 | 4 | 4 | yes |

**Verifier notes**

Two deviations from standard SOFA renal. (1) The 4-point creatinine test is strict (`creatinina > 5`) while standard is >=5.0, and no band covers (4.9, 5.0], so a creatinine of exactly 5.0 mg/dL - a commonly reported exact value denoting severe renal failure (standard 4 points) - falls through every branch to else and scores 0 renal points. That is a 4-point undercount at the top of the scale. (2) The nominal 2-point band is written 2.0-4.0 (standard 2.0-3.4), but because the 3-point branch (3.5-4.9) is evaluated first via elif, creatinine 3.5-4.0 correctly resolves to 3; the practical 2-point range is 2.0 to <3.5, effectively equivalent to standard, so (2) causes no wrong scores except a hairline reference gap at (3.4, 3.5). Urine-output cutoffs (<200=4, <500=3, strict) match standard; debito==0 is ignored (open-low bound), treated as no data. Impact rated high because Cr=5.0 mg/dL is a realistic, frequently-reported exact value and the failure silently zeroes the renal subscore, lowering total SOFA and potentially mis-triaging a patient in severe renal failure.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/sofa.py` | 142-154 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sofa-BE-10-009`

**Related rules:**

- [RULE-CLINICAL-SCORING-001](RULE-CLINICAL-SCORING-001-sofa-total-score-sum-of-six-organ-sub-scores.md)

## Notes

Test test_sofa.py:121-139 (creatinina 3.7->3, 6->4, debito 450->3 via any(), debito 50->4).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
