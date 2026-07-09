# Architecture Decision Records — Design Audit of the Legacy Frontend

ADRs produced by the legacy design audit of `trilhas-frontend`
(`Dev-Infra-Grupo-AMH/trilhas-frontend` @ `f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`, audited 2026-07-03).

Each ADR follows MADR format and reviews one significant legacy design decision: what the
legacy platform did (cited to source), the evident rationale, an audit assessment, and a
recommended decision for the new platform. **Ratification batch completed 2026-07-09:**
ADR-0001 and ADR-0019 are **accepted**; ADRs 0002–0018 are **superseded by ADR-0019**
(stack ratification: Next.js + Radix UI + Tailwind CSS v4). ADRs 0020–0029 are **accepted**
(backend clinical architecture — verified implemented in code).

Supporting evidence: [../design/design-system-inventory.md](../design/design-system-inventory.md)
(full token/component/UX inventory with source citations).

## Index

### Foundations: stack, theming, tokens

| ADR | Title | Status | Recommendation in one line |
|---|---|---|---|
| [0001](0001-frontend-stack-and-ui-library.md) | Frontend framework and UI-library foundation | **accepted** | Upgrade in place to Next.js (app router) + React 18+ + AntD v5; replace Less `modifyVars` theming with `ConfigProvider` tokens; make PT-BR-only an explicit, reversible i18n decision. |
| [0002](0002-dark-first-compact-base-theme.md) | Dark-first, compact base theme baked at build time | superseded by ADR-0019 | Keep dark+compact as the documented default (glare/density rationale) but as one of two symmetric token-driven variants. |
| [0003](0003-light-mode-client-overlay.md) | Light mode as a client-only, cookie-gated CSS overlay | superseded by ADR-0019 | Replace the 4-layer cascade overlay (cookie + full reload + ~30 patches) with token-driven, reload-free theme switching. |
| [0004](0004-per-tenant-white-label-runtime-color.md) | Per-tenant white-label via runtime-recompiled primary color | superseded by ADR-0019 | Keep per-tenant branding; resolve one deterministic token before first paint instead of runtime Less recompilation (fixes flash-of-default-orange). |
| [0005](0005-design-token-source-of-truth-and-governance.md) | Design-token source of truth and governance | superseded by ADR-0019 | Single tokens source generating build config + CSS variables, with a lint asserting every `var(--x)` resolves (legacy left `--warning-color` undefined). |
| [0006](0006-no-formal-token-scales.md) | No formal token scales (spacing, radius, elevation, z-index, motion, type) | superseded by ADR-0019 | Adopt full formal scales derived from the legacy's implicit clusters instead of 100%-literal px/rem values. |
| [0007](0007-neumorphic-elevation-visual-signature.md) | Neumorphic dual-shadow elevation as visual signature | superseded by ADR-0019 | Preserve the signature look as a governed, contrast-verified elevation-token scale applied via a shared utility. |

### Components, layout, information architecture

| ADR | Title | Status | Recommendation in one line |
|---|---|---|---|
| [0008](0008-pagecontainer-app-shell-cascading-refetch.md) | PageContainer app shell with cascading per-page tenant refetch | superseded by ADR-0019 | Keep one app shell; back tenant context with a shared cache; move auth/tenant gating to route-level guards. |
| [0009](0009-information-architecture-no-persistent-nav.md) | Drill-down tiles, header switcher, FAB, no persistent nav | superseded by ADR-0019 | Keep tile drill-down + header switcher; add one real full-depth breadcrumb component. |
| [0010](0010-drawer-in-drawer-secondary-view-pattern.md) | Drawer-in-drawer as the secondary/tertiary-view pattern | superseded by ADR-0019 | Keep DrawerBuilder; add a generic overlay-stack manager (nesting, Esc/back, focus trapping). |
| [0011](0011-js-window-width-responsive-strategy.md) | Responsive layout via JS window-width comparisons | superseded by ADR-0019 | One shared breakpoint token set feeding JS and CSS; forked component trees only where density truly differs. |
| [0012](0012-canonical-primitives-vs-parallel-implementations.md) | Canonical primitives vs parallel and dead implementations | superseded by ADR-0019 | Canonicalize the core primitive set; consolidate duplicate tab/badge implementations; retire dead components; enforce via registry + lint. |

### Clinical UX

