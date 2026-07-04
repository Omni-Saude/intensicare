# Design Language — IntensiCare v2

**Owner:** design-token-systems-designer · **Status:** draft for reconciliation barrier **C2** · **Authority precedence:** vision ≻ directive ≻ audit (CONTRACTS §5), per `docs/plan/_work/dispositions/design-adrs.yaml`.

This document states the design *principles* that govern IntensiCare's visual system and the reasoning behind them. It answers "what do we believe and why"; the companion `design-tokens.md` answers "what are the exact values and how are they built and enforced." Every principle below traces to an audit fact (`DES-*`), an audit ADR (`ADR-000n-*`), a vision fact (`VIS-*`), or a ledger constraint (`CON-*`). Nothing here is invented aesthetic preference disconnected from the audit — where a legacy pattern is validated, it is kept; where a legacy pattern is a defect, it is named as such and not repeated.

---

## 1. Why this document exists

The legacy `trilhas-frontend` (audited: 463 .ts/.tsx, 153 .less, 117 component dirs, commit `f9656be`) is the largest source of both *validated product intuition* and *unaddressed patient-safety risk* IntensiCare v2 inherits. The audit (`design-inventory` brief, `docs/design/design-system-inventory.md`) and its 18 ADRs (`docs/adr/0001`–`0018`) draw a hard line between what to **preserve** (`DES-8-01`) and what to **replace** (`DES-8-02`). This design language operationalizes that line as principle, so every downstream screen/component/token decision inherits it automatically instead of re-litigating it per surface.

---

## 2. Core principles

### 2.1 Dark-first "quiet ICU," with a genuinely symmetric light theme

**Principle:** The default experience is dark and low-glare — a "quiet ICU" that does not compete for attention with the clinical environment (dimmed rooms, monitor glow, night shifts) — but light mode is a **first-class, structurally identical sibling**, not an afterthought bolted on top.

**Why:** The legacy system got half of this right and half of it wrong. `ADR-0002` validates the dark+compact default as sound (glare-reduction rationale, inferred but never falsified) and this design language **adopts it verbatim** (`design-adrs.yaml` disposition: ADOPT). But the legacy light mode (`ADR-0003`) was built as a *client-side overlay on top of* the dark bundle: a cookie-gated preference, a full `window.location.reload()` to switch (discarding in-flight form state, open drawers, scroll position), a dynamically-imported `LightTheme.less` that re-imports stock AntD light CSS over the dark cascade, ~30 hand-written patch rules, and 23/153 `.less` files hand-rolling `&.light{}` blocks (one drifting to the inconsistent `&.is-light`). This was rated **the single most fragile legacy mechanism** and audit explicitly says it "must not be carried forward" (`ADR-0003`, `DES-C-02`).

**What this means downstream:** dark and light are two token *resolutions* of the same semantic surface graph, switched live via a `data-theme` attribute / CSS custom properties (no reload, no second CSS bundle to compile, no drift-prone per-component patch files). A component author never writes `.light{}`; they consume `semantic.surface.canvas`, and the token resolves differently per theme automatically. See `design-tokens.md#theme-modes` for the mechanism.

**Symmetry is a design requirement, not just an implementation detail.** The legacy's worst *visual* defect under this principle was the neumorphic elevation asymmetry — `ItemDefault`'s dark dual-shadow (`5px 5px 10px #0b0b0b, -5px -5px 10px #1d1d1d`) collapsed to a **flat** single shadow in light mode (`0px 0px 10px #d1d1d1`), while `ItemNotificacao` kept the dual-shadow in both themes (`DES-2-07`, `ADR-0007`). Symmetric means: whatever visual language a surface carries in dark mode, it carries the *token-equivalent* language in light mode — same elevation grammar (dual embossed shadow, never a degraded flat one), same severity encoding, same density behavior. Two visually distinct, but structurally identical, sibling themes.

### 2.2 Two color systems, permanently decoupled

**Principle:** Brand chrome (tenant-customizable) and clinical severity (immutable, safety-critical) are two structurally separate token trees. Nothing may make them interact.

**Why:** This is the audit's own top-flagged risk: "conflating them is the top-flagged risk for reintroducing a patient-safety bug" (`DES-0-02`). The legacy got the *concept* right — `statusTrilha` (severity) and `--primary-color` (brand) were independently sourced and never coupled in code (`DES-2-03`) — but the governance around that separation was informal (an `any`-typed object, not a typed contract). `ADR-0013` promotes this to a first-class rule: `clinical.*` tokens must remain "structurally separate from `brand.*` tokens... tenant rebranding MUST NOT alter what a clinical severity color means" (`ADR-C-08`, ledger `CON-0041`/`CON-0049`).

