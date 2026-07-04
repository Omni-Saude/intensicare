# Alert Routing — Concept B: Route to Whoever Can Act *Now*

**Stance:** role-context-first. An alert's job is not to "appear on a screen" — it is to
**reach a specific human who can act on it right now**. So the primary routing key is never
the bed alone and never a flat broadcast: it is a computed **recipient set** derived from
**(severity tier) × (role responsibility) × (location proximity) × (shift/on-call roster) ×
(live presence & availability)**. The three delivery surfaces named in the brief —
**dashboard chip ▸ unit board ▸ web-push RRT (<5s)** — are the tiers of that resolver: each
tier widens the recipient set from *the one owner* to *everyone present on the unit* to *the
role that can respond regardless of location*. Alerts escalate along a **responsibility
chain**, not up a UI z-index.

This concept deliberately commits to *addressing* as the design center. It does **not** hedge
toward a severity-only ladder (same broadcast to all, just louder) nor toward a
location-only board (everything lives on the setor grid and hopes someone looks). Divergence
is the point: the differentiator is a **roster/presence resolver** and **recipient-level
suppression** ("is someone already acting on this patient?").

---

## 1. Fixed design authority honored (non-negotiable)

- **One realtime channel.** Chip, unit board, and RRT push all subscribe to the **same** push
  transport with shared reconnect/backoff — the routing *fan-out* happens server-side into
  topic-multiplexed recipient queues, not by adding a second socket. No `setInterval` polling
  of the unit board [DES-C-05, ADR-C-12, ADR-C-13, ADR-0017-01]. This closes the legacy
  bell-instant-but-grid-stale disagreement [DES-6-02].
- **Severity = color + icon + shape**, never color alone; `clinical.*` scale structurally
  separate from tenant `brand.*` [ADR-C-08, DES-C-01]. The two legacy severity bugs
  (hardcoded amber toast, hardcoded `VERMELHO` panel) are fixed, not ported [ADR-C-09].
- **Dark-first, token-driven**, one live-switchable token set — no full-reload light toggle,
  no runtime AntD recompile [DES-C-02, DES-C-03, ADR-C-03]. Neumorphic dual-shadow elevation
  kept as a governed `elevation.*` pair with a `prefers-contrast` flat fallback [DES-C-07].
- **Radix primitives** for every generic shell part of the routing UI — the chip is a Radix
  Toast/Popover, escalation confirms use one Dialog, the roster picker one Dropdown; no
  second competing primitive [ADR-C-06].
- **WCAG 2.2 AA** contrast for all clinical text/status over neumorphic surfaces in both
  themes [ADR-C-04].
- **Advisory, auditable, deny-by-default.** Every routed alert is written to the prontuário at
  NGS Level 2; routing suggests *who acts*, never *the decision* — the physician remains
  responsible [VIS-C-07, VIS-C-08]. Recipient resolution obeys deny-by-default per-route
  permission and server-side authorization; the client only renders what the server already
  authorized [ADR-C-05, ADR-C-14].

---

## 2. The routing model (the divergent core)

### 2.1 Recipient resolver — "who can act now"

For every fired alert the server computes an ordered **recipient chain** before any surface
lights up:

```
alert(patient P, severity S, triggering-param X)
        │
        ▼
┌─────────────────────────── RESOLVER ───────────────────────────┐
│ OWNER      = assigned clinician for P this shift               │  ← roster
│              (bedside nurse for nursing-actionable alerts;     │
│               attending intensivist for physician alerts)      │
│ COVERING   = charge nurse / on-call intensivist for the setor  │  ← roster + on-call
│ RESPONDER  = on-shift RRT physician (Rafael), hospital-wide    │  ← on-call, location-free
│ presence(role) = { at-workstation | on-unit-mobile | remote |  │  ← live presence
│                    scrubbed-in/busy | off-shift }              │
└────────────────────────────────────────────────────────────────┘
        │
        ▼   tier map by severity  (SLA windows = CAT legend)
```

