# Screen Spec — Command Center (Home Surface)

**Owner:** command-center-designer · **Status:** draft for reconciliation barriers **C2** (severity/density/IA UX) and **C3** (realtime latency, PPV feed, paint budget) · **Authority precedence:** ADR-001 ≻ vision ≻ directive ≻ audit (CONTRACTS §5).

This is the definitive home-surface spec: the **bed-grid command center** that is the first thing every role sees. The judge panel selected **Concept C — Acuity-Flow Command Center** (`_work/panels/home-surface/decision.yaml`, winner `c`, 4.0/4.0) with **eight mandatory adoption conditions** (`must_fix`). Every one is discharged here and traced in §14. Ideas grafted from the losing concepts (A "Monitor Wall", B "Drill-Down Workstation") are marked **[salvage:A]** / **[salvage:B]** inline and registered in §15.

The grid **is** the analytic instrument: each occupied bed carries an *acuity vector* — current severity band **and** its trajectory (rising / steady / falling) — over one shared realtime channel, with coordinator analytics woven into the same surface rather than siloed on a separate tab. This screen renders machinery owned elsewhere and never re-implements it: the alert lifecycle, why-panel, routing, and PPV/alarm-fatigue analytics live in `screens/alert-triage.md`; threshold governance and the weekly-report cadence live in `screens/admin-config.md`; the canonical severity/lifecycle model is `_work/platform/severity-model.yaml`; exact token values are `design/design-tokens.md`; source freshness is `_work/platform/amh-freshness.yaml`; the accessibility contract is `design/accessibility-standard.md`. It invents no clinical content — every cutoff lives in the alert catalog and units registry.

Every claim cites a source: a persona criterion (`PER-*`), a moment of truth (`MOT-*`), a hazard (`HAZ-*`), a vision metric (`VIS-*`), an audit fact (`ADR-*`/`DES-*`), a ledger constraint (`CON-*`), an accessibility requirement/gate (`A11Y-REQ-*`/`A11Y-GATE-*`), a WCAG success criterion (`SC n.n.n`), or a token/entity name.

---

## 0. Design-system frame (what this screen is built from)

- **Home surface is the bed-grid command center**; there is **no persistent side nav**. Wayfinding is tile drill-down + a header **context switcher** + **one persistent breadcrumb extended to full depth** (`ADR-0009-01`). Drill-down opens a managed **overlay/drawer stack** (Esc/back + focus trap), never a routed page change or `reload()` (`ADR-0010-01`; retires the legacy 4-deep uncoordinated `DrawerBuilder` nesting, `DES-4-04`).
- **Dark-first "quiet ICU" default** with a symmetric token-driven light theme (`ADR-0002`/`ADR-0003`; `A11Y-REQ-22` — monitor-wall defaults to dark regardless of saved preference but stays switchable). Neumorphic elevation is a governed `elevation.*` token pair contrast-verified in both themes, with a flat fallback under `prefers-contrast: more` (`ADR-0007`/`A11Y-REQ-24`).
- **Severity is `clinical.*` only, structurally separate from tenant `brand.*`** (`CON-0041`/`DES-C-01`) and never `semantic.feedback.*`; **always triple-encoded color + icon + shape** (`CON-SEED-11`, `SC 1.4.1`), never a hardcoded literal (`A11Y-GATE-07`). Rebranding a tenant never changes what a severity means (§4).
- **One realtime push channel** (WebSocket, shared reconnect/backoff) feeds the grid, the ribbon, presence, and the notification bell (`ADR-0017-01`/`DES-C-05`/`ADR-C-13`). The board **never polls** — grid and KPIs cannot disagree about one event (the inverse of the legacy silent-poll `tempo_atualizacao` gap, `DES-6-02`). See §8.
- **Abnormal-value flagging is a first-class service** (`ADR-0014-01`/`DES-C-06`): every vital/lab/score value on this surface is colored+iconed by *its own* band from the reference-range service — SpO₂ 60 % never renders identically to SpO₂ 99 % (`DES-5-04` gap closed).
- **Deny-by-default authorization**, enforced server-side ahead of shell render; the API independently authorizes every request (`ADR-C-05`/`ADR-C-14`/`DES-C-08`). The client density/role config is UX/defense-in-depth only.
- **The surface is never the delivery guarantee (`HAZ-025`).** The command center is a shared *ambient* instrument; per-severity delivery (WS push / mobile page to RRT / audible) and ack-SLA escalation defined in `severity-model.yaml` remain mandatory and individually audited regardless of who is looking at the wall (`alert-triage.md §1.2`).

---

## 1. Layout — three laminated regions inside the app shell

The standard app shell (PageContainer successor, `ADR-0008`) hosts a fixed header and three stacked regions. `container-type: inline-size` is set on the grid shell so density resolves against the **surface's own width**, not `window.innerWidth` (§5).

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│ [logo] │ CONTEXT: Empresa▾ ● Estab.▾ ▲ Setor▾ ● │ densidade ▣▤▦ │ 🟢 ao vivo · há 6s │ 🔔3 │ 👤│  ← shell header
│ TRILHA: Grupo AUSTA ▸ Hospital AUSTA ▸ UTI Adulto ▸ (Leito 12 ▸ Ocupação)            │  ← full-depth breadcrumb
├───────────────────────────────────────────────────────────────────────────────────┤
│ RIBBON  Ocupação 26/30 ▮▮▮▯ · Acuidade ⬢2 ▲3 ▢5 ●14 ⌀2 não-aval · SLA 12min (2 em risco)│  ← Fernanda woven dashboard
├───────────────────────────────────────────────────────────────────────────────────┤
│ GRADE DE LEITOS  (colunas por container query · spatial por padrão)                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                              │
│  │Leito 01│ │Leito 02│ │Leito 03│ │Leito 04│ │Leito 05│ …                            │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘                              │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### 1.1 Shell header
Everything in the header is a *filter, mode, or lateral context switch* — never (on the home surface) a route change. It carries: the **context switcher** (§2.1), the **full-depth breadcrumb** (§2.2), the **density control** (§5), the **freshness pill** `ao vivo · reconectando · dados defasados (há Xs)` [salvage:A] as the single shared staleness truth (§6, `MOT-04`), and the **notification bell** (same channel as the grid). Consistent-help entry point sits at the same relative point across shell pages (`SC 3.2.6`).

### 1.2 The Acuity–Occupancy Ribbon (top, ~64–96px, collapsible)
Dra. Fernanda's real-time occupancy/acuity dashboard **woven into the grid**, not a separate page (`PER-FERNANDA-01`, `MOT-03`). Three laminated micro-widgets, all rendered from the **same authoritative feed** as the cells with **no client-side re-derivation** (`MF-4`/`ADR-C-13`, §7.2): an **occupancy meter**, an **acuity distribution** bar (with a first-class *não-avaliado* segment, `MF-2`), and a live **response-time SLA gauge** (≤ 15 min target, `VIS-7.1-03`). Full spec in §7. It collapses to a 1-line summary for bedside roles but **never drops the crítico count / cross-unit floor** (`MF-5`, §7.3) [salvage:A].

