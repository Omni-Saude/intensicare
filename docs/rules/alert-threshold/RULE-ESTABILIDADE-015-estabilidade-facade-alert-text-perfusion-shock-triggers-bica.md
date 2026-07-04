# RULE-ESTABILIDADE-015 — Estabilidade facade alert-text - perfusion/shock triggers & bicarbonate (criteria 1-6, 11)

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Recommendation / alert-text catalog (get_payload_trilha_estabilidade) rendered by the v3 model's get_detalhe for fired criteria. This capture covers the numeric-threshold criteria 1-6 (myocardiopathy/perfusion, out-of-protocol noradrenaline, occult shock, septic shock in spontaneous ventilation, negative fluid balance, shock index) and 11 (restricted bicarbonate in sepsis).

## Inputs

| name | type | unit |
|---|---|---|
| lactato arterial | float | mmol/L |
| ScVO2 (saturacao venosa central) | float | % |
| delta PCO2 | float | mmHg |
| balanco hidrico acumulado | float | ml |
| pH | float |  |
| bicarbonato (BIC) | float | mEq/L |

## Outputs

| name | type |
|---|---|
| alerta + recomendacoes (per criterion) | string |

## Logic

```text
criterio_1 miocardiopatia septica -> prova volemica + dobutamina SE lactato > 2 mmol/L
           OR ScVO2 < 70% OR delta PCO2 > 6; solicitar ecocardiograma.
criterio_2 inicio de noradrenalina fora do protocolo SEPSE -> checar ressuscitacao, culturas,
           dispositivos > 5 dias, abertura da ficha; garantir PAI + noradrenalina via CVC.
criterio_3 lactato > 2 mmol/L sem DVA e sem VM (choque oculto) -> abrir ficha, prova volemica,
           dobutamina; se refratario IOT + sedoanalgesia RASS -2 a -3.
criterio_4 choque septico em ventilacao espontanea -> IOT p/ otimizar DO2/VO2, RASS -2 a -3.
criterio_5 BH acumulado negativo > 2000 ml -> desafio hidrico 500 ml Ringer bolus ate 30 ml/kg.
criterio_6 indice de choque positivo -> checar disfuncao organica, abrir SEPSE, 500ml Ringer ate 30ml/kg.
criterio_11 bicarbonato na SEPSE: indicar APENAS se pH < 7.15 E BIC < 16.
```

## Edge cases (as implemented)

Text-layer thresholds: lactato>2, ScVO2<70, deltaPCO2>6, BH negativo>2000ml, bicarbonate indicated only if pH<7.15 AND BIC<16. Criteria 10, 12, 13 of the same facade function are qualitative antihypertensive-management alerts with no numeric cutoffs (see notes).

## Divergence

Cross-implementation (facade text vs v3 predicate code): the displayed alert text asserts conditions the v3 predicates never test. (a) criterio_1 text uses lactato > 2 while v3 criterio_1 (RULE-003) uses lactate >= 2, and the text's ScVO2<70 / deltaPCO2>6 branches are absent from the v3 code entirely; (b) criterio_5 text says "BH negativo > 2000ml" while v3 criterio_5 (RULE-001) compares cumulative balance < 2000 (positive, unwindowed) — see RULE-001 divergence; (c) criterio_11 text states bicarbonate is appropriate only if pH<7.15 AND BIC<16, whereas v3 criterio_11 (RULE-011) flags BIC>16 AND pH>7.2 (inverse framing with different numeric cutoffs). This text-vs-code mismatch is a NEW reconciliation finding.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** Sepsis-3 (Singer et al., JAMA 2016;315:801) hyperlactatemia >2 mmol/L; Surviving Sepsis Campaign 2021 fluid resuscitation 30 ml/kg; EGDT ScvO2 target >=70% (Rivers et al., NEJM 2001;345:1368; incorporated into SSC); venous-arterial deltaPCO2 >6 mmHg as marker of inadequate flow (Vallee et al., Intensive Care Med 2008); SSC-2021 bicarbonate pH 7.15. ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486643/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | ok |
| units | ok |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| lactato=2.0 | Sepsis-3 hyperlactatemia >2 mmol/L; facade text criterio_1 says >2 -> not yet triggered | facade text asserts lactato>2; BUT paired v3 criterio_1 (RULE-003) fires on lactate>=2 (inclusive) -> text/predicate disagree at 2.0 | no |
| ScVO2=68; deltaPCO2=7 | ScVO2<70% and deltaPCO2>6 mmHg both indicate inadequate perfusion (guideline-concordant) -> criterio_1 advice applies | facade text lists ScVO2<70 / deltaPCO2>6 branches, but v3 criterio_1 predicate has NO ScVO2 or deltaPCO2 test -> displayed condition never verified by trigger | no |
| balanco_hidrico_acumulado=-2500 | text criterio_5 'BH negativo >2000ml' -> fluid-responsive, fire | v3 criterio_5 (RULE-001) compares cumulative ganhos-perdas < 2000 (POSITIVE, unwindowed) -> fires for almost any BHA below +2000ml; sign/window bug vs the displayed text | no |
| pH=7.18; BIC=15 | text criterio_11 bicarbonate indicated only if pH<7.15 AND BIC<16 -> here pH>=7.15 so NOT indicated | text states pH<7.15 (matches SSC 7.15); paired v3 criterio_11 (RULE-011) uses pH>7.2 -> inverse framing + different cutoff | no |

