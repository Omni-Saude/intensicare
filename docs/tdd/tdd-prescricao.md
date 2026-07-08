# TDD: Prescrição — Medication Prescription System

- **Status:** draft
- **Domain:** prescricao (clinical — medication management)
- **ADRs:** ADR-026 (Drug Interaction Safety), ADR-027 (Prescription Lifecycle State Machine)
- **Contracts:** docs/contracts/prescricao-openapi.yaml

---

## 1. Context and Scope

### 1.1 Business Context

The Prescrição module is the medication prescription subsystem of IntensiCare, an intensive-care clinical information system. It replaces a legacy system that encodes 43 business rules for safe medication prescribing in the ICU setting. The new system must preserve all existing safety guarantees while improving extensibility, auditability, and interoperability.

### 1.2 Scope

| In Scope | Out of Scope |
|---|---|
| Creation, modification, and lifecycle management of medication prescriptions | Pharmacy dispensing and inventory management |
| Drug-drug and drug-allergy interaction checking at prescription time | Real-time vital-signs integration for dose triggers |
| Weight-based dose calculation with renal adjustment and pediatric safeguards | Billing and insurance coding |
| Structured scheduling with frequency patterns | Nurse administration workflow (handled by administração module) |
| Full audit trail on all mutations (LGPD compliance) | Drug formulary management (external master data) |
| Optimistic concurrency control | Offline/prescribing |
| Prescription lifecycle state machine (draft → active → completed / discontinued) | Clinical decision support beyond drug interactions |

### 1.3 Legacy Rule Inventory (43 rules)

The 43 legacy rules are grouped into the following categories:

1. **Dose Validation (12 rules)** — Weight-based ceilings, renal adjustment thresholds, pediatric weight-band limits, maximum single-dose caps, maximum daily-dose caps, infusion-rate limits, concentration-range checks, age-contraindicated drugs, pregnancy-category blocks, lactation warnings, duplicate-therapy detection, tapering-requirement flags.

2. **Interaction Checking (8 rules)** — Drug-drug interactions (severity levels: contraindicated, severe, moderate, minor), drug-allergy cross-reactivity, drug-food interactions, duplicate-ingredient detection, cumulative-QT-prolongation risk, serotonergic-syndrome risk, nephrotoxic-combination alerts, hepatotoxic-combination alerts.

3. **Scheduling and Administration (7 rules)** — Frequency validation (QID, TID, BID, QD, QOD, PRN, continuous), interval-minimum enforcement, administration-window tolerance, PRN lockout intervals, infusion-rate ramp-up/down, incompatible-Y-site detection, sequence-dependent administration ordering.

4. **Lifecycle and Workflow (6 rules)** — Draft-to-active authorization gate, active-to-completed auto-transition on stop date, active-to-discontinued clinical-reason requirement, modification-scope restrictions per state, co-signature requirements for high-risk drugs, renewal-required-before-expiry.

5. **Patient Safety (6 rules)** — Allergy verification (must be checked before first dose), weight-required-for-weight-based drugs, renal-function-required-for-renally-cleared drugs, pregnancy-test-required gate, duplicate-prescription detection, maximum-duration limits.

6. **Data Integrity and Audit (4 rules)** — Optimistic locking on concurrent edits, immutable audit log, soft-delete only (no hard delete), PHI encryption at rest.

---

## 2. High-Level Design

### 2.1 Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                      │
│  POST   /api/v1/prescricao           Create prescription      │
│  GET    /api/v1/prescricao/{id}      Read prescription        │
│  PUT    /api/v1/prescricao/{id}      Update prescription      │
│  POST   /api/v1/prescricao/{id}/state Transition lifecycle    │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                   Service Layer                               │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ Prescription │  │  Interaction  │  │ Dose Calculator    │   │
│  │ Lifecycle    │  │  Engine       │  │ (weight/renal/     │   │
│  │ State Machine│  │  (ADR-026)    │  │  pediatric)        │   │
│  │ (ADR-027)    │  │               │  │                    │   │
│  └──────┬───────┘  └──────┬────────┘  └─────────┬──────────┘   │
│         │                 │                     │              │
│  ┌──────▼─────────────────▼─────────────────────▼──────────┐   │
│  │                 Validation Pipeline                      │   │
│  │  (43 legacy rules as composable validators)              │   │
│  └────────────────────────┬─────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     Data Layer                                   │
│  ┌──────────────┐  ┌────────────────┐  ┌───────────────────┐    │
│  │ Prescription  │  │ Drug Database   │  │ Audit Log         │    │
│  │ Repository    │  │ (local cache +   │  │ (immutable,       │    │
│  │ (ORM +        │  │  external       │  │  encrypted)       │    │
│  │  versioning)  │  │  ANVISA API)    │  │                   │    │
│  └──────────────┘  └────────────────┘  └───────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