### 1.3 The Bed Grid (center — the surface)
A responsive grid of **bed cells** laid out by one shared column-span function over the full width domain with no gaps (§5), closing the legacy `(2400px, 2800px]` dead-band (`ADR-0011-01`/`ADR-C-07`/`DES-4-05`). Cell anatomy, occupancy states, the acuity vector, sort behavior, and the ack model are §3; severity choreography is §4.

### 1.4 The Working Rail / overlay-stack drawer (right or overlay)
Selecting a bed opens its detail through the **overlay-stack manager** (`ADR-0010-01`): 24 h score-trend chart (`PER-CARLOS-03`/`PER-RAFAEL-02`), the bed's active-alert list with the why-panel (`alert-triage.md §4`), vitals/labs with abnormal flags + per-datum staleness, and ack + outcome-documentation actions. No routed page change, no reload. Keyboard/focus model in §10; ladder in §2.3.

---

## 2. Drill-down IA — context switcher, full-depth breadcrumb, disclosure ladder

### 2.1 Context switcher — unit + tenant, with per-unit acuity badges [salvage:B]
Three Radix dropdowns in the header: **empresa (tenant) ▸ estabelecimento ▸ setor (unit)**. Switching a level is **lateral movement** that re-scopes the whole surface (grid + ribbon) in place; it preserves current depth where meaningful (`ADR-0009-01`).

- **Per-unit acuity badge on every option** [salvage:B] — each `setor`/`estabelecimento` option carries the **worst active severity** currently in that scope (color+icon+shape), so a coordinator sees a `critical` on an *unopened* unit before switching into it (`MOT-03`).
- **The badge is not a safe *sole* channel for an off-screen critical** (safety-officer-B/`HAZ-023`/`HAZ-025`). It is (a) actionable — tap-to-jump into that unit — and (b) backstopped by the ribbon's always-visible cross-unit crítico floor (`MF-5`, §7.3) and by the individual per-severity delivery guarantee (§0, `HAZ-025`). No critical ever depends only on someone opening a dropdown.
- **Tenant (empresa) switch re-resolves `brand.*` once, server-side, before paint** — no flash-of-default-orange (`ADR-C-01`, `design-tokens.md §7`). **`clinical.*` never changes with tenant** (`DES-C-01`), so severity meaning is tenant-invariant.
- Units/estabelecimentos the user is not authorized for are **absent** from the switcher and grid (deny-by-default, server-side; the client omission is defense-in-depth only, `ADR-C-05`/`ADR-C-14`).

### 2.2 Full-depth breadcrumb + deep-link reconstruction [salvage:B]
One reusable breadcrumb component in the shell, an ARIA `nav` landmark, **extended to full depth** — `Grupo ▸ Hospital ▸ Setor ▸ Leito ▸ Ocupação` — the exact segments the legacy hand-built Tag trail never reached (`ADR-0009-01`; retires the dead `Breadcrumbs` component, `DES-3-06`). Every segment is a link (lateral/upward jump).

- **Deep-link reconstruction** [salvage:B] — Dr. Rafael's `<5s` critical push (`PER-RAFAEL-01`) deep-links straight to a bed's L3 detail; the shell **reconstructs the full breadcrumb from the deep link**, so his push carries `Estabelecimento ▸ Setor ▸ Leito` as wayfinding while he is en route (`PER-RAFAEL-02`, `MOT-15`). A push becomes an *oriented arrival*, not "run to the app."

### 2.3 The L0–L4 progressive-disclosure ladder [salvage:B], owned by one overlay-stack manager
A single formalized ladder, one manager (`ADR-0010-01`), **max depth 2** (`A11Y-REQ-07`):

| Level | Trigger | Surface | Content |
|---|---|---|---|
| **L0** | land on scope | grid + ribbon | acuity/occupancy at a glance |
| **L1** | — | bed cell | glanceable severity, dominant score + trend arrow, **triggering-parameter chip** [salvage:B], staleness age, dedicated ack (§3) |
| **L2** | hover **or** keyboard focus **or** touch "espiar" affordance | Radix popover peek | read-only latest vitals set + top active alerts; dismissible, hoverable, persistent (`SC 1.4.13`) |
| **L3** | click / Enter | bed drawer | 24 h trends, per-alert why-panel, vitals/labs + abnormal flags, ack + outcome docs |
| **L4** | action in L3 | drawer-in-drawer | clinical form engine, prescrição, balanço hídrico — a 3rd push promotes to a routed view, never a 3-deep trap (`A11Y-REQ-07`) |

**L2 must not be hover-only** (ux-researcher-B `must_fix`; `MOT-15`): hover does not exist on Rafael's phone or the monitor wall, so L2 is reachable by keyboard focus and by an explicit touch "espiar" control. Overlay-stack keyboard/focus semantics are in §10.2.

### 2.4 Filters (compose with sort + pinning)
`Meus pacientes` (Ana), `Minha unidade` (Carlos), `Todas as unidades` (Fernanda), `Acuidade ≥ URG`, `Elegível a RRT` (Rafael).

- **`Meus pacientes` is a *dim-not-navigate* filter** [salvage:A] — it **dims** non-assigned beds on the *same* surface (zero navigation) so Ana's 4–5 beds stand out without leaving the command center (`PER-ANA` load). Dimming reduces opacity/saturation but **never** removes a bed from the accessibility tree, and a dimmed bed that escalates to `urgent`/`critical` re-surfaces to full salience (safety over focus).

---

## 3. The bed cell — occupancy + acuity anatomy

### 3.1 Cell anatomy (progressive by density, §5)
- **Frame / severity** — the border/glow carries the patient's **highest active severity** (§4.4) using `clinical.severity.<band>.signal-*` (the vivid non-text status color, WCAG non-text ≥3:1, `SC 1.4.11`), backed by the band **icon** (severity glyph) and **shape** cue so severity survives greyscale (`CON-SEED-11`). Elevation via `elevation.*` (ceiling per §5).
- **Occupancy state** — empty/cleaning/reserved/blocked/transfer rendered with a distinct fill + hatch, never confusable with a low-acuity occupied bed (§3.2).
- **Identity** — `Leito NN` (encodes physical location — exactly what Rafael needs en route, `PER-RAFAEL-01`), patient name, age, sex icon.
- **Dominant score + trend arrow** — the driving score (MEWS / NEWS2) in `type.family.mono` tabular figures (the new monospace family, `DES-2-05` fix) with the acuity **trajectory arrow** (↑ rising / → steady / ↓ falling / — indeterminate), governed by §3.3.
- **Triggering-parameter chip** [salvage:B] — the single parameter that pushed the score (`FR 24`, `SpO₂ 88`, `PA 84/50`) with its unit; a **hard L1 element, never hidden behind disclosure** (`PER-ANA-02`/`PER-C-04`, `MOT-06`). **It is read-only** — the act target is separate (§3.5, `MF-6`).
- **Micro-indicadores** (PT-BR verbatim, `DES-3-05`) — noradrenalina · ventilação mecânica · sedação · hemodiálise · LOS — shown in workstation/phone-deep density only.
- **Abnormal-value flags** — vitals/labs breaching reference ranges flagged by *their own* band (`ADR-0014-01`), never a hardcoded literal (`A11Y-GATE-07`).
- **Staleness age badge** — `atualizado há Xs` per cell (§6), the strongest `HAZ-024` treatment on this panel.

