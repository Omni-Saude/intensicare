# Test Strategy — IntensiCare v2

**Owner:** qa-test-strategist · **Status:** draft for reconciliation barrier **C3** · **Authority precedence:** vision ≻ directive ≻ audit (CONTRACTS §5).

This document specifies how every clinical and technical guarantee made elsewhere in the plan gets **verified, automatically, before and after every deploy**. It does not re-derive clinical thresholds (they live in `docs/plan/_work/alerts/*.yaml` and `docs/plan/clinical/`), architecture (`docs/plan/architecture/alert-engine.md`, `data-model.md`, `security-lgpd.md`, `observability-slo.md`), or CI mechanics (`docs/implementation-plan.md` §4) — it is the **test layer that proves those documents are true in running code**. Every claim below cites a source: a brief fact (`VIS-*`, `IMP-*`, `MEWS-*`/`NEWS2-*`/`SOFA-*`/`qSOFA-*`), a ledger constraint (`CON-*`), an invariant (`INV-1..6`), or an existing `REQ-INV-*` verification-register row this document operationalizes into runnable tests.

> **Scope boundary.** `alert-engine.md §10`, `data-model.md §9`, `security-lgpd.md §7`, and `observability-slo.md §8` already declare **what** must be true for each `REQ-INV-*` row and sketch a one-line test idea in their "Verification" column. This document is the **test-execution layer**: concrete suites, fixtures, drill names, tooling, cadence, and CI wiring that discharge those rows. Where this document names a test that does not exist yet in `tests/`, that is a build gap flagged for the owning team (named per row), not a silent assumption.

---

## 1. Test pyramid for clinical decision-support software

A conventional unit/integration/e2e pyramid under-tests the two things that actually kill or hurt a patient in this system: a **wrong clinical threshold** compiled once and fired thousands of times, and a **silent** platform failure (stale poll, dropped alert, un-audited mutation). The pyramid below adds two clinical-specific layers (rule vectors, property-based scorer tests) below the conventional integration layer, and keeps chaos/drills as a standing top layer that runs on every release, not only after incidents.

```
                        ▲  fewer, slower, closer to production
        ┌───────────────────────────────────────────────┐
        │  L7  Chaos / failure drills (6 invariants)     │  scheduled + pre-release gate
        ├───────────────────────────────────────────────┤
        │  L6  Alert-storm load tests (>500 alerts/min)  │  nightly + pre-release gate
        ├───────────────────────────────────────────────┤
        │  L5  Visual regression + a11y automation       │  every PR touching UI
        ├───────────────────────────────────────────────┤
        │  L4  Contract tests (Athena/Gold, HL7, FHIR)   │  every PR (mocked) + nightly (live sandbox)
        ├───────────────────────────────────────────────┤
        │  L3  Integration tests (API, DB, Redis, ARQ)   │  every PR (Job 2, existing)
        ├───────────────────────────────────────────────┤
        │  L2  Property-based scorer tests (hypothesis)  │  every PR (Job 2, existing suite extended)
        ├───────────────────────────────────────────────┤
        │  L1  Rule test vectors (alert-catalog fixtures)│  every PR (Job 2, new suite)
        └───────────────────────────────────────────────┘
                        ▼  more, faster, run on every commit
```

L1 and L2 are the clinical-correctness floor and must be **the fastest and most numerous** — they run in-process, no DB, no network, sub-second per test. L4 is split mocked/live because Athena/Gold sandbox access is a shared, rate-limited external dependency (`ADR001-C-01`); the mocked contract tests run on every PR, the live-sandbox variant runs nightly and is not a PR-merge gate. L6/L7 are expensive and disruptive by design (they inject faults and generate load) and therefore run pre-release and on a schedule rather than per-commit — but every one of them still maps to a specific `REQ-INV-*` row (§7) so "runs less often" never means "guarantees less."

---

## 2. Layer 1 — Rule test vectors: the alert catalog's `test_vectors` ARE the test suite

**This is not a new artifact.** `docs/plan/_work/alerts/*.yaml` (9 domain files — `sepsis.yaml`, `aki.yaml`, `respiratory.yaml`, `hemodynamics.yaml`, `neuro-sedation.yaml`, `electrolyte.yaml`, `pharmaco-interaction.yaml`, `early-warning-scores.yaml`, `correlation-engine.yaml`; 2,490 lines total) already define, per alert, a `test_vectors` block with a stable shape:

```yaml
test_vectors:
  - {id: TV-1, kind: fire, inputs: {creatinina: 1.6, creatinina_basal: 1.0, debito_urinario_horario: 0.9},
     expected: fire, note: "Cr 1.6 = 1.6x baseline (>=1.5x) -> stage 1 -> watch"}
  - {id: TV-5, kind: boundary, inputs: {creatinina: 1.5, creatinina_basal: 1.0, ...},
     expected: fire, note: "Cr exactly 1.5x baseline -> stage 1 (>=1.5x inclusive) ..."}
```

