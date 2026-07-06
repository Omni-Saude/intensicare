# Neuro-Sedation Domain — IntensiCare v2 Clinical Specification

**Guild:** Clinical (neuro-sedation domain designer) · **Vision ref:** §3.5 (Delirium / Sedação, priority P7) ·
**Platform:** AMH Data Platform consumer (ADR-001) · **Legacy cluster:** `sedacao` (27 rules, 3 coexisting
analgosedation pathway generations).

This document reconciles the legacy's three analgosedation implementations — **v3 automático** (wired production,
12-criterion), **v1 automático** (legacy/superseded), and the **manual** nurse-entered pathway — each with its own
criterion set and its own `VERMELHO/AMARELO/NEUTRO` aggregator (`RULE-SEDACAO-014`, `-023`, `-021`), into **one**
evidence-anchored **RASS / CAM-ICU / PADIS-aligned suite**: sedation-depth targeting, daily awakening (SAT) triggers,
delirium screening cadence, iatrogenic-delirium risk, propofol-infusion-syndrome surveillance, and controlled-pain
detection. Every threshold below cites a guideline/paper and/or a `RULE-SEDACAO-*` catalog ID. Disputed aggregation,
UNVERIFIABLE ml/h dosing, and P1/P2/P3 defects are designed to the reference-anchored **recommended default** and
marked **pending RAT-SEDACAO-\***; the ratification committee decides (CONTRACTS §Precedence; CON-SEED-08).

All outputs are advisory, physician-owned (VIS-C-01, VIS-C-08), recorded to the prontuário at NGS Level 2 (VIS-C-07).
No automatic diagnosis (VIS-C-01).

---

## 1. Clinical scope

**In scope.** Adult ICU (UTI) analgosedation and delirium management, per PADIS 2018 (Devlin 2018), the RASS
(Sessler 2002; Ely 2003), and CAM-ICU (Ely 2001):

1. **Sedation-depth targeting** — detect a patient sedated *deeper than target* (over-sedation, RASS < −3) without a
   documented deep-sedation indication, and detect *agitation* (RASS > +1) with device-removal / self-extubation risk.
2. **Daily awakening (SAT) / sedation-minimisation** — flag a mechanically ventilated patient who is a
   sedation-lightening candidate (adequate oxygenation, still on continuous sedative) and whose morning sedation was
   **not** reduced, and surface prolonged continuous sedation (>96 h) for withdrawal/tolerance surveillance.
3. **Delirium screening** — surface a **positive CAM-ICU**, and flag a **screening-cadence gap** (no CAM-ICU recorded
   for >24 h in an at-risk patient, with hypoactive-delirium suspicion).
4. **Iatrogenic-delirium risk** — continuous-infusion benzodiazepine in an elderly, sedated patient (PADIS
   "avoid benzodiazepines" recommendation).
5. **Propofol-infusion-syndrome (PRIS) surveillance** — prolonged high-exposure propofol with missing safety labs.
6. **Pain assessment** — uncontrolled pain by the validated dual scale (VISUAL / COMPORTAMENTAL-BPS), the analgesia
   ("A") pillar of PADIS analgosedation.

**Out of scope / delegated.**
- **Weight-based sedative *dosing* / overdose thresholds** — the legacy ml/h infusion-volume cutoffs
  (`RULE-SEDACAO-005/010/015`) have **no** published clinical anchor and are UNVERIFIABLE; they are **not** ported as
  firing thresholds (see §6, RAT-SEDACAO-01/03). A weight-based (mcg/kg/min or mg/kg/h) dosing model or the ml/h→dose
  conversion service (SYS-C-04) is required first; the units registry has no weight-indexed *sedative* dose parameter
  today (§7 open question).
- **Neuromuscular-blockade (BNM) management and ventilator weaning-readiness** → **respiratory** domain
  (`RULE-SEDACAO-004` weaning screen, `-007` NMBA-de-escalation target `clinical/domains/respiratory.md`); this domain
  only *consumes* BNM presence as a deep-sedation-indication context flag.
- **Drug-withdrawal syndrome on abrupt BZD/opioid discontinuation** (catalog DDX-005) → **drug-interactions** domain;
  this domain emits `neurosed.prolonged_sedation.flagged` which that domain consumes.
- **Early mobilisation** (vision VIS-3.5-06, TEAM Study NEJM 2022) — *not* in the existing DEL-\* catalog and a
  mobility/rehab concept; recorded as a **deferred** future alert (§7), not designed here.
- **RASS/SOFA-CNS aggregate scoring** → clinical-scoring domain (RASS is *consumed* here, not computed).