### 3.2 Occupancy states — first-class visual layer [salvage:A/B] + the not-evaluated state (MF-2)
Occupancy is a first-class layer, fixing the legacy empty-vs-`NEUTRO` indistinguishability (`DES-5-03`). PT-BR verbatim states:

| State | Encoding | Note |
|---|---|---|
| `vazio` / **Vago** | dashed neutral outline + "Vago" label [salvage:B], distinct fill, no severity glyph | empty is **never** the flat `#212433`-style occupied-NEUTRO border of legacy |
| `reservado` | hatch pattern + reserve glyph | [salvage:A] |
| `higienização` | hatch pattern + turnover glyph | [salvage:A] |
| `bloqueado` | crosshatch + block glyph | out of service |
| `em transferência / alta` | transition glyph | flow management |
| `ocupado` | severity frame per §4 | the acuity-bearing state |
| **`não avaliado — dados ausentes`** (MF-2) | **distinct** neutral-slate fill + a `help-circle`/no-data glyph + dashed `clinical.status.stale` border | **NOT green/normal, NOT empty** |

**The not-evaluated state (`MF-2`/`HAZ-030`) is load-bearing.** An occupied bed whose score **cannot be computed because a required input is missing** must render as its own `não avaliado` state — never as `normal` (a calm green cell would falsely read as "evaluated, stable") and never as `vazio`. Correspondingly, the ribbon acuity distribution counts these in a **separate `não-avaliado` segment** and **excludes them from the `normal` count** (§7.1). `não avaliado` is distinct from `stale`: *stale* = we had a value, it aged out; *não avaliado* = we never had enough to score.

### 3.3 The acuity vector & trajectory arrows — the tested baseline/delta rule (MF-7, MF-8)
The acuity vector = **severity band** (§4) + **trajectory** derived from deltas of the implemented scores MEWS / NEWS2 / qSOFA / SOFA (`VIS-2-01..04`). A wrong or stale-derived arrow is **false reassurance** (`HAZ-031`), so the rule is explicit, tested, and staleness-aware:

- **Baseline / window.** Trajectory of the dominant score = `current` vs. `baseline`, where `baseline` = the score value at `T − W_trend`. `W_trend` default **4 h** (short-recent trend for the glance signal), configurable at C3; the full 24 h curve lives in the L3 sparkline (`PER-CARLOS-03`). Window and δ are a *design* parameter set (not a clinical cutoff), ratified at C2/C3, not invented per cell.
- **Delta + hysteresis.** `Δ = current − baseline`. **rising** if `Δ ≥ δ`; **falling** if `Δ ≤ −δ`; **steady** if `|Δ| < δ`. `δ` is a hysteresis band (default **1 score point**) to prevent flicker/oscillation at the boundary.
- **Tie-break favors safety.** At an exact boundary, resolve toward the **higher-acuity** reading: `rising ≻ steady ≻ falling`. The system must not *under-call* deterioration (the false-reassurance direction of `HAZ-031`).
- **Sparse-sampling → indeterminate, not steady.** If the window holds fewer than 2 valid score computations, trajectory is **indeterminate**: render `—` with `tendência indisponível`, **never a steady arrow** (a steady arrow from one sample is false reassurance).
- **Staleness inheritance / suppression (`MF-7`+`MF-8`/`HAZ-024`).** Staleness is evaluated against each input's `staleness_max_for_alerting` (`amh-freshness.yaml`, §6):
  - If any input backing the **current** score is stale → the arrow is **suppressed to `—`** + the `clinical.status.stale` mark (you cannot assert a direction from a frozen value; `MOT-04`).
  - If only the **baseline** input is stale but current is fresh → the arrow renders with a **visible caveat** (dashed arrow + `base defasada`), never as a confident solid arrow.
  - In all cases the arrow **inherits the stale mark or is suppressed** — a rising/falling arrow computed on stale inputs is never shown unqualified. This is contract-checked alongside §7.2.

### 3.4 Spatial default + acuity-flow opt-in + pinning (MF-1) and flow-sort freeze (MF-3)
- **Spatial is the contractual default for every role** (`MF-1`/`MOT-01`) — beds in physical bed-number order, preserving "leito 7 is leito 7" muscle memory. **Acuity-flow sort** (deteriorating-to-top clustering) is **opt-in per user** and **cannot become a role default until validated with nurses** (their Risk 1; ux-researcher-C `must_fix`). This is a ratification gate, flagged in §16 — no role boots into flow by default.
- **Pinning** [salvage from decision] — assigned beds can be **pinned** (a tap toggle on the cell; **not** a drag, §13/`SC 2.5.7`) so a nurse's 4–5 never migrate out of sightline in any sort mode.
- **Flow-sort freeze (`MF-3`/`HAZ-026`).** In acuity-flow mode, re-sort/migration **freezes** while any pointer is pressing/hovering a cell, while keyboard focus is anywhere in the grid, or while an ack is mid-activation. Pending migrations are queued and applied only after the interaction ends plus a short debounce. Combined with identity-bound ack (§3.5), a re-order can **never** retarget an ack to the wrong bed.
- **Escalation choreography** — a bed crossing **upward into URG or CRIT** lifts one elevation step and (in flow mode) migrates toward the top cluster; downward/steady changes are quiet (color+shape+arrow update, no motion). Motion is token-scaled and reduced-motion-gated (§4.3).

### 3.5 Ack — read target separated from act target (MF-6)
Concept C originally doubled the triggering-parameter chip as the 1-click ack; the panel rejected that (`MF-6`/`MOT-08`): an accidental ack corrupts `PER-ANA-03` click-path telemetry and the `VIS-7.1-03` time-to-action clock.

