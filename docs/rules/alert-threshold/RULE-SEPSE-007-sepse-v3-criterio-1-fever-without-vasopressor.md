# RULE-SEPSE-007 — SEPSE v3 criterio_1 - fever without vasopressor

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
Intended - absence of noradrenaline (6h) AND temperature > 38.2C in last 24h.

## Inputs

- balanco.qt_vol_nora (float, ml/h)
- balanco.temp (float, Celsius)

## Outputs

- criterio_1 (boolean)

## Logic

```text
balanco_6h  = balancos(dt >= now-6h); balanco_24h = balancos(dt >= now-24h)
return all([
  balanco_6h.filter(qt_vol_nora__gt=0).exists(),     # PRESENCE (docstring says absence)
  balanco_24h.filter(temp__gt=38.2).exists(),
]) if balanco_6h and balanco_24h else False
```

## Edge cases (as implemented)

Guarded False if either window empty.

## Divergence

DISCREPANCY - docstring specifies "ausencia de noradrenalina" but code omits the negation (uses qt_vol_nora__gt=0 presence). Temperature threshold 38.2C strict >.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** SIRS temperature criterion (Bone RC et al., ACCP/SCCM Consensus 1992; carried into Sepsis-2): fever = temperature > 38.3 C. Institutional 'sem vasopressor' gating maps to the intent of detecting de-novo organ dysfunction not attributable to established shock (Sepsis-3, Singer et al. JAMA 2016). ([source](https://pubmed.ncbi.nlm.nih.gov/26903336/))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| temp_24h=38.5; noradrenaline_6h=absent | Fever present + not on vasopressor -> criterion SHOULD fire (docstring intent 'ausencia de noradrenalina') | all([nora present=FALSE, temp>38.2=TRUE]) = FALSE | no |
| temp_24h=38.5; noradrenaline_6h=running | Patient already on vasopressor -> criterion should NOT fire per intent | all([nora present=TRUE, temp>38.2=TRUE]) = TRUE (inverted) | no |
| temp_24h=38.25; noradrenaline_6h=running | SIRS fever requires >38.3 -> 38.25 is NOT fever on temperature | temp>38.2 = TRUE at 38.25 (fires on temperature) | no |
| temp_24h=38.2; noradrenaline_6h=running | Boundary: 38.2 is not fever by either 38.2 or 38.3 rule | temp>38.2 = FALSE (strict >) -> criterion FALSE | yes |

**Verifier notes**

Two documented differences. (1) Noradrenaline gate inverted: docstring specifies ABSENCE of noradrenaline but code uses qt_vol_nora__gt=0 PRESENCE, so the criterion only fires for patients already on a vasopressor and never for the intended febrile-not-yet-on-pressor patient - a logic inversion that alters which patients this MAJOR v3 criterion flags (moderate: biases the alert toward already-shocked patients and misses de-novo fever). (2) Temperature cutoff >38.2 C vs the SIRS reference >38.3 C - 0.1 C more sensitive, low impact on its own. Characterizes and confirms the extraction-stage DISCREPANCY.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 362-382 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-101`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

DISCREPANCY - docstring specifies "ausencia de noradrenalina" but code omits the negation (uses qt_vol_nora__gt=0 presence). Temperature threshold 38.2C strict >.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
