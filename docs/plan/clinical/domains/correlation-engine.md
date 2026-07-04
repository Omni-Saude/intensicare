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
alarms. This is the central alarm-fatigue lever (baseline ignored-rate 25% → goal ≤ 10%, VIS-7.1-04).

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
and the control event `correlation.member_suppressed` (§5).

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

## 5. Suppression vs amplification (the alarm-fatigue mechanism)

A correlation **REPLACES** its member alerts. When a clinical correlation (1/2/3) fires, the engine emits
`correlation.member_suppressed` to the alert dispatcher with `{correlation_alert_id, suppressed_member_alert_ids,
suppress_until, reason}`. For the correlation's dedup/cooldown window the dispatcher **pushes only the
correlation** to the clinician and **folds** the member alerts. Two invariants protect safety:

1. **No signal is lost from the record.** Each member alert is still computed and still written to the prontuário
   at NGS-2 (VIS-C-07); suppression is a *presentation* fold, never a *computation* skip. This reuses the
   corrected acknowledgement/rollup semantics of `RULE-ALERTAS-006`/`-007`/`-010` (ADAPT) and the dedup/cooldown
   intent of `RULE-ALERTAS-016` (ADAPT), lifted from ad-hoc bed-type React plumbing to an explicit severity-rank
   fold.
2. **Suppression never downgrades severity.** The correlation's severity is `max(member severities)` for chains
   1–2 and an explicit **amplification** to critical for chain 3. This is the direct fix for the legacy
   last-writer-wins bug `RULE-PIORA-CLINICA-010` / `RULE-ALERTAS-003` (P0/DISCREPANCY) where a later AMARELO could
   silently overwrite an earlier VERMELHO — v2 uses an explicit severity-rank comparison, never alphabetical sort
   (`RULE-ALERTAS-010`) and never loop-order overwrite.

Net effect on the alarm budget: the **3 clinical deterioration correlations (1/2/3)** **replace ~9–10 member
pushes/100 beds/day** (each folds ≥ 2 members), lifting per-push PPV (correlations are ≥ as specific as
their most-specific member) while cutting push count — both levers of VIS-7.1-02 / VIS-7.1-04. **Chain 4
(`ALERT-CORR-EXAM-REDUND-04`) is excluded from this suppression-vs-amplification accounting (B3-004):** it is an
efficiency/stewardship alert that folds **no** member and is net-additive (+2 volume, still counted in the fleet
total), so the fatigue math must not credit it with member suppression.

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
(SEPSIS-AKI 2 + RESP-HEMO 1 + QTC-ELEC 1 + EXAM-REDUND 2), with a **net reduction** in total pushes driven by the
**3 clinical correlations** (each folds ≥ 2 member alerts). The EXAM-REDUND 2 is an efficiency/stewardship
addition (net-additive, folds no member) and is **excluded from the suppression accounting** (B3-004), though its
+2 volume stays in the fleet total.

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
    - correlation.member_suppressed
```
