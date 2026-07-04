# Patient Timeline — Concept C: Score-Decomposition-First (the CFM-transparent audit spine)

**Concept ID:** C · **Panel:** the patient timeline as the core clinical object · **Stance:** score-decomposition-first
**Design authority (fixed, non-negotiable):** dark-first default (ADR-0002-01); formal token scales as single source of truth (ADR-0005/0006, DES-C-03) incl. the added monospace family for tabular clinical values (DES-2-05 fix); Radix headless primitives for generic non-clinical behavior — Collapsible, Accordion, Tabs, Tooltip, Dialog (ADR-0012-01 "adopt a headless library for generic non-clinical concerns"); **ONE realtime push channel** (ADR-0017-01, DES-C-05, ADR-C-13); severity encoded as **color + icon + shape (+ text)**, never color alone (ADR-0013-01, WCAG 2.2 AA §1.4.1); WCAG 2.2 AA throughout.

---

## 1. Thesis (the deliberate divergence)

The other timeline concepts make the **24 h trend line** or the **what-changed delta feed** the hero, and treat the score as an opaque number that the trend merely plots. Concept C refuses that. Here the hero — the object the entire layout is built around — is the **score-component table**: the decomposition of MEWS / NEWS2 / qSOFA / SOFA into the individual parameters that produced the number, each with its raw value, its point contribution, its reference band, and its staleness age.

Everything else on the timeline is *derived from and arranged around* that decomposition:
- the **24 h trend** is the history of a decomposition (a stack of expandable chips, not a bare polyline);
- the **what-changed delta** is a *component-level* delta ("which parameter's points moved and by how much"), never a bald score delta;
- the **correlation explanation** is a link between two decompositions;
- the **SBAR handoff** is a decomposition rendered as prose.

Why this stance is the right divergence for an ICU CDS: the platform is legally **advisory only** — the physician remains responsible for the final clinical decision (VIS-C-08, VIS-8.3-01), alerts must be charted at NGS Level 2 (VIS-C-07, VIS-8.3-01), and the software is SaMD Classe II precisely *because* it does not diagnose or replace judgment (VIS-C-01). An advisory score that cannot be **audited on the spot** is a liability. A score you can expand into "RR 24 → +2 pts, SpO₂ 91 % → +2 pts, everything else 0" is one a clinician can trust, contest, or dismiss in seconds. Decomposition-first is CFM transparency made into the layout's backbone. It is also the single best antidote to alarm fatigue: the fastest way to kill a false positive is to *see the one artifactual component that caused it* (a slipped SpO₂ probe reading), and the fastest way to trust a true positive is to see the coherent cluster of components behind it.

This concept does **not** hedge toward trend-first or feed-first. The trend and the feed exist here only as views onto the decomposition.

---

## 2. Layout

One patient, one timeline, inside the standard app shell (PageContainer successor, ADR-0008-01). No persistent side nav; wayfinding is tile-drill-down + header context switcher + ONE persistent breadcrumb extended to full depth (leito → ocupação), fixing the legacy trail that never reached the deepest screens (ADR-0009-01, DES-4-02). Three regions:

### 2.1 The Score Spine (left, the time axis)
A vertical, most-recent-at-top time axis over the **24 h window by default** (Carlos's PER-CARLOS-03 / PER-C-03; Rafael's PER-RAFAEL-02), scrubbable and extendable (72 h / full-stay). The spine carries **parallel score lanes** — MEWS and NEWS2 (general deterioration, VIS-2-01/02) as the dominant pair, with qSOFA and SOFA (sepsis triage / organ dysfunction, VIS-2-03/04) as selectable lanes. Each recalculation event is a **score chip**, not a plotted point:

- chip = value in **tabular monospace** + severity band by the `clinical.*` scale as **color + icon + shape + text** (ADR-0013-01) + a **trend arrow** (↑ rising / → steady / ↓ falling) that is the delta vs the previous chip.
- chips are the primary interactive target: selecting one drives the center panel. The spine *is* the navigation; scrolling the spine is scrubbing time.
- score latency is honored — a chip appears < 30 s after its inputs land, via the one channel (PER-C-01, VIS-C-09).

