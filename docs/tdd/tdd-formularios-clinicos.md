# TDD: Formulários Clínicos — Dynamic Clinical Forms Engine

- **Status:** draft
- **Domain:** formularios-clinicos (Clinical Documentation / Dynamic Forms)
- **ADRs:** ADR-029 (Hybrid form engine: client-side rendering + server-side validation with shared schema)
- **Contracts:** `docs/contracts/formularios-clinicos-openapi.yaml` (3 endpoints)

## 1. Context and Scope

### 1.1 Problem

The legacy IntensiCare platform encodes **49 business rules** for structured clinical assessment forms — RASS (sedation), CAM-ICU (delirium), BPS/NRS (pain), Glasgow (coma), SOFA (organ failure), LPP/NPUAP (pressure injury staging), and multi-discipline global assessments (nursing, physiotherapy, speech therapy, psychology, music therapy, pharmacy).

An audit of the 49 legacy rules (`docs/rules/extraction/phase2/catalog/formularios-clinicos.yaml`) revealed systemic defects:

- **Type discrepancy across tiers:** RASS values stored as `number` in frontend vs `string` in backend (RULE-EVOLUCOES-003, cross-referenced as RULE-FORMULARIOS-CLINICOS-006)
- **Duplicate forms between roles:** LPP/NPUAP form duplicated verbatim between nursing and nutrition (`dataFormEnfermagem` / `dataFormNutricionista` — RULE-FORMULARIOS-CLINICOS-002)
- **Divergent vocabularies:** Peri-wound edema codes differ (`crepitacao_edema_com_sulco_maior_4cm` vs `crepitacao_maior_4cm`); exudate options reduced from 5 (BWAT standard) to 4 (RULE-FORMULARIOS-CLINICOS-002/003/004)
- **Implausible numeric bounds:** O₂ flow rate ceiling of 1000 L/min (RULE-FORMULARIOS-CLINICOS-012), no unit labeling on vasoactive drug quantities (RULE-FORMULARIOS-CLINICOS-042)
- **No cross-field validation:** If RASS = -5 (unarousable), CAM-ICU should be non-applicable — no such rule enforced
- **Three independent visibility mechanisms:** Nullify switch, `checavel` display-toggle, permission-driven disabling — inconsistent and fragile

The 49 rules were dispositioned as: **28 ADOPT** (preserved as-is), **10 ADOPT-CORRECTED** (fixed spelling/code-drift/required-field bugs while keeping clinical content), **2 ADAPT** (changed mechanism but same clinical intent), **4 RETIRE** (icons, routing artifacts), and **5 RATIFIED via escalation** (UNVERIFIABLE/AMBIGUOUS rules escalated per policy).

### 1.2 Scope

This TDD covers the **Formulários Clínicos domain** — the v2 dynamic clinical forms engine replacing the legacy's 15+ `dataForm*` configs and the `CollapsedFields` visibility system:

| In Scope | Out of Scope |
|---|---|
| Dynamic form rendering from declarative `FormConfig` TypeScript definitions | Rich-text narrative evolution rendering (covered by ADR-028) |
| Client-side Zod validation generated from config | Pharmacy dispensing workflow |
| Server-side Pydantic validation congruent with client | Real-time vital-signs integration for alerts |
| Cross-field conditional visibility (show/hide, require/optional) | Drug interaction checking (covered by ADR-026/prescricao) |
| Auto-scoring for RASS, CAM-ICU, Glasgow, SOFA (server-computed) | Billing/insurance coding |
| Form versioning (`definition_version` on every submission) | Nurse administration workflow |
| Form composition for role-specific extensions (base + extensions) | |
| Offline-first submission with IndexedDB queue + Background Sync | |
| Save-draft / partial submission | |
| Audit trail on all form config mutations (INV-3) | |

### 1.3 Key Architectural Decisions

Per ADR-029 (Option 3 — Hybrid):

1. **`FormConfig` TypeScript as authoring source of truth.** Forms defined as TypeScript objects in `frontend-v2/lib/form-engine/configs/`. The engine renders directly from these (zero fetch, <50ms FCP).

2. **Build-time schema generation.** A CI script compiles each `FormConfig` into:
   - JSON Schema for documentation/cross-platform validation
   - Pydantic models for server-side validation
   Both artifacts are commit-and-versioned. Congruence is guaranteed by construction.

3. **`definition_version` as first-class citizen.** Every `FormConfig` carries a semantic version (e.g., `"rass-v1.0"`). Propagated to generated artifacts, sent on submission, stored with the record, used to select the correct validation schema.

