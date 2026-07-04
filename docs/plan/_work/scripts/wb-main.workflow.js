export const meta = {
  name: 'wb-main',
  description: 'Phase B: 35 disposition agents + escalation lane + 9 domain designers + platform/experience guilds + panel concepts + governance',
  phases: [
    { title: 'Dispositions', detail: '38 shards via 35 agents' },
    { title: 'Escalations', detail: 'P0/P1/UNVERIFIABLE/AMBIGUOUS drafters + design-ADRs' },
    { title: 'Domains', detail: '9 clinical domain designers (gated on own shards)' },
    { title: 'Platform', detail: 'AMH, data model, security, API, SRE' },
    { title: 'Experience', detail: 'tokens, a11y, frontend, alerting UX, forms' },
    { title: 'Panels', detail: '3 topics x 3 divergent concepts' },
    { title: 'Governance', detail: 'regulatory, validation, QA (after domains)' },
  ],
}

const R = { type: 'object', required: ['artifacts', 'n_records'], properties: {
  artifacts: { type: 'array', items: { type: 'string' } },
  n_records: { type: 'number' }, notes: { type: 'string' } } }

const PRE = `Repo: /Users/familia/intensicare (cwd). FIRST read docs/plan/_work/schemas/CONTRACTS.md and obey it (write fence, evidence discipline, PT-BR vocabulary verbatim, atomic/incremental writes).`

// ---------- B1: disposition agents (35 agents / 38 shards) ----------
const HI = 'high', MED = 'medium'
const DISPO = [
  { key: 'sepse-p1', shards: ['sepse-p1'], eff: HI }, { key: 'sepse-p2', shards: ['sepse-p2'], eff: HI }, { key: 'sepse-p3', shards: ['sepse-p3'], eff: HI },
  { key: 'evolucoes-p1', shards: ['evolucoes-p1'], eff: HI }, { key: 'evolucoes-p2', shards: ['evolucoes-p2'], eff: HI },
  { key: 'balanco-hidrico-p1', shards: ['balanco-hidrico-p1'], eff: HI }, { key: 'balanco-hidrico-p2', shards: ['balanco-hidrico-p2'], eff: HI },
  { key: 'formularios-clinicos-p1', shards: ['formularios-clinicos-p1'], eff: HI }, { key: 'formularios-clinicos-p2', shards: ['formularios-clinicos-p2'], eff: HI },
  { key: 'prescricao-p1', shards: ['prescricao-p1'], eff: HI }, { key: 'prescricao-p2', shards: ['prescricao-p2'], eff: HI },
  { key: 'movimentacao-adt-p1', shards: ['movimentacao-adt-p1'], eff: MED }, { key: 'movimentacao-adt-p2', shards: ['movimentacao-adt-p2'], eff: MED },
  { key: 'auth-usuarios-p1', shards: ['auth-usuarios-p1'], eff: MED }, { key: 'auth-usuarios-p2', shards: ['auth-usuarios-p2'], eff: MED },
  { key: 'operacional-infra-p1', shards: ['operacional-infra-p1'], eff: MED }, { key: 'operacional-infra-p2', shards: ['operacional-infra-p2'], eff: MED },
  { key: 'tenancy-organizacao-p1', shards: ['tenancy-organizacao-p1'], eff: MED }, { key: 'tenancy-organizacao-p2', shards: ['tenancy-organizacao-p2'], eff: MED },
  { key: 'comunicacao-p1', shards: ['comunicacao-p1'], eff: MED }, { key: 'comunicacao-p2', shards: ['comunicacao-p2'], eff: MED },
  { key: 'auditoria-logs', shards: ['auditoria-logs'], eff: MED },
  { key: 'sinais-vitais', shards: ['sinais-vitais'], eff: HI },
  { key: 'documentacao-faturamento', shards: ['documentacao-faturamento'], eff: MED },
  { key: 'alertas', shards: ['alertas'], eff: HI },
  { key: 'sedacao', shards: ['sedacao'], eff: HI },
  { key: 'indicadores-etl', shards: ['indicadores-etl'], eff: MED },
  { key: 'estabilidade', shards: ['estabilidade'], eff: HI },
  { key: 'ventilacao', shards: ['ventilacao'], eff: HI },
  { key: 'cadastros-ui', shards: ['cadastros-ui'], eff: MED },
  { key: 'clinical-scoring', shards: ['clinical-scoring'], eff: HI },
  { key: 'trilhas-engine', shards: ['trilhas-engine'], eff: MED },
  { key: 'tail-eficiencia-piora', shards: ['eficiencia', 'piora-clinica'], eff: HI },
  { key: 'tail-nutricao-profilaxia', shards: ['nutricao', 'profilaxia'], eff: HI },
  { key: 'tail-equilibrio-antimicrobiano', shards: ['equilibrio', 'antimicrobiano'], eff: HI },
]

