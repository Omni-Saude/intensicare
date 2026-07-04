# RULE-ANTIMICROBIANO-003 — Antimicrobial stewardship criteria catalog (12 criteria: duration, spectrum, weight/renal dose, CVC, candidemia, cultures, CAP/COVID)

| Field | Value |
|---|---|
| Cluster | antimicrobiano |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Antimicrobial stewardship pathway payload (payload_trilha_antimicrobiano, aliased as payload_antimicrobiano_automatica): 12 stewardship criteria, each an alerta label plus one or more recomendacoes, covering antibiotic duration, spectrum de-/escalation, weight- and renal-function dose adjustment, CVC-related infection, empiric candidemia, culture solicitation, and CAP/COVID de-escalation. Consumed by get_detalhe() to render triggered criteria.

## Inputs

| name | type | unit |
|---|---|---|
| antibiotic duration | float | days |
| internacao time | float | hours |
| CVC dwell time | float | days |
| TAX (temperature) | float | degC |
| PCR (C-reactive protein) | float |  |

## Outputs

| name | type | unit |
|---|---|---|
| alerta + recomendacoes | string |  |

## Logic

```text
criterio_1  mesmo antibiotico ha > 7 dias -> considerar suspensao.
criterio_2  antibiotico de curto espectro iniciado com internacao > 48h ->
            suspender OU escalonar (Tazocin/Cefepime) + parecer infectologia.
criterio_3  ajuste de dose pelo PESO (tabela via imagem S3). SEM ajuste renal:
            Polimixina B, Linezolida, Oxacilina, Tigeciclina, Clindamicina.
criterio_4  ajuste de dose pela FUNCAO RENAL / clearence reduzido (tabela via imagem S3);
            mesmas excecoes de nao-ajuste renal que criterio_3.
criterio_5  reavaliar duracao (suspender por tempo/melhora clinica; se refratario ->
            avaliar falencia, coletar todas as culturas, imagem e escalonar espectro).
criterio_6  atraso na administracao -> acionar enfermeiro(a)/plantonista.
criterio_7  CVC > 7 dias evoluindo com febre -> avaliar retirada/troca + hemocultura
            bacterias x2; avaliar integridade e sinais flogisticos.
criterio_8  Febre > 38,3 degC + considerar retirada de CVC (> 7 dias) -> avaliar
            integridade/sinais flogisticos, retirada/troca + hemocultura bacterias x2.
criterio_9  risco de candidemia -> equinocandina (Anidulafungina/Micafungina/Caspofungina)
            + parecer infectologia + culturas: sangue bacterias x2, secrecao traqueal,
            urina, RX torax, EAS.
criterio_10 risco de candidemia -> equinocandina + parecer infectologia + 2 amostras de
            cultura de sangue para FUNGOS.
criterio_11 iniciado antimicrobiano -> avaliar solicitar culturas (sangue bacterias x2,
            secrecao traqueal, urina, RX torax, EAS).
criterio_12 antibioticoterapia para PAC com PCR < 100 OU COVID-19 confirmado ->
            considerar suspensao; considerar DPOC/congestao pulmonar/broncoaspiracao.
```

## Edge cases (as implemented)

Numeric cutoffs: same-antibiotic > 7d (criterio_1); short-spectrum start with internacao > 48h (criterio_2); CVC > 7d (criterio_7, criterio_8); fever > 38,3 degC (criterio_8); PCR < 100 (criterio_12). criterio_9 and criterio_10 carry the IDENTICAL alerta label ("Paciente grave com risco de candidemia") but differ in workup: criterio_9 = full bacterial+fungal workup (blood x2, tracheal, urine, chest X-ray, EAS); criterio_10 = fungi-only, 2 blood samples. Dose-adjustment tables for criterio_3 (weight) and criterio_4 (renal) are external S3 PNG images, not inline values. get_detalhe() on TrilhaAntimicrobianoModel surfaces only criteria 3,4,5,6,8; TrilhaCincoSintetico.get_detalhe iterates criteria 1..12.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** IDSA 2016 Clinical Practice Guideline for the Management of Candidiasis (Pappas et al., Clin Infect Dis 2016;62:e1-e50) for empiric echinocandin therapy; IDSA 2009 Guidelines for Diagnosis and Management of Intravascular Catheter-Related Infection (Mermel et al., Clin Infect Dis 2009;49:1-45) for CVC removal + paired blood cultures; Surviving Sepsis Campaign 2021 (Evans et al., Intensive Care Med 2021;47:1181-1247) for shorter antibiotic duration + daily de-escalation + procalcitonin/biomarker-guided discontinuation. Fever 38.3 degC threshold per IDSA febrile-neutropenia single-measurement definition. ([source](https://academic.oup.com/cid/article/62/4/e1/2462830 ; https://academic.oup.com/cid/article/49/11/1770/344574 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC8486643/
))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| scenario=non-neutropenic ICU patient at risk of candidemia; TAX=-; CVC_days=- | IDSA 2016: preferred empiric therapy = echinocandin (caspofungin / micafungin / anidulafungin), strong recommendation | criterio_9 / criterio_10 -> empiric candidemia tx with Anidulafungina OR Micafungina OR Caspofungina + infectology parecer | yes |
| TAX=38.5; CVC_days=10 | IDSA 2009 CRBSI: suspected catheter source with fever -> obtain paired blood cultures (>=2 sets, catheter + peripheral) and evaluate catheter removal/exchange | criterio_8 (fever >38,3 + CVC >7d) -> avaliar retirada/troca do CVC + hemocultura para bacterias em 2 amostras + sinais flogisticos | yes |
| antibiotic_duration_days=8 | SSC 2021: suggest shorter over longer antimicrobial duration with adequate source control; daily reassessment for de-escalation | criterio_1 (mesmo antibiotico >7 dias) -> considerar suspensao; criterio_5 -> reavaliar duracao | yes |
| TAX=38.3; CVC_days=7 | IDSA single-measurement fever definition uses >=38.3 degC; a temp of exactly 38.3 degC meets the fever threshold | criterio_8 uses strict > 38,3 and CVC > 7d, so 38.3 degC / 7 days exactly do NOT trigger (boundary excluded) | no |
| diagnosis=CAP, PCR/CRP 80 (<100) | SSC 2021: procalcitonin/biomarker + clinical evaluation may guide antimicrobial discontinuation (biomarker-guided de-escalation supported in principle) | criterio_12 (CAP + PCR < 100 OR confirmed COVID-19) -> considerar suspensao de antibioticos | yes |