4. **Cross-field validation DSL.** A declarative `CrossFieldRule` grammar in `FormConfig` drives both Zod `.refine()` (client) and Pydantic validators (server), replacing the legacy's three independent visibility mechanisms.

5. **Offline-first with deferred sync.** Forms render from the JS bundle. Submissions queued in IndexedDB; synchronized via Background Sync API when online. Server re-validates and rejects stale-schema submissions with draft preservation.

6. **Form composition via `composeForms()`.** Base forms + role-specific extensions eliminate the verbatim duplication between nursing/nutrition LPP forms.

7. **Scoring metadata in `FormConfig`.** `scoring: { type, version, components, serverComputed }` tells the client whether scoring is server-side (SOFA, Glasgow) or can be computed locally.

## 2. High-Level Design

### 2.1 Component Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                   Formulários Clínicos Domain                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────┐  ┌────────────────┐  ┌───────────────────┐  │
│  │ Clinical Forms  │  │ Form Schema    │  │ Scoring Engine    │  │
│  │ API (FastAPI)   │  │ Registry       │  │ (server-side)     │  │
│  │ 3 endpoints     │  │ (in-memory)    │  │ SOFA/Glasgow/     │  │
│  │                 │  │                │  │ RASS/CAM-ICU      │  │
│  └───────┬─────────┘  └───────┬────────┘  └─────────┬─────────┘  │
│          │                    │                      │            │
│  ┌───────┴────────────────────┴──────────────────────┴─────────┐  │
│  │              Form Validation Layer (server-side)              │  │
│  │  Pydantic models generated from FormConfig TypeScript         │  │
│  │  Cross-field validators (clinical invariants)                 │  │
│  └──────────────────────────────┬───────────────────────────────┘  │
│                                 │                                  │
│  ┌──────────────────────────────┴───────────────────────────────┐  │
│  │              Clinical Forms Store (PostgreSQL)                 │  │
│  │  Tables: clinical_form_submission, form_definition_version,    │  │
│  │  form_score, submission_draft, audit_trail                     │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
         │                                       │
         ▼                                       ▼
┌─────────────────────┐              ┌────────────────────────┐
│  Frontend (React)   │              │  AMH Gold (Athena)      │
│  FormEngine.tsx     │              │  Patient context        │
│  Zod validation     │              │  (weight, renal, etc.)  │
│  IndexedDB queue    │              │  Read-only              │
│  Service Worker     │              │                         │
└─────────────────────┘              └────────────────────────┘
```

### 2.2 Component Responsibilities

| Component | Responsibility |
|---|---|
| **Clinical Forms API** | 3 REST endpoints: list form types, list patient submissions, submit new assessment |
| **Form Schema Registry** | In-memory index of `FormConfig` definitions by `form_type` + `definition_version`. Loaded at startup from generated Pydantic models. |
| **Scoring Engine** | Computes SOFA, Glasgow, RASS, CAM-ICU scores server-side from submitted component values. Validates clinical invariants (e.g., RASS = -5 → CAM-ICU not applicable). |
| **Form Validation Layer** | Validates submissions against the Pydantic model matching the submission's `definition_version`. Rejects schema-version mismatches, type violations, and cross-field rule failures. |
| **Frontend FormEngine** | Renders forms from TypeScript `FormConfig`. Validates with Zod. Handles conditional show/hide. Queues offline submissions. Displays server-computed scores. |
| **Form Composition** | `composeForms(baseConfig, extension)` merges `FormConfig` objects with declared conflict strategy (override/merge/append). Eliminates role-specific duplication. |

### 2.3 Data Flow — Submit Clinical Form

```
Client (React + FormEngine)
    │
    ▼
[1] Load FormConfig from TypeScript bundle (instant, zero fetch)
    │
    ▼
[2] Render form: groups → fields with renderers (StringField, SelectField, etc.)
    │
    ▼
[3] User fills fields; cross-field rules show/hide/require conditionally
    │
    ▼
[4] Client-side Zod validation (buildZodSchema + crossFieldRules)
    │
    ├── FAIL ──► Show inline errors, block submission
    │
    ▼
[5] If online: POST /api/v1/patients/{mpi_id}/clinical-forms
    If offline: queue in IndexedDB, register Background Sync
    │
    ▼
[6] Server: validate against Pydantic model matching definition_version
    │
    ├── FAIL (schema mismatch) ──► 422 with current schema; client renders updated form with preserved draft
    ├── FAIL (validation) ──► 422 with field errors
    │
    ▼
