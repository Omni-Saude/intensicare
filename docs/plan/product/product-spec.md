# IntensiCare v2 — Product Specification

Deliverable of the clinical-ux-researcher (product layer). Prose is English; PT-BR clinical
vocabulary from the source briefs is preserved verbatim, accents included.

Inputs (authority order per CONTRACTS.md §General-5): `_work/briefs/design-adrs.json` (audit),
`_work/briefs/vision.json`, `_work/briefs/personas.json`, `_work/briefs/implementation-plan.json`,
`_work/briefs/existing-alert-catalog.json` (vision lineage), `_work/constraints/ledger.yaml` (skim).
Conflicts are recorded in §6, never silently resolved.

ID conventions:
- Persona criteria `PER-<NAME>-NN` — the 12 ids from personas.json are load-bearing and reused verbatim.
- User stories `US-NN` — US-01..US-12 keep the MoSCoW ids from implementation-plan.md §2.2 verbatim;
  US-13+ extend the set.
- Metrics reference persona-criterion ids and vision metric ids (`VIS-7.1-NN`, `VIS-7.2-NN`).
- Existing alert ids (`SEP-*`, `AKI-*`, `RESP-*`, `HEMO-*`, `DEL-*`, `ELY-*`, `DDX-*`) come from
  docs/clinical/alert-catalog.md v1.0.0 and must be reconciled per CON-SEED-10.

---

## 1. Personas × jobs-to-be-done

Four personas (personas.json). Severity vocabulary note: the existing catalog uses CRIT/URG/WARN/INFO
with action SLAs (CAT-C-02..05: CRIT < 5 min, URG < 30 min, WARN < 2 h, INFO < 6 h); the new platform's
canonical scale is `normal | watch | urgent | critical` (CONTRACTS alert schema). The mapping between
the scales is owned by alert-engine-architect + design-token-systems-designer (CON-SEED-11) — this spec
cites both without resolving.

### 1.1 PER-CARLOS — Dr. Carlos, Médico Intensivista

12-year intensivist, 20-bed adult ICU (Hospital AUSTA); 60% procedures / 40% patient review. Arrives
7h, reviews critical patients, joins the 8h multidisciplinary round, responds to deterioration alerts
between procedures, covers remote calls at night. Today he receives ~200 alerts/day with ~80% false
positives (personas.json needs_2l).

Jobs-to-be-done:
- **JTBD-CARLOS-1** — When I arrive or between procedures, I need to know *which of my 20 patients is
  deteriorating right now*, without hand-calculated scores arriving hours late.
  → US-02, US-03, US-06, US-07, US-13..US-20 · PER-CARLOS-01, PER-CARLOS-02
- **JTBD-CARLOS-2** — When an alert interrupts a procedure, I need to judge in seconds whether it is
  real and what drove it, so interruptions are worth their cost.
  → US-04, US-21, US-22 · PER-CARLOS-02, PER-ANA-02
- **JTBD-CARLOS-3** — When reviewing a patient at the bedside, I need the 24h score/vitals trajectory,
  not point values. → US-10, US-24 · PER-CARLOS-03
- **JTBD-CARLOS-4** — When a score is elevated, I want evidence-based next-step context so the time
  from alert to action shrinks. → US-11 · VIS-7.1-03

### 1.2 PER-ANA — Enf. Ana, Enfermeira de UTI

8-year ICU nurse, 4–5 patients per 12h shift; today collects vitals every 2h, manually calculates and
charts MEWS (~20 min/shift per patient), escalates when high, documents interventions.

Jobs-to-be-done:
- **JTBD-ANA-1** — Eliminate manual score calculation entirely; vitals I collect should become scores
  automatically. → US-01, US-02, US-07 · PER-ANA-01
- **JTBD-ANA-2** — When an alert fires, show me *exactly which parameter* triggered it (FR? SpO2? PA?)
  so I check the right thing first. → US-04, US-21 · PER-ANA-02
- **JTBD-ANA-3** — Let me record my response to an alert in one click, mid-care, without a form maze.
  → US-05, US-12, US-22 · PER-ANA-03
- **JTBD-ANA-4** — At shift change, hand over a faithful picture of each patient's last 12–24h
  (scores, alerts, what was done). → US-24 · PER-CARLOS-03, PER-ANA-03

### 1.3 PER-FERNANDA — Dra. Fernanda, Coordenadora de UTI

Medical coordinator over 30 beds (adult, coronary, neonatal ICUs); reports quality metrics to clinical
direction; manages bed allocation, discharges, admissions, transfers.

Jobs-to-be-done:
- **JTBD-FERNANDA-1** — See real-time occupancy and acuity across all units at a glance.
  → US-06, US-09 · PER-FERNANDA-01
- **JTBD-FERNANDA-2** — Track alert response time and alert burden as quality indicators, weekly.
  → US-09, US-23, US-29 · PER-FERNANDA-02, VIS-7.1-03, VIS-7.1-04
- **JTBD-FERNANDA-3** — Justify capacity/investment decisions with data, not perception; export to
  hospital quality tools. → US-30 · PER-FERNANDA-03
- **JTBD-FERNANDA-4** — Govern alert thresholds: detect a noisy alert type, tune it safely, prove the
  change was authorized and versioned. → US-25, US-26 · PER-CARLOS-02, VIS-7.2-05

### 1.4 PER-RAFAEL — Dr. Rafael, Equipe de Resposta Rápida (RRT)

RRT physician answering acute-deterioration calls anywhere in the hospital; carries a corporate
smartphone. Flow: receives critical-score notification, reviews patient data while moving, attends and
stabilizes, documents desfecho (melhorou, transferido para UTI, etc.).

Jobs-to-be-done:
- **JTBD-RAFAEL-1** — Be paged within seconds of a critical score, with score, trend and patient
  location on the lock screen. → US-08 · PER-RAFAEL-01
