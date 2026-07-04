# RULE-SEPSE-009 — SEPSE v3 criterio_3 - respiratory failure prescription

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Intended absence of noradrenaline (12h) AND prescription of invasive vent or intubation (24h).

## Inputs

- balanco.qt_vol_nora (float, ml/h)
- cpoe.vent_mecanica_invasiva, cpoe.intubacao_orotraqueal (float)

## Outputs

- criterio_3 (boolean)

## Logic

```text
return all([
  balanco_12h.filter(qt_vol_nora__gt=0).exists(),      # PRESENCE (docstring says absence)
  cpoe_24h.filter(Q(vent_mecanica_invasiva__gt=0) | Q(intubacao_orotraqueal__gt=0)).exists(),
]) if cpoe_24h and balanco_12h else False
```

## Edge cases (as implemented)

Guarded False if windows empty.

## Divergence

DISCREPANCY - missing negation on noradrenaline vs docstring.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** Respiratory organ dysfunction proxy (prescription of invasive mechanical ventilation / intubation) as sepsis-associated acute organ dysfunction (Sepsis-3, Singer et al. JAMA 2016; SOFA respiratory component). Institutional 'sem vasopressor' gating per intent of detecting de-novo dysfunction. ([source](https://pubmed.ncbi.nlm.nih.gov/26903336/))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | n/a |
| units | n/a |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| vent_or_intubation_prescribed_24h=true; noradrenaline_12h=absent | Respiratory failure requiring intubation + not on pressor -> SHOULD fire (docstring intent 'absence of noradrenaline') | all([nora present=FALSE, vent/intub prescribed=TRUE]) = FALSE | no |
| vent_or_intubation_prescribed_24h=true; noradrenaline_12h=running | Already on vasopressor -> should NOT fire per intent | all([nora present=TRUE, prescribed=TRUE]) = TRUE (inverted) | no |
| vent_or_intubation_prescribed_24h=false; noradrenaline_12h=absent | No respiratory-support prescription -> should not fire | all([nora present=FALSE, prescribed=FALSE]) = FALSE | yes |

**Verifier notes**

Confirms the extraction DISCREPANCY. The noradrenaline gate is inverted vs the docstring: code uses balanco_12h.filter(qt_vol_nora__gt=0).exists() (PRESENCE) where the intent is ABSENCE. The criterion therefore fires only when the patient IS on noradrenaline and an invasive-vent/intubation order exists, and never fires for the intended not-on-pressor patient with a new respiratory-support order. No published equation exists for this institutional organ-dysfunction proxy (units/coeffs n/a); the difference is purely the inverted vasopressor gate. Moderate impact - as a MAJOR v3 criterion the inversion biases which patients contribute to the alert.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 427-450 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-103`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

DISCREPANCY - missing negation on noradrenaline vs docstring.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
