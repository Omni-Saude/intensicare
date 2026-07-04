# RULE-SEPSE-045 — Sepsis C8 (major) - Glasgow drop or delirium

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Major criterion - Glasgow decreased by >= 2 points vs the most-recent 24h value OR delirium present.

## Inputs

- glasgow (current) (int)
- glasgow_em_24 (prior 24h) (int)
- delirium (bool)

## Outputs

- criterio_8 (bool)

## Logic

```text
glasgow_em_24 = filter(pk__in lookback, criado_em>now-24h).order_by('-criado_em').values_list('glasgow').first()
any([
  (glasgow - glasgow_em_24 <= -2) if (glasgow_em_24 and glasgow) else False,
  delirium if delirium else False])
```

## Edge cases (as implemented)

Needs both current and prior glasgow truthy. Drop of exactly 2 (delta -2) triggers. Test current=3 prior=5 -> -2 -> True; prior=4 -> -1 -> False.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Sepsis-3 organ-dysfunction framework (Singer M et al, JAMA 2016): acute alteration in mental status is a recognized sepsis organ-dysfunction sign; SOFA CNS is GCS-based and qSOFA scores altered mentation (GCS < 15). Delirium (CAM-ICU) is the standard construct for sepsis-associated acute encephalopathy; an acute drop in GCS reflects new neurologic dysfunction. ([source](https://jamanetwork.com/journals/jama/fullarticle/2492881))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| glasgow=3; glasgow_em_24=5; delirium=false | acute GCS drop of 2 -> True | true | yes |
| glasgow=4; glasgow_em_24=5; delirium=false | drop of 1 (< 2) -> False | false | yes |
| glasgow=5; glasgow_em_24=3; delirium=false | GCS improved (+2), no acute decline -> False | false | yes |
| glasgow=15; glasgow_em_24=15; delirium=true | delirium present -> True | true | yes |

**Verifier notes**

Logic direction is CORRECT: (glasgow - glasgow_em_24 <= -2), lines 316-318, fires only on a DECREASE of >=2 points, matching the intended acute neurologic deterioration - notably the OPPOSITE of the sign-inverted v3 bug in RULE-SEPSE-016 (which computed last-minus-penultimate >= 2, detecting an INCREASE). Third test vector confirms an improving GCS does not fire. The delirium OR-branch aligns with CAM-ICU / sepsis-associated encephalopathy. The exact ">=2 point drop" cutoff is an institutional choice with no single contradicting published number and is clinically consistent with the Sepsis-3 organ-dysfunction framework; all checked dimensions match.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 305-323 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-033`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Test test_trilha_sepse.py:153-166.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
