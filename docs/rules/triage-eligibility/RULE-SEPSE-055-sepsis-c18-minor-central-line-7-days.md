# RULE-SEPSE-055 — Sepsis C18 (minor) - central line > 7 days

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Minor criterion - presence of CVC/CDL for more than 7 days (boolean flag).

## Inputs

- presenca_cvc_cdl_7_dias (bool)

## Outputs

- criterio_18 (bool)

## Logic

```text
return dp.presenca_cvc_cdl_7_dias
```

## Edge cases (as implemented)

Direct boolean passthrough (may return None if field null). Test False->False, True->True.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published scoring reference. Central venous catheter dwell time >7 days is a CLABSI infection-source RISK FACTOR (CDC/HICPAC Guidelines for the Prevention of Intravascular Catheter-Related Infections, O'Grady NP et al. 2011), not a physiological sepsis-score criterion. The >7-day duration is judged by the clinician at data entry and passed as a boolean. ([source](https://www.cdc.gov/infection-control/hcp/intravascular-catheter-related-infection/index.html))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a - boolean passthrough, no computed threshold |
| units | days (7) captured by human, not computed |
| ranges | n/a |
| rounding | n/a |
| cutoffs | 7-day threshold is an institutional risk-factor convention; no scored-criterion reference to verify against |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| presenca_cvc_cdl_7_dias=false | n/a | returns False | yes |
| presenca_cvc_cdl_7_dias=true | n/a | returns True | yes |
| presenca_cvc_cdl_7_dias= | n/a | returns None (else-False guard commented out; None is falsy downstream) | yes |

**Verifier notes**

Infection-source risk-factor business rule, not a published/computed sepsis scale - flagged for internal review, NOT treated as wrong. Duration (>7d) is captured by the human at data entry rather than computed, so there is no equation/unit/rounding to audit. Implementation note (not a reference discrepancy): direct passthrough of presenca_cvc_cdl_7_dias with the else-False guard commented out, so a NULL field returns None rather than False; harmless because None is falsy where the criterion is counted. Test test_trilha_sepse.py:274-277.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 470-475 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-043`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Duration threshold (7 days) is captured by the human at data entry, not computed. Test test_trilha_sepse.py:274-277.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
