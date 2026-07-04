# Home Surface — Concept B: Drill-Down Workstation

**Stance:** drill-down-workstation-first. The home surface is a *spatial* bed-grid
workstation you enter by drilling **down the org hierarchy** (empresa ▸ estabelecimento ▸
setor ▸ leito/ocupação), not an alert feed you triage top-down. Every screen keeps a
**persistent unit/tenant context switcher** (lateral movement) and a **single full-depth
breadcrumb** so no view is ever a dead end. Bed detail is reached by **progressive
disclosure** — glance → peek → drawer → drawer-in-drawer — never a full page reload.

This concept deliberately commits to the space-first reading of ADR-0009 (keep tile
drill-down + header switcher; one reusable full-depth breadcrumb) [ADR-0009-01]. It does
**not** hedge toward an alert-inbox or single-patient-focus home; divergence is the point.

---

## 1. Fixed design authority honored (non-negotiable)

- **Dark-first, token-driven** — one live-switchable token set, no full-reload light
  toggle, no runtime AntD recompile [DES-C-02, DES-C-03, ADR-C-03]. Neumorphic dual-shadow
  elevation kept as a governed `elevation.*` token pair, with a flat-shadow fallback under
  `prefers-contrast`/paint budget [DES-C-07, ADR-C-04].
- **Radix primitives** for the generic non-clinical shell (dropdown context switcher,
  breadcrumb, dialog/drawer stack, tabs, tooltip) — one canonical implementation each,
  no second competing primitive [ADR-C-06].
- **One realtime channel** — bed tiles, scores, and the notification bell subscribe to the
  same push transport with shared reconnect/backoff; **no `setInterval` polling** of the
  bed board [DES-C-05, ADR-C-12, ADR-C-13]. Realtime payloads patch the tile or trigger a
  refetch; the transport is never a second source of truth.
- **Severity = color + icon + shape**, never color alone; `clinical.*` scale structurally
  separate from tenant `brand.*` [ADR-C-08, DES-C-01]. The two legacy severity bugs
  (hardcoded amber toast, hardcoded `VERMELHO` panel) are fixed, not ported [ADR-C-09].
- **WCAG 2.2 AA** contrast for all clinical text/status over neumorphic surfaces in both
  themes [ADR-C-04].
- **Threshold-based abnormal-value flagging** on tiles and in drawers — the legacy "no
  flagging anywhere" baseline is a gap to close, not to replicate [DES-C-06, ADR-0014-01].

---

## 2. Layout

### 2.1 App shell (persistent across every depth) — extends ADR-0008 PageContainer

A single shell row, always mounted, tenant context backed by a shared cache keyed on route
IDs (no per-mount cascading refetch) [ADR-0008-01]:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ [logo] │ CONTEXT SWITCHER  Empresa▾  Estabelecimento▾  Setor▾ │ density: ▣▤▦ │ 🟢live │ 🔔3 │ 👤│
│ BREADCRUMB:  Grupo AUSTA ▸ Hospital AUSTA ▸ UTI Adulto ▸ (Leito 12 ▸ Ocupação) │
├──────────────────────────────────────────────────────────────────────────────┤
│  ACUITY SUMMARY BAR   ● 2 crítico  ▲ 3 urgente  ◆ 5 atenção  ● 12 normal  ▢ 4 vago │
│                                                                                │
│  BED GRID  (density-driven column span)                                        │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                          │
│  │Leito 01│ │Leito 02│ │Leito 03│ │Leito 04│ │Leito 05│  … acuity-sorted        │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

- **Context switcher** = three Radix dropdowns (empresa / estabelecimento / setor). Each
  option carries a unit-level acuity badge (worst active severity in that unit), so a
  coordinator sees a critical bed on an *unopened* unit before switching into it. Switching
  a level is **lateral movement** that preserves current depth where meaningful. A tenant
  (empresa) switch re-resolves the `brand.*` primary color once, server-side, before paint
  — no flash-of-default-orange [ADR-C-01]. `clinical.*` never changes with tenant.
