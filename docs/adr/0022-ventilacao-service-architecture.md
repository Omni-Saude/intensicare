# 0022. Ventilação service architecture: merge vs separate vs shared library

Status: accepted
Date: 2026-07-07
Depends on: ADR-001 (AMH Data Platform consumer), ADR 0017 (realtime consolidation), ADR 0020 (trilhas-engine architecture)

## Context and Problem Statement

IntensiCare's respiratory/ventilation domain (`domain_respiratory.py`, 1 035 lines) implements 11 alert evaluators covering ARDS staging (Berlin Definition), ventilatory deterioration trend analysis, patient-ventilator asynchrony detection, weaning/extubation readiness (two complementary bundles), prolonged intubation (COVID-adjusted), lung-protective ventilation (high Pplat / excessive tidal volume), FiO₂×PEEP mismatch (moderate and severe tiers), and pain assessment (NRS + BPS). It enforces mission-law FiO₂-as-fraction (CANON_PINS / SYS-01), computes S/F and P/F ratios, and implements a CRIT-never-auto-resolve guard. The domain is one of 14+ clinical domain modules in `src/intensicare/services/` alongside hemodynamics (`domain_hemo.py`, 931 lines), sepsis (`domain_sepsis.py`), AKI, electrolytes, and others — all loaded by the shared alert engine (`alert_engine.py`) and compiled by `alert_compiler.py`.

The legacy platform's ventilation rules were scattered across the `estabilidade` cluster (with unit confusion: FiO₂ percent-vs-fraction, lactate mg/dL-vs-mmol/L) and lacked a dedicated respiratory domain. The v2 rebuild correctly isolates ventilation into one module, but the architecture of *how* that module integrates with the broader platform — as a merged function inside the monolithic alert engine, as a separately deployable microservice, or as an independently versioned shared library — has not been decided.

The question is not whether ventilation logic should exist (it does, and is clinically ratified), but **how it should be packaged, deployed, and versioned** relative to the other 13+ clinical domains, the alert compiler, the correlation engine, and the two evaluation runners (NRT and micro-batch).

### Decision Drivers

- **ADR-001 / CON-0001:** no own ingestion; clinical reads from AMH Gold via Athena only. Operational vitals (SpO₂, FiO₂ from ventilator/monitor) arrive via the operational-ingress path (RAT-INGRESS-01).
- **VIS-4.2-03:** respiratory domain operates hybrid/NRT — SpO₂/FiO₂ ratio is continuous-monitor-driven (NRT), PaO₂/PaCO₂ ABG is micro-batch (Gold-via-Athena).
- **INV-3:** every alert must stamp the exact `definition_version` that fired it. Changing a ventilation threshold must mint a new version independently of other domains.
- **CON-SEED-12 / SYS-01:** FiO₂-as-fraction enforcement is mission law; the computation boundary must reject percent inputs at build time. This logic must be shared (ventilation, hemodynamics, and sepsis all consume FiO₂).
- **VIS-4-03 correlation #2:** "SDRA + choque" — the correlation engine consumes both `respiratory.ards_severity` and `hemodynamics.shock.refractory`. The two domains must emit events on a shared message bus or event store.
- **VIS-C-09:** sub-30s latency for critical alerts on the NRT path. Service-boundary overhead (serialization, network hop) matters.
- **Deployment independence:** ventilation rules evolve at a different cadence than, say, electrolyte or delirium rules. A ventilation-only threshold change should not force re-deployment of the entire clinical stack.

## Considered Options

### Option 1: Merge — all domains in one monolithic alert-engine process

Keep the current architecture: `domain_respiratory.py` (and `domain_hemo.py`, `domain_sepsis.py`, etc.) are Python modules loaded into the same Python process by the shared `alert_engine.py`. The NRT runner and micro-batch runner import domain evaluators directly; the correlation engine reads in-process alert results. Versioning is at the alert-definition level (`_work/alerts/respiratory.yaml`), not the module level.

- **Pros:**
  - Zero inter-process overhead — function calls, not RPC. Critical for the sub-30s NRT latency budget (VIS-C-09).
  - Simplest operational surface: one deployable artifact, one health check, one scaling profile.
  - Shared utilities (`_ensure_fio2_fraction`, `_compute_sf_ratio`, `_band_severity`) are trivially shared as Python imports — no packaging/versioning overhead.
  - The alert compiler's build-time gates (unit-check, band-partition, facade==predicate) already operate across all domain YAML files in one CI pass. No cross-service coordination needed for a consistent build.
  - Proven: the current codebase already works this way; 14+ domain modules coexist without conflict.

- **Cons:**
  - A ventilation-only change (e.g., updating ARDS staging thresholds per a new guideline) requires full re-deployment of the entire clinical evaluation stack — all 14+ domains redeploy for one threshold tweak.
  - No blast-radius isolation: a memory leak or CPU spike in one domain's evaluator affects all others.
  - Independent versioning of domain logic is impossible at the deployable level — all domains share one artifact version, even though their clinical logic evolves independently.
  - The shared FiO₂-fraction utility is imported by at least three domains (respiratory, hemodynamics, sepsis); a breaking change to it forces coordinated changes across all consumers. Without explicit SemVer contracts on internal utilities, this is a fragile dependency.

