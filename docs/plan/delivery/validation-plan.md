# Clinical Validation Plan — IntensiCare v2

**Owner:** clinical-validation-methodologist · **Status:** executable protocol — dossier input for the delivery barrier · **Realizes:** review-queue `RQ-4` (Clinical validation protocol), the detailed form of `regulatory-plan.md` §3 (Clinical Evaluation) Tiers 1–2 and PMCF.

**Authority precedence** (CONTRACTS §5): `ADR-001 ≻ vision ≻ directive ≻ audit`. This plan operationalizes **vision §6** (study designs) and **§7** (success metrics). Every clinical / study / target number is traced to a vision fact (`VIS-*`) or persona criterion (`PER-*`); every platform-mechanism number (SLA windows, lifecycle timers, schema constraints) is traced to its owning spec — the alert engine (`alert-engine.md`), the data model (`data-model.md`), a ledger constraint (`CON-*`), an invariant (`INV-1..6`), or the PPV ledger (`ppv-ledger-draft.yaml`). Conflicts with a source are **recorded, never silently resolved** (CONTRACTS §5); see the flagged item in §2.1 and Open Questions.

> **The load-bearing idea of this plan.** IntensiCare validation has two halves that must not be confused. (1) **The platform instruments itself.** The alert lifecycle `raise → acknowledge → act → resolve` (alert-engine.md §9) is an append-only audited event stream (INV-1); PPV, time-to-action, and alarm-fatigue fall directly out of it with **no chart review** (§3.1). (2) **Sensitivity and mortality cannot be self-measured** — a system cannot certify its own false negatives, and it never sees the patients it stayed silent on. Those need an **external gold standard**: blinded retrospective chart-review adjudication (§3.2). Keeping these two measurement regimes distinct is the single methodological requirement everything else hangs on. A third rule governs the whole program: because thresholds are **versioned data, not code** (INV-3, `REQ-INV-3-2`), any mid-study tuning mints a new `alert_definition_version` and is thereby *attributable and firewall-able* from the endpoints (§4).

---

## 0. Scope and structure

Two studies, staged by evidentiary strength, plus the instrumentation and governance that make them executable:

| § | Component | Vision anchor | Role |
|---|-----------|---------------|------|
| **§1** | Before-after observational study (quality-improvement phase) | `VIS-6.1-*` | Fast, single-arm-in-time signal; feasibility + effect-size priors for §2 |
| **§2** | Stepped-wedge cluster RCT (confirmatory) | `VIS-6.2-*` | Level-1 evidence; the SaMD effectiveness claim |
| **§3** | Metrics-instrumentation table (all `VIS-7.1-*` + `VIS-7.2-*`) | `VIS-7.1-*`, `VIS-7.2-*` | The concrete collection mechanism for every success metric |
| **§4** | Interim analyses + alert-tuning governance | `VIS-C-15`, INV-3 | Keeps mid-study tuning from contaminating endpoints |
| **§5** | IRB / CEP submission considerations | `VIS-6.2-07`, `VIS-C-05/06/14/16` | LGPD basis + consent-waiver rationale |

This plan does **not** re-derive clinical thresholds — those live in the alert catalog and units registry (CONTRACTS §3). It measures whether the alerts, as specified, change care.

---

## 1. Study 1 — Before-After Observational Study (Quality-Improvement phase)

### 1.1 Design (`VIS-6.1-01`)

A within-site before-after comparison at two ICUs:

```
  Control period (3 mo)          Washout (2 wk)              Intervention period (3 mo)
  conventional MEWS/NEWS         Phase-2 alert engine        Phase-2 alerts ACTIVE with
  monitoring, NO Phase-2         deployed shadow-mode;       team notification enabled
  alerts; data captured         staff training +            (raise → notify → ack → act)
  retrospectively               threshold calibration
  ─────────────────────►        ─────────►                  ─────────────────────►
```

- **Control (3 months, `VIS-6.1-01`):** conventional MEWS/NEWS monitoring, no Phase-2 alerts firing to clinicians; the engine may run in **shadow mode** (evaluating, logging, but not notifying) so control-period alert *would-have-fired* events are captured retrospectively for a within-patient baseline PPV/volume estimate without influencing care.
- **Washout (2 weeks, `VIS-6.1-01`):** training and calibration; excluded from analysis to avoid a learning-curve confound.
- **Intervention (3 months, `VIS-6.1-01`):** Phase-2 alerts active with team notification through the delivery layer (alert-engine.md §7).

**Rationale for the QI framing.** This phase is a *quality-improvement* deployment of an already-live decision-support tool, not a randomized experiment; it is the ethics/consent-lightest tier (§5.3) and produces the effect-size and ICC priors the §2 sample size assumes.

### 1.2 Population and eligibility (`VIS-6.1-04`)

**Inclusion (`VIS-6.1-04`):** adult ICU patients age **≥ 18 years** with expected stay **> 24 h** and **≥ 1 set of vital signs plus ≥ 1 laboratory result in the first 24 h**. The last clause is a *data-sufficiency* gate: a patient with no labs cannot generate a lab-driven alert and would only add noise to the denominators.

