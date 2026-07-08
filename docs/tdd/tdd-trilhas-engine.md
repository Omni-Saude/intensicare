# TDD: Trilhas Engine — Motor de Trilhas Clínicas

- **Status:** draft
- **Domain:** Clinical / Care Pathway Engine (motor de vias de cuidado)
- **ADRs:** ADR-001 (AMH Data Platform consumer), ADR-020 (trilhas-engine architecture), ADR-021 (trilhas-engine data model)
- **Contracts:** `docs/contracts/pathways-openapi.yaml` (6 endpoints)

## 1. Context and Scope

### 1.1 Problem

The legacy IntensiCare platform runs a Django-based **trilhas-engine** — a care-pathway composition and evaluation engine that governs which clinical surveillance domains are active for a given bed, how pathway items (criteria) are evaluated, and how results surface to the frontend. An audit of 18 legacy rules (`docs/rules/extraction/phase2/catalog/trilhas-engine.yaml`) revealed systemic defects:

- **Facade/predicate drift (SYS-04):** rendered rationale diverges from actual evaluation logic
- **Chained-comparison misparse (SYS-06):** Python chained comparisons produce incorrect boolean evaluation
- **Band-edge gaps (SYS-07):** severity bands have unreachable gaps and missing boundary checks
- **Dead/unwired criteria (SYS-08):** criteria defined but never evaluated, silently failing

The 18 rules were dispositioned as: 5 RETIRE (no clinical content), 5 SUPERSEDE (replaced by v2 Alert Engine), 6 ADAPT (sound clinical intent, reimplement on new substrate), 1 ADOPT-CORRECTED (12-slug pathway-type vocabulary), and 1 RATIFIED with an AMBIGUOUS-band escalation.

### 1.2 Scope

This TDD covers the **Trilhas Engine domain service** — the v2 replacement for the legacy's pathway-composition, criterion-evaluation, and enrollment-management responsibilities. It does NOT cover:

- The Alert Engine's per-domain threshold evaluation (covered by `alert-engine.md`)
- The Correlation Engine's cross-domain aggregation (covered by `correlation-engine.md`, deferred to post-MVP)
- Phase-tracking state machine (deferred to post-MVP per ADR-020 Option 4 evaluation)

### 1.3 Key Architectural Decisions

Per ADR-020 and ADR-021, the Trilhas Engine adopts:

1. **Declarative rule engine** (not state machine, not workflow engine): every clinical domain is a set of declarative alert definitions in YAML, evaluated statelessly per patient per poll tick.
2. **Immutable, content-addressed definitions as YAML artifacts (build-time):** definitions are version-controlled files; the compiled registry is a build artifact loaded at engine startup. Alert instances stamp `definition_version_id` (SHA-256 content hash). No temporal-join ambiguity — the alert points at an exact, immutable definition.
3. **Patient-to-pathway cardinality 1:N, scoped per encounter (admission):** each `patient_pathway` row carries `mpi_id`, `encounter_id`, `bed_id`, and `unit`. The legacy's per-encounter vs per-patient-lifetime ambiguity (ESC-AMBIGUOUS-308) is resolved explicitly at the schema level.
4. **Phase-tracking state machine deferred to post-MVP:** the "patient is in sepsis screening phase" concept is derived from alert-firing patterns by the Correlation Engine — not part of the core evaluation architecture.
5. **ADR-001 compliance:** clinical data reads from AMH Gold via Athena only; no own ingestion; patient identity is `mpi_id` from the MPI.

## 2. High-Level Design

