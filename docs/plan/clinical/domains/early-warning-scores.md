# Early-Warning Scores Domain — IntensiCare v2 Clinical Specification

**Guild:** Clinical (early-warning-scores designer) · **Vision ref:** §2 (Fase 1 — MEWS/NEWS2/SOFA/qSOFA,
status *Implementado*) · **Platform:** AMH Data Platform consumer (ADR-001) · **Legacy clusters:**
`clinical-scoring` (18 rules), `piora-clinica` (12 rules — the in-house proprietary EWS), `eficiencia`
(2 rules land here: aggregation + discharge readiness).

This document owns **continuity** of the four Phase-1 scorers and reconciles them with the published
references and the clinical-scoring / piora-clinica / eficiencia cluster dispositions. Every threshold cites
a guideline/paper and/or a `RULE-*` catalog ID. All SOFA sub-score P0 defects (FiO2 percent-vs-fraction,
vasopressor units, renal/liver boundaries) are **designed to the reference-anchored recommended default and
marked pending `RAT-CLINICAL-SCORING-01..06`** — per SYS-C-03 every P0 rule must be RATIFY, never silently
adopted. Severity uses **only** `normal | watch | urgent | critical`.

---

## 1. Clinical scope

**In scope.** The four Phase-1 early-warning scores for adult ICU (UTI), computed as pure deterministic
functions (VIS-2-06, no ML in MVP) on each new observation:

1. **MEWS** (Subbe 2001) — general clinical deterioration, aggregate 0–15 (MEWS-v1.0).
2. **NEWS2** (RCP 2017) — the NHS standard, aggregate 0–20 incl. the hypercapnic **Scale 2** variant (NEWS2-v1.0).
3. **SOFA** (Vincent 1996) — daily organ dysfunction, 0–24 (six 0–4 organ sub-scores) (SOFA — **v2.0.0** after the P0 fixes below).
4. **qSOFA** (Seymour 2016 / Sepsis-3) — bedside sepsis triage, 0–3 (qSOFA-v1.0). **Computed here, emitted to the
   sepsis domain**, which owns the qSOFA-based alert (SEP-002). No qSOFA alert is defined in this domain.

Plus two continuity items the cluster dispositions route here: the **efficiency alert aggregation** shape
(RULE-EFICIENCIA-001, ADAPT → §3.6) and the **ICU discharge/step-down readiness** composite
(RULE-EFICIENCIA-008, ADAPT → §3.7).

**Alerts owned by this domain (4, deliberately few and rich):**
`ALERT-EWS-NEWS2-DETERIORATION-01` (urgent), `ALERT-EWS-TREND-RISING-02` (watch),
`ALERT-EWS-SOFA-ACUTE-ORGAN-DYSFUNCTION-03` (urgent), `ALERT-EWS-DISCHARGE-READINESS-04` (normal).

**Out of scope / delegated.** ARDS staging → **respiratory** (consumes our `relacao_pao2_fio2`); AKI/KDIGO
staging → **aki** (supplies `creatinina`, `debito_urinario`); vasopressor `mL/h → mcg/kg/min` conversion and
shock-index trending → **hemodynamics**; pain-scale and RASS-target management → **neuro-sedation**;
transfusion appropriateness → **hemodynamics** (RULE-EFICIENCIA-002/003/004/012). Automatic diagnosis is
forbidden — all outputs are advisory, physician-owned (VIS-C-01, VIS-C-08), recorded to the prontuário at NGS
Level 2 (VIS-C-07).

**Supersession headline (see §3.5 for the precise loss ledger).** The legacy in-house **`piora-clinica`
proprietary 9-criterion EWS is SUPERSEDED by MEWS + NEWS2.** The proprietary bands had **no external
validation anchor** (RULE-PIORA-CLINICA-001/003/005/011 verdict UNVERIFIABLE) and carried multiple P0 defects
(unreachable severe-pain bands, VERMELHO→AMARELO downgrade, sign loss). Replacing it with the validated
NEWS2/MEWS is a **safety improvement**, not merely a refactor.

---

## 2. Typed, unit-checked inputs

Every unit is the canonical from `_work/units/registry.yaml`. **FiO2 is a fraction 0.21–1.0** (mission law
CON-SEED-12; percent is edge/display only — this is the fix for the cluster-wide SYS-01 defect). **Lactate is
mmol/L only** (SYS-03). Weight-indexed quantities require a validated `peso` (SYS-09: legacy weight-parse
inflated weight ~10× by stripping the decimal separator).

