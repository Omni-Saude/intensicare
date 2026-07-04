# Timeline Model — Concept A: Trend-Canvas-First

**Panel:** patient timeline as the core clinical object.
**Deliberate stance:** the patient *is* a continuous 24h multi-parameter canvas with clinical-score
overlays. Every other affordance (what-changed deltas, score-component disclosure, correlation
explanations, staleness, SBAR handoff) is a *projection of, or interaction on, that one canvas* —
not a separate surface. You read the **shape** of the trend before you read any number.

This concept deliberately does NOT hedge toward an event-feed-first or snapshot-card-first model.
Its bet: in an ICU, deterioration is a *slope*, and the false-positive problem (Carlos: 200
alerts/day, 80% FP — `personas.md §1`) is fundamentally a *context* problem that a threshold blip
in isolation cannot solve but a trend in view can.

---

## 1. Layout

Three fixed zones over one shared horizontal time axis. Dark-first, compact base
(`ADR-0002-01`); `clinical.*` severity tokens structurally separate from `brand.*`
(`ADR-C-08`, `DES-C-01`); neumorphic elevation as the surface signature (`ADR-0007-01`).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ IDENTITY STRIP  Leito 07 · A. Souza · 68a · LOS 4d   [NAD][VM][SED][HD]      │  ← device chips (MicroIndicadores, DES-3-05)
│ NEWS2 9 ▲+3/4h   MEWS 5   SOFA 8 (d4)   qSOFA 2      ⟳ há 40s   ● ao vivo     │  ← composite score + Δ + sync/staleness
├──────────────────┬──────────────────────────────────────────┬───────────────┤
│ LEFT RAIL        │            THE CANVAS (24h axis)          │ WHAT-CHANGED  │
│ (labels+latest+  │                                          │ RAIL          │
│  staleness dot)  │  ── one shared time axis, 00h → now ──   │               │
│                  │                                          │ Δ janela 4h:  │
│ ▸ SCORE   9   ●  │  ╱╲___╱▔▔▔  NEWS2 area, sev-banded        │ NEWS2  +3 ▲   │
│ ─────────────────│  ▁▂▃▅▇  SOFA step · qSOFA ▮ ticks         │ SpO₂/FiO₂ −22%│
│ HR      118  ●  │  ∿∿∿╱╲∿  HR sparkline, ref-range shaded   │ Lactato +1.2  │
│ RR       28  ●  │  ___╱▔▔▔  RR, urgent band from 24         │ RR     +8 ▲   │
│ SpO₂/FiO₂ 148 ● │  ▔▔╲__    ratio falling → moderate band   │               │
│ PAM      58  ●  │  ▔╲___    MAP band (SBP/MAP)              │ (window       │
│ Temp    38.4 ●  │  __╱▔▔     step markers                   │  selectable:  │
│ · · · · · · · · │                                          │  4/8/24/72h)  │
│ Lactato  2.4 ○  │  •      •        • sparse lab markers     │               │
│ K⁺       5.1 ○  │     •        •                            │               │
│ ─────────────────│  ▲sepse ◆ATB ✚fluid  ●ack  EVENT LANE    │               │
└──────────────────┴──────────────────────────────────────────┴───────────────┘
           ▲ synchronized scrub cursor (playhead) crosses ALL lanes
