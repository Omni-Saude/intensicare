# 0021. trilhas-engine data model: versioned pathways, state snapshots, and patient-pathway cardinality

Status: accepted
Date: 2026-07-07
Depends on: ADR-001 (AMH Data Platform consumer), ADR 0020 (trilhas-engine architecture)
Audit source: trilhas-engine cluster — 18 legacy rules; data model audit of `ahlabs-trilhas` @ `8166c07e` and `trilhas-frontend` @ `f9656be2`

## Context and Problem Statement

The legacy trilhas-engine stores care-pathway data in a Django ORM model layer (`ahlabs-trilhas`) with the following shape, reconstructed from the 18 audited rules:

- **Pathway definitions (`Trilha*Model` classes)** are Python model classes, not database rows. The 9 automatic pathway models (`TrilhaSedacaoV3`, `TrilhaEstabilidadeV3`, `TrilhaSepseV3`, `TrilhaProfilaxiaV3`, `TrilhaVentilacao`, `TrilhaAntimicrobiano`, `TrilhaNutricao`, `TrilhaEquilibrio`, `TrilhaGlozaZero`) are hard-coded in `trilha_automatica.models` — there is no `pathway_definition` table, no versioning, and no runtime registration (`RULE-TRILHAS-ENGINE-001`, `009`).
- **Pathway instances (`Trilha*` rows)** are created per patient per admission via `CriarTrilhas` (4 manual rows per prontuario: Estabilidade, Sedacao, Sepse, Ventilacao — `RULE-TRILHAS-ENGINE-011`). Automatic pathways are re-linked to beds via `AtualizarTrilhasV3` (`RULE-TRILHAS-ENGINE-012`). The patient-pathway cardinality is effectively **M:N** (one patient can have multiple pathway rows; one pathway type can exist for multiple patients), but the relationship is scoped per-encounter (`nr_atendimento`) in some code paths and per-patient-lifetime in others — an unresolved ambiguity flagged as AMBIGUOUS (`RULE-TRILHAS-ENGINE-012`, ESC-AMBIGUOUS-308).
- **No state snapshots.** The only state-like concept is the `assistido` (attended) boolean flag on a pathway row, toggled client-side via a React checkbox. There is no audit trail of state transitions, no timestamped lifecycle, and no resolution tracking (`RULE-TRILHAS-ENGINE-007`).
- **No versioning of pathway definitions.** Changing a criterion threshold means editing Python code in a model method and deploying — there is no record of which version of a pathway definition fired which alert, no reproducibility for historical alerts, and no ability to A/B test threshold changes.
- **The 12-slug pathway-type enumeration exists in two diverged copies** (`AssistidoChoices.tipo` vs `ObservacaoChoices.tipo_trilha`) with drifted display labels and different `max_length` constraints — no single canonical source (`RULE-TRILHAS-ENGINE-018`).

The v2 IntensiCare replaces the trilhas-engine with a declarative Alert Engine (ADR 0020). This ADR resolves the data-model questions that the legacy left open: **how should pathway (now alert) definitions be versioned? Should the system persist state snapshots of patient clinical context? What is the correct patient-to-alert cardinality, and how is it scoped?**

### Decision Drivers

- **INV-3** (`CON-0068`/`IMP-C-03`): every score and alert must stamp the exact `algorithm_version` / `definition_version` that produced it. Historical alerts must be exactly reproducible for the 7-year retention window.
- **INV-1** (`CON-0066`/`IMP-C-01`): every state transition (alert lifecycle, threshold config change) must write an immutable, append-only `audit_trail` row. Legal requirement: LGPD + CFM 1.821/07.
- **DM-C-01** (`CON-0183`): PT-BR clinical vocabulary preserved verbatim with accents — display labels are a clinical asset, not a localization concern.
- **ADR001-C-02** (`CON-0002`): patient identity is the MPI `mpi_id`; IntensiCare mints no patient identifiers.
- **ADR001-C-04** (`CON-0004`): historical scores/alerts written back to Gold `fact_patient_score` / `fact_alert`.
- **DM-C-11** (`CON-0029`): `threshold_config` is operational-only, never persisted to Gold.
- The legacy's AMBIGUOUS-band escalations (ESC-AMBIGUOUS-308: per-encounter vs per-patient-lifetime scoping) must be resolved explicitly, not carried forward.

## Considered Options

### Option 1: Versioned pathway definitions as mutable database rows with history tables (ledger-style)