function dispoPrompt(a) {
  const files = a.shards.map(s => `docs/plan/_work/catalog/shards/${s}.yaml`).join(' and ')
  const outs = a.shards.map(s => `docs/plan/_work/dispositions/${s}.yaml`).join(' and ')
  const clusters = [...new Set(a.shards.map(s => s.replace(/-p\d$/, '')))]
  return `${PRE}
You are a rule-disposition archaeologist. Task: assign EXACTLY ONE disposition to EVERY rule in ${files} (escalation refs are embedded per rule).
Also read: docs/plan/_work/briefs/vision.json, docs/plan/_work/briefs/adr-001.json, ${clusters.map(c => `docs/plan/_work/briefs/clusters/${c}.json`).join(', ')}, and skim docs/plan/_work/constraints/ledger.yaml entry texts.
Write ${outs} — each file: {shard: <name>, cluster: <cluster>, records: [...]} using the EXACT disposition record schema from CONTRACTS.md. Write records incrementally as you decide them. Do not skip, merge, or add rules: output record count must equal shard rule_count.
Decision guidance:
- Clinical logic (thresholds, scores, pathways, alert criteria) feeds v2 domains -> target "clinical/domains/<sepsis|aki|respiratory|hemodynamics|neuro-sedation|electrolyte|pharmaco-interaction|early-warning-scores|correlation-engine>.md#<slug-guess>". Anchors are best-guess slugs; reconciled later.
- Legacy app plumbing (Tasy ETL internals, PM2/uwsgi/deploy, legacy tenancy wiring, legacy UI mechanics, legacy notification transport) -> RETIRE (platform change: AMH Gold consumer, new stack per ADR-001) or SUPERSEDE by the vision/impl-plan mechanism (name it). Lessons worth keeping (e.g. deny-by-default authz, audit patterns) -> ADAPT with target architecture/security-lgpd.md or the fitting architecture doc.
- Controlled clinical vocabularies (enum lists, scales, per-discipline form vocabularies) are ASSETS: usually ADOPT/ADAPT with target design/screens/clinical-forms.md or the fitting domain doc; preserve PT-BR values verbatim.
- Escalation bands P0/P1/UNVERIFIABLE => disposition RATIFY, ratify_ref RAT-<CLUSTER>-<NN> (NN = your sequence per cluster), target "RATIFICATION.md#rat-<cluster>-<nn>". Band AMBIGUOUS => RATIFY if clinically worth keeping else RETIRE. Bands P2/P3 => decide normally per the policy and cite the escalation in justification.
- Catalog status DISCREPANCY => NEVER plain ADOPT (use ADOPT-CORRECTED with the reference-correct form named in justification, or ADAPT/SUPERSEDE/RETIRE/RATIFY). Plain ADOPT only when status OK and verdict VERIFIED or NOT_APPLICABLE.
- catalog_echo must copy the rule's status and verification.verdict EXACTLY as in your shard file; source_quote must be a verbatim >=20-char substring of the rule's name/description/logic/edge_cases/notes.
Return receipt {artifacts: [${a.shards.map(s => `"docs/plan/_work/dispositions/${s}.yaml"`).join(', ')}], n_records: <total>, notes}.`
}

// ---------- B2: escalation lane ----------
const ESC = [
  { id: 'esc-p0', model: 'fable', eff: 'high', out: 'resolutions-p0.yaml', scope: 'ONLY the 12 P0 items', detail: `For each P0 item ALSO read its full rule doc (the "Rule doc." link under docs/rules/). Every P0 outcome is RATIFY. Draft committee-grade content: {item_id, rule_id, band: P0, outcome: RATIFY, ratify: {question: <one concrete decision question>, options: [{id, text, clinical_risk}], recommended: <option id>, rationale: <reference-anchored, cite guideline>}, disposition_note}. The recommended default must be the reference-correct behavior, never the legacy defect.` },
  { id: 'esc-p1a', model: 'opus', eff: 'high', out: 'resolutions-p1a.yaml', scope: 'P1 items 1-23 (in document order)', detail: 'Every P1 outcome is RATIFY. Same record schema as P0 (question/options/recommended/rationale), 3-6 lines of rationale each; read the rule doc only when the excerpt is insufficient.' },
  { id: 'esc-p1b', model: 'opus', eff: 'high', out: 'resolutions-p1b.yaml', scope: 'P1 items 24-45 (in document order)', detail: 'Every P1 outcome is RATIFY. Same record schema as P0 (question/options/recommended/rationale).' },
  { id: 'esc-unv-a', model: 'sonnet', eff: 'high', out: 'resolutions-unverifiable-a.yaml', scope: 'UNVERIFIABLE items 1-50 (in document order)', detail: 'Outcome RATIFY for every item, but GROUP related rules (same cluster/theme) into shared owner-confirmation questions: records: [{item_id, rule_id, outcome: RATIFY, group: <group-id>}], groups: [{group_id, question, options, recommended, member_rule_ids}]. Typical question: "Confirm proprietary rule intent: <theme> — is the legacy behavior intended?"' },
  { id: 'esc-unv-b', model: 'sonnet', eff: 'high', out: 'resolutions-unverifiable-b.yaml', scope: 'UNVERIFIABLE items 51-101 (in document order)', detail: 'Same grouped-RATIFY schema as the first UNVERIFIABLE drafter.' },
  { id: 'esc-amb', model: 'sonnet', eff: 'high', out: 'resolutions-ambiguous.yaml', scope: 'all 56 AMBIGUOUS items', detail: 'Per item recommend keep-vs-drop: {item_id, rule_id, outcome: RATIFY | RETIRE-RECOMMENDED, recommendation: 1-3 lines}. RATIFY when the rule may carry clinical value; RETIRE-RECOMMENDED when it is legacy plumbing or unusable as extracted.' },
]

