# RULE-SEPSE-011 — SEPSE v3 criterio_5 - hypotension without vasopressor

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
No noradrenaline (12h) AND (PAS<90 OR PAD<60 OR PAM<65) in last 6h.

## Inputs

- balanco.pas, balanco.pad, balanco.pam, balanco.qt_vol_nora (float, mmHg / ml/h)

## Outputs

- criterio_5 (boolean)

## Logic

```text
return all([
  not balanco_12h.filter(qt_vol_nora__gt=0).exists(),
  balanco_6h.filter(Q(pas__lt=90) | Q(pad__lt=60) | Q(pam__lt=65)).exists(),
]) if balanco_6h and balanco_12h else False
```

## Edge cases (as implemented)

DB-level filter; NULL BP values are excluded by the < comparison (not coerced to 0 here).

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Singer M et al. The Third International Consensus Definitions for Sepsis and Septic Shock (Sepsis-3). JAMA 2016;315(8):801-810 (septic shock: vasopressor to maintain MAP >=65 mmHg); Surviving Sepsis Campaign 2021 (MAP >=65 mmHg resuscitation target); ACCP/SCCM sepsis-induced hypotension SBP <90 mmHg. ([source](https://jamanetwork.com/journals/jama/fullarticle/2492881))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | PAS<90 / PAD<60 / PAM<65 thresholds vs standard sepsis hypotension anchors |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| qt_vol_nora_12h=0; pam_6h=64 | MAP 64 < 65 mmHg, no vasopressor -> untreated hypotension -> positive | not(nora exists)=True; Q(pam<65) matches 64 -> True; all=True | yes |
| qt_vol_nora_12h=0; pas=90; pad=60; pam=65 | all at/above thresholds (strict <) -> no hypotension -> negative | pas<90 F, pad<60 F, pam<65 F -> exists()=False -> all=False | yes |
| qt_vol_nora_12h=5; pam_6h=50 | MAP 50 but already on noradrenaline -> untreated-hypotension criterion N/A -> negative | not(nora exists)=False -> all=False | yes |

**Verifier notes**

BP cutoffs match standard sepsis hypotension definitions (MAP<65 Sepsis-3/SSC target; SBP<90 severe-sepsis hypotension; DBP<60 diastolic hypotension). NULL BP correctly excluded by strict-less comparison. Catalog reconciliation (lines 1960-1961) flags a UI-label mismatch ('PAS<90 ou PAM<60' omits PAD, shows MAP<60) vs code (PAS<90 OR PAD<60 OR PAM<65) - a documentation/label discrepancy only; code thresholds are the clinically correct ones. Docstring mislabels PAD as 'PAS (PAD)' but filters the pad column correctly.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 479-502 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-105`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

Docstring mislabels PAD as "Pressao arterial sistolica (PAD)"; code correctly filters pad.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