**Reconciliation summary (three pathways → one design).** The three aggregators disagree on criterion subset and
vote thresholds and none has a published anchor (`RULE-SEDACAO-014/021/023`, all NOT_APPLICABLE / verify:false). We
therefore **do not port any institutional aggregator verbatim.** The v2 suite is rebuilt on the *published* anchors —
the RASS target bands (Sessler 2002; PADIS 2018), CAM-ICU (Ely 2001), and the SAT/daily-interruption evidence (Kress
2000; Girard 2008) — carrying legacy criteria forward only where VERIFIED or corrected to the reference (§3). The
divergent aggregation is captured in the RATIFY table (§6, RAT-SEDACAO-05/09).

---

## 2. Typed, unit-checked inputs

Every input unit is the canonical from `_work/units/registry.yaml`. **RASS is a signed ordinal integer −5..+4**
(`rass`, points) — sign must never be coerced (P0-10 legacy discarded ±direction by reading the first char). FiO2 is
**fraction 0.21–1.0** at every predicate (mission law; SYS-01); a P/F ratio built from percent FiO2 is ~100× wrong.

| Input (PT-BR param) | Quantity | Unit (canonical) | Source | Staleness max |
|---|---|---|---|---|
| `rass` | richmond_agitation_sedation_scale | `points` (−5..+4) | AMH Gold Observation LOINC 75826-6 | PT4H |
| `cam_icu` | delirium_assessment | `enum {positivo,negativo,nao_avaliavel}` | Observation LOINC 8683-5/8684-3/8686-8 | PT12H |
| `escala_dor_numerica` | numeric_pain_scale | `points` (0–10) | Observation (EVA/VISUAL) | PT6H |
| `escala_dor_comportamental` | behavioral_pain_scale | `points` (3–12) | Observation (BPS/COMPORTAMENTAL) | PT6H |
| `idade` | age | `years` | Patient (MPI demographics) | static |
| `relacao_pao2_fio2` | pf_ratio | `ratio` | respiratory domain (FiO2 **fraction**!) | PT6H |
| `fio2` | inspired_oxygen_fraction | `fraction` | Observation LOINC 19935-6 | PT6H |
| `peep` | positive_end_expiratory_pressure | `cmH2O` | ventilator HL7 ORU | PT6H |
| `ventilacao_mecanica` | on_invasive_ventilation | `boolean` | Procedure / device presence | PT6H |
| `sedativo_continuo_presente` | continuous_sedative_present | `boolean` | MedicationAdministration (any of midazolam/propofol/cetamina/dexmedetomidina/fentanil) | PT4H |
| `benzodiazepinico_continuo` | continuous_benzodiazepine | `boolean` | MedicationAdministration (midazolam/diazepam/lorazepam) | PT4H |
| `propofol_continuo_gt_96h` | prolonged_propofol_flag | `boolean` | derived from MedicationAdministration start (>96 h continuous) | PT6H |
| `sedativo_continuo_gt_96h` | prolonged_sedation_flag | `boolean` | derived from MedicationAdministration start (>96 h continuous) | PT6H |
| `bloqueador_neuromuscular` | nmba_present | `boolean` | MedicationAdministration (rocuronium/cisatracurium) | PT6H |
| `indicacao_sedacao_profunda` | deep_sedation_indication | `boolean` | derived: SDRA grave OR ECMO OR BNM ativo OR hipertensão intracraniana OR estado de mal epiléptico | PT12H |
| `sedacao_paliativa` | palliative_sedation | `boolean` | care-plan flag (`diurna_sedoanalgesia_justificativas == "Sedacao paliativa"`) | PT24H |
| `reducao_sedacao_matinal_pct` | morning_sedation_reduction | `percent` | derived: (dose 06:00 − dose 10:00)/dose 06:00 | PT6H |
| `cpk_resultado_48h` | lab_result_present | `boolean` | lab_result presence (CPK) in 48 h | PT48H |
| `transaminases_resultado_48h` | lab_result_present | `boolean` | lab_result presence (TGO/AST + TGP/ALT) in 48 h | PT48H |
| `triglicerides_resultado_48h` | lab_result_present | `boolean` | lab_result presence (triglycerides) in 48 h | PT48H |
| `horas_desde_ultimo_cam_icu` | time_since_last_screen | `h` | derived from last CAM-ICU Observation timestamp | PT1H |

**Unit / correctness hazards carried from the audit (handled at the edge normalizer or upstream, never in clinical logic):**
- **RASS sign** — signed ordinal; a "deep-sedation" predicate must use the *inclusive lower band* `−5 ≤ rass ≤ −3`
  (SYS-06 / `RULE-SEDACAO-003`: legacy wrote `−3 ≤ x ≤ −5`, an unsatisfiable, always-False bound order).
