# IntensiCare v2 — Journey Maps: 20 Moments of Truth

Deliverable of the clinical-ux-researcher (product layer). Companion to
`docs/plan/product/product-spec.md` (persona/JTBD/story definitions, metric instruments).

A **moment of truth (MOT)** is an instant where the product either earns or loses clinical trust.
Each moment lists: persona(s), trigger, steps, what the system must show/do, the success metric
(persona criterion `PER-*` or vision metric `VIS-*`), and failure modes to design against. Failure
modes cite audited legacy defects (`ADR-*`) where the v1 frontend already demonstrated the trap —
those must be designed out, not ported (design-adrs.json).

Persona key: CARLOS = Dr. Carlos (Médico Intensivista) · ANA = Enf. Ana (Enfermeira de UTI) ·
FERNANDA = Dra. Fernanda (Coordenadora de UTI) · RAFAEL = Dr. Rafael (Equipe de Resposta Rápida).

Coverage: CARLOS 12 moments · ANA 11 · FERNANDA 4 · RAFAEL 4 (some moments shared).

---

## MOT-01 — 07:00 arrival scan: "what happened overnight?"

- **Persona(s):** CARLOS (primary); ANA (parallel nursing version at shift start).
- **Trigger:** Dr. Carlos arrives at 7h and must decide which patients to see first before the 8h
  round (persona flow: arrives 7h, reviews critical patients).
- **Steps:** (1) Opens the painel de leitos for his unit. (2) Scans 20 beds for score, trend arrow,
  active alert status, tempo desde último vital. (3) Sorts/filters by severity or score delta
  overnight. (4) Picks the 3–4 patients to review at bedside first.
- **System must show/do:** bed grid with score + trend direction + alert state per bed (US-06);
  overnight change emphasized (score delta since ~19h); staleness indicator per bed; one tap into the
  24h trend (US-10).
- **Success metric:** PER-FERNANDA-01 (board freshness — instrument shared); PER-CARLOS-03 (trend in
  one step); VIS-7.1-03 (earlier prioritization shortens time-to-action).
- **Failure modes to design against:** board fed by slow polling while the bell is push-fed — states
  disagree (ADR-0017, ADR-C-13); no staleness cue, so a bed with 6h-old vitals looks "stable"; all
  beds visually equal regardless of value severity (ADR-0014); board unreadable at wall distance.

## MOT-02 — 08:00 round multidisciplinar: one story per bed

- **Persona(s):** CARLOS, ANA, FERNANDA (joint).
- **Trigger:** The 8h multidisciplinary round moves bed to bed (flows of all three personas).
- **Steps:** (1) Team stops at a bed. (2) Opens patient detail: scores (MEWS, SOFA, NEWS2), 24h
  trends, active alerts + dispositions, interventions logged. (3) Discusses; decisions reference the
  displayed components. (4) Moves on in <2–3 min per bed.
- **System must show/do:** single patient summary combining US-02/04/10/21/24 data; per-component
  score breakdown to answer "por que subiu?"; alert dispositions from the night visible.
- **Success metric:** PER-CARLOS-03; PER-ANA-02; VIS-7.1-03.
- **Failure modes:** data scattered across drawers-within-drawers losing round rhythm (ADR-0010 depth
  without a stack manager); score shown without components (PER-C-04 violated); yesterday's
  acknowledgments invisible so the team re-litigates handled alerts.

## MOT-03 — Coordinator morning review: capacity and quality at a glance

- **Persona(s):** FERNANDA.
- **Trigger:** Morning review before meeting clinical direction (persona flow: reviews quality
  indicators, manages beds).
- **Steps:** (1) Opens the multi-unit occupancy/acuity dashboard (30 beds, 3 ICUs). (2) Checks
  occupancy, acuity mix, active critical alerts. (3) Checks yesterday's tempo de resposta and alert
  burden. (4) Flags beds for discharge/transfer decisions.
- **System must show/do:** real-time occupancy dashboard (US-06/US-09); response-time KPI vs. goal
  (≤15 min, VIS-7.1-03); alert burden per unit; export path for the direction meeting (US-30).
- **Success metric:** PER-FERNANDA-01; VIS-7.1-03; PER-FERNANDA-03.
- **Failure modes:** occupancy stale without a freshness stamp (mistrust → back to phone calls);
  KPIs computed differently here vs. the weekly report (US-29 reconciliation AC); neonatal/coronary
  units mixed into one undifferentiated average.

