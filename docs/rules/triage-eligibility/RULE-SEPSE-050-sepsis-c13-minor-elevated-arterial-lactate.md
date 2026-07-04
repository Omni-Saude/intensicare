# RULE-SEPSE-050 — Sepsis C13 (minor) - elevated arterial lactate

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
Minor criterion - arterial lactate >= 2.5 mmol/L.

## Inputs

- lactato_arterial (float, mmol/L, 0-20)

## Outputs

- criterio_13 (bool)

## Logic

```text
bool((lactato_arterial >= 2.5) if lactato_arterial else False)
```

## Edge cases (as implemented)

Inclusive >=2.5. lactato 0 -> False. Test 2.4->False, 2.5->True.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Surviving Sepsis Campaign 2021 (Evans L et al., Crit Care Med 2021;49:e1063-e1143) and severe-sepsis definitions: serum lactate > 2 mmol/L marks tissue hypoperfusion/organ dysfunction; > 4 mmol/L = high risk. ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486643/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | diff - legacy uses lactate >= 2.5 mmol/L; SSC uses > 2 mmol/L |
| units | mmol/L correct (NOT mg/dL) - unit is right, only the numeric cutoff differs |
| ranges | 0-20 mmol/L plausible |
| rounding | n/a |
| cutoffs | diff - inclusive >= 2.5 vs SSC strict > 2 |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| lactato_arterial=2.5 | true | true | yes |
| lactato_arterial=2.4 | true | false | no |
| lactato_arterial=2.0 | false | false | yes |
| lactato_arterial=0 | false | false | yes |

**Verifier notes**

Threshold discrepancy: legacy fires at lactate >= 2.5 mmol/L vs the Surviving Sepsis Campaign hyperlactatemia threshold of > 2 mmol/L, so lactate 2.0-2.49 mmol/L is missed on this minor criterion (reduced sensitivity). Units are correctly mmol/L (the mmol/L-vs-mg/dL trap this audit targets is NOT present here). 2.5 mmol/L sits near some labs' upper limit of normal, so may be an institutional choice; documented as difference, not corrected. Legacy confirmed at trilha_sepse.py:385-390.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 385-390 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-038`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Test test_trilha_sepse.py:219-224.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
