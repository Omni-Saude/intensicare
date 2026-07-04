# Respiratory Domain — IntensiCare v2 Clinical Specification

**Guild:** Clinical (respiratory domain designer) · **Vision ref:** §3.3 (Insuficiência Respiratória, priority P5,
Fase 2b) · **Platform:** AMH Data Platform consumer (ADR-001) · **Legacy cluster:** `ventilacao` (26 rules, three
competing ventilation pathways).

This document reconciles the legacy's three independent ventilation pathways — the **trilha_manual** 10-criterion
pathway (C1–C10), the parallel **trilha_automatica v1** pathway (active + a dead alert function), and the
**facade weaning/PEEP-titration/PRONA/tracheostomy protocol** — into **one** evidence-anchored surveillance design:
a **Berlin ARDS staging layer over SpO₂/FiO₂ (S/F) surveillance**, a **ventilatory-deterioration trend**, a
**patient–ventilator asynchrony** flag, a **weaning-readiness bundle**, and a **prolonged-intubation / tracheostomy**
timer. Every threshold below cites a guideline/paper and/or a `RULE-VENTILACAO-*` catalog ID. Disputed P0/P1/UNVERIFIABLE
defects are designed to the reference-anchored **recommended default** and marked **pending RAT-VENTILACAO-\***; the
ratification committee decides (§7).

> **MISSION LAW — FiO₂ is a fraction 0–1 at every computation boundary.** Registry `fio2.canonical_unit = "fraction"`
> (CON-SEED-12, CON-0155, SYS-01). Percent is an *edge input* (÷100 on ingest) and a *display transform* only. Every
> S/F and P/F formula in this document consumes FiO₂ as a fraction. The legacy defect where C2/C3 divided FiO₂ by 100
> as a percentage while C8 compared it as a fraction (`fio2 < 0.4`) — an internally inconsistent, safety-critical
> unit clash — is **not ported**; it is the SYS-01 kill.

---

## 1. Clinical scope

**In scope.** Adult ICU (UTI) respiratory failure surveillance in mechanically ventilated and oxygen-supplemented
patients, per the Berlin Definition (2012) and the vision §3.3 alert set:

1. **ARDS surveillance & Berlin staging** — non-invasively via the **S/F ratio** (SpO₂/FiO₂), the validated surrogate
   for P/F (Rice 2007) that avoids repeated arterial blood-gas sampling (vision VIS-3.3-01); confirmed by P/F when an
   ABG is available. Staged leve → moderada → grave with matching severity.
2. **Lung-protective ventilation companion** — tidal-volume-per-PBW and plateau-pressure advisory embedded in the ARDS
   layer (ARDSNet ≤6 mL/kg PBW; plateau ≤30 cmH₂O). **Pending RAT-VENTILACAO-02** (legacy used an unsafe absolute
   VT>500 mL, not weight-indexed).
3. **Ventilatory deterioration** — a short-horizon trend on S/F and FiO₂ demand (Rice 2017).
4. **Patient–ventilator asynchrony** — spontaneous RR above set RR with an elevated plateau pressure (Thille 2016).
5. **Weaning / extubation readiness** — the ERS/ATS spontaneous-breathing-trial readiness bundle (Boles 2007) with the
   RSBI (Yang & Tobin 1991).
6. **Prolonged intubation / tracheostomy timing** — orotracheal ventilation beyond 10 days (TracMan-era timing), with a
   COVID-specific deferral **pending RAT-VENTILACAO-05**.
7. **Oxygenation targets** — SpO₂ target bands including the COPD / hypercapnia-risk lowered target (BTS 2017), used as a
   gating context, not a standalone alert.

**Out of scope / delegated.**
- **Cross-domain correlations** (vision VIS-4-03 "SDRA + choque"): the *respiratory half* is emitted here
  (`respiratory.ards.staged`); the combined **ARDS-with-shock** (RULE-VENTILACAO-010, ADOPT, P/F<150 + vasopressor +
  prolonged admission) and **shock-without-ventilation** (RULE-VENTILACAO-012, ADOPT-CORRECTED) reasoning lives in the
  **correlation-engine** domain.
- **SOFA-respiratory / NEWS2-Scale-2 scoring** → **clinical-scoring** domain (this domain *publishes* the FiO₂-normalized
  P/F and S/F they consume; CON-0110 gates SOFA-resp 3/4 on mechanical ventilation).
- **Vasopressor unit conversion** (`mL/h → mcg/kg/min`, SYS-C-04) → **hemodynamics** domain; this domain consumes the
  already-canonical `dose_vasopressor`.
- **Ventilator-parameter form bounds & nursing/secretion enums** (RULE-VENTILACAO-018–023, -026) →
  `design/screens/clinical-forms.md`. This doc reuses only the controlled *mode/device/modality* vocabulary (§6).
- Automatic diagnosis is forbidden — outputs are advisory, physician-owned (VIS-C-01, VIS-C-08), recorded to the
  prontuário at NGS Level 2 (VIS-C-07).

