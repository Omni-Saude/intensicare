# RULE-SEPSE-010 — SEPSE v3 criterio_4 - newly started vasopressor

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
Noradrenaline OR vasopressin started in last 6h AND absent beyond ~24h (26h window).

## Inputs

- balanco.qt_vol_nora, balanco.qt_vol_vaso (float, ml/h)

## Outputs

- criterio_4 (boolean)

## Logic

```text
balanco_6h = balancos(dt >= now-6h); balanco_mais_24h = balancos(dt < now-26h)
return all([
  balanco_6h.filter(Q(qt_vol_nora__gt=0) | Q(qt_vol_vaso__gt=0)).exists(),
  not balanco_mais_24h.filter(Q(qt_vol_nora__gt=0) | Q(qt_vol_vaso__gt=0)).exists(),
]) if balanco_6h and balanco_mais_24h else False
```

## Edge cases (as implemented)

Beyond-24h absence implemented as strictly older than now-26h (2h grace).

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Sepsis-3 septic shock definition (Singer et al., JAMA 2016; Shankar-Hari et al., JAMA 2016): vasopressor requirement to maintain MAP >= 65 mmHg identifies circulatory dysfunction. Detecting NEW vasopressor initiation operationalizes new-onset shock; no published equation governs the temporal-window logic itself. ([source](https://pubmed.ncbi.nlm.nih.gov/26903336/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| noradrenaline_started_2h_ago=true; vasopressor_before_26h=none | New vasopressor start (present now, absent historically) -> fire | all([nora\|vaso present 6h=TRUE, not present >26h=TRUE]) = TRUE | yes |
| noradrenaline_running_3_days=true | Chronic/ongoing vasopressor (not newly started) -> should NOT fire | all([present 6h=TRUE, not present >26h=FALSE (is present old)]) = FALSE | yes |
| vasopressor=none | No vasopressor at all -> should not fire | all([present 6h=FALSE, ...]) = FALSE | yes |
| vasopressin_started_4h_ago=true; none_before_26h=true | Vasopressin (2nd-line pressor) new start also counts -> fire | Q(qt_vol_nora__gt=0)\|Q(qt_vol_vaso__gt=0) present 6h=TRUE, absent >26h=TRUE -> TRUE | yes |

**Verifier notes**

Logic is internally consistent and aligns with the Sepsis-3 concept that vasopressor requirement marks circulatory dysfunction; this criterion operationalizes NEW initiation (noradrenaline OR vasopressin present in last 6h AND absent before the 26h window). No unit, coefficient, or threshold error - qt_vol>0 presence checks are correct, and the 2h grace (now-26h rather than exactly now-24h) is a documented implementation buffer, not a clinical discrepancy. The temporal windowing has no authoritative published equation to contradict; on every reference-checkable dimension it is consistent. VERIFIED.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 452-477 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-104`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
