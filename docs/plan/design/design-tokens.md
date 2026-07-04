# Design Tokens — IntensiCare v2 (Style Dictionary spec)

**Owner:** design-token-systems-designer (severity band co-owned with alert-engine-architect) · **Status:** draft for reconciliation barrier **C2** · **Authority precedence:** vision ≻ directive ≻ audit (CONTRACTS §5).

This is the executable-shape companion to `docs/plan/design/design-language.md`: exact values, file layout, build pipeline, and the literal-by-literal migration disposition from the legacy 15-variable token set. Every value that carries clinical meaning ships with its computed WCAG contrast ratio (not asserted — computed against real relative-luminance math, reproducible by anyone with the hex pair). Every principle citation (`§2.n`) refers to `design-language.md`.

---

## 1. Governance & source of truth

**One JSON source, compiled by Style Dictionary, generating every platform output.** This closes the legacy's dead-copy defect: `variables.less` (15 vars) was duplicated verbatim into `next.config.js` and `variables.less` itself was **never `@import`-ed** — a dead file masquerading as the source of truth (`ADR-0005`, `DES-2-01`).

```
tokens/
  primitives/
    color-ramps.json       # raw hue/lightness ramps — NEVER consumed directly by components
    spacing.json
    radius.json
    z-index.json
    motion.json
    type.json
    elevation.json
    breakpoints.json
  brand/
    brand.schema.json       # shape a tenant record must satisfy; validated at ingest
    brand.default.json      # platform fallback tenant (no customer logged in / login screen)
  clinical/
    severity.json           # normal|watch|urgent|critical — see §6
    status.json             # non-severity clinical status badges (e.g. `attended`) — see §6.5
  semantic/
    surface.json            # canvas/raised/overlay per theme
    text.json
    action.json             # buttons/links — sources from brand.*
    feedback.json           # non-clinical success/warning/error/info (form validation, save toasts)
    alert.json              # sources from clinical.severity.*
  $themes.json               # dark | light theme resolution map
config/
  style-dictionary.config.js
build/                        # generated — CSS custom properties, TS types, JSON for backend email/PDF templating
```

**Three consumable layers** (the primitives layer is a fourth, internal-only layer components never import from directly):

