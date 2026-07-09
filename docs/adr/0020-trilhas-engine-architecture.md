# 0020. trilhas-engine architecture: state machine vs declarative rule engine

**Status: IMPLEMENTED** (2026-07-09)

Delivered across 4 milestones:

- **M1: Schema + CI Gates** — ``pathway.schema.json``, Gates A/B/C in ``validate_alerts.py``
- **M2: PredicateCompiler + YAML migration** — 4 pathway YAML definitions under ``_work/alerts/pathways/`` (ventilacao, sepse, desmame, nutricao)
- **M3: Stateless TrilhasEngine + Evaluator** — ``trilhas_engine.py``, ``trilhas_evaluator.py``, ``trilhas_compiler.py``
- **M4: API adapter + legacy deprecation** — ``pathways.py`` wired to new engine, ``trilhas_state.py`` deprecated, ``domain_trilhas_engine.py`` re-exports both

---
Date: 2026-07-07
Depends on: ADR-001 (AMH Data Platform consumer), ADR 0017 (realtime consolidation)
Audit source: trilhas-engine cluster — 18 legacy rules extracted, catalogued, and dispositioned (2026-07-03)

## Context and Problem Statement

The legacy IntensiCare platform runs a Django-based **trilhas-engine** — a care-pathway composition and evaluation engine that governs which clinical surveillance domains are active for a given bed, how pathway items (criteria) are evaluated, and how results surface to the frontend. The engine spans 18 audited rules across five categories: care-pathway composition (9 rules), alert-threshold display (2), triage-eligibility (3), scheduling-operational (1), drug-dosing (1), and one cross-cutting pathway-type enumeration. The audit dispositions the rules as follows: 5 **RETIRE** (no clinical content or pure legacy wiring), 5 **SUPERSEDE** (replaced by v2 Alert Engine mechanisms), 6 **ADAPT** (sound clinical intent, reimplement on new substrate), 1 **ADOPT-CORRECTED** (the 12-slug pathway-type vocabulary), and 1 **RATIFIED** with an AMBIGUOUS-band escalation.

The rules reveal the engine's architectural nature:

- **Pathway composition is static model lists, keyed by bed type** (`automatica` vs `homecare`), hard-coded as Django model-class arrays (`RULE-TRILHAS-ENGINE-001`, `002`). Bed-type-based model selection is legacy wiring tied to the retired Tasy ETL stack (`RULE-TRILHAS-ENGINE-009`).
- **Criterion evaluation is imperative Python** — each pathway model implements `calcular_criterio_N()` methods, with systemic defects around dead/unwired criteria (`SYS-08`), band-edge gaps (`SYS-06/07`), and facade/predicate drift (`SYS-04`).
- **Interactive protocols** (Sepse, Profilaxia) are gated by exact string name matching in the frontend, with a divergent API contract (boolean `true` vs string `"false"`) and a known routing bug (`RULE-TRILHAS-ENGINE-005`, `014`, `015`).
- **Lifecycle/state management** is implicit — the engine has no first-class alert lifecycle; "assistido" (attended) is a toggle flag on a pathway row, and ownership-gated un-assist is enforced ad-hoc in React (`RULE-TRILHAS-ENGINE-007`).

ADR-001 mandates that v2 read clinical data **only from AMH Gold via Athena** — the legacy's Tasy-direct ETL path is retired. The v2 vision defines a domain-based monitoring architecture: 7 clinical domains (early-warning, sepsis, AKI, respiratory, hemodynamic, electrolytes, delirium) evaluated by a declarative Alert Engine with explicit lifecycle, versioning, and audit. The question this ADR resolves is: **what architecture replaces the trilhas-engine's pathway-composition, criterion-evaluation, and lifecycle-management responsibilities?**

### Decision Drivers

