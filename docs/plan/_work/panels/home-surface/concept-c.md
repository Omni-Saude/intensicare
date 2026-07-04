# Home Surface — Concept C: Acuity-Flow Command Center

**Concept ID:** C · **Panel:** bed-grid command center home surface · **Stance:** acuity-flow-first
**Design authority (fixed, non-negotiable):** dark-first default (ADR-0002-01); formal token scales as the single source of truth (ADR-0005/0006, DES-C-03); Radix primitives for generic non-clinical behavior (orchestrator directive; ADR-0012-01 "adopt a headless library for generic non-clinical concerns"); ONE realtime push channel (ADR-0017-01, DES-C-05, ADR-C-13); severity encoded as **color + icon + shape** together, never color alone (ADR-0013-01, WCAG 2.2 AA); WCAG 2.2 AA throughout.

---

## 1. Thesis (why this concept diverges)

The bed grid is not a passive floor map that a coordinator reads *after* the fact and that alerts merely decorate. In Concept C the grid **is** the analytic instrument. Two forces choreograph it in real time:

1. **Acuity** — each bed carries an acuity *vector*: current clinical severity band **and** its trajectory (rising / steady / falling), derived from the deltas of the already-implemented scores MEWS, NEWS2, qSOFA, SOFA over the 24 h window (VIS-2-01…04). The grid weights, orders (optionally), and animates by that vector so deterioration is visible at a glance, not buried in a spatial layout.
2. **Occupancy** — bed state (occupied / empty / cleaning / reserved / blocked) is a first-class visual layer, not an afterthought. This directly fixes the legacy defect where an empty bed and a NEUTRO occupied bed were "indistinguishable except by content" (DES-5-03).

Coordinator analytics are **woven into the grid**, not siloed on a separate dashboard tab. Dra. Fernanda's real-time occupancy/acuity dashboard (PER-FERNANDA-01) is an ambient *ribbon* laminated to the top of the same surface everyone else uses, fed by the same one realtime channel — so the grid and the KPIs can never visibly disagree (ADR-C-13). This is the deliberate divergence: **occupancy + acuity choreography for Fernanda, with her analytics living inside the grid rather than beside it**, while the bedside roles get exactly the density they need from the same cell contract.

---

## 2. Layout

Three stacked regions inside the standard app shell (PageContainer successor; ADR-0008). No persistent side nav — wayfinding stays tile-drill-down + header context switcher + ONE persistent breadcrumb extended to full depth (ADR-0009-01).

### 2.1 The Acuity–Occupancy Ribbon (top, ~64–96px, collapsible)
Fernanda's dashboard, woven in. Per selected scope (a unit, or all units), three laminated micro-widgets rendered from the same realtime feed:

- **Occupancy meter** — filled/empty/cleaning/reserved/blocked as a segmented bar with numeric fill (e.g. `26/30`) and capacity headroom. Replaces the legacy operational-only occupancy gauge (DES-5-05) and gives Fernanda the "data, not perception" she needs to justify bed capacity (PER-FERNANDA needs_2l).
- **Acuity distribution** — a stacked severity bar (CRIT / URG / WARN / INFO / normal counts) using the `clinical.*` scale (LEGEND-SEV; CAT-C-02…05). Each segment labeled with a number and a shape/pattern token, **not color alone**, so it is legible to color-blind users and on a wallboard from across the room.
- **Response-time SLA gauge** — live mean time-to-action against the program target ≤ 15 min (VIS-7.1-03), with an at-risk count. This is Fernanda's quality indicator surfaced continuously, not just in the weekly export (PER-FERNANDA-02).

A **unit switcher** (adult / coronary / neonatal — PER-FERNANDA context_2l) sits in the ribbon; switching re-scopes the whole surface. The ribbon collapses to a 1-line summary for bedside roles who don't need coordinator KPIs (role-default, see §4).

### 2.2 The Bed Grid (center, the surface)
A responsive grid of **bed cells** laid out by **ONE shared density/column-span function** covering the full viewport-width domain with no gaps — explicitly closing the legacy `(2400px, 2800px]` dead-band bug and the two drifted bucket chains (ADR-0011-01, DES-C-04, ADR-C-07). This same function is what powers the three density modes (§3).

