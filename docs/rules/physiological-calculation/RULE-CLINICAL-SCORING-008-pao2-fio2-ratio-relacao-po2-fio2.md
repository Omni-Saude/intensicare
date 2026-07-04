# RULE-CLINICAL-SCORING-008 — PaO2/FiO2 ratio (relacao PO2/FiO2)

| Field | Value |
|---|---|
| Cluster | clinical-scoring |
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | high |

## Rule
Computes the PaO2/FiO2 oxygenation ratio used by SOFA and by sedation/ventilation/sepse pathways; returns boolean False when either input is non-positive (used as a "no data" sentinel).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| po2 | float | mmHg | 0-500 (validator) |
| fio2 | float | percent-or-fraction (ambiguous; see divergence) | 0 or 21-100 (validator) |

## Outputs

| name | type | unit |
|---|---|---|
| relacao | float \| bool(False) | ratio |

## Logic

```text
if po2 > 0 and fio2 > 0:
    return po2 / fio2
return False   # sentinel; note False == 0 in downstream numeric comparisons
```

## Edge cases (as implemented)

Returns False (not 0/None) when po2<=0 or fio2<=0. Downstream comparisons like `0 < ratio < 200` therefore treat missing data as False (excluded). No rounding; no division-by-zero (guarded).

## Divergence

UNIT DISCREPANCY: FiO2Validator restricts fio2 to 0 or 21..100 (a percentage), but every clinical threshold using this ratio (SOFA 400/300/200/100; ventilacao 150/200/250/300) and all tests (fio2=1 -> ratio=po2) treat fio2 as a fraction 0.21..1.0. Tests set attributes directly, bypassing the validator. With percentage FiO2 the ratio is ~100x too small vs standard P/F. Same ratio is also referenced with fio2 as fraction (<0.4) in ventilacao criterio_8, and divided by 100 (percentage assumption) in the FiO2xPEEP table `arredondar`. The codebase is internally inconsistent on FiO2 units.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** high
- **Reference:** PaO2/FiO2 (P/F) oxygenation ratio. Vincent JL, et al. SOFA, Intensive Care Med. 1996 (respiratory component thresholds 400/300/200/100) and Berlin Definition of ARDS (ARDS Definition Task Force, JAMA 2012;307:2526-2533). In every authoritative use PaO2 is in mmHg and FiO2 is a FRACTION (0.21-1.0), so a P/F of 300 corresponds to e.g. PaO2 150 mmHg at FiO2 0.5. ([source](https://www.mdcalc.com/calc/2378/horowitz-index-p-f-ratio))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | n/a |
| units | diff |
| ranges | diff |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| po2=100; fio2=1.0 | 100 | 100.0 | yes |
| po2=100; fio2=50 | 200 | 2.0 | no |
| po2=80; fio2=40 | 200 | 2.0 | no |
| po2=0; fio2=1.0 | no-data/undefined | false | yes |

**Verifier notes**

The equation (PaO2/FiO2) and the non-positive-input guard are correct. The defect is a unit inconsistency, not an arithmetic one: DadosProntuario.FiO2Validator constrains fio2 to 0 or 21..100 (a PERCENTAGE), yet all downstream thresholds (SOFA respiratory 400/300/200/100; ventilacao 150-300; ARDS/Berlin) and every unit test assume FiO2 as a FRACTION 0.21-1.0. If a validator-conformant percentage FiO2 ever reaches this property the ratio is ~100x too small, which would drive the SOFA respiratory subscore to the maximum 4 points and spuriously classify severe ARDS. Tests set attributes directly (fio2=1.0), masking the bug. The codebase is internally inconsistent (same ratio elsewhere assumes fraction <0.4, and a FiO2xPEEP table divides FiO2 by 100). The False sentinel (==0 numerically) is a benign no-data convention. Impact high given the potential for maximal, silent mis-scoring if percentage FiO2 is ever used at runtime.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/dados_prontuario.py` | 181-185 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-pfratio-BE-10-001`

**Related rules:**

- [RULE-CLINICAL-SCORING-002](../clinical-scoring/RULE-CLINICAL-SCORING-002-sofa-respiratory-sub-score-pao2-fio2.md)
- [RULE-CLINICAL-SCORING-011](../clinical-scoring/RULE-CLINICAL-SCORING-011-sofa-attribute-sourcing-from-prontuario-model-save.md)

## Notes

Consumed by SOFA respiratory sub-score (RULE-002) and ventilacao/sedacao/sepse pathways (other clusters).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