A chip that was computed on **stale or missing** inputs is visibly caveated (§5), because a NEWS2 missing its consciousness component is not a valid NEWS2 and must not masquerade as one — a CFM-auditability requirement, not a nicety.

### 2.2 The Decomposition Panel (center, the payload — the stance signature)
Selecting/expanding a score chip opens its **component table** — the object this whole concept is built to serve. For the selected timepoint, one row per score component. For NEWS2 (Royal College of Physicians NEWS2): respiratory rate, SpO₂, air-or-oxygen, systolic BP, pulse, consciousness (ACVPU), temperature. For qSOFA the three catalog-defined components: RR ≥ 22 rpm, GCS ≤ 13, SBP ≤ 100 mmHg (CAT-SEP-002). Each row shows:

| column | content |
|--------|---------|
| **Component** | parameter name, PT-BR verbatim from the clinical vocabulary (e.g. "Frequência respiratória", "Nível de consciência") |
| **Value** | raw value + unit, tabular monospace; **abnormal values flagged by color + icon** against the reference band — fixing the top legacy gap where SpO₂ 60 % and 99 % rendered identically (ADR-0014-01, DES-C-06, DES-5-04) |
| **Points** | the points this component contributed to the score — the audit column |
| **Reference band** | the normal/mild/moderate/critical band the value falls in (severity scale, DES-C-06) |
| **Δ since prev** | the **what-changed delta**: did this component's points move vs the previous timepoint, by how much, direction — the components that *drove* the score change are highlighted |
| **Staleness** | age of the underlying measurement (e.g. "há 8 min"); a stale row is flagged, and a component with no data reads **"sem dado"**, never a silent zero |