## MOT-04 — The invisible moment: vitals become a score, silently

- **Persona(s):** ANA (primary); CARLOS (beneficiary).
- **Trigger:** Monitor sends HL7 ORU-R01; vitals land; score recomputes (US-01/02).
- **Steps:** (1) Ana collects/validates vitals as usual. (2) Within seconds the bed card and patient
  screen show the updated score — no manual MEWS arithmetic (baseline: 20 min/shift/patient). (3) Ana
  glances to confirm the new value registered.
- **System must show/do:** score refresh <30s after coleta (PER-CARLOS-01); visible "last updated"
  timestamp; zero manual calculation demanded (PER-ANA-01); idempotent ingestion so monitor
  retransmissions never duplicate (IMP-C-02).
- **Success metric:** PER-ANA-01 (0 manual calculations); PER-CARLOS-01 (≤30 s, p95).
- **Failure modes:** silent ingestion failure with the old score still displayed as if current (no
  staleness cue — dead man's switch IMP-C-05 exists server-side but the UI must also show feed
  health); duplicated vitals producing false alerts; unit mismatch corrupting the score
  (CON-SEED-12 edge normalization).

## MOT-05 — Alert triage on the unit board

- **Persona(s):** CARLOS (between procedures); ANA.
- **Trigger:** An alert fires and lands on the dashboard/board (US-03); Carlos has ~10 seconds of
  attention mid-procedure-day; today 80% of his 200 alerts/day are false positives.
- **Steps:** (1) Notification appears (board + bell). (2) Carlos reads severity, patient, headline
  parameter in one glance. (3) Decides: go now / delegate / open detail / dismiss with disposition.
  (4) Acknowledges (Reconhecer) if taking it (US-05).
- **System must show/do:** severity encoded by color + icon + shape (CON-SEED-11); headline shows
  triggering parameter + value inline (PER-ANA-02); one-click Reconhecer and one-click disposition
  (US-22); dedup/cooldown so the same event doesn't restack (CONTRACTS suppression).
- **Success metric:** PER-CARLOS-02 (<3 FP/patient-day); VIS-7.1-03 (ack starts the action clock);
  VIS-7.1-04.
- **Failure modes:** severity-blind notification styling — legacy toast hardcoded one amber icon for
  everything (ADR-C-09a); alert arrives at the bell but not the board (ADR-C-13); no inline parameter
  so every triage costs a navigation; repeated identical alerts every few minutes training dismissal.

## MOT-06 — "Qual parâmetro disparou?" — alert explanation at bedside

- **Persona(s):** ANA (primary); CARLOS.
- **Trigger:** Ana reaches the bedside after an alert and must verify the trigger before intervening
  (persona need: clear identification — RR? SpO2? BP?).
- **Steps:** (1) Opens alert detail from the bed card. (2) Reads trigger payload: parameter(s), value
  + unit, threshold crossed, window, input staleness. (3) Cross-checks the monitor. (4) Confirms or
  marks 'não procede' (US-22).
- **System must show/do:** full explanation panel (US-21): components with points (US-04), evidence
  citation, algorithm_version; ≤2 taps from any alert surface.
- **Success metric:** PER-ANA-02 (100% alerts explain themselves); VIS-7.1-02 (explanations enable
  honest dispositions).
- **Failure modes:** empty/generic explanation ("score elevado") forcing manual reconstruction;
  criteria panel colored by a hardcoded severity instead of each criterion's own state (ADR-C-09b);
  stale input (4h-old lactato) presented as current — staleness must print per input.

## MOT-07 — Deterioration review: the 24h story

- **Persona(s):** CARLOS.
- **Trigger:** Between procedures, Carlos reviews a flagged patient in depth (JTBD-CARLOS-3).
- **Steps:** (1) Opens patient trend view. (2) Reads 24h score curve(s) with alert markers. (3)
  Toggles component vitals (FR, SpO2, PA…) under the score curve. (4) Decides on therapy change;
  notes expected trend reversal.
- **System must show/do:** gráfico 24h per score type (US-10) with overlay of alerts and
  interventions; component drill-down; comparable time axes.
