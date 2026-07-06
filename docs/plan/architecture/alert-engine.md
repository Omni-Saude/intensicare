# Alert Engine Architecture — IntensiCare v2

**Owner:** alert-engine-architect · **Status:** draft for reconciliation barriers **C2** (severity + lifecycle) and **C3** (latency + PPV) · **Authority precedence:** ADR-001 ≻ vision ≻ directive ≻ audit (CONTRACTS §5).

This document specifies the evaluation engine that turns AMH-Gold and operational clinical data into audited, deliverable alerts. Every number cites a source: a brief fact id (`VIS-*`, `ADR001-*`, `IMP-*`, `DM-*`, `CAT-*`, `SYS-*`, `P0-*`), a ledger constraint (`CON-*`), or an invariant (`INV-1..6`). Nothing clinical is invented here — clinical cutoffs live in the alert catalog and the units registry; this doc is the *machinery*.

> **Platform reality this engine consumes (ADR-001).** IntensiCare implements **no ingestion of its own** and reads clinical data **only from the AMH Gold layer via Amazon Athena** (`ADR001-C-01`/`CON-0001`). The Gold batch pipeline freshness is **p95 < 30 min** for Silver-Entities (`ADR001-F-02`) and the inherited data-availability SLO is **99.5%** (`ADR001-C-10`/`CON-0010`). PostgreSQL/TimescaleDB is **operational-only** — computed scores, active alerts, threshold configs — never an analytical store (`ADR001-C-03`/`CON-0003`). Historical scores/alerts are written back to Gold `fact_patient_score` / `fact_alert` (`ADR001-C-04`/`CON-0004`). This batch reality is the single most load-bearing fact in the latency decomposition below.

---

## 1. Evaluation architecture

The engine is a **consumer**, not an ingester. Two runners share one alert-definition registry, one suppression layer, one lifecycle state machine, one delivery layer, and one audit writer:

- **Micro-batch runner** — scheduled ARQ jobs (`IMP-3.2-06`) poll AMH Gold via Athena (`ADR001-C-01`) at a per-domain cadence. Each poll is **incremental** (high-watermark on `ingested_at` / Gold snapshot id), normalizes to canonical units at the edge, evaluates alert-definitions whose `evaluation_mode ∈ {micro_batch, hybrid}`, persists scores/alerts to the operational store, and periodically writes back to Gold `fact_patient_score`/`fact_alert` (`DM-AMH-03`/`-04`, `CON-0027`/`CON-0028`).
- **Near-real-time (NRT) runner** — event-driven. A new operational row (a `vital_sign` hypertable insert, or a freshly computed `clinical_score`) enqueues an evaluation of `evaluation_mode ∈ {near_real_time, hybrid}` definitions for that one patient, then persists and delivers immediately. This is the path US-01/02/03 depend on (`IMP-2.2-01..03`: vitals stored <5s, MEWS <30s, alert <5s).
- **Correlation engine** (Fase 2d, `VIS-5.2-04`) — a second-pass evaluator over persisted domain alerts/scores implementing the three vision cross-domain correlations (`VIS-4-03`): Sepsis+AKI, Respiratory+Hemodynamic, Drug+Electrolyte. Runs at hybrid/micro-batch cadence; out of scope for the MVP stage budget.

### 1.1 Per-domain evaluation-mode matrix

Mode is dictated by **(a)** where the data physically lands (Gold-via-Athena vs the operational store) and **(b)** the clinically required latency. Sources: vision §4.2 data-source table (`VIS-4.2-01..07`), vision §3 latency justifications, catalog data-availability (`DATA-AVAIL-01..09`).

| Domain | Primary source(s) | Cadence (`VIS-4.2-*`) | Required latency | **Mode** | Justification |
|---|---|---|---|---|---|
| **Early-warning scores** (MEWS / NEWS2 / qSOFA bedside) | Vitals HR/RR/temp/BP/SpO₂/AVPU → operational hypertable | continuous / per vitals set | score <30s, alert <5s (`IMP-2.2-02/03`) | **near-real-time** | Vitals land in `vital_sign` at high frequency; event-driven eval is the only way to hit <30s. **This is the sole path that requires a sub-batch data feed to honor `VIS-C-09` under `ADR001-C-01`** — see §1.2. |
| **Sepsis** | qSOFA vitals (operational, NRT) **+** lactato/PCT/WBC/cultura (Gold) | vitals continuous; labs on-result / 5 min (`VIS-4.2-01`) | early detection <1h (`VIS-3.1-01`) | **hybrid** | Bedside qSOFA components NRT; lab confirmation micro-batch. Lab arrival (Gold batch ≤30 min) dominates end-to-end — acceptable against the <1h clinical target. |
| **AKI (KDIGO)** | Creatinine + hourly urine output (Gold + operational balance) | every 1–6h (`VIS-4.2-02`) | reduce recognition by 6h (`VIS-6.1-02`) | **micro-batch** | Creatinine is lab-cadence; 30-min Gold freshness ≪ 6h target. No NRT need. |
| **Electrolytes** | Electrolyte panel (Gold, on lab result) | on lab result (`VIS-4.2-06`) | K⁺/Na⁺/Ca²⁺ fatal in minutes–hours (`VIS-3.6-01`) | **micro-batch (expedited poll)** | Lab-only source ⇒ Gold path. Highest-acuity CRIT band (K⁺>6.5, `VIS-3.6-02`) ⇒ tighten the lab-partition poll to ~1–2 min to minimize the *poll* stage; **source freshness stays AMH-batch-bound (flagged risk)** — strongest micro-batch candidate for the streaming escape hatch (§1.2). |
| **Hemodynamic** | Continuous BP/HR (invasive monitor, operational) **+** lactate (Gold) | continuous; lactate lab (`VIS-4.2-04`) | shock index sustained >15 min (`VIS-3.4-02`) | **hybrid / NRT** | Shock index needs a continuous monitor stream → NRT; lactate clearance is micro-batch. |
| **Respiratory** | SpO₂/FiO₂ (ventilator/monitor, operational) **+** blood gas (Gold) | every 5 min; ABG lab (`VIS-4.2-03`) | ventilatory deterioration >20% in 6h (`VIS-3.3-05`) | **hybrid / NRT** | SpO₂/FiO₂ ratio is continuous-monitor-driven → NRT; PaO₂/PaCO₂ ABG is micro-batch. |
| **Drug interactions** | MedicationRequest / MedicationAdministration (Gold) | on order/admin (`VIS-4.2-07`) | on event | **micro-batch** | Medication events flow through Gold at order/admin cadence; batch acceptable. |
| **Delirium** | RASS / CAM-ICU (Gold + nursing record) | every 4–12h (`VIS-4.2-05`) | shift-based screening (`VIS-3.5`) | **micro-batch** | Documented per shift; 30-min Gold freshness ≪ 4–12h cadence. |

