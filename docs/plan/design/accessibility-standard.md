# Accessibility Standard — IntensiCare v2

**Owner:** accessibility-auditor · **Status:** draft, binding on every design deliverable ·
**Role:** cross-cutting gate (orchestrator prompt roster item 26: *"WCAG 2.2 AA/AAA standard,
color-blind-safe severity validation, keyboard/focus model for drawer stacks, reduced-motion
policy; gate on every design deliverable"*) · **Authority precedence:** ADR-001 ≻ vision ≻
directive ≻ audit (CONTRACTS §5).

This document is the accessibility contract every `docs/plan/design/**` deliverable — token spec,
component library, and every `screens/<flow>.md` — must satisfy before it can pass Phase D
completeness review. It does not re-litigate visual language (design-token-systems-designer owns
exact hex/shape values at barrier **C2**); it supplies the **pass/fail method**, the **testable
requirements** (`A11Y-REQ-*`), and the **gate checklist** (`A11Y-GATE-*`) those decisions must
clear, plus a validated example palette as evidence for that decision.

Inputs read: `_work/briefs/design-adrs.json` (audit ADRs, esp. 0010 drawer-in-drawer, 0013 severity
color, 0014 abnormal-value flagging), `_work/briefs/design-inventory.json` (legacy token/UX
inventory), `_work/briefs/personas.json`, `_work/constraints/ledger.yaml` (skim), the ratified
`docs/plan/_work/platform/severity-model.yaml` (four-band `clinical.*` scale + delivery tiers,
owner alert-engine-architect), `docs/plan/architecture/alert-engine.md` (lifecycle, aria-relevant
delivery semantics), and `docs/rules/ESCALATIONS.md` (RULE-AUTH-USUARIOS-063, shared-PIN finding —
cited in §7). Conflicts are recorded, never silently resolved.

---

## 1. WCAG 2.2 conformance baseline

**Floor: WCAG 2.2 AA everywhere** (W3C Recommendation, 5 Oct 2023) — the LGPD/CFM/SaMD regulatory
floor already commits IntensiCare to accessible decision-support software; AA is the non-negotiable
minimum for every screen. **Ceiling: WCAG 2.2 AAA for critical clinical values** — any UI element
that surfaces a `clinical.severity.critical` value, a life-critical numeric (e.g. K⁺, lactate, an
alert's triggering vital), or the acknowledge control for a `critical`/`urgent` alert, must clear
the AAA criteria listed below wherever an AAA variant exists. This ceiling is scoped, not global —
it does not require AAA on incidental chrome (breadcrumbs, tenant switcher, admin config forms).

### 1.1 Success criteria this standard operationalizes

| SC | Name | Level | IntensiCare application |
|---|---|---|---|
| 1.4.1 | Use of Color | A | Severity is **never** color-only (§2); color-coded table cells/borders always carry a redundant icon or text cue. |
| 1.4.3 | Contrast (Minimum) | AA | Body/label text ≥ 4.5:1; large text (≥18pt / ≥14pt bold) ≥ 3:1. Baseline for all UI text. |
| 1.4.6 | Contrast (Enhanced) | AAA | ≥ 7:1 normal text / ≥ 4.5:1 large text — **mandatory** for any rendered `critical`-severity numeric or label (§2.2). |
| 1.4.11 | Non-text Contrast | AA | ≥ 3:1 for icons, chart data points, severity borders/glow, focus indicators, form-field borders against adjacent color(s). |
| 1.4.12 | Text Spacing | AA | No loss of content/function when a user overrides line-height ≥1.5×, paragraph spacing ≥2×, letter-spacing ≥0.12×, word-spacing ≥0.16× — verify on dense bed-tile and table layouts. |
| 1.4.13 | Content on Hover or Focus | AA | Any hover/focus popover (e.g. "why this alert fired," score-component breakdown, `Display` tooltips) must be dismissible without moving pointer, hoverable, and persistent until dismissed/invalid. |
| 2.1.1 / 2.1.2 | Keyboard / No Keyboard Trap | A | Every interactive element operable by keyboard alone; overlay stack never traps focus beyond its own level (§3). |
| 2.3.1 | Three Flashes or Below Threshold | A | **Hard ban, not a preference:** no severity indicator, however styled, may flash faster than 3 Hz, with or without `prefers-reduced-motion` (§4). |
| 2.4.3 | Focus Order | A | Tab order follows the visual/reading order inside every overlay level and every clinical form group. |
| 2.4.7 | Focus Visible | AA | A visible focus indicator on every operable control in both themes and both density modes. |
| 2.4.11 | Focus Not Obscured (Minimum) | AA (new 2.2) | The focused element is never fully hidden behind a sticky header/footer, a toast, or a lower overlay level (§3.5). |
| 2.4.13 | Focus Appearance | AAA (new 2.2) | For the **critical-alert acknowledge control** specifically: focus indicator area ≥ the AAA geometry (≥2px solid perimeter, ≥3:1 contrast against adjacent colors) — this is the control a stressed clinician tabs to under a 2-minute ack SLA (`response_sla_source: CON-0062`, severity-model.yaml). |
| 2.5.5 | Target Size (Enhanced) | AAA | ≥44×44 CSS px target — required for the 1-click ack control (`CON-0091`/`PER-C-05`) and any bedside/gloved-hand touch action (§6). |
| 2.5.7 | Dragging Movements | AA (new 2.2) | Any drag interaction (e.g. a future bed-reassignment drag-drop) MUST ship a single-pointer tap/menu alternative — no drag-only affordance. Flag to `command-center-designer`. |
| 2.5.8 | Target Size (Minimum) | AA (new 2.2) | ≥24×24 CSS px floor for every pointer target platform-wide (spacing exception only if an inline text link or an equivalent larger control exists elsewhere). |
| 3.2.6 | Consistent Help | A (new 2.2) | If a help/support entry point exists, it appears at the same relative point across `PageContainer`-shell pages. |
| 3.3.7 | Redundant Entry | A (new 2.2) | The schema-driven clinical form engine (ADR-0015) MUST NOT re-ask for information already supplied earlier in the same multi-step/drawer flow (auto-populate or offer selection) — binds `form-engine-designer`. |
| 3.3.8 | Accessible Authentication (Minimum) | AA (new 2.2) | No step in login **or e-signature** may rely solely on a cognitive-function test (recalling/transcribing a PIN) without an alternative or assistive mechanism (§7 — directly closes the shared-PIN finding, `RULE-AUTH-USUARIOS-063`). |
| 4.1.2 | Name, Role, Value | A | Every custom primitive (`Ball`, `DrawerBuilder`→overlay-stack, severity chip, MicroIndicadores icon) exposes an accessible name/role/state — no bare `<div onClick>`. |
| 4.1.3 | Status Messages | AA | Live alert/status updates are programmatically determinable without a forced focus change (§5). |

### 1.2 AAA critical-value scoping rule (`A11Y-REQ-01`)

**`A11Y-REQ-01`** — Any DOM node whose primary content is a `clinical.severity.critical` value (a
critical alert card, a critical-flagged vital/lab cell per the abnormal-value flagging service,
`CON-0054`/`DES-C-06`) MUST meet 1.4.6 (7:1 / 4.5:1 large) and 2.4.13 (enhanced focus) if
interactive. Everything else on the same screen needs only 1.4.3/2.4.7 (AA). This scoping keeps
AAA achievable without contorting the whole palette (a known trade-off: full-AAA color systems
usually can't also hit brand/tenant flexibility — ADR-0004).

---

## 2. Color-blind-safe severity validation

### 2.1 Rule: color is always the third channel, never the only one

Severity in IntensiCare v2 is **always triple-encoded — color + icon + shape** (`CON-SEED-11`,
severity-model.yaml, echoing ADR-0013's fix mandate `CON-0041`/`CON-0042`). This is not a style
preference; §2.3 below shows *why* it is load-bearing: at least one adjacent severity pair
collapses toward indistinguishability under common color-vision deficiency (CVD) simulation in
**every** candidate palette tested. **`A11Y-REQ-02`** — no screen spec may encode severity, alert
resolution (true/false-positive), or any pass/fail state by hue alone; each must carry a distinct
icon **and** a distinct shape/outline treatment that reads identically in greyscale.

### 2.2 Method

Every candidate severity palette (dark theme + light theme) MUST pass, before it can be ratified at
barrier **C2**:

1. **WCAG contrast** — `A11Y-REQ-03`: each severity token ≥ 4.5:1 against its theme's canonical
   surface background (AA text minimum); `critical` ≥ 7:1 (AAA, §1.2); all four ≥ 3:1 as a
   non-text/graphical object (borders, chart points) per SC 1.4.11.
2. **CVD simulation** — `A11Y-REQ-04`: simulate each token under **protanopia, deuteranopia, and
   tritanopia** (dichromacy — the total-loss end of each cone-deficiency spectrum, the worst case a
   partial anomalous-trichromat still clears if the full dichromat passes) using a linear-RGB
   Brettel/Viénot-derived transform, then compute pairwise **CIE76 ΔE\*ab** in Lab space between
   every pair of the four severities, under normal vision and under each of the three simulations.
   A pair with ΔE ≥ 10 is "clearly a different color" under that vision type; ΔE < 10 is
   **LOW-RISK** and that pair's icon+shape divergence becomes load-bearing, not decorative, for
   that vision type.
3. **Manual confirmation** — `A11Y-REQ-05`: before ship, re-verify the ratified token set with a
   dedicated tool (browser DevTools "Emulate vision deficiencies," or Sim Daltonism / Coblis) on
   the actual rendered component, not swatches — icon+shape rendering at real severity-chip size
   can itself fail at small sizes (§6 touch-target floor also protects legibility here).

This is a reproducible, scriptable check (method, not a fixed artifact) — re-run it whenever
design-token-systems-designer proposes or edits severity hex values.

### 2.3 Evidence: validated example palette

The candidates below are legacy-informed (derived from `statusTrilha` ball colors — audit
`DES-2-02`) and satisfy `A11Y-REQ-03`; they are **example evidence for the C2 decision**, not a
ratified token file (design-token-systems-designer owns the final `clinical.*` hex — `CON-0041`).

**Dark theme** (surface `#0B0F14`, ADR-0002 dark-first default):

| Severity | Hex | Contrast vs `#0B0F14` | AA text (4.5) | AAA text (7.0) |
|---|---|---|---|---|
| normal | `#35D48A` | 10.01:1 | PASS | PASS |
| watch | `#E8C34D` | 11.30:1 | PASS | PASS |
| urgent | `#FF9142` | 8.59:1 | PASS | PASS |
| critical | `#FF7A90` | 7.72:1 | PASS | **PASS** (§1.2 `A11Y-REQ-01`) |

**Light theme** (surface `#F4F6F8`, ADR-0003 symmetric token-driven variant):

| Severity | Hex | Contrast vs `#F4F6F8` | AA text (4.5) | AAA text (7.0) |
|---|---|---|---|---|
| normal | `#0B7A42` | 5.00:1 | PASS | fail |
| watch | `#8A6A00` | 4.68:1 | PASS | fail |
| urgent | `#A34014` | 5.87:1 | PASS | fail |
| critical | `#8F1B29` | 8.23:1 | PASS | **PASS** |

**Pairwise ΔE\*ab under CVD simulation** (dark theme shown; light theme yields the same pattern —
full worksheet in `docs/plan/_work/scripts/` if regenerated). Bold = LOW-RISK (< 10), i.e. color
alone will not separate that pair for that vision type — icon+shape is what actually carries the
distinction:

| Pair | Normal vision | Protanopia | Deuteranopia | Tritanopia |
|---|---|---|---|---|
| normal ↔ watch | 68.5 | 58.8 | 74.1 | 65.2 |
| normal ↔ urgent | 98.5 | 69.8 | 90.2 | 90.3 |
| normal ↔ critical | 110.7 | 46.5 | 72.1 | 78.1 |
| watch ↔ urgent | 36.5 | 12.0 | 16.8 | 26.1 |
| **watch ↔ critical** | 72.8 | 12.7 | **3.9** | 13.6 |
| urgent ↔ critical | 48.5 | 24.5 | 19.9 | 13.3 |

**Finding (`A11Y-FINDING-01`):** `normal` (the green/teal family) stays safely separated from the
"warm" cluster under all three CVD types in both themes (ΔE ≥ 41.8 worst case). Within the warm
cluster — `watch`/`urgent`/`critical` (amber/orange/red) — at least one adjacent-or-skip pair drops
below the safe threshold under at least one CVD type in **both** themes; deuteranopia (the most
common CVD, ~5–6% of males) is the worst case, collapsing `watch↔critical` to ΔE 3.9 (dark) / 7.8
(light). **This quantifies exactly why ADR-0013's mandate is correct and non-negotiable**: a
deuteranope glancing at a bed tile cannot reliably tell "relevant change, review in 2h" from
"imminent risk to life" by color alone. The icon (`eye` vs `alert-octagon`) and shape (rounded-square
vs octagon) must therefore differ enough to be legible at the smallest severity-chip render size —
`A11Y-GATE-06`.

### 2.4 Severity → icon/shape reference (from severity-model.yaml, restated for this gate)

| Severity | Color family | Icon | Shape | Delivery tier |
|---|---|---|---|---|
| normal | green | `check-circle` | circle | 4 (advisory, no push) |
| watch | amber | `eye` | rounded-square | 3 |
| urgent | orange | `exclamation` | triangle | 2 |
| critical | red | `alert-octagon` | octagon | 1 (interruptive) |

Icon and shape MUST differ pairwise for every one of the 6 severity pairs simultaneously (not just
the LOW-RISK ones above) — a future re-hue of the palette must not silently reuse an icon or
outline shape across two bands. `A11Y-REQ-06`.

### 2.5 Legacy severity bugs this standard forecloses

Both live legacy bugs the audit found (ADR-0013, `CON-0042`/`ADR-C-09`) are accessibility failures,
not just visual ones, and are explicitly out of bounds for v2: (a) a toast whose icon color is
hardcoded regardless of the alert's real severity is a **1.4.1 violation by construction** — a
sighted colorblind user AND a screen-reader user (§5) both get the wrong severity signal; (b) a
criteria panel colored by a literal `'VERMELHO'` key instead of each criterion's own value fails
the same way. `A11Y-GATE-07` requires every severity-colored/iconed/announced element derive its
encoding from the actual current severity value at render time, never a hardcoded literal.

---

## 3. Keyboard & focus model — managed drawer/overlay stack

Scope: the overlay-stack manager ADR-0010 identifies as missing infrastructure (legacy had no
Esc/back coordination or shared focus trapping across its 16 `DrawerBuilder` call sites). This is
new infrastructure for `frontend-architect`; this section is its accessibility contract.

### 3.1 Stack model

A single global stack. Each push records `{id, level, role, trigger_element_ref, initial_focus_ref}`.
`level` starts at 1; **`A11Y-REQ-07`: max depth is 2** (matches the legacy pattern worth keeping —
ADR-0010, "nests up to 2 levels deep" — DES-3-02/DES-4-04). A 3rd push is rejected/replaces the
current level-2 overlay rather than growing an unbounded, unmanageable focus-trap chain.

### 3.2 Esc / back semantics

- **`A11Y-REQ-08`** — `Escape` closes **only the topmost** overlay, never cascades through the
  stack. This is ADR-0010's explicit recommendation and the one behavior legacy's ungoverned
  `DrawerBuilder` instances never got right (no shared coordination existed at all).
- **`A11Y-REQ-09`** — Hardware/OS back (Android back gesture, browser back button) is intercepted
  while any overlay is open (one `history` entry pushed per open level) and also closes **only the
  topmost** overlay; only when the stack is empty does back navigate the underlying route. This
  keeps "back" semantically identical to Esc for a keyboard/switch/AT user who cannot press a
  screen close (×) button.
- Closing any level restores the trigger element's focus exactly (`A11Y-REQ-11` below) — never
  bubbles focus to `<body>`.

### 3.3 Focus trap

- **`A11Y-REQ-10`** — Each open level is `role="dialog"` (or `role="alertdialog"` for a destructive
  confirmation, e.g. discard/delete), `aria-modal="true"`, labelled via `aria-labelledby` pointing
  at its visible heading. `Tab`/`Shift+Tab` cycles **only** within that level's focusable set.
- Content behind the topmost level (the page, and any level-1 drawer under an open level-2 drawer)
  is marked `inert` (or `aria-hidden="true"` as a fallback for browsers without `inert` support) so
  a screen-reader virtual cursor cannot wander into it — this closes a gap the legacy pattern had no
  answer for (no `aria-modal` behavior is documented in the audit's DrawerBuilder facts).
- Background scroll is locked while any overlay is open; the overlay's own content scrolls
  independently (preserves the legacy 95vw-below-1260px / 50vw-above sizing behavior, ADR-0010).

### 3.4 Initial focus & restore

- **`A11Y-REQ-11`** — On open, focus moves to the overlay's first meaningful interactive control or
  its heading — **not** automatically to the close (×) button, and **not** automatically to a
  destructive default action. Exception: an `alertdialog` confirming a destructive action places
  focus on the **safe** default (Cancel), never the destructive one.
- On close, focus returns to the exact `trigger_element_ref` that opened it (the tile, chip, or
  button clicked/activated) — critical for a keyboard user navigating the dense bed-grid, where
  losing your place means re-tabbing across dozens of tiles.
- If closing an overlay unmounts its form state (a `destroyOnClose`-equivalent decision, owned by
  `form-engine-designer`), any pending success/error messaging generated at the moment of unmount
  MUST still be announced via a live region that outlives the unmount (§5), not silently dropped.

### 3.5 Focus not obscured (SC 2.4.11)

**`A11Y-REQ-12`** — The currently focused control, at any stack level, is never fully hidden behind
a sticky header/footer, a toast, or the edge of a lower overlay level. This binds the z-index token
scale (ADR-0006/`CON-0036`'s formal-scales mandate): stacking order MUST guarantee the active
level's focused element paints above every non-overlay-stack element and above lower overlay
levels.

---

## 4. Reduced-motion policy

- **`A11Y-REQ-13`** (hard ban, always on) — No animation, in either theme or density mode, and
  regardless of user preference, flashes faster than **3 times per second** (SC 2.3.1, Level A —
  not a "nice to have," a seizure-safety floor). This covers any future pulsing critical-alert
  treatment: use a static high-contrast border/icon + a textual "NEW" badge instead of a pulse.
- **`A11Y-REQ-14`** — Under `prefers-reduced-motion: reduce`: all non-essential motion (drawer
  slide-in/out, fade transitions, ambient/decorative animation, gauge-needle sweeps) collapses to
  an instant or near-instant (≤ the motion scale's shortest token, ADR-0006 — exact duration is
  design-token-systems-designer's call at C2) opacity/visibility change. Essential motion that
  *carries meaning* (a live trend sparkline, a value visibly counting) is retained but (a) capped in
  speed, and (b) always paired with a static text alternative (the delta value as a number) so the
  meaning is never conveyed by motion alone — this is the same "never encode by one channel" logic
  as §2.1, applied to motion instead of color.
- **`A11Y-REQ-15`** — Live, auto-updating surfaces (bed-grid tiles re-rendering on WebSocket push)
  never auto-scroll the viewport or reflow focus out from under a keyboard/screen-reader user; new
  data updates in place. This also protects SC 4.1.3 (status messages must not force a focus
  change) and keeps the bed-grid usable while a clinician is mid-navigation.
- Applies uniformly across monitor-wall, workstation, and phone density modes (ADR-0011) — a
  monitor-wall's larger, more numerous tiles make uncontrolled motion worse, not better, for
  attention management.

---

## 5. Screen-reader semantics for live alert regions

### 5.1 aria-live level per severity

Derived directly from the ratified delivery tiers in `severity-model.yaml` (owner
alert-engine-architect) — this section is the accessibility rendering of that same lifecycle, not a
competing model:

| Severity | Delivery tier | Live-region role/politeness | Rationale |
|---|---|---|---|
| critical | 1 (interruptive, never rate-limited) | `role="alert"` (implicit `aria-live="assertive"`, `aria-atomic="true"`) on the alert card itself | Matches "mandatory ack," never-suppressed delivery (`CON-0062`, severity-model.yaml `rate_limited: false`). Does **not** force a focus change (SC 3.2.1/3.2.2) — a life-critical announcement must not yank focus from whatever the clinician is doing; it interrupts *audibly*, and a persistent, keyboard-reachable ack control (§1.1, SC 2.4.13) is always available. |
| urgent | 2 (push + mobile, ack expected) | Dedicated `aria-live="assertive"` region (not page-level `alert`) | Announced promptly without the page-wide interruption semantics of `role="alert"`. |
| watch | 3 (WS push + badge, no page) | `aria-live="polite"` | Announced at the next pause in speech — matches "no escalation," non-interruptive delivery. |
| normal | 4 (advisory, no push) | `aria-live="off"` on the push channel; surfaced only in a standard navigable landmark (a "worklist"/log region a screen-reader user reaches on demand) | Matches "no push, no page" (delivery_tier 4) — an advisory should not compete for auditory attention at all. |

`A11Y-REQ-16` binds this table: severity-to-politeness mapping is a **build-time-checkable**
contract (mirrors the units-registry pattern, `CON-SEED-12`) — a component rendering a `critical`
alert without `role="alert"`/assertive semantics is a defect, not a style choice.

### 5.2 Anti-stomping: coalesced live regions

A raw `aria-live` region that mutates faster than a screen reader can speak causes **stomping** —
later DOM mutations interrupt/replace the announcement of earlier ones, and the user hears only the
last update, silently. Given the platform's own multi-domain fan-out (up to 7 Phase-2 alert
domains + early-warning scores can all fire near-simultaneously), this is a real risk, not a
theoretical one.

**`A11Y-REQ-17`** — One live-region container **per severity tier** (four containers total, not one
per alert). Updates to a container are coalesced at a floor of ~1 announcement per 2 seconds per
container; when multiple alerts arrive within that window, the announcement states the count and
the latest item, e.g. *"3 new critical alerts. Latest: bed 12, SpO₂ 82%, falling."* This never
delays the **visual** alert (which still renders and paints immediately, feeding the p95 < 30s /
RRT <5s budgets in `docs/plan/architecture/alert-engine.md` §8) — only the redundant *spoken*
announcement is batched. `critical`'s never-rate-limited delivery guarantee (§5.1) is about alert
*generation/suppression*, not about announcement-batching; the alert itself is never dropped or
delayed, only its screen-reader narration is debounced to stay intelligible.

### 5.3 Accessible name for every alert

**`A11Y-REQ-18`** — Every alert's accessible name/description states, in order: severity word
(never color name), triggering parameter and its value + trend direction, and location (bed/patient
identifier) — directly operationalizing persona constraint **`PER-C-04`**/`CON-0090` ("every alert
MUST expose which specific parameter triggered it") for screen-reader users, not just sighted ones.
Example: *"Critical. Heart rate 142, rising. Bed 07, Patient J.S."* — never *"Alert. Bed 07."*

### 5.4 Feedback/error severity (ties ADR-0016)

`ADR-0016`'s recommendation to classify errors by severity (validation | permission | server)
independent of backend shape (`CON-C-11`) maps onto ARIA as: inline validation errors →
`aria-describedby` + `aria-invalid="true"` on the field (never a blocking modal for a validation
error); permission/auth errors → `role="alert"` toast (assertive, non-blocking); server/destructive
failures → `role="alertdialog"` only when the user must decide next action. **`A11Y-REQ-19`** — no
error class defaults to a blocking `Modal.error` regardless of severity (the audited legacy
`handleApiError` behavior, `ADR-0016-01`) — that pattern is retired, not ported.

---

## 6. Touch target & glare/night-shift guidance

### 6.1 Touch targets

- **`A11Y-REQ-20`** — Platform-wide floor: **24×24 CSS px** (SC 2.5.8) for every pointer target; if
  a control must render smaller (dense table cell, inline chip), it needs either ≥24px of
  unobstructed spacing to the next target or an equivalent full-size control reachable elsewhere.
- **`A11Y-REQ-21`** — **44×44 CSS px** (SC 2.5.5, AAA) for: the alert acknowledge control
  (`CON-0091`/`PER-C-05`, "1-click ack"), any bedside touch action performed with gloved hands, and
  every RRT mobile-app primary action (`CON-0092`/`PER-C-06`, <5s notification-to-visible-action).
  Clinical staff frequently operate gloved, under time pressure, or on a shared bedside tablet —
  the AAA target-size floor is the appropriate default here, not an edge-case accommodation.
- Monitor-wall density mode (ADR-0011) is glanceable, not primarily interactive — its targets may
  legitimately sit closer to the 24px floor since its primary input is a pointer/mouse at a
  workstation, not a touchscreen; workstation and phone modes default to the 44px floor for primary
  actions.

### 6.2 Glare and night-shift ergonomics

- The dark-first "quiet ICU" default (ADR-0002) has a genuine clinical-ergonomics rationale beyond
  aesthetics: sustained bright-white UI in a dim ICU bay or overnight causes glare against the
  physical environment and degrades a clinician's dark adaptation right before/after a bedside
  observation. `A11Y-REQ-22`: **monitor-wall mode defaults to dark theme regardless of the viewer's
  saved light/dark preference**, but remains user-switchable (never a forced, unescapable state —
  that would itself be an accessibility regression for a user who needs light theme for contrast-
  sensitivity reasons).
- **`A11Y-REQ-23`** — Neither theme uses pure `#FFFFFF` or pure `#000000` as a large surface fill:
  pure white on a large panel causes halation/glare under typical ICU fluorescent lighting reflected
  off monitor glass; pure black crushes the neumorphic elevation signature's shadow detail (ADR-0007)
  to invisible. Light-theme surface ≈ `#F4F6F8` (used in §2.3); dark-theme surface ≈ `#0B0F14`.
- **`A11Y-REQ-24`** — Honor `prefers-contrast: more` with the flat-shadow fallback ADR-0007 already
  recommends for the neumorphic elevation scale (dual embossed shadows can visually blur clinical
  text at high-contrast/low-vision settings); this also satisfies the `CON-0037`/`ADR-C-04`
  ledger constraint requiring an explicit contrast check on any clinical content over an embossed
  surface, in both themes.
- No severity or status encoding may depend on a color's saturation/brightness alone under glare
  (e.g. a washed-out monitor at a distance) — this is exactly what §2's icon+shape mandate already
  guarantees; glare is functionally a fourth "vision deficiency" this standard already defends
  against.

---

## 7. Accessible authentication — the shared-PIN closure

The audit's shared-default-signing-PIN finding (`RULE-AUTH-USUARIOS-063`, P0/legal-review item —
"every `Usuario.pin` created without an explicit value inherits the same org-wide default... any
user whose PIN was never rotated legally signs clinical documents with a shared secret") is a
patient-safety/legal defect the platform must fix regardless of accessibility framing (routed to
`security-lgpd-engineer` / RATIFICATION.md for the legal-review disposition). This standard adds
the **accessibility** constraint on whatever replaces it:

**`A11Y-REQ-25`** — SC 3.3.8 (Accessible Authentication, Minimum, AA, new in 2.2): the redesigned
e-signature/PIN flow MUST NOT rely solely on a cognitive-function test (recalling or transcribing a
PIN) with no alternative — provide at least one of: (a) a password-manager-compatible flow (no
paste-blocking), (b) a platform biometric/passkey option where the device supports it, or (c) a
mechanism to assist (e.g. PIN re-entry with no arbitrary attempt-count lockout that forces
memorization under stress). This applies equally to standard login. A per-user, individually-set
signing credential (closing the shared-default defect) and an accessible authentication path are
two independent requirements on the same redesign — satisfying one does not satisfy the other.

---

## 8. The A11Y GATE — required for every design deliverable

Every `docs/plan/design/screens/<flow>.md`, `design-tokens.md`, and `component-library.md` MUST
include an "Accessibility gate" subsection that checks off every applicable item below by ID, or
explains why an item is not applicable to that surface. Phase D's completeness critic treats a
missing gate subsection as equivalent to a missing test-vector set on an alert (back to owner).

- [ ] **A11Y-GATE-01** — Every text/label meets SC 1.4.3 (4.5:1 / large-text 3:1); every
      `critical`-scoped element additionally meets SC 1.4.6 (7:1 / 4.5:1) per `A11Y-REQ-01`.
- [ ] **A11Y-GATE-02** — Every icon, chart mark, severity border/glow, and focus ring meets SC
      1.4.11 (≥3:1 non-text contrast) against its adjacent color(s), in both themes.
- [ ] **A11Y-GATE-03** — No status, severity, resolution, or validation state is encoded by color
      alone (`A11Y-REQ-02`); each has a distinct icon and shape/outline per §2.4.
- [ ] **A11Y-GATE-04** — Any severity or status palette proposed/edited has been run through the
      §2.2 method (WCAG contrast + 3-CVD-simulation ΔE check) with results recorded, not just
      eyeballed.
- [ ] **A11Y-GATE-05** — No animation on this screen exceeds 3 flashes/second under any
      circumstance (`A11Y-REQ-13`); `prefers-reduced-motion: reduce` is honored for all
      non-essential motion (`A11Y-REQ-14`); essential motion has a static text fallback.
- [ ] **A11Y-GATE-06** — Icon+shape pairs remain visually distinct at the smallest rendered
      severity-chip/badge size used on this screen (protects the LOW-RISK CVD pairs in §2.3).
- [ ] **A11Y-GATE-07** — Every severity-colored/iconed/announced element derives its encoding from
      the live current severity value — no hardcoded literal severity anywhere in the spec (closes
      both ADR-0013 legacy bugs, §2.5).
- [ ] **A11Y-GATE-08** — Every overlay/drawer on this screen specifies: Esc closes only itself
      (`A11Y-REQ-08`), back-button semantics match Esc (`A11Y-REQ-09`), `role="dialog"`/`alertdialog`
      + `aria-modal` + focus trap (`A11Y-REQ-10`), initial-focus target and exact focus-restore
      target (`A11Y-REQ-11`), and stack depth ≤2 (`A11Y-REQ-07`).
- [ ] **A11Y-GATE-09** — Every live-updating region on this screen names its `aria-live`
      politeness per the §5.1 severity table and, if it can receive bursts, its coalescing behavior
      (`A11Y-REQ-16`/`A11Y-REQ-17`).
- [ ] **A11Y-GATE-10** — Every alert/status element's accessible name follows the §5.3 order
      (severity → parameter+value+trend → location) — never severity/location alone.
- [ ] **A11Y-GATE-11** — Every pointer target meets the 24×24 floor (`A11Y-REQ-20`); every
      acknowledge/primary bedside/mobile action meets the 44×44 floor (`A11Y-REQ-21`).
- [ ] **A11Y-GATE-12** — No large surface on this screen uses pure `#FFFFFF`/`#000000`
      (`A11Y-REQ-23`); embossed/neumorphic surfaces carrying clinical text pass a stated contrast
      check in both themes (`CON-0037`) and have a `prefers-contrast: more` fallback
      (`A11Y-REQ-24`).
- [ ] **A11Y-GATE-13** — Any drag interaction on this screen ships a single-pointer alternative
      (`A11Y-REQ-14` §2.5.7 row) — or the screen has no drag interactions (state which).
- [ ] **A11Y-GATE-14** — Any authentication/e-signature step on this screen offers a path that is
      not a pure cognitive-function test (`A11Y-REQ-25`) — or the screen has none.
- [ ] **A11Y-GATE-15** — Every custom component used has a stated accessible name/role/state
      mapping (SC 4.1.2) — no bare clickable `<div>`/`<span>` without a role.
- [ ] **A11Y-GATE-16** — If the schema-driven clinical form engine is used on this screen, no field
      re-asks information already captured earlier in the same flow (SC 3.3.7, `A11Y-REQ-*` in §1.1).

---

## 9. Open reconciliations

- **Exact severity token hex/shape values** are ratified by `design-token-systems-designer` at
  barrier **C2**; §2.3's palette is validated evidence for that decision, not the final artifact.
  Whatever is ratified MUST be re-run through the §2.2 method before ship.
- **Motion-scale durations** (ADR-0006, "instant" token value for `A11Y-REQ-14`) are
  `design-token-systems-designer`'s call at C2; this standard only fixes the ceiling (3 Hz hard
  ban) and the reduced-motion behavior, not exact milliseconds.
- **Drag interactions**: none are currently specified in any Phase-B design deliverable; §1.1's
  2.5.7 row and `A11Y-GATE-13` are pre-registered so `command-center-designer` cannot introduce one
  later without the single-pointer alternative.
- **Accessible-authentication mechanism choice** (§7, passkey vs assisted-PIN vs both) is
  `security-lgpd-engineer`'s design call; this standard fixes only the SC 3.3.8 constraint the
  choice must satisfy, and notes the shared-PIN legal-review disposition is tracked separately in
  RATIFICATION.md via `RULE-AUTH-USUARIOS-063`.