- **Pain scales** — NRS capped at 10, BPS capped at 12; the severe band must be `low ≤ x ≤ high`, never the
  chained-comparison `7 <= dor > 10` misparse that silently suppresses the severe grade (SYS-06; catalog P0-04/05).
- **FiO2** — canonical fraction 0.21–1.0; `relacao_pao2_fio2` and `fio2` used in the SAT candidate logic are
  ~100× wrong if FiO2 arrives as percent (SYS-01; `RULE-SEDACAO-004/016`). Normalized upstream (respiratory domain).
- **Sedative dose (ml/h)** — **not** a clinical unit; the legacy overdose/weaning ml/h cutoffs are UNVERIFIABLE and
  are **not** consumed by any alert here (SYS-02; SYS-C-04; §6).
- **Comma-decimal / field-name legacy bugs** (`trigliceres` typo → inert PRIS leg, `RULE-SEDACAO-012`; `pins/peep/pf/fio2`
  bare-attribute reads, `RULE-SEDACAO-004`) are data-mapping fixes at ingest, not clinical logic changes.

---

## 3. Trigger / staging logic

Severity uses **only** `normal | watch | urgent | critical`. This is a low-acuity (P7) domain: the fleet PPV floor
(≥0.60) and ignored-rate ceiling (≤10%) are protected by (a) preferring **watch** over higher tiers, (b) requiring
**two consecutive assessments / sustained ≥4 h** for depth alerts, and (c) **gating on the absence of a documented
indication** so an intentionally deep-sedated patient never fires.

### 3.0 The RASS scale (legacy PT-BR enumeration preserved verbatim; verified against Sessler 2002)

The legacy numeric enumeration `[+4,+3,+2,+1,0,−1,−2,−3,−4,−5]` (cluster `rass_str_enum`) is adopted verbatim. The
descriptive Portuguese labels below are the Sessler-2002 validated scale (PADIS 2018 endorsed); institutional wording
should be confirmed against the legacy catalog string before build (§7).

| RASS | Termo (PT-BR) | Band used here |
|---|---|---|
| +4 | Combativo | **agitação** (AGITATION-02) |
| +3 | Muito agitado | **agitação** |
| +2 | Agitado | **agitação** |
| +1 | Inquieto / ansioso | limiar de agitação (> +1 fires) |
| 0 | Alerta e calmo | **alvo** (light-sedation target 0..−2) |
| −1 | Sonolento | **alvo** |
| −2 | Sedação leve | **alvo** |
| −3 | Sedação moderada | limiar de over-sedation (< −3 fires) |
| −4 | Sedação profunda | **over-sedation** (OVERSED-01) |
| −5 | Irresponsivo / não desperta | **over-sedation** |

**Light-sedation target = RASS 0 to −2** (PADIS 2018 weak-recommendation light sedation). Deep sedation
(`−5 ≤ rass ≤ −3`) is *off-target only when no deep-sedation indication is documented*.

### 3.1 Over-sedation off-target — `ALERT-NEUROSED-OVERSED-01` (severity: watch)

```
over_sedation :=
    ventilacao_mecanica
    AND (-5 <= rass AND rass <= -3)                 # inclusive band; RULE-SEDACAO-003 ADOPT-CORRECTED (fixes -3<=x<=-5 bound-order)
    AND NOT indicacao_sedacao_profunda              # no SDRA grave/ECMO/BNM/HIC/EME  (RULE-SEDACAO-016 ADOPT-CORRECTED)
    AND NOT sedacao_paliativa                        # RULE-SEDACAO-011 ADOPT-CORRECTED (fixes presence/absence inversion)
    sustained over >= 2 consecutive RASS assessments (>= PT4H)
```
Reconciles **DEL-001** (deep-sedation branch). `RULE-SEDACAO-016` corrected: strict **PEEP < 10 cmH2O** per its own
`_REGRAS` text (legacy drifted to `PEEP <= 10`) is used where a low-ventilatory-support qualifier is applied; here we
gate on *indication absence* rather than a PEEP cut to keep the alert simple and PPV-protective.

### 3.2 Agitation / device-removal risk — `ALERT-NEUROSED-AGITATION-02` (severity: urgent)

```
agitation :=
    rass > +1                                        # RASS +2..+4; Sessler 2002 agitation band
    sustained over >= 2 consecutive RASS assessments OR any single RASS >= +3
```
Split from **DEL-001** (agitation branch) and **promoted to urgent**: RASS ≥ +2 carries self-extubation /
device-removal risk (immediate bedside action), a materially different response than the watch-level over-sedation
half. A single RASS ≥ +3 (muito agitado/combativo) fires immediately without the sustained requirement.