Pathway definitions live as rows in an `alert_definition` table. Each row has an `id`, `domain`, `name`, `trigger_logic`, `inputs`, `severity`, etc. Changing a definition inserts a new row in `alert_definition_version` with a `version_number`, `content_hash`, and `valid_from` timestamp. The engine always evaluates against the version with `valid_from <= NOW()` and highest `version_number`. Alert instances reference `definition_version_id`. Superseded versions are retained indefinitely for audit reproducibility.

- **Pros:**
  - Standard SQL pattern (slowly changing dimension type 2). DB-level referential integrity between alerts and the definition version that fired them.
  - `valid_from` timestamps enable time-travel queries: "what definition was active when this alert fired on June 15?"
  - Mutable definitions with immutable history are familiar to operations teams — "edit a threshold" is an INSERT, not a code change.
- **Cons:**
  - The "current active version" must be resolved at query time with `valid_from <= NOW()` — a window function or subquery per evaluation. Adds latency to the hot path unless cached.
  - Synchronizing definition changes across environments (dev → staging → prod) requires a migration process for database rows, not just version-controlled YAML files.
  - The audit trail of *who changed what* is on the `alert_definition_version` table — but this duplicates INV-1's `audit_trail` if not carefully scoped. Two tables carrying similar data risks divergence.
  - The `valid_from` approach cannot represent "this definition was evaluated at time T and produced this alert" without storing the evaluation timestamp separately from the definition's validity window — the alert's `evaluated_at` is the ground truth, and it must match a version whose `valid_from <= evaluated_at < valid_to`. This is a temporal-join correctness problem that SCD type 2 is notorious for getting wrong at the edges.

### Option 2: Immutable, content-addressed alert definitions as YAML/JSON artifacts (build-time)

Alert definitions live as version-controlled YAML files in `docs/plan/_work/alerts/<domain>.yaml`. The build process (CI) validates each definition against the CONTRACTS schema, runs the unit-check and criterion-reachability gates (ADR 0020 §2), hashes the canonicalized content, and emits a `definition_version` tuple `(version_number, content_hash, compiled_at)`. The compiled registry is loaded at engine startup. Alert instances store `definition_version_id` (the content hash). The YAML files are the source of truth; the compiled registry is a build artifact.

- **Pros:**
  - **Content addressing eliminates temporal-join ambiguity.** The alert's `definition_version_id` is a cryptographic hash of the exact definition content. Given the hash, the definition is deterministically reproducible — no `valid_from` window, no edge-case temporal joins. Reproducibility for the 7-year window is a content-lookup, not a temporal query.
  - **Git is the audit trail for definition changes.** Who changed what, when, and why lives in the commit history. There is one source of truth (the YAML file), one validation pipeline (CI), and one deploy artifact (the compiled registry). No risk of a DBA editing a threshold directly in production and bypassing review.
  - **Environment promotion is version-controlled release.** Promoting a threshold change from staging to prod is a merge + deploy — the same process as code. No separate "definition migration" tooling needed.
  - **Build-time validation is deterministic.** The CI gates (unit resolution, criterion reachability, band partition, facade==predicate) run on every commit. A definition that fails CI cannot be deployed. This is the ADR 0020 architecture's core safety property, and it depends on definitions being build-time artifacts, not runtime-mutable rows.
- **Cons:**
  - Changing a threshold requires a code change (edit YAML, commit, CI, deploy) — slower than a database UPDATE. Acceptable because: (a) clinical thresholds should never be changed without review (patient safety); (b) the legacy had no review process at all for Python code changes; (c) the `threshold_config` table (§6 of `alert-engine.md`) handles per-tenant tuning of score-to-severity bands, which *is* a runtime configuration concern — it is the escape valve for operational threshold tuning, with its own INV-1 audit trail.
  - Content hashing requires canonicalization (consistent key ordering, whitespace normalization) — a small build-step complexity. Mitigated: the CONTRACTS schema enforces a canonical YAML structure; the hash is computed over the parsed, normalized AST, not raw file bytes.
  - Cannot support runtime A/B testing of different definition versions on the same patient population without deploying multiple registry versions simultaneously. This is a future concern (not in MVP scope) and can be addressed by supporting multiple active registries keyed by `experiment_id` if needed.

### Option 3: Patient-pathway state snapshots (persist a clinical context snapshot per patient per evaluation cycle)

Every time the engine evaluates a patient, it persists a `patient_clinical_snapshot` row: the patient's current `mpi_id`, `bed_id`, `unit`, the set of input values that went into the evaluation, the scores computed, and which alert definitions fired. This is the "state snapshot" approach — the database contains a complete, self-contained record of the patient's clinical state at each evaluation point, independent of the source data.

