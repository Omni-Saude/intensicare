# RULE-SEPSE-018 — SEPSE v3 criterio_12 - hypothermia (minor)

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
No noradrenaline (6h) AND temperature < 36C in last 6h.

## Inputs

- balanco.temp, balanco.qt_vol_nora (float, Celsius / ml/h)

## Outputs

- criterio_12 (boolean)

## Logic

```text
return all([
  not balanco_6h.filter(qt_vol_nora__gt=0).exists(),
  balanco_6h.filter(temp__lt=36).exists(),
]) if balanco_6h else False
```

## Edge cases (as implemented)

DB filter temp<36; nulls excluded.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** SIRS temperature criterion (ACCP/SCCM Consensus Conference, Bone RC et al., Chest 1992;101:1644-55; re-affirmed Levy MM et al. 2001 SCCM/ESICM/ACCP/ATS/SIS, Crit Care Med 2003;31:1250-6): body temperature < 36 C (or > 38 C). ([source](https://www.esicm.org/wp-content/uploads/2018/03/file4.pdf))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | ok |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| temp_c=35.5 | fire (<36 C) | fire (temp__lt=36 True) | yes |
| temp_c=36.0 | no-fire (SIRS is strict <36) | no-fire (36 < 36 is False) | yes |
| temp_c=38.5 | no-fire (this hypothermia criterion; fever handled separately) | no-fire | yes |

**Verifier notes**

Hypothermia minor criterion matches the SIRS temperature-low threshold exactly (strict <36 C, Celsius). DB-level filter excludes NULL temps so there is no missing-data false positive (unlike the get_number-based criteria). Fever (>38 C) is a separate criterion. No discrepancy.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 763-781 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-112`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

Minor criterion.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