- **Success metric:** PER-CARLOS-03; VIS-7.1-03.
- **Failure modes:** trend chart slow or hidden behind deep navigation (goes unused — instrument
  `trend_chart_viewed` will expose this); interventions not on the timeline so cause/effect is
  guesswork; chart illegible in dark theme at bedside (ADR-0002 pending ICU validation, ADR-C-04).

## MOT-08 — Reconhecer + 1-click response logging

- **Persona(s):** ANA (primary); CARLOS.
- **Trigger:** Action taken at bedside must be recorded without leaving care (PER-ANA-03).
- **Steps:** (1) From the alert, Ana taps the action taken (predefined set, US-12). (2) Record writes
  with user + timestamp. (3) Alert state updates everywhere (board, bell, coordinator view) at once.
- **System must show/do:** 1-click logging (PER-ANA-03); append-only audit trail (IMP-C-01); state
  fan-out on the shared push channel (ADR-C-13).
- **Success metric:** PER-ANA-03 (median click-path = 1); VIS-7.1-03 (closes the action clock);
  VIS-7.1-04 (acknowledged ≠ ignored).
- **Failure modes:** multi-field modal form mid-care (logging skipped → metrics undercount real
  care); full-screen blocking spinner on save (ADR-0016 FadeLoading pattern); ack recorded locally
  but other surfaces stay "unhandled", double-dispatching colleagues.

## MOT-09 — False-positive feedback: "não procede"

- **Persona(s):** CARLOS; ANA.
- **Trigger:** Bedside check disproves the alert (part of today's 80% FP burden).
- **Steps:** (1) One click marks 'não procede' (US-22). (2) Optional reason tag (one more tap, never
  required). (3) Disposition feeds PPV and FP/patient-day analytics (US-23). (4) Recurrently noisy
  alert types surface in Fernanda's governance queue (US-25).
- **System must show/do:** frictionless capture; visible loop-closure ("this feedback tunes the
  system") to sustain participation; never silently disables an alert type (US-22 AC3).
- **Success metric:** PER-CARLOS-02; VIS-7.1-02 (PPV 35→≥60%); VIS-7.1-04.
- **Failure modes:** feedback feels like a void (no visible consequence → participation decays);
  disposition buried in a submenu; punitive framing (who dismissed) instead of alert-quality framing;
  dismissing-without-judging conflated with 'não procede' (corrupts PPV).

## MOT-10 — Sepsis triage: the golden hour

- **Persona(s):** CARLOS (decision); ANA (bundle execution).
- **Trigger:** 'qSOFA ≥2 com tendência de lactato' fires (SEP-002/US-13); if lactato ≥ 4.0 mmol/L +
  MAP < 65 mmHg → 'choque séptico iminente' (crítico).
- **Steps:** (1) Critical alert reaches Carlos <5s. (2) Detail shows which qSOFA criteria + lactato
  trend with timestamps. (3) Carlos orders the sepsis pathway (SSC 1h bundle: lactato, culturas, ATB,
  cristaloide, vasopressor — CAT-SEP-002 evidence). (4) Ana logs actions (US-12); antibiotic time
  captured. (5) Follow-up: clearance de lactato monitored (HEMO-002).
- **System must show/do:** crítico severity treatment (action <5 min class, CAT-C-02); criteria-level
  explanation; time-since-alert prominent; downstream lactate-clearance follow-up armed.
- **Success metric:** VIS-7.1-01 (sensitivity ≥80% within 1h); VIS-6.1-02 (time-to-antibiotic −60
  min); VIS-7.1-03.
- **Failure modes:** false-negative by design gaps (qSOFA limitations under β-bloqueadores — surface
  the caveat, US-13 AC5); alert fires but bundle progress is untracked so "detected early, treated
  late" is invisible; duplicate sepsis alerts from SIRS + qSOFA paths not correlated (noise at the
  worst moment).

## MOT-11 — Critical lab lands: K⁺ 6.8 mmol/L

- **Persona(s):** ANA (first responder); CARLOS (prescription).
- **Trigger:** Lab result posts K+ > 6.5 mmol/L → 'Hipercalemia grave' crítico (ELY-001a/US-15).
- **Steps:** (1) Alert fires on result arrival. (2) Ana sees value, prior K+, delta, and ECG/QTc
  context if present. (3) Carlos is notified in the same severity class; protocol started. (4)
  Repeat-K+ scheduled; alert tracks recheck.
- **System must show/do:** on-result latency within SLO; crítico handling <5 min (CAT-C-02);
  context lines (medicamentos hipercalemiantes, Cr) per CAT-ELY-001; safety cross-check with QTc/Mg
  (DDX/ELY correlation, US-20 correlation 3).
- **Success metric:** VIS-6.1-02 (arrest reduction −50% goal); VIS-7.1-03.
- **Failure modes:** critical lab arriving as a generic row with no visual escalation (ADR-0014 —
  legacy rendered SpO2 60% identically to 99%); alert racing the lab-validation workflow (repeated
  fire on corrected result — dedup on result lineage); hemolyzed-sample FPs souring trust (recheck
  affordance matters).

## MOT-12 — AKI stage progression recognized in time

- **Persona(s):** CARLOS.
- **Trigger:** 'Progressão AKI — mudança de estágio em 24h' (AKI-004/US-14) or a first 'KDIGO
  Estágio 1' (AKI-001).
- **Steps:** (1) Alert shows stage, firing criterion (Cr vs. diurese), creatinina basal used. (2)
  Carlos reviews the Cr/diurese curves. (3) Checks nephrotoxic exposures (AKI-005 context). (4)
  Adjusts therapy (fluids, doses per CrCl — DDX-006 link).
- **System must show/do:** basal transparency (menor valor 3 meses/admissão — verifiable); stage
  history timeline; drug-context join.
- **Success metric:** VIS-6.1-02 (recognition −6h); VIS-7.1-02.
- **Failure modes:** wrong/opaque baseline creatinine → wrong stage → mistrust of the whole domain;
  diurese criterion silently inactive because hourly urine output isn't charted (DATA-AVAIL-04 —
  coverage must be visible); stage alerts re-firing daily without new information.

