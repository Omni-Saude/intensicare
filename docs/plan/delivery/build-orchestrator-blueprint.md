# Build-Orchestrator Blueprint — IntensiCare v2

**Owner:** build-blueprint author · **Status:** handover to the build orchestrator (human or agent) · **Authority precedence:** ADR-001 ≻ vision ≻ directive ≻ audit (`docs/plan/_work/schemas/CONTRACTS.md` §5).

This document is THE handover. It converts the ratified design corpus (`docs/plan/**`) into an executable operating guide: what the build orchestrator does first, who owns which file, which gate must be green before a phase advances, and how every decision already made is journaled so it is never re-derived. Read it top-to-bottom once, then work Section 3 as the backlog. Every load-bearing claim cites its source — a plan `file#section`, a `HANDOFF.yaml` id (`AUDIT-*`, `TECH-*`, `REG-*`, `CLIN-*`, `SEC-*`), a brief fact (`VIS-*`, `IMP-*`, `ADR001-*`, `DM-*`), a ledger constraint (`CON-*`), an invariant (`INV-1..6` / `REQ-INV-*`), a systemic-defect class (`SYS-*`), or a ratification id (`RAT-*`, `ASK-*`).

The design corpus is **CI-green on `main`** (lint, tests on Python 3.12/3.13, security scan; `HANDOFF.yaml` context) and PR #1 is merged (audit KB: 959 rules / 351 escalations / 18 ADRs). The v1 MVP backend runs and passes its own suite. This blueprint governs the v2 build **on top of** that baseline.

---

## 0. Mission + operating doctrine (for the build orchestrator)

**Mission.** Ship IntensiCare v2 — a SaMD Classe II ICU decision-support platform (`VIS-C-02`) that is a *consumer* of the AMH Data Platform (`ADR001-C-01`), computes early-warning + 7-domain alerts (`VIS-4-02`), and meets its SLOs (ingest→alert p95 < 30 s `VIS-C-09`; > 500 alerts/min `VIS-C-11`; 99.9% `VIS-C-10`) with the 6 pre-first-patient invariants proven (`IMP-C-01..06`).

**Operating doctrine — non-negotiable, mirrors `CONTRACTS.md`:**

1. **Verify-on-disk over agent claims.** An agent's receipt is a *claim*; the truth is the file on disk and the gate that re-counts it (`CONTRACTS.md` "gates verify your files on disk; an unverifiable claim equals no work"). The orchestrator merges nothing on a receipt alone — it runs the gate. *(Worked example this blueprint itself produced: the source directive stated "v1 has no frontend here"; on-disk inspection found a real Vite/React 19 SPA in `frontend/`. Section 1 records the corrected disposition. Trust the disk.)*
2. **Exclusive file ownership.** Each work order (WO) names the file(s) it may write; two WOs never write the same file concurrently. Cross-WO changes go through the owning WO, not around it. This is the build-side analogue of the CONTRACTS "write fence".
3. **Mechanical phase gates before phase transitions.** A phase closes only when its named CI gate is green (Section 7). Gates are scripts, not opinions — extend the `docs/plan/_work/scripts/check_*.py` pattern (draft/strict modes) into `scripts/` for code.
4. **Journaled decisions.** Every non-trivial build decision is appended to a build journal (`docs/plan/delivery/BUILD-JOURNAL.md`, orchestrator-owned) with its WO id, the spec clause that governed it, and the gate that proved it. Ratification-pending choices are journaled with their `RAT-*` id and the version flag guarding them (rule 7).
5. **Resume protocol.** On resume: (a) `git status` + last BUILD-JOURNAL entry establish where work stopped; (b) re-run the current phase gate to distinguish "claimed done" from "verified done"; (c) consult `HANDOFF.yaml` `blocked:` for any newly-unblocked item; (d) never trust an in-flight WO's partial state — re-run its acceptance gate from clean.
6. **Never port a RATIFY-pending default silently.** Any threshold/aggregation/behavior whose intent is ratification-gated (Section 4) ships **behind a version flag** (`algorithm_version` / `definition_version` bump), annotated `pending RAT-*` in code and journal, defaulting to the reference-anchored recommended default — never the legacy value, never unmarked (`CONTRACTS.md` disposition policy; `sepsis.yaml` header pattern).
7. **The plan is the contract.** `docs/plan/**` governs. Code that diverges from a spec is a bug in the code; a genuinely needed spec change is a **spec-change PR first, code second** (Section 6).

---

## 1. BUILD-ADR-001 — v1.0 MVP codebase disposition

**Decision (owner ack required at build kickoff — BUILD-ADR-001):** adopt **BROWNFIELD-CORE + GREENFIELD-SURFACES**. Keep and extend the v1 FastAPI backend skeleton; replace v1's ad-hoc alert generation with the new declarative engine; build all new subsystems (AMH integration, correlation, notification tiers, audit/pgcrypto, ARQ) greenfield; rebuild the frontend greenfield on the design-system stack.

**Why brownfield-core (rationale).** The v1 backend matches the plan's stack pins **exactly** — FastAPI + PostgreSQL 16/TimescaleDB 2.18 + Redis 7 + MLLP listener + the 4 cited scorers + JWT + `threshold_config` + WebSocket (`IMP-3.2-01..06`; verified in `src/intensicare/`). It is **CI-green** (`HANDOFF.yaml` context). The data-model and alert-engine specs were written **as evolutions of the v1 schema** — `data-model.md` §2 is literally titled a resolution that adopts the shipped `__tablename__ = "clinical_score"` and the already-present `algorithm_version` column; §3 is a *delta* table, not a rewrite. The MLLP listener is now **ADR-blessed operational ingress** (`_work/adrs/operational-vitals-ingress.md`, RAT-INGRESS-01), not a liability. Schema continuity + CI-green + exact pin-match make a rewrite pure risk with no upside.

**Alternative considered — full greenfield.** Rejected. It discards a green CI baseline and a 590-line battle-shaped MLLP parser (`mllp_listener.py`), forces re-derivation of the operational schema the specs already evolve, and multiplies integration risk — with zero schema or SLO benefit. ADR-001's own Alternativa-A rejection logic applies by analogy (rebuild cost 3–5× vs consume-and-extend, `ADR001-F-03`). Greenfield is retained **only** where v1 has no fit-for-purpose asset (new subsystems; the frontend, per below).

**Module-by-module disposition.** Posture ∈ {keep, extend, replace, reference-only}. "extend" = keep the file, add columns/behavior per the governing spec.