### 3.3 SAT / sedation-minimisation — `ALERT-NEUROSED-SAT-03` (severity: watch)

```
sat_candidate_not_lightened :=
    ventilacao_mecanica
    AND sedativo_continuo_presente
    AND relacao_pao2_fio2 > 200                       # adequate oxygenation; RULE-SEDACAO-006/017 ADOPT (Berlin 2012 moderate-ARDS boundary)
    AND fio2 < 0.50                                   # RULE-SEDACAO-006 ADOPT (FiO2 fraction!)
    AND NOT indicacao_sedacao_profunda
    AND ( reducao_sedacao_matinal_pct < 50 percent    # morning sedation not reduced >=50%; recommended default pending RAT-SEDACAO-02
          OR sedativo_continuo_gt_96h )                # prolonged continuous sedation surveillance; RULE-SEDACAO-011 ADOPT-CORRECTED
    assessed once per morning window (06:00-10:00 local)
```
The daily-awakening evidence is Kress 2000 (daily sedation interruption) and Girard 2008 (ABC / SAT+SBT). The
**≥50 %** morning-reduction cut and its exact-half boundary come from `RULE-SEDACAO-009` (DISCREPANCY, P1) and are the
**recommended default pending RAT-SEDACAO-02**: `reducao_sedacao_matinal_pct < 50` flags failure; a reduction of
*exactly* 50 % counts as compliant (`>= 50%` passes), correcting the legacy operator-precedence bug. This alert also
absorbs the sedation-lightening-candidate concept (`RULE-SEDACAO-006/017`) and prolonged-sedation surveillance
(`RULE-SEDACAO-011`).

### 3.4 Delirium — CAM-ICU positivo — `ALERT-NEUROSED-DELIRIUM-04` (severity: urgent)

```
delirium_positive :=
    cam_icu == positivo                               # Ely 2001 (CAM-ICU): acute change/fluctuation + inattention + (RASS != 0 OR disorganized thinking)
```
Reconciles **DEL-002** (aligned). CAM-ICU is a validated instrument (Ely 2001), so a positive screen is a
high-PPV, directly actionable event (PADIS 2018 delirium bundle). Fires once per positive screen (deduped per
assessment).

### 3.5 Delirium screening-cadence gap / hypoactive suspicion — `ALERT-NEUROSED-SCREEN-GAP-05` (severity: watch)

```
screening_gap :=
    ventilacao_mecanica OR sedativo_continuo_presente   # at-risk population
    AND horas_desde_ultimo_cam_icu > 24 h               # no CAM-ICU in >24h
    AND (-3 <= rass AND rass <= -1)                      # RASS -1..-3, hypoactive-delirium suspicion window
    AND NOT sedativo_continuo_presente_ultimas_4h        # not explained by active sedation (DEL-004)
```
Reconciles **DEL-004** (extended: adds the explicit >24 h cadence clock to the vision's "no CAM-ICU record"
condition). Evidence: van den Boogaard 2014 (hypoactive delirium under-recognition); PADIS 2018 screening cadence.
PT-BR alert text (verbatim from DEL-004): *"Paciente com RASS reduzido sem sedativos. Considerar CAM-ICU para
delirium hipoativo."*

### 3.6 Iatrogenic-delirium risk — `ALERT-NEUROSED-IATRO-06` (severity: watch)

```
iatrogenic_delirium_risk :=
    benzodiazepinico_continuo
    AND idade > 65 years
    AND rass <= -2
    AND NOT indicacao_sedacao_profunda
```
Reconciles **DEL-003** (aligned). Evidence: PADIS 2018 (suggests non-benzodiazepine sedation — propofol or
dexmedetomidine — over benzodiazepines in mechanically ventilated adults to reduce delirium). Advisory suggests a
dexmedetomidine/propofol substitution; the *dosing* recommendation text is RATIFY-pending (RAT-SEDACAO-11).

### 3.7 Propofol-infusion-syndrome surveillance — `ALERT-NEUROSED-PRIS-07` (severity: watch)

```
pris_surveillance :=
    propofol_continuo_gt_96h                            # prolonged high-exposure propofol
    AND ( NOT cpk_resultado_48h
          OR NOT transaminases_resultado_48h
          OR NOT triglicerides_resultado_48h )          # a required safety lab missing in 48h
```
Reconciles nothing in the DEL-\* catalog (**new**). Evidence: Mirrakhimov 2015 (PRIS); PADIS 2018. Carries
`RULE-SEDACAO-012` (ADOPT) forward, fixing the `trigliceres` field-name typo that silently made the triglyceride leg
inert. This is a *safety-lab-gap* alert (prompts CPK / transaminases / triglycerides + lactate/pH review), not a PRIS
diagnosis.