### 1.2 NRT vs Athena-only — resolved by the operational-ingress clarification (RAT-INGRESS-01)

The NRT and hybrid rows above depend on a **sub-batch operational feed** (the "local TimescaleDB source … streaming via HL7 ORU / invasive monitor" in `VIS-4.2-01/03/04`). Strictly read, `ADR001-C-01` (`CON-0001`) forbids own ingestion and mandates **Athena-only reads from Gold**. This engine *consumes* that feed; the reconciliation is **owned by `architecture/system-architecture.md §3.3` and formalized in `docs/plan/_work/adrs/operational-vitals-ingress.md`** (**RAT-INGRESS-01**), not left open here:

- **The resolution (one story).** `ADR001-C-01`'s "no own ingestion / Athena-only" is scoped to **analytical and clinical-context data** (labs, meds, demographics, cultures, documents), which stay Gold/Athena-only. **Bedside-monitor vitals are operational telemetry**, ingested sub-batch via the **existing Phase-1 MLLP listener** (ORU-R01, `VIS-2-05`) into the operational store, idempotent on `MSH-10` (INV-2, §4.1). Gold stays the **sole analytical source** — the same vitals are replayed from Gold for retrospective scoring and the `fact_*` write-back (`ADR001-C-04`). This is a **proposed clarification of ADR-001, pending platform-team ratification** (CTO Office + AMH Engineering); until ratified it is the **working design**, and the latency budget (§8) is stated for the owned pipeline with source freshness held separate.
- **The quantified trigger.** ADR-001 left the Alternativa-B trigger *qualitative* ("insuficiente para o caso de uso de UTI", ADR-001 open-question 1). The quantification lives in `system-architecture.md §6` (**T1**): if the operational MLLP path cannot hold `VIS-C-09` p95 < 30s for vitals-driven scores (measured over a rolling 7-day window) — or the feed is unavailable beyond the availability floor — ADR-001's **Alternativa B** (one dedicated MSK topic, `ADR001-F-08`) activates.
- **Handoff:** amh-integration-architect owns the ratification (RAT-INGRESS-01) and the Alternativa-B decision (`CON-0001`, standing); latency signoff at **barrier C3**.

---

## 2. Declarative, versioned alert-definition schema

Every alert is a **declarative record** (the CONTRACTS `_work/alerts/<domain>.yaml` schema), not imperative code. Fields: `alert_id`, `name` (PT-BR verbatim, accents preserved — `CON-0183`/`DM-C-01`), `severity` (clinical.* band, §3), `trigger {logic, window}`, `inputs [{name, type, unit, source, staleness_max}]`, `evidence`, `suppression {…}`, `ppv_budget`, `response {required, ack_sla}`, `test_vectors` (≥3, ≥1 boundary), `reconciliation`.

**Two engine-specific fields extend the CONTRACTS schema:**
- `evaluation_mode: micro_batch | near_real_time | hybrid` — selects the runner (§1).
- `definition_version` + content hash — every definition is versioned; the engine stamps the firing `definition_version` on each alert it raises. This delivers **100% auditable alert-algorithm versioning** (`VIS-C-13`/`VIS-7.2-05`) and mirrors the score-side `algorithm_version` invariant (INV-3, `IMP-C-03`). Changing any threshold mints a new version; superseded versions are retained for the 7-year window (`DM-RP-03`) so any historical alert is exactly reproducible.

### 2.1 Build-time unit-check hook (closes the SYS-01/02/03 defect classes)

Every `input.unit` **must** be a canonical unit or a declared alias in `docs/plan/_work/units/registry.yaml`. A unit that is neither is a **build-time error in the alert-definition schema**, not a runtime surprise (registry LAW, `registry.yaml` line 21; `CON-SEED-12`). The gate is already implemented:

- `docs/plan/_work/scripts/check_units.py` loads the registry, builds the allowed set (`canonical_unit` ∪ `aliases`, normalized), and fails any `_work/alerts/*.yaml` input or domain-doc ` ```yaml domain-inputs ` input whose unit does not resolve. It additionally pins mission canonicals via `CANON_PINS` (lactate `mmol/L`, FiO₂ `fraction`, vasopressor `mcg/kg/min`, temperature `degC`, creatinine `mg/dL`). Modes: `draft` (warn on missing docs) / `strict` (CI-failing).
- This is what makes the systemic unit defects *un-shippable*: FiO₂ percent-vs-fraction (`SYS-01`/`P0-01`/`P0-07`/`P0-11`), lactate mg/dL-vs-mmol/L (`SYS-03`), vasopressor ml/h-vs-mcg/kg/min (`SYS-02`/`SYS-C-04`/`CON-0060`). Edge normalization happens once on ingest; the computation boundary only ever sees canonical units. `mL/h` on a dosing input is rejected at build time — it must pass through the vasopressor conversion service first (`taxa_infusao` → `dose_vasopressor`, registry).

### 2.2 Build-time systemic-defect gates (CI-failing) — designs out the SYS-04..08 defect classes

**Owner: the alert-definition compiler** — the build step that loads every `_work/alerts/<domain>.yaml` record and domain-doc ` ```yaml domain-inputs ` block, validates it against the CONTRACTS schema, and emits the versioned definition registry (§2). Like the §2.1 unit gate, every check below runs in CI **strict mode and fails the build**: the legacy systemic defect classes (`SYS-*`, escalations-systemic brief) are made *unshippable by construction*, not caught in code review. Each SYS class has exactly one owning gate (owner map at the end of this section).

**Gate A — criterion-coverage (kills `SYS-08` dead/unwired/unreachable criteria).** Every criterion declared in an alert definition must be **wired and evaluable**:

- every `inputs[].name` is referenced by the parsed `trigger.logic` AST, and every criterion/branch of that AST is **reachable** — no structurally-always-false gate (the legacy `SYS-08` patterns: `vars(...).fromkeys(...)` always-False diagnosis filters, commented-out `calcular_criterio_N` wiring, bands written so they can never fire);
- every criterion is exercised by at least one **can-fire test vector** — a vector in which that criterion's truth changes the firing outcome.

A declared input never referenced, a branch no vector can exercise, or a criterion that cannot contribute to any firing is a **CI build failure**. This is the criterion-reachability/coverage gate the hazard log expects of §2 (HAZ-009): a criterion that "appears to exist but can never contribute to an alert" cannot compile.

