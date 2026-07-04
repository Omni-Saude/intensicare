# Home Surface — Concept A: "The Monitor Wall"

**Panel:** bed-grid command center home surface · **Concept:** A · **Designer stance:** monitor-wall-first
**Primary persona anchor:** Dra. Fernanda (real-time occupancy/acuity across 30 beds)
**Deliberate thesis:** maximal glanceable density · severity choreography · zero navigation.

> Divergence note (for the judge panel): this concept commits hard to a wall-mounted, glance-from-across-the-room
> command surface. It does **not** hedge toward a click-to-drill workstation model or a mobile-first inbox. Where a
> stance costs a persona (Dr. Rafael on a phone), that cost is stated plainly, not softened. Fixed design authority is
> respected verbatim: dark-first (`ADR-0002-01`), formal tokens (`DES-C-03`, `ADR-0006-01`), Radix primitives, ONE
> realtime channel (`ADR-C-13`, `DES-C-05`), severity by color+icon+shape (`ADR-0013-01`, `ADR-0014-01`), WCAG 2.2 AA.

---

## 1. Concept in one paragraph

The home surface is not a menu that leads to the ICU — it **is** the ICU, rendered as one severity-choreographed grid
of bed tiles that a clinician reads the way an air-traffic controller reads a radar scope: from three metres away,
pre-attentively, without a single click. The legacy four-level drill (`empresa → estabelecimento → setor → leito`,
`DES-4-03`) collapses into **one grid + three density modes + inline expansion**. You do not *navigate* to detail; you
change *density*. Acuity is the layout: the sickest, least-attended beds physically rise to the eye's first fixation and
carry motion; attended and stable beds go quiet. This directly serves Fernanda's live occupancy/acuity mandate
(`PER-FERNANDA-01`) and makes the mission-critical bed board — today the *least* live view in the product
(`ADR-0017-01`, "LIFE-SAFETY risk") — the *most* live.

---

## 2. Layout

### 2.1 Persistent header (no side nav, no page chrome — `ADR-0009-01`)
A single fixed bar; everything here is a *filter or a mode*, never a route change (zero navigation):

- **Unit segment switcher** — `Todos · UTI Adulto · Coronariana · Neonatal` (Radix Segmented/ToggleGroup). Lateral
  context switch, not a drill (`DES-4-02` header-switcher pattern, kept). Selecting a unit re-scopes the grid in place.
- **Density mode control** — `Mural · Enfermaria · Foco` (Wall / Ward / Focus). Radix ToggleGroup, single-select.
  Auto-defaulted by viewport via the ONE unified responsive density function (`ADR-C-07`), user override persisted.
- **"Meus pacientes" filter** — a toggle that dims all beds except the signed-in nurse's 4–5 (`PER-ANA` load), on the
  same wall, no separate screen.
- **Acuity summary strip** — live counts per severity (`crítico N · urgente N · alerta N · assistido N`) using the
  canonical count-badge primitive (`ADR-C-06`; one implementation, not the legacy two). This is the alarm-fatigue
  pressure gauge and Fernanda's headline number.
- **Ocupação gauge** — occupied / total with the operational occupancy encoding (`DES-3-05`, DashboardCard gauge),
  now promoted to the governed severity tokens instead of the divergent `#FFAB00` literal (`DES-5-03` bug fixed).
- **Realtime freshness pill** — `ao vivo · reconectando · dados defasados (há Xs)`. Fixes the legacy silent-staleness
  gap where the grid could lag the bell by up to `tempo_atualizacao` seconds (`ADR-0017-01`, `DES-6-02`). One channel,
  one freshness truth.
- **Export snapshot** — one action to emit the current acuity/occupancy state to hospital quality tooling
  (`PER-FERNANDA-03`, `PER-C-08`).

The header carries the single persistent breadcrumb from `ADR-0009-01` (extended to full depth), but on the home
surface the trail root *is* home — depth only appears when a Focus card is open.

### 2.2 The bed grid (main region)
Tiles laid out by the **unified density/column-span function** (`DES-C-04`, `ADR-C-07`) across the full viewport domain
with **no dead band** (the legacy `(2400px, 2800px]` undefined-span bug, `DES-4-05`, must not recur). Column count is a
function of `(viewport width, density mode)`, shared between JS and CSS from one named breakpoint source. Tiles use the
neumorphic dual-shadow elevation as a **governed token pair** (`ADR-0007-01`, `DES-C-07`), with a flat fallback under
`prefers-contrast` and at Mural density (paint-cost budget, see Risk R3).

