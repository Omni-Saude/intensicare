# RULE-SEPSE-054 — Sepsis C17 (minor) - depressed consciousness in last 12h

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
Minor criterion - most-recent 12h Glasgow <= 13.

## Inputs

- glasgow (int)

## Outputs

- criterio_17 (bool)

## Logic

```text
glasgow = filter(lookback, criado_em>now-12h).order_by('-criado_em').values_list('glasgow').first()
(glasgow <= 13) if glasgow else False
```

## Edge cases (as implemented)

Inclusive <=13. 12h window (not 24h). glasgow falsy -> False. Test glasgow=14->False.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Singer M et al. Sepsis-3 (JAMA 2016;315:801) qSOFA - altered mentation = any GCS <15; Vincent JL et al. SOFA (Intensive Care Med 1996;22:707) neurological subscore = 1 point at GCS 13-14 (i.e. any GCS <15 is abnormal). ([source](https://www.mdcalc.com/calc/2654/qsofa-quick-sofa-score-sepsis))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | diff - legacy uses GCS<=13; qSOFA/SOFA use GCS<15 (i.e. <=14) |
| units | GCS points - correct |
| ranges | 12h lookback window (vs 24h for the lab minors) |
| rounding | n/a (inclusive <=) |
| cutoffs | diff - legacy threshold GCS<=13 is one point stricter than the reference altered-mentation threshold (GCS<15); legacy misses GCS=14 |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| glasgow=15 | not altered (GCS not <15) -> False | 15<=13 -> False | yes |
| glasgow=14 | altered mentation (GCS<15) -> POSITIVE (qSOFA/SOFA) | 14<=13 -> False | no |
| glasgow=13 | altered -> True | 13<=13 -> True | yes |
| glasgow=10 | altered -> True | True | yes |

**Verifier notes**

Exact difference: legacy fires only at GCS<=13, whereas both qSOFA (Sepsis-3) and the SOFA neuro subscore treat any GCS<15 (i.e. GCS 14) as abnormal altered mentation. Legacy therefore misses an isolated GCS of 14 (mild confusion). Clinical impact low: this is one MINOR criterion in a multi-criteria two-axis screen, GCS 14 represents only mild depression, and other majors/minors can still trigger the alert; but it is a genuine one-point-stricter cutoff vs the authoritative reference. The active criterio_17 is Glasgow-based (an older leukocyte-based version is commented out, lines 427-456); 12h window; glasgow 0/None -> False. Test test_trilha_sepse.py:261-272.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 458-468 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-042`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

There is an earlier commented-out leukocyte-based criterio_17 (lines 427-456); the active one is Glasgow-based. Test test_trilha_sepse.py:261-272.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