| Sev (catalog) | Action window | Tier-1 surface (immediate) | Escalate to (if unacked) | Tier-3 |
|---|---|---|---|---|
| **CRIT** | <5 min [CAT-C-02] | **parallel multicast**: owner chip **+** unit board **+** RRT web push **<5s** | — (already all tiers) | audit + coordinator KPI |
| **URG** | <30 min [CAT-C-03] | owner chip + unit board | RRT push after Tier-1 SLA (owner no-ack, e.g. 5 min) | coordinator |
| **WARN** | <2 h [CAT-C-04] | owner chip | unit board after ~30 min no-ack | — |
| **INFO** | <6 h [CAT-C-05] | batched into owner's worklist (no board, no push) | owner chip on shift handover | — |

The three brief-named surfaces are literally the three tiers. **CRIT does not escalate
sequentially** — a <5-min window can't afford waiting for an owner no-ack timer, so it fans
out to all three at once and the <5s push [PER-C-06, PER-RAFAEL-01, latency budget
`personas_rrt_push_s: 5`] is fired in parallel with the chip.

### 2.2 Presence short-circuits the timer

The distinctive move: **presence collapses the escalation timer**. If the OWNER is
`scrubbed-in/busy`, `remote`, or `off-unit` at fire time, the resolver does **not** spend the
full Tier-1 SLA waiting — it routes to COVERING (and, for CRIT, RESPONDER) **immediately in
parallel**, and marks the owner's chip as "notified, unavailable". Conversely if the OWNER is
`at-workstation` and already **acting on this patient** (§6), a new lower-tier alert for the
same patient is demoted to an ambient chip rather than re-escalated — nobody re-summons a
person who is already at the bedside.

### 2.3 Shift context (day ▸ night reshaping)

The resolver reads the **active shift roster + on-call schedule** as data. The same CRIT
sepsis alert resolves to different humans at 10h vs 03h: by day OWNER=Carlos at a workstation
gets the chip and RRT gets the board; at night Carlos "covers remote calls" [personas
flow_2l] so he is `remote` — CRIT then routes on-site RRT (Rafael) as primary actor **plus a
remote push to Carlos** for awareness, never assuming a remote attending is the one who can
act now.

> **Dependency (flagged, not invented):** the roster/on-call source and the live-presence
> signal are not specified in any brief. This concept *requires* them; §8 risk 1 and the YAML
> record them as the top open dependency for ratification, not as settled fact.

---

## 3. Layout — the three surfaces

### 3.1 Surface 1 — Dashboard severity chip (the owner's ambient tier)

Rendered wherever the OWNER already is (bed grid, bed drawer, worklist). A Radix
Toast/Popover chip, **not** the legacy always-amber toast:

```
┌───────────────────────────────────────────────┐
│ ◐ URG · Leito 12 · Sepse — qSOFA 2, lactato 2,4│  ← color+icon+shape by clinical.*
│    FR 24 rpm · há 8s          [Ver] [✓ Assumir]│  ← triggering param X at chip level
└───────────────────────────────────────────────┘
```

- Severity via `clinical.*` **color + icon + shape** (CRIT filled octagon / URG triangle /
  WARN diamond / INFO circle) [ADR-C-08, DES-2-02]; icon color derives from the alert's real
  severity, fixing the hardcoded-amber bug [ADR-C-09, DES-5-03].
- The **triggering parameter is shown on the chip** ("FR 24 rpm") so *what fired* is legible
  with zero drill-down [PER-ANA-02, PER-C-04].
- **`✓ Assumir` = 1-click ack/own** [PER-ANA-03, PER-C-05]. Ack stops the escalation timer for
  this recipient and flips the patient to **ASSISTIDO** across every surface (§5), mirroring
  the `statusTrilha` `assistido` override [DES-2-03].
- Chips **stack and coalesce per patient** — never one toast per raw alert; the per-patient
  budget (§6) caps how many can appear.

### 3.2 Surface 2 — Unit board (the shared "who's covering" tier)

The setor board (successor to `ListOcupacoes` [DES-4-03]) carries a **routing rail**: a
severity-ranked column of *active, unacked* alerts for the unit, each row annotated with its
**current recipient and escalation state** — the thing a location-only board omits.

```
UNIT BOARD · UTI Adulto        live ●          [Meus leitos] [Todos] [só CRIT]
┌──────── routing rail ─────────────────────────────────────────────────────┐
│ ⬢ CRIT Leito 07 Choque séptico   → RRT (push 3s) + Enf. Ana   00:42  [Assumir]│
│ ▲ URG  Leito 12 Sepse qSOFA      → Enf. Ana (chip, no-ack 4:10) ↑ 00:50 [Assumir]│
│ ◆ WARN Leito 03 KDIGO 1          → Dr. Carlos (chip)            02:05  [Assumir]│
└────────────────────────────────────────────────────────────────────────────┘
[ bed grid below — tiles carry the same acuity band + triggering param ]
```

