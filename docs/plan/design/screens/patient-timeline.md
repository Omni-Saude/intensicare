# Screen Spec — Patient Timeline (the core clinical object)

**Owner:** patient-timeline-designer · **Status:** draft for reconciliation barriers **C2** (severity + decomposition UX) and **C3** (score latency + partial-score/staleness safety) · **Authority precedence:** ADR-001 ≻ vision ≻ directive ≻ audit (CONTRACTS §5).

This spec defines the **single-patient timeline**: the surface a clinician opens for one occupation (leito → ocupação) to answer *"what is this patient's state, what changed, and why."* The winning model is **concept C — score-decomposition-first** (`docs/plan/_work/panels/timeline-model/decision.yaml`, winner `c`, 4.15 over B 4.10): the hero object is the **score-component table** (the CFM-transparent audit spine), and the 24 h trend, the what-changed deltas, the correlation explanations, and the SBAR handoff are all **views derived from that decomposition**. Concept B (event-stream what-changed) was the closest runner-up and its strongest mechanisms are **grafted here** — every graft is marked `[salvage:B]` (or `[salvage:A]` from the trend-canvas concept). The eight panel `must_fix` items are addressed inline and re-listed with traceability in §16.

This screen **invents no clinical content**. Every point mapping, band, and cutoff lives in the versioned scorer service and the domain docs (`clinical/domains/early-warning-scores.md`, `clinical/domains/sepsis.md`, `clinical/domains/correlation-engine.md`); the units registry and `_work/platform/amh-freshness.yaml` own staleness; `_work/platform/severity-model.yaml` owns severity. Every claim cites a source: a ledger/constraint id (`CON-*`, `ADR-*`, `SYS-C-*`), a brief fact (`VIS-*`, `PER-*`, `CAT-*`, `DM-*`, `DES-*`), a persona criterion (`PER-C-*`), a user story (`US-*`), a hazard (`HAZ-*`), an invariant (`INV-*`), or a journey moment (`MOT-*`).

Companion surfaces: the **home bed-grid command center** owns the live floor view (`PER-FERNANDA-01`, §14); **alert-triage.md** owns the alert lifecycle, the why-panel, and the RRT desfecho form; **handoff.md** owns the SBAR shift-handoff generated from this timeline's deltas.

---

## 0. Design-system frame (what this screen is built from — fixed, non-negotiable)

- **Dark-first "quiet ICU" default** with a symmetric token-driven light theme (`ADR-0002-01`/`ADR-0003`); no full-reload light toggle. Neumorphic elevation is a governed `elevation.*` token pair with WCAG contrast verified in both themes and a flat-shadow `prefers-contrast` fallback (`ADR-0007-01`/`CON-0037`/`ADR-C-04`).
- **Formal token scales are the single source of truth** (`ADR-0005/0006`, `DES-C-03`), including the **monospace family for tabular clinical values** (`DES-2-05` fix) so a component table's numerals scan-align.
- **Radix headless primitives for generic non-clinical behavior only** (`ADR-0012-01`): `Collapsible`/`Accordion` (chip and row expansion), `Tabs` (score-lane / window switch), `Tooltip`/`HoverCard` (baseline + provenance peek), `Dialog` (SBAR + secondary forms). No second competing primitive (`ADR-C-06`).
- **ONE realtime push channel** (`lib/realtime`, WebSocket + SSE fallback, shared reconnect/backoff, `ADR-0017-01`/`DES-C-05`/`ADR-C-13`). New score chips and stream events **append/patch** over the same channel as the bed grid and the notification bell — the transport is never a second source of truth (`ADR-C-12`). The timeline **never polls**; a stale board that looks live is the deadliest legacy failure (`DES-6-02`, MOT-18).
- **Severity is `clinical.severity.{normal,watch,urgent,critical}`, structurally separate from tenant `brand.*`** (`CON-0041`/`DES-C-01`), and **always triple-encoded — color + icon + shape (+ text)**, never color alone (`CON-SEED-11`/`ADR-0013-01`, WCAG 1.4.1). Encoding is read from `lib/severity` at render time off the **live** value — never a hardcoded literal (forecloses both audited legacy severity bugs, `ADR-C-09`/§2.5 of the accessibility standard). Bands and encodings per `severity-model.yaml`: normal green·check-circle·circle; watch amber·eye·rounded-square; urgent orange·exclamation·triangle; critical red·alert-octagon·octagon.
- **Abnormal-value flagging is a first-class service** (`ReferenceRangeFlag`, §5.3 of component-library; `ADR-0014-01`/`CON-0054`/`DES-C-06`): every value in a decomposition row or a lab chip is flagged against *its own* reference band — the direct fix for the top legacy gap where SpO₂ 60 % and 99 % rendered identically (`DES-5-04`).
- **Route permission is deny-by-default, enforced server-side** ahead of shell render; the API independently authorizes every request (`ADR-C-05`/`ADR-C-14`/`DES-C-08`). The client role-default (which depth boots) is UX only.
- **Components reused (no new primitives invented here):** `ScoreBadge` (§5.2), `VitalsList`/`ReferenceRangeFlag` (§5.3), `TrendChart` (§5.4), `AlertCard`/`AlertDispositionControl` (§5.5), `StalenessBanner` (§5.7), `OverlayStack` (§5.9), `Breadcrumb` (§5.10), `Tabs` (§5.11), `ConnectionStatusIndicator` (§5.13), `SkeletonLoader` (§5.15), `RRTMobileCard`/`OutcomeDocumentationSheet` (§5.16), all from `docs/plan/design/component-library.md`.

---

## 1. Layout — three regions over one time axis