### 3.8 Uncontrolled pain — `ALERT-NEUROSED-PAIN-08` (severity-scaling: watch → **urgent**)

```
uncontrolled_pain :=                                    # severity-scaling; output = worst band. PENDING SAFETY-OFFICER RE-CHECK (R2)
    MODERATE (watch):  (4 <= escala_dor_numerica <= 6) OR (7 <= escala_dor_comportamental <= 9)
    SEVERE   (urgent): (escala_dor_numerica >= 7)      OR (escala_dor_comportamental >= 10)   # NRS 7–10 / BPS 10–12
    both bands confirmed on TWO consecutive fluid-balance records   # two-consecutive-confirmation; RULE-SEDACAO-001/002
```
Reconciles nothing in the DEL-\* catalog (**new** — analgesia pillar). Evidence: PADIS 2018 pain-assessment standard;
Payen 2001 (BPS). Dual-scale bands carried verbatim from `RULE-SEDACAO-001` (moderate: VISUAL 4–6 / BPS 7–9) and
`RULE-SEDACAO-002` (severe: VISUAL 7–10 / BPS 10–12); both require the condition true on **two consecutive** balances
before firing (a built-in PPV protection). The severe band now emits a **distinct urgent escalation** (ack < 30 min;
scale maximums **NRS 10 / BPS 12 MUST fire it**) — restoring the escalation that was lost when severe pain was folded
into watch; moderate pain stays watch. Bands are `low ≤ x ≤ high`, never the `7 <= dor > 10` / `10 <= sinais > 12`
chained-comparison misparse that silently suppressed the severe grade (SYS-06 / P0-04 / P0-05). This reinstates the
domain's flagged *single genuine clinical loss* (severe uncontrolled pain) and is the conservative option adopted in
red-team round 1 — **pending safety-officer re-check (R2)**.

---

## 4. Evidence citations for every threshold

| Threshold | Value | Evidence (guideline/paper) | Legacy rule & disposition |
|---|---|---|---|
| Light-sedation target | RASS 0 to −2 | Devlin 2018 (PADIS); Sessler 2002 | — (target definition) |
| Deep sedation (off-target) | −5 ≤ RASS ≤ −3 | Sessler 2002; Devlin 2018 | RULE-SEDACAO-003 **ADOPT-CORRECTED** (bound-order −3≤x≤−5) |
| Deep-sed + low vent support qualifier | PEEP < 10 cmH2O | Sessler 2002; Devlin 2018 | RULE-SEDACAO-016 **ADOPT-CORRECTED** (legacy PEEP≤10) |
| Agitation | RASS > +1 (immediate at ≥ +3) | Sessler 2002; Ely 2003 | DEL-001 (catalog) — split/promoted |
| Sedation-lightening candidate (oxygenation) | P/F > 200, FiO2 < 0.50 | ARDS Definition Task Force 2012 (Berlin); Devlin 2018 | RULE-SEDACAO-006/017 **ADOPT** |
| SAT / daily interruption | morning reduction ≥ 50 % | Kress 2000; Girard 2008 (ABC) | RULE-SEDACAO-009 → **RAT-SEDACAO-02** (recommended default) |
| Prolonged sedation surveillance | continuous > 96 h | Devlin 2018 (tolerance/withdrawal) | RULE-SEDACAO-011 **ADOPT-CORRECTED** (presence/absence inversion) |
| CAM-ICU positive | positivo | Ely 2001 NEJM; Ely 2003 JAMA | DEL-002 (catalog) |
| Delirium screening cadence | CAM-ICU q ≤ 24 h; gap > 24 h | van den Boogaard 2014; Devlin 2018 | DEL-004 (catalog) |
| Hypoactive-delirium suspicion window | RASS −1 to −3, no active sedation | van den Boogaard 2014 | DEL-004 (catalog) |
| Iatrogenic-delirium risk | BZD infusion + age > 65 + RASS ≤ −2 | Devlin 2018 (PADIS, avoid BZD) | DEL-003 (catalog) |
| PRIS exposure | propofol continuous > 96 h | Mirrakhimov 2015; Devlin 2018 | RULE-SEDACAO-012 **ADOPT** (fixes `trigliceres` typo) |
| PRIS safety labs | CPK, TGO/TGP, triglycerides in 48 h | Mirrakhimov 2015 | RULE-SEDACAO-012 **ADOPT** |
| Pain — moderate (**watch**) | VISUAL 4–6 / BPS 7–9 (2 consecutive) → watch | Devlin 2018; Payen 2001 (BPS) | RULE-SEDACAO-001 **ADOPT** |
| Pain — severe (**urgent**, restored escalation, pending R2) | VISUAL 7–10 / BPS 10–12 (2 consecutive) → urgent | Devlin 2018; Payen 2001 | RULE-SEDACAO-002 **ADOPT** |
| NMBA-de-escalation (delegated → respiratory) | P/F > 150 + rocuronium/cisatracurium | Papazian 2010 (ACURASYS); Moss 2019 (ROSE) | RULE-SEDACAO-007 **ADOPT** (`respiratory.md`) |
| Overdose / high-dose (NOT ported) | ml/h infusion volume | none (UNVERIFIABLE) | RULE-SEDACAO-005/010/015 → **RAT-SEDACAO-01/03** |