- **The chip is read-only** (§3.1). The ack is a **dedicated `Reconhecer` affordance** on the cell (and in L3), a distinct control sized **≥44×44 px** (`A11Y-REQ-21`/`SC 2.5.5`). One tap = ack (`PER-ANA-03`/`PER-C-05`, 1 click preserved), no confirm dialog.
- **Inline undo** — ack raises a 5 s `Desfazer` snackbar as defense-in-depth against a mis-tap, so "keep 1-click but with an inline undo" is satisfied without a second required click.
- **Identity-bound (`MF-3`/`HAZ-026`).** The ack payload binds `{bed_id, patient mpi_id, alert_id, alert_definition_version}` captured at **pointer-down / keydown**, not at pointer-up — so even a race with a re-sort acknowledges the intended bed or fails closed, never a neighbor.
- Ack is an optimistic patch reconciled against the authoritative record over the one channel (`ADR-C-12`, §8); it moves `raised → acknowledged` and writes the audit row per `alert-triage.md §2.2`. This surface owns the *affordance*; the lifecycle machinery is not duplicated here.

---

## 4. Severity choreography — `clinical.*` tokens only, color + icon + shape

All severity encoding on this surface uses **`clinical.severity.*`** (and the additive **`clinical.status.*`**); **never** `brand.*`, **never** `semantic.feedback.*`, **never** a hardcoded literal (`A11Y-GATE-07`; forecloses both legacy bugs — the hardcoded amber toast and the literal `'VERMELHO'` panel, `DES-5-02`/`ADR-C-09`).

### 4.1 The four-band scale (from `severity-model.yaml` + `design-tokens.md §6`)

| Band | PT-BR (statusTrilha, verbatim) | Color family | Icon | Shape | Action SLA | Delivery tier |
|---|---|---|---|---|---|---|
| `normal` | **NEUTRO** | green | `check-circle` | circle | review < 6h | 4 (advisory, no push) |
| `watch` | **AMARELO** | amber | `eye` | rounded-square | < 2h (`CAT-C-04`) | 3 |
| `urgent` | **LARANJA** | orange | `exclamation` | triangle | < 30min (`CAT-C-03`) | 2 (mobile push) |
| `critical` | **VERMELHO** | red | `alert-octagon` | octagon | < 5min (`CAT-C-02`) | 1 (interruptive, never rate-limited) |

Exact hex per role (`on-surface`, `signal`, `fill`/`on-fill`, `wash`) and computed contrast are in `design-tokens.md §6.2` — `critical` clears AAA 7:1 for its text-bearing roles (`A11Y-REQ-01`/`SC 1.4.6`); `signal` preserves the vivid legacy `VERMELHO.ballColor` hue for the non-text glow. Cells consume the tokens via `semantic.alert.*` aliases; the density function never re-picks a literal. The `watch↔critical` pair collapses to ΔE 3.9 under deuteranopia (`A11Y-FINDING-01`), which is *why* icon+shape are load-bearing here, not decorative — they must stay distinct at the smallest chip size (`A11Y-GATE-06`).

### 4.2 `clinical.status.*` — additive, never masking (supersedes legacy ASSISTIDO override)
Legacy `ASSISTIDO` was a blue **override** that could *replace* — and thus visually mask — a true severity. It is **retired as an override** and re-modeled as an **additive** badge (`design-tokens.md §6.3/§6.5`):

- **`clinical.status.attended`** — blue `#4C9FE8` dot + `person-check`, an **additive corner badge** meaning "a clinician is engaged." Rendered **alongside** the true severity color+icon+shape, **never replacing it** — a `critical` under response still reads `critical` (closes the patient-safety masking the legacy override carried).
- **`clinical.status.stale`** — gray `#8A8F99` dot + `clock-alert` + dashed border modifier. Additive — dims confidence, **never silently downgrades** a displayed severity (§6, `MF-7`/`MF-8`).

### 4.3 Motion / attention economy [salvage:A] + reduced-motion
- **Only unattended criticals (and urgents) animate** [salvage:A] — a `critical`/`urgent` bed with **no** `attended` badge carries motion (an escalation lift/sweep) until acknowledged; on ack the motion stills and the `attended` badge is added **additively** (the severity color remains, §4.2). This is the panel's best attention-budget rule — the wall shows *"severity no one is holding"* (`HAZ-023`, `MOT-05`/`MOT-18`). Adapted from Concept A's "ASSISTIDO desaturation" to the additive-badge model so quieting never masks severity.
- **Sub-URG drift is quiet** — a `watch`/`normal` band change updates color+shape+arrow with **no motion, no toast** (only PPV-budgeted, deduped, suppressed alerts drive chips and motion; `HAZ-023`, `VIS-7.1-04` ≤ 10 %). This prevents the Christmas-tree re-creation of legacy noise.
- **Reduced motion / seizure safety.** All motion uses `motion.duration.*`/`motion.easing.*`, GPU transform/opacity only. Under `prefers-reduced-motion: reduce`, every non-essential transition collapses to `motion.duration.instant` and escalation becomes an **instant** color+icon+shape+arrow change with a static "NOVO" badge (`A11Y-REQ-14`). **Hard ban:** nothing flashes faster than 3 Hz under any preference (`A11Y-REQ-13`/`SC 2.3.1`). Live tiles never auto-scroll the viewport or reflow focus (`A11Y-REQ-15`, §8).

### 4.4 Aggregation — max-severity-wins
A cell's displayed severity = **MAX** of the patient's component severities, **never last-writer-wins** — a `VERMELHO` evaluated earlier is never overwritten by a later `AMARELO`/`LARANJA` (`severity-model.yaml` aggregation; the P0-10 downgrade defect, `CON-0182`). Multiple alerts collapse to the single worst glyph + a `+N` count badge (density without noise); the full list is at L2/L3.

---

## 5. Three density modes via container queries (monitor-wall / workstation / phone)

One named breakpoint set (`design-tokens.md §5`), shared verbatim by CSS `@container` queries and any JS density hint — retiring the legacy three-strategy mess (`useWindowSize()`+`collapseRule`, forked `GridView`/`MobileView`, two drifted bucket chains; `DES-2-08`/`DES-4-05`). Density resolves by **container query against the grid shell's width** (`container-type: inline-size`), never `window.innerWidth`.

**Column count is a continuous formula, not a bucket if-chain** — this is what makes the `(2400,2800]px` dead-band structurally impossible (`ADR-C-07`):

```
columns(containerWidthPx) = clamp(4, floor(containerWidthPx / 320), 12)
```

Defined once, unit-tested across the full width domain (0 → ∞), consumed by both this grid and the dashboard tile grid (`DES-7-02`).

| Mode (`@container`) | Range | Intent / persona | Cell content preset | Ribbon | Motion | Elevation ceiling |
|---|---|---|---|---|---|---|
| **monitor-wall** | ≥ 1920px | wall glance across the room; Fernanda / night watch (`MOT-18`) | severity (color+icon+shape) · `Leito` · dominant score · trend arrow · staleness age | prominent, expanded | escalation flash only | `elevation.sm` — flatten for paint budget (`§4.1`) |
| **workstation** | 768–1919px | default working density; Carlos + Ana at a station | + triggering-parameter chip · top-2 micro-indicadores · abnormal flags | standard | full acuity-flow choreography | `elevation.md` |
| **phone** | ≤ 767px | Rafael en route; Ana single-bed deep; single column | + inline 24 h sparkline · active-alert preview · dedicated ack | collapsed to 1-line floor (`MF-5`) | full, plus inline expand | `elevation.sm` |