One patient, one timeline, inside the standard app shell (PageContainer successor, `ADR-0008-01`) with the single persistent **full-depth breadcrumb** `Estabelecimento ▸ Setor ▸ Leito ▸ Ocupação` (`ADR-0009-01`, fixing the trail that never reached the deepest legacy screens). Three regions:

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ PATIENT RAIL (sticky)   Leito 12 · A.P. · 67a · ♀ · LOS 4d      NOW STRIP (sticky)          │
│ ⬢ CRÍTICO (worst active) · MicroIndicadores: NAD · VM · sedação  MEWS 6▲ NEWS2 8▲ qSOFA 2 SOFA 9 │
│ [ SBAR ▸handoff.md ]  [ Tendência 24h ▾ ]  [ desfecho ▸ ]        ⟳ ao vivo · vital há 4min   │
│ ── CRITICAL VALUES RAIL (never collapses, §6): ⬢ K⁺ 6.8 mmol/L (há 12min) · ⬢ Lactato 4.2 ── │
├──────────────────────────────┬──────────────────────────────────────┬───────────────────────┤
│ SCORE SPINE (left, time axis)│ DECOMPOSITION PANEL (center, hero)    │ CONTEXT RAIL (right)  │
│ most-recent-at-top, 24h dflt │ selected chip → component table       │ ▸ Correlations        │
│                              │                                       │ ▸ Active alerts       │
│ ▌⬢ 09:14 NEWS2 8 ▲ (v1.0.0) ◄│ NEWS2 8 · NEWS2-v1.0.0 · 07 of 07     │ ▸ What-changed digest │
│ ▌◆ 09:02 MEWS 6 → (v1.0.0)   │ ┌─ component ─ value ─ pts ─ band ─Δ─ idade┐│                │
│ ▌⬢ 08:31 qSOFA 2 ▲ (v1.0.0)  │ │ Freq. resp.  24 rpm  +2  urgent +2  8min ││ ⚠ advisory —      │
│ ── 07:00 início do plantão ──│ │ SpO₂         91 %    +3  crit   +2  8min ││  o médico decide  │
│ ▌○ 06:10 NEWS2 5 ↓ (melhora) │ │ Ar/O₂        O₂     +2  —      →  8min ││  (VIS-C-08)       │
│ ⧗ Sem gasometria há 6h       │ │ PA sist.     118    0   normal  →  8min ││                   │
│ … carregar turno anterior    │ │ Pulso        104    +1  watch   →  8min ││                   │
│                              │ │ Consciência  A(ACVPU)0  normal  →  22min││                   │
│                              │ │ Temperatura  38.4°C  +1  watch  →  40min││                   │
│                              │ └────────────────────────────────────────┘│                   │
│                              │ what-changed: NEWS2 6→8 · SpO₂ 96→91 (+2)  │                   │
└──────────────────────────────┴──────────────────────────────────────┴───────────────────────┘
        ▲ synchronized scrub cursor crosses spine + trend + decomposition [salvage:A]
