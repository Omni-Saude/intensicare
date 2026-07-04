# RULE-ESTABILIDADE-024 — Estabilizacao (trilha2) - shock work-up & vasopressor escalation text catalog

| Field | Value |
|---|---|
| Cluster | estabilidade |
| Category | care-pathway |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Recommendation/alert-text catalog for the estabilizacao (trilha2) pathway. Criteria for malperfusion, noradrenaline initiation, high-dose noradrenaline, hyperlactatemia, antihypertensives in shock, and refractory shock with dobutamine, plus sparse criterio_7/10 stubs.

## Inputs

| name | type | unit |
|---|---|---|
| noradrenalina dose | float | mcg/kg/h (as labelled) |
| FC | float | bpm |

## Outputs

| name | type |
|---|---|
| alerta + recomendacoes | string |

## Logic

```text
criterio_1 ma perfusao (TEC prolongado) -> checar lactato/ScVO2/deltaPCO2, prova volemica ou inotropico.
criterio_2 noradrenalina iniciada nas ultimas 24h -> checar ressuscitacao/culturas/dispositivos/SEPSE;
           garantir PAI e noradrenalina via CVC.
criterio_3 noradrenalina dose alta > 0.5 mcg/kg/h -> Hidrocortisona 50 mg EV 6/6h + Vasopressina EV continua.
criterio_4 hiperlactatemia -> checar TEC/ScVO2/deltaPCO2, prova volemica + dobutamina.
criterio_5 choque + anti-hipertensivos -> suspender anti-hipertensivo/beta-bloqueador.
criterio_6 choque refratario + altas doses nora+dobutamina: FC > 130 bpm -> reduzir/suspender dobutamina.
criterio_7 (alerta "Noradrenalina >0,5mcg/kg/min, associar corticoide e vasopressina") - EMPTY recomendacoes.
criterio_10 (alerta "Noradrenalina e anti-hipertensivos na prescricao") - EMPTY recomendacoes.
```

## Edge cases (as implemented)

Structural gap: keys jump criterio_6 -> criterio_7 -> criterio_10 (criteria 8 and 9 absent). criterio_7 alerta contains a stray smart-quote after "vasopressina". Noradrenaline dose unit is mcg/kg/H (criterio_3) which conflicts with the mcg/kg/MIN used in the estabilidade facade (RULE-016).

## Divergence

Noradrenaline high-dose threshold labelled mcg/kg/H here (criterio_3) vs mcg/kg/MIN in the estabilidade facade (RULE-016 criterio_7) — a cross-pathway unit inconsistency on the same >0.5 value.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** Surviving Sepsis Campaign 2021 (Evans L, et al. Crit Care Med 2021;49(11):e1063-e1143): IV hydrocortisone 200 mg/day given as 50 mg IV q6h (or continuous) for septic shock on vasopressors; corticosteroid trigger norepinephrine/epinephrine >=0.25 mcg/kg/MIN for >=4h; add vasopressin (typically at norepinephrine 0.25-0.5 mcg/kg/MIN). Vasopressor dosing is weight-rate per MINUTE. Sepsis-3 for the hyperlactatemia concept. ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486643/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | ok |
| units | diff |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| scenario=high-dose noradrenaline, criterio_3 | hydrocortisone 50 mg IV q6h + continuous vasopressin (SSC 2021) | text: 'hidrocortisona 50mg EV 6/6hs + vasopressina EV continua' — content matches; but dose unit stated as mcg/kg/H not mcg/kg/MIN | no |
| scenario=corticosteroid trigger value, criterio_3 | norepinephrine >=0.25 mcg/kg/min (SSC 2021) | alert text uses >0.5 mcg/kg/h (wrong unit; value 0.5 within vasopressin-add range but stated per hour) | no |
| scenario=refractory shock, tachycardia, criterio_6 | excessive beta-1 chronotropy (HR>130) impairs LV filling -> reduce/hold dobutamine | text: FC>130bpm reduces LV filling -> avaliar reducao/suspensao da dobutamina — concept matches | yes |
| scenario=hyperlactatemia, criterio_4 | assess perfusion (lactate/ScvO2/deltaPCO2), volume + inotrope for low output | text: checar TEC/ScVO2/deltaPCO2, prova volemica + dobutamina — concept matches | yes |

**Verifier notes**

Verified against legacy source (core/facade/trilha_estabilizacao.py:1-54), a display-only alert/recommendation text catalog. Clinical recommendation CONTENT is consistent with SSC 2021 (hydrocortisone 50 mg q6h, continuous vasopressin, dobutamine reduction at HR>130, lactate/ perfusion work-up). Primary DISCREPANCY: criterio_3 alert states the noradrenaline high-dose threshold as ">0,5mcg/kg/H" whereas the guideline standard (and the sibling estabilidade facade RULE-016 criterio_7) express it in mcg/kg/MIN. 0.5 mcg/kg/min = 30 mcg/kg/h, so the two units differ 60x; the '/h' label in clinician-facing text is a genuine unit error of exactly the class this audit targets. Impact moderate: this file performs no numeric comparison so it will not itself misfire, but (a) it shows an incorrect unit in clinical guidance and (b) any downstream reuse of the '/h' framing against a real mcg/kg/min feed would spuriously classify almost any noradrenaline exposure as 'high dose'. Threshold value 0.5 also exceeds the SSC corticosteroid trigger of 0.25 mcg/kg/min (0.5 is the top of the vasopressin- add band) — later/stricter escalation. Additional non-clinical defects: structural key gap (criterio_6 -> _7 -> _10, missing 8/9), criterio_7 and criterio_10 have empty recomendacoes, and criterio_7 alerta carries a stray smart-quote. Rule status was AMBIGUOUS; characterized here as a units DISCREPANCY with otherwise reference-consistent content.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/facade/trilha_estabilizacao.py` | 1-54 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-estabilizacao-BE-01-014`

**Related rules:**

- [RULE-ESTABILIDADE-015](../alert-threshold/RULE-ESTABILIDADE-015-estabilidade-facade-alert-text-perfusion-shock-triggers-bica.md)
- [RULE-ESTABILIDADE-016](../drug-dosing/RULE-ESTABILIDADE-016-estabilidade-facade-alert-text-vasopressor-inotrope-escalati.md)
- [RULE-ESTABILIDADE-025](../alert-threshold/RULE-ESTABILIDADE-025-estabilizacao-v1-alert-with-criterio-6-combination-clause.md)

## Notes

AMBIGUOUS: overlaps heavily with the estabilidade facade/v3 (RULE-015/016) but is a SEPARATE pathway (payload_trilha_estabilizacao, feeds trilha2) with sparser content and missing criteria; not merged (variant). Phase-1 description labelled this payload_estabilizacao_ automatica, but the cited file core/facade/trilha_estabilizacao.py actually defines payload_trilha_estabilizacao; trilha2.py imports a sibling payload_estabilizacao_automatica from trilha_automatica/facade/estabilizacao.py (not captured here). Dosing content -> verify:true.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