**Reconciliation summary (three pathways → one design).** The legacy pathways disagree on thresholds
(COVID tracheostomy >10 d in C6 vs >14 d in the facade), on FiO₂ units (percent in C2/C3 vs fraction in C8), on
alert aggregation (trilha_manual count+override, trilha_automatica v1 subset count, plus a dead legacy alert function),
and on ventilator-parameter bounds across four forms. We **do not port any institutional aggregation verbatim**: the
three-state VERMELHO/AMARELO/NEUTRO mechanism (RULE-VENTILACAO-014 ADAPT) is replaced by the v2 `normal|watch|urgent|
critical` scale, the narrower trilha_automatica v1 subset (RULE-VENTILACAO-015) is superseded, and the never-called
legacy alert (RULE-VENTILACAO-016) is retired. The v2 layer is rebuilt on the *published* anchors the vision keeps —
Berlin S/F bands, ERS/ATS weaning readiness, ARDSNet lung protection — with legacy criteria carried forward only where
VERIFIED or corrected to the reference.

---

## 2. Typed, unit-checked inputs

Every unit is the canonical from `_work/units/registry.yaml`. **FiO₂ is a fraction 0–1** (mission law). Weight-/height-
indexed quantities (PBW, mL/kg) require a validated `peso`/`altura` (SYS-09: legacy weight-parse `70,5 → 705 kg`).

| Input (PT-BR param) | Quantity | Unit (canonical) | Source | Staleness max |
|---|---|---|---|---|
| `saturacao_o2` (SpO₂) | peripheral_oxygen_saturation | `percent` | AMH Gold Observation LOINC 2708-6 | PT15M |
| `fio2` | inspired_oxygen_fraction | `fraction` (0.21–1.0) | Observation LOINC 19935-6 / ventilator OBX | PT15M |
| `pao2` | arterial_partial_pressure_o2 | `mmHg` | blood gas LOINC 2703-7 (opt, when ABG) | PT6H |
| `paco2` | arterial_partial_pressure_co2 | `mmHg` | blood gas LOINC 2019-8 | PT6H |
| `ph_arterial` | acidity | `pH` | blood gas LOINC 2744-1 | PT6H |
| `relacao_spo2_fio2` (S/F) | sf_ratio | `ratio` | derived = SpO₂ / FiO₂(fraction) | PT15M |
| `relacao_pao2_fio2` (P/F) | pf_ratio | `ratio` | derived = PaO₂ / FiO₂(fraction) | PT6H |
| `peep` | positive_end_expiratory_pressure | `cmH2O` | Observation LOINC 20077-4 / ventilator | PT1H |
| `pressao_plato` | plateau_pressure | `cmH2O` | ventilator OBX (opt) | PT1H |
| `pressao_inspiratoria` | peak_inspiratory_pressure | `cmH2O` | ventilator OBX (opt) | PT1H |
| `volume_corrente` | tidal_volume_absolute | `mL` | ventilator OBX | PT1H |
| `volume_corrente_pbw` | tidal_volume_indexed | `mL/kg` | derived = VT / PBW(altura, sex) | PT1H |
| `frequencia_respiratoria` | respiratory_rate | `rpm` | Observation LOINC 9279-1 (spontaneous) | PT1H |
| `frequencia_respiratoria_programada` | respiratory_rate | `rpm` | ventilator OBX (set RR) — see §7 OQ-1 | PT1H |
| `indice_respiracao_rapida_superficial` (RSBI) | ratio | `ratio` | derived = RR / VT(L) | PT1H |
| `altura` | body_height | `cm` | Observation LOINC 8302-2 | PT30D |
| `peso` | body_weight | `kg` | Observation LOINC 29463-7 (for PBW/dosing) | PT7D |
| `idade` | age | `years` | Patient | static |
| `rass` | richmond_agitation_sedation_scale | `points` (−5..+4) | sedação domain, Observation LOINC 75826-6 | PT4H |
| `glasgow` | glasgow_coma_scale | `points` (3–15) | Observation LOINC 9269-2 | PT8H |
| `dose_vasopressor` | weight_indexed_vasopressor_rate | `mcg/kg/min` | hemodynamics domain (MedicationAdministration) | PT1H |
| `tipo_suporte_ventilatorio` | ventilation_support_type | `enum` (§6) | ventilator / clinical form | PT4H |
| `dispositivo_via_aerea` | airway_device | `enum` (§6) | clinical form / EMR | PT12H |
| `modalidade_ventilatoria` | ventilation_modality | `enum` (§6) | ventilator / clinical form | PT4H |
| `infiltrado_bilateral` | bilateral_infiltrates_present | `boolean` | imaging DiagnosticReport (CXR/CT) | PT24H |
| `edema_cardiogenico_excluido` | ards_cardiac_exclusion | `boolean` | clinical assessment (Berlin qualifier) | PT24H |
| `dpoc_risco_hipercapnia` | copd_hypercapnia_risk | `boolean` | Condition (SNOMED, DPOC) | static |
| `covid19_ativo` | covid19_active | `boolean` | Condition (COVID-19) | PT7D |
| `dias_em_ventilacao_mecanica` | days_on_mechanical_ventilation | `count` (days) | derived — see §7 OQ-2 / RAT-VENTILACAO-01 | PT1H |

