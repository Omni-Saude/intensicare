# RULE-SEPSE-048 — Sepsis C11 (minor) - tachycardia

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | threshold |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
Minor criterion - heart rate > 100 bpm using 24h value (falling back to 12h).

## Inputs

- fc_24hrs (int, bpm)
- fc_12hrs (int, bpm)

## Outputs

- criterio_11 (bool)

## Logic

```text
fc_24hrs = filter(lookback, criado_em>now-24h).values_list('frequencia_cardiaca').first()
fc_12hrs = filter(lookback, criado_em>now-12h).values_list('frequencia_cardiaca').first()
return (fc_24hrs>100) if fc_24hrs else (False or fc_12hrs>100) if fc_12hrs else False
# parsed: if fc_24hrs: fc_24hrs>100 ; elif fc_12hrs: fc_12hrs>100 ; else False
```

## Edge cases (as implemented)

Because 12h data is a subset of 24h, the 24h branch dominates; 12h branch only reached when no 24h value. Strict >100.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** ACCP/SCCM Consensus Conference (Bone RC et al.), Chest 1992;101:1644-1655. SIRS heart-rate criterion: HR > 90 bpm. ([source](https://pubmed.ncbi.nlm.nih.gov/1303622/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | diff - legacy uses HR > 100 bpm; SIRS tachycardia criterion is HR > 90 bpm |
| units | bpm correct |
| ranges | plausible |
| rounding | n/a |
| cutoffs | diff - strict > 100 vs SIRS strict > 90; 12h fallback branch uses same 100 threshold |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| fc_24hrs=110 | true | true | yes |
| fc_24hrs=95 | true | false | no |
| fc_24hrs=100 | true | false | no |
| fc_24hrs=90 | false | false | yes |
| fc_24hrs=; fc_12hrs=105 | true | true | yes |

**Verifier notes**

Threshold discrepancy: legacy fires only at HR > 100, but the SIRS tachycardia criterion is HR > 90, so HR 91-100 bpm is silently missed on this minor criterion (reduced sensitivity). The catalog AMBIGUOUS status concerns conditional-expression precedence (collapses to 'use 24h value if present else 12h'); both branches apply the same >100 cutoff, so the threshold difference vs SIRS holds regardless of branch. Clinical tachycardia is often defined generically as >100, so this may be an institutional choice; documented as difference, not corrected. Legacy confirmed at trilha_sepse.py:343-364.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 343-364 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-036`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

AMBIGUOUS: convoluted conditional-expression precedence; the intended OR of 24h/12h collapses to "use 24h if present else 12h". Test test_trilha_sepse.py:189-201 (fc=110->True).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