### 2.3 Reading order = acuity order (the choreography spine)
Within the active unit scope, tiles are **severity-weighted sorted** so the highest-acuity *unattended* beds occupy the
top-left F-pattern fixation zone. Bed number is always printed on the tile (spatial memory is preserved for staff who
know "leito 7"), but the *visual* stack is acuity-first. A stable, all-`NEUTRO` unit therefore renders as a calm grid;
a deteriorating unit visibly reorganizes toward the top-left.

---

## 3. Three density modes

| Mode | Target display | Beds visible | Per-tile content | Interaction |
|---|---|---|---|---|
| **Mural** (Wall) | Wall-mounted 3–5 m read | All beds in unit scope (30+) | Leito #, patient initials, **one** highest-severity token (color+icon+shape), worst current score (NEWS2/MEWS integer) + trend arrow, `MicroIndicadores` reduced to 2 max | Ambient; no per-tile clicks expected |
| **Enfermaria** (Ward) | Workstation default | ~8–16 | Above + top 2–3 active alerts, **24 h score sparkline** (`PER-CARLOS-03`), threshold-flagged deranged vitals (`ADR-0014-01`), full `MicroIndicadores` row (noradrenaline, ventilação mecânica, sedação, hemodiálise, LOS, mortalidade esperada — `DES-3-05`), one-click acknowledge | Hover reveals ack/assign; click → Foco |
| **Foco** (Focus) | Deep single-bed read, still on the grid | 1–3 (expanded inline, neighbors reflow — **not** a drawer) | Full vitals panel with reference-range flagging, 24 h trend charts, ordered alert list each showing its **triggering parameter** (`PER-ANA-02`), `Critérios` / care-pathway strip (`TabRecomendacoes`, `TrilhaInterativa` for Sepse/Profilaxia), inline acknowledge/escalate | Inline expand-in-place; Esc collapses |

Density is a **single control**, not navigation. Switching Mural→Foco does not change URL context or lose scroll/state
(a deliberate rejection of the legacy full-`reload()` and drawer-stack patterns, `DES-2-09`, `DES-4-04`). Deep secondary
work that genuinely exceeds an inline card (full prescrição, Balanço Hídrico entry, the config-driven form engine
`DES-3-03`) still opens through the governed overlay-stack manager (`ADR-0010-01`) — Focus does not pretend to hold
everything (see Risk R7).

---

## 4. Severity choreography (the differentiator)

### 4.1 Redundant encoding — never color alone (`ADR-0013-01`, `ADR-0014-01`, WCAG 2.2 AA 1.4.1)
Every severity level is carried by **four** simultaneous channels so the wall is legible to color-vision-deficient
staff, at distance, and to screen readers:

| Clinical scale (`clinical.*`) | Catalog sev / SLA (`CAT LEGEND-SEV`) | statusTrilha term (verbatim, `DES-2-02`) | Color token | Shape | Motion (unattended only) |
|---|---|---|---|---|---|
| `critical` | CRIT · ação < 5 min | **VERMELHO** | `clinical.critical` | filled octagon (stop) | slow pulse ring |
| `urgent` | URG · ação < 30 min | **LARANJA** | `clinical.urgent` | filled triangle | single attention sweep on arrival |
| `watch` | WARN · ação < 2 h | **AMARELO** | `clinical.watch` | filled diamond | none |
| `info` | INFO · ação < 6 h | (AMARELO, low) | `clinical.info` | hollow diamond | none |
| `normal` | — | **NEUTRO** | `clinical.normal` | hollow dot | none |
| *attended override* | — | **ASSISTIDO** | `clinical.assisted` | ring + check | motion **suppressed**, tile desaturated |

Color hexes are **not invented here**: they are promoted from the legacy `statusTrilha` table (`DES-2-02`) into
contrast-checked `clinical.*` tokens, structurally separate from tenant `brand.*` (`ADR-C-08`, `DES-C-01`). Final
re-derived hex needs clinical sign-off (`ADR-0013` open question — "red bed = crisis" muscle memory). Motion durations
reference named `motion.*` tokens pending the token pass (`ADR-0006-01` open question) — no literal ms invented.

### 4.2 The choreography rules (alarm-fatigue is a design lever, not an afterthought)
1. **Only unattended criticals animate.** A `critical` bed pulses until someone acknowledges/assigns it; on ACK it snaps
   to **ASSISTIDO** (`assistido===true` override, `DES-2-03`) — desaturated, motion stilled. The wall thus shows *"what
   is on fire and no one is holding"*, which is the number that matters, not raw red count.