```

### 1.1 The Score Spine (left — the time axis)
A vertical, most-recent-at-top axis over the **24 h window by default** (`PER-CARLOS-03`/`PER-C-03`; `PER-RAFAEL-02`), scrubbable and extendable (72 h / full-stay via `Tabs` toggle). Parallel **score lanes**: MEWS + NEWS2 as the dominant pair (general deterioration, `VIS-2-01/02`), qSOFA + SOFA as selectable lanes (sepsis triage / organ dysfunction, `VIS-2-03/04`). Each recalculation is a **score chip** (`ScoreBadge`, §5.2), not a plotted point: value in tabular monospace + severity band (color+icon+shape+text) + a **trend arrow** governed by §4.3 + the **algorithm-version** tag (`NEWS2-v1.0.0`, `SOFA-v2.0.0`; `VIS-C-13`). Selecting a chip drives the center panel; scrolling the spine is scrubbing time. A chip appears **< 30 s after its inputs land** over the one channel (`PER-C-01`/`VIS-C-09`, MOT-04). Improvement chips (`melhora`, hollow circle) are shown, quietly — improvement is a change too, and matters at handoff `[salvage:B]`.

Interleaved on the spine as first-class **stream events** `[salvage:B]`: alert fires, human acks, med start/stop/escalations, correlation events (§7), **shift markers** (`── 07:00 início do plantão ──`), and **gap events** — *absence of expected data surfaced as a clinical change* (`⧗ Sem gasometria há 6h`, `Sem RASS há 8h`), the single strongest partial-data mechanism on the panel (`[salvage:B]`, HAZ-030/HAZ-024). Gap-event cadence thresholds derive from each parameter's `staleness_max` in the units registry / `amh-freshness.yaml`, never ad-hoc constants (safety-officer-b must_fix, HAZ-024).

### 1.2 The Decomposition Panel (center — the hero, the stance signature)
Selecting/expanding a chip opens its **component table** (§2, §3): one semantic `<table>` row per score component, each with value, points, reference band, Δ-since-prev, and staleness age. This is the object the whole concept is built to serve and the literal answer to "qual parâmetro disparou?" (`PER-ANA-02`/`PER-C-04`, MOT-06, §8). The panel header states score identity, aggregate value, `algorithm_version`, component-completeness (`07 of 07`), and the one-line **advisory banner** *"apoio à decisão — o médico decide"* (`VIS-C-08`, HAZ-034).

### 1.3 The Context Rail (right)
Three stacked, collapsible `Accordion` cards fed by the same timeline: **Correlations** (§7), **Active alerts** (`AlertCard`, one-click ack → NGS-2, §8), and the **What-changed digest** (§5). Bed selection and secondary forms use the managed `OverlayStack` (§11): Esc/back closes only the topmost level, per-level focus trap, depth ≤ 2 (`ADR-0010-01`, `A11Y-REQ-07/08`).

### 1.4 Progressive-disclosure depths (one density function, no forked trees)
Density is one token-driven, unit-tested function keyed on viewport width **and** explicit user choice, covering the full width domain with no dead-band (`ADR-0011-01`/`ADR-C-07`/`DES-C-04`; closes the legacy `(2400,2800]px` gap). Not a forked render tree — the same component contract at three disclosure levels.

| Depth | Persona / context | Spine | Decomposition | Rail |
|---|---|---|---|---|
| **Collapsed** | Rafael en route on a phone; narrow breakpoint (`RRTMobileCard`, §9) | dominant lane, last 3–4 chips, current band + arrow + critical-values rail | current score's **top-3 contributing rows** + what-changed line | SBAR + active alerts + critical values |
| **Standard** | Ana/Carlos at a station | MEWS+NEWS2 lanes, 24 h chips | full component table + Δ column + staleness + **one-tap 24 h trend** (§2.2) | all three cards |
| **Audit** | Carlos on a critical event; Fernanda's retrospective review | all four lanes + correlation bands | full table + per-component sparklines expanded inline + version line | all cards + correlation drawer |

The decomposition **never disappears** across depths — it only summarizes (top-3 rows) or fully expands (sparklines). The critical-values rail (§6) and the one-tap 24 h trend (§2.2) are present at **every** depth.

---

## 2. Score chips → progressive disclosure (chip → table → trend / sparkline)

### 2.1 Chip → component table (disclosure step 1)
Expanding a `ScoreBadge` chip reveals its component table via Radix `Collapsible`/`Accordion` over a real semantic `<table>` (a large screen-reader + keyboard win of the table-first stance, §13). Keyboard: arrow-navigable spine (roving tabindex), `Enter`/`Space` expands, focus-visible throughout. Selecting any **historical** chip re-decomposes at that timepoint — you can audit *why the score was 8 at 03:00* (`[salvage:C-core]`, MOT-19 case review).

### 2.2 The continuous 24 h score trend is ONE interaction from the default depth  — **[must_fix #2]**
Concept C originally buried the trend behind chip → row → per-component sparkline (a third click). That is **too much disclosure for the "visualização rápida" criterion** (`PER-CARLOS-03`, MOT-07 hidden-trend failure mode). Correction, grafting concept A's trend canvas `[salvage:A]`:

- A persistent **`Tendência 24h ▾`** control sits in the patient-rail header **and** on every score chip; **one tap** opens the aggregate 24 h score curve for that score (`TrendChart`, §5.4) — the continuous line `PER-CARLOS-03` and MOT-07 require, reachable from **Standard (default) depth in a single interaction**, never three. The `trend_chart_viewed` instrument is emitted so a demoted-and-unused trend is caught (MOT-07).
- The `TrendChart` draws the score line over `clinical.*` band-colored background reference bands (a crossing into a critical band is visible on the curve itself, not only at the badge), overlays **alert and intervention markers** (MOT-07 cause/effect), and exposes an **accessible data-table fallback** toggled by a visually hidden control (§5.4 a11y — a screen-reader user gets the same 24 h trend).
- **Per-component 24 h sparklines** remain the *deeper* (second) disclosure — a click on any decomposition row opens that parameter's micro-trend, expanded inline at Audit depth. The aggregate trend (one tap) and the per-component sparkline (two taps) are distinct: the must_fix is satisfied by the aggregate curve at one tap.

### 2.3 Sparse labs and staleness on the trend `[salvage:A]`
Labs (lactate, K⁺, creatinine…) arrive every 1–6 h; the trend renders them as **markers only, never interpolated into a line** — a drawn line would imply data that does not exist (`[salvage:A]`, concept A risk 4). Past a parameter's `staleness_max` the trailing segment renders **dashed/hatched**; on channel disconnect the trend **freezes with a "desatualizado · última sync HH:MM" banner** rather than presenting stale data as live (`[salvage:A]`, `ADR-0017-01`, §10). Continuity is never faked.

---

## 3. The Points column — decomposition + the ratification gate  — **[must_fix #6, #8]**

The **Points** column is the audit column — the points each component contributed to the aggregate. It is also the single largest patient-safety liability on this screen, so its provenance is governed hard.

### 3.1 Display == compute; render only from the ratified, versioned scorer service
- The Points column, the aggregate value, and the component rows render **exclusively from the versioned scorer service output** — the persisted `clinical_score` row (with its `algorithm_version` and input-snapshot reference, `INV-3`, early-warning-scores §5). **The UI never re-derives a point mapping** (`HAZ-016` display==compute; safety-officer-a/c must_fix). A decomposition row shows the *stored* per-component points computed by the same algorithm that produced the aggregate — not a UI-side table.
- **UI-side point tables are forbidden** (`SYS-C-03`; decision.yaml must_fix). The component→points mapping is authored **once**, in the scorer service, from the published definitions: RCP NEWS2 2017, Subbe MEWS (QJM 2001), Vincent SOFA (Intensive Care Med 1996), Seymour qSOFA (JAMA 2016); qSOFA cutoffs from `CAT-SEP-002` (RR≥22, SBP≤100, GCS<15). See early-warning-scores.md §3–§4 for every banded threshold.

### 3.2 Unverified mappings are blocked from display until RATIFY completes
Per `SYS-C-03` every P0 scoring rule is RATIFY, never silently adopted. Any component whose point mapping is **not yet ratified** is **blocked from rendering as a fact** — the Points cell shows a placeholder *"mapeamento pendente de ratificação (RAT-…)"* with the version withheld, **not a number** (`HAZ-001/002/003` P0 scoring hazards). The currently ratification-blocked mappings (early-warning-scores §7) and their placeholders:

| Component | Blocked until | Reason (P0/P1) |
|---|---|---|
| SOFA respiratory (P/F) | `RAT-CLINICAL-SCORING-01/05` | FiO₂ percent-vs-fraction → P/F ~100× wrong (SYS-01, P0-01/07) |
| SOFA cardiovascular (vasopressor) | `RAT-CLINICAL-SCORING-03` | raw mL volume vs weight-indexed mcg/kg/min (SYS-02, P0-02) |
| SOFA renal (Cr/urine) | `RAT-CLINICAL-SCORING-04` | over-wide 2-pt band + `(4.9,5.0]` dead gap → 4-pt undercount at peak acuity (P0-03) |
| SOFA liver (bilirubin) | `RAT-CLINICAL-SCORING-02` | strict-`<` dead gaps returning None (SYS-07, P1) |

Because SOFA carries the P0 fixes, its version is **`SOFA-v2.0.0`** (output changes for identical inputs); NEWS2/MEWS/qSOFA are `v1.0.0`. The panel renders the exact version that produced the row, so a historical score is reproducible for 7 years (`VIS-C-13`, `INV-3`). When a decomposition would be a **live detection of miscompute** — e.g. creatinine 5.0 mg/dL contributing 0 points (the exact HAZ-003/HAZ-019 dead-gap class) — the ratification block prevents laundering wrong math as transparency (safety-officer-c rationale).

---

## 4. Partial-score & staleness semantics (honoring AMH freshness)  — **[must_fix #1, #3]**

A score computed on missing or stale inputs must never masquerade as a valid one — the physician is legally responsible for the decision (`VIS-C-08`, HAZ-030/HAZ-024). Three first-class states, all `[salvage:C-core]` reinforced by the panel's strongest partial-data mechanisms.

### 4.1 `sem dado` — a missing component is never a silent zero
A component with no data reads **`sem dado`**, never coerced to 0 (which would silently understate the aggregate). Its row is flagged; the `VitalsList`/`ReferenceRangeFlag` `no-data` state carries the flag word in its accessible name.

### 4.2 `score parcial` — principled per-score validity, ratified, not cosmetic  — **[must_fix #1]**
Whether a missing component **invalidates** vs **degrades** a score must be clinically ratified per score, so the caveat is principled, not decorative (HAZ-030). The reference-anchored **recommended default** (designed here, marked **RATIFY → `RAT-EWS-02`**, routes to `RATIFICATION.md`; committee confirms):

**A partial aggregate is always a *lower bound* on the true score** (every missing component contributes ≥ 0). Let `lower` = Σ present components and `upper` = `lower` + Σ (max possible points of each missing component, from the published band tables). Classify against the score's alert threshold `T`:

| Condition | State | UI treatment |
|---|---|---|
| `lower ≥ T` | **VALID-SUFFICIENT** | render normally + note *"computado com N de M componentes; já ≥ limiar"* — the missing components cannot change the disposition |
| `lower < T ≤ upper` | **INDETERMINATE — `score parcial, não descartável`** | show the **range `[lower, upper]`**, flag the chip, prompt re-measure of the missing component; the score cannot exclude deterioration |
| `upper < T` | **VALID-BELOW** | render + note *"abaixo do limiar mesmo no pior caso"* |

**Per-score invalidating components (RATIFY, the principled core).** A component that can *alone* raise a single-red-parameter / high-risk response and is likely un-instrumented is **invalidating** — its absence forces `score parcial` regardless of the arithmetic above:

- **NEWS2 without consciousness (ACVPU)** → **INVALIDATES.** Consciousness C/V/P/U each contributes +3 (a single-red-parameter → urgent response, early-warning-scores §3.1); it is nurse-entered at PT4H staleness and the most likely to be absent. A comatose (U) patient with no ACVPU entry silently loses +3 — the exact HAZ-030 catastrophe named in the must_fix. NEWS2 missing ACVPU renders `score parcial — consciência ausente`, never a bare NEWS2.
- **qSOFA without GCS** → **INVALIDATES** (GCS<15 is one of three equal components; absence cannot exclude a +1 that reaches the ≥2 high-risk threshold).
- **SOFA missing any organ sub-score** → **INDETERMINATE** by the range rule (organ points are bounded 0–4 each); the aggregate is shown as a range, not a point value.
- All other missing components → classified by the range rule.

Every partial chip and every partial row carries the **red-flag-indeterminate** note when a red-flag-capable component is missing ("não é possível descartar parâmetro vermelho"). This is a design rule anchored to the published score definitions + HAZ-030; the exact invalidate/degrade boundary per score is the `RAT-EWS-02` committee decision.

### 4.3 Chip trend-arrow delta baseline rule  — **[must_fix #3]**
A wrong arrow on the spine is false reassurance (HAZ-031). The arrow (↑/→/↓) is a delta against an **explicit baseline**, never a defaulted "steady":

- **Baseline** = the most-recent prior `clinical_score` row of the **same score type AND same `algorithm_version`**, within a **PT4H lookback window** (aligned to the NEWS2 re-arm cooldown, early-warning-scores §3.1). No prior row in the window → the chip shows **`— sem base`** (no arrow), never `→`.
- **Direction** (aggregate scores are integer points): `↑` if `Δ ≥ +1`, `↓` if `Δ ≤ −1`, `→` if `Δ = 0`. This adjacent-recompute arrow is **distinct from** the rising-*trend* alert, which uses the authoritative `Δ ≥ 3 across ≥ 2 consecutive scorings within PT8H` rule (`ALERT-EWS-TREND-RISING-02`, `RULE MEWS-1-29/31`) — the arrow is a glance cue, not the alert.
- **Sparse-sampling guard.** If baseline and current differ in completeness (one is `score parcial`), the arrow is annotated **`base parcial`** and de-emphasized — a delta between a full and a partial score is not a true trajectory.
- **Prior-value provenance `[salvage:B]`.** The baseline value **and its timestamp** are always on hover/focus (`HoverCard`) and in the chip's accessible name (HAZ-031). No delta headline anywhere on this screen is shown without its prior value + timestamp, or the explicit `sem valor anterior` (safety-officer-b must_fix, a contract test).

### 4.4 Per-component staleness age honors AMH freshness  — **[data-staleness indicators]**
Every decomposition row's **Staleness** column shows the age of the underlying clinical measurement (`recorded_at`/collected_at, **never** `ingested_at` — `DM-C-08`/`amh-freshness.yaml` semantics). A row past its parameter's `staleness_max` is flagged; the chip that was computed on any stale input carries a caveat marker so the responsible clinician sees *exactly which component is old*. Thresholds bind to the units registry / `amh-freshness.yaml`, per parameter — e.g. operational vitals `5min` (`vitals_operational`), electrolytes `1h` (`labs_electrolytes`), sepsis labs `2h` (`labs_sepsis`), ABG `1h`, creatinine `12h`, RASS/CAM-ICU `12h` — never per-chart constants (HAZ-024, safety-officer-a must_fix). On operational-vitals staleness > 5 min the derived score is marked `stale` and **new** threshold-cross alerts are suppressed (frozen-value guard, `amh-freshness.yaml vitals_operational` fallback), while the last score stays visible with a staleness badge (never blanked).

---

## 5. What-changed deltas since last review  — **[graft from concept B]**

The **What-changed digest** (Context Rail card + the spine's delta events) answers *"what is different since I last looked / since handoff"* — the narrative-of-change reading concept B championed, decomposed to the component level as concept C requires.

- **Component-level, never a bald score delta.** Every delta names its parameter: *"NEWS2 6→8: SpO₂ 96 %→91 % (+2 pts); demais componentes inalterados"* (`PER-ANA-02`/`PER-C-04`, `[salvage:B]` + `[salvage:C-core]`). The Δ-since-prev column in the decomposition (§1.2) highlights the component(s) that *drove* the change.
- **Ranked by contribution to score change** `[salvage:A]` (the what-changed delta rail ranked by contribution, MOT-01/MOT-07): the digest orders deltas by how many points they moved, so the eye lands on what mattered.
- **"Since last review" anchor.** The digest window anchors to either (a) the clinician's own last view of this patient, or (b) the last **shift marker** (the since-last-handoff delta digest anchored to shift markers, `[salvage:B]`, MOT-17) — selectable via `Tabs`. The shift-marker digest is exactly what `handoff.md` projects into SBAR-Avaliação.
- **Prior-value + timestamp on every headline** (§4.3, HAZ-031). **Burst-collapse** `×N` by dedup key and **quiet improvement** events keep the digest to actionable change, not raw volume `[salvage:B]` — but a burst-collapse **never merges across severity classes**, and any severity **upgrade** always renders a new, announced card (safety-officer-b must_fix, HAZ-026).

---

## 6. Point-critical labs stay triage-visible without expanding any table  — **[must_fix #5]**

A `clinical.severity.critical` value (K⁺ > 6.5 mmol/L `CAT-ELY-001`; lactate ≥ 4 mmol/L; the alert's triggering vital) demands action **now**, regardless of any trend or disclosure state — a critical K⁺ must never require disclosure clicks to be seen (HAZ-023-class). Grafting concept A's forced-interruptive callout and concept B's always-on now-strip:

- The patient rail carries a **Critical Values rail** that **never collapses at any depth** (§1, §1.4). Every active critical-band lab/vital renders there as a pinned chip — value + band (color+icon+shape+text) + staleness age — with **zero expansion required**. It is present in Collapsed depth (Rafael's phone), Standard, and Audit.
- A critical value **also** escalates to a pinned spine event **and** an `AlertCard` in the rail (§8) with `role="alert"` assertive announcement (§13), independent of which score lane or window is selected. This is a **tested invariant, not styling** (safety-officer-a/ux-researcher-a must_fix, MOT-11): any critical-band value is always pinned + assertively announced regardless of trend shape or zoom.
- **Never auto-resolve on a stale panel.** An open critical electrolyte alert is not auto-cleared on a stale panel (`amh-freshness.yaml labs_electrolytes` fallback); the critical-values rail shows the staleness age so a frozen critical value is visibly old, not silently trusted.
- AAA scoping: the critical value's numeral meets 1.4.6 (7:1) and, if interactive (the ack), 2.4.13 enhanced focus + 44×44 target (`A11Y-REQ-01/21`, accessibility standard §1.2).

---

## 7. Correlation-explanation surfaces (member events + evidence)

The exactly-three vision-sanctioned cross-domain correlations (`VIS-4-03`, correlation-engine.md): **Sepse + AKI**, **Respiratória + Hemodinâmica**, **Drogas + Eletrólitos (QTc + K⁺/Mg²⁺)**. Rendered two ways, never as a black box:

- **As a first-class stream event on the spine** `[salvage:B]` — a `🔗 Correlação` event with a **`por quê? ▾`** disclosure that names the **member events** (back-linked into the spine, each inspectable), the **causal lag**, the **triggering values** in canonical units, the **evidence citations**, and the **member alerts it suppressed** (`member_alerts_suppressed`) so the clinician can drill into any folded single-domain detail (correlation-engine.md §8 explainability output, MOT-13). Because both members already exist on the spine, the correlation is anchored to what the clinician can see.
- **As the synchronized scrub cursor** `[salvage:A]` — dragging the vertical playhead across spine + trend + decomposition reports every lane's value at one timestamp: co-occurrence as a **spatial fact at one instant**, no separate correlation view needed (MOT-13). A **tap-to-pin** fallback ships for touch (Rafael one-handed en route; safety-officer-a/ux-researcher-a must_fix, MOT-15) so the correlation read is not mouse-only.
- **Advisory discipline.** Captions are strictly **co-occurrence, not causation** `[salvage:A]` — the system states what crossed together, never *why* as a diagnosis; each correlation carries the *"o médico decide"* banner (`VIS-C-01`/`VIS-C-08`, SaMD Classe II). No free-text inference; limited to the three sanctioned pairs. Severity of a correlated insight is `MAX(member severities)` — a critical constituent never hides under a watch summary (severity-model aggregation `max-severity-wins`, MOT-13).

---

## 8. Which-parameter-triggered visibility (PER-ANA-02)

The decomposition panel **is** the answer to "qual parâmetro disparou?" — no other concept makes it the whole center panel (`PER-ANA-02`/`PER-C-04`, MOT-06). For an **alert** tied to this timeline, the Context Rail `AlertCard` (§5.5) shows the triggering parameter(s) inline in the headline with value + unit + threshold crossed + window + per-input staleness, each value flagged by *its own* band (`ReferenceRangeFlag`), and a **1-click acknowledge** that charts to **NGS Level 2** (`PER-ANA-03`/`VIS-C-07`) — optimistic and reconciled against the authoritative record over the one channel (`ADR-C-12`). Only PPV-budgeted, deduped, suppressed alerts render — not the legacy 200/day at 80 % FP (`PER-C-02`/`VIS-7.1-02`). The full four-block **why-panel** (triggering parameters, evidence citation, rule id + version, data-coverage note) is reachable in ≤ 2 taps and is **owned by `alert-triage.md` §4** (`US-21`); this screen surfaces it, does not redefine it. Auditability is the alarm-fatigue lever: seeing the single artifactual component (a slipped SpO₂ probe) instantly dismisses a false positive; seeing the coherent multi-component cluster instantly justifies a true one — adding *explanation*, never alert volume (`PER-C-02`, `VIS-7.1-02/04`).

---

## 9. RRT en-route view (PER-RAFAEL-02) + the desfecho separation  — **[must_fix #7]**

The **Collapsed depth is Rafael's phone view** (`RRTMobileCard`, §5.16). A `critical`-score push reaches his corporate smartphone **< 5 s** (`PER-RAFAEL-01`/`PER-C-06`, same one channel `ADR-C-13`) and deep-links straight into this timeline; the shell reconstructs the full breadcrumb so he sees **location** as wayfinding en route (`PER-RAFAEL-02`, MOT-14/MOT-15). The Collapsed view loads, one-handed and in motion: the current band + trend arrow, the **top-3 contributing components** + the what-changed line (so he knows *what drives the crisis* before arrival, not just that a number is high), the **critical-values rail** (§6), and each vital's **own staleness timestamp** ("dados de HH:MM") for a graceful partial render on hospital Wi-Fi dead spots (MOT-15). The one-tap `Tendência 24h` (§2.2) gives him shape.

**Outcome documentation is a separate structured desfecho flow, NOT the SBAR dialog doing double duty** (ux-researcher-c must_fix, MOT-16). Rafael's `desfecho ▸` control opens the **`OutcomeDocumentationSheet`** (§5.16, `US-28`, owned by `alert-triage.md` §3): a **structured outcome picker** (`melhorou`, `transferido para UTI`, `óbito`, `permanece em observação`, …) + optional free text, structured-options-first, completable in **< 1 minute** measured **form-open → save** (`PER-RAFAEL-03`/`PER-C-07`; `form_opened`/`form_saved` telemetry, MOT-16). The record links the dispatching alert(s) in the audit trail (`VIS-7.1-03`). The SBAR generator (`handoff.md`) is a *read* projection of the timeline; the desfecho is a *structured write* — conflating them under-serves the < 1-min instrument, so they are distinct instruments with distinct controls.

---

## 10. States

- **Loading** — content-shaped `SkeletonLoader` (§5.15): skeleton chips on the spine, skeleton rows in the table; patient rail + now strip render immediately from cached context. Never a full-viewport blocking spinner (`ADR-0016-01`, retires `FadeLoading`/`DES-5-07`).
- **Stale / disconnected** — one channel, so loss is **loud, never silent** (`ConnectionStatusIndicator` §5.13 + `StalenessBanner` §5.7): a connection banner + per-**component** staleness age + trend **freeze-on-disconnect with "última sync HH:MM"** `[salvage:A]`; dashed trailing segments past `staleness_max` (§2.3). The deliberate inverse of the legacy silent-poll where a red alert lagged the grid (`DES-6-02`, MOT-18).
- **Missing component** — `sem dado` + `score parcial` per §4.
- **Empty timeline** — freshly admitted patient with < 1 computed score → explicit empty state noting the first score pends the first vitals set (`VIS-6.1-04`); an explicit "início da internação" anchor so an empty timeline reads as *new patient*, not *broken feed* `[salvage:B]`.
- **Error / permission** — classified error (validation / permission / server) mapped to visual weight (inline / toast / modal), backend-shape-agnostic (`ADR-C-11`); **no class defaults to a blocking modal** (`A11Y-REQ-19`, retires the legacy `handleApiError`). Permission-denied re-routes per deny-by-default (`ADR-C-05`).
- **Reduced motion / contrast** — chip-appearance and expand transitions gated by `prefers-reduced-motion` (instant state-change fallback); `prefers-contrast` flattens neumorphic elevation to a flat-shadow token; AA contrast verified in both themes over embossed surfaces (`ADR-C-04`). Essential motion (a live sparkline) is retained but paired with the static delta number (§4.3), never motion-only (`A11Y-REQ-14`).

---

## 11. Focus, keyboard & overlay stack

- **Spine** — roving `tabindex`; ↑/↓ moves between chips/events; `Enter`/`Space` expands a chip (Radix `Collapsible`); focus-visible ring meets contrast in both themes (`A11Y-REQ` 2.4.7).
- **Decomposition** — a real semantic `<table>` with header cells; each row independently focusable; a per-component sparkline expands in place (`Enter`) and collapses (`Esc` on the row, reversible/in-place).
- **Overlay stack** — SBAR preview, bed selection, and secondary forms use `OverlayStack` (§5.9): single global stack, **max depth 2** (`A11Y-REQ-07`); `Escape` closes **only the topmost** level and hardware/OS **back** matches Esc (`A11Y-REQ-08/09`); each level `role="dialog"`/`alertdialog` + `aria-modal` + focus trap; background `inert`; initial focus on the first meaningful control (not the ×, not a destructive default), and on close focus returns to the exact trigger chip/button (`A11Y-REQ-10/11`); focused control never obscured by the sticky header/now-strip (`A11Y-REQ-12`, 2.4.11).

---

## 12. Realtime semantics

- **One channel** (`lib/realtime`, `ADR-0017-01`/`ADR-C-13`): a new score chip, stream event, correlation, or alert **appends/patches** a timeline item or triggers a scoped refetch; the payload is a thin idempotent patch reconciled against the authoritative record, never a second source of truth (`ADR-C-12`). Bell + board + timeline cannot disagree about one event — they share the channel and its latency class.
- **Latency** — score chip **< 30 s** after inputs land (`PER-C-01`/`VIS-C-09`, MOT-04); `critical` push to RRT **< 5 s** (`PER-C-06`). Correlation events are bounded by their slower member's arrival (AMH Gold batch p95 < 30 min for lab members; correlation-engine §9) — the timeline shows the member arrival times so a late correlation is not read as a late crisis.
- **aria-live per severity** (§13, accessibility standard §5.1): a new `critical` chip/alert announces assertively (`role="alert"`) without forcing focus; `urgent` assertive region; `watch` polite; `normal` off (log/worklist only). Announcements are coalesced one per severity container per ~2 s to prevent screen-reader stomping (`A11Y-REQ-17`) — the visual chip still paints immediately.
- **Live update never reflows focus** — new chips update in place; the viewport never auto-scrolls out from under a keyboard/AT user mid-navigation (`A11Y-REQ-15`, 4.1.3).

---

## 13. Accessibility gate (binding — accessibility-standard.md §8)

- **A11Y-GATE-01** — All text/labels ≥ 4.5:1 (large 3:1); every `critical`-scoped element (critical-values rail §6, a critical chip/row) additionally ≥ 7:1 (1.4.6, `A11Y-REQ-01`). Tabular monospace numerals (`DES-2-05`).
- **A11Y-GATE-02** — Icons, chart marks, severity borders/glow, focus rings ≥ 3:1 non-text contrast in both themes (1.4.11).
- **A11Y-GATE-03** — No severity/partial/resolution state encoded by color alone; each carries a distinct icon **and** shape/outline reading identically in greyscale (`A11Y-REQ-02`, §2.4). `score parcial`, `sem dado`, `melhora`, and `ASSISTIDO` are text+icon states, not hues.
- **A11Y-GATE-04** — The severity palette used is the ratified `clinical.*` set run through the §2.2 CVD-ΔE method at C2; this screen references tokens, never raw hex (design-token-systems-designer owns final hex).
- **A11Y-GATE-05** — No animation exceeds 3 Hz (`A11Y-REQ-13`, seizure floor); `prefers-reduced-motion` honored for chip/expand transitions; the essential live sparkline has the static delta-number fallback (§4.3).
- **A11Y-GATE-06** — Severity icon+shape pairs stay distinct at the smallest chip render size used (protects the deuteranopia `watch↔critical` LOW-RISK pair, accessibility-standard §2.3).
- **A11Y-GATE-07** — Every severity-colored/iconed/announced element derives encoding from the **live** value via `lib/severity` — no hardcoded literal (closes both legacy severity bugs, §0).
- **A11Y-GATE-08** — Overlay stack: Esc closes only itself; back matches Esc; `role="dialog"`/`alertdialog` + `aria-modal` + focus trap; initial-focus + exact focus-restore; depth ≤ 2 (§11, `A11Y-REQ-07/08/09/10/11`).
- **A11Y-GATE-09** — Every live region names its `aria-live` politeness per the §5.1 severity table + its coalescing behavior (§12, `A11Y-REQ-16/17`).
- **A11Y-GATE-10** — Every alert/chip accessible name follows severity → parameter+value+trend → location (never color/location alone), e.g. *"Crítico. SpO₂ 91 %, em queda, +3 pts. NEWS2 8. Leito 12."* (`A11Y-REQ-18`, `PER-C-04`).
- **A11Y-GATE-11** — Pointer targets ≥ 24×24; the 1-click ack and every RRT mobile primary action ≥ 44×44 (`A11Y-REQ-20/21`).
- **A11Y-GATE-12** — No pure `#FFF`/`#000` large surface (`A11Y-REQ-23`); embossed surfaces carrying clinical text pass a stated contrast check in both themes + a `prefers-contrast: more` flat-shadow fallback (`A11Y-REQ-24`/`CON-0037`).
- **A11Y-GATE-13** — The scrub cursor is a drag idiom → ships the tap-to-pin single-pointer alternative (§7, `A11Y-REQ` 2.5.7). No other drag interaction on this screen.
- **A11Y-GATE-14** — No authentication/e-signature step on this screen (the NGS-2 charting ack rides the alert lifecycle owned by alert-triage.md); N/A here.
- **A11Y-GATE-15** — Every custom component (`ScoreBadge`, spine chip, decomposition row, critical-values chip) exposes accessible name/role/state (4.1.2) — no bare `<div onClick>`.
- **A11Y-GATE-16** — The decomposition is read-only; the schema-driven clinical form engine is not used here (the desfecho form is owned by alert-triage.md), so 3.3.7 redundant-entry is N/A on this screen.