| Input (PT-BR param) | Quantity | Unit (canonical) | Source | Staleness max | Used by |
|---|---|---|---|---|---|
| `frequencia_cardiaca` | heart_rate | `bpm` | Observation LOINC 8867-4 | PT1H | MEWS, NEWS2 |
| `frequencia_respiratoria` | respiratory_rate | `rpm` | Observation LOINC 9279-1 | PT1H | MEWS, NEWS2, qSOFA |
| `pressao_arterial_sistolica` | systolic_blood_pressure | `mmHg` | Observation LOINC 8480-6 | PT1H | MEWS, NEWS2, qSOFA |
| `pressao_arterial_media` | mean_arterial_pressure | `mmHg` | Observation LOINC 8478-0 | PT1H | SOFA-cardio, discharge |
| `temperatura` | body_temperature | `degC` | Observation LOINC 8310-5 | PT6H | MEWS, NEWS2 |
| `saturacao_o2` | peripheral_oxygen_saturation | `percent` | Observation LOINC 2708-6 | PT1H | NEWS2, discharge |
| `nivel_consciencia` | consciousness (AVPU/ACVPU) | `enum {A,C,V,P,U}` | Observation (nursing) | PT4H | MEWS(AVPU), NEWS2(ACVPU) |
| `glasgow` | glasgow_coma_scale | `points` | Observation LOINC 9269-2 | PT8H | SOFA-CNS, qSOFA, discharge |
| `fio2` | inspired_oxygen_fraction | `fraction` | Observation LOINC 19935-6 | PT6H | SOFA-resp (P/F) |
| `pao2` | arterial_partial_pressure_o2 | `mmHg` | blood gas LOINC 2703-7 | PT12H | SOFA-resp (P/F) |
| `paco2_arterial` | arterial_partial_pressure_co2 | `mmHg` | blood gas LOINC 2019-8 | PT6H | NEWS2 Scale-2 selection |
| `relacao_pao2_fio2` | pf_ratio | `ratio` | derived (respiratory domain; FiO2 fraction!) | PT12H | SOFA-resp |
| `plaquetas` | platelet_count | `10^3/uL` | lab_result LOINC 777-3 | PT24H | SOFA-coag |
| `bilirubina` | total_bilirubin | `mg/dL` | lab_result LOINC 1975-2 | PT24H | SOFA-liver |
| `creatinina` | serum_creatinine | `mg/dL` | lab_result LOINC 2160-0 (aki) | PT24H | SOFA-renal |
| `debito_urinario` | urine_output_volume | `mL` | aki domain (24h total) | PT24H | SOFA-renal |
| `debito_urinario_horario` | urine_output_rate_indexed | `mL/kg/h` | aki domain (needs `peso`) | PT6H | SOFA-renal (rate form) |
| `dose_vasopressor` | weight_indexed_vasopressor_rate | `mcg/kg/min` | hemodynamics conversion service | PT1H | SOFA-cardio, discharge |
| `lactato_arterial` | lactate | `mmol/L` | lab_result LOINC 2524-7 | PT6H | discharge readiness |
| `peso` | body_weight | `kg` | Observation LOINC 29463-7 | PT7D | SOFA-renal (rate), dosing |
| `mechanical_ventilation` | boolean | `boolean` | device/Procedure flag | PT6H | SOFA-resp 3/4 gate |
| `supplemental_o2` | boolean | `boolean` | Observation (O2 therapy) | PT1H | NEWS2 +2 |
| `hypercapnic` | boolean | `boolean` | clinical context flag | PT7D | NEWS2 Scale-2 |
| `mews` / `news2` / `sofa` / `qsofa` | aggregate scores | `points` | derived (this domain) | PT1H–PT24H | alerts |

**Unit hazards carried from the audit (handled at the edge normalizer, never in clinical logic):**
- **FiO2** — canonical fraction 0.21–1.0. Legacy `FiO2Validator` stored **21–100 (percent)** while every P/F
  and SOFA-respiratory threshold (400/300/200/100) compared it as a fraction ⇒ ratio **~100× too small**
  (SYS-01, P0-01/P0-07, RULE-CLINICAL-SCORING-002/008). Normalized to fraction upstream in the respiratory
  domain; a bare FiO2 with no unit is a build-time error.
- **Vasopressor** — canonical `mcg/kg/min`. Legacy SOFA-cardio scored a raw noradrenaline **ml volume** at a
  `>10` cutoff (SYS-02, P0-02, RULE-CLINICAL-SCORING-005). `mL/h` is **not** convertible without drug
  concentration + weight (SYS-C-04); the hemodynamics conversion service supplies the canonical rate.
- **Weight** — comma-decimal parse (`70,5 → 705 kg`) inflated `mL/kg/h` ~10× and masked oliguria (SYS-09,
  P0-08). SOFA-renal's urine-rate band is never computed without a validated `peso`.
- **Consciousness enum** — AVPU/ACVPU is **not yet a registry parameter** (see §8 open question); used as
  `type: enum, unit: "enum"` with value set `{A,C,V,P,U}` pending a registry entry.

---

## 3. Trigger / staging logic

### 3.1 NEWS2 — the fleet EWS workhorse (`ALERT-EWS-NEWS2-DETERIORATION-01`, urgent)

NEWS2 thresholds are **authoritative and MUST NOT change** (NEWS2-C-01); carried verbatim from the RCP 2017
tables (implemented, scorers.json NEWS2-2-07..15):

```
respiratory_rate: <=8 -> 3 | 9-11 -> 1 | 12-20 -> 0 | 21-24 -> 2 | >=25 -> 3
spo2 Scale 1 (default): >=96 -> 0 | 94-95 -> 1 | 92-93 -> 2 | <=91 -> 3
spo2 Scale 2 (hypercapnic, chronic type-2 resp failure): >=93 -> 0 | 88-92 -> 1 | 86-87 -> 2 | 84-85 -> 2 | <=83 -> 3
supplemental_o2: on O2 -> +2
systolic_bp: <=90 -> 3 | 91-100 -> 2 | 101-110 -> 1 | 111-219 -> 0 | >=220 -> 3
heart_rate: <=40 -> 3 | 41-50 -> 1 | 51-90 -> 0 | 91-110 -> 1 | 111-130 -> 2 | >=131 -> 3
consciousness (ACVPU): A -> 0 | C/V/P/U -> 3
temperature: <=35.0 -> 3 | 35.1-36.0 -> 1 | 36.1-38.0 -> 0 | 38.1-39.0 -> 1 | >=39.1 -> 2
aggregate risk: low 0-4 | medium 5-6 | high >=7 ; single red parameter = any component == 3
```