function escPrompt(e) {
  return `${PRE}
You are an escalation-resolution drafter. Read docs/plan/_work/escalations/escalations.yaml and take ${e.scope}. ${e.detail}
Write docs/plan/_work/escalations/${e.out} (top-level: {scope: "${e.scope}", records: [...]}). Write incrementally. item_id values must match escalations.yaml exactly.
Return receipt {artifacts: ["docs/plan/_work/escalations/${e.out}"], n_records, notes}.`
}

const ADR_DISPO = `${PRE}
You are the design-ADR dispositioner. Read docs/plan/_work/briefs/design-adrs.json (18 legacy-frontend design ADRs) and the design-authority section of docs/prompts/intensicare-build-plan-orchestrator-prompt.md (the "Design authority already exercised" bullets — they are DECIDED).
Write docs/plan/_work/dispositions/design-adrs.yaml: {records: [{adr_id: "0001".."0018", title, disposition: ADOPT|ADAPT|SUPERSEDE|RETIRE, justification (>=80 chars, cite the mission design-authority bullet or audit recommendation), target: "design/<doc>.md#<slug>" or null for RETIRE}]}. All 18, exactly once.
Return receipt {artifacts: ["docs/plan/_work/dispositions/design-adrs.yaml"], n_records, notes}.`