**Unit hazards carried from the audit (all handled at the edge normalizer, never in clinical logic):**
- **FiO₂** — canonical **fraction 0.21–1.0**. `percent → fraction ×0.01`. Legacy `FiO2Validator` stored 21–100 while
  S/F, P/F, SOFA-resp and Berlin/weaning thresholds compared it as a fraction → ratio ~100× too small (SYS-01/P0-07;
  RULE-VENTILACAO-004/005/011). **Any S/F or P/F computed from percent FiO₂ is a build-time error.**
- **Weight / height** — comma-decimal parse (`70,5 → 705 kg`, `1,70 m`) inflated weight-indexed values ~10× (SYS-09).
  PBW and `volume_corrente_pbw` are never computed without validated `altura` + sex; `debito`/dosing likewise need `peso`.
- **Ventilator-pressure bounds** diverged 0–40/0–30 vs 5–18/5–40 across four legacy forms
  (RULE-VENTILACAO-018/019/020/022/023); reconciled to **PEEP 0–24 cmH₂O, PINS/plateau 0–30 cmH₂O** (ARDSNet PEEP/FiO₂
  ceiling + Amato driving-pressure limit) at the form layer, not here.
- **Vasopressor** — canonical `mcg/kg/min`; `mL/h` is **not** convertible without concentration + weight (SYS-C-04). The
  weaning bundle consumes the already-converted rate from hemodynamics.

---

## 3. Trigger / staging logic

Severity uses **only** `normal | watch | urgent | critical`. Each block cites its evidence and the legacy disposition;
RATIFY criteria are *designed to the recommended default* and flagged **pending RAT-VENTILACAO-\***.

### 3.1 ARDS surveillance & Berlin staging — `ALERT-RESP-ARDS-STAGING-01` (staged: watch → urgent → critical)

Berlin qualifiers gate the alert (Berlin Definition 2012): acute onset ≤1 week, **PEEP ≥5 cmH₂O**, bilateral infiltrates
not fully explained by cardiac failure/fluid overload. Staging uses S/F (non-invasive, primary) and P/F (when ABG present).

```
ards_gate :=
    on_mechanical_ventilation_or_cpap
    AND peep >= 5 cmH2O                       # Berlin minimum PEEP/CPAP
    AND infiltrado_bilateral == true          # bilateral infiltrates (CXR/CT)
    AND edema_cardiogenico_excluido == true    # not fully cardiogenic (Berlin qualifier)

# FiO2 is a FRACTION here. S/F = SpO2(percent numeric) / FiO2(fraction).  P/F = PaO2(mmHg) / FiO2(fraction).
stage(leve)     := ards_gate AND ( relacao_spo2_fio2 <= 315 AND relacao_spo2_fio2 > 235 )   # ~P/F 200–300  -> severity WATCH
                              OR  ( pf_available AND relacao_pao2_fio2 <= 300 AND relacao_pao2_fio2 > 200 )
stage(moderada) := ards_gate AND ( relacao_spo2_fio2 <= 235 AND relacao_spo2_fio2 > 148 )   # ~P/F 100–200  -> severity URGENT
                              OR  ( pf_available AND relacao_pao2_fio2 <= 200 AND relacao_pao2_fio2 > 100 )
stage(grave)    := ards_gate AND ( relacao_spo2_fio2 <= 148 )                                # ~P/F <100     -> severity CRITICAL
                              OR  ( pf_available AND relacao_pao2_fio2 <= 100 )

# When an ABG is present, P/F is authoritative and overrides the S/F band (S/F overestimates when SpO2 > 97%).
```

**Severity ladder.** One richer alert, staged: **leve = watch, moderada = urgent, grave = critical** (alarm-fatigue:
one ARDS signal per patient with an escalating tier, not three separate channels). Schema `severity` is declared as the
actionable core (**urgent**); the emitted `respiratory.ards.staged` event carries the exact `stage` and firing severity.

**Lung-protective companion (embedded advisory, pending RAT-VENTILACAO-02).** For any staged patient, evaluate
`volume_corrente_pbw` against the ARDSNet target and plateau against Amato:
```
lung_protective_violation :=
    volume_corrente_pbw > 6 mL/kg-PBW        # recommended default; ARDSNet ARMA 2000. PBW from altura+sex (Devine), NOT peso
    OR ( pressao_plato present AND pressao_plato > 30 cmH2O )   # Amato NEJM 2015
```
Legacy C1 (RULE-VENTILACAO-003) flagged an **absolute VT > 500 mL** — not weight-indexed, contradicting the PBW
calculator (RULE-VENTILACAO-001 ADOPT). The corrected weight-indexed threshold is a **P1 RATIFY** (RAT-VENTILACAO-02);
until ratified this violation annotates the ARDS alert rather than forcing a separate critical channel.