1. **`brand.*`** — tenant-resolved, single hex + Style-Dictionary-computed tint/shade/contrast-pair. One tenant, one token, resolved before first paint (`§2.3`).
2. **`clinical.*`** — severity + status. Immutable, structurally forbidden from referencing `brand.*` (`§2.2`). Typed, not `as any` (closing `DES-2-03`/`ADR-0013`'s "typed as any, never in the token file" defect).
3. **`semantic.*`** — the only layer components import from. `semantic.action.primary` aliases `brand.primary`; `semantic.alert.critical.*` aliases `clinical.severity.critical.*`; `semantic.surface.canvas` resolves per active theme. This indirection is what makes theme-switching and rebranding a token-resolution swap, never a component code change.

**Enforcement (closes `ADR-C-02`/`CON-0035`, the `--warning-color` permanently-unset defect class):**

- `scripts/check_tokens.py` (sibling to the existing `scripts/check_units.py` unit-registry gate) parses every `var(--...)` reference across `src/**/*.{css,ts,tsx}` and asserts it resolves to a name emitted by the Style Dictionary build. A miss is a **build-time failure**, not a runtime no-op. Same `draft`/`strict` mode convention as `check_units.py` (warn in draft, CI-fail in strict).
- Every token file entry requires a `$description` and a `source_ref` field pointing at either this doc, an `ADR-*`/`DES-*` audit fact, or a ledger `CON-*` id — no token may exist with an untraceable rationale.
- No literal hex/px/ms value is permitted outside `tokens/primitives/*`. A primitive may only be referenced by a `brand.*`, `clinical.*`, or `semantic.*` alias — never by a component.
- CI blocks a second definition of any registered `semantic.*` name (mirrors `ADR-C-06`'s primitive-duplication rule, applied to tokens).

---

## 2. Theme modes (§2.1)

Two runtime-switchable resolutions of one semantic graph, toggled via `<html data-theme="dark|light">`, no bundle swap, no reload:

```json
// tokens/$themes.json
{
  "dark":  { "selector": "[data-theme='dark']",  "default": true },
  "light": { "selector": "[data-theme='light']" }
}
```

`semantic.surface.canvas` (and every other semantic token) is defined once per theme in the Style Dictionary source; the build emits both resolutions as scoped CSS custom properties under each theme's selector. A user's stored preference sets the attribute server-side on the initial HTML response (no client JS required to render the correct theme on first paint) — the same "resolve before first paint" discipline as tenant branding (§4).

| Surface token | Dark value | Light value |
|---|---|---|
| `semantic.surface.canvas` | `#0E1014` | `#F5F6F8` |
| `semantic.surface.raised` | `#171A21` | `#FFFFFF` |
| `semantic.surface.overlay` | `#1F232C` | `#FFFFFF` (+ `elevation.lg` shadow, no separate fill) |
| `semantic.text.primary` | `#E9ECF1` | `#1A1D24` |
| `semantic.text.secondary` | `#A6ADBB` | `#565D6D` |
| `semantic.border.default` | `rgba(255,255,255,0.08)` | `rgba(20,22,28,0.10)` |

`semantic.text.primary` on `semantic.surface.canvas`: dark 15.8:1, light 15.6:1 (both AAA). Both themes carry the identical elevation grammar — dual embossed shadow, never a flat degrade (§4, `ADR-C-04`).

---

## 3. Formal scales (§2.6)

### 3.1 Spacing

8px base rhythm with a 4px half-step, replacing the legacy's *implicit, uncodified* 4/8-multiple bias (`DES-2-06`: `padding: 8px` ×11, `margin-top: 0.5rem` ×13, never named).

| Token | Value | Legacy disposition |
|---|---|---|
| `spacing.0` | 0px | new |
| `spacing.1` | 4px | formalizes the ad-hoc half-step |
| `spacing.2` | 8px | formalizes the dominant literal |
| `spacing.3` | 12px | new |
| `spacing.4` | 16px | formalizes `1rem` literal |
| `spacing.5` | 20px | new |
| `spacing.6` | 24px | new |
| `spacing.8` | 32px | new |
| `spacing.10` | 40px | new |
| `spacing.12` | 48px | new |
| `spacing.16` | 64px | new |
| `spacing.20` | 80px | new |
| `spacing.24` | 96px | new |

Unit is **px only** at the token-definition layer (components consume via `rem`-emitting CSS var so user font-size zoom still works) — this bans the legacy's px/rem duplicate-literal drift (`8px`≡`0.5rem`, `10px`≡`0.625rem`, `12px`≡`0.75rem`, `DES-2-06`) at the source.

### 3.2 Radius

Legacy had 13 literals collapsing into 3 real clusters plus circular (`DES-2-06`); formalized as exactly those 3 clusters, single-unit:

| Token | Value | Use | Legacy literals absorbed |
|---|---|---|---|
| `radius.sm` | 8px | inputs, buttons, chips | `8px`, `0.5rem`, `6px`, `10px` |
| `radius.md` | 16px | cards, drawers, panels | `16px`, `0.625rem`, `0.75rem`, `1rem` |
| `radius.full` | 9999px | avatars, status dots, pills | `50%` ×17 |

### 3.3 Z-index

Legacy: 11 undocumented literals (`1`×10, `99999`×2 full-screen overlay, `1031`×2 nprogress, `9999`, `999`) with no scale (`DES-2-07`). Named scale, one axis:

| Token | Value | Purpose |
|---|---|---|
| `z.base` | 0 | default stacking context |
| `z.raised` | 10 | cards/tiles with elevation |
| `z.sticky` | 100 | sticky headers, breadcrumb bar |
| `z.dropdown` | 200 | select/menu popovers |
| `z.overlay` | 300 | drawer/modal scrim + panel (managed overlay stack, `ADR-0010`) |
| `z.toast` | 400 | non-blocking toasts/snackbars |
| `z.modal` | 500 | blocking modals (error, confirm) |
| `z.page-loader` | 600 | full-page progress indicator (replaces the legacy nprogress 1031 literal) |
| `z.critical-alert` | 9000 | interruptive critical-severity alert surface — always above every other layer, including modals, by design (`clinical.severity.critical` is never suppressed, `docs/plan/_work/platform/severity-model.yaml`) |

The overlay-stack manager (`ADR-0010`) increments within `z.overlay`'s band per nesting depth rather than each drawer hand-picking a literal — closing the "no shared stack manager" gap the audit found in the 4-deep `ListOcupacoes` drawer nest (`DES-4-04`).

### 3.4 Motion

Legacy: no tokens, ad-hoc durations `0.2s`–`1s`, two named keyframes (`slide-in/out-top` 0.25s, `fadeIn` 0.5s) (`DES-2-07`).

| Token | Value | Use |
|---|---|---|
| `motion.duration.instant` | 0ms | `prefers-reduced-motion` fallback for every duration below |
| `motion.duration.fast` | 120ms | micro-interactions (hover, focus ring) |
| `motion.duration.base` | 200ms | default transitions (drawer slide, tab switch) |
| `motion.duration.slow` | 320ms | panel expand/collapse |
| `motion.duration.deliberate` | 480ms | full-screen transitions |
| `motion.easing.standard` | `cubic-bezier(0.2, 0, 0, 1)` | default |
| `motion.easing.decelerate` | `cubic-bezier(0, 0, 0, 1)` | entrances |
| `motion.easing.accelerate` | `cubic-bezier(0.3, 0, 1, 1)` | exits |

**Motion never carries severity meaning alone** (`§2.4` extends to motion, not just color): a `critical`-band pulse animation is a *reinforcing* channel on top of color+icon+shape, and every such animation has a static, equally-legible `prefers-reduced-motion` fallback — never a state that exists only while animating.

### 3.5 Typography

Legacy: Poppins loaded twice (Google Fonts + one dead malformed `@font-face`), zero monospace anywhere, a **non-monotonic root font-size cascade** (93.75% ≤1590px / 85.5% ≤1480px / 100% ≤1260px — CSS cascade order makes 100% win below 1260px, so the 85.5% shrink only silently applies in the 1261–1480px band), 20+ unscaled font-size literals, only 4 weight literals despite loading 3 weights (`DES-2-05`, `ADR-0006`).

**Fix, don't port, the cascade bug (`ADR-C-03`/`CON-0036`):** root size is a strictly monotonic non-decreasing step function of the breakpoint token set (§5):

| Breakpoint | Root font-size |
|---|---|
| `phone` (< 768px) | 100% (16px) |
| `workstation` (768–1919px) | 100% (16px) |
| `monitor-wall` (≥ 1920px) | 106.25% (17px) — bed-board legibility at viewing distance |

A bounded modular scale (ratio 1.125, base 16px), single unit (`rem`), replacing the 20+ literal ramp:

| Token | Size | Weight tokens available |
|---|---|---|
| `type.size.xs` | 0.75rem (12px) | 400, 500, 600 |
| `type.size.sm` | 0.875rem (14px) | 400, 500, 600 |
| `type.size.base` | 1rem (16px) | 400, 500, 600 |
| `type.size.md` | 1.125rem (18px) | 400, 500, 600 |
| `type.size.lg` | 1.25rem (20px) | 500, 600 |
| `type.size.xl` | 1.5rem (24px) | 600 |
| `type.size.2xl` | 1.875rem (30px) | 600 |
| `type.size.3xl` | 2.25rem (36px) | 600 |

`type.family.sans` = brand display/UI face (Poppins retained pending a typography-specific brief; this spec fixes only the load defect: one `@font-face`/one Google Fonts request, the dead malformed declaration retired). **New:** `type.family.mono` — a tabular monospace face (e.g. system `ui-monospace` stack) for vitals/lab numeric values, closing the audit's explicit gap ("no monospace anywhere," `DES-2-05`) and directly supporting scannable abnormal-value comparison (`§2.8`, `design-tokens.md#clinical-severity`).

---

## 4. Elevation (§2.5) — governed neumorphic scale

Three tiers, dual-shadow, symmetric across both themes (fixing the legacy's dark-dual/light-flat asymmetry, `DES-2-07`/`ADR-0007`). Each pair = a shadow (recession, offset toward the assumed light source) + a highlight (relief, offset away from it), both required — a single-shadow "flat" fallback exists only behind `prefers-contrast: more`.

| Token | Dark theme (on `surface.raised` `#171A21`) | Light theme (on `surface.raised` `#FFFFFF`) |
|---|---|---|
| `elevation.sm` | `2px 2px 4px rgba(0,0,0,0.45), -2px -2px 4px rgba(255,255,255,0.03)` | `2px 2px 5px rgba(20,22,28,0.10), -2px -2px 5px rgba(255,255,255,0.9)` |
| `elevation.md` | `4px 4px 8px rgba(0,0,0,0.55), -4px -4px 8px rgba(255,255,255,0.04)` | `4px 4px 10px rgba(20,22,28,0.12), -4px -4px 10px rgba(255,255,255,0.9)` |
| `elevation.lg` | `8px 8px 16px rgba(0,0,0,0.60), -8px -8px 16px rgba(255,255,255,0.05)` | `8px 8px 20px rgba(20,22,28,0.14), -8px -8px 20px rgba(255,255,255,0.9)` |
| `elevation.flat` (high-contrast fallback) | `0 1px 0 rgba(255,255,255,0.10)` inset + `semantic.border.default` outline | `0 1px 2px rgba(20,22,28,0.16)` + `semantic.border.default` outline |

**Contrast is verified against the fill the shadow sits on, not the shadow itself** (`ADR-C-04`): every `clinical.*` and `semantic.text.*` token used on an embossed surface is checked against `semantic.surface.raised`, in addition to `semantic.surface.canvas` — see the ratio columns in §6. A shadow pixel never carries text; this is what makes the contrast check well-defined.

### 4.1 Elevation budget (paint-cost governance, `ADR-0007` open note)

`ADR-0007` flags neumorphic shadows as potentially costly at scale on a dense, many-tile bed-board grid, unbenchmarked. Governing rule pending that benchmark: at `monitor-wall` density (§5, potentially dozens of simultaneously-visible bed tiles), tiles default to `elevation.sm` only; `elevation.md`/`lg` are reserved for singly-focused surfaces (drawers, modals, the one selected/expanded bed tile). This is a density-tiered mitigation, not a removal of the signature — re-benchmark before locking at barrier C3.

---

## 5. Density modes — one breakpoint token set, container queries (§2.7)

**One named breakpoint set**, shared verbatim by CSS `@container` queries and any JS that needs the same boundary (e.g. server-rendered density hints) — replacing the legacy's two independent, drifted systems (`collapseRule`/`collapseRuleMobile` JS constants vs. 33 one-off `@media` widths, `DES-2-08`).

| Token | Range | Density mode |
|---|---|---|
| `breakpoint.phone` | 0 – 767px | `phone` |
| `breakpoint.workstation` | 768 – 1919px | `workstation` |
| `breakpoint.monitor-wall` | ≥ 1920px | `monitor-wall` |

Density mode is resolved by **container query against the bed-grid container's own width** (`container-type: inline-size` on the grid shell), not `window.innerWidth`. This directly retires the three-strategy legacy mess: the dominant 49-file `useWindowSize()`+`collapseRule` pattern, the rare forked-tree pattern (`GridView`/`MobileView`), and the two independently-drifted bucket if-chains in `ListOcupacoes` (5 buckets, dead band `(2400px, 2800px]` → `span=undefined` → full-width bug) and `ListDashboard` (a different 4-bucket set) (`DES-4-04`/`DES-4-05`, `ADR-0011`).

**Column count is a continuous formula over container width, not a bucket if-chain** — this is what makes the `(2400,2800]` dead-band class of bug structurally impossible, per `ADR-C-07`:

```
columns(containerWidthPx) = clamp(4, floor(containerWidthPx / 320), 12)
```

This single function replaces both legacy bucket chains and is defined once, unit-tested across the full width domain (0 → ∞), and consumed by both the bed-board grid and the dashboard tile grid — closing the "two near-identical grids hand-duplicated with drift" finding (`DES-7-02`).

| Density mode | Typical `columns()` result | Row height | Elevation ceiling (§4.1) |
|---|---|---|---|
| `phone` | 4 | compact, single-column detail drill-down | `elevation.sm` |
| `workstation` | 6–8 | standard | `elevation.md` |
| `monitor-wall` | 8–12 | compact, high tile count | `elevation.sm` (§4.1) |

Final pixel boundaries are provisional pending real ICU workstation/monitor-wall hardware validation (`ADR-0011` open question, carried in `design-language.md §4`).

---

## 6. `clinical.*` severity tokens — normal | watch | urgent | critical

Canonical scale per `docs/plan/_work/platform/severity-model.yaml` (co-owned; this section supplies the exact hex values that document deferred to design-tokens). Structurally separate from `brand.*` (§2.2) — no `clinical.severity.*` definition may reference a `brand.*` token, enforced by the token-source lint (§1).

### 6.1 Roles per band

Each band ships **four** roles, not one hex, because "on-surface text" and "solid chip fill with white label" have different, non-interchangeable contrast requirements:

- **`.on-surface-dark` / `.on-surface-light`** — text/icon color used directly on `surface.canvas`/`surface.raised`. This is the role the AA/AAA floor (`§2.8`) applies to directly.
- **`.signal-dark` / `.signal-light`** — the vivid, non-text status-dot / border-glow color (WCAG non-text 3:1 floor against the surface it sits on; deliberately more saturated than `.on-surface` so the dot reads as a "signal," preserving the legacy's vivid `statusTrilha.ballColor` visual intent).
- **`.fill`** — solid chip/badge background, one value shared across both themes (a filled surface carries its own contrast context regardless of page theme), paired with `.on-fill` = white text always.
- **`.wash`** — `.fill` at low alpha (row/card tint background), decorative only, no text ever placed directly on `.wash` without also using `.on-surface-*`.

### 6.2 Values and computed contrast

Contrast ratios below are computed via the WCAG relative-luminance formula against `semantic.surface.canvas` and `semantic.surface.raised` (§2), reproducible from the hex values alone.

| Band | Role | Value | vs. canvas | vs. raised | Floor required | Result |
|---|---|---|---|---|---|---|
| **normal** | `on-surface-dark` | `#2DD269` | 9.55 | 8.73 | AA 4.5 | ✅ AAA |
| | `on-surface-light` | `#1B8141` | 4.56 | 4.93 | AA 4.5 | ✅ AA |
| | `signal-dark` | `#2DD269` | 9.55 | 8.73 | non-text 3.0 | ✅ |
| | `signal-light` | `#23A352` | — | — | non-text 3.0 | ✅ (≥3.0 both surfaces) |
| | `fill` / `on-fill` | `#1D8844` / `#FFFFFF` | — | — | AA 4.5 (white-on-fill) | ✅ 4.51 |
| | `wash` | `#1D8844` @ 12% alpha | decorative | — | n/a | — |
| **watch** | `on-surface-dark` | `#F2B90D` | 10.63 | 9.72 | AA 4.5 | ✅ AAA |
| | `on-surface-light` | `#8D6C07` | 4.54 | 4.91 | AA 4.5 | ✅ AA |
| | `signal-dark` | `#F2B90D` | 10.63 | 9.72 | non-text 3.0 | ✅ |
| | `signal-light` | `#B28809` | — | — | non-text 3.0 | ✅ |
| | `fill` / `on-fill` | `#947108` / `#FFFFFF` | — | — | AA 4.5 | ✅ 4.54 |
| | `wash` | `#947108` @ 12% alpha | decorative | — | n/a | — |
| **urgent** | `on-surface-dark` | `#F96F06` | 6.62 | 6.06 | AA 4.5 | ✅ AA (comfortably) |
| | `on-surface-light` | `#B95305` | 4.51 | 4.88 | AA 4.5 | ✅ AA |
| | `signal-dark` | `#F96F06` | 6.62 | 6.06 | non-text 3.0 | ✅ |
| | `signal-light` | `#E96806` | — | — | non-text 3.0 | ✅ |
| | `fill` / `on-fill` | `#C25705` / `#FFFFFF` | — | — | AA 4.5 | ✅ 4.51 |
| | `wash` | `#C25705` @ 14% alpha | decorative | — | n/a | — |
| **critical** | `on-surface-dark` | `#F5828F` | 7.68 | 7.02 | **AAA 7.0** | ✅ AAA |
| | `on-surface-light` | `#A90E20` | 7.01 | 7.58 | **AAA 7.0** | ✅ AAA |
| | `signal-dark` | `#EC132C` | ≥3.0 | ≥3.0 | non-text 3.0 | ✅ (vivid — preserves legacy `VERMELHO.ballColor #FF1633` hue family) |
| | `signal-light` | `#EC132C` | ≥3.0 | ≥3.0 | non-text 3.0 | ✅ |
| | `fill` / `on-fill` | `#B20E22` / `#FFFFFF` | — | — | **AAA 7.0** (white-on-fill) | ✅ 7.05 |
| | `wash` | `#B20E22` @ 16% alpha | decorative | — | n/a | — |

**Why `critical` gets its own, more saturated `signal` value than a simple palette step:** the legacy `VERMELHO.ballColor` (`#FF1633`) is preserved almost exactly in hue/vividness for the non-text status dot/border-glow (`#EC132C`), honoring the "red bed = crisis" clinical muscle-memory the audit flags as an open question (`ADR-0013`) — while the *text-bearing* roles (`on-surface`, `fill`) use a deliberately different, deeper red tuned purely for the AAA floor, because the legacy's actual ball color fails AA as body text (`#FF1633` white-on-fill computes to 3.88:1 — fails AA 4.5 for text, though it clears the 3:1 non-text floor a dot/border needs). This is the resolution the audit's open question was waiting on: **keep the vivid hue for the non-text signal, do not force that same literal to also carry text** — clinical sign-off on this specific split is still requested at barrier C2 (`design-language.md §4`).

### 6.3 Migration mapping — legacy `statusTrilha` → `clinical.severity`

Restates and hex-completes `docs/plan/_work/platform/severity-model.yaml`'s `legacy_statusTrilha` map (`CON-SEED-11`; `RULE-PIORA-CLINICA-005/010/011`):

| Legacy `statusTrilha` state | Legacy `ballColor` | Legacy `color` | → `clinical.severity` band | Disposition |
|---|---|---|---|---|
| `NEUTRO` | `#00DC50` | `#5BCE85` | `normal` | ADAPT — hue preserved in `.signal-dark`; new AA-checked `.on-surface`/`.fill` roles added (legacy had none) |
| `AMARELO` | `#ffd900` | `#cebc5a` | `watch` | ADAPT — hue preserved; roles added |
| `LARANJA` | `#ff5900` | `#F9A65A` | `urgent` | ADAPT — hue preserved; roles added |
| `VERMELHO` | `#FF1633` | `#C54C5C` | `critical` | ADAPT — hue preserved *only* in `.signal`; `.on-surface`/`.fill` deepened for AAA (§6.2 rationale) |
| `ASSISTIDO` (override, blue `#4FBFE1`/`#00B0FF`) | — | — | **not ported as a severity band** | RETIRE as an override mechanism — see `design-language.md §4`; re-modeled as an additive, non-severity `clinical.status.attended` badge (§6.5) so "being attended" can never visually mask a true `critical` alert (closing a patient-safety risk the legacy's override design carried) |

### 6.4 Migration mapping — existing alert catalog `CRIT/URG/WARN/INFO` → `clinical.severity`

Restates `docs/plan/_work/platform/severity-model.yaml`'s `existing_catalog` map (source: `LEGEND-SEV`, `alert-catalog.md` L13-21; `CAT-C-02..05`):

| Catalog severity | Catalog definition (action SLA) | → `clinical.severity` band | `alert.severity` DB enum (`DM-VOCAB-03`) |
|---|---|---|---|
| `CRIT` | risco iminente de vida, ação < 5 min | `critical` | `critical` |
| `URG` | deterioração significativa, ação < 30 min | `urgent` | `urgent` |
| `WARN` | alteração relevante, ação < 2h | `watch` | `watch` |
| `INFO` | tendência/risco, ação < 6h | `normal` | *(no DB row — see note)* |

**Note on `INFO`→`normal` and the data-model gap:** `docs/data/model.md`'s `alert.severity` enum has only three values (`watch`, `urgent`, `critical` — `DM-VOCAB-03`), no `normal`/`info`. `normal` is therefore the *bed-board/score baseline band* (rendered as an advisory badge, `delivery_tier: 4`, no alert row created) rather than a persisted alert. This is a recorded, not silently resolved, gap: persisting `normal`-band advisories as auditable, PPV-analyzable rows would require adding a delivery-only `info` value to the `alert.severity` enum — routed to barrier C2 for reconciliation with the data-architect (already flagged in `severity-model.yaml`; restated here because it determines whether the `normal` token pair in §6.2 is ever bound to a persisted, auditable record or only to live UI state).

### 6.5 `clinical.status.*` — non-severity status modifiers

A structurally separate token family for status information that is **not** a severity signal and must never share a slot with `clinical.severity.*`:

| Token | Meaning | Encoding | Composes with severity how |
|---|---|---|---|
| `clinical.status.attended` | A clinician is actively engaged with this alert/patient (legacy `ASSISTIDO` concept) | blue `#4C9FE8` dot/badge, `person-check` icon, additive corner badge | **Additive overlay only** — rendered *alongside* the true severity color+icon+shape, never replacing it (§6.3 disposition) |
| `clinical.status.stale` | Underlying data has exceeded its `staleness_max` and the score/severity shown may not reflect current state | gray `#8A8F99` dot, `clock-alert` icon, dashed border modifier | Additive — dims confidence, never silently downgrades a displayed severity |

### 6.6 Semantic feedback tokens — kept out of clinical territory

Legacy AntD semantic color names (`@success-color`, `@info-color`, `@default-color`, `@danger-color`/`@error-color`, `@warning-color`) had **zero call sites by name** — dead tokens (`ADR-0013`: "AntD semantic tokens have ZERO call sites — dead"). Where a genuinely non-clinical feedback need exists (form validation success, a save-confirmation toast, a permission-denied notice), it is served by `semantic.feedback.{success,warning,error,info}` — a separate token family with its own values, deliberately **not** aliased to `clinical.severity.*`, so a form-validation "error" toast can never be visually confused with, or accidentally coupled to, a `critical` patient-safety alert (direct application of `§2.2`).

---

## 7. Brand tokens — tenant resolution (§2.3)

```json
// tokens/brand/brand.schema.json (shape)
{
  "tenant_id": "string",
  "primary_hex": "string (validated #RRGGBB)",
  "resolved_at": "server | edge",     // MUST NOT be 'client'
  "contrast_guard_applied": "boolean"
}
```

**Resolution pipeline (closes `ADR-C-01`/`CON-0034`, the flash-of-default-orange double-apply bug):**

1. Tenant is known from the authenticated session/subdomain before the first byte is streamed.
2. `brand.primary` is looked up once, server-side, and written into the initial HTML response as a `data-brand-primary` attribute / inlined `:root` custom property — never re-applied by a second client-side effect.
3. No `dynamic-antd-theme`-style runtime CSS recompilation exists in this architecture; brand color is a CSS custom property, full stop.

**Contrast guard (new — the legacy had none: "no contrast/validation guard on tenant hex today," `ADR-0004`):** at ingest, `primary_hex` is checked for ≥4.5:1 contrast against both `semantic.surface.canvas` and a computed on-brand text color. If the raw tenant hex fails, Style Dictionary's build step computes `brand.primary-accessible` (lightness-clamped toward the passing band) for use anywhere brand color carries text/icon meaning (buttons, active nav), while the raw `primary_hex` remains available for pure decorative accents (logo wordmark backgrounds, etc.) where contrast doesn't apply. `contrast_guard_applied: true` is stamped on the token record whenever this adjustment fires, so it is auditable per tenant.

Derived roles, all computed by the Style Dictionary transform (never hand-authored per tenant):

| Token | Derivation |
|---|---|
| `brand.primary` | tenant `primary_hex`, or `brand.primary-accessible` if the guard fired |
| `brand.primary.hover` | `primary` lightness −8% |
| `brand.primary.active` | `primary` lightness −14% |
| `brand.primary.tint` | `primary` @ 12% alpha (subtle backgrounds) |
| `brand.primary.on-primary` | computed white/near-black, whichever passes ≥4.5:1 against `primary` |

`brand.default.json` supplies the platform fallback (login screen, no tenant resolved yet) — a neutral blue (`#3D6BFF`) deliberately outside every `clinical.severity` hue family (green/amber/orange/red), so a not-yet-tenant-branded screen can never be mistaken for a severity signal.

---

## 8. Migration map — legacy token-by-token disposition

Full accounting of the legacy's 15 declared Less variables (`DES-2-01`) plus the `statusTrilha`/catalog severity migration already covered in §6.3–6.4. Disposition vocabulary: **PRESERVE** (concept and rough value carried forward), **ADAPT** (concept kept, value/mechanism corrected), **REPLACE** (concept kept, value discarded — new token, no relation to old hex), **RETIRE** (dead; not ported).

| Legacy token | Legacy value | Consumers | Disposition | → New token |
|---|---|---|---|---|
| `@primary-color` | `#fe6d01` | 14 sites (live) | ADAPT | `brand.primary` — now tenant-resolved, contrast-guarded, resolved server-side (§7); `#fe6d01` becomes just one tenant's value, not the platform default |
| `@secondary-color` | `#606060` | live | REPLACE | `semantic.text.secondary` (theme-resolved, §2 — not a single flat gray) |
| `@primary-color-shade` | `darken(@primary-color, 47%)` | 1 use (live) | REPLACE | `brand.primary.active` — computed by the Style Dictionary transform, not a manual `darken()` call at point of use |
| `@background-color` | `#333` | 0 (unwired) | RETIRE | none — dead weight, no successor needed |
| `@success-color` | `#258a10` | 0 (name never referenced) | RETIRE → REPLACE | `semantic.feedback.success` (§6.6) — new value, new non-clinical scope; NOT `clinical.severity.normal` |
| `@info-color` | `#1a3bb7` | 0 | RETIRE → REPLACE | `semantic.feedback.info` (§6.6) |
| `@default-color` | `#bbbbbb` | 0 | RETIRE | none |
| `@danger-color` / `@error-color` | `#ff1633` (alias) | 0 (name unused) | RETIRE → REPLACE | `semantic.feedback.error` (§6.6) — new value; note the legacy hex coincidentally equals `statusTrilha.VERMELHO.ballColor`, but the *name* was never wired to that meaning, so no clinical continuity is actually being broken here |
| `@warning-color` | *(none — declared, never set)* | `var(--warning-color)` read by `Display.tsx`, always resolves empty (**live bug**) | **ADAPT + fix** | This was the legacy's one latent abnormal-value-flagging hook (`Display.tsx` renders a generic clinical field). It is rewired to resolve dynamically to the applicable `clinical.severity.*` band computed by the reference-range service (`ADR-0014`'s abnormal-value flagging capability), closing the dead-variable bug and the flagging gap in the same move — not simply "set it to some static color" |
| `@skeleton-text` | `#eee3` | 0 (dead) | RETIRE | replaced conceptually by a content-shaped skeleton primitive (owned by frontend-architecture, `ADR-0016`) — no direct token successor |
| `@degree` | `120deg` | 0 (dead) | RETIRE | none |
| `@grad-perc` | `-100%` | 0 (dead) | RETIRE | none |
| `@header-opacity` | `0.8` | 0 (dead) | RETIRE | none |
| `@border-width` | `3px` | 0 (dead — real borders use 1/3/4/5px literals elsewhere) | RETIRE → REPLACE | `border.width.default` = 1px, `border.width.emphasis` = 2px (new, minimal 2-step scale; the legacy's unused 3px and its scattered 1/3/4/5px literals are not carried forward as a set) |
| `@collapse-rule` | `1260px` (duplicate of JS `collapseRule` constant) | live, drift-prone | REPLACE | `breakpoint.workstation` lower bound (§5) — single source, no JS/CSS duplicate to drift |
| *(JS)* `collapseRuleMobile` | `800px` | 49 files reference the pair | REPLACE | `breakpoint.phone` upper bound = 767px (§5) — shifted to the conventional 768px device boundary as part of unifying to one unbucketed formula, not preserved at the old 800px literal |
| 23 `box-shadow` literals (2 unrelated languages: flat vs. dual-shadow) | various | live | REPLACE | `elevation.{sm,md,lg}` × `{dark,light}` (§4) |
| 11 z-index literals | `1`×10, `99999`×2, `1031`×2, `9999`, `999` | live | REPLACE | named `z.*` scale (§3.3) |
| `statusTrilha.ts` (5-state × 6-shade hex table) | see §6.3 | 7 components (live) | ADAPT (4 states) / RETIRE (1 state, `ASSISTIDO`) | `clinical.severity.{normal,watch,urgent,critical}` + `clinical.status.attended` (§6.3, §6.5) |
| 6+ divergent severity-hex reinventions (`handleIconByStatus.ts`, `HorarioCheck.tsx` ×2, `ItemProtocoloSepse.tsx`, `DashboardCard.tsx`, `DisplayNotificaoes.tsx`'s hardcoded `#FFAB00`) | various, `DES-5-02` | live, inconsistent | RETIRE all literals | every one of these call sites is required to consume `clinical.severity.*` (or `semantic.feedback.*` if genuinely non-clinical) — no direct successor hex is offered because the point is to remove the literal, not relabel it |

---

## 9. Cross-references

- `docs/plan/design/design-language.md` — principles this spec implements; read first for the "why."
- `docs/plan/_work/platform/severity-model.yaml` — canonical severity/lifecycle model this spec's §6 supplies exact hex values for.
- `docs/plan/_work/scripts/check_units.py` — existing sibling enforcement pattern for `scripts/check_tokens.py` (§1).
- `docs/plan/_work/dispositions/design-adrs.yaml` — per-ADR ADOPT/ADAPT/SUPERSEDE dispositions this spec implements.
- `docs/plan/_work/constraints/ledger.yaml` — `CON-SEED-11`, `CON-0034`–`CON-0051` (owned), and the routed-not-resolved items in `design-language.md §4`.