// ---------- B4: domain designers ----------
const DOMAINS = [
  { d: 'sepsis', model: 'fable', shards: ['sepse-p1', 'sepse-p2', 'sepse-p3'], cat: 'SEP-*', vis: '§3.1',
    extra: `Reconcile the legacy's four sepsis variants (v1/v3/manual/pathway) into ONE evidence-anchored screening + bundle-tracking design (Sepsis-3 + SSC-2021 hour-1 bundle). The v1-AND vs v3-OR aggregation dispute is RATIFY: design both branches, pick the reference-anchored recommended default, and mark the design point "pending RAT-SEPSE-*". Include lactate in mmol/L only.` },
  { d: 'aki', model: 'opus', shards: ['balanco-hidrico-p1', 'balanco-hidrico-p2'], cat: 'AKI-*', vis: '§3.2',
    extra: `KDIGO staging engine: baseline-creatinine strategy (documented hierarchy: known baseline > 7d min > MDRD back-calculation), urine-output windows (6h/12h/24h rolling — NOT the legacy 07:00-07:00 nursing day; ADAPT its intent, fix the windowing), nephrotoxin exposure logic. Mine balanco-hidrico dispositions for fluid-balance rules worth adapting and their month-boundary bugs to avoid.` },
  { d: 'respiratory', model: 'opus', shards: ['ventilacao'], cat: 'RESP-*', vis: '§3.3',
    extra: `Berlin criteria + SpO2/FiO2 (SF-ratio) surveillance + weaning-readiness bundle. Design a CONTROLLED VOCABULARY for ventilation modes (the legacy matched typo-ridden strings — list the canonical modes with PT-BR labels + synonyms mapping). FiO2 is a fraction 0-1 at every computation boundary.` },
  { d: 'hemodynamics', model: 'opus', shards: ['estabilidade', 'tail-equilibrio-antimicrobiano'], cat: 'HEMO-*', vis: '§3.4',
    extra: `Shock indices, lactate clearance (mmol/L), vasopressor escalation ladder. YOU OWN the vasopressor unit-conversion service spec (the audit's #1 finding, RULE-ESTABILIDADE-016 + RULE-ESTABILIDADE-024 min-vs-hour drift): canonical mcg/kg/min; explicit ml/h conversion requiring drug concentration + patient weight; reject unconvertible inputs loudly. Write that spec as a section of your domain doc with its own anchor #vasopressor-unit-conversion-service.` },
  { d: 'neuro-sedation', model: 'opus', shards: ['sedacao'], cat: 'DEL-*', vis: '§3.5',
    extra: `RASS / CAM-ICU / PADIS-aligned suite: sedation-depth targets, daily awakening (SAT) triggers, delirium screening cadence, agitation alerts. Preserve the legacy RASS PT-BR enumeration verbatim where adopted (it verified against Sessler 2002).` },
  { d: 'electrolyte', model: 'opus', shards: ['sinais-vitais', 'tail-equilibrio-antimicrobiano'], cat: 'ELY-*', vis: '§3.6',
    extra: `Critical-value thresholds for K+, Na+, Mg2+, Ca2+ (ionized), PO4 with UKKA/ESICM anchors; paired-condition alerts (e.g. hyperkalemia + digoxin; QTc-relevant K/Mg lows feed the pharmaco domain via your interface). The legacy hyperkalemia K>6 rescue protocol (RULE-EQUILIBRIO-004) verified well — adopt with citation.` },
  { d: 'pharmaco-interaction', model: 'opus', shards: ['prescricao-p1', 'prescricao-p2', 'tail-equilibrio-antimicrobiano'], cat: 'DDX-*', vis: '§3.7',
    extra: `QTc-prolonging combinations (+ K/Mg interaction with electrolyte domain), serotonergic combinations, nephrotoxic stacking (feeds AKI), CNS-depression stacking. Adapt the legacy antimicrobial-stewardship timers (antimicrobiano cluster) as stewardship alerts. Interaction knowledge base is declarative + versioned.` },
  { d: 'early-warning-scores', model: 'opus', shards: ['clinical-scoring', 'tail-eficiencia-piora'], cat: 'none (Phase-1 scorers)', vis: '§2 (Fase 1)',
    extra: `You own MEWS/NEWS2/SOFA/qSOFA continuity: reconcile the implemented scorers (docs/plan/_work/briefs/scorers.json) with the clinical-scoring cluster dispositions and published references; the legacy in-house "piora clinica" EWS is largely SUPERSEDED by MEWS/NEWS2 — say precisely what is lost. Define the score-versioning policy (algorithm_version, invariant #3): version string format, migration/recompute rules, dual-write window. Also define SOFA FiO2 handling (fraction!) fixing the P0 sub-score defects.` },
  { d: 'correlation-engine', model: 'fable', shards: ['trilhas-engine', 'alertas', 'tail-eficiencia-piora'], cat: 'none (new layer)', vis: '§4.1',
    extra: `Design the multi-domain correlation layer: domain-event model (each domain emits typed events per its interface), temporal join windows, causal chains (sepsis->AKI; respiratory+hemodynamic; drug+electrolyte QTc), suppression-vs-amplification logic (a correlation REPLACES its member alerts with one richer alert — alarm-fatigue budget), explainability output (every correlated alert lists member events + evidence). Your _work/alerts/correlation-engine.yaml defines the correlation alerts (e.g. ALERT-CORR-SEPSIS-AKI-01) with the same schema.` },
]

function domainPrompt(sp) {
  const dispoFiles = [...new Set(sp.shards.flatMap(k => (DISPO.find(a => a.key === k) || { shards: [k] }).shards))]
    .map(s => `docs/plan/_work/dispositions/${s}.yaml`).join(', ')
  return `${PRE}
You are the ${sp.d} domain designer (clinical guild) for IntensiCare v2 — vision ${sp.vis}. Deliverables:
1. docs/plan/clinical/domains/${sp.d}.md — the full domain spec: clinical scope; trigger/staging logic with typed unit-checked inputs; evidence citations for EVERY threshold (guideline/paper and/or RULE-id); how RATIFY-pending rules are handled (design to the recommended default, marked "pending RAT-*"); interactions with other domains; exactly one fenced block tagged \`\`\`yaml domain-inputs (schema in CONTRACTS.md).
2. docs/plan/_work/alerts/${sp.d}.yaml — every alert of this domain per the CONTRACTS alert schema (>=3 test vectors incl. boundary; suppression; numeric ppv_budget with est_volume_per_100_beds_day and rationale; reconciliation entry for every existing catalog alert matching ${sp.cat} — statuses aligned|extended|changed|new|dropped; dropped needs a reason).
3. docs/plan/_work/domain-interfaces/${sp.d}.yaml — {domain, consumes: [{quantity, unit, source}], emits_events: [{event, meaning, fields}], latency_assumption_ms, volume_estimate_per_100_beds_day}.
Read: docs/plan/_work/briefs/vision.json, existing-alert-catalog.json, escalations-systemic.json, adr-001.json; your cluster briefs; YOUR cluster dispositions: ${dispoFiles}; docs/plan/_work/units/registry.yaml (every input unit MUST match it — if a unit you need is missing, add an open question to your domain doc and use the mission canonical); docs/plan/_work/constraints/ledger.yaml (skim).
${sp.extra}
Alarm-fatigue accounting: the fleet PPV target is >=0.60 and ignored-rate <=10% — justify each alert's ppv_budget and prefer FEWER, richer alerts. Severity uses ONLY normal|watch|urgent|critical.
Return receipt {artifacts: [3 paths], n_records: <alert count>, notes}.`
}

