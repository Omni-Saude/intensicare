# IntensiCare v2 — Frontend Architecture & Clinical Component Library

Deliverable of the **frontend-architect**. Defines the module boundaries, realtime-client
architecture, Radix-wrapped clinical component inventory, Storybook/visual-regression toolchain,
performance budgets, offline/degraded-mode posture, i18n scaffolding, and PWA/web-push surface for
the IntensiCare v2 frontend.

Inputs read in full: `docs/plan/_work/briefs/design-adrs.json` (18 legacy ADRs, `docs/adr/0001`–`0018`),
`docs/plan/_work/briefs/design-inventory.json` (legacy `trilhas-frontend` audit), `docs/plan/_work/briefs/vision.json`,
`docs/plan/_work/briefs/personas.json`, `docs/plan/_work/constraints/ledger.yaml`,
`docs/plan/product/product-spec.md` (US-01..US-30), `docs/plan/product/journey-maps.md` (MOT-01..20),
`docs/plan/architecture/system-architecture.md`, `docs/adr/0017-fragmented-real-time-architecture.md`.

Every design decision below is traced to a constraint ID (`CON-xxxx` in the ledger, or `ADR-C-xx` /
`DES-C-xx` / `PER-C-xx` / `VIS-C-xx` in the source briefs) or a user story (`US-xx`). Where this
document makes a call beyond what a brief settled, it is flagged **[DECISION]** and, where the stakes
warrant it, spun out into one of the three ADR drafts in `docs/plan/_work/adrs/`.

---

## 0. Stack decision (extends ADR-0001)

`ADR-0001` (legacy: Next.js 12 pages-router + React 17 + AntD 4, no i18n) recommended Next.js
app-router + React 18+ + AntD v5 as the *minimum* viable upgrade path. This plan adopts a further
step **[DECISION]**, directed for the v2 rebuild:

| Axis | Decision | Rationale |
|---|---|---|
| Framework | **Next.js (App Router), React 19** | Server Components let the tenant-color/permission resolution required by `ADR-C-01`/`CON-0050` and `ADR-C-05` happen server-side, ahead of first paint, with no client re-application step — the exact fix the audit demanded for the flash-of-default-orange and client-JSX-gated-render bugs. React 19 `use()` + Actions simplify the mutation flows the config-driven form engine needs (§6). |
| Language | **TypeScript, `strict: true`, `noUncheckedIndexedAccess: true`** | `CON-0043`/`ADR-C-10` requires clinical form configs to fail at compile time, not runtime, for a malformed shape — only enforceable under full strict mode. |
| Component primitives | **Radix UI (unstyled) + a first-party token layer**, not AntD v5 | The legacy's biggest primitive failure was *silent duplication* (two tab impls, two icon systems, two badge treatments — `ADR-C-06`/`CON-0044`-adjacent). Radix's headless primitives ship one correct a11y/state implementation per concern (focus trap, roving tabindex, dismiss-on-Escape) and force us to author exactly one styled wrapper per primitive, which is what a "canonical primitives" CI gate (`ADR-C-06`) needs to check against. AntD v5 was considered and rejected as the base because its themeable surface still couples visual and behavioral concerns in ways that made the legacy's parallel-implementation problem easy to fall into again. |
| Data layer | **TanStack Query v5** | Replaces the legacy's per-mount cascading REST refetch with no shared cache (`ADR-C-05`, `DES-4-01`) and the auth context that re-verifies on every mount with no cache (`DES-6-01`). |
| Realtime | **One realtime client module**, WebSocket primary + SSE fallback, shared reconnect/backoff | Direct implementation of `ADR-0017` Option 2, `ADR-C-12`/`ADR-C-13`, `CON-0045`/`CON-0046`/`CON-0053`. See §2 and `docs/plan/_work/adrs/realtime-channel-consolidation.md`. |
| Forms | **Config-driven schema engine**, typed, `zod`-validated | Preserves the legacy's "strongest reusable IP" (`DES-C-07`) while fixing `CON-0043`. See `docs/plan/_work/adrs/form-engine-stack.md`. |
| i18n | **`next-intl`, PT-BR as sole shipped locale, message-key discipline from day 1** | `ADR-0001` flags zero i18n as a legacy defect; v2 must not repeat "PT-BR strings inline" even while shipping PT-BR-only. See §7. |
| Styling | **CSS variables + a generated token module** (no LESS, no runtime recompile) | Direct fix for `CON-0050`/`CON-0051`/`ADR-C-02` (dead `--warning-color` bug) and `CON-0049` (severity vs. brand decoupling). Full token architecture (spacing/radius/elevation/z-index/motion/type scales) is the `design-token-systems-designer`'s deliverable (`CON-0049`–`CON-0052` owners); this document only states the *contract* the component layer consumes: every color/space/radius/shadow/duration value used by a component in §5 MUST resolve through a named token, never a literal, and CI MUST fail on an unresolved `var(--x)` (`ADR-C-02`, standing invariant, non-negotiable at this layer too). |

---

## 1. Module boundaries

