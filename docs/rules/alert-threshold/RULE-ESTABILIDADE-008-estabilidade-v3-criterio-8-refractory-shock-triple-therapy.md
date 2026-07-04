# RULE-ESTABILIDADE-008 — Estabilidade v3 criterio_8 - refractory shock triple therapy

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Noradrenaline > 70ml/h AND vasopressin > 5ml/h in last 4h AND absence of adrenaline in last 4h. Defined but UNWIRED.

## Inputs

| name | type | unit |
|---|---|---|
| balanco.qt_vol_nora | float | ml/h |
| balanco.qt_vol_vaso | float | ml/h |
| balanco.qt_vol_adre | float | ml/h |

## Outputs

| name | type |
|---|---|
| criterio_8 | boolean |

## Logic

```text
return all([
  balanco_4h.filter(qt_vol_nora__gt=70, qt_vol_vaso__gt=5).exists(),
  not balanco_4h.filter(qt_vol_adre__gt=0).exists(),
]) if (ultimo_balanco and balanco_4h and ultima_evolucao) else False
```

## Edge cases (as implemented)

nora>70 AND vaso>5 must co-occur in the SAME record (comma = AND). Unwired.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** Surviving Sepsis Campaign 2021 (Evans et al., Crit Care Med 2021): add epinephrine (adrenaline) as a third agent when MAP remains inadequate despite norepinephrine + vasopressin (refractory septic shock). ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486643/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | diff |
| units | diff |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| qt_vol_nora_mlh=75; qt_vol_vaso_mlh=6; qt_vol_adre_mlh=0 | SSC: on NE+vasopressin with inadequate MAP -> add epinephrine (concept OK); facade '>1.5 mcg/kg/min' but 75 ml/h ~1.14 mcg/kg/min @64 mcg/mL,70 kg -> displayed dose NOT met | filter(nora>70, vaso>5) T, not adre>0 T -> True; alert asserts >1.5 mcg/kg/min | no |
| qt_vol_nora_mlh=70; qt_vol_vaso_mlh=6; qt_vol_adre_mlh=0 | no published ml/h anchor exists; 70 ml/h ~1.07 mcg/kg/min still below facade 1.5 either way | nora>70 is strict -> 70 not >70 -> filter empty -> False | no |
| qt_vol_nora_mlh=80; qt_vol_vaso_mlh=6; qt_vol_adre_mlh=2 | patient already on adrenaline -> 'add adrenaline' alert correctly suppressed | not balanco_4h.filter(qt_vol_adre__gt=0).exists() -> False -> criterion False | yes |

**Verifier notes**

Concept matches SSC-2021 escalation ladder (epinephrine as third agent for refractory shock on NE+vasopressin, gated by absence of adrenaline — verified correct in vector 3). DISCREPANCY is the same unit mismatch as RULE-007: predicate uses ml/h (nora>70, vaso>5) while guideline/facade (RULE-016 criterio_8) use mcg/kg/min (>1.5 displayed). Under a plausible dilution >70 ml/h maps to ~1.1 mcg/kg/min, not the 1.5 shown. The nora>70 AND vaso>5 must co-occur in the SAME balance record (Django comma = AND), a reasonable "on both agents" proxy. Moderate impact: displayed dose overstates actual by design and depends on unknown concentration/weight. Predicate is UNWIRED (not in calcular_criterios), so no live alert. ml/h cutoffs are institution-specific/unverifiable.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_estabilidade.py` | 499-521 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-03-068`

**Related rules:**

- [RULE-ESTABILIDADE-016](../drug-dosing/RULE-ESTABILIDADE-016-estabilidade-facade-alert-text-vasopressor-inotrope-escalati.md)

## Notes

Facade criterio_8 = 'Noradrenalina > 1,5mcg/kg/min, associar adrenalina' (dose in mcg/kg/min, code in ml/h) — see divergence on RULE-016.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