// ---------- B5 platform / B6 experience / panels / B7 governance ----------
const PLATFORM = [
  { id: 'amh-integration', model: 'opus', eff: 'high', wait: [],
    p: `You are the amh-integration-architect. Deliverable: docs/plan/architecture/system-architecture.md — C4 L1-L3 of IntensiCare v2 as an AMH Data Platform CONSUMER (ADR-001 is law): Athena/Gold consumption patterns (polling cadence vs freshness), MPI mpi_id identity flows, HAPI FHIR enrichment calls, Gold write-back schemas fact_patient_score + fact_alert (column-level), data-freshness SLO handling + staleness propagation to the UI, the Alternative-B MSK streaming escape-hatch trigger criteria (as a decision table), API-contract/breaking-change policy with the platform team, ECS Fargate deployment topology (sa-east-1, same VPC). Also write docs/plan/_work/platform/amh-freshness.yaml: {sources: [{source, freshness_slo, staleness_max_for_alerting, fallback}]}. Read briefs: adr-001, vision, implementation-plan, data-model + ledger. Every ADR-001 constraint you rely on: cite ADR001-C-NN.` },
  { id: 'data-architect', model: 'opus', eff: 'high', wait: [],
    p: `You are the data-architect. Deliverable: docs/plan/architecture/data-model.md — evolve docs/data/model.md (brief: data-model.json) for Phase 2: versioned declarative alert-definition schema; correlation events; medication + lab entities; hypertable/retention strategy per entity (resolve CON-SEED-03 precisely); algorithm-versioning tables (invariant #3 — resolve CON-SEED-02 clinical_score naming + algorithm_version column); immutable audit-trail design (invariant #1, append-only + anti-mutation trigger); encryption-at-rest columns (invariant #4, pgcrypto for PHI). Include full DDL sketches. Also write docs/plan/_work/platform/data-model-entities.yaml: {entities: [{name, kind: table|hypertable, retention, phi: bool, invariants: [INV-n]}]}. Requirements as REQ-INV-<n>-<k> table rows (ID | Requirement | Verification | Owning component). Read briefs: data-model, vision, implementation-plan, adr-001 + ledger.` },
  { id: 'security-lgpd', model: 'opus', eff: 'high', wait: ['auth-usuarios-p1', 'auth-usuarios-p2'],
    p: `You are the security-lgpd-engineer. Deliverable: docs/plan/architecture/security-lgpd.md — threat model (STRIDE per interface), PHI data-flow map + RIPD inputs, pgcrypto/KMS design (invariant #4; KMS per tenant per ADR-001), role/permission model DENY-BY-DEFAULT (mine docs/plan/_work/dispositions/auth-usuarios-p*.yaml — the shared-signing-PIN finding RULE-AUTH-USUARIOS-063 is the cautionary tale: name it and design the countermeasure: per-user credentials, no shared defaults, signing requires individual key + audit), LGPD conformity matrix (encryption at rest/in transit, retention, access audit), pentest/SBIS/ISO-27001 preparation checklist. REQ-INV-* rows for invariants 1 and 4. Read briefs: adr-001, implementation-plan, vision + ledger.` },
  { id: 'api-designer', model: 'sonnet', eff: 'high', wait: [],
    p: `You are the api-designer. Deliverables: docs/plan/architecture/api/openapi.yaml (OpenAPI 3.1: patients, vitals, scores, alerts lifecycle raise/ack/act/resolve, thresholds config tenant->unit->bed, dashboard, auth; error envelope; JWT now with SSO/IAM-Identity-Center migration note per ADR-001; URL versioning /api/v1), docs/plan/architecture/api/asyncapi.yaml (ONE WebSocket channel + SSE fallback: alert events, bed-grid updates, presence; reconnect/backoff semantics), docs/plan/architecture/api/api-design.md (principles, versioning policy, breaking-change rules, pagination, idempotency keys, rate limits, error envelope with examples). Severity enum everywhere: normal|watch|urgent|critical. Alert payloads carry: triggering parameters w/ values+units+trends, evidence citation, rule ids, staleness stamps. Read briefs: vision, adr-001, implementation-plan, data-model, existing-alert-catalog + ledger.` },
  { id: 'sre-observability', model: 'sonnet', eff: 'high', wait: [],
    p: `You are the sre-observability-engineer. Deliverable: docs/plan/architecture/observability-slo.md — OTEL->AMP/Grafana per ADR-001; SLO catalog from implementation-plan §7.3 (MVP vs Prod columns, resolve against vision p95<30s via a stage-decomposed latency budget TABLE: gold-availability -> poll -> normalize -> evaluate -> persist -> deliver, each with p95 target; this is the C3 input); dead-man's-switch design (invariant #5) + health-check spec; retry/backoff (invariant #6, ARQ) with DLQ; capacity model 30->90 beds->multi-hospital; DR: RPO/RTO per impl-plan; alert-on-no-alerts monitoring. REQ-INV-5/6 rows. Read briefs: implementation-plan, adr-001, vision + ledger.` },
]