**Alert = a NEW upward crossing, not a static high state.** In ICU, many patients sit chronically at
NEWS2 ≥7 (ventilated, on pressors); a static-level alert would have PPV < 0.2 and swamp the channel. The
alert is **edge-triggered**: `news2 >= 7 AND news2_prev < 7`, OR a **new** single red parameter (=3) that was
not red at the prior measurement. Cooldown PT4H re-arms only after the score drops below 7. Scale 2 is
selected only when `hypercapnic == true` (NEWS2-C-02). The urgent-assessment two-tier logic (aggregate ≥5 OR
any red) is preserved (NEWS2-C-03) but the medium band (5–6) is routed to the **trend** alert (§3.2), not a
static snapshot.

### 3.2 MEWS + rising trend (`ALERT-EWS-TREND-RISING-02`, watch)

MEWS thresholds are **authoritative and MUST NOT change** (MEWS-C-01); carried verbatim (MEWS-1-04..28):

```
heart_rate: <=40 -> 3 | 41-50 -> 2 | 51-100 -> 0 | 101-110 -> 1 | 111-129 -> 2 | >=130 -> 3
systolic_bp: <=70 -> 3 | 71-80 -> 2 | 81-100 -> 1 | 101-199 -> 0 | >=200 -> 2
respiratory_rate: <=8 -> 3 | 9-14 -> 0 | 15-20 -> 1 | 21-29 -> 2 | >=30 -> 3
temperature: <=35.0 -> 3 | 35.1-36.0 -> 1 | 36.1-38.0 -> 0 | 38.1-38.5 -> 1 | >=38.6 -> 2
avpu: A -> 0 | V -> 1 | P -> 2 | U -> 3 ; aggregate 0-15
```

**Trend, not snapshot.** `rising := (news2 - news2_start >= 3) OR (mews - mews_start >= 3)` across ≥2
consecutive scorings within PT8H. MEWS trend requires ≥2 samples (MEWS-C-02, MEWS-1-29) via
`compute_trend()` returning `increasing|decreasing|stable` (MEWS-1-31). The Δ≥3 threshold (not ≥2) and the
≥2-consecutive-sample requirement suppress measurement noise and hold PPV at the fleet floor. This absorbs
the NEWS2 medium band and gives lead time toward the ≥80 % <1h early-detection target (VIS-7.1-01).

**MEWS has no standalone alert.** It is computed and emitted (`ews.score.computed`) but a static "MEWS ≥5"
alert is deliberately omitted — it would double-fire against NEWS2-01 on overlapping physiology. Deliberate
alarm-fatigue reduction, recorded in the reconciliation block.

### 3.3 SOFA — organ dysfunction with the P0 fixes (`ALERT-EWS-SOFA-ACUTE-ORGAN-DYSFUNCTION-03`, urgent)

`sofa_total` is the **arithmetic sum of six 0–4 organ sub-scores** (RULE-CLINICAL-SCORING-001, **ADOPT**;
Vincent 1996). The alert fires on `sofa_total - sofa_total_baseline_24h >= 2` — the **Sepsis-3 acute
organ-dysfunction definition** (Singer 2016). Sub-scores, with dispositions:

#### 3.3.1 SOFA total score {#sofa-total-score}
Straight sum 0–24 (RULE-CLINICAL-SCORING-001 ADOPT). No unit/boundary defect.

#### 3.3.2 SOFA respiratory (P/F) — **P0 FiO2-fraction fix**, pending `RAT-CLINICAL-SCORING-01/05`
```
relacao_pao2_fio2 = pao2 (mmHg) / fio2 (FRACTION 0.21-1.0)     # NEVER percent (SYS-01)
>=400 -> 0 | 300-399 -> 1 | 200-299 -> 2 | 100-199 -> 3 | <100 -> 4
3- and 4-point bands ONLY when mechanical_ventilation == true (SOFA-C-02); otherwise capped at 2.
```
**Recommended default (RATIFY).** Canonical FiO2 is the **fraction** (mission law); the P/F ratio inherits it.
The legacy percent storage made the ratio ~100× too small, forcing nearly every ventilated patient to the
worst band (P0-01/P0-07). We also **gate the 3/4 bands on ventilation** (legacy applied them
unconditionally). RULE-CLINICAL-SCORING-002 and -008 are **RATIFY** (P0) — designed here to the reference,
committee confirms the canonical FiO2 unit and the `False`-as-sentinel fix (008 returned `bool False` as
"no data", which behaves as 0 downstream).

#### 3.3.3 SOFA coagulation {#sofa-coagulation-sub-score}
Platelets `>=150 -> 0 | 100-149 -> 1 | 50-99 -> 2 | 20-49 -> 3 | <20 -> 4` (×10³/µL)
(RULE-CLINICAL-SCORING-003 **ADOPT**; Vincent 1996). No defect.

#### 3.3.4 SOFA liver — **boundary fix**, pending `RAT-CLINICAL-SCORING-02`
```
bilirubina (mg/dL), CLOSED intervals: <1.2 -> 0 | 1.2-1.9 -> 1 | 2.0-5.9 -> 2 | 6.0-11.9 -> 3 | >=12.0 -> 4
```
Legacy used strict `<` at 1.9/5.9/11.9, leaving dead gaps that returned `None` (SYS-07, P1). Corrected to
closed intervals. RULE-CLINICAL-SCORING-004 is **RATIFY** (the None-gap could crash/miscount the total).