---

## 5. Interactions with other domains

- **Neuro-sedation → drug-interactions.** Emits `neurosed.prolonged_sedation.flagged` (continuous BZD/opioid/propofol
  > 96 h or > 7 d); the **drug-interactions** domain consumes it for withdrawal-syndrome risk on abrupt
  discontinuation (catalog DDX-005) and synergistic CNS-depression (DDX-003).
- **Neuro-sedation ↔ respiratory.** Consumes `relacao_pao2_fio2` (FiO2 **fraction**) and `peep` from the respiratory
  domain for the SAT candidate logic; delegates BNM-de-escalation (`RULE-SEDACAO-007`) and ventilator
  weaning-readiness (`RULE-SEDACAO-004`) to it. Deep sedation is frequently *indicated* by severe ARDS/BNM —
  `indicacao_sedacao_profunda` is derived partly from respiratory state, so OVERSED-01 does **not** fire against an
  intentionally deep-sedated ARDS/ECMO patient.
- **Neuro-sedation ↔ clinical-scoring.** RASS is the SOFA-CNS / consciousness input shared cluster-wide; SOFA/GCS
  computation lives in clinical-scoring, RASS/CAM-ICU are consumed here.
- **Neuro-sedation → correlation engine.** Delirium-positive + sedation-depth events feed the correlation engine's
  delirium-risk reasoning (benzodiazepine exposure + hypoactive delirium). Not one of the three vision-named
  correlations (VIS-4-03), so this is an emit-only feed.
- **Platform / experience.** The three legacy aggregators and the manual Sedativo entry model (`RULE-SEDACAO-027`,
  RETIRE — Tasy-era per-drug uniqueness constraint) are replaced by the v2 alert-lifecycle + FHIR
  MedicationAdministration consumption (ADR-001 C-01/C-05). Alert acknowledgement is 1-click (CON-0091).

---

## 6. RATIFY design points (designed to recommended default; committee decides)

Per CONTRACTS §Precedence and CON-SEED-08, **no P1 / UNVERIFIABLE rule is silently resolved.** Each below is built to
a reference-anchored *recommended default* and flagged pending the named RAT anchor (`RATIFICATION.md`).