Every alert carries 4–7 vectors of three `kind`s: `fire` (true positive), `no-fire` (true negative, including the deliberately-adjacent "almost fires but a gate blocks it" cases — e.g. AKI nephrotoxin TV-3, where the drug combo is present but the renal signal isn't), and `boundary` (exact-threshold edge cases — e.g. sepsis lactate `2.0` must NOT fire, `2.01` must fire, per the strict `>` in the SSC-2021 anchor). This is a richer contract than most rule-engine test suites get for free, and duplicating it as hand-written pytest cases would create exactly the drift risk (two sources of truth for the same threshold) that `MEWS-C-01`/`NEWS2-C-01`/`SOFA-C-01`/`qSOFA-C-01` ("thresholds MUST NOT change; behavior-preserving refactor only") exist to prevent.

### 2.1 Execution contract

- **Harness:** `tests/rules/test_alert_vectors.py` (new) is a thin YAML-driven pytest parametrization, not a rule reimplementation. It:
  1. Globs `docs/plan/_work/alerts/*.yaml`, parses each `alerts[].test_vectors[]`.
  2. Builds a pytest `parametrize` id of `{domain}::{alert_id}::{test_vector.id}` (e.g. `aki::ALERT-AKI-KDIGO-STAGE-01::TV-5`) so a failing vector reports exactly which clinical rule broke, not a generic assertion line number.
  3. Feeds `inputs` into the alert-engine's rule evaluator for that `alert_id` (the `evaluate_alert_definition(alert_id, inputs) -> fired: bool` entry point owned by `alert-engine.md` §2–3) and asserts the boolean matches `expected in {fire, boundary→fire/no-fire per its own expected field}`.
  4. Fails the build (not skips) if any `alert_id` referenced by a YAML file has no matching definition loaded by the engine — this is the trip-wire that catches "catalog says X fires, code doesn't implement X yet" before it reaches a bed.
- **Freshness gate:** a companion check (`scripts/check_vector_coverage.py`, mirrors the existing `scripts/check_units.py` draft/strict convention) fails CI in `strict` mode if any `alert_id` in the loaded rule engine has **zero** `test_vectors` in its catalog entry — every shippable alert must carry executable proof of its own fire/no-fire/boundary behavior before merge.
- **Independence from implementation:** the harness never imports the alert-engine's internal threshold constants to construct expectations — `expected` is read verbatim from the YAML, which is itself sourced from `vision.md` §3.1–§3.7 (evidence-cited thresholds). This is what makes it a **rule test**, not a mirror of the code under test: a bug that hardcodes the wrong constant in both the engine and a hand-written assertion would pass a self-referential test but fails here because the vector's expected value traces to the vision brief, not the code.
- **Reconciliation vectors:** several vectors encode a *boundary between two alerts*, not just a single alert's edge (e.g. AKI nephrotoxin TV-3 documents "owned by pharmaco DDX-003, not this alert" when the renal signal is absent). These are tagged and cross-checked: the harness additionally asserts the *other* named alert (`DDX-003`) fires on the same input where the vector says it should, catching the classic two-rules-both-silent or two-rules-both-loud regression at domain boundaries.

### 2.2 Coverage math

2,490 lines / 9 domains, ~5–7 vectors per alert, ~40+ alerts across the catalog → **≈220–280 rule test vectors**, each a deterministic, sub-millisecond assertion. This is the single highest-leverage test investment in the plan: it is 1:1 traceable to the clinical evidence citations in `vision.md`, requires no test-writer clinical judgment (the vector is already adjudicated), and directly defends the PPV/alarm-fatigue targets (`VIS-7.1-02` ≥0.60, `VIS-7.1-04` ≤10% ignored) by proving the no-fire and boundary cases as rigorously as the fire cases.

---

## 3. Layer 2 — Property-based tests for scorers (Hypothesis)

The four early-warning scorers (`src/intensicare/services/{mews,news2,sofa,qsofa}.py`) are exhaustively banded, pure, deterministic functions (`SCORERS-C-01`: identical inputs → identical outputs; `SCORERS-C-02`: `None` inputs → 0 points, tracked separately). That purity is exactly what makes them property-testable instead of example-testable: example tests (already in `tests/test_mews.py`, `test_news2.py`, `test_sofa.py`, `test_qsofa.py`) prove specific points on the curve; property tests prove the **shape** of the curve holds everywhere, including inputs no one thought to write an example for.

**Tooling:** `hypothesis>=6.100,<7.0` added to the `test` optional-dependency group in `pyproject.toml` (alongside existing `pytest`/`pytest-asyncio`); new module `tests/property/test_scorer_properties.py`.

### 3.1 Monotonicity properties

For every scorer, worse physiology must never score better. Concretely, for each component in isolation (holding all other inputs fixed at a normal value):

- **MEWS heart rate** — `calculate_mews` component score is non-increasing as HR moves from 51–100 (normal, 0 pts) toward either the bradycardic (`≤40`) or tachycardic (`≥130`) extreme, i.e. it is **U-shaped, monotonic on each side of the normal band**, never non-monotonic within a side (`MEWS-1-04..09`).
- **MEWS systolic BP** — same U-shape property, with the added constraint that severe hypotension (`≤70`, 3 pts) must score **strictly higher** than severe hypertension (`≥200`, 2 pts) — an asymmetric U, so the property test parametrizes each side independently rather than assuming symmetry (`MEWS-1-10..14`).
- **NEWS2 respiratory rate, SpO₂ (both scales), systolic BP, heart rate, temperature** — each is independently U-shaped or monotonic per `NEWS2-2-07..14`; the SpO₂ property test runs **twice**, once per scale (`hypercapnic=False` / `True`), asserting the two scales are independently monotonic and that Scale 2's normal band (`≥93%`) sits at a lower absolute SpO₂ than Scale 1's (`≥96%`) — this directly encodes the clinical intent of `NEWS2-C-02` (two distinct scales) as a checkable property rather than a comment.
- **SOFA respiration, coagulation, liver, renal (creatinine axis)** — each of the four is monotonic across its full 0–4 band as the underlying physiological variable worsens (`SOFA-3-08..10`, `SOFA-3-15`).
- **SOFA renal composite** — `score_renal(creatinine, urine_output) == max(score_from_creatinine, score_from_urine_output)`, **never the sum** — this is `SOFA-C-03` as an executable property: generate random `(creatinine, urine_output)` pairs and assert the composite never exceeds either individual axis's max, and equals whichever axis scores higher.
- **SOFA cardiovascular** — monotonic in vasopressor dose within a fixed pressor type (`SOFA-3-12/13`), and a categorical property that a patient on **any** pressor scores `≥2`, strictly higher than a patient at target MAP with no pressor (`SOFA-3-11`), regardless of the exact dose.
- **qSOFA** — each of the 3 binary criteria is independently a step function (0 below threshold, 1 at/above `QSOFA-4-05/06/07`); the composite is the arithmetic sum, so a property test asserts `calculate_qsofa` output is always `sum(criterion_i)` for `hypothesis`-generated `(rr, sbp, gcs)` triples — this also mechanically proves `qSOFA-4-08`'s risk-category cutoff (`≥2` high risk) is consistent with the per-criterion definitions, closing a class of "someone changed one criterion's threshold and forgot the composite" regressions.

### 3.2 Band-edge (boundary) properties

Every named threshold constant in the scorer briefs (`MEWS_HR_BRADY_SEVERE_MAX = 40`, `NEWS2_RED_SCORE = 3`, `SOFA_MAP_NORMAL = 70`, `QSOFA_RR_TACHYPNEA_MIN = 22`, etc. — `MEWS-1-04..28`, `NEWS2-2-04..14`, `SOFA-3-04..16`, `qSOFA-4-04..07`) gets a **generated** boundary test, not a hand-picked one: `hypothesis.strategies.integers()`/`floats()` constrained to `[threshold-1, threshold, threshold+1]` (and, where the brief specifies strict-vs-inclusive — e.g. qSOFA "≥22" is inclusive, sepsis "lactate > 2" is strict — the correct comparison operator is asserted, not just "some change happens at the boundary"). This is the property-test analogue of the alert-catalog's `boundary` test-vector kind (§2) but at the *component-scorer* level rather than the *alert-firing* level — together they give two independent boundary proofs (scorer band edge, alert firing edge) for every clinical number that appears in both a scorer and a downstream alert (e.g. qSOFA feeds `ALERT-SEPSIS-SCREEN-01`/`-ORGAN-02`).

- **Total-score range invariants:** `calculate_mews(...) ∈ [0, 15]` (`MEWS-1-03`), `calculate_news2(...).score ∈ [0, 20]` (`NEWS2-2-03`), `calculate_sofa(...).score ∈ [0, 24]` (`SOFA-3-03`), `calculate_qsofa(...).score ∈ [0, 3]` (`qSOFA-4-03`) — each asserted for **any** hypothesis-generated input combination, including all-`None` (which must score 0 per `SCORERS-C-02`, not raise).
- **Determinism/purity property:** call each scorer twice with the same hypothesis-generated input; assert bit-identical output (`SCORERS-C-01`). This is cheap insurance against an accidental hidden-state bug (e.g. a memoization cache keyed wrong) that no example test would catch because example tests, by construction, only ever call a function once per case.
- **MEWS trend property (`MEWS-1-29`, `MEWS-C-02`):** `compute_trend([single_score])` must return `None` (below the 2-sample minimum) for any hypothesis-generated single-element list; `compute_trend([s1, s2, ...])` with a hypothesis-generated **monotonically increasing** sequence must return `"increasing"`, and symmetrically for decreasing/stable — this generates the trend-direction proof across arbitrarily long sequences instead of the 2–3 example sequences a hand-written test would use.

### 3.3 Non-goals (explicit)

Property tests do **not** replace the alert catalog's evidence-cited example vectors (§2) — they prove the scorer's *internal consistency* (shape, range, determinism), not that a given band boundary is the *clinically correct* one (that provenance is the literature citation in `MEWS-1-02`/`NEWS2-2-02`/`SOFA-3-02`/`qSOFA-4-02`, verified by a clinical reviewer, not a test). A property test suite that passed on a scorer with every threshold shifted by 10% would still be "monotonic" — this is why L1 and L2 are both mandatory, not either/or.

---

## 4. Layer 3 — Contract tests for AMH integration (Athena schemas, Gold write-back)

`ADR001-C-01`/`CON-0001` establishes that IntensiCare performs **no ingestion of its own** and reads all clinical source data from the AMH Gold layer via Amazon Athena; `ADR001-C-04`/`CON-0004` establishes a write-back obligation to Gold `fact_patient_score`/`fact_alert`. Both directions are **cross-team contracts** — a schema drift on either side (AMH renames a Gold column, or IntensiCare's write-back payload silently drops a required field) fails silently in production because neither side's own test suite exercises the other's schema. Contract tests close that gap.

### 4.1 Read-side contract — Athena/Gold schemas

- **Schema-conformance test (`tests/contract/test_gold_read_schema.py`, mocked):** for each domain's declared `inputs[].source` in `docs/plan/_work/alerts/*.yaml` (e.g. `"AMH Gold lab_result (LOINC 2160-0)"`), assert the mocked Athena query response fixture (`tests/fixtures/gold/*.json`, one per Gold table IntensiCare reads: `lab_result`, `Observation`, `DiagnosticReport`, `MedicationRequest`/`MedicationAdministration`, `Procedure`, `Condition`) has the expected column names, types, and the cited LOINC code present in the fixture data. This runs on **every PR** — no live Athena dependency, pure schema-shape assertion against a versioned fixture.
- **Consumer-driven contract (Pact-style, nightly against a live/sandbox Gold dataset):** `tests/contract/test_gold_read_live.py`, gated behind an `AMH_SANDBOX` env flag, runs the **same** query shapes the micro-batch runner issues in production (high-watermark incremental poll, column-projected — never `SELECT *`, per `security-lgpd.md` I4) against a real or sandboxed Gold/Athena endpoint and asserts the response still matches the fixture schema. A drift here is the earliest possible signal that AMH changed a Gold table shape — it fails the nightly job, not a 3am page during real ingestion.
- **Staleness/freshness contract:** each `inputs[].staleness_max` value in the alert catalog (e.g. `PT24H` for creatinine, `PT1H` for continuous vitals) is asserted against `ADR001-F-02`'s Gold batch-freshness SLO (p95 < 30 min) — a unit test in `tests/contract/test_staleness_budget.py` fails if any alert declares a `staleness_max` tighter than the Gold pipeline can honor for a Gold-sourced (non-NRT) input, catching the class of bug where a clinical author writes a staleness window that AMH's own SLO cannot satisfy (`ADR001-C-10`/`CON-0010`).

### 4.2 Write-side contract — Gold write-back

- **Payload-shape contract (`tests/contract/test_gold_writeback.py`):** asserts every write-back to `fact_patient_score`/`fact_alert` carries `mpi_id` (no locally-minted patient identifier — `ADR001-C-02`/`CON-0002`), `algorithm_version`/`definition_version` (`REQ-INV-3-3`, data-model.md §9), and **no direct identifiers** (`nome`/`CPF`/`CNS`/`display_name`/`mrn`) — the PHI-minimization boundary `REQ-INV-4-S3` (`security-lgpd.md` §7). This is a schema-and-content assertion together: right shape, right columns present, wrong columns (PHI) provably absent.
- **Idempotent write-back property:** replaying the same score/alert write-back twice (same `mpi_id` + `recorded_at` + `algorithm_version`) must not create a duplicate Gold fact row — mirrors the ingestion-idempotency invariant (INV-2, §7) applied to the outbound direction, using the same natural-key `ON CONFLICT` discipline.
- **Schema-version compatibility:** `ADR001-C-09` requires schema-versioned writes; a contract test asserts the write-back payload declares its schema version and that a Gold-side schema-registry fixture accepts it — this is the pairing test to the read-side drift detector above, so both directions of the AMH boundary are defended.

### 4.3 HL7/FHIR synthetic fixtures

The MLLP listener (`src/intensicare/mllp_listener.py`, `tests/test_mllp_listener.py` already exists) and the FHIR client (`src/intensicare/fhir/client.py`, `tests/test_fhir.py` already exists) both need a **corpus of synthetic messages**, not just the handful of examples in current tests, to exercise the full domain-input surface the alert catalog declares:

- **`tests/fixtures/hl7/`** — synthetic ORU^R01 messages covering: (a) the happy path per vital-sign type referenced across the catalog (HR, RR, SBP, temp, SpO₂ — `VIS-2.5`/`aki.yaml`/`respiratory.yaml` inputs); (b) a **duplicate `MSH-10`** message (proves `REQ-INV-2` ingestion idempotency, §7); (c) malformed/partial segments (missing `OBX`, truncated message, wrong encoding) to exercise the parser's error path without crashing the listener; (d) ventilator-manufacturer-specific `OBX` segments referenced in `VIS-3.3-09` ("manufacturer-specific OBX segments") — at least two synthetic vendor variants so the respiratory domain's mapping logic isn't validated against only one shape.
- **`tests/fixtures/fhir/`** — synthetic FHIR R4 Bundles for every resource type the catalog's `inputs[].source` cites: `Observation` (vitals, labs, RASS/CAM-ICU, blood gas), `DiagnosticReport` (cultures), `MedicationRequest`/`MedicationAdministration` (antimicrobials, vasopressors, sedatives), `Condition` (suspected-infection documentation), `Procedure` (RRT, contrast administration). Each fixture is built to satisfy exactly one alert-catalog test vector's `inputs` (§2), so the same logical scenario (e.g. AKI TV-1: `creatinina: 1.6, creatinina_basal: 1.0`) has both a rule-vector-level assertion (engine fires) and an ingestion-level fixture (a FHIR `Observation` bundle that, once parsed, produces those exact field values) — this closes the gap between "the rule is correct" (L1) and "the pipeline correctly produces the rule's inputs from a real message" (L4).
- **Generation discipline:** fixtures are hand-authored from the LOINC codes already declared per input in the catalog (e.g. `LOINC 2160-0` creatinine, `LOINC 2524-7` lactate) — never invented ad hoc — so a fixture review is a spot-check against the catalog's own `source` field, not a fresh clinical judgment call.

---

## 5. Layer 5 — Alert-storm load tests (>500 alerts/min, `VIS-7.2-03`)

`VIS-7.2-03`/`VIS-C-11` requires processing throughput **>500 alerts/min**; `VIS-C-09` requires ingestion-to-alert p95 latency **<30s** even under that load — the two must be tested **together**, not independently, because a naive load test that only checks throughput can hide a latency collapse at the p95/p99 tail exactly when a real mass-casualty or multi-unit-deterioration event would need the system most.

- **Tooling:** `locust` (Python-native, integrates with the existing async FastAPI stack) driving synthetic HL7/FHIR traffic from the §4.3 fixture corpus at controlled rates, plus a direct alert-engine micro-benchmark (`pytest-benchmark`) for the pure rule-evaluation hot path in isolation from I/O.
- **`test_storm_baseline`** — steady-state 500 alerts/min for 10 minutes; assert p95 ingestion→alert latency stays **<30s** (`VIS-C-09`) throughout, not just at the start; assert zero dropped/lost alerts (cross-checked against `REQ-INV-6` delivery guarantees, §7).
- **`test_storm_burst`** — a 3x burst (1,500 alerts/min) sustained for 60 seconds atop the 500/min baseline, simulating a multi-bed simultaneous-deterioration event (e.g. a unit-wide sepsis screening sweep after a shift-change batch of labs lands in Gold) — asserts the system degrades **gracefully** (queue depth bounded, backpressure applied, no crash) rather than silently dropping alerts; this is the throughput analogue of the chaos drills in §6 and is where ARQ's retry/backoff behavior (`INV-6`) is exercised under real load rather than fault-injection alone.
- **`test_storm_ppv_fleet_floor`** — replays a **volume-weighted mix** of the alert catalog's own `ppv_budget.est_volume_per_100_beds_day` figures (e.g. sepsis screen ~7/100-beds/day, AKI staging ~5/100-beds/day) scaled up to storm rate, to catch a class of bug that pure-synthetic uniform-traffic load tests miss: rules with heavier per-alert compute (e.g. `ALERT-SEPSIS-SCREEN-01`'s multi-branch SIRS/qSOFA/infection-gate logic) becoming the throughput bottleneck when their real-world share of traffic is disproportionately represented.
- **Capacity ceiling / soak:** a longer (2h) soak at 500/min checks for resource leaks (connection pool exhaustion, Redis memory growth, ARQ queue backlog creep) that a 10-minute burst test cannot surface — ties to the capacity model in `observability-slo.md` §6 (30 → 90 beds → multi-hospital scaling).
- **Gate:** all four scenarios run **pre-release** (not per-PR — they take real wall-clock time and dedicated infrastructure) and their pass/fail is a release gate; `test_storm_baseline`'s p95 metric is also wired into the Grafana dashboard (a) described in `observability-slo.md` §1.2 so the same number that gates a release is the number on-call watches in production.

---

## 6. Layer 6 — Chaos / failure drills against the six invariants

Each of the six pre-first-patient invariants (`IMP-C-01..06` / `CON-0066..0071` / `INV-1..6`) already has a **verification-register row** naming a test idea (`alert-engine.md` §10, `data-model.md` §9, `security-lgpd.md` §7, `observability-slo.md` §8). This section names the **drill** — a scheduled, repeatable, actively-fault-injecting exercise — that discharges each row, distinct from the always-on unit/integration tests that also touch the same invariant.

| # | Invariant | Drill name | What it injects | Pass criterion | Discharges |
|---|---|---|---|---|---|
| 1 | Immutable audit trail | **DRILL-AUDIT-TAMPER** | Direct `UPDATE`/`DELETE` attempt against a seeded `audit_trail` row, via both the app's DB role and a raw psql session with elevated (but non-superuser) privileges | Every attempt raises/blocks via `trg_audit_trail_immutable`; row bytes unchanged before/after; the *attempt itself* is not silently swallowed (it errors visibly to the caller) | `REQ-INV-1-1`, `REQ-INV-1-S2` |
| 1 | Immutable audit trail | **DRILL-AUDIT-COMPLETENESS** | Drive every mutating/PHI-read endpoint (alert ack/resolve, threshold edit, definition-version mint, login, PHI read) through a full request cycle and diff the audit table before/after | Exactly one new `audit_trail` row per action, correct `actor`/`action`/`entity_id`, `request_id` ties to the OTEL trace | `REQ-INV-1-2`, `REQ-INV-1-S1` |
| 2 | Ingestion idempotency | **DRILL-DUPLICATE-REPLAY** | Feed the identical HL7 message (same `MSH-10`) twice via MLLP, and re-run the identical Athena/Gold poll window twice | Exactly one `vital_sign`/fact row each time; no duplicate alert fired from the replay | `REQ-INV-2` |
| 3 | Algorithm versioning | **DRILL-VERSION-PIN** | Fire an alert under definition v_n, bump the alert definition to v_n+1 (new threshold), then re-query the original alert | Original alert still resolves to v_n's exact body/threshold, not v_n+1's — historical reproducibility over the 7-year retention window (`DM-RP-03`) | `REQ-INV-3-1`, `REQ-INV-3-2`, `REQ-INV-3-3` |
| 4 | Encryption at rest | **DRILL-CROSS-TENANT-DECRYPT** | Attempt to decrypt tenant A's `patient_cache` PHI columns using tenant B's per-tenant KMS-issued DEK | Decrypt fails for every field; raw table bytes/`pg_dump` show ciphertext only, no plaintext PHI leak on the failed attempt | `REQ-INV-4-1`, `REQ-INV-4-2`, `REQ-INV-4-S1`, `REQ-INV-4-S2` |
| 4 | Encryption at rest | **DRILL-PHI-EGRESS-SCRUB** | Force a Gold write-back, a notification dispatch, and a log/trace emission for a patient carrying full PHI, then scan all three egress payloads | Zero occurrences of `nome`/`CPF`/`CNS`/`MRN`/`display_name` in any of the three payloads; only `mpi_id` + aggregates present | `REQ-INV-4-S3` |
| 5 | Health check / dead-man's switch | **DRILL-POLLER-KILL** | Kill the micro-batch Athena poller process mid-cycle; separately, stop the NRT operational stream feed | External watchdog pages on-call within the ≤30s probe interval (`VIS-C-09`-aligned); `/api/v1/health` readiness flips to degraded for the affected component; alert-on-no-alerts staleness monitor fires per the `(unit, domain)` thresholds in `observability-slo.md` §4.3 | `REQ-INV-5` |
| 6 | Retry with backoff | **DRILL-NOTIFICATION-BLACKHOLE** | Drop every delivery-channel ack (WS, mobile push) so every notification attempt appears to fail | ARQ retries exhaust per the tiered backoff policy (`observability-slo.md` §5.1), the notification lands in the DLQ, DLQ arrival raises an operational alert, and client-side dedup on `dedup_key` guarantees no duplicate is shown once delivery eventually succeeds | `REQ-INV-6` |

**Cadence and gate.** All six drills run (a) on every release candidate as a **release gate** (a drill failure blocks promotion to staging/prod — these are the six things the vision explicitly says must exist "before the first real patient," so they are treated with first-patient severity indefinitely, not just at MVP cut-over), and (b) on a standing weekly schedule against staging, independent of any release, to catch regressions introduced by unrelated infrastructure changes (a Redis upgrade, a network-policy change) that no code-level PR would trigger. Each drill run's pass/fail and timing (e.g. DRILL-POLLER-KILL's actual page latency vs the 30s budget) is recorded and trended — a drill that "passes" at 29s today and creeps toward 30s over successive runs is itself a signal, not just a boolean gate.