### 2.1 Component Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Trilhas Engine Domain                      │
├────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │ Pathway API │  │ Enrollment   │  │ Progress Tracker   │ │
│  │ (REST)      │  │ Manager      │  │ & Criteria Eval    │ │
│  └──────┬──────┘  └──────┬───────┘  └─────────┬──────────┘ │
│         │                │                     │            │
│  ┌──────┴────────────────┴─────────────────────┴──────────┐ │
│  │              Pathway Registry (compiled YAML)            │ │
│  │  Loaded at startup; content-addressed definitions        │ │
│  └──────────────────────────┬──────────────────────────────┘ │
│                             │                                │
│  ┌──────────────────────────┴──────────────────────────────┐ │
│  │              Operational Store (PostgreSQL)               │ │
│  │  Tables: pathway_definition, patient_pathway,             │ │
│  │  pathway_state, pathway_criteria, criteria_evaluation,     │ │
│  │  audit_trail                                              │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
┌────────────────┐           ┌────────────────────┐
│  AMH Gold      │           │  Alert Engine      │
│  (Athena)      │           │  (domain evaluator)│
│  clinical data │           │  fires alerts per  │
│  read-only     │           │  definition        │
└────────────────┘           └────────────────────┘
```

### 2.2 Data Flow

1. **Startup:** The Trilhas Engine loads the compiled pathway registry (YAML definitions validated at CI build time, content-hashed). Definitions are indexed by `domain` and `slug`.

2. **Pathway catalog queries** (`GET /pathways`, `GET /pathways/{id}`): Read from the in-memory registry, enriched with active patient counts from the operational store.

3. **Patient enrollment** (`POST /patients/{mpi_id}/pathways`): Creates a `patient_pathway` row with the patient's current `encounter_id`, `bed_id`, and `unit` (from the `patient_cache`). Sets `current_state` to the pathway's initial state. Dispatches initial criteria evaluation.

4. **Criteria evaluation** (`PUT /patients/{mpi_id}/pathways/{id}/criteria`): Updates the evaluation status of pathway criteria for the given enrollment. May trigger state transition if criteria conditions are met. Each evaluation writes an immutable `audit_trail` row (INV-1).

5. **Progress query** (`GET /patients/{mpi_id}/pathways/{id}/progress`): Returns the patient's current state, criteria summary, state history, and trend assessment — derived from the operational store, not computed on-the-fly from source data.

6. **Alert Engine integration:** The Trilhas Engine does NOT evaluate clinical thresholds — it manages pathway enrollment and criteria tracking. The Alert Engine (separate domain) evaluates clinical alert definitions and fires alerts. The two engines share the `patient_cache` and `encounter_id` context; the Alert Engine reads active pathway enrollments to determine which alert definitions are applicable.

## 3. Data Model

### 3.1 Entity-Relationship

```
pathway_definition (immutable, content-addressed)
    │
    │ 1:N
    ▼
patient_pathway (per patient, per encounter, per pathway)
    │
    ├── 1:N ──► pathway_state_history (state transitions)
    │
    └── 1:N ──► criteria_evaluation (per-criterion evaluations)
                    │
                    └── references: pathway_criteria (from definition)
