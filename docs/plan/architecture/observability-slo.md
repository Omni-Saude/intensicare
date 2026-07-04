# Observability, SLOs & Reliability — IntensiCare v2

**Owner:** sre-observability-engineer · **Status:** draft for reconciliation barrier **C3** (latency + PPV), co-owned with alert-engine-architect and amh-integration-architect · **Authority precedence:** ADR-001 ≻ vision ≻ directive ≻ audit (CONTRACTS §5).

This document specifies how IntensiCare observes itself: the OTEL→AMP/Grafana pipeline mandated by ADR‑001, the SLO catalog (MVP vs Production), the stage-decomposed latency budget that is this deliverable's input to barrier **C3**, the dead-man's-switch/health-check design for invariant **#5**, the retry/backoff+DLQ design for invariant **#6**, a capacity model from a single 30-bed unit to multi-hospital scale, disaster-recovery targets, and alert-on-no-alerts monitoring. Every number cites a source: a brief fact id (`VIS-*`, `ADR001-*`, `IMP-*`, `PER-*`), a ledger constraint (`CON-*`), or an invariant (`INV-1..6`). Nothing here overrides `docs/plan/architecture/alert-engine.md` (the alert engine's own §7 dead-man's-switch note and §8 latency decomposition are the upstream source for §3–§4 below); this document is the **observability-and-ops** specialization: how those mechanisms are instrumented, alerted on, sized, and recovered.

---

## 1. Platform reality this document instruments (ADR‑001)

IntensiCare **emits into an existing stack, it does not stand up its own.** Metrics and traces go via **OpenTelemetry → Amazon Managed Prometheus (AMP) → Grafana**, the stack the AMH Data Platform already operates (`ADR001-C-06`/`CON-0006`: *"Métricas e traces serão emitidos via OpenTelemetry para o stack AMP + Grafana existente"*). Concretely:

- **No bespoke metrics backend, no bespoke tracing backend.** No self-hosted Prometheus/Jaeger/Tempo — that would duplicate AMH DP infrastructure exactly as ADR‑001's rejected Alternativa A duplicated ingestion (3–5× cost, `ADR001-F-03`).
- **Deployment substrate:** ECS Fargate, shared VPC/accounts with the AMH Data Platform, region **sa-east-1** (`ADR001-C-08`, `ADR001-F-04`). OTEL Collector runs as an ECS Fargate **sidecar** per task (not a shared host-level daemon, since Fargate has no host access) or as its own small Fargate service if a shared collector is preferred; either way it remote-writes to the same AMP workspace the AMH DP uses.
- **Security inheritance:** the OTEL Collector's AMP remote-write and any Grafana access ride the inherited IAM Identity Center SSO + per-tenant KMS + Lake Formation ABAC model (`ADR001-C-07`) — IntensiCare does not mint its own credentials or dashboards-as-a-separate-tenant.
- **Data-plane boundary unaffected:** telemetry (metrics/traces/logs about the *system*) is orthogonal to the Athena-only clinical-data-read boundary (`ADR001-C-01`); OTEL never carries PHI in span/metric attributes (LGPD Art. 46 / `IMP-C-04` — mirror the audit-trail's pgcrypto discipline: telemetry uses `mpi_id` only where already treated as an operational key, never name/CPF/CNS).

### 1.1 Signal inventory

| Signal | Instrument | Emits from | Key attributes |
|---|---|---|---|
| **Traces** | OTEL auto-instrumentation (FastAPI, SQLAlchemy async, httpx/Athena client, Redis, ARQ) + manual spans at stage boundaries (§3) | API service, MLLP listener, ARQ workers | `stage` (`poll_nrt\|poll_micro_batch\|normalize\|evaluate\|persist\|deliver`), `evaluation_mode` (`micro_batch\|near_real_time\|hybrid`), `alert_definition_id`, `tenant_id`, `unit_id` — never PHI |
| **Metrics** | OTEL Metrics API → AMP (Prometheus remote-write) | Same services | Counters (ingested rows, alerts raised, retries, DLQ arrivals), histograms (per-stage latency, matching §3 table), gauges (`last_poll_success_at`, `last_score_at` per unit/domain — feeds §5) |
| **Logs** | Structured JSON logs, correlated to trace id (OTEL log/trace correlation) | All services | Never a substitute for metrics/traces on the hot path — logs are for post-hoc audit correlation, not alerting latency |
| **Health/readiness** | Custom `/api/v1/health` endpoint (§4) polled by an external watchdog and scraped for readiness gauges | API service | Component readiness booleans + per-(unit,domain) staleness gauges |

### 1.2 Dashboards (Grafana, on the existing workspace)

Four dashboards, each keyed to a section below: **(a) SLO overview** (§2 catalog, error-budget burn), **(b) Latency stage waterfall** (§3 table, per-stage p50/p95/p99 + budget line), **(c) Liveness & staleness** (§5, per-unit/domain heartbeat matrix + dead-man's-switch status), **(d) Delivery & DLQ** (§6, retry counts, DLQ depth, time-in-DLQ). Every panel that plots a target line cites the source constraint in its description field so the dashboard itself is traceable back to `VIS-*`/`IMP-*`/`ADR001-*`.

---

## 2. SLO catalog — MVP vs Production

Source: implementation-plan §7.3 (`IMP-C-11..16`), cross-checked against vision §7.2 (`VIS-C-09..11`) and ADR‑001 §Consequências (`ADR001-C-10`). **These are three different scopes, not one number restated three ways** — flagging the scope distinction is itself part of this deliverable, since a naive reading could conflate them:

| SLO | Scope | MVP target | Production target | Source |
|---|---|---|---|---|
| API availability | IntensiCare's own API (uptime of `/api/v1/*`) | **99%** | **99.5%** | `IMP-C-11` |
| Platform availability | End-to-end product availability (API + delivery path) as advertised to stakeholders | — | **99.9%** | `VIS-C-10`/`VIS-7.2-02` |
| AMH data availability (inherited) | Gold-layer analytics availability, upstream of IntensiCare, not owned by it | **99.5%** (inherited, no MVP/Prod split — ADR‑001 does not phase this) | **99.5%** | `ADR001-C-10`/`ADR001-F-01` |
| Ingestion latency p95 (vital → stored) | `normalize`+`persist` stages | **< 500 ms** | **< 200 ms** | `IMP-C-12` |
| Score-calculation latency p95 | `evaluate` stage | **< 30 s** | **< 5 s** | `IMP-C-13` |
| Alert latency p95 | `deliver` stage | **< 5 s** | **< 2 s** | `IMP-C-14` |
| Ingest→alert latency p95 (end-to-end, owned pipeline) | `poll→normalize→evaluate→persist→deliver` (poll per-path: `poll_nrt`/`poll_micro_batch`) | **≤ 30 s** (envelope; see §3) | **≤ 30 s**, comfortably (Σ ≈ 9 s NRT / ≈ 16 s micro-batch) | `VIS-C-09`/`VIS-7.2-01`, resolved via `CON-SEED-01` — see §3 |
| RRT mobile-push latency | Critical-tier delivery only | — | **< 5 s** | `CON-0092`/`PER-C-06` |
| Processing throughput | Sustained alert-evaluation rate | — | **> 500 alerts/min** | `VIS-C-11`/`VIS-7.2-03` |
| False-positive rate | Per-patient-day **distribution**, all alerts (fleet mean is diagnostic only) | — | share of patient-days with > 3 dispositioned FP **≤ 5%**, and p95 FP/patient-day **< 3** | `CON-0088`/`PER-C-02`, definition: `ppv-ledger-draft.yaml` method |
| Alarm-fatigue rate | Ignored / total alerts | baseline 25% | **≤ 10%** | `VIS-7.1-04` |
| RPO (operational DB) | PostgreSQL/TimescaleDB operational store | **24 h** (daily backup) | **1 h** (WAL shipping) | `IMP-C-15` |
| RTO (operational DB) | Time to restore service | **4 h** | **1 h** | `IMP-C-16` |
| Data retention | TimescaleDB (vitals, scores, alerts) | — | **7 years** (LGPD/CFM) | `VIS-7.2-04`, `DM-RP-03` |
| Algorithm-version auditability | Every fired score/alert traceable to its exact algorithm/definition version | — | **100%** | `VIS-7.2-05`, `INV-3` |

**Note on the availability trio.** "99%/99.5%" (API), "99.9%" (platform) and "99.5%" (inherited data) are not in conflict — they measure different things at different layers — but a Grafana SLO dashboard that shows only one number invites the reader to assume it's the whole story. §2's dashboard **(a)** plots all three with distinct panels and an explicit annotation of scope, per the anti-conflation instruction above.

---

## 3. Stage-decomposed latency budget (barrier C3 input)

**This table is the canonical input this deliverable owes barrier C3.** It operationalizes the resolution already recorded for `CON-SEED-01` in `docs/plan/_work/budgets/latency.yaml` and `alert-engine.md §8`, re-expressed with **gold availability as its own explicit first row** (per this deliverable's brief) rather than folded into a generic "source freshness" label — same quantity, clearer name for an SRE audience that will alert on it directly as an AMP time series.

**The conflict this resolves (`CON-SEED-01`).** Vision states one ceiling — ingest→alert p95 **< 30 s** (`VIS-C-09`). Implementation-plan splits it into score p95 (**<30 s MVP / <5 s prod**, `IMP-C-13`) and alert p95 (**<5 s MVP / <2 s prod**, `IMP-C-14`). Summed naively at MVP, 30 s + 5 s = 35 s > 30 s — a false contradiction, resolved below.

**Resolution.** The 30 s SLO is the end-to-end envelope IntensiCare **owns**, measured over five controllable stages. Gold availability sits *before* that clock and is **inherited, not owned** (`ADR001-C-01`/`C-10`) — it is reported for transparency and for the alert-on-no-alerts watchdog (§5), but it is excluded from the committed 30 s budget. The impl-plan "score" and "alert" numbers are **intra-budget stage ceilings** (evaluate and deliver respectively), not independent frames stacked against the ceiling.

| # | Stage | p95 target (Prod) | p95 ceiling (MVP) | Included in 30s SLO? | What it measures | Source |
|---|---|---|---|---|---|---|
| 0 | **gold availability** *(AMH Gold source freshness — inherited)* | NRT path ≈ **2 s**; batch path ≤ **30 min** | same (not phased) | **No** — reported, not budgeted | Time from clinical datum origin to IntensiCare's queryable surface (Athena/Gold snapshot visibility, or operational-stream visibility for the MLLP/NRT path) | `ADR001-F-02`, `ADR001-C-10` |
| 1a | **poll_nrt** *(NRT path)* | **1,000 ms** | 1,000 ms | Yes | Event pickup from the Redis stream (NRT runner) — trigger pickup only, no Athena query on the hot path | `VIS-2-08`, `IMP-3.2-05` |
| 1b | **poll_micro_batch** *(micro-batch path)* | **8,000 ms** *(stated assumption — replaced by measured p95)* | 8,000 ms | Yes | Athena SELECT round-trip for one incremental, partition-pruned poll (queue wait + planning + S3/Iceberg scan + result fetch). Assumption stated in `latency.yaml`; instrumented as the `athena_poll_roundtrip_seconds` histogram so the pilot-measured p95 replaces it (breach re-opens C3). The ~1–2 min expedited electrolyte cadence is the *trigger interval*; this row is the per-poll query cost inside it. **Not** the §4.1 `SELECT 1`-class connectivity probe. | `ADR001-C-01`, `IMP-3.2-06` |
| 2 | **normalize** | **500 ms** | 500 ms | Yes | Parse HL7/FHIR → canonical units at the edge (build-time unit-check hook, `CON-SEED-12`, already gates this — no runtime unit-mismatch cost) | `IMP-C-12` |
| 3 | **evaluate** | **5,000 ms** | **23,000 ms** NRT / **16,000 ms** micro-batch (re-scoped per path: 30 s − poll_path − normalize 500 − persist 500 − deliver_MVP 5000; honours IMP-C-14 <5s MVP alert; not a standalone 30 s) | Yes | Run score algorithm + alert-definition predicates | `IMP-C-13`, `IMP-C-14` |
| 4 | **persist** | **500 ms** | 500 ms | Yes | Write `clinical_score` + `alert` + `audit_trail` rows (append-only INV‑1, idempotent upsert INV‑2) | `IMP-C-12`, `CON-0066`, `CON-0067` |
| 5 | **deliver** | **2,000 ms** | 5,000 ms | Yes | ARQ enqueue → WS/mobile push, at-least-once (INV‑6, §6) | `IMP-C-14`, `CON-0071`, `CON-0092` |
| | **Owned pipeline Σ — NRT path (1a + 2–5, Prod, linear upper bound)** | **9,000 ms = 9 s** | **= 30,000 ms** (MVP column sums exactly to the ceiling: 1000+500+23000+500+5000) | vs ceiling `VIS-C-09` **30 s** | Conservative — linear sum over-estimates true p95 since stages are not perfectly correlated | |
| | **Owned pipeline Σ — micro-batch path (1b + 2–5, Prod, linear upper bound)** | **16,000 ms = 16 s** | **= 30,000 ms** (8000+500+16000+500+5000) | vs ceiling `VIS-C-09` **30 s** | Same conservatism; carries the 1b Athena round-trip assumption until pilot-measured | |

**Checks.** Production Σ: NRT **9 s** and micro-batch **16 s**, both **≪ 30 s** — 21 s / 14 s of headroom absorbs the MVP `evaluate` relaxation and sum-vs-true-p95 slack on each path. `deliver` 2 s < RRT push budget 5 s (`CON-0092`) — **pass**. Engine detection→delivery ≤9 s (NRT) / ≤16 s (micro-batch) leaves the remainder of the clinical 5-minute critical action window for human response (`CON-0062`). Throughput (>500 alerts/min, `VIS-C-11`) and platform availability (99.9%, `VIS-C-10`) are unaffected by this decomposition — they scale with ARQ/Redis worker count (§7), not with per-event latency.

**What "gold availability" being row 0 changes for observability (vs treating it as a footnote):** it becomes a **first-class AMP metric** — `amh_gold_freshness_seconds` (gauge, per domain/table) — with its own panel and its own alert rule feeding §5's staleness watchdog, rather than an assumption baked silently into the pipeline. When it breaches 30 min p95, that is visible on dashboard (b) *before* it manifests as a missed clinical alert.

**Two domain classes read this table differently:**
- **NRT-path domains** (early-warning scores MEWS/NEWS2/qSOFA, hemodynamic/respiratory continuous-monitor legs) use the **2 s** gold-availability row via the operational MLLP feed and can meet the full 30 s end-to-end promise (`VIS-C-09`) today.
- **Batch-path domains** (AKI, electrolytes, drug-interactions, delirium, sepsis-lab legs) sit behind the **30-min** gold-availability row; for them, bedside→alert = 30 min + 16 s (micro-batch owned Σ, incl. the 1b Athena round-trip) and the 30 s SLO applies **from the poll boundary onward**, not end-to-end. This is acceptable against their clinical targets (AKI 6h, delirium 4–12h) except the electrolyte CRIT band, flagged as the strongest candidate for ADR‑001's Alternativa‑B streaming escape hatch (`ADR001-F-08`) — decision owned by amh-integration-architect, signoff at C3.

Machine-readable source of truth (single source of the NUMBERS): `docs/plan/_work/budgets/latency.yaml`. The **sole canonical PROSE** statement of the `CON-SEED-01` resolution is `alert-engine.md §8` (B3-005); this table is a downstream SRE-facing restatement (gold-availability promoted to row 0) and introduces **no number absent** from `latency.yaml`. The MVP `evaluate` ceiling here is corrected from 26,000 to **23,000 ms** to match `latency.yaml`, and `deliver_MVP` = 5,000 ms is now explicit, so the MVP column sums to exactly 30,000 ms and honours IMP-C-14's <5s MVP alert budget (B3-001) — the earlier "no numeric change" claim did not hold for the MVP column and is withdrawn. The poll stage is rendered per-path (`poll_nrt` 1,000 ms / `poll_micro_batch` 8,000 ms assumed Athena SELECT round-trip) with per-path Σs (9 s / 16 s), mirroring the `latency.yaml` split (RT1-LAT-03) — render-only; `latency.yaml` remains the number source.

---

## 4. Dead-man's-switch design + health-check spec — invariant #5

**Risk if absent (verbatim, `IMP-C-05`): "sistema cai e ninguém sabe"** — the system goes down and nobody knows. Because the platform reality is a batch-fed consumer (§1), the signature failure mode is not a crash but **silent staleness**: an Athena poll starts failing, scores freeze at their last value, no new alert fires, and the bed-board *looks calm* while the engine is actually blind. Two independent mechanisms convert silence into a paged signal.

### 4.1 `/api/v1/health` — readiness contract

**Current state vs spec (build gap, flagged for the API-team barrier):** `src/intensicare/main.py` today exposes only an unversioned `GET /health` returning a static `{"status": "healthy", "version", "environment"}` — a liveness stub, not a readiness probe, and not at the invariant's required path `/api/v1/health` (`IMP-C-05` verbatim path). This section is the spec that closes that gap; it is **not yet implemented**.

**Required response shape:**

```json
{
  "status": "healthy | degraded | unhealthy",
  "version": "0.1.0",
  "environment": "production",
  "checked_at": "2026-07-04T12:00:00Z",
  "components": {
    "database":        { "status": "ok", "latency_ms": 4 },
    "redis":           { "status": "ok", "latency_ms": 1 },
    "arq_workers":     { "status": "ok", "active": 4, "queued": 12 },
    "athena":          { "status": "ok", "last_probe_latency_ms": 340 }
  },
  "liveness": {
    "early_warning_scores": { "unit_a": { "last_poll_success_at": "...", "last_score_at": "...", "status": "fresh" } },
    "sepsis":                { "unit_a": { "...": "...", "status": "fresh" } },
    "aki":                   { "unit_a": { "...": "...", "status": "stale" } }
  }
}
```

- **`status`** is the worst of: any hard component failure (DB/Redis unreachable) → `unhealthy`; any component degraded or any `(unit, domain)` liveness entry `stale` (§4.2 thresholds) → `degraded`; otherwise `healthy`. HTTP status code mirrors it: 200 for `healthy`/`degraded` (still serving), 503 for `unhealthy`.
- **`components`** checks each dependency IntensiCare actually depends on per ADR‑001: PostgreSQL/TimescaleDB (operational store, `ADR001-C-03`), Redis (cache/queue, `IMP-3.2-05`), ARQ worker pool liveness (heartbeat key in Redis), and Athena connectivity (a cheap `SELECT 1`-equivalent against the Gold catalog) — the four things whose failure silently starves the pipeline. The `athena.last_probe_latency_ms` figure is **connectivity-probe latency only** (`SELECT 1`-class, hundreds of ms) — it is *not* representative of a data-poll SELECT round-trip, which is budgeted separately at `poll_micro_batch` (§3 row 1b, 8 s assumed p95).
- **`liveness`** is the per-`(unit, domain)` heartbeat matrix from §4.2 — this is what turns "the process is up" into "the process is *actually producing scores*", which is the entire point of the invariant.

### 4.2 External watchdog

- **Placement:** *outside* the ECS service being watched — a CloudWatch Synthetics canary or a small scheduled Lambda, per `IMP-C-05`'s "script externo de monitoramento" (the invariant explicitly requires the watchdog not share fate with the thing it watches).
- **Cadence:** probes `/api/v1/health` every **≤ 30 s**, aligned to the `VIS-C-09` 30 s ceiling so a health failure is detected within one SLO window.
- **Escalation — out-of-band, no shared fate (REQ-INV-5-S1).** 2 consecutive failed probes (timeout, non-2xx, or `status: unhealthy`) → page on-call. The page MUST NOT ride IntensiCare's own delivery path: it is emitted by the canary/Lambda **directly** to an **independent notification channel** — `SNS → independent pager` (e.g. SNS→PagerDuty) — that shares **no** component with the watched system: **not** the ARQ workers, **not** Redis, **not** the WebSocket/mobile-push layer that carries clinical Tier-1 alerts (`alert-engine.md §3`), and **not AMP alarm evaluation**. So the dead-man page is generated and delivered *even when IntensiCare's entire delivery layer and the AMP backend are down* — which is exactly the failure mode it exists to catch. (The earlier spec routed this "via the same interruptive channel as a critical clinical alert (Tier 1)"; that **shared fate** with the thing being watched — the specific RT1-LAT-02 defect — and is **withdrawn**.) Dead-man pages are **never rate-limited or suppressed** (mirrors the clinical carve-out in `alert-engine.md §5`).
- **No-data alarm on the probe metric itself (REQ-INV-5-S2).** The *absence* of `healthcheck_probe_result` is itself alarmed: if no probe result arrives for **> 2 probe intervals (> 60 s)**, the independent channel pages — a metric that stops arriving must never read as "healthy". This no-data alarm is evaluated **out-of-band of AMP** (on the CloudWatch metric the canary writes natively, and/or a dead-man timer on the SNS side), so a total AMP outage cannot silence it.
- **Emission (secondary — for humans, not for paging):** the watchdog *additionally* emits `healthcheck_probe_result` via OTEL → AMP (`CON-0006`) for Grafana visibility, but **AMP is never the sole path to the page** — it is the convenience dashboard, not the safety mechanism.

### 4.2.1 Failure-domain analysis — what watches the watcher

The dead-man's switch is only meaningful if its own failure is contained. The independence requirement is stated as an explicit failure-domain table (verified in the INV-5 chaos test, §8):

| Failure injected | Watched system | IC delivery layer (ARQ/Redis/WS) | AMP backend | Independent probe + SNS pager | Page still arrives? |
|---|---|---|---|---|---|
| Delivery layer dies (ARQ/Redis/WS) | down | **down** | up | up | **Yes** — probe sees non-2xx / stale liveness, SNS pages out-of-band of the dead delivery layer |
| Athena poll stalls (silent staleness) | degraded | up | up | up | **Yes** — liveness gauges go `stale`, §4.3 fires (delivery layer still up, so its normal path is valid here) |
| AMP backend outage | up | up | **down** | up | **Yes** — the no-data alarm is evaluated out-of-band of AMP; the page does not depend on AMP |
| Canary/Lambda itself dies | up | up | up | **down** | **Yes** — the SNS-side no-data timer on the probe stream (> 2 intervals) pages; this is the "watch the watcher" leg |
| Whole IntensiCare account/region loss | down | down | down | up (separate domain) | **Yes** — canary + SNS topic live in a **separate failure domain** (own account and/or paired Region) from the ECS service they probe |

The last two rows are the "quis custodiet" answer: the watcher is watched by **(a)** an SNS-side dead-man timer on the probe metric's arrival, and **(b)** placing the canary and its SNS topic in a **separate failure domain** (separate AWS account, and/or a paired Region alongside sa-east-1) from the ECS service it probes, so a blast radius that takes out IntensiCare does not also take out its watchdog. This is the one place IntensiCare deliberately does **not** reuse its own (or the shared AMP) infrastructure — the cost of a second, tiny, independent notification path is justified by the "sistema cai e ninguém sabe" risk it closes (`IMP-C-05`). Note the §4.3 alert-on-no-alerts pages ride the normal interruptive path because they detect a *different* failure mode (pipeline stale while the delivery layer is **up**); the §4.2 dead-man page is the one that must survive delivery-layer death, and it alone is out-of-band.

### 4.3 Alert-on-no-alerts (staleness watchdog) — the second, complementary mechanism

A healthy process can still be silently *wrong* — e.g. the Athena poll succeeds, returns zero new rows because of an upstream Gold ingestion stall, and no alert fires simply because nothing crossed a threshold. Per `(unit, domain)`, raise an **operational** alert (distinct from clinical alerts, but delivered through the same Tier-1 interruptive channel per §4.2) when any of:

1. `now() − last_poll_success_at > poll_interval × 3` for that domain's evaluation mode (micro-batch cadence per `alert-engine.md §1.1`).
2. An NRT/hybrid domain has ingested **zero rows** for a unit beyond its expected vitals cadence (continuous monitoring implies a maximum silent gap, e.g. 5 min for a unit with occupied beds).
3. Observed score/alert volume for `(unit, domain)` drops to **zero** over a rolling window whose historical baseline for that unit is non-zero (a statistical "nothing is happening" detector, catching the case where polling succeeds mechanically but returns no clinically meaningful signal).

Per-patient, a **stale-data badge** surfaces on the bed-board when a monitored patient has had no fresh vital within the expected window — this is the same mechanism as `alert-engine.md §7.2` / `DES-C-06`, restated here from the monitoring/alerting side: the metric backing that badge (`vital_staleness_seconds` per bed) is the same gauge the AMP dashboard (b) plots.

**Why this matters more than it looks:** this is the mechanism that makes ADR‑001's inherited ≤30-min Gold batch lag (§3, row 0) *visible* the moment it degrades, instead of degrading invisibly into a missed clinical deterioration. It is the direct answer to "sistema cai e ninguém sabe" for the failure mode that matters most in a batch-consumer architecture — not the API crashing, but the pipeline going quietly stale.

---

## 5. Retry, backoff & DLQ — invariant #6

**Risk if absent (verbatim, `IMP-C-06`): "alertas perdidos"** — alerts lost. Delivery uses **ARQ's native retry** (`IMP-3.2-06`) on every outbound notification (WebSocket push, mobile push, SMS).

### 5.1 Retry policy

| Parameter | Value | Rationale |
|---|---|---|
| Retry strategy | Exponential backoff with jitter | ARQ native (`IMP-3.2-06`); avoids thundering-herd retry storms against a degraded downstream (e.g. a push-notification provider outage) |
| Max attempts | Tiered by severity: **critical** — higher retry ceiling before DLQ (delivery is safety-critical, exhaust more budget before giving up); **watch/normal** — lower ceiling, faster fail-to-digest | Mirrors the severity-tiered delivery model in `alert-engine.md §3` (Tier 1 vs Tier 3/4) |
| Backoff base/cap | Base delay short enough that a `critical` alert's total retry window stays inside the 5-minute clinical action window (`CON-0062`) before DLQ; capped to avoid a multi-minute final-attempt gap | Delivery must fail fast enough into DLQ (§5.2) for the operational alert to still leave time for a manual channel fallback |
| At-least-once semantics | Every notification retried until channel-acked or attempts exhausted | `CON-0071`/`IMP-C-06` |
| Client-side dedup | Each notification carries `dedup_key` + monotonic `version`; clients dedup on receipt | At-least-once transport + client dedup = effectively-once UX (`alert-engine.md §7.1`) |

### 5.2 Dead-letter queue

- **Trigger:** a notification that exhausts its retry budget without a channel ack is moved to a DLQ (a dedicated Redis/ARQ queue or a `notification_dlq` table row — implementation detail for the delivery-layer owner; the **observability contract** is what follows).
- **No alert is ever silently dropped:** DLQ arrival **itself raises an operational alert** through the same Tier-1 interruptive channel as §4.2/§4.3 — a delivery failure for a `critical` clinical alert is, from the on-call SRE's perspective, exactly as urgent as the health-check failing.
- **Metrics emitted (OTEL → AMP):** `notification_retry_total{channel,severity}` (counter), `notification_dlq_total{channel,severity}` (counter), `notification_dlq_depth` (gauge), `notification_dlq_age_seconds` (histogram — time an item has sat in DLQ). Dashboard (d) plots all four; a DLQ-depth-not-draining alert rule (depth > 0 for longer than the retry window) pages on-call independently of the per-item DLQ-arrival alert, catching a stuck-drain scenario.
- **Reconciliation path:** a scheduled ARQ job periodically re-attempts DLQ items against the delivery channel (manual or automatic replay) and/or surfaces them for manual escalation (e.g. phone call to the RRT if mobile push is persistently failing) — the DLQ is a holding area with visibility, not a graveyard.

---

## 6. Capacity model: 30 → 90 beds → multi-hospital

Baseline sizing target from implementation-plan §3.2: Docker Compose is **"suficiente para 1–3 UTIs (30–90 leitos)"** — 1–3 ICUs, 30–90 beds — for the MVP deployment target. Production scales past this on ECS Fargate (`ADR001-C-08`). The stepped-wedge validation trial design (4 hospitals × 2 ICUs each, 8 clusters total, `VIS-6.2-01`) is the concrete multi-hospital reference point beyond the single-site MVP.

| Tier | Beds | ICUs / hospitals | Substrate | Vitals ingest rate (approx., 1 vitals-set/patient/5min NRT-driven units) | Alert throughput headroom vs `VIS-C-11` (>500/min) | Notes |
|---|---|---|---|---|---|---|
| **Pilot (MVP)** | 30 | 1 ICU, 1 hospital | Docker Compose, single Postgres/TimescaleDB + Redis + 1 API + 1 MLLP listener + N ARQ workers | ~6 rows/min at steady state, bursty on admission/HL7 batches | Massive headroom — 500/min target is sized for future scale, not pilot load | This is the "1–3 UTIs (30–90 leitos)" reference config (`IMP-3.2` §3.2) |
| **Single-hospital scale-out** | 90 | up to 3 ICUs, 1 hospital | Still Docker Compose per impl-plan, or early ECS Fargate migration | ~18 rows/min steady state | Comfortable headroom | Upper bound of the explicitly pinned MVP capacity target |
| **Multi-hospital (Production)** | 4 hospitals × ~2 ICUs × ~30 beds ≈ 240 beds | 8 ICUs, 4 hospitals | ECS Fargate, shared VPC/accounts with AMH DP, sa-east-1 (`ADR001-C-08`) | ~48 rows/min steady-state NRT, plus micro-batch domains poll-driven independent of bed count | Within throughput budget but no longer trivially so — first tier where ARQ worker count and Redis throughput need explicit sizing, not assumption | Matches the stepped-wedge trial's real deployment footprint — the first production multi-tenant shape this architecture must actually support |
| **Beyond trial scale** | Open-ended | N hospitals | Horizontal ECS Fargate task scaling (API + ARQ workers), Redis Cluster if single-node throughput becomes the bottleneck, per-tenant Athena workgroup isolation via Lake Formation ABAC (`ADR001-C-07`) | Scales linearly with bed count for NRT domains; batch domains scale with Gold poll partitioning, not linearly with beds | Requires the >500 alerts/min target (`VIS-C-11`) to be re-validated against real multi-hospital alert-definition fan-out, not assumed | Explicitly out of MVP scope; flagged for a dedicated capacity-planning pass once the pilot's real alert-per-bed rate is measured |

**Scaling levers, in the order they become the bottleneck:**
1. **ARQ worker count** (horizontal — stateless workers behind Redis) absorbs `evaluate`/`deliver` stage load first; each ARQ worker pool scales independently per tenant if isolation is required.
2. **Redis throughput** (pub/sub + task queue + score cache) — single-node Redis is adequate through the multi-hospital tier per the **fan-out sizing in §6.1** (previously asserted "per the sizing above", which carried no fan-out number — now quantified); a Redis Cluster migration is the next lever if pub/sub fan-out (bed-board pushes across hundreds of concurrently-viewing clinicians) saturates a single node.
3. **PostgreSQL/TimescaleDB** — hypertable chunking and read replicas for dashboard/analytics queries before write-path sharding; the operational store stays **operational-only** (`ADR001-C-03`) so historical/analytical query load is offloaded to Gold (`fact_patient_score`/`fact_alert`, `ADR001-C-04`), keeping the operational DB's write path uncontended by BI-style reads — this is a load-bearing capacity decision, not just a data-modeling one.
4. **Athena/Gold read concurrency** — bounded by the AMH DP's own capacity, inherited not owned (`ADR001-C-01`); if per-tenant Athena workgroups become a bottleneck at N-hospital scale, that is an AMH-DP-side capacity conversation, escalated via the standing `CON-0001` ownership, not something IntensiCare provisions itself.

**Load-test requirement (from impl-plan §6, Sprint 9):** *"Testes de carga (30-90 leitos simulados)"* — load tests at the pinned 30–90 bed ceiling are already a planned Fase‑3 activity; this capacity model additionally recommends a second load-test pass at the ~240-bed / 4-hospital tier before the stepped-wedge trial's intervention arms go live, since that is the first point this document identifies real headroom risk. It further requires a **storm load-test** (all-beds-critical burst, §6.1) at that tier.

### 6.1 Alert-storm capacity & latency — the ≥ 500 alerts/min burst (`VIS-C-11`)

The §3 owned-pipeline Σ (9 s p95) is validated only at steady-state trickle (~6 / 18 / 48 rows/min, table above). The committed throughput SLO is **> 500 alerts/min** (`VIS-C-11` / `VIS-7.2-03`), and the worst case is not a steady 500/min but a **correlated burst** — a power/monitor event or a mass-deterioration scenario driving **all beds critical at once**. Because `critical` is **never rate-limited, budget-suppressed, or admission-controlled** (`alert-engine.md §3` / §5 carve-outs), the delivery queue is unbounded exactly when load peaks. This section sizes the path to hold latency under that burst.

**Burst reference load.** 240-bed production tier, pathological all-beds-critical burst: up to ~240 critical alerts near-simultaneously, each fanning out to a WS push per clinician viewing that unit's bed-board **plus** a mobile page to the RRT. Sustained-rate reference: ≥ 500 alerts/min.

| Stage under storm | Bottleneck | Sizing to hold the SLO | Target under burst |
|---|---|---|---|
| **evaluate** (ARQ workers) | worker-pool saturation → queue wait | Size ARQ worker count to drain ≥ 500/min with headroom: at an estimated ~50–100 ms evaluate p50/alert, one worker clears ~600–1200/min, so **≥ 2–4 workers** hold ≥ 500/min steadily and **~8–12** clear a 240-alert burst inside the deliver window. Workers are stateless behind Redis (§6 lever 1) → scale horizontally. | evaluate p95 < 5 s under burst (`IMP-C-13`) |
| **deliver** (ARQ → WS / mobile) | at-least-once retry amplification against a degraded downstream | A **dedicated critical-tier ARQ queue** separate from watch/normal so a low-tier backlog never head-of-line-blocks a critical page; critical retry budget bounded to stay inside the 5-min action window (§5.1, `CON-0062`). | deliver p95 < 2 s; **RRT push < 5 s** (`CON-0092`) held under burst |
| **Redis fan-out** | single-node pub/sub throughput for bed-board broadcast | Single-node Redis sustains ~O(10⁴) pub/sub msg/s (est.) — adequate for the 240-bed WS fan-out; **Redis Cluster is the pre-provisioned next lever** (§6 lever 2) if concurrent-viewer fan-out (hundreds of clinicians × per-bed topics) saturates a node. Fan-out is O(critical alerts × subscribers), so the burst multiplies **here**, not at evaluate. | pub/sub publish < 50 ms p95 |
| **WebSocket broadcast** | per-connection push + reconnect storms | Coalesce bed-board grid updates (one topic-family message per bed per tick, per `realtime-channel-consolidation` ADR) rather than one WS frame per alert; cap concurrent connections per API task and scale API tasks horizontally. | grid update < 2 s; no unbounded frame amplification |

**Per-source storm detection (one operational alert, not N criticals).** When a single source (a unit, a monitor gateway, an MLLP feed) emits alerts above a burst threshold — e.g. **> 20 critical alerts / 60 s from one unit**, a rate no real physiology produces simultaneously — the engine raises **one** operational "alert-storm on `<source>`" page instead of N clinical pages, and flags the unit as storm-affected on the bed-board. All N clinical alerts are still **recorded, audited, and visible**; only the *paging* is coalesced to one operational signal, so the RRT is not paged 240 times and no clinical alert is dropped. (This detects a **source-level anomaly**, not per-patient acuity — distinct patients' criticals are never suppressed; cf. `alert-engine.md §5` carve-outs and the never-suppress invariant.)

**Validity range of the 9 s budget.** The §3 Σ = 9 s p95 holds **for arrival rates up to the sustained ≥ 500/min SLO with the worker/Redis sizing above**. Above that, or during an all-beds-critical burst without the dedicated critical queue + storm detection, deliver-stage p95 degrades first (queue wait), then evaluate. The 9 s budget is therefore stated as valid **at or below the `VIS-C-11` sustained rate with §6.1 sizing in place** — not unconditionally.

---

## 7. Disaster recovery — RPO/RTO

Source: implementation-plan §7.3 (`IMP-C-15`, `IMP-C-16`). Scope is the **operational** PostgreSQL/TimescaleDB store (`ADR001-C-03`) — the analytical Gold layer's own DR posture is inherited from, and owned by, the AMH Data Platform (out of scope here, per `ADR001-C-01`/`C-10`).

| Target | MVP | Production | Mechanism |
|---|---|---|---|
| **RPO** (max acceptable data loss) | **24 h** | **1 h** | MVP: daily `pg_dump`/snapshot backup. Production: continuous WAL shipping (point-in-time recovery), consistent with PostgreSQL 16 (`IMP-3.2-03`) + TimescaleDB 2.18 (`IMP-3.2-04`) native WAL-based PITR |
| **RTO** (max acceptable downtime to restore) | **4 h** | **1 h** | MVP: manual restore-from-snapshot runbook. Production: standby replica promotion (same-AZ or cross-AZ within sa-east-1, `ADR001-F-04`) with automated failover, cutting restore time from "rebuild from backup" to "promote and repoint" |

**Observability tie-in (why this belongs in this document, not just the DB-ops runbook):** DR posture is only as good as its **detection** latency — a WAL-shipping replica that has silently fallen behind is a false sense of safety. This document's dead-man's-switch design (§4) extends naturally to DR: `replication_lag_seconds` is emitted as an OTEL metric alongside the liveness gauges, with an alert threshold set well inside the 1‑h production RPO (e.g. paging if lag exceeds a fraction of the RPO budget, giving time to react before an actual failover event would breach it). Backup-completion is likewise a metric (`backup_last_success_at`), not just a cron-job log line — a failed nightly backup with no monitoring is the DR equivalent of the "sistema cai e ninguém sabe" risk `IMP-C-05` calls out for the live system.

**Explicitly out of scope here:** application-level DR (multi-region active-active, cross-region failover of the API tier) is not specified by implementation-plan §7.3 and is not invented in this document — the RPO/RTO table above is the literal source, restated with its observability hooks made explicit.

---

## 8. Invariant verification register — REQ-INV-5 / REQ-INV-6

Consistent with `alert-engine.md §10`'s register format, restated here from the observability/monitoring owner's perspective (what is *instrumented and alerted on*, as opposed to what is *architecturally guaranteed*):

| ID | Requirement | Observability instrumentation | Verification method | Owning component |
|---|---|---|---|---|
| **REQ-INV-5** | Dead-man's switch: `/api/v1/health` readiness + external ≤30s watchdog paging **out-of-band** via an independent SNS→pager path (no shared fate with the delivery layer or AMP, §4.2/§4.2.1 — REQ-INV-5-S1); **no-data alarm** on `healthcheck_probe_result` absence >2 intervals (REQ-INV-5-S2); alert-on-no-alerts staleness monitor per `(unit, domain)`; silence becomes a paged operational alert (`CON-0070`/`IMP-C-05`). | `healthcheck_probe_result` metric (external watchdog) with an **out-of-band no-data alarm**; independent SNS→pager channel sharing no component with ARQ/Redis/WS/AMP; per-component readiness booleans in `/api/v1/health`; `last_poll_success_at`/`last_score_at`/`vital_staleness_seconds` gauges per `(unit, domain)`/bed; Grafana dashboard (c) | Synthetic watchdog probe + alert-rule-fires test; **no-shared-fate chaos test (§4.2.1) — kill the delivery layer (ARQ/Redis/WS) AND the AMP backend → assert the out-of-band SNS page STILL arrives** within the watchdog interval (≤30s); no-data-alarm test — stop `healthcheck_probe_result` → assert page within >2 intervals; kill-the-poller test asserts staleness page (§4.3); dashboard (c) reviewed at each on-call handoff | Independent watchdog path (canary/Lambda + SNS→pager in a **separate failure domain**, §4.2.1) + Health/observability layer (`/api/v1/health` — **build gap, §4.1**) + staleness-watchdog scheduled job |
| **REQ-INV-6** | At-least-once delivery: ARQ native retry + exponential backoff on every notification; DLQ on exhaustion + operational alert; client-side dedup on `dedup_key` for effectively-once UX (`CON-0071`/`IMP-C-06`). | `notification_retry_total`, `notification_dlq_total`, `notification_dlq_depth`, `notification_dlq_age_seconds` metrics; Grafana dashboard (d) | Fault-injection test — drop channel acks — asserts retries exhaust per the tiered policy (§5.1) then land in DLQ, and that DLQ arrival raises an operational alert (§5.2); dedup test asserts no duplicate client-visible notification under forced redelivery; DLQ-depth alert-rule test | Delivery layer (ARQ workers, DLQ, WS/mobile push channels) + client-side dedup logic |

---

## 9. Constraints this document owns or discharges

| Constraint | Barrier | Where addressed |
|---|---|---|
| `ADR001-C-06`/`CON-0006` OTEL→AMP/Grafana | standing | §1 |
| `CON-SEED-01` latency-SLO split (gold-availability-first restatement, SRE-facing) | **C3** | §3 |
| `IMP-C-11..14` SLO catalog MVP/Prod | C3 | §2 |
| `CON-0070`/`IMP-C-05` INV-5 dead-man's switch + health check | B | §4 |
| `CON-0071`/`IMP-C-06` INV-6 retry/backoff + DLQ | C3 | §5 |
| `IMP-C-15`/`IMP-C-16` RPO/RTO | B | §7 |
| Capacity target "1–3 UTIs (30–90 leitos)" (impl-plan §3.2) → multi-hospital | not yet barrier-assigned | §6 |
| `VIS-C-11` throughput >500 alerts/min, `CON-0088` <3 FP/patient-day, `VIS-7.1-04` alarm fatigue ≤10% | C3 | §2, §6 |
| `CON-0092`/`PER-C-06` RRT push <5s | C3 | §2, §3, §5.1 |

**Build gap flagged, not silently fixed:** `/api/v1/health` (§4.1) does not yet exist at the invariant-required path with the required readiness contract — `src/intensicare/main.py` has an unversioned `/health` liveness stub only. This is recorded here as an implementation TODO against `INV-5`/`CON-0070`, owned jointly by the API-service team and platform-reliability-engineer (ledger owner of `CON-0070`).

**Open reconciliations flagged for C3:** the electrolyte-CRIT-band streaming escape hatch (`ADR001-F-08`, §3) remains amh-integration-architect's decision; this document's row-0 gold-availability metric is the instrumentation that will make the trigger condition (`VIS-C-09` breach on vitals-driven scores) empirically observable rather than asserted. The >500 alerts/min throughput target's storm behavior at genuine multi-hospital scale is now sized in **§6.1** (ARQ workers, dedicated critical queue, Redis fan-out, WS coalescing, per-source storm detection) and its validity range against arrival rate is stated; the residual open item is confirming the §6.1 sizing against **pilot-measured alert-per-bed rates** via the storm load-test before the stepped-wedge intervention arms go live.