| Component | Responsibility |
|---|---|
| **Prescription Lifecycle State Machine** | Enforces legal state transitions (draft → active → completed/discontinued). Guards each transition with preconditions. See ADR-027. |
| **Interaction Engine** | Checks drug-drug and drug-allergy interactions against ANVISA-approved database. Uses local cache with external fallback. Returns severity-graded alerts. See ADR-026. |
| **Dose Calculator** | Computes weight-based doses (mg/kg), applies renal adjustment factors (Cockcroft-Gault), enforces pediatric weight-band limits. |
| **Scheduling Engine** | Parses frequency abbreviations into concrete administration times. Validates interval minima. Handles PRN lockout and continuous infusion rate schedules. |
| **Validation Pipeline** | Composes all 43 rules as independent, chainable validators. Each validator returns pass/fail/warn with structured reasons. |
| **Audit Service** | Records every mutation as an immutable, encrypted audit event. Provides tamper-evident log for LGPD compliance. |

### 2.3 Data Flow — Create Prescription

```
Client Request
    │
    ▼
[1] Deserialize & validate request body (Pydantic)
    │
    ▼
[2] Load patient context (weight, renal function, allergies, age, pregnancy status, active prescriptions)
    │
    ▼
[3] Run Validation Pipeline (43 rules) against proposed prescription + patient context
    │
    ├── FAIL (hard block) ──► 422 with structured errors
    ├── WARN (soft alert) ──► Continue with warnings in response metadata
    │
    ▼
[4] Run Interaction Engine (ADR-026)
    │   ├── Check local drug database cache
    │   └── Fallback to external ANVISA API on cache miss
    │
    ├── CONTRAINDICATED ──► 409 Conflict with interaction details
    ├── SEVERE/MODERATE ──► Warning in response, requires override confirmation
    │
    ▼
[5] Calculate dose (if weight-based / renal-adjusted / pediatric)
    │
    ▼
[6] Generate schedule from frequency pattern
    │
    ▼
[7] Persist with version=1, encrypt PHI fields at rest
    │
    ▼
[8] Record audit event: CREATE
    │
    ▼
201 Created — Return prescription resource with warnings metadata
```

### 2.4 Data Flow — Lifecycle Transition

```
Client Request (POST /{id}/state)
    │
    ▼
[1] Load prescription with optimistic lock check (version)
    │
    ▼
[2] State Machine: evaluate transition guard
    │   ├── draft → active:  requires authorization (prescriber + co-signature if high-risk)
    │   ├── active → completed: requires stop_date in past
    │   ├── active → discontinued: requires clinical_reason
    │   └── Other transitions: rejected
    │
    ├── GUARD FAILED ──► 422 with guard violation details
    │
    ▼
[3] Apply state transition, increment version
    │
    ▼
[4] Record audit event: STATE_TRANSITION (from → to)
    │
    ▼
200 OK — Return updated prescription
```

---

## 3. Data Model

### 3.1 Core Entities

#### Prescricao (Prescription)

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK, immutable | Generated server-side |
| `patient_id` | UUID | FK → Patient, required | Links to patient master data |
| `medication_id` | UUID | FK → Medication, required | Links to drug formulary |
| `estado` | Enum | `draft`, `active`, `completed`, `discontinued` | Lifecycle state (ADR-027) |
| `dose` | Decimal(10,4) | > 0, required | Prescribed dose in mg |
| `dose_unit` | Enum | `mg`, `mcg`, `g`, `UI`, `mEq`, `mmol` | Unit of measure |
| `dose_calculation` | JSON | nullable | Weight-based calc metadata: `{weight_kg, mg_per_kg, renal_factor, pediatric_factor}` |
| `via_administracao` | Enum | `IV`, `IM`, `SC`, `PO`, `NG`, `SL`, `TOP`, `IN` | Route of administration |
| `frequencia` | Enum | `QID`, `TID`, `BID`, `QD`, `QOD`, `PRN`, `CONTINUOUS` | Frequency pattern |
| `frequencia_detalhe` | JSON | nullable | Schedule details: `{interval_hours, specific_times[], prn_lockout_minutes, infusion_rate_ml_h}` |
| `data_inicio` | DateTime | required | First administration date/time |
| `data_fim` | DateTime | nullable, ≥ data_inicio | Stop date (auto-completes on passage) |
| `instrucoes` | Text | nullable, max 2000 chars | Free-text administration instructions |
| `prescritor_id` | UUID | FK → User, required | Prescribing clinician |
| `co_signatario_id` | UUID | FK → User, nullable | Co-signing clinician (high-risk drugs) |
| `indicacao_clinica` | Text | nullable | Clinical indication/reason |
| `versao` | Integer | ≥ 1, required | Optimistic lock version |
| `criado_em` | DateTime | auto, immutable | Creation timestamp |
| `atualizado_em` | DateTime | auto | Last modification timestamp |
| `criado_por` | UUID | FK → User, immutable | Creator |
| `atualizado_por` | UUID | FK → User | Last modifier |