**Bed cell anatomy** (progressive disclosure by density mode):
- **Frame** — neumorphic elevation via the governed `elevation.*` token pair (ADR-0007-01, DES-C-07); the border/glow carries clinical severity color, backed by an **icon** (severity glyph) and a **shape** cue (band-specific corner/notch), so severity survives grayscale (ADR-0013-01).
- **Occupancy state** — empty/cleaning/reserved/blocked rendered with a distinct fill + hatch pattern, never confusable with a low-acuity occupied bed.
- **Identity** — bed id (encodes physical location, which is exactly what Rafael needs en route, PER-RAFAEL-01), patient name/age/sex.
- **Dominant score** — the driving score value (MEWS / NEWS2) in tabular monospace (the token set adds a monospace family for clinical values; DES-2-05 fix) with a **trend arrow** (↑ rising / → steady / ↓ falling) = the acuity trajectory.
- **Triggering-parameter chip** — the single parameter that pushed the score (RR? SpO₂? BP?), the literal thing Enf. Ana asks for (PER-ANA-02, PER-C-04). The chip is also the **1-click acknowledge** target (PER-ANA-03).
- **Micro-indicators** — vasopressor / mechanical ventilation / sedation / dialysis / LOS days (the legacy MicroIndicadores row, DES-3-05), shown in Standard/Focus density only.
- **Abnormal-value flags** — vitals/labs that breach reference ranges get threshold-based color+icon flagging (fixing the "no abnormal-value flagging anywhere" top gap, ADR-0014-01, DES-C-06); e.g. SpO₂ 60 % never renders identically to SpO₂ 99 % again.

**Acuity flow choreography.** When a bed's acuity vector changes band *upward into URG or CRIT*, the cell animates: it lifts (elevation token step-up) and, in flow-sort mode, migrates toward the top cluster. Downward/steady changes are quiet (no motion, just the color+shape+arrow update). Motion is a token-scale transition, gated by `prefers-reduced-motion` (falls back to an instant state change). This is the "flow" — the eye is drawn to *trajectory*, not to raw alert count.

**Flow vs. Spatial toggle.** Default per user is **Spatial** (beds in physical bed-number order — preserves "bed 7 is bed 7" muscle memory). Users who watch acuity (Carlos, Fernanda) can switch to **Acuity flow** (deteriorating-to-top clustering). Assigned beds can be **pinned** so they never migrate out of a nurse's sightline.

### 2.3 The Working Rail / Drawer layer (right or overlay)
Selecting a bed opens a detail drawer using the drawer-in-drawer pattern with a real **overlay-stack manager** — Esc/back closes only the topmost, per-level focus trap (ADR-0010-01, fixing the legacy no-coordination gap). The drawer holds: 24 h score trend chart (Carlos's PER-CARLOS-03 / PER-RAFAEL-02), the active alert list for that bed with the triggering inputs, vitals/labs with abnormal-value flags, and the ack + outcome-documentation actions. No routed page change, no reload.

---

## 3. Three density modes (from the one density function)

| Mode | Intent / persona | Cell content | Ribbon | Motion |
|------|------------------|--------------|--------|--------|
| **Overview (wallboard)** | Unit wall display + Fernanda's across-the-room glance; large + >2800px monitors | severity (color+icon+shape) · bed id · dominant score · trend arrow only | prominent, expanded | flatten elevation for paint budget (ADR-0007 paint-cost caveat); escalation flash only |
| **Standard** | Default working density; Carlos + Ana at a station | Overview + triggering-parameter chip · top-2 micro-indicators · vitals staleness age | standard | full acuity-flow choreography |
| **Focus** | "My beds" deep work; Ana's 4–5 assigned beds, Carlos reviewing critical patients | Standard + inline 24 h score sparkline · active-alert preview · inline 1-click ack | collapsed to 1 line | full, plus inline expand |

All three are produced by the same unit-tested density function keyed on viewport width **and** an explicit user-chosen density preference, so column-span is always defined across the full width domain (ADR-C-07). Density is a token-driven preference, not a forked render tree (DES-C-04).

---

## 4. Interactions & role defaults

- **Ack an alert:** one click on the cell's triggering-parameter chip (or the drawer's inline ack) — no reload, optimistic patch reconciled against the authoritative record via the one channel (ADR-C-12). Meets PER-ANA-03 (1-click) and records the alert to the chart at NGS Level 2 (VIS-C-07).
- **Filters:** *My beds* (Ana), *My unit* (Carlos), *All units* (Fernanda), *Acuity ≥ URG* (surface only deteriorating), *RRT-eligible* (Rafael). Filters compose with the flow/spatial toggle.
- **Role-default surface config:** bedside roles (nurse, intensivist) boot into Standard/Focus with the ribbon collapsed; coordinator boots into Overview with the ribbon expanded and the unit switcher active. Route/role gating is **deny-by-default** (ADR-C-05, DES-C-08) — the client config is UX only; the API independently authorizes (ADR-C-14).
- **Analytics drill:** clicking any ribbon widget opens a woven analytics drawer (response-time distribution, occupancy history, acuity trend) with **export** to hospital quality tools (PER-FERNANDA-03, PER-C-08) — analytics stay *inside* the grid surface, the stance's signature.