[7] Server: compute score if form has scoring metadata (SOFA, Glasgow, RASS, CAM-ICU)
    │
    ▼
[8] Persist submission + score + definition_version + audit trail
    │
    ▼
201 Created — Return submission with computed score
```

### 2.4 Data Flow — Conditional Visibility (Cross-Field Rules)

```
User changes field value (e.g., selects "ausente" for secretion type)
    │
    ▼
CrossFieldRule engine evaluates all rules where `when.field` matches changed field:
    │
    ├── when: { field: 'tipo_secrecao', op: 'eq', value: 'ausente' }
    │   then: { hide: ['exsudato', 'aspecto_secrecao'] }
    │   → Hides exudate and secretion-aspect fields
    │
    ├── when: { field: 'rass_score', op: 'eq', value: -5 }
    │   then: { hide: ['cam_icu_feature_1', 'cam_icu_feature_2', 'cam_icu_feature_3', 'cam_icu_feature_4'] }
    │   → Hides entire CAM-ICU section (RASS = -5 → unarousable → CAM-ICU not applicable)
    │
    └── when: { field: 'tipo_lpp', op: 'eq', value: 'nova_lesao' }
        then: { show: ['estagio_lpp'], require: ['estagio_lpp'] }
        → Shows LPP staging field and makes it required
```

## 3. Data Model

### 3.1 Entity-Relationship

```
form_definition_version (immutable, content-addressed)
    │
    │ 1:N
    ▼
clinical_form_submission (per patient, per form type, per assessment)
    │
    ├── 1:1 ──► form_score (computed score for scoring forms)
    │
    └── references: form_definition_version (the schema used)
```

### 3.2 Core Tables

#### `form_definition_version`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | Surrogate key |
| `form_type` | VARCHAR(32) NOT NULL | `rass`, `cam_icu`, `bps_nrs`, `glasgow`, `sofa`, `lpp`, `global_admission` |
| `definition_version` | VARCHAR(32) NOT NULL | Semantic version (e.g., `"v1.0"`, `"v2016.2"`) |
| `display_name` | VARCHAR(255) NOT NULL | PT-BR display name |
| `definition_content` | JSONB NOT NULL | Full FormConfig as JSON (canonicalized for comparison) |
| `definition_hash` | VARCHAR(128) NOT NULL | SHA-256 content hash (INV-3) |
| `pydantic_module` | VARCHAR(255) NOT NULL | Python import path for generated Pydantic model |
| `deprecated` | BOOLEAN DEFAULT false | Whether this version is superseded |
| `superseded_by` | VARCHAR(32) | Points to newer version |
| `created_at` | TIMESTAMPTZ DEFAULT NOW() | |

**Indexes:**
- `(form_type, definition_version)` — UNIQUE, lookup by type + version
- `(form_type, deprecated)` — list active versions per form type

#### `clinical_form_submission`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | Generated server-side |
| `mpi_id` | VARCHAR(64) NOT NULL | Patient identity from MPI |
| `encounter_id` | VARCHAR(64) NOT NULL | Admission identifier |
| `form_type` | VARCHAR(32) NOT NULL | `rass`, `cam_icu`, `bps_nrs`, `glasgow`, `sofa` |
| `definition_version_id` | INT FK → form_definition_version | Schema version used |
| `data` | JSONB NOT NULL | Form-specific field values |
| `score` | NUMERIC(10,4) | Computed score (nullable for non-scoring forms) |
| `score_components` | JSONB | Breakdown of score components (e.g., SOFA sub-scores) |
| `notes` | TEXT | Clinician notes |
| `created_by` | VARCHAR(128) | Submitting professional |
| `created_at` | TIMESTAMPTZ DEFAULT NOW() | |
| `submitted_offline` | BOOLEAN DEFAULT false | Whether submitted via deferred sync |
| `offline_submitted_at` | TIMESTAMPTZ | When sync occurred (if offline) |

**Indexes:**
- `(mpi_id, form_type, created_at DESC)` — patient's form history
- `(encounter_id, form_type)` — per-encounter assessments
- `(created_at)` — temporal queries

#### `form_score`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | |
| `submission_id` | UUID UNIQUE FK → clinical_form_submission | One score per submission |
| `form_type` | VARCHAR(32) NOT NULL | |
| `total_score` | NUMERIC(10,4) | Computed total (e.g., SOFA 0-24, Glasgow 3-15) |
| `components` | JSONB NOT NULL | Per-component scores (e.g., `{"respiratorio": 2, "cardiovascular": 3, ...}`) |
| `computed_at` | TIMESTAMPTZ DEFAULT NOW() | |

#### `submission_draft`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | |
| `mpi_id` | VARCHAR(64) NOT NULL | |
| `form_type` | VARCHAR(32) NOT NULL | |
| `draft_data` | JSONB NOT NULL | Partially filled field values |
| `last_saved_at` | TIMESTAMPTZ DEFAULT NOW() | |
| `client_id` | VARCHAR(128) | Device/browser identifier |
| `expires_at` | TIMESTAMPTZ | Auto-cleanup after 72h |

#### `audit_trail` (shared schema, INV-1)

Immutable append-only log for all form definition changes and submission mutations.

### 3.3 FormConfig TypeScript Schema (Extended for v2)

The existing `FormConfig` is extended per ADR-029:

```typescript
interface CrossFieldRule {
  when: {
    field: string;
    op: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'in';
    value: any;
  };
  then: {
    hide?: string[];
    show?: string[];
    require?: string[];
    optional?: string[];
    setValue?: { field: string; value: any }[];
  };
}

