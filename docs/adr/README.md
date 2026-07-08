# Architecture Decision Records — Design Audit of the Legacy Frontend

ADRs produced by the legacy design audit of `trilhas-frontend`
(`Dev-Infra-Grupo-AMH/trilhas-frontend` @ `f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`, audited 2026-07-03).

Each ADR follows MADR format and reviews one significant legacy design decision: what the
legacy platform did (cited to source), the evident rationale, an audit assessment, and a
recommended decision for the new platform. All outcomes are **proposed** — recommendations
pending team ratification, not ratified decisions.

Supporting evidence: [../design/design-system-inventory.md](../design/design-system-inventory.md)
(full token/component/UX inventory with source citations).

## Index

### Foundations: stack, theming, tokens

| ADR | Title | Recommendation in one line |
|---|---|---|
| [0001](0001-frontend-stack-and-ui-library.md) | Frontend framework and UI-library foundation | Upgrade in place to Next.js (app router) + React 18+ + AntD v5; replace Less `modifyVars` theming with `ConfigProvider` tokens; make PT-BR-only an explicit, reversible i18n decision. |
| [0002](0002-dark-first-compact-base-theme.md) | Dark-first, compact base theme baked at build time | Keep dark+compact as the documented default (glare/density rationale) but as one of two symmetric token-driven variants. |
| [0003](0003-light-mode-client-overlay.md) | Light mode as a client-only, cookie-gated CSS overlay | Replace the 4-layer cascade overlay (cookie + full reload + ~30 patches) with token-driven, reload-free theme switching. |
| [0004](0004-per-tenant-white-label-runtime-color.md) | Per-tenant white-label via runtime-recompiled primary color | Keep per-tenant branding; resolve one deterministic token before first paint instead of runtime Less recompilation (fixes flash-of-default-orange). |
| [0005](0005-design-token-source-of-truth-and-governance.md) | Design-token source of truth and governance | Single tokens source generating build config + CSS variables, with a lint asserting every `var(--x)` resolves (legacy left `--warning-color` undefined). |
| [0006](0006-no-formal-token-scales.md) | No formal token scales (spacing, radius, elevation, z-index, motion, type) | Adopt full formal scales derived from the legacy's implicit clusters instead of 100%-literal px/rem values. |
| [0007](0007-neumorphic-elevation-visual-signature.md) | Neumorphic dual-shadow elevation as visual signature | Preserve the signature look as a governed, contrast-verified elevation-token scale applied via a shared utility. |

### Components, layout, information architecture

| ADR | Title | Recommendation in one line |
|---|---|---|
| [0008](0008-pagecontainer-app-shell-cascading-refetch.md) | PageContainer app shell with cascading per-page tenant refetch | Keep one app shell; back tenant context with a shared cache; move auth/tenant gating to route-level guards. |
| [0009](0009-information-architecture-no-persistent-nav.md) | Drill-down tiles, header switcher, FAB, no persistent nav | Keep tile drill-down + header switcher; add one real full-depth breadcrumb component. |
| [0010](0010-drawer-in-drawer-secondary-view-pattern.md) | Drawer-in-drawer as the secondary/tertiary-view pattern | Keep DrawerBuilder; add a generic overlay-stack manager (nesting, Esc/back, focus trapping). |
| [0011](0011-js-window-width-responsive-strategy.md) | Responsive layout via JS window-width comparisons | One shared breakpoint token set feeding JS and CSS; forked component trees only where density truly differs. |
| [0012](0012-canonical-primitives-vs-parallel-implementations.md) | Canonical primitives vs parallel and dead implementations | Canonicalize the core primitive set; consolidate duplicate tab/badge implementations; retire dead components; enforce via registry + lint. |

### Clinical UX

| ADR | Title | Recommendation in one line |
|---|---|---|
| [0013](0013-clinical-severity-color-system.md) | Clinical severity color system (`statusTrilha`) vs ad-hoc literals | Promote to a typed, contrast-checked `clinical.*` severity token scale, separate from tenant branding; fix the severity-blind toast. |
| [0014](0014-no-abnormal-value-threshold-flagging.md) | No threshold/reference-range flagging of abnormal values | Build a centralized reference-range service + shared abnormal-value severity scale across vitals/labs/fluid balance/SOFA; ready for AI-agent severity signals. |
| [0015](0015-config-driven-dynamic-clinical-form-engine.md) | Config/schema-driven dynamic clinical form engine | Preserve and modernize the form engine: typed shared schema + one unified visibility/nullability rule engine (replacing three uncoordinated mechanisms). |
| [0016](0016-feedback-and-loading-patterns.md) | Feedback and loading patterns | Centralize error handling in an HTTP-client interceptor with severity-based UI, decoupled from DRF's error shape. |

### Data flow and integration

| ADR | Title | Recommendation in one line |
|---|---|---|
| [0017](0017-fragmented-real-time-architecture.md) | Fragmented real-time architecture (WebSocket + Firestore + polling) | Standardize on one push transport with shared reconnect/backoff for notifications, chat, and feeds. |
|| [0018](0018-client-integration-and-authorization-model.md) | Client integration and authorization model | Deny-by-default server-enforced route guards (legacy `validateRoute` defaulted to `ignorePermission=true`); add a client query cache. |
|| [0019](0019-stack-ratification-radix-tailwind.md) | Stack ratification: Radix UI + Tailwind CSS v4 | Ratify Radix UI + Tailwind CSS v4 over Ant Design v5; record the decision and complementary libraries. |

### trilhas-engine: architecture and data model (back-end)

|| ADR | Title | Recommendation in one line |
||---|---|---|
|| [0020](0020-trilhas-engine-architecture.md) | trilhas-engine architecture: state machine vs declarative rule engine | Declarative, versioned alert-definition engine with build-time CI gates; 18 legacy rule dispositions mapped to v2 constructs. |
|| [0021](0021-trilhas-engine-data-model.md) | trilhas-engine data model: versioning, snapshots, and cardinality | Immutable content-addressed definitions (Git as audit trail); 1:N patient-to-alert per encounter; no state snapshots — reproducibility via operational hypertables + Gold write-back. |

## How these were produced

Three parallel design-inventory audits (tokens; component library & IA; clinical UX patterns)
over the pinned commit, consolidated into the design-system inventory, then one writer per
ADR working from the inventory plus direct source verification. Raw inventory notes:
[../design/_inventory/](../design/_inventory/).