---

## 14. Scope boundary & cross-surface coverage  — **[must_fix #4]**

This is a **single-patient** timeline. It is deliberately **not** Fernanda's live floor view, and that boundary must not become a coverage gap (MOT-03).

- **PER-FERNANDA-01 (real-time occupancy/acuity dashboard) is owned by the home bed-grid command-center surface** — `BedGrid`/`BedCard` (§5.1) + `KpiDashboardWidgets` (§5.17), stories `US-06`/`US-09`, journey moments MOT-01 (07:00 scan), MOT-03 (coordinator morning review), MOT-18 (monitor-wall glance). That surface is the multi-unit live view; **this timeline is the drill-down / case-review target** reached from it.
- On **this** surface Fernanda is served for **retrospective case review and quality export**: Audit depth reconstructs a deterioration event component-by-component for M&M review, verifies the ack-timestamp response-time SLA against the ≤ 15 min target (`PER-FERNANDA-02`/`VIS-7.1-03`), and the SBAR + decomposition export to hospital quality tools (`PER-FERNANDA-03`/`PER-C-08`, `handoff.md`).
- The boundary is **logged as a risk (R2)** in concept-c and pinned here so the plan demonstrably covers PER-FERNANDA-01 elsewhere (decision.yaml must_fix; the command-center screen spec is the owner).