```

- **Identity strip** — bed, name, age, length-of-stay, device chips (noradrenaline / mechanical
  ventilation / sedation / dialysis, reusing the `MicroIndicadores` vocabulary, `DES-3-05`). The
  current composite score with its **what-changed delta** (`NEWS2 9 ▲+3/4h`) is the single
  largest element: score-first, trend-annotated. Scores are MEWS, NEWS2, SOFA, qSOFA
  (`VIS-2-01..04`) — computed by the platform, never hand-calculated (`PER-C-03`).
- **The canvas** — vertically stacked **small-multiple lanes**, all locked to one horizontal 24h
  axis (default; presets 4h/8h/24h/72h). Ordering top→down = clinical priority:
  1. **Score lane** (tallest, the anchor): NEWS2/MEWS as a filled area whose fill is banded by
     `clinical.*` severity (normal/watch/urgent/critical); SOFA as a daily step line; qSOFA as
     discrete tick marks. This is where the eye lands first.
  2. **Vital lanes**: HR, RR, SpO₂/FiO₂ ratio, BP (SBP + MAP as a band), Temp — each a sparkline
     with its reference range drawn as a shaded normal corridor, so out-of-range excursions
     literally leave the safe band. Threshold flagging by band, per `ADR-C-06`/`ADR-0014-01`
     (fixes the legacy "SpO₂ 99% and 60% render identically" gap, `DES-5-04`).
  3. **Lab lanes**: lactate, creatinine, K⁺, Na⁺ … as **sparse point markers** on the same axis —
     never interpolated into a continuous line (labs arrive every 4–6h; a drawn line would imply
     data that does not exist).
  4. **Event lane** (bottom): alert firings, med changes, interventions, acks — pinned to their
     timestamp, encoded by severity **color + icon + shape** (`ADR-0013-01`).
- **What-changed rail** — a computed Δ summary over the selected window (`ΔNEWS2 +3`,
  `ΔSpO₂/FiO₂ −22% in 6h` echoing `VIS-3.3-05`, `Δlactato +1.2`). This is the deltas-first reading
  of the same canvas, ranked by contribution to score change.

---

## 2. Interactions

- **Synchronized scrub cursor (the correlation engine).** Hover or keyboard-drag a vertical
  playhead across the canvas; every lane reports its value at that timestamp on a crosshair. The
  *vertical line itself* is the correlation explanation: at 03:14 you see RR jump, SpO₂/FiO₂ fall,
  and the NEWS2 area cross into `urgent` — one glance, one instant, all parameters. No separate
  "correlation view" is needed because co-occurrence is spatial.
- **Score-component progressive disclosure.** Click the score lane → it expands into a stacked
  contribution band showing each parameter's *points into the score* over time (RR contributes 3,
  SpO₂ 2, BP 1 …). At the cursor timestamp this answers Ana's "which parameter triggered?"
  (`PER-ANA-02`, `PER-C-04`) directly on the trend, not in a modal. Collapses back to the area
  summary — disclosure is reversible and in-place.
- **Correlation explanation on an alert.** Selecting an event-lane alert glyph highlights the
  contributing lanes, draws thin connectors from the alert to the vitals/labs that crossed
  threshold, and prints a plain-language caption sourced from the alert's own trigger logic
  (e.g. *"qSOFA 2 + lactato 2,4 mmol/L → SEP-002"*, `CAT-SEP-002`). Caption is worded as temporal
  **co-occurrence, not causation** — the system states what crossed together, never *why*.
- **One-click acknowledge / outcome.** An alert glyph carries a single ack affordance
  (`PER-C-05`, `PER-ANA-03`); ack applies the `ASSISTIDO` blue override to the glyph
  (`ADR-0013-01` — the concept models ASSISTIDO as a state, not a color hack) and stamps
  responder + time into the event lane, feeding response-time metrics.
- **Zoom / pan.** Presets 4h/8h/24h/72h; pinch/scroll to zoom, drag to pan. 24h is the default
  (Carlos's `PER-CARLOS-03` "gráfico 24h"); RRT mobile defaults to 8h.
- **SBAR handoff toggle.** A view toggle reflows the *same timeline object* into an
  SBAR-structured read: **S**ituação = current scores + what-changed deltas; **B**ackground =
  admission, LOS, devices, 72h compressed trend; **A**valiação = active alerts + out-of-band
  parameters at the cursor; **R**ecomendação = pending acks / open bundle items. It is a
  *projection*, not a second data model — SBAR sections are queries over the canvas.

---

## 3. States

- **Loading** — content-shaped lane skeletons, never a full-viewport blocking spinner
  (`ADR-0016-01`, fixes `DES-5-07`'s `FadeLoading`).
- **No data for a parameter** — the lane shows an explicit "sem dados" gap; no line is fabricated.
- **Stale sample** — when a parameter's newest sample exceeds its `staleness_max`, the trailing
  segment renders **dashed/hatched** and the left-rail dot goes amber (●→○). The canvas never
  interpolates across a staleness gap, so continuity is never faked. This is the explicit
  staleness indicator the legacy bed board *lacked* (`ADR-0017-01`, `DES-6-02`).
- **Realtime update** — a new sample slides in at the right edge over the **single** push channel
  (`ADR-C-13`); the payload is a thin idempotent patch reconciled against the authoritative record,
  never a second source of truth (`ADR-C-12`). Slide animation respects `prefers-reduced-motion`.
- **Disconnected** — the canvas *freezes* with a "desatualizado · última sync HH:MM" banner rather
  than presenting stale data as live. Reconnect backfills the gap.
- **Acknowledged alert** — glyph adopts the `ASSISTIDO` state (blue), distinct from its raw
  severity.
- **Error** — inline, severity-classified (validation/permission/server), not a blanket modal
  (`ADR-0016-01`, `ADR-C-11`).

---

## 4. How each persona succeeds

- **Dr. Carlos (intensivist).** Opens a patient and reads the 24h score-lane *shape* in one glance —
  his literal success criterion is "visualização rápida de tendências (gráfico 24h)"
  (`PER-CARLOS-03`). The what-changed rail (`ΔNEWS2 +3/4h`) tells him *deterioration vs. noise*
  without hunting. Because a threshold blip is now seen inside its trend, he can dismiss a
  self-resolving spike instead of reflex-reacting — directly attacking his 80%-false-positive pain
  and supporting `<3 FP/patient-day` (`PER-C-02`). Score availability <30s (`PER-C-01`) is met by
  the single push channel feeding the canvas.
- **Enf. Ana (nurse).** Scores are drawn automatically — zero manual MEWS calculation
  (`PER-C-03`, `PER-ANA-01`). The score-component disclosure shows *exactly which parameter*
  contributed the deterioration points at any timestamp (`PER-ANA-02`, `PER-C-04`) — "RR? SpO₂?
  BP?" is answered on the trend. She acks and logs her response in one click on the alert glyph
  (`PER-ANA-03`, `PER-C-05`).
- **Dra. Fernanda (coordinator).** The timeline is her *drill-down target* from an acuity board,
  and it makes her quality metric visible: the horizontal distance from an alert glyph to its
  `ASSISTIDO` ack glyph *is* response time, readable per patient. The SBAR projection and its
  underlying structured records give her the exportable substrate for weekly KPI reporting
  (`PER-FERNANDA-02`, `PER-C-08`). She succeeds when time-to-response is a visible, aggregable
  artifact rather than a perception.
- **Dr. Rafael (RRT).** On mobile the canvas collapses to a thumb-scrollable, vertically stacked
  8h view: header carries score + **patient location** + latest vitals so he reads trend + current
  state *en route* (`PER-RAFAEL-02`). The SBAR toggle gives him the situation in seconds on arrival;
  the same one-click ack/outcome affordance lets him document the outcome in under a minute
  (`PER-RAFAEL-03`). His <5s critical notification (`PER-C-06`) rides the same push channel.

---

## 5. Risks (honest weaknesses of the trend-canvas bet)

1. **Density vs. legibility.** Many stacked lanes are unreadable on small/mobile screens. Mitigation:
   priority ordering + collapsible lanes; RRT gets a curated subset (score + 3 vitals + events),
   not the full stack. Residual risk: nurses may want *more* lanes than fit.
2. **A point-critical value can hide in a trend.** K⁺ 6,6 mmol/L (`CAT-ELY-001`) demands action
   *now* regardless of slope; a trend-first canvas structurally under-weights the instantaneous
   critical lab. Mitigation: critical lab markers always escalate to a pinned event-lane glyph +
   forced score-strip callout — but this is a genuine tension with the snapshot-first stance and an
   honest cost of this concept.
3. **Paint cost.** Neumorphic surfaces + many live sparklines on a dense screen risk jank
   (`ADR-0007-01` explicitly demands a paint-cost benchmark). Mitigation: canvas/SVG render budget,
   point decimation, offscreen lanes not animated.
4. **False continuity / false causation.** A drawn line can imply data between sparse lab samples;
   connector lines can imply causation. Mitigation: sparse labs are markers-only (never lines);
   captions are strictly co-occurrence language.
5. **Touch scrubbing is weak.** The scrub cursor is a mouse/keyboard idiom; RRT on a phone needs a
   tap-to-pin fallback. Residual UX cost.
6. **A11y of tiny glyphs.** Triple-encoding (color+icon+shape) on small event glyphs is hard to keep
   AA-contrast and distinguishable; sliding updates risk `prefers-reduced-motion` violations.
   Mitigation in §a11y below.

---

## 6. Alarm-fatigue impact

Showing each alert *inside its 24h trend context* lets clinicians distinguish sustained
deterioration from a self-resolving blip, so they react to slopes rather than to isolated threshold
crossings — this is the concept's direct lever on Carlos's 80%-false-positive burden and the
`<3 FP/patient-day` target (`PER-C-02`), *without* adding any new alert type.

## 7. Accessibility notes (WCAG 2.2 AA)

Severity is triple-encoded (color + icon + shape) per `ADR-0013-01`; all lanes meet AA contrast in
both dark and light themes (`ADR-C-04`); the scrub cursor is fully keyboard-operable with an ARIA
live region announcing value-at-cursor per lane; slide-in updates and animated transitions are
disabled under `prefers-reduced-motion`, and a `prefers-contrast` flat-shadow fallback replaces
neumorphic elevation for clinical content.
