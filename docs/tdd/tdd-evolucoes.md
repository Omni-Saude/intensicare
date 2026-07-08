# TDD: Evoluções Clínicas — Clinical Notes System

- **Status:** draft
- **Domain:** Clinical / Documentação Clínica (Clinical Notes / Evolution)
- **ADRs:** ADR-028 (evoluções architecture), ADR-0015 (form engine), ADR-0029 (form engine extension), ADR-0025 (MovimentacaoStateStore), ADR-0020 (trilhas-engine), ADR-0007 (audit trail), ADR-0008 (L0-hard — sistema nunca decide conduta), ADR-0005 (decisão clínica exclusiva do profissional)
- **Contracts:** `docs/contracts/evolucoes-openapi.yaml` (3 endpoints: list, create, detail)

## 1. Context and Scope

### 1.1 Problem

As evoluções clínicas são o principal instrumento de documentação em UTIs brasileiras — um **registro narrativo longitudinal** produzido por múltiplos profissionais (médico, enfermeiro, fisioterapeuta, nutricionista, farmacêutico, psicólogo, fonoaudiólogo, musicoterapeuta) em turnos sucessivos, descrevendo o estado do paciente, intercorrências, resposta à terapêutica e plano de cuidados.

O catálogo de regras legadas (`docs/rules/extraction/phase2/catalog/evolucoes.yaml`) contém **81 regras** — o segundo maior cluster do projeto (atrás apenas de movimentação/ADT com 74 regras). As regras cobrem:

- **14 papéis clínicos** com formulários de evolução específicos (médico, enfermagem, fisioterapia, farmácia, nutrição, psicologia, fonoaudiologia, musicoterapia, técnico de enfermagem, admissão, alta/remoção, movimentação, intercorrência, balanço hídrico).
- **Campos estruturados** coexistindo com **texto livre**: sinais vitais, scores (SOFA, Glasgow, RASS), dados de ventilação mecânica, acesso venoso, dispositivos invasivos, medicações em uso, intercorrências e o texto narrativo.
- **SOFA pré-calculado** exibido como badge (RULE-EVOLUCOES-001/002).
- **Inconsistências de tipo** entre modelos (ex.: RASS como `number` em Ocupação vs `string` em DadosProntuario — RULE-EVOLUCOES-003).
- **Padrão SBAR implícito**: seções dos formulários mapeiam para Situation-Background-Assessment-Recommendation.

O problema arquitetural central é: **qual o grau de estruturação das evoluções clínicas?** A resposta afeta três dimensões concorrentes: aceitação clínica (texto livre é preferido), capacidade analítica (dados estruturados habilitam ML), e conformidade médico-legal (trilha de auditoria, imutabilidade, não-repúdio).

### 1.2 Scope

This TDD covers the **Evoluções Clínicas domain service** — the v2 replacement for the legacy clinical notes system. It encompasses:

- Template engine for structured SBAR sections (Situation, Background) rendered via the form engine (ADR-0015/ADR-029)
- Rich-text narrative sections (Assessment, Recommendation) with Markdown free-text enrichment
- Pre-population of structured fields from `MovimentacaoStateStore` (ADR-0025) and scoring services (SOFA, Glasgow, RASS)
- Immutable note storage with revision chain (no edits, only amendments)
- Multi-disciplinary role-specific templates (14 clinical roles)
- Audit trail for every view and amendment (ADR-0007, CFM/ANVISA compliance)
- Integration with bundles/trilhas-engine (ADR-0020) for pathway adherence tracking
- LLM-assisted enrichment of narrative sections (summarization, entity extraction, bundle suggestions)

**Out of scope:**

- The LLM inference pipeline itself (covered by the AI/ML TDD)
- EWS/NRT pipeline (upstream data provider)
- Form engine core (ADR-0015/ADR-029 — reused, not reimplemented)
- Patient MPI and identity management (ADR-001)

### 1.3 Key Architectural Decisions

Per ADR-028, the Evoluções system adopts:

1. **Template híbrido SBAR (Option 2):** Structured sections (Situation + Background with typed fields, Zod validation, pre-populated) coexist with rich-text narrative sections (Assessment + Recommendation with Markdown). This balances clinician acceptance with analyzability.

2. **14 role-specific templates, versioned:** Each clinical role has a dedicated template (Jinja2-like for structured sections + Markdown for free-text). Template changes produce new `definition_version`; historical evolutions render with the template version they were created under.

3. **Immutable notes with amendment chain:** Notes are never edited in-place. Corrections are adendos — new documents referencing the original. Every version includes content hash for non-repudiation (CFM 1.638/2002, 1.821/2007).

4. **Pre-population from state store:** The Background section is pre-filled with the latest known values from `MovimentacaoStateStore` (ADR-0025), EWS/NRT pipeline, and scoring services. The clinician verifies and adjusts — not re-types. Manually corrected values are flagged in the audit trail.

5. **Deterministic rules over structured fields:** The 81 legacy rules consume typed fields from the Background section. No critical rule depends solely on LLM extraction — the deterministic path (structured fields → rules → alerts) is primary.

