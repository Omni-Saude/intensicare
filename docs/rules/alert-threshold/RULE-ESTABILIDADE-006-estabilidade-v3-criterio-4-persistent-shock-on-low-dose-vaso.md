# RULE-ESTABILIDADE-006 — Estabilidade v3 criterio_4 - persistent shock on low-dose vasopressor

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Respiratory rate > 20 AND noradrenaline > 10ml/h in last 4h AND (lactate > 2 OR TEC > 3) AND spontaneous / room-air ventilation. Defined but UNWIRED.

## Inputs

| name | type | unit |
|---|---|---|
| balanco.fr | float | ipm |
| balanco.qt_vol_nora | float | ml/h |
| evolucao.diurna_lactato | float | mmol/L |
| evolucao.tempo_enchimento_capilar | float | s |
| evolucao.diurna_ventilacao | string |  |

## Outputs

| name | type |
|---|---|
| criterio_4 | boolean |

## Logic

```text
return all([
  balanco_4h.filter(fr__gt=20).exists(),
  balanco_4h.filter(qt_vol_nora__gt=10).exists(),
  any([ get_number(diurna_lactato) > 2, get_number(tempo_enchimento_capilar) > 3 ]),
  evolucao.diurna_ventilacao.strip().lower() in [*get_ventilacao("ar_ambiente"), *get_ventilacao("ventilacao_espontanea")],
]) if (ultimo_balanco and balanco_4h and ultima_evolucao) else False
```

## Edge cases (as implemented)

FR strict >20, nora strict >10, lactate strict >2, TEC strict >3. Unwired.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Sepsis-3 (Singer et al., JAMA 2016 — septic shock: vasopressor + serum lactate >2 mmol/L); ANDROMEDA-SHOCK (Hernandez et al., JAMA 2019 — abnormal capillary refill time >3 s); SIRS respiratory criterion RR >20/min (qSOFA uses RR >=22). ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC4968574/ , https://pmc.ncbi.nlm.nih.gov/articles/PMC6439620/))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok |
| coefficients | ok |
| units | n/a |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| FR=22; qt_vol_nora_mlh=15; diurna_lactato=2.5; TEC_s=2; diurna_ventilacao=ar ambiente | septic-shock hypoperfusion (lactate>2) in spontaneous ventilation -> FLAG | fr>20 T, nora>10 T, any(2.5>2 T) T, vent in room-air/spontaneous T -> True | yes |
| FR=25; qt_vol_nora_mlh=12; diurna_lactato=2.0; TEC_s=3; diurna_ventilacao=ar ambiente | lactate 2.0 is NOT >2 (Sepsis-3 strict) and CRT 3.0 is NOT >3 (ANDROMEDA strict) -> no perfusion marker -> NO flag | any([2.0>2 F, 3>3 F]) -> False -> criterion False | yes |
| FR=20; qt_vol_nora_mlh=15; diurna_lactato=3.0; TEC_s=2; diurna_ventilacao=cateter nasal | RR 20 is NOT >20 (SIRS strict boundary) -> respiratory clause fails -> NO flag | balanco_4h.filter(fr__gt=20) empty -> False -> criterion False | yes |

**Verifier notes**

All three published anchors match on value AND boundary direction: lactate >2 mmol/L (Sepsis-3 septic-shock threshold, strict), capillary refill time >3 s (ANDROMEDA-SHOCK abnormal, strict), RR >20/min (SIRS, strict). Room-air / spontaneous-ventilation gate is clinically coherent (the alert targets septic shock not yet intubated). The qt_vol_nora >10 ml/h clause is an institution-specific pump-volume threshold with no published anchor (not convertible to mcg/kg/min without concentration+weight); it does not contradict any reference, so verdict stays VERIFIED. Predicate is UNWIRED (calcular_criterios never calls criterio_4), so no live impact.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_estabilidade.py` | 321-362 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-03-064`

**Related rules:**

- [RULE-ESTABILIDADE-015](RULE-ESTABILIDADE-015-estabilidade-facade-alert-text-perfusion-shock-triggers-bica.md)

## Notes

Facade criterio_4 = 'Choque septico em ventilacao espontanea: otimizar DO2 e VO2'.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