A secondary, orthogonal **content-density preference** (`enxuto ↔ rico`) lets a user shift how much each cell shows *within* a structural mode (e.g. a workstation user watching "my beds" can request the rich preset; a wall can be forced lean) — density is a token-driven preference, **not a forked render tree** (`DES-C-04`). Final pixel boundaries are provisional pending real ICU hardware validation (`ADR-0011` open question, §16).

---

## 6. Staleness on every datum (MOT-04, HAZ-024) [salvage:A]

Staleness is a first-class visual state at three scopes, all measured on the **clinical timestamp** (`vital_sign.recorded_at` / lab `collected_at`), **not** `ingested_at` (`DM-C-08`/`CON-0026`):

1. **Surface (freshness pill)** [salvage:A] — `ao vivo · reconectando · dados defasados (há Xs)` in the header, the single shared staleness truth for the channel (`MOT-04`, §8).
2. **Per-cell age badge** — `atualizado há Xs` on every cell — the strongest `HAZ-024` treatment; a bed with 6 h-old vitals can never look "stable" (`MOT-01`/`MOT-18` deadliest failure: a stalled board that looks normal).
3. **Per-datum** — every vital/lab/score value carries its own `clinical.status.stale` mark (dashed/gray + age) when past **its source's** `staleness_max_for_alerting`, so a fresh cell can still flag a stale lactate.

Per-source thresholds (from `amh-freshness.yaml`) that drive the per-datum mark and the §3.3 trajectory suppression:

| Source | `staleness_max` | Feeds |
|---|---|---|
| `vitals_operational` (MLLP NRT) | **5 min** | MEWS/NEWS2/qSOFA, respiratory, hemodynamic |
| `vitals_gold` (batch) | 30 min | analytical/replay |
| `blood_gas_respiratory` | 1 h ABG / 5 min SpO₂·FiO₂ | respiratory |
| `hemodynamic_monitor` | 5 min monitor / 2 h lactate | hemodynamic |
| `labs_electrolytes` (K⁺/Na⁺) | 1 h | electrolytes |
| `labs_sepsis` (lactate/PCT) | 2 h | sepsis |
| `labs_renal` (creatinine) | 12 h | AKI |
| `medication_events` | 6 h | infusions, interactions |
| `delirium_assessments` (RASS/CAM-ICU) | 12 h | delirium |
| `mpi_demographics` | 24 h (advisory, **never** a scoring input) | identity |

Beyond `staleness_max`, new threshold-cross alerts on that source are suppressed upstream (frozen-value guard, `amh-freshness.yaml` fallback) — the surface renders the last value **badged stale**, never silently as current, and never auto-resolves an open CRIT on a stale panel.

---

## 7. Coordinator analytics — the woven ribbon (PER-FERNANDA-01/02/03)

### 7.1 The ribbon IS the live occupancy/acuity dashboard (PER-FERNANDA-01)
Per selected scope (a unit, or `Todas as unidades` across adult / coronary / neonatal via the switcher), always-on, no context switch (`MOT-03`):

- **Occupancy meter** — segmented bar `ocupado / vazio / higienização / reservado / bloqueado` with numeric fill (`26/30`) and capacity headroom — true capacity data, not perception, to justify bed investment (`PER-FERNANDA` needs). Replaces the legacy operational-only gauge (`DES-5-05`).
- **Acuity distribution** [salvage:A] — a stacked severity bar `⬢ crítico N · ▲ urgente N · ▢ atenção N · ● normal N` on the `clinical.*` scale, each segment labeled with a **number + shape/pattern, not color alone** (legible on the wall and to CVD users, `SC 1.4.1`). It doubles as an always-on **alarm-fatigue pressure gauge** for the coordinator. **Crucially, a first-class `⌀ não-avaliado N` segment** (`MF-2`/`HAZ-030`): not-evaluated beds are counted separately and **never fold into `normal`**, so an absent-data unit can never read as "all stable."
- **Response-time SLA gauge** — live mean time-to-action against the ≤ 15 min target (`VIS-7.1-03`) with an at-risk count — Fernanda's quality indicator surfaced continuously, not only in the weekly export.

### 7.2 Same feed, no re-derivation — contract-tested (MF-4, ADR-C-13)
The occupancy meter, acuity counts, and SLA gauge are **fields in the same authoritative WebSocket payload** that renders the cells — the client performs **no independent re-derivation** of severity, counts, or SLA. A **contract test** asserts, for any single snapshot, that `ribbon.acuity_counts == Σ(cell severities)` and `ribbon.sla == server SLA field` — so the grid and the KPIs **cannot disagree** (`ADR-C-13`, closing the legacy bell-vs-grid divergence `DES-6-02`). The §3.3 trajectory staleness inheritance is checked in the same contract suite. This is the divergence Concept C is built to make impossible.

### 7.3 Collapse preserves the crítico floor (MF-5) [salvage:A]
Bedside roles (nurse, intensivist) boot with the ribbon **collapsed to a 1-line summary**; but collapse **never removes the crítico/urgente count or cross-unit awareness** (`MF-5`/`MOT-03`/`MOT-05`). The collapsed line always retains: the current scope's `crítico N · urgente N` and a **cross-unit worst-severity indicator** (so a `critical` on another unit stays visible even when the ribbon is down). This is the always-on acuity floor [salvage:A] — the ribbon dims, it does not blind.

### 7.4 Analytics drill → KPI report (PER-FERNANDA-02) + export (PER-FERNANDA-03)
Clicking any ribbon widget opens a woven **analytics drawer** (response-time distribution, occupancy history, acuity trend) — analytics stay *inside* the grid surface, the stance's signature.

- **Weekly KPI report (`PER-FERNANDA-02`, `MOT-20`)** — the live SLA gauge is the real-time face of the same metrics engine that renders the weekly report. The drawer is the *entry point*; the report/PPV/alarm-fatigue analytics are **rendered by `alert-triage.md §5–§6`** and the report reconciles **exactly** with this live dashboard for the same period (`MOT-20` failure mode: report and dashboard disagreeing → one engine, two renderings). Threshold-tuning governance is `admin-config.md`.
- **Export (`PER-FERNANDA-03`, `MOT-20`)** — every widget and the report export to hospital quality tools, LGPD-minimized (`PER-C-08`/`VIS-C-05`).

Ownership boundary: this screen **owns** `PER-FERNANDA-01` (the live woven dashboard) and the drill entry points; it **does not** re-implement the analytics/report/governance surfaces (`alert-triage.md`, `admin-config.md`).

---

## 8. Realtime update semantics — one WebSocket channel