#### 3.3.5 SOFA cardiovascular — **vasopressor-unit fix**, pending `RAT-CLINICAL-SCORING-03`
```
MAP < 70 mmHg (no pressor)                          -> 1
dopamine <=5 mcg/kg/min OR dobutamine any dose      -> 2
dopamine 5.1-15 mcg/kg/min OR (nor|epi) <=0.1       -> 3
dopamine >15 mcg/kg/min OR (nor|epi) >0.1           -> 4
```
All vasopressor inputs are **weight-indexed mcg/kg/min** (CLINICAL-SCORING-C-03), obtained from the
hemodynamics conversion service (`mL/h` needs concentration + weight, SYS-C-04). Legacy scored a raw
noradrenaline **ml volume** at `>10` and omitted dopamine/epinephrine entirely (P0-02). RULE-CLINICAL-SCORING-005
is **RATIFY**.

#### 3.3.6 SOFA CNS {#sofa-cns-sub-score}
GCS `15 -> 0 | 13-14 -> 1 | 10-12 -> 2 | 6-9 -> 3 | <6 -> 4` (RULE-CLINICAL-SCORING-006 **ADOPT**; Teasdale
1974 range 3–15). No defect.

#### 3.3.7 SOFA renal — **band + MAX fix**, pending `RAT-CLINICAL-SCORING-04`
```
creatinine (mg/dL): <1.2 -> 0 | 1.2-1.9 -> 1 | 2.0-3.4 -> 2 | 3.5-4.9 -> 3 | >=5.0 -> 4
urine (mL/day):     <200 -> 4 | 200-499 -> 3 | >=500 -> 0
renal_subscore = MAX(creatinine_band, urine_band)     # SOFA-C-03, not any-first-match
```
Legacy widened the 2-point band to `2.0-4.0` (std 2.0–3.4) and used strict `>5`, leaving a dead gap at
`(4.9, 5.0]` (Cr exactly 5.0 scored 0 instead of 4 — a 4-point undercount at peak acuity, P0-03).
RULE-CLINICAL-SCORING-007 is **RATIFY**.

#### 3.3.8 SOFA input sourcing / assembly {#sofa-input-sourcing} {#sofa-input-assembly}
The verified logic that copies `fio2/po2/plaquetas/bilirrubinas/pam/dobutamina/noradrenalina/glasgow/
creatinina/debito_urinario_24h` from the prontuário then recomputes every sub-score
(RULE-CLINICAL-SCORING-011/012, **ADAPT**) is clinically sound but was a Django `save()`-hook side effect. In
v2 it becomes an **explicit deterministic SOFA compute service** invoked on each new observation (VIS-2-06),
not an implicit ORM hook.

### 3.4 qSOFA — computed, emitted, not alerted here
qSOFA `= (RR>=22 rpm) + (SBP<=100 mmHg) + (GCS<15)`, high-risk ≥2 (qSOFA-C-01/C-02; Seymour 2016). Computed
here and emitted (`ews.qsofa.computed`); the **sepsis** domain owns the qSOFA alert (SEP-002). No duplicate.

### 3.5 Legacy `piora-clinica` proprietary EWS — SUPERSEDED (precise loss ledger)

The in-house 9-criterion graded (+/−) score (FR, temperatura, PAS, FC, nível de consciência, dor numérica
0–10, dor comportamental 3–12, SpO2-regular, SpO2-DPOC; aggregate NEUTRO/AMARELO/VERMELHO) is **superseded by
NEWS2 + MEWS.** What is lost, relocated, or improved:

| Legacy element | Fate under NEWS2/MEWS | Rule / disposition |
|---|---|---|
| Proprietary aggregate NEUTRO/AMARELO/VERMELHO (RULE-PIORA-CLINICA-010) | **SUPERSEDED** by NEWS2 low/medium/high → `normal/watch/urgent`. Its P0 defects (last-writer-wins downgrade of a VERMELHO to AMARELO; `soma+=int(criterio[0])` sign loss; unreachable 15–21 band) are **not ported** (CLU-PIORA-CLINICA-C-01). | RULE-PIORA-CLINICA-010 **RATIFY** (RAT-PIORA-CLINICA-08) |
| **Pain sub-scores** (NRS 0–10 criterio_6; BPS 3–12 criterio_7) | **LOST from the EWS aggregate** — NEWS2/MEWS do **not** score pain. Pain is relocated to **neuro-sedation/pharmaco** as an analgesia signal, not a deterioration input. The buggy unreachable severe-pain bands (`7<=dor>10`, `10<=sinais>12`, P0-04/05) are discarded. **This is the single genuine clinical loss and is flagged RATIFY** (should pain remain a deterioration input?). | RULE-PIORA-CLINICA-006/007 **RATIFY** |
| Temperature sub-score contiguity gap (37.9<t<38.0 scored 0) | **Fixed and folded** into NEWS2/MEWS temperature banding (which have no gap). | RULE-PIORA-CLINICA-002 **ADOPT-CORRECTED** → §3.5.1 |
| FR / PAS / FC / consciousness proprietary bands | **SUPERSEDED** by the validated NEWS2/MEWS component bands. FC/PAS sub-score corrections (disabled 2− band, `fc==50` shadowing) are the hemodynamics domain's. | RULE-PIORA-CLINICA-001/003/004/005 (RATIFY except 004 ADOPT-CORRECTED → hemodynamics) |
| SpO2 regular + DPOC dual pathway (008/009) | **SUPERSEDED** by NEWS2 **Scale 1 / Scale 2** (correct polarity). Legacy criterio_8 `sato2>96 → 2+` "hiperoxia" inversion and the criterio_8/9 SpO2 **double-counting** are discarded. | RULE-PIORA-CLINICA-008/009 **RATIFY** |
| Per-criterion recommendation text (criterio_1–3 only; RULE-PIORA-CLINICA-011) | **REDISTRIBUTED** to domain responses (sepsis bundle, antipyretic, fluid challenge). criterio_4–9 had no text. PT-BR labels preserved verbatim as legacy vocabulary. | RULE-PIORA-CLINICA-011 **RATIFY** |

