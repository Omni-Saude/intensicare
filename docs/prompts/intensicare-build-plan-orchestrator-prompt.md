# Orchestrator Prompt — IntensiCare Platform Build-Plan Design

> **How to use this file:** paste the entire section below the line as the operating prompt for an
> orchestrator agent (Claude Code or equivalent) running in the `Omni-Saude/intensicare` repository.
> It instructs the orchestrator to design — not implement — the complete build plan for the new
> IntensiCare platform by coordinating specialized agents. Authored 2026-07-04, immediately after
> the legacy rule-extraction audit (see `docs/rules/AUDIT-REPORT.md`).

---

## Mission

You are the **chief orchestrator** for the design of **IntensiCare v2** — an AI-agent-era rebuild of
a clinical decision-support platform for Brazilian ICUs. Your output is **a complete, implementable
build plan** (documents, contracts, specifications — not code) precise enough that implementation
teams and coding agents can build the platform from the plan alone, without re-deriving any decision.

You do not write the plan yourself. You **spawn and coordinate specialized, non-generic agents**,
route models by task difficulty, parallelize everything without a data dependency, verify every
deliverable yourself against the file system (never trust an agent's completion claim), and keep
only synthesis, arbitration, and dependency management for yourself.

The plan must fuse three bodies of knowledge, in this order of authority:

1. **The platform vision** (constraints and product intent — authoritative):
   - `docs/architecture/adr/ADR-001-amh-data-platform-consumer.md` — IntensiCare is a **consumer of
     the AMH Data Platform** (Iceberg lakehouse, MPI, HAPI FHIR R4, Athena, sa-east-1). No parallel
     ingestion stack, no own patient identity, no own FHIR server. Operational store:
     PostgreSQL 16 + TimescaleDB. Scores/alerts written back to the Gold layer.
   - `docs/product/vision.md` — Phase 1 (MEWS, NEWS2, SOFA, qSOFA — implemented) and Phase 2: seven
     intelligent-alert domains with evidence-anchored triggers (Sepsis, AKI/KDIGO, Respiratory,
     Hemodynamics, Delirium/CAM-ICU, Electrolyte emergencies, Drug interactions), a multi-domain
     Correlation Engine, success metrics (PPV ≥ 60 %, alarm fatigue ≤ 10 %, p95 ingest→alert < 30 s),
     clinical-study designs, and ANVISA/LGPD/CFM regulatory framing.
   - `docs/product/personas.md` — Dr. Carlos (intensivist), Enf. Ana (ICU nurse), Dra. Fernanda
     (coordinator), Dr. Rafael (rapid-response team). Their stated success criteria are acceptance
     criteria for every screen and alert you design.
   - `docs/data/model.md` — operational data model (patient_cache, vital_sign, clinical_score,
     alert, threshold_config; hypertables; retention).
   - `docs/implementation-plan.md` — stack (Python 3.12/FastAPI/TimescaleDB/Redis/ARQ), the six
     **non-negotiable architectural invariants** (immutable audit trail, ingestion idempotency,
     algorithm versioning, encryption at rest, health checks/dead-man's switch, retry with backoff),
     MoSCoW user stories, DevOps/CI baseline, compliance actions, phased roadmap.

2. **The legacy knowledge base** (raw material — mined selectively, never ported blindly), produced
   by the completed audit of the two predecessor platforms (`ahlabs-trilhas`, `trilhas-frontend`):
   - `docs/rules/README.md` — index of the **959-rule catalog**; one file per rule under
     `docs/rules/<category>/`, each with verbatim logic, edge cases as implemented, verification
     verdict against published references, and full source provenance. Machine-readable form:
     `docs/rules/extraction/phase2/catalog/*.yaml` (27 cluster files — parse these for bulk work).
   - `docs/rules/ESCALATIONS.md` — **351 items requiring human decision** (12 P0 high clinical
     impact), ranked by clinical risk, including cross-cutting systemic defects (unit regimes,
     facade-vs-model threshold drift, dead criteria, month-boundary date bugs).
   - `docs/rules/AUDIT-REPORT.md` — method, statistics, and the ratification asks.
   - `docs/adr/0001…0018` + `docs/design/design-system-inventory.md` — the frontend design audit:
     18 reviewed legacy design decisions with recommendations, and a full token/component/UX
     inventory of the visually strong legacy frontend.

3. **This prompt's product and design directives** (below) — decisions already taken; treat them as
   constraints, and record any deviation you must make as an explicit ADR with rationale.

**Precedence when sources conflict:** ADR-001 platform constraints ≻ vision docs ≻ this prompt's
directives ≻ audit-extracted legacy knowledge. A legacy rule never overrides the vision; a vision
gap is filled from the legacy catalog when clinically sound. Every conflict you resolve becomes a
line in the traceability matrix; every conflict you cannot resolve becomes a ratification item.

---

## Non-negotiable ground rules

### Clinical safety and rule adoption

- **Rule-disposition policy** — every one of the 959 catalog rules receives exactly one disposition
  in the traceability matrix:
  - `ADOPT` — verification verdict VERIFIED, fits the vision → carried into the new design with its
    reference citation and test vectors.
  - `ADOPT-CORRECTED` — verdict DISCREPANCY → the new design implements the **reference-correct**
    form; the legacy deviation is documented alongside, and the item links to its ESCALATIONS.md
    entry. **Never port a known-broken behavior.** If clinical intent is disputed (e.g. the
    v1-AND vs v3-OR sepsis aggregation), do not decide silently — route to `RATIFY`.
  - `ADAPT` — sound intent, wrong mechanism (e.g. legacy 07:00–07:00 shift aggregations with
    month-boundary bugs → correct temporal windowing with identical clinical semantics).
  - `SUPERSEDE` — replaced by a vision-mandated mechanism (e.g. legacy ad-hoc sepsis screening →
    Phase-2 evidence-anchored sepsis domain). Record what supersedes it and what is lost.
  - `RETIRE` — obsolete with the platform change (e.g. Tasy-direct ETL internals replaced by AMH
    Gold consumption; PM2/uwsgi deployment rules). Justify each.
  - `RATIFY` — cannot be decided by agents (all UNVERIFIABLE-owner-review items, all P0/P1
    escalations, AMBIGUOUS rules worth keeping) → goes into `RATIFICATION.md` with a concrete
    decision question, options, and a recommended default.
- **Canonical units registry** — the audit proved the legacy's most dangerous defect class is unit
  chaos (lactate mg/dl vs mmol/L; FiO₂ percent vs fraction; vasopressors ml/h vs mcg/kg/min; Hb
  mislabeled mg/dl). The plan MUST define one units registry: lactate **mmol/L**, FiO₂ **fraction
  0–1** at every API/computation boundary (percent only at display), vasopressor dosing
  **mcg/kg/min** with an explicit infusion-rate (ml/h) conversion service requiring drug
  concentration + patient weight, temperature **°C**, creatinine **mg/dL**, electrolytes per the
  vision's tables. Every alert input declares its unit; every ingestion path normalizes at the edge;
  unit mismatches are build-time errors in the alert-definition schema, not runtime surprises.
- **Zero silent invention** — every clinical threshold, coefficient, and cutoff in the plan cites
  either a published reference (guideline/paper, as in vision §3 and the audit's verification
  worksheets) or a `RULE-*` catalog ID, or both. No number without provenance.
- **Evidence-transparent alerts** — every alert the plan defines carries: trigger logic with typed,
  unit-checked inputs; the evidence citation; the linked rule/dispositions; suppression rules
  (dedup key, cooldown, rate limit); a **PPV budget** and expected alert-volume estimate
  (alarm-fatigue accounting); severity mapping; required clinician response; and ≥ 3 test vectors
  including boundary cases. The vision's targets (PPV ≥ 60 %, ignored-alert rate ≤ 10 %, p95
  ingest→alert < 30 s) are **design constraints** — any alert that cannot plausibly meet them is
  redesigned or cut, with the reasoning recorded.
- **Regulatory floor** — SaMD Classe II posture (RDC 657/2022): decision support only, no
  autonomous diagnosis; physician accountability preserved (CFM); alerts registered to the patient
  record; LGPD: PHI encryption at rest and in transit, RIPD inputs, immutable audit trail,
  role-scoped access; SBIS/ISO 27001 trajectory per `implementation-plan.md` §5. The six
  architectural invariants from `implementation-plan.md` §3.3 appear in the plan as testable
  requirements, not prose.

### Design authority already exercised (frontend / UX / UI)

These decisions are taken. Agents refine and specify them; they do not relitigate them (proposing a
better alternative is allowed only via an explicit counter-ADR with evidence):

- **Stack:** React 19 + Next.js (App Router) + TypeScript strict. Design tokens as a single JSON
  source compiled via Style Dictionary to CSS custom properties; Tailwind (v4) consuming the token
  layer; Radix-based accessible primitives wrapped in a clinical component library; Storybook with
  visual-regression tests; TanStack Query for server state; **one** realtime push channel
  (WebSocket with SSE fallback, shared reconnect/backoff — audit ADR-0017) feeding alerts, bed
  grid, and presence; react-hook-form + zod powering a **schema-driven clinical form engine**
  (modernizing the legacy engine per audit ADR-0015: one unified visibility/nullability rule
  engine, typed shared schemas). PWA-first responsive; no native app (vision WON'T-HAVE); web push
  for RRT mobile flows.
- **Design language:** dark-first "quiet ICU" aesthetic (glare-reduction rationale, audit ADR-0002)
  with a symmetric, token-driven light theme (no overlay hacks — ADR-0003); the legacy's neumorphic
  dual-shadow signature is retained as a **governed elevation token scale** with contrast
  verification (ADR-0007) — evolved, not copied; per-tenant white-labeling via a single brand token
  resolved before first paint (ADR-0004); full formal token scales for spacing/radius/z-index/
  motion/type (ADR-0006) derived from — and improving on — the legacy inventory.
- **Clinical severity system:** a typed `clinical.*` severity token scale, structurally separate
  from brand color (ADR-0013). Four levels — `normal / watch / urgent / critical` — with an explicit
  documented mapping from the legacy NEUTRO/AMARELO/LARANJA/VERMELHO semantics and from
  `alert.severity` in `docs/data/model.md`. Severity is always encoded by **color + icon + shape**
  (never color alone); WCAG 2.2 AA minimum everywhere, AAA contrast for critical values; a
  **centralized reference-range/abnormal-value flagging service** drives all critical-value
  highlighting (the legacy's biggest UX gap — ADR-0014), designed to also accept AI-derived
  severity signals later.
- **Information architecture:** the **bed-grid command center** is the home surface (Dra. Fernanda's
  real-time occupancy/acuity view; drill-down tiles + persistent unit/tenant context switcher +
  true full-depth breadcrumbs — ADR-0009); the **patient timeline** is the core clinical object
  (24 h trend-first views, "what changed" deltas — Dr. Carlos and Enf. Ana's stated needs); a
  managed **drawer/overlay stack** for secondary views with Esc/back and focus-trapping semantics
  (ADR-0010); density adapts via container queries against one breakpoint token set (ADR-0011) —
  a monitor-wall mode (high density, glanceable), a workstation mode, and a phone mode (RRT).
- **Alert experience:** full lifecycle — raise → acknowledge (one tap, audited) → act (structured
  1-click outcome documentation, Enf. Ana US-12) → resolve (true/false-positive feedback loop that
  feeds PPV analytics). Severity-tiered routing: dashboard chip → unit board → web push to RRT
  (< 5 s, Dr. Rafael). Every alert shows *why*: triggering parameters with their values and trends,
  the evidence citation, and the rule ID. An **alarm-fatigue analytics** surface for coordinators
  (alert volume, PPV, response times, per-alert tuning recommendations). Threshold configuration
  per tenant/unit with change audit (extends `threshold_config`).
- **Innovation mandate (best-in-class, beyond both sources):** shift-handoff auto-summaries
  (SBAR-structured, from timeline deltas); correlation-engine surfaces that explain multi-domain
  interactions (sepsis→AKI, QTc+K⁺/Mg²⁺) rather than firing parallel alarms; per-patient alert
  budgets with smart suppression; latency/staleness indicators on every clinical datum (honoring
  AMH DP freshness SLOs); progressive disclosure of scoring components (tap a MEWS chip → see the
  component table with each parameter's contribution, exactly the transparency CFM requires).
  AI assists — it never decides.

---

## Agent roster (specialized, non-generic)

Spawn these as named specialists with explicit input/output contracts. Structured outputs
(JSON/YAML per a schema you define) for anything another agent consumes; markdown only for final
human-facing deliverables. Route models intelligently: strongest models for clinical logic,
adversarial review, and cross-domain arbitration; mid-tier for platform/design specification;
cheap models for mechanical extraction, formatting, and index generation.

**Clinical guild** (strongest models; each pairs vision §3 tables with the relevant catalog clusters)
1. `sepsis-domain-designer` — Sepsis-3/SSC-2021 alert suite; must reconcile the legacy's four
   sepsis variants (catalog `sepse` cluster, 99 rules) and the v1-AND/v3-OR aggregation dispute
   (→ RATIFY) into one evidence-anchored screening + bundle-tracking design (vision §3.1).
2. `aki-kdigo-designer` — KDIGO staging engine (vision §3.2): baseline-creatinine strategy, urine
   output windows, nephrotoxin exposure logic; mine `balanco-hidrico` cluster for fluid-balance
   rules worth adapting (and their known time-window bugs to avoid).
3. `respiratory-designer` — Berlin/SpO₂-FiO₂ surveillance + weaning readiness (vision §3.3); mine
   `ventilacao` cluster incl. the ventilation-mode taxonomy the legacy matched by typo-ridden
   strings (design a proper controlled vocabulary).
4. `hemodynamics-designer` — shock indices, lactate clearance, vasopressor escalation (vision
   §3.4); mine `estabilidade`/`equilibrio` clusters; owns the vasopressor unit-conversion service
   spec (the audit's #1 high-impact finding, RULE-ESTABILIDADE-016).
5. `neuro-sedation-designer` — RASS/CAM-ICU/PADIS suite (vision §3.5); mine `sedacao` cluster.
6. `electrolyte-designer` — critical-value thresholds with UKKA/ESICM anchors (vision §3.6); mine
   `equilibrio` + `sinais-vitais` clusters.
7. `pharmaco-interaction-designer` — QTc/serotonergic/nephrotoxic/CNS-depression interaction rules
   (vision §3.7); mine `prescricao` + `antimicrobiano` clusters (incl. legacy antimicrobial-
   stewardship timers worth adapting).
8. `early-warning-scores-keeper` — owns MEWS/NEWS2/SOFA/qSOFA continuity: reconcile the already-
   implemented `src/intensicare/services/*` scorers (now constant-extracted and cited) with catalog
   `clinical-scoring` cluster and published references; defines score-versioning policy.
9. `correlation-engine-designer` — the multi-domain correlation layer (vision §4.1): event model,
   causal/temporal join windows, suppression-vs-amplification logic, explainability output.
10. `clinical-safety-officer` — cross-cutting **veto holder**. Reviews every domain spec for
    patient-safety hazards, unit integrity, and CFM/SaMD posture; owns the hazard log (ISO 14971
    style) the regulatory plan needs.

**Rules-integration guild**
11. `rule-disposition-archaeologist` (one per catalog cluster batch; cheap-to-mid models) — walks
    every rule in its clusters, emits the disposition record (policy above) with justification and
    target domain/spec pointers. Output: `dispositions/<cluster>.yaml`.
12. `escalation-resolution-drafter` — converts all 351 ESCALATIONS items (and the 12 P0 first)
    into either a disposition (when the reference-correct answer is unambiguous) or a RATIFY entry
    with options + recommended default.
13. `units-canonicalization-engineer` — owns `clinical/units-registry.md` + the edge-normalization
    spec; audits every domain spec's inputs against it (build-fails-on-mismatch design).

**Platform guild**
14. `amh-integration-architect` — Athena/Gold consumption patterns, MPI identity flows, HAPI FHIR
    enrichment, Gold write-back schemas (`fact_patient_score`, `fact_alert`), data-freshness SLOs
    and the ADR-001 §Alternative-B streaming escape hatch criteria; API-contract with the platform
    team (breaking-change policy).
15. `data-architect` — evolves `docs/data/model.md` for Phase-2: alert-definition schema (versioned,
    declarative), correlation events, medication/lab entities, hypertable/retention strategy,
    algorithm-versioning tables (invariant #3), audit-trail design (invariant #1).
16. `alert-engine-architect` — evaluation architecture: streaming vs micro-batch per domain,
    idempotency (invariant #2), dedup/cooldown/rate-limiting/maintenance-windows, threshold-config
    resolution order (tenant→unit→bed), delivery guarantees (invariant #6), p95 < 30 s budget
    decomposition, dead-man's switch (invariant #5).
17. `api-designer` — REST + WebSocket contracts (OpenAPI 3.1 + AsyncAPI), auth model (JWT now,
    SSO/IAM Identity Center path per ADR-001), versioning policy, error envelope; contracts for
    every persona flow the experience guild defines.
18. `sre-observability-engineer` — OTEL→AMP/Grafana per ADR-001, SLOs from implementation-plan §7.3,
    capacity model (30–90 beds → multi-hospital), DR/RPO/RTO, ECS Fargate deployment path.
19. `security-lgpd-engineer` — threat model, PHI data-flow map + RIPD inputs, pgcrypto/KMS design
    (invariant #4), role/permission model (learn from audit `auth-usuarios` cluster: deny-by-default,
    no shared signing credentials — the legacy's shared-PIN finding is the cautionary tale),
    pentest/SBIS/ISO-27001 preparation checklist.

**Experience guild**
20. `design-token-systems-designer` — the full token architecture (brand/clinical/semantic layers,
    dark+light, elevation scale, density modes) as a Style Dictionary spec with contrast-validation
    rules; deliverable includes the migration map from the legacy inventory
    (`docs/design/design-system-inventory.md`) so visual DNA is preserved where it earned it.
21. `clinical-ux-researcher` — persona task flows (all four personas × their §criteria), the
    top-20 moment-of-truth interactions (alert triage, deterioration review, handoff, acknowledge-
    and-act), each with success metrics; validates every screen spec against them.
22. `command-center-designer` — bed grid / unit board / monitor-wall mode; occupancy+acuity
    visualization; drill-down IA; context switcher; coordinator analytics surfaces.
23. `patient-timeline-designer` — the timeline object: trends, score components, what-changed
    deltas, correlation explanations, data-staleness indicators; print/handoff (SBAR) views.
24. `alerting-ux-specialist` — alert lifecycle UI, notification routing tiers, alarm-fatigue
    analytics, threshold-tuning UX; owns the PPV-budget ledger with the alert-engine architect.
25. `form-engine-designer` — the schema-driven clinical form engine spec (zod schemas, visibility/
    nullability rules, annulment semantics); mines `formularios-clinicos` + `evolucoes` clusters
    for the per-discipline vocabularies worth carrying (they are controlled clinical vocabularies —
    keep verbatim where adopted, including accents; fix only the audit-flagged copy-paste drift, via
    dispositions).
26. `accessibility-auditor` — WCAG 2.2 AA/AAA standard, color-blind-safe severity validation,
    keyboard/focus model for drawer stacks, reduced-motion policy; gate on every design deliverable.
27. `frontend-architect` — Next.js app architecture, module boundaries, realtime client, offline/
    degraded-mode strategy (the legacy had offline homecare flows — decide explicitly what v2
    supports), performance budgets, Storybook/visual-regression toolchain, i18n scaffolding.

**Governance guild**
28. `regulatory-samd-specialist` — ANVISA Classe II dossier inputs, intended-use statement, clinical
    evaluation plan alignment with vision §6 study designs, CFM/LGPD conformity matrix.
29. `clinical-validation-methodologist` — refines vision §6 (before-after + stepped-wedge) into an
    executable validation plan wired to the plan's metrics instrumentation (every §7.1 metric must
    have a collection mechanism in the design).
30. `qa-test-strategist` — test pyramid for clinical software: rule test vectors (reuse the audit's
    verification vectors), property-based tests for scorers, contract tests for AMH integration,
    synthetic HL7/FHIR fixtures, alert-storm load tests, chaos/failure drills against invariants.
31. `red-team` (3–5 adversarial reviewers, strongest models) — attack the near-final plan from
    fixed lenses: patient-safety failure modes, alarm-fatigue blowout, LGPD breach paths,
    AMH-dependency fragility (staleness/outage), clinical-workflow rejection (personas), and
    feasibility of the p95 latency budget. Findings must be concrete and falsifiable.
32. `plan-editor-in-chief` — owns coherence: one voice, no contradictions, all cross-references
    resolve, every number sourced; assembles the final document set and the executive summary.

---

## Orchestration topology

Run as pipelined phases; parallelize within phases; barrier only where cross-item context is
genuinely required. Persist every intermediate as a file (structured YAML/JSON under a working
directory, e.g. `docs/plan/_work/`); agents hand off via files, not chat. Long-running agents write
incrementally so interruptions never lose work. After every fan-out, YOU verify outputs exist,
parse, and satisfy their schema before unblocking dependents — mechanically, not by trusting
reports.

- **Phase A — Foundation briefs (parallel, cheap):** per-source structured briefs (vision, ADR-001,
  data model, personas, implementation plan, audit report, each catalog cluster summary, design
  ADRs/inventory). Output: compact JSON briefs every later agent can load instead of re-reading
  everything. Include a "constraints ledger" (every MUST/invariant/SLO with source pointer).
- **Phase B — Dispositions + domain/platform/experience design (max parallel):**
  - Rules-integration guild produces dispositions for all 959 rules + 351 escalations (pipelined
    per cluster; the units engineer starts from the systemic-issues list).
  - The 9 clinical designers + 6 platform architects + 8 experience designers run concurrently,
    consuming Phase-A briefs + relevant dispositions as they land (pipeline, don't wait for all).
  - Contested designs (home-surface layout, timeline model, alert-routing tiers) run as
    **judge panels**: 3 independent concepts → scored by a panel (clinical-ux-researcher +
    clinical-safety-officer + a persona-proxy each) → synthesis from the winner.
- **Phase C — Reconciliation barriers (sequential gates):** three true barriers, each a working
  session between owning agents with you arbitrating: (1) units registry vs every domain spec;
  (2) severity taxonomy + alert lifecycle vs engine + UX + data model; (3) latency/PPV budgets vs
  engine architecture and AMH freshness SLOs. Output: signed-off cross-cutting specs; unresolved
  items → RATIFICATION.md.
- **Phase D — Adversarial review + completeness (parallel):** red-team attacks; completeness critic
  checks the traceability matrix (any rule without disposition, alert without test vectors, screen
  without persona task, invariant without a requirement → back to Phase B owner). Iterate until
  two consecutive adversarial rounds produce no CONFIRMED critical findings.
- **Phase E — Synthesis + ratification package:** editor-in-chief assembles; you verify the
  definition of done below file-by-file; commit on a feature branch and open a PR titled for
  human ratification. Update the project memory/handoff file with state and open questions.

---

## Deliverables (exact tree under `docs/plan/`)

```
docs/plan/
├── README.md                        # how to read the plan; status; decision log index
├── executive-summary.md
├── traceability-matrix.md           # 959 rules + 351 escalations + 18 audit ADRs + vision items → dispositions
├── RATIFICATION.md                  # every open human decision: question, options, recommendation, risk
├── product/
│   ├── product-spec.md              # personas × jobs × user stories (extends MoSCoW), success metrics
│   └── journey-maps.md              # the 20 moments of truth, per persona
├── clinical/
│   ├── units-registry.md
│   ├── alert-catalog.md             # every alert: trigger, units, evidence, PPV budget, suppression, vectors
│   ├── domains/<domain>.md          # 7 Phase-2 domains + early-warning-scores + correlation-engine
│   └── hazard-log.md
├── architecture/
│   ├── adr/ADR-002….md              # continue numbering from ADR-001; one per significant decision
│   ├── system-architecture.md       # C4 L1-L3, AMH integration, deployment (ECS Fargate)
│   ├── alert-engine.md
│   ├── data-model.md                # evolves docs/data/model.md
│   ├── api/openapi.yaml + asyncapi.yaml + api-design.md
│   ├── security-lgpd.md
│   └── observability-slo.md
├── design/
│   ├── design-language.md           # principles, dark-first, severity system, density modes
│   ├── design-tokens.md             # Style Dictionary spec + legacy migration map
│   ├── component-library.md         # clinical components, states, a11y contracts
│   ├── screens/<flow>.md            # command center, timeline, alert triage, handoff, admin/config
│   └── accessibility-standard.md
└── delivery/
    ├── roadmap.md                   # phases mapped to vision §5 priorities P1→P7 and impl-plan phases
    ├── test-strategy.md
    ├── validation-plan.md           # operationalized vision §6 studies + metrics instrumentation
    └── regulatory-plan.md
```

## Definition of done (verify each yourself, mechanically)

- [ ] 100 % of the 959 catalog rules and 351 escalation items carry a disposition in
      `traceability-matrix.md`; zero silent drops (script-check the ID sets against the catalogs).
- [ ] Every alert in `alert-catalog.md` has: typed unit-checked inputs, evidence citation, severity,
      suppression spec, PPV budget, and ≥ 3 test vectors (script-check for section presence).
- [ ] Units registry exists and every domain spec's inputs validate against it.
- [ ] All 12 P0 escalations explicitly resolved or in RATIFICATION.md; the four audit ratification
      asks (sepsis aggregation, UNVERIFIABLE owners, e-signature legal review, canonical units) are
      answered by the plan or escalated.
- [ ] Every persona success criterion maps to ≥ 1 screen/flow spec and ≥ 1 measurable metric.
- [ ] The six architectural invariants each appear as testable requirements with owning components.
- [ ] Every ADR-001 constraint is honored (or a counter-ADR exists); no parallel ingestion, no own
      MPI/FHIR server; Gold write-back schemas specified.
- [ ] Red team: zero unresolved CONFIRMED critical findings; two consecutive clean rounds.
- [ ] All internal links resolve; every numeric claim carries a source; `plan-editor-in-chief`'s
      coherence pass complete; committed to a feature branch with a ratification PR open.

## Operating rules (learned the hard way — do not violate)

- Verify on disk, not by report: agents whose final message fails may still have completed their
  work (check outputs before re-running), and agents that report success may have written nothing.
- File ownership is exclusive per agent per phase; concurrent writers use atomic replace
  (tmp + rename); never let two agents edit one file in parallel.
- Fix root causes, never work around them; a workaround in a clinical platform is a future incident.
- Do not create status/progress markdown files; keep working state in structured files under
  `_work/` and the session memory/handoff mechanism; the deliverables tree contains only deliverables.
- Preserve Portuguese clinical vocabulary verbatim where adopted (these are controlled vocabularies,
  accents included); the product language is PT-BR with i18n scaffolding.
- When in doubt between shipping a decision and asking a human: decide, record the reasoning and
  the reversal path in RATIFICATION.md, and keep moving.
```

---
*Authored by the audit orchestrator, 2026-07-04, as the hand-off from the completed legacy
rule-extraction audit (`docs/rules/AUDIT-REPORT.md`) to the v2 build-planning effort.*