## MOT-13 — Correlated insight: one story, not three alarms

- **Persona(s):** CARLOS.
- **Trigger:** Correlation Engine (Fase 2d/US-20) links active alerts — e.g. Sepse + AKI ('sepse é #1
  causa de AKI', VIS-4-03).
- **Steps:** (1) Instead of independent alarms, one correlated insight appears. (2) Carlos expands
  it: constituent alerts, shared signals, temporal relation. (3) Treats the syndrome, not the
  fragments; dispositions apply coherently.
- **System must show/do:** grouped notification (single stream); explanation of the link (US-20 AC3);
  constituent alerts inspectable; measurable notification reduction vs. ungrouped.
- **Success metric:** PER-CARLOS-02; VIS-7.1-04; VIS-7.1-02.
- **Failure modes:** black-box correlation ("related" without why — clinicians will not trust it);
  grouping that hides a crítico constituent under a watch-level summary (severity must escalate to
  the max member); cross-unit correlation latency making the "insight" arrive after the clinician
  already connected the dots.

## MOT-14 — RRT dispatch: the <5-second page

- **Persona(s):** RAFAEL.
- **Trigger:** Critical score/alert anywhere in the hospital dispatches the RRT (US-08).
- **Steps:** (1) Push hits the corporate smartphone <5s after the score crítico. (2) Lock-screen
  lock-screen payload: severity band + opaque deep-link ONLY (PHI-free, alert-routing §payload). (3) One tap → authenticated PWA opens full context (score, trend, location; content-load p95 budgeted); Rafael accepts and moves; acceptance is timestamped.
- **System must show/do:** PER-RAFAEL-01 latency with delivery receipts; retry/backoff (IMP-C-06);
  one tap from lock screen to full patient context inside the authenticated PWA; acceptance visible to the unit team.
- **Success metric:** PER-RAFAEL-01 (<5 s p95); VIS-7.1-03.
- **Failure modes:** push delivered but silent under OS notification settings (delivery ≠ awareness —
  receipts + escalation path if unaccepted); deep-link fails to resolve (fallback: unit-board context + audited incident); duplicate dispatch when score re-fires mid-response.

## MOT-15 — En-route review on mobile

- **Persona(s):** RAFAEL.
- **Trigger:** Walking to the ward after accepting the dispatch (persona flow: reviews data while
  moving).
- **Steps:** (1) One tap from the notification opens the patient screen (US-27). (2) Reads últimos
  vitals with per-item staleness, score trend, triggering alert explanation. (3) Mentally stages the
  approach before arrival.
- **System must show/do:** PER-RAFAEL-02 content completeness; one-handed readable layout; loads on
  hospital Wi-Fi dead spots (graceful partial render with explicit "dados de HH:MM" stamps).
- **Success metric:** PER-RAFAEL-02; VIS-7.1-03.
- **Failure modes:** desktop layout crammed onto a phone (legacy responsive strategy had undefined
  bands and forked trees — ADR-0011/ADR-C-07); blank screen while everything fetches (content-shaped
  progressive load, ADR-0016); vitals shown without timestamps — en-route trust requires knowing how
  old each number is.

## MOT-16 — RRT desfecho: close the loop in under a minute

- **Persona(s):** RAFAEL; (FERNANDA and CARLOS consume the closed loop).
- **Trigger:** Patient stabilized; Rafael must document before the next call (persona flow:
  documenta desfecho — melhorou, transferido para UTI, etc.).
- **Steps:** (1) Opens desfecho form from the active dispatch (US-28). (2) Picks the structured
  outcome; optional note. (3) Saves <1 min; record links the dispatching alert(s). (4) Unit team and
  coordinator dashboards reflect the closed loop.
- **System must show/do:** PER-RAFAEL-03 timing telemetry (form-opened → saved); structured options
  first, free text optional; audit-trail linkage to alerts (VIS-7.1-03 terminal event).
- **Success metric:** PER-RAFAEL-03 (<60 s median); VIS-7.1-03.
- **Failure modes:** long form → documentation deferred and lost (the 1-minute budget is the
  product); desfecho disconnected from the alert (analytics can't compute alert→outcome); no offline
  tolerance — a dead zone at save time discards the entry.

## MOT-17 — Shift handoff: the 19:00 SBAR

- **Persona(s):** ANA → oncoming nurse; CARLOS → night physician. *(SBAR framing per orchestrator
  directive; content grounded in platform data — validation flagged in product-spec §6.)*
- **Trigger:** 12h shift boundary (persona flow).
- **Steps:** (1) Ana opens the handoff summary for her 4–5 patients (US-24). (2) Reviews per patient:
  24h scores/trends, active alerts + dispositions, interventions, vitals staleness. (3) Walks the
  oncoming nurse through it at the bedside/board. (4) Handoff generation is logged.
- **System must show/do:** auto-assembled summary (zero re-transcription); per-patient one-screen
  density; print/read mode for the huddle.
- **Success metric:** PER-CARLOS-03 (trend synthesis); PER-ANA-03 (no manual assembly); VIS-7.1-03
  (night team starts oriented).
- **Failure modes:** summary omits overnight-relevant pending items (an unacknowledged watch-level
  alert dies in the gap between shifts); data cut at generation time without a stamp (oncoming nurse
  reads 18:40 data at 19:25); handoff replacing — rather than structuring — the verbal exchange.

## MOT-18 — Night shift: the monitor-wall glance

- **Persona(s):** ANA (night); CARLOS (remote call coverage); RAFAEL (hospital-wide watch).
- **Trigger:** 03:00, low staffing; the unit board on the wall is the ambient safety net.
- **Steps:** (1) Periodic glance at the wall board from anywhere in the unit. (2) Normal = calm
  visual field; any watch/urgent/critical bed is unmissable at distance. (3) Staleness anomalies
  (feed down, vital overdue) are as visible as clinical alerts. (4) Carlos, remote, sees the same
  truth on his phone.
- **System must show/do:** dark-first theme legible at distance and glare-free (ADR-0002 default,
  pending ICU validation); severity legible by shape + color at meters (CON-SEED-11 encoding);
  "silence = verified normal" — feed health explicitly rendered; remote parity via the same push
  channel.
- **Success metric:** PER-FERNANDA-01 instrument (board freshness); PER-RAFAEL-01 (night dispatch
  path); VIS-7.2-02 (availability — the wall is the availability the night team experiences).
- **Failure modes:** the deadliest: a stalled board that looks normal (data freshness must be a
  first-class visual state, ADR-0017 — the most safety-critical view was the least live in v1);
  night-dimmed colors collapsing severity distinctions (contrast check both themes, ADR-C-04);
  polling-interval board disagreeing with the bell heard from the corridor (ADR-C-13).

## MOT-19 — Threshold tuning after a noisy week

- **Persona(s):** FERNANDA (owner); CARLOS (clinical reviewer).
- **Trigger:** US-23 analytics show an alert type with low PPV/high volume (e.g. a WARN-tier rule
  flooding a unit); the team is dismissing reflexively — alarm-fatigue risk (VIS-7.1-04 trending
  wrong).
- **Steps:** (1) Fernanda opens the governance queue ranked by PPV × volume (US-23 AC4). (2) Reviews
  the offender's dispositions and evidence. (3) Drafts a threshold proposal (US-25) with
  justification. (4) Runs the retrospective preview (US-26): estimated volume delta, which historical
  alerts would not have fired. (5) Carlos approves; change activates with effective-from timestamp;
  version recorded. (6) Two weeks later the before/after markers on US-23 charts show the effect.
- **System must show/do:** end-to-end governance trail (propose→approve→activate→observe); immutable
  threshold versions referenced by fired alerts (VIS-7.2-05); non-relaxable safety floors flagged
  (US-25 AC5).
- **Success metric:** VIS-7.1-04 (25% → ≤10%); VIS-7.1-02; PER-CARLOS-02.
- **Failure modes:** tuning by config-file edit with no audit (regulatory exposure — VIS-C-13,
  IMP-C-01); over-tuning that trades FPs for missed events with nobody watching sensitivity
  (VIS-7.1-01 must be co-displayed as guardrail); preview treated as approval (US-26 AC3); threshold
  changed mid-study period without the study team's knowledge (VIS-6.x integrity).

## MOT-20 — Friday: weekly KPI report and export

- **Persona(s):** FERNANDA.
- **Trigger:** Weekly quality cycle; meeting with clinical direction/administration (persona flow).
- **Steps:** (1) Relatório semanal de KPIs clínicos generates on schedule (US-29). (2) Fernanda
  reviews: tempo médio até ação, PPV, taxa de alarm fatigue, alert burden, latency compliance,
  occupancy/acuity. (3) Exports the pack for ferramentas de qualidade hospitalar (US-30). (4) Uses
  the series to argue capacity/investment with data, not perception (persona need).
- **System must show/do:** PER-FERNANDA-02 cadence with missed-run alerting; numbers reconciling
  exactly with US-23 dashboards; audited, LGPD-conformant export (VIS-C-05, IMP-C-01).
- **Success metric:** PER-FERNANDA-02; PER-FERNANDA-03.
- **Failure modes:** report and dashboard disagreeing for the same week (credibility gone — one
  metrics engine, two renderings); export schema drifting silently and breaking the hospital quality
  tool's import (US-30 AC3 versioning); PHI over-exposure in exports (minimization per VIS-C-05);
  report arriving late without anyone noticing (dead-man's-switch the schedule, IMP-C-05).

---

## Metric coverage summary

- Every MOT carries ≥1 measurable success metric: PER-CARLOS-01 (MOT-04), PER-CARLOS-02 (MOT-05, 09,
  13, 19), PER-CARLOS-03 (MOT-01, 02, 07, 17), PER-ANA-01 (MOT-04), PER-ANA-02 (MOT-02, 06),
  PER-ANA-03 (MOT-08, 09, 17), PER-FERNANDA-01 (MOT-01, 03, 18), PER-FERNANDA-02 (MOT-20),
  PER-FERNANDA-03 (MOT-03, 20), PER-RAFAEL-01 (MOT-14, 18), PER-RAFAEL-02 (MOT-15), PER-RAFAEL-03
  (MOT-16) — all 12 persona criteria exercised.
- Vision metrics exercised: VIS-7.1-01 (MOT-10), VIS-7.1-02 (MOT-06, 09, 12, 13, 19), VIS-7.1-03
  (MOT-01..03, 05, 07, 08, 10, 11, 14..17), VIS-7.1-04 (MOT-05, 09, 13, 19), VIS-7.2-02 (MOT-18),
  VIS-7.2-05 (MOT-19), VIS-6.1-02 goals (MOT-10, 11, 12).
- Recurring failure-mode themes for the design system (input to screen specs): staleness as a
  first-class visual state (MOT-01, 04, 06, 15, 17, 18); one push channel for bell + board
  (ADR-C-13: MOT-01, 05, 08, 18); severity encoded per event, never hardcoded (ADR-C-09: MOT-05,
  06); explanation always attached (MOT-05, 06, 10, 12, 13); 1-interaction capture budgets (MOT-08,
  09, 16).
