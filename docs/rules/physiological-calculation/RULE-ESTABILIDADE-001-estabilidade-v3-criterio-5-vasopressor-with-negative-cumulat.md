# RULE-ESTABILIDADE-001 — Estabilidade v3 criterio_5 - vasopressor with negative cumulative fluid balance

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | physiological-calculation |
| Type | formula |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Intended: noradrenaline started in last 6h AND cumulative fluid balance < -2000ml AND no >=500ml Ringer/saline bolus in last 4h. The code diverges substantially from this documented intent. Criterion is defined but UNWIRED (calcular_criterios does not call it).

## Inputs

| name | type | unit |
|---|---|---|
| balanco.qt_vol_nora | float | ml/h |
| balanco.qt_vol_ganhos (all-time Sum) | float | mL |
| balanco.qt_vol_perdas (all-time Sum) | float | mL |
| evolucao.diurna_lactato | float | mmol/L |

## Outputs

| name | type |
|---|---|
| criterio_5 | boolean |

## Logic

```text
balanco_acumulado = aggregate(total_ganhos=Sum(qt_vol_ganhos), total_perdas=Sum(qt_vol_perdas))  # over ALL balancos, no time window
return all([
  balanco_6h.filter(qt_vol_nora__gt=0).exists(),
  get_number(total_ganhos) - get_number(total_perdas) < 2000,   # docstring intent: BHA < -2000 (negative)
  get_number(evolucao.diurna_lactato) > 0.5,                    # docstring intent: no >=500ml Ringer/saline in 4h
]) if (ultimo_balanco and balanco_4h and ultima_evolucao) else False
```

## Edge cases (as implemented)

Cumulative balance is summed over the ENTIRE history (not a window). Comparison uses < 2000 (positive) rather than the documented < -2000, so it fires for almost any BHA below +2000 ml. The third clause tests lactate > 0.5 instead of the documented Ringer/ saline volume. Guarded by presence of ultimo_balanco/balanco_4h/ultima_evolucao else False.

## Divergence

Code vs its own docstring: (1) threshold sign — code `< 2000` vs documented `< -2000`; (2) window — code sums ALL balancos vs documented last-6h/last-4h window; (3) third clause — code tests `diurna_lactato > 0.5` vs documented "no >=500ml Ringer/saline in 4h".

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** Surviving Sepsis Campaign 2021 (Evans L et al., Crit Care Med 2021;49(11):e1063-e1143) — fluid resuscitation/de-resuscitation; Malbrain ML et al. Ann Intensive Care 2018;8:66 (ROSE concept, conservative/negative fluid balance after stabilization). No published standard fixes a specific "-2000 mL" cumulative-balance cutoff — that intent value is institutional. ([source](https://pubmed.ncbi.nlm.nih.gov/34605781/))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | intended -2000 mL negative-balance target is institutional (not a published constant) |
| units | mL (balance); mmol/L (lactate) — plausible |
| ranges | cumulative balance summed over ENTIRE history, not the documented 6h/4h window |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| nora_6h=present; sum_ganhos_minus_perdas_mL=-3200; diurna_lactato=2.0 | fire (truly negative balance < -2000 mL, on vasopressor) | fires (-3200 < 2000 True; lactate 2.0 > 0.5 True) — right output, wrong logic | yes |
| nora_6h=present; sum_ganhos_minus_perdas_mL=1000; diurna_lactato=1.0 | no fire (net +1000 mL is a POSITIVE balance, not negative) | fires (+1000 < 2000 True; lactate 1.0 > 0.5 True) — false positive from sign error | no |
| nora_6h=present; sum_ganhos_minus_perdas_mL=-3200; diurna_lactato=0.4 | fire (negative balance; documented 3rd clause is absence of >=500 mL Ringer/saline bolus, unrelated to lactate) | no fire (lactate 0.4 > 0.5 False blocks it) — third clause tests lactate, not fluid bolus | no |

**Verifier notes**

Three code-vs-docstring divergences confirmed against the source (lines 364-396): (1) SIGN — code `< 2000` (positive) vs documented `< -2000`, so it fires for essentially any balance below +2000 mL including positive balances (clinically inverted — would mislabel over-resuscitated patients as needing a fluid challenge); (2) WINDOW — code Sum() aggregates all balancos with no time window vs documented last-6h; (3) THIRD CLAUSE — code tests `diurna_lactato > 0.5` vs the documented "no >=500 mL Ringer/saline bolus in 4h". The specific -2000 mL target is institutional (UNVERIFIABLE component), but the sign inversion is an unambiguous defect against the rule's own clinical intent. Impact rated moderate on logic; mitigated to none in production because the criterion is UNWIRED (commented out in calcular_criterios).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_estabilidade.py` | 364-396 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-03-065`

**Related rules:**

- [RULE-ESTABILIDADE-014](../alert-threshold/RULE-ESTABILIDADE-014-estabilidade-v3-alert-level-calcular-alerta-calcular-alerta.md)
- [RULE-ESTABILIDADE-015](../alert-threshold/RULE-ESTABILIDADE-015-estabilidade-facade-alert-text-perfusion-shock-triggers-bica.md)

## Notes

Facade alert text for criterio_5 (RULE-015) describes "BH acumulado negativo em mais de 2000ml". Unwired in calcular_criterios. Same clinical theme as manual pathway has no direct equivalent.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