| v1 module (`src/intensicare/…`) | LoC | Posture | Governing spec | Acceptance gate |
|---|---|---|---|---|
| `main.py` (app factory, lifespan, `/health`) | 89 | **extend** | `observability-slo.md` §4.1; `system-architecture.md` §2 | `/api/v1/health` readiness (DB+Redis+ARQ+Athena) replaces static stub — `REQ-INV-5`; lifespan opens real pools (v1 has `TODO` stubs) |
| `config.py` | 119 | **extend** | `system-architecture.md` §8; `security-lgpd.md` §4.2 | Adds Athena/Glue, per-tenant KMS DEK, OTEL endpoint, ARQ settings; no secret literals (`security-lgpd.md` §5.1) |
| `core/database.py` (async session) | 68 | **keep** | `data-model.md` >Platform reality | Unchanged pattern; new tables register against same `Base` |
| `core/redis.py` | 37 | **extend** | `alert-engine.md` §7.1; `HANDOFF.yaml` TECH-004 | ARQ queue + `IdempotencyStore` moved memory→Redis (TECH-004) |
| `core/websocket.py` | 134 | **extend** | `alert-engine.md` §7.1 (`CON-0045/0046/0053`) | Single realtime channel — bed-board state + notifications share one push class; thin idempotent patch on `dedup_key` |
| `mllp_listener.py` (HL7 MLLP, MSH-10 idempotency) | 590 | **keep** | `_work/adrs/operational-vitals-ingress.md` (RAT-INGRESS-01); `alert-engine.md` §4.1 | ADR-blessed operational vitals ingress; `INV-2` replay test (`DRILL-DUPLICATE-REPLAY`); SYS-09/10 edge-parse hardening on the normalize path |
| `fhir/client.py` | 303 | **extend** | `ADR001-C-05`; `system-architecture.md` §4.3 | Read-only HAPI enrichment, keyed `mpi_id`, ABAC-scoped; never a scoring source; no own FHIR server |
| `services/mews.py` | 251 | **extend + ADOPT-CORRECTED** | `HANDOFF.yaml` AUDIT-001; `RATIFICATION.md`; scorers brief `MEWS-*` | Correct 4 inflated bands to Subbe 2001; bump `MEWS-v1.0.1`; new vectors; **behind version flag, pending clinical sign-off** (Section 4) |
| `services/news2.py` | 256 | **extend + ADOPT-CORRECTED** | `HANDOFF.yaml` AUDIT-002; scorers brief `NEWS2-*` | Fix Scale-2 SpO₂ bands (RCP 2017) + integrate `supplemental_o2`; bump version; new vectors; **pending sign-off** |
| `services/sofa.py` | 470 | **extend** | `HANDOFF.yaml` AUDIT-003; `RAT-SEPSE-*` (vasopressor unit) | Unify dual live/replay risk-classification into single source of truth; `SOFA-C-03` renal = max(cr,uo); cardiovascular rate mcg/kg/min pending `ASK-5`/`RAT-CLINICAL-SCORING-*` |
| `services/qsofa.py` | 164 | **keep** | scorers brief `qSOFA-*` | Property tests `qSOFA-4-03..08`; composite = Σ criteria |
| `services/alert_engine.py` (ad-hoc threshold→alert) | 127 | **replace → reference-only** | `alert-engine.md` (whole) | New declarative engine (WO-008). v1 imperative threshold-check retained read-only as reference; deleted from the import graph once WO-008 passes L1 vectors |
| `services/vitals.py` | 439 | **extend** | `alert-engine.md` §2.2 (SYS-09/10); units registry | Canonical-unit normalize at edge; locale decimal parse (`SYS-09`); tz-explicit windows (`SYS-10`) |
| `services/patients.py` | 162 | **extend** | `system-architecture.md` §4.2 (`ADR001-C-02`) | Becomes MPI identity resolver + `patient_cache` sync; mints no ids |
| `services/dashboard.py` | 303 | **extend** | `design/screens/command-center.md`; `alert-engine.md` §7.1 | Bed-board via the single push channel; staleness badge (`system-architecture.md` §5.3) |
| `api/v1/alerts.py` | 157 | **extend** | `HANDOFF.yaml` AUDIT-007/008; `api/openapi.yaml` | Response `{alerts,total}` not bare array (AUDIT-007); severity enum → `normal/watch/urgent/critical` (AUDIT-008); lifecycle `acting`/`escalated` |
| `api/{patients,vitals,thresholds}.py`, `api/v1/{auth,dashboard}.py` | ~460 | **extend** | `api/openapi.yaml`; `alert-engine.md` §6 | `threshold_config` 3-scope (`bed_id`); every mutation → `audit_trail` (`INV-1`); contract tests from `openapi.yaml` |
| `auth/` package (JWT, deps) | 136 | **keep (MVP) → supersede (Fase 3)** | `IMP-2.2` MVP; `ADR001-C-07` prod | JWT for MVP; superseded by IAM Identity Center SSO in Fase 3 (WO-037) |
| `auth.py` (dev stub: accepts any Bearer) | 48 | **replace** | `security-lgpd.md` §5 (DENY-BY-DEFAULT) | Duplicate of `auth/`; the "any non-empty Bearer" stub is a security defect — collapse into `auth/`, delete the stub |
| `models/{vital_sign,clinical_score,alert,threshold_config,patient_cache}.py` | ~145 | **extend** | `data-model.md` §3 delta table | Per-table deltas: `algorithm_version NOT NULL`+FK; `alert.definition_version_id`/`correlation_event_id`, enum extensions; `threshold_config.bed_id`; `patient_cache` pgcrypto PHI |
| `models/user.py` | 25 | **keep (MVP) → reference-only (Fase 3)** | `ADR001-C-07` | Local users for MVP; IAM IC subject becomes actor once SSO lands |
| `frontend/` (Vite + React 19 + Tailwind v4 + Recharts SPA) | ~8 comps | **replace → reference-only** | `design/component-library.md` §ADR-0001; `design-tokens.md` | **Verify-on-disk correction:** a v1 SPA *does* exist here, but the design specs mandate **Next.js App Router (server-side tenant/permission resolution) + Radix + Style Dictionary + Storybook** — the Vite SPA has none of these and uses the wrong severity enum (`info/warning/critical`, AUDIT-008). Greenfield-rebuild; the SPA's API-client + component intent are reference-only |

**New subsystems — greenfield (no v1 equivalent):** AMH integration layer — Gold Reader (Athena high-watermark poller, `system-architecture.md` §3), Gold Writer (`fact_patient_score`/`fact_alert`, §5), MPI client (§4), FHIR enrichment (extends `fhir/client.py`, §4.3); **correlation engine** (`alert-engine.md` §1; `correlation-engine.yaml`); **notification/routing tiers** (`severity-model.yaml`, `design/screens/alert-routing.md`); **`audit_trail` + pgcrypto** (`INV-1`/`INV-4`, `data-model.md` §6/§7); **ARQ delivery** (`INV-6`, `alert-engine.md` §7.1); the Phase-2 tables `alert_definition(_version)`, `algorithm_registry`, `alert_enablement`, `correlation_event`, `lab_result`, `medication_order/administration` (`data-model.md` §4/§5); the **design-token system** (Style Dictionary) + Storybook + a11y automation (`design/*`).

---

## 2. Environment bootstrap (command-level)

