# RULE-SEPSE-026 — SEPSE v3 criterio_20 - recent abdominal surgery (minor)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
No noradrenaline (6h) AND recent surgery flag present in latest evolution.

## Inputs

- evolucao.enf_cirurgia_recente (float)
- balanco.qt_vol_nora (float, ml/h)

## Outputs

- criterio_20 (boolean)

## Logic

```text
return all([
  not balanco_6h.filter(qt_vol_nora__gt=0).exists(),
  get_number(ultima_evolucao.enf_cirurgia_recente),
]) if ultima_evolucao and balanco_6h else False
```

## Edge cases (as implemented)

Uses generic enf_cirurgia_recente flag (not abdominal-specific despite docstring).

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published scale assigns a discrete sepsis-screening weight to a generic 'recent surgery' flag; recent/major surgery is a recognized sepsis RISK FACTOR / source (Surviving Sepsis Campaign 2021, Evans L et al., Crit Care Med 2021;49(11):e1063-e1143; CDC Adult Sepsis Event) but not a scored SIRS/qSOFA/Sepsis-3 criterion. The noradrenaline-absence gate is an institutional construct. ([source](https://journals.lww.com/ccmjournal/fulltext/2021/11000/surviving_sepsis_campaign__international.21.aspx))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| enf_cirurgia_recente=1; balanco_6h_nora=0 | no published truth value (risk factor, not scored criterion) | True (get_number(1) truthy AND no nora) | n/a |
| enf_cirurgia_recente=0; balanco_6h_nora=0 | n/a | False (flag falsy) | n/a |
| enf_cirurgia_recente=1; balanco_6h_nora=5 | n/a | False (nora present gates it out) | n/a |

**Verifier notes**

Institutional business rule (minor criterion in v3 automatic pathway). Flag for internal review: docstring says 'recent ABDOMINAL surgery' but code uses the generic enf_cirurgia_recente flag (surgical site not restricted) - internal doc/code mismatch, not a reference discrepancy. No authoritative source to grade against.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 1030-1051 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-120`

**Related rules:**

- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-058](RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
