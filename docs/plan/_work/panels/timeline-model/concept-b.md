# Patient Timeline — Concept B: Event-Stream Spine

**Stance:** event-stream-first. The patient timeline is a **vertical, reverse-chronological
stream of discrete clinical events** — score-band crossings, alert fires, delta events (Δlactate,
ΔNa⁺, ΔQTc, ΔCr), med start/stop/escalations, lab results, KDIGO stage changes, RASS/CAM-ICU
transitions, and human actions (ack, intervention, outcome). **What changed** is the spine; the
event *is* the unit of the clinical object. Continuous 24h trend charts are **on-demand
disclosures anchored to an event** — you expand a score event to see its 24h line, you never
start from a wall of overlaid charts.

This concept deliberately commits to the *narrative-of-change* reading: the ICU day is a sequence
of transitions, and a clinician reasons "what is different since I last looked / since handoff"
far more often than "draw me the shape of the last 24 hours." It does **not** hedge toward a
trend-chart-first or a live-vitals-dashboard timeline — divergence is the point. Trends exist and
are one interaction away, but they are subordinate to the event that motivates looking at them.

---

## 1. Fixed design authority honored (non-negotiable)

- **Dark-first, token-driven** — one live-switchable token set, no full-reload light toggle, no
  runtime AntD recompile [DES-C-02, ADR-C-03]. Neumorphic dual-shadow elevation kept as a governed
  `elevation.*` token pair (event cards sit on embossed surfaces) with a flat-shadow fallback under
  `prefers-contrast`/paint budget [DES-C-07, ADR-C-04].
- **Radix primitives** for the generic shell — the stream is a Radix scroll/roving-tabindex list;
  event expansion uses Radix `Collapsible`; L3/L4 detail uses the one canonical dialog/drawer stack;
  tooltips/popovers are Radix. No second competing primitive [ADR-C-06].
- **One realtime channel** — new events arrive on the **same push transport** as the bed board and
  the notification bell, shared reconnect/backoff; **no `setInterval` polling** [DES-C-05, ADR-C-13].
  A realtime payload appends/patches a stream item or triggers a scoped refetch; the transport is
  never a second source of truth [ADR-C-12].
- **Severity = color + icon + shape**, never color alone; `clinical.*` scale structurally separate
  from tenant `brand.*` [ADR-C-08, DES-C-01]. Each event card's rail encodes severity redundantly.
  The two legacy severity bugs (hardcoded amber toast, hardcoded `VERMELHO` panel) are fixed, not
  ported [ADR-C-09]. `ASSISTIDO` blue override is modeled as an event state, not a color hack
  [DES-2-03].
- **WCAG 2.2 AA** contrast for all clinical text/values over neumorphic surfaces in both themes;
  tabular clinical numbers use a monospace token for scan-alignment [ADR-C-04].
- **Threshold-based abnormal-value flagging** on every value shown in an event card, sourced from
  the alert catalog thresholds — the legacy "no flagging anywhere" baseline is a gap to close, not
  to replicate [DES-C-06, ADR-0014-01].
- **CFM/SaMD posture** — every alert event is a record in the prontuário at NGS Level 2 [VIS-C-07];
  events are advisory, the physician owns the decision [VIS-C-01, VIS-C-08]; each event card carries
  the **auditable algorithm version** that produced it [VIS-C-13].

---

## 2. Layout

### 2.1 The timeline surface (L3 for one patient/ocupação)