- **ADR001-C-01**: no own ingestion; clinical reads from AMH Gold via Athena only.
- **VIS-4-02**: the v2 Alert Engine evaluates 7 clinical domains, each with declarative alert definitions.
- **VIS-5.2**: a Correlation Engine for cross-domain aggregation (sepsis+AKI, respiratory+hemodynamic, drug+electrolyte).
- **CON-SEED-11**: canonical four-band severity scale (normal/watch/urgent/critical), triple-encoded.
- **INV-1**: every state transition must write an immutable audit trail.
- **INV-3**: every alert must stamp the exact `definition_version` that fired it.
- The legacy's systemic defect classes (SYS-04 through SYS-08 — facade drift, AND/OR collapse, chained-comparison misparse, band-edge gaps, dead criteria) must be made *un-shippable by construction*, not caught in code review.
- 6 rules have clinical intent worth preserving (ADAPT); their mechanisms must be reimplemented on the v2 Alert Engine substrate, not ported as Django code.

## Considered Options

### Option 1: State machine engine (port the trilhas-engine pattern, modernized)

A domain-driven state machine per clinical domain. Each patient occupies a state per domain (e.g., `sepsis.screening → sepsis.identified → sepsis.shock → sepsis.resolved`), and transitions are triggered by clinical events (lab result, vital sign crossing a threshold). Pathway items are actions attached to states. The interactive protocol workflow (accept/refuse) becomes state transitions. The 12-slug pathway-type vocabulary becomes the domain enumeration.

- **Pros:**
  - Naturally models the clinical progression narrative (sepsis stages, AKI KDIGO stages).
  - The legacy's "pathway items in order" and interactive-protocol accept/refuse map cleanly onto state transitions.
  - Explicit state makes it obvious what "phase" of care a patient is in — useful for the bed-board and handoff.
- **Cons:**
  - State explosion: 7 domains × N states each × per-patient = large combinatorial space. Cross-domain correlations (sepsis+AKI) require composing two state machines — non-trivial.
  - State transitions are imperative code, re-introducing the legacy's systemic defect surface (dead transitions, unreachable states, off-by-one guards) unless the state machine itself is declarative — a declarative state machine is isomorphic to a rule engine.
  - The legacy's criterion-evaluation defects (SYS-04/06/07/08) came from imperative stateful code; a state machine implementation in Python carries the same risk unless every transition guard is declarative and build-time checked.
  - Does not naturally model concurrent, independent criteria firing within one domain (e.g., KDIGO creatinine-based staging AND urine-output-based staging firing simultaneously for the same patient).

### Option 2: Declarative rule engine (alert-definition-driven, stateless evaluation)

Every clinical domain is a set of declarative alert definitions (`_work/alerts/<domain>.yaml`). Each definition declares its inputs, trigger predicate (a composable boolean expression), severity band, evaluation mode (micro-batch / near-real-time / hybrid), and suppression rules. The engine evaluates all definitions for a patient on each input event or poll tick; each firing creates an alert instance with a full lifecycle state machine (raised → acknowledged → acting → resolved/escalated/expired). There is no persistent "pathway" state between evaluations — the engine is stateless at the evaluation layer; state lives only on the alert instances.