```
apps/web/
├── app/                          # Next.js App Router — routes only, no business logic
│   ├── (auth)/login/
│   ├── (shell)/                  # authenticated shell — server-side tenant+permission
│   │   ├── layout.tsx            #   resolution BEFORE render (fixes ADR-C-01, ADR-C-05)
│   │   ├── units/[unitId]/       #   bed-board (US-06), core screen
│   │   │   ├── page.tsx
│   │   │   └── beds/[bedId]/     #   patient detail, drawer-routed (§5.9)
│   │   ├── rrt/                  #   mobile RRT surface (US-08, US-27, US-28) — PWA entry
│   │   ├── coordinator/          #   Fernanda's KPI dashboard (US-09, US-29, US-30)
│   │   └── governance/           #   threshold-change queue (US-25, US-26)
│   └── api/                      # route handlers used ONLY for BFF concerns (auth cookie
│                                  # exchange, SSE fallback proxy) — never business logic
├── modules/                      # feature modules, one per bounded clinical concern
│   ├── bed-board/                #   grid, filters, density function (fixes ADR-C-07/CON-0052)
│   ├── patient/                  #   header, score badges, vitals, trend charts
│   ├── alerts/                   #   alert card, disposition control, notification center
│   ├── clinical-forms/           #   config-driven form engine (§6, owned with forms-engine-architect)
│   ├── handoff/                  #   shift handoff summary (US-24)
│   ├── rrt/                      #   mobile attendance flow, outcome documentation (US-27/28)
│   └── coordinator-kpis/         #   dashboard widgets, export (US-29/30)
├── components/                   # canonical, generic (non-clinical) primitives — ONE impl each
│   ├── overlay/                  #   Drawer, OverlayStack manager (fixes ADR-C from ADR-0010)
│   ├── data-display/             #   Table, Tabs, Badge, IconSystem
│   └── feedback/                 #   Toast, ErrorBoundary, Skeleton, StalenessBanner
├── lib/
│   ├── design-tokens/            # generated from design-token-systems-designer's source (§0)
│   ├── query/                    # TanStack Query client, query-key registry, cache policies
│   ├── realtime/                 # THE single realtime client (§2) — no feature imports a
│   │                             #   transport directly
│   ├── severity/                 # clinical.* severity scale + reference-range service (CON-0054)
│   │                             #   — consumed, never re-implemented, by any component
│   ├── i18n/                     # next-intl config, PT-BR message catalog, key lint
│   └── auth/                     # deny-by-default route-guard helpers (ADR-C-05/CON-0047)
└── styles/                       # :root token CSS, theme data-attribute switch (no reload)
```

**Boundary rules (CI-enforced, not just documented):**

1. `modules/*` may import from `components/*` and `lib/*`, never from another `modules/*` directly
   (cross-module state goes through `lib/query` cache or `lib/realtime` topics). This is what
   prevents the legacy's ad-hoc coupling (e.g., chat presence directly poking bed-board refetch).
2. Only `lib/realtime` may hold a WebSocket/SSE connection object. No component or module opens a
   transport itself — this is the structural fix for the legacy's "two WebSocket connections for one
   feature" (`DES-6-02`) and is how `ADR-C-06`'s "no second implementation of a registered primitive"
   extends to transports.
3. Only `lib/severity` computes or maps a clinical severity color/band. No component hardcodes a
   severity hex or literal band cutoff — this is the structural fix for `CON-0049` and the two live
   severity bugs (`ADR-C-09`): toast icon color and criteria-panel color must both read through this
   module, never a hardcoded key.
4. `app/(shell)/layout.tsx` performs tenant/permission resolution as a **server** step; no page may
   render behind a client-side `token && tenant.id && !loading` gate (closes `ADR-C-05`, `DES-4-01`,
   `DES-4-04`).

---

## 2. Realtime client — one module, WebSocket + SSE fallback

Full decision record: `docs/plan/_work/adrs/realtime-channel-consolidation.md`. Summary for the
component layer:

- **`lib/realtime/client.ts`** is the only object in the frontend allowed to hold a live connection.
  It exposes `subscribe(topic, handler)` / `publish(topic, payload)` (ack-only mutations, e.g.
  mark-read) and nothing else to consumers.
- **Transport:** WebSocket primary (matches the backend's `FastAPI REST + WebSocket` container,
  `system-architecture.md` line 80/100); **SSE fallback** for networks/proxies that block WS upgrade
  (a real ICU-hospital-network condition the legacy never had to handle because the bed board never
  attempted push at all). Fallback selection is automatic and transparent to subscribers — a
  component never knows which transport is live.
- **Shared reconnect/backoff**, exponential with jitter, single implementation, replacing zero
  implementations today (`ADR-0017` Consequences, `CON-0045`).
- **Topic multiplexing** over one connection per client: `bed.<bedId>.alert`, `bed.<bedId>.vitals`,
  `unit.<unitId>.occupancy`, `notification.<userId>`, `rrt.<userId>.dispatch`. Replaces the legacy's
  two WebSocket connections + Firestore doc + poll timer with one pipe (`DES-6-02`).
- **System-of-record discipline (`CON-0045`, standing invariant):** every payload on the wire is
  either (a) a "something changed, refetch" signal that triggers a `queryClient.invalidateQueries`
  call, or (b) a thin, idempotent patch (`{bedId, alertId, severity, version}`) that the client
  reconciles against the TanStack Query cache by version, never applied blind. The realtime module
  itself is not a cache; `lib/query` remains the only place a component reads state from.