const EXPERIENCE = [
  { id: 'design-tokens', model: 'sonnet', eff: 'high', wait: [],
    p: `You are the design-token-systems-designer. Deliverables: docs/plan/design/design-language.md (principles: dark-first "quiet ICU", symmetric light theme, governed neumorphic elevation-token scale with contrast verification, per-tenant single brand token resolved before first paint, severity NEVER color-alone: color+icon+shape) and docs/plan/design/design-tokens.md (Style Dictionary spec: brand/clinical/semantic layers; full scales for spacing/radius/z-index/motion/type/elevation; density modes monitor-wall/workstation/phone via container queries against one breakpoint token set; clinical.* severity tokens normal|watch|urgent|critical with WCAG 2.2 AA + AAA-for-critical contrast rules AND the documented mapping from legacy NEUTRO/AMARELO/LARANJA/VERMELHO hexes + existing-catalog CRIT/URG/WARN/INFO; migration map from the legacy inventory: token-by-token preserve/replace). Read briefs: design-inventory, design-adrs, vision + docs/plan/_work/dispositions/design-adrs.yaml if present + ledger.` },
  { id: 'accessibility', model: 'sonnet', eff: 'high', wait: [],
    p: `You are the accessibility-auditor. Deliverable: docs/plan/design/accessibility-standard.md — WCAG 2.2 AA baseline + AAA for critical clinical values; color-blind-safe severity validation method (severity = color+icon+shape, verify each pair distinguishable under protanopia/deuteranopia/tritanopia simulation); keyboard/focus model for the managed drawer/overlay stack (Esc/back semantics, focus trap + restore); reduced-motion policy; screen-reader semantics for live alert regions (aria-live levels per severity); touch-target and glare/night-shift guidance; the a11y GATE checklist every screen spec must pass. Read briefs: design-adrs (esp. 0010/0013/0014), design-inventory, personas.` },
  { id: 'frontend-architect', model: 'sonnet', eff: 'high', wait: [],
    p: `You are the frontend-architect. Deliverable: docs/plan/design/component-library.md — React 19 + Next.js App Router + TS strict architecture: module boundaries (app shell, clinical components, data layer TanStack Query, ONE realtime client WebSocket+SSE fallback with shared reconnect/backoff per audit ADR-0017), Radix-wrapped clinical component inventory (each: purpose, states, a11y contract, severity handling), Storybook + visual-regression toolchain, performance budgets (bed-grid 60fps at 90 beds, first-paint budget), offline/degraded-mode DECISION (v2 supports read-only degraded mode with staleness banners; no offline writes — legacy homecare offline flows are RETIRED: record as ADR draft), i18n scaffolding PT-BR-first, PWA + web-push for RRT. Write ADR drafts as docs/plan/_work/adrs/<slug>.md for: realtime-channel-consolidation, offline-mode-scope, form-engine-stack. Read briefs: design-adrs, design-inventory, vision, personas + ledger.` },
  { id: 'alerting-ux', model: 'opus', eff: 'high', wait: [],
    p: `You are the alerting-ux-specialist. Deliverables: docs/plan/design/screens/alert-triage.md (full alert lifecycle UI: raise -> acknowledge one-tap audited -> act structured 1-click outcome documentation per Enf. Ana US-12 -> resolve with true/false-positive feedback feeding PPV analytics; severity-tiered routing dashboard chip -> unit board -> web push to RRT <5s per Dr. Rafael; every alert shows WHY: triggering parameters w/ values+trends, evidence citation, rule id; alarm-fatigue analytics surface for coordinators: volume, PPV, response times, per-alert tuning recommendations) and docs/plan/design/screens/admin-config.md (threshold configuration per tenant/unit/bed with change audit extending threshold_config; alert enable/disable with governance guardrails: safety-critical alerts cannot be silently disabled). Also docs/plan/_work/budgets/ppv-ledger-draft.yaml: {alerts: [], fleet_targets: {ppv: 0.60, ignored_max: 0.10}, method: how PPV will be measured from ack/act/resolve feedback}. Read briefs: personas, vision, existing-alert-catalog, design-adrs + ledger.` },
  { id: 'form-engine', model: 'opus', eff: 'high', wait: ['formularios-clinicos-p1', 'formularios-clinicos-p2', 'evolucoes-p1', 'evolucoes-p2'],
    p: `You are the form-engine-designer. Deliverable: docs/plan/design/screens/clinical-forms.md — the schema-driven clinical form engine spec (modernizing audit ADR-0015): zod schemas as single source; ONE unified visibility/nullability rule engine (declarative conditions); annulment semantics (a nulled answer is auditable, not deleted); typed shared schemas backend<->frontend; per-discipline vocabularies carried VERBATIM PT-BR (accents included) from the formularios-clinicos + evolucoes dispositions — list the adopted vocabularies with their RULE-ids and fix ONLY audit-flagged copy-paste drift via the dispositions (e.g. the crepitacao_edema 4cm enum split RULE-FORMULARIOS-CLINICOS-002/003/004: name the canonical value, cite the disposition); offline-safe drafts; form versioning. Read: docs/plan/_work/dispositions/formularios-clinicos-p*.yaml + evolucoes-p*.yaml, briefs formularios-clinicos + evolucoes cluster briefs, design-adrs (0015) + ledger.` },
]