- **Pros:**
  - Complete reproducibility: given a snapshot row, every downstream decision (which alerts fired, with what severity) can be re-derived without re-querying AMH Gold or the operational store. This is stronger than definition-version reproducibility alone — it reproduces the *inputs*, not just the *algorithm*.
  - Decouples the evaluation from source data availability: if AMH Gold is temporarily unavailable, historical snapshots are still queryable for audit/analytics.
  - Naturally supports "what was the patient's state when this alert fired?" queries without joining across the operational hypertables and Gold.
- **Cons:**
  - **Massive storage cost.** A full snapshot per patient per evaluation cycle (potentially every ~30s for NRT domains, every 5 min for hybrid) for a 30-bed ICU with 7 domains means millions of rows per day. Each row carries the full input vector — dozens of clinical parameters. This is a data-volume problem, not a query-performance problem; the cost is in storage and write throughput.
  - **Redundant with the operational store.** The input values (vital signs, lab results) already live in `vital_sign` and `lab_result` hypertables. The snapshot duplicates them. The `fact_patient_score` and `fact_alert` write-back to Gold (`ADR001-C-04`) already provides the analytical reproducibility path.
  - **Snapshot ≠ ground truth.** The snapshot captures what the engine *saw* at evaluation time, but source data can be corrected/amended later (a lab result retracted, a vital sign corrected). The snapshot would then diverge from the authoritative record — creating two competing "truths." The operational store + Gold `fact_*` tables are the single source of truth; the snapshot introduces a third copy with its own consistency problems.
  - The legacy had no snapshots and suffered no patient-safety incident from their absence — the gap was *definition* versioning (no way to know which algorithm version fired an alert), not *input* versioning.

### Option 4: Patient-to-alert 1:N, scoped per encounter (admission), with explicit bed re-association

Each `alert` row carries `mpi_id` (patient identity, from ADR-001), `encounter_id` (the `nr_atendimento` / admission identifier from the source system), `bed_id`, and `unit`. The patient-to-alert cardinality is **1:N** (one patient can have many alerts; each alert belongs to exactly one patient and one encounter). When a patient is transferred between beds, the `patient_cache` bed re-association triggers a re-evaluation for that patient — existing alerts are not moved or copied; new alerts carry the new `bed_id`. The legacy's AMBIGUOUS-band question (per-encounter vs per-patient-lifetime) is resolved: **per encounter** — an alert is always associated with a specific admission, matching the clinical reality that a patient's sepsis episode during admission #1 is a distinct clinical event from their AKI during admission #6.

- **Pros:**
  - Resolves the AMBIGUOUS escalation (ESC-AMBIGUOUS-308) explicitly: the per-encounter scope is the correct clinical unit of surveillance — patient-lifetime scope makes no clinical sense for acute ICU events.
  - `encounter_id` enables per-admission analytics (alert count per stay, time-to-resolution per admission) without temporal-join ambiguity.
  - Bed re-association is a non-event for existing alerts — no migration, no row updates. New evaluations pick up the new bed and context naturally.
  - Aligns with the `fact_alert` Gold write-back schema (`CON-0028`, `DM-AMH-04`), which already carries `encounter_id`.
- **Cons:**
  - Requires a reliable `encounter_id` from the source system (AMH Gold). If the source system's admission identifier is unreliable or missing for some patients, alerts fall back to `mpi_id`-only — introducing a NULLable column with two interpretations. Mitigation: `encounter_id` is `NOT NULL` by schema contract; missing encounters are a data-quality defect surfaced by the staleness watchdog (`alert-engine.md` §7.2), not silently accepted.
  - Cross-admission analytics (e.g., "this patient had 3 septic episodes across 5 admissions") requires joining on `mpi_id` across encounters — straightforward with the MPI but an extra query dimension.

## Decision Outcome

Chosen option: **Option 2 (immutable, content-addressed definitions) for versioning, rejecting Option 3 (state snapshots), and adopting Option 4 (patient-to-alert 1:N, per encounter) for cardinality.**

**Justification:**

### Versioning: Option 2 (content-addressed, build-time artifacts)

The core argument is **reproducibility without temporal-join ambiguity**. Given an alert's `definition_version_id` (a content hash), the exact definition that produced it is deterministically retrievable — no `valid_from` windows, no edge-case temporal joins, no risk of a DBA having edited a threshold directly in production. This directly satisfies INV-3 (`CON-0068`): "every score and alert must stamp the exact algorithm_version/definition_version that produced it."