**Ownership note.** The ledger (`docs/plan/_work/constraints/ledger.yaml`) assigns implementation ownership of each invariant's underlying mechanism to a named architect role (`CON-0066`→data-architect, `CON-0067`→amh-integration-architect, `CON-0068`→data-architect, `CON-0069`→security-architect, `CON-0070`→platform-reliability-engineer, `CON-0071`→alert-engine-architect). This document does not reassign that ownership — QA owns the **drill harness and gate**; each named architect owns the **mechanism the drill exercises**, and is the required reviewer when their drill fails.

---

## 7. REQ-INV traceability matrix

Every invariant maps to at least one test/drill; most map to several across layers, which is intentional — an invariant this severe (pre-first-patient, "DEVE ser implementado") should never depend on a single test passing.

| Invariant | REQ-INV row(s) (existing register) | Test/drill(s) in this strategy | Layer |
|---|---|---|---|
| **INV-1** — immutable audit trail | `REQ-INV-1-1`, `REQ-INV-1-2`, `REQ-INV-1-3` (data-model.md §9); `REQ-INV-1-S1..S3` (security-lgpd.md §7) | DRILL-AUDIT-TAMPER, DRILL-AUDIT-COMPLETENESS + existing integration tests per mutating endpoint | L3, L7 |
| **INV-2** — ingestion idempotency | `REQ-INV-2` (alert-engine.md §10) | DRILL-DUPLICATE-REPLAY + HL7 fixture (c) duplicate-`MSH-10` case (§4.3) + Gold-poll-replay contract test (§4.2) | L3, L4, L7 |
| **INV-3** — algorithm versioning | `REQ-INV-3-1`, `REQ-INV-3-2`, `REQ-INV-3-3` (data-model.md §9) | DRILL-VERSION-PIN + write-back version-column contract test (§4.2) + scorer `algorithm_version` string assertions (existing `MEWS-1-01`/`NEWS2-2-01`/`SOFA-3-01`/`qSOFA-4-01` example tests) | L3, L4, L7 |
| **INV-4** — encryption at rest | `REQ-INV-4-1..3` (data-model.md §9); `REQ-INV-4-S1..S3` (security-lgpd.md §7) | DRILL-CROSS-TENANT-DECRYPT, DRILL-PHI-EGRESS-SCRUB + write-back PHI-absence contract test (§4.2) | L4, L7 |
| **INV-5** — health check / dead-man's switch | `REQ-INV-5` (alert-engine.md §10; observability-slo.md §8) | DRILL-POLLER-KILL + `/api/v1/health` readiness contract test (blocked on the build gap noted in `observability-slo.md` §4.1 — flagged, not silently assumed done) | L7 |
| **INV-6** — retry with backoff | `REQ-INV-6` (alert-engine.md §10; observability-slo.md §8) | DRILL-NOTIFICATION-BLACKHOLE + `test_storm_baseline`/`test_storm_burst` delivery-loss assertions (§5) | L6, L7 |