6. **LLM as assistant, not substitute:** Narrative sections are enriched by LLM (summarization, entity extraction, bundle suggestions, omission detection). Suggestions are displayed as side-cards the clinician can accept, ignore, or dismiss. Consistent with ADR-0008 (L0-hard).

7. **ADR-001 compliance:** All patient identity via `mpi_id` from MPI. Clinical data reads from AMH Gold via Athena only.

## 2. High-Level Design

### 2.1 Component Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    Evoluções Domain Service                           │
├──────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────────────┐  │
│  │ Evolution    │  │ Template      │  │ Pre-population          │  │
│  │ API (REST)   │  │ Engine        │  │ Manager                 │  │
│  └──────┬───────┘  └───────┬───────┘  └────────────┬─────────────┘  │
│         │                  │                        │                │
│  ┌──────┴──────────────────┴────────────────────────┴─────────────┐ │
│  │              Template Registry (compiled YAML)                   │ │
│  │  Loaded at startup; 14 role-specific SBAR templates, versioned   │ │
│  └────────────────────────────┬────────────────────────────────────┘ │
│                               │                                      │
│  ┌────────────────────────────┴────────────────────────────────────┐ │
│  │              Operational Store (PostgreSQL)                       │ │
│  │  Tables: evolucao, evolucao_template, evolucao_revision,         │ │
│  │  evolucao_section, audit_trail, template_version                 │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                               │                                      │
│  ┌────────────────────────────┴────────────────────────────────────┐ │
│  │                     Form Engine (ADR-0015/ADR-029)                │ │
│  │  Renders structured Situation + Background sections               │ │
│  │  Extended with `rich-text` field renderer for narrative sections  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌────────────────┐  ┌──────────────────┐  ┌─────────────────────┐
│  AMH Gold      │  │  Scoring         │  │  Trilhas Engine     │
│  (Athena)      │  │  Services        │  │  (ADR-020)          │
│  clinical data │  │  (SOFA, Glasgow, │  │  pathway adherence  │
│  read-only     │  │   RASS, etc.)    │  │  from bundle confirm│
└────────────────┘  └──────────────────┘  └─────────────────────┘

         ┌──────────────────────────────────────────┐
         │  MovimentacaoStateStore (ADR-0025)        │
         │  Patient state: vitals, devices, vent,    │
         │  access, medications — pre-population src │
         └──────────────────────────────────────────┘
```

### 2.2 Data Flow

1. **Startup:** The Evoluções Engine loads the compiled template registry (YAML definitions validated at CI build time, versioned, content-hashed). Templates are indexed by `role` and `definition_version`.

2. **List evolutions** (`GET /patients/{mpi_id}/evolucoes`): Queries the operational store for all evolutions for the patient, ordered by `created_at` DESC. Supports pagination (`offset`/`limit`) and filtering by `type` (admissao, diaria, alta, obito, intercorrencia).

3. **Create evolution** (`POST /patients/{mpi_id}/evolucoes`):
   - Resolves the appropriate template for the clinician's role and requested `type`.
   - Pre-populates the Background section from `MovimentacaoStateStore` (vitals, scores, devices, medications).
   - Pre-computes SOFA score from the Scoring Service and displays as badge.
   - Validates structured sections against template schema (Zod).
   - Accepts narrative sections as Markdown text.
   - Stores as an immutable evolucao row with `content_hash` (SHA-256).
   - Dispatches to Trilhas Engine for bundle adherence tracking if bundles confirmed in Recommendation section.
   - Writes `audit_trail` row (INV-1).

4. **Detail evolution** (`GET /evolucoes/{id}`): Returns the full evolution including structured sections parsed from JSONB and narrative sections as Markdown text. Renders with the template version used at creation time.

5. **Amendment flow** (no dedicated endpoint — internal logic):
   - A correction is a NEW evolution row with `amends_evolution_id` pointing to the original.
   - Both original and amendment are preserved immutably.
   - The amendment references the same `template_version` unless the template has changed.
   - Amendment chain is navigable via `amends_evolution_id` / `amended_by` (1:1 relationship).

6. **LLM enrichment** (async, post-creation):
   - After an evolution is created, an async job sends the narrative sections (Assessment + Recommendation) to the LLM pipeline.
   - Results (summarization, entity extraction, bundle suggestions, omission flags) are stored as `enrichment` JSONB on the evolution row.
   - Enrichments are non-blocking — the evolution is available immediately; enrichments appear as side-cards when ready.

## 3. Data Model

### 3.1 Entity-Relationship

```
evolucao_template (immutable, versioned per clinical role)
    │
    │ 1:N (template used by many evolutions)
    ▼
evolucao (immutable clinical note)
    │
    ├── 1:1 ──► evolucao (amends / amended by — revision chain)
    │
    ├── 1:N ──► evolucao_section (structured content per SBAR section)
    │
    └── 1:N ──► audit_trail (views, amendments, creations)