**Net.** NEWS2/MEWS are externally validated (RCP 2017; Subbe 2001); the proprietary bands were UNVERIFIABLE
and defect-laden. Supersession improves safety. The only substantive loss — **pain as a deterioration
input** — is explicitly deferred to the ratification committee.

#### 3.5.1 Piora-clínica temperatura correction {#piora-clinica-temperatura}
The legacy axillary-temp sub-score's 1+ (37.6–37.9) and 2+ (38.0–38.2) bands left `37.95 °C` scoring 0
(RULE-PIORA-CLINICA-002 **ADOPT-CORRECTED**). v2 does not revive the proprietary sub-score; temperature is
scored by NEWS2/MEWS (contiguous bands, no gap). The correction is recorded here to close the escalation.

#### 3.5.2 Score-computation trigger {#score-computation-trigger}
Legacy created a `PioraClinica` record **unconditionally on every vital-signs INSERT** regardless of value
(RULE-PIORA-CLINICA-012 **SUPERSEDE**). Under ADR-001 (AMH Gold/Athena consumer), score computation is
triggered by the **ingestion/scoring pipeline** on each new observation, not by an implicit per-INSERT ORM
side effect. *Lost:* implicit synchronous per-insert record creation. *Replaced by:* pipeline-triggered
deterministic score computation.

### 3.6 Efficiency alert aggregation {#eficiencia-alert-aggregation}
The count-based AMARELO/VERMELHO → enum aggregation (RULE-EFICIENCIA-001 **ADAPT**) is structurally sound but
in legacy only 3 of 10 criteria (c3, c5, c10) were ever computed (the rest commented out). v2 reuses the
aggregation **shape** but rewires the full criteria set so every clinical signal reaches the alert. In this
domain the only wired consumer is the discharge-readiness composite (§3.7); transfusion/restraint/coma
criteria route to hemodynamics/neuro-sedation.

### 3.7 ICU discharge / step-down readiness {#icu-discharge-readiness} (`ALERT-EWS-DISCHARGE-READINESS-04`, normal)
```
discharge_ready := admitted_gt_24h
  AND glasgow >= 14
  AND dose_vasopressor == 0 mcg/kg/min
  AND pressao_arterial_media >= 65 mmHg
  AND lactato_arterial < 2 mmol/L                # Sepsis-3 resolved-hypoperfusion marker
  AND NOT mechanical_ventilation
  AND saturacao_o2 >= 92 percent (room air / low-flow)
  AND no_active_deterioration_alert              # no EWS-01/-02/-03 firing
```
Rebuilds RULE-EFICIENCIA-008 (**ADAPT**), fixing the three legacy defects: the wrong aggregate key
(`temp`→`max_temp`) that forced the gate permanently False, the truthiness GCS check (→ `>=14`), and the
inverted `TEC>5 / lactate>2` requirement (→ *absence* of instability, `lactate < 2`). Advisory only — the
physician owns the disposition (VIS-C-08). The clinically-sound intent is anchored by the VERIFIED facade
payload RULE-EFICIENCIA-012 (AABB/TRICC restrictive posture).

---

## 4. Evidence citations for every threshold

| Threshold | Value | Evidence (guideline/paper) | Legacy rule(s) & disposition |
|---|---|---|---|
| MEWS bands (HR/SBP/RR/temp/AVPU) | 0–15 aggregate, per §3.2 | Subbe CP et al. QJM 2001;94(10):521-526 | scorers.json MEWS-v1.0 (MEWS-C-01 **MUST NOT change**) |
| NEWS2 bands (7 components) | 0–20 aggregate, per §3.1 | Royal College of Physicians. NEWS2. London: RCP, 2017; Smith GB et al. Resuscitation 2013;84(4):465-470 | scorers.json NEWS2-v1.0 (NEWS2-C-01 **MUST NOT change**) |
| NEWS2 high-risk / red param | aggregate ≥7 / any component =3 | RCP 2017 (urgent/emergency response) | NEWS2-2-04/06 |
| NEWS2 Scale 2 (hypercapnic) | SpO2 ≥93=0 … ≤83=3 | RCP 2017 (chronic type-2 resp failure) | NEWS2-C-02 |
| SOFA total | sum of six 0–4 sub-scores, 0–24 | Vincent JL et al. Intensive Care Med 1996;22(7):707-710 | RULE-CLINICAL-SCORING-001 **ADOPT** |
| SOFA respiratory (P/F) | ≥400=0 … <100=4 (FiO2 **fraction**; 3/4 need vent) | Vincent 1996; ARDS Definition Task Force JAMA 2012;307(23):2526-2533 | RULE-CLINICAL-SCORING-002/008 **RATIFY** (P0; RAT-CLINICAL-SCORING-01/05) |
| SOFA coagulation | plt ≥150=0 … <20=4 (×10³/µL) | Vincent 1996 | RULE-CLINICAL-SCORING-003 **ADOPT** |
| SOFA liver | bili <1.2=0 … ≥12.0=4 mg/dL (closed intervals) | Vincent 1996 | RULE-CLINICAL-SCORING-004 **RATIFY** (RAT-CLINICAL-SCORING-02) |
| SOFA cardiovascular | MAP<70=1; dopa/epi/nor tiers **mcg/kg/min**; dobut any=2 | Vincent 1996 | RULE-CLINICAL-SCORING-005 **RATIFY** (P0; RAT-CLINICAL-SCORING-03) |
| SOFA CNS | GCS 15=0 … <6=4 | Vincent 1996; Teasdale G, Jennett B. Lancet 1974;2(7872):81-84 | RULE-CLINICAL-SCORING-006 **ADOPT** |
| SOFA renal | Cr <1.2=0 … ≥5.0=4; urine <200=4/<500=3; **MAX** | Vincent 1996 | RULE-CLINICAL-SCORING-007 **RATIFY** (P0; RAT-CLINICAL-SCORING-04) |
| Acute organ dysfunction | Δ SOFA ≥2 from 24h baseline | Singer M et al. JAMA 2016;315(8):801-810 (Sepsis-3) | design-new on ADOPT total |
| qSOFA | ≥2 of {RR≥22, SBP≤100, GCS<15} | Seymour CW et al. JAMA 2016;315(8):762-774; Singer 2016 | scorers.json qSOFA-v1.0 (qSOFA-C-01/02) |
| EWS rising trend | Δ ≥3 across ≥2 consecutive scorings | Subbe 2001; RCP 2017 (act on trend) | scorers.json MEWS-1-29/31 (compute_trend) |
| Discharge stability lactate | < 2 mmol/L | Singer 2016 (resolved hypoperfusion) | RULE-EFICIENCIA-008 **ADAPT**; -012 **ADOPT** facade |
| Discharge readiness gate | GCS≥14, no pressor, MAP≥65, off vent | Carson JL et al. JAMA 2016;316(19):2025-2035 (AABB posture) | RULE-EFICIENCIA-008/001 **ADAPT** |
| Piora-clínica temp contiguity | 1+ band extended to <38.0 (no gap) | folded into NEWS2/MEWS temp bands | RULE-PIORA-CLINICA-002 **ADOPT-CORRECTED** |

