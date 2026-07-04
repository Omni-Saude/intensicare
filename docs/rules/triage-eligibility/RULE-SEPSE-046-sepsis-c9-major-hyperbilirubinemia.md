# RULE-SEPSE-046 — Sepsis C9 (major) - hyperbilirubinemia

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Major criterion - bilirubin > 2 mg/dL.

## Inputs

- bilirrubinas (float, mg/dL, 0-30)

## Outputs

- criterio_9 (bool)

## Logic

```text
(bilirrubinas > 2) if bilirrubinas else False
```

## Edge cases (as implemented)

Strict >2 (2 -> False). Test 2->False, 3->True.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Vincent JL et al. The SOFA score. Intensive Care Med 1996;22:707-710 (hepatic component: bilirubin 2.0-5.9 mg/dL = 2 points, organ dysfunction). Also ACCP/SCCM severe-sepsis organ-dysfunction lists (hyperbilirubinemia total bilirubin > 2 mg/dL / > 34 umol/L). ([source](https://link.springer.com/article/10.1007/BF01709751))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | threshold 2 mg/dL matches hepatic organ-dysfunction cutoff |
| units | mg/dL correct (SOFA/severe-sepsis use mg/dL; not umol/L) |
| ranges | input 0-30 mg/dL plausible |
| rounding | n/a |
| cutoffs | strict > 2; SOFA hepatic dysfunction begins at bilirubin = 2.0 (>=2 pts), so exactly 2.0 differs by one boundary point but published 'severe sepsis' lists phrase it as '> 2 mg/dL' |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| bilirrubinas=2.0 | false | false | yes |
| bilirrubinas=3.0 | true | true | yes |
| bilirrubinas=2.1 | true | true | yes |
| bilirrubinas=0 | false | false | yes |

**Verifier notes**

Major criterion. > 2 mg/dL is the standard hepatic organ-dysfunction threshold (SOFA 2-point band 2.0-5.9 mg/dL). Falsy guard means bilirubin 0 -> False (harmless). Units correct in mg/dL. Legacy confirmed at trilha_manual/models/trilha_sepse.py:325-330.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 325-330 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-034`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Test test_trilha_sepse.py:168-173.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