```

### 3.2 Core Tables

#### `evolucao_template`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | Surrogate key |
| `role` | VARCHAR(32) NOT NULL | Clinical role (medico, enfermagem, fisioterapeuta, etc.) |
| `type` | VARCHAR(32) NOT NULL | Evolution type (admissao, diaria, alta, obito, intercorrencia) |
| `definition_version` | VARCHAR(32) NOT NULL | Semantic version of this template (e.g., "1.0.0") |
| `definition_hash` | VARCHAR(128) NOT NULL | SHA-256 content hash for non-repudiation (INV-3) |
| `name` | VARCHAR(255) NOT NULL | PT-BR display name (DM-C-01) |
| `sections` | JSONB NOT NULL | SBAR section definitions with field schemas |
| `active` | BOOLEAN DEFAULT true | Whether this template version is active for new evolutions |
| `created_at` | TIMESTAMPTZ DEFAULT NOW() | |
| `superseded_by` | INT FK → evolucao_template | Pointer to next version (NULL if current) |

**Constraints:**
- UNIQUE `(role, type, definition_version)`
- At most one active template per `(role, type)` pair

**Indexes:**
- `(role, type, active)` — resolve template for new evolutions
- `(definition_hash)` — lookup by content address

#### `evolucao`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | Evolution identifier |
| `mpi_id` | VARCHAR(64) NOT NULL | Patient identity from MPI (ADR-001) |
| `encounter_id` | VARCHAR(64) NOT NULL | Admission identifier from AMH Gold |
| `template_id` | INT FK → evolucao_template | Template version used |
| `type` | VARCHAR(32) NOT NULL | Evolution type (admissao, diaria, alta, obito, intercorrencia) |
| `role` | VARCHAR(32) NOT NULL | Clinical role of the author |
| `content` | TEXT NOT NULL | Narrative text (Markdown) for Assessment + Recommendation sections (max 50,000 chars) |
| `structured_data` | JSONB NOT NULL | Typed field values for Situation + Background sections |
| `content_hash` | VARCHAR(128) NOT NULL | SHA-256(content || structured_data::text) for non-repudiation |
| `sofa_score` | INT | Pre-computed SOFA score at time of creation (NULL if not applicable) |
| `sofa_badge_displayed` | BOOLEAN DEFAULT false | Whether SOFA badge was shown (RULE-EVOLUCOES-002) |
| `bundles_confirmed` | JSONB | Array of bundle slugs confirmed in Recommendation section |
| `enrichment` | JSONB | LLM enrichment results (summarization, entities, suggestions, omissions) |
| `amends_evolution_id` | UUID FK → evolucao | If this is an amendment, points to the original (NULL for originals) |
| `status` | ENUM('draft','liberado','assinado') DEFAULT 'liberado' | Document workflow status (RULE-EVOLUCOES-076) |
| `created_by` | VARCHAR(128) NOT NULL | Professional who authored the evolution |
| `created_by_role` | VARCHAR(32) NOT NULL | Clinical role at time of creation |
| `created_at` | TIMESTAMPTZ DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | Last update (only for enrichment/enrichment; content is immutable) |

**Constraints:**
- UNIQUE `(id)` — UUID primary key
- FK `amends_evolution_id` → `evolucao(id)` — self-referential revision chain
- FK `template_id` → `evolucao_template(id)` — template immutability enforced

**Indexes:**
- `(mpi_id, created_at DESC)` — list evolutions for a patient
- `(mpi_id, type, created_at DESC)` — filtered listing by type
- `(encounter_id)` — evolutions within an admission
- `(created_by, created_at DESC)` — professional's evolutions
- `(amends_evolution_id)` — revision chain navigation

#### `evolucao_section` (optional denormalization for query performance)

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | |
| `evolucao_id` | UUID FK → evolucao | Parent evolution |
| `section_key` | VARCHAR(32) NOT NULL | SBAR section: 'situation', 'background', 'assessment', 'recommendation' |
| `field_values` | JSONB | Per-field values extracted from structured_data or content |
| `created_at` | TIMESTAMPTZ DEFAULT NOW() | |

#### `audit_trail` (shared schema — INV-1)

Every evolution lifecycle event writes an immutable audit row:

| Field | Value for evolutions |
|-------|---------------------|
| `entity_type` | `'evolucao'` |
| `entity_id` | `evolucao.id` |
| `action` | `'created'`, `'viewed'`, `'amended'`, `'liberado'`, `'assinado'`, `'enriched'` |
| `actor` | User ID or system |
| `details` | JSONB with relevant context (view timestamp, amendment reason, enrichment version) |
| `timestamp` | Event time |

### 3.3 Template Definition YAML Schema

```yaml
# docs/plan/_work/templates/evolucoes/<role>-<type>.yaml
role: medico
type: diaria
name: "Evolução Médica Diária"
definition_version: "1.0.0"
active: true
description: "Template de evolução médica diária para pacientes de UTI"