**PEEP/FiO₂ titration adequacy (embedded advisory, pending RAT-VENTILACAO-03/04).** The legacy PEEP/FiO₂ table checks
(C2/C3, RULE-VENTILACAO-004/005) carried the SYS-01 FiO₂-percent bug and a dead `False and peep>0` guard; with FiO₂
normalized to fraction, the ARDSNet lower-PEEP/higher-FiO₂ table can flag a PEEP-below-table mismatch, but the exact
table binding is **P1 RATIFY** (RAT-VENTILACAO-03/04) — captured, not fired, in v2 until ratified.

### 3.2 Ventilatory deterioration — `ALERT-RESP-DETERIORATION-02` (severity: urgent)

```
ventilatory_deterioration :=
    delta_sf_ratio_6h <= -0.20 * relacao_spo2_fio2_6h_ago      # >20% fall in S/F over 6h (FiO2 fraction throughout)
    OR ( fio2_atual > 1.30 * fio2_6h_ago AND saturacao_o2_atual <= saturacao_o2_6h_ago )  # >30% rise in FiO2 to hold SpO2
```
Evidence: Rice TW et al., Chest 2017 (catalog RESP-003); the trend is computed on the ADOPT-normalized S/F, FiO₂ (fraction).
**Suppression is load-bearing** here (transient desaturation on suctioning/turning): require the fall to persist across
**≥2 consecutive S/F samples** and exclude readings within a documented airway-maintenance event.

### 3.3 Patient–ventilator asynchrony — `ALERT-RESP-ASYNCHRONY-03` (severity: watch)

```
ventilator_asynchrony :=
    on_mechanical_ventilation
    AND frequencia_respiratoria > frequencia_respiratoria_programada   # spontaneous RR above set RR (both rpm)
    AND ( pressao_plato present AND pressao_plato > 30 cmH2O )          # elevated plateau (vision §3.3 "if available")
```
Evidence: Thille AW et al., Intensive Care Med 2016 (vision VIS-3.3-06); plateau limit Amato NEJM 2015. When plateau is
absent (Média data availability, RULE-DATA-AVAIL ventilator), the alert degrades to "insufficient data" — it does **not**
fire on the RR criterion alone, protecting PPV. Severity **watch**: asynchrony is a titration prompt, rarely
minutes-to-life-critical on its own.

### 3.4 Weaning / extubation readiness — `ALERT-RESP-WEANING-READY-04` (severity: normal)

```
weaning_ready := ALL sustained for >= 2h:
    relacao_spo2_fio2 > 315                     # adequate oxygenation (S/F; equiv P/F > 300)  — catalog RESP-004
    AND peep <= 8 cmH2O                          # low PEEP
    AND fio2 <= 0.40                             # FRACTION (recommended default, pending RAT-VENTILACAO-06 / P0)
    AND ( rsbi < 105 if rsbi present )           # RSBI Yang & Tobin 1991 (RR/VT in L); optional
    AND rass >= -2                               # arousable (RULE-VENTILACAO-007 ADAPT; Sessler 2002)
    AND glasgow > 8                              # RULE-VENTILACAO-007 ADAPT disjunct
    AND dose_vasopressor <= 0.2 mcg/kg/min       # no high vasopressor support (canonical mcg/kg/min)
    AND days_on_mechanical_ventilation >= 1       # >1 day VM (pending RAT-VENTILACAO-01 duration primitive)
```
Evidence: Boles JM et al., Eur Respir J 2007 (ERS/ATS weaning consensus; catalog RESP-004); Yang & Tobin, NEJM 1991
(RSBI); RULE-VENTILACAO-017 (facade weaning protocol, ADOPT). **RAT-VENTILACAO-06 (P0):** legacy C8 (RULE-VENTILACAO-011)
compared `fio2 < 0.4` as a fraction while siblings used percent — the mission-law fraction resolves the number, but the
P0 escalation still requires committee sign-off on this alert-forcing extubation-readiness criterion. **RAT-VENTILACAO-01
(UNVERIFIABLE):** the `days_on_mechanical_ventilation` primitive (RULE-VENTILACAO-002) had `.days`-truncation and
`abs()`-on-future-timestamp quirks; recommended default is a floor of whole elapsed days from the first VM record with no
`abs()`. The legacy C4 unreachable branch (dispositivo compared against modalidade values PCV/VCV, RULE-VENTILACAO-025)
is corrected by comparing `modalidade_ventilatoria` (§6). Severity **normal**: this is a positive opportunity prompt
(start an SBT), not a deterioration.

### 3.5 Prolonged intubation / tracheostomy timing — `ALERT-RESP-PROLONGED-INTUB-05` (severity: watch)

