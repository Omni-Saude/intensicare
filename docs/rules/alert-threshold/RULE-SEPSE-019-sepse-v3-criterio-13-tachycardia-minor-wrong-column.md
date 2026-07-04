# RULE-SEPSE-019 — SEPSE v3 criterio_13 - tachycardia (minor, wrong column)

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
Intended - no noradrenaline (6h) AND heart rate > 100 bpm in last 6h.

## Inputs

- balanco.fr (used), balanco.fc (intended) (float, ipm / bpm)
- balanco.qt_vol_nora (float, ml/h)

## Outputs

- criterio_13 (boolean)

## Logic

```text
return all([
  not balanco_6h.filter(qt_vol_nora__gt=0).exists(),
  balanco_6h.filter(fr__gt=100).exists(),     # fr = respiratory rate; docstring wants FC (heart rate)
]) if balanco_6h else False
```

## Edge cases (as implemented)

Filters fr>100 (respiratory rate), physiologically almost never true.

## Divergence

DISCREPANCY - filters fr (frequencia respiratoria) instead of fc (frequencia cardiaca) despite docstring "Frequencia cardiaca > 100 bpm".

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** SIRS heart-rate criterion (ACCP/SCCM 1992, Bone RC et al., Chest 1992;101:1644-55): heart rate > 90/min. Docstring intends the common tachycardia threshold HR > 100 bpm. ([source](https://www.esicm.org/wp-content/uploads/2018/03/file4.pdf))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | n/a |
| units | diff |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| fc_bpm=120; fr_ipm=18 | fire (tachycardia HR>90/>100) | no-fire (fr=18 > 100 is False; heart rate never inspected) | no |
| fc_bpm=150; fr_ipm=30 | fire | no-fire (fr=30 > 100 is False) -- RR>100 is physiologically impossible | no |
| fc_bpm=80; fr_ipm=22 | no-fire (HR normal) | no-fire (fr=22 > 100 False) -- correct outcome only by coincidence | yes |

**Verifier notes**

Extraction-flagged DISCREPANCY confirmed. Code filters balanco.fr (frequencia respiratoria / respiratory rate) > 100 instead of balanco.fc (frequencia cardiaca / heart rate). Because a respiratory rate above 100/min essentially never occurs, criterio_13 is effectively a dead criterion that is always False - tachycardia, a cardinal early sepsis sign, never contributes to the minor count. It is one of ~9 minor criteria so overall screening degradation is partial (hence moderate, not high). Separately, even the intended threshold (>100) is stricter than the SIRS reference (>90 bpm).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 783-801 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-113`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

DISCREPANCY - filters fr (frequencia respiratoria) instead of fc (frequencia cardiaca) despite docstring "Frequencia cardiaca > 100 bpm".

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