### Option 2: Separate microservice per clinical domain

Each clinical domain (ventilation, hemodynamics, sepsis, AKI, etc.) becomes an independently deployable microservice with its own API, data access, scaling, and versioning. Ventilation runs as `ventilacao-service`, exposing a gRPC or HTTP endpoint that accepts clinical inputs and returns evaluated alerts. The alert engine becomes an orchestrator that fans out to domain services.

- **Pros:**
  - True deployment independence: a ventilation threshold change deploys only `ventilacao-service`; other domains are untouched.
  - Blast-radius isolation: a bug or resource exhaustion in ventilation does not affect sepsis or electrolyte evaluation.
  - Independent versioning: ventilation can ship `v3.1.0` with updated ARDS staging while hemodynamics stays at `v3.0.0`.
  - Domain teams can own their own codebase, CI/CD pipeline, and SLO — aligns with a team-topologies model if the clinical domains are staffed by separate squads.

- **Cons:**
  - **Latency:** every domain evaluation crosses a process boundary (serialization + network hop). The NRT runner must evaluate multiple domains per vital-sign event; 7 domain calls × (serialize + RTT) can consume a material fraction of the <30s budget. gRPC on localhost is fast (~100 µs) but not zero — and the complexity of managing 7+ service connections is real.
  - **Cross-cutting shared logic:** `_ensure_fio2_fraction()` is needed by respiratory, hemodynamics, and sepsis. In a microservice world, it must be either duplicated, published as a shared library (re-introducing the versioning problem), or called as yet another service.
  - **Correlation engine cost:** the correlation engine (VIS-4-03) consumes events from multiple domains — with separate services, it must subscribe to 7+ event streams or poll 7+ APIs, adding latency and coordination complexity.
  - **Operational overhead:** 7+ services × (deployment, health checks, scaling, logging, tracing, circuit breakers, retries) — a substantial operational burden for a platform whose clinical evaluation core is ~10 KLoC of Python.
  - **Testing complexity:** cross-domain integration tests (e.g., "sepsis shock detected → lactate clearance evaluated by hemodynamics") require orchestrating multiple service instances.
  - Not justified by current team structure: the clinical evaluation logic is maintained by a single clinical-engineering team, not 7+ independent squads.

### Option 3: Shared library — domain modules as independently versioned Python packages

Extract each clinical domain into an independently versioned Python package (e.g., `intensicare-ventilacao`, `intensicare-hemodinamica`) published to a private PyPI repository. The alert engine declares them as dependencies with pinned version ranges. Shared utilities (FiO₂ fraction, band-to-severity mapping, unit normalizers) live in `intensicare-core`. The monolith deployment persists, but domain logic is versioned and released independently.

- **Pros:**
  - **Independent versioning without service-boundary overhead.** A ventilation threshold change ships as `intensicare-ventilacao==3.1.0`; the alert engine picks it up on next deployment (or hot-reload if designed for it). Other domains stay on their current versions.
  - **No latency penalty:** all domain code runs in-process — function calls, not RPC.
  - **Shared utilities have a home:** `intensicare-core` provides FiO₂ enforcement, unit conversion, severity mappings, and the alert-result data classes with explicit SemVer. Breaking changes are versioned; consumers pin compatible ranges.
  - **CI can gate cross-package compatibility:** the alert compiler validates all alert-definition YAML files against the installed package versions; a ventilation YAML that references a threshold not present in the pinned `intensicare-core` version fails at build time.
  - **Operational simplicity preserved:** one deployable artifact (the alert engine + its pinned package set). One health check, one scaling profile.
  - **Aligns with the existing codebase pattern:** domain modules are already cleanly separated by file (`domain_respiratory.py`, `domain_hemo.py`); extracting them to packages formalizes the existing boundary.

- **Cons:**
  - **Packaging overhead:** 14+ Python packages to maintain, each with its own `pyproject.toml`, CI publish step, and version history. Non-trivial for a small team.
  - **No blast-radius isolation:** a bug in `intensicare-ventilacao==3.1.0` still crashes the entire alert-engine process — all domains go down together.
  - **Dependency hell risk:** if `intensicare-hemodinamica` pins `intensicare-core>=2.0` and `intensicare-ventilacao` pins `intensicare-core<2.0`, the alert engine cannot satisfy both. Requires disciplined SemVer and a compatibility matrix.
  - **Hot-reload complexity:** if the engine supports loading new package versions without restart, it introduces state-migration complexity (in-flight evaluations, active alert lifecycles). A restart-based model is simpler but means ventilation updates still restart the whole engine.
  - **Over-engineering signal:** 14 packages for ~10 KLoC of Python is a high ceremony-to-code ratio. The current single-module-per-file structure is already well-organized; formal packages may be solving a scaling problem the team does not yet have.

### Option 4: Domain modules with SemVer contracts, monorepo packaging (recommended)