| RAT anchor | Rule(s) | Dispute | **Recommended default (reference-anchored)** |
|---|---|---|---|
| **RAT-SEDACAO-01** | RULE-SEDACAO-005 | Overdose ml/h cutoffs (midazolam≥15, propofol≥20…) — no anchor (UNVERIFIABLE) | **Do NOT port ml/h.** No overdose alert emitted until a weight-based (mcg/kg/min) model or the ml/h→dose conversion service (SYS-C-04) + a drug-concentration table exists. |
| **RAT-SEDACAO-02** | RULE-SEDACAO-009 | ≥50 % morning-reduction check; exact-half boundary (P1, operator-precedence bug) | **`reduction < 50 %` flags SAT failure; exactly 50 % is compliant (`≥50 %` passes).** Feeds SAT-03. |
| **RAT-SEDACAO-03** | RULE-SEDACAO-010 | High-dose NMBA ml/h cutoff — no anchor | **Delegated to respiratory; weight-based only.** Not consumed here. |
| **RAT-SEDACAO-04** | RULE-SEDACAO-013 | First-non-zero active-sedative priority label — no clinical basis | **Drop the priority-labeling mechanism**; per-drug context comes from FHIR MedicationAdministration directly. |
| **RAT-SEDACAO-05 / -09** | RULE-SEDACAO-014, -021, -023 | Which of 3 aggregators (v3/v1/manual) is canonical | **None verbatim.** Suite rebuilt on RASS/CAM-ICU/PADIS anchors (§3); v3/v1/manual vote schemes retired. |
| **RAT-SEDACAO-06** | RULE-SEDACAO-018 | Sedation-justified-by-severity composite (chained `0<ratio>=200` + EME/SHIC/PCR) — UNVERIFIABLE | **Use strict `P/F > 200`** per its own `_REGRAS`; the severity composite becomes the `indicacao_sedacao_profunda` gate, not a firing predicate. |
| **RAT-SEDACAO-07** | RULE-SEDACAO-019 | Poor-oxygenation-with-light/absent-sedation composite — UNVERIFIABLE | **Retain the concept as SAT-03 context**; do not emit as a standalone unvalidated composite. |
| **RAT-SEDACAO-08** | RULE-SEDACAO-020 | Severity-without-sedation; `_REGRAS` P/F<200 vs superseded `<150` | **Use Berlin `P/F < 200`** (current `_REGRAS`); discard the `<150` `_ANTIGAS_REGRAS`. |
| **RAT-SEDACAO-10** | RULE-SEDACAO-022 | "last 24h" = `timedelta.days == 0` (calendar-day) helper | **True rolling 24 h window** (`now − event ≤ PT24H`), not calendar-day. Applies to any 24 h lookback. |
| **RAT-SEDACAO-11** | RULE-SEDACAO-025 | Per-drug reduction/substitution recommendation free-text — proprietary | **Advisory text deferred**; IATRO-06 suggests "consider non-BZD (propofol/dexmedetomidine)" generically pending committee wording. |
| **RAT-SEDACAO-12** | RULE-SEDACAO-026 | Sedative enumeration + `Midazolan` display-label typo | **Store canonical keys `{fentanil,midazolam,propofol,cetamina,dexmedetomidina}`**; fix display label to "Midazolam"; source drug identity from FHIR, not a bespoke enum. |

**P0/systemic note.** No P0 rule falls in this cluster's *own* dispositions, but the shared FiO2 (SYS-01), vasopressor
(SYS-02), and weight-parse (SYS-09) hazards touch SAT-03's `relacao_pao2_fio2`/`fio2` inputs — all resolved by the
units registry canonicals (CON-SEED-12) and normalized upstream, never re-derived here.

---

## 7. Open questions

1. **RASS PT-BR word labels** (§3.0) — the cluster brief extracted only the numeric enumeration verbatim; the
   descriptive Portuguese terms are the Sessler-2002 validated scale. Confirm the exact institutional wording against
   the legacy catalog string before build to honour "preserve verbatim where adopted."
2. **Weight-indexed sedative-dose unit missing** — `_work/units/registry.yaml` has `dose_vasopressor` (mcg/kg/min,
   vasopressors only) and the `taxa_infusao`+`concentracao_farmaco`+`peso` conversion pattern, but **no** weight-based
   *sedative* dose parameter (midazolam/propofol/fentanyl mcg/kg/min or mg/kg/h). Required before RAT-SEDACAO-01/03 can
   yield a firing overdose alert. Mission canonical assumed: mcg/kg/min via the same conversion service.
3. **PRIS lab-value thresholds** — PRIS-07 currently checks only *presence* of CPK / transaminases / triglycerides
   (boolean). If the committee wants value thresholds (e.g. CPK, triglycerides), the units `U/L` (CPK) and `mg/dL`
   (triglycerides) must be added to the registry (not present today).
4. **Δ-baseline lookback** for `reducao_sedacao_matinal_pct` — assumes a fixed 06:00→10:00 local window; confirm the
   morning-window mechanics and the sedation-dose source field with the data-model guild (mirrors the sepsis
   Δ-lookback open question; vision open question).
5. **Early mobilisation** (VIS-3.5-06, TEAM 2022) is a deferred future alert, not in the DEL-\* catalog — confirm
   whether it belongs to neuro-sedation or a future mobility/rehab domain.
6. All non-boolean/non-derived units required by this domain **exist** in the registry; `boolean` and `h` primitives
   are used for presence flags and elapsed-time; no numeric clinical threshold uses a unit outside the registry.

---