- **JTBD-RAFAEL-2** — While en route, load the patient's latest vitals + trend on mobile so I arrive
  oriented. → US-27 · PER-RAFAEL-02
- **JTBD-RAFAEL-3** — Document the desfecho in under a minute and get back in service.
  → US-28 · PER-RAFAEL-03

---

## 2. User stories (MoSCoW)

US-01..US-12 are reproduced from implementation-plan.md §2.2 with ids, MoSCoW class and original
acceptance criteria verbatim (IMP-2.2-01..12); this spec adds supplementary acceptance criteria (AC)
and persona-criteria mappings. US-13..US-30 extend the set for Phase-2 alert domains, correlation
explanations, alarm-fatigue analytics, handoff summaries, threshold governance, and RRT mobile flows.

### 2.1 MUST — Fase 1 (MVP)

**US-01 (MUST, Fase 1)** — As Enf. Ana, I want sinais vitais ingested automatically via HL7 v2 so that
manual score calculation is eliminated. *(IMP-2.2-01)*
- AC1 (verbatim): mensagens HL7 ORU-R01 com vitais são parseadas e armazenadas em <5s após recebimento.
- AC2: ingestion is idempotent on `MSH-10` (IMP-C-02) — replayed messages never create duplicate vitals
  or duplicate alerts.
- AC3: every stored vital carries recorded-at and ingested-at timestamps so downstream latency
  (PER-CARLOS-01, VIS-7.2-01) is measurable.
- Persona criteria: **PER-ANA-01**. Metrics: PER-CARLOS-01 (feeds), VIS-7.2-01.

**US-02 (MUST, Fase 1)** — As Dr. Carlos, I want the MEWS of each patient calculated in real time.
*(IMP-2.2-02)*
- AC1 (verbatim): MEWS disponível em <30s após ingestão dos vitais, tela mostra score + tendência.
- AC2: 100% of scores are system-computed and stamped with `algorithm_version` (IMP-C-03); there is no
  manual score-entry path (PER-C-03).
- AC3: score latency (vitals collection → score available) is emitted as telemetry per computation.
- Persona criteria: **PER-CARLOS-01, PER-ANA-01**. Metrics: PER-CARLOS-01, VIS-7.2-01.

**US-03 (MUST, Fase 1)** — As Dr. Carlos, I want alerts when MEWS ≥ 5 (urgente) or ≥ 7 (crítico).
*(IMP-2.2-03)*
- AC1 (verbatim): alerta gerado em <5s após score exceder threshold, notificação no dashboard.
- AC2: alert severity follows the canonical clinical scale; the MEWS ≥5/≥7 tiers map to it explicitly
  (CON-SEED-11 owns the mapping).
- AC3: every alert is registered in the prontuário at NGS Level 2 (VIS-C-07) and is advisory only —
  no automatic diagnosis or treatment decision (VIS-C-01, VIS-C-08).
- AC4: suppression/dedup is defined per alert (CONTRACTS suppression block) so repeated threshold
  crossings do not multiply notifications.
- Persona criteria: **PER-CARLOS-02**. Metrics: PER-CARLOS-02, VIS-7.1-02, VIS-7.1-04.

**US-04 (MUST, Fase 1)** — As Enf. Ana, I want to see which parameters contributed to the elevated
score. *(IMP-2.2-04)*
- AC1 (verbatim): tela de detalhes do score mostra componentes individuais (FR, SpO2, PA, etc.).
- AC2: each component shows measured value + unit + points contributed, so "qual parâmetro disparou"
  is answerable at a glance (PER-C-04).
- AC3: abnormal components are visually distinguished using the shared clinical severity scale — never
  a neutral row for SpO2 60% (design gap ADR-0014 must not recur).
- Persona criteria: **PER-ANA-02**. Metrics: PER-ANA-02.

**US-05 (MUST, Fase 1)** — As Dr. Carlos, I want to acknowledge (reconhecer) an alert to signal I am
handling it. *(IMP-2.2-05)*
- AC1 (verbatim): botão "Reconhecer" no alerta registra timestamp + usuário.
- AC2: acknowledgment writes an append-only audit_trail record (IMP-C-01) and is visible to the whole
  team in real time on every surface showing that alert (ADR-C-13).
- AC3: acknowledgment is one interaction from the alert surface (foundation for PER-ANA-03).
- Persona criteria: **PER-ANA-03**. Metrics: VIS-7.1-03, VIS-7.1-04.

**US-06 (MUST, Fase 1)** — As Dra. Fernanda, I want the painel de leitos da UTI with scores and alert
status. *(IMP-2.2-06)*
- AC1 (verbatim): grid de leitos mostrando nome, score, status do alerta, tempo desde último vital.
- AC2: "tempo desde último vital" is a first-class staleness indicator on every bed card — silence must
  be distinguishable from normality (ADR-0017 gap).
- AC3: board alert state arrives on the same push channel/latency class as notifications, so bell and
  grid never visibly disagree (ADR-C-13).
- Persona criteria: **PER-FERNANDA-01**. Metrics: PER-FERNANDA-01.

### 2.2 SHOULD — Fase 2 (original set)

**US-07 (SHOULD, Fase 2)** — As Dr. Carlos, I want SOFA and NEWS2 scores in addition to MEWS
(including the NEWS2 hypercapnic Scale 2 variant, VIS-2-02). *(IMP-2.2-07)*
- AC1: SOFA (daily organ dysfunction) and NEWS2 computed automatically with the same latency and
  versioning guarantees as MEWS (PER-CARLOS-01, IMP-C-03).
- AC2: score detail view shows per-component breakdown (as US-04) for each score type.
- Persona criteria: **PER-ANA-01, PER-CARLOS-01**. Metrics: PER-CARLOS-01.