- **Breadcrumb** = one reusable component in the shell, ARIA `nav` landmark, extended to
  **full depth** including `leito` and `ocupação` — the exact segments the legacy trail
  never reached [ADR-0009-01]. Every segment is a link (lateral/upward jump). This replaces
  the hand-built Tag trail and retires the dead `Breadcrumbs` component [DES-3-06].
- **Density toggle** = three modes (§2.3), persisted per user+role.
- **Realtime status chip** — explicit `live / reconnecting / stale` state; a stale grid is
  visibly marked, closing the legacy bell-vs-grid disagreement [DES-6-02, ADR-0017-01].

### 2.2 Bed tile anatomy (the unit of the grid)

Each tile is one `leito`/`ocupação`. Progressive-disclosure **level L1**. Contents, densest
information at the top-left glance path:

- **Acuity band** — left border + corner glyph encoding worst active severity via
  `clinical.*`: **color + icon + shape** (critical = filled octagon; urgente = triangle;
  atenção = diamond; normal = circle; **ASSISTIDO** = blue ring override when
  `assistido===true`, mirroring `statusTrilha` semantics) [DES-2-02, DES-2-03].
- **Bed identity** — `Leito NN`, patient name, age, sex icon.
- **Top active alert with its triggering parameter shown at tile level** — e.g.
  "FR 24 rpm" or "SpO₂/FiO₂ 210" — so the parameter that fired is legible **without**
  opening the drawer (Ana's hard requirement, §4.2) [PER-ANA-02, PER-C-04].
- **Latest score + 24h sparkline** — MEWS/NEWS2 value in a **monospace/tabular** token,
  with an inline 24h trend sparkline [VIS-2-01, VIS-2-02, PER-CARLOS-03].
- **MicroIndicadores row** (PT-BR verbatim) — noradrenalina, ventilação mecânica, sedação,
  hemodiálise, tempo de internação (LOS), mortalidade esperada % [DES-3-05].
- **Ack affordance** — a single control that acknowledges the top alert in **1 click**
  from the tile, without opening anything [PER-ANA-03, PER-C-05].
- **Abnormal-value flagging** — vitals/labs shown on the tile carry the shared
  normal/atenção/moderado/crítico band (color+icon+shape), sourced from the alert catalog
  thresholds, not invented here [DES-C-06; e.g. CAT-SEP-002, CAT-ELY-001].

### 2.3 Three density modes (the required three modes)

One token-driven column-span function covering the **full** viewport-width domain with no
gaps — the legacy `(2400px, 2800px]` dead-band must not recur [ADR-C-07, DES-4-05]:

| Mode | Name (PT-BR) | Tile size | Beds/screen | Primary user | What it shows |
|------|--------------|-----------|-------------|--------------|---------------|
| **D1** | **Leito** (conforto) | large | ~8–15 | Carlos / Ana at a bedside workstation | full tile: score+sparkline, all MicroIndicadores, triggering parameter, ack |
| **D2** | **Setor** (compacto) | medium | ~20–30 | Carlos reviewing a whole 20-bed ICU | condensed MicroIndicadores, score+glyph, triggering parameter |
| **D3** | **Central** (mural) | tile→acuity chip | whole unit / multi-unit wall | Fernanda, occupancy/acuity at a glance | acuity glyph + bed id + top-alert glyph + occupancy heat; a true command-center wall view |

Density is orthogonal to breakpoint: the shared function takes `(viewportWidth, densityMode)`
→ span, unit-tested across the full width domain. D3 downgrades neumorphic shadows to the
flat-shadow token to keep paint cost bounded on a large wall monitor [ADR-0007-01].

### 2.4 Progressive disclosure ladder

| Level | Trigger | Surface | Content |
|-------|---------|---------|---------|
| **L0** | land on setor | bed grid | acuity summary bar + tiles |
| **L1** | — | bed tile | glanceable acuity, score, triggering parameter, ack |
| **L2** | hover / keyboard focus | Radix popover | latest full vitals set + top-3 active alerts, read-only peek |
| **L3** | click tile / Enter | bed drawer | 24h score & vitals trends, per-alert detail (which parameter, threshold, evidence), 1-click actions, alert history |
| **L4** | action in L3 | drawer-in-drawer | clinical form engine (`FormDadosProntuario`), prescrição, balanço hídrico [DES-3-03] |

The L3/L4 overlay stack is owned by **one overlay-stack manager**: `Esc`/back closes only
the topmost; each level is focus-trapped; the breadcrumb updates to reflect L3 depth
(`… ▸ Leito 12 ▸ Ocupação`) [ADR-0010-01]. No level triggers a page reload.

---

## 3. States

- **Loading** — content-shaped skeleton grid (tile-shaped, not generic bars); shell +
  breadcrumb render immediately from cached context [ADR-0016-01].
- **Empty bed (`vago`)** — explicit distinct treatment (dashed neutral outline + "Vago"
  label), **not** the legacy flat `#212433` border that was indistinguishable from an
  occupied NEUTRO bed [DES-5-03].
- **Occupied — normal** — NEUTRO green circle, no alert glyph.
- **Occupied — active alert** — acuity band by worst severity; multiple alerts collapse to
  the single worst glyph on the tile, full list at L2/L3. Suppression/dedup already applied
  upstream so the tile shows *actionable* state, not raw alert count.
- **ASSISTIDO** — blue override ring when the bed's alert is being handled, mirroring the
  `statusTrilha` `assistido` override so a bed under active response reads differently from
  an unhandled one [DES-2-03].
- **Realtime stale/reconnecting** — grid dims + `stale` chip; no silent divergence.
- **Permission-gated** — beds/units the user lacks permission for are absent from the
  switcher and grid; enforcement is deny-by-default and server-side, the client grid is
  defense-in-depth only [ADR-C-05, ADR-C-14].

---

## 4. How each persona succeeds

### 4.1 Dr. Carlos — Médico Intensivista (20-bed adult ICU)
Arrives 07h; the shell restores his last context (Hospital AUSTA ▸ UTI Adulto) from cached
route IDs, lands directly on his 20-bed grid in **D2 (Setor)** density, **acuity-sorted** so
the sickest beds are top-left. He scans crítico/urgente beds first, clicks a tile → **L3
drawer** with the **24h score trend** and the per-alert detail showing exactly which
parameter fired and against which threshold [PER-CARLOS-03, VIS-2-01]. High-specificity
sort + suppression keep him from the 200-alerts/day/80%-false-positive world; he acts on the
few acuity-ranked beds. Between procedures he re-enters via the persistent breadcrumb.
**Wins:** score <30s after collection surfaced on the tile [PER-C-01]; ≥3 FP/day suppressed
upstream, surfaced as *actionable* acuity only [PER-C-02]; 24h trend one click deep.

### 4.2 Enf. Ana — Enfermeira de UTI (4–5 patients)
Filters the grid to **"Meus leitos"** (her assignment) in **D1 (Leito)** density. Each tile
already shows the **triggering parameter at L1** — "FR 24 rpm", "SpO₂ 88%" — so she never
hunts for *what* fired [PER-ANA-02, PER-C-04]. MEWS/NEWS2 is auto-calculated and shown; she
does **zero** manual score math [PER-ANA-01, PER-C-03]. She acknowledges/logs a response in
**1 click** from the tile (or L3 for a fuller note) [PER-ANA-03, PER-C-05]. **Wins:** the
"which parameter?" question is answered before any drill-down; response logging is 1 click.

### 4.3 Dra. Fernanda — Coordenadora de UTI (30 beds, adult/coronary/neonatal)
Her home is **D3 (Central / mural)**: one wall view of **all** her units. The **acuity
summary bar** and per-unit acuity badges on the **context switcher** give real-time
occupancy + acuity across adult, coronária, and neonatal without opening each unit
[PER-FERNANDA-01]. She sweeps units via the switcher (lateral movement), reads the
occupancy/acuity heatmap, and the response-time KPI (avg alert→ack) is a first-class tile in
the summary bar — her quality indicator [PER-FERNANDA-02, VIS-7.1-03]. Unit data is
exportable to hospital quality tools [PER-C-08, PER-FERNANDA-03]. **Wins:** true real-time
multi-unit occupancy/acuity command center; capacity arguments backed by data, not
perception.

### 4.4 Dr. Rafael — Equipe de Resposta Rápida (mobile, hospital-wide)
Rafael is **not** expected to drill from the top on a phone. A critical-score push
notification **deep-links straight to L3** for that bed; the shell **reconstructs the full
breadcrumb** from the deep link, so he sees the patient's **location** (Estabelecimento ▸
Setor ▸ Leito) as wayfinding while en route [PER-RAFAEL-02]. On mobile the grid collapses to
a single-column acuity-sorted list (same tiles, responsive span), and L3 shows latest vitals
+ trend. Outcome documentation is an L4 form reachable in one action, completable in
<1 minute [PER-RAFAEL-03, PER-C-07]. **Wins:** <5s push [PER-C-06] lands him on the bed with
full-depth location context; the breadcrumb turns a deep-link into oriented navigation.

