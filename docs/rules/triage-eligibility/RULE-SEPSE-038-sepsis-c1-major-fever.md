# RULE-SEPSE-038 — Sepsis C1 (major) - fever

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
Major sepsis criterion - temperature > 38.3 C.

## Inputs

- temperatura (float, Celsius, 0 or 20-43)

## Outputs

- criterio_1 (bool)

## Logic

```text
(temperatura > 38.3) if temperatura else False
```

## Edge cases (as implemented)

temperatura 0/None -> False. Strict >38.3. Test 37->False, 38.5->True.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Levy MM, Fink MP, Marshall JC, et al. 2001 SCCM/ESICM/ACCP/ATS/SIS International Sepsis Definitions Conference. Crit Care Med 2003;31(4):1250-1256 (also Intensive Care Med 2003). Diagnostic criteria for sepsis, general variables: Fever = core temperature > 38.3 C. ([source](https://pubmed.ncbi.nlm.nih.gov/12682500/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | 38.3 threshold matches 2001 definitions fever cutoff exactly |
| units | Celsius, matches reference (core temperature in C) |
| ranges | temperatura 0 or 20-43 C; 0/None treated as missing -> False |
| rounding | none; strict > comparison |
| cutoffs | strict > 38.3 matches reference (>38.3 C) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| temperatura=37.0 | not fever (<=38.3) -> criterion negative | 37.0 > 38.3 -> False | yes |
| temperatura=38.3 | boundary: reference fever is strictly >38.3, so 38.3 is negative | 38.3 > 38.3 -> False | yes |
| temperatura=38.5 | fever (>38.3) -> positive | 38.5 > 38.3 -> True | yes |
| temperatura=0 | missing/invalid -> not scored | falsy 0 -> False | yes |

**Verifier notes**

Matches 2001 sepsis definitions fever threshold on cutoff, direction, and units. Scope note (not a discrepancy): legacy scores only the fever limb; the reference also lists hypothermia (<36 C) as a general variable, but that is handled by separate criteria outside this rule.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 225-230 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-026`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Test test_trilha_sepse.py:66-71.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
