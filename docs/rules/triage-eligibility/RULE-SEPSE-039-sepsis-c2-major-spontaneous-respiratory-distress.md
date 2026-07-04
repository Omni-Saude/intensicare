# RULE-SEPSE-039 — Sepsis C2 (major) - spontaneous respiratory distress

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
Major criterion - (FR>20 OR SatO2<96) AND no mechanical ventilation.

## Inputs

- fr (int, ipm, 0-50)
- sato2 (int, percent)
- ventilacao_mecanica_exists (bool)

## Outputs

- criterio_2 (bool)

## Logic

```text
all([
  any([ (fr>20) if fr else False, (sato2<96) if sato2 else False ]),
  not verificar_objeto_existe(dp,'ventilacao_mecanica')])
```

## Edge cases (as implemented)

fr/sato2 falsy -> that disjunct False. Presence of VM forces False. Test fr=22->True; add VM->False.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** SIRS/sepsis general variables (1992 ACCP/SCCM Consensus; retained in 2001 SCCM/ESICM/ACCP/ATS/SIS conference, Levy et al. Crit Care Med 2003;31:1250-1256): tachypnea = respiratory rate > 20 breaths/min. SpO2 < 96% is an institutional oxygenation screen; exclusion of mechanically-ventilated patients is institutional (spontaneous respiratory distress). ([source](https://pubmed.ncbi.nlm.nih.gov/12682500/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | FR>20 matches SIRS tachypnea threshold (>20 ipm). SatO2<96 is institutional, no single canonical source. |
| units | fr in ipm (breaths/min) matches; sato2 in percent |
| ranges | fr 0-50, falsy fr/sato2 -> that disjunct False |
| rounding | none |
| cutoffs | FR>20 (strict) matches SIRS; SatO2<96 (strict); ANDed with NOT on mechanical ventilation |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| fr=22; sato2=98; vm=false | tachypnea (>20) present, not ventilated -> positive | any([True, False]) and not False -> True | yes |
| fr=22; sato2=98; vm=true | ventilated -> spontaneous-distress criterion excluded | any([True,...]) and not True -> False | yes |
| fr=18; sato2=94; vm=false | RR not tachypneic but SpO2<96 -> positive by oxygenation limb | any([False, True]) and not False -> True | yes |
| fr=20; sato2=96; vm=false | boundary: RR not >20, SpO2 not <96 -> negative | any([False, False]) -> False | yes |

**Verifier notes**

The verifiable core (tachypnea FR>20) matches the SIRS/2001 sepsis tachypnea threshold exactly. SatO2<96% and the mechanical-ventilation exclusion are institutional additions consistent with a spontaneous-respiratory-distress screen; no unit/coefficient mismatch found.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 232-249 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-027`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)

## Notes

Test test_trilha_sepse.py:73-88.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