```
prolonged_intubation :=
    dispositivo_via_aerea == "TOT"                       # orotracheal tube (not TQT/DNI)
    AND days_on_mechanical_ventilation > 10               # RULE-VENTILACAO-008 (ADOPT, VERIFIED)

covid_tracheostomy_deferral (companion, pending RAT-VENTILACAO-05):
    covid19_ativo == true -> use threshold days_on_mechanical_ventilation >= 14   # AAO-HNS 2020 recommended default
```
Evidence: RULE-VENTILACAO-008 (ADOPT; TracMan-era tracheostomy-timing evidence, Young D et al., JAMA 2013); the COVID
deferral resolves the legacy contradiction between C6 (>10 d, RULE-VENTILACAO-009) and the facade (>14 d,
RULE-VENTILACAO-017) — a **P1 RATIFY** (RAT-VENTILACAO-05); recommended default **≥14 days** for active COVID-19 per
AAO-HNS/international guidance. Fires once at the threshold crossing (deduped for the admission); prompts a
multidisciplinary tracheostomy-timing discussion, not an emergency.

### 3.6 Oxygenation-target context (gating, not a standalone alert)

```
oxygenation_target_ok :=
    ( dpoc_risco_hipercapnia == true  AND saturacao_o2 >= 88 percent AND saturacao_o2 <= 92 percent )
    OR ( dpoc_risco_hipercapnia == false AND saturacao_o2 >= 94 percent AND saturacao_o2 <= 98 percent )
```
Evidence: O'Driscoll BR et al., BTS Guideline, Thorax 2017 (94–98% general / 88–92% hypercapnic-risk); RULE-VENTILACAO-013
(ADOPT, VERIFIED, COPD lowered target). Used to contextualize deterioration/weaning (a COPD patient at SpO₂ 90% is **at
target**, not deteriorating), reducing false positives — an alarm-fatigue lever, not its own alert channel.

---

## 4. Evidence citations for every threshold

| Threshold | Value | Evidence (guideline/paper) | Legacy rule(s) & disposition |
|---|---|---|---|
| ARDS mild (S/F) | S/F ≤315 (& >235); P/F 200–300 | Berlin (ARDS Def. Task Force, JAMA 2012); Rice 2007 Chest (S/F) | catalog RESP-001; RULE-VENTILACAO-017 ADOPT |
| ARDS moderate (S/F) | S/F ≤235 (& >148); P/F 100–200 | Berlin 2012 | catalog RESP-002 |
| ARDS severe (S/F) | S/F ≤148; P/F <100 | Berlin 2012 | catalog RESP-002b |
| Berlin PEEP minimum | PEEP ≥5 cmH₂O | Berlin 2012 | RULE-VENTILACAO-017 ADOPT |
| Lung-protective VT | ≤6 mL/kg PBW | ARDSNet ARMA, NEJM 2000 | RULE-VENTILACAO-001 ADOPT; RULE-VENTILACAO-003 **RATIFY** (RAT-VENTILACAO-02; legacy absolute >500 mL) |
| Plateau pressure limit | ≤30 cmH₂O | Amato MB et al., NEJM 2015 | RULE-VENTILACAO-018/023 (form bounds); vision §3.3 |
| PEEP/FiO₂ titration table | ARDSNet lower-PEEP/higher-FiO₂ | ARDSNet ARMA/ALVEOLI, NEJM 2000 | RULE-VENTILACAO-004/005 **RATIFY** (RAT-VENTILACAO-03/04; FiO₂ fraction) |
| S/F deterioration | ΔS/F ≤ −20% in 6h | Rice TW et al., Chest 2017 | catalog RESP-003 |
| FiO₂ escalation | FiO₂ ↑ >30% to hold SpO₂ | Rice 2017; vision VIS-3.3-05 | catalog RESP-003 |
| Asynchrony | spontaneous RR > set RR AND plateau >30 cmH₂O | Thille AW et al., ICM 2016 | vision VIS-3.3-06 |
| Weaning oxygenation | S/F >315 (P/F >300) | Boles 2007 ERS/ATS | catalog RESP-004; RULE-VENTILACAO-017 ADOPT |
| Weaning PEEP / FiO₂ | PEEP ≤8; FiO₂ ≤0.40 (fraction) | Boles 2007 | RULE-VENTILACAO-011 **RATIFY** (RAT-VENTILACAO-06 / P0) |
| RSBI | <105 (RR/VT, breaths·min⁻¹·L⁻¹) | Yang & Tobin, NEJM 1991 | catalog RESP-004 |
| Weaning arousal | RASS ≥ −2 AND GCS >8 | Sessler 2002 (RASS); Teasdale 1974 (GCS) | RULE-VENTILACAO-007 **ADAPT** |
| Weaning vasopressor ceiling | ≤0.2 mcg/kg/min | Boles 2007; SSC-2021 | catalog RESP-004 (canonical mcg/kg/min) |
| Prolonged intubation | TOT >10 days | TracMan (Young D, JAMA 2013) | RULE-VENTILACAO-008 **ADOPT** (VERIFIED) |
| COVID tracheostomy | ≥14 days (recommended default) | AAO-HNS COVID-19 tracheostomy 2020 | RULE-VENTILACAO-009 **RATIFY** (RAT-VENTILACAO-05; legacy C6 >10 d vs facade >14 d) |
| SpO₂ target (general) | 94–98% | O'Driscoll BR, BTS, Thorax 2017 | RULE-VENTILACAO-013 ADOPT |
| SpO₂ target (COPD/hypercapnia) | 88–92% | BTS 2017 | RULE-VENTILACAO-013 **ADOPT** (VERIFIED) |
| Prone positioning (context) | P/F <150 → consider prone | PROSEVA (Guerin C, NEJM 2013) | RULE-VENTILACAO-017 ADOPT; RULE-VENTILACAO-010 ADOPT (→ correlation-engine) |