---

## 5. States

- **Loading:** content-shaped skeleton grid (cell-shaped placeholders), never a full-viewport blocking spinner (ADR-0016-01, DES-5-07). Ribbon shows skeleton meters.
- **Empty scope:** unit with no beds → explicit empty state with capacity note; empty bed cells always visually distinct from occupied.
- **Stale / disconnected:** because there is exactly one channel, a dropped connection is made **loud, never silent** — a connection-state banner plus a per-cell staleness age badge (e.g. "atualizado há 45 s"). This is the deliberate inverse of the legacy silent-poll defect where "a red alert can take up to `tempo_atualizacao` seconds to reach the grid" and bell/grid visibly disagreed (DES-6-02, ADR-0017-01). Reconnect uses shared backoff.
- **Reconnecting:** banner shows retry; last-known state stays visible, dimmed, timestamped.
- **Error / permission-denied scope:** classified error (validation / permission / server) mapped to visual weight; permission-denied re-routes per deny-by-default guard (ADR-C-11, ADR-C-05).

---

## 6. How each persona succeeds

**Dr. Carlos (intensivista).** Acuity-flow sort lifts deteriorating patients to the top the moment their MEWS/NEWS2 trajectory turns — real-time deterioration detection instead of a nurse's hours-later hand calculation (PER-CARLOS needs_2l). Only **PPV-budgeted, deduped, suppressed** engine alerts render as chips, so the surface reflects actionable signal, not the legacy 200/day at 80 % false-positive — supporting his < 3 FP/patient-day bar (PER-C-02) and the program PPV ≥ 60 % goal (VIS-7.1-02). Score is live in < 30 s via the one channel (PER-C-01, VIS-C-09). Focus mode's inline sparkline + drawer give his 24 h trend view (PER-CARLOS-03).

**Enf. Ana (enfermeira).** MEWS is computed and rendered automatically on every cell — zero manual calculation (PER-ANA-01, replacing 20 min/shift/patient). Each cell names the *exact* parameter that triggered (the chip: RR / SpO₂ / BP), satisfying PER-ANA-02 / PER-C-04. That chip is also her 1-click acknowledge (PER-ANA-03). A *My beds* Focus filter with **pin** keeps her 4–5 assigned beds fixed in sightline even in acuity-flow mode.

**Dra. Fernanda (coordenadora).** The ribbon **is** her real-time occupancy/acuity dashboard (PER-FERNANDA-01), always on, across adult/coronary/neonatal via the unit switcher — not a separate page she has to open. Occupancy sub-states give her true capacity headroom to justify bed investment with data, not perception. The live SLA gauge surfaces mean response time continuously (feeding the weekly KPI report, PER-FERNANDA-02) and every widget exports to hospital quality tools (PER-FERNANDA-03, PER-C-08). Weaving analytics into the grid is precisely how this concept serves her without a context switch.