const PANEL_TOPICS = [
  { t: 'home-surface', owner: 'command-center', stances: [
    'monitor-wall-first: maximal glanceable density, severity choreography, zero navigation',
    'drill-down-workstation-first: bed-grid tiles with progressive disclosure and persistent unit/tenant context switcher + full-depth breadcrumbs',
    'acuity-flow-first: occupancy+acuity choreography for Dra. Fernanda with coordinator analytics woven into the grid'],
    brief: 'the bed-grid command center home surface (audit ADR-0009 IA; Dra. Fernanda real-time occupancy/acuity; three density modes)' },
  { t: 'timeline-model', owner: 'patient-timeline', stances: [
    'trend-canvas-first: continuous 24h multi-parameter canvas with score overlays',
    'event-stream-first: what-changed deltas and clinical events as the spine, trends on demand',
    'score-decomposition-first: score chips expand into component tables (CFM transparency) driving the layout'],
    brief: 'the patient timeline as the core clinical object (24h trend-first, what-changed deltas, score component progressive disclosure, correlation explanations, staleness indicators, SBAR handoff view)' },
  { t: 'alert-routing', owner: 'alerting-routing', stances: [
    'severity-ladder-first: strict tier mapping severity->channel with escalation timers',
    'role-context-first: routing by role+location+shift context (who can act now)',
    'budget-aware-first: per-patient alert budgets and smart suppression shaping what gets pushed where'],
    brief: 'severity-tiered alert routing (dashboard chip -> unit board -> web push RRT <5s), per-patient alert budgets, smart suppression' },
]

function conceptPrompt(topic, idx) {
  const stance = topic.stances[idx]
  const letter = ['a', 'b', 'c'][idx]
  return `${PRE}
You are concept designer ${letter.toUpperCase()} in a judge panel for: ${topic.brief}. Your DELIBERATE stance: ${stance}. Do not hedge toward the other stances — the panel needs divergence. Respect the fixed design authority (dark-first, tokens, Radix, one realtime channel, severity color+icon+shape, WCAG 2.2 AA).
Write docs/plan/_work/panels/${topic.t}/concept-${letter}.md (the concept: layout, interactions, states, how EACH of the four personas succeeds, risks) and docs/plan/_work/panels/${topic.t}/concept-${letter}.yaml ({concept: "${letter}", key_decisions: [], persona_coverage: {carlos, ana, fernanda, rafael: 1-line each}, risks: [], alarm_fatigue_impact: 1-line, a11y_notes: 1-line}).
Read briefs: personas, vision, design-adrs, design-inventory, existing-alert-catalog.
Return receipt {artifacts: [2 paths], n_records: 1, notes}.`
}