interface ScoringMetadata {
  type: 'sofa' | 'glasgow' | 'rass' | 'cam_icu' | 'bps' | 'nrs';
  version: string;
  components: string[];
  serverComputed: boolean;
  scoreRange?: { min: number; max: number };
}

interface FormConfig {
  id: string;
  definitionVersion: string;
  title: string;
  description?: string;
  groups: FormGroup[];
  validation?: FormValidation;
  crossFieldRules?: CrossFieldRule[];
  scoring?: ScoringMetadata;
  composition?: {
    extends?: string;      // base form id
    roles?: string[];      // applicable roles
  };
}
```

### 3.4 Scoring Models

#### SOFA Score (0-24, 6 organ systems)
| Component | Field | Range | Description |
|-----------|-------|-------|-------------|
| Respiratório | `sofa_resp_pf_ratio` | 0-4 | PaO₂/FiO₂ ratio (mmHg) |
| Coagulação | `sofa_coag_platelets` | 0-4 | Platelets (×10³/µL) |
| Hepático | `sofa_hep_bilirubin` | 0-4 | Bilirubin (mg/dL) |
| Cardiovascular | `sofa_cv_map` | 0-4 | MAP + vasopressor dose (mcg/kg/min, converted via ADR-0022) |
| SNC | `sofa_cns_glasgow` | 0-4 | Glasgow Coma Scale |
| Renal | `sofa_renal_creatinine` | 0-4 | Creatinine (mg/dL) + urine output |

_Invariant:_ Cardiovascular score validation per ADR-029 §9: MAP < 70 mmHg → minimum score 1; vasopressor → score ≥ 3 depending on dose.

#### RASS Score (-5 to +4)
Ordinal select field with labels:
`+4` Combativo, `+3` Muito agitado, `+2` Agitado, `+1` Inquieto, `0` Alerta e calmo, `-1` Sonolento, `-2` Sedação leve, `-3` Sedação moderada, `-4` Sedação profunda, `-5` Incapaz de despertar

_Invariant:_ If RASS = -4 or -5, CAM-ICU assessment is not applicable.

#### CAM-ICU (Binary: positive/negative)
4 Features: Feature 1 (alteração aguda/flutuante), Feature 2 (inatenção), Feature 3 (pensamento desorganizado), Feature 4 (nível de consciência alterado).
_Scoring rule:_ Positive = Feature 1 AND Feature 2 AND (Feature 3 OR Feature 4) all positive.

#### Glasgow Coma Scale (3-15)
| Component | Range |
|-----------|-------|
| Abertura ocular | 1-4 |
| Resposta verbal | 1-5 (special: 1 = intubado → value `NT` accepted) |
| Resposta motora | 1-6 |

### 3.5 The 49-Rule Disposition Summary

| Disposition | Count | Meaning | Examples |
|-------------|-------|---------|----------|
| ADOPT | 28 | Preserved verbatim in v2 | NPUAP staging enum (001), diuresis vocabulary (013), respiratory equipment checklist (024) |
| ADOPT-CORRECTED | 10 | Clinical content kept, implementation bugs fixed | Spelling fixes (020, 023, 026), code-drift alignment (002/003/004), required-field enforcement (018) |
| ADAPT | 2 | Same clinical intent, different mechanism | O₂ flow bound corrected (012), capillary refill threshold (005) |
| RETIRE | 4 | No clinical content | SVG icons (017, 038), gender icons (039), duplicate route (040) |
| RATIFIED | 5 | UNVERIFIABLE/AMBIGUOUS escalated | Drug vocabulary (014, 042), discipline list (037), gender representation (039) |

## 4. APIs and Contracts

### 4.1 Contract Reference

Full OpenAPI specification: `docs/contracts/formularios-clinicos-openapi.yaml`

### 4.2 Endpoints

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| `GET` | `/api/v1/clinical-forms` | `listClinicalFormTypes` | List available form types with metadata (name, description, score_range, fields) |
| `GET` | `/api/v1/patients/{mpi_id}/clinical-forms` | `listPatientClinicalForms` | List patient's submitted forms (filterable by form_type, paginated) |
| `POST` | `/api/v1/patients/{mpi_id}/clinical-forms` | `submitClinicalForm` | Submit a new clinical assessment (validates, scores, persists) |

### 4.3 Key Request/Response Structures

#### POST `/api/v1/patients/{mpi_id}/clinical-forms` — Submit Form

**Request Body:**
```json
{
  "form_type": "sofa",
  "definition_version": "sofa-v2016.2",
  "data": {
    "sofa_resp_pf_ratio": 185,
    "sofa_coag_platelets": 95,
    "sofa_hep_bilirubin": 2.1,
    "sofa_cv_map": 62,
    "sofa_cv_vasopressor_dose": 0.15,
    "sofa_cns_glasgow": 11,
    "sofa_renal_creatinine": 3.4,
    "sofa_renal_urine_output": 350
  },
  "notes": "Paciente em ventilação mecânica. Noradrenalina 0.15 mcg/kg/min."
}
```

**Response 201:**
```json
{
  "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "mpi_id": "550e8400-e29b-41d4-a716-446655440000",
  "form_type": "sofa",
  "definition_version": "sofa-v2016.2",
  "data": { "..." },
  "score": 11,
  "score_components": {
    "respiratorio": 3,
    "coagulacao": 2,
    "hepatico": 1,
    "cardiovascular": 3,
    "snc": 1,
    "renal": 1
  },
  "notes": "Paciente em ventilação mecânica...",
  "created_at": "2026-07-07T09:15:00Z",
  "created_by": "Dr. Carlos Eduardo Lima"
}
```

### 4.4 Error Responses

| HTTP Status | Code | Meaning |
|-------------|------|---------|
| 400 | `invalid_form_type` | `form_type` not in supported set |
| 400 | `version_mismatch` | `definition_version` unknown or deprecated |
| 404 | `patient_not_found` | MPI ID does not exist |
| 409 | `duplicate_submission` | Same form type submitted within minimum interval (configurable per form) |
| 422 | `validation_failed` | Field-level or cross-field validation errors |
| 422 | `clinical_invariant_failed` | Clinical invariant violated (e.g., RASS=-5 + CAM-ICU submitted) |
| 422 | `score_computation_failed` | Server could not compute score (missing component data) |

## 5. Critical Flows

### 5.1 Happy Path: Submit SOFA Assessment (Online)

```
1. Clinician opens SOFA form → FormEngine renders from TypeScript bundle
2. Cross-field rules: cardiovascular vasopressor_dose field shown because MAP < 70
3. Clinician fills all 6 organ-system sections
4. Client-side Zod validation passes
5. POST /api/v1/patients/{mpi_id}/clinical-forms with definition_version="sofa-v2016.2"
6. Server: loads Pydantic model for sofa-v2016.2
7. Server: validates all fields — passes
8. Server: computes SOFA score — total=11 (mortality ~40-50%)
9. Server: persists submission + score + audit trail
10. Returns 201 with computed score
11. Client displays score with severity badge
```

### 5.2 Edge Case: RASS = -5 Blocks CAM-ICU

```
1. Clinician submits RASS assessment: score = -5 (unarousable)
2. Clinician attempts to open CAM-ICU form
3. Cross-field rule fires: RASS = -5 → hide all CAM-ICU fields
4. Form engine shows: "CAM-ICU não aplicável — RASS = -5 (paciente incapaz de despertar)"
5. If clinician somehow bypasses client validation and submits CAM-ICU with RASS=-5:
   Server rejects with 422: "clinical_invariant_failed: CAM-ICU requires RASS ≥ -3"