Reached from a bed tile, a deep-linked push, or a coordinator drill-down. The shell (context
switcher + full-depth breadcrumb `… ▸ Leito 12 ▸ Ocupação`) stays mounted above it [ADR-0008-01,
ADR-0009-01]. Three regions, stream-dominant:

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ PATIENT RAIL (sticky)                                    │  NOW STRIP (sticky)  │
│ Leito 12 · Ana P. · 67a · ♀ · LOS 4d                     │ MEWS 6 ▲  NEWS2 7 ▲  │
│ ⬢ CRÍTICO (worst active)   [ SBAR handoff ]  [ 24h ▾ ]   │ qSOFA 2  SOFA 9      │
│ MicroIndicadores: noradrenalina · VM · sedação · HD      │ ⟳ live · lab 8m atrás│
├───────────────────────────────────────────────────────────────────────────────┤
│ EVENT STREAM (reverse-chronological, the spine)                                 │
│                                                                                 │
│  ▌⬢ 09:14  qSOFA 1→2  •  Δlactato +0.7 mmol/L/h (2.4→3.8)   [detalhe ▾][ack ✓] │  ← delta event
│  ▌◆ 09:02  Noradrenalina 0.30→0.48 µg/kg/min (+60%)         [detalhe ▾][ack ✓] │  ← med escalation
│  ▌◆ 08:40  🔗 Correlação: Sepse + AKI — KDIGO 1→2 sob sepse  [por quê? ▾]      │  ← correlation
│  ▌▲ 08:31  Creatinina 1.6→2.1 mg/dL (basal 0.9) · KDIGO 2   [detalhe ▾]        │  ← lab + score
│  ▌● 08:05  ✅ Ana ackou SEP-002 · "avaliação à beira-leito"  (assistido)        │  ← human action
│  ▌⬢ 07:52  ALERTA SEP-002 qSOFA≥2 + lactato ↑  (v2.3.1)     [detalhe ▾][ack ✓] │  ← alert fire
│  ─────────  07:00  ── início do plantão / handoff ──────────────────────────    │  ← shift marker
│  ▌○ 06:10  MEWS 4→3  (melhora)                                                   │
│  … infinite scroll, day dividers, "carregar turno anterior"                     │
└───────────────────────────────────────────────────────────────────────────────┘
```

- **Patient rail (sticky left / top on mobile)** — identity, worst active acuity glyph, LOS,
  MicroIndicadores (PT-BR verbatim: noradrenalina, ventilação mecânica, sedação, hemodiálise, tempo
  de internação, mortalidade esperada %) [DES-3-05]. Two buttons: **SBAR handoff** (§2.4) and a
  global **24h ▾** that overlays every trend at once *only if explicitly requested* — the escape
  hatch for the trend-first reader, never the default.
- **Now strip (sticky right / top)** — the current values of the four scores with their **band
  arrow** (▲ rising, ▼ falling, = stable vs. previous), plus the realtime status chip and the
  **staleness clock** of the oldest load-bearing input. This is the only always-on "state" surface;
  everything else is change.
- **Event stream** — the spine. Each event is a card on a severity rail; newest at top; day/shift
  dividers; infinite scroll back through the stay ("carregar turno anterior").

### 2.2 Event card anatomy (the unit of the object)

Every card, densest info on the left glance path:

- **Severity rail + glyph** — left border + leading glyph via `clinical.*`: **color + icon +
  shape** (crítico = filled octagon ⬢; urgente = triangle ▲; atenção = diamond ◆; normal = circle
  ●; melhora = hollow circle ○; `ASSISTIDO` = blue ring override when the event is being handled)
  [DES-2-02, DES-2-03].
- **Timestamp** (monospace) — event clock time; relative age on hover.
- **What-changed headline** — the delta, verbatim and quantitative: `qSOFA 1→2`,
  `Creatinina 1.6→2.1 mg/dL (basal 0.9)`, `Noradrenalina 0.30→0.48 µg/kg/min (+60%)`. The `from→to`
  and the signed magnitude are **first-class text**, never buried in a chart the user must eyeball.
- **Triggering parameter** — for alert events, the exact parameter that fired is *in the headline*
  (Ana's hard requirement) — "SEP-002 qSOFA≥2 + lactato ↑" [PER-ANA-02, PER-C-04].
- **Abnormal-value flag** — each value carries the shared normal/atenção/moderado/crítico band
  (color+icon+shape) from catalog thresholds, not invented here [DES-C-06; CAT-SEP-002, CAT-ELY-001].
- **Provenance chips** — source (FHIR Observation / MedicationAdministration / lab), and for alerts
  the **algorithm version** (`v2.3.1`) for auditability [VIS-C-13].
- **Actions** — `[detalhe ▾]` (in-place progressive disclosure, §2.3) and, for actionable alerts,
  **1-click ack** directly on the card [PER-ANA-03, PER-C-05].

### 2.3 Progressive disclosure — score components & trend on demand

Disclosure is **in-place expansion of an event**, not navigation. Three depths per event:

| Depth | Trigger | Reveals |
|-------|---------|---------|
| **E0 collapsed** | default | rail + timestamp + what-changed headline + triggering parameter + ack |
| **E1 `detalhe ▾`** | click / Enter | **score-component breakdown** — the sub-scores that summed to the value (e.g. MEWS: FR +2, PA +1, FC +1, Temp +0, consciência +1 → 6; NEWS2 per-parameter points; SOFA per-organ points), each row flagged by its own band; the alert's threshold + evidence citation; the **prior value + timestamp** that anchored the delta |
| **E2 `24h ▾` on the expanded event** | click | the **on-demand 24h trend line** for *that one parameter/score*, drawn inline under the event, with the event marked on it — trend as the answer to "is this a blip or a slope?", summoned by the change, not the frame |

This is the concept's core inversion: **the number-and-its-decomposition come first; the curve is
summoned by the event.** Score-component disclosure [MEWS/NEWS2/SOFA/qSOFA — VIS-2-01..04] lives at
E1 so a clinician sees *which organ/parameter drove the score* before deciding to look at shape.

### 2.4 SBAR handoff view — a projection of the stream

Because the object is already a chronological narrative of change, the **SBAR** view is a
*deterministic projection of the same event stream*, not a separate hand-authored screen — the
strongest argument for event-stream-first:

- **S (Situação)** — current worst acuity, active unacked alerts, now-strip scores with arrows.
- **B (Background)** — admission event + the stay's pinned milestones (intubação, início de
  vasopressor, TRS, mudanças de estágio KDIGO) auto-selected from event severity/kind.
- **A (Avaliação)** — the **since-last-handoff delta digest**: every band crossing and delta event
  since the last `início do plantão` marker, plus active **correlations** (§2.5).
- **R (Recomendação)** — pending actions: unacked alerts, overdue re-evaluations (e.g. CAM-ICU
  não registrado >24h [CAT-DEL-004]), and safety flags (e.g. ΔNa⁺ approaching the 10 mmol/L/24h
  ceiling [CAT-C-01]).

SBAR is filterable to a shift window and exportable to hospital quality tools [PER-C-08]; each item
deep-links back to its source event. Building the handoff costs the clinician nothing to author —
it is the stream, re-projected.

### 2.5 Correlation events — explained inline

The three vision correlations are **first-class stream events**, not a side panel [VIS-4-03]:
(1) Sepse + AKI ("sepse é #1 causa de AKI"); (2) Respiratória + Hemodinâmica ("SDRA + choque");
(3) Drogas + Eletrólitos ("QTc + K⁺/Mg²⁺"). A correlation event renders with a 🔗 glyph and a
**`por quê? ▾`** disclosure that names the two contributing domains, the two source events (each a
back-link into the stream), and the plain-language clinical rationale. Because both contributing
events already exist on the spine, the correlation is *anchored to what the clinician can see* — no
opaque black-box score. Advisory only; physician owns the call [VIS-C-01, VIS-C-08].

### 2.6 Staleness as an event and a state

Two complementary treatments — a divergence strength of event-stream-first:
- **State** — the now-strip staleness clock shows the age of the oldest load-bearing input per
  score; if it exceeds an input's `staleness_max`, the score value is visibly marked *stale* (dimmed
  + ⧗ glyph), never silently shown as current [DES-6-02, ADR-0017-01].
- **Event** — a **gap in expected cadence becomes its own stream card** ("Sem gasometria há 6h",
  "Sem RASS registrado há 8h"): absence of data is itself a clinical change worth surfacing, which a
  trend chart (which just flatlines or stops) cannot express. This directly serves the Δ-based
  alerts whose baselines depend on a prior value existing [vision open-question on lookback anchors].

---

## 3. States

- **Loading** — content-shaped skeleton *cards* (event-shaped, not generic bars); patient rail +
  now strip render immediately from cached context [ADR-0016-01].
- **Fresh admission / sparse stream** — few events; explicit "início da internação" anchor card so
  an empty stream reads as *new patient*, not *broken feed*.
- **Normal / improving** — melhora events (hollow circle ○, e.g. `MEWS 4→3`) are shown, not hidden:
  improvement is a change too, and matters at handoff.
- **Active alert** — severity rail by the event's own severity; multiple simultaneous fires are
  separate cards, but a burst from one dedup key collapses to one card with a "×N" count (suppression
  applied upstream) so the stream shows *actionable change*, not raw volume.
- **ASSISTIDO** — once an alert event is acked, a linked human-action card appears and the original
  alert's rail switches to the blue `assistido` override, mirroring `statusTrilha` semantics so a
  handled event reads differently from an open one [DES-2-03].
- **Stale / reconnecting** — now-strip chip + dimmed stale scores + explicit "Sem dados há N min"
  gap cards; no silent divergence between bell, grid, and timeline [ADR-C-13].
- **Permission-gated** — a patient the user cannot see is absent; enforcement is deny-by-default and
  server-side, the client is defense-in-depth only [ADR-C-05, ADR-C-14].

---

## 4. How each persona succeeds

### 4.1 Dr. Carlos — Médico Intensivista (20-bed adult ICU)
On round he opens a patient and reads **top-down through change**: the newest cards tell him what
moved since he last looked — `qSOFA 1→2`, `Δlactato +0.7/h`, `noradrenalina +60%` — each with the
triggering parameter inline and score value <30s after collection surfaced in the now-strip
[PER-C-01]. He expands one event to **E1** to see the score-component decomposition (which parameter
drove MEWS/NEWS2, which organ drove SOFA) and, only when he needs shape, pulls the **E2 24h trend**
for that one parameter [PER-CARLOS-03, VIS-2-01]. High-specificity suppression keeps the stream to
actionable change, not the 200-alerts/80%-FP world [PER-C-02]. **Wins:** "what changed since round"
is the literal top of the screen; 24h trend is one expansion deep, summoned by the event that
warrants it.

### 4.2 Enf. Ana — Enfermeira de UTI (4–5 patients)
Every alert card shows the **triggering parameter in the headline** — "SEP-002 qSOFA≥2 + lactato ↑",
"FR 24 rpm" — so she never hunts for *what* fired [PER-ANA-02, PER-C-04]. Scores are auto-calculated
and shown in the now-strip and on each score event; she does **zero** manual math [PER-ANA-01,
PER-C-03]. She acknowledges/logs a response in **1 click** on the card, which drops a linked
human-action event and flips the alert to `assistido` [PER-ANA-03, PER-C-05]. The **gap events**
("Sem RASS há 8h") tell her what documentation is owed before it becomes an escalation. **Wins:**
the "which parameter?" answer is the headline; logging is 1 click and visibly closes the loop.

### 4.3 Dra. Fernanda — Coordenadora de UTI (30 beds, adult/coronary/neonatal)
Fernanda lives on the bed board, but for any bed she drills into, the timeline gives her the
**SBAR handoff view** as an instant, deterministic case summary — no clinician had to author it —
and the **since-last-handoff delta digest** is exactly her quality lens: she reads response latency
(alert event → ack event timestamp) as her KPI [PER-FERNANDA-02, VIS-7.1-03], and the whole stream
plus SBAR is exportable to hospital quality tools [PER-C-08, PER-FERNANDA-03]. Correlation events
let her audit *why* a deterioration cascaded across domains. **Wins:** a free, standardized case
narrative per patient; response-time and cascade evidence backed by timestamped events, not
perception.

### 4.4 Dr. Rafael — Equipe de Resposta Rápida (mobile, hospital-wide)
A critical-score push (<5s) **deep-links straight to the patient timeline**; the shell reconstructs
the full breadcrumb so he sees **location** (Estabelecimento ▸ Setor ▸ Leito) as wayfinding en route
[PER-RAFAEL-01, PER-RAFAEL-02]. On the phone the stream is the single-column native shape — no
chart-wall to pan — so the last few *changes* (latest vitals as events, the delta that fired) load
first and read while moving; he taps **SBAR** for the 15-second story before he arrives. Outcome
documentation is a linked human-action card reachable in one tap, completable in <1 minute
[PER-RAFAEL-03, PER-C-07]. **Wins:** the event stream is inherently mobile-first (a list, not a
canvas); deep-link + breadcrumb turn a push into oriented arrival; SBAR is the pre-arrival brief.

---

## 5. Risks (and mitigations)

1. **Trend-first clinicians feel deprived of the 24h chart.** Some read shape first. *Mitigation:*
   the global **24h ▾** in the patient rail overlays all trends on demand, and every event has an
   E2 inline trend — trends are one interaction away, never removed. Validate the default framing
   with Carlos; this is the biggest divergence risk vs a trend-first concept A.
2. **Stream volume / scroll fatigue.** A busy patic can generate many events. *Mitigation:*
   upstream dedup/cooldown/rate-limit before a card ever renders; burst collapse ("×N"); severity
   and kind filters; shift dividers; improvement events are visually quiet (hollow glyph). Depends
   on suppression being enforced upstream [VIS-7.1-04 target ≤10% ignored].
3. **Losing the "current state at a glance."** A pure change-log could obscure *where the patient
   is now*. *Mitigation:* the sticky now-strip is the always-on state surface; SBAR-S restates the
   current situation. The stream is change; the strip is state; both are always visible.
4. **Delta events depend on a prior value that may not exist.** Baseline-anchor lookback is
   under-specified in the vision [vision open question]. *Mitigation:* absence becomes an explicit
   gap event rather than a silently missing delta; the E1 disclosure always names the prior value +
   timestamp it compared against, or says "sem valor anterior".
5. **Correlation events as black boxes.** A cross-domain link could read as an opaque score.
   *Mitigation:* `por quê?` always names both contributing source events (back-linked) and the
   rationale; advisory only, physician decides [VIS-C-01].
6. **SBAR projection drift from bedside reality.** An auto-projected handoff could omit nuance.
   *Mitigation:* SBAR items deep-link to source events for verification; the clinician can pin/annotate;
   it augments, never replaces, the handoff conversation.
7. **Realtime single-channel dependency.** One channel is a single point of failure. *Mitigation:*
   shared reconnect/backoff + explicit stale state + gap events; the stream never silently shows old
   data [ADR-0017-01, ADR-C-13].

---

## 6. Alarm-fatigue posture

Event-stream-first is *structurally* calmer for the reader: one card per actionable change (not one
per raw alert), burst-collapse by dedup key, severity encoded redundantly (color+icon+shape),
improvement events visually quiet, and the newest-change-on-top ordering means the eye lands on the
few things that moved — but this only holds if dedup/cooldown/rate-limit are enforced **upstream**
before a card renders, and if the now-strip absorbs steady-state so the stream carries only
transitions [VIS-7.1-04 target ≤10% ignored].

---

## 7. Accessibility notes

Severity always color **+ icon + shape** (never color alone); WCAG 2.2 AA contrast for all clinical
values over neumorphic surfaces in both dark and light, with a flat-shadow `prefers-contrast`
fallback; the stream is a keyboard-navigable roving-tabindex list (↑/↓ between events, Enter to
expand E1/E2, `Esc` collapses); each event card is an ARIA article with an accessible name built
from its what-changed headline; the SBAR view is a landmark-structured document; tabular clinical
numbers and `from→to` deltas use a monospace token for scan-alignment [ADR-C-04, ADR-C-08,
ADR-0010-01].