**US-08 (SHOULD, Fase 2)** — As Dr. Rafael (RRT), I want critical alerts on my smartphone.
*(IMP-2.2-08)*
- AC1: push notification delivered in <5 seconds after a critical score (PER-RAFAEL-01); delivery uses
  retry with backoff (IMP-C-06) and emits delivery receipts for latency measurement.
- AC2: the notification carries score, trend direction, and patient location (persona needs_2l).
- AC3: tapping opens the mobile patient screen (US-27) directly.
- Persona criteria: **PER-RAFAEL-01, PER-RAFAEL-02**. Metrics: PER-RAFAEL-01.

**US-09 (SHOULD, Fase 2)** — As Dra. Fernanda, I want a metrics dashboard (tempo de resposta, taxa de
alertas). *(IMP-2.2-09)*
- AC1: dashboard shows tempo médio até ação clínica pós-alerta (VIS-7.1-03) and alert burden
  (alertas/paciente/dia) per unit, with trend over time.
- AC2: real-time occupancy/acuity view across the coordinator's units (PER-FERNANDA-01).
- Persona criteria: **PER-FERNANDA-01, PER-FERNANDA-02**. Metrics: VIS-7.1-03, VIS-7.1-04.

**US-10 (SHOULD, Fase 2)** — As Dr. Carlos, I want the score trend of the last 24h as a chart.
*(IMP-2.2-10)*
- AC1: 24h trend chart (gráfico 24h) per patient for each score type, with alert markers overlaid.
- AC2: chart renders from the bedside/board detail in one navigation step.
- Persona criteria: **PER-CARLOS-03**. Metrics: PER-CARLOS-03.

### 2.3 COULD — Fase 3 (original set)

**US-11 (COULD, Fase 3)** — As Dr. Carlos, I want evidence-based suggestions for elevated scores.
*(IMP-2.2-11)*
- AC1: suggestions cite their published evidence (guideline/paper), consistent with the zero-silent-
  invention rule; the physician remains responsible for the final decision (VIS-C-08).
- AC2: suggestions are advisory content only — never auto-ordered actions (VIS-C-01).
- Persona criteria: **PER-ANA-02** (explanation/transparency family). Metrics: VIS-7.1-03.

**US-12 (COULD, Fase 3)** — As Enf. Ana, I want to document the action taken after an alert in 1
click. *(IMP-2.2-12)*
- AC1: from the alert surface, a predefined action set is loggable in a single interaction; the record
  captures user, timestamp, action (audit_trail, IMP-C-01).
- AC2: logged actions feed VIS-7.1-03 (time-to-action) measurement.
- Persona criteria: **PER-ANA-03**. Metrics: PER-ANA-03, VIS-7.1-03.

### 2.4 Extension — Phase-2 alert domains (US-13..US-19)