```

### 3.2 Core Tables

#### `pathway_definition`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | Surrogate key |
| `slug` | VARCHAR(64) UNIQUE NOT NULL | Canonical pathway identifier (e.g., `ventilacao`, `sepse`) |
| `name` | VARCHAR(255) NOT NULL | PT-BR display name (DM-C-01) |
| `description` | TEXT | Clinical description |
| `active` | BOOLEAN DEFAULT true | Whether the pathway is active for enrollment |
| `definition_version_id` | VARCHAR(128) NOT NULL | SHA-256 content hash of the YAML definition |
| `definition_content` | JSONB NOT NULL | Normalized, canonicalized definition (states, criteria, transitions) |
| `compiled_at` | TIMESTAMPTZ NOT NULL | When the registry was compiled in CI |
| `created_at` | TIMESTAMPTZ DEFAULT NOW() | |


#### `patient_pathway`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | Surrogate key |
| `mpi_id` | VARCHAR(64) NOT NULL | Patient identity from MPI (ADR-001) |
| `encounter_id` | VARCHAR(64) NOT NULL | Admission identifier from AMH Gold |
| `pathway_definition_id` | INT FK → pathway_definition | The pathway the patient is enrolled in |
| `bed_id` | VARCHAR(32) | Current bed at time of enrollment |
| `unit` | VARCHAR(64) | Current unit at time of enrollment |
| `current_state_id` | VARCHAR(32) NOT NULL | Current state in the pathway |
| `status` | ENUM('active','completed','archived') DEFAULT 'active' | Enrollment status |
| `severity` | ENUM('normal','watch','urgent','critical') | Derived severity from criteria (CON-SEED-11) |
| `enrolled_at` | TIMESTAMPTZ DEFAULT NOW() | |
| `enrolled_by` | VARCHAR(128) | User who enrolled the patient |
| `completed_at` | TIMESTAMPTZ | |
| `updated_at` | TIMESTAMPTZ DEFAULT NOW() | |

**Indexes:**
- `(mpi_id, encounter_id)` — list patient's pathways per admission
- `(pathway_definition_id, status)` — count active enrollments per pathway
- `(bed_id, status)` — bed-board queries
- `(updated_at)` — staleness watchdog

#### `pathway_state_history`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | |
| `patient_pathway_id` | INT FK → patient_pathway | |
| `from_state` | VARCHAR(32) | Previous state (NULL for initial) |
| `to_state` | VARCHAR(32) NOT NULL | New state |
| `changed_at` | TIMESTAMPTZ DEFAULT NOW() | |
| `reason` | TEXT | Why the transition occurred (e.g., "criteria met: pf-ratio < 200, fio2 > 50") |
| `triggered_by` | VARCHAR(128) | User or system that triggered the transition |

#### `criteria_evaluation`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | |
| `patient_pathway_id` | INT FK → patient_pathway | |
| `criteria_id` | VARCHAR(64) NOT NULL | Criteria identifier from the YAML definition |
| `met` | BOOLEAN NOT NULL | Whether the criterion is satisfied |
| `value` | VARCHAR(128) | Observed value (e.g., "185" for PaO₂/FiO₂) |
| `evaluated_at` | TIMESTAMPTZ DEFAULT NOW() | |
| `evaluated_by` | VARCHAR(128) | User or system that performed evaluation |

#### `audit_trail` (INV-1, shared schema)

Every state transition writes an immutable audit row: `entity_type='patient_pathway'`, `entity_id`, `action` (e.g., `state_transition`, `criteria_evaluated`, `enrollment_created`), `actor`, `details` (JSONB), `timestamp`.

### 3.3 Pathway Definition YAML Schema

```yaml
# docs/plan/_work/pathways/<slug>.yaml
slug: ventilacao
name: "Ventilação Mecânica"
description: "Acompanhamento de pacientes em ventilação mecânica invasiva"
definition_version: "1.0.0"
active: true

states:
  - id: initial
    name: "Avaliação Inicial"
    order: 0
    description: "Paciente recém-inscrito"
  - id: weaning
    name: "Desmame"
    order: 1
    description: "Em processo de desmame ventilatório"
  - id: discharged
    name: "Alta do Pathway"
    order: 2
    is_terminal: true

criteria:
  - id: crit-pf-ratio
    name: "Relação PaO₂/FiO₂"
    category: oxigenacao
    description: "Relação entre pressão parcial de oxigênio arterial e fração inspirada de oxigênio"
    unit: mmHg
    normal_range: "> 300"
    alert_threshold: "< 200"

  - id: crit-fio2
    name: "FiO₂"
    category: oxigenacao
    unit: "%"
    normal_range: "≤ 40"
    alert_threshold: "> 50"

transitions:
  - from: initial
    to: weaning
    condition: "crit-pf-ratio.met == false AND crit-fio2.met == false"
  - from: weaning
    to: discharged
    condition: "crit-pf-ratio.met == true AND crit-fio2.met == true"