---

## 5. Interactions with other domains

- **Respiratory + Hemodynamic** (vision VIS-4-03 "SDRA + choque"). ARDS-STAGING-01 emits `respiratory.ards.staged`; the
  **correlation-engine** combines it with hemodynamic shock. RULE-VENTILACAO-010 (ADOPT; P/F<150 + vasopressor<25 +
  admission>7 d) and RULE-VENTILACAO-012 (ADOPT-CORRECTED; shock without VM, lactate>2 mmol/L per Sepsis-3) target
  `clinical/domains/correlation-engine.md`; this domain supplies the respiratory half only.
- **Respiratory → clinical-scoring.** This domain **publishes** the FiO₂-normalized `relacao_pao2_fio2` and
  `relacao_spo2_fio2`; clinical-scoring consumes P/F for the SOFA-respiratory sub-score (CON-0110: 3/4 only on VM) and
  SpO₂/PaCO₂ for NEWS2 Scale-1 vs Scale-2 selection (CON-0107). The FiO₂-fraction law is the shared kill-switch (SYS-01).
- **Respiratory → sepsis.** Sepsis consumes `relacao_pao2_fio2` (FiO₂ fraction) and `paco2` for its oxygenation
  minor-criterion; ARDS staging itself stays here (sepsis.md §5 delegates ARDS to respiratory).
- **Respiratory ← sedação / delirium.** The weaning bundle consumes `rass` (arousal) and `glasgow`; deep sedation
  (RASS < −3) suppresses a weaning-ready signal. Asynchrony findings feed the sedation/analgesia titration loop.
- **Respiratory ← hemodynamics.** Weaning consumes the already-converted `dose_vasopressor` (mcg/kg/min); the `mL/h`
  conversion is hemodynamics' (SYS-C-04) — never done here.
- **Platform.** Ventilator data arrives via HL7 ORU manufacturer-specific OBX (vision VIS-3.3-09) normalized into AMH
  Gold; all reads are Athena-against-Gold (ADR-001-C-01), no own FHIR/ingestion. Alerts recorded to prontuário NGS L2
  (VIS-C-07); the mode/device/modality vocabulary (§6) is the shared controlled vocabulary with `clinical-forms`.

---

## 6. Controlled vocabulary — ventilation modes (supersedes legacy typo-matched free text)

The legacy matched **exact free-text strings** including misspellings and misroutes (RULE-VENTILACAO-024, DISCREPANCY,
P3), e.g. `'espontnaea'`, `'estpotanea'`, `'esponatea'` and mis-mapped `'vni/ mascara facial'`, `'ve pela tqt por
mascara'` — all classified as spontaneous breathing. v2 **supersedes** live free-text matching with three structured
enumerations (RULE-VENTILACAO-025 ADAPT — PT-BR values/labels preserved verbatim, the `vm_invasiva`↔`'Cateter Nasal de
O2'` label mismatch corrected; historical free text migrated once, not matched live). **PT-BR labels are verbatim.**

### 6.1 `tipo_suporte_ventilatorio` — ventilation support type

| Canonical value | PT-BR label (verbatim) | Synonyms / legacy strings mapped in (one-time migration) |
|---|---|---|
| `ar_ambiente` | "Ar ambiente / Espontânea" | `ar_ambiente`, `ventilacao_ar_ambiente`, `espontanea`, `espontnaea`, `estpotanea`, `esponatea` (misspellings) |
| `oxigenoterapia` | "Oxigenoterapia suplementar" | `mascara_facial_o2`, `tenda_o2_tqt`, `ventilacao_suporte_o2`, `cateter nasal de o2`, `mascara facial` |
| `vni` | "VM Não Invasiva" | `vm_nao_invasiva`, `vni`, `ventilacao_suporte_o2`('VNI'), `vni/ mascara facial` (was mis-mapped to spontaneous) |
| `vm_invasiva` | "VM Invasiva" | `vm_invasiva`, `ventilacao_mecanica_invasiva`, `assistida`, `controlada`, `ve pela tqt por mascara` (was mis-mapped) |
| `intermitente` | "Intermitente" | `intermitente` |
| `nao_informado` | "Não informado" | `''` (empty), null |

Legacy `assistida` / `controlada` (the latter labeled "Será desativado") collapse into `vm_invasiva`; the finer
assist/control distinction moves to `modalidade_ventilatoria`. The invasive/CPAP subset (`vm_invasiva`, `vni`) sets
`on_mechanical_ventilation_or_cpap` for the Berlin gate; `vm_invasiva` sets `on_mechanical_ventilation`.

### 6.2 `dispositivo_via_aerea` — airway device