Rollout follows vision §5.2: Fase 2a (Meses 1-3) Sepse + AKI + Eletrólitos; Fase 2b (Meses 4-6)
Hemodinâmica + Respiratória; Fase 2c (Meses 7-9) Interações Medicamentosas + Delirium; Fase 2d
(Meses 10-12) Correlation Engine + ML preditivo (the ML part is WON'T for this plan, §4). All domain
stories inherit the cross-cutting ACs: parameter-level explanation (US-21), prontuário registration
(VIS-C-07), suppression budgets, and reconciliation of the 32 existing alert ids (CON-SEED-10).

**US-13 (SHOULD, Fase 2a)** — As Dr. Carlos, I want sepsis screening alerts so that sepsis is detected
early enough to change outcomes (sepsis is the #1 cause of death in Brazilian ICUs; detection <1h
reduces mortality 25-30%, VIS-3.1-01).
- AC1: 'SIRS + suspeita de infecção' fires on ≥2 SIRS criteria + infection suspicion per SEP-001 logic
  (CAT-SEP-001; VIS-3.1-02).
- AC2: 'qSOFA ≥2 com tendência de lactato' fires on qSOFA ≥2 AND (lactato > 2 mmol/L OR delta > 0.5
  mmol/L/h) per SEP-002 (VIS-3.1-03); lactato ≥ 4.0 mmol/L + MAP < 65 mmHg elevates to crítico with
  flag 'choque séptico iminente' (CAT-SEP-002, VIS-3.1-04).
- AC3: 'Procalcitonina em elevação' and 'Desmame antimicrobiano' guidance per SEP-003a/b (VIS-3.1-05,
  VIS-3.1-06).
- AC4: each alert names the exact criteria met (which SIRS/qSOFA components, lactato values with
  timestamps) — PER-ANA-02 at domain level.
- AC5: known limitations from the catalog (SIRS low specificity; qSOFA false-negatives under
  β-bloqueadores/immunosuppression) are surfaced in the alert detail as context, not suppressed.
- Persona criteria: **PER-CARLOS-02, PER-ANA-02**. Metrics: VIS-7.1-01, VIS-6.1-02 (time-to-antibiotic
  −60 min goal), VIS-7.1-02.

**US-14 (SHOULD, Fase 2a)** — As Dr. Carlos, I want AKI KDIGO staging alerts so that AKI is recognized
at reversible stages (AKI in 30-60% of ICU patients, 6.5× mortality, VIS-3.2-01).
- AC1: 'KDIGO Estágio 1/2/3' alerts per CAT-AKI-001..003 thresholds (creatinina and diurese criteria,
  incl. anúria ≥12h and TRS initiation for stage 3).
- AC2: creatinina basal is computed as the catalog defines (menor valor 3 meses/admissão, lookback
  90d) and shown alongside the alert so the ratio is verifiable.
- AC3: 'Progressão AKI' fires on stage change within 24h (CAT-AKI-004, VIS-3.2-05).
- AC4: 'Risco de AKI por nefrotoxicidade aditiva' per CAT-AKI-005 combinations.
- AC5: the alert states which criterion fired (Cr-based vs diurese-based) with values and units.
- Persona criteria: **PER-CARLOS-02, PER-ANA-02**. Metrics: VIS-6.1-02 (AKI recognition −6h goal),
  VIS-7.1-02.

**US-15 (SHOULD, Fase 2a)** — As Enf. Ana and Dr. Carlos, I want critical electrolyte alerts so that
potentially fatal K+/Na+/Ca2+/Mg2+ disturbances are acted on within minutes (VIS-3.6-01).
- AC1: tiered alerts per ELY-001..006 (e.g. 'Hipercalemia grave' crítico K+ > 6.5 mmol/L, urgente
  > 6.0; 'Hiponatremia grave' crítico Na+ < 120 mmol/L; full tier tables per CAT-ELY-001..006,
  VIS-3.6-02..09).
- AC2: 'Delta Na⁺ perigoso' safety alert (ALERTA DE SEGURANÇA) when correction > 10 mmol/L in 24h —
  correction must not exceed 8-10 mmol/L/24h (CAT-C-01, VIS-3.6-06).
- AC3: alerts fire on lab-result arrival (on result) within the alert-latency SLO; crítico-tier
  electrolyte alerts demand action <5 min (CAT-C-02).
- AC4: context lines (ECG/QTc, medicamentos hipercalemiantes) shown when the trigger uses them.
- Persona criteria: **PER-CARLOS-02, PER-ANA-02**. Metrics: VIS-6.1-02 (arrest reduction 50% goal),
  VIS-7.1-02.

**US-16 (SHOULD, Fase 2b)** — As Dr. Carlos, I want hemodynamic instability alerts so that occult
hypoperfusion and refractory shock are caught before collapse (unrecognized shock mortality > 80%,
VIS-3.4-01).
- AC1: 'Shock Index elevado' HR/SBP > 0.9 and modified SI HR/MAP > 1.3, both sustained > 15 min
  (CAT-HEMO-001, VIS-3.4-02/03).
- AC2: 'Clearance de lactato inadequado' < 10% in 2h or lactato > 2 mmol/L after 6h resuscitation
  (CAT-HEMO-002, VIS-3.4-04).
- AC3: 'Escalonamento de vasopressor' per CAT-HEMO-003a/b/c incl. choque refratário (noradrenalina
  > 1.0 μg/kg/min AND MAP < 65 mmHg > 30 min).
- AC4: fluid-responsiveness alert (CAT-HEMO-004) degrades gracefully when PPV/SVV monitors are absent
  (data availability Baixa, DATA-AVAIL-09) — the alternative trigger path is used and labeled.
- AC5: vasopressor doses displayed in mcg/kg/min with conversion provenance (CON-SEED-12).
- Persona criteria: **PER-CARLOS-02**. Metrics: VIS-7.1-02, VIS-7.1-03.

**US-17 (SHOULD, Fase 2b)** — As Dr. Carlos, I want respiratory deterioration alerts so that SDRA and
ventilatory decline are graded and trended without waiting for gasometria (VIS-3.3-01).
- AC1: SDRA severity alerts on SpO₂/FiO₂ ≤ 315 / ≤ 235 / ≤ 148 with PaO2/FiO2 confirmation when ABG
  available (CAT-RESP-001/002, VIS-3.3-02..04), including the SpO2 > 97% overestimation caveat.
- AC2: 'Deterioração ventilatória' on >20% SpO2/FiO2 drop in 6h or >30% FiO2 increase (CAT-RESP-003,
  VIS-3.3-05).
- AC3: 'Prontidão para desmame' (INFO-class) when all CAT-RESP-004 criteria sustained ≥2h.
- AC4: FiO2 handled as fraction 0-1 at every computation boundary; percent is display-only
  (CON-SEED-12).
- Persona criteria: **PER-CARLOS-02**. Metrics: VIS-7.1-02, VIS-7.1-03.

**US-18 (SHOULD, Fase 2c)** — As Dr. Carlos, I want drug-interaction alerts so that the 5-10% of ICU
adverse events from serious interactions are intercepted (VIS-3.7-01).
- AC1: 'QTc prolongamento — risco de Torsades' per DDX-001 (QTc > 500 ms + ≥2 CredibleMeds drugs;
  WARN variants with K+/Mg2+ context and delta QTc > 60 ms).
- AC2: 'Síndrome serotoninérgica' per DDX-002; 'Depressão respiratória sinérgica' per DDX-003
  (≥2 CNS depressants + RR < 10 or SpO2 < 90%).
- AC3: 'Duplicidade terapêutica' per DDX-004; 'Síndrome de abstinência' per DDX-005; 'Antimicrobiano
  sem ajuste renal' per DDX-006 (CrCl < 30 mL/min).
- AC4: every drug alert lists the offending medication pair/set by name with start dates.
- AC5: dependency on complete medication data (availability Média/Baixa, DATA-AVAIL-06/07) is
  explicit: alerts state data coverage when it is partial.
- Persona criteria: **PER-CARLOS-02, PER-ANA-02**. Metrics: VIS-7.1-02.

**US-19 (SHOULD, Fase 2c)** — As Enf. Ana and Dr. Carlos, I want delirium and sedation alerts so that
delirium (50-80% of ventilated patients, 3× mortality, VIS-3.5-01) is screened and acted on.
- AC1: 'RASS alvo fora da faixa' per DEL-001 (RASS > +1 or < −3 sem indicação de sedação profunda,
  sustained ≥2 consecutive assessments).
- AC2: 'Delirium — CAM-ICU positivo' per DEL-002 feature logic; 'Risco de delirium iatrogênico' per
  DEL-003; 'Delirium hipoativo possivelmente não reconhecido' per DEL-004 with its prompt text
  ('Considerar CAM-ICU para delirium hipoativo').
- AC3: because structured RASS/CAM-ICU availability is Baixa (DATA-AVAIL-08), the product provides
  structured capture of RASS/CAM-ICU at the bedside as part of this story — alerts must not depend on
  free-text parsing.
- AC4: 'Mobilização inadequada' reminder per VIS-3.5-06 (>24h without mobilization record in an
  eligible patient).
- Persona criteria: **PER-ANA-02, PER-CARLOS-02**. Metrics: VIS-7.1-02, VIS-7.1-04.

### 2.5 Extension — correlation, explainability, alarm fatigue, handoff, governance, RRT, coordinator (US-20..US-30)

**US-20 (SHOULD, Fase 2d)** — As Dr. Carlos, I want cross-domain correlated insights instead of
parallel alarms, so that related deterioration reads as one clinical story.
- AC1: exactly the three vision-defined correlations are implemented first: (1) Sepse + AKI ('sepse é
  #1 causa de AKI'); (2) Respiratória + Hemodinâmica ('SDRA + choque'); (3) Drogas + Eletrólitos
  ('QTc + K+/Mg2+') (VIS-4-03).
- AC2: when a correlation is active, constituent alerts group into a single correlated insight with
  one notification stream; individual alerts remain inspectable inside it.
- AC3: the correlated insight explains the link (which alerts, which shared signals, time relation) —
  correlation without explanation is not shippable.
- AC4: grouping demonstrably reduces notification count vs. ungrouped baseline in replay tests.
- Persona criteria: **PER-CARLOS-02, PER-ANA-02**. Metrics: VIS-7.1-02, VIS-7.1-04, PER-CARLOS-02.

**US-21 (MUST for every alert domain it ships with, Fase 2a onward)** — As Enf. Ana, I want every
alert to expose *why it fired*, so that I never have to reverse-engineer an alarm.
- AC1: every alert record carries a structured trigger payload: parameter name(s), measured value(s)
  with unit, threshold crossed, observation window, staleness of each input (CONTRACTS alert schema).
- AC2: the alert detail renders this payload plus the evidence citation (guideline/paper) and
  `algorithm_version` — auditable end to end (IMP-C-03, VIS-7.2-05).
- AC3: 100% of fired alerts pass a "non-empty explanation" gate; an alert with an empty trigger
  payload is a build/test failure.
- AC4: explanation is readable at bedside in ≤ 2 taps/clicks from any alert surface.
- Persona criteria: **PER-ANA-02**. Metrics: PER-ANA-02, VIS-7.1-03.

**US-22 (SHOULD, Fase 2a onward)** — As Dr. Carlos or Enf. Ana, I want to mark an alert's disposition
(procede / não procede) in one click, so that false positives are captured at the moment of judgment.
- AC1: disposition capture is one interaction from the alert surface (PER-ANA-03 pattern), recording
  user, timestamp, disposition in the append-only audit trail (IMP-C-01).
- AC2: dispositions feed PPV (VIS-7.1-02) and FP/patient-day (PER-CARLOS-02) computation per alert
  type — this is the instrumentation backbone of the before-after study secondary outcomes
  (VIS-6.1-03).
- AC3: a 'não procede' disposition never silently disables an alert type — it only feeds analytics
  and the governance queue (US-25).
- Persona criteria: **PER-ANA-03, PER-CARLOS-02**. Metrics: VIS-7.1-02, PER-CARLOS-02.

**US-23 (SHOULD, Fase 2b)** — As Dra. Fernanda, I want alarm-fatigue analytics, so that alert noise is
managed as a quality metric, not an anecdote.
- AC1: per unit and per alert type: PPV (confirmed dispositions / total), taxa de alarm fatigue
  (alertas ignorados / total, VIS-7.1-04 definition), alert burden (alertas/paciente/dia,
  VIS-6.2-04), and ack-time distribution vs. severity SLAs (CAT-C-02..05).
- AC2: baselines and goals from vision §7.1 are rendered against actuals (PPV 35% → ≥60%; fatigue 25%
  → ≤10%).
- AC3: time-series views make threshold-change effects visible (before/after markers linked to
  threshold versions from US-25).
- AC4: the noisiest alert types (lowest PPV × highest volume) are ranked as a governance work queue.
- Persona criteria: **PER-FERNANDA-02, PER-CARLOS-02**. Metrics: VIS-7.1-02, VIS-7.1-04.

**US-24 (SHOULD, Fase 2b)** — As Enf. Ana (and Dr. Carlos for medical handoff), I want a shift handoff
summary per patient, so that the oncoming team inherits the full deterioration picture. *(SBAR framing
is an orchestrator directive; content fields below are grounded in existing data. Needs clinical
validation — see §6.)*
- AC1: per-patient summary assembling: score trajectory last 24h (all score types), active alerts with
  dispositions and acknowledgments, interventions/actions logged (US-05/US-12/US-22), and current
  staleness of each vital stream.
- AC2: generated on demand at shift boundaries for a patient or a whole unit; read-optimized for
  bedside and board contexts.
- AC3: handoff generation is logged (audit event) so handoff coverage is measurable per shift.
- AC4: content requires zero manual recalculation or transcription by the nurse (PER-ANA-01 spirit).
- Persona criteria: **PER-CARLOS-03, PER-ANA-03**. Metrics: PER-CARLOS-03, VIS-7.1-03.

**US-25 (SHOULD, Fase 2b)** — As Dra. Fernanda (with Dr. Carlos as clinical reviewer), I want a
governed threshold-change workflow, so that tuning is safe, authorized, and auditable.
- AC1: threshold configuration supports tenant and unit granularity and is stored locally
  (threshold_config constraint, ledger) — never hardcoded in alert code.
- AC2: workflow is propose → review/approve (role-gated) → activate with effective-from timestamp;
  every step in the append-only audit trail (IMP-C-01).
- AC3: every threshold version is immutable and referenced by fired alerts, so any historical alert
  can be traced to the exact threshold + algorithm version that produced it (VIS-7.2-05, VIS-C-13).
- AC4: changes require a recorded justification citing evidence or analytics (e.g. US-23 queue item).
- AC5: safety floor: regulatory/guideline-mandated critical thresholds are marked non-relaxable
  below their published values without a RATIFY-level escalation.
- Persona criteria: **PER-CARLOS-02, PER-FERNANDA-02**. Metrics: VIS-7.2-05, VIS-7.1-02.

**US-26 (COULD, Fase 2c)** — As Dra. Fernanda, I want a retrospective preview of a proposed threshold
change, so that a tuning decision after a noisy week is evidence-based before it goes live.
- AC1: replay of the stored last-N-days data against the proposed threshold produces estimated alert
  volume delta and which historical alerts would/would not have fired.
- AC2: preview output attaches to the US-25 proposal record.
- AC3: preview is decision support only — activation still requires the US-25 approval path.
- Persona criteria: **PER-CARLOS-02, PER-FERNANDA-02**. Metrics: VIS-7.1-02, VIS-7.1-04.

**US-27 (SHOULD, Fase 2b)** — As Dr. Rafael, I want the en-route mobile patient screen, so that I
arrive at the bedside already oriented.
- AC1: screen shows patient location, latest vitals (últimos vitals) each with its own timestamp/
  staleness, current scores with trend direction, and the triggering alert's explanation (US-21).
- AC2: reachable in one tap from the push notification (US-08); usable one-handed while moving.
- AC3: renders on the responsive web app (WON'T: native app, §4) on corporate smartphones.
- Persona criteria: **PER-RAFAEL-02**. Metrics: PER-RAFAEL-02, VIS-7.1-03.

**US-28 (SHOULD, Fase 2b)** — As Dr. Rafael, I want to document the desfecho of an RRT attendance in
under a minute, so that documentation never queues behind the next call.
- AC1: structured desfecho options reflecting the persona flow (melhorou, transferido para UTI, etc.)
  plus optional free text; completable in <1 minuto (PER-RAFAEL-03).
- AC2: desfecho record links the alert(s) that dispatched the call, with user + timestamps in the
  audit trail; it closes the loop for time-to-action metrics (VIS-7.1-03).
- AC3: form-opened and form-saved events are emitted so the <1 min criterion is continuously measured.
- Persona criteria: **PER-RAFAEL-03**. Metrics: PER-RAFAEL-03, VIS-7.1-03.

**US-29 (SHOULD, Fase 2b)** — As Dra. Fernanda, I want the relatório semanal de KPIs clínicos, so that
quality review runs on data with a fixed cadence.
- AC1: weekly (7-day) report per unit covering the platform-measured KPIs: tempo médio até ação
  clínica pós-alerta, PPV, taxa de alarm fatigue, alert burden, score latency compliance, occupancy/
  acuity summary. (Indicators the platform does not measure — e.g. taxa de infecção from Fernanda's
  flow — are out of scope; see §6.)
- AC2: report generation is an audited scheduled event; misses page the operations owner (dead man's
  switch pattern, IMP-C-05).
- AC3: report values reconcile exactly with the US-23 analytics for the same period.
- Persona criteria: **PER-FERNANDA-02**. Metrics: PER-FERNANDA-02.

**US-30 (SHOULD, Fase 2b)** — As Dra. Fernanda, I want unit-level data exports to hospital quality
tools, so that institutional quality management consumes IntensiCare data directly (PER-C-08).
- AC1: export of KPI and alert/score aggregates in machine-readable form (file download and/or API
  pull) suitable for ferramentas de qualidade hospitalar.
- AC2: exports respect LGPD: sensitive-data minimization, purpose limitation to clinical decision
  support/quality (VIS-C-05), and every export logged with requester, scope, timestamp (IMP-C-01).
- AC3: export schema is versioned and documented; a schema change is a breaking-change event.
- Persona criteria: **PER-FERNANDA-03**. Metrics: PER-FERNANDA-03.

---

## 3. Success metrics — instrumentation

Every metric below names the event/audit data that measures it. Instrumentation is a product
requirement: a criterion without its instrument shipping in the same phase is not "done".

### 3.1 The 12 persona criteria

| Criterion | Requirement (PT verbatim) | Target | Instrument (event/audit data) | Stories |
|---|---|---|---|---|
| PER-CARLOS-01 | "Score disponível em <30s após coleta de vitals" | ≤ 30 s | Timestamp pair per score: vitals `recorded_at` → `clinical_score.calculated_at`; OTel span + p95 gauge per unit/day. Decomposition vs. impl-plan SLOs pending (CON-SEED-01). | US-01, US-02, US-07 |
| PER-CARLOS-02 | "Menos de 3 falsos positivos por paciente-dia" | < 3 FP/patient-day | 'não procede' disposition events (US-22) ÷ patient-days (census from occupancy data); per unit and per alert type. | US-03, US-13..20, US-22, US-23, US-25, US-26 |
| PER-CARLOS-03 | "Visualização rápida de tendências (gráfico 24h)" | 24 h window, fast | UI telemetry `trend_chart_viewed` (success rate, time-to-render); 24h-window API query span. | US-02, US-10, US-24 |
| PER-ANA-01 | "Zero cálculos manuais de score" | 0 manual calculations | Structural: 100% `clinical_score` rows system-generated with non-null `algorithm_version`; no manual-entry endpoint exists; pilot time-motion check vs. 20 min/shift/patient baseline. | US-01, US-02, US-07 |
| PER-ANA-02 | "Alerta mostra exatamente qual parâmetro disparou" | 100% of alerts | Non-empty structured trigger payload on every alert record (US-21 gate); screen-spec audit that the breakdown renders. | US-04, US-21, US-13..US-20 |
| PER-ANA-03 | "Registro rápido de resposta ao alerta (1 clique)" | 1 click | Interaction telemetry: click-path length from alert surface to persisted `alert_response`/disposition audit event; median = 1. | US-05, US-12, US-22 |
| PER-FERNANDA-01 | "Dashboard de ocupação em tempo real" | real-time (push-fed) | Data-freshness metric on board (`now − max(updated_at)`); push delivery latency shared with alert channel (ADR-C-13). | US-06, US-09 |
| PER-FERNANDA-02 | "Relatório semanal de KPIs clínicos" | weekly (7-day) cadence | `report_generated` audit events with period coverage + delivery success; missed-run alerting. | US-09, US-23, US-29 |
| PER-FERNANDA-03 | "Dados exportáveis para ferramentas de qualidade hospitalar" | capability, 100% audited | `export_completed` audit events (requester, scope, format); export-schema conformance test. | US-30 |
| PER-RAFAEL-01 | "Notificação mobile em <5 segundos após score crítico" | < 5 s | `alert.created_at` → device delivery receipt; p95 daily; retry/backoff telemetry (IMP-C-06). | US-08 |
| PER-RAFAEL-02 | "Tela de paciente com últimos vitals + tendência" | content completeness | Mobile screen-load event asserting latest vitals (with staleness) + trend present; time-to-interactive. | US-08, US-27 |
| PER-RAFAEL-03 | "Documentação de desfecho em <1 minuto" | < 60 s | Duration between `outcome_form_opened` and `outcome_saved` audit events; median < 60 s; completion rate. | US-28 |

### 3.2 Vision §7.1 clinical metrics

| Metric (VIS id) | Baseline → Goal | Instrument |
|---|---|---|
| VIS-7.1-01 Sensibilidade para sepse (detecção em < 1h) | 45% → ≥ 80% | Adjudicated sepsis case registry (before-after study, VIS-6.1) joined to SEP-* alert timestamps; sensitivity = alerted-within-1h ÷ adjudicated cases. Depends on US-13 + study data collection. |
| VIS-7.1-02 PPV dos alertas (acionáveis / total) | 35% → ≥ 60% | Confirmed dispositions (US-22) ÷ total fired alerts, per alert type; matches per-alert `ppv_budget` in the alert schema (CONTRACTS). Surfaced in US-23. |
| VIS-7.1-03 Tempo médio até ação clínica pós-alerta | 42 min → ≤ 15 min | `alert.created_at` → first clinical response audit event (Reconhecer with action, US-12/US-22 action, or RRT desfecho US-28); median + p95, per severity. |
| VIS-7.1-04 Taxa de alarm fatigue (alertas ignorados) | 25% → ≤ 10% | Alerts unacknowledged past their severity action SLA (CAT-C-02..05) or dismissed-without-view ÷ total; per unit/shift in US-23. |
| VIS-7.1-05 Redução de mortalidade em UTI | baseline Fase 1 → −10% | Study outcome (28-day ICU mortality) from the before-after / stepped-wedge registries (VIS-6.1-03, VIS-6.2-04), linked via mpi_id; not app telemetry alone. |

### 3.3 Vision §7.2 technical metrics

| Metric (VIS id) | Goal | Instrument |
|---|---|---|
| VIS-7.2-01 Latência ingestão → alerta (p95) | < 30 s | End-to-end OTel trace (ingest event → alert emitted) with stage spans (ingest, score, alert); p95 dashboard + SLO burn alerts. Canonical decomposition vs. IMP-C-12..14 owned by alert-engine-architect (CON-SEED-01). |
| VIS-7.2-02 Disponibilidade da plataforma | 99.9% | `/api/v1/health` external synthetic probes + dead man's switch (IMP-C-05); monthly availability report. Conflict with IMP-C-11 (API 99% MVP / 99.5% prod) recorded in §6, not resolved here. |
| VIS-7.2-03 Throughput de processamento | > 500 alerts/min | Staging load-test gate per release + production `alerts_emitted_total` peak-rate counter. |
| VIS-7.2-04 Retenção de dados (TimescaleDB) | 7 years (LGPD/CFM) | Retention-policy configuration under version control + automated verification job; per-entity policy (raw vital_sign 90d vs. scores/alerts 7y) pending data-architect (CON-SEED-03). |
| VIS-7.2-05 Versionamento de algoritmos de alerta | 100% auditable | 100% of `clinical_score` and alert rows carry non-null `algorithm_version` (IMP-C-03); threshold versions immutable and referenced by fired alerts (US-25); append-only `audit_trail` (IMP-C-01). |

---

## 4. WON'T-HAVE (explicit, this plan)

Product-scope exclusions (implementation-plan §2.2 WON'T, IMP-2.2-13):
1. **Modelo preditivo de sepse (ML)** — not clinically validated; requires a formal study; vision
   defers ML to Fase 2d/Fase 4 with formal validation and possible ANVISA Classe III implications
   (IMP-6-05). Phase-2 processing stays deterministic (VIS-2-06).
2. **SMART-on-FHIR apps** — requires Keycloak + complex OAuth2 flow; postponed.
3. **App mobile nativo (React Native)** — the responsive web app covers ~80% of the need; RRT flows
   (US-08/27/28) ship on responsive web.

Platform/positioning exclusions (vision §8 + ADR-001 constraints, recorded in the ledger):
4. **Automatic diagnosis or autonomous treatment decisions** — alerts are advisory; the physician
   holds the final clinical decision (VIS-C-01, VIS-C-08); leaving this would break the SaMD Classe
   II classification (VIS-8.1-01).
5. **Own data-ingestion pipelines (NiFi/Kafka/Debezium)** — clinical data is read from the AMH Gold
   layer via Amazon Athena only (CON-0001).
6. **Proprietary patient identifiers** — MPI `mpi_id` is the identity (CON-0002).
7. **Operating its own FHIR server** — consumes the existing HAPI FHIR server (CON-0005).
8. **HIPAA/GDPR compliance claims** — wrong jurisdictions; LGPD + SBIS replace them (IMP-5.1-05,
   IMP-C-07).
9. **TISS XML billing integration** — FHIR R4 suffices for clinical interop; billing is delegated to
   the hospital bus (IMP-5.1-04).
10. **ML runtime in the deterministic alert path** — no ML inference inside Phase-2 alert evaluation
    (VIS-2-06); predictive models arrive only with Fase 2d/Fase 4 validation gates.

---

## 5. Traceability — story → persona criteria → metrics

| Story | Persona criteria (PER-*) | Success metrics |
|---|---|---|
| US-01 | PER-ANA-01 | PER-ANA-01; feeds PER-CARLOS-01, VIS-7.2-01 |
| US-02 | PER-CARLOS-01, PER-ANA-01 | PER-CARLOS-01, VIS-7.2-01, VIS-7.2-05 |
| US-03 | PER-CARLOS-02 | PER-CARLOS-02, VIS-7.1-02, VIS-7.1-04 |
| US-04 | PER-ANA-02 | PER-ANA-02 |
| US-05 | PER-ANA-03 | VIS-7.1-03, VIS-7.1-04 |
| US-06 | PER-FERNANDA-01 | PER-FERNANDA-01 |
| US-07 | PER-ANA-01, PER-CARLOS-01 | PER-CARLOS-01, PER-ANA-01 |
| US-08 | PER-RAFAEL-01, PER-RAFAEL-02 | PER-RAFAEL-01 |
| US-09 | PER-FERNANDA-01, PER-FERNANDA-02 | VIS-7.1-03, VIS-7.1-04, PER-FERNANDA-01 |
| US-10 | PER-CARLOS-03 | PER-CARLOS-03 |
| US-11 | PER-ANA-02 | VIS-7.1-03 |
| US-12 | PER-ANA-03 | PER-ANA-03, VIS-7.1-03 |
| US-13 | PER-CARLOS-02, PER-ANA-02 | VIS-7.1-01, VIS-7.1-02, VIS-6.1-02 (time-to-antibiotic) |
| US-14 | PER-CARLOS-02, PER-ANA-02 | VIS-6.1-02 (AKI recognition), VIS-7.1-02 |
| US-15 | PER-CARLOS-02, PER-ANA-02 | VIS-6.1-02 (arrest reduction), VIS-7.1-02 |
| US-16 | PER-CARLOS-02 | VIS-7.1-02, VIS-7.1-03 |
| US-17 | PER-CARLOS-02 | VIS-7.1-02, VIS-7.1-03 |
| US-18 | PER-CARLOS-02, PER-ANA-02 | VIS-7.1-02 |
| US-19 | PER-ANA-02, PER-CARLOS-02 | VIS-7.1-02, VIS-7.1-04 |
| US-20 | PER-CARLOS-02, PER-ANA-02 | PER-CARLOS-02, VIS-7.1-02, VIS-7.1-04 |
| US-21 | PER-ANA-02 | PER-ANA-02, VIS-7.1-03 |
| US-22 | PER-ANA-03, PER-CARLOS-02 | VIS-7.1-02, PER-CARLOS-02, PER-ANA-03 |
| US-23 | PER-FERNANDA-02, PER-CARLOS-02 | VIS-7.1-02, VIS-7.1-04 |
| US-24 | PER-CARLOS-03, PER-ANA-03 | PER-CARLOS-03, VIS-7.1-03 |
| US-25 | PER-CARLOS-02, PER-FERNANDA-02 | VIS-7.2-05, VIS-7.1-02 |
| US-26 | PER-CARLOS-02, PER-FERNANDA-02 | VIS-7.1-02, VIS-7.1-04 |
| US-27 | PER-RAFAEL-02 | PER-RAFAEL-02, VIS-7.1-03 |
| US-28 | PER-RAFAEL-03 | PER-RAFAEL-03, VIS-7.1-03 |
| US-29 | PER-FERNANDA-02 | PER-FERNANDA-02 |
| US-30 | PER-FERNANDA-03 | PER-FERNANDA-03 |

Coverage check: all 12 persona criteria appear in ≥1 story; all VIS-7.1 and VIS-7.2 metrics have a
named instrument (§3.2/§3.3); WON'T list explicit (§4).

---

## 6. Recorded conflicts and open questions (not resolved here)

1. **Latency decomposition** — vision §7.2 gives one number (ingest→alert p95 < 30 s); impl-plan §7.3
   splits ingestion <500 ms / score <30 s / alert <5 s (MVP). CON-SEED-01; owner alert-engine-architect
   (resolve at C3). This spec cites both without choosing.
2. **Availability** — VIS-7.2-02 states 99.9% platform availability; IMP-C-11 states API 99% MVP /
   99.5% produção. Both are vision-authority; recorded, not resolved.
3. **Retention per entity** — blanket 7y (VIS-7.2-04) vs. raw vital_sign 90d in the data model
   (CON-SEED-03); owner data-architect.
4. **SBAR handoff framing (US-24, MOT-17)** — "SBAR" is an orchestrator directive, not in vision/
   personas; the content fields are grounded in platform data, but the handoff format needs clinical
   validation before screen-spec freeze.
5. **Weekly report content** — Fernanda's flow reviews mortalidade / tempo de resposta / taxa de
   infecção; the platform measures response/alert/score metrics. Taxa de infecção has no data source
   in any brief — excluded from US-29 pending a data-source decision.
6. **FP/patient-day denominator** — census/patient-day source for PER-CARLOS-02 needs a canonical
   definition from data-architect (occupancy events vs. ADT feed).
7. **Low-availability inputs** — PPV/SVV (DATA-AVAIL-09) and structured CAM-ICU/RASS (DATA-AVAIL-08)
   gate US-16/US-19; US-19 therefore includes structured bedside capture as product scope.
8. **Severity-scale mapping** — legacy NEUTRO/AMARELO/LARANJA/VERMELHO, catalog CRIT/URG/WARN/INFO,
   and canonical normal/watch/urgent/critical must be mapped once, centrally (CON-SEED-11); product
   copy in this spec quotes source scales verbatim pending that mapping.