**Verifier notes**

This rule is a qualitative stewardship care-pathway catalog (12 alerta+recomendacao entries), not a scored equation, so equation/coefficients/rounding are n/a. Every clinically anchorable element matches its authoritative reference: (a) empiric echinocandin (anidulafungin/ micafungin/caspofungin) for candidemia risk = IDSA 2016 strong recommendation for non-neutropenic ICU patients (criterio_9, criterio_10); (b) CVC removal/exchange with two blood-culture samples on fever = IDSA 2009 CRBSI management (criterio_7, criterio_8); (c) reassess/shorten antibiotic course, escalate/de-escalate spectrum, biomarker-guided discontinuation = SSC 2021 (criterio_1, criterio_2, criterio_5, criterio_11, criterio_12). The numeric thresholds that are institution-specific protocol choices -- same-antibiotic >7d, short-spectrum start with internacao >48h, CVC >7d, CRP/PCR <100 for CAP de-escalation -- are NOT drawn from a single published equation but are consistent with and do not contradict the cited guidelines (SSC endorses shorter durations and biomarker-guided stops without fixing an exact day/CRP cutoff). One immaterial boundary observation (test vector 4): criterio_8 uses a strict fever cutoff > 38,3 degC whereas IDSA's neutropenic-fever definition is >= 38.3 degC, so a temperature of exactly 38.3 degC would not trigger in legacy; clinically negligible (a single 0.0 degC boundary point on a low-specificity sign that is one of two OR-linked catheter criteria). criterio_9 and criterio_10 intentionally share the identical alerta label but differ in workup (full bacterial+fungal vs fungi-only 2 blood samples) -- both align with guideline culture practice. No frontend copy exists; trilha_automatica/facade/antimicrobiano.py is a pure alias re-export, so no cross-implementation discrepancy. Clinical content preserved verbatim.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/facade/trilha_antimicrobiano.py` | 1-94 | `8166c07eae` | primary |
| ahlabs-trilhas | `trilha_automatica/facade/antimicrobiano.py` | 1-4 | `8166c07eae` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-antimicrobiano-BE-01-019`

**Related rules:**

- [RULE-ANTIMICROBIANO-001](../alert-threshold/RULE-ANTIMICROBIANO-001-antimicrobiano-alert-color-active-calcular-alerta-v2.md)
- [RULE-ANTIMICROBIANO-002](../alert-threshold/RULE-ANTIMICROBIANO-002-antimicrobiano-alert-color-legacy-unused-calcular-alerta.md)

## Notes

trilha_automatica/facade/antimicrobiano.py only re-exports the same dict (payload_antimicrobiano_automatica = payload_trilha_antimicrobiano) - a pure alias, NOT a divergent second copy, so no cross-implementation discrepancy exists. No frontend copy of this stewardship logic was found: the only frontend "antimicrobiano" hits (trilhas-frontend src/utils/dataForms/dataFormFarmaceutico.ts lines 555/623/639) are unrelated pharmacist-intervention dropdown options, not this rule. verify=true because the catalog embeds threshold/eligibility decisions with published clinical anchors (fever > 38.3 degC + catheter management ~ IDSA CRBSI; empiric echinocandin for candidemia ~ IDSA candidiasis guidance; antibiotic-duration/de-escalation stewardship; CRP-guided CAP de-escalation). Clinical content preserved verbatim; not corrected.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
