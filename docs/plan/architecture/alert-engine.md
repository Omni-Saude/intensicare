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

### 1.2 Conflict recorded, not resolved: NRT vs Athena-only (routed to C3)

The NRT and hybrid rows above depend on a **sub-batch operational feed** (the "local TimescaleDB source … streaming via HL7 ORU / invasive monitor" in `VIS-4.2-01/03/04`). Strictly, `ADR001-C-01` (`CON-0001`) forbids own ingestion and mandates **Athena-only reads from Gold**. Per CONTRACTS §5 (ADR-001 ≻ vision) this is a genuine conflict; per the zero-silent-resolution rule I **record and route** it rather than decide it:

- On a **pure-batch reading** of ADR-001, every NRT/hybrid domain degrades to **micro-batch**, and `VIS-C-09` (<30s) can be met **only from the poll boundary onward** — bedside→alert then equals AMH source freshness (≤30 min) + the owned pipeline. The vitals-driven early-warning promise (US-01/02/03) is *not* achievable this way.
- To honor `VIS-C-09` on vitals/monitor scores, IntensiCare needs a sub-batch feed: either the existing **MLLP path** into the operational store, or ADR-001's **Alternativa B — one dedicated MSK streaming topic** bypassing the batch pipeline (`ADR001-F-08`). ADR-001 left the trigger *qualitative* ("insuficiente para o caso de uso de UTI", ADR-001 open-question 1). **This engine supplies the missing quantification: the trigger is exactly `VIS-C-09` p95 < 30s applied to vitals-driven scores.**
- **Handoff:** amh-integration-architect owns the Alternativa-B decision (`CON-0001`, standing); latency signoff at **barrier C3**. Until resolved, the latency budget (§8) is stated for the owned pipeline with source freshness held separate.

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

Targets: alarm-fatigue ≤ 10% (`VIS-7.1-04`), PPV ≥ 60% (`VIS-7.1-02`), and **< 3 false positives / patient-day** (`CON-0088`/`PER-C-02`). Layers, evaluated in order:

1. **Dedup** — `dedup_key = mpi_id + alert_definition_id (+ criterion)`. A duplicate within cooldown increments the recurrence counter on the existing active alert instead of raising a new row.
2. **Cooldown** — per alert-definition; default from `threshold_config.cooldown_minutes` (`DM-T-05`). A suppressed alert stays suppressed until cooldown elapses **unless severity escalates** (see rule below).
3. **Rate-limit** — per patient per alert from `threshold_config.rate_limit_per_hour` (`DM-T-05`).
4. **Per-patient alert budget (smart suppression)** — a token-bucket per `(mpi_id, severity-tier)`. When the `watch`/`normal` budget is exhausted, further low-tier alerts are **coalesced into a digest** rather than paged. Directly serves `PER-C-02` and `VIS-7.1-04`.
5. **Maintenance windows** — scheduled suppression (known procedure, device recalibration): alerts are still **recorded and audited** but not delivered/paged.

**Suppression never applies to** (patient-safety carve-outs): `critical` severity; any **severity increase** on an existing `dedup_key` (a `watch→critical` transition always surfaces — never masked by cooldown, mirroring §3.1); and operational/dead-man's-switch alerts (§7).

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
1. **The 30s SLO is the end-to-end envelope IntensiCare *owns*, measured over the five controllable stages `poll → normalize → evaluate → persist → deliver`.** The impl-plan splits are **intra-budget stage ceilings**, not independent reference frames: impl *score* maps to the **evaluate** stage, impl *alert* maps to the **deliver** stage.
2. **Production stage targets are binding** (they sum comfortably under 30s). The MVP relaxations are **re-scoped** so `evaluate_MVP ≤ 30s − Σ(other stages)`; the MVP evaluate ceiling can grow toward the headroom but **the end-to-end p95 still ≤ 30s**. The 35s contradiction disappears because the two impl numbers were never meant to be added *against* the vision ceiling — they sit *inside* it.
3. **Source freshness is inherited and excluded from the committed SLO.** Upstream AMH source→Gold latency (≤30 min p95, `ADR001-F-02`) is outside IntensiCare's control (`ADR001-C-01`/`C-10`) and is surfaced for transparency, not counted in the 30s. End-to-end bedside→alert = `source_freshness + owned_pipeline`.