Option 1 (SCD type 2 rows) is a familiar pattern but introduces temporal-join correctness problems that are well-known to produce subtle bugs at validity-window boundaries. The legacy's AMBIGUOUS escalation around per-encounter vs per-patient-lifetime is exactly this class of bug — temporal scope ambiguity. Content addressing eliminates the ambiguity entirely: the alert points at a specific, immutable definition, not a time range.

The concern about "changing a threshold requires a deploy" is mitigated by the separation of concerns in the v2 architecture: **clinical thresholds** (K⁺ > 6.5, KDIGO stage boundaries) live in alert definitions and *should* require review + deploy because they affect patient safety. **Operational tuning** (per-tenant MEWS score→severity band mapping, cooldown intervals) lives in `threshold_config` — a runtime-mutable table with its own INV-1 audit trail — providing the escape valve for configuration changes that do not alter clinical logic.

### State snapshots: Rejecting Option 3

State snapshots are rejected for the v2 MVP for three reasons:

1. **Redundancy and consistency risk.** The input values already live in `vital_sign` and `lab_result` hypertables. The `fact_patient_score` and `fact_alert` write-back to Gold provides the analytical reproducibility path. A third copy (snapshots) creates a consistency problem: when source data is corrected, the snapshot diverges from the authoritative record.

2. **The legacy gap was *definition* versioning, not *input* versioning.** The audit's systemic defect classes (SYS-04/06/07/08) are defects in the algorithm, not in the input capture. The v2's content-addressed definitions + hypertable-based input storage + Gold write-back provide full reproducibility without snapshot duplication.

3. **Cost is disproportionate to benefit.** Full snapshots per patient per evaluation cycle generate massive write volume. The benefit — independent auditability when AMH Gold is unavailable — is a disaster-recovery concern, not a clinical-operations concern. The operational store + Gold write-back is the authoritative record; an additional snapshot table is a third copy that adds storage cost and consistency risk without addressing a patient-safety gap.

If a future regulatory requirement demands per-evaluation input snapshots, the architecture supports adding them as a separate, purpose-built `evaluation_input` hypertable that records only the *deltas* (which inputs changed since the last evaluation) rather than full snapshots — a more storage-efficient design that can be layered on without changing the core model.

### Patient-to-alert cardinality: Option 4 (1:N, per encounter)

The 1:N, per-encounter model is the only option that matches both clinical reality and the v2 architecture's data flow:

- **Clinical reality:** An ICU alert (sepsis, AKI, respiratory deterioration) is an event within a specific admission. The same patient's sepsis during admission #1 is a distinct clinical event from their AKI during admission #6. Per-patient-lifetime scope conflates unrelated episodes; per-encounter scope keeps them separate and analyzable.
- **Data flow:** The AMH Gold layer provides `encounter_id` as part of the patient context. The MPI provides `mpi_id`. The `patient_cache` carries both and associates them with `bed_id` and `unit`. An alert naturally carries the encounter context available at evaluation time.
- **Bed re-association:** When a patient transfers beds, the `patient_cache` update triggers re-evaluation. New alerts carry the new `bed_id` and possibly a new `encounter_id` (if the transfer coincides with a new admission). Existing alerts are unaffected — no row migration, no state-transfer complexity. This resolves the legacy's bed-re-link AMBIGUITY (ESC-AMBIGUOUS-308): the re-evaluation picks up the current encounter context naturally.

The legacy's alternative — M:N patient-to-pathway, with pathways created once per lifetime and re-linked to beds — is the root cause of the AMBIGUOUS-band escalation: it's unclear whether a v3 pathway row belongs to the *patient* or the *current encounter*. The 1:N per-encounter model eliminates this ambiguity at the schema level.

### Consequences

**Positive:**
- **Definition reproducibility is deterministic.** `definition_version_id = SHA256(canonicalized_definition_content)`. No temporal-join correctness problems — the alert points at an immutable artifact.
- **Git is the audit trail for clinical logic changes.** Every threshold change is a reviewed, version-controlled commit. No production DBA can silently edit a clinical cutoff.
- **The legacy's per-encounter ambiguity is resolved at the schema level.** `alert.encounter_id NOT NULL` is enforced by the schema contract; missing encounters are data-quality defects surfaced by the staleness watchdog, not silently accepted.
- **Bed re-association is a non-event for existing alerts.** No migration, no row updates — the patient's new bed context flows naturally into the next evaluation cycle.
- **Storage efficiency.** No redundant snapshots. Input data lives once in the operational hypertables and is written back to Gold for analytics. The audit trail captures state *transitions* (lifecycle events, config changes), not state *snapshots*.
- **The 12-slug pathway-type enumeration (ADOPT-CORRECTED)** is adopted into the v2 data model as the `domain` field on `alert_definition`, corrected to a single canonical source with accented PT-BR labels per `DM-C-01`/`CON-0183`.