- **Same-channel guarantee (`CON-0046`):** the bed-board grid and the notification bell subscribe to
  the *same* `bed.<bedId>.alert` topic family. This is what makes bell/grid disagreement (the audit's
  named life-safety defect, `ADR-C-13`) structurally impossible rather than merely unlikely.
- **Connection-state UI:** `<ConnectionStatusIndicator>` (§5.13) is mounted once in the shell and
  reflects `lib/realtime`'s connection state machine (`connected | reconnecting | degraded`); this is
  new surface area the legacy had nowhere (`ADR-0017` Consequences).
- **Ownership boundary:** the *server-side* transport/protocol contract (gateway or managed pub/sub,
  message envelope, auth-on-connect) is the `realtime-architect`'s deliverable (`CON-0045`/`CON-0046`/
  `CON-0053` owners). This document owns the *client* consuming that contract and the guarantee that
  no second client-side transport implementation is ever added.

---

## 3. Data layer — TanStack Query

- One `QueryClient` per browser tab, hydrated from server-rendered initial data where the route
  supports it (bed-board first paint, §8).
- **Query-key registry** (`lib/query/keys.ts`) is the single source of key-shape truth — no
  ad-hoc key construction in feature modules, closing off the legacy's "cascading refetch, no shared
  cache" failure mode (`ADR-C-05`) at the root.
- **Cache policies by data class:**
  - Clinical vitals/alerts/occupancy: `staleTime: 0`, refresh is realtime-driven (§2), never
    interval-polled (`CON-0053`, `DES-C-05`).
  - Reference/config data (unit list, threshold definitions, form configs): `staleTime` in minutes,
    background-revalidated.
  - Mutations (acknowledge alert, log intervention, RRT outcome) use optimistic updates with
    server-confirmed rollback, instrumented per `US-05`/`US-12`/`US-22`/`US-28` (event-emission
    acceptance criteria).