**Verifier notes**

The displayed alert-text thresholds are each individually VERIFIED against published references (lactate>2 Sepsis-3, ScVO2<70% EGDT, deltaPCO2>6 mmHg, 30 ml/kg SSC fluid, bicarbonate pH 7.15). The DISCREPANCY is cross-implementation, not a reference error: get_payload text asserts thresholds the paired v3 predicates never test (ScVO2/deltaPCO2 branches absent; lactate>2 text vs >=2 code; criterio_5 negative-BH text vs positive-<2000 code sign bug). Clinician sees guideline-concordant conditions the trigger did not actually verify -> moderate impact (misleading, but the guidance text itself is clinically sound; criteria are unwired in calcular_criterios).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/facade/trilha_estabilidade.py` | 1-57, 92-101 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilidade-BE-01-013`

**Related rules:**

- [RULE-ESTABILIDADE-001](../physiological-calculation/RULE-ESTABILIDADE-001-estabilidade-v3-criterio-5-vasopressor-with-negative-cumulat.md)
- [RULE-ESTABILIDADE-002](../physiological-calculation/RULE-ESTABILIDADE-002-estabilidade-v3-criterio-6-shock-index-with-beta-blocker-vas.md)
- [RULE-ESTABILIDADE-003](RULE-ESTABILIDADE-003-estabilidade-v3-criterio-1-hypoperfusion-on-vasopressor.md)
- [RULE-ESTABILIDADE-004](../care-pathway/RULE-ESTABILIDADE-004-estabilidade-v3-criterio-2-new-vasopressor-missing-sepsis-wo.md)
- [RULE-ESTABILIDADE-005](RULE-ESTABILIDADE-005-estabilidade-v3-criterio-3-lactate-elevation-with-sepsis-the.md)
- [RULE-ESTABILIDADE-006](RULE-ESTABILIDADE-006-estabilidade-v3-criterio-4-persistent-shock-on-low-dose-vaso.md)
- [RULE-ESTABILIDADE-011](RULE-ESTABILIDADE-011-estabilidade-v3-criterio-11-bicarbonate-despite-compensated.md)
- [RULE-ESTABILIDADE-024](../care-pathway/RULE-ESTABILIDADE-024-estabilizacao-trilha2-shock-work-up-vasopressor-escalation-t.md)

## Notes

Same get_payload_trilha_estabilidade() function also defines criteria 10 ('Uso de Noradrenalina e presenca de anti-hipertensivos'), 12 ('Hipotensao recorrente e anti- hipertensivos') and 13 ('Hipertensao recorrente, otimizar anti-hipertensivos') as qualitative alerts pairing with v3 RULE-010/012/013 — captured here to avoid information loss. Verify the lactate/ScVO2/deltaPCO2/bicarbonate anchors against Sepsis-3 / SSC guidance.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