---

## 15. Traceability

### 15.1 Constraints & criteria discharged here
| Constraint / story / criterion | Where addressed |
|---|---|
| `PER-CARLOS-03`/`PER-C-03` 24 h trend, fast | §1.1, §2.2 (one-tap `TrendChart`) |
| `PER-C-01`/`VIS-C-09` score < 30 s | §1.1, §12 |
| `PER-ANA-02`/`PER-C-04` which parameter triggered | §1.2, §5, §8 |
| `PER-ANA-03`/`PER-C-05` 1-click ack → NGS-2 | §8 (`VIS-C-07`) |
| `PER-RAFAEL-01`/`PER-C-06` push < 5 s · `PER-RAFAEL-02` en-route content | §9 |
| `PER-RAFAEL-03`/`PER-C-07` desfecho < 1 min (structured, separate) | §9 |
| `PER-FERNANDA-02/03`/`PER-C-08` case review + export; `PER-FERNANDA-01` boundary | §14 |
| `VIS-C-08`/`VIS-C-01` advisory, physician decides · `VIS-C-13` auditable version | §1.2, §3, §7 |
| `VIS-2-01..04` MEWS/NEWS2/qSOFA/SOFA · `CAT-SEP-002` qSOFA cutoffs | §1.1, §3 |
| `VIS-4-03` the three correlations · correlation-engine §8 explainability | §7 |
| `PER-C-02`/`VIS-7.1-02/04` PPV / FP / alarm-fatigue via auditability | §8 |
| `ADR-0013-01`/`CON-SEED-11` triple-encoded severity; `ADR-C-09` no hardcoded literal | §0, §13 |
| `ADR-0014-01`/`CON-0054` abnormal-value flagging | §0, §1.2 |
| `ADR-0017-01`/`ADR-C-12/13` one realtime channel, loud staleness | §0, §10, §12 |
| `ADR-0010-01` overlay stack; `ADR-0011-01`/`ADR-C-07` one density function | §1.3, §1.4, §11 |
| `SYS-C-03`/`HAZ-001/002/003/016` Points ratification gate, display==compute | §3 |
| `HAZ-030` partial score · `HAZ-031` delta baseline · `HAZ-024` staleness · `HAZ-023` critical labs | §4, §6 |
| `DM-C-08` staleness on clinical timestamp; `amh-freshness.yaml` per-source staleness_max | §4.4 |