- **Error classification** (`CON-0044`, owned here): an HTTP client interceptor classifies every
  failure as `validation | permission | server` from HTTP status + a backend-agnostic envelope
  contract (never assumes a DRF-shaped body — the legacy's `handleApiError` bug), and maps that
  classification to visual weight per `ADR-0016`'s recommendation: inline for validation, toast for
  permission, modal only for server faults that block the current task. No component calls
  `Modal.error` directly.

---

## 4. Design-token consumption contract

Ownership of the token *source* (spacing/radius/elevation/z-index/motion/type scales, the
brand-vs-clinical color split) sits with `design-token-systems-designer` (`CON-0049`–`CON-0052`).
This document fixes what the component layer promises to do with that source, since every clinical
component in §5 depends on it:

- Every component in §5 is styled exclusively via CSS custom properties generated from the token
  source; **zero literal hex/px/ms values** in component code. CI lints for raw literals in
  `modules/*` and `components/*` and fails the build (closes `ADR-C-02`/`CON-0051` at the consumption
  edge, not just the token-definition edge).
- `clinical.*` severity tokens and `brand.*` tenant tokens are imported from **separate** modules
  (`lib/severity/tokens` vs `lib/design-tokens/brand`) with no shared identifier — this makes
  `CON-0049` a type-level guarantee: a component cannot accidentally key a severity color off a brand
  token because the two token namespaces don't share a type.
- Theme switching (dark/light, compact/comfortable) is a `data-theme`/`data-density` attribute swap
  with CSS custom-property redefinition — **no `window.location.reload()`**, fixing the legacy's
  single most-flagged theming defect (`ADR-C` under `ADR-0003`, `CON-0050`).
- Breakpoints are consumed from one generated `lib/design-tokens/breakpoints` module shared by CSS
  container queries and any JS layout math (the bed-grid density function, §5.1) — no component
  computes its own `window.innerWidth` bucket chain (closes `ADR-C-07`/`CON-0052`, including the
  audited `(2400px,2800px]` dead band).

---

## 5. Radix-wrapped clinical component inventory

Each entry: purpose, states, a11y contract, severity handling. "Radix primitive" names the headless
base; "—" means no direct Radix equivalent (bespoke, built to the same a11y discipline).

### 5.1 `BedGrid` / `BedCard`

- **Radix primitive:** — (custom virtualized grid; Radix `Tooltip`/`HoverCard` for the per-bed
  quick-peek).
- **Purpose:** the core screen (`US-06`, MOT-01) — one card per bed, density-adaptive, showing score,
  trend direction, active alert state, and time-since-last-vital at a glance.
- **States:** `occupied-stable | occupied-alerting(severity) | occupied-assisted-override |
  empty | stale(>staleness-threshold) | loading-skeleton | reconnecting-degraded`.
- **A11y contract:** grid role with `aria-rowcount`/`aria-colcount`; each card is a single tab stop
  with arrow-key roving navigation between cards (not into card internals) so a clinician can scan 90
  beds by keyboard; each card's accessible name states patient identifier, bed number, current
  severity word (not just color), and score value — never color-only signaling (WCAG 1.4.1, and the
  direct fix for `DES-5-04`'s "SpO2 99% and 60% render identically" gap once wired to `lib/severity`).
  Focus-visible ring meets contrast in both themes (`ADR-C-04`).
- **Severity handling:** border/glow/ball color reads `clinical.*` via `lib/severity` only (`CON-0049`);
  `ASSISTIDO`-style human-override state is modeled explicitly as its own state value, not a
  post-hoc override of the raw severity (carries forward `statusTrilha`'s override semantics per
  `ADR-0013`, `open_questions` item on re-derived hex needing clinical sign-off — flagged for
  ratification, not decided here). Empty beds get a visually distinct neutral treatment, not the
  same flat border the legacy gave both empty and NEUTRO-occupied beds (`DES-5-03`).
- **Density function:** one shared, unit-tested function mapping viewport width → column span,
  covering the *full* width domain with no gap band (fixes `ADR-C-07`; the legacy's undefined
  `(2400,2800]` span bug is a named regression test, not a "nice to have").
- **Performance:** see §8 — this is the 60fps/90-bed budget owner.

### 5.2 `ScoreBadge`

- **Radix primitive:** `Tooltip` (component breakdown on hover/focus).
- **Purpose:** renders MEWS/SOFA/NEWS2/qSOFA with the correct escalation band, replacing the legacy's
  static `Tag color="warning"` regardless of score (`DES-5-05`).
- **States:** `normal | elevated | urgent | critical`, each with its own band boundary per score type
  (e.g., MEWS ≥5 urgente / ≥7 crítico per `US-03`), sourced from `lib/severity`'s reference-range
  service, not hardcoded per component (`CON-0054`).
- **A11y contract:** the numeric score and the band word are both in the accessible name
  (`"MEWS 8, crítico"`), satisfying `PER-C-04` (which parameter/value drove the state must always be
  inspectable, not just implied by color).
- **Severity handling:** identical token path to `BedGrid`; tapping/clicking opens the per-component
  breakdown (`US-04`, US-07 AC2) — "por que subiu?" from MOT-02 — never just the aggregate number.

### 5.3 `VitalsList` / `ReferenceRangeFlag`

- **Radix primitive:** — (semantic `dl`/table markup; Radix `Popover` for the reference-range detail).
- **Purpose:** the direct fix for the audit's **top clinical UX gap** (`DES-C-06`/`ADR-C-14 (0014)`):
  every vital/lab value is flagged against its reference range, not rendered through a neutral
  `ListItem` row regardless of magnitude.
- **States:** `within-range | mild | moderate | critical | no-data | pending-context (age/condition-
  adjusted range not yet resolved)`.
- **A11y contract:** flag state is conveyed by icon + text label + color, never color alone; each row
  is independently focusable and its accessible name includes the flag word.
- **Severity handling:** consumes `lib/severity`'s reference-range service, explicitly designed to
  **also accept agent/algorithm-derived signals** later (per `ADR-0014`'s recommendation) without a
  component-level API change — the component takes a `severity` prop, not a raw value plus inline
  threshold logic. Reference ranges themselves (age/context-adjusted bands) are a clinical-content
  deliverable, not decided in this document (`open_questions` in `design-inventory.json`).

### 5.4 `TrendChart`

- **Radix primitive:** — (SVG/canvas chart; Radix `Toggle Group` for score-type/time-window switch).
- **Purpose:** 24h score/vital trend (`US-10`, `PER-CARLOS-03`, MOT-02), with the delta-since-
  overnight emphasis MOT-01 calls for.
- **States:** `loading | populated | sparse-data (fewer than N points) | no-data`.
- **A11y contract:** chart exposes an accessible data-table fallback (`<table>` toggled via a visually
  hidden control) — a screen-reader user must be able to get the same 24h trend a sighted clinician
  gets, not just a `<canvas>` with no text alternative.
- **Severity handling:** the plotted line/area uses `clinical.*` band colors as background reference
  bands (not just a single-color line), so a value crossing into a critical band is visually evident
  on the trend itself, not only at the current-value badge.

### 5.5 `AlertCard` / `AlertDispositionControl`

- **Radix primitive:** `AlertDialog` (destructive dispositions), `DropdownMenu` (disposition picker).
- **Purpose:** surfaces an active alert with its full explanation (`US-21`) and lets a clinician
  acknowledge/disposition it in one interaction (`US-05`, `US-22`, `PER-C-05`).
- **States:** `active-unacknowledged | acknowledged | dispositioned(reason) | expired |
  superseded-by-newer-alert`.
- **A11y contract:** disposition control is operable via keyboard alone in the "1 click" budget
  (`PER-C-05`) — a single `Enter`/`Space` on a default action commits the most common disposition;
  the dropdown for alternate dispositions is a secondary, discoverable-but-not-required path.
- **Severity handling:** **fixes both named legacy severity bugs** (`ADR-C-09`): the card's icon color
  is *always* derived from the alert's actual severity via `lib/severity` (never the legacy's
  hardcoded amber `#FFAB00` toast), and a multi-criterion alert colors *each criterion* by that
  criterion's own value, never a single hardcoded `'VERMELHO'` key for the whole panel.
- **Explainability:** every instance renders "exactly which parameter triggered it" (`PER-C-04`) —
  this is a required prop, not an optional enhancement; a component instantiated without it is a
  type error.

### 5.6 `NotificationCenter`

- **Radix primitive:** `Popover` + `ScrollArea`.
- **Purpose:** single bell/drawer subscribing to `lib/realtime`'s `notification.<userId>` topic
  (§2) — replaces the legacy's two independent WebSocket connections for list + toast (`DES-6-02`).
- **States:** `empty | unread(count) | connection-degraded (shows the same `ConnectionStatusIndicator`
  state, §5.13, so a clinician knows *why* nothing new has arrived)`.
- **A11y contract:** `aria-live="polite"` region for new-notification announcement; the unread-count
  badge is the **canonical** badge implementation (§5.14) — no second hand-rolled count treatment.

### 5.7 `StalenessBanner`

- **Radix primitive:** — (bespoke banner, `role="status"`).
- **Purpose:** new surface with no legacy equivalent, required by the offline/degraded-mode decision
  (§9, `docs/plan/_work/adrs/offline-mode-scope.md`): whenever `lib/realtime`'s connection state is
  `degraded` for longer than a threshold, or a specific bed/patient's data is older than its
  freshness SLA, this banner makes staleness explicit rather than letting a stale board "look stable"
  (the MOT-01 failure mode named against the legacy).
- **States:** `fresh (hidden) | degraded-connection | stale-data(ageMinutes) | reconnected (transient
  confirmation)`.
- **A11y contract:** `role="status"`/`aria-live="polite"`, non-modal — never blocks interaction with
  the (still-usable, if stale) underlying data.

### 5.8 `ClinicalFormEngine` (config-driven)

- **Radix primitive:** `Form` primitives are hand-rolled on top of native `<form>` + Radix `Select`,
  `Checkbox`, `RadioGroup`, `Switch` per field type.
- **Purpose:** modernizes `FormDadosProntuario` (`DES-C-07`, "strongest reusable IP") — one engine
  dispatching a typed field-config array to per-type renderers, backing all clinical documentation
  (nursing, physician, RRT outcome `US-28`, fluid balance, etc.).
- **States:** per-field `pristine | dirty | validating | error | disabled(permission|conditional)`;
  per-form `draft | submitting | submitted | submit-failed`.
- **A11y contract:** every field-type renderer owns its own label association, error announcement
  (`aria-describedby` + `aria-invalid`), and keyboard operability — defined once per type, inherited
  by all 14+ role configs, so a11y is not re-litigated per config the way styling was in the legacy.
- **Severity handling:** N/A directly, but score-bearing fields (e.g., a form that captures a RASS or
  GCS value) render their live-computed score through `ScoreBadge` (§5.2) inline, not a static tag.
- **Full stack decision:** `docs/plan/_work/adrs/form-engine-stack.md`.

### 5.9 `OverlayStack` (Drawer manager)

- **Radix primitive:** `Dialog` (as the drawer base, `modal` + non-modal variants).
- **Purpose:** generalizes the legacy's `DrawerBuilder` (`DES-3-02`, preserve) into a managed stack
  that fixes the missing coordination the audit flagged (`ADR-0010`): nesting depth, Esc/back closing
  only the topmost layer, per-level focus trap.
- **States:** `closed | open(depth: n) | closing(animating)`.
- **A11y contract:** each level traps focus independently; `Escape` closes exactly one level; screen
  readers announce the new drawer's heading on open; background content gets `inert`/`aria-hidden`
  at every depth, not just depth 1 (the legacy's gap).

### 5.10 `Breadcrumb`

- **Radix primitive:** — (semantic `nav > ol`).
- **Purpose:** the **one** persistent, full-depth breadcrumb recommended by `ADR-0009`, replacing the
  legacy's hand-built Tag trail that stopped short of the deepest screens and the dead, unused
  Breadcrumb component that already existed but was never wired up (`DES-3-06`).
- **A11y contract:** `nav aria-label="breadcrumb"`, current page marked `aria-current="page"`.

### 5.11 `Tabs`

- **Radix primitive:** `Tabs`.
- **Purpose:** the **canonical** tab implementation (fixes `ADR-C-06`: legacy had AntD Tabs *and* a
  bespoke `CustomTabs` sliding-underline variant at 2 sites — CI blocks a second tab implementation
  from being registered).
- **Severity handling:** when tabs represent per-criterion or per-trilha state (as `TabRecomendacoes`
  did), each tab's indicator color reads `lib/severity` keyed to *that tab's own* criterion — the
  direct fix for the hardcoded-`'VERMELHO'` bug (`ADR-C-09`).

### 5.12 `IconSystem`

- **Radix primitive:** — (`Slot`-based polymorphic icon wrapper).
- **Purpose:** one sizing/registration contract for both a general icon set and the clinical
  role-icon set (Enfermagem, Médico, Fisioterapeuta, etc.), fixing the legacy's two unrelated icon
  systems with no shared sizing contract (`DES-3-01`, `ADR-C-06`).
- **A11y contract:** decorative icons are `aria-hidden`; meaningful icons require an explicit label
  prop (no icon ships without an accessible name path).

### 5.13 `ConnectionStatusIndicator`

- **Radix primitive:** `Tooltip`.
- **Purpose:** surfaces `lib/realtime`'s connection state machine (§2) — new to v2, the legacy had no
  connection-state UI anywhere (`ADR-0017` Consequences).
- **States:** `connected | reconnecting(attempt n) | degraded(fallback-transport-active) | offline`.
- **A11y contract:** `role="status"`, state-change announced via `aria-live="polite"` at most once per
  transition (debounced) to avoid announcement spam during flapping connections.

### 5.14 `CountBadge`

- **Purpose:** the canonical unread/count badge (fixes `ADR-C-06`: legacy had AntD `Badge` *and* a
  hand-rolled capped-at-99 div keyed off the wrong color source — `@secondary-color`, not the alert
  palette, `DES-3-06`).
- **Severity handling:** when the count represents unacknowledged *alerts* (not generic unread
  messages), its color reads the highest-severity item in the count via `lib/severity`, never a
  fixed brand/secondary color.

### 5.15 `SkeletonLoader`

- **Purpose:** content-shaped loading placeholders per `ADR-0016`'s recommendation, replacing the
  legacy's generic 4-row `SkeletonList` and full-viewport-blocking `FadeLoading` spinner used for
  "most mutations" (`DES-5-07`).
- **Rule (formalized, `CON-0044`-adjacent):** page-load = content-shaped skeleton; mutation = inline,
  non-blocking spinner scoped to the affected control; full-screen block reserved for destructive,
  irreversible actions only — a clinician must be able to keep working elsewhere on screen while a
  background save completes.

### 5.16 `RRTMobileCard` / `OutcomeDocumentationSheet`

- **Radix primitive:** `Dialog` (bottom-sheet variant on small viewports).
- **Purpose:** the en-route mobile patient screen (`US-27`) and <1-minute outcome documentation
  (`US-28`, `PER-C-07`) — responsive web, explicitly **not** a native app (`product-spec.md` §4 WON'T,
  US-27 AC3).
- **States:** patient screen `loading | loaded | stale`; outcome sheet `empty | drafting |
  submitting | submitted`.
- **A11y contract:** large touch targets (one-handed, in motion, per `PER-RAFAEL` flow); outcome
  options are a single-tap structured list plus an optional free-text field, not a multi-step form.

### 5.17 `KpiDashboardWidgets` (Fernanda's coordinator surface)

- **Purpose:** occupancy/acuity, alert-response-time, alarm-fatigue, and score-latency-compliance
  widgets (`US-09`, `US-23`, `US-29`) plus the export action (`US-30`, `PER-C-08`).
- **A11y contract:** every chart widget ships the same accessible-table fallback pattern as
  `TrendChart` (§5.4) — a coordinator using assistive tech gets the same KPI numbers.
- **Note:** the export button is a thin trigger; the export pipeline itself (schema versioning, LGPD
  minimization, audit logging per export) is `analytics-etl-lead`'s deliverable (`CON-0094` owner) —
  this component only owns the request/confirmation UI.

---

## 6. Storybook + visual-regression toolchain

- **Storybook 8** (Vite builder, matching the Next.js/Vite-compatible toolchain), one story file per
  component in `components/*` and `modules/*/components/*`.
- **Story coverage requirement (CI-enforced):** every state enumerated in §5's "States" column must
  have a corresponding story — a component cannot ship with an undocumented state, which is how the
  legacy accumulated silently-broken states (e.g., SOFA always rendering the same static tag
  regardless of score, `DES-5-05`, because no story ever exercised the "score = 20" case).
- **A11y checks:** `@storybook/addon-a11y` (axe-core) gates every story in CI — zero serious/critical
  violations to merge. This is the mechanical enforcement of the a11y contracts in §5.
- **Visual regression:** Chromatic (or a self-hosted Playwright + `pixelmatch` equivalent if
  Chromatic's SaaS dependency is rejected — a hosting decision out of this document's scope) runs on
  every PR against both themes (dark/light) × both densities (compact/comfortable) × two viewport
  classes (bed-board desktop, RRT mobile) — 8 permutations per changed story. This is the concrete
  mechanism satisfying `ADR-C-04` ("any surface carrying clinical content over a neumorphic background
  MUST pass an explicit contrast check in both themes") continuously, not as a one-time audit.
- **Severity-token snapshot test:** a dedicated Storybook story renders every `clinical.*` band at
  every component that consumes it (`BedGrid`, `ScoreBadge`, `AlertCard`, `Tabs`, `CountBadge`) in a
  single matrix page — a reviewer can visually confirm severity-color consistency across the whole
  component set in one screenshot diff, directly targeting the legacy's "green/amber/red reinvented
  in 6+ places" defect (`DES-5-02`).
- **Interaction tests:** `@storybook/test` (`play` functions) drive keyboard-only interaction through
  `OverlayStack`, `AlertDispositionControl`, and `ClinicalFormEngine` conditional-field logic in CI —
  the three areas where the legacy had the most undocumented, un-tested state machines (drawer
  nesting, `nullifyFields`/`checavel` conditional visibility).

---

## 7. i18n scaffolding — PT-BR-first

- **Library:** `next-intl`, App-Router-native, server-component-compatible (needed since tenant/locale
  resolution happens server-side per §0/§1).
- **Locale posture:** PT-BR is the only shipped locale at launch (matches legacy reality and current
  scope — `DES-1-01` notes the legacy was PT-BR-only with zero i18n infrastructure). v2 does **not**
  ship a second locale; it ships the *scaffolding* so adding one later is a message-catalog exercise,
  not a rearchitecture:
  - Every user-facing string in `modules/*` and `components/*` is a message key (`t('bedGrid.staleFor', {minutes})`),
    never an inline literal — enforced by an ESLint rule banning bare string JSX children in those
    directories (with a narrow, explicitly-listed exception list for truly non-localizable content
    like ICD-style codes).
  - Clinical vocabulary (RASS labels, SDRA severity bands, disposition reasons, etc.) is centralized
    in one PT-BR message namespace per domain, reusing the verbatim PT-BR vocabulary already
    catalogued in the clinical-scoring/sepse/etc. clusters, so the string of record matches what
    clinicians already expect (muscle memory, echoing the `ADR-0013` open question about not
    surprising clinicians with re-derived values).
  - Number/date formatting goes through `next-intl`'s formatters (`pt-BR` locale) from day 1, so time-
    since-vital, score deltas, and 24h-window labels are never manually string-built (a source of the
    legacy's inconsistent formatting).
  - Locale files are structured per-module (`lib/i18n/messages/pt-BR/bed-board.json`, etc.) mirroring
    the module boundary in §1, so a future locale addition is reviewable module-by-module.

---

## 8. Performance budgets

| Budget | Target | Notes |
|---|---|---|
| **Bed-grid frame rate** | **60fps sustained at 90 occupied beds**, including one active realtime patch/sec across the visible set | Virtualize rows beyond the viewport (only mount visible + overscan-1 row of `BedCard`s); severity-color and score updates from `lib/realtime` patch only the affected card's CSS custom properties, never a full-grid re-render; `React.memo` + stable keys keyed on bed ID, not array index. Neumorphic dual-shadow elevation (`ADR-0007`) is validated against this budget specifically — the audit flagged 23 unbenchmarked box-shadow declarations as a paint-cost risk at bed-board scale (`ADR-0007` Notes); if dual-shadow demonstrably regresses the 60fps target under load-testing, the flat-shadow fallback (already required for `prefers-contrast`) becomes the default at this density, not just an accessibility fallback. **[flagged for the visual/perf validation pass — not resolved here.]** |
| **First contentful paint, bed-board route** | **< 1.5s** on a representative ICU-network profile (mid-tier corporate Wi-Fi, not fiber) | Server-rendered initial bed-grid HTML (tenant color + first page of beds resolved server-side per §0/§1) with client hydration completing before the realtime subscription attaches — a clinician sees *a* board immediately, then it goes live. |
| **Time-to-interactive, bed-board route** | **< 2.5s** | Route-level code splitting: `clinical-forms` module (heaviest, 14+ configs) is not in the bed-board's initial bundle; it loads on first drawer-open. |
| **Score-badge render latency after a realtime patch** | **< 100ms** from message receipt to DOM update | Supports the *feel* of `PER-C-01`'s <30s score-availability SLO (which is primarily a backend/ingestion budget, `VIS-C-09`) — the frontend's contribution to that budget must be negligible, not the bottleneck. |
| **RRT mobile notification-to-render** | Screen usable **< 2s** after tapping a push notification (contributes to `PER-C-06`'s <5s end-to-end budget, most of which is backend dispatch latency) | Patient screen (§5.16) is precached (service worker, §10) so opening it from a notification doesn't cold-start a full bundle fetch on a hospital Wi-Fi/cellular handoff. |
| **JS bundle, initial route** | **< 200KB gzipped** for the bed-board shell (excluding lazily-loaded modules) | Radix primitives are tree-shaken per-component import, not a monolithic UI-kit import (this is part of why AntD v5's larger surface was rejected in §0). |
| **Visual-regression CI wall time** | **< 8 min** for the full 8-permutation matrix (§6) on a changed-story diff | Keeps the toolchain from becoming a reason to skip it. |

All budgets are enforced via CI (Lighthouse CI for paint/TTI/bundle-size budgets, a custom
`BedGrid` frame-rate harness using Playwright + `requestAnimationFrame` sampling for the 60fps
budget) — a PR that regresses a budget fails, it is not a manual review checklist item.

---

## 9. Offline / degraded-mode decision

**Full ADR draft:** `docs/plan/_work/adrs/offline-mode-scope.md`. Summary:

**v2 decision:** the frontend supports a **read-only degraded mode** with explicit staleness
banners (`StalenessBanner`, §5.7) when connectivity to the realtime channel and/or the API is
lost or degraded. **v2 does not support offline writes of any kind.** The legacy `trilha_homecare`
offline-sync mechanism (single-tenant-hardcoded to `whitelabel='homecare'`, with a documented
timestamp-labeling corruption defect and no cross-tenant generalization —
`operacional-infra.json` `CLU-OPERACIONAL-INFRA-07`/`RULE-OPERACIONAL-INFRA-021/022`) is
**retired**, not ported, generalized, or reused as a starting point for v2's degraded mode.

Rationale in brief (full reasoning + rejected options in the ADR): an ICU clinical-decision-support
tool writing clinical actions (dispositions, form submissions, vitals overrides) while offline
creates a reconciliation-conflict and stale-clinical-judgment risk that the audit's own findings
about the legacy offline path (`DES-C` risk class, tenant-hardcoding, timestamp corruption) argue
against reintroducing, especially for a patient-safety-classified SaMD Class II system (`VIS-C-01`,
`VIS-C-02`). Read access to already-fetched data remains available (service-worker cache, §10)
specifically so the RRT mobile flow (§5.16) degrades gracefully rather than blanking, but no
mutation is queued for later replay.

---

## 10. PWA + web-push for RRT

- **Scope:** the RRT surface (`app/(shell)/rrt/`) is the PWA entry point — installable, with a web
  app manifest carrying the actual IntensiCare v2 name/icons/colors (the legacy manifest still said
  "teleUTI" with disconnected black/white colors, `DES-2-09` — not repeated).
- **Web Push:** critical-score notifications (`US-08`, `PER-C-06`, <5s target) are delivered via the
  Web Push API + a service worker, backed by the same realtime-channel event that feeds
  `NotificationCenter` (§5.6/§2) — one event, two delivery surfaces (in-app + OS-level push), never
  two independently-triggered paths that could disagree.
- **Service worker scope:** precaches the app shell and the RRT mobile route (§8's RRT-render
  budget); caches **read** API responses for the degraded-mode reading experience (§9); explicitly
  does **not** implement a background-sync write queue (§9's no-offline-writes decision).
- **Notification payload:** carries enough to render `RRTMobileCard` (§5.16) without a network
  round-trip on tap — bed/patient identifier, triggering score + band, location — satisfying US-27's
  "reachable in one tap" and "usable one-handed while moving" acceptance criteria even on a marginal
  connection.
- **Platform note:** this is a responsive PWA, explicitly not a native iOS/Android app
  (`product-spec.md` §4 WON'T, confirmed at `US-27` AC3) — Web Push (not APNs/FCM native push) is the
  correct mechanism for this scope, with the understanding that iOS Safari's web-push support
  constraints (PWA must be installed to home screen for push to work reliably) are an operational
  onboarding requirement for RRT staff, not a frontend architecture gap. **[flagged — RRT device
  provisioning/onboarding is outside this document's scope; note for the delivery/rollout plan.]**

---

## 11. Traceability

| Constraint / story | Where addressed |
|---|---|
| `ADR-C-01` / `CON-0050` (tenant color resolved once, server-side) | §0, §1 rule 4 |
| `ADR-C-02` / `CON-0051` (every `var(--x)` resolves, CI-enforced) | §0, §4 |
| `ADR-C-04` (contrast check both themes on neumorphic surfaces) | §6 visual-regression matrix |
| `ADR-C-05` / `CON-0050` (deny-by-default route guard, server-side gate) | §1 rule 4, §0 |
| `ADR-C-06` (no second impl of a registered primitive) | §1 rule 2/3, §5.11/5.12/5.14 |
| `ADR-C-07` / `CON-0052` (breakpoint function covers full domain) | §4, §5.1 |
| `ADR-C-09` (fix both severity bugs, don't port) | §5.5, §5.11 |
| `ADR-C-10` / `CON-0043` (typed form-config schema) | §0, §5.8, `form-engine-stack.md` |
| `ADR-C-11` / `CON-0044` (backend-shape-agnostic error classification) | §3 |
| `ADR-C-12`/`ADR-C-13` / `CON-0045`/`CON-0046` (realtime not a 2nd source of truth; same channel) | §2 |
| `ADR-C-15` / `CON-0048` (privacy toggle must gate the feed, not mask it) | Noted as out of this component set (camera player is `auth-security-architect`'s owned surface, `CON-0048` owner) — flagged so the camera component, when built, imports `lib/realtime`'s connection-gating pattern rather than a CSS blur-only toggle. |
| `DES-C-01`/`CON-0049` (severity/brand decoupling) | §0, §1 rule 3, §4 |
| `DES-C-05`/`CON-0053` (no polling for bed board) | §2, §3 |
| `DES-C-06`/`CON-0054` (threshold-based abnormal-value flagging) | §5.3, §5.2 |
| `PER-C-01` (score <30s) | §8 (frontend contribution budget) |
| `PER-C-04`/`CON-0090` (alert shows exact parameter) | §5.5 |
| `PER-C-05`/`CON-0091` (1-click ack) | §5.5 |
| `PER-C-06`/`CON-0092` (mobile notif <5s) | §10, §8 |
| `PER-C-07`/`CON-0093` (<1min outcome doc) | §5.16 |
| `US-06`/MOT-01 | §5.1, §5.7 |
| `US-10`/MOT-02 | §5.4 |
| `US-21` | §5.5 |
| `US-27`/`US-28` | §5.16, §10 |
| `US-29`/`US-30`/`PER-C-08` | §5.17 |

## 12. Open items for ratification (not decided in this document)

1. Whether re-derived `clinical.*` severity hex values may differ from the legacy's "red bed = crisis"
   muscle-memory palette — needs clinical sign-off (`design-adrs.json` open_questions, `ADR-0013`).
   `BedGrid`/`ScoreBadge`/`AlertCard` are all built to consume the token, so this is purely a
   token-value question, not a component-architecture one.
2. Reference-range source and severity-band count (3-tier vs. 4-tier) for `ReferenceRangeFlag` —
   pending clinical ratification (`design-inventory.json` open_questions, `ADR-0014`).
3. Neumorphic dual-shadow elevation's actual paint cost at the 90-bed/60fps budget (§8) is
   unbenchmarked; the flat-shadow fallback path exists but a go/no-go on dual-shadow-as-default at
   this density needs a load-test pass before ship.
4. Whether Chromatic (SaaS) or a self-hosted visual-regression runner is used (§6) — a hosting/vendor
   decision, not an architecture one.
5. iOS web-push onboarding friction for RRT staff (§10) — a delivery/rollout concern, flagged for the
   `delivery` track.
