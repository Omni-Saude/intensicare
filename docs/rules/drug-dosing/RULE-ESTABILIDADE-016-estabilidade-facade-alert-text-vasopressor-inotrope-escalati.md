# RULE-ESTABILIDADE-016 — Estabilidade facade alert-text - vasopressor/inotrope escalation ladder (criteria 7-9)

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | drug-dosing |
| Type | decision-tree |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | high |

## Rule
Recommendation / alert-text catalog for the septic-shock vasopressor and inotrope escalation steps (criteria 7-9), rendered by the v3 model's get_detalhe. Contains the institutional dosing regimens surfaced when noradrenaline dose crosses fixed cutoffs or dobutamine causes tachycardia.

## Inputs

| name | type | unit |
|---|---|---|
| noradrenalina dose | float | mcg/kg/min |
| FC | float | bpm |

## Outputs

| name | type |
|---|---|
| escalation regimen (alerta + recomendacoes) | string |

## Logic

```text
criterio_7 noradrenalina > 0.5 mcg/kg/min -> Hidrocortisona 50 mg EV 6/6h (or switch current
  corticoid to hydrocortisone) + Vasopressina EV continua 6 ml/h (dose maxima; diluicao
  institucional: Vasopressina 2 amp em SG5% 98 ml).
criterio_8 noradrenalina > 1.5 mcg/kg/min -> associar Adrenalina (1 mg/mL, 1 amp 10 mL em
  SG5% 90 mL = 0.1 mg/mL; iniciar 10 ml/h, progredir ate 100 ml/h).
criterio_9 choque refratario + altas doses de dobutamina: se FC > 130 bpm considerar SUSPENDER
  dobutamina (taquicardia reduz enchimento de VE e debito cardiaco) e associar Adrenalina
  (mesma diluicao/titulacao acima).
```

## Edge cases (as implemented)

Noradrenaline cutoffs strictly >0.5 and >1.5 mcg/kg/min; tachycardia cutoff FC>130 bpm.

## Divergence

Cross-implementation (facade text vs v3 predicate code): (a) UNITS — facade dosing is in noradrenaline mcg/kg/min (>0.5, >1.5) whereas the paired v3 predicates trigger on qt_vol_nora infusion volume in ml/h (RULE-007 >20 ml/h; RULE-008 >70 ml/h + vaso>5 ml/h), which are not convertible without concentration/weight; (b) criterio_9 text centres on FC > 130 bpm tachycardia, but v3 criterio_9 (RULE-009) tests only noradrenaline>50 ml/h AND dobutamine>10 ml/h and never checks FC. A clinician sees text claiming a mcg/kg/min threshold the trigger did not verify. NEW reconciliation finding.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** high
- **Reference:** Surviving Sepsis Campaign 2021 (Evans et al., Crit Care Med 2021): add vasopressin usually when norepinephrine 0.25-0.5 mcg/kg/min; IV hydrocortisone 200 mg/d when norepinephrine or epinephrine >= 0.25 mcg/kg/min for >= 4h; epinephrine as second-line vasopressor in refractory shock. Tachycardia (FC>130 bpm) impairs LV filling/CO (physiology of inotrope-induced tachyarrhythmia). ([source](https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-guidelines-2021))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | diff |
| units | diff |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| nora_text_threshold=0.5 mcg/kg/min; nora_predicate_threshold=20 ml/h (RULE-007) | SSC adds vasopressin/hydrocortisone ~0.25-0.5 mcg/kg/min -> 0.5 is guideline-plausible | predicate fires at qt_vol_nora>20 ml/h; e.g. 4mg/250ml (16 mcg/ml) at 20 ml/h = 5.3 mcg/min = ~0.076 mcg/kg/min for 70kg -> ~6-7x BELOW the 0.5 mcg/kg/min the text displays | no |
| nora_text_threshold=1.5 mcg/kg/min; nora_predicate_threshold=70 ml/h + vaso>5 ml/h (RULE-008) | very-high-dose refractory shock -> add epinephrine (reasonable) | predicate uses ml/h volumes not convertible to mcg/kg/min without concentration/weight -> displayed dose unverifiable against trigger | no |
| FC=140 | text criterio_9: FC>130 bpm -> consider stopping dobutamine (physiologically sound) | v3 criterio_9 (RULE-009) tests only nora>50 ml/h AND dobuta>10 ml/h; FC is never read -> alert about FC>130 fires (or not) independent of actual heart rate | no |

**Verifier notes**

The mcg/kg/min doses in the displayed text are individually plausible against SSC-2021 (0.5 is at the upper end of the 0.25-0.5 vasopressin/hydrocortisone window). The DISCREPANCY is a UNIT MISMATCH between the text (noradrenaline mcg/kg/min) and the paired v3 predicates (qt_vol_nora in ml/h): ml/h -> mcg/kg/min is not convertible without drug concentration and patient weight, and for common dilutions the ml/h trigger fires far below the mcg/kg/min the text asserts. criterio_9 text centres on FC>130 bpm that the predicate never evaluates. This is exactly the mcg/kg/min-vs- ml/h class of defect the audit targets -> high impact (clinician may act on a dose threshold the trigger never measured, or receive corticosteroid/vasopressin prompts at a much lower actual dose).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/facade/trilha_estabilidade.py` | 58-85 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-01-012`

**Related rules:**

- [RULE-ESTABILIDADE-007](../alert-threshold/RULE-ESTABILIDADE-007-estabilidade-v3-criterio-7-high-dose-noradrenaline-without-a.md)
- [RULE-ESTABILIDADE-008](../alert-threshold/RULE-ESTABILIDADE-008-estabilidade-v3-criterio-8-refractory-shock-triple-therapy.md)
- [RULE-ESTABILIDADE-009](../alert-threshold/RULE-ESTABILIDADE-009-estabilidade-v3-criterio-9-dobutamine-with-high-dose-noradre.md)
- [RULE-ESTABILIDADE-024](../care-pathway/RULE-ESTABILIDADE-024-estabilizacao-trilha2-shock-work-up-vasopressor-escalation-t.md)

## Notes

Facade function is get_payload_trilha_estabilidade (aka estabilidade_automatica text layer). Noradrenaline unit here is mcg/kg/MIN; the estabilizacao sibling (RULE-024 criterio_3) labels the analogous threshold mcg/kg/H — an additional cross-pathway unit inconsistency. Dosing regimens are drug-dosing content: verify against SSC vasopressor/corticosteroid guidance.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
