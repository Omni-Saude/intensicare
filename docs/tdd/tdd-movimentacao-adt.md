# TDD: Movimentação-ADT — Gestão de Movimentação de Pacientes

- **Status:** draft
- **Domain:** Patient Movement / ADT (Admission, Discharge, Transfer)
- **ADRs:** ADR-001 (AMH Data Platform consumer), ADR-025 (Movimentação-ADT integration pattern)
- **Contracts:** `docs/contracts/movimentacao-openapi.yaml` (4 endpoints)

## 1. Context and Scope

### 1.1 Problem

ADT (Admission, Discharge, Transfer) is the operational core of any Hospital Information System (HIS). The IntensiCare platform needs accurate, low-latency awareness of patient location, admission status, and movement history to power clinical agents (e.g., Helena's follow-up journeys), bed-board dashboards, and operational analytics.

The legacy system (`ahlabs-trilhas`) maintained an **implicit, fragmented ADT state**: no dedicated movement domain, no single source of truth for patient location, and 74 rules governing the full patient lifecycle (admission types, internal transfers, discharges, edge cases like AMA discharge, evasion, early readmission). The legacy code surfaced 9 UNVERIFIABLE RATIFIED rules in `domain_movimentacao.py` — basic computational utilities (length-of-stay, bed lookup keys, patient demographic fields, camera RTSP URLs) with no orchestration layer.

Per ADR-025, the v2 IntensiCare adopts a **materialized view pattern**: the AMH Data Platform remains the canonical source of truth for ADT data; IntensiCare maintains a local materialized projection (`MovimentacaoStateStore`) in PostgreSQL, populated incrementally from CDC topics.

### 1.2 Scope

This TDD covers the **Movimentação-ADT domain service** — the complete patient movement lifecycle:

- **Patient movement history:** admission, transfer, discharge events
- **Bed grid management:** real-time bed status (free, occupied, blocked, cleaning)
- **Materialized state store:** local projection of ADT state for fast agent queries
- **LGPD erasure cascade:** partitioned by `mpi_id` with safe replay guarantees
- **Daily reconciliation:** automated divergence check against AMH Data Platform source of truth

Out of scope:
- Direct writes to Tasy HIS (prohibited per ADR-001/ADR-0013)
- Event sourcing / full event log (rejected per ADR-025, re-evaluate if >500 events/sec sustained)
- Clinical surveillance / alert evaluation (covered by Alert Engine and Trilhas Engine TDDs)

### 1.3 Key Architectural Decisions

Per ADR-025:

1. **Option 2 — Materialized view in PostgreSQL (not event sourcing, not stateless CDC consumer).** Local state store populated incrementally from AMH CDC topics. Reads are local (~5ms); writes are amortized per CDC event.

2. **AMH Data Platform is source of truth.** The local projection is an explicitly derived cache — if divergence occurs, CDC prevails. Reconstruction via snapshot + replay CDC, not independent backup.

3. **Daily reconciliation with source of truth.** Automated health check compares sampled patients' location/status against AMH Gold; divergences logged as warnings and auto-corrected via range reprocessing.

4. **LGPD-compliant erasure cascade.** Tables partitioned by `mpi_id`; erasure deletes all rows for the patient in a single transaction. CDC replay does not reintroduce erased patients (AMH suppresses their events).

5. **74 movement rules applied incrementally per CDC event.** Rules are DMN decision tables (ADR-0012); each CDC event triggers evaluation of relevant rules against the local projection. Window-based rules (e.g., "readmission <24h") query the local store, not remote CDC.

6. **ADR-001 compliance:** zero writes to Tasy or AMH Data Platform. The projection is read-only cache. Operational state changes (bed status updates) are local only and reconciled against AMH daily.

## 2. High-Level Design

### 2.1 Component Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                  Movimentação-ADT Domain Service                       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────┐  ┌───────────────┐  ┌───────────────────────────┐  │
│  │ Movement API │  │ Bed Grid API  │  │ Reconciliation Job        │  │
│  │ (REST)       │  │ (REST)        │  │ (Scheduled, daily)        │  │
│  └──────┬───────┘  └───────┬───────┘  └─────────────┬─────────────┘  │
│         │                  │                         │                │
│  ┌──────┴──────────────────┴─────────────────────────┴────────────┐  │
│  │               MovimentacaoStateStore (PostgreSQL)                │  │
│  │  Schema: movimentacao                                           │  │
│  │  Tables: patient_location_current, admission_episode,            │  │
│  │          transfer_log, discharge_summary, bed_status             │  │
│  └────────────────────────────┬────────────────────────────────────┘  │
│                               │                                       │
│  ┌────────────────────────────┴────────────────────────────────────┐  │
│  │              CDC Consumer (ADT topics)                            │  │
│  │  Topics: cdc.amh.tasy.internacao, cdc.amh.tasy.movimentacao,     │  │
│  │          cdc.amh.tasy.alta                                        │  │
│  │  DMN Rules: 74 movement rules applied incrementally              │  │
│  └────────────────────────────┬────────────────────────────────────┘  │
│                               │                                       │
└───────────────────────────────┼───────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    AMH Data Platform (source of truth)                 │
│  - CDC topics (Kafka/MSK)                                            │
│  - AMH Gold (Athena) — reconciliation queries                        │
│  - Snapshot export (S3) — bootstrap                                  │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

1. **CDC Ingestion (continuous):** The CDC consumer listens to AMH ADT topics. Each event (admission, transfer, discharge) is translated into a domain event and applied to the `MovimentacaoStateStore`.

2. **Incremental Rule Evaluation:** After state store update, relevant DMN rules (from the 74-rule catalog) are evaluated. Example: a discharge event triggers rules for discharge-without-medication, follow-up scheduling, and early-readmission detection.

3. **Agent Queries (on-demand):** Agents like Helena read from the local state store with low-latency SQL queries (no external API call to AMH). Example: "all patients discharged in the last 7 days without follow-up."

4. **API Operations (REST):** The Movement API and Bed Grid API expose the state store via the OpenAPI contract. Bed status updates (e.g., block for maintenance) are local-only operations, reconciled daily.

5. **Daily Reconciliation (scheduled):**
   - Query AMH Gold via Athena for a random sample of active patients
   - Compare `patient_location_current` and `admission_episode.status` against Gold
   - Log divergences; auto-correct by reprocessing CDC range for divergent patients
   - Emit metric `movimentacao_reconciliation_divergence_count`

6. **Bootstrap (one-time / recovery):**
   - Load snapshot from AMH Data Platform S3 export (batch)
   - Record snapshot CDC offset
   - Replay CDC events from offset to current
   - Validate consistency with a full reconciliation pass

## 3. Data Model

### 3.1 Entity-Relationship

```
admission_episode (one per patient per hospital stay)
    │
    │ 1:N
    ▼
transfer_log (movement events within an admission)
    │
    │ derives
    ▼
patient_location_current (current location, updated per transfer)
    │
    │ concludes with
    ▼
discharge_summary (terminal event for an admission)

bed_status (independent entity, updated by movement events + manual API)
    │
    │ references
    ▼
patient_location_current (current occupant)
```

### 3.2 Core Tables (Schema `movimentacao`)

#### `admission_episode`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | |
| `mpi_id` | VARCHAR(64) NOT NULL | Patient identity from MPI |
| `encounter_id` | VARCHAR(64) UNIQUE NOT NULL | Admission identifier from AMH (nr_atendimento) |
| `admission_type` | VARCHAR(32) NOT NULL | `eletiva`, `urgencia`, `transferencia_externa` |
| `admission_datetime` | TIMESTAMPTZ NOT NULL | When the patient was admitted |
| `primary_diagnosis` | VARCHAR(16) | CID-10 primary code |
| `status` | VARCHAR(16) NOT NULL | `active`, `discharged`, `transferred_out` |
| `unit_at_admission` | VARCHAR(64) | Initial unit |
| `source_cdc_offset` | BIGINT | CDC offset of the latest event applied |
| `created_at` | TIMESTAMPTZ DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ DEFAULT NOW() | |

**Indexes:**
- `(mpi_id, status)` — agent queries for active patients
- `(admission_datetime)` — temporal queries (length-of-stay, readmission windows)
- `(encounter_id)` — lookup from CDC events

#### `patient_location_current`

| Column | Type | Description |
|--------|------|-------------|
| `mpi_id` | VARCHAR(64) PRIMARY KEY | One row per admitted patient |
| `encounter_id` | VARCHAR(64) NOT NULL FK → admission_episode | Current admission |
| `unit` | VARCHAR(64) NOT NULL | Current unit (e.g., UTI-1) |
| `bed_id` | VARCHAR(32) | Current bed (e.g., L-101) |
| `specialty` | VARCHAR(64) | Responsible clinical specialty |
| `admitted_to_unit_at` | TIMESTAMPTZ | When patient arrived at current unit |
| `last_movement_at` | TIMESTAMPTZ | Timestamp of most recent movement |
| `source_cdc_offset` | BIGINT | CDC offset of the latest event applied |
| `updated_at` | TIMESTAMPTZ DEFAULT NOW() | |

**Indexes:**
- `(unit, bed_id)` — bed grid queries
- `(unit)` — unit-based filtering
- `(specialty)` — specialty-based filtering

#### `transfer_log`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | |
| `mpi_id` | VARCHAR(64) NOT NULL | |
| `encounter_id` | VARCHAR(64) NOT NULL FK → admission_episode | |
| `from_unit` | VARCHAR(64) | NULL for admission |
| `to_unit` | VARCHAR(64) | NULL for discharge |
| `from_bed` | VARCHAR(32) | |
| `to_bed` | VARCHAR(32) | |
| `transfer_datetime` | TIMESTAMPTZ NOT NULL | When the movement occurred |
| `transfer_type` | VARCHAR(32) NOT NULL | `admission`, `transfer`, `discharge` |
| `reason` | TEXT | Clinical reason for transfer |
| `source_cdc_offset` | BIGINT | CDC offset of source event |
| `created_at` | TIMESTAMPTZ DEFAULT NOW() | |

**Indexes:**
- `(mpi_id, transfer_datetime DESC)` — patient movement history
- `(encounter_id, transfer_datetime)` — per-admission timeline
- `(to_unit, transfer_datetime)` — unit inflow analysis

#### `discharge_summary`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | |
| `encounter_id` | VARCHAR(64) UNIQUE NOT NULL FK → admission_episode | One row per discharge |
| `mpi_id` | VARCHAR(64) NOT NULL | |
| `discharge_datetime` | TIMESTAMPTZ NOT NULL | |
| `discharge_type` | VARCHAR(32) NOT NULL | `domiciliar`, `transferencia_hospitalar`, `obito`, `alta_pedido`, `evasao` |
| `destination` | VARCHAR(128) | Post-discharge destination |
| `discharge_diagnosis` | VARCHAR(16) | CID-10 at discharge |
| `follow_up_scheduled` | BOOLEAN DEFAULT false | Whether follow-up was scheduled |
| `continuity_medication_prescribed` | BOOLEAN DEFAULT false | Medication continuity at discharge |
| `source_cdc_offset` | BIGINT | |
| `created_at` | TIMESTAMPTZ DEFAULT NOW() | |

**Indexes:**
- `(mpi_id, discharge_datetime DESC)` — agent queries for discharged patients
- `(discharge_datetime)` — temporal analytics
- `(follow_up_scheduled, discharge_datetime)` — follow-up gap detection

#### `bed_status`

| Column | Type | Description |
|--------|------|-------------|
| `bed_id` | VARCHAR(32) PRIMARY KEY | Unique bed identifier |
| `unit` | VARCHAR(64) NOT NULL | |
| `room` | VARCHAR(64) | Room/enfermaria |
| `status` | ENUM('free','occupied','blocked','cleaning') NOT NULL | |
| `current_patient_mpi_id` | VARCHAR(64) | NULL if free/blocked/cleaning |
| `occupied_since` | TIMESTAMPTZ | |
| `last_cleaned_at` | TIMESTAMPTZ | |
| `block_reason` | TEXT | Reason for blocked status |
| `notes` | TEXT | |
| `updated_at` | TIMESTAMPTZ DEFAULT NOW() | |

**Indexes:**
- `(unit, status)` — bed grid queries
- `(current_patient_mpi_id)` — find bed by patient

### 3.3 The 74 Movement Rules

The 74 rules govern the full movement lifecycle. They are implemented as DMN decision tables (ADR-0012) and evaluated incrementally per CDC event. Key categories:

| Category | Count | Examples |
|----------|-------|----------|
| Admission validation | ~12 | Elective vs urgency admission, external transfer validation, bed availability check |
| Transfer validation | ~18 | ICU ↔ ward transfers, surgical block → recovery, isolation requirements, bed vacancy check |
| Discharge validation | ~16 | Home discharge with/without follow-up, hospital transfer, death, AMA discharge, evasion |
| Edge cases | ~10 | Readmission <24h (same CID → quality alert), programmed readmission, post-surgical observation overflow |
| Quality / Safety alerts | ~8 | Discharge without continuity medication notification, readmission rate monitoring, prolonged LOS flag |
| Operational | ~10 | Bed cleaning status, maintenance blocking, overflow capacity, surge protocol triggers |

Rules that require temporal windows (e.g., "readmission <24h") query the local `admission_episode` and `discharge_summary` tables — no remote CDC fetch needed.

### 3.4 Legacy Rule Mapping (domain_movimentacao.py)

The 9 UNVERIFIABLE RATIFIED rules in `src/intensicare/services/domain_movimentacao.py` are utility functions preserved as-is:

| Rule | Function | Role in v2 |
|------|----------|------------|
| RULE-MOVIMENTACAO-ADT-001 | `tempo_permanencia()`, `buscar_dias_internacao()` | Length-of-stay calculation |
| RULE-MOVIMENTACAO-ADT-002 | `build_micro_indicators_payload()` | Clinical micro-indicator aggregation |
| RULE-MOVIMENTACAO-ADT-003 | `surface_expected_mortality()` | Mortality score surfacing |
| RULE-MOVIMENTACAO-ADT-005 | `build_bed_lookup_key()` | Compound bed lookup key |
| RULE-MOVIMENTACAO-ADT-006 | `bed_patient_snapshot()` | Empty-snapshot default |
| RULE-MOVIMENTACAO-ADT-007 | `patient_basic_fields()` | Patient name/age display |
| RULE-MOVIMENTACAO-ADT-008 | `build_vinculo_lookup()` | Patient-bed relationship lookup |
| RULE-MOVIMENTACAO-ADT-010 | `build_camera_rtsp_url()` | Camera RTSP URL construction |
| RULE-MOVIMENTACAO-ADT-011 | `compute_assistido_flag()` | Bed attended-flag logic |

## 4. APIs and Contracts

### 4.1 Contract Reference

Full OpenAPI specification: `docs/contracts/movimentacao-openapi.yaml`

### 4.2 Endpoints

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| `GET` | `/api/v1/patients/{mpi_id}/movements` | `listPatientMovements` | Patient movement history (filterable by type: admission/transfer/discharge) |
| `POST` | `/api/v1/patients/{mpi_id}/movements` | `registerPatientMovement` | Register a movement event (manual entry or API-driven) |
| `GET` | `/api/v1/beds` | `getBedGrid` | Bed grid with status and occupancy summary |
| `PUT` | `/api/v1/beds/{bed_id}` | `updateBedStatus` | Manually update bed status (block, free, cleaning) |

### 4.3 Key Request/Response Structures

- **PatientMovement:** `id`, `mpi_id`, `type` (admission/transfer/discharge), `from_unit`, `to_unit`, `from_bed`, `to_bed`, `timestamp`, `notes`, `registered_by`, `created_at`
- **BedStatus:** `id`, `unit`, `room`, `status` (free/occupied/blocked/cleaning), `current_patient_mpi_id`, `current_patient_name`, `occupied_since`, `last_cleaned_at`, `notes`

### 4.4 Error Responses

- **409 Conflict:**
  - Bed already occupied: `{"detail": "Leito L-101 já está ocupado"}`
  - Patient already admitted without discharge: `{"detail": "Paciente PAT-0042 já possui internação ativa sem alta"}`
  - Invalid transfer (no vacancy): `{"detail": "Unidade UTI-2 não possui vagas disponíveis"}`
- **404:** `{"detail": "Recurso não encontrado"}`

### 4.5 Manual vs CDC-Sourced Movements

- **CDC-sourced events** (from AMH topics) are the authoritative movement records
- **Manual `POST` operations** allow local registration (e.g., bed maintenance block) and are flagged with `source: "manual"` in the internal record
- Manual movements are reconciled against CDC during the daily job; CDC always prevails in case of conflict

## 5. Critical Flows

### 5.1 Happy Path: Patient Admission → Transfer → Discharge

```
1. CDC Event: patient admitted to UTI-1, bed L-101
   → INSERT admission_episode (status='active')
   → UPSERT patient_location_current (unit='UTI-1', bed_id='L-101')
   → INSERT transfer_log (type='admission', to_unit='UTI-1', to_bed='L-101')
   → UPDATE bed_status SET status='occupied', current_patient_mpi_id='PAT-0042'

2. CDC Event: patient transferred to UTI-2, bed L-205
   → INSERT transfer_log (type='transfer', from_unit='UTI-1', to_unit='UTI-2')
   → UPDATE patient_location_current (unit='UTI-2', bed_id='L-205')
   → UPDATE bed_status L-101: status='cleaning'
   → UPDATE bed_status L-205: status='occupied', current_patient_mpi_id='PAT-0042'

3. CDC Event: patient discharged home
   → UPDATE admission_episode SET status='discharged'
   → DELETE patient_location_current (patient no longer in hospital)
   → INSERT discharge_summary (discharge_type='domiciliar')
   → INSERT transfer_log (type='discharge', from_unit='UTI-2', from_bed='L-205')
   → UPDATE bed_status L-205: status='cleaning', current_patient_mpi_id=NULL
```

### 5.2 Agent Query: Discharged Patients Without Follow-Up

```
SELECT ds.mpi_id, ds.discharge_datetime, ds.discharge_type
FROM movimentacao.discharge_summary ds
WHERE ds.discharge_datetime >= NOW() - INTERVAL '7 days'
  AND ds.follow_up_scheduled = false
  AND ds.discharge_type = 'domiciliar'
ORDER BY ds.discharge_datetime DESC;
```

Returns list for Helena agent to initiate follow-up journey.

### 5.3 Bed Re-Association on Transfer (Edge Cases)

```
Scenario A: Transfer between units within same admission
→ Normal flow (5.1 step 2 above)

Scenario B: Transfer coincides with new admission (rare)
→ Previous admission_episode closed (status='discharged')
→ New admission_episode created
→ patient_location_current reflects new encounter

Scenario C: Patient transferred, but bed status update fails
→ Transfer is recorded in transfer_log and patient_location_current
→ Bed status divergence flagged in daily reconciliation
→ Auto-corrected: bed_status aligned with patient_location_current
```

### 5.4 Edge Cases

| Scenario | Handling |
|----------|----------|
| CDC event with unknown `mpi_id` | Logged as WARNING; event stored in dead-letter queue for manual review |
| CDC event out of order (late arrival) | Re-applied idempotently; `source_cdc_offset` prevents double-processing |
| Concurrent bed status update (manual + CDC) | Last-write-wins with `updated_at`; reconciliation corrects divergence |
| Patient readmitted <24h, same CID | DMN rule fires quality alert; event published to `maezo.adt.qualidade.reinternacao_precoce` |
| Discharge without continuity medication | DMN rule fires notification; event published; agent Helena picks up for follow-up |
| Bed blocked for maintenance during patient occupancy | Rejected with 409: "Leito ocupado — transfira o paciente antes de bloquear" |
| Missing encounter_id in CDC event | Patient flagged in stale-data watchdog; event deferred until encounter resolution |

## 6. Security Controls

### 6.1 Authentication & Authorization

- **Authentication:** JWT Bearer tokens (same as all IntensiCare services)
- **Authorization (RBAC):**
  - `clinician`: view patient movement history, view bed grid
  - `unit_manager`: clinician + register manual movements, update bed status
  - `admin`: full access + trigger reconciliation job
  - `readonly`: view-only (dashboards, analytics)

### 6.2 Data Protection

- **PHI (Protected Health Information):** Patient identity (`mpi_id`, `current_patient_name`) is stored in movement and bed tables. All tables are in the `movimentacao` schema with restricted access.
- **LGPD Erasure Cascade:** `DELETE FROM movimentacao.* WHERE mpi_id = $1`. Executed in a single transaction across all 5 tables. Order: `bed_status` (nullify `current_patient_mpi_id`), `transfer_log`, `patient_location_current`, `discharge_summary`, `admission_episode`.
- **CDC Replay Safety:** Erased patients are not reintroduced during CDC replay because AMH Data Platform suppresses or truncates their CDC events post-erasure (ADR-0002).
- **Encryption:** TLS 1.3 in transit; PostgreSQL TDE at rest.
- **Audit Trail:** All manual movement registrations and bed status changes write to the shared `audit_trail` table (INV-1). CDC-sourced events are auditable via the `source_cdc_offset` trace to the AMH event log.

### 6.3 Input Validation

- `mpi_id` format validated against MPI convention
- Movement `type` restricted to `admission`, `transfer`, `discharge`
- Bed `status` restricted to `free`, `occupied`, `blocked`, `cleaning`
- Transfer validation: `from_unit`/`from_bed` must match current `patient_location_current`
- Admission validation: patient must not have an active `admission_episode`
- SQL injection prevented via parameterized queries

## 7. Observability

### 7.1 Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `movimentacao_cdc_events_processed_total` | Counter | Total CDC events processed (by topic, type) |
| `movimentacao_cdc_consumer_lag` | Gauge | CDC consumer lag in seconds (per topic) |
| `movimentacao_active_patients` | Gauge | Currently admitted patients |
| `movimentacao_bed_occupancy_ratio` | Gauge | Occupied / total beds (by unit) |
| `movimentacao_movements_total` | Counter | Movement events (by type: admission/transfer/discharge) |
| `movimentacao_reconciliation_divergence_count` | Gauge | Divergences found in last reconciliation (0 = healthy) |
| `movimentacao_dmn_rule_evaluation_duration_seconds` | Histogram | Rule evaluation latency per CDC event |
| `movimentacao_lgpd_erasure_duration_seconds` | Histogram | Erasure cascade execution time |

### 7.2 Logs

- **Structured JSON** with required fields: `timestamp`, `level`, `service` (`movimentacao-adt`), `trace_id`, `mpi_id` (where applicable), `encounter_id`, `action`, `message`
- **Levels:**
  - `INFO`: CDC event processed, movement registered, bed status updated, reconciliation pass completed
  - `WARNING`: CDC consumer lag > 60s, reconciliation divergence detected, unknown `mpi_id` in CDC event
  - `ERROR`: CDC consumer crash, DMN rule evaluation failure, database constraint violation

### 7.3 Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| `MovimentacaoCDCConsumerLag` | Consumer lag > 120s for 5min | critical |
| `MovimentacaoReconciliationDivergence` | `reconciliation_divergence_count` > 0 | warning |
| `MovimentacaoHighBedOccupancy` | `bed_occupancy_ratio` > 0.95 for 10min | warning |
| `MovimentacaoDMNRuleFailures` | Rule evaluation error rate > 1% for 5min | critical |
| `MovimentacaoStaleCDCData` | No CDC events received for > 30min | critical |

### 7.4 Grafana Dashboard

Planned panels:
- **Bed Occupancy Overview:** stacked bar by unit (free/occupied/blocked/cleaning)
- **Movement Throughput:** admission/transfer/discharge rate over time
- **CDC Consumer Health:** lag, throughput, error rate
- **Active Patients by Unit:** current count with LOS distribution
- **Reconciliation Status:** divergence count, last successful run
- **Readmission Alert Feed:** recent <24h readmissions by same CID

## 8. Implementation Plan

### 8.1 Phases

| Phase | Deliverable | Effort | Dependencies |
|-------|-------------|--------|--------------|
| **Phase 1: Schema & Migration** | Create `movimentacao` schema, all 5 tables, indexes, FK constraints | 1d | PostgreSQL operational store |
| **Phase 2: CDC Consumer** | Kafka/MSK consumer for 3 ADT topics, event translation, idempotent upsert logic, dead-letter queue | 3d | AMH CDC topics access |
| **Phase 3: State Store Population** | Incremental state store update logic (admission → transfer → discharge), bed status sync | 2d | Phase 1, Phase 2 |
| **Phase 4: DMN Rule Engine** | 74 movement rules as DMN decision tables, incremental evaluation per CDC event, event publishing for quality/safety alerts | 3d | Phase 3, DMN engine (ADR-0012) |
| **Phase 5: REST API** | Movement history, movement registration, bed grid, bed status update (4 endpoints) | 2d | Phase 3 |
| **Phase 6: Reconciliation Job** | Daily job: Athena query for sample patients, compare with state store, log/auto-correct divergences, Grafana metric | 2d | Phase 3, AMH Gold Athena access |
| **Phase 7: Bootstrap Procedure** | Snapshot load from S3, offset recording, CDC replay, full reconciliation validation | 2d | Phase 2, Phase 3, Phase 6 |
| **Phase 8: LGPD Erasure** | Cascading delete procedure, erasure test in CI, CDC replay safety validation | 1d | Phase 3 |
| **Phase 9: Observability** | Metrics, structured logging, alerts, Grafana dashboard | 1d | All phases |

**Total estimated effort:** ~17 days (single developer)

### 8.2 MVP Scope Boundary

**In MVP:**
- CDC consumer for 3 ADT topics
- Materialized state store (all 5 tables)
- Movement history API and bed grid API (4 endpoints)
- 74 movement rules evaluated incrementally (DMN)
- Daily reconciliation with AMH Gold
- Bootstrap procedure (snapshot + replay)
- LGPD erasure cascade
- Basic RBAC

**Deferred to post-MVP:**
- Full event sourcing (re-evaluate if >500 events/sec sustained)
- Real-time bed-board WebSocket push (REST polling sufficient for MVP)
- Advanced analytics (LOS prediction, readmission risk scoring)
- Integration with external bed management systems beyond Tasy

## 9. Alternatives Considered

### 9.1 Stateless CDC Consumer (No Local State)

Query CDC on-demand per agent interaction. Rejected because: latency dependency on external CDC/API call (~50-200ms vs ~5ms local), inability to run temporal window queries without scanning CDC history, and coupling agent SLA to upstream platform SLA. Per ADR-025, this option would require re-evaluating 74 rules from scratch per interaction — prohibitive cost.

### 9.2 Full Event Sourcing (Kafka Event Log + Projections)

Maintain a complete internal event log of all movements (`maezo.adt.movimentacao` topic), with projections derived via KStreams. Rejected for MVP because: complexity disproportionate to a ~200-500 bed hospital's event volume (~50-200 events/min), expanded LGPD erasure surface (events contain PHI requiring crypto-shredding), and infrastructure cost (additional Kafka topics, stream processing). Re-evaluation trigger per ADR-025: if sustained event rate exceeds ~500/sec.

### 9.3 Direct Tasy Queries (Bypass AMH Data Platform)

Query Tasy HIS directly for patient location and movement data. Rejected because: violates ADR-001 (IntensiCare is an AMH Data Platform consumer, not a Tasy client), introduces a second data path with its own consistency problems, and Tasy's operational database is not designed for the query patterns agents need (temporal windows, aggregations).

### 9.4 Event-Driven Without CDC (API Polling)

Poll AMH Gold REST API periodically for movement changes. Rejected because: polling introduces latency (polling interval) and misses transient states (a patient transferring through 3 units in 10 minutes would only capture the final state). CDC provides ordered, incremental event stream — the correct primitive for movement tracking.

---

## References

- `docs/adr/0025-movimentacao-adt-integration-pattern.md` — ADR-025: integration pattern decision (materialized view, 74 rules, daily reconciliation)
- `docs/architecture/adr/ADR-001-amh-data-platform-consumer.md` — ADR-001: IntensiCare as AMH Data Platform consumer
- `docs/contracts/movimentacao-openapi.yaml` — REST API OpenAPI 3.1.0 specification (4 endpoints)
- `src/intensicare/services/domain_movimentacao.py` — existing partial implementation (9 UNVERIFIABLE RATIFIED rules)
- `docs/rules/extraction/phase2/catalog/movimentacao-adt.yaml` — catalog of 74 movement rules
- `docs/plan/architecture/data-model.md` — v2 operational data model
- `docs/architecture/adr/ADR-0002-lgpd-data-erasure.md` — LGPD erasure architecture (referenced)
- `docs/architecture/adr/ADR-0012-dmn-decision-tables.md` — DMN rule engine (74 rules implementation)
- `docs/architecture/adr/ADR-0013-cdc-consumer-contract.md` — CDC consumer contract (referenced)