**Repo layout.** Backend evolves **in place** under `src/intensicare/` (brownfield-core). Frontend is a **new app dir** `frontend/` rebuilt on Next.js (the existing Vite SPA is moved to `frontend/_legacy-vite-reference/` read-only, or a sibling `web/`, orchestrator's call — journal it). Gates live in `scripts/` mirroring `docs/plan/_work/scripts/`. Alembic migrations under `alembic/versions/`.

**Backend pins** (`IMP-3.2-01..06`, `pyproject.toml`): Python **3.12+** (CI matrix 3.12/3.13); FastAPI (async, OpenAPI, WebSocket); PostgreSQL **16** + TimescaleDB **2.18** (`CON-SEED-04`, `system-architecture.md` §9); Redis **7**; **ARQ** task queue; SQLAlchemy async + Alembic; hatchling build; Ruff (lint+format, cyclomatic ≤10 `IMP-C-18`), MyPy strict (`IMP-C-19` ≥90% MVP/100% prod), Bandit, `hypothesis` (test group, `test-strategy.md` §3), pytest+pytest-asyncio, pre-commit (8 hooks).

**Frontend pins** (`component-library.md` §2): Node LTS; **Next.js App Router + React 19**; TypeScript **strict**; **Tailwind v4**; **Radix UI** (unstyled) + first-party token layer; **Style Dictionary** (one JSON token source → CSS vars + TS types); **Storybook** + visual-regression (Playwright `toHaveScreenshot`); `axe-core`/`@axe-core/playwright` a11y automation.

**Local dev.** `docker-compose.yml` (already present) extends with an ARQ worker service + a Next.js dev service; `make dev-up`/`dev-down`/`test`/`lint`/`check` (`IMP-4.4-01`). Add `make db-revision`/`db-migrate` for the Phase-2 migrations.

**AWS (sa-east-1, `ADR001-C-08`/`ADR001-F-04`) — same VPC/accounts as AMH DP.** ECS Fargate tasks: API, Alert Engine (ARQ), MLLP listener (`system-architecture.md` §8). RDS PostgreSQL 16 + TimescaleDB 2.18 (operational-only, `ADR001-C-03`), Redis 7, private subnets, internal ALB. **IAM postures to request (named dependencies, not self-served):** (a) **Athena/Glue Data Catalog** read grants + a **per-tenant Athena workgroup** with its own concurrency + bytes-scanned limits (`system-architecture.md` §3.4, OQ-5); (b) **Lake Formation ABAC** grants deciding which Gold partitions IntensiCare may scan (`ADR001-C-07`); (c) **per-tenant KMS** data-key issuance for pgcrypto DEKs (`security-lgpd.md` §4.2); (d) **IAM Identity Center** SSO federation (Fase 3). **Observability:** OTEL exporters → existing **AMP + Grafana** (`ADR001-C-06`); no parallel metrics stack.

**CI pipeline stages** (extend `.github/workflows/ci.yml`; existing jobs: `frontend, lint, test[3.12/3.13], coverage, security, build, deploy-staging, release`; `test-strategy.md` §10.2):

| Stage | Adds | Blocks merge? |
|---|---|---|
| lint | Ruff + MyPy strict (existing) | yes |
| test | + **L1 rule-vector** suite (`tests/rules/`), **L2 property** scorer suite (`tests/property/`), **L4 mocked contract** (`tests/contract/`) on 3.12/3.13 | yes |
| coverage | `--cov-fail-under=80` (enforce; today reporting-only), ≥95% scorer/engine carve-out (`test-strategy.md` §10.1; `IMP-C-17` still open) | yes |
| **build-gates** (new fast job) | `check_units.py` (units registry, `SYS-01/02/03`), **criterion-coverage** (`REQ-GATE-01`, `SYS-08`), **band-partition** (`REQ-GATE-02`, `SYS-06/07`), **facade==predicate** (`REQ-GATE-03`, `SYS-04`), `check_vector_coverage.py`, `check_tokens.py`, traceability (Section 6) | yes |
| **contract** (from `api/openapi.yaml` + `asyncapi.yaml`) | schema-conformance of REST/WS + Athena/Gold read/write shapes (mocked) | yes |
| a11y + visual (job `frontend`/new `Job 2b`) | `axe-core` zero-AA-violations; Playwright snapshot matrix (both themes × severity) | yes (a11y); visual = human approval |
| security | Bandit + Trivy(+Cosign) (existing); DRILLs run in the release job | yes |
| **storm + drills** (new, pre-release gate) | L6 storm (>500/min) + 6 L7 chaos drills | yes, pre-release |

---

## 3. Build phases + work orders

Fase mapping: `IMP-6-01..05` (Fase 0 Foundation → Fase 4 ML/Advanced) × vision priorities `VIS-5.1` **P1 Sepse, P2 AKI, P3 Eletrólitos, P4 Hemodinâmica, P5 Respiratória, P6 Drogas, P7 Delirium** and rollout order `VIS-5.2` (2a Sepse+AKI+Eletrólitos → 2b Hemo+Resp → 2c Drogas+Delirium → 2d Correlation). Each WO: {scope · governing spec · inputs · acceptance gate · depends-on · parallel-with · agent+tier}. Model tiers: **strong** = engine/correlation/security-critical; **mid** = CRUD/UI assembly; **cheap** = mechanical codegen/tests-from-vectors (Section 5).

### Fase 0 — Foundation (Weeks 1–2, `IMP-6-01`). The 6 invariants FIRST — they gate everything.

- **WO-001 — `audit_trail` immutable (INV-1).** *Scope:* `audit_trail` hypertable + `trg_audit_trail_immutable` anti-mutation trigger + `REVOKE UPDATE,DELETE`; encrypted before/after snapshots.
  - *Spec:* `data-model.md` §6 (`IMP-C-01`/`CON-0066`, `HANDOFF` TECH-001) · *Inputs:* §6 DDL verbatim.
  - *Gate:* `REQ-INV-1-1` migration test + `DRILL-AUDIT-TAMPER` (UPDATE/DELETE blocked, row bytes unchanged).
  - *Depends:* none · *Parallel:* WO-002/003 · *Agent:* backend-core/**strong**.
- **WO-002 — pgcrypto PHI encryption (INV-4).** *Scope:* `pgcrypto` ext; `patient_cache` PHI→BYTEA (`display_name,mrn,birth_date,cpf,cns`); per-tenant KMS DEK via GUC; `mrn_bidx` blind index; `age_derivation` service.
  - *Spec:* `data-model.md` §7 + `security-lgpd.md` §4 (`IMP-C-04`/`CON-0069`, TECH-002, RT1-SEC-03) · *Inputs:* §7 DDL; `security-lgpd.md` §4.2 key hierarchy.
  - *Gate:* `REQ-INV-4-1..3` + `DRILL-CROSS-TENANT-DECRYPT` + `DRILL-PHI-EGRESS-SCRUB` (no plaintext DOB in `pg_dump`).
  - *Depends:* none · *Parallel:* WO-001/003 · *Agent:* security/**strong**.
- **WO-003 — algorithm versioning (INV-3).** *Scope:* `algorithm_registry` (immutable); `clinical_score.algorithm_version` → NOT NULL + FK; legacy backfill migration.
  - *Spec:* `data-model.md` §5 + §2 (`IMP-C-03`/`CON-0068`) · *Inputs:* §5.1/§5.2 DDL.
  - *Gate:* `REQ-INV-3-1` (no table `clinical_scores`; zero NULLs) + `DRILL-VERSION-PIN`.
  - *Depends:* none · *Parallel:* WO-001/002 · *Agent:* backend-core/**mid**.
- **WO-004 — health check + dead-man's switch (INV-5).** *Scope:* `/api/v1/health` readiness (DB+Redis+ARQ+Athena + per-(unit,domain) liveness matrix); external CloudWatch/Lambda watchdog ≤30 s; alert-on-no-alerts staleness monitor.
  - *Spec:* `observability-slo.md` §4 + `alert-engine.md` §7.2 (`IMP-C-05`, AUDIT-004, TECH-003) · *Inputs:* §4.1 response shape.
  - *Gate:* `REQ-INV-5` + `DRILL-POLLER-KILL` (watchdog pages ≤30 s; readiness flips degraded).
  - *Depends:* WO-005 (ARQ liveness key) · *Parallel:* WO-001/002/003 · *Agent:* platform-reliability/**strong**.
- **WO-005 — ARQ retry/backoff + DLQ (INV-6).** *Scope:* ARQ worker; exponential-backoff retry on every notification (WS/mobile/SMS); DLQ + operational alert on exhaustion; client dedup on `dedup_key`.
  - *Spec:* `alert-engine.md` §7.1 + `observability-slo.md` §5 (`IMP-C-06`/`CON-0071`, AUDIT-005 — retires the dead `tenacity` dep) · *Inputs:* §5.1 retry policy.
  - *Gate:* `REQ-INV-6` + `DRILL-NOTIFICATION-BLACKHOLE` (retries→DLQ→op-alert; no silent loss).
  - *Depends:* none · *Parallel:* WO-001/002/003 · *Agent:* alert-engine/**strong**.
- **WO-006 — ingestion idempotency hardening (INV-2).** *Scope:* confirm MLLP `MSH-10` `ON CONFLICT DO NOTHING` (already present) + add Gold-poll natural key `(mpi_id,recorded_at,source_system,measurement)`.
  - *Spec:* `alert-engine.md` §4.1 (`IMP-C-02`/`CON-0067`) · *Inputs:* existing `mllp_listener.py`.
  - *Gate:* `REQ-INV-2` + `DRILL-DUPLICATE-REPLAY` (same MSH-10 twice + re-poll window twice → one row).
  - *Depends:* none · *Parallel:* all Fase 0 · *Agent:* integration/**mid**.
- **WO-007 — DevOps baseline + CI gate wiring.** *Scope:* docker-compose ARQ + Next services; ECS Fargate task defs (skeleton: API, Engine, MLLP); OTEL→AMP wiring; extend `ci.yml` with build-gates/contract/a11y/storm jobs (Section 2).
  - *Spec:* `IMP-4.1/4.3`; `system-architecture.md` §8; `test-strategy.md` §10.2 · *Inputs:* existing `ci.yml` 8-job pipeline.
  - *Gate:* CI green with new jobs present (draft-mode until their WOs land).
  - *Depends:* none · *Parallel:* all · *Agent:* platform-reliability/**mid**.
- **WO-008 — declarative alert-definition compiler + build-time SYS gates.** *Scope:* load `_work/alerts/*.yaml` + domain-doc machine blocks → versioned definition registry; `evaluate_alert_definition(alert_id, inputs)->bool` entry point; Gate A (criterion-coverage), B (band-partition), C (facade==predicate).
  - *Spec:* `alert-engine.md` §2/§2.1/§2.2 (`REQ-GATE-01/02/03`, `SYS-04/06/07/08`) · *Inputs:* CONTRACTS alert schema; the 9 catalogs.
  - *Gate:* seeded-defect tests (unwire a criterion → build fails; reintroduce a strict `>5.0` renal edge → fails; hand-edit a facade threshold → fails).
  - *Depends:* WO-009 · *Parallel:* WO-003/005 · *Agent:* alert-engine/**strong**.
- **WO-009 — units registry strict + canonical pins.** *Scope:* wire `_work/units/registry.yaml` + `check_units.py --strict` into CI; enforce `CANON_PINS` (lactate mmol/L, FiO₂ fraction, vasopressor mcg/kg/min, temp degC, creatinine mg/dL).
  - *Spec:* `alert-engine.md` §2.1 (`CON-SEED-12`, `SYS-01/02/03`) · **canonical convention pending `ASK-5`** (Section 4).
  - *Gate:* `check_units.py --mode strict` green over all catalogs + domain-doc blocks.
  - *Depends:* none · *Parallel:* WO-007 · *Agent:* integration/**cheap**.
- **WO-010 — regulatory README correction.** *Scope:* remove "HIPAA"/"GDPR"; substitute "LGPD"/"SBIS".
  - *Spec:* `IMP-C-07`/`IMP-5.1-05` · *Gate:* grep finds no HIPAA/GDPR in `README.md`.
  - *Depends:* none · *Parallel:* all · *Agent:* backend-core/**cheap**.

### Fase 1 — Hardening kept modules + corrections pipeline (Weeks 3–8, `IMP-6-02`).

- **WO-011 — canonical severity model + AUDIT-008.** *Scope:* `normal/watch/urgent/critical` clinical.* scale, triple-encoded (color+icon+shape); highest-severity-wins (`P0-10`, never last-writer-wins); align backend+frontend enums.
  - *Spec:* `alert-engine.md` §3/§3.1 + `severity-model.yaml` (`CON-SEED-11`, AUDIT-008) · *Gate:* severity-mapping unit tests + `P0-10` downgrade regression.
  - *Depends:* WO-001 · *Parallel:* WO-012/013 · *Agent:* alert-engine/**strong**.
- **WO-012 — MEWS correction (AUDIT-001).** *Scope:* adjust 4 inflated bands (HR ≤40:3→2, 41–50:2→1, RR ≤8:3→2, Temp ≤35:3→2) to Subbe 2001; bump `MEWS-v1.0.1`; regen vectors. **Ships behind `algorithm_version` flag, pending clinical sign-off** (Section 4, P0).
  - *Spec:* `HANDOFF` AUDIT-001; scorers `MEWS-*` · *Gate:* L2 property + updated example vectors; journal marks pending.
  - *Depends:* WO-003, WO-022 · *Parallel:* WO-013/014 · *Agent:* alert-engine/**strong**.
- **WO-013 — NEWS2 correction (AUDIT-002).** *Scope:* fix Scale-2 SpO₂ boundary bands to RCP 2017 + integrate `supplemental_o2`; bump version; new vectors; **pending sign-off**.
  - *Spec:* `HANDOFF` AUDIT-002 · *Gate:* L2 two-scale monotonicity (`NEWS2-C-02`).
  - *Depends:* WO-003, WO-022 · *Parallel:* WO-012/014 · *Agent:* alert-engine/**strong**.
- **WO-014 — SOFA single-source-of-truth (AUDIT-003).** *Scope:* unify live vs replay risk-classification; renal = max(cr,uo) (`SOFA-C-03`); cardiovascular vasopressor rate mcg/kg/min **pending `RAT-CLINICAL-SCORING-*`/`ASK-5`**.
  - *Spec:* `HANDOFF` AUDIT-003; `RATIFICATION.md` · *Gate:* L2 property + parity test live==replay.
  - *Depends:* WO-003 · *Parallel:* WO-012/013 · *Agent:* alert-engine/**mid**.
- **WO-015 — schema deltas: alert/threshold enums + scopes.** *Scope:* `alert.definition_version_id`+`correlation_event_id`; `status`+=`acting,escalated`; `severity`+=`normal`; `threshold_config.bed_id`+unique scope key.
  - *Spec:* `data-model.md` §3.1 (B2-001) · *Gate:* migration tests; `REQ-INV-3-2`.
  - *Depends:* WO-001/003 · *Parallel:* WO-016 · *Agent:* backend-core/**mid**.
- **WO-016 — API contract fixes AUDIT-007 + contract tests.** *Scope:* `GET /api/v1/alerts` → `{alerts,total}`; lifecycle endpoints; generate REST/WS contract tests from `api/openapi.yaml`+`asyncapi.yaml`.
  - *Spec:* `HANDOFF` AUDIT-007; `api/api-design.md` · *Gate:* contract job green; frontend+backend agree.
  - *Depends:* WO-011/015 · *Parallel:* WO-017 · *Agent:* backend-core/**mid**.
- **WO-017 — threshold_config 3-scope resolution + audit.** *Scope:* bed≻unit≻tenant most-specific-wins; every write→`audit_trail` (INV-1).
  - *Spec:* `alert-engine.md` §6; `data-model.md` §3.1a · *Gate:* resolution unit tests; `REQ-INV-1-2`.
  - *Depends:* WO-001/015 · *Parallel:* WO-016 · *Agent:* backend-core/**mid**.
- **WO-018 — MPI resolver + patient_cache sync.** *Scope:* MPI client; `patient_cache` upsert stamping `synced_at`; discharge+30d flush; demographics never a scoring input.
  - *Spec:* `system-architecture.md` §4 (`ADR001-C-02`) · *Gate:* cache-miss re-resolve; unreachable-MPI never blocks alert.
  - *Depends:* WO-002 · *Parallel:* WO-019 · *Agent:* integration/**mid**.
- **WO-019 — Gold Reader (Athena poller).** *Scope:* incremental high-watermark poll (`ingested_at`/snapshot id); per-domain cadence; per-tenant workgroup; cadence backpressure; canonical-unit normalize at edge.
  - *Spec:* `system-architecture.md` §3.1/§3.2/§3.4 (`ADR001-C-01`, OQ-5) · *Gate:* idempotent re-poll; `tests/contract/test_gold_read_schema.py`.
  - *Depends:* WO-009 · *Parallel:* WO-018/020 · *Agent:* integration/**strong**.
- **WO-020 — Gold Writer (write-back).** *Scope:* periodic `fact_patient_score`/`fact_alert` load carrying `algorithm_version`/`definition_version`; one-directional; never read back for scoring.
  - *Spec:* `system-architecture.md` §5 (`ADR001-C-04`, `REQ-INV-3-3`); cadence OQ-2 · *Gate:* `tests/contract/test_gold_writeback.py` — PHI provably absent (`REQ-INV-4-S3`), version present, idempotent.
  - *Depends:* WO-003 · *Parallel:* WO-019 · *Agent:* integration/**strong**.
- **WO-021 — Phase-2 hot-cache tables + FHIR enrichment.** *Scope:* `lab_result`, `medication_order/administration` hypertables/tables; FHIR client enrichment pulls.
  - *Spec:* `data-model.md` §4.3/§4.4; `system-architecture.md` §4.3 · *Gate:* FHIR fixtures (`test-strategy.md` §4.3); `ON CONFLICT` idempotency.
  - *Depends:* WO-002 · *Parallel:* WO-019/020 · *Agent:* integration/**mid**.
- **WO-022 — L1 rule-vector harness + L2 property scorer tests.** *Scope:* `tests/rules/test_alert_vectors.py` (YAML-driven; 50 alerts / 266 vectors), `tests/property/test_scorer_properties.py` (Hypothesis).
  - *Spec:* `test-strategy.md` §2/§3 · *Gate:* build fails if any `alert_id` lacks a definition or any alert has 0 vectors (`check_vector_coverage.py`).
  - *Depends:* WO-008 · *Parallel:* WO-012/013 · *Agent:* QA/**cheap**.
- **WO-023 — design-token system + frontend scaffold.** *Scope:* Style Dictionary source→CSS/TS; Next.js App Router + Radix wrappers; Storybook; `check_tokens.py`.
  - *Spec:* `design-tokens.md`, `component-library.md` §2/§3 · *Gate:* `check_tokens.py` strict; Storybook builds; a11y AA on scaffold.
  - *Depends:* WO-011 · *Parallel:* WO-016 · *Agent:* frontend-platform/**mid**.

### Fase 2 — Domains in P1–P7 order (Weeks 9–14+, `IMP-6-03`; rollout `VIS-5.2`). Each domain WO = alert definitions (executable fixtures from `_work/alerts/<domain>.yaml`) + engine wiring + UI surface.

- **WO-024 — P1 Sepsis (rollout 2a).** *Scope:* `sepsis.yaml` (6 alerts, 31 vectors); screening/organ/shock/bundle; hybrid mode. **Aggregation v1-AND vs v3-OR behind flag, pending `RAT-SEPSE-02`** (Section 4).
  - *Spec:* `vision.md` §3.1; `clinical/domains/sepsis.md` · *Gate:* all 31 vectors pass L1; PPV budget ≥0.60.
  - *Depends:* WO-008/019/022 · *Parallel:* WO-025/026 · *Agent:* alert-engine/**strong**.
- **WO-025 — P2 AKI (2a).** *Scope:* `aki.yaml` (3 alerts, 17 vectors); KDIGO 1/2/3 + progression; micro-batch.
  - *Spec:* `vision.md` §3.2 · *Gate:* 17 vectors; boundary Cr=1.5× inclusive.
  - *Depends:* WO-008/019/022 · *Parallel:* WO-024/026 · *Agent:* alert-engine/**mid**.
- **WO-026 — P3 Electrolytes (2a).** *Scope:* `electrolyte.yaml` (6 alerts, 39 vectors); K⁺/Na⁺/Ca²⁺/Mg²⁺ + Δ-Na; **expedited ~1–2 min poll, best-effort until OQ-5 quota proven → §6 T2**.
  - *Spec:* `vision.md` §3.6 · *Gate:* 39 vectors; CRIT never auto-resolves on stale.
  - *Depends:* WO-008/019/022 · *Parallel:* WO-024/025 · *Agent:* alert-engine/**mid**.
- **WO-027 — Early-warning scores wiring (NRT).** *Scope:* `early-warning-scores.yaml` (4 alerts, 25 vectors); MEWS/NEWS2/qSOFA/SOFA NRT path off `vital_sign` inserts (US-01/02/03).
  - *Spec:* `alert-engine.md` §1.1; `system-architecture.md` §3.3 · *Gate:* 25 vectors; NRT p95 stage budget (`alert-engine.md` §8).
  - *Depends:* WO-012/013/014 · *Parallel:* WO-024 · *Agent:* alert-engine/**strong**.
- **WO-028 — P4 Hemodynamics (2b).** *Scope:* `hemodynamics.yaml` (6 alerts, 34 vectors); shock index, lactate clearance, vaso-escalation; hybrid/NRT.
  - *Spec:* `vision.md` §3.4 · *Gate:* 34 vectors.
  - *Depends:* WO-027 · *Parallel:* WO-029 · *Agent:* alert-engine/**mid**.
- **WO-029 — P5 Respiratory (2b).** *Scope:* `respiratory.yaml` (5 alerts, 24 vectors); SpO₂/FiO₂ Berlin bands; hybrid/NRT.
  - *Spec:* `vision.md` §3.3 · *Gate:* 24 vectors; FiO₂ fraction unit enforced.
  - *Depends:* WO-027 · *Parallel:* WO-028 · *Agent:* alert-engine/**mid**.
- **WO-030 — P6 Drug interactions (2c).** *Scope:* `pharmaco-interaction.yaml` (8 alerts, 34 vectors); QTc/serotonin/nephro-additive; micro-batch.
  - *Spec:* `vision.md` §3.7 · *Gate:* 34 vectors.
  - *Depends:* WO-021 · *Parallel:* WO-031 · *Agent:* alert-engine/**mid**.
- **WO-031 — P7 Delirium/neuro-sedation (2c).** *Scope:* `neuro-sedation.yaml` (8 alerts, 38 vectors); RASS/CAM-ICU; **pain-band top-band corrections pending `RAT` (BPS/NRS misparse, `SYS-06`)**.
  - *Spec:* `vision.md` §3.5 · *Gate:* 38 vectors; band-partition (`REQ-GATE-02`).
  - *Depends:* WO-021 · *Parallel:* WO-030 · *Agent:* alert-engine/**mid**.
- **WO-032 — Correlation engine (2d).** *Scope:* `correlation-engine.yaml` (4 alerts, 24 vectors); Sepsis+AKI, Resp+Hemo, Drug+Electrolyte; second-pass over persisted alerts; MAX-severity fold. **Start only after ≥2 member domains live.**
  - *Spec:* `alert-engine.md` §1/§5.1; `data-model.md` §4.2; `VIS-4-03` · *Gate:* 24 vectors; fold never suppresses (HAZ-026).
  - *Depends:* WO-024 + one of WO-025/026 · *Parallel:* WO-033 · *Agent:* alert-engine/**strong**.
- **WO-033 — notification/routing tiers + lifecycle.** *Scope:* 4-tier delivery; lifecycle state machine (`raise→ack→act→resolve`/`escalated`/`expired`); band-aware escalation ladder; suppression layers.
  - *Spec:* `alert-engine.md` §3/§5/§9; `design/screens/alert-routing.md` · *Gate:* PPV/fatigue instrumentation; escalation timers.
  - *Depends:* WO-005/011 · *Parallel:* WO-032 · *Agent:* alert-engine/**strong**.
- **WO-034 — clinical UI surfaces.** *Scope:* 7 screens — command-center/bed-board, alert-triage, patient-timeline, alert-routing, clinical-forms, admin-config, handoff.
  - *Spec:* `design/screens/*` · *Gate:* a11y AA (AAA critical values); visual-regression matrix; screen-reader pass on ack + bed-board.
  - *Depends:* WO-023/033 · *Parallel:* domain WOs · *Agent:* clinical-UI/**mid**.
- **WO-035 — L4 contract + L6 storm + L7 drills.** *Scope:* Athena/Gold + HL7 + FHIR contract corpus; storm ≥500/min + 3× burst; 6 chaos drills.
  - *Spec:* `test-strategy.md` §4/§5/§6 · *Gate:* storm p95<30 s + zero-loss; all 6 drills pass.
  - *Depends:* all domain + INV WOs · *Parallel:* WO-034 · *Agent:* QA/**mid**.
- **WO-036 — clinical validation (CLIN-001/002).** *Scope:* 48 h real HL7 traffic (hospital AUSTA); MEWS/NEWS2/SOFA/qSOFA vs gold-standard protocol.
  - *Spec:* `HANDOFF` CLIN-001/002; `delivery/validation-plan.md` · *Gate:* validation report signed.
  - *Depends:* WO-027 · *Parallel:* WO-035 · *Agent:* QA + clinical/**strong**.

### Fase 3 — Production (Weeks 15–20, `IMP-6-04`).

- **WO-037 — SSO/IAM path.** *Scope:* IAM Identity Center SSO (supersede v1 JWT + local `users`); Lake Formation ABAC; per-tenant KMS in prod; `rrt` cross-unit role.
  - *Spec:* `ADR001-C-07`; `security-lgpd.md` §5/§5.3.1 · *Gate:* DENY-BY-DEFAULT role tests; cross-tenant decrypt fails.
  - *Depends:* WO-002 · *Parallel:* WO-038 · *Agent:* security/**strong**.
- **WO-038 — DR + capacity + TLS.** *Scope:* WAL shipping (RPO 1 h/RTO 1 h); capacity 30→90→multi-hospital; TLS/HTTPS (Caddy+LE).
  - *Spec:* `IMP-C-15/16`; `observability-slo.md` §6/§7; `HANDOFF` SEC-002 · *Gate:* DR drill (`replication_lag` metric inside RPO); capacity soak.
  - *Depends:* WO-007 · *Parallel:* WO-037 · *Agent:* platform-reliability/**mid**.
- **WO-039 — security + regulatory readiness.** *Scope:* pentest (`SEC-001`); ANVISA SaMD Classe II cadastro (`REG-001`/`VIS-C-02`); LGPD RIPD (`REG-002`/`VIS-C-06`); SBIS/ISO 27001 roadmap.
  - *Spec:* `regulatory-plan.md`; `security-lgpd.md` §8 · *Gate:* pentest report clean; RIPD delivered to DPO.
  - *Depends:* WO-035 · *Parallel:* WO-037/038 · *Agent:* security + clinical/**strong**.

### Fase 4 — Alternative-B evaluation (Weeks 21+, `IMP-6-05`).

- **WO-040 — Alternativa-B MSK trigger evaluation.** *Scope:* instrument the quantified **T1** trigger — vitals ingest→alert p95 > 30 s over rolling 7-day window with MLLP healthy, OR MLLP unavailable > 0.5% bed-hours; **T2** electrolyte CRIT freshness. Decide/defer per §6 table. **Do NOT activate before Fase 4** (T5).
  - *Spec:* `system-architecture.md` §6 (`ADR001-F-08`, OQ-1/OQ-3) · *Gate:* telemetry review + CTO/AMH joint sign-off if activated.
  - *Depends:* production telemetry (Fase 2/3) · *Parallel:* none · *Agent:* integration/**strong**.

**Critical path + parallelism.** The gating spine is **WO-001..006 (invariants) → WO-008/009 (compiler+units) → WO-019/020 (Gold I/O) → WO-024/027 (first domain + EWS NRT) → WO-032/033 (correlation+routing) → WO-035/036 (drills+validation)**. Everything else parallelizes off it: the three invariant tracks (audit/crypto/versioning) run concurrently in Fase 0; domain WOs 024–031 fan out once WO-008/019/022 land (respecting the 2a→2b→2c→2d rollout); frontend (WO-023/034) runs alongside the backend domains. Correlation (WO-032) is the one hard sequencing constraint — it may not start until ≥2 member domains are live.

---

## 4. Ratification dependency map

**Rule (doctrine §6, `CONTRACTS.md` disposition policy):** a `RATIFY`-pending default **ships behind a version flag** (`algorithm_version`/`definition_version`), defaults to the reference-anchored recommended default (never the legacy value), is annotated `pending RAT-*` in code + journal, and is switchable without a redeploy once ratified. The build **proceeds**; only the *flip to a disputed alternative* blocks on humans. `RATIFICATION.md` (1832 lines, 5 asks `ASK-1..5`, 12 P0 + 45 P1 + 101 UNVERIFIABLE-owner queues) is the register.

| Ratification class | Blocks (cannot flip without sign-off) | Proceeds on default (marked pending) | Owner |
|---|---|---|---|
| **MEWS correction** (AUDIT-001) | Flip to Subbe-2001 as clinical-live default | Build `MEWS-v1.0.1` behind flag; legacy MEWS-v1.0 retained for replay | Clinical committee (P0) |
| **NEWS2 correction** (AUDIT-002) | Flip Scale-2 + `supplemental_o2` live | Build corrected version behind flag | Clinical committee (P0) |
| **Sepsis aggregation** (`RAT-SEPSE-02`, `ASK-4`) | Choose v1-AND vs v3-OR as canonical | Ship recommended default: OR-within published sets, AND-gated by infection (`sepsis.yaml` `ALERT-SEPSIS-SCREEN-01`) | Clinical committee |
| **Canonical units** (`ASK-5`) | Final FiO₂ fraction / lactato mmol/L / vasopressor mcg/kg/min convention | `CANON_PINS` already enforce recommended defaults (WO-009); reimplementation waits on the ratified convention | Eng+clinical |
| **SOFA vasopressor rate** (`RAT-CLINICAL-SCORING-*`) | Flip raw-ml→mcg/kg/min tiers | Build reference rate tiers behind version; requires upstream rate derivation | Clinical committee |
| **Pain-band corrections** (`SYS-06`, BPS/NRS) | Confirm top-band reachable fix | Corrected band ships; band-partition gate enforces reachability | Clinical committee |
| **E-signature findings** (`ASK-3`) | Shared default signing PIN (`RULE-AUTH-USUARIOS-063`); CryptoCubo advanced profile sans ICP-Brasil (`RULE-DOCUMENTACAO-FATURAMENTO-032`) | Feature stays DENY-BY-DEFAULT / disabled until legal rules on MP 2.200-2 | Legal |
| **UNVERIFIABLE owner rules** (`ASK-2`, ~101–204 dispositions) | Adopt any proprietary rule whose intent only owner can confirm | Not built until confirmed; no silent adoption | Product/clinical owner |
| **Operational vitals ingress** (`RAT-INGRESS-01`) | Permanent scope of `ADR001-C-01` clarification | MLLP is working design-of-record; rejection → pure-batch fallback (hazard-logged) or accelerated Alt-B | CTO Office + AMH Eng |
| **Coverage gate number** (`IMP-C-17`) | Final 70/80/85 reconciliation | Enforce ≥80% now (`test-strategy.md` §10.1) | Barrier C3 |
| **Audit retention** (CFM 20 y vs 7 y) | Final audit_trail retention | Ship 7 y; flagged for legal (`data-model.md` §10) | Legal |

### 4.1 `HANDOFF.yaml` blocked-item → WO discharge map

Every `blocked:` item in `HANDOFF.yaml` maps to the WO that closes it — the resume-protocol cross-reference (doctrine §5). An item is "done" only when its WO's acceptance gate is green, not when its WO is claimed complete.

| HANDOFF id | Severity | Discharged by | Deadline |
|---|---|---|---|
| TECH-001 (`audit_trail` immutable) | critical | WO-001 | before pilot |
| TECH-002 (pgcrypto PHI) | critical | WO-002 | before pilot |
| AUDIT-001 (MEWS inflated bands) | critical | WO-012 (flag) | before pilot |
| AUDIT-002 (NEWS2 Scale-2) | critical | WO-013 (flag) | before pilot |
| AUDIT-004 (`/health` no DB/Redis) | high | WO-004 | before pilot |
| TECH-003 (external dead-man switch) | high | WO-004 | before pilot |
| AUDIT-005 (retry/backoff / dead `tenacity`) | high | WO-005 | Fase 2 |
| AUDIT-008 (severity enum mismatch) | medium | WO-011 | Fase 2 |
| AUDIT-003 (SOFA dual-path) | medium | WO-014 | Fase 2 |
| AUDIT-007 (alerts array vs `{alerts,total}`) | medium | WO-016 | Fase 2 |
| TECH-004 (IdempotencyStore → Redis) | medium | WO-006 | Fase 2 |
| CLIN-001 (48 h real HL7) / CLIN-002 (validation protocol) | critical/high | WO-036 | Fase 2 / Q3 |
| SEC-002 (TLS/HTTPS prod) | high | WO-038 | Fase 3 |
| SEC-001 (external pentest) / REG-001 (ANVISA) / REG-002 (RIPD) | high/critical | WO-039 | Fase 3–Q4 |

`ops_backlog` items (`HANDOFF.yaml`) — staging GitHub Environment, the coverage `fail-under` gate, Bandit/pip-audit `|| true` gating, the legacy hardcoded Postgres password in `ahlabs-trilhas` — are folded into WO-007 (CI wiring) and WO-039 (security), except the coverage-gate number which is `RAT`-blocked (`IMP-C-17`, §4).

---

## 5. Implementation agent roster + model routing

Guilds mirror the plan's architect roles (`test-strategy.md` §6 ownership map). Each guild obeys the **verification protocol**: (a) write only its WO's named files (doctrine §2); (b) produce a data receipt whose counts match disk; (c) the orchestrator re-runs the WO's acceptance gate before accepting — receipt never substitutes for gate (doctrine §1).

| Guild | Owns | Model tier | Rationale |
|---|---|---|---|
| **backend-core** | app scaffold, `config`, DB/session, models, migrations, CRUD APIs | **mid** (strong for INV-1 audit) | Mechanical schema/CRUD; audit immutability is safety-critical |
| **alert-engine** | declarative compiler, SYS gates, scorers, domain wiring, correlation, severity, lifecycle, suppression | **strong** | Clinical-correctness + latency-critical; a wrong band fires thousands of times (`test-strategy.md` §1) |
| **integration** | Gold Reader/Writer, MPI, FHIR, MLLP, hot-cache, Alt-B | **strong** (mid for cache CRUD) | ADR-001 boundary; schema-drift fails silently in prod |
| **frontend-platform** | Style Dictionary, Next.js scaffold, Radix wrappers, Storybook | **mid** | UI assembly on a governed token system |
| **clinical-UI** | 7 clinical screens, a11y, visual-regression | **mid** | Screen assembly; a11y gates are mechanical |
| **QA** | L1/L2/L4 harness, storm, chaos drills, coverage gate | **cheap** (mid for drills) | Tests-from-vectors is mechanical codegen; the vectors are pre-adjudicated |
| **security** | pgcrypto/KMS, RBAC, SSO, pentest, RIPD | **strong** | INV-4 + LGPD; a leak is unrecoverable |
| **platform-reliability** | health/dead-man, ARQ/DLQ, OTEL, DR, capacity, CI | **strong** (mid for CI wiring) | INV-5/6; silent failure is the signature risk |

**Tier assignment principle:** strong for engine/correlation/security-critical and any INV-1..6 mechanism; mid for CRUD/UI assembly; cheap for mechanical codegen and tests-derived-from-fixtures (the vectors carry the clinical judgment, not the coder).

---

## 6. Traceability + provenance duty

**Every implemented alert/rule carries its ids in code.** Each alert-definition module/record annotates its `ALERT-<DOMAIN>-<SLUG>-NN` and every `RULE-<CLUSTER>-NNN` it draws on (from `docs/rules/extraction/phase2/catalog/*.yaml` — the authoritative 959 ids; `catalog-index.json` is stale, `CONTRACTS.md` §7). Scorers annotate their `algorithm_version` + the scorers-brief ids (`MEWS-*` etc.).

**A generated traceability check runs in CI** (mirror `docs/plan/_work/scripts/check_alert_catalog.py` + `check_matrix.py`): assert (a) every `alert_id` in `_work/alerts/*.yaml` has a loaded engine definition and ≥1 test vector; (b) every `rule_ref` has disposition ADOPT/ADOPT-CORRECTED/ADAPT (`merged.json`); (c) every implemented alert traces back to a `traceability-matrix.md` row; (d) no code cites a stale/unknown id. This is the code-side twin of the plan gates already green on `main`.

**Divergence protocol:** `docs/plan/**` is the contract. If code needs to deviate from a spec, open a **spec-change PR first** (edit the governing `docs/plan` file, re-run its plan gate), then the code PR referencing it — code second. A silent code/spec divergence is a build defect, caught by the traceability gate (facade==predicate, `REQ-GATE-03`, is the same principle inside one alert).

---

## 7. Definition of done — per phase + final

**Per-phase DoD (mechanical gate, doctrine §3):**

- **Fase 0 DoD:** all 6 invariant WOs (WO-001..006) pass their `REQ-INV-*` tests **and** their named drills (`DRILL-AUDIT-TAMPER/-COMPLETENESS`, `-DUPLICATE-REPLAY`, `-VERSION-PIN`, `-CROSS-TENANT-DECRYPT`/`-PHI-EGRESS-SCRUB`, `-POLLER-KILL`, `-NOTIFICATION-BLACKHOLE`); the alert-compiler + SYS gates (A/B/C) fail on seeded defects; `check_units.py --strict` green. No real patient data touches the system before this closes (`IMP-C-01..06` "antes do primeiro paciente real").
- **Fase 1 DoD:** kept modules hardened; AUDIT-001/002/003/007/008 corrected (pending-flags journaled); L1 (266 vectors) + L2 property suites green; contract job green from `openapi.yaml`/`asyncapi.yaml`; coverage ≥80% (≥95% scorer/engine); design-token system + `check_tokens.py` strict green.
- **Fase 2 DoD (per domain):** all `<domain>.yaml` vectors pass L1; band-partition/criterion-coverage/facade gates green; UI surface passes a11y AA (AAA critical values) + visual-regression; correlation engine only after ≥2 domains live and its fold proven HAZ-026-safe; PPV instrumentation emitting.
- **Fase 3 DoD:** SSO/ABAC/KMS live; DR drill meets RPO/RTO; pentest clean; ANVISA cadastro + LGPD RIPD filed.
- **Fase 4 DoD:** Alt-B trigger instrumented; decision journaled (activate/defer) with CTO+AMH sign-off if activated.

**Final DoD (staging, before first real patient / pilot):** SLOs met in staging — **owned-pipeline p95 < 30 s** (`VIS-C-09`, NRT Σ≈9 s / micro-batch Σ≈16 s per `alert-engine.md` §8), **storm ≥ 500/min** with p95 held and zero loss (`VIS-C-11`, `test-strategy.md` §5), **PPV instrumentation live** (`VIS-7.1-02` ≥0.60 measured, fatigue ≤10%); **a11y gates** green (WCAG 2.2 AA floor / AAA critical); **security review** passed (pentest, RIPD, DENY-BY-DEFAULT roles); **all 6 invariants verified** by their named drills (`test-strategy.md` §6/§7) on the release candidate; every shipped alert **traceable** (Section 6) and every pending-RATIFY default **flagged, never silent** (Section 4). Clinical validation (CLIN-001 48 h real HL7; CLIN-002 gold-standard protocol) signed.

---

*Provenance: this blueprint was authored by reading `CONTRACTS.md`, `HANDOFF.yaml`, briefs (`implementation-plan.json`, `adr-001.json`, `vision.json`), `architecture/{system-architecture,alert-engine,data-model}.md`, `delivery/test-strategy.md`, `observability-slo.md`, `security-lgpd.md`, `RATIFICATION.md`, `_work/adrs/operational-vitals-ingress.md`, the 9 `_work/alerts/*.yaml` catalogs (50 alerts / 266 vectors), the gate scripts, and the on-disk v1 code (`src/intensicare/` — 40 modules / ~4.9k LoC — and `frontend/`). Divergences from the source directive are recorded in Section 1 (v1 frontend exists on disk) and Section 0 (verify-on-disk doctrine).*