- **Pros:**
  - **Build-time defect elimination.** Every input.unit must resolve in the canonical units registry (check_units.py strict). Every criterion must be reachable and exercised by a can-fire test vector (Gate A). Every graded band must partition its input domain with no gaps, no overlaps, no unreachable bands, and boundary test vectors per edge (Gate B). Rendered rationale is generated from the same AST the engine evaluates (Gate C, facade==predicate). The SYS-04/06/07/08 defect classes become CI build failures — un-shippable by construction.
  - **Versioning trivial.** Every definition change mints a new `definition_version` + content hash. The engine stamps the firing version on every alert. Historical alerts are exactly reproducible for the 7-year retention window (INV-3).
  - **Concurrent, independent criteria naturally supported.** Multiple alert definitions in the same domain can fire independently on the same patient — no state-machine concurrency problem.
  - **Cross-domain correlation decoupled.** A separate Correlation Engine consumes persisted domain alerts and applies correlation rules (sepsis+AKI, respiratory+hemodynamic) without entangling the domain evaluators.
  - **ADR-001 alignment.** The engine is a consumer: micro-batch runner polls Athena; NRT runner processes operational vitals. No own ingestion, no Tasy coupling.
  - Maps cleanly onto the 6 ADAPT rules: ownership-gated acknowledgment (RULE-007) → alert lifecycle with `acknowledged_by`; overdue-item flag (RULE-008) → `ack_sla` breach timer; admission-triggered domain enablement (RULE-011) → Correlation Engine admission hook; bed re-link (RULE-012) → `patient_cache` bed re-association triggers re-evaluation; refuse justification (RULE-015) → `resolution = false_positive` with required `justification` field; recommendation/intervention rendering (RULE-016) → alert definition's `evidence` + `recommendations` fields in the CONTRACTS schema.
- **Cons:**
  - No first-class "patient is in sepsis screening phase" concept — the "phase" must be inferred from which alert definitions are currently firing. This is addressable via the Correlation Engine's domain-state derivation but adds a layer.
  - The legacy's "pathway items in order" (a sequential checklist within a pathway) does not map directly onto independent alert definitions; the v2 would need an explicit ordered-bundle construct if that UX is preserved.
  - Stateless evaluation means every poll re-evaluates all definitions for all active patients; the cost is bounded by incremental high-watermark polling and definition-level dedup, but it is a different cost profile than a state machine that only evaluates transitions from the current state.

### Option 3: Workflow engine (BPMN/sequential process per pathway)

Each care pathway is modeled as a formal workflow (e.g., BPMN or a workflow DSL) with sequential steps, branching, and human tasks. The interactive protocol workflow (accept → execute bundle items → complete) is the native paradigm. The engine instantiates a workflow instance per patient per pathway and advances it as clinical data arrives.

- **Pros:**
  - The sequential-checklist UX (pathway items in order) maps perfectly onto workflow steps.
  - Human tasks (acknowledge alert, execute intervention, document outcome) are first-class workflow constructs with built-in timers, escalations, and SLAs.
  - Workflow engines (Camunda, Temporal, AWS Step Functions) provide operational tooling (retry, visibility, audit) out of the box.
- **Cons:**
  - **Wrong evaluation paradigm for clinical surveillance.** Most clinical alerts are *stateless threshold crossings*, not sequential processes. A K⁺ > 6.5 critical alert should fire immediately regardless of what "step" the patient is in — a workflow that gates critical alerts behind step progression is a patient-safety risk.
  - The legacy's 9 automatic pathway models are simultaneous, independent surveillance dimensions — not a single sequential process. Modeling them as parallel workflow branches is heavyweight and obscures the clinical reality that they are orthogonal monitors.
  - BPMN/workflow DSLs are designed for business processes with human actors and days-to-weeks timelines — the sub-second latency requirement (p95 <30s end-to-end, <5s for critical delivery) is mismatched with workflow engine overhead.
  - Vendor/tooling lock-in: a workflow engine choice ties the clinical evaluation core to a specific runtime (Camunda, Temporal) with its own scaling, licensing, and operability profile — the alert-definition approach is runtime-agnostic (the definitions compile to ARQ jobs + Python predicates).
  - The legacy's SYS-04/06/07/08 defect classes (facade drift, band gaps, dead criteria) are not addressed by a workflow engine — they are defects in the *predicate logic*, not in the orchestration layer.

### Option 4: Hybrid — declarative rule engine for threshold evaluation + lightweight state machine for pathway phase tracking

Use Option 2's declarative alert-definition engine for all clinical threshold evaluation and alert firing — the life-safety-critical path. Layer a lightweight, read-only "domain phase" derivation on top: the Correlation Engine, after evaluating all domain alerts for a patient, derives a `domain_state` (e.g., `sepsis: screening | identified | shock | resolved`) from the *pattern of currently firing alert definitions*, purely as a derived view for the bed-board and clinical handoff. No alert is gated on phase; phase never suppresses a critical alert.