```

### 3.4 The 12-Slug Pathway Type Vocabulary (ADOPT-CORRECTED)

From `RULE-TRILHAS-ENGINE-018`, corrected to a single canonical source per DM-C-01 (`CON-0183`):

| Slug | PT-BR Label |
|------|-------------|
| `ventilacao` | Ventilação Mecânica |
| `sepse` | Sepse |
| `estabilidade` | Estabilidade Hemodinâmica |
| `sedacao` | Sedação |
| `profilaxia` | Profilaxia |
| `antimicrobiano` | Antimicrobiano |
| `nutricao` | Nutrição |
| `equilibrio` | Equilíbrio Hidroeletrolítico |
| `gloza-zero` | Glasgow Zero |
| `renal` | Função Renal / AKI |
| `delirium` | Delirium |
| `respiratorio` | Insuficiência Respiratória |

This vocabulary is adopted as the initial `slug` enumeration for `pathway_definition.slug` and maps onto the v2's 7 clinical domains.

## 4. APIs and Contracts

### 4.1 Contract Reference

Full OpenAPI specification: `docs/contracts/pathways-openapi.yaml`

### 4.2 Endpoints

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| `GET` | `/api/v1/pathways` | `listPathways` | List all available care pathways (catalog) |
| `GET` | `/api/v1/pathways/{id}` | `getPathway` | Get pathway details with criteria and states |
| `GET` | `/api/v1/patients/{mpi_id}/pathways` | `listPatientPathways` | List patient's active pathways (filterable by status) |
| `POST` | `/api/v1/patients/{mpi_id}/pathways` | `enrollPatientInPathway` | Enroll patient in a pathway (triggers initial evaluation) |
| `PUT` | `/api/v1/patients/{mpi_id}/pathways/{id}/criteria` | `updatePathwayCriteria` | Update criteria evaluation for a pathway enrollment |
| `GET` | `/api/v1/patients/{mpi_id}/pathways/{id}/progress` | `getPathwayProgress` | Get detailed progress: state, history, criteria, trend |

### 4.3 Key Request/Response Structures

- **Pathway:** `id`, `name`, `slug`, `description`, `active`, `states[]`, `criteria[]`, timestamps
- **PatientPathway:** `id`, `mpi_id`, `pathway` (embedded), `current_state`, `criteria[]` (with evaluation), `status`, `severity`, enrollment timestamps
- **PathwayProgress:** `patient_pathway_id`, `mpi_id`, `pathway_name`, `current_state`, `criteria_summary` (total/met/not_met/pending), `state_history[]`, `trend`, `recommendation`

### 4.4 Error Responses

- **404:** `{"detail": "Pathway não encontrado"}` — resource not found
- **409:** `{"detail": "Paciente já está inscrito neste pathway"}` — duplicate enrollment
- **422:** validation errors from criteria schema

## 5. Critical Flows

### 5.1 Happy Path: Patient Enrollment and Criteria Evaluation

```
1. Clinician views pathway catalog → GET /pathways
2. Clinician enrolls patient → POST /patients/{mpi_id}/pathways
   - System resolves encounter_id, bed_id, unit from patient_cache
   - Creates patient_pathway row with state='initial'
   - Writes audit_trail: enrollment_created
3. Clinician evaluates criteria → PUT /patients/{mpi_id}/pathways/{id}/criteria
   - Updates criteria_evaluation rows with met/value
   - Checks transition conditions
   - If conditions met: updates current_state, writes state_history row, writes audit_trail
4. Clinician checks progress → GET /patients/{mpi_id}/pathways/{id}/progress
   - Returns state, criteria summary, trend, recommendation
```

### 5.2 Bed Re-Association (RULE-TRILHAS-ENGINE-012 resolution)

```
1. Patient transfers from bed L-101 to L-205 → patient_cache updated
2. Re-evaluation trigger: system detects bed change for active enrollments
3. New evaluations pick up the new bed_id and unit
4. Existing patient_pathway rows are NOT migrated — bed change is historical context
5. If transfer coincides with new admission (new encounter_id):
   - Existing pathways are marked completed
   - New enrollment cycle begins for the new encounter
```

### 5.3 Ownership-Gated Acknowledgment (RULE-TRILHAS-ENGINE-007)

```
1. Alert fires for a pathway criteria violation
2. Clinician acknowledges → `acknowledged_by` is set with user ID
3. Reversal (un-acknowledge) is ownership-gated:
   - Only the acknowledging clinician OR a supervisor can reverse
   - Reversal writes audit_trail with reason
   - Implemented as application-layer check, not database constraint