---

## 5. Score-versioning policy (`algorithm_version`, invariant #3)

Mandated by CON-0068 (invariant #3, "DEVE ser implementado antes do primeiro paciente real"), CON-0129 /
VIS-C-13 (100 % auditable), and CON-SEED-02 (data model must add the `algorithm_version` column to the
`clinical_scores` table). **This is a hard prerequisite, not optional.**

**Version string format.** `<SCORE>-v<MAJOR>.<MINOR>.<PATCH>` — e.g. `NEWS2-v1.0.0`, `MEWS-v1.0.0`,
`qSOFA-v1.0.0`, `SOFA-v2.0.0`. The current legacy scorers are v1.0 (scorers.json MEWS/NEWS2/SOFA/qSOFA
`-v1.0`); **SOFA bumps to `v2.0.0`** because the P0 FiO2-fraction, vasopressor-unit, and renal/liver boundary
fixes change the output for the same input.

**Semantics (governs recompute):**
- **MAJOR** — any threshold/banding/unit change that alters the score for identical inputs (e.g. the SOFA P0
  fixes). Requires recompute + a dual-write window (below). Alerts must reference the new MAJOR.
- **MINOR** — a new *optional* input or sub-score handling that does **not** change existing outputs (e.g.
  adding NEWS2 Scale-2 auto-selection where it was previously manual). No recompute of historical rows.
- **PATCH** — non-clinical fixes (logging, null-handling that does not change a band). No recompute.

**Migration / recompute rules.**
1. **Historical scores are immutable** — a version bump never mutates an existing `clinical_scores` row
   (audit integrity, VIS-C-13). Recompute writes **new rows** tagged with the new `algorithm_version`.
2. Every stored score row carries: `algorithm_version`, `computed_at`, the **input snapshot reference**
   (which observations, with their staleness flags), and the evidence refs — so any historical score is
   reproducible and auditable (100 %).
3. A **recompute job** re-scores the affected retention window (per-entity retention: scores 7y, raw vitals
   90d — CON-SEED-03) under the new MAJOR, writing parallel rows; it never deletes the old-version rows.
4. Gold write-back (`fact_patient_score`, ADR001-C-04) carries `algorithm_version` as a dimension so
   corporate analytics can slice before/after a bump. A Gold-schema change to add the column is a
   **versioned breaking change** (ADR001-C-09).

**Dual-write window.** On a MAJOR bump, both the outgoing and incoming versions are computed and stored in
parallel for a defined window (recommended **≥30 days or one validation cycle**, aligned to the vision §6.1
control-vs-intervention / §6.2 stepped-wedge study needs). During the window: **alerts fire off the NEW
version**; the OLD version stays queryable so the before/after study and the DSMB (VIS-C-15) can compare
score distributions and alert rates without a discontinuity. The window close is a governance decision
recorded in the audit trail.

---

## 6. Interactions with other domains

- **→ Sepsis.** Emits `ews.qsofa.computed` (SEP-002 consumes qSOFA) and `ews.organ_dysfunction.detected`
  (ΔSOFA≥2). The sepsis doc already lists `quick_sofa (points)` under *consumes* — this domain is the producer.
- **→ Respiratory.** Consumes `relacao_pao2_fio2` (FiO2 **fraction**) and `paco2_arterial` for SOFA-resp and
  NEWS2 Scale-2 selection; ARDS staging is the respiratory domain's (RULE-CLINICAL-SCORING-017 ADAPT lives there).
- **→ Hemodynamics.** Consumes the canonical `dose_vasopressor` (mcg/kg/min) from the conversion service
  (SYS-C-04) for SOFA-cardio and MAP=(2·PAD+PAS)/3 (RULE-CLINICAL-SCORING-009 ADOPT, hemodynamics-owned). The
  piora-clínica FC/PAS sub-score corrections (RULE-PIORA-CLINICA-003/004) are hemodynamics'.
- **→ AKI.** Consumes `creatinina`, `debito_urinario`, `debito_urinario_horario` (needs validated `peso`) for
  SOFA-renal; KDIGO staging is the aki domain's.
- **→ Neuro-sedation.** Consumes `glasgow`, `rass`; the relocated **pain** signals (NRS/BPS) and the age
  utility (RULE-CLINICAL-SCORING-010 ADOPT-CORRECTED) live there.
- **→ Correlation engine / platform.** Emits `ews.deterioration.detected` / `ews.trend.rising` /
  `ews.score.computed`; the eficiencia redundant-exam and delirium-risk bundles (RULE-EFICIENCIA-007/010
  ADAPT) route to correlation-engine / neuro-sedation.

---

## 7. RATIFY design points (designed to the recommended default; committee decides)

Per SYS-C-03, **every P0 rule is RATIFY** — designed to the reference default, never silently adopted.

| RAT anchor | Dispute | Recommended default (reference-anchored) |
|---|---|---|
| **RAT-CLINICAL-SCORING-01 / 05** (RULE-CLINICAL-SCORING-002/008, P0) | FiO2 percent vs fraction feeding SOFA-resp + P/F | **FiO2 = fraction 0.21–1.0** (mission law); P/F = pao2/fio2(fraction); percent is edge/display only. Fix the `False`-as-"no data" sentinel to explicit null. §3.3.2 |
| **RAT-CLINICAL-SCORING-03** (RULE-CLINICAL-SCORING-005, P0) | SOFA-cardio raw ml volume vs weight-indexed rate | **mcg/kg/min** tiers (nor/epi ≤0.1=3/>0.1=4; dopa 2/3/4; dobut any=2; MAP<70=1) via the hemodynamics conversion service. §3.3.5 |
| **RAT-CLINICAL-SCORING-04** (RULE-CLINICAL-SCORING-007, P0) | SOFA-renal over-wide 2-pt band + `(4.9,5.0]` dead gap | **Cr 2.0–3.4=2, ≥5.0=4 closed**; urine <200=4/<500=3; renal = **MAX**(cr,urine). §3.3.7 |
| **RAT-CLINICAL-SCORING-02** (RULE-CLINICAL-SCORING-004, P1) | SOFA-liver strict-`<` dead gaps returning None | **Closed intervals** 1.2–1.9 / 2.0–5.9 / 6.0–11.9 / ≥12.0. §3.3.4 |
| **RAT-CLINICAL-SCORING-06** (RULE-CLINICAL-SCORING-014, P2) | Divergent homecare RASS labels | **One canonical RASS label set** (manual/frontend incl. the `''` sentinel); homecare divergence discarded unless intentional. |
| **RAT-PIORA-CLINICA-04/05** (RULE-PIORA-CLINICA-006/007, P0) | **Pain as a deterioration input?** — severe-pain bands unreachable | NEWS2/MEWS omit pain; pain relocated to neuro-sedation/pharmaco. **Recommended: drop pain from the EWS aggregate**; committee confirms whether pain should re-enter as a deterioration signal. |
| **RAT-PIORA-CLINICA-08** (RULE-PIORA-CLINICA-010, P0) | Proprietary aggregate overwrite/sign-loss/dead-band | **Superseded by NEWS2** (max-severity-wins, sign-preserving, validated). §3.5 |
| **RAT-PIORA-CLINICA-01/02/03/06/07/09** (001/003/005/008/009/011, UNVERIFIABLE/P1) | Proprietary FR/PAS/consciousness/SpO2 bands + facade text | **Superseded by validated NEWS2/MEWS**; PT-BR vocabulary preserved verbatim; committee confirms nothing clinically unique is discarded. |
| **RAT-EFICIENCIA-03** (RULE-EFICIENCIA-005, P0) | Coma-without-sedation GCS<13 vs <6 + AND-collapsed sedative filter | Routed to neuro-sedation; not an EWS alert. Recorded here as an interaction. |

**RAT-EWS-01 (new, this domain).** The **hypercapnic (NEWS2 Scale-2) selection source** is unspecified in the
scorer (scorers.json open question) — recommended default: a chronic type-2 respiratory-failure flag from
clinical context, defaulting to **Scale 1** when absent; committee confirms the flag provenance.

---

## 8. Open questions

1. **Consciousness enum not in registry.** AVPU (MEWS) / ACVPU (NEWS2) is used as `type: enum, unit: "enum"`
   with value set `{A,C,V,P,U}`. `_work/units/registry.yaml` has `cam_icu` (enum), `glasgow` and `rass`
   (points) but **no AVPU/ACVPU parameter** — request the units engineer add `nivel_consciencia`
   (canonical `enum`, ACVPU superset). Until then the mission canonical `enum` token is used.
2. **Δ-baseline lookback.** `sofa_total_baseline_24h` and the trend `*_at_window_start` need a defined
   prior-value source (vision open question). Design assumes the same score's most-recent prior row within
   the window; confirm mechanics with the data-model guild.
3. **Pain as a deterioration input** (RAT-PIORA-CLINICA-04/05) — the one substantive loss in superseding the
   proprietary EWS; committee decision.
4. **SOFA v2.0.0 recompute scope** — whether the dual-write window recomputes the full 7-year score retention
   or only the active-encounter window (§5); governance + cost decision.
5. All other units required **exist** in the registry; no additional new unit is requested.

---

```yaml domain-inputs
domain: early-warning-scores
inputs:
  - {name: frequencia_cardiaca, type: quantity, unit: "bpm", source: "AMH Gold Observation LOINC 8867-4"}
  - {name: frequencia_respiratoria, type: quantity, unit: "rpm", source: "AMH Gold Observation LOINC 9279-1"}
  - {name: pressao_arterial_sistolica, type: quantity, unit: "mmHg", source: "AMH Gold Observation LOINC 8480-6"}
  - {name: pressao_arterial_media, type: quantity, unit: "mmHg", source: "AMH Gold Observation LOINC 8478-0"}
  - {name: temperatura, type: quantity, unit: "degC", source: "AMH Gold Observation LOINC 8310-5"}
  - {name: saturacao_o2, type: quantity, unit: "percent", source: "AMH Gold Observation LOINC 2708-6"}
  - {name: nivel_consciencia, type: enum, unit: "enum", source: "AMH Gold Observation (AVPU/ACVPU {A,C,V,P,U}; not yet in registry)"}
  - {name: glasgow, type: quantity, unit: "points", source: "AMH Gold Observation LOINC 9269-2"}
  - {name: fio2, type: quantity, unit: "fraction", source: "AMH Gold Observation LOINC 19935-6 (canonical fraction; percent edge/display only)"}
  - {name: pao2, type: quantity, unit: "mmHg", source: "AMH Gold blood gas LOINC 2703-7"}
  - {name: paco2_arterial, type: quantity, unit: "mmHg", source: "AMH Gold blood gas LOINC 2019-8"}
  - {name: relacao_pao2_fio2, type: quantity, unit: "ratio", source: "respiratory domain (pao2 mmHg / fio2 fraction)"}
  - {name: plaquetas, type: quantity, unit: "10^3/uL", source: "AMH Gold lab_result LOINC 777-3"}
  - {name: bilirubina, type: quantity, unit: "mg/dL", source: "AMH Gold lab_result LOINC 1975-2"}
  - {name: creatinina, type: quantity, unit: "mg/dL", source: "aki domain / AMH Gold lab_result LOINC 2160-0"}
  - {name: debito_urinario, type: quantity, unit: "mL", source: "aki domain (24h total)"}
  - {name: debito_urinario_horario, type: quantity, unit: "mL/kg/h", source: "aki domain (requires validated peso)"}
  - {name: dose_vasopressor, type: quantity, unit: "mcg/kg/min", source: "hemodynamics conversion service (mL/h not convertible without concentration+peso)"}
  - {name: lactato_arterial, type: quantity, unit: "mmol/L", source: "AMH Gold lab_result LOINC 2524-7"}
  - {name: peso, type: quantity, unit: "kg", source: "AMH Gold Observation LOINC 29463-7 (validated parse)"}
  - {name: mechanical_ventilation, type: boolean, unit: "boolean", source: "AMH Gold device/Procedure flag"}
  - {name: supplemental_o2, type: boolean, unit: "boolean", source: "AMH Gold Observation (O2 therapy)"}
  - {name: hypercapnic, type: boolean, unit: "boolean", source: "clinical context flag (RAT-EWS-01)"}
  - {name: mews, type: quantity, unit: "points", source: "clinical-scoring domain (MEWS-v1.0.0)"}
  - {name: news2, type: quantity, unit: "points", source: "clinical-scoring domain (NEWS2-v1.0.0)"}
  - {name: sofa, type: quantity, unit: "points", source: "clinical-scoring domain (SOFA-v2.0.0)"}
  - {name: qsofa, type: quantity, unit: "points", source: "clinical-scoring domain (qSOFA-v1.0.0)"}
alerts:
  - ALERT-EWS-NEWS2-DETERIORATION-01
  - ALERT-EWS-TREND-RISING-02
  - ALERT-EWS-SOFA-ACUTE-ORGAN-DYSFUNCTION-03
  - ALERT-EWS-DISCHARGE-READINESS-04
rule_refs:
  - RULE-CLINICAL-SCORING-001
  - RULE-CLINICAL-SCORING-002
  - RULE-CLINICAL-SCORING-003
  - RULE-CLINICAL-SCORING-004
  - RULE-CLINICAL-SCORING-005
  - RULE-CLINICAL-SCORING-006
  - RULE-CLINICAL-SCORING-007
  - RULE-CLINICAL-SCORING-008
  - RULE-CLINICAL-SCORING-009
  - RULE-CLINICAL-SCORING-011
  - RULE-CLINICAL-SCORING-012
  - RULE-CLINICAL-SCORING-014
  - RULE-PIORA-CLINICA-001
  - RULE-PIORA-CLINICA-002
  - RULE-PIORA-CLINICA-003
  - RULE-PIORA-CLINICA-004
  - RULE-PIORA-CLINICA-005
  - RULE-PIORA-CLINICA-006
  - RULE-PIORA-CLINICA-007
  - RULE-PIORA-CLINICA-008
  - RULE-PIORA-CLINICA-009
  - RULE-PIORA-CLINICA-010
  - RULE-PIORA-CLINICA-011
  - RULE-PIORA-CLINICA-012
  - RULE-EFICIENCIA-001
  - RULE-EFICIENCIA-008
  - RULE-EFICIENCIA-012
interfaces:
  emits_events:
    - ews.score.computed
    - ews.deterioration.detected
    - ews.trend.rising
    - ews.organ_dysfunction.detected
    - ews.qsofa.computed
    - ews.discharge_readiness.detected
  consumes:
    - {quantity: pf_ratio, unit: "ratio", source: "respiratory domain"}
    - {quantity: weight_indexed_vasopressor_rate, unit: "mcg/kg/min", source: "hemodynamics domain"}
    - {quantity: serum_creatinine, unit: "mg/dL", source: "aki domain"}
    - {quantity: urine_output_volume, unit: "mL", source: "aki domain"}
    - {quantity: urine_output_rate_indexed, unit: "mL/kg/h", source: "aki domain"}
    - {quantity: mean_arterial_pressure, unit: "mmHg", source: "hemodynamics domain (MAP formula)"}
```