**Dr. Rafael (RRT).** The home surface is the desktop command center, but its **cell contract and the one realtime channel are the same feed** that pushes to his phone in < 5 s on a critical score (PER-RAFAEL-01, PER-C-06). Bed id encodes physical location, so his push carries score + trend + location for free. On the surface, an *RRT-eligible* filter flags deteriorating beds needing rapid response. His mobile view is the same cell collapsed to the mobile density bucket (same function, no fork), and the drawer gives latest vitals + trend en route (PER-RAFAEL-02) plus a 1-click outcome-documentation flow completable in < 1 min (PER-RAFAEL-03, PER-C-07).

---

## 7. Risks & mitigations

1. **Moving-target reordering.** Acuity-flow migration can break spatial muscle memory ("where did bed 7 go?"). → Spatial is the default; flow is an opt-in toggle; migrations animate + are throttled; assigned beds can be pinned.
2. **Motion as distraction / accessibility failure.** Escalation animation could overwhelm or violate reduced-motion needs. → All motion is token-scaled and gated by `prefers-reduced-motion`, falling back to an instant color+icon+shape state change with no translation.
3. **Analytics overload for bedside roles.** Weaving KPIs into the grid risks clutter for Carlos/Ana. → Ribbon is collapsible and role-default-collapsed for bedside roles; coordinator KPIs never intrude on the cell itself.
4. **Neumorphic paint cost at wallboard density.** 30–60 embossed cells is the exact scenario the audit flagged as costly (ADR-0007-01). → Elevation is a token; Overview/wallboard mode flattens to a single flat-shadow token; paint cost benchmarked before ship; `prefers-contrast` gets a flat fallback (ADR-C-04).
5. **Christmas-tree alarm fatigue.** If every acuity flicker colors + animates, the surface re-creates the legacy noise. → Only PPV-budgeted, deduped/suppressed alerts drive chips and motion; sub-URG band drift is shown quietly (color+shape, no motion, no toast); honors the ≤ 10 % alarm-fatigue goal (VIS-7.1-04).
6. **Single channel = single point of failure.** One realtime channel means one thing to lose. → Connection loss is loud (banner + per-cell staleness age), never silent; shared reconnect/backoff; last-known state stays visible and timestamped. This is a *feature* versus the legacy silent poll (ADR-0017-01).
7. **Severity re-derivation vs. muscle memory.** New `clinical.*` hex may differ from legacy "red bed = crisis" reflexes (ADR open question). → Severity is triple-encoded (color+icon+shape) so meaning survives any hue change and any color-vision profile; final hue set pending clinical sign-off, flagged as ratification-blocked.
8. **Wallboard legibility.** Coordinator glance from across the room needs contrast + text, not color alone. → Ribbon segments carry numbers + patterns; AA contrast verified in dark and light on neumorphic surfaces (ADR-C-04, WCAG 2.2 AA).

---

## 8. Evidence trail
Personas PER-CARLOS/ANA/FERNANDA/RAFAEL + criteria PER-C-01…08 · ADR-0002 (dark-first) · ADR-0005/0006 + DES-C-03 (tokens) · ADR-0007 + DES-C-07 (neumorphic elevation) · ADR-0009 (IA / no persistent nav) · ADR-0010 (overlay-stack manager) · ADR-0011 + DES-C-04 + ADR-C-07 (one density function, no dead-band) · ADR-0012 (Radix / headless for generic concerns) · ADR-0013 + ADR-C-08/09 (clinical severity color+icon+shape) · ADR-0014 + DES-C-06 (abnormal-value flagging) · ADR-0016 (skeleton vs spinner) · ADR-0017 + ADR-C-12/13 + DES-C-05/6-02 (one realtime channel) · ADR-0018 + ADR-C-05/14 (deny-by-default auth) · VIS-2-01…04 (implemented scores) · VIS-7.1-02/03/04 (PPV, response-time, alarm-fatigue goals) · VIS-C-07/09 (NGS-2 charting, <30s latency) · LEGEND-SEV + CAT-C-02…05 (severity/SLA scale).