```

### 5.4 Edge Cases

| Scenario | Handling |
|----------|----------|
| Patient not found in patient_cache | 404 with `detail: "Paciente não encontrado no cache de pacientes"` |
| Missing encounter_id | Patient flagged as `stale_data`; enrollment rejected with data-quality error |
| Duplicate enrollment (same patient + same pathway + same encounter) | 409 Conflict |
| Pathway deactivated after enrollment | Existing enrollments continue; new enrollments rejected |
| Criteria evaluation with unknown criteria_id | 422 with detail listing invalid criteria IDs |
| Concurrent state transitions (two clinicians evaluating simultaneously) | Optimistic locking on `updated_at`; last-write-wins with audit trail of both |
| Patient discharged (encounter closed) | All active enrollments automatically marked `completed` via batch job |

## 6. Security Controls

### 6.1 Authentication & Authorization

- **Authentication:** JWT Bearer tokens via existing IntensiCare auth endpoint
- **Authorization:** Role-based access control (RBAC):
  - `clinician`: enroll patients, evaluate criteria, view progress
  - `supervisor`: all clinician permissions + un-acknowledge alerts, archive pathways
  - `admin`: manage pathway definitions (via CI/CD, not runtime API)
  - `readonly`: view-only access to catalog and progress

### 6.2 Data Protection

- **Patient identity:** `mpi_id` from MPI; IntensiCare mints no patient identifiers (ADR-001)
- **LGPD compliance:** erasure cascade deletes all `patient_pathway`, `pathway_state_history`, `criteria_evaluation`, and `audit_trail` rows for a given `mpi_id`
- **Audit immutability:** `audit_trail` rows are append-only; no UPDATE or DELETE permitted at the application layer (INV-1)
- **Encryption:** data at rest via PostgreSQL TDE; data in transit via TLS 1.3

### 6.3 Input Validation

- All API inputs validated against OpenAPI schema at the gateway layer
- `criteria_id` values validated against the pathway's definition (not arbitrary strings)
- `encounter_id` format validated against AMH Gold convention
- SQL injection prevented via parameterized queries (SQLAlchemy ORM)

## 7. Observability

### 7.1 Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `trilhas_enrollments_total` | Counter | Total enrollment operations (by pathway, status) |
| `trilhas_criteria_evaluations_total` | Counter | Total criteria evaluations (by pathway, criteria_id) |
| `trilhas_state_transitions_total` | Counter | Total state transitions (by from_state, to_state) |
| `trilhas_active_enrollments` | Gauge | Current active enrollments (by pathway, unit) |
| `trilhas_evaluation_duration_seconds` | Histogram | Latency of criteria evaluation operations |
| `trilhas_definition_load_duration_seconds` | Histogram | Registry load time at startup |

### 7.2 Logs

- **Structured JSON** with required fields: `timestamp`, `level`, `service` (`trilhas-engine`), `trace_id`, `mpi_id` (where applicable), `encounter_id`, `action`, `message`
- **Levels:**
  - `INFO`: enrollment created, criteria evaluated, state transition
  - `WARNING`: stale patient data, criteria evaluation with missing inputs
  - `ERROR`: failed evaluation, database constraint violations, missing pathway definition

### 7.3 Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| `TrilhasHighEvaluationLatency` | p95 > 500ms for 5min | warning |
| `TrilhasEnrollmentFailures` | error rate > 1% for 5min | critical |
| `TrilhasStalePatientCache` | `stale_data` flag count > 10% of active patients | warning |
| `TrilhasDefinitionLoadFailure` | Registry fails to load at startup | critical |

## 8. Implementation Plan

### 8.1 Phases

| Phase | Deliverable | Effort | Dependencies |
|-------|-------------|--------|--------------|
| **Phase 1: Core Schema** | Database tables (`pathway_definition`, `patient_pathway`, `pathway_state_history`, `criteria_evaluation`), migrations, indexes | 2d | PostgreSQL operational store |
| **Phase 2: YAML Compiler** | CI build step: validate YAML against CONTRACTS schema, canonicalize, compute content hash, emit compiled registry JSON | 2d | CONTRACTS schema defined |
| **Phase 3: Pathway API** | `GET /pathways`, `GET /pathways/{id}` — catalog endpoints, in-memory registry | 1d | Phase 1, Phase 2 |
| **Phase 4: Enrollment API** | `GET /patients/{mpi_id}/pathways`, `POST /patients/{mpi_id}/pathways` — enrollment management with patient_cache integration | 2d | Phase 1, patient_cache service |
| **Phase 5: Criteria Evaluation** | `PUT /patients/{mpi_id}/pathways/{id}/criteria`, state transition logic, audit trail | 3d | Phase 1, Phase 4 |
| **Phase 6: Progress API** | `GET /patients/{mpi_id}/pathways/{id}/progress` — progress aggregation, trend calculation, recommendations | 2d | Phase 5 |
| **Phase 7: Integration** | Alert Engine integration, bed re-association triggers, encounter-close batch job | 2d | Alert Engine, patient_cache |
| **Phase 8: Observability** | Metrics, structured logging, alerts, Grafana dashboard | 1d | All phases |
| **Phase 9: LGPD Erasure** | Cascading delete by `mpi_id`, erasure test in CI | 1d | Phase 1 |

**Total estimated effort:** ~16 days (single developer)

### 8.2 MVP Scope Boundary

**In MVP:**
- Pathway catalog (6 endpoints)
- Patient enrollment and criteria evaluation
- State transitions with audit trail (INV-1)
- Content-addressed definitions (INV-3)
- 1:N patient-to-pathway per encounter
- 12-slug vocabulary as `pathway_definition.slug` enumeration
- Basic RBAC (clinician, supervisor, readonly)

**Deferred to post-MVP:**
- Phase-tracking state machine (Option 4 from ADR-020)
- Cross-domain correlation (Correlation Engine, `VIS-5.2`)
- Sequential checklist UX (ordered bundle items within a pathway)
- A/B testing of definition versions (`experiment_id`-keyed registries)
- `threshold_config` escape valve for per-tenant operational tuning

## 9. Alternatives Considered

### 9.1 State Machine Engine

Modeling each clinical domain as a state machine (sepsis: screening → identified → shock → resolved). Rejected because: state explosion (7 domains × N states × per-patient), imperative transition guards reintroduce SYS-04/06/07/08 defect classes, and concurrent independent criteria firing within one domain is unnatural in a state machine.

### 9.2 Workflow Engine (BPMN)

Modeling pathways as formal workflows with sequential steps and human tasks. Rejected because: clinical alerts are stateless threshold crossings, not sequential processes — gating critical alerts behind step progression is a patient-safety risk. BPMN overhead is mismatched with sub-second alert latency requirements.

### 9.3 Mutable Database Row Definitions (SCD Type 2)

Storing definitions as mutable DB rows with history tables (`alert_definition_version`). Rejected because: temporal-join ambiguity (`valid_from <= NOW()`) at validity-window boundaries is a known correctness problem. Content addressing eliminates this — the alert points at an exact, immutable artifact.

### 9.4 Patient-Pathway M:N / Per-Patient-Lifetime

Rejected in favor of 1:N per encounter. An ICU alert is an event within a specific admission — per-patient-lifetime scope conflates unrelated clinical episodes and was identified as the root cause of the legacy's AMBIGUOUS-band escalation (ESC-AMBIGUOUS-308).

---

## References

- `docs/adr/0020-trilhas-engine-architecture.md` — ADR-020: declarative rule engine architecture decision
- `docs/adr/0021-trilhas-engine-data-model.md` — ADR-021: versioned pathways, state snapshots, cardinality
- `docs/architecture/adr/ADR-001-amh-data-platform-consumer.md` — ADR-001: IntensiCare as AMH Data Platform consumer
- `docs/contracts/pathways-openapi.yaml` — REST API OpenAPI 3.1.0 specification (6 endpoints)
- `docs/rules/extraction/phase2/catalog/trilhas-engine.yaml` — catalog of 18 legacy rules with dispositions
- `docs/rules/care-pathway/RULE-TRILHAS-ENGINE-018-care-pathway-type-enumeration-assistidochoices-vs-observacao.md` — 12-slug vocabulary (ADOPT-CORRECTED)
- `docs/plan/architecture/alert-engine.md` — v2 Alert Engine architecture (definition schema, dual-runner, build-time gates)
- `docs/product/vision.md` — vision §4: 7 clinical domains and alert taxonomy