```

### 5.3 Edge Case: Glasgow with Intubated Patient

```
1. Patient is intubated — verbal response cannot be assessed
2. Clinician selects "verbal = NT (não testável — paciente intubado)"
3. Glasgow total = ocular + motor (verbal excluded)
4. Score stored with verbal="NT" and total annotated: "8 (NT verbal)"
5. Client validates: "NT" is accepted as special value for verbal field only
```

### 5.4 Edge Case: Offline Submission with Schema Update

```
1. Clinician loads SOFA form offline (FormConfig v2016.2 from JS bundle)
2. While offline, FormConfig updated to v2016.3 (new field added)
3. Clinician fills form and submits → queued in IndexedDB
4. Connectivity restored → Background Sync fires
5. Server receives definition_version="sofa-v2016.2" but current is v2016.3
6. Server: v2016.2 model loaded (historical schemas preserved)
7. Server: validates against v2016.2 → passes (no breaking changes between versions)
8. If breaking change existed: server returns 422 with v2016.3 schema
   → client loads updated form, preserves draft data, shows diff to clinician
```

### 5.5 Save Draft and Resume

```
1. Clinician starts filling the 24-field Global Admission form
2. Interrupted → clicks "Salvar Rascunho"
3. Client: saves partial data to submission_draft + IndexedDB
4. Later: clinician returns, loads draft
5. Form pre-filled with saved values; continues filling
6. Submits → draft deleted after successful submission
7. Drafts auto-expire after 72h (cleanup batch job)
```

### 5.6 Form Composition: LPP Nursing vs Nutrition

```
1. Base LPP config (lpp.base.config.ts): NPUAP staging, wound assessment
2. Nursing extension (lpp.enfermagem.config.ts): adds Braden scale, repositioning schedule
3. Nutrition extension (lpp.nutricao.config.ts): adds nutritional assessment, albumin levels
4. composeForms(lppBaseConfig, enfermagemExtension) → unified nursing LPP form
5. composeForms(lppBaseConfig, nutricaoExtension) → unified nutrition LPP form
6. No duplication of base LPP fields between roles
```

### 5.7 Edge Cases Summary

| Scenario | Handling |
|----------|----------|
| Patient not found | 404 with `detail: "Paciente não encontrado"` |
| Unknown form_type | 400 with list of valid types |
| Unknown definition_version | 400 with current version; suggest reload |
| Cross-field rule: hidden required field | Field is hidden AND its required status is suppressed; validated as optional |
| Concurrent submission (same form, same patient) | Last-write-wins with audit trail; minimum interval enforced if configured |
| Score computation fails (missing components) | 422 with list of missing fields needed for score |
| Draft data from outdated schema | Client migrates draft via schema-diff on load; warns clinician if data loss |
| Large form submission (>100KB payload) | Body size limit at API gateway; streaming parse for >10KB forms |

## 6. Security Controls

### 6.1 Authentication & Authorization

- **Authentication:** JWT Bearer tokens (same as all IntensiCare services)
- **Authorization (RBAC):**
  - `clinician`: submit forms, view own submissions, save drafts
  - `supervisor`: clinician + view all unit submissions, override clinical invariants
  - `admin`: manage form definitions (via CI/CD, not runtime API)
  - `readonly`: view-only access to form types and submissions

### 6.2 Data Protection

- **Patient identity:** `mpi_id` from MPI; IntensiCare mints no patient identifiers (ADR-001)
- **LGPD compliance:** erasure cascade deletes all `clinical_form_submission`, `form_score`, `submission_draft`, and `audit_trail` rows for a given `mpi_id`
- **PHI encryption:** `data` (JSONB with clinical observations) stored with transparent field-level encryption
- **Audit immutability:** `audit_trail` rows are append-only; no UPDATE or DELETE (INV-1)
- **Encryption:** TLS 1.3 in transit; PostgreSQL TDE at rest

### 6.3 Input Validation

- All API inputs validated against OpenAPI schema at the gateway layer
- `form_type` restricted to the 7 canonical types (rass, cam_icu, bps_nrs, glasgow, sofa, lpp, global_admission)
- `data` JSONB validated against the Pydantic model for the submitted `definition_version`
- Cross-field clinical invariants enforced server-side (client validation is UX only)
- SQL injection prevented via parameterized queries (SQLAlchemy ORM)
- Body size limit enforced at API gateway (configurable, default 100KB)

## 7. Observability

### 7.1 Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `clinical_forms_submissions_total` | Counter | Total submissions (by form_type, online/offline) |
| `clinical_forms_validation_failures_total` | Counter | Validation failures (by form_type, rule category) |
| `clinical_forms_score_computation_duration_seconds` | Histogram | Scoring latency (by form_type) |
| `clinical_forms_offline_queue_depth` | Gauge | Pending offline submissions in IndexedDB |
| `clinical_forms_submission_duration_seconds` | Histogram | End-to-end submission latency |
| `clinical_forms_draft_count` | Gauge | Active drafts (by form_type) |
| `clinical_forms_definition_load_duration_seconds` | Histogram | Schema registry load time at startup |
| `clinical_forms_client_render_duration_ms` | Histogram | FCP for form rendering (client-side metric) |

### 7.2 Logs

- **Structured JSON** with required fields: `timestamp`, `level`, `service` (`clinical-forms`), `trace_id`, `mpi_id` (where applicable), `form_type`, `definition_version`, `action`, `message`
- **Levels:**
  - `INFO`: submission created, score computed, draft saved, sync completed
  - `WARNING`: offline sync with schema mismatch, clinical invariant near-boundary, deprecated version used
  - `ERROR`: validation pipeline failure, score computation error, database constraint violation

### 7.3 Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| `ClinicalFormsHighSubmissionLatency` | p95 > 500ms for 5min | warning |
| `ClinicalFormsValidationFailureSpike` | error rate > 5% for 5min | warning |
| `ClinicalFormsScoreComputationFailure` | Any score computation error | critical |
| `ClinicalFormsOfflineQueueBacklog` | >100 pending for >1h | warning |
| `ClinicalFormsDefinitionLoadFailure` | Registry fails to load at startup | critical |
| `ClinicalFormsStaleSchemaWarning` | >10% of submissions use deprecated version | warning |

## 8. Implementation Plan

### 8.1 Phases

| Phase | Deliverable | Effort | Dependencies |
|-------|-------------|--------|--------------|
| **Phase 1: Core Schema** | Database tables (form_definition_version, clinical_form_submission, form_score, submission_draft), migrations, indexes | 2d | PostgreSQL operational store |
| **Phase 2: Build Pipeline** | `generate-form-schemas` script: TypeScript FormConfig → JSON Schema + Pydantic models. Pre-commit hook + CI check. | 3d | FormConfig types finalized |
| **Phase 3: Schema Registry** | In-memory registry loading generated Pydantic models at startup. Index by form_type + definition_version. | 1d | Phase 2 |
| **Phase 4: Form Types API** | `GET /clinical-forms` — list form types with metadata from registry | 1d | Phase 3 |
| **Phase 5: Submission API** | `POST /patients/{mpi_id}/clinical-forms` — validate, score, persist. `GET /patients/{mpi_id}/clinical-forms` — list submissions. | 3d | Phase 3, Phase 4 |
| **Phase 6: Scoring Engine** | SOFA, Glasgow, RASS, CAM-ICU scoring functions. Clinical invariant validators (RASS+CAM-ICU coherence, Glasgow sub-scores, SOFA cardiovascular). | 3d | Phase 5 |
| **Phase 7: Cross-Field Rules** | DSL parser for `CrossFieldRule`. Extend `buildZodSchema()` with `.refine()`. Server-side Pydantic validators for same rules. Conditional visibility in renderers. | 3d | Phase 2 |
| **Phase 8: Form Composition** | `composeForms()` utility. Base + extensions pattern. Generated schemas for each composition. | 2d | Phase 2 |
| **Phase 9: Offline Support** | IndexedDB submission queue. Service Worker Background Sync. Draft save/load/resume. Schema-version conflict resolution. | 3d | Phase 5 |
| **Phase 10: Form Config Migration** | Author 15+ FormConfig TypeScript files for all 49 rules. Generate Pydantic models. Validation against legacy test vectors. | 4d | Phase 2, Phase 7, Phase 8 |
| **Phase 11: Observability** | Metrics, structured logging, alerts, Grafana dashboard | 1d | All phases |
| **Phase 12: LGPD Erasure** | Cascading delete by mpi_id, erasure test in CI | 1d | Phase 1 |

**Total estimated effort:** ~27 days (single developer)

### 8.2 MVP Scope Boundary

**In MVP:**
- Form type catalog (1 endpoint)
- Form submission with server-side validation and scoring (2 endpoints)
- 5 core scoring forms: RASS, CAM-ICU, BPS/NRS, Glasgow, SOFA
- Cross-field rules for conditional visibility
- `definition_version` on all submissions
- Client-side Zod validation congruent with server Pydantic
- Offline-first submission with IndexedDB queue
- Save-draft and resume
- Form composition for LPP (nursing + nutrition)
- Basic RBAC (clinician, supervisor, readonly)

**Deferred to post-MVP:**
- Global Admission form (24 fields, multi-discipline vocabularies)
- Physiotherapy, speech therapy, music therapy, psychology discipline-specific forms
- Full form config migration for all 49 rules (remaining ~25 non-scoring rules)
- Form analytics dashboard (submission rates, score trends)
- A/B testing of form versions (`experiment_id` keyed)
- WebSocket push for real-time score updates on bed-board

## 9. Alternatives Considered

### 9.1 Pure Client-Side (Option 1 from ADR-029)

Keep the existing approach: TypeScript FormConfig, Zod client-side, no server-side schema sharing. Rejected because: validation divergence risk (Zod vs Pydantic maintained manually — exactly the RULE-EVOLUCOES-003 bug class), no versioning infrastructure, composition requires fragile JS object manipulation, and cross-field rules unsupported by the current `buildZodSchema()`.

### 9.2 Pure Server-Driven (Option 2 from ADR-029)

Backend as single source of truth; client renders from JSON Schema served by API. Rejected because: network dependency breaks offline capability, latency penalty for first paint (~50-200ms fetch vs <50ms bundle), JSON Schema verbosity for PT-BR labels and UI hints, and migration cost of rewriting 15+ legacy FormConfigs on the backend.

### 9.3 Event-Sourced Form Submissions

Full event log of every field change (not just final submission). Rejected for MVP because: event volume for 24-field forms with frequent saves is disproportionate to clinical value, and the existing audit trail already captures every submission mutation. Re-evaluate if real-time collaborative editing is required.

### 9.4 Separate Form Config for Each Role (No Composition)

Each role (nursing, nutrition, physiotherapy) maintains its own complete FormConfig, even for shared forms. Rejected because: perpetuates the legacy's verbatim duplication (RULE-FORMULARIOS-CLINICOS-002), increases maintenance surface, and makes cross-discipline data aggregation fragile (different field codes for same clinical concept).

### 9.5 Client-Side Scoring for SOFA/Glasgow

Compute scores in the browser, not server-side. Rejected because: SOFA cardiovascular scoring depends on unit conversion (vasopressor mcg/kg/min — ADR-0022), which requires server-side drug concentration data. Server-side scoring ensures a single, auditable computation path and prevents client-side tampering with clinical scores.

---

## References

- `docs/adr/0029-formularios-clinicos-dynamic-form-engine.md` — ADR-029: hybrid form engine architecture decision
- `docs/adr/0015-config-driven-dynamic-clinical-form-engine.md` — ADR-0015: recommendation to modernize the engine
- `docs/adr/0022-unit-conversion-service.md` — ADR-0022: unit conversion service (SOFA cardiovascular dependency)
- `docs/adr/0028-structured-clinical-evolution-renderer.md` — ADR-028: rich-text renderer for narrative evolutions
- `docs/contracts/formularios-clinicos-openapi.yaml` — REST API OpenAPI 3.1.0 specification (3 endpoints)
- `docs/rules/extraction/phase2/catalog/formularios-clinicos.yaml` — catalog of 49 legacy rules
- `docs/plan/_work/dispositions/formularios-clinicos-p1.yaml` — Phase 1 dispositions (rules 001-023)
- `docs/plan/_work/dispositions/formularios-clinicos-p2.yaml` — Phase 2 dispositions (rules 024-045)
- `docs/rules/extraction/phase3/formularios-clinicos-batch1.yaml` — verified test vectors (rules 001-013)
- `docs/rules/extraction/phase3-verification/formularios-clinicos-batch2.yaml` — verified test vectors (rule 014)
- `frontend-v2/lib/form-engine/FormEngine.tsx` — existing FormEngine implementation
- `frontend-v2/lib/form-engine/types.ts` — existing FormConfig TypeScript types
- `src/intensicare/api/clinical_forms.py` — existing clinical forms API endpoint
- `src/intensicare/schemas/clinical_forms.py` — existing Pydantic submission schemas
- `tests/test_clinical_forms.py` — existing test suite (6 test cases)
- `docs/product/vision.md` — vision §4: clinical domains and form taxonomy

---

*This TDD is a living document. Update as design decisions evolve through ADR amendments and implementation discoveries.*