- Each rail row shows **→ recipient + delivery state + time-in-tier**, so anyone on the unit
  sees *who owns it and whether it's slipping* — the accountability the legacy board never
  surfaced. `↑` marks a row mid-escalation.
- **`Assumir` from the rail** reassigns ownership to the actor and acks in 1 click; a
  **`Repassar`** (hand-off) opens one Radix Dialog to route to a named covering role.
- Filters: `Meus leitos` (Ana), `Todos`, `só CRIT`. Board and chip are the **same channel**,
  so they can never disagree about an event [ADR-C-13].

### 3.3 Surface 3 — Web push to RRT (<5s, location-free tier)

Rafael carries a corporate smartphone [personas PER-RAFAEL]; he has no unit context. A CRIT
(or escalated URG) fires a **web-push notification in <5s** [PER-C-06, latency budget
`personas_rrt_push_s: 5`] that **deep-links straight to the patient**, carrying the payload he
needs while en route: **score + trend + location (Estabelecimento ▸ Setor ▸ Leito) + latest
vitals** [PER-RAFAEL-02].

```
[push]  ⬢ CRÍTICO · Choque séptico iminente
        Leito 07 · UTI Adulto · Hosp. AUSTA
        Lactato 4,1 · MAP 58 · qSOFA 3
        ▸ toque para abrir  ·  há 3s
```

Opening the push lands on a **mobile responder view** (latest vitals + 24h trend + a 1-action
**outcome form** completable in <1 min) [PER-RAFAEL-03, PER-C-07]. Acking from the push marks
ASSISTIDO on the unit board and chip in the same instant [ADR-C-13].

### 3.4 Routing config (roster & escalation policy)

A coordinator-facing config (Fernanda): the **shift roster / on-call assignment** (who is
OWNER / COVERING / RESPONDER per setor per shift), per-tier **SLA windows**, and per-patient
**budget** ceilings. Deny-by-default: only authorized roles edit routing [ADR-C-05].

---

## 4. Interactions

- **Assumir (1 click)** — ack + take ownership; stops *this recipient's* timer, sets
  ASSISTIDO everywhere, writes to prontuário NGS2 [PER-C-05, VIS-C-07].
- **Repassar (hand-off)** — one Dialog; route to a named role/person; the chain restarts at
  that recipient with a fresh Tier-1 timer; logged.