Keep the monorepo + single deployable architecture (Option 1's simplicity) but formalize domain boundaries with explicit SemVer contracts and a package-like structure *within* the monorepo. Each domain module exposes a public API (`__all__`), carries a `__version__`, and declares its dependencies on shared utilities via import — with a CI-enforced compatibility check. The alert compiler validates that every `definition_version` in `_work/alerts/<domain>.yaml` is compatible with the domain module's version. FiO₂ fraction, unit normalization, and severity mappings live in `intensicare.core` as the shared foundation with its own SemVer.

- **Pros:**
  - Combines Option 1's operational simplicity (one deployable) with Option 3's versioning rigor (independent domain versions, explicit contracts).
  - No network latency, no multi-service orchestration, no packaging overhead — all code runs in-process.
  - CI-enforced compatibility: a ventilation YAML update that requires a `domain_respiratory.py` change is caught at build time if the versions don't match.
  - Shared utilities (`intensicare.core`) have explicit SemVer — a breaking FiO₂ change forces a major version bump and coordinated consumer updates, caught at CI.
  - The monorepo structure already exists; this option formalizes it without restructuring.
  - Gradual migration path: start with SemVer contracts on today's modules; extract to separate packages (Option 3) later if independent deployment becomes necessary.

- **Cons:**
  - Still no blast-radius isolation — a bug in one domain crashes the whole engine.
  - Still one deployment artifact — a ventilation-only change still triggers full redeployment.
  - The CI compatibility check is custom infrastructure that must be built and maintained.
  - The "package-like structure within a monorepo" is an unusual pattern that may confuse new contributors expecting either true monolith or true packages.

## Decision Outcome

Recommend **Option 4** (domain modules with SemVer contracts, monorepo packaging) as the immediate architecture, with an explicit migration path to **Option 3** (shared library packages) if and when deployment independence or team separation justifies the packaging overhead.

The ventilation domain's clinical logic is mature (11 ratified alert evaluators, ARDS staging per Berlin Definition, FiO₂-as-fraction enforcement) and will evolve at a guideline-driven cadence (e.g., a new ARDS definition, updated weaning criteria). Independent versioning of the ventilation module — without forcing re-deployment of AKI, electrolytes, or delirium — is the primary architectural need. But the team is small, the total codebase is ~10 KLoC, the NRT latency budget is tight (<30s), and the correlation engine depends on in-process event consumption. A full microservice decomposition (Option 2) trades one solved problem (fast in-process evaluation) for seven new ones (service orchestration, network latency, distributed tracing, cross-service testing). A shared-library extraction (Option 3) solves versioning but adds packaging overhead disproportionate to the current scale.

Option 4 captures the versioning benefit while preserving the operational simplicity the team already has. It is reversible: if the team grows to separate domain squads, or if a specific domain (e.g., ventilation with its NRT ventilator-stream dependency) needs independent scaling, the SemVer-bounded module is already structured for extraction into a package or service.

### Consequences

**Good:**

- Ventilation thresholds can evolve independently — update `domain_respiratory.py`'s version, update `_work/alerts/respiratory.yaml`'s `definition_version`, and CI validates compatibility. No other domain is affected.
- Shared FiO₂ fraction enforcement (`intensicare.core.unit_guards.ensure_fio2_fraction`) has explicit SemVer — a breaking change forces a coordinated major-version bump, caught at build time.
- No latency penalty: all 11 ventilation evaluators run as direct function calls inside the NRT/micro-batch runner process.
- One deployable, one health check, one scaling profile — operational simplicity preserved.
- Correlation engine consumes in-process events — no cross-service orchestration.

**Bad:**

- A bug in `domain_respiratory.py` still crashes the entire alert engine; no blast-radius isolation.
- A ventilation-only change still triggers full engine redeployment (though only the ventilation module's version changes — the deployable version reflects the max of all domain versions).
- The CI compatibility check (domain module version ↔ alert-definition version) is custom infrastructure with ongoing maintenance cost.
- The "SemVer contracts in a monorepo" pattern may be unfamiliar; requires documentation and team discipline.

### Migration path

1. **Immediate (this sprint):** add `__version__ = "3.0.0"` to `domain_respiratory.py` and all other domain modules. Add a CI check that every `_work/alerts/<domain>.yaml` alert's `definition_version` prefix matches the domain module's major version. Document the contract: a YAML threshold change that needs a code change must bump both.
2. **Short-term (next sprint):** extract shared utilities (`_ensure_fio2_fraction`, `_compute_sf_ratio`, `_compute_pf_ratio`, `_band_severity`, the `RespiratoryAlertResult` dataclass) into `intensicare/core/respiratory_utils.py` with its own `__version__`. All three consuming domains (respiratory, hemodynamics, sepsis) import from this single source.
3. **Medium-term (if team grows):** promote `intensicare/core/` to a standalone `intensicare-core` package (Option 3). Extract the highest-churn domain first (likely ventilation or sepsis) into `intensicare-ventilacao`. The SemVer contracts established in step 1 make this extraction mechanical.
4. **Long-term (if latency or scaling demands it):** promote the highest-load domain to a microservice (Option 2). The well-defined API surface from steps 1-3 makes the gRPC boundary straightforward.