---

## 8. A11y test automation

`docs/plan/design/accessibility-standard.md` sets a **WCAG 2.2 AA floor everywhere, AAA ceiling for critical clinical values** and enumerates a numbered `A11Y-REQ-*`/`A11Y-GATE-*` register (contrast ratios, focus geometry, motion/reduced-motion, dialog semantics, target sizes, authentication). This is tested at two tiers:

- **Automated, every PR touching UI:** `axe-core` (via `@axe-core/playwright` or equivalent) run against every screen in CI, asserting zero WCAG 2.2 AA violations — this catches the mechanically-checkable subset (missing labels, contrast ratios computed against real relative-luminance math per `design-tokens.md`, focus-order, ARIA role/attribute correctness) automatically and cheaply. Contrast assertions specifically re-derive the ratios `design-tokens.md` already computed (e.g. dark-theme text-on-canvas 15.8:1) as a **regression** check — a token change that silently drops a ratio below 4.5:1 (`A11Y-REQ-03`) fails the build, not a design review months later.
- **Targeted automated checks for the register's non-generic items** — items `axe-core` cannot verify by itself get purpose-built assertions: focus-appearance geometry for the critical-alert acknowledge control (`A11Y-REQ-13`, AAA focus indicator ≥2px/≥3:1, since this is the control a stressed clinician tabs to under the ack SLA); pointer-target-size floors (24×24 general / 44×44 for ack/primary actions, `A11Y-REQ-20`/`-21`, `A11Y-GATE-11`); `prefers-reduced-motion`/`prefers-contrast: more` media-query honoring (`A11Y-REQ-14`/`-24`) via a headless-browser emulated-media test matrix; dialog stack-depth ≤2 and focus-trap/restore correctness (`A11Y-REQ-07/10/11`) via component-level interaction tests; the SC 3.3.8 authentication-cognitive-test exemption (`A11Y-REQ-25`) verified by asserting the login flow contains no puzzle/transcription/calculation step.
- **Manual, pre-release:** a screen-reader pass (VoiceOver + NVDA minimum, matching the two most common assistive-tech stacks) on the alert-acknowledge flow and the bed-board grid specifically — these are the two flows the accessibility standard singles out as safety-critical (an alert a screen-reader user cannot perceive or acknowledge is a patient-safety gap, not a cosmetic one) and are not fully substitutable by automation; findings feed back into the `A11Y-REQ-*` register rather than being tracked ad hoc.
- **Gate:** `A11Y-GATE-*` checklist items (accessibility-standard.md's own gate list, e.g. `A11Y-GATE-11`) are wired as required PR checks for any diff touching `src/**/*.{css,ts,tsx}` component code — mirroring the existing `check_tokens.py`/`check_units.py` draft/strict pattern already established for token and unit governance in this codebase.

---

## 9. Visual regression

The design-token system (`design-tokens.md`) defines a single semantic graph resolved into **two runtime-switchable themes** (dark/light, `data-theme` attribute, no bundle swap) with clinically-meaningful `clinical.*` severity tokens that are structurally forbidden from referencing `brand.*` — a visual regression suite is what proves that separation holds pixel-for-pixel, not just at the token-JSON level.

- **Tooling:** Playwright's built-in screenshot-diffing (`toHaveScreenshot`) or Chromatic, snapshotting every screen in **both themes** and, for severity-bearing components (alert cards, bed-board tiles, score badges), under **each severity level** (`normal|watch|urgent|critical`) — the state space that actually matters clinically, not just "the page looks the same."
- **Priority surfaces (from the design brief):** the bed-board grid (dark-theme default for monitor-wall mode, `A11Y-REQ-22`), the alert-acknowledge dialog (focus geometry + severity color are both safety-relevant), score-trend sparklines/charts, and the embossed/neumorphic surfaces called out as needing an explicit contrast check in both themes (`CON-0037`) — these are exactly the components most likely to visually regress silently when a shared primitive changes.
- **CVD (color-vision-deficiency) simulation:** `design-tokens.md`/`accessibility-standard.md` reference a "3-CVD-simulation ΔE check" method for severity colors — this is automated as a visual-regression variant: each severity-bearing snapshot is additionally rendered through a protanopia/deuteranopia/tritanopia filter and diffed against a stored baseline, asserting severity remains distinguishable by shape/icon/outline (not color alone, `A11Y-REQ-02`) even when color information is degraded.
- **Cadence:** every PR touching `src/**/*.{css,ts,tsx}` or `tokens/**` runs the full snapshot matrix; a diff requires explicit human approval (updating the baseline) — this is a **review gate**, not an auto-pass/auto-fail, because a legitimate design change will always produce a pixel diff; the value is forcing every visual change through a human decision point rather than shipping silently.
- **Token-drift trip-wire:** paired with the existing `scripts/check_tokens.py` build-time check (any `var(--...)` reference that doesn't resolve to a Style-Dictionary-emitted name fails the build) — visual regression catches *rendered* drift, `check_tokens.py` catches *referential* drift; both are needed because a token can resolve successfully to the wrong value without either check alone catching it.

---

## 10. Coverage targets + CI wiring

### 10.1 Coverage targets

`IMP-C-17` records an **unresolved conflict** between the CI job's enforced gate (`≥80%`, `IMP-4.3-01` Job 3) and the phased quality-metrics table (`≥70%` MVP / `≥85%` Production, §7.2 line 459) — the implementation-plan brief explicitly declines to reconcile this ("not resolved here per precedence rule"). This document does not silently pick a number either; it records the operational reality and the QA-owned recommendation:

- **As-is:** `pyproject.toml` `[tool.pytest.ini_options]` runs with branch coverage (`[tool.coverage.run] branch = true`, `source = ["intensicare"]`) and emits `coverage.xml`, but the current `ci.yml` Coverage Report job (see §10.2) **combines and reports** coverage — it does not currently enforce a `--cov-fail-under` gate in the workflow YAML inspected for this strategy. This is itself a gap: a reported-but-unenforced number is not a gate.
- **Recommendation (QA judgment, flagged for barrier C3 sign-off, not silently applied):** enforce **≥80%** line **and** branch coverage as the PR-merge gate (splitting the difference conservatively toward the CI-job's already-implemented number rather than the aspirational 85%, since 85% is stated as a Production-phase target and this repo is pre-MVP-complete), with two carve-outs that must be **excluded from the denominator, not merely tolerated at a lower bar**: (a) the four scorer modules and the alert-engine rule-evaluation path carry a **≥95%** target given L1/L2's density of vectors makes that bar cheap to hit and the clinical cost of an uncovered branch there is disproportionate; (b) generated/vendored code and `if TYPE_CHECKING:`/`__main__` guards stay excluded per the existing `[tool.coverage.report] exclude_also` config.
- **Mutation-adjacent check:** because coverage percentage alone does not prove assertion quality (a line can be "covered" by a test that never asserts on its outcome), the L1 rule-vector suite's per-vector granularity (§2.1) and the L2 property suite's range/determinism assertions (§3.2) are the actual quality backstop for the clinical core — coverage percentage is reported for the whole codebase but is not treated as sufficient evidence for the scorer/rule-engine modules specifically.

### 10.2 CI wiring (extends `.github/workflows/ci.yml`, impl-plan §4)

The existing 7-job pipeline (Lint → Test[3.12+3.13] → Coverage → Security → [main] Build+Push → [main] Deploy Staging → [tag] Release, `IMP-4.3-01`) is extended, not replaced:

| Job | New content this strategy adds | Trigger | Blocks merge? |
|---|---|---|---|
| **Job 2 — Test** (existing) | L1 rule-vector suite (`tests/rules/`), L2 property suite (`tests/property/`), L4 mocked contract tests (`tests/contract/test_gold_read_schema.py`, `test_gold_writeback.py`) added to the same pytest run already executing on the 3.12+3.13 matrix | Every push/PR | Yes |
| **Job 2b — A11y & Visual** (new) | `axe-core` scan + Playwright visual-regression matrix (§8, §9), scoped to diffs touching `src/**/*.{css,ts,tsx}`/`tokens/**` | Every PR touching UI paths | Yes (a11y violations); visual diffs require human approval, not auto-fail |
| **Job 3 — Coverage** (existing, extended) | Add `--cov-fail-under=80` enforcement (currently reporting-only per §10.1); scoped sub-check for the ≥95% scorer/rule-engine carve-out | Every push/PR | Yes |
| **Job 4 — Security** (existing) | Unchanged by this strategy; DRILL-CROSS-TENANT-DECRYPT/DRILL-PHI-EGRESS-SCRUB (§6) are **not** run here — they need seeded multi-tenant data and are heavier than a Bandit/Trivy static scan, so they live in the new nightly/release-gate job below | — | Yes (unchanged) |
| **Job 8 — Contract (live sandbox)** (new) | `tests/contract/test_gold_read_live.py` against `AMH_SANDBOX` (§4.1) | Nightly (scheduled `workflow_dispatch`/cron), and pre-release | No (PR-blocking would couple every PR to a shared external sandbox's availability); failures page the amh-integration-architect owner |
| **Job 9 — Storm & Drills** (new) | L6 alert-storm load tests (§5) + all six L7 chaos drills (§6) against a disposable staging-like environment | Nightly (storm baseline only, cheaper) + full suite pre-release/pre-promotion | **Yes, pre-release** (release gate, not PR gate) |
| **Job 10 — Vector/token freshness** (new, fast) | `scripts/check_vector_coverage.py` (§2.1: every alert has ≥1 test vector), `scripts/check_tokens.py`/`scripts/check_units.py` (existing scripts, wired as required checks if not already) | Every push/PR | Yes |

This keeps the **PR-merge gate fast** (Lint + Test[incl. L1/L2/L4-mocked] + Coverage + Security + freshness checks — all sub-15-minutes per the existing `IMP-C-21` CI-time gate, MVP <10min/Production <15min) while making the **release gate strictly stronger** than the merge gate (adds live-sandbox contract tests, storm tests, and all six chaos drills) — a PR can merge to `develop` on the fast gate, but nothing reaches `main`→staging→production without the full drill suite passing, which is the correct ordering given `IMP-C-01..06`'s "before the first real patient" severity.

---

## 11. Open items (not resolved here, flagged for barrier C3)

- **Coverage-gate number** (`IMP-C-17`): this document recommends ≥80% (§10.1) but does not have authority to close the 70/80/85 conflict on its own — needs explicit barrier C3 sign-off.
- **`/api/v1/health` build gap** (`observability-slo.md` §4.1): DRILL-POLLER-KILL's `/api/v1/health` readiness-contract assertion cannot be written against the invariant-required contract until the API team closes the gap between the current unversioned `/health` liveness stub and the specified readiness contract — the drill's *watchdog-paging* half can be built and gated today; its *readiness-endpoint* half is blocked on that build item, not on this test strategy.
- **Live AMH sandbox availability**: `AMH_SANDBOX`-gated nightly contract tests (§4.1, §10.2 Job 8) assume a shared sandbox Athena/Gold endpoint exists with representative data; provisioning that sandbox is an infrastructure dependency this document assumes but does not own.
- **Alert-engine test entry point naming** (§2.1): this strategy assumes an `evaluate_alert_definition(alert_id, inputs) -> fired: bool`-shaped entry point exists or will exist per `alert-engine.md` §2–3; the exact function signature is an implementation detail owned by the alert-engine-architect, not fixed by this document.

---

## 12. Reference index

- Vision: `docs/plan/_work/briefs/vision.json` (`VIS-*`)
- Implementation plan: `docs/plan/_work/briefs/implementation-plan.json` (`IMP-*`)
- Scorers: `docs/plan/_work/briefs/scorers.json` (`MEWS-*`, `NEWS2-*`, `SOFA-*`, `qSOFA-*`, `SCORERS-C-*`)
- Alert catalog (executable fixtures): `docs/plan/_work/alerts/{sepsis,aki,respiratory,hemodynamics,neuro-sedation,electrolyte,pharmaco-interaction,early-warning-scores,correlation-engine}.yaml`
- Architecture: `docs/plan/architecture/{alert-engine,data-model,security-lgpd,observability-slo}.md` (`INV-1..6`, `REQ-INV-*`)
- Constraint ledger: `docs/plan/_work/constraints/ledger.yaml` (`CON-*`, owners, `invariant_id`)
- Design/accessibility: `docs/plan/design/{accessibility-standard,design-tokens,design-language,component-library}.md` (`A11Y-REQ-*`, `A11Y-GATE-*`)
- CI: `.github/workflows/ci.yml`; build config: `pyproject.toml`
