# Data Model Architecture — IntensiCare v2 (Phase 2)

**Owner:** data-architect · **Status:** draft for reconciliation barrier **B** · **Authority precedence:** ADR-001 ≻ vision ≻ directive ≻ audit (CONTRACTS §5).
**Evolves:** `docs/data/model.md` (brief `data-model.json`). **Resolves:** `CON-SEED-02` (clinical_score naming + `algorithm_version`), `CON-SEED-03` (precise per-entity retention). **Realizes invariants:** **INV-1** immutable audit trail (`CON-0066`/`IMP-C-01`), **INV-3** algorithm versioning (`CON-0068`/`IMP-C-03`), **INV-4** encryption-at-rest for PHI (`CON-0069`/`IMP-C-04`).

This document extends the Phase-1 operational schema into the Phase-2 clinical surface (7 domain detectors + correlation engine, `VIS-4-02`/`VIS-4-03`) and pins the three data-layer invariants that MUST exist before the first real patient (`IMP-C-01/03/04`). Every number/name cites a source: a brief fact (`DM-*`, `VIS-*`, `ADR001-*`, `IMP-*`), a ledger constraint (`CON-*`), or an invariant (`INV-1..6`). Clinical cutoffs are **not** invented here — they live in the alert catalog and units registry; this doc is the *persistence contract*.

> **Platform reality (ADR-001).** PostgreSQL/TimescaleDB is **operational-only** — computed scores, active alerts, threshold configs, and short-lived hot caches — **never an analytical store** (`ADR001-C-03`/`CON-0003`). IntensiCare implements **no ingestion of its own** and reads clinical source data **only from the AMH Gold layer via Amazon Athena** (`ADR001-C-01`/`CON-0001`). Patient identity is the MPI `mpi_id`; IntensiCare mints **no** patient identifiers (`ADR001-C-02`/`CON-0002`). Historical scores/alerts are written back to Gold `fact_patient_score` / `fact_alert` (`ADR001-C-04`/`CON-0004`, `DM-AMH-03/04`). Encryption inherits per-tenant **KMS** and Lake Formation ABAC from the platform (`ADR001-C-07`/`CON-0007`); `pgcrypto` (INV-4) protects PHI **at the row level inside** the operational DB, layered on top of KMS volume encryption. PostgreSQL major version is pinned to **16** by implementation-plan §3.2 (`CON-SEED-04`).

---

## 1. Entity map (evolved conceptual ER)

Phase-1 entities are unchanged in shape; Phase-2 adds the medication, lab, alert-definition, correlation, audit, and algorithm-registry surfaces.

```
                         ┌───────────────────────────── AMH Data Platform (source of truth) ─────────────────────────────┐
                         │  MPI (mpi.patients)      Gold layer / Iceberg      HAPI FHIR      fact_patient_score/fact_alert │
                         └───────┬───────────────────────┬──────────────────────┬────────────────────────▲────────────────┘
                    read (sync)  │        read (Athena)   │      read (Athena)    │        write-back (batch)│
        ┌───────────────┐        ▼                        ▼                      ▼                          │
        │ patient_cache │◄── mpi_id ──┐         ┌──────────────┐        ┌──────────────┐                    │
        │  (PHI, INV-4) │             ├── 1:N ─►│  vital_sign  │        │  lab_result  │ (cache)            │
        └───────┬───────┘             │         │ (hypertable) │        │ (hypertable) │                    │
                │ 1:N                 │         └──────┬───────┘        └──────┬───────┘                    │
                │                     │                │ originates            │ feeds                       │
   ┌────────────┼─────────────┐       │                ▼                       ▼                             │
   │            │             │       │        ┌──────────────┐   evaluates   ┌───────────────────┐          │
   ▼            ▼             ▼       │        │clinical_score│◄──────────────│ alert_definition  │          │
┌──────────┐┌──────────────┐┌──────┐ │        │ (hypertable, │   uses ver.   │  + _version (INV-3)│          │
│medication ││medication_   ││ ...  │ │        │  INV-3)      │               └─────────┬─────────┘          │
│_order     ││administration│└──────┘ │        └──────┬───────┘                         │ raises             │
└──────────┘└──────────────┘          │               │ triggers                        ▼                    │
                                      │               ▼                        ┌──────────────┐  correlates  │
   ┌──────────────────┐   config      │        ┌──────────────┐                │    alert     │─────► fact_* ─┘
   │ threshold_config │───────────────┘        │correlation_  │◄───────────────│ (hypertable, │
   │  (versioned)     │                        │   event      │   links 2+     │  INV-3)      │
   └──────────────────┘                        │ (hypertable) │                └──────┬───────┘
                                               └──────────────┘                       │ every mutation
   ┌───────────────────────────────────────────────────────────────────────────────► ▼
   │  algorithm_registry (immutable)                                          ┌──────────────┐
   └──────────────────────────────────────────────────────────────────────── │ audit_trail  │ append-only + anti-mutation trigger (INV-1)
                                                                              │ (hypertable) │
                                                                              └──────────────┘
```