**Negative:**
- Changing a clinical threshold requires a code change (edit YAML → commit → CI → deploy). This is slower than a database UPDATE — by design, for patient safety, but it removes the ability to hotfix a threshold in under 5 minutes. Mitigated by the `threshold_config` escape valve for operational tuning (score→severity band mapping), which is runtime-mutable with INV-1 audit.
- Content hashing requires YAML canonicalization in the build step. A whitespace-only change to a definition file that changes the canonicalized AST (e.g., reordering keys) produces a new content hash even though the clinical meaning is identical. Mitigated by the CONTRACTS schema enforcing a canonical key order and the build step normalizing the AST before hashing.
- No per-evaluation input snapshot means that reproducing "what inputs did the engine see at time T" requires joining `vital_sign`/`lab_result` by timestamp — an extra query for audit/analytics, but one that the Gold `fact_*` tables already support.

**Risks and Mitigations:**
- **Risk:** Content hashing produces different hashes on different build machines due to OS-level YAML library differences. **Mitigation:** The build step runs in a pinned Docker image with a locked YAML library version; the hash is computed over the parsed, normalized Python dict (using `json.dumps(sort_keys=True)` on the canonicalized AST), not raw file bytes.
- **Risk:** A threshold change that passes CI but has an unintended clinical effect (e.g., widening a band edge moves 15% of patients from watch to normal) is not caught by the build-time gates — the gates validate logical correctness (no gaps, no overlaps, no dead criteria), not clinical appropriateness. **Mitigation:** This is inherent to any threshold change, regardless of storage format. The definition's `test_vectors` field (≥3 per definition, ≥1 boundary) provides regression coverage for known clinical scenarios. The `ppv_budget` field gates false-positive volume at the source. A clinical review process (outside the engineering pipeline) is the appropriate gate for threshold appropriateness — the build-time gates ensure the threshold is *evaluable*, not that it is *correct*.
- **Risk:** `encounter_id` is unreliable from the source system for some tenants, causing `NOT NULL` constraint violations and blocking evaluation. **Mitigation:** The `patient_cache` sync from AMH Gold is the single point of encounter resolution. If `encounter_id` is missing, the patient is flagged as `stale_data` on the bed board (staleness watchdog, `alert-engine.md` §7.2) and alerts are suppressed with a data-quality reason — not a constraint violation. The `NOT NULL` contract is enforced at the application layer with a graceful degradation path, not at the database constraint level (the column allows NULL but the application never writes NULL — it writes a sentinel `UNKNOWN_ENC` and raises a data-quality operational alert).

## References

- `docs/plan/architecture/data-model.md` — v2 operational data model (Phase-1 baseline + Phase-2 deltas)
- `docs/plan/architecture/alert-engine.md` — v2 Alert Engine: definition schema (§2), lifecycle (§9), threshold-config resolution (§6), invariants (§4/§10)
- `docs/architecture/adr/ADR-001-amh-data-platform-consumer.md` — ADR-001: AMH Gold consumer, MPI identity, Gold write-back
- `docs/adr/0020-trilhas-engine-architecture.md` — ADR 0020: declarative rule engine decision (build-time gates, dual-runner)
- `docs/rules/care-pathway/RULE-TRILHAS-ENGINE-012-atualizartrilhasv3-v3-care-pathway-bootstrap-and-bed-re-link.md` — AMBIGUOUS per-encounter vs per-patient-lifetime scoping (ESC-AMBIGUOUS-308)
- `docs/rules/care-pathway/RULE-TRILHAS-ENGINE-018-care-pathway-type-enumeration-assistidochoices-vs-observacao.md` — 12-slug enumeration with drifted labels (ADOPT-CORRECTED)
- `docs/plan/_work/dispositions/trilhas-engine.yaml` — detailed rule dispositions with justifications and evidence
- `docs/plan/architecture/adr/ADR-005-realtime-channel-consolidation.md` — realtime architecture consolidation
