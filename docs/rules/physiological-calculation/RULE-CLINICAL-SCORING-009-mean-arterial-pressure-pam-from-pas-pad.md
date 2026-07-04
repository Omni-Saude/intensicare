# RULE-CLINICAL-SCORING-009 — Mean arterial pressure (PAM) from PAS/PAD

| Field | Value |
|---|---|
| Cluster | clinical-scoring |
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Derives mean arterial pressure from systolic (PAS) and diastolic (PAD) pressures; used inside SOFA cardiovascular scoring.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| pad | float | mmHg | 0-150 |
| pas | float | mmHg | 0 or 50-250 |

## Outputs

| name | type | unit |
|---|---|---|
| pam | float | mmHg |

## Logic

```text
pam = ((2 * pad) + pas) / 3   if (pad and pas) else 0
```

## Edge cases (as implemented)

If either pad or pas is falsy (0/None) pam=0. Standard MAP formula. No rounding.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Standard estimated mean arterial pressure: MAP = (SBP + 2*DBP)/3, weighting diastole 2:1 because diastole occupies ~2/3 of the cardiac cycle. StatPearls, Physiology, Mean Arterial Pressure; MDCalc MAP calculator. ([source](https://www.mdcalc.com/calc/74/mean-arterial-pressure-map))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | ok |
| units | ok |
| ranges | n/a |
| rounding | ok |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| pas=120; pad=80 | 93.33 | 93.33 | yes |
| pas=100; pad=60 | 73.33 | 73.33 | yes |
| pas=90; pad=50 | 63.33 | 63.33 | yes |
| pas=0; pad=80 | undefined/no-data | 0 | yes |

**Verifier notes**

`((2*pad)+pas)/3` is exactly the standard estimated MAP formula with correct 2:1 diastolic weighting. No rounding is applied (full float), matching the reference calculator. When either PAS or PAD is falsy (0/None) the result is 0, a reasonable no-data sentinel that never produces a spurious mid-range MAP. Feeds SOFA cardiovascular scoring (RULE-005) where MAP<70 -> 1 point.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/sofa.py` | 57-61 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-pam-BE-10-002`

**Related rules:**

- [RULE-CLINICAL-SCORING-005](../clinical-scoring/RULE-CLINICAL-SCORING-005-sofa-cardiovascular-sub-score-vasopressors-map.md)
- [RULE-CLINICAL-SCORING-011](../clinical-scoring/RULE-CLINICAL-SCORING-011-sofa-attribute-sourcing-from-prontuario-model-save.md)

## Notes

Standard MAP = (2*DBP + SBP)/3. Computed inside SOFA.atualizar_atributos_sofa (the same expression is captured within the SOFA attribute-sourcing workflow RULE-011, sofa.py:40-67); the DadosProntuario.pam field itself is commented out.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