sections:
  situation:
    label: "Situação"
    description: "Identificação do paciente e contexto do atendimento"
    order: 0
    fields:
      - key: paciente_nome
        type: string
        label: "Paciente"
        required: true
        pre_populate: true
        source: mpi.patient_name
        editable: false
      - key: data_hora
        type: datetime
        label: "Data/Hora"
        required: true
        pre_populate: true
        source: system.current_time
        editable: true
      - key: tipo_evolucao
        type: select
        label: "Tipo de Evolução"
        required: true
        options: ["Rotina", "Admissão", "Intercorrência", "Alta", "Óbito"]

  background:
    label: "Background"
    description: "Dados clínicos objetivos — sinais vitais, scores, dispositivos"
    order: 1
    fields:
      - key: sinais_vitais
        type: group
        label: "Sinais Vitais"
        pre_populate: true
        source: ews_nrt.latest_vitals
        fields:
          - key: pas
            type: number
            label: "PA Sistólica (mmHg)"
            required: true
            unit: mmHg
            pre_source: ews_nrt.pas
          - key: pad
            type: number
            label: "PA Diastólica (mmHg)"
            unit: mmHg
            pre_source: ews_nrt.pad
          - key: fc
            type: number
            label: "Frequência Cardíaca (bpm)"
            unit: bpm
            pre_source: ews_nrt.fc
          - key: fr
            type: number
            label: "Frequência Respiratória (irpm)"
            unit: irpm
            pre_source: ews_nrt.fr
          - key: spo2
            type: number
            label: "SpO₂ (%)"
            unit: "%"
            pre_source: ews_nrt.spo2
          - key: temperatura
            type: number
            label: "Temperatura (°C)"
            unit: "°C"
            pre_source: ews_nrt.temp

      - key: scores
        type: group
        label: "Scores Clínicos"
        fields:
          - key: sofa
            type: number
            label: "SOFA"
            range: [0, 24]
            pre_populate: true
            source: scoring.sofa
            display: badge
            badge_rule: ">= 0 → mostrar badge 'Escore SOFA: {value}'"
            rule_ref: RULE-EVOLUCOES-001, RULE-EVOLUCOES-002
          - key: glasgow
            type: number
            label: "Glasgow"
            range: [3, 15]
            pre_populate: true
            source: scoring.glasgow
          - key: rass
            type: number
            label: "RASS"
            range: [-5, 4]
            note: "Normalizado para number; legado tinha type mismatch string/number"
            rule_ref: RULE-EVOLUCOES-003

      - key: dispositivos
        type: group
        label: "Dispositivos Invasivos e Suporte"
        fields:
          - key: ventilacao_mecanica
            type: boolean
            label: "Ventilação Mecânica"
            pre_populate: true
            source: state_store.vent_mode
          - key: acesso_venoso_central
            type: boolean
            label: "Acesso Venoso Central"
            pre_populate: true
            source: state_store.cvc
          # ... additional devices

  assessment:
    label: "Avaliação"
    description: "Evolução narrativa e impressão clínica — texto livre rico"
    order: 2
    renderer: rich-text
    field:
      key: assessment_text
      type: string
      format: markdown
      max_length: 25000
      required: true
      enrichment:
        summarization: true
        entity_extraction: true
        omission_detection: true

  recommendation:
    label: "Recomendação / Plano"
    description: "Plano terapêutico, conduta e bundles — texto livre com hints estruturados"
    order: 3
    renderer: rich-text-with-hints
    field:
      key: recommendation_text
      type: string
      format: markdown
      max_length: 25000
      required: true
    hints:
      - type: bundle_suggestion
        source: trilhas_engine.active_pathways
        display: checklist
        track_adherence: true
      - type: clinical_alerts
        source: alert_engine.active_alerts
        display: warning_cards