| ADR | Title | Status | Recommendation in one line |
|---|---|---|---|
| [0013](0013-clinical-severity-color-system.md) | Clinical severity color system (`statusTrilha`) vs ad-hoc literals | superseded by ADR-0019 | Promote to a typed, contrast-checked `clinical.*` severity token scale, separate from tenant branding; fix the severity-blind toast. |
| [0014](0014-no-abnormal-value-threshold-flagging.md) | No threshold/reference-range flagging of abnormal values | superseded by ADR-0019 | Build a centralized reference-range service + shared abnormal-value severity scale across vitals/labs/fluid balance/SOFA; ready for AI-agent severity signals. |
| [0015](0015-config-driven-dynamic-clinical-form-engine.md) | Config/schema-driven dynamic clinical form engine | superseded by ADR-0019 | Preserve and modernize the form engine: typed shared schema + one unified visibility/nullability rule engine (replacing three uncoordinated mechanisms). |
| [0016](0016-feedback-and-loading-patterns.md) | Feedback and loading patterns | superseded by ADR-0019 | Centralize error handling in an HTTP-client interceptor with severity-based UI, decoupled from DRF's error shape. |

### Data flow and integration

| ADR | Title | Status | Recommendation in one line |
|---|---|---|---|
| [0017](0017-fragmented-real-time-architecture.md) | Fragmented real-time architecture (WebSocket + Firestore + polling) | superseded by ADR-0019 | Standardize on one push transport with shared reconnect/backoff for notifications, chat, and feeds. |
| [0018](0018-client-integration-and-authorization-model.md) | Client integration and authorization model | superseded by ADR-0019 | Deny-by-default server-enforced route guards (legacy `validateRoute` defaulted to `ignorePermission=true`); add a client query cache. |
| [0019](0019-stack-ratification-radix-tailwind.md) | Stack ratification: Radix UI + Tailwind CSS v4 | **accepted** | Ratify Radix UI + Tailwind CSS v4 over Ant Design v5; record the decision and complementary libraries. |

### trilhas-engine: architecture and data model (back-end)

| ADR | Title | Status | Recommendation in one line |
|---|---|---|---|
| [0020](0020-trilhas-engine-architecture.md) | trilhas-engine architecture: state machine vs declarative rule engine | **accepted** (implemented 2026-07-09) | Declarative, versioned alert-definition engine with build-time CI gates; 18 legacy rule dispositions mapped to v2 constructs. |
| [0021](0021-trilhas-engine-data-model.md) | trilhas-engine data model: versioning, snapshots, and cardinality | **accepted** | Immutable content-addressed definitions (Git as audit trail); 1:N patient-to-alert per encounter; no state snapshots — reproducibility via operational hypertables + Gold write-back. |

### Clinical domains (back-end)

| ADR | Title | Status | Recommendation in one line |
|---|---|---|---|
| [0022](0022-ventilacao-service-architecture.md) | Ventilação service architecture | **accepted** | Monolith merge (Option 1) with SemVer contracts; FiO₂-as-fraction enforced at build time. |
| [0023](0023-estabilidade-scoring-model.md) | Estabilidade scoring model | **accepted** | Threshold-based primary (Option 1) with ML enrichment deferred (Option 3 hybrid). |
| [0024](0024-piora-clinica-detection-strategy.md) | Piora Clínica detection — 13 rules | **accepted** | Standalone PioraClinicaService (Option 1); DMN decision tables; L0-hard constraint. |
| [0025](0025-movimentacao-adt-integration-pattern.md) | Movimentação-ADT integration — 74 rules | **accepted** | Materialized view in PostgreSQL (Option 2); CDC consumer; daily reconciliation. |
| [0026](0026-prescricao-drug-interaction-safety.md) | Prescrição drug interaction safety — 43 rules | **accepted** | Local ANVISA base + external API fallback; 4 severity levels. |
| [0027](0027-prescricao-lifecycle-state-machine.md) | Prescrição lifecycle state machine | **accepted** | Formal state machine (Option 2) with 5 states + transition guards. |
| [0028](0028-evolucoes-clinical-notes-architecture.md) | Evoluções Clínicas — 81 rules, 14 roles | **accepted** | Hybrid SBAR template (Option 2); immutable notes; LLM as assistant. |
| [0029](0029-formularios-clinicos-dynamic-form-engine.md) | Formulários Clínicos dynamic form engine — 49 rules | **accepted** | Hybrid (Option 3): TypeScript source + build-time schema; offline-first. |

### Legacy reference

| ADR | Title | Status | Notes |
|---|---|---|---|
| [ADR-001](ADR-001-amh-data-platform-consumer.md) | AMH Data Platform Consumer | **accepted** | Foundational: IntensiCare as consumer of AMH Data Platform |

## How these were produced

Three parallel design-inventory audits (tokens; component library & IA; clinical UX patterns)
over the pinned commit, consolidated into the design-system inventory, then one writer per
ADR working from the inventory plus direct source verification. Raw inventory notes:
[../design/_inventory/](../design/_inventory/).