**Entity-name ↔ table-name mapping (preserved per `DM-C-12`).** Conceptual ER names remain `Patient / VitalSign / Score / Alert`; DDL table names are `patient_cache / vital_sign / clinical_score / alert` (singular). See §2 for the CON-SEED-02 ruling.

---

## 2. CON-SEED-02 — table naming + `algorithm_version` (RESOLVED)

**Conflict.** implementation-plan §3.3 invariant #3 (`IMP-C-03`) names the table `clinical_scores` (plural) with an `algorithm_version` column; `docs/data/model.md` (`DM-T-03`) defines `clinical_score` (singular) and never declares that column.

**Resolution (data model is authoritative for physical names, barrier B).**

1. **Canonical physical name is `clinical_score` (singular).** Rationale: (a) `model.md` (authority `vision`, `DM-T-03`) uses singular; (b) *every* existing table follows singular convention — `patient_cache`, `vital_sign`, `alert`, `threshold_config` (`DM-T-01/02/04/05`); (c) the shipped Phase-1 code already declares `__tablename__ = "clinical_score"` in `src/intensicare/models/clinical_score.py`. The impl-plan's `clinical_scores` is a documentation typo, not a schema. **All plan docs MUST cite `clinical_score`.**
2. **The `algorithm_version` column is adopted, verbatim, onto `clinical_score`** (satisfying invariant #3). The Phase-1 model already carries `algorithm_version VARCHAR(32)` (nullable) in code; Phase-2 makes it **`NOT NULL`** and joins it to a first-class `algorithm_registry` (§5). This is the only schema change invariant #3 requires — the *table* was never renamed.
3. New multi-row Phase-2 tables continue the **singular** convention (`lab_result`, `medication_order`, `medication_administration`, `alert_definition`, `alert_definition_version`, `correlation_event`, `audit_trail`, `algorithm_registry`).

---

## 3. Phase-1 baseline (recap + Phase-2 deltas)

Column shapes for `patient_cache`, `vital_sign`, `clinical_score`, `alert`, `threshold_config` are as in `model.md` §Tabelas (`DM-T-01..05`) and are **not repeated** here except where Phase-2 adds columns. Referential integrity (`DM-C-02`), the three hypertables (`DM-C-03/04/05`), and multi-tenancy via indexed `tenant_id` (`DM-C-15`) are carried forward unchanged. PT-BR clinical vocabulary is preserved verbatim with accents (`DM-C-01`/`CON-0183`).

**Phase-2 deltas to existing tables:**

| Table | Delta | Source |
|---|---|---|
| `patient_cache` | Add PHI columns `cpf`, `cns` (encrypted, §6); wrap `display_name`, `mrn`, `birth_date` under pgcrypto (INV-4). | `IMP-C-04`/`CON-0069`/`CON-0103` |
| `clinical_score` | `algorithm_version` → `NOT NULL`, FK to `algorithm_registry` (INV-3). | `IMP-C-03`/`CON-0068` |
| `alert` | Add `definition_version_id` FK → `alert_definition_version` (stamps the exact firing definition, INV-3); add `correlation_event_id` (nullable) FK → `correlation_event`. | INV-3, `VIS-4-03` |
| `threshold_config` | Every write is mirrored into `audit_trail` (INV-1); superseded rows retained (config is versioned, never hard-deleted while referenced). | INV-1 |

---

## 4. Phase-2 new entities

### 4.1 Versioned declarative alert-definition schema (`alert_definition` + `alert_definition_version`)

Alert logic is **declarative data, not imperative code** — the persistence mirror of the CONTRACTS `_work/alerts/<domain>.yaml` schema and the engine schema in `alert-engine.md` §2. Two tables give an immutable version chain: a stable identity row plus an append-only version row whose content is content-hashed. The engine stamps the exact `alert_definition_version.id` onto every `alert` it raises, so any historical alert is byte-for-byte reproducible for the 7-year window (`DM-RP-03`).

```sql
-- Stable identity of an alert rule (one row per alert_id, e.g. 'SEP-001').
CREATE TABLE alert_definition (
    id              BIGSERIAL PRIMARY KEY,
    alert_id        VARCHAR(32)  NOT NULL,          -- catalog id: SEP/AKI/RESP/HEMO/DEL/ELY/DDX-NNN (CON-SEED-10)
    tenant_id       VARCHAR(32),                    -- NULL = platform-default definition (tenant may override)
    domain          VARCHAR(24)  NOT NULL,          -- sepse|aki|respiratoria|hemodinamica|delirium|eletrolitos|drogas
    name            VARCHAR(255) NOT NULL,          -- PT-BR verbatim, accents preserved (DM-C-01/CON-0183)
    current_version_id BIGINT,                      -- FK set after first version insert (see below)
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, alert_id)
);

-- Append-only version chain. A change to ANY field mints a new row; never UPDATE in place.
CREATE TABLE alert_definition_version (
    id              BIGSERIAL PRIMARY KEY,
    definition_id   BIGINT       NOT NULL REFERENCES alert_definition(id),
    version         INT          NOT NULL,          -- monotonic per definition_id (1,2,3,…)
    content_hash    CHAR(64)     NOT NULL,          -- SHA-256 of the canonical YAML body; dedups no-op edits
    severity        VARCHAR(16)  NOT NULL,          -- clinical.* band: normal|watch|urgent|critical (alert-engine §3)
    evaluation_mode VARCHAR(16)  NOT NULL,          -- micro_batch|near_real_time|hybrid (alert-engine §1)
    trigger_logic   JSONB        NOT NULL,          -- {logic, window} declarative predicate
    inputs          JSONB        NOT NULL,          -- [{name,type,unit,source,staleness_max}] — units canonical (CON-SEED-12)
    suppression     JSONB        NOT NULL,          -- {rate_limit_per_hour, cooldown_minutes, dedup_key}
    ppv_budget      DECIMAL(4,3),                   -- target PPV for this definition
    evidence        TEXT,                           -- guideline citation (e.g. Surviving Sepsis 2021, VIS-3.1-02)
    response        JSONB        NOT NULL,          -- {required, ack_sla}
    algorithm_version VARCHAR(32) REFERENCES algorithm_registry(algorithm_version), -- scorer coupling (INV-3)
    valid_from      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    created_by      VARCHAR(255) NOT NULL,
    UNIQUE (definition_id, version),
    UNIQUE (definition_id, content_hash)            -- editing back to a prior body is a no-op, not a new version
);
ALTER TABLE alert_definition
    ADD CONSTRAINT fk_current_version
    FOREIGN KEY (current_version_id) REFERENCES alert_definition_version(id);

-- alert rows point at the EXACT version that fired (INV-3):
ALTER TABLE alert ADD COLUMN definition_version_id BIGINT
    REFERENCES alert_definition_version(id);
```

`alert_definition_version` is **immutable** (append-only, enforced by the same INV-1 anti-mutation pattern of §5.3 applied to this table): no `UPDATE`/`DELETE` of a version once any `alert` references it. This is the alert-side analogue of the score-side `algorithm_version` invariant.

### 4.2 Correlation events (`correlation_event`)

The Fase-2d correlation engine (`VIS-5.2-04`) is a **second-pass evaluator over persisted domain alerts/scores** implementing exactly the three cross-domain correlations vision defines (`VIS-4-03`): (1) Sepsis+AKI, (2) Respiratory+Hemodynamic, (3) Drug+Electrolyte. A correlation is itself a first-class, auditable, versioned artifact that **references** ≥2 contributing alerts (many-to-many) and may raise its own escalated `alert`.

```sql
CREATE TABLE correlation_event (
    id                  BIGSERIAL,
    mpi_id              VARCHAR(64) NOT NULL REFERENCES patient_cache(mpi_id),
    correlation_type    VARCHAR(32) NOT NULL,       -- sepsis_aki | resp_hemodynamic | drug_electrolyte (VIS-4-03)
    definition_version_id BIGINT REFERENCES alert_definition_version(id), -- the correlation rule version (INV-3)
    severity            VARCHAR(16) NOT NULL,        -- clinical.* band; correlation typically escalates
    detected_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    window_start        TIMESTAMPTZ NOT NULL,        -- co-occurrence window the correlation evaluated over
    window_end          TIMESTAMPTZ NOT NULL,
    rationale           TEXT,                        -- PT-BR: e.g. "sepse é #1 causa de AKI" (VIS-4-03)
    raised_alert_id     BIGINT REFERENCES alert(id), -- the escalated alert this correlation produced (nullable)
    PRIMARY KEY (id, detected_at)                    -- composite PK required for hypertable time key
);
SELECT create_hypertable('correlation_event', 'detected_at');

-- M:N link: which domain alerts contributed to a correlation.
CREATE TABLE correlation_event_alert (
    correlation_event_id BIGINT NOT NULL,
    alert_id             BIGINT NOT NULL REFERENCES alert(id),
    role                 VARCHAR(24),                -- 'primary' | 'contributing'
    PRIMARY KEY (correlation_event_id, alert_id)
);
```

### 4.3 Medication entities (`medication_order`, `medication_administration`)

Vision domains 3.5/3.7 and §4.2 require an **active medication list** (drug, dose, route, frequency, start) plus **administrations with infusion rate** (vasopressors, sedatives) — sourced from **FHIR MedicationRequest / MedicationAdministration** in Gold (`VIS-3.7-10`, `VIS-4.2-07`, `ADR001-C-01`). Locally these are a **hot operational cache** for evaluation only (drug-interaction and delirium detectors); Gold remains the source of truth.

```sql
-- Active orders — FHIR MedicationRequest cache (order/admin cadence, VIS-4.2-07).
CREATE TABLE medication_order (
    id              BIGSERIAL PRIMARY KEY,
    mpi_id          VARCHAR(64) NOT NULL REFERENCES patient_cache(mpi_id),
    fhir_id         VARCHAR(64) NOT NULL,            -- MedicationRequest.id in HAPI FHIR (idempotency key)
    rxnorm_code     VARCHAR(32),                     -- coding; drug identity for interaction checks
    drug_name       VARCHAR(255) NOT NULL,           -- PT-BR display, accents preserved
    drug_class      VARCHAR(64),                     -- for therapeutic-duplication (VIS-3.7-06): PPI, anticoagulant…
    dose            DECIMAL(10,3),
    dose_unit       VARCHAR(16),                     -- canonical unit (CON-SEED-12; registry-validated)
    route           VARCHAR(24),                     -- IV | PO | SC …
    frequency       VARCHAR(32),
    started_at      TIMESTAMPTZ,
    stopped_at      TIMESTAMPTZ,                      -- NULL = still active
    status          VARCHAR(16) NOT NULL,            -- active | completed | stopped | on-hold
    source_system   VARCHAR(32) NOT NULL DEFAULT 'amh_gold',
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (fhir_id)                                 -- ON CONFLICT DO NOTHING idempotency (INV-2 pattern)
);
CREATE INDEX ix_medorder_active ON medication_order (mpi_id) WHERE stopped_at IS NULL;

-- Administrations — FHIR MedicationAdministration cache, with infusion rate (vasopressors, VIS-3.4-09).
CREATE TABLE medication_administration (
    id              BIGSERIAL,
    mpi_id          VARCHAR(64) NOT NULL REFERENCES patient_cache(mpi_id),
    order_id        BIGINT REFERENCES medication_order(id),
    fhir_id         VARCHAR(64) NOT NULL,
    administered_at TIMESTAMPTZ NOT NULL,
    dose            DECIMAL(10,3),
    dose_unit       VARCHAR(16),                     -- canonical (e.g. vasopressor mcg/kg/min, CON-SEED-12)
    infusion_rate   DECIMAL(10,3),                   -- rate for continuous infusions
    rate_unit       VARCHAR(16),                     -- canonical; mL/h rejected pre-conversion at ingest edge
    source_system   VARCHAR(32) NOT NULL DEFAULT 'amh_gold',
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id, administered_at),
    UNIQUE (fhir_id, administered_at)
);
SELECT create_hypertable('medication_administration', 'administered_at');
```

### 4.4 Lab results (`lab_result`)

Sepsis/AKI/electrolyte/drug detectors need lactate, PCT, WBC, creatinine, electrolyte panels, blood gas (`VIS-3.1-07`, `VIS-3.2-07`, `VIS-3.6-11`, `VIS-4.2-01/06`) via **FHIR Observation / DiagnosticReport** in Gold. Local `lab_result` is a hot cache; a hypertable because labs are a time-series event stream keyed by result time.

```sql
CREATE TABLE lab_result (
    id              BIGSERIAL,
    mpi_id          VARCHAR(64) NOT NULL REFERENCES patient_cache(mpi_id),
    fhir_id         VARCHAR(64) NOT NULL,            -- Observation.id (idempotency)
    loinc_code      VARCHAR(16),                     -- analyte identity (lactate, creatinine, K+, WBC, PCT…)
    analyte         VARCHAR(64) NOT NULL,            -- PT-BR display; e.g. 'lactato', 'creatinina', 'potássio'
    value_num       DECIMAL(12,4),
    value_unit      VARCHAR(16),                     -- canonical (lactate mmol/L, creatinine mg/dL — CON-SEED-12)
    value_text      VARCHAR(128),                    -- for non-numeric results (e.g. cultura: positiva/negativa)
    reference_low   DECIMAL(12,4),
    reference_high  DECIMAL(12,4),
    abnormal_flag   VARCHAR(8),                      -- H | L | HH | LL | N
    collected_at    TIMESTAMPTZ NOT NULL,            -- specimen collection (clinical time)
    resulted_at     TIMESTAMPTZ NOT NULL,            -- result availability
    source_system   VARCHAR(32) NOT NULL DEFAULT 'amh_gold',
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id, collected_at),
    UNIQUE (fhir_id, collected_at)
);
SELECT create_hypertable('lab_result', 'collected_at');
CREATE INDEX ix_lab_patient_analyte ON lab_result (mpi_id, loinc_code, collected_at DESC);
```

---

## 5. Algorithm versioning (INV-3) — `CON-0068`/`IMP-C-03`

**Requirement.** Every computed score and every raised alert MUST record the exact algorithm/definition version that produced it, so historical results are auditable and reproducible ("Impossibilidade de auditar scores históricos" is the stated risk if absent, `IMP-C-03`).

### 5.1 `algorithm_registry` (immutable scorer catalog)

```sql
CREATE TABLE algorithm_registry (
    algorithm_version VARCHAR(32) PRIMARY KEY,        -- e.g. 'MEWS@1.2.0', 'NEWS2@2.0.0', 'SOFA@1.0.0'
    score_type        VARCHAR(16) NOT NULL,           -- MEWS|NEWS2|SOFA|qSOFA (DM-VOCAB-02)
    semver            VARCHAR(16) NOT NULL,            -- 1.2.0
    spec_hash         CHAR(64) NOT NULL,              -- SHA-256 of the scorer spec/coefficients
    description       TEXT,                           -- PT-BR change note, accents preserved
    effective_from    TIMESTAMPTZ NOT NULL DEFAULT now(),
    retired_at        TIMESTAMPTZ,                    -- soft-retire; row never deleted
    UNIQUE (score_type, semver)
);
```

### 5.2 Coupling to `clinical_score` (make column NOT NULL)

```sql
-- Phase-1 already has algorithm_version VARCHAR(32) NULLable; Phase-2 tightens it (CON-SEED-02 resolution).
UPDATE clinical_score SET algorithm_version = score_type || '@0.0.0' WHERE algorithm_version IS NULL; -- backfill legacy
ALTER TABLE clinical_score ALTER COLUMN algorithm_version SET NOT NULL;
ALTER TABLE clinical_score
    ADD CONSTRAINT fk_score_algorithm
    FOREIGN KEY (algorithm_version) REFERENCES algorithm_registry(algorithm_version);
```

Alerts are versioned analogously via `alert.definition_version_id → alert_definition_version` (§4.1). Correlations via `correlation_event.definition_version_id` (§4.2). A threshold change (in `threshold_config`) does **not** mutate a score version — thresholds are config, versioned separately and audited under INV-1.

---

## 6. Immutable audit trail (INV-1) — `CON-0066`/`CON-0097`/`IMP-C-01`

**Requirement.** An **append-only** `audit_trail` table **with an anti-mutation trigger**, in place **before the first real patient ingest** — stated risk if absent: *"Ilegal (LGPD + CFM 1.821/07)"* (`IMP-C-01`). Every clinically/legally significant mutation (alert lifecycle transitions — ack/resolve, threshold edits, definition-version mints, PHI reads) writes one immutable row. It is a hypertable so retention/partitioning are chunk-managed like the other time-series entities.

```sql
CREATE TABLE audit_trail (
    id            BIGSERIAL,
    event_ts      TIMESTAMPTZ NOT NULL DEFAULT now(),
    tenant_id     VARCHAR(32),
    actor         VARCHAR(255) NOT NULL,            -- IAM Identity Center subject (ADR001-C-07)
    action        VARCHAR(48)  NOT NULL,            -- alert.acknowledge | alert.resolve | threshold.update | phi.read …
    entity_table  VARCHAR(48)  NOT NULL,
    entity_id     VARCHAR(64)  NOT NULL,
    mpi_id        VARCHAR(64),                      -- subject patient, when applicable
    before_state  BYTEA,                            -- pgcrypto-encrypted prior snapshot (may contain PHI, INV-4)
    after_state   BYTEA,                            -- pgcrypto-encrypted new snapshot
    request_id    VARCHAR(64),                      -- OTEL trace id (ADR001-C-06) for cross-system correlation
    PRIMARY KEY (id, event_ts)
);
SELECT create_hypertable('audit_trail', 'event_ts');

-- Anti-mutation trigger: block UPDATE and DELETE unconditionally (append-only).
CREATE OR REPLACE FUNCTION audit_trail_no_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'audit_trail is append-only (INV-1 / CON-0066): % blocked', TG_OP;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_trail_immutable
    BEFORE UPDATE OR DELETE ON audit_trail
    FOR EACH ROW EXECUTE FUNCTION audit_trail_no_mutation();

-- Also revoke UPDATE/DELETE at the grant level (defense in depth):
REVOKE UPDATE, DELETE ON audit_trail FROM intensicare_app;
GRANT  INSERT, SELECT  ON audit_trail TO   intensicare_app;
```

The same append-only trigger pattern is applied to `alert_definition_version` and `algorithm_registry` (both immutable once referenced). **Note (open):** CFM 1.821/07 sets a **20-year** minimum retention for the *prontuário*; the audit-trail retention below is aligned to the stated 7-year platform window but is flagged for legal ratification — see §8 and Open Questions.

---

## 7. Encryption at rest for PHI (INV-4) — `CON-0069`/`CON-0103`/`IMP-C-04`

**Requirement.** `pgcrypto` column-level encryption for PHI — **explicitly `nome, CPF, CNS`** (`IMP-C-04`/`CON-0103`); stated risk if absent: *"Violação LGPD Art. 46"*. This is layered **on top of** the inherited per-tenant **KMS** volume/storage encryption (`ADR001-C-07`/`CON-0007`) — pgcrypto protects against DB-level exposure (dumps, replicas, insider reads) that volume encryption does not. Only `patient_cache` (and encrypted audit snapshots) hold direct PHI; all other tables key on the pseudonymous `mpi_id` (`ADR001-C-02`).

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- PHI columns stored as BYTEA ciphertext (pgp_sym_encrypt). Key supplied per-request from KMS-issued
-- data key (per-tenant, ADR001-C-07); never stored in the DB or in code.
ALTER TABLE patient_cache
    ADD COLUMN cpf         BYTEA,                    -- NEW PHI: Brazilian tax id
    ADD COLUMN cns         BYTEA,                    -- NEW PHI: Cartão Nacional de Saúde
    ALTER COLUMN display_name TYPE BYTEA USING pgp_sym_encrypt(display_name, current_setting('app.dek')),
    ALTER COLUMN mrn          TYPE BYTEA USING pgp_sym_encrypt(mrn,          current_setting('app.dek'));
-- birth_date kept as DATE but access-logged (INV-1); if LGPD-restricted, store encrypted too.

-- Read path (app sets the per-tenant data-encryption key into a GUC for the transaction):
--   SELECT pgp_sym_decrypt(display_name, current_setting('app.dek')) FROM patient_cache WHERE mpi_id = $1;
-- Every such PHI read emits an audit_trail row action='phi.read' (INV-1).

-- Deterministic search on encrypted identifiers uses a keyed HMAC blind index, not the ciphertext:
ALTER TABLE patient_cache
    ADD COLUMN mrn_bidx BYTEA;                       -- hmac(mrn, index_key) — allows equality lookup without decryption
CREATE INDEX ix_patient_mrn_bidx ON patient_cache (mrn_bidx);
```

---

## 8. Hypertable & retention strategy per entity — `CON-SEED-03` (RESOLVED)

**Conflict.** vision §7.2 advertises a blanket *"TimescaleDB 7-year retention"* (`VIS-C-12`/`VIS-7.2-04`); `model.md` retains **raw `vital_sign` only 90 days** (scores/alerts 7y) (`DM-RP-01..04`).

**Resolution (precise, per-entity).** The 7-year figure is a **platform-level compliance obligation**, satisfied by the **AMH Gold layer (Apache Iceberg)** which is the authoritative long-term store for all raw clinical source data (vitals, labs, meds are *read from* Gold, `ADR001-C-01`, `DM-DATA-01`). The **operational** PostgreSQL/TimescaleDB keeps only a **hot working window** per entity (`ADR001-C-03` — operational-only). Thus there is no real conflict once the two tiers are distinguished: **raw source data → 7y+ at Gold; operational/derived data → per-entity hot window locally, with derived scores/alerts also kept 7y locally for lifecycle + write-back.**

| Entity | Kind | Local hot retention | 7-yr compliance met at | Mechanism | PHI | Invariants | Source |
|---|---|---|---|---|---|---|---|
| `patient_cache` | table | discharge + 30 days | MPI (source of truth) | app flush job; `is_active`/`synced_at` | **yes** | INV-4 | `DM-RP-04`, `DM-C-07` |
| `vital_sign` | hypertable | **90 days** | AMH Gold (Iceberg) | `add_retention_policy('vital_sign', INTERVAL '90 days')` | no | — | `DM-RP-01`, `DM-C-03` |
| `lab_result` | hypertable | **90 days** | AMH Gold (Iceberg) | `add_retention_policy('lab_result', INTERVAL '90 days')` | no | — | `VIS-4.2-06` + parity with vitals |
| `medication_order` | table | discharge + 30 days | AMH Gold (FHIR) | app flush job on `stopped_at`/discharge | no | — | operational cache, `ADR001-C-01` |
| `medication_administration` | hypertable | **90 days** | AMH Gold (FHIR) | `add_retention_policy('medication_administration', INTERVAL '90 days')` | no | — | parity with vitals |
| `clinical_score` | hypertable | **7 years** | local (also write-back Gold `fact_patient_score`) | `add_retention_policy(…, INTERVAL '7 years')` | no | INV-3 | `DM-RP-02`, `DM-C-04`, `CON-0027` |
| `alert` | hypertable | **7 years** | local (also write-back Gold `fact_alert`) | `add_retention_policy(…, INTERVAL '7 years')` | no | INV-3 | `DM-RP-03`, `DM-C-05`, `CON-0028` |
| `correlation_event` | hypertable | **7 years** | local (+ write-back with parent alert) | `add_retention_policy(…, INTERVAL '7 years')` | no | INV-3 | alert-class artifact, parity `DM-RP-03` |
| `alert_definition` | table | indefinite (while active) | local | never dropped while `is_active`/referenced | no | INV-3 | §4.1 |
| `alert_definition_version` | table | ≥ 7 years (immutable) | local | append-only; retained ≥ longest referencing alert | no | INV-1, INV-3 | §4.1 |
| `algorithm_registry` | table | indefinite (immutable) | local | append-only; retained ≥ longest referencing score | no | INV-3 | §5.1 |
| `threshold_config` | table | indefinite (versioned) | local | superseded rows kept; changes audited | no | INV-1 | `DM-C-11`, `DM-RP` (no drop) |
| `audit_trail` | hypertable | **7 years** (flag: CFM 20y) | local | `add_retention_policy(…, INTERVAL '7 years')`; **append-only** | yes (encrypted) | INV-1, INV-4 | `IMP-C-01`, §6 note |

**Continuous aggregates (optional, deferred).** To retain *analytic* value of vitals/labs beyond 90 days without keeping raw rows, hourly continuous aggregates (`vital_sign_1h`, `lab_result_1d`) MAY be materialized and retained 7y locally — but this is **not required**, since Gold already holds the raw history (`DM-DATA-01`). Recorded as an option, not a mandate, to respect operational-only (`ADR001-C-03`).

```sql
-- Retention policies (TimescaleDB background jobs; drop chunks older than the window):
SELECT add_retention_policy('vital_sign',                INTERVAL '90 days');
SELECT add_retention_policy('lab_result',                INTERVAL '90 days');
SELECT add_retention_policy('medication_administration', INTERVAL '90 days');
SELECT add_retention_policy('clinical_score',            INTERVAL '7 years');
SELECT add_retention_policy('alert',                     INTERVAL '7 years');
SELECT add_retention_policy('correlation_event',         INTERVAL '7 years');
SELECT add_retention_policy('audit_trail',               INTERVAL '7 years'); -- pending CFM ratification (§Open)
```

---

## 9. Invariant verification register (REQ-INV-1 / -3 / -4)

Requirements owned by this data model. IDs are `REQ-INV-<invariant>-<k>`. (INV-2/5/6 are registered in `alert-engine.md` §10.)

| ID | Requirement | Verification | Owning component |
|---|---|---|---|
| **REQ-INV-1-1** | `audit_trail` exists as an **append-only** table before the first real-patient ingest; a `BEFORE UPDATE OR DELETE` trigger raises and blocks every mutation (`CON-0066`/`CON-0097`/`IMP-C-01`). | Migration test asserts trigger present; attempt `UPDATE`/`DELETE` on a seeded row → exception, row unchanged; CI integration test. | Operational DB / migrations (`audit_trail` + `trg_audit_trail_immutable`). |
| **REQ-INV-1-2** | Every alert lifecycle transition (ack/resolve/expire), threshold edit, definition-version mint, and PHI read writes exactly one `audit_trail` row with actor, action, before/after, and OTEL `request_id` (`ADR001-C-06`). | For each mutating endpoint, integration test asserts one audit row with correct `action`/`actor`/`entity_id`; assert `request_id` ties to the OTEL trace. | API service layer (alerts, thresholds) + audit writer. |
| **REQ-INV-1-3** | `alert_definition_version` and `algorithm_registry` are immutable once referenced — no in-place edit of a version; a change mints a new row (append-only). | Attempt to `UPDATE` a referenced version/registry row → blocked; content edited back to a prior body is deduped by `content_hash`/`spec_hash`, not a new version. | Definition/registry stores + append-only triggers. |
| **REQ-INV-3-1** | Canonical table is `clinical_score` (singular); `algorithm_version` is `NOT NULL` and FK to `algorithm_registry` — resolves CON-SEED-02 (`IMP-C-03`/`CON-0068`). | Schema assertion: `clinical_score.algorithm_version` NOT NULL + FK exists; no table named `clinical_scores`; backfill migration leaves zero NULLs. | `clinical_score` model + `algorithm_registry`. |
| **REQ-INV-3-2** | Every raised `alert` stamps `definition_version_id` (exact firing `alert_definition_version`); every `correlation_event` stamps its rule version — historical alerts are reproducible for 7y. | Fire an alert, bump the definition to v+1, re-query the old alert → still resolves to the original version body; version chain test. | Alert engine write path + `alert_definition_version`. |
| **REQ-INV-3-3** | Score/alert write-back to Gold `fact_patient_score`/`fact_alert` carries the `algorithm_version`/`definition_version` so corporate analytics can partition by algorithm (`ADR001-C-04`/`CON-0004`). | Write-back integration test asserts the version column is present and populated in the Gold fact payload. | Gold write-back job (amh-integration handoff). |
| **REQ-INV-4-1** | PHI columns `nome (display_name), CPF, CNS, MRN` in `patient_cache` are stored `pgcrypto`-encrypted (BYTEA); plaintext never persisted (`CON-0069`/`CON-0103`/`IMP-C-04`). | Inspect raw table bytes → ciphertext only; a dump contains no plaintext PHI; decrypt-round-trip unit test with a per-tenant key. | `patient_cache` + pgcrypto/key-management. |
| **REQ-INV-4-2** | Encryption keys are per-tenant, KMS-issued data keys injected per transaction (GUC), never stored in the DB or source (`ADR001-C-07`/`CON-0007`). | Grep schema/seed for embedded keys → none; verify DEK is set per session and rotated; cross-tenant decrypt with wrong key fails. | Key-management (KMS integration) + app session bootstrap. |
| **REQ-INV-4-3** | Equality lookup on encrypted `MRN` uses a keyed HMAC blind index, not plaintext or ciphertext scan; encrypted `before/after_state` in `audit_trail` protects PHI in snapshots. | Query by `mrn_bidx` returns the row without decrypting; confirm no plaintext MRN index exists; audit snapshot bytes are ciphertext. | `patient_cache` blind index + `audit_trail` encryption. |

---

## 10. Open questions / handoffs

1. **CFM 1.821/07 retention.** The prontuário minimum is **20 years**; §8 sets `audit_trail` to 7y aligned to the stated platform window (`VIS-C-12`). Whether the audit trail is legally part of the prontuário (→ 20y) is routed to legal/compliance ratification. (Extends `data-model.json` open-Q on backup/recovery for long windows.)
2. **Gold write-back SLA** for `fact_patient_score`/`fact_alert` (real-time / hourly / daily) — owned by amh-integration-architect (`data-model.json` open-Q).
3. **NRT operational feed vs Athena-only** for meds/labs/vitals used by NRT detectors — the ADR-001 Alternativa-B decision is owned by amh-integration-architect and signed off at barrier C3 (see `alert-engine.md` §1.2). This data model states the *hot cache* shape regardless of feed mechanism.
4. **`threshold_config.unit` matching** (exact vs wildcard) — unchanged open question from `data-model.json`; affects `alert_definition.tenant_id` override resolution.
5. **`patient_cache` primary key** — recommend `PRIMARY KEY (mpi_id)` (natural key, one cache row per patient); confirms `data-model.json` open-Q.