```

### 3.4 The 14 Clinical Role Vocabulary

From the legacy rules catalog and ADR-028:

| Role Slug | PT-BR Label | Template Types |
|-----------|-------------|----------------|
| `medico` | Médico | admissao, diaria, alta, obito, intercorrencia |
| `enfermagem` | Enfermagem | admissao, diaria, alta, obito, intercorrencia |
| `fisioterapeuta` | Fisioterapeuta | diaria, alta, intercorrencia |
| `farmacia` | Farmácia | diaria, intercorrencia |
| `nutricao` | Nutrição | diaria, intercorrencia |
| `psicologia` | Psicologia | diaria |
| `fonoaudiologia` | Fonoaudiologia | diaria |
| `musicoterapia` | Musicoterapia | diaria |
| `tec_enfermagem` | Técnico de Enfermagem | diaria |
| `admissao` | Admissão | admissao |
| `alta_remocao` | Alta/Remoção | alta |
| `movimentacao` | Movimentação | diaria |
| `intercorrencia` | Intercorrência | intercorrencia |
| `balanco_hidrico` | Balanço Hídrico | diaria |

### 3.5 Rule Categories and Distribution (81 Rules)

| Category | Count | Key Rules |
|----------|-------|-----------|
| `clinical-scoring` | 4 | RULE-EVOLUCOES-001 (SOFA pre-computed), RULE-EVOLUCOES-002 (SOFA badge threshold), RULE-EVOLUCOES-003 (RASS type mismatch), RULE-EVOLUCOES-004 (Glasgow validation) |
| `data-validation` | ~35 | Field-level validation: required fields, type constraints, cross-field consistency, RASS normalization |
| `care-pathway` | ~38 | Bundle adherence, pathway triggers, alert thresholds (SOFA ≥ 2 + infection → sepsis alert; VM > 21d → tracheostomy alert) |
| `billing-administrative` | 2 | Administrative workflow rules |
| `triage-eligibility` | 1 | Admission triage criteria |
| **Total** | **81** | |

**Status distribution:**
- **OK:** ~65 rules — sound clinical intent, reimplement on new substrate
- **AMBIGUOUS:** ~8 rules — need clinical sign-off before reimplementation
- **DISCREPANCY:** ~5 rules — type mismatch or logic errors to be corrected (e.g., RULE-EVOLUCOES-003 RASS type)

## 4. APIs and Contracts

### 4.1 Contract Reference

Full OpenAPI specification: `docs/contracts/evolucoes-openapi.yaml`

### 4.2 Endpoints

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| `GET` | `/api/v1/patients/{mpi_id}/evolucoes` | `listEvolucoes` | List patient's clinical evolutions, ordered by creation date DESC. Supports pagination and type filter. |
| `POST` | `/api/v1/patients/{mpi_id}/evolucoes` | `createEvolucao` | Create a new clinical evolution for the patient. |
| `GET` | `/api/v1/evolucoes/{id}` | `getEvolucao` | Get full detail of a specific evolution, including structured and narrative content. |

### 4.3 Key Request/Response Structures

**Evolucao (response):**
- `id` (UUID) — unique identifier
- `mpi_id` (UUID) — patient identity
- `type` (enum: admissao, diaria, alta, obito, intercorrencia)
- `content` (string, max 50000) — narrative text in Markdown
- `structured_data` (object) — typed field values from structured sections (extended beyond base contract)
- `sofa_score` (int, nullable) — pre-computed SOFA at creation time
- `bundles_confirmed` (array) — bundle slugs confirmed in Recommendation
- `enrichment` (object, nullable) — LLM enrichment results
- `amends_evolution_id` (UUID, nullable) — revision chain pointer
- `status` (enum: draft, liberado, assinado)
- `template_version` (string) — definition_version used
- `content_hash` (string) — SHA-256 for non-repudiation
- `created_at` (datetime) — immutable creation timestamp
- `created_by` (string) — authoring professional
- `updated_at` (datetime, nullable) — enrichment updates only

**EvolucaoCreate (request):**
- `type` (enum: admissao, diaria, alta, obito, intercorrencia) — required
- `content` (string, max 50000) — narrative text in Markdown
- `structured_data` (object) — typed structured fields (pre-populated defaults can be overridden)
- `bundles_confirmed` (array, optional) — bundle adherence confirmation
- `status` (enum: draft, liberado) — workflow status

### 4.4 Error Responses

- **400:** `{"detail": "Dados inválidos"}` — validation errors (missing required fields, type mismatch, maxLength)
- **404:** `{"detail": "Paciente com MPI ID informado não foi encontrado."}` — patient not found
- **404:** `{"detail": "Evolução não encontrada."}` — evolution not found
- **409:** `{"detail": "Template não encontrado para role={role}, type={type}"}` — no active template for role/type
- **422:** `{"detail": "Campos estruturados não conformes ao schema do template"}` — structured_data fails Zod validation against template

## 5. Critical Flows

### 5.1 Happy Path: Create Daily Medical Evolution

```
1. Clinician navigates to patient → system loads latest evolutions (GET /patients/{mpi_id}/evolucoes)
2. Clinician clicks "Nova Evolução" → system resolves template for (role=medico, type=diaria)
3. System pre-populates Background:
   - Vitals from EWS/NRT pipeline (latest within configurable window)
   - Scores from Scoring Service (SOFA, Glasgow, RASS)
   - Devices/medications from MovimentacaoStateStore (ADR-0025)
   - SOFA computed → badge displayed if SOFA >= 0 (RULE-EVOLUCOES-002)
4. Clinician reviews pre-populated fields, corrects any values
   - Manually corrected fields flagged in audit trail as "manual_override"
5. Clinician writes narrative Assessment in rich-text editor (Markdown)
6. System suggests bundles based on structured data + active pathways
   - E.g., "VM > 21d → sugerir avaliação para traqueostomia"
7. Clinician confirms bundles in Recommendation section
8. Clinician clicks "Salvar e Liberar" (status=liberado) or "Salvar" (status=draft)
9. System validates structured_data against template Zod schema
10. System computes content_hash = SHA-256(content || structured_data::text)
11. System persists evolucao row (immutable) + audit_trail row
12. System dispatches async LLM enrichment job
13. System notifies Trilhas Engine of confirmed bundles for pathway adherence tracking
14. Response returns 201 with the created evolution
```

### 5.2 Amendment Flow (Correction as Adendo)

```
1. Clinician views an existing evolution → GET /evolucoes/{id}
   - View logged to audit_trail (action='viewed')