**What this means downstream:** a tenant admin can pick any brand hex without a code change ever touching what "critical" looks like, and no future refactor can accidentally make `clinical.severity.critical` derive from, blend with, or fall back to `brand.primary`. This is enforced structurally in the token source (`design-tokens.md#governance`), not just by convention.

### 2.3 Per-tenant single brand token, resolved before first paint

**Principle:** Tenant branding is exactly one deterministic color token, resolved once — server-side or before hydration — with no client-side re-application step, ever.

**Why:** The legacy's only per-tenant customization surface was a single hex (`cor_primaria`), and it was applied via a genuinely bad pattern: `changeColorTheme()` triggered *both* a `dynamic-antd-theme` runtime Less recompile *and* a `--primary-color`/`--primary-shadow-color` CSS-variable set, applied **twice per page load** — `_app.tsx` hardcodes the default orange (`#fe6d01`) on mount, then `PageContainer` overwrites it later once the real tenant color loads. The result is a visible flash-of-wrong-color on every session (`DES-1-02`, `ADR-0004`). `ADR-C-01` names the fix directly: the tenant token "MUST be resolved once, server-side or before first paint, with no client-side re-application step."

**What this means downstream:** there is exactly one `brand.primary` token per tenant, resolved at the layer that renders the first byte (SSR / edge), never mutated by a second client pass. No runtime Less/CSS recompilation library. See `design-tokens.md#tenant-branding` for the resolution pipeline and the contrast-guard this design language adds (the legacy had *no* validation that an arbitrary tenant hex stayed accessible against surface/text — that gap is closed here, not ported forward).

### 2.4 Severity is never color alone — color + icon + shape, always

**Principle:** Every clinical severity signal is triple-encoded: a color, an icon, and a shape (or silhouette/border treatment). No surface may communicate severity through color as the sole channel.

**Why:** This is a direct, non-negotiable mandate from the reconciliation ledger: "Severity mapping duty: one canonical `clinical.*` scale normal/watch/urgent/critical with explicit documented mappings... Severity always encoded color + icon + shape" (`CON-SEED-11`). It is also a WCAG 1.4.1 (Use of Color) requirement, and a direct fix for two live legacy bugs the audit found: (a) `DisplayNotificaoes` hardcodes the toast icon color to amber (`#FFAB00`) **regardless of the alert's actual severity** — a severity-blind notification, and (b) `TabRecomendacoes` colors its criteria panel by the literal string `'VERMELHO'` at every severity instead of each criterion's own alert value (`ADR-0013`, ledger `CON-0042`). Both are must-fix, not must-port (`ADR-C-09`).

**What this means downstream:** the `alert-engine-architect`'s severity model (`docs/plan/_work/platform/severity-model.yaml`, co-owned with this role) already proposes the icon/shape slot per band — this design language ratifies it and design-tokens.md assigns the exact color values:

| Band | Color family | Icon | Shape |
|---|---|---|---|
| normal | green | check-circle | circle |
| watch | amber | eye | rounded-square |
| urgent | orange | exclamation | triangle |
| critical | red | alert-octagon | octagon |

A component that renders severity by color swatch only (no icon slot, no shape) is a defect by this principle, full stop — it must fail review the same way an unresolved `var(--x)` fails CI (§2.6).

### 2.5 Governed neumorphic elevation, contrast-verified

**Principle:** The soft-UI dual-shadow ("neumorphic") elevation signature is preserved as a **brand identity asset**, but only inside a governed, symmetric, contrast-checked token scale — never as an ungoverned per-component `box-shadow` literal.

**Why:** Audit flags the neumorphic look as a validated, distinctive signature "worth a formal elevation-token pair" (`DES-2-07`) and explicitly lists it under PRESERVE (`DES-8-01`, `ADR-0007`). But the legacy execution was ungoverned: 23 `box-shadow` declarations, two unrelated visual languages (flat vs. dual-shadow) with zero shared token, and the light-mode asymmetry described in §2.1. `ADR-C-04` sets the non-negotiable guardrail: "Any surface carrying clinical text/status content over a neumorphic/embossed background MUST pass an explicit WCAG contrast check in both light and dark themes before shipping."