#### InteracaoAlerta (Interaction Alert)

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | Generated |
| `prescricao_id` | UUID | FK → Prescricao | Parent prescription |
| `medicamento_interagente_id` | UUID | FK → Medication | Interacting drug |
| `tipo` | Enum | `drug_drug`, `drug_allergy`, `drug_food`, `duplicate_ingredient` | Interaction type |
| `gravidade` | Enum | `contraindicated`, `severe`, `moderate`, `minor` | Severity level |
| `mecanismo` | Text | required | Clinical mechanism description |
| `recomendacao` | Text | required | Recommended clinical action |
| `fonte` | Enum | `anvisa_local`, `anvisa_external` | Data source |
| `resolvido` | Boolean | default false | Whether clinician acknowledged |
| `resolvido_por` | UUID | nullable | Who resolved |
| `resolvido_em` | DateTime | nullable | When resolved |
| `criado_em` | DateTime | auto | When detected |

#### AuditoriaPrescricao (Audit Entry)

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | Generated |
| `prescricao_id` | UUID | FK → Prescricao, indexed | Target prescription |
| `acao` | Enum | `CREATE`, `UPDATE`, `STATE_TRANSITION`, `SOFT_DELETE` | Action type |
| `estado_anterior` | JSON | nullable | Snapshot before mutation (encrypted) |
| `estado_posterior` | JSON | required | Snapshot after mutation (encrypted) |
| `diferencas` | JSON | nullable | Diff of changed fields |
| `motivo` | Text | nullable | Reason for change (required for discontinue) |
| `realizado_por` | UUID | FK → User, required | Who performed the action |
| `realizado_em` | DateTime | auto, required | When performed |
| `ip_origem` | String(45) | required | Client IP address |
| `user_agent` | Text | nullable | Client user agent |

#### AgendaPrescricao (Schedule)

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | Generated |
| `prescricao_id` | UUID | FK → Prescricao | Parent prescription |
| `horario_previsto` | DateTime | required | Scheduled administration time |
| `horario_realizado` | DateTime | nullable | Actual administration time |
| `dose_administrada` | Decimal(10,4) | nullable | Actual dose given |
| `status` | Enum | `pending`, `administered`, `missed`, `refused`, `held` | Administration status |
| `enfermeiro_id` | UUID | FK → User, nullable | Administering nurse |
| `observacao` | Text | nullable | Administration notes |

### 3.2 Supporting Enums and Value Objects

```python
class EstadoPrescricao(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"

class Frequencia(str, Enum):
    QID = "QID"           # 4x/day (every 6h)
    TID = "TID"           # 3x/day (every 8h)
    BID = "BID"           # 2x/day (every 12h)
    QD = "QD"             # 1x/day (every 24h)
    QOD = "QOD"           # every other day
    PRN = "PRN"           # as needed
    CONTINUOUS = "CONTINUOUS"  # continuous infusion

class ViaAdministracao(str, Enum):
    IV = "IV"             # intravenous
    IM = "IM"             # intramuscular
    SC = "SC"             # subcutaneous
    PO = "PO"             # oral
    NG = "NG"             # nasogastric
    SL = "SL"             # sublingual
    TOP = "TOP"           # topical
    IN = "IN"             # inhaled

class GravidadeInteracao(str, Enum):
    CONTRAINDICATED = "contraindicated"
    SEVERE = "severe"
    MODERATE = "moderate"
    MINOR = "minor"

class ResultadoValidacao(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
```

### 3.3 State Machine Definition (ADR-027)

```
                    ┌──────────┐
                    │  DRAFT   │
                    └────┬─────┘
                         │
              ┌──────────▼──────────┐
              │    activate()       │
              │  Guards:            │
              │  - prescritor auth  │
              │  - co-sign if       │
              │    high-risk drug   │
              │  - interactions     │
              │    resolved         │
              │  - dose validated   │
              └──────────┬──────────┘
                         │
                    ┌────▼─────┐
                    │  ACTIVE  │
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
    ┌─────────▼──┐  ┌────▼─────────┐
    │ complete() │  │ discontinue()│
    │ Guard:     │  │ Guard:       │
    │ - stop     │  │ - clinical   │
    │   date in  │  │   reason     │
    │   past     │  │   required   │
    └──────┬─────┘  └──────┬───────┘
           │               │
    ┌──────▼───┐    ┌──────▼────────┐
    │COMPLETED │    │ DISCONTINUED  │
    └──────────┘    └───────────────┘

Allowed transitions:
  DRAFT → ACTIVE          (activate)
  ACTIVE → COMPLETED      (complete, auto on stop_date passage)
  ACTIVE → DISCONTINUED   (discontinue, requires clinical_reason)
  DRAFT → DISCONTINUED    (discard draft)

Disallowed transitions (rejected with 422):
  ACTIVE → DRAFT
  COMPLETED → ANY
  DISCONTINUED → ANY
  DRAFT → COMPLETED       (must pass through ACTIVE)
```

---

## 4. APIs and Contracts

