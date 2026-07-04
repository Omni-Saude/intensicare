# RULE-SEPSE-044 — Sepsis C7 (major) - oliguria or rising creatinine

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | decision-tree |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Major criterion - 24h urine output <= 1200 ml OR (creatinine > 2 AND not on hemodialysis).

## Inputs

- debito_urinario_24h (float, mL/24h, 0-10000)
- creatinina (float, mg/dL, 0-20)
- hemodialise (bool)

## Outputs

- criterio_7 (bool)

## Logic

```text
any([
  (debito_urinario_24h <= 1200) if debito_urinario_24h else False,
  all([(creatinina > 2) if creatinina else False, not hemodialise])])
```

## Edge cases (as implemented)

debito 0 -> falsy -> that disjunct False (so anuria recorded as 0 is NOT flagged). Inclusive <=1200. Test debito 1200->True,1201->False; creat 3 with hemodialise True->False.

## Divergence

DISCREPANCY: fixed 1200 mL/24h threshold rather than weight-based (<0.5 mL/kg/h). _ANTIGAS_REGRAS used the weight-based version. Also debito==0 evaluates falsy so true anuria is excluded. Test test_trilha_sepse.py:140-151.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** SOFA renal component (Vincent JL et al. Intensive Care Med 1996;22:707-710): creatinine 2.0-3.4 mg/dL = 2 pts; urine < 500 mL/day = 3 pts; < 200 mL/day = 4 pts. KDIGO 2012 AKI oliguria = urine output < 0.5 mL/kg/h (~840 mL/24h for a 70 kg adult). ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC6880479/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | diff |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| debito_urinario_24h=1200; creatinina=0.9; hemodialise=false | 1200 mL/24h (~0.71 mL/kg/h @70kg) NOT oliguric by SOFA(<500)/KDIGO(<0.5) -> False | true | no |
| debito_urinario_24h=1201; creatinina=0.9; hemodialise=false | not oliguric -> False | false | yes |
| debito_urinario_24h=0; creatinina=0.9; hemodialise=false | anuria (0 mL) = severe AKI -> True | false | no |
| debito_urinario_24h=2000; creatinina=3; hemodialise=false | creat 3.0 mg/dL = SOFA renal 2 pts -> True | true | yes |
| debito_urinario_24h=2000; creatinina=3; hemodialise=true | on HD, creat not interpretable as new AKI -> exclude | false | yes |

**Verifier notes**

Two documented differences vs reference. (1) Oliguria uses a fixed <=1200 mL/24h threshold (lines 291-293), far above the SOFA oliguria cut (<500 mL/day) and the KDIGO weight-based cut (0.5 mL/kg/h ~ 840 mL/24h @70kg): a urine output of 1200 mL/24h is normal yet fires this MAJOR criterion -> over-triggering / false positives. (2) debito_urinario_24h == 0 is falsy, so true anuria (the most severe case) is EXCLUDED from the oliguria disjunct -> false negative in the sickest patients (mitigated only if creatinine is concurrently >2). The creatinine >2 not-on-HD disjunct aligns with the SOFA 2-point renal cutoff (strict >2 vs SOFA >=2.0 means creatinine exactly 2.0 is not flagged - minor boundary nuance). Net moderate impact: bidirectional error (false positives from the 1200 cut, false negative on anuria). Matches extraction DISCREPANCY status.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 288-303 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-032`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

DISCREPANCY: fixed 1200 mL/24h threshold rather than weight-based (<0.5 mL/kg/h). _ANTIGAS_REGRAS used the weight-based version. Also debito==0 evaluates falsy so true anuria is excluded. Test test_trilha_sepse.py:140-151.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
