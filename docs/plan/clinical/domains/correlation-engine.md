# Correlation Engine — Domain Specification (IntensiCare v2)

> Guild: clinical · Vision anchor: §4.1 (Correlation Engine box), Fase 2d (§5.2, VIS-5.2-04) ·
> Deliverable pair: `_work/alerts/correlation-engine.yaml`, `_work/domain-interfaces/correlation-engine.yaml` ·
> Severity scale: `normal | watch | urgent | critical` (clinical.* only) ·
> Fleet targets: PPV ≥ 0.60, ignored-rate ≤ 10% (VIS-7.1-02, VIS-7.1-04).

## 1. Clinical scope

The Correlation Engine is the **multi-domain reasoning layer** that sits above the seven Fase-2 detectors
(Sepsis, AKI, Respiratory, Hemodynamic, Delirium, Electrolyte, Drug–Drug Interaction — VIS-4-02). Its job is
not to stage any single organ system; it is to detect **causal chains and dangerous co-occurrences that no
single detector can see**, and to emit **one richer alert per chain that REPLACES its member alerts** so the
clinician sees a single, explained, actionable signal instead of a cluster of simultaneous single-domain
alarms. It is **one alarm-fatigue lever of five, not "the" lever**: on its own catalog volumes it directly
removes only a **defensible ~1–6 %** of fleet push traffic (honest arithmetic in §5.4), so the fleet
ignored-rate target (25 % → ≤ 10 %, VIS-7.1-04) is a **combined outcome of five levers** — enumerated with
their owning specs in §5.4 — never a figure this engine delivers alone. What this engine contributes is
(a) higher per-push PPV (a correlation is ≥ as specific as its most-specific member) and (b) two folding
layers that cut how many concurrent pushes a deteriorating patient generates: the pairwise causal-correlation
fold (§5.1) and the cross-domain deterioration-cluster fold (§5.2).

Vision §4.1 (VIS-4-03) fixes **exactly three cross-domain clinical correlations**; this domain implements all
three, plus one efficiency correlation carried from the `eficiencia` cluster:

| # | Correlation | Chain | Alert |
|---|-------------|-------|-------|
| 1 | **Sepsis + AKI** — "sepse é #1 causa de AKI" | septic organ dysfunction / shock → renal hypoperfusion + inflammation → KDIGO ≥ 1 | `ALERT-CORR-SEPSIS-AKI-01` (critical) |
| 2 | **Respiratory + Hemodynamic** — "SDRA + choque" | moderate/severe ARDS concurrent with shock → combined cardiopulmonary failure, RV strain | `ALERT-CORR-RESP-HEMO-02` (critical) |
| 3 | **Drug + Electrolyte** — "QTc + K⁺/Mg²⁺" | QT-prolonging drug + QTc > 500 ms + hypoK/hypoMg → Torsades substrate | `ALERT-CORR-QTC-ELEC-03` (critical, by amplification) |
| 4 | **Redundant diagnostic ordering** (efficiency/**stewardship** — **not** a deterioration correlation; excluded from the suppression-vs-amplification accounting, §5) | repeat same-class exam order within its reassessment window | `ALERT-CORR-EXAM-REDUND-04` (normal) |

**Out of scope (explicit):** the correlation engine does **not** re-derive any physiological threshold — every
member threshold is owned and cited by the member domain. It does **not** perform automatic diagnosis and does
not replace clinical judgement (VIS-C-01, VIS-C-08); a correlated alert is advisory and is recorded in the
prontuário at NGS Level 2 (VIS-C-07). ML-predictive correlation (also scheduled for Fase 2d) is a **separate,
later** deliverable and is deliberately excluded here: Fase-1/Fase-2 processing is deterministic Python, no ML
runtime in scope (VIS-2-06).

## 2. Domain-event model

Each Fase-2 detector emits **typed events** on the Redis pub/sub bus (VIS-2-08) per its own
`_work/domain-interfaces/<domain>.yaml`. The correlation engine is a **consumer of events, not of raw
quantities**: it subscribes per admitted ICU patient (see §7, admission-triggered) and maintains a bounded
per-patient buffer of the most recent member events. Every event carries `{mpi_id, encounter_id, detected_at,
alert_id, …domain fields}`; carried quantities are **already canonical** (units resolved at the member
domain's edge, `_work/units/registry.yaml`), so the engine never re-normalizes and never re-touches a raw
FiO₂/vasopressor/lactate value (the SYS-01/SYS-02/SYS-03 unit hazards are handled upstream).

Member events consumed (source domain → event):

- sepsis → `sepsis.organ_dysfunction.detected`, `sepsis.shock.detected`
- aki → `aki.stage.detected`, `aki.kdigo.stage_change`
- respiratory → `respiratory.ards.detected`
- hemodynamics → `hemodynamic.shock.detected`, `hemodynamic.vasopressor.escalating`
- drug-interaction → `drug.qtc.prolonged`
- electrolyte → `electrolyte.hypokalemia.detected`, `electrolyte.hypomagnesemia.detected`
- (efficiency) AMH Gold `ServiceRequest`/`DiagnosticReport` repeat-order signal

Events emitted (full field lists in the interface contract): `correlation.sepsis_aki.detected`,
`correlation.resp_hemo.detected`, `correlation.qtc_electrolyte.detected`, `correlation.redundant_exam.detected`,
the cross-domain `correlation.deterioration_cluster.detected` (§5.2), and the control event
`correlation.member_suppressed` (§5).

## 3. Temporal join windows

A correlation is a **temporal join** of member events on `mpi_id`+`encounter_id`. The window is chosen from
the **clinical latency of the causal chain**, not from a system default:

| Correlation | Join window | Ordering | Clinical basis |
|-------------|-------------|----------|----------------|
| Sepsis + AKI | **PT72H** | sepsis-first (AKI onset at/after sepsis onset) | SA-AKI develops hours–days after sepsis onset; KDIGO uses a 48 h creatinine window, extended to 72 h to capture delayed septic AKI (ADQI-28, Zarbock 2023). |
| Respiratory + Hemodynamic | **PT6H** | concurrent | ARDS and shock in combined cardiopulmonary failure are effectively simultaneous states; 6 h tolerates asynchronous lab/ventilator sampling. |
| Drug + Electrolyte QTc | **PT24H** | concurrent | QTc ECG, active-drug list and electrolyte result rarely coincide to the minute; 24 h binds one "current substrate" snapshot. |
| Redundant exam | **PT720H** (per-class ≤ 30 d) | prior-order-first | Reassessment windows are exam-class-specific (5/7/14/21/30 d); the outer bound is the largest class window. |

The engine evaluates a chain on **each arriving member event** (event-driven), looking back over the window for
the complementary member. Because a correlation can only fire once **both** members are present, its effective
latency is paced by the slower member's data cadence (e.g. AKI biomarker sampling), **not** by the engine's own
compute — see §9 and the interface `latency_assumption_ms`.

**Boundary convention (unit-checked).** Window edges use the same strict/inclusive discipline as the member
thresholds so test vectors are deterministic: the 72 h causal window is **inclusive up to but not beyond** 72 h
(`TV-5`/`TV-6` of SEPSIS-AKI-01); the per-class exam windows are **strict `< W`** so a repeat at exactly the
window edge is treated as legitimately due (`TV-4`/`TV-5` of EXAM-REDUND-04).

## 4. Causal chains — trigger/staging logic (typed, unit-checked)

All thresholds below are **inherited from the member domains** and re-cited here for traceability; every unit is
canonical per `_work/units/registry.yaml`. Full boolean logic, inputs and ≥ 3 test vectors (incl. boundary) per
alert are in `_work/alerts/correlation-engine.yaml`.

### 4.1 Sepsis + AKI → `ALERT-CORR-SEPSIS-AKI-01` (critical)

```
sepsis_active AND aki_active AND causal_temporal_link
  sepsis_active := sepsis.organ_dysfunction.detected OR sepsis.shock.detected           within PT72H
  aki_active    := aki.stage.detected, kdigo_stage >= 1                                  within PT72H
                   (creatinina rise >= 0.3 mg/dL / PT48H  OR  creatinina >= 1.5x baseline
                    OR  debito_urinario_horario < 0.5 mL/kg/h for >= PT6H)
  causal_link   := aki_onset_at  within PT72H  at-or-after  sepsis_onset_at
```

- **Units:** `creatinina` mg/dL, `debito_urinario_horario` mL/kg/h (needs a validated `peso` — SYS-09 weight
  parse hazard is handled by the AKI domain edge), `lactato_arterial` mmol/L, timestamps in epoch seconds.
- **Evidence:** ADQI-28 SA-AKI consensus (Zarbock, *Nat Rev Nephrol* 2023); Bagshaw *CJASN* 2007 (sepsis = leading
  ICU-AKI cause); KDIGO-2012 (stage anchors); SSC-2021 (Evans, *Crit Care Med* 2021); vision VIS-3.2-01, VIS-4-03.
- **Rule refs:** none directly adoptable — the legacy sepsis-oliguria rule `RULE-SEPSE-014` is **P0 / RATIFY**
  (dead `fromkeys` DRC gate + weight-strip bug, ESC-P0-08) and MUST NOT be ported; the correlation is built on the
  **corrected** AKI-domain KDIGO event, not on RULE-SEPSE-014. See §6.

### 4.2 Respiratory + Hemodynamic → `ALERT-CORR-RESP-HEMO-02` (critical)

```
ards_moderate_or_severe AND shock_active                                    joined within PT6H
  ards_moderate_or_severe := respiratory.ards.detected,
                             relacao_pao2_fio2 <= 200 ratio  OR  relacao_spo2_fio2 <= 235 ratio
  shock_active            := hemodynamic.shock.detected
                             OR (pressao_arterial_media < 65 mmHg AND dose_vasopressor > 0 mcg/kg/min)
```

- **Units:** `relacao_pao2_fio2`/`relacao_spo2_fio2` dimensionless ratio — **FiO₂ MUST be the canonical fraction
  0–1** or the P/F ratio is ~100× too small (SYS-01); this is enforced at the respiratory-domain edge.
  `pressao_arterial_media` mmHg; `dose_vasopressor` mcg/kg/min — mL/h is **not** convertible without concentration
  + weight (CON-0060 / SYS-C-04), so this consumes the hemodynamics conversion-service output only.
- **Evidence:** Berlin Definition (*JAMA* 2012, moderate P/F ≤ 200); SEPSISPAM (Asfar, *NEJM* 2014, MAP ≥ 65);
  Vieillard-Baron *ICM* 2016 (acute cor pulmonale in ARDS — rationale for the combined alert); VIS-3.3, VIS-3.4-01.

### 4.3 Drug + Electrolyte QTc → `ALERT-CORR-QTC-ELEC-03` (critical, **amplification**)

```
qtc > 500 ms
  AND qt_prolonging_drug_count >= 1                       (CredibleMeds Known-Risk active)
  AND (potassio < 3.5 mmol/L OR magnesio < 0.7 mmol/L)    joined within PT24H
```

- **Units:** `qtc` ms (guard `0.48 s` → 480 ms at edge); `qt_prolonging_drug_count` count; `potassio`,
  `magnesio` mmol/L (Mg²⁺ divalent — mEq/L is **not** 1:1, factor 0.5, per registry).
- **Amplification, not just suppression:** individually the QTc arm (DDX-001b) and the electrolyte arms
  (ELY-002c hypokalemia-trend, ELY-006c hypomagnesemia-context) are WARN. Their **co-occurrence is the classic
  reversible TdP substrate** (Drew, *Circulation* 2010 AHA/ACCF), so the correlation **escalates to critical** and
  surfaces the correctable trigger. This is the one correlation where the fused severity is *higher* than any
  member — the correlation exists precisely because neither WARN alone conveys the arrhythmia risk.
- **Evidence:** Drew *Circulation* 2010; Tisdale *Circ CQO* 2013; CredibleMeds QTdrugs; VIS-3.7-02, VIS-3.6-02/09.

### 4.4 Redundant diagnostic ordering → `ALERT-CORR-EXAM-REDUND-04` (normal)

Per-class window test: a new exam order fires if a prior **same-class** order/result lies within that class's
reassessment window `W(class)` (hemograma 5 d, bioquímica 7 d, RX tórax rotina 14 d, marcadores tireoide 21 d,
sorologias 30 d). **Corrected** from `RULE-EFICIENCIA-007`'s legacy defect, which summed positive window-hits
**across unrelated classes** into one undifferentiated threshold (ADAPT — same cost/burden intent, fixed
mechanism). This is an **efficiency/stewardship** alert (`category: efficiency-stewardship`), **not** a
deterioration correlation: it is standalone and folds **no** member alert, so it is **excluded from the
suppression-vs-amplification accounting** (§5, B3-004); severity `normal` additionally keeps it out of the
deterioration-alarm attention budget. Evidence: RULE-EFICIENCIA-007 (ADAPT) + Choosing Wisely critical-care
policy (Halpern, *Crit Care Med* 2014).

## 5. Folding, amplification, and the honest alarm-fatigue accounting

The engine reduces *delivered pushes* through **two folding layers** — a pairwise **causal-correlation** fold
(§5.1) and a cross-domain **deterioration-cluster** fold (§5.2) — plus, for one chain, an explicit
**amplification** (§5.1). §5.3 states the two safety invariants both layers obey; §5.4 gives the honest,
arithmetic-bounded contribution of the engine to the fleet fatigue target and names the other levers that carry
the rest.

### 5.1 Pairwise causal-correlation fold + amplification (chains 1/2/3)

A causal correlation **REPLACES** its member alerts with one new, richer, self-explaining alert. When a clinical
correlation (1/2/3) fires, the engine emits `correlation.member_suppressed` to the alert dispatcher with
`{correlation_alert_id, suppressed_member_alert_ids, suppress_until, reason}`. For the correlation's dedup/cooldown
window the dispatcher **pushes only the correlation** and **folds** the member alerts. Chain 3 additionally
**amplifies** — two WARN members become one `critical` (the TdP substrate, §4.3). This is the fold the three
vision-sanctioned pairs (VIS-4-03) produce; it does **not** cover a deterioration that lights up EWS + Sepsis +
Hemo without matching one of the three pairs — that residual is the job of §5.2.

**BREAK-THROUGH rule — the fold cooldown is a concurrency dedup, never a silence for escalation (HAZ-026-safe,
HAZ-027-safe) — [RT2-PATIENT-SAFETY-01].** The fold suppresses only the **re-push of a member instance that was
already concurrent with the correlation at push time**. It NEVER suppresses a severity escalation or a new
interruptive member. On **each evaluation cycle** the engine **re-evaluates every folded member's current
severity**, and:

- a **NEW member alert** that joins an existing fold at severity **≥ urgent** — a member instance not part of the
  correlation at push time (e.g. `ALERT-SEPSIS-SHOCK-03` firing at hour 6 of a live `ALERT-CORR-SEPSIS-AKI-01`
  fold, or an AKI KDIGO stage-3 event arriving after a stage-1 member was folded) — **RE-NOTIFIES IMMEDIATELY at
  its own delivery tier**, regardless of the correlation's cooldown (`PT12H`/`PT4H`/`PT8H`);
- a **severity INCREASE within any folded member domain** (`watch→urgent→critical`) likewise **breaks through and
  re-pages at the higher tier** the same cycle it is detected;
- only a member re-firing at **unchanged-or-lower** severity, **still concurrent** with the live correlation, is
  folded.

This **composes with, and never overrides,** the never-suppress-critical invariant (§5.3 inv. 2; `alert-routing.md`
§4 banner; `architecture/alert-engine.md` §5 carve-outs; HAZ-026): `critical`/`urgent` are never budget-suppressed,
rate-limited, or maintenance-muted, and the fold cooldown is **not** an exception to that for a new or escalating
member. The §6 recommended default ("never fold across a *higher* member severity than the correlation's own") is
**necessary but not sufficient on its own**: because all three correlations are themselves `critical`, an
*equal-severity* `critical` member would otherwise fold silently — the break-through rule closes exactly that gap
(a new-or-escalating `critical` member delivers even when the correlation is already `critical`). Verified by the
`SEPSIS-AKI-01` break-through test vectors (`_work/alerts/correlation-engine.yaml`).

### 5.2 Cross-domain deterioration-cluster fold (shared-physiology suppression group) — [RT1-ALARM-FATIGUE-02]

The three pairwise correlations catch three *specific* causal pairs. They do **not** catch the common case where
**one physiological deterioration co-fires several domains at once** — e.g. an evolving septic shock that
simultaneously trips the **EWS** trend (NEWS2/MEWS rising), the **Sepsis** screen / organ-dysfunction alert, and
the **Hemodynamic** shock / vasopressor alert off the *same* falling MAP + rising lactate. `Sepsis↔EWS`,
`Sepsis↔Hemo` and `EWS↔Hemo` are **not** among the three pairs, so without a further net a single decompensation
delivers many concurrent urgent/critical pushes for one patient, each counted as an independent alert. The
**deterioration-cluster fold** is the presentation-layer net that closes this gap: concurrent deterioration
pushes that share a patient, a time window, and a physiological driver are folded into **ONE
`deterioration-cluster` notification** (`correlation.deterioration_cluster.detected`). Machine form in
`_work/alerts/correlation-engine.yaml` (`cross_domain_grouping:` → `GROUP-CORR-DETERIORATION-CLUSTER-01`).

- **Grouping key** = `mpi_id + encounter_id` **AND** an **overlapping cluster window** **AND** a **shared
  physiological driver**:
  - *Cluster window* — the member pushes must fall inside a rolling **`cluster_window` (default PT1H, config,
    RAT-CORR-01)**. The fold is about *concurrency*, so the window is short (a fraction of the members' cooldowns),
    **not** a causal-latency window like §3's PT72H; two pushes more than `cluster_window` apart are separate
    clusters.
  - *Shared physiological driver* — the concurrent members must be driven by the **same overlapping input axis**,
    read from the triggering-input sets the members already carry (no re-derivation, §2). Two named axes cover the
    co-fire cases the finding lists: **(a) perfusão/circulatório** — falling `pressao_arterial_media`, rising
    `lactato_arterial`, rising `dose_vasopressor`, rising HR / falling SBP → co-fires EWS + Sepsis + Hemo;
    **(b) respiratório** — falling `spo2`/`relacao_pao2_fio2`, rising `fio2` / RR → co-fires EWS + Sepsis +
    Respiratory. A cluster **names its driver** in the notification so the clinician sees *what one thing* is
    deteriorating. Members with **no** shared input axis are **not** folded — they are genuinely independent
    problems and must stay separate pushes.
- **What folds.** Any concurrent deterioration push (severity `watch`/`urgent`/`critical`) for that key —
  including a **fired pairwise correlation** (§5.1) plus a leftover member the pair did not fold, or two/three
  bare domain alerts when no pairwise correlation applies. The efficiency/stewardship chain 4 and any
  `normal`-band advisory are **never** cluster members (B3-004; only deterioration signals cluster).
- **The cluster notification** carries: **`severity = max(member severities)`**; the **ordered member list** with,
  per member, its **own severity, triggering parameter + value + trend, and evidence citation intact** (§8
  explainability applies per member — nothing is summarized away); the **named driver**; and each member's
  deep-link so the clinician can open any single-domain detail. It emits `correlation.deterioration_cluster.detected`
  and one `correlation.member_suppressed` per folded member.
- **Delivery.** The single cluster push is delivered on the **highest member's delivery tier** — a `critical`
  member still pages the RRT on the Tier-1 path (`severity-model.yaml`; `alert-triage.md §1`), so folding **cuts
  the number of interruptions without demoting the loudest one**. The cluster fold **composes with, and never
  overrides**, the alert-engine / alert-routing invariant that `critical`/`urgent` are never budget-suppressed,
  rate-limited or maintenance-muted — a fold is one richer push at the top severity, not a dropped or delayed one.
- **Accounting.** In the fatigue metrics a cluster is recorded as **N members folded → 1 delivered push**
  (delivered-push count drops by `N−1`); each folded member still counts **individually** toward PPV
  (`ppv-ledger-draft.yaml`), so the fold feeds only the push-count / ignored-rate reduction and never inflates PPV
  (§5.4).

### 5.3 Two safety invariants both folding layers obey

1. **No signal is lost from the record — folding ≠ suppression.** Every member alert is still **computed**, still
   individually **dispositionable**, and still written to the prontuário at NGS-2 (VIS-C-07); only the *push* is
   deduplicated. The member's content (parameter, value, trend, threshold, evidence) is preserved verbatim inside
   the fold, never collapsed to a bare count. This reuses the corrected acknowledgement/rollup semantics of
   `RULE-ALERTAS-006`/`-007`/`-010` (ADAPT) and the dedup/cooldown intent of `RULE-ALERTAS-016` (ADAPT), lifted
   from ad-hoc bed-type React plumbing to an explicit severity-rank fold.
2. **Folding never downgrades severity.** The folded alert's severity is `max(member severities)` (pairwise chains
   1–2 and every deterioration cluster) or an explicit **amplification** to `critical` (chain 3). This is the
   direct fix for the legacy last-writer-wins bug `RULE-PIORA-CLINICA-010` / `RULE-ALERTAS-003` (P0/DISCREPANCY)
   where a later AMARELO could silently overwrite an earlier VERMELHO — v2 uses an explicit severity-rank
   comparison, never alphabetical sort (`RULE-ALERTAS-010`) and never loop-order overwrite, and a `critical`
   member is never masked under a lower-severity summary (HAZ-026-safe).

### 5.4 Honest alarm-fatigue accounting — the engine is one lever of five — [RT1-ALARM-FATIGUE-03]

**What the engine directly removes.** The **3 clinical correlations** fire ≈ **4/100 beds/day** (SEPSIS-AKI 2 +
RESP-HEMO 1 + QTC-ELEC 1; EXAM-REDUND is net-additive, excluded per B3-004), each folding ≥ 2 members — so the
pairwise layer folds on the order of **~8 member pushes** and nets **~4 fewer delivered pushes** per 100 beds/day.
Against the summed fleet catalog volume of **≈ 137 pushes/100 beds/day** (Σ `est_volume_per_100_beds_day` over the
ten `_work/alerts/*.yaml` catalogs) that is a **gross fold of ~6 % and a net push reduction of ~1–3 %**. The
cross-domain cluster fold (§5.2) adds further reduction whenever a decompensation co-fires domains, but its
magnitude scales with **co-fire frequency, which is not yet measured** — so the engine's **total
directly-attributable push reduction is a defensible ~1–6 %**, an order of magnitude short of a 15-point
ignored-rate swing. **This engine does not, and is not claimed to, carry the 25 % → ≤ 10 % target by itself.**

**The levers that actually carry ignored-rate 25 % → ≤ 10 % (VIS-7.1-04)**, each owned elsewhere:

| # | Lever | What it does for fatigue | Owning spec |
|---|-------|--------------------------|-------------|
| 1 | **Per-alert PPV budgets** | every alert ships a `ppv_budget` (target PPV ≥ 0.60) so low-value alerts never enter the stream | each `_work/alerts/*.yaml` `ppv_budget`; ledger `_work/budgets/ppv-ledger-draft.yaml` |
| 2 | **Suppression machinery** (dedup / cooldown / rate-limit / maintenance / budget-coalescing) | collapses duplicate and low-tier volume before delivery | `architecture/alert-engine.md §5`; `design/screens/alert-routing.md §4` |
| 3 | **Severity-tiered delivery** | only `urgent`/`critical` interrupt; `watch`/`normal` go to badge/digest, not a push | `_work/platform/severity-model.yaml`; `design/screens/alert-triage.md §1` |
| 4 | **Cross-domain folding** (this engine) | §5.1 pairwise + §5.2 deterioration-cluster — the ~1–6 % above | `clinical/domains/correlation-engine.md §5` (here) |
| 5 | **Threshold tuning loop** | per-alert PPV-vs-volume governance retunes noisy alerts over time | `design/screens/admin-config.md §3`; ppv-ledger tuning recommendation; US-23/US-25/US-26 |

The 25 % → ≤ 10 % figure is the **combined, measured** outcome of levers 1–5 validated against real fleet
telemetry, **not** a quantity this engine produces alone. Whether the five together close the full gap is a
fleet-level empirical question **routed to C3** (ppv-ledger fleet-target validation); this doc claims only lever 4
and its bounded ~1–6 %. **Chain 4 (`ALERT-CORR-EXAM-REDUND-04`) is excluded from all of the above accounting
(B3-004):** it is an efficiency/stewardship alert that folds **no** member and is net-additive (+2 volume, still
counted in the fleet total), so the fatigue math must not credit it with member suppression.

## 6. RATIFY-pending rules — designed-to-default

Per CONTRACTS (evidence discipline; RATIFY policy), rules that cannot be decided by agents are designed to the
**recommended default** and marked **pending RAT-***; the engine is built so the eventual ratification changes a
parameter, not the architecture.

- **`RULE-SEPSE-014` (P0 / RAT-SEPSE-*, ESC-P0-08):** the legacy septic-oliguria criterion is structurally dead
  (a `vars(...).fromkeys(...)` DRC gate that can never be True) and carries the SYS-09 weight-strip bug. **Not
  ported.** The Sepsis+AKI correlation consumes the **corrected AKI-domain KDIGO event** instead of this rule;
  the ADQI-28 SA-AKI definition is the recommended default. Pending the sepsis cluster's RAT for the oliguria
  criterion, the correlation is unaffected because it does not depend on RULE-SEPSE-014's predicate.
- **Suppression aggression (fleet policy, pending RAT-CORR-01, recommended default):** how aggressively a
  correlation folds its members is a product-safety choice. **Recommended default:** fold members for the
  correlation's cooldown window, always keep the member in the prontuário, and never fold across a *higher*
  member severity than the correlation's own. This mirrors the AMBIGUOUS-band alert rollup questions
  `RULE-ALERTAS-014` (RAT-ALERTAS-03) and the counting-primitive questions `RULE-ALERTAS-001`/`-002`
  (RAT-ALERTAS-01/02); the engine reads a single `suppression_policy` config so ratification flips a flag.
- **`RULE-EFICIENCIA-007` (ADAPT):** adopted with the per-class-window correction (§4.4); no RATIFY needed, but
  the exact class→window map is an institutional parameter surfaced for clinical sign-off.

No correlation threshold is silently invented: chains 1–3 cite published guidelines directly and inherit member
thresholds; chain 4 cites its ADAPT rule + Choosing Wisely.

## 7. Interactions with other domains

- **Admission-triggered subscription (`RULE-TRILHAS-ENGINE-011` ADAPT, `#admission-triggered-domains`):** on ICU
  admission (`Encounter` from AMH Gold) the engine subscribes the patient to the relevant member-event streams —
  replacing the legacy `CriarTrilhas` use case that hard-coded four manual trilha rows per prontuário. Enablement
  is by care-context, not bed-type.
- **Domain routing (`RULE-TRILHAS-ENGINE-001` SUPERSEDE, `#domain-routing`):** the legacy bed-type-keyed pathway
  composition (`TrilhaSepseV3`, etc.) is superseded by domain-based routing off AMH Gold; the correlation engine
  is the consumer side of that routing, joining detector events rather than static pathway model-lists.
- **Consumes** events from all six clinical detectors (§2). **Emits** `correlation.*` events consumed by the
  alert dispatcher (for the member fold) and written to AMH Gold `fact_alert` (ADR-001 C-04) for corporate
  analytics and the trial's alarm-fatigue outcome (VIS-6.2-04).
- **Redundant-exam correlation** consumes AMH Gold `ServiceRequest`/`DiagnosticReport` directly (order history),
  the one member that is not a physiological detector event.

## 8. Explainability output

Every correlated alert is **self-explaining**: it lists its **member events + evidence** so the clinician sees
*why* the two domains linked. The emitted event and the pushed alert carry, per correlation:

- the **member event refs** (`sepsis_event_ref`+`aki_event_ref`, `ards_event_ref`+`shock_event_ref`,
  `qtc_event_ref`+`electrolyte_event_ref`) with their timestamps and the **causal lag** (e.g. `causal_lag_h`);
- the **triggering values** in canonical units (kdigo_stage, lactato, P/F, MAP, vasopressor dose, QTc, K⁺, Mg²⁺);
- the **evidence citations** (guideline/paper) backing the chain;
- the **member alerts it suppressed** (`member_alerts_suppressed`) so the clinician can drill into any folded
  single-domain detail.

This satisfies the SaMD-Classe-II advisory posture (VIS-C-01/-C-08, decision stays with the physician) and the
100%-auditable algorithm-versioning requirement (VIS-C-13): the correlation records exactly which member events,
thresholds and evidence produced it.

## 9. Latency, volume, SLO posture

The engine's own compute (a bounded temporal join over recent per-patient events) is sub-second; the interface
declares `latency_assumption_ms: 8000` as the compute+dispatch budget once both members are present. The
**binding** latency is (a) member-event arrival, itself bounded by the AMH Gold batch pipeline P95 < 30 min
(ADR001-F-02) rather than the vision < 30 s ingestion-to-alert SLO (VIS-C-09) — the batch path cannot meet 30 s
today, and ADR-001 names a dedicated MSK streaming channel as the Fase-4 escape hatch — and (b) the **join window
itself** (a correlation cannot fire before its slower member exists). Correlated-alert volume ≈ 6/100 beds/day
(SEPSIS-AKI 2 + RESP-HEMO 1 + QTC-ELEC 1 + EXAM-REDUND 2). The **3 clinical correlations** each fold ≥ 2 member
alerts and the deterioration-cluster fold (§5.2) folds concurrent co-fires, for a **bounded ~1–6 % direct push
reduction — see the honest accounting in §5.4** (the engine is one alarm-fatigue lever of five, not the whole
25 % → ≤ 10 % swing). The EXAM-REDUND 2 is an efficiency/stewardship addition (net-additive, folds no member) and
is **excluded from the suppression accounting** (B3-004), though its +2 volume stays in the fleet total.

## 10. Open questions

- **OQ-CORR-01 (units registry gap):** KDIGO stage is a derived **ordinal 0–3** consumed from the AKI domain, but
  `_work/units/registry.yaml` has no `kdigo_stage` parameter. Designed to the mission-canonical dimensionless
  `points`/`enum` primitive for now; **recommend adding a `kdigo_stage` parameter (quantity `aki_stage`, ordinal
  0–3, enum/points)** to the registry so the correlation input unit is first-class rather than typed `enum`.
- **OQ-CORR-02 (exam-class taxonomy):** the per-class reassessment windows (§4.4) assume an exam-class taxonomy
  and class→window map not yet in the briefs; surfaced for clinical/informatics sign-off (institutional parameter).
- **OQ-CORR-03 (suppression policy ratification):** the recommended-default suppression aggression (§6) should be
  ratified once (RAT-CORR-01) alongside the alert-rollup AMBIGUOUS items (RAT-ALERTAS-01/02/03) so the fleet has a
  single alarm-fold policy.

---

```yaml domain-inputs
domain: correlation-engine
inputs:
  # Member domain EVENTS (carried quantities already canonical per _work/units/registry.yaml).
  - {name: sepsis_event, type: enum, unit: enum, source: "sepsis domain {sepsis.organ_dysfunction.detected, sepsis.shock.detected}"}
  - {name: kdigo_stage, type: enum, unit: enum, source: "aki domain aki.stage.detected (ordinal 0-3; OQ-CORR-01)"}
  - {name: creatinina, type: quantity, unit: mg/dL, source: "aki domain aki.stage.detected (LOINC 2160-0)"}
  - {name: debito_urinario_horario, type: quantity, unit: mL/kg/h, source: "aki domain aki.stage.detected (requires validated peso, SYS-09)"}
  - {name: lactato_arterial, type: quantity, unit: mmol/L, source: "sepsis domain event (LOINC 2524-7)"}
  - {name: relacao_pao2_fio2, type: quantity, unit: ratio, source: "respiratory domain respiratory.ards.detected (FiO2 canonical fraction, SYS-01)"}
  - {name: relacao_spo2_fio2, type: quantity, unit: ratio, source: "respiratory domain respiratory.ards.detected"}
  - {name: ards_severity, type: enum, unit: enum, source: "respiratory domain event field {leve, moderada, grave}"}
  - {name: pressao_arterial_media, type: quantity, unit: mmHg, source: "hemodynamics domain event (LOINC 8478-0)"}
  - {name: dose_vasopressor, type: quantity, unit: mcg/kg/min, source: "hemodynamics domain event (conversion service, CON-0060/SYS-C-04)"}
  - {name: qtc, type: quantity, unit: ms, source: "drug-interaction domain drug.qtc.prolonged (LOINC 44974-4)"}
  - {name: qt_prolonging_drug_count, type: quantity, unit: count, source: "drug-interaction domain event (CredibleMeds Known-Risk active drugs)"}
  - {name: potassio, type: quantity, unit: mmol/L, source: "electrolyte domain electrolyte.hypokalemia.detected (LOINC 6298-4)"}
  - {name: magnesio, type: quantity, unit: mmol/L, source: "electrolyte domain electrolyte.hypomagnesemia.detected (LOINC 19123-9)"}
  - {name: exam_class, type: enum, unit: enum, source: "AMH Gold ServiceRequest category (exam-class taxonomy, OQ-CORR-02)"}
  - {name: prior_order_within_window, type: boolean, unit: boolean, source: "AMH Gold ServiceRequest/DiagnosticReport (same-class prior within W(class))"}
  - {name: sepsis_onset_at, type: quantity, unit: s, source: "sepsis domain event detected_at (epoch seconds)"}
  - {name: aki_onset_at, type: quantity, unit: s, source: "aki domain event detected_at (epoch seconds)"}
alerts:
  - ALERT-CORR-SEPSIS-AKI-01
  - ALERT-CORR-RESP-HEMO-02
  - ALERT-CORR-QTC-ELEC-03
  - ALERT-CORR-EXAM-REDUND-04
rule_refs:
  - RULE-TRILHAS-ENGINE-001   # SUPERSEDE -> #domain-routing (event-based routing replaces bed-type pathway lists)
  - RULE-TRILHAS-ENGINE-011   # ADAPT     -> #admission-triggered-domains (admission subscription)
  - RULE-EFICIENCIA-007       # ADAPT     -> #redundant-exam-ordering (per-class window correction)
  - RULE-ALERTAS-006          # ADAPT     -> severity-rank fold (member rollup)
  - RULE-ALERTAS-007          # ADAPT     -> unattended-severity surfacing
  - RULE-ALERTAS-010          # ADAPT     -> explicit severity-rank (not alphabetical sort)
  - RULE-ALERTAS-016          # ADAPT     -> dedup/cooldown suppression
interfaces:
  consumes:
    - {quantity: lactate, unit: mmol/L, source: "sepsis domain event"}
    - {quantity: quick_sofa, unit: points, source: "sepsis domain event"}
    - {quantity: mean_arterial_pressure, unit: mmHg, source: "sepsis/hemodynamics domain event"}
    - {quantity: serum_creatinine, unit: mg/dL, source: "aki domain event"}
    - {quantity: urine_output_rate_indexed, unit: mL/kg/h, source: "aki domain event"}
    - {quantity: kdigo_stage, unit: enum, source: "aki domain event (OQ-CORR-01)"}
    - {quantity: pf_ratio, unit: ratio, source: "respiratory domain event"}
    - {quantity: sf_ratio, unit: ratio, source: "respiratory domain event"}
    - {quantity: weight_indexed_vasopressor_rate, unit: mcg/kg/min, source: "hemodynamics domain event"}
    - {quantity: shock_index, unit: ratio, source: "hemodynamics domain event"}
    - {quantity: corrected_qt_interval, unit: ms, source: "drug-interaction domain event"}
    - {quantity: count, unit: count, source: "drug-interaction domain event (qt_prolonging_drug_count)"}
    - {quantity: serum_potassium, unit: mmol/L, source: "electrolyte domain event"}
    - {quantity: serum_magnesium, unit: mmol/L, source: "electrolyte domain event"}
  emits_events:
    - correlation.sepsis_aki.detected
    - correlation.resp_hemo.detected
    - correlation.qtc_electrolyte.detected
    - correlation.redundant_exam.detected
    - correlation.deterioration_cluster.detected   # cross-domain shared-physiology fold (§5.2, GROUP-CORR-DETERIORATION-CLUSTER-01)
    - correlation.member_suppressed
```