**Exclusion (protocol-defined, consistent with the engine's own eligibility semantics):** re-admissions within the same episode are counted once (dedup by encounter, mirroring the evaluation-idempotency key, alert-engine.md §4.2); comfort-care / end-of-life admissions where escalation alerts are clinically moot are flagged and analyzed in a pre-specified sensitivity subgroup, not silently dropped.

**Unit of analysis:** the ICU **admission** (encounter). Sample frame = the occupancy census that also supplies `patient_days` for rate denominators (`ppv-ledger` `fp_per_patient_day` / `alert_burden`; US-23 AC1 / `VIS-6.2-04`).

### 1.3 Endpoints mapped to §7.1 metrics (baseline → target)

**Primary outcomes (`VIS-6.1-02`):**

| # | Primary endpoint | Direction / target | Fact id | Collection mechanism (§3 detail) |
|---|------------------|--------------------|---------|----------------------------------|
| P1 | Time-to-antibiotic in sepsis | reduce by **60 min** | `VIS-6.1-02` | first `MedicationAdministration` of an antimicrobial (FHIR, `VIS-3.1-08`) minus adjudicated sepsis-recognition time (§3.2 chart review) |
| P2 | Time-to-recognition of AKI KDIGO ≥ 1 | reduce by **6 h** | `VIS-6.1-02` | AKI-alert `created_at` (or first documented AKI note) minus first creatinine/urine-output crossing KDIGO-1 (`VIS-3.2-02`); serial creatinine + hourly UO (`VIS-3.2-07`) |
| P3 | Incidence of cardiac arrest from electrolyte disturbance | reduce by **50%** | `VIS-6.1-02` | code-event registry ⋈ electrolyte panel (`VIS-3.6-*`) within the causal window; two-physician attribution |

**Secondary outcomes (`VIS-6.1-03`) — these are the §7.1 metrics measured in-study:**

| Secondary endpoint | Baseline → target | Fact id | Instrumentation (§3) |
|--------------------|-------------------|---------|----------------------|
| Alert fired-vs-confirmed rate (**PPV**) | 35% → **≥ 60%** | `VIS-6.1-03` / `VIS-7.1-02` | resolve-step feedback loop (§3.1) |
| Clinical response time (**time-to-action**) | 42 min → **≤ 15 min** | `VIS-6.1-03` / `VIS-7.1-03` | audited lifecycle timestamps (§3.1) |
| 28-day ICU mortality | Fase-1 baseline → **−10% rel.** | `VIS-6.1-03` / `VIS-7.1-05` | EMR discharge outcome, SAPS-3-adjusted (§3.2) |
| Ventilator-free days | ↑ (descriptive) | `VIS-6.1-03` | EMR ventilation record (`VIS-3.3-08`) |
| ICU-free days | ↑ (descriptive) | `VIS-6.1-03` | occupancy census / LOS |
| Alarm-fatigue rate (**ignored alerts**) | 25% → **≤ 10%** | `VIS-7.1-04` / `PER-CARLOS-02` | ack-SLA timeout events (§3.1) |

### 1.4 Analysis plan (`VIS-6.1-06`)

- **Continuous outcomes** (times-to-event as durations): **paired t-test or Mann-Whitney U** per distribution (`VIS-6.1-06`).
- **Categorical outcomes** (mortality, cardiac-arrest incidence): **χ² or Fisher exact** (`VIS-6.1-06`).
- **Temporal-trend / secular-confound control:** **interrupted time-series (ITS)** with segmented regression at the intervention start, so a pre-existing downward trend is not misattributed to the alerts (`VIS-6.1-06`).
- **Confounder adjustment:** **propensity-score** adjustment for age, **SAPS 3**, comorbidities (`VIS-6.1-06`).
- **Analysis populations:** all eligible admissions (`VIS-6.1-04`); the comfort-care subgroup analyzed separately (§1.2).

### 1.5 Sample size (`VIS-6.1-05`)

**2 ICUs × 30 beds × 3 months ≈ 540 admissions per period** (`VIS-6.1-05`). Powered at **80%**, **α = 0.05**, to detect a **20% relative reduction in time-to-antibiotic** (`VIS-6.1-05`). The 540/period figure implies ≈ 9 admissions/bed over 90 days (≈ 10-day mean LOS) — plausible for adult ICU and consistent with the §2 per-cluster accrual of ≈ 45 eligible admissions/month (`VIS-6.2-05`). The observed control-period effect size and alert PPV/volume become the priors for §2.4.

---

## 2. Study 2 — Stepped-Wedge Cluster Randomized Controlled Trial (confirmatory)

### 2.1 Design and randomization unit (`VIS-6.2-01`, `VIS-6.2-02`)

**Stepped-wedge cluster RCT (SW-CRT):** **8 ICU clusters** (4 hospitals × 2 ICUs each), total period **18 months**, **4 transition steps** (`VIS-6.2-01`).

- **Randomization unit = the ICU cluster.** Clusters are randomized to *transition timing* (the step at which they cross from control to intervention) (`VIS-6.2-02`). Randomization is by ICU, not by patient, because the intervention (an always-on alert engine wired to a unit's monitors and staff workflow) cannot be masked or toggled per patient.
- **Unidirectional crossover (`VIS-C-14`):** all clusters **start in control**, all clusters **end in intervention** — no cluster is ever denied the benefit. This is an ethical hard constraint, not a design preference.

> **⚠ Recorded conflict (CONTRACTS §5 — not silently resolved).** `VIS-6.2-01` parenthetically states "**3 clusters migrate to intervention per period**," which does not divide evenly into **8 clusters over 4 steps** (that requires **2 clusters/step**). The balanced, analyzable design is **4 sequences of 2 clusters crossing at each of 4 steps** (§2.2). The "3 per period" figure is carried verbatim but flagged for the **trial biostatistician** to reconcile in the Statistical Analysis Plan (SAP) before registration; it may reflect an unbalanced allocation or a baseline-period counting convention. See Open Questions.

### 2.2 Wedge schedule (balanced reading — SAP to finalize)

Five measurement periods (1 baseline + 4 post-step), each ≈ **18 mo / 5 ≈ 3.6 months** (`VIS-6.2-01`). ▓ = intervention active, ░ = control:

| Sequence (2 clusters each) | P0 (baseline) | P1 | P2 | P3 | P4 |
|---|:---:|:---:|:---:|:---:|:---:|
| Seq A (clusters 1–2) | ░ | ▓ | ▓ | ▓ | ▓ |
| Seq B (clusters 3–4) | ░ | ░ | ▓ | ▓ | ▓ |
| Seq C (clusters 5–6) | ░ | ░ | ░ | ▓ | ▓ |
| Seq D (clusters 7–8) | ░ | ░ | ░ | ░ | ▓ |

Every cluster contributes both control and intervention person-time; the design is its own control for time-invariant cluster effects, and the calendar-time columns let the model separate the **secular trend** from the **intervention effect** (the property a before-after design lacks). All start ░, all end ▓ (`VIS-C-14`).

### 2.3 Endpoints (`VIS-6.2-03`, `VIS-6.2-04`)

**Primary — hierarchical / composite (`VIS-6.2-03`), tested in fixed order to control multiplicity:**

| Rank | Primary endpoint | Type | Fact id | Instrumentation |
|---|------------------|------|---------|-----------------|
| 1 | Time to adequate antibiotic in sepsis (hours) | time-to-event | `VIS-6.2-03` | §3.2 adjudicated onset → FHIR `MedicationAdministration` |
| 2 | Incidence of AKI KDIGO ≥ 2 during ICU stay | binary/count | `VIS-6.2-03` | KDIGO-2 rule crossing (`VIS-3.2-03`) confirmed on chart |
| 3 | Serious adverse events from unrecognized electrolyte disturbance | count | `VIS-6.2-03` | SAE registry ⋈ electrolyte panel (§3.2 adjudication) |

**Secondary (`VIS-6.2-04`) — several are the §7.1/§7.2 metrics:**

| Secondary endpoint | Fact id | Instrumentation (§3) |
|--------------------|---------|----------------------|
| 28-day ICU mortality | `VIS-6.2-04` / `VIS-7.1-05` | EMR outcome, risk-adjusted (§3.2) |
| Mechanical-ventilation duration | `VIS-6.2-04` | EMR ventilation record |
| ICU length of stay | `VIS-6.2-04` | occupancy census |
| Alert burden (alerts/patient/day) | `VIS-6.2-04` | `total_raised / patient_days` (`ppv-ledger` `alert_burden`) |
| Alarm-fatigue rate (ignored/total) | `VIS-6.2-04` / `VIS-7.1-04` | ack-SLA timeout events (§3.1) |
| Hospital costs (total ICU-stay cost) | `VIS-6.2-04` | hospital cost accounting export (`PER-FERNANDA-03`) |

### 2.4 Sample-size sketch with assumptions stated (`VIS-6.2-05`)

**Target N (`VIS-6.2-05`):** 8 clusters × ≈ 45 eligible admissions/month × 18 months = **≈ 6,480 patients**.

**Stated assumptions (all `VIS-6.2-05` unless noted):**

| Assumption | Value | Source |
|------------|-------|--------|
| Clusters | 8 | `VIS-6.2-01`, `VIS-6.2-05` |
| Accrual per cluster | ≈ 45 eligible admissions/month | `VIS-6.2-05` |
| Duration | 18 months | `VIS-6.2-01`, `VIS-6.2-05` |
| Target power | **> 90%** | `VIS-6.2-05` |
| Two-sided α | **0.05** | `VIS-6.2-05` |
| Intracluster correlation (ICC) | **0.02** | `VIS-6.2-05` |
| Detectable effect | **25% reduction in the composite primary** | `VIS-6.2-05` |
| Eligibility | as §1.2 (`VIS-6.1-04`) | `VIS-6.1-04` |

**Design-effect note (methodologist sketch, to be formalized in the SAP).** A cluster trial inflates the required N by the **design effect** `DEFF = 1 + (m̄ − 1)·ICC`, where `m̄` is the mean cluster-period size. The SW structure earns most of it back through the within-cluster before/after contrast and the number of crossover points; specialized SW sample-size machinery (e.g., Hussey–Hooper closed form or a GLMM-based simulation matching §2.5) must confirm that **≈ 6,480 patients with ICC = 0.02 across 8 clusters and 4 steps** yields **> 90% power** at **α = 0.05** for a **25%** composite reduction (`VIS-6.2-05`). The **6,480 figure is arithmetically consistent** (8 × 45 × 18 = 6,480); the *power* it delivers is the quantity the biostatistician must verify against the design effect and the (recorded) step-allocation question in §2.1. The §1 before-after study supplies the empirical ICC and baseline event rate that this verification consumes.

### 2.5 Analysis plan (`VIS-6.2-06`)

- **Model:** **generalized linear mixed model (GLMM)** with a **random effect for cluster** (`VIS-6.2-06`); a fixed effect for **calendar-time period** (the SW secular-trend term) and a fixed **intervention (▓/░) indicator** — the latter's coefficient is the treatment effect.
- **Outcome distributions:** **Gamma with log-link** for time-to-event durations; **binomial** for incidence (`VIS-6.2-06`).
- **Covariates:** age, sex, **SAPS 3**, comorbidities, admission type (`VIS-6.2-06`).
- **Primary analysis:** **intention-to-treat (ITT)** — every admission analyzed by its cluster's randomized status in that period (`VIS-6.2-06`).
- **Sensitivity:** **per-protocol**, adjusted for **alert adherence** (`VIS-6.2-06`) — and, added here to serve §4, **stratified by `alert_definition_version`** so a mid-study tuning event is a covariate, not a confound.

### 2.6 Contamination handling

Cluster randomization means contamination is the primary internal-validity threat. Five firewalls:

1. **Cluster-level, not patient-level, assignment** — a patient never receives a mix of control and intervention because assignment is by ICU-period (§2.1); there is no within-unit control arm to leak into.
2. **Staff crossover control** — physicians/nurses covering multiple study ICUs (a real risk given the RRT persona `PER-RAFAEL`, who answers calls hospital-wide) are enumerated; the analysis records the treating unit per encounter, and a sensitivity model excludes cross-covered admissions. RRT mobile alerts (`PER-RAFAEL-01`, < 5 s) are scoped to intervention-active units only during the trial.
3. **Version freeze within a step** — the alert **`definition_version` is frozen for the duration of each measurement period** (§4.3); a cluster's "intervention" is a *fixed* specification, not a moving target, so the ▓ columns are comparable across sequences.
4. **Shadow-mode blanking in control** — control-period clusters may run the engine in shadow mode for later comparison but **must not surface alerts** to control-period staff; delivery is disabled at the notification layer (alert-engine.md §7), audited to prove no leakage.
5. **Wash-in accounting** — the first ≈ 2 weeks after a cluster crosses over (learning curve, mirroring §1.1 washout) is pre-specified as a **transition exposure** term in the GLMM rather than pooled into steady-state intervention time.

---

## 3. Metrics-Instrumentation Table

**Every `VIS-7.1-*` and `VIS-7.2-*` success metric with its concrete collection mechanism in the platform.** The backbone is the audited alert lifecycle and the PPV ledger method (`ppv-ledger-draft.yaml`):

> **The feedback loop.** Alert lifecycle `raise → acknowledge → act → resolve` (alert-engine.md §9). Every transition is an **append-only `audit_trail` row (INV-1 / `CON-0066`)**; terminal state carries `alert.resolution ∈ {true_positive, false_positive, intervention_done}` (`DM-VOCAB-05`) plus the one-click disposition (`procede` / `não procede`, US-22). Operational rows and the Gold **`fact_alert`** write-back (`CON-0028`) are the two read surfaces analytics use. **Denominator rule (`ppv-ledger` `method.denominator_rule`):** only *dispositioned* alerts count toward PPV; an un-triaged alert is `pending` (excluded) or, once its ack-SLA lapses unacked, `ignored` (feeds alarm-fatigue, **not** PPV) — so a backlog cannot silently tank PPV.

| # | Metric (vision name) | Fact id | Baseline → Target | Concrete collection mechanism | Signal / source of truth | Grouping · window |
|---|----------------------|---------|-------------------|-------------------------------|--------------------------|-------------------|
| M1 | Sensibilidade para sepse (detecção < 1 h) | `VIS-7.1-01` | 45% → **≥ 80%** | **Retrospective chart-review gold standard (§3.2)** — sensitivity = alerts firing ≤ 1 h before/after adjudicated sepsis onset ÷ all adjudicated sepsis onsets. **Not self-instrumenting** (needs the true-positive denominator the system never sees). | Adjudication dataset ⋈ `fact_alert.created_at` (sepse domain, `VIS-3.1-*`) | per unit · study period |
| M2 | PPV dos alertas (acionáveis / total) | `VIS-7.1-02` | 35% → **≥ 60%** | **Resolve-step feedback loop** — `PPV = TP/(TP+FP)`, `TP = resolution∈{true_positive, intervention_done} ∨ disposition=procede`; `FP = resolution=false_positive ∨ disposition=não procede` (`ppv-ledger` `method.classification`). Only dispositioned alerts. | `alert.resolution` + one-click disposition → `fact_alert` (`CON-0028`) | per_alert_type · per_unit · per_tenant · per_severity_band; rolling 7 d + 30 d |
| M3 | Tempo médio até ação clínica pós-alerta | `VIS-7.1-03` | 42 min → **≤ 15 min** (p50) | **Audited lifecycle timestamps** — `time_to_action = resolved_at − created_at`; the finer `ack → act` transition (`acknowledged_at`, `intervention_started_at`) gives time-to-recognition and time-to-intervention-start sub-metrics. | `alert.created_at / acknowledged_at / resolved_at` (`DM-T-04`); each transition an `audit_trail` row (INV-1) | per_severity_band · rolling 7 d/30 d; p50 target `ppv-ledger` `time_to_action_p50_max=PT15M` |
| M4 | Taxa de alarm fatigue (alertas ignorados) | `VIS-7.1-04` | 25% → **≤ 10%** | **Ack-SLA timeout events** — an alert that breaches its ack-window (crit 2 min / urg 10 min / watch 60 min, alert-engine.md §9) with `status` still `raised` and auto-expires unacked is `ignored`; `ignored_rate = ignored / total_raised`. Acknowledged-then-`não procede` is a **false positive, not ignored**. | `status` transition `raised → expired` (system timer, audited) → `fact_alert` | per_alert_type · per_unit · rolling 7 d/30 d; supports `PER-CARLOS-02` — a per-patient-day **distribution** gate (share of patient-days with > 3 dispositioned FP ≤ 5%, and p95 FP/patient-day < 3) via `fp_patient_day_gt3_share` / `fp_patient_day_p95` over (patient, calendar-day) cells; fleet-mean `fp_per_patient_day` is diagnostic only |
| M5 | Redução de mortalidade em UTI | `VIS-7.1-05` | Fase-1 baseline → **−10% (rel.)** | **Clinical-outcome dataset** — 28-day ICU mortality from EMR discharge disposition (`VIS-6.1-03` / `VIS-6.2-04`), **SAPS-3 risk-adjusted**; effect estimated by the study models (§1.4 ITS / §2.5 GLMM), **not** from the alert loop. | EMR discharge status ⋈ SAPS 3; encounter grain | per cluster/period (§2.5); risk-adjusted |
| M6 | Latência ingestão → alerta (p95) | `VIS-7.2-01` (`VIS-C-09`) | — → **< 30 s** | **Engine stage telemetry** — per-stage timestamps across the canonical latency decomposition (alert-engine.md §8; `latency.yaml`); p95 over a rolling window. | poll → eval → raise → deliver stage timers | p95 · rolling window; SLO gate |
| M7 | Disponibilidade da plataforma | `VIS-7.2-02` (`VIS-C-10`) | — → **99.9%** | **Uptime / deep-health-check probes** (invariant #5 dead-man's switch, alert-engine.md §7.2) + synthetic monitors; note inherited AMH data-availability SLO **99.5%** (`ADR001-C-10`) is tracked separately. | platform SLO telemetry / health endpoint | monthly SLO |
| M8 | Throughput de processamento | `VIS-7.2-03` (`VIS-C-11`) | — → **> 500 alerts/min** | **Alert-storm load test** (test-strategy.md §5) pre-go-live **+** a production counter of raised-alerts/min sustained-rate. | engine emit counter | peak-rate assertion + production observability |
| M9 | Retenção de dados (TimescaleDB) | `VIS-7.2-04` (`VIS-C-12`) | — → **7 years** | **Per-entity retention policy** (data-model.md §7 retention table); a migration/config assertion test proves the 7-year window is set and superseded versions are retained ≥ longest referencing alert. | retention-policy config; schema test | per-entity; LGPD/CFM compliance |
| M10 | Versionamento de algoritmos de alerta | `VIS-7.2-05` (`VIS-C-13`) | — → **100% auditable** | **INV-3** — every `clinical_score.algorithm_version` `NOT NULL` + FK to `algorithm_registry` (`REQ-INV-3-1`); every raised `alert` stamps `definition_version_id` (`REQ-INV-3-2`); Gold write-back carries the version (`REQ-INV-3-3`). Coverage = fraction of scores/alerts with non-null version = **100%** (enforced by the NOT-NULL constraint + immutability trigger). | `clinical_score` / `alert_definition_version` / `algorithm_registry`; coverage query | schema-level; 100% by construction |

**Count: 10 metrics instrumented (5 × `VIS-7.1` + 5 × `VIS-7.2`).** Study-specific endpoint instrumentation (time-to-antibiotic, AKI-recognition time, electrolyte cardiac arrest / SAE) is specified inline in §1.3 and §2.3 and shares the §3.2 chart-review pipeline.

### 3.1 Self-instrumenting metrics (M2, M3, M4) — from the lifecycle loop, no chart review

M2/M3/M4 are computed entirely from audited lifecycle state; they require **no** external adjudication:

- **PPV (M2)** reads the resolve-step disposition. A `correlation_event` (US-20) grouping N constituent alerts counts as **one** dispositioned unit for fleet PPV; constituents keep per-type PPV (`ppv-ledger` `method.correlation_note`) — grouping is not double-counted as improved PPV.
- **Time-to-action (M3)** and **alarm-fatigue (M4)** are pure timestamp/state arithmetic on the `alert` table.
- **Per-alert targets** are governed, not fleet-uniform: e.g. SIRS `SEP-001` carries `ppv_target=0.55` (higher FP tolerance — low SIRS specificity, `CAT-SEP-001`), electrolyte `ELY-001` carries `ppv_target=0.75`, `ignored_max=0.03` (objective lab cutoff) (`ppv-ledger` per-alert budgets). The study reports both the **fleet aggregate vs `VIS-7.1-02/04`** and the **per-type budget attainment**.
- **`tune-me` signal:** an alert type whose 30-day PPV < its target for **2 consecutive windows** raises a governance recommendation (`ppv-ledger` `method.tuning_recommendation`) — the input to §4.2.

### 3.2 Gold-standard metrics (M1 sensitivity, M5 mortality attribution) — retrospective chart-review protocol

Sensitivity and cause-specific harm cannot be self-measured; a system does not observe its own false negatives. Protocol:

- **Reference standard.** For sepsis (M1): **Sepsis-3** adjudication (Seymour et al., JAMA 2016 — `VIS-3.1-03`; Singer 2016). Two independent physician adjudicators review the full chart **blinded to whether an alert fired**; disagreements resolved by a third adjudicator. Adjudicated **sepsis onset time** is the anchor for both M1 (sensitivity) and the P1 time-to-antibiotic clock (§1.3). Analogous blinded adjudication supplies the AKI-KDIGO (`VIS-3.2-02/03`) and electrolyte-SAE (`VIS-3.6-*`) reference sets.
- **Sampling plan (two-stage, to bound chart-review cost).**
  1. **All alert-positive encounters** are reviewed (confirms TP/FP → cross-checks M2 PPV against the self-instrumented value).
  2. **Alert-negative encounters** are sampled by **enriched two-stage sampling**: a **100% stratum** of high-suspicion alert-negatives flagged by an objective proxy (any lactate > 2 mmol/L, any new antimicrobial, any culture order, any creatinine rise — the `VIS-3.1-07` / `VIS-3.2-07` data elements) plus a **random low-suspicion stratum** (e.g. 10–15%). Sensitivity is estimated with **inverse-probability weighting** by stratum so the un-reviewed low-suspicion mass is represented without reviewing every chart. This is the standard capture-recapture-style approach to estimating false negatives at bounded cost; the exact stratum fractions are set from the §1 pilot event rate and fixed in the SAP.
- **Mortality (M5).** 28-day ICU mortality is an EMR field (no adjudication needed for the *event*), but **attribution / risk adjustment** uses SAPS 3 and the §2.5 GLMM; cause-specific arrest attribution (P3) uses the same two-physician review.
- **Blinding & timing.** Adjudication runs **retrospectively** on locked chart data, blinded to arm/alert status, to keep the reference standard independent of the index test.

### 3.3 Technical metrics (M6–M10) — from telemetry and schema

M6–M9 are platform-observability quantities (latency budget `latency.yaml` / alert-engine.md §8; SLO telemetry; load test test-strategy.md §5; retention config data-model.md §7). **M10 is unique: it is 100% *by construction*** — the `NOT NULL` `algorithm_version` / `definition_version_id` constraints and the append-only immutability triggers (`REQ-INV-3-1/2`) make an un-versioned score or alert *unwritable*, so auditability coverage cannot fall below 100% without a schema violation. M10 is therefore also the enabling mechanism for §4.

---

## 4. Interim Analyses and Alert-Tuning Governance

Two things happen *during* an 18-month trial that a naïve plan would let contaminate the endpoints: (a) safety-driven interim looks, and (b) the operational reality that alert thresholds get tuned. Both are governed here.

### 4.1 Interim analyses and DSMB (`VIS-6.2-07`, `VIS-C-15`)

- **Independent DSMB**, meeting **quarterly** (`VIS-C-15`, `VIS-6.2-07`) — 6 scheduled looks over 18 months.
- **Pre-specified stopping rules** in the SAP: efficacy, futility, and **harm** (e.g. an alarm-fatigue or alert-burden signal, `VIS-6.2-04`, exceeding a safety ceiling; a mortality signal in the wrong direction). Because SW-CRT accrues continuously, interim efficacy testing uses an **α-spending function** (e.g. O'Brien–Fleming) so the 6 looks preserve the overall **α = 0.05** (`VIS-6.2-05`); the final analysis uses the residual α.
- **The before-after study (§1)** has no formal stopping boundary (single pre/post contrast) but is monitored by the same QI oversight for safety signals before §2 launches.
- **What the DSMB sees:** unblinded arm-level rates; the trial team stays blinded to comparative results between looks.

### 4.2 Mid-study threshold-tuning governance (who may retune, and how)

**Who.** Threshold changes are **not** ad hoc. The ICU coordinator persona (**Dra. Fernanda**, `PER-FERNANDA`) owns the governed threshold-change queue (US-25); a type is nominated by the `tune-me` signal (§3.1). During the trial, **any change to a study alert requires DSMB awareness and a protocol amendment** (§4.3) — the operational owner proposes, the trial governance approves.

**How it is versioned (INV-3 — the invariant this section is built on).** A threshold change is **data, not code**:
- Changing any threshold **mints a new `alert_definition_version`** (immutable, content-hashed); the engine stamps the exact firing `definition_version_id` on every alert (`REQ-INV-3-2`, alert-engine.md §2). Superseded versions are retained for the 7-year window (`DM-RP-03`), so any historical alert remains byte-for-byte reproducible.
- `threshold_config` changes are **versioned separately and mirrored into `audit_trail` (INV-1)**; a config change does **not** mutate a score/alert version — the two are decoupled (data-model.md §5).
- **Non-relaxable safety floor.** `safety_critical=true` alerts (all critical-band + the ELY-003c delta-Na leg, `CON-0061`) **cannot be silently disabled**, and their thresholds **cannot be relaxed below the published guideline** without a **RATIFY-level escalation** (admin-config.md sec 5; `ppv-ledger` per-alert `safety_critical`). Tuning during a trial can only *tighten toward* or hold the guideline value for these.

**How it is audited.** Every transition and every config write is an append-only `audit_trail` row (INV-1); `REQ-INV-3-3` guarantees the version rides into Gold `fact_alert`, so analytics can **partition every endpoint by the algorithm version in force**.

### 4.3 The contamination firewall (tuning ↔ endpoints)

The mechanism that lets tuning and clean endpoints coexist:

1. **Version freeze within a measurement step (§2.6.3).** No study-alert `definition_version` changes *inside* an active period; changes land only at **step boundaries** and are pre-registered as **protocol amendments**. A cluster's "intervention" is therefore a fixed, named version-set for the whole period.
2. **Version as covariate/stratum.** The **PPV-ledger windowing keys before/after markers to `threshold_config` version + `alert_definition_version`** (`ppv-ledger` `method.windowing`), and the §2.5 **per-protocol sensitivity analysis stratifies by `alert_definition_version`**. A tuning event thus becomes an *analyzable covariate*, never a hidden confound.
3. **Attribution, not contamination.** Because `REQ-INV-3-2` makes every alert carry the exact version that produced it, a mid-study change's effect on M2/M3/M4 is **measured** (the before/after-tuning contrast) rather than smeared across the primary endpoint. This is the concrete payoff of INV-3 for the trial: 100% version auditability (M10) is what turns an operational necessity (tuning) into a methodologically clean event.
4. **QI/before-after (§1) is the tuning sandbox.** Calibration-driven tuning is concentrated in the §1 washout and QI phase; the confirmatory §2 runs on the version-set frozen at each step, minimizing amendments.

---

## 5. IRB / CEP Submission Considerations

A **two-tier ethics pathway** matching the two-study structure; both tiers gate on the LGPD posture and the mandatory RIPD (`VIS-C-06`, regulatory-plan.md §4 L1).

### 5.1 Tier structure

| | Study 1 — Before-After (QI) | Study 2 — Stepped-Wedge RCT |
|---|------------------------------|------------------------------|
| Ethics body | Institutional **CEP** (may treat as quality-improvement / minimal-risk) | **CEP + CONEP** (`VIS-6.2-07`, `VIS-C-16`) |
| Registration | Institutional QI registry | **ReBEC + ClinicalTrials.gov** (`VIS-6.2-07`, `VIS-C-16`) — before execution |
| Consent | **Waiver** (QI rationale, §5.3) | **Individual-consent waiver with opt-out** (institutional intervention) (`VIS-6.2-07`) |
| Oversight | QI safety monitoring (§4.1) | **Independent DSMB, quarterly** (`VIS-C-15`) |
| Risk framing | Deployment of live decision-support; minimal incremental risk | Institutional intervention, unidirectional crossover — no denial of benefit (`VIS-C-14`) |

### 5.2 LGPD data use

- **Sensitive personal data.** All processing is of *dado pessoal sensível* (health data, LGPD Art. 5º II — `VIS-C-05`), purpose-bound to clinical decision support and its evaluation (Art. 6º I).
- **Legal basis.** *Tutela da saúde* / proteção da vida e da incolumidade física (Art. 11 II "g" / Art. 7º VII) — the same basis regulatory-plan.md §4 (L2) records; the study is a secondary use of data already lawfully processed for care, not a new collection.
- **RIPD.** The mandatory *Relatório de Impacto à Proteção de Dados* (`VIS-C-06`) must cover the study data flows (chart abstraction, adjudication datasets, Gold analytics) before any real-data analysis.
- **Minimization for analysis.** Analytic datasets carry `mpi_id` (no locally-minted identifier) and **no direct identifiers** (`nome`/`CPF`/`CNS`/`mrn`) — the PHI-minimization boundary already enforced on Gold write-back (`REQ-INV-4-S3`; test-strategy.md §4.2). Adjudicators work on a controlled, access-logged chart extract; every PHI read is an `audit_trail` row (Art. 37 registro de operações; INV-1 / `CON-0066`).
- **Retention.** Study data honor the **7-year** TimescaleDB window (`VIS-C-12`); the open CFM 1.821/07 20-year *prontuário* question (data-model.md §8) is flagged for legal, not resolved here.

### 5.3 Consent-waiver rationale (QI phase, §1)

The waiver for Study 1 rests on the standard research-ethics criteria, all satisfied here:

1. **Minimal incremental risk.** The intervention is an *advisory* alert to the clinician (`VIS-C-01`, `VIS-C-08`); the physician remains the responsible decision-maker (CFM, `VIS-C-08`) and every alert is recorded to the prontuário at NGS-2 (`VIS-C-07`). The system never diagnoses or treats autonomously — it cannot, by classification (regulatory-plan.md §2).
2. **Impracticability of individual consent** for a unit-level, always-on workflow change affecting every admission — consenting per patient would bias exposure and is operationally impossible for an institutional intervention.
3. **No denial of benefit / no withholding of standard care** — control-period patients receive conventional MEWS/NEWS monitoring (existing standard, `VIS-6.1-01`); the QI deployment *adds* a safety net.
4. **Public/collective health benefit** proportionate to the minimal risk (sepsis is the #1 ICU cause of death, `VIS-3.1-01`).

For **Study 2**, the same logic supports the **consent waiver with opt-out** (`VIS-6.2-07`): the cluster-level intervention cannot be individually randomized, all clusters ultimately receive it (`VIS-C-14`), and an opt-out honors individual autonomy without breaking the design. CONEP review is mandatory because it is prospective randomized research (`VIS-C-16`).

### 5.4 Registration and oversight checklist (`VIS-6.2-07`, `VIS-C-15/16`)

- [ ] CEP approval (both studies) · CONEP approval (Study 2) — `VIS-C-16`
- [ ] ReBEC + ClinicalTrials.gov registration **before** Study 2 execution — `VIS-C-16`
- [ ] Independent DSMB charter + quarterly schedule — `VIS-C-15`, `VIS-6.2-07`
- [ ] RIPD covering study data flows — `VIS-C-06`
- [ ] SAP finalized (resolves §2.1 step-allocation flag + §2.4 power verification) before first crossover
- [ ] Consent-waiver + opt-out mechanism approved — `VIS-6.2-07`

---

## 6. Traceability summary

| Deliverable requirement | Vision / persona anchor | Section | Instrumentation / mechanism |
|-------------------------|-------------------------|---------|-----------------------------|
| Before-after design + endpoints + inclusion + duration + analysis | `VIS-6.1-01..06` | §1 | §3.1–§3.2 |
| Stepped-wedge: unit, endpoints, sample size, contamination | `VIS-6.2-01..06`, `VIS-C-14` | §2 | §3 |
| Every §7.1 metric instrumented | `VIS-7.1-01..05` | §3 (M1–M5) | lifecycle loop + chart review |
| Every §7.2 metric instrumented | `VIS-7.2-01..05` | §3 (M6–M10) | telemetry + schema (INV-3) |
| PPV from resolve-step feedback | `VIS-7.1-02` | §3 M2, §3.1 | `alert.resolution` / `fact_alert` |
| Time-to-action from audited ack→act | `VIS-7.1-03` | §3 M3 | lifecycle timestamps (INV-1) |
| Sepsis sensitivity from chart review + sampling | `VIS-7.1-01` | §3 M1, §3.2 | two-stage IPW adjudication |
| Ignored-alert rate from ack-SLA timeouts | `VIS-7.1-04` | §3 M4 | `raised → expired` timer events |
| Interim analyses + tuning governance (versioned/audited) | `VIS-C-15`, INV-3 (`REQ-INV-3-2`) | §4 | `alert_definition_version` + `audit_trail` |
| IRB/CEP: LGPD + consent-waiver | `VIS-C-05/06/14/16`, `VIS-6.2-07` | §5 | two-tier ethics pathway |
| FP/patient-day safety guardrail | `PER-CARLOS-02` (distribution: > 3-FP patient-day share ≤ 5% **and** p95 < 3), `PER-CARLOS-01` (< 30 s) | §1.3, §3 M4 | `fp_patient_day_gt3_share` + `fp_patient_day_p95` (per-patient-day distribution, `ppv-ledger` method); fleet-mean `fp_per_patient_day` diagnostic only |
| RRT mobile latency scoping (contamination) | `PER-RAFAEL-01` (< 5 s) | §2.6.2 | delivery-layer scoping |

### Open Questions (recorded per CONTRACTS §5, not resolved)

1. **`VIS-6.2-01` step allocation.** "3 clusters migrate per period" is arithmetically inconsistent with 8 clusters / 4 steps (needs 2/step). Balanced 4-sequence design assumed (§2.2); the trial biostatistician reconciles in the SAP before registration.
2. **`VIS-6.2-05` power vs design effect.** N ≈ 6,480 is arithmetically confirmed (8 × 45 × 18); the > 90% power claim at ICC = 0.02 must be verified against the SW design effect using the §1 empirical ICC/event-rate priors (§2.4).
3. **Retention horizon.** 7-year platform window (`VIS-C-12`) vs CFM 1.821/07 20-year prontuário minimum (data-model.md §8) — legal ratification pending; affects long-term study-data retention.
4. **Baseline provenance for M5/M1.** `VIS-7.1-05` mortality baseline and `VIS-7.1-01` 45% sepsis-sensitivity baseline are Fase-1 figures; the SAP must fix whether the §2 comparator is the §1 control period or the historical Fase-1 cohort.

---

*Compiled by the clinical-validation-methodologist as the executable form of `RQ-4`. The SAP (biostatistician), the RIPD (DPO, `VIS-C-06`), and CEP/CONEP submissions remain the authoritative owners of final statistical, privacy, and ethical sign-off; this plan feeds them one traceable source. Not for real-patient data until the regulatory-plan.md §8 blockers close.*