| Canonical value | PT-BR label (verbatim) | Notes |
|---|---|---|
| `TOT` | "Tubo Orotraqueal" | orotracheal tube; gates prolonged-intubation timer (§3.5) |
| `TQT` | "Traqueostomia" | tracheostomy; excludes from the intubation timer |
| `DNI` | "Dispositivo Não Invasivo" | legacy labeled "Será desativado"; NIV interface/mask |

Legacy defect corrected (RULE-VENTILACAO-025): the invasive support value had been paired with the nasal-cannula label
`'Cateter Nasal de O2'` — that O₂ device now lives under `tipo_suporte_ventilatorio = oxigenoterapia`, not the airway
device enum.

### 6.3 `modalidade_ventilatoria` — ventilation modality

| Canonical value | PT-BR label (verbatim) | Notes |
|---|---|---|
| `PSV` | "PSV" | pressure support (spontaneous); weaning-relevant |
| `VCV` | "VCV" | volume-controlled |
| `PCV` | "PCV" | pressure-controlled |

The legacy C4 weaning branch compared the **`dispositivo`** field against uppercase `PCV`/`VCV` values that only exist in
**`modalidade`**, making the controlled-mode branch unreachable outside tests (RULE-VENTILACAO-007/-025). v2 evaluates
`modalidade_ventilatoria ∈ {VCV, PCV}` for controlled-mode logic and `PSV` for spontaneous-mode weaning.

---

## 7. RATIFY design points & open questions

Per CONTRACTS §Precedence and the escalations brief (SYS-C-03), **no P0/P1/UNVERIFIABLE rule is silently resolved.** Each
is built to a reference-anchored *recommended default* and flagged pending its RAT anchor (targets
`RATIFICATION.md#rat-ventilacao-NN`).

| RAT anchor | Rule / band | Dispute | **Recommended default (reference-anchored)** |
|---|---|---|---|
| **RAT-VENTILACAO-01** | RULE-VENTILACAO-002 (UNVERIFIABLE) | `days_on_mechanical_ventilation` primitive: `.days` truncation + `abs()` on future timestamps | Whole elapsed days from first VM record, no `abs()`; used by §3.4/§3.5 |
| **RAT-VENTILACAO-02** | RULE-VENTILACAO-003 (P1) | Lung-protective VT: absolute >500 mL vs weight-indexed | **VT >6 mL/kg PBW** (ARDSNet); PBW from altura+sex (Devine), not peso |
| **RAT-VENTILACAO-03** | RULE-VENTILACAO-004 (P1) | PEEP/FiO₂ table C2: dead `False and peep>0` guard + FiO₂ percent | Restore PEEP>0 guard; **FiO₂ fraction** (mission law) |
| **RAT-VENTILACAO-04** | RULE-VENTILACAO-005 (P1) | Severe PEEP/FiO₂ table C3: FiO₂ percent vs fraction | **FiO₂ fraction** (single canonical unit) |
| **RAT-VENTILACAO-05** | RULE-VENTILACAO-009 (P1) | COVID tracheostomy timing: code >10 d vs facade/guideline >14 d | **≥14 days** for active COVID-19 (AAO-HNS 2020) |
| **RAT-VENTILACAO-06** | RULE-VENTILACAO-011 (P0) | Extubation-readiness FiO₂ fraction/percent clash (alert-forcing) | **FiO₂ ≤0.40 fraction** (mission law); committee confirms the safety-critical bundle |

**Open questions.**
1. **OQ-1 — set/programmed RR parameter.** The registry has `frequencia_respiratoria` (rpm, spontaneous) but no distinct
   *set/programmed* RR parameter; the asynchrony logic (§3.3) needs both. The **unit is satisfied** (canonical `rpm`); I
   use `frequencia_respiratoria_programada` (unit rpm, mission canonical) and request the units/data-model guild add the
   parameter name to the registry.
2. **OQ-2 — `days_on_mechanical_ventilation` source.** Derived from the first VM record timestamp; pending
   RAT-VENTILACAO-01 for the truncation/sign correction and confirmation of the VM-start event source in AMH Gold.
3. **OQ-3 — plateau-pressure availability.** Vision §3.3 gives no plateau threshold for the ARDS severity alerts (only the
   asynchrony >30 cmH₂O cutoff, vision open question). ARDS staging therefore does **not** require plateau; the
   lung-protective companion uses plateau only when present.
4. **OQ-4 — S/F ↔ P/F equivalence caveat.** S/F overestimates oxygenation when SpO₂ >97% (Rice 2007); when an ABG is
   present, P/F is authoritative and overrides the S/F band. All S/F and P/F use **FiO₂ as a fraction**.
5. All units required exist in the registry (or, for OQ-1, the unit exists while the parameter name is requested).

---