2. **New-critical entrance.** A bed crossing into `critical` performs one border sweep + reorders into the fixation zone;
   a `polite`/`assertive` live-region announces it (§6). Entrances are rate-limited by the catalog's dedup/cooldown
   (`suppression.cooldown`, `rate_limit` in the alert schema) so one patient can't strobe the wall.
3. **One token per tile in Mural.** A bed with 6 active alerts shows its single worst severity + a `+5` count badge, not
   six markers — density without noise.
4. **Assisted-decay.** ASSISTIDO tiles fade one elevation step, keeping attention budget on the unheld.
5. **Empty ≠ sick.** `vazio / reservado / higienização` bed states get their own neutral chrome, fixing the legacy bug
   where an empty bed and a `NEUTRO` occupied bed were distinguishable only by content (`DES-5-03`).

This choreography is the concept's answer to `VIS-7.1-04` (alarm fatigue ≤ 10%) and `PER-C-02` (< 3 false
positives/patient-day): the surface makes *un-actioned severity* loud and *held/stable* severity quiet.

---

## 5. States (exhaustive)

**Bed states:** `vazio` · `reservado` · `higienização/turnover` · occupied-`normal` · occupied-`watch` ·
occupied-`urgent` · occupied-`critical` · **ASSISTIDO** (attended override) · `dados defasados` (per-tile stale) ·
`em transferência/alta`.

**Alert states on a tile:** none · single · multiple (worst + `+N` badge) · acknowledged→ASSISTIDO · suppressed
(cooldown active, shown as a muted dot) · escalated (RRT paged).

**Realtime states (whole surface):** `ao vivo` · `reconectando` (shared backoff, `ADR-C-12`) · `defasado` (last-updated
timestamp shown, tiles get a freshness veil) · `offline`. All driven by the ONE channel so bell, grid, and summary can
never disagree (`ADR-C-13`).

**Loading:** content-shaped skeleton grid (`ADR-0016-01`) — never the legacy full-viewport blocking `FadeLoading`
(`DES-5-07`), because staff must keep reading other beds while one loads.

**Partial failure:** a bed that fails to hydrate shows a per-tile inline error with retry — not a screen-wide
`Modal.error` (`ADR-C-11`, `DES-5-07`). The wall degrades gracefully.

**Empty results:** no beds in unit / filter yields none → calm empty-state card, not an error.

**Density transition:** reflow is animated with `motion.reflow`, suppressed under `prefers-reduced-motion`.

---

## 6. Accessibility (WCAG 2.2 AA — `ADR-C-04`)

- Severity never by color alone: color + domain icon + shape + a text label on every tile (§4.1).
- Contrast: all clinical text/score/label tokens contrast-checked over the neumorphic **dark** surface *and* the
  light overlay before ship (`ADR-C-04`); text legibility never depends on the severity glow.
- Keyboard: the grid is a roving-tabindex 2-D widget (arrow keys move cell-to-cell, Enter → Foco, Esc collapses);
  every tile action (ack, assign, escalate) is reachable and has a visible `focus-visible` ring.
- Screen reader: a live region announces state changes — `aria-live="assertive"` for a **new critical**, `polite`
  for lower severities and de-escalations; each announcement names bed, patient, severity, and triggering parameter.
- Motion: `prefers-reduced-motion` swaps the critical pulse for a **static double-ring** (severity still redundantly
  encoded) and disables reflow animation.
- Contrast preference: `prefers-contrast` flattens the neumorphic elevation to a solid high-contrast border.

---

## 7. How each persona succeeds

**Dr. Carlos — Intensivista (`PER-CARLOS`).** At 7h he stands in the doorway and reads all 20 beds in one glance: the
severity sort has already floated his deteriorating patients to the top-left and they carry motion; stable beds are
quiet. In **Enfermaria** mode each tile carries the 24 h score sparkline he wants (`PER-CARLOS-03`). Because only
unattended severity animates and the catalog's dedup/suppression governs entrances, the wall shows him actionable signal,
not the 200-alert/80%-false-positive noise he suffers today — supporting `PER-C-02` (< 3 FP/patient-day). Scores land on
tiles < 30 s after collection via the one push channel (`PER-C-01`, `VIS-C-09`). Between procedures he re-triages from
across the room without touching anything.