### 8.1 Stage table (each p95; near-real-time path unless noted)

| # | Stage | p95 | Assumption | Source ref |
|---|---|---|---|---|
| 0 | **source freshness** *(INHERITED — not in the 30s)* | NRT ≈ **2 s**; **batch ≤ 30 min** | NRT: operational stream/monitor datum query-visible ≈2s. Batch: AMH Gold P95 <30 min — uncontrollable, held separate. | `ADR001-F-02`, `ADR001-C-10` |
| 1 | **poll** | **1,000 ms** | Event pickup from Redis stream (NRT) / expedited micro-batch trigger. | `VIS-2-08` (Redis pub/sub), `IMP-3.2-05` |
| 2 | **normalize** | **500 ms** | Parse HL7/FHIR → canonical units at the edge; within the ingest-vital write envelope. | `IMP-C-12` (<500ms MVP), `CON-SEED-12` |
| 3 | **evaluate** | **5,000 ms** | Run score + alert-definition predicates (production score budget). | `IMP-C-13` (score <5s prod) |
| 4 | **persist** | **500 ms** | Write `clinical_score` + `alert` + `audit_trail` (ON CONFLICT / append). | `IMP-C-12`, INV-1 (`CON-0066`), INV-2 (`CON-0067`) |
| 5 | **deliver** | **2,000 ms** | ARQ enqueue → WS/mobile push, at-least-once. | `IMP-C-14` (alert <2s prod), INV-6 (`CON-0071`), `CON-0092` (<5s RRT) |
| | **Owned pipeline Σ (stages 1–5, linear upper bound)** | **9,000 ms = 9 s** | Conservative — a linear sum of stage p95s over-estimates true e2e p95 (stages not perfectly correlated). | vs ceiling **`VIS-C-09` 30 s** |

**Checks.** Owned Σ **9s ≪ 30s** ceiling (`VIS-C-09`), leaving ~21s headroom that absorbs MVP relaxation and the sum-vs-true-p95 slack. Deliver **2s < 5s** RRT mobile push (`CON-0092`/`PER-C-06`). Engine detection→delivery ≤9s leaves the remainder of the **5-min** critical action window for the human response (`CON-0062`). Throughput target **>500 alerts/min** (`VIS-C-11`) and availability **99.9%** (`VIS-C-10`) are unaffected by this decomposition (ARQ/Redis horizontal scale).

**Barrier C3 note.** Final signoff of these stage numbers, of the source-freshness exclusion, and of the Alternativa-B trigger (§1.2) belongs to C3 (latency + PPV), co-owned with amh-integration-architect and platform-reliability-engineer. Full machine-readable budget: `docs/plan/_work/budgets/latency.yaml`.

**Canonical-source designation (`CON-SEED-01`, B3-005).** This §8 is the **sole canonical PROSE** statement of the `CON-SEED-01` resolution. `docs/plan/_work/budgets/latency.yaml` is its **machine-readable companion — the single source of the numbers** (it self-describes as such, not as a competing canonical). `observability-slo.md §3` is a **downstream restatement** that must introduce no number absent from `latency.yaml`. The three artifacts state one resolution once, not three times: prose here, numbers in `latency.yaml`, SRE-facing restatement in `observability-slo.md §3`.

---

## 9. Alert lifecycle state machine (every transition audited — INV-1; feeds PPV analytics)

Task lifecycle `raise → acknowledge → act → resolve` reconciled with the data-model `status` enum `{active, acknowledged, resolved, expired}` (`DM-VOCAB-04`) and `resolution` enum `{true_positive, false_positive, intervention_done}` (`DM-VOCAB-05`).