const GOVERNANCE = [
  { id: 'regulatory-samd', model: 'opus', eff: 'high',
    p: `You are the regulatory-samd-specialist. Deliverable: docs/plan/delivery/regulatory-plan.md — ANVISA SaMD Classe II (RDC 657/2022) dossier inputs: intended-use statement (decision support only, no autonomous diagnosis, physician accountability CFM), classification rationale, clinical evaluation plan aligned with vision §6 studies, LGPD/RIPD action list, CFM conformity matrix (alerts registered to patient record; score-component transparency), SBIS/ISO-27001 trajectory, hazard-log linkage (ISO 14971 — reference docs/plan/clinical/hazard-log.md), the regulatory review-queue items (brief review-queue) folded in. Read briefs: vision, implementation-plan, review-queue, audit-report.` },
  { id: 'validation-methodologist', model: 'opus', eff: 'high',
    p: `You are the clinical-validation-methodologist. Deliverable: docs/plan/delivery/validation-plan.md — operationalize vision §6: before-after observational study + stepped-wedge cluster RCT (8 ICUs, 18 months, 4 steps): endpoints mapped to §7.1 metrics, sample-size sketch, data collection wired to the plan's instrumentation (EVERY §7.1 metric names its collection mechanism: e.g. PPV from resolve-feedback loop, time-to-action from ack/act audit trail, sensitivity from retrospective chart review protocol), interim-analysis and alert-tuning governance during the study, IRB/CEP considerations. Read briefs: vision, personas + docs/plan/_work/budgets/ppv-ledger-draft.yaml if present.` },
  { id: 'qa-test-strategist', model: 'sonnet', eff: 'high',
    p: `You are the qa-test-strategist. Deliverable: docs/plan/delivery/test-strategy.md — test pyramid for clinical software: rule test vectors (REUSE the alert catalog's test_vectors — state that _work/alerts/*.yaml vectors are executable fixtures), property-based tests for scorers (hypothesis: monotonicity, band edges), contract tests for AMH integration (Athena schemas, Gold write-back), synthetic HL7/FHIR fixtures, alert-storm load tests (>500 alerts/min per vision §7.2), chaos/failure drills against the six invariants (name each drill), a11y test automation, visual regression, coverage targets + CI wiring (impl-plan §4). REQ-INV coverage: every invariant maps to at least one drill/test. Read briefs: implementation-plan, vision, scorers + skim 2-3 files in docs/plan/_work/alerts/ for vector shape.` },
]

// ---------- execution ----------
phase('Dispositions')
const shardDone = {}   // agent-key -> promise
for (const a of DISPO) {
  shardDone[a.key] = agent(dispoPrompt(a), { label: `dispo:${a.key}`, phase: 'Dispositions', model: 'sonnet', effort: a.eff, schema: R })
}
const allDispo = Promise.all(Object.values(shardDone))

const escPromises = ESC.map(e => agent(escPrompt(e), { label: e.id, phase: 'Escalations', model: e.model, effort: e.eff, schema: R }))
const adrDispoP = agent(ADR_DISPO, { label: 'design-adr-dispo', phase: 'Escalations', model: 'sonnet', effort: 'medium', schema: R })

async function afterShards(keys, fn) {
  await Promise.all(keys.map(k => shardDone[k]))
  return fn()
}

const domainPromises = DOMAINS.map(sp =>
  afterShards(sp.shards, () => agent(domainPrompt(sp), { label: `domain:${sp.d}`, phase: 'Domains', model: sp.model, effort: 'high', schema: R })))

const platformPromises = PLATFORM.map(x =>
  afterShards(x.wait, () => agent(x.p + `\nReturn receipt {artifacts, n_records: 1, notes}.`, { label: x.id, phase: 'Platform', model: x.model, effort: x.eff, schema: R })))

const expPromises = EXPERIENCE.map(x =>
  afterShards(x.wait, () => agent(x.p + `\nReturn receipt {artifacts, n_records: 1, notes}.`, { label: x.id, phase: 'Experience', model: x.model, effort: x.eff, schema: R })))

const panelPromises = PANEL_TOPICS.flatMap(t => [0, 1, 2].map(i =>
  agent(conceptPrompt(t, i), { label: `panel:${t.t}:${['a', 'b', 'c'][i]}`, phase: 'Panels', model: 'opus', effort: 'high', schema: R })))

const domains = await Promise.all(domainPromises)
log(`Domains complete: ${domains.filter(Boolean).length}/9 — starting governance`)

const govPromises = GOVERNANCE.map(x =>
  agent(x.p + `\nReturn receipt {artifacts, n_records: 1, notes}.`, { label: x.id, phase: 'Governance', model: x.model, effort: x.eff, schema: R }))

const [dispo, esc, adrD, plat, exp, panels, gov] = await Promise.all([
  allDispo, Promise.all(escPromises), adrDispoP, Promise.all(platformPromises),
  Promise.all(expPromises), Promise.all(panelPromises), Promise.all(govPromises),
])

const count = arr => arr.filter(Boolean).length
return {
  dispositions_ok: count(dispo), dispositions_total: dispo.length,
  disposition_records: dispo.filter(Boolean).reduce((s, r) => s + (r.n_records || 0), 0),
  escalations_ok: count(esc), design_adr_dispo: adrD ? adrD.n_records : 0,
  domains_ok: count(domains), platform_ok: count(plat), experience_ok: count(exp),
  panels_ok: count(panels), governance_ok: count(gov),
}