**Gate B — band-partition / dead-code (kills `SYS-06` chained-comparison misparse + `SYS-07` off-by-one band edges).** For every graded scale in a definition (SOFA sub-score bands, KDIGO stages, ARDS severity bands, pain/agitation grades, any `normal/watch/urgent/critical`-banded trigger), the compiler runs an **exhaustive band-partition check** over the declared input domain:

1. **No gaps** — the union of band intervals covers the whole admissible input range; no value falls through to `None`/0 (the `SYS-07` dead gaps at band edges, e.g. SOFA creatinine `(4.9, 5.0]`, bilirubin `[1.9, 2.0)` / `[5.9, 6.0)` / `[11.9, 12.0)`).
2. **No overlaps** — bands are mutually exclusive; every value maps to exactly one band.
3. **No unreachable band** — every band interval, intersected with the input validator's admissible range, is non-empty. The `SYS-06` misparse (`7 <= dor > 10`, impossible when the validator caps the scale at 10) is exactly an empty top band and fails here: the most severe grade can never again be silently unreachable.
4. **Explicit edge semantics + boundary vectors** — every band edge declares closed/open semantics (`[a, b)` style — a chained comparison cannot be expressed ambiguously in the declarative schema), and every edge of a graded scale carries a boundary test vector asserting the expected band (extends the CONTRACTS ≥1-boundary-vector minimum to *every* band edge).

**Gate C — facade == predicate (kills `SYS-04` facade/predicate drift).** Every clinician-facing rationale — the rendered thresholds, units, and criterion identifiers in the alert payload (`CON-0090`/`PER-C-04`, "which specific parameter triggered it") — is **generated from the same parsed AST the engine evaluates**, never hand-written in parallel. A rendered number, unit, or criterion absent from the firing AST is a build failure: the displayed rationale and the firing condition cannot diverge by construction.

*`SYS-05` note:* the declarative schema itself (§2 — one explicit boolean `trigger.logic`, no imperative query-filter aggregation) removes the v1-vs-v3 AND/OR-collapse surface, and Gate A finishes the job: an AND-collapsed exclusion that can never be true is an unreachable branch and fails the can-fire check.

**Sibling gates (cross-references — completing the SYS-01..10 owner map):**

- `SYS-01`/`SYS-02`/`SYS-03` (FiO₂ percent-vs-fraction, vasopressor dose-unit chaos, lactate mg/dL-vs-mmol/L) — killed by the **§2.1 build-time unit gate** (`check_units.py` strict, `CON-SEED-12`): this section's sibling and its pattern.
- `SYS-09`/`SYS-10` (weight decimal-separator ~10× parse inflation; month-agnostic day-of-month window filtering) are **edge-parser duties of the ingestion normalize stage** (§1 micro-batch runner "normalizes to canonical units at the edge"; §8.1 stage 2), not definition-compiler gates: the normalize layer owns locale-aware decimal parsing (property-tested with `70,5`/`70.5`-style vectors against the units-registry conversions, `SYS-09`) and absolute-instant, timezone-explicit time-window construction — never day-of-month matching (`SYS-10`). Verified by the normalize layer's own CI suite; named here so every SYS class has exactly one owner.

| ID | Requirement | Verification | Owning component |
|---|---|---|---|
| **REQ-GATE-01** | Criterion coverage: every declared criterion/input is wired into the `trigger.logic` AST, reachable, and exercised by a can-fire vector; dead/unwired/unreachable criteria are CI build failures (`SYS-08`). | Compiler check over all `_work/alerts/*.yaml` + domain-doc machine blocks in CI strict mode; seeded-defect test: unwire one criterion → build fails. | **Alert-definition compiler** (build/CI) |
| **REQ-GATE-02** | Band partition: every graded scale partitions its admissible input range — no gaps, no overlaps, no unreachable band, explicit edge semantics, boundary vector per edge (`SYS-06`/`SYS-07`). | Compiler interval-arithmetic check per scale in CI strict mode; seeded-defect test: reintroduce a strict `> 5.0` renal band edge → build fails. | **Alert-definition compiler** (build/CI) |
| **REQ-GATE-03** | Facade==predicate: rendered rationale/units/thresholds are generated from the firing AST; a rendered clinical number/unit/criterion absent from the AST is a CI build failure (`SYS-04`). | Compiler render-vs-AST diff in CI strict mode; seeded-defect test: hand-edit one facade threshold → build fails. | **Alert-definition compiler** (build/CI) + payload renderer |

---

## 3. Severity model (canonical clinical.* scale) — resolves `CON-SEED-11` (barrier C2)

One canonical four-band scale, **`normal / watch / urgent / critical`**, used for both score/patient status (bed-board) and alert severity. It is **structurally separate from tenant `brand.*` tokens** (`CON-0041`/`ADR-C-08`/`DES-C-01`): tenant rebranding must never change what a severity color *means*. Severity is always **triple-encoded — color + icon + shape** (`CON-SEED-11`) so it survives colour-blindness / greyscale (WCAG 1.4.1). Exact token hex/shape values are the design-token-systems-designer's at C2; slots proposed here.

| Band | Definition | Response expectation | Delivery tier | Encoding (color · icon · shape) |
|---|---|---|---|---|
| **normal** | Within expected range / advisory trend or opportunity; no deterioration. | Review < 6h (advisory) — from INFO SLA `CON-0065`/`CAT-C-05` | **Tier 4** — bed-board / worklist advisory only; no push, no page; suppressible/coalescable | green · check-circle · circle |
| **watch** | Relevant change worth noticing. | Clinical action < 2h (`CON-0064`/`CAT-C-04`) | **Tier 3** — WS push + bed-board badge; no page **at raise**; escalates to the **assigned clinician (R2)** on `PT60M` ack-SLA breach, **not** the RRT (only urgent/critical climb toward RRT — §9, `alert-routing.md` §2) | amber · eye · rounded-square |
| **urgent** | Significant deterioration. | Clinical action < 30 min (`CON-0063`/`CAT-C-03`) | **Tier 2** — WS push + bed-board + mobile push; ack expected; escalate on ack-SLA breach | orange · exclamation · triangle |
| **critical** | Imminent life risk. | Clinical action < 5 min (`CON-0062`/`CAT-C-02`) | **Tier 1** — interruptive multi-channel: WS push + **mobile page to RRT <5s** (`CON-0092`/`PER-C-06`) + bed-board + audible; **mandatory ack**; escalate on ack-SLA breach; **never rate-limited** | red · alert-octagon · octagon |

