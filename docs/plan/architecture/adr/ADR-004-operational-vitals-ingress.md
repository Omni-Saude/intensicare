# ADR-DRAFT: Operational vitals ingress (HL7 MLLP → operational store) — a scoped clarification of ADR-001-C-01

Status: **draft — proposed clarification of ADR-001, pending platform-team ratification (RAT-INGRESS-01)**
Date: 2026-07-04
Author: amh-integration-architect (v2 design phase)
Clarifies: `ADR-001` §Implicação 1 (`ADR001-C-01` / `CON-0001`) — "no own ingestion (NiFi/Kafka/Debezium); Athena-only reads from AMH Gold".
Resolves red-team finding: **RT1-LAT-01** (the MLLP ↔ ADR-001 contradiction).

## Context and Problem Statement

The single most load-bearing ADR-001 constraint, `ADR001-C-01` / `CON-0001`, reads (verbatim PT):
*"O Intensicare NÃO implementará ingestão própria (NiFi, Kafka, Debezium). Lerá dados clínicos do Gold
layer da AMH Data Platform via Amazon Athena."* — IntensiCare implements no own ingestion and reads
clinical data only from AMH Gold via Amazon Athena.

Two facts are simultaneously true and appear to collide:

1. The vitals-driven early-warning promise `VIS-C-09` requires bedside→alert **p95 < 30 s**. The AMH Gold
   batch pipeline is **p95 < 30 min** (`ADR001-F-02`) — two-plus orders of magnitude too slow for the
   sub-batch vitals path (MEWS / NEWS2 / qSOFA, US-01/02/03). ADR-001 itself named this exact seam
   ("insuficiente para o caso de uso de UTI", ADR-001 open-question 1).
2. IntensiCare v2 already ships a **Phase-1 HL7 v2 MLLP listener** (`VIS-2-05`;
   `src/intensicare/mllp_listener.py`) that receives bedside-monitor **ORU-R01** messages into the
   operational TimescaleDB store.

The red-team (**RT1-LAT-01**, critical) found the deliverables handled this collision three inconsistent
ways at once: (a) recorded it as an *unresolved* conflict "routed to C3" (`alert-engine.md §1.2`),
(b) simultaneously committed the MLLP feed as delivering `VIS-C-09` < 30 s "today" (`observability-slo.md §3`,
`amh-freshness.yaml`), and (c) silently re-scoped `ADR001-C-01` to "clinical analytics"
(`system-architecture.md §3.3`). This ADR replaces those three readings with **one**.

## Decision Drivers

- `ADR001-C-01` / `CON-0001` — no own ingestion; Athena-only clinical reads from Gold. The governing
  constraint; nothing here may violate it (CONTRACTS §5: ADR-001 ≻ vision — a vision promise cannot
  silently override an ADR constraint; the reconciliation must be explicit and ratified).
- `VIS-C-09` — vitals ingest→alert p95 < 30 s; unachievable through a 30-min batch.
- The MLLP listener **already exists** (Phase 1, `VIS-2-05`) — this is a *clarification of scope*, not a
  new ingestion stack. NiFi / Kafka / Debezium remain excluded (`ADR001-F-10`).
- INV-2 idempotency (`CON-0067` / `IMP-C-02`) — HL7 `MSH-10` dedup is already specified
  (`alert-engine.md §4.1`).
- `ADR001-C-03` — the operational PostgreSQL/TimescaleDB store must never become an analytical store.

## The clarification (the ONE story every deliverable now tells)

`ADR001-C-01`'s "no own ingestion / Athena-only" governs **ANALYTICAL and clinical-context data** — labs,
medications, demographics / identity, cultures, diagnoses, documents. Those reach IntensiCare **only** from
the AMH Gold layer via Athena (or, for enrichment, the existing HAPI FHIR server, `ADR001-C-05`).
IntensiCare stands up **no** ingestion pipeline for that class of data — no NiFi / Kafka / Debezium, no
parallel lakehouse (`ADR001-F-10`).

**Bedside-monitor vital signs are a distinct class: operational telemetry, not an analytical read.** They
arrive **sub-batch via the existing Phase-1 HL7 v2 MLLP listener** (ORU-R01, `VIS-2-05`) into the
**operational** TimescaleDB store (`ADR001-C-03`), keyed idempotently on `MSH-10` (INV-2). This operational
ingress:

- feeds **only** the live near-real-time scoring path (MEWS / NEWS2 / qSOFA, and the continuous-monitor
  legs of the hemodynamic / respiratory domains);
- is **not** an analytical store and never becomes one (`ADR001-C-03`);
- does **not** replace Gold as the source of the same vitals for analytics — **the same vital signs are
  ALSO delivered to Gold by the AMH platform and are replayed from Gold** for retrospective / analytical
  scoring and for the `fact_patient_score` / `fact_alert` write-back (`ADR001-C-04`). **Gold remains the
  sole analytical source**; the operational MLLP feed is a live-scoring accelerator, not a second system
  of record.