```
                 ack-SLA breach                     action-SLA breach
                 (system/timer)                     (system/timer)
        ┌──────────────────────────┐        ┌──────────────────────────┐
        ▼                          │        ▼                          │
  ┌──────────┐  ack (clinician) ┌────────────┐  act (clinician) ┌────────┐  resolve ┌──────────┐
  │  RAISED  │────────────────▶ │ACKNOWLEDGED│────────────────▶ │ ACTING │────────▶ │ RESOLVED │
  │ (active) │                  │            │                  │        │          │(true_pos/│
  └──────────┘                  └────────────┘                  └────────┘          │false_pos/│
     │   │                            │                                              │interv.)  │
     │   │ condition clears / TTL     │ resolve (direct)                             └──────────┘
     │   └───────────────▶ ┌─────────┐│                                               (terminal)
     │  auto-clear         │ EXPIRED │◀┘
     │                     └─────────┘
     │ ack-SLA breach            (terminal)
     ▼
 ┌───────────┐  ack (escalation-tier clinician / RRT)
 │ ESCALATED │──────────────────────────────────────▶ (ACKNOWLEDGED)
 └───────────┘
```

| From | To | Actor | Audited | SLA / trigger |
|---|---|---|---|---|
| — | **raised** (active) | system (engine) | ✅ | definition predicate fires + passes suppression |
| raised | **acknowledged** | clinician (1-click, `CON-0091`/`PER-C-05`) | ✅ | ack-window: crit 2 min / urg 10 min / watch 60 min |
| acknowledged | **acting** | clinician | ✅ | intervention start |
| acting | **resolved** | clinician | ✅ | action-window: crit <5 min / urg <30 min / watch <2h (`CON-0062..64`); sets `resolution` |
| acknowledged | **resolved** | clinician | ✅ | direct resolve; sets `resolution` |
| raised | **escalated** | system (timer) **or** clinician (manual "Escalar agora") | ✅ | ack-window breached → **band-aware** climb: `watch` (`PT60M`) → assigned clinician (R2), **not** RRT; `urgent`/`critical` → page next tier (RRT). Manual "Escalar agora" early-triggers the same transition (`triggered_by` = system vs user_id) |
| acknowledged | **escalated** | system (timer) **or** clinician (manual "Escalar agora") | ✅ | action-window breached → page next tier. Manual "Escalar agora" early-triggers the same transition (`triggered_by`) |
| escalated | **acknowledged** | escalation-tier clinician | ✅ | — |
| raised | **expired** | system | ✅ | triggering condition cleared before ack, or alert TTL |

- **Every transition writes an immutable `audit_trail` row** (INV-1, `CON-0066`; append-only + anti-mutation trigger). Legal requirement (LGPD + CFM 1.821/07).
- **`acting` and `escalated` extend the data-model `status` enum** (currently active/acknowledged/resolved/expired). Auto-clear routes to `expired` to stay within the enum; human resolutions use `true_positive/false_positive/intervention_done`. **Reconciliation (→ C2 / data-architect):** add `acting` + `escalated` (or model `acting` as acknowledged + `intervention_started_at`, `escalated` as a flag). The persistence side of this reconciliation is now adopted in `data-model.md` §3/§4.1/§10 (B2-001).
- **Escalation actor + target (canonical with `severity-model.yaml` and `alert-routing.md` §2):** the `raised → escalated` and `acknowledged → escalated` transitions may be driven by the **system timer** OR by a **clinician manually** ("Escalar agora"); the manual path is an *early trigger of the same transition*, audited with `triggered_by` distinguishing `system` from a `user_id` (B2-002). The `raised → escalated` climb is **band-aware** (B2-003): a `watch` breaching its `PT60M` ack-SLA escalates to the **assigned clinician (R2)**, **never** to the RRT; only `urgent` and `critical` climb toward the RRT tier (`alert-routing.md` §2 is the source of the correct ladder). The `watch` §3 delivery descriptor therefore reads "no page *at raise*; escalates to the assigned clinician on `PT60M` ack breach", not "no escalation".
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