Progressive disclosure is the core interaction: **chip → component table → per-component 24 h sparkline** (a third click on any row opens that parameter's own 24 h micro-trend). Radix `Accordion`/`Collapsible` supplies the expand/collapse mechanics; the table itself is a real semantic `<table>` (a large screen-reader and keyboard win of the table-first stance, §5/§7). The panel header states the score identity, its version/algorithm id (VIS-C-13, 100 %-auditable versioning), and the one-line "this is decision support; the physician decides" advisory (VIS-C-08).

**What-changed, decomposed.** Between two adjacent chips the panel foregrounds *the component(s) whose points changed* — e.g. "NEWS2 6 → 8: SpO₂ 96 % → 91 % (+2 pts); todos os outros componentes inalterados." This is the divergence from a feed-first concept: a delta here is always attributable to a named parameter, which is exactly what Ana asks for (PER-ANA-02, PER-C-04).

### 2.3 The Context Rail (right)
Three stacked, collapsible cards, all fed by the same timeline:

- **Correlations** — the exactly-three cross-domain correlations defined in the vision (VIS-4-03): Sepse + AKI ("sepse é #1 causa de AKI"), Respiratória + Hemodinâmica ("SDRA + choque"), Drogas + Eletrólitos ("QTc + K⁺/Mg²⁺"). When two score/domain lanes co-fire in-window, a **correlation band** links them on the spine and this card renders the plain-language explanation of *why* the two decompositions reinforce each other — advisory, cited, never a diagnosis (VIS-C-01, VIS-C-08).
- **Active alerts** — the engine alerts tied to this timeline, each showing its **triggering inputs** (which is just a decomposition of the alert's boolean), its severity/SLA band (CAT-C-02…05), and a **1-click acknowledge** that charts to NGS Level 2 (PER-ANA-03, VIS-C-07) via an optimistic patch reconciled against the authoritative record over the one channel (ADR-C-12). Only PPV-budgeted, deduped, suppressed alerts render — not the legacy 200/day at 80 % FP (PER-C-02, VIS-7.1-02).
- **SBAR handoff** — a one-action generator (§4) that assembles the timeline into Situation / Background / Assessment / Recommendation prose, exportable to hospital quality tools (PER-FERNANDA-03, PER-C-08).

Bed selection and deep secondary forms use the drawer-in-drawer pattern with a real **overlay-stack manager** — Esc/back closes only the topmost, per-level focus trap (ADR-0010-01, fixing the legacy no-coordination gap). No routed page change, no reload.

---

## 3. Progressive-disclosure density (one function, three depths)

Density is a **token-driven preference over one unit-tested density function** keyed on viewport width *and* explicit user choice, covering the full width domain with no gaps — closing the legacy `(2400px, 2800px]` dead-band and the two drifted bucket chains (ADR-0011-01, DES-C-04, ADR-C-07). Not a forked render tree.

| Depth | Persona / context | Spine | Decomposition | Rail |
|-------|-------------------|-------|---------------|------|
| **Collapsed** | Rafael en route on a phone; narrow breakpoint | dominant lane only, last 3–4 chips, current band + arrow | current score's decomposition **top-3 contributing rows** + what-changed line | SBAR + active alerts only |
| **Standard** | Ana/Carlos at a station | MEWS+NEWS2 lanes, 24 h chips | full component table + Δ column + staleness | all three cards |
| **Audit** | Carlos reviewing a critical event; Fernanda's retrospective quality review | all four lanes + correlation bands | full table + per-component sparklines expanded inline + algorithm-version line | all cards + correlation drawer |

All three depths are the same component contract at different disclosure levels — the decomposition never disappears, it only summarizes (top-3 rows) or fully expands (sparklines).

---

## 4. Interactions & role defaults

- **Expand a score** → Radix Collapsible reveals its component table (progressive disclosure step 1). **Expand a component row** → its 24 h sparkline (step 2). Keyboard: arrow-navigable spine, `Enter`/`Space` expands, focus-visible throughout.
- **Scrub time** — drag the spine or pick a window preset (24 h default, 72 h, full-stay). Selecting any historical chip re-decomposes at that timepoint — you can audit *why the score was 8 at 03:00*.
- **Acknowledge an alert** — one click on the rail alert (PER-ANA-03), optimistic + reconciled over the one channel (ADR-C-12), charted at NGS-2 (VIS-C-07).
- **Generate SBAR** — one action builds S = current dominant score + band; B = 24 h trajectory + the what-changed deltas; A = the live decomposition + correlations + active alerts; R = the advisory responses from the alert catalog (`response.required`, e.g. "avaliação médica beira-leito"), explicitly framed as advisory (VIS-C-08). Radix `Dialog` hosts preview + **export** (PER-FERNANDA-03, PER-C-08). This doubles as Rafael's < 1-min outcome documentation (PER-RAFAEL-03, PER-C-07).
- **Role defaults** — Ana/Rafael boot Collapsed→Standard with SBAR prominent; Carlos boots Standard; Fernanda boots Audit for review. Route/role gating is **deny-by-default** (ADR-C-05, DES-C-08); the client config is UX only, the API independently authorizes (ADR-C-14).

---

## 5. States

- **Loading** — content-shaped skeleton: skeleton chips on the spine, skeleton rows in the table. Never a full-viewport blocking spinner (ADR-0016-01, DES-5-07).
- **Stale / disconnected** — one channel, so loss is **loud, never silent** (the deliberate inverse of the legacy silent-poll where a red alert lagged the grid, DES-6-02, ADR-0017-01): a connection banner + per-**component** staleness age. A score chip computed on stale inputs carries a caveat marker; the responsible clinician sees *exactly which component is old*.
- **Missing component** — a score component with no data reads **"sem dado"** and the chip is flagged "score parcial", because a partial-input score is not a valid score — a patient-safety + CFM-audit requirement, not silently coerced to zero.
- **Empty timeline** — freshly admitted patient with < 1 computed score → explicit empty state noting first score pends first vitals set (VIS-6.1-04 inclusion echo).
- **Error / permission** — classified error (validation / permission / server) mapped to visual weight (inline / toast / modal), backend-shape-agnostic (ADR-C-11); permission-denied re-routes per deny-by-default (ADR-C-05).
- **Reduced motion / contrast** — chip-appearance and expand transitions are token-scaled and gated by `prefers-reduced-motion` (instant state change fallback); `prefers-contrast` flattens neumorphic elevation to a flat-shadow token; AA contrast verified in dark and light over embossed surfaces (ADR-C-04).

---

## 6. How each persona succeeds

**Dr. Carlos (intensivista).** The decomposition is his real-time deterioration audit: a rising MEWS/NEWS2 chip expands to show *which organ system is failing* before he opens the chart, and the what-changed line tells him it was SpO₂, not an artifact — real detection, not a nurse's hours-later hand calculation (PER-CARLOS needs_2l). Because he can dismiss an artifactual single-component spike in one glance and trust a coherent multi-component cluster, the surface holds his < 3 FP/patient-day bar and the PPV ≥ 60 % goal (PER-C-02, VIS-7.1-02). The 24 h spine is his trend view (PER-C-03); scores land < 30 s (PER-C-01, VIS-C-09); Audit depth gives per-component sparklines + the algorithm version for a defensible chart note (VIS-C-13).

**Enf. Ana (enfermeira).** MEWS/NEWS2 are computed automatically on every chip — zero manual calculation (PER-ANA-01, replacing 20 min/shift/patient). The component table is the literal answer to her core need: it **names the exact parameter that triggered** with its point contribution and reference band (PER-ANA-02, PER-C-04) — no other concept makes "which parameter?" the whole center panel. Alert acknowledgement is 1-click (PER-ANA-03). At shift change she generates the SBAR in one action from the same timeline.

**Dra. Fernanda (coordenadora).** Honest fit: the timeline is single-patient, so it is not her live floor dashboard — but it is her **case-review and quality instrument**. Audit depth lets her reconstruct a deterioration event component-by-component for M&M review, verify response-time SLA against the ≤ 15 min target on the alert-ack timestamps (PER-FERNANDA-02, VIS-7.1-03), and **export** the decomposed timeline + SBAR to hospital quality tools (PER-FERNANDA-03, PER-C-08). Her real-time occupancy/acuity dashboard (PER-FERNANDA-01) lives on the home/bed-grid surface, not here — a deliberate scope boundary, logged as a risk.

**Dr. Rafael (RRT).** The Collapsed depth *is* his phone view: the < 5 s critical-score push (PER-RAFAEL-01, PER-C-06, same one channel ADR-C-13) deep-links straight into the timeline showing the current band, the top-3 contributing components, and the what-changed line — so he knows *what is driving the crisis* before he arrives, not just that a number is high (PER-RAFAEL-02). Latest vitals + trend are the decomposition + spine, en route. On scene, the SBAR generator is his < 1-min outcome documentation (PER-RAFAEL-03, PER-C-07).

---

## 7. Risks & mitigations

1. **Decomposition overload / cognitive cost.** A full component table per timepoint can be heavier than a glanceable trend line. → Collapsed depth shows only top-3 contributing rows + the one what-changed line; full table and sparklines are opt-in disclosure; the spine alone (band + arrow) suffices for triage without ever expanding.
2. **Weak fit for Fernanda's live-floor need.** A single-patient timeline is not a real-time unit dashboard (PER-FERNANDA-01). → Explicit scope boundary: her live acuity/occupancy view is the bed-grid surface; here she is served for retrospective quality/case review and export. Stated, not solved on this surface.
3. **Invented point tables = clinical-safety risk.** Rendering a "Points" column demands the *correct* per-component point mapping for each score. → The decomposition renders only from the already-implemented, versioned scorers (VIS-2-01…04); qSOFA components are the catalog-defined cutoffs (CAT-SEP-002); NEWS2/MEWS/SOFA point tables come from their published definitions (RCP NEWS2; Subbe MEWS; Vincent SOFA) — never hand-authored here. Any component whose mapping is unverified is flagged for ratification, not displayed as fact.
4. **Partial / stale score masquerading as valid.** A score computed on a missing or old component could mislead a physician who is legally responsible for the decision (VIS-C-08). → "sem dado" + "score parcial" caveats are first-class states (§5); per-component staleness age is always visible; a stale chip is visibly marked. Loud, never silent (ADR-0017-01).
5. **Correlation explanations drifting toward diagnosis.** Plain-language "why these two co-fire" text risks reading as an automatic diagnosis, breaching SaMD Classe II scope (VIS-C-01). → Correlations are limited to the exactly-three vision-sanctioned pairs (VIS-4-03), each cited, each framed as advisory reinforcement with the "physician decides" banner (VIS-C-08); no free-text inference.
6. **Neumorphic paint cost on dense tables.** Embossed elevation across a long component table + sparklines is the exact scenario the audit flagged as costly (ADR-0007-01). → Elevation is a token; Audit depth flattens to a single flat-shadow token; `prefers-contrast` fallback; paint cost benchmarked before ship (ADR-C-04).
7. **Severity re-derivation vs. muscle memory.** New `clinical.*` hex may differ from legacy "red = crisis" reflexes (ADR-0013 open question). → Severity is triple-encoded color + icon + shape + text, so meaning survives any hue change and any color-vision profile; final hue set pending clinical sign-off, flagged ratification-blocked.
8. **Alarm fatigue via decomposition noise.** If every component flicker animates, the table re-creates legacy noise. → Only PPV-budgeted/deduped/suppressed alerts drive the rail; component rows update quietly (color + shape, no motion); the decomposition *reduces* fatigue by making dismissal of false positives instant (see §8).

---

## 8. Alarm-fatigue posture
The decomposition-first stance treats **auditability as the primary alarm-fatigue lever**: the fastest way to dismiss a false positive is to see the single artifactual component that produced it, and the fastest way to act on a true positive is to see the coherent component cluster behind it — so the timeline adds *explanation*, never alert volume, directly serving PPV ≥ 60 % (VIS-7.1-02), < 3 FP/patient-day (PER-C-02), and the ≤ 10 % alarm-fatigue goal (VIS-7.1-04), on top of the catalog's dedup/cooldown/rate-limit suppression.

## 9. Evidence trail
Personas PER-CARLOS/ANA/FERNANDA/RAFAEL + criteria PER-C-01…08 · ADR-0002 (dark-first) · ADR-0005/0006 + DES-C-03 + DES-2-05 (tokens, monospace for tabular values) · ADR-0007 + ADR-C-04 + DES-C-07 (neumorphic elevation, contrast) · ADR-0008/0009 (shell, IA/breadcrumb depth) · ADR-0010 (overlay-stack manager) · ADR-0011 + DES-C-04 + ADR-C-07 (one density function, no dead-band) · ADR-0012 (Radix headless for generic concerns) · ADR-0013 + ADR-C-08/09 (clinical severity color+icon+shape) · ADR-0014 + DES-C-06 + DES-5-04 (abnormal-value flagging) · ADR-0016 (skeleton vs spinner) · ADR-0017 + ADR-C-12/13 + DES-C-05/6-02 (one realtime channel) · ADR-0018 + ADR-C-05/14 (deny-by-default auth) · VIS-2-01…04 (implemented scores) · VIS-4-03 (the three correlations) · VIS-7.1-02/03/04 (PPV, response-time, alarm-fatigue goals) · VIS-C-01/07/08/09/13 (SaMD scope, NGS-2 charting, physician responsible, <30s latency, auditable versioning) · CAT-SEP-002 (qSOFA components) · CAT-C-02…05 (severity/SLA bands) · published scorers: RCP NEWS2, Subbe et al. MEWS (QJM 2001), Vincent et al. SOFA (Intensive Care Med 1996), Seymour et al. qSOFA (JAMA 2016).