The two feeds are therefore **not** two analytical sources in conflict — they are one **operational (live)**
path and one **analytical (canonical / replay)** path for the same physiological signal. The Athena-only
rule holds unbroken for every analytical and clinical-context read; the MLLP listener is operational
ingress, which `ADR001-C-01`'s "no own ingestion" clause does not address.

## Considered Options

1. **Pure-batch reading of `ADR001-C-01`** — no operational vitals ingress; all vitals via Gold/Athena.
   *Rejected:* makes `VIS-C-09` (< 30 s) unachievable for bedside early-warning — the core UTI use case
   ADR-001 itself flags as "insuficiente". Retained only as the fallback if this clarification is *not*
   ratified (see Consequences), and then only with an explicit hazard-log entry for the ~30-min
   early-warning latency it reintroduces.
2. **Activate Alternativa B now** — one dedicated MSK streaming topic (`ADR001-F-08`). *Rejected for MVP:*
   ADR-001 forbids MVP activation (Fase 4 only) and it is heavier than needed when a Phase-1 MLLP listener
   already exists. Alternativa B stays the **Fase-4 escape hatch**, triggered per `system-architecture.md §6`
   (quantified T1).
3. **Operational MLLP ingress for vitals, Gold-only for everything analytical, as a scoped clarification of
   `ADR001-C-01` (this ADR).** *Chosen.* Uses the existing listener, honors Athena-only for all analytical
   and clinical-context reads, keeps Gold the sole analytical source with vitals replay, preserves INV-2
   idempotency, and requires no new broker.

## Decision Outcome

Adopt **Option 3**. `ADR001-C-01` is **clarified, not overturned**: "no own ingestion / Athena-only" is
scoped to analytical and clinical-context data; bedside-monitor vitals are operational telemetry ingested
sub-batch via the existing Phase-1 MLLP listener into the operational store, with Gold retained as the sole
analytical source and vitals replayed from Gold for retrospective scoring and write-back.

This is the single reconciliation every deliverable now states:

- `architecture/system-architecture.md §3.3` presents the MLLP operational ingress as the sanctioned
  (pending-ratification) sub-batch path, not an unresolved conflict.
- `architecture/alert-engine.md §1.2` references this ADR as the resolution of the NRT-vs-Athena conflict
  it previously only "recorded and routed".
- `_work/platform/amh-freshness.yaml` `vitals_operational` is annotated as operational ingress under this
  ADR; `vitals_gold` is the analytical / replay source.
- `architecture/observability-slo.md §3` treats the NRT path's ≈ 2 s gold-availability row as the
  operational MLLP feed — now on a sanctioned basis, not an implicit exception.
- `_work/coverage/adr001-map.yaml` maps `ADR001-C-01` to this ADR (the clarifying / counter ADR) plus the
  system-architecture ingress anchor.

### Ratification note — RAT-INGRESS-01

This is a **proposed clarification of ADR-001** and is **not binding until ratified** by the ADR-001
stakeholders — **CTO Office + Time de Engenharia AMH** (`ADR001-F-09`) — jointly with amh-integration-architect,
at reconciliation barrier **B / C3**. Until ratified it is the **working design of record**. The ratification
question is narrow: *does the AMH platform team accept that an operational HL7 MLLP listener for bedside
vitals is outside the intent of `ADR001-C-01`'s "no own ingestion" clause, given the same vitals remain
Gold-sourced for all analytics?* A rejection forces Option 1 (pure batch, with the ~30-min early-warning
latency hazard logged) or an accelerated Alternativa-B decision (`system-architecture.md §6`).

### Consequences

**Good:**

- Removes the RT1-LAT-01 contradiction — one story across all five deliverables.
- `VIS-C-09` (< 30 s) becomes achievable for vitals **today**, using an already-built listener, with no new
  ingestion infrastructure and no violation of the Athena-only analytical-read rule.
- Gold stays the single analytical source of truth; no dual-source divergence risk for analytics.
- Keeps Alternativa B (MSK) as the clean Fase-4 escalation if operational MLLP proves insufficient
  (`system-architecture.md §6`, T1).

**Bad / residual:**

- Depends on platform-team ratification (RAT-INGRESS-01); until then the reconciliation is "proposed", and a
  rejection reopens the latency gap.
- Two delivery paths for one signal (operational MLLP live + Gold replay) must be reconciled so the live and
  analytical scores agree; the replay path must be proven to reproduce the live score (`algorithm_version`
  pinning, `system-architecture.md §5`) — added to the C3 validation set.
- The operational store now has a write path (MLLP) that is not a Gold read; INV-2 idempotency and the
  operational-only rule (`ADR001-C-03`) are the guardrails that keep it from drifting into a shadow
  analytical store.

## Open questions for ratification

1. **RAT-INGRESS-01** — platform-team acceptance of the scope clarification above. The single blocking
   question.
2. Whether the MLLP listener stays the permanent operational vitals path or is itself superseded by
   Alternativa B's MSK topic in Fase 4 if a broader set of sources needs sub-batch delivery
   (`system-architecture.md §6.2`).
3. The operational-vs-replay score-agreement validation (does a Gold-replayed score equal the live MLLP
   score for the same vitals set?) — owned at C3 with the latency signoff.