### 4.1 Endpoint Summary

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/prescricao` | Create a new prescription (draft state) | prescriber |
| `GET` | `/api/v1/prescricao/{id}` | Retrieve prescription by ID | clinician |
| `PUT` | `/api/v1/prescricao/{id}` | Update prescription fields (state-dependent scope) | prescriber |
| `POST` | `/api/v1/prescricao/{id}/state` | Transition prescription lifecycle state | prescriber |

Full contract: `docs/contracts/prescricao-openapi.yaml`

### 4.2 Request/Response Patterns

#### POST /api/v1/prescricao — Create Prescription

**Request Body (abridged):**
```json
{
  "patient_id": "uuid",
  "medication_id": "uuid",
  "dose": 500.0,
  "dose_unit": "mg",
  "via_administracao": "IV",
  "frequencia": "TID",
  "data_inicio": "2026-07-08T08:00:00Z",
  "data_fim": "2026-07-15T08:00:00Z",
  "instrucoes": "Diluir em 100ml SF 0.9%. Infundir em 30 min.",
  "indicacao_clinica": "Pneumonia adquirida na comunidade"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "estado": "draft",
  "versao": 1,
  "...": "...",
  "alertas": [
    {
      "tipo": "drug_allergy",
      "gravidade": "moderate",
      "mecanismo": "Cross-reactivity with documented penicillin allergy",
      "recomendacao": "Monitor for allergic reaction. Consider alternative."
    }
  ],
  "dose_calculation": {
    "weight_kg": 70.0,
    "mg_per_kg": 7.14,
    "renal_factor": 1.0,
    "pediatric_factor": null
  }
}
```

#### PUT /api/v1/prescricao/{id} — Update Prescription

**Headers:**
```
If-Match: 1   (optimistic lock — must match current versao)
```

**Response 409 (version conflict):**
```json
{
  "error": "version_conflict",
  "message": "Prescription was modified by another user. Reload and retry.",
  "current_version": 2,
  "your_version": 1
}
```

**Response 422 (state restricts modification):**
```json
{
  "error": "modification_not_allowed",
  "message": "Cannot modify dose on an ACTIVE prescription. Discontinue and create a new one.",
  "current_state": "active",
  "blocked_fields": ["dose", "dose_unit", "medication_id"]
}
```

#### POST /api/v1/prescricao/{id}/state — Transition Lifecycle

**Request Body:**
```json
{
  "transition": "activate",
  "co_signatario_id": "uuid"  // required for high-risk drugs
}
```

**Response 422 (guard failure):**
```json
{
  "error": "transition_guard_failed",
  "transition": "draft → active",
  "failed_guards": [
    {
      "guard": "interactions_resolved",
      "detail": "1 severe and 2 moderate interactions are unresolved"
    },
    {
      "guard": "co_signature_required",
      "detail": "Medication requires co-signature (high-risk: anticoagulant)"
    }
  ]
}
```

### 4.3 Error Codes

| HTTP Status | Code | Meaning |
|---|---|---|
| 201 | — | Prescription created |
| 200 | — | Success |
| 400 | `invalid_frequency` | Frequency incompatible with route or medication |
| 400 | `invalid_schedule` | Schedule parameters invalid |
| 404 | `prescription_not_found` | ID does not exist or is soft-deleted |
| 409 | `version_conflict` | Optimistic lock mismatch |
| 409 | `interaction_contraindicated` | Contraindicated interaction blocks create/update |
| 409 | `duplicate_prescription` | Same drug, same patient, overlapping period |
| 422 | `validation_failed` | One or more validation rules failed |
| 422 | `transition_guard_failed` | State transition preconditions not met |
| 422 | `modification_not_allowed` | Field cannot be modified in current state |
| 422 | `dose_out_of_range` | Dose exceeds safety limits |
| 422 | `missing_required_data` | Weight/renal/allergy data missing for safety check |

---

## 5. Critical Flows

### 5.1 Happy Path — Full Prescription Lifecycle

```
1. CREATE (draft)
   Clinician creates prescription for Ceftriaxone 1g IV BID.
   → System validates dose against weight (no adjustment needed).
   → Interaction engine checks: no contraindications, 1 moderate alert.
   → Created in DRAFT state, version 1.
   → Audit log: CREATE event.

2. REVIEW & ACTIVATE
   Clinician reviews alerts, acknowledges moderate interaction.
   → POST /{id}/state {transition: "activate"}
   → Guard checks: prescriber authorized, interactions resolved, dose validated.
   → Transition: DRAFT → ACTIVE, version 2.
   → Audit log: STATE_TRANSITION event.

3. UPDATE (active — limited scope)
   Nurse adjusts administration instructions (instrucoes field).
   → PUT /{id} with If-Match: 2
   → State allows modification of instrucoes but not dose/medication.
   → Version 3.
   → Audit log: UPDATE event (diferencas: instrucoes changed).

