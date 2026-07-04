# RULE-SEPSE-013 — SEPSE v3 criterio_7 - hyperlactatemia without vasopressor

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
No noradrenaline (12h) AND arterial lactate >= 3.

## Inputs

- evolucao.diurna_lactato (float, mmol/L)
- balanco.qt_vol_nora (float, ml/h)

## Outputs

- criterio_7 (boolean)

## Logic

```text
return all([
  not balanco_12h.filter(qt_vol_nora__gt=0).exists(),
  get_number(ultima_evolucao.diurna_lactato) >= 3,
]) if balanco_12h and ultima_evolucao else False
```

## Edge cases (as implemented)

get_number(null)->0, so lactate>=3 fails safely on missing values.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Surviving Sepsis Campaign 2021 (Evans L et al., Crit Care Med 2021;49:e1063) - elevated lactate >2 mmol/L marks tissue hypoperfusion; Sepsis-3 septic shock uses lactate >2 mmol/L; SSC database analysis: 'elevated' cutoffs 1.6-2.5 mmol/L, >4 mmol/L strongly mortality-associated. ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486643/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | legacy threshold lactate >=3 mmol/L |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| qt_vol_nora_12h=0; diurna_lactato=3.0 | lactate 3.0 > 2 -> elevated -> positive | not(nora)=True; get_number(3.0)>=3 True; all=True | yes |
| qt_vol_nora_12h=0; diurna_lactato=2.5 | lactate 2.5 > 2 mmol/L -> elevated per SSC/Sepsis-3 -> should flag | 2.5 >= 3 -> False -> all=False (NOT flagged) | no |
| qt_vol_nora_12h=0; diurna_lactato= | no lactate value -> no criterion | get_number(null)=0; 0>=3 False -> all=False | yes |

**Verifier notes**

Legacy uses lactate >=3 mmol/L; SSC 2021 / Sepsis-3 treat >2 mmol/L as the elevated/tissue-hypoperfusion anchor (severe >4). The >=3 cutoff is stricter than any guideline 'elevated' threshold, so lactate 2-3 mmol/L is missed by this single criterion (reduced sensitivity). Impact low: 2-3 mmol/L is prognostically weaker than >4 and such patients are usually captured by other organ-dysfunction criteria; units correct and fails safe on missing data. Flag as possibly-intentional protocol choice for internal review.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 528-548 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-107`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