- **One channel** (`ADR-0017-01`/`DES-C-05`/`ADR-C-13`) feeds the grid, ribbon, presence, and bell with shared reconnect/backoff. The board **never polls**. Payloads **patch the affected cell(s)/ribbon fields in place** — only changed cells re-render (§11).
- **Connection states, loud never silent** — `ao vivo` / `reconectando` (shared backoff, `ADR-C-12`) / `dados defasados` (last-known state stays visible, dimmed, timestamped) / `offline`. A dropped connection is made loud via the freshness pill + per-cell age (§6) — the deliberate inverse of the legacy silent poll where a red alert could lag the bell by `tempo_atualizacao` seconds (`DES-6-02`, `MOT-01`/`MOT-05`/`MOT-18`).
- **Optimistic ack reconciliation** — the §3.5 ack applies an optimistic patch, reconciled against the authoritative record over the same channel (`ADR-C-12`); on conflict the authoritative state wins and the undo snackbar reflects it.
- **Critical is always on top** — an interruptive `critical` surface renders at `z.critical-alert` (9000), above every other layer including modals, because `critical` is never suppressed (`design-tokens.md §3.3`, `severity-model.yaml`).
- **Screen-reader coalescing** — live updates use one `aria-live` container **per severity tier** (four total), coalesced at ~1 announcement / 2 s to prevent stomping (`A11Y-REQ-17`), e.g. *"3 novos alertas críticos. Último: Leito 12, SpO₂ 82%, em queda."* The **visual** update is never delayed by narration batching (feeds the `<30s` / RRT `<5s` budgets, `VIS-C-09`/`PER-C-06`).
- **The channel is not the delivery guarantee (`HAZ-025`).** Losing the channel degrades the *ambient* surface loudly; it never suppresses the individual per-severity push/page/escalation, which run independently (§0).

---

## 9. States (exhaustive)

- **Loading** — content-shaped skeleton grid (cell-shaped placeholders), never a full-viewport blocking spinner (`ADR-0016-01`/`DES-5-07`); shell + breadcrumb render immediately from cached context; ribbon shows skeleton meters.
- **Empty scope** — a unit with no beds → explicit empty-state card with a capacity note; empty (`vazio`/Vago) cells always visually distinct from occupied (§3.2).
- **Bed states** — `vazio`/Vago · `reservado` · `higienização` · `bloqueado` · `em transferência/alta` · occupied-`normal` · occupied-`watch` · occupied-`urgent` · occupied-`critical` · **`não avaliado — dados ausentes`** (`MF-2`) · per-datum/`stale`.
- **Alert states on a cell** — none · single · multiple (worst + `+N`) · acknowledged (adds `attended` badge, motion stills) · suppressed (muted `×N` recurrence dot) · escalated (RRT paged). Lifecycle machinery: `alert-triage.md §2`.
- **Realtime states (whole surface)** — `ao vivo` · `reconectando` · `dados defasados` · `offline` (§8).
- **Trajectory states** — rising / steady / falling / **indeterminate `—`** / **stale-caveated** (§3.3).
- **Error / permission-denied scope** — classified error (validation / permission / server) mapped to visual weight; **no error class defaults to a blocking `Modal.error`** (`A11Y-REQ-19`, retires the legacy `handleApiError`); permission-denied re-routes per deny-by-default (`ADR-C-05`/`ADR-C-11`). A single cell that fails to hydrate shows a per-cell inline error + retry, never a screen-wide modal — the grid degrades gracefully.

---

## 10. Keyboard & focus behavior

### 10.1 The grid is a roving-tabindex 2-D composite
- One Tab stop enters the grid; **arrow keys** move cell-to-cell, `Home`/`End` to row ends, `PageUp`/`PageDown` by viewport, `Enter` opens L3, the cell's `Reconhecer` and pin toggle are reachable within the focused cell (`SC 2.1.1`). A visible `focus-visible` ring on every operable control in both themes and all densities (`SC 2.4.7`), never obscured by the sticky header/ribbon/toast (`SC 2.4.11`/`A11Y-REQ-12`).
- **Flow-sort freezes while focus is in the grid** (`MF-3`, §3.4) so arrow-key navigation is never disrupted by a re-order under the caret.
- **Target sizes** — 24×24 floor platform-wide (`A11Y-REQ-20`/`SC 2.5.8`); **44×44** for `Reconhecer` and any bedside/mobile primary action (`A11Y-REQ-21`/`SC 2.5.5`). Monitor-wall (pointer-at-workstation, glanceable) may sit nearer the 24px floor; workstation/phone default to 44px for primary actions.

### 10.2 Overlay-stack manager (L3/L4)
Per `accessibility-standard.md §3`: `Escape` closes **only the topmost** level (`A11Y-REQ-08`); hardware/browser **back matches Esc** (`A11Y-REQ-09`); each level is `role="dialog"` (or `alertdialog` for a destructive confirm) + `aria-modal="true"` + `aria-labelledby`, focus-trapped, background `inert` (`A11Y-REQ-10`); **initial focus** lands on the first meaningful control/heading, never the × or a destructive default (`A11Y-REQ-11`); **on close, focus returns exactly to the trigger cell/chip/button** — critical in a dense grid where losing your place means re-tabbing dozens of cells; **max depth 2** (`A11Y-REQ-07`), a 3rd push promotes to a routed view.

### 10.3 L2 peek — keyboard + touch equivalents
The L2 read-only peek opens on hover **and** on keyboard focus **and** via an explicit touch "espiar" control (`MOT-15` — hover absent on phone/wall); the popover is dismissible without moving the pointer, hoverable, and persistent until dismissed/invalidated (`SC 1.4.13`).

### 10.4 Accessible names
Every alert/severity element's accessible name follows severity → parameter+value+trend → location (`A11Y-REQ-18`/`A11Y-GATE-10`), e.g. *"Crítico. Frequência cardíaca 142, subindo. Leito 07, paciente J.S."* — never *"Alerta. Leito 07."* Every custom primitive exposes name/role/state (`SC 4.1.2`) — no bare `<div onClick>`.

---

## 11. Performance budget — 90 beds at 60 fps

Target scope: Fernanda's full census (30 adult + coronary + neonatal, up to **90 beds** in `Todas as unidades`) at **60 fps** (16.67 ms frame budget).

- **Elevation budget** — at monitor-wall density (dozens of simultaneous cells) tiles default to `elevation.sm` only; `elevation.md/lg` are reserved for singly-focused surfaces (drawer, the one expanded cell) — the density-tiered mitigation for the neumorphic paint cost the audit flagged (`ADR-0007-01 §4.1`). `prefers-contrast: more` → `elevation.flat`.
- **Compositor-only motion** — all animation is GPU `transform`/`opacity`; no layout/paint on animation frames. Escalation flash only at monitor-wall; reduced-motion and monitor-wall both drop motion to `motion.duration.instant`.
- **Diffed patch, windowed render** — WebSocket payloads patch only changed cells (§8); off-screen cells are virtualized/windowed so DOM node count stays bounded regardless of census. Container query resolves density once per container resize, not per scroll frame.
- **Skeleton-first paint** (`ADR-0016-01`) — content-shaped skeleton avoids a blocking first paint; steady-state per-cell patch target < 16 ms.
- **Announcement debounce** — the ~1/2 s per-tier `aria-live` coalescing (§8) keeps screen-reader narration intelligible under multi-domain fan-out without touching the visual latency budget.
- **Benchmark gate** — paint cost at 90 cells × `elevation.sm` + escalation flash is benchmarked on real ICU wall hardware and a low-spec ICU PC **before ship** (`ADR-0007-01` open note; re-benchmark at C3, §16).