2. Clinician clicks "Corrigir" (Amend)
3. System creates a new evolution draft, pre-filled with original content
   - amends_evolution_id = original.id
   - template_id = original.template_id (same template version)
4. Clinician modifies content/structured_data
5. Clinician saves → new evolucao row created
   - Original remains immutable (no UPDATE)
   - New row has amends_evolution_id pointing to original
   - Audit trail records 'amended' action on original + 'created' on amendment
6. When viewing the evolution, the system shows the latest amendment with a link/banner to view the revision chain
```

### 5.3 Pre-Population with Degraded Mode

```
1. Evolution creation requested
2. System attempts pre-population:
   - Calls MovimentacaoStateStore.get_patient_state(mpi_id, encounter_id)
   - Calls ScoringService.get_latest_scores(mpi_id)
   - Calls EWSNRTService.get_latest_vitals(mpi_id)
3. If all services respond within timeout (configurable, default 2s):
   - Fields are pre-populated with latest values
   - Source of each value recorded in structured_data metadata
4. If any service fails or times out:
   - Affected fields appear empty with "Indisponível — preencher manualmente" placeholder
   - System logs WARNING with degraded_fields list
   - Clinician manually enters values
   - Metric: evolucoes_prepopulation_degraded_total incremented
5. The evolution creation is NEVER blocked by pre-population failures
```

### 5.4 LLM Enrichment (Async, Non-Blocking)

```
1. Evolution created successfully → 201 response returned immediately
2. Async job dispatched to LLM enrichment queue:
   - Input: assessment_text + recommendation_text + structured_data summary
   - Tasks: summarization, entity extraction, bundle suggestions, omission detection
3. LLM results stored as evolucao.enrichment JSONB:
   {
     "summary": "Paciente estável, em desmame ventilatório...",
     "entities": [...],
     "suggested_bundles": ["bundle-pav", "bundle-sedacao"],
     "omissions": ["VM > 14d sem menção a traqueostomia"],
     "enrichment_version": "1.0.0",
     "enriched_at": "2026-07-07T14:31:00Z"
   }
4. Frontend polls or receives WebSocket notification when enrichment is ready
5. Enrichments displayed as side-cards — clinician can accept (confirms bundle), ignore, or dismiss
6. Accepted suggestions trigger:
   - Bundle confirmed → Trilhas Engine notified
   - Entity extracted → added to structured_data (future version may promote to structured fields)