- **Pros:**
  - Combines the safety of Option 2 (critical alerts fire unconditionally; build-time defect gates) with the clinical-narrative value of Option 1 (visible "phase" for handoff and bed-board).
  - Phase derivation is read-only and decoupled — a bug in phase derivation can never suppress or delay a clinical alert, because phase is downstream of alert evaluation.
  - Reuses the same alert-definition catalog: no second set of rules to maintain.
- **Cons:**
  - Adds a derivation layer that must be designed, tested, and maintained — more surface area than Option 2 alone.
  - The "phase" is always an approximation (inferred from alert patterns, not a clinician-declared state) — must be clearly labeled as derived, not authoritative.
  - Still does not provide the legacy's sequential-checklist UX; that would require an additional ordered-bundle construct.

## Decision Outcome

Chosen option: **Option 2 (Declarative rule engine)**, with the explicit acknowledgment that Option 4's phase derivation is a natural extension within the Correlation Engine's scope (`VIS-5.2-04`) and should be evaluated as a post-MVP enhancement — not as part of the core evaluation architecture.

**Justification:**

1. **Patient safety is the overriding driver.** The legacy's systemic defect classes (SYS-04 through SYS-08) are defects in predicate logic that can suppress or misclassify clinical alerts. The declarative approach with build-time CI gates (unit resolution, criterion reachability, band-partition exhaustiveness, facade==predicate) makes these defect classes *un-shippable by construction*. No other option provides this guarantee — a state machine or workflow engine would still evaluate predicates in imperative code, carrying the same defect surface the audit flagged.

2. **ADR-001 compliance is structural, not bolted-on.** The micro-batch/NRT dual-runner architecture (§1 of `alert-engine.md`) is the direct realization of ADR-001's "consumer, not ingester" mandate: the micro-batch runner polls AMH Gold via Athena (the sole analytical source), while the NRT runner processes operational vitals (the operational-telemetry carve-out, RAT-INGRESS-01). A workflow engine or state machine would still need these two data paths — but would embed them inside a heavier runtime with no offsetting clinical benefit.

3. **The 6 ADAPT rules map cleanly onto declarative constructs** without losing clinical intent: ownership-gated acknowledgment → `acknowledged_by` + ownership check on reversal; overdue-item flag → `ack_sla` timer breach; admission-triggered enablement → Correlation Engine admission hook; recommendation/intervention rendering → alert-definition `evidence`/`recommendations` fields; refuse justification → `resolution.justification`; bed re-link → `patient_cache` re-association triggers re-evaluation. The 5 RETIRE rules (display-only styling, bed-type UI gates, payload variant wiring) have no clinical content to port. The 5 SUPERSEDE rules (v2/v3 model composition, homecare pathway selection, eligibility gating, accept-protocol workflow) are replaced by the Alert Engine's domain-based routing and generic acknowledgment workflow.

4. **The one ADOPT-CORRECTED rule** — the 12-slug pathway-type controlled vocabulary — is consumed directly as the initial domain enumeration for the Correlation Engine's phase derivation, corrected to a single canonical source with accented labels.

5. **Versioning and audit are first-class**, not retrofitted. Every alert definition is versioned (content hash + version number); every firing stamps the version; superseded versions are retained for the 7-year window. Every alert lifecycle transition writes an immutable `audit_trail` row (INV-1). A state machine or workflow engine *can* do this, but the declarative schema makes it the natural persistence shape rather than an additional layer.

### Consequences