### 15.2 Salvage grafts (marked at point of use)
- `[salvage:B]` — stream events on the spine; gap events (absence-as-change); since-last-handoff delta digest anchored to shift markers; correlation as a first-class stream event with `por quê?` back-links; prior-value + timestamp provenance on every delta; burst-collapse ×N + quiet melhora (never across severity); sticky now-strip state-vs-change separation; SBAR as a deterministic projection (→ `handoff.md`). (§1.1, §4.3, §5, §7)
- `[salvage:A]` — one-tap 24 h `TrendChart` (trend-canvas as first-class); markers-only sparse labs (no interpolation); dashed/hatched stale segments + freeze-on-disconnect with last-sync banner; the synchronized scrub cursor as the correlation read (co-occurrence spatial fact); what-changed rail ranked by contribution; co-occurrence-not-causation caption discipline. (§2.2, §2.3, §5, §7, §10)

---

## 16. `must_fix` traceability  — **8 / 8 addressed**

Panel decision `must_fix` (`docs/plan/_work/panels/timeline-model/decision.yaml`), each mapped to where it is resolved:

1. **`score parcial` semantics clinically ratified per score (which missing components invalidate vs degrade; NEWS2 without consciousness), HAZ-030** → **§4.2** — the lower/upper-bound classification + per-score invalidating-component table (NEWS2/ACVPU invalidates), designed to the recommended default and marked **RATIFY `RAT-EWS-02`**.
2. **A continuous 24 h score trend reachable in one interaction from the default depth (PER-CARLOS-03, MOT-07)** → **§2.2** — persistent `Tendência 24h` control opens the aggregate `TrendChart` in one tap from Standard depth; per-component sparklines demoted to the deeper level `[salvage:A]`.
3. **Chip trend arrows need an explicit delta baseline rule (window, sparse-sampling), HAZ-031** → **§4.3** — baseline = most-recent prior same-type/same-version row within PT4H; `— sem base` when absent; sparse-sampling `base parcial` guard; prior-value + timestamp provenance.
4. **Pair this surface with the home dashboard so PER-FERNANDA-01 is covered elsewhere (MOT-03)** → **§14** — PER-FERNANDA-01 explicitly owned by the bed-grid command center (`BedGrid`/`KpiDashboardWidgets`, US-06/09, MOT-01/03/18); this timeline is the drill-down; boundary logged as R2.
5. **Point-critical labs triage-visible from the spine/alert rail without expanding any table (HAZ-023)** → **§6** — non-collapsing Critical Values rail at every depth + pinned spine event + assertive `AlertCard` as a tested invariant; never auto-resolve on a stale panel.
6. **Points-column ratification gate mandatory before ship: only published, versioned scorer mappings render, unverified blocked** → **§3.1–§3.2** — render only from the versioned scorer service; unverified mappings blocked with a `pending ratificação` placeholder, not a number.
7. **Rafael's outcome documentation is a real structured desfecho flow, not the SBAR dialog doing double duty (PER-RAFAEL-03, MOT-16)** → **§9** — `desfecho ▸` opens the structured `OutcomeDocumentationSheet` (US-28, alert-triage.md §3), measured form-open→save < 1 min; SBAR is a separate read projection (reinforced in `handoff.md`).
8. **Points column renders ONLY from the ratified, versioned scorer service; UI-side point tables forbidden; unverified blocked until RATIFY (SYS-C-03; HAZ-001/002/003; HAZ-016 display==compute)** → **§3** — display==compute enforced; the SOFA P0 RATIFY set (`RAT-CLINICAL-SCORING-01..05`) blocked from display until ratified; `SOFA-v2.0.0` reproducible per `INV-3`/`VIS-C-13`.