### 3.1 Severity aggregation invariant — **highest-severity-wins, never last-writer-wins**

When several criteria or domains contribute to one alert, `severity = MAX(component severities)`. Last-writer-wins is **forbidden**: it is the P0-10 defect where a later AMARELO silently overwrote an earlier VERMELHO, downgrading a red alert (`CON-0182`/`CLU-PIORA-CLINICA-C-01`, `P0-10`). Equivalently, on the color scale, `VERMELHO` can never be overwritten by a lower band evaluated later. Dead-zone/gap branches are **corrected, not ported** (`CON-0133`/`CLU-ALERTAS-C-01`).

Full mappings and the lifecycle live in `docs/plan/_work/platform/severity-model.yaml`.

---

## 4. Idempotency

### 4.1 Ingestion idempotency — **INV-2** (`CON-0067`/`IMP-C-02`)
- **HL7/MLLP path:** `MSH-10` (message control id) is the unique key; `INSERT … ON CONFLICT (msh10) DO NOTHING`. A redelivered HL7 message never creates a duplicate `vital_sign` row (risk if absent: "duplicação de dados clínicos, alertas falsos", `IMP-C-02`).
- **Athena/Gold path:** the poll is idempotent by construction — a **high-watermark** (last `ingested_at` / Gold snapshot id) bounds each incremental read, and the operational upsert uses a natural key `(mpi_id, recorded_at, source_system, measurement)` with `ON CONFLICT DO NOTHING`. Re-polling an overlapping window therefore never double-writes. `vital_sign.ingested_at` is kept distinct from `recorded_at` (`DM-C-08`) so freshness and clinical-collection time are separable.

### 4.2 Evaluation idempotency — dedup keys
- **Evaluation fingerprint:** each evaluation is keyed by `(alert_definition_id, mpi_id, input_fingerprint)` where `input_fingerprint` is a deterministic hash of the exact canonical input tuple + `definition_version`. Identical inputs ⇒ identical decision ⇒ identical `dedup_key`.
- **Alert dedup_key:** `(mpi_id, alert_definition_id, window_bucket)`. Alert persistence is `ON CONFLICT (dedup_key) DO NOTHING` (or increment a recurrence counter). A replay, a re-poll, or an at-least-once redelivery is therefore **absorbed** — the pipeline is safe to re-run end-to-end.

---

## 5. Suppression machinery (alarm-fatigue control)

Targets: alarm-fatigue ≤ 10% (`VIS-7.1-04`), PPV ≥ 60% (`VIS-7.1-02`), and **< 3 false positives / patient-day** (`CON-0088`/`PER-C-02` — operationalized as a per-patient-day *distribution* metric, not a fleet mean: §5.1 and `ppv-ledger-draft.yaml` method). Layers, evaluated in order:

1. **Dedup** — `dedup_key = mpi_id + alert_definition_id (+ criterion)`. A duplicate within cooldown increments the recurrence counter on the existing active alert instead of raising a new row.
2. **Cooldown** — per alert-definition; default from `threshold_config.cooldown_minutes` (`DM-T-05`). A suppressed alert stays suppressed until cooldown elapses **unless severity escalates** (see rule below).
3. **Rate-limit** — per patient per alert from `threshold_config.rate_limit_per_hour` (`DM-T-05`). **Applies to `normal`/`watch` only.** `urgent`/`critical` are **never** per-patient rate-limited (`alert-routing.md` §4 banner; `severity-model.yaml` `rate_limited: false` for both interruptive tiers; carve-out below). On an `urgent`/`critical` definition the catalog `rate_limit` field therefore bounds **only the re-page cadence of a single still-active alert instance** (a recurrence control layered on dedup+cooldown), never a delivery cap — a genuine new firing or a severity escalation on these tiers always delivers.
4. **Per-patient alert budget (smart suppression)** — a token-bucket per `(mpi_id, severity-tier)`. When the `watch`/`normal` budget is exhausted, further low-tier alerts are **coalesced into a digest** rather than paged. Directly serves `PER-C-02` and `VIS-7.1-04`.
5. **Maintenance windows** — scheduled suppression (known procedure, device recalibration): alerts are still **recorded and audited** but not delivered/paged.

**Suppression never applies to** (patient-safety carve-outs): **`critical` and `urgent` severity** — both interruptive tiers are never budget-suppressed, budget-demoted, digest-held, rate-limited, or maintenance-muted (`alert-routing.md` §4 banner); any **severity increase** on an existing `dedup_key` (a `watch→critical` transition always surfaces — never masked by cooldown, mirroring §3.1); and operational/dead-man's-switch alerts (§7).

### 5.1 Per-patient urgent/critical concurrency model — what bounds the never-suppressed tiers

The layer-4 budget/digest machinery applies to `normal`/`watch` **only**; `urgent`/`critical` are **never** budget-suppressed, budget-demoted, digest-held, or maintenance-muted (carve-outs above; `alert-routing.md` §4 banner). **The fleet fatigue targets therefore do not bound these tiers by suppression:** the ≤10% ignored-rate (`VIS-7.1-04`) and the watch/normal token budget are fleet/low-tier *delivery* mechanisms, and the `PER-C-02` FP gate is a *measurement* guardrail, not a throttle. Because interruptive load concentrates on the sickest patients (budget depletion correlates with acuity), the per-patient urgent/critical load is modeled explicitly here rather than left to fleet averages:

- **Fleet expectation.** Summed catalog `est_volume_per_100_beds_day` across the nine `_work/alerts/*.yaml` catalogs: **critical 24 + urgent 52 = 76 interruptive alerts/100 beds/day** (of 137 total) — a fleet mean of ~0.76 urgent/critical pages per patient-day. The mean is misleading: the distribution is heavy-tailed, and decompensation concentrates it 10–20× on the affected patient-day. *(Attribution caveat — `RT2-ALARM-03`: each alert's whole `est_volume` is booked to its **single declared band**, so dynamic-severity alerts are mis-attributed in **both** directions — the electrolyte alerts are booked `critical` though their logic steps down to urgent/watch (over-attributing the top tier), while `ALERT-AKI-KDIGO-STAGE-01` is booked `watch` though its stage-3 band is `critical` (under-attributing it). The per-tier figure is an order-of-magnitude pager-load input, **not** a certified two-sided bound; the follow-up is a **declared per-band volume split** for dynamic-severity alerts plus the build-drift check below.)*
- **Expected pages per decompensating patient-day.** A septic-shock decompensation plausibly involves **~8–13 distinct urgent/critical definitions** firing at least once in 24h (sepsis `SCREEN-01`/`ORGAN-02`/`SHOCK-03`/`BUNDLE-OVERDUE-04`; EWS `NEWS2-DETERIORATION-01` + `SOFA-ACUTE-ORGAN-DYSFUNCTION-03`; hemo `LACTATE-CLEARANCE-02`/`VASO-ESCALATION-03`/`REFRACTORY-SHOCK-04`; electrolyte `POTASSIUM-01`; AKI `PROGRESSION-02`; correlations `SEPSIS-AKI-01`/`RESP-HEMO-02`), recurrences absorbed per-definition by dedup/cooldown. **Expected ≈ 10–16 interruptive deliveries/patient-day before folding; ≈ 8–14 after the applicable correlation folds** (below).
- **Worst case (structural re-page envelope) — the explicit C3 RRT pager-load sizing input.** Per-definition `rate_limit` on an `urgent`/`critical` definition is **not** a delivery throttle — these tiers are **never** rate-limited (§5 carve-out; `alert-routing.md` §4 banner; `severity-model.yaml` `rate_limited: false`) — it bounds only the **re-page cadence of a single still-active instance**. Read as re-page caps, the septic-shock co-fire set above sums to **50 interruptive deliveries/24h for one patient**; the absolute structural ceiling with all **29** urgent/critical definitions at their re-page caps is **96/24h** (urgent 44 + critical 52). A genuine **new firing** or a **severity escalation** sits outside this envelope and **always delivers**. This figure is the explicit **C3 input for RRT pager-load / on-call fan-out sizing** and the honest denominator for any top-tier fatigue claim; it is consumed **with** the delivery/latency budget (`_work/budgets/latency.yaml`; §8 stage table — deliver ≤ 2 s, RRT push < 5 s) and the routing tiers (`severity-model.yaml` Tier-1/Tier-2; `alert-routing.md` §2–§3) that size the paging path. **Build-drift check (`RT2-ALARM-03`, owner: alert-definition compiler, CI strict):** the hand-maintained aggregates in this section (per-tier volume, definition count, Σ re-page caps) are re-derived from the summed catalog values and the build **fails on drift**, so a catalog change — e.g. the `PAIN-08 → urgent` reclassification that staled the prior `73`/`93` figures — can no longer silently invalidate this C3 input.
- **Interaction with correlation folding.** The correlation engine folds member pushes for exactly three pairs (`ALERT-CORR-SEPSIS-AKI-01` folds sepsis organ/shock + AKI-stage members, PT12H cooldown; `ALERT-CORR-RESP-HEMO-02` folds ARDS + vaso-escalation/shock-index members, PT4H; `ALERT-CORR-QTC-ELEC-03` folds QTc + K⁺/Mg²⁺ context members, PT8H) — members stay recorded (prontuário NGS-2); only the concurrent *push* folds into the higher-severity correlation page. On the decompensating patient this removes ~2–4 pages/day; fleet-wide the three folds cover ≤ ~8 member pushes of the 137/day total (< 6%). Sepsis↔EWS, Sepsis↔Hemo and EWS↔Hemo co-fires are folded by the cross-domain **deterioration-cluster fold** (`correlation-engine.md` §5.2), not by the three pairwise correlations. **Fold break-through (HAZ-026-safe, `correlation-engine.md` §5.1 break-through rule):** the correlation cooldown is a *concurrency* dedup, not a cooldown-length silence — a **new member** joining a live fold at ≥ `urgent` (e.g. `ALERT-SEPSIS-SHOCK-03` firing at hour 6 of a live `SEPSIS-AKI-01` fold), or any **severity increase** within a folded member, **re-notifies immediately at its own tier** regardless of the correlation cooldown; the fold never suppresses a severity escalation or a new critical member, composing with the never-suppress-critical carve-out above (equal-severity critical members do not fold silently even though the correlation is itself critical).
- **Same-physiology urgent/critical FOLD — an upgrade, never a suppression (HAZ-026-safe).** When multiple urgent/critical alerts fire concurrently for one patient off the same physiology (overlapping trigger inputs — e.g. one hypotension/lactate excursion driving shock-index, vaso-escalation and sepsis-organ criteria), the delivery layer folds them into **one richer page at MAX severity** (§3.1) carrying every member's triggering parameter (`CON-0090`). No member is dropped, delayed, or demoted: every member alert is persisted, audited, and keeps its own §9 lifecycle and escalation ladder; any severity **increase** still breaks through immediately (HAZ-026 carve-out preserved). What is bounded is the number of *distinct interruptive deliveries*, never the alert records — this is what keeps the ~50/24h worst case from being delivered as ~50 distinct pages while staying safe against HAZ-026 (suppression masking a real deterioration).
- **Bounding summary for the never-suppressed tiers:** (1) per-definition `dedup`/`cooldown`/`rate_limit` — recurrence controls bounding re-pages of one definition (for `urgent`/`critical` they bound re-page *frequency* of a still-active instance **only** — these tiers are never rate-limited, §5 carve-out; a new firing or a severity upgrade always delivers); (2) the same-physiology upgrade-fold; (3) the three correlation folds; (4) per-alert `ppv_budget` gates bounding false-positive volume at the source; (5) the `PER-C-02` per-patient-day FP **distribution** gate (share of patient-days with > 3 dispositioned FP ≤ 5%, and p95 FP/patient-day < 3 — `ppv-ledger-draft.yaml` method) as the measurement guardrail that makes per-patient concentration visible instead of averaged away.

---

## 6. Threshold-config resolution: tenant → unit → bed (every change audited — **INV-1**)

`threshold_config` maps a score to its `watch/urgent/critical` bands per scope (`DM-T-05`). Today it carries `tenant_id` + `unit` (NULL = tenant-wide, `DM-C-11`/`CON-0029`). This engine **extends it with a nullable `bed_id`** column (`patient_cache` already carries `bed_id` + `unit`, `DM-T-01`), giving three scopes.

- **Resolution = most-specific-wins:** for a patient in `(tenant, unit, bed)`, select the row matching `bed_id`; else the `unit` row; else the tenant default (`unit` NULL, `bed_id` NULL). Precedence **bed ≻ unit ≻ tenant**.
- **Every change audited (INV-1, `CON-0066`/`IMP-C-01`):** each `INSERT/UPDATE/DELETE` on `threshold_config` writes an append-only `audit_trail` row (`updated_by`, `updated_at`, before/after). This is the auditable-versioning requirement (`VIS-C-13`) for tunable thresholds. `threshold_config` stays **operational-only — no Gold persistence** (`DM-C-11`/`CON-0029`).
- **Scope note:** `threshold_config` governs **score→severity band** mapping (MEWS/NEWS2/SOFA/qSOFA). Fixed clinical cutoffs (e.g. K⁺ > 6.5) live **versioned in the alert-definition** (§2), not here.
- **Reconciliation (→ C2 / data-architect):** adding `bed_id` extends the `DM-T-05` schema; flagged for the data model.

---

## 7. Delivery guarantees — **INV-6** (`CON-0071`/`IMP-C-06`) + dead-man's switch — **INV-5** (`CON-0070`/`IMP-C-05`)

### 7.1 Delivery (INV-6)
- **ARQ native retry + exponential backoff** on every notification (WS push, mobile push, SMS) — `IMP-3.2-06`; risk if absent: "alertas perdidos" (`IMP-C-06`).
- **At-least-once**: a delivery is retried until channel-acked or max-retries → **DLQ**. DLQ arrival raises an operational alert (§7.2) — **no alert is ever silently dropped**.
- **Client-side dedup**: each notification carries the alert `dedup_key` + a monotonic `version`; clients dedup on it, so **at-least-once transport + client dedup = effectively-once UX**. Satisfies "realtime payload is a thin idempotent patch reconciled against the record" (`CON-0045`/`ADR-C-12`).
- **Single channel/latency class**: bed-board state and notifications go through the **same push channel** so they cannot visibly disagree about one event (`CON-0046`/`CON-0053`/`DES-C-05`). Bed-board must not rely on REST polling.
- Every alert is also recorded in the patient chart at NGS Level 2 (`VIS-C-07`) and each alert exposes **which specific parameter triggered it** (`CON-0090`/`PER-C-04`).

### 7.2 Dead-man's switch + alert-on-no-alerts (INV-5)
The batch reality makes **silent staleness** the signature failure: an Athena poll fails, scores freeze, no clinical alert fires — the unit looks calm but the engine is blind. Two mechanisms convert silence into a paged signal:

- **Liveness** — `/api/v1/health` reports component readiness: DB, Redis, ARQ workers, Athena connectivity, and **per-(unit,domain) `last_poll_success_at` / `last_score_at`**. An **external watchdog** (outside the ECS service — CloudWatch synthetic / Lambda, emitting via OTEL→AMP per `CON-0006`) probes it every **≤30s** (aligned to `VIS-C-09`); 2 consecutive misses or degraded readiness pages on-call. This is the "script externo de monitoramento" of `IMP-C-05` (risk if absent: "sistema cai e ninguém sabe").
- **Alert-on-no-alerts (staleness watchdog)** — per `(unit, domain)`, raise an **operational** alert when: last successful poll older than `poll_interval × 3`; **or** an NRT domain has ingested zero rows for a unit beyond its expected cadence; **or** observed score/alert volume drops to zero over a window whose historical baseline is non-zero. Per-patient, a **stale-data flag** surfaces on the bed-board when a monitored patient has no fresh vital within the expected window (ties to abnormal-value flagging, `CON-0054`/`DES-C-06`). This is the mechanism that makes ADR-001's ≤30-min Gold lag *visible* instead of dangerous.

---

## 8. Latency budget — ONE canonical decomposition — resolves `CON-SEED-01` (final signoff barrier C3)

**The conflict (`CON-SEED-01`).** Vision states **one** number — p95 ingest→alert **< 30s** (`VIS-C-09`/`VIS-7.2-01`). Implementation-plan **splits** it — score p95 **<30s MVP / <5s prod** (`IMP-C-13`) and alert p95 **<5s MVP / <2s prod** (`IMP-C-14`). Summed naively, the MVP figures give score(30s)+alert(5s) = **35s > 30s** — they contradict the vision ceiling.

**Canonical resolution (proposed; binding subject to C3):**
1. **The 30s SLO is the end-to-end envelope IntensiCare *owns*, measured over the five controllable stages `poll → normalize → evaluate → persist → deliver`** (the poll stage is per-path: `poll_nrt` for the NRT runner, `poll_micro_batch` for the Athena runner — §8.1 rows 1a/1b). The impl-plan splits are **intra-budget stage ceilings**, not independent reference frames: impl *score* maps to the **evaluate** stage, impl *alert* maps to the **deliver** stage.
2. **Production stage targets are binding** (they sum comfortably under 30s). The MVP relaxations are **re-scoped** so `evaluate_MVP ≤ 30s − Σ(other stages)`; the MVP evaluate ceiling can grow toward the headroom but **the end-to-end p95 still ≤ 30s**. The 35s contradiction disappears because the two impl numbers were never meant to be added *against* the vision ceiling — they sit *inside* it.
3. **Source freshness is inherited and excluded from the committed SLO.** Upstream AMH source→Gold latency (≤30 min p95, `ADR001-F-02`) is outside IntensiCare's control (`ADR001-C-01`/`C-10`) and is surfaced for transparency, not counted in the 30s. End-to-end bedside→alert = `source_freshness + owned_pipeline`.

### 8.1 Stage table (each p95; near-real-time path unless noted)

| # | Stage | p95 | Assumption | Source ref |
|---|---|---|---|---|
| 0 | **source freshness** *(INHERITED — not in the 30s)* | NRT ≈ **2 s**; **batch ≤ 30 min** | NRT: operational stream/monitor datum query-visible ≈2s. Batch: AMH Gold P95 <30 min — uncontrollable, held separate. | `ADR001-F-02`, `ADR001-C-10` |
| 1a | **poll_nrt** *(NRT path)* | **1,000 ms** | Event pickup from the Redis stream (NRT runner). | `VIS-2-08` (Redis pub/sub), `IMP-3.2-05` |
| 1b | **poll_micro_batch** *(micro-batch path)* | **8,000 ms** *(stated planning assumption — replaced by measured p95)* | Athena SELECT round-trip for one incremental, partition-pruned poll: queue wait + query planning + S3/Iceberg scan + result fetch. **Assumption:** 8 s p95 for the narrow high-watermark reads this engine issues (single lab/domain partition, small result set) — multi-second and dominated by Athena queue+planning overhead, not scan volume; the pilot-measured p95 replaces this number, and a measured breach re-opens the micro-batch Σ at C3. The ~1–2 min expedited electrolyte cadence (§1.1) is the *trigger interval*; this row is the per-poll query cost inside it. | `ADR001-C-01` (Athena-only reads), `IMP-3.2-06` |
| 2 | **normalize** | **500 ms** | Parse HL7/FHIR → canonical units at the edge; within the ingest-vital write envelope. | `IMP-C-12` (<500ms MVP), `CON-SEED-12` |
| 3 | **evaluate** | **5,000 ms** | Run score + alert-definition predicates (production score budget). | `IMP-C-13` (score <5s prod) |
| 4 | **persist** | **500 ms** | Write `clinical_score` + `alert` + `audit_trail` (ON CONFLICT / append). | `IMP-C-12`, INV-1 (`CON-0066`), INV-2 (`CON-0067`) |
| 5 | **deliver** | **2,000 ms** | ARQ enqueue → WS/mobile push, at-least-once. | `IMP-C-14` (alert <2s prod), INV-6 (`CON-0071`), `CON-0092` (<5s RRT) |
| | **Owned pipeline Σ — NRT path (1a + 2–5, linear upper bound)** | **9,000 ms = 9 s** | Conservative — a linear sum of stage p95s over-estimates true e2e p95 (stages not perfectly correlated). | vs ceiling **`VIS-C-09` 30 s** |
| | **Owned pipeline Σ — micro-batch path (1b + 2–5, linear upper bound)** | **16,000 ms = 16 s** | Same conservatism; carries the 1b Athena round-trip assumption until measured. | vs ceiling **`VIS-C-09` 30 s** |

**Checks.** Owned Σ: NRT **9 s** and micro-batch **16 s**, both ≪ the **30 s** ceiling (`VIS-C-09`), leaving ~21 s / ~14 s headroom respectively to absorb MVP relaxation and the sum-vs-true-p95 slack. The MVP `evaluate` re-scope is per-path: NRT **23,000 ms**, micro-batch **16,000 ms** (`30,000 − poll_path − 500 − 500 − deliver_MVP 5,000`) — each path's MVP column sums to exactly 30,000 ms. Deliver **2s < 5s** RRT mobile push (`CON-0092`/`PER-C-06`). Engine detection→delivery ≤9s (NRT) / ≤16s (micro-batch) leaves the remainder of the **5-min** critical action window for the human response (`CON-0062`). Throughput target **>500 alerts/min** (`VIS-C-11`) and availability **99.9%** (`VIS-C-10`) are unaffected by this decomposition (ARQ/Redis horizontal scale).

**Barrier C3 note.** Final signoff of these stage numbers, of the source-freshness exclusion, and of the Alternativa-B trigger (§1.2) belongs to C3 (latency + PPV), co-owned with amh-integration-architect and platform-reliability-engineer. Full machine-readable budget: `docs/plan/_work/budgets/latency.yaml`.

**Canonical-source designation (`CON-SEED-01`, B3-005).** This §8 is the **sole canonical PROSE** statement of the `CON-SEED-01` resolution. `docs/plan/_work/budgets/latency.yaml` is its **machine-readable companion — the single source of the numbers** (it self-describes as such, not as a competing canonical). `observability-slo.md §3` is a **downstream restatement** that must introduce no number absent from `latency.yaml`. The three artifacts state one resolution once, not three times: prose here, numbers in `latency.yaml`, SRE-facing restatement in `observability-slo.md §3`.

---

## 9. Alert lifecycle state machine (every transition audited — INV-1; feeds PPV analytics)

Task lifecycle `raise → acknowledge → act → resolve` reconciled with the data-model `status` enum `{active, acknowledged, resolved, expired}` (`DM-VOCAB-04`) and `resolution` enum `{true_positive, false_positive, intervention_done}` (`DM-VOCAB-05`).

```
  ┌──────────┐  ack (clin.)  ┌────────────┐  act (clin.)  ┌────────┐  resolve  ┌──────────┐
  │  RAISED  │─────────────▶ │ACKNOWLEDGED│─────────────▶ │ ACTING │─────────▶ │ RESOLVED │
  └──┬────┬──┘               └──────┬─────┘               └───┬────┘           │ (true_pos│
     │    │                         │                         │                │ /false_  │
     │    │ ack-SLA breach          │ action-SLA breach       │ action-SLA     │ pos/     │
     │    │ (timer, band-aware)     │ (timer)                 │ breach (timer) │ interv.) │
     │    │                         │                         │                └──────────┘
     │    │                         │  resolve (direct) ──────┼──────────────▶  (RESOLVED)
     │    ▼                         ▼                         ▼                  (terminal)
     │  ┌──────────────────────────────────────────────────────────┐  ack (RRT / next tier)
     │  │                        ESCALATED                          │────────────▶ (ACKNOWLEDGED)
     │  └──────────────────────────────────────────────────────────┘
     │
     │ condition clears / TTL (auto-clear)
     ▼
  ┌──────────┐
  │ EXPIRED  │
  │(terminal)│
  └──────────┘

  Timer edges into ESCALATED (system/timer, all clocks measured from created_at — entering a later
  state never resets the clock, §2.1 one-global-clock rule): raised→escalated on ack-SLA breach
  (band-aware: watch→assigned clinician R2, urgent/critical→RRT); acknowledged→escalated AND
  acting→escalated on action-SLA breach. The acting→escalated edge (RT2-PATIENT-SAFETY-07) closes the
  former acting dead-end.
```

| From | To | Actor | Audited | SLA / trigger |
|---|---|---|---|---|
| — | **raised** (active) | system (engine) | ✅ | definition predicate fires + passes suppression |
| raised | **acknowledged** | clinician (1-click, `CON-0091`/`PER-C-05`) | ✅ | ack-window: crit 2 min / urg 10 min / watch 60 min |
| acknowledged | **acting** | clinician | ✅ | intervention start |
| acting | **resolved** | clinician | ✅ | action-window: crit <5 min / urg <30 min / watch <2h (`CON-0062..64`); sets `resolution` |
| acting | **escalated** | system (timer) **or** clinician (manual "Escalar agora") | ✅ | **action-window breached while in `acting`** → page next tier (`urgent`/`critical` → RRT; `watch` → assigned clinician R2). Clock is crit 5 min / urg 30 min / watch 2h (`CON-0062..64`), **measured from `created_at`** — entering `acting` does **not** stop the action clock (mirrors the §2.1 one-global-clock rule for ack). **Closes the `acting` dead-end (`RT2-PATIENT-SAFETY-07`):** a responder who taps intervention-start then is pulled away no longer sits in `acting` indefinitely on a `critical` whose <5-min action window (`CON-0062`) is measured but was never timer-enforced. Manual "Escalar agora" early-triggers the same transition (`triggered_by` = system vs user_id) |
| acknowledged | **resolved** | clinician | ✅ | direct resolve; sets `resolution` |
| raised | **escalated** | system (timer) **or** clinician (manual "Escalar agora") | ✅ | ack-window breached → **band-aware** climb: `watch` (`PT60M`) → assigned clinician (R2), **not** RRT; `urgent`/`critical` → page next tier (RRT). Manual "Escalar agora" early-triggers the same transition (`triggered_by` = system vs user_id) |
| acknowledged | **escalated** | system (timer) **or** clinician (manual "Escalar agora") | ✅ | action-window breached → page next tier. Manual "Escalar agora" early-triggers the same transition (`triggered_by`) |
| escalated | **acknowledged** | escalation-tier clinician | ✅ | — |
| raised | **expired** | system | ✅ | triggering condition cleared before ack, or alert TTL |

- **Every transition writes an immutable `audit_trail` row** (INV-1, `CON-0066`; append-only + anti-mutation trigger). Legal requirement (LGPD + CFM 1.821/07).
- **`acting` and `escalated` extend the data-model `status` enum** (currently active/acknowledged/resolved/expired). Auto-clear routes to `expired` to stay within the enum; human resolutions use `true_positive/false_positive/intervention_done`. **Reconciliation (→ C2 / data-architect):** add `acting` + `escalated` (or model `acting` as acknowledged + `intervention_started_at`, `escalated` as a flag). The persistence side of this reconciliation is now adopted in `data-model.md` §3/§4.1/§10 (B2-001).
- **Escalation actor + target (canonical with `severity-model.yaml` and `alert-routing.md` §2):** the `raised → escalated`, `acknowledged → escalated`, and `acting → escalated` transitions may be driven by the **system timer** OR by a **clinician manually** ("Escalar agora"); the manual path is an *early trigger of the same transition*, audited with `triggered_by` distinguishing `system` from a `user_id` (B2-002). The `raised → escalated` climb is **band-aware** (B2-003): a `watch` breaching its `PT60M` ack-SLA escalates to the **assigned clinician (R2)**, **never** to the RRT; only `urgent` and `critical` climb toward the RRT tier (`alert-routing.md` §2 is the source of the correct ladder). The `watch` §3 delivery descriptor therefore reads "no page *at raise*; escalates to the assigned clinician on `PT60M` ack breach", not "no escalation".
- **No timer dead-ends (`RT2-PATIENT-SAFETY-07`).** Every non-terminal state has a **system-timer exit**, so a stalled alert can never sit un-escalated: `raised` exits on the ack-SLA timer (or auto-clears to `expired`), and **both `acknowledged` and `acting` exit on the action-SLA timer** (`acting → escalated`). The action-window clock (crit 5 min / urg 30 min / watch 2h, `CON-0062..64`) is a **single clock measured from `created_at`**; **entering `acting` does not restart or stop it** (mirroring §2.1's one-global-clock discipline for ack). Worked example: a `critical` alert acked and moved to `acting` at t0 that is still unresolved at t0 + 5 min **escalates to the RRT** (system-timer page), because tapping intervention-start does not pause the `CON-0062` <5-min action window; the recurrence-dedup of §5 folds any re-fire into the existing active row, so this timer is the only thing that re-pages a genuinely stalled `acting` critical.
- **Feeds PPV analytics** (co-owned, barrier C3): `resolution` gives **PPV = TP/(TP+FP)** (target ≥60%, `VIS-7.1-02`); `acknowledged_at − created_at` gives time-to-recognition; `resolved_at − created_at` gives time-to-action (target ≤15 min, `VIS-7.1-03`); expired-unacked / total feeds alarm-fatigue (≤10%, `VIS-7.1-04`). These flow to Gold `fact_alert` (`CON-0028`).

---

## 10. Invariant verification register (REQ-INV-2 / -5 / -6)

| ID | Requirement | Verification | Owning component |
|---|---|---|---|
| **REQ-INV-2** | Ingestion idempotency: `MSH-10` (HL7) / natural key (Gold poll) is the unique key; `INSERT … ON CONFLICT DO NOTHING`; redelivered or re-polled data never duplicates a `vital_sign` row (`CON-0067`/`IMP-C-02`). | Replay test: feed the same `MSH-10` twice **and** the same Gold poll window twice → exactly one row; CI unit+integration test; audit shows a single ingest. | Ingestion/normalize layer (micro-batch runner + NRT ingest edge); DB uniqueness constraint on the natural key. |
| **REQ-INV-5** | Dead-man's switch: `/api/v1/health` readiness + external ≤30s watchdog; alert-on-no-alerts staleness monitor per `(unit,domain)`; silence becomes a paged operational alert (`CON-0070`/`IMP-C-05`). | Synthetic watchdog probe in AMP; chaos test (kill poller / stop stream) → operational alert fires within the watchdog interval; staleness thresholds unit-tested. | Health/observability layer (`/api/v1/health`, external watchdog via OTEL→AMP, `CON-0006`) + staleness-watchdog job. |
| **REQ-INV-6** | At-least-once delivery: ARQ native retry + exponential backoff on every notification; DLQ on exhaustion + operational alert; client-side dedup on alert `dedup_key` for effectively-once UX (`CON-0071`/`IMP-C-06`). | Fault-injection: drop channel acks → retries then DLQ + operational alert; client-dedup test; assert no alert silently lost. | Delivery layer (ARQ workers, DLQ, WS/mobile push) + client dedup. |

---

## 11. Constraints this document owns or discharges

| Constraint | Barrier | Where addressed |
|---|---|---|
| `CON-SEED-01` latency-SLO split | **C3** | §8 (canonical decomposition) |
| `CON-SEED-11` severity mapping | **C2** | §3 + `severity-model.yaml` |
| `CON-SEED-12` unit build-time error | C1 (units) | §2.1 (hook reference) |
| `CON-0062..0065` severity action SLAs | C3 | §3 table, §9 |
| INV-1/-2/-5/-6 (`CON-0066/67/70/71`) | B/C3 | §4, §6, §7, §9, §10 |
| `CON-0088` <3 FP/patient-day · `CON-0090` expose trigger · `CON-0092` RRT <5s | C3 | §5, §7.1, §8.1 |
| `CON-0182` never downgrade · `CON-0133` correct dead-zone | C3 | §3.1 |
| `CON-0045/0046/0053` single realtime channel | C3 | §7.1 |
| `CON-0029/0033` threshold_config operational + tenant | B | §6 |

Open reconciliations flagged for data-architect (C2): `bed_id` on `threshold_config` (§6); `acting`/`escalated`/`info` additions to the `status`/`severity` enums (§3, §9).