**Positive:**
- The four systemic defect classes that produced the P0-10 (downgrade-overwrite), SYS-04 (facade drift), SYS-06 (chained-comparison misparse), SYS-07 (band-edge gaps), and SYS-08 (dead criteria) are prevented at build time, not caught in code review.
- The engine is runtime-agnostic: alert definitions are YAML/JSON artifacts that compile to ARQ jobs + Python predicates. The team can change the job queue (ARQ → Celery → Temporal), the database (PostgreSQL → any SQL), or the deployment model without touching a single alert definition.
- Cross-domain correlation (sepsis+AKI, respiratory+hemodynamic) is a clean second pass over persisted alerts — no entanglement with the per-domain evaluators.
- The 18-rule audit disposition is directly traceable to v2 constructs: every ADAPT rule has a named target (`clinical/domains/sepsis.md#protocol-response-workflow`, etc.), and every RETIRE/SUPERSEDE rule has a recorded justification for why no successor artifact is needed.

**Negative:**
- The legacy's "pathway items in order" sequential UX does not have a direct v2 equivalent. The v2 alert model presents independent, concurrent alerts; a sequential-checklist construct (ordered bundle items within a pathway) would require additional schema and UX design if the clinical need persists.
- Stateless re-evaluation means every patient is re-evaluated on every poll tick. The cost is bounded by high-watermark incremental polling and definition-level dedup, but the per-patient cost is higher than a state machine that only evaluates transitions from the current state. Mitigated by: (a) the micro-batch runner's incremental poll only touches patients with new data since the last poll; (b) the NRT runner evaluates only the one patient whose vital sign just arrived; (c) definition-level dedup prevents redundant persistence.
- The "phase" inference gap (knowing which sepsis stage a patient is in, as opposed to which alerts are firing) is real and should be tracked as a Correlation Engine post-MVP enhancement (Option 4).

**Risks and Mitigations:**
- **Risk:** The team builds imperative evaluation code inside declarative-looking wrappers, reproducing the SYS-04 facade-drift defect in a new syntax. **Mitigation:** Gate C (facade==predicate) in CI strict mode — rendered rationale is generated from the AST, not hand-written. A hand-edited threshold in the rendered payload that diverges from the AST is a build failure.
- **Risk:** The alert-definition catalog grows faster than the build-time gates can validate, and the CI step becomes a bottleneck. **Mitigation:** The gates run per-definition and are trivially parallelizable. The initial catalog is 9 domains with ~30 definitions total; the gate runtime is dominated by I/O (loading YAML), not computation.
- **Risk:** The 12-slug vocabulary adoption creates a dependency on the legacy's domain taxonomy that might not match the v2's 7-domain clinical decomposition. **Mitigation:** The 12 slugs are adopted as a *starting controlled vocabulary*, not a final domain model. The v2's 7 domains (early-warning, sepsis, AKI, respiratory, hemodynamic, electrolytes, delirium) map onto a superset/subset of the legacy's 12, and the vocabulary is explicitly declared as the enumeration for the Correlation Engine's domain-state derivation — not as the alert-definition namespace.

## References

- `docs/rules/extraction/phase2/catalog/trilhas-engine.yaml` — catalog of 18 legacy rules with dispositions
- `docs/plan/_work/dispositions/trilhas-engine.yaml` — detailed disposition justifications and evidence
- `docs/plan/architecture/alert-engine.md` — v2 Alert Engine architecture (declarative schema, dual-runner, build-time gates, lifecycle, suppression)
- `docs/architecture/adr/ADR-001-amh-data-platform-consumer.md` — ADR-001: IntensiCare as AMH Data Platform consumer
- `docs/product/vision.md` — vision §4: 7 clinical domains and alert taxonomy
- `docs/rules/care-pathway/RULE-TRILHAS-ENGINE-018-care-pathway-type-enumeration-assistidochoices-vs-observacao.md` — the 12-slug pathway-type enumeration (ADOPT-CORRECTED)
- `docs/plan/architecture/adr/ADR-005-realtime-channel-consolidation.md` — realtime channel consolidation (ADR-0017 successor)
