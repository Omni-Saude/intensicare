# RULE-SEPSE-012 — SEPSE v3 criterio_6 - thrombocytopenia without vasopressor

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
No noradrenaline (6h) AND platelets < 100000 in last 24h.

## Inputs

- evolucao.diurna_plaquetas (int (via DB filter), /mm3)
- balanco.qt_vol_nora (float, ml/h)

## Outputs

- criterio_6 (boolean)

## Logic

```text
return all([
  not balanco_6h.filter(qt_vol_nora__gt=0).exists(),
  evolucao_24h.filter(diurna_plaquetas__lt=100000).exists(),
]) if balanco_6h and evolucao_24h else False
```

## Edge cases (as implemented)

diurna_plaquetas is a CharField; DB __lt compares as text/number depending on backend - potential lexical comparison risk.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Vincent JL et al. The SOFA (Sepsis-related Organ Failure Assessment) score. Intensive Care Med 1996;22:707-710 - coagulation subscore: platelets <100 x10^3/uL = 2 points. Sepsis-3 (Singer 2016) uses SOFA increase >=2. ([source](https://link.springer.com/article/10.1007/BF01709751))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | platelet threshold 100000/mm3 vs SOFA 2-point boundary (<100 x10^3/uL) |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| qt_vol_nora_6h=0; diurna_plaquetas=99000 | 99k < 100k -> SOFA coag >=2 organ dysfunction -> positive | not(nora)=True; filter(plaquetas__lt=100000) matches -> True; all=True | yes |
| qt_vol_nora_6h=0; diurna_plaquetas=100000 | exactly 100k -> SOFA 1 point (not <100) -> negative | 100000 not < 100000 -> exists()=False -> all=False | yes |
| qt_vol_nora_6h=3; diurna_plaquetas=50000 | thrombocytopenia but on vasopressor -> untreated criterion N/A -> negative | not(nora exists)=False -> all=False | yes |

**Verifier notes**

Numeric threshold 100000/mm3 matches SOFA coagulation 2-point cutoff. IMPLEMENTATION RISK (not a reference discrepancy): diurna_plaquetas is a CharField; Django __lt on a text column can do lexical rather than numeric comparison on some backends (e.g. '99000' > '100000' lexically because '9'>'1'), which could invert the test. Backend-dependent bug flagged for internal review; the clinical cutoff itself is correct.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 504-526 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-106`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
