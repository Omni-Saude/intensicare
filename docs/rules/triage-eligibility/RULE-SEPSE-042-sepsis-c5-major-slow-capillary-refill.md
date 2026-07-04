# RULE-SEPSE-042 — Sepsis C5 (major) - slow capillary refill

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
Major criterion - capillary refill time > 5 s.

## Inputs

- tec (int, seconds, 0 or 3-20)

## Outputs

- criterio_5 (bool)

## Logic

```text
(tec > 5) if tec else False
```

## Edge cases (as implemented)

tec 0 -> False. Strict >5. Test tec=5->False, 6->True.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Hernandez G et al. (ANDROMEDA-SHOCK) Effect of a Resuscitation Strategy Targeting Peripheral Perfusion Status vs Serum Lactate Levels on 28-Day Mortality Among Patients With Septic Shock. JAMA 2019;321(7):654-664. Abnormal capillary refill time (CRT) defined as > 3 seconds (glass-slide technique, distal phalanx). SSC 2021 endorses CRT-guided resuscitation. ([source](https://jamanetwork.com/journals/jama/fullarticle/2724361))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| tec=6 | abnormal CRT (>3s) -> True | true | yes |
| tec=5 | abnormal CRT (>3s) -> True | false | no |
| tec=4 | abnormal CRT (>3s) -> True | false | no |
| tec=3 | not >3s -> normal -> False | false | yes |
| tec=0 | not recorded/normal -> False | false | yes |

**Verifier notes**

Legacy (line 270) fires only when CRT > 5 s; the published abnormal-perfusion threshold (ANDROMEDA-SHOCK, SSC 2021) is > 3 s. The 5 s cut is stricter/more specific, so patients with CRT 3.1-5.0 s (established hypoperfusion by the reference) are missed by this major criterion. Low impact: CRT is one of several major criteria and the overall alert still requires >=2 majors AND >=3 minors; the 5 s cut is also internally consistent with the homecare 'tec_5s' item (RULE-SEPSE-030). Code matches its own docstring.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 269-270 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-030`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Test test_trilha_sepse.py:115-122.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