**What this means downstream:** elevation ships as `elevation.{sm,md,lg}` × `{dark,light}`, each a governed dual-shadow pair (see `design-tokens.md#elevation`), and every `clinical.*` text/icon token is contrast-verified specifically against the **embossed panel fill** color (`surface.raised`), not just the flat canvas — because that is the surface clinical content actually sits on. A `prefers-contrast: more` fallback collapses the embossed pair to a flat, higher-contrast treatment (ADR-0007's own recommendation). Paint cost on the bed-board grid (many simultaneous embossed tiles) is a named open risk (`ADR-0007` notes: "soft-UI shadows costly at scale — must benchmark") and is governed by a density rule in `design-tokens.md#elevation-budget`, not left to per-screen discretion.

### 2.6 Formal scales over literals — and a hard governance floor

**Principle:** Spacing, radius, z-index, motion, and type are each a bounded, named, source-of-truth scale. No raw pixel/rem literal, and no undeclared CSS custom property, may ship.

**Why:** The single largest quantified defect in the audit is the literal-to-token ratio: ~340 raw color/spacing/shadow/z-index literals against 15 declared tokens (`DES-2-04`, `ADR-0006`), of which 5 of the 15 had **zero consumers** and one — `--warning-color` — was read by `Display.tsx` and **never set anywhere**, silently no-opping the one abnormal-value affordance the legacy had (`ADR-0005`, ledger `CON-0035`). `ADR-C-02` states the fix as an invariant: "Every `var(--x)` referenced in source MUST resolve to a generated token definition; CI/lint MUST fail the build otherwise." A second concrete defect this principle forbids repeating: the legacy root font-size cascade was **non-monotonic** across breakpoints (93.75% ≤1590px, 85.5% ≤1480px, 100% ≤1260px — cascade order makes the 100% rule win below 1260px, so the 85.5% shrink only silently applies in the 1261–1480px band) (`DES-2-05`, `ADR-C-03`).

**What this means downstream:** one JSON token source, compiled via Style Dictionary, generates every platform output (CSS custom properties, TS types); a CI lint resolves every `var(--x)` reference in the codebase against that generated set and fails the build on any miss (closing the exact `--warning-color` defect class, not just that one instance). The type scale's responsive root size is defined as a strictly monotonic step function of the breakpoint token set (§2.7) — never decreasing as viewport grows. Full values in `design-tokens.md#formal-scales`.

### 2.7 Density adapts via container queries against one breakpoint token set

**Principle:** There is exactly one named breakpoint set (phone / workstation / monitor-wall), shared verbatim between JS and CSS, and density adaptation is driven by **container queries against a container's own width**, not `window.innerWidth` listeners scattered across components.

**Why:** The legacy responsive strategy was three uncoordinated mechanisms sharing no single source: a dominant `useWindowSize()` + `collapseRule`(1260px)/`collapseRuleMobile`(800px) pattern across 49 files; a rare forked-tree pattern (`GridView`/`MobileView`); and an ad-hoc bucket if-chain in `ListOcupacoes` with a **confirmed live bug** — the band (2400px, 2800px] falls through every branch, leaving `span` `undefined` and rendering full-width cards on large monitors — plus a second, independently-drifted bucket set in `ListDashboard` covering different breakpoints for the same visual decision (`DES-4-04`/`DES-4-05`, `ADR-0011`). `ADR-C-07` forbids the dead band recurring: "the shared responsive density/column-span function MUST cover the full viewport-width domain with no gaps."

**What this means downstream: this is the exact mission mandate** — "density adapts via container queries against one breakpoint token set (ADR-0011)" — carried as ADAPT in the reconciliation ledger (`design-adrs.yaml`). Column/row density per density mode is a **continuous formula over container width**, not a bucketed if-chain, so there is no width value that falls through undefined. Full breakpoint values and the density formula are in `design-tokens.md#density-modes`.

### 2.8 Accessibility floor: WCAG 2.2 AA everywhere, AAA where a life-safety decision rides on it

**Principle:** Every token pairing that carries clinical text, icon, or status meaning meets WCAG 2.2 Level AA (4.5:1 normal text / 3:1 large text and non-text UI components) at minimum. The `critical` severity band — the band whose response SLA is under 5 minutes and whose alert can never be rate-limited (`docs/plan/_work/platform/severity-model.yaml`) — meets **AAA (7:1)** for its text/icon token in both themes.

**Why:** This is the ledger's explicit contrast mandate (`CON-0037`/`ADR-C-04`) applied at the color-value level, and it directly closes two legacy defects: the near-miss occupancy-gauge amber (`#FFAB00`) silently diverging from `statusTrilha.AMARELO` (`#ffd900`) with no contrast rationale for either (`DES-5-03`), and the complete absence of any documented contrast check anywhere in the legacy token set. WCAG 2.2 additionally introduces Success Criterion 2.5.8 (Target Size, Minimum) — relevant because acknowledgment controls for `urgent`/`critical` alerts are exactly the kind of small, high-stakes control this SC protects; this design language sets the interactive target-size floor at 24×24 CSS px (AA) with a 44×44 recommendation for primary alert-acknowledgment actions given gloved-hand, high-stress ICU use.

**What this means downstream:** every hex value in `design-tokens.md#clinical-severity` ships with its computed contrast ratio against both `surface.canvas` and `surface.raised`, in both themes, so the ratio is auditable rather than asserted. No brand or clinical token is added to the source without this check attached.

---

## 3. Preserve vs. replace — the governing table

This is the audit's own PRESERVE/REPLACE split (`DES-8-01`/`DES-8-02`), restated as the design language's operating contract. Anything not on the PRESERVE side is being actively redesigned, not incrementally patched.

| Preserve (validated IP — evolve, don't discard) | Replace (defect or dead-end — do not port) |
|---|---|
| Dark-first, compact-by-default aesthetic as an explicit, documented decision (§2.1) | 5-layer theming stack; full-page-reload light-mode toggle; runtime AntD Less recompilation (§2.1) |
| Two-tier color separation — immutable clinical severity vs. tenant-overridable brand — now made structurally enforced, not just conventional (§2.2) | Informal, `any`-typed severity object with zero compile-time contract (§2.2, §2.6) |
| Neumorphic dual-shadow elevation as a brand signature (§2.5) | Ungoverned per-component shadow literals; light-mode flat-shadow asymmetry (§2.5) |
| Per-tenant single-hex white-label **capability** (§2.3) | Double-apply flash-of-default-color mechanism; no contrast guard on the tenant hex (§2.3) |
| Config/schema-driven clinical form engine (`FormDadosProntuario`) — the audit's own "strongest reusable IP" call (`DES-3-03`, `ADR-0015`) — owned jointly with the form-engine spec, referenced here only for token/visual consistency | `as any`-typed form configs; three uncoordinated conditional-field mechanisms |
| Canonical primitives with real adoption: `DrawerBuilder` (16 sites), `AlertDelete`, `Ball` status-dot, `MaterialIcon` (`DES-3-02`, `ADR-0012`) | A second, competing implementation of any registered primitive (breadcrumb, tabs, count badge) — CI-blocked per `ADR-C-06` |
| Firestore-out-of-record principle — realtime signaling/presence only, never system-of-record (`DES-6-02`, `ADR-0017`) | REST-polling the mission-critical bed board; three independent realtime channels with no shared reconnect/backoff |
| "Red bed = crisis" clinician muscle memory as a *hue-family* starting point for the critical band (flagged open question, `ADR-0013`) | The exact legacy hex values where they fail the AA/AAA contrast floor (§2.8) — see `design-tokens.md#migration-map` for the literal-by-literal disposition |

---

## 4. Open decisions routed to reconciliation barriers

Per the zero-silent-resolution rule this program operates under, the following are recorded as **open**, not resolved here:

- **Exact critical-band hue vs. legacy muscle memory** — `ADR-0013`'s own open question: "whether re-derived severity hex may differ from legacy... needs clinical sign-off." `design-tokens.md#clinical-severity` proposes hue-family-preserving, contrast-corrected values and flags this for clinical sign-off at barrier C2.
- **ASSISTIDO, the legacy's 5th severity-adjacent state** — the legacy `statusTrilha` had a 5th state, `ASSISTIDO`, that *overrides* the raw alert color whenever `assistido===true` (`DES-2-03`). The canonical `clinical.*` scale this platform ships (`normal/watch/urgent/critical`, per `docs/plan/_work/platform/severity-model.yaml`) has no override slot, deliberately: an override that visually *replaces* a true severity color risks masking a critical alert behind a "someone is on it" blue, which is the opposite of the "severity is immutable, never suppressed for critical" principle this document holds. This design language's disposition: **do not port ASSISTIDO as a severity override**; model "being attended" as a separate, additive `clinical.status.attended` badge that composites *alongside* — never in place of — the true severity color+icon+shape. Routed for clinical/product sign-off alongside the severity band count itself.
- **Elevation paint-cost budget on the bed-board grid** — `ADR-0007`'s own unresolved note; `design-tokens.md#elevation-budget` proposes a density-tiered mitigation (fewer/simpler shadow tiers at `monitor-wall` density where many tiles render simultaneously) pending a real benchmark.
- **Final breakpoint pixel values** — proposed in `design-tokens.md#density-modes`, pending validation against real ICU workstation and monitor-wall hardware (`ADR-0011` open question).

---

## 5. Cross-references

- `docs/plan/design/design-tokens.md` — the Style Dictionary token spec this language governs.
- `docs/plan/_work/platform/severity-model.yaml` — canonical `clinical.*` severity/lifecycle model (co-owned with alert-engine-architect); this document's §2.4 ratifies its color+icon+shape mandate.
- `docs/plan/_work/dispositions/design-adrs.yaml` — per-ADR disposition (ADOPT/ADAPT/SUPERSEDE) this language implements.
- `docs/plan/_work/briefs/design-inventory.json`, `docs/plan/_work/briefs/design-adrs.json` — source audit facts and constraints cited throughout (`DES-*`, `ADR-000n-*`).
- `docs/plan/_work/constraints/ledger.yaml` — `CON-*` entries owned by this role (`CON-SEED-11`, `CON-0034`–`CON-0051` range).