4. COMPLETE
   Stop date passes (data_fim < now).
   → Background job or manual trigger: POST /{id}/state {transition: "complete"}
   → Guard: data_fim must be in the past.
   → Transition: ACTIVE → COMPLETED, version 4.
   → Audit log: STATE_TRANSITION event.
```

### 5.2 Edge Case — Discontinue with Clinical Reason

```
1. Prescription is ACTIVE.
2. Patient develops acute kidney injury. Clinician decides to discontinue nephrotoxic drug.
3. POST /{id}/state {transition: "discontinue", motivo: "AKI — Cr 3.2, suspender vancomicina"}
4. Guard: motivo (clinical_reason) is present and non-empty → passes.
5. Transition: ACTIVE → DISCONTINUED.
6. Audit log records the clinical reason.
```

### 5.3 Edge Case — Contraindicated Interaction Blocks Activation

```
1. Prescription created in DRAFT for Warfarin 5mg PO QD.
2. Patient has active prescription for Ciprofloxacin (strong CYP interaction).
3. Interaction engine returns: CONTRAINDICATED (INR risk).
4. Attempt to activate fails — transition guard "interactions_resolved" fails.
5. Clinician must either:
   a. Discontinue the conflicting prescription first, OR
   b. Override with documented clinical justification (if policy allows).
```

### 5.4 Edge Case — Concurrent Modification (Optimistic Lock)

```
1. Clinician A loads prescription (version 3).
2. Clinician B loads same prescription (version 3).
3. Clinician B updates instrucoes → succeeds, version becomes 4.
4. Clinician A attempts to update dose → sends If-Match: 3.
5. Server rejects: 409 version_conflict (current_version: 4, your_version: 3).
6. Clinician A must reload and re-apply changes.
```

### 5.5 Edge Case — Pediatric Dose Safety

```
1. Patient is 3 years old, 14 kg.
2. Prescription for Paracetamol, weight-based dosing.
3. Dose Calculator:
   - Standard: 10-15 mg/kg/dose → 140-210 mg
   - Pediatric weight-band ceiling: max 500 mg/dose
   - Renal adjustment: not applicable (normal renal function)
4. If dose specified as 800mg → FAIL (exceeds weight-band ceiling for 14kg).
5. System returns 422 with dose range recommendation.
```

### 5.6 Edge Case — Renal Adjustment

```
1. Patient: Cr 3.8 mg/dL, weight 80 kg, age 65, female.
2. Cockcroft-Gault: eCrCl ≈ 14 mL/min (severe impairment).
3. Prescription for Meropenem (renally cleared).
4. Dose Calculator:
   - Standard dose: 1g Q8H
   - Renal factor: 0.25 (CrCl 10-25 → reduce to 25%)
   - Recommended: 250mg Q12H
5. Warning raised if prescribed dose deviates >20% from calculated recommendation.
```

### 5.7 Edge Case — PRN Scheduling with Lockout

```
1. Prescription: Morphine 2mg IV PRN for pain.
2. PRN detail: lockout interval = 4 hours (minimum time between doses).
3. Scheduling engine enforces: even though PRN, no dose can be administered
   within 4 hours of the previous dose.