- **Escalar agora** — manual early escalation to the next tier without waiting the SLA (e.g.
  owner knows they're about to scrub in).
- **Adiar/Snooze (bounded)** — WARN/INFO only, capped and audited; CRIT/URG cannot be snoozed.
- **Ver** — opens the bed drawer with per-alert detail: which parameter, threshold, evidence
  citation, 24h trend [PER-CARLOS-03, PER-ANA-02].
- All actions are **idempotent patches** reconciled against the authoritative record — the
  realtime layer is transport only, never a second source of truth [ADR-C-12].

---

## 5. States

- **Delivered / unacked** — chip visible, escalation timer running, rail row shows time-in-tier.
- **Escalating (`↑`)** — Tier-1 SLA elapsed or presence short-circuited; recipient set widened;
  rail row shows the new recipient and that it climbed.
- **ASSISTIDO** — someone `Assumir`-ed; blue override ring/marker on every surface, timers
  stopped, further same-patient lower-tier alerts demoted to ambient [DES-2-03].
- **Owner unavailable** — presence = scrubbed-in/remote/off-shift; chip shows "notified,
  unavailable", routing already went parallel to COVERING/RESPONDER (§2.2).
- **Resolved / expired** — alert condition cleared or superseded; leaves the rail, retained in
  history + prontuário.
- **Realtime stale/reconnecting** — explicit `live / reconnecting / stale` chip on the board;
  a stale board is visibly marked so it can't silently show old routing state [ADR-0017-01].
- **Push undeliverable** — if the RRT web push isn't confirmed within the <5s budget, the
  resolver **falls back** (escalates to on-call/coordinator surface) rather than silently
  dropping — a failed push is itself an escalation event, not a no-op.
- **Loading** — content-shaped skeleton rail (not generic bars) [ADR-0016-01].

---

## 6. Per-patient alert budgets + smart (role-context) suppression

- **Per-patient budget.** Each patient carries a rolling alert budget seeded from each alert's
  `ppv_budget.est_volume_per_100_beds_day` and Carlos's hard ceiling of **<3 false positives
  per patient-day** [PER-C-02, alert-schema `ppv_budget`]. When a patient nears budget,
  additional **lower-severity** alerts for that patient are **demoted, not multicast** —
  collapsed into the worklist rather than firing a new chip/push. CRIT is **never** budgeted
  away (patient-safety floor).
- **Upstream suppression** (shared with the platform): dedup by `patient_id+alert_id`,
  cooldown, rate-limit, maintenance-window awareness — enforced **before** routing, so a
  surface only ever lights on *actionable* state [alert-schema `suppression`].
- **Recipient-level suppression (the divergent layer).** Standard suppression asks "have we
  fired this alert recently?". This concept also asks **"is someone already acting on this
  patient?"** — if a patient is ASSISTIDO or the OWNER is present at the bedside, correlated
  lower-tier alerts are demoted for *that recipient* (they're already there) while still being
  logged and still escalating if the situation worsens. This directly attacks alarm fatigue at
  the point of delivery, targeting ignored-alert rate **≤10%** [VIS-7.1-04] and mean
  time-to-action **≤15 min** (baseline 42) [VIS-7.1-03].

---

## 7. How each persona succeeds

### 7.1 Dr. Carlos — Médico Intensivista (20-bed adult ICU)
By day Carlos is OWNER for physician-actionable alerts on his unit and usually
`at-workstation`. URG/WARN reach him as **ambient chips** carrying the triggering parameter;
he clicks `Ver` for the 24h trend + threshold + evidence [PER-CARLOS-03]. Because routing is
targeted and budgeted, he is not in the 200-alerts/day/80%-FP world — only *his* patients'
*actionable* alerts reach him, ≥3 FP/day suppressed upstream [PER-C-01, PER-C-02]. When he
scrubs into a procedure, presence flips him `busy`: his alerts route to COVERING immediately
rather than rotting on an unwatched chip (§2.2). **At night** he is `remote`; CRIT then makes
on-site RRT the actor and sends him a parallel awareness push — he is never assumed to be the
one who can act now. **Wins:** targeted, low-FP delivery; presence-aware coverage so an
in-procedure attending never blocks an alert.

### 7.2 Enf. Ana — Enfermeira de UTI (4–5 patients)
Ana is OWNER for nursing-actionable alerts on her assignment. Her chips and her `Meus leitos`
rail filter show **exactly which parameter fired** — "FR 24 rpm", "SpO₂ 88%" — before any
drill-down [PER-ANA-02, PER-C-04], with MEWS/NEWS2 auto-calculated, zero manual math
[PER-ANA-01]. She `Assumir`s in **1 click**, which acks, stops the timer, and flips the
patient ASSISTIDO everywhere [PER-ANA-03, PER-C-05]. If she's mid-task with another patient
and doesn't ack an URG in the Tier-1 window, it escalates to the charge nurse — she is backed
up, not left as a single point of failure. **Wins:** the "which parameter?" question is
answered at the chip; 1-click ownership; guaranteed backup via the chain.

### 7.3 Dra. Fernanda — Coordenadora de UTI (30 beds, adult/coronary/neonatal)
Fernanda owns the **routing config** (§3.4) — the shift roster, SLA windows, and budgets that
decide who-acts-now across her units. Her monitoring view is the **escalation KPI**: mean
time-in-tier, **alert→ack response time** (her quality indicator, baseline 42 min → goal ≤15
min) [PER-FERNANDA-02, VIS-7.1-03], escalation/override rates, and ignored-alert rate
[VIS-7.1-04], all exportable to hospital quality tools [PER-C-08, PER-FERNANDA-03]. Because
every alert carries an explicit recipient and delivery-state, she has *data* on where routing
slips (a role chronically no-acking, an over-budget patient) rather than perception. **Wins:**
response-time becomes a first-class, per-recipient measurable; capacity/staffing arguments
backed by routing data.

### 7.4 Dr. Rafael — Equipe de Resposta Rápida (mobile, hospital-wide)
Rafael is RESPONDER — the location-free role the resolver reaches when an alert needs someone
who can act now regardless of where the patient is. He gets the **<5s web push** [PER-C-06]
deep-linking to the patient with score + trend + **location** + latest vitals as wayfinding
while he moves [PER-RAFAEL-02]. For CRIT he's in the *parallel* first wave (not waiting on an
owner no-ack); for URG he's the escalation target. He documents the outcome in a 1-action form
in <1 min [PER-RAFAEL-03, PER-C-07], and his ack marks ASSISTIDO on board + chip instantly
[ADR-C-13]. If a push can't be confirmed in the budget, it falls back to on-call so he's never
the silent single point of delivery (§5). **Wins:** <5s push with full location + vitals
context; he's routed *by role*, so he's reachable for any bed in the hospital.

---

## 8. Risks (and mitigations)

1. **Roster/presence data dependency (top risk).** The whole model assumes a trustworthy
   shift roster/on-call source and a live-presence signal — neither is specified in any brief.
   *Mitigation:* degrade gracefully to **severity-only broadcast** when roster/presence is
   unavailable (owner-unknown ⇒ route to unit board + on-call as if all-present); flag as the
   #1 ratification dependency. Wrong owner resolution is a safety risk, so the fallback must be
   *wider*, never narrower.
2. **Mis-addressing sends an alert to the wrong human.** A stale roster could route to someone
   off-shift. *Mitigation:* presence gating (off-shift never resolves as OWNER), parallel CRIT
   multicast so no single resolution is load-bearing, and a visible recipient on the rail so a
   human can `Repassar` a mis-route in 1 click.
3. **Escalation storms / paging fatigue on RRT.** If many owners are unavailable, everything
   escalates to Rafael. *Mitigation:* per-patient budgets + recipient-level suppression (§6);
   CRIT-only push floor; coordinator sees escalation-rate KPI to rebalance staffing.
4. **Presence signal wrong (busy clinician marked available).** Could delay coverage.
   *Mitigation:* short Tier-1 SLA as a backstop even when presence says "available"; manual
   `Escalar agora`; CRIT never depends on presence at all (parallel fan-out).
5. **Single realtime channel is a single point of failure.** *Mitigation:* shared
   reconnect/backoff, explicit `stale` state, and push-undeliverable fallback (§5)
   [ADR-0017-01].
6. **Accountability could read as surveillance.** Showing "who owns / who no-acked" on a
   shared board may feel punitive. *Mitigation:* frame as coverage/hand-off, not blame; expose
   individual attribution only to the coordinator role, unit rail shows role + state, not
   performance scoring.
7. **Advisory-only boundary.** Routing must never read as the system making the clinical
   decision. *Mitigation:* recipients *act*; the alert is advisory and logged NGS2; physician
   stays responsible [VIS-C-08, VIS-C-07].

---

## 9. Alarm-fatigue posture

Routing *is* the anti-fatigue mechanism here: an alert reaches **one owner first**, not every
screen; it only widens when unacked or when presence proves the owner can't act; per-patient
budgets demote low-value lower-severity alerts; and **recipient-level suppression** silences
alerts for a patient someone is already handling. Redundant color+icon+shape lets the eye land
on the few actionable rows. The net intent is fewer, better-addressed interruptions — driving
ignored-alert rate toward **≤10%** [VIS-7.1-04] and time-to-action toward **≤15 min**
[VIS-7.1-03], with a hard floor that CRIT is never budgeted or suppressed away.

---

## 10. Accessibility notes

Severity always encoded **color + icon + shape** (never color alone), WCAG 2.2 AA contrast for
all clinical values over neumorphic surfaces in both themes with a `prefers-contrast`
flat-shadow fallback [ADR-C-04, ADR-C-08]; chip toasts are ARIA live regions (`assertive` for
CRIT, `polite` for WARN/INFO) so a screen-reader user hears routing without watching; the
routing rail is a keyboard-navigable list with `Assumir`/`Repassar` reachable by keyboard and
focus-visible; the RRT push view is a single focus-trapped responder screen; tabular clinical
numbers (score, lactato, MAP) use a monospace token for scan-alignment.