**Enf. Ana — Enfermeira de UTI (`PER-ANA`).** She flips **"Meus pacientes"** and the wall dims to her 4–5 beds — same
surface, zero navigation. Every score is auto-computed and printed (`PER-ANA-01`, zero manual calc). When a bed alerts,
the **specific deranged vital is the one flagged** by the reference-range encoding (`ADR-0014-01`) — she sees *which*
parameter fired (RR? SpO₂? PA?) without opening anything (`PER-ANA-02`, `PER-C-04`). Acknowledge is **one inline click on
the tile** (`PER-ANA-03`, `PER-C-05`), which flips the bed to **ASSISTIDO** — no drawer, no modal.

**Dra. Fernanda — Coordenadora de UTI (`PER-FERNANDA`) — the anchor.** This is her command center. The header segment
lets her hold `Todos` or pivot to `UTI Adulto · Coronariana · Neonatal`; the acuity summary strip + ocupação gauge give
her real-time occupancy AND acuity in one line (`PER-FERNANDA-01`), continuously, not on a poll tick. A live
response-time readout (mean time-to-ACK) sits beside the summary as the quality indicator she reports upward
(`PER-FERNANDA-02` cadence handled by the separate weekly export). Distinct `vazio/reservado/higienização` bed states let
her manage flow — admissions, discharges, transfers — from the same grid. **Export snapshot** pushes the current state to
hospital quality tooling (`PER-FERNANDA-03`, `PER-C-08`).

**Dr. Rafael — Resposta Rápida / RRT (`PER-RAFAEL`) — the honest weak fit.** A wall-first stance is inherently
large-display; Rafael is on a corporate phone. He is served two ways, both stated without softening the thesis: (1) the
**same** surface at the narrowest responsive breakpoint collapses to a single-column, severity-sorted list — "the wall
for one hand" — which *is* his triage queue; (2) his < 5 s critical-score push (`PER-RAFAEL-01`, same channel `ADR-C-13`)
**deep-links straight into that bed's Foco card**, showing latest vitals + 24 h trend + leito/setor location while he
moves (`PER-RAFAEL-02`). Outcome documentation < 1 min (`PER-RAFAEL-03`) runs through the form engine, off this surface.
Concept A optimizes the wall; Rafael rides the responsive collapse of it. This is logged as Risk R2.

---

## 8. Risks

- **R1 — Red-wall normalization (primary).** A wall-first surface at high census can desensitize staff to a field of
  critical tokens. *Mitigation:* only-unattended-animates + ASSISTIDO desaturation + catalog dedup/suppression +
  count-capped summary strip. *Residual:* at genuine surge (many simultaneous unheld criticals) the wall is still
  loud — which is arguably correct, but the fatigue risk is real and must be measured against `VIS-7.1-04`.
- **R2 — Mobile RRT under-served.** Dr. Rafael's phone gets only a responsive collapse + deep-link, not a purpose-built
  mobile surface. A mobile-first concept would beat Concept A here; this is the deliberate cost of the stance.
- **R3 — Neumorphic paint cost at Mural density.** 30+ tiles with dual-shadow elevation + pulse animation can drop
  frames on a wall display or a low-spec ICU PC (`ADR-0007-01` explicitly flags this, unbenchmarked). *Mitigation:*
  flat-elevation fallback at Mural density and under `prefers-contrast`; GPU-only transform/opacity for motion; hard
  paint-cost budget before ship.
- **R4 — Density default mismatch.** Wrong auto-selected mode makes the wall look sparse on a phone or cramped on a
  monitor. *Mitigation:* viewport-driven default via the unified density function, persisted user override.
- **R5 — Cross-unit acuity comparability.** Neonatal vs adult vs coronariana use different early-warning scores; one
  integer across units could mislead a coordinator scanning `Todos`. *Mitigation:* per-unit score labeling; do not imply
  a common scale. Needs clinical ratification.
- **R6 — Severity token contrast on embossed dark surfaces.** Promoted `clinical.*` hex over neumorphic dark must pass
  AA in both themes (`ADR-C-04`); a naive port of legacy `statusTrilha` hex may fail. *Mitigation:* contrast gate in CI;
  final hex pending clinical sign-off (`ADR-0013` open question).
- **R7 — "Zero navigation" over-promise.** Deep clinical work (prescrição, Balanço Hídrico, 14 role forms) cannot live
  in an inline Foco card; at some depth the overlay-stack/route returns, so the zero-nav claim holds for the *read/triage*
  path, not for deep data entry. Stated as a scope boundary, not a solved problem.
