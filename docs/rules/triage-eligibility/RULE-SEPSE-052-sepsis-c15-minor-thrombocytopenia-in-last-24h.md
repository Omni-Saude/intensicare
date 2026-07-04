# RULE-SEPSE-052 — Sepsis C15 (minor) - thrombocytopenia in last 24h

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | low |

## Rule
Minor criterion - most-recent 24h platelets < 100000/mm3.

## Inputs

- plaquetas (int, /mm3, 0-700000)

## Outputs

- criterio_15 (bool)

## Logic

```text
plaquetas = filter(lookback, criado_em>now-24h).values_list('plaquetas').first()
(plaquetas < 100000) if plaquetas else False
```

## Edge cases (as implemented)

plaquetas falsy (0/None) -> False (so 0 platelets recorded as 0 not flagged). Strict <100000. Test 100000->False, 99999->True.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** low
- **Reference:** Levy MM et al. 2001 SCCM/ESICM/ACCP/ATS/SIS International Sepsis Definitions Conference (Crit Care Med 2003;31:1250) - thrombocytopenia (platelet <100,000/uL) listed as an organ-dysfunction variable; Vincent JL et al. SOFA score (Intensive Care Med 1996;22:707) coagulation subscore = 2 points at platelets <100 x10^3/uL. ([source](https://www.mdcalc.com/calc/691/sequential-organ-failure-assessment-sofa-score))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | platelet cutoff 100,000/mm3 matches severe-sepsis organ-dysfunction / SOFA coag-2 threshold |
| units | /mm3 (cells/uL) - correct |
| ranges | 0-700000 plausible; strict < comparison |
| rounding | n/a |
| cutoffs | < 100000 strict matches reference |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| plaquetas=100000 | not thrombocytopenic at threshold (<100000 strict) -> False | 100000<100000 -> False | yes |
| plaquetas=99999 | thrombocytopenia -> True | 99999<100000 -> True | yes |
| plaquetas=50000 | thrombocytopenia -> True | True | yes |
| plaquetas=0 | profound thrombocytopenia -> POSITIVE | 0 is falsy -> False (not flagged) | no |

**Verifier notes**

Cutoff, units and strict-< direction match the recognized platelet <100,000/uL organ-dysfunction threshold. Only mismatch is the falsy-guard edge: a recorded platelet value of exactly 0 (or None) returns False instead of positive; a true platelet count of 0 is not physiologically real, so impact is low. Test test_trilha_sepse.py:240-252 confirms 100000->False, 99999->True.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 404-413 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-040`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Test test_trilha_sepse.py:240-252.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