4. Attempting to schedule a dose at T+2h → 422 violation.
```

### 5.8 Edge Case — Continuous Infusion Rate Validation

```
1. Prescription: Noradrenaline 4mg in 250ml D5W, continuous IV.
2. Infusion rate: 5-30 ml/h (typical range).
3. Frequency: CONTINUOUS with infusion_rate_ml_h = 50 → FAIL.
4. Rate exceeds safety ceiling for concentration. System recommends valid range.
```

---

## 6. Security Controls

### 6.1 Authentication and Authorization

| Concern | Implementation |
|---|---|
| Authentication | JWT Bearer token (OAuth2) — validated by API gateway |
| Authorization (coarse) | Role-based: `prescriber` (create/activate), `clinician` (read), `admin` (override) |
| Authorization (fine) | Row-level: clinician must belong to patient's care team |
| Co-signature | High-risk drugs require a second prescriber's approval before activation |
| Override | Severe interaction overrides require elevated privilege + audit justification |

### 6.2 Data Protection (LGPD)

| Requirement | Implementation |
|---|---|
| PHI encryption at rest | AES-256-GCM on `estado_anterior`, `estado_posterior` in audit table; transparent field-level encryption via ORM |
| PHI encryption in transit | TLS 1.3 minimum for all API endpoints |
| Data minimization | Audit log captures only changed fields (`diferencas`), not full snapshots where unnecessary |
| Right to access | Patient data export endpoint returns all prescriptions + audit trail |
| Right to deletion | Soft-delete only (required for clinical audit integrity); anonymization after legal retention period (20 years) |
| Data residency | All data stored in Brazil (AWS sa-east-1 / on-premises) |
| Access logging | Every read and write to prescription data is logged with timestamp, user, IP, and action |

### 6.3 Audit Trail

- **Immutable**: Audit entries are append-only, no update or delete operations permitted at the database level (table permissions: INSERT + SELECT only).
- **Tamper-evident**: Each audit entry includes a SHA-256 hash of the previous entry, forming a cryptographic chain.
- **Encrypted**: Patient-identifiable data within audit entries (`estado_anterior`, `estado_posterior`) is encrypted at the application layer before persistence.
- **Retention**: 20 years minimum (Brazilian medical records requirement).

### 6.4 Input Validation

- All string fields: length limits, character whitelist (UTF-8, no control characters).
- All numeric fields: range checks enforced at the API boundary (Pydantic) and service layer.
- UUID fields: validated format, referential integrity checked.
- Date/time: `data_inicio` ≤ `data_fim`, no dates in the distant past/future without explicit override.

---

## 7. Observability

### 7.1 Metrics

| Metric Name | Type | Description |
|---|---|---|
| `prescricao_create_total` | Counter | Total prescription creations (by medication, unit) |
| `prescricao_state_transition_total` | Counter | State transitions (by from_state, to_state) |
| `prescricao_interaction_alert_total` | Counter | Interaction alerts (by severity, type) |
| `prescricao_interaction_contraindicated_total` | Counter | Contraindicated blocks |
| `prescricao_validation_failure_total` | Counter | Rule validation failures (by rule_id) |
| `prescricao_version_conflict_total` | Counter | Optimistic lock conflicts |
| `prescricao_dose_override_total` | Counter | Dose overrides by clinicians |
| `prescricao_drug_db_cache_hit_ratio` | Gauge | Cache hit rate for local drug database |
| `prescricao_request_duration_seconds` | Histogram | API request latency (by endpoint) |

### 7.2 Logging

| Level | Event | Content |
|---|---|---|
| INFO | Prescription created | `{prescription_id, patient_id, medication_id, user_id}` |
| INFO | State transition | `{prescription_id, from_state, to_state, user_id}` |
| WARN | Interaction detected | `{prescription_id, severity, interaction_type, drugs[]}` |
| WARN | Contraindicated blocked | `{prescription_id, interaction_id, drugs[]}` |
| WARN | Version conflict | `{prescription_id, client_version, server_version}` |
| ERROR | Drug DB unavailable | `{source, attempt, latency_ms, error}` |
| ERROR | Validation pipeline error | `{prescription_id, rule_id, exception}` |
| ERROR | Encryption failure | `{operation, entity_type, entity_id}` |

### 7.3 Alerts

| Alert | Condition | Severity | Response |
|---|---|---|---|
| High contraindication rate | >5 contraindicated interactions in 10 minutes | P2 | Investigate drug database quality |
| Drug DB cache misses >50% | Cache hit ratio < 0.5 for 5 minutes | P2 | Check ANVISA external API health |
| Encryption service down | Any encryption failure in last 1 minute | P1 | Immediate response — PHI unprotected |
| Audit log write failure | Any INSERT failure on audit table | P0 | Critical — stop accepting mutations |
| Version conflict rate spike | >20 conflicts in 5 minutes | P3 | Check for UI issues causing stale reads |

---

## 8. Implementation Plan

### 8.1 Phases

#### Phase 0 — Foundation (Week 1-2)
- **Dependencies**: Database schema, patient/allergy data available
- **Deliverables**:
  - Database migrations: `prescricao`, `interacao_alerta`, `auditoria_prescricao`, `agenda_prescricao` tables
  - ORM models and base repository with optimistic locking
  - Pydantic schemas for all request/response DTOs
  - Field-level encryption setup for PHI columns
  - Audit log append-only table with hash chain
- **Effort**: 5 days

#### Phase 1 — Core Prescription CRUD (Week 2-3)
- **Deliverables**:
  - `POST /api/v1/prescricao` — create prescription in draft state
  - `GET /api/v1/prescricao/{id}` — read prescription with all relations
  - `PUT /api/v1/prescricao/{id}` — update with optimistic locking
  - State-dependent field modification scope enforcement
  - Soft-delete support
  - Full audit logging on all mutations
- **Effort**: 5 days

#### Phase 2 — State Machine (Week 3) — ADR-027
- **Deliverables**:
  - State machine engine with transition table and guard evaluation
  - `POST /api/v1/prescricao/{id}/state` endpoint
  - Guard implementations: authorization, interactions-resolved, co-signature, stop-date, clinical-reason
  - State transition audit events
- **Effort**: 3 days

#### Phase 3 — Validation Pipeline (Week 3-4)
- **Deliverables**:
  - Validator framework (chain-of-responsibility pattern)
  - Implementation of all 43 legacy rules as validators
  - Dose Calculator: weight-based, renal adjustment (Cockcroft-Gault), pediatric weight-bands
  - Scheduling Engine: frequency → concrete times, PRN lockout, infusion rate validation
  - Structured validation result aggregation (pass/warn/fail per rule)
- **Effort**: 5 days

#### Phase 4 — Interaction Engine (Week 4) — ADR-026
- **Deliverables**:
  - Local ANVISA drug database cache (SQLite or embedded Postgres extension)
  - Drug-drug interaction lookup (pairwise severity matrix)
  - Drug-allergy cross-reactivity lookup
  - External ANVISA API fallback client with circuit breaker
  - Cache warming and TTL-based refresh strategy
  - Integration into create/update flow
- **Effort**: 5 days

#### Phase 5 — Scheduling & Administration Integration (Week 5)
- **Deliverables**:
  - Schedule generation on activation (from frequency pattern to concrete times)
  - Administration event ingestion from nurse workflow
  - Dose-due alerts and missed-dose detection
  - Auto-completion when stop date passes
- **Effort**: 3 days

#### Phase 6 — Observability, Testing & Hardening (Week 5-6)
- **Deliverables**:
  - Prometheus metrics instrumentation
  - Structured logging with correlation IDs
  - Alert definitions and runbooks
  - Integration tests covering all 43 rules
  - Performance testing (concurrent modification scenarios)
  - LGPD compliance audit
  - Load testing for interaction engine cache
- **Effort**: 5 days

### 8.2 Total Estimated Effort

| Phase | Days |
|---|---|
| 0 — Foundation | 5 |
| 1 — Core CRUD | 5 |
| 2 — State Machine | 3 |
| 3 — Validation Pipeline | 5 |
| 4 — Interaction Engine | 5 |
| 5 — Scheduling & Admin | 3 |
| 6 — Observability & Testing | 5 |
| **Total** | **31 days (~6 weeks)** |

### 8.3 Key Risks

| Risk | Impact | Mitigation |
|---|---|---|
| ANVISA external API instability | Interaction checks fail or time out | Local cache with 24h TTL; circuit breaker; graceful degradation (warn, don't block) |
| 43 legacy rules have undocumented edge cases | Incorrect validation during migration | Parallel-run with legacy system for 2 weeks; compare outputs |
| Performance of interaction checks at scale | Slow prescription creation | Pre-load patient's active medication list; batch interaction queries |
| Encryption key management | PHI exposure if keys compromised | AWS KMS / HashiCorp Vault; key rotation every 90 days |
| Co-signature workflow UX friction | Clinician workaround of safety gates | Minimize co-signature requirement to truly high-risk drugs only; async co-sign via notification |

---

## 9. Alternatives Considered

### 9.1 Interaction Engine: External-Only vs. Local Cache

| Approach | Pros | Cons | Decision |
|---|---|---|---|
| **External ANVISA API only** | Always up-to-date, no cache management | Latency (200-500ms), dependency on external service, rate limits | Rejected |
| **Local database only** | Fast (<5ms), offline-capable | Stale data risk, large DB maintenance burden | Rejected |
| **Local cache + external fallback (ADR-026)** | Fast normal path, up-to-date fallback, resilient | Cache invalidation complexity, dual-code-path testing | **Selected** |

### 9.2 State Machine: Conditional Logic vs. Formal FSM

| Approach | Pros | Cons | Decision |
|---|---|---|---|
| **If/else in service layer** | Simple, fast to implement | Hard to audit transitions, guards scattered, difficult to extend | Rejected |
| **Formal FSM library (transitions/py) + guard pattern (ADR-027)** | Explicit transition table, guard composition, auditable, testable | Additional dependency, learning curve | **Selected** |

### 9.3 Dose Calculation: Client-Side vs. Server-Side

| Approach | Pros | Cons | Decision |
|---|---|---|---|
| **Client-side (frontend)** | Immediate feedback, reduced server load | Inconsistent across clients, bypassable, harder to audit | Rejected |
| **Server-side** | Single source of truth, auditable, consistent | Slightly higher latency per request | **Selected** |

### 9.4 Optimistic vs. Pessimistic Locking

| Approach | Pros | Cons | Decision |
|---|---|---|---|
| **Pessimistic (SELECT FOR UPDATE)** | No conflict resolution needed | Row locks held for duration of user edit session; deadlock risk; poor UX for long edits | Rejected |
| **Optimistic (version field)** | No long-held locks, better concurrency, simpler | Requires client-side conflict resolution; potential for user frustration on conflict | **Selected** |

### 9.5 Monolithic Validation vs. Composable Pipeline

| Approach | Pros | Cons | Decision |
|---|---|---|---|
| **Single validation function** | Simple call site | 43 rules in one function = unmaintainable, untestable in isolation | Rejected |
| **Composable validator pipeline** | Each rule isolated, independently testable, easy to add/remove rules | Slightly more boilerplate | **Selected** |

---

## Appendix A: Rule-to-Validator Mapping

| # | Legacy Rule | Category | Validator Class | Outcome |
|---|---|---|---|---|
| 1 | Weight-based dose ceiling | Dose | `WeightBasedDoseCeilingValidator` | FAIL if exceeds mg/kg max |
| 2 | Renal adjustment required | Dose | `RenalAdjustmentRequiredValidator` | WARN if CrCl < 30 and no adjustment |
| 3 | Pediatric weight-band limit | Dose | `PediatricWeightBandValidator` | FAIL if exceeds age/weight band |
| 4 | Max single-dose cap | Dose | `MaxSingleDoseValidator` | FAIL if exceeds absolute max |
| 5 | Max daily-dose cap | Dose | `MaxDailyDoseValidator` | FAIL if cumulative exceeds max |
| 6 | Infusion rate limit | Dose | `InfusionRateLimitValidator` | FAIL if rate exceeds ceiling |
| 7 | Concentration range check | Dose | `ConcentrationRangeValidator` | WARN if outside standard range |
| 8 | Age-contraindicated drug | Dose | `AgeContraindicationValidator` | FAIL if drug contraindicated for age |
| 9 | Pregnancy category block | Dose | `PregnancyCategoryValidator` | FAIL if Category X and pregnant |
| 10 | Lactation warning | Dose | `LactationWarningValidator` | WARN if excreted in breast milk |
| 11 | Duplicate therapy detection | Dose | `DuplicateTherapyValidator` | FAIL if same class already prescribed |
| 12 | Tapering requirement flag | Dose | `TaperingRequirementValidator` | WARN if drug requires taper |
| 13-20 | Drug-drug interactions | Interaction | `DrugInteractionValidator` (8 sub-checks) | CONTRAINDICATED/SEVERE/MODERATE/MINOR |
| 21 | Drug-allergy cross-reactivity | Interaction | `AllergyCrossReactivityValidator` | CONTRAINDICATED/SEVERE/MODERATE |
| 22 | Drug-food interaction | Interaction | `DrugFoodInteractionValidator` | WARN |
| 23 | Duplicate ingredient | Interaction | `DuplicateIngredientValidator` | FAIL |
| 24 | Cumulative QT prolongation | Interaction | `QTcProlongationValidator` | WARN |
| 25 | Serotonergic syndrome risk | Interaction | `SerotonergicSyndromeValidator` | WARN |
| 26 | Nephrotoxic combination | Interaction | `NephrotoxicCombinationValidator` | WARN |
| 27 | Hepatotoxic combination | Interaction | `HepatotoxicCombinationValidator` | WARN |
| 28 | Frequency validation | Schedule | `FrequencyValidator` | FAIL if invalid for route/drug |
| 29 | Interval minimum enforcement | Schedule | `IntervalMinimumValidator` | FAIL if below minimum interval |
| 30 | Administration window tolerance | Schedule | `AdminWindowValidator` | WARN if window too narrow |
| 31 | PRN lockout interval | Schedule | `PrnLockoutValidator` | FAIL if lockout violated |
| 32 | Infusion ramp-up/down | Schedule | `InfusionRampValidator` | WARN if no ramp specified |
| 33 | Y-site incompatibility | Schedule | `YSiteCompatibilityValidator` | FAIL if incompatible |
| 34 | Sequence-dependent ordering | Schedule | `SequenceOrderingValidator` | WARN |
| 35 | Draft-to-active auth gate | Lifecycle | `ActivationAuthGuard` | FAIL if unauthorized |
| 36 | Active-to-completed auto | Lifecycle | `AutoCompleteGuard` | Guard: stop_date check |
| 37 | Active-to-discontinued reason | Lifecycle | `DiscontinueReasonGuard` | FAIL if no reason |
| 38 | Modification scope per state | Lifecycle | `ModificationScopeGuard` | FAIL if blocked field |
| 39 | Co-signature for high-risk | Lifecycle | `CoSignatureGuard` | FAIL if missing |
| 40 | Renewal before expiry | Lifecycle | `RenewalRequiredGuard` | WARN if expiring soon |
| 41 | Allergy verification | Safety | `AllergyVerificationValidator` | FAIL if allergies unchecked |
| 42 | Weight required | Safety | `WeightRequiredValidator` | FAIL if weight missing for weight-based drug |
| 43 | Maximum duration limit | Safety | `MaxDurationValidator` | WARN if exceeding recommended duration |

---

## Appendix B: External Dependencies

| Dependency | Purpose | SLA | Failure Mode |
|---|---|---|---|
| ANVISA Drug Interaction API | Drug-drug and drug-allergy interaction data | 99.5% uptime | Fallback to local cache; if cache miss, block with WARN |
| Patient Service | Patient demographics, weight, renal function, allergies | 99.9% uptime (internal) | Cannot create prescriptions without patient context |
| Medication Master Data | Drug formulary, routes, default doses | 99.9% uptime (internal) | Cannot create prescriptions without medication data |
| User/Auth Service | Prescriber identity, roles, credentials | 99.9% uptime (internal) | Cannot authenticate or authorize |
| Audit Service / Log Aggregator | Centralized audit log storage | 99.5% uptime | Local buffer; audit entries queued and retried |
| Notification Service | Co-signature requests, dose-due alerts | 99% uptime | Non-blocking; notifications queued |

---

*This TDD is a living document. Update as design decisions evolve through ADR amendments and implementation discoveries.*