```yaml domain-inputs
domain: neuro-sedation
inputs:
  - {name: rass, type: quantity, unit: "points", source: "AMH Gold Observation LOINC 75826-6 (RASS, signed -5..+4)"}
  - {name: cam_icu, type: enum, unit: "enum", source: "AMH Gold Observation LOINC 8683-5/8684-3/8686-8 (CAM-ICU)"}
  - {name: escala_dor_numerica, type: quantity, unit: "points", source: "AMH Gold Observation (EVA/VISUAL 0-10)"}
  - {name: escala_dor_comportamental, type: quantity, unit: "points", source: "AMH Gold Observation (BPS/COMPORTAMENTAL 3-12)"}
  - {name: idade, type: quantity, unit: "years", source: "MPI demographics (Patient)"}
  - {name: relacao_pao2_fio2, type: quantity, unit: "ratio", source: "respiratory domain (FiO2 fraction)"}
  - {name: fio2, type: quantity, unit: "fraction", source: "AMH Gold Observation LOINC 19935-6"}
  - {name: peep, type: quantity, unit: "cmH2O", source: "AMH Gold ventilator HL7 ORU"}
  - {name: ventilacao_mecanica, type: boolean, unit: "boolean", source: "Procedure / device presence"}
  - {name: sedativo_continuo_presente, type: boolean, unit: "boolean", source: "AMH Gold MedicationAdministration (sedatives)"}
  - {name: benzodiazepinico_continuo, type: boolean, unit: "boolean", source: "AMH Gold MedicationAdministration (BZD)"}
  - {name: propofol_continuo_gt_96h, type: boolean, unit: "boolean", source: "derived from MedicationAdministration start (>96h)"}
  - {name: sedativo_continuo_gt_96h, type: boolean, unit: "boolean", source: "derived from MedicationAdministration start (>96h)"}
  - {name: bloqueador_neuromuscular, type: boolean, unit: "boolean", source: "AMH Gold MedicationAdministration (rocuronium/cisatracurium)"}
  - {name: indicacao_sedacao_profunda, type: boolean, unit: "boolean", source: "derived (SDRA grave/ECMO/BNM/HIC/EME)"}
  - {name: sedacao_paliativa, type: boolean, unit: "boolean", source: "care-plan flag (diurna_sedoanalgesia_justificativas)"}
  - {name: reducao_sedacao_matinal_pct, type: quantity, unit: "percent", source: "derived (06:00-10:00 sedation dose delta)"}
  - {name: cpk_resultado_48h, type: boolean, unit: "boolean", source: "AMH Gold lab_result presence (CPK)"}
  - {name: transaminases_resultado_48h, type: boolean, unit: "boolean", source: "AMH Gold lab_result presence (TGO/TGP)"}
  - {name: triglicerides_resultado_48h, type: boolean, unit: "boolean", source: "AMH Gold lab_result presence (triglycerides)"}
  - {name: horas_desde_ultimo_cam_icu, type: quantity, unit: "h", source: "derived from last CAM-ICU Observation timestamp"}
alerts:
  - ALERT-NEUROSED-OVERSED-01
  - ALERT-NEUROSED-AGITATION-02
  - ALERT-NEUROSED-SAT-03
  - ALERT-NEUROSED-DELIRIUM-04
  - ALERT-NEUROSED-SCREEN-GAP-05
  - ALERT-NEUROSED-IATRO-06
  - ALERT-NEUROSED-PRIS-07
  - ALERT-NEUROSED-PAIN-08
rule_refs:
  - RULE-SEDACAO-001
  - RULE-SEDACAO-002
  - RULE-SEDACAO-003
  - RULE-SEDACAO-004
  - RULE-SEDACAO-005
  - RULE-SEDACAO-006
  - RULE-SEDACAO-007
  - RULE-SEDACAO-008
  - RULE-SEDACAO-009
  - RULE-SEDACAO-010
  - RULE-SEDACAO-011
  - RULE-SEDACAO-012
  - RULE-SEDACAO-013
  - RULE-SEDACAO-014
  - RULE-SEDACAO-015
  - RULE-SEDACAO-016
  - RULE-SEDACAO-017
  - RULE-SEDACAO-018
  - RULE-SEDACAO-019
  - RULE-SEDACAO-020
  - RULE-SEDACAO-021
  - RULE-SEDACAO-022
  - RULE-SEDACAO-023
  - RULE-SEDACAO-024
  - RULE-SEDACAO-025
  - RULE-SEDACAO-026
  - RULE-SEDACAO-027
interfaces:
  emits_events:
    - neurosed.sedation.off_target
    - neurosed.agitation.detected
    - neurosed.sat.not_lightened
    - neurosed.delirium.positive
    - neurosed.delirium.screening_gap
    - neurosed.iatrogenic_delirium.risk
    - neurosed.pris.surveillance
    - neurosed.prolonged_sedation.flagged
  consumes:
    - {quantity: pf_ratio, unit: "ratio", source: "respiratory domain"}
    - {quantity: inspired_oxygen_fraction, unit: "fraction", source: "respiratory domain / Observation"}
    - {quantity: positive_end_expiratory_pressure, unit: "cmH2O", source: "respiratory domain / ventilator"}
```