```

### 5.5 Edge Cases

| Scenario | Handling |
|----------|----------|
| No active template for role/type | 409 with detail listing available templates |
| structured_data fails Zod validation | 422 with field-level error array, clinician can fix and resubmit |
| content exceeds maxLength (50,000) | 400 — content too long |
| Patient not found in MPI | 404 — patient not found |
| Missing encounter_id (patient not admitted) | 400 — "Paciente sem atendimento ativo" |
| Amendment chain exceeds max depth (configurable, default 5) | 400 — "Número máximo de adendos excedido; considere nova evolução" |
| Concurrent amendment of same evolution | Optimistic locking on content_hash; 409 Conflict if hash changed since read |
| Template version retired after evolution created | Evolution stored with retired template_id; rendering uses historical template definition |
| LLM enrichment fails or times out | enrichment remains NULL; evolution fully functional without enrichment; retry policy (exponential backoff, max 3 attempts) |
| SOFA computation service unavailable | sofa_score set to NULL; badge hidden; no blocking |
| Pre-populated value is stale (> N hours) | Value displayed with "⚠️ Atualizado há Xh" warning; clinician can refresh or override |

## 6. Security Controls

### 6.1 Authentication & Authorization

- **Authentication:** JWT Bearer tokens via existing IntensiCare auth endpoint
- **Authorization:** Role-based access control (RBAC):
  - `clinician` (all roles): create, view evolutions for patients in their unit
  - `supervisor`: all clinician permissions + view audit trail, view amendments across unit
  - `admin`: manage template versions (via CI/CD, not runtime API)
  - `readonly`: view-only access to evolutions
  - `auditor`: view evolutions + full audit trail (CFM compliance)

### 6.2 Data Protection

- **Patient identity:** `mpi_id` from MPI; IntensiCare mints no patient identifiers (ADR-001)
- **Content immutability:** `evolucao` rows are INSERT-only; no UPDATE to content, structured_data, or content_hash after creation (enforced at application layer)
- **Non-repudiation:** Every evolution carries `content_hash` (SHA-256) and `created_by`; content hash verifiable at any time
- **LGPD compliance:** Erasure cascade deletes all `evolucao`, `evolucao_section`, and `audit_trail` rows for a given `mpi_id`
- **Audit immutability:** `audit_trail` rows are append-only; no UPDATE or DELETE permitted (INV-1)
- **Encryption:** Data at rest via PostgreSQL TDE; data in transit via TLS 1.3
- **PHI access logging:** Every view of an evolution (GET detail) writes an audit_trail row with `action='viewed'`

### 6.3 Input Validation

- All API inputs validated against OpenAPI schema at the gateway layer
- `type` must be a valid enum value
- `content` max 50,000 characters; Markdown injection sanitized (no raw HTML, no script tags)
- `structured_data` validated against the resolved template's Zod schema at the application layer
- `bundles_confirmed` slugs validated against `trilhas-engine` pathway registry
- SQL injection prevented via parameterized queries (SQLAlchemy ORM)

### 6.4 Medical-Legal Compliance (CFM/ANVISA)

| Requirement | Implementation |
|-------------|----------------|
| Immutability (CFM 1.638/2002) | INSERT-only; no UPDATE on content/structured_data |
| Attribution (CFM 1.821/2007) | `created_by` + `created_by_role` + JWT principal |
| Timestamp precision | `created_at` with timezone, server-authoritative |
| Audit trail | Every create/view/amend logged to immutable audit_trail |
| Non-repudiation | SHA-256 content_hash verifiable at any time |
| Amendment as adendo | Corrections are new rows with amends_evolution_id; original preserved |
| Template traceability | `template_id` + `definition_version` recorded per evolution |

## 7. Observability

### 7.1 Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `evolucoes_created_total` | Counter | Total evolutions created (by role, type) |
| `evolucoes_viewed_total` | Counter | Total evolution views (by role) |
| `evolucoes_amended_total` | Counter | Total amendments created |
| `evolucoes_prepopulation_degraded_total` | Counter | Pre-population degradations (by service) |
| `evolucoes_prepopulation_latency_seconds` | Histogram | Pre-population service call latency |
| `evolucoes_validation_errors_total` | Counter | Zod validation failures (by field) |
| `evolucoes_enrichment_latency_seconds` | Histogram | LLM enrichment job latency |
| `evolucoes_enrichment_failures_total` | Counter | LLM enrichment failures |
| `evolucoes_bundle_confirmations_total` | Counter | Bundle confirmations via evolution (by bundle slug) |
| `evolucoes_template_resolution_cache_hits` | Counter | Template cache hit rate |

### 7.2 Logs

- **Structured JSON** with required fields: `timestamp`, `level`, `service` (`evolucoes-engine`), `trace_id`, `mpi_id` (where applicable), `evolution_id`, `action`, `message`
- **Levels:**
  - `INFO`: evolution created, viewed, amended; enrichment completed; bundle confirmed
  - `WARNING`: degraded pre-population, stale pre-populated values, enrichment retry
  - `ERROR`: template not found, validation failure, enrichment exhausted retries, database constraint violations

### 7.3 Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| `EvolucoesHighCreationLatency` | p95 > 1000ms for 5min | warning |
| `EvolucoesPrepopulationDegraded` | degraded rate > 10% for 5min | warning |
| `EvolucoesValidationErrorSpike` | error rate > 5% for 5min | warning |
| `EvolucoesTemplateResolutionFailure` | Any template resolution error | critical |
| `EvolucoesEnrichmentQueueBacklog` | Queue depth > 100 for 10min | warning |
| `EvolucoesEnrichmentFailureRate` | Failure rate > 20% for 10min | critical |

## 8. Implementation Plan

### 8.1 Phases

| Phase | Deliverable | Effort | Dependencies |
|-------|-------------|--------|--------------|
| **Phase 1: Core Schema** | Database tables (`evolucao_template`, `evolucao`, `evolucao_section`), migrations, indexes, constraints | 2d | PostgreSQL operational store |
| **Phase 2: Template Compiler** | CI build step: validate YAML against template schema, canonicalize, compute content hash, emit compiled registry JSON | 2d | Template YAML schema defined |
| **Phase 3: Template Registry** | In-memory template registry loaded at startup, indexed by (role, type, active), template resolution API | 1d | Phase 1, Phase 2 |
| **Phase 4: Evolution API — List** | `GET /patients/{mpi_id}/evolucoes` with pagination and type filter | 1d | Phase 1 |
| **Phase 5: Evolution API — Create** | `POST /patients/{mpi_id}/evolucoes` with template resolution, pre-population, Zod validation, content hash, audit trail | 3d | Phase 1, Phase 3, MovimentacaoStateStore, Scoring Service |
| **Phase 6: Evolution API — Detail** | `GET /evolucoes/{id}` with full content, structured_data, enrichment, revision chain | 1d | Phase 1 |
| **Phase 7: Amendment Flow** | Self-referential amendment chain, optimistic locking, revision navigation, max-depth enforcement | 2d | Phase 5, Phase 6 |
| **Phase 8: Pre-Population Pipeline** | Integration with MovimentacaoStateStore (ADR-0025), EWS/NRT, Scoring Service; degraded mode; staleness detection | 3d | Phase 5, MovimentacaoStateStore, EWS/NRT, Scoring Service |
| **Phase 9: LLM Enrichment** | Async enrichment queue, retry policy, enrichment storage, frontend side-card integration | 3d | Phase 5, LLM pipeline |
| **Phase 10: Bundle Integration** | Bundle confirmation tracking, notification to Trilhas Engine (ADR-0020) | 2d | Phase 5, Trilhas Engine |
| **Phase 11: Rule Implementation** | Reimplement 81 legacy rules: ~65 OK rules rewritten, ~8 AMBIGUOUS rules with clinical sign-off, ~5 DISCREPANCY rules corrected (e.g., RASS type normalization) | 5d | Phase 5, Phase 8 |
| **Phase 12: Observability** | Metrics, structured logging, alerts, Grafana dashboard | 1d | All phases |
| **Phase 13: LGPD Erasure** | Cascading delete by `mpi_id`, erasure test in CI | 1d | Phase 1 |
| **Phase 14: Rich-Text Renderer** | Extend form engine (ADR-0015/ADR-029) with `rich-text` field renderer for Assessment + Recommendation sections | 2d | Form Engine |

**Total estimated effort:** ~29 days (single developer)

### 8.2 MVP Scope Boundary

**In MVP:**
- Evolution API (3 endpoints: list, create, detail)
- Template resolution for 14 clinical roles
- Pre-population from MovimentacaoStateStore, EWS/NRT, Scoring Service (with degraded mode)
- SOFA pre-computation and badge display (RULE-EVOLUCOES-001/002)
- RASS type normalization (number — RULE-EVOLUCOES-003 correction)
- Immutable notes with content hash (non-repudiation)
- Amendment chain (adendos, not in-place edits)
- Audit trail for every create/view/amend (INV-1)
- Template versioning with `definition_version` traceability (INV-3)
- Basic RBAC (clinician, supervisor, readonly, auditor)
- LGPD erasure cascade

**Deferred to post-MVP:**
- Full LLM enrichment pipeline (summarization, entity extraction, omission detection)
- Bundle adherence tracking via Trilhas Engine integration
- Voice-to-text input for narrative sections
- Template version migration of historical evolutions (render with original template)
- Cross-evolution trend analysis (SOFA trajectory, vitals trends across evolutions)
- Multi-professional collaborative editing (concurrent drafts)
- A/B testing of template versions

## 9. Alternatives Considered

### 9.1 Texto Livre Puro (Option 1 from ADR-028)

Narrative-only evolution with a single rich-text field, no structured sections. Rejected because: NLP/LLM becomes a critical dependency for all analytical functionality (search, aggregation, alert triggering); the 81 legacy rules cannot be applied deterministically; medico-legal completeness requirements may not be satisfied; and real-time validation during data entry is impossible.

### 9.2 Totalmente Estruturado (Option 3 from ADR-028)

Every clinical observation coded as a SNOMED/LOINC pair. Rejected because: near-certain clinician rejection ("checklist medicine"); nuanced diagnostic reasoning is not reducible to codes; vocabulary maintenance is ongoing and specialized; and the legacy's 14 mixed-format forms would require complete rewriting with prohibitive transition cost.

### 9.3 Form Engine for Everything

Using the form engine (ADR-0015) for ALL sections including narrative. Rejected because: the form engine is optimized for typed fields with validation; forcing narrative text into structured form fields would degrade the writing experience. Instead, the form engine is extended with a `rich-text` renderer for narrative sections only.

### 9.4 Mutable Notes with Edit History (SCD Type 2)

Allowing in-place edits with a history table tracking changes. Rejected because: CFM 1.638/2002 and 1.821/2007 require the original record to remain intact as a legal document. Amendment chain (adendos) preserves both the original and the correction as separate immutable documents, satisfying medico-legal requirements.

### 9.5 Single Template for All Roles

One universal evolution template instead of 14 role-specific templates. Rejected because: each clinical role documents different aspects of care (physiotherapist focuses on respiratory mechanics; nutritionist on caloric intake and GI tolerance; pharmacist on drug levels and interactions). A single template would either be overwhelmingly large or omit role-critical fields, driving clinicians to use free-text workarounds.

---

## References

- `docs/adr/0028-evolucoes-clinical-notes-architecture.md` — ADR-028: SBAR hybrid template architecture (Option 2)
- `docs/adr/0015-form-engine.md` — ADR-0015: Dynamic form engine for structured fields
- `docs/adr/0029-form-engine-extension.md` — ADR-0029: Form engine rich-text extension
- `docs/adr/0025-movimentacao-state-store.md` — ADR-0025: Patient state store for pre-population
- `docs/adr/0020-trilhas-engine-architecture.md` — ADR-0020: Pathway engine for bundle adherence
- `docs/adr/0007-audit-trail.md` — ADR-0007: Immutable audit trail
- `docs/adr/0008-l0-hard.md` — ADR-0008: L0-hard constraint (system never decides conduct)
- `docs/adr/0005-clinical-decision.md` — ADR-0005: Clinical decision is exclusive to the professional
- `docs/contracts/evolucoes-openapi.yaml` — REST API OpenAPI 3.1.0 specification (3 endpoints)
- `docs/rules/extraction/phase2/catalog/evolucoes.yaml` — 81 legacy rules with categories and dispositions
- CFM Resolução 1.638/2002 — Prontuário médico: obrigatoriedade e conteúdo mínimo
- CFM Resolução 1.821/2007 — Prontuário eletrônico: requisitos de segurança e autenticação
- The Joint Commission (2017) — SBAR communication standard for safe clinical handoff