---

## 12. How each persona succeeds

- **Dr. Carlos (intensivista).** Opt-in acuity-flow lifts deteriorating patients the moment their MEWS/NEWS2 trajectory turns (§3.3), score live in `<30s` over the one channel (`PER-C-01`/`VIS-C-09`); only PPV-budgeted, deduped chips render, supporting `<3 FP/patient-day` (`PER-C-02`/`VIS-7.1-02`); L3 gives his 24 h trend (`PER-CARLOS-03`). `MOT-01`/`MOT-05`/`MOT-07`.
- **Enf. Ana (enfermeira).** MEWS auto-rendered per cell — zero manual calculation (`PER-ANA-01`/`PER-C-03`, replacing 20 min/shift); the read-only chip names the exact triggering parameter (`PER-ANA-02`/`PER-C-04`); the dedicated `Reconhecer` is her 1-click ack with undo (`PER-ANA-03`/`MF-6`); `Meus pacientes` dim-not-navigate + pin keep her 4–5 fixed in sightline [salvage:A]. `MOT-04`/`MOT-06`/`MOT-08`.
- **Dra. Fernanda (coordenadora).** The ribbon **is** her always-on occupancy/acuity dashboard across adult/coronary/neonatal (`PER-FERNANDA-01`), same feed as the cells (`MF-4`), with the live SLA gauge feeding the weekly report (`PER-FERNANDA-02`) and export (`PER-FERNANDA-03`) — no context switch. `MOT-03`/`MOT-20`.
- **Dr. Rafael (RRT).** Same cell contract + one channel push score+trend+location to his phone in `<5s` (bed id encodes location, `PER-RAFAEL-01`/`PER-C-06`); the deep link reconstructs the full breadcrumb as wayfinding [salvage:B] (`PER-RAFAEL-02`/`MOT-15`); phone mode is the same density function bucket (no fork); L3 gives en-route vitals + trend with per-datum staleness, and outcome docs complete in `<1 min` (`PER-RAFAEL-03`/`PER-C-07`, `alert-triage.md §3`). `MOT-14`/`MOT-16`.

---

## 13. Accessibility gate (required by `accessibility-standard.md §8`)

- [x] **A11Y-GATE-01** — All text/label meets `SC 1.4.3` (4.5:1 / large 3:1); every `critical`-scoped value/ack meets `SC 1.4.6` (7:1) per `A11Y-REQ-01` (`design-tokens.md §6.2`; §4.1).
- [x] **A11Y-GATE-02** — Icons, severity borders/glow, chart marks, focus rings ≥ 3:1 non-text in both themes (`signal-*` roles; §4.1).
- [x] **A11Y-GATE-03** — No severity/status/occupancy/resolution state encoded by color alone; each carries a distinct icon **and** shape/outline (§3.2/§4.1, `A11Y-REQ-02`).
- [x] **A11Y-GATE-04** — The severity palette is the C2-validated set run through the §2.2 CVD/ΔE method (`design-tokens.md §6`); this screen introduces no new severity hex.
- [x] **A11Y-GATE-05** — No animation exceeds 3 Hz (`A11Y-REQ-13`); `prefers-reduced-motion` collapses non-essential motion to instant; the trend arrow/sparkline (essential motion) always has a static delta/text alternative (§3.3/§4.3).
- [x] **A11Y-GATE-06** — Icon+shape pairs stay distinct at the smallest chip size (monitor-wall glyphs verified), protecting the `watch↔critical` LOW-RISK pair (§4.1).
- [x] **A11Y-GATE-07** — Every severity-colored/iconed/announced element derives encoding from the live current severity value — no hardcoded literal (§4, closes both legacy bugs).
- [x] **A11Y-GATE-08** — Overlay stack: Esc closes topmost only, back matches Esc, `role=dialog`/`alertdialog`+`aria-modal`+focus trap, stated initial-focus + exact restore, depth ≤ 2 (§10.2).
- [x] **A11Y-GATE-09** — Live regions named per the §5.1 severity table, one container per tier, with §8 coalescing (`A11Y-REQ-16/17`).
- [x] **A11Y-GATE-10** — Alert accessible names follow severity → parameter+value+trend → location (§10.4).
- [x] **A11Y-GATE-11** — 24×24 floor platform-wide; 44×44 for `Reconhecer`/bedside/mobile primary actions (§10.1).
- [x] **A11Y-GATE-12** — No pure `#FFFFFF`/`#000000` large surface (`A11Y-REQ-23`); neumorphic cells carrying clinical text pass the both-theme contrast check and have a `prefers-contrast: more` flat fallback (§5/§11, `A11Y-REQ-24`).
- [x] **A11Y-GATE-13** — **No drag interactions on this screen.** Pinning and flow/spatial are tap/toggle controls; the §9 open reconciliation pre-registers that any future bed-reassignment drag ships a single-pointer alternative (`SC 2.5.7`).
- [x] **A11Y-GATE-14** — No authentication/e-signature step on this surface (handled in auth/e-sign flows, `accessibility-standard §7`).
- [x] **A11Y-GATE-15** — Every custom primitive (cell, severity chip, trend arrow, occupancy glyph, ribbon segment, `Reconhecer`) has a stated name/role/state (§10.4, `SC 4.1.2`).
- [x] **A11Y-GATE-16** — The clinical form engine is used only at L4; it does not re-ask information captured earlier in the same flow (`SC 3.3.7`) — binds `form-engine-designer`.

---

## 14. must_fix traceability (all 8 → where addressed)

