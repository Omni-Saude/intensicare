# RULE-CLINICAL-SCORING-001 — SOFA total score (sum of six organ sub-scores)

| Field | Value |
|---|---|
| Cluster | clinical-scoring |
| Category | clinical-scoring |
| Type | formula |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Total SOFA is the arithmetic sum of the six organ sub-scores; recomputed on every SOFA.save(). Surfaced in the prontuario payload and read (currently unused) by TrilhaSepse.buscar_score_sofa.

## Inputs

| name | type | unit |
|---|---|---|
| pontos_criterio_1 | int | points 0-4 |
| pontos_criterio_2 | int | points 0-4 |
| pontos_criterio_3 | int | points 0-4 |
| pontos_criterio_4 | int | points 0-4 |
| pontos_criterio_5 | int | points 0-4 |
| pontos_criterio_6 | int | points 0-4 |

## Outputs

| name | type | unit |
|---|---|---|
| escore_sofa | int | points 0-24 |

## Logic

```text
escore_sofa = pontos_criterio_1 + pontos_criterio_2 + pontos_criterio_3
            + pontos_criterio_4 + pontos_criterio_5 + pontos_criterio_6
```

## Edge cases (as implemented)

Any sub-score returning None (bilirubin gap in RULE-004 or renal gap in RULE-007) would raise on sum. Test: creatinina=6 -> 4; +plaquetas=15 -> +4 = 8.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Vincent JL, Moreno R, Takala J, et al. The SOFA (Sepsis-related Organ Failure Assessment) score to describe organ dysfunction/failure. Intensive Care Med. 1996;22(7):707-710. Total SOFA = arithmetic sum of the six organ sub-scores, range 0-24. ([source](https://link.springer.com/article/10.1007/BF01709751))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | ok (unweighted sum, each organ 0-4) |
| units | ok (points) |
| ranges | ok (0-24 total) |
| rounding | n/a (integer sum) |
| cutoffs | n/a (aggregation only) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| sub_scores=[0, 0, 0, 0, 0, 0] | 0 | 0 | yes |
| sub_scores=[4, 4, 0, 0, 0, 0]; note=creatinina=6 ->4, plaquetas=15000 ->4 | 8 | 8 | yes |
| sub_scores=[4, 4, 4, 4, 4, 4] | 24 | 24 | yes |

**Verifier notes**

Pure arithmetic sum matches the reference definition. Caveat (not a defect in this rule): if a sub-score returns None (bilirubin gaps in RULE-004 or creatinine gap in RULE-007) the sum() raises TypeError; that risk is owned by RULE-004/007, not the aggregation formula.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/sofa.py` | 156-166 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sofa-BE-10-010`

**Related rules:**

- [RULE-CLINICAL-SCORING-002](RULE-CLINICAL-SCORING-002-sofa-respiratory-sub-score-pao2-fio2.md)
- [RULE-CLINICAL-SCORING-003](RULE-CLINICAL-SCORING-003-sofa-coagulation-sub-score-platelets.md)
- [RULE-CLINICAL-SCORING-004](RULE-CLINICAL-SCORING-004-sofa-liver-sub-score-bilirubin.md)
- [RULE-CLINICAL-SCORING-005](RULE-CLINICAL-SCORING-005-sofa-cardiovascular-sub-score-vasopressors-map.md)
- [RULE-CLINICAL-SCORING-006](RULE-CLINICAL-SCORING-006-sofa-cns-sub-score-glasgow.md)
- [RULE-CLINICAL-SCORING-007](RULE-CLINICAL-SCORING-007-sofa-renal-sub-score-creatinine-urine-output.md)
- [RULE-CLINICAL-SCORING-011](RULE-CLINICAL-SCORING-011-sofa-attribute-sourcing-from-prontuario-model-save.md)
- [RULE-CLINICAL-SCORING-012](RULE-CLINICAL-SCORING-012-sofa-score-input-assembly-first-movimentacao.md)

## Notes

Test trilha_manual/tests/test_sofa.py:141-148.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
