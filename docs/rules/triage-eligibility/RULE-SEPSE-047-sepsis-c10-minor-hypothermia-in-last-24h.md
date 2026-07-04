# RULE-SEPSE-047 — Sepsis C10 (minor) - hypothermia in last 24h

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
Minor criterion - most-recent 24h temperature < 36 C.

## Inputs

- temp_24hrs (float, Celsius)

## Outputs

- criterio_10 (bool)

## Logic

```text
temp_24hrs = filter(pk__in lookback, criado_em>now-24h).values_list('temperatura').first()
(temp_24hrs < 36) if temp_24hrs else False
```

## Edge cases (as implemented)

Value pulled from lookback chain, not current record. Test prior temp=36->False, 35->True.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** ACCP/SCCM Consensus Conference (Bone RC et al.), Chest 1992;101:1644-1655. SIRS temperature criterion: < 36 C or > 38 C. ([source](https://pubmed.ncbi.nlm.nih.gov/1303622/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | hypothermia threshold 36 C matches SIRS |
| units | Celsius correct |
| ranges | plausible |
| rounding | n/a |
| cutoffs | strict < 36 matches SIRS lower bound |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| temp_24hrs=36 | false | false | yes |
| temp_24hrs=35 | true | true | yes |
| temp_24hrs=36.5 | false | false | yes |
| temp_24hrs= | false | false | yes |

**Verifier notes**

Minor (SIRS) criterion; captures the hypothermia arm of the SIRS temperature criterion (fever arm >38 handled by the separate major criterio_1). Value pulled from 24h lookback chain, not the current record. Legacy confirmed at trilha_sepse.py:332-341.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 332-341 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-035`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Test test_trilha_sepse.py:175-187.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