| # | must_fix (from `decision.yaml`) | Hazard / moment | Where addressed |
|---|---|---|---|
| **MF-1** | Contractually keep **Spatial as default with pinning**; validate Acuity-flow reordering with nurses before it can be a role default | Risk 1 / `MOT-01` | **§3.4** — Spatial is the contractual per-role default; acuity-flow is opt-in and gated on nurse validation (§16); pinning is a tap toggle. |
| **MF-2** | Distinguish **'not evaluated — data missing'** from 'evaluated, no alert' on the cell; ribbon acuity distribution must exclude not-evaluated from 'normal' | `HAZ-030` | **§3.2** (distinct `não avaliado` cell state, not green/not empty) + **§7.1** (separate `não-avaliado` ribbon segment, excluded from `normal`). |
| **MF-3** | **Flow-sort migration must freeze** under an in-progress pointer/keyboard action so the ack can never retarget to the wrong bed | `HAZ-026` masking | **§3.4** (layout freeze during interaction) + **§3.5** (identity-bound ack captured at pointer-/key-down) + **§10.1** (freeze while grid focused). |
| **MF-4** | Ribbon SLA gauge and cell states from the **same authoritative feed, no client re-derivation**; verify by contract test | `ADR-C-13` | **§7.2** — single WS payload, no re-derivation, contract test asserts ribbon == Σ cells and SLA == server field. |
| **MF-5** | **Ribbon collapse must never remove the crítico count / cross-unit awareness** — collapsed ribbon still shows the acuity floor | `MOT-03`/`MOT-05` | **§7.3** (collapsed 1-line floor retains crítico/urgente + cross-unit worst) + **§1.2**; backstops the switcher badge (§2.1). |
| **MF-6** | **Separate the read target from the act target** — chip-as-ack invites accidental acks; keep 1-click on a dedicated affordance or with inline undo | `MOT-08` | **§3.5** — chip is read-only; dedicated `Reconhecer` (44×44) is the 1-click ack **plus** a 5 s inline `Desfazer`. |
| **MF-7** | Trajectory arrows need an **explicit tested baseline/delta rule** (window, sparse-sampling, tie-break); vectors past `staleness_max` inherit the stale mark or are suppressed | `HAZ-031`/`HAZ-024` | **§3.3** — W_trend/δ/hysteresis, safety tie-break (rising≻steady≻falling), sparse→indeterminate `—`, staleness inheritance/suppression; contract-checked §7.2. |
| **MF-8** | Trajectory arrows **suppress or visibly caveat when computed on stale inputs** | `MOT-04` | **§3.3** (current-input stale → suppress to `—`+stale; baseline stale → dashed `base defasada` caveat) reinforced by **§6** per-datum staleness. |

**must_fix addressed: 8 / 8.**

---

## 15. Salvage graft register

| Grafted idea | Origin | Where grafted (and any adaptation) |
|---|---|---|
| `Meus pacientes` **dim-not-navigate** filter (zero navigation for Ana's 4–5) | **[salvage:A]** | §2.4 — dims non-assigned on the same surface; escalations re-surface to full salience. |
| **Only-unattended-criticals-animate** attention economy ("severity no one is holding", `HAZ-023`) | **[salvage:A]** | §4.3 — adapted: quieting is via the **additive** `attended` badge, not the retired ASSISTIDO override, so severity is never masked. |
| **Acuity summary strip** as an always-on alarm-fatigue pressure gauge | **[salvage:A]** | §7.1 acuity distribution + §7.3 collapsed floor. |
| Distinct **`vazio`/`reservado`/`higienização`** bed states (empty never confusable with NEUTRO occupied) | **[salvage:A]** | §3.2 occupancy states. |
| Explicit **'Vago'** dashed treatment distinct from occupied-NEUTRO | **[salvage:B]** | §3.2 (`vazio`/Vago row). |
| **Realtime freshness pill** (`ao vivo`/`reconectando`/`dados defasados`) as the single shared staleness truth | **[salvage:A]** | §1.1 header + §6.1 + §8 connection states. |
| **Full-depth breadcrumb reconstruction** from a deep-linked push (RRT wayfinding) | **[salvage:B]** | §2.2 — reconstructs `Estab. ▸ Setor ▸ Leito` for Rafael (`PER-RAFAEL-02`/`MOT-15`). |
| **Per-unit acuity badges** on the context switcher (worst severity before entering a unit) | **[salvage:B]** | §2.1 — actionable, backstopped so it is never the sole channel for an off-screen critical. |
| **Triggering parameter as a hard L1 tile element** (never behind disclosure) | **[salvage:B]** | §3.1 chip (`PER-ANA-02`/`MOT-06`) — but read-only, act target separated (`MF-6`). |
| **Formalized L0–L4 progressive-disclosure ladder** owned by one overlay-stack manager | **[salvage:B]** | §2.3 + §10.2. |

---

## 16. Constraints owned/discharged + open reconciliations

| Item | Barrier | Where |
|---|---|---|
| `PER-FERNANDA-01` live occupancy/acuity dashboard (woven ribbon) | C2/C3 | §1.2, §7.1–7.3 |
| `PER-FERNANDA-02`/`03` KPI report + export (entry points; rendered by `alert-triage.md`/`admin-config.md`) | C3 | §7.4 |
| `PER-ANA-02`/`PER-C-04` triggering parameter exposed on tile · `PER-ANA-03`/`PER-C-05` 1-click ack | C2 | §3.1, §3.5 |
| `PER-CARLOS-03` 24 h trend · `PER-C-01`/`VIS-C-09` score `<30s` | C3 | §1.4, §8, §12 |
| `PER-RAFAEL-01/02` push+wayfinding · `PER-C-06` `<5s` | C3 | §2.2, §8, §12 |
| `CON-SEED-11` triple-encoded severity · `CON-0041`/`DES-C-01` clinical/brand decoupling | C2 | §4 |
| `ADR-0011-01`/`ADR-C-07` one density function, no dead-band · container queries | C2 | §5 |
| `ADR-0017-01`/`ADR-C-13`/`DES-C-05` one channel, no polling, no divergence | C3 | §7.2, §8 |
| `ADR-0010-01` overlay-stack manager · `ADR-0009-01` IA/breadcrumb/no side nav | C2 | §2.2, §2.3, §10.2 |
| `ADR-0013-01`/`ADR-0014-01` severity + abnormal-value flagging | C2/C3 | §3.1, §4 |
| `HAZ-024/025/026/030/031` treatments | C3 (safety) | §3.2–3.5, §6, §7.2, §8 |

**Open reconciliations (routed, not resolved):**
- **Acuity-flow as a role default is ratification-blocked** — it may not become any role's boot default until validated with nurses (`MF-1`, ux-researcher-C). Spatial ships as the default; flow ships opt-in.
- **`W_trend` / `δ` / hysteresis values** (§3.3) are design parameters ratified at C2/C3 with clinical input, then locked into the trajectory contract test (§7.2) — not invented per cell.
- **Final `clinical.*` severity hues** await clinical sign-off at C2 (`ADR-0013` open question); triple encoding means meaning survives any re-hue, but the palette must be re-run through the `accessibility-standard §2.2` CVD/ΔE method before ship.
- **Density pixel boundaries** (§5) are provisional pending real ICU wall/workstation hardware validation (`ADR-0011`); the **90-bed × elevation.sm paint-cost benchmark** (§11) must pass on that hardware before locking at C3.
- **`não avaliado` / `normal` persistence** — surfacing not-evaluated and `normal`-band advisories as first-class auditable rows depends on the `alert.severity` enum reconciliation with the data-architect (`severity-model.yaml`; `alert-triage.md §7`).