```yaml domain-inputs
domain: respiratory
inputs:
  - {name: saturacao_o2, type: quantity, unit: "percent", source: "AMH Gold Observation LOINC 2708-6"}
  - {name: fio2, type: quantity, unit: "fraction", source: "AMH Gold Observation LOINC 19935-6 / ventilator OBX"}
  - {name: pao2, type: quantity, unit: "mmHg", source: "AMH Gold blood gas LOINC 2703-7"}
  - {name: paco2, type: quantity, unit: "mmHg", source: "AMH Gold blood gas LOINC 2019-8"}
  - {name: ph_arterial, type: quantity, unit: "pH", source: "AMH Gold blood gas LOINC 2744-1"}
  - {name: relacao_spo2_fio2, type: quantity, unit: "ratio", source: "derived = SpO2 / FiO2(fraction)"}
  - {name: relacao_pao2_fio2, type: quantity, unit: "ratio", source: "derived = PaO2 / FiO2(fraction)"}
  - {name: peep, type: quantity, unit: "cmH2O", source: "AMH Gold Observation LOINC 20077-4 / ventilator"}
  - {name: pressao_plato, type: quantity, unit: "cmH2O", source: "ventilator OBX (optional)"}
  - {name: pressao_inspiratoria, type: quantity, unit: "cmH2O", source: "ventilator OBX (optional)"}
  - {name: volume_corrente, type: quantity, unit: "mL", source: "ventilator OBX"}
  - {name: volume_corrente_pbw, type: quantity, unit: "mL/kg", source: "derived = VT / PBW(altura, sex)"}
  - {name: frequencia_respiratoria, type: quantity, unit: "rpm", source: "AMH Gold Observation LOINC 9279-1 (spontaneous)"}
  - {name: frequencia_respiratoria_programada, type: quantity, unit: "rpm", source: "ventilator OBX (set RR; see OQ-1)"}
  - {name: indice_respiracao_rapida_superficial, type: quantity, unit: "ratio", source: "derived = RR / VT(L) (RSBI)"}
  - {name: altura, type: quantity, unit: "cm", source: "AMH Gold Observation LOINC 8302-2"}
  - {name: peso, type: quantity, unit: "kg", source: "AMH Gold Observation LOINC 29463-7"}
  - {name: idade, type: quantity, unit: "years", source: "AMH Gold Patient"}
  - {name: rass, type: quantity, unit: "points", source: "sedacao domain, Observation LOINC 75826-6"}
  - {name: glasgow, type: quantity, unit: "points", source: "AMH Gold Observation LOINC 9269-2"}
  - {name: dose_vasopressor, type: quantity, unit: "mcg/kg/min", source: "hemodynamics domain (MedicationAdministration)"}
  - {name: tipo_suporte_ventilatorio, type: enum, unit: "enum", source: "ventilator / clinical form (see §6)"}
  - {name: dispositivo_via_aerea, type: enum, unit: "enum", source: "clinical form / EMR (see §6)"}
  - {name: modalidade_ventilatoria, type: enum, unit: "enum", source: "ventilator / clinical form (see §6)"}
  - {name: infiltrado_bilateral, type: boolean, unit: "boolean", source: "imaging DiagnosticReport (CXR/CT)"}
  - {name: edema_cardiogenico_excluido, type: boolean, unit: "boolean", source: "clinical assessment (Berlin qualifier)"}
  - {name: dpoc_risco_hipercapnia, type: boolean, unit: "boolean", source: "Condition (SNOMED, DPOC)"}
  - {name: covid19_ativo, type: boolean, unit: "boolean", source: "Condition (COVID-19)"}
  - {name: dias_em_ventilacao_mecanica, type: quantity, unit: "count", source: "derived (see OQ-2 / RAT-VENTILACAO-01)"}
alerts:
  - ALERT-RESP-ARDS-STAGING-01
  - ALERT-RESP-DETERIORATION-02
  - ALERT-RESP-ASYNCHRONY-03
  - ALERT-RESP-WEANING-READY-04
  - ALERT-RESP-PROLONGED-INTUB-05
rule_refs:
  - RULE-VENTILACAO-001
  - RULE-VENTILACAO-002
  - RULE-VENTILACAO-003
  - RULE-VENTILACAO-004
  - RULE-VENTILACAO-005
  - RULE-VENTILACAO-007
  - RULE-VENTILACAO-008
  - RULE-VENTILACAO-009
  - RULE-VENTILACAO-011
  - RULE-VENTILACAO-013
  - RULE-VENTILACAO-014
  - RULE-VENTILACAO-015
  - RULE-VENTILACAO-016
  - RULE-VENTILACAO-017
  - RULE-VENTILACAO-024
  - RULE-VENTILACAO-025
interfaces:
  emits_events:
    - respiratory.ards.staged
    - respiratory.deterioration.detected
    - respiratory.asynchrony.detected
    - respiratory.weaning.ready
    - respiratory.prolonged_intubation.flagged
  consumes:
    - {quantity: richmond_agitation_sedation_scale, unit: "points", source: "sedacao domain"}
    - {quantity: glasgow_coma_scale, unit: "points", source: "clinical-scoring / neuro"}
    - {quantity: weight_indexed_vasopressor_rate, unit: "mcg/kg/min", source: "hemodynamics domain"}
```