---

## 5. Risks (and mitigations)

1. **Drill-depth latency for mobile RRT.** A pure top-down hierarchy would be slow on a
   phone. *Mitigation:* push notifications deep-link straight to L3; the breadcrumb
   back-fills the path so hierarchy is *context*, not a required click sequence.
2. **Coordinator blind spot.** A bed-grid home could bury a critical alert on a unit that
   isn't currently on screen. *Mitigation:* acuity sort, acuity summary bar, and per-unit
   acuity badges on the context switcher surface worst-severity across *all* units; D3 mural
   shows the whole floor. This is the single biggest divergence risk vs an alert-inbox home
   and must be validated with Fernanda.
3. **Neumorphic paint cost at D3 on wall monitors.** Dual-shadow tiles ×100+ beds. *Mitigation:*
   D3 uses the flat-shadow elevation token; benchmark paint budget before ship [ADR-0007-01].
4. **Progressive disclosure hiding the triggering parameter.** If the parameter only lived
   in L3, Ana would fail. *Mitigation:* triggering parameter is a hard L1 (tile) element.
5. **Full-grid alarm saturation.** Showing every bed's alert can read as noise. *Mitigation:*
   §6; depends on upstream suppression/dedup being enforced before the tile.
6. **Density × breakpoint gap regression.** *Mitigation:* one unit-tested span function over
   the full width domain; no undefined band [ADR-C-07].
7. **Realtime single-channel dependency.** One channel is a single point of failure.
   *Mitigation:* shared reconnect/backoff + explicit `stale` state; grid never silently
   shows old data [ADR-0017-01].

---

## 6. Alarm-fatigue posture

Acuity-ranked tiles, one worst-severity glyph per bed (not one glyph per alert), a
**crítico-only filter**, and severity encoded redundantly (color+icon+shape) let the eye
land on the few actionable beds; realtime patches update state in place instead of
re-animating the whole grid each poll tick — but a full-grid home only stays calm if
dedup/cooldown/rate-limit are enforced **upstream** before a tile ever lights up
[VIS-7.1-04 target ≤10% ignored].

---

## 7. Accessibility notes

Severity always color **+ icon + shape** (never color alone); WCAG 2.2 AA contrast for all
clinical values over neumorphic surfaces in both dark and light, with a flat-shadow
`prefers-contrast` fallback; full keyboard drill-down (tile grid is a roving-tabindex
composite, L2 peek on focus, L3/L4 focus-trapped with `Esc` closing only the topmost); the
breadcrumb is an ARIA `nav` landmark; tabular clinical numbers use a monospace token for
scan-alignment [ADR-C-04, ADR-C-08, ADR-0010-01].
