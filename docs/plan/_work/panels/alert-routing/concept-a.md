# Alert Routing — Concept A: "A Escada de Escalonamento" (The Escalation Ladder)

**Panel:** severity-tiered alert routing · per-patient alert budgets · smart suppression · **Concept:** A
**Designer stance:** severity-ladder-first — a strict, deterministic severity→channel mapping governed by escalation timers
**Primary persona anchor:** Dr. Rafael (RRT) receives *only what has climbed the ladder*; Enf. Ana catches alerts at the first rung.
**Deliberate thesis:** the severity ladder is a literal ladder that alerts **climb via timers**. One severity band → one channel tier. An unacked alert is *promoted up the ladder* the instant its ack-SLA breaches. Nothing routes by heuristic; everything routes by band + clock.

> Divergence note (for the judge panel): this concept commits hard to a **deterministic escalation state machine**. It does **not** hedge toward a budget-economy-first model (where attention cost demotes alerts) nor a context-aware smart-suppression-first model (where inference silences alerts). Here, budgets and suppression are *subordinate governors* that may quiet a **channel** but may **never** lower a recorded clinical severity and **never** touch `critical`. Where strictness costs nuance, that cost is stated plainly (Risks R2, R6). Fixed design authority is respected verbatim: dark-first (`ADR-0002-01`), formal tokens (`DES-C-03`, `ADR-0006-01`), Radix primitives, ONE realtime channel (`ADR-C-13`, `DES-C-05`), severity by color+icon+shape (`ADR-0013-01`, `ADR-0014-01`, WCAG 1.4.1), WCAG 2.2 AA (`ADR-C-04`).

---

## 1. Concept in one paragraph

Routing is not a notification firehose with filters bolted on; it is a **four-rung ladder** every alert occupies and can only ascend. The rungs are the panel's own channel progression — **dashboard chip → unit board → web push RRT (<5 s)** — extended to the four canonical `clinical.*` bands (`platform/severity-model.yaml`). Severity decides the *entry rung*; an **escalation timer** (the band's ack-SLA) decides *when it climbs*. `normal` enters silently at the chip and never climbs on its own; `critical` enters at the top rung, pages the RRT in < 5 s, and can only be silenced by a human acknowledgment. Between them, an unacked `watch` or `urgent` alert is **promoted one rung per breached SLA**, deterministically, audibly, and audit-logged. This makes escalation *inevitable and visible*: a clinician trusts that an alert they miss will not go quiet — it will get louder and reach the next tier. Per-patient budgets and dedup/cooldown suppression sit **below** the ladder as governors on the two lowest rungs only; they compress noise without ever demoting a band or dropping a life-safety page (`rate_limited: false` for `critical`, `severity-model.yaml` L60). The ladder is the single source of routing truth, driven by the one push channel so the chip, the board, and the RRT device can never disagree about where an alert is (`ADR-C-13`).

---

## 2. The channel ladder (the spine)

Four rungs, ascending reach. Each severity band **enters** at a fixed rung and **climbs** on ack-SLA breach. This table is the concept — everything else serves it.

| Rung | Channel | Enters here (band) | Reach | Interruptive? | Ack-SLA clock (time to next climb) | Source |
|---|---|---|---|---|---|---|
| **R0** | **Dashboard chip** (in-app, per-clinician, silent) | `normal` / INFO | signed-in clinician only | no | none (`normal` never auto-climbs; action < 6 h) | `severity-model` tier 4; `CAT-C-05` |
| **R1** | **Unit board badge** (shared grid, ambient, WS push) | `watch` / WARN | whole unit, glanceable | no | **PT60M** ack → climb to R2 | `severity-model` tier 3; `CAT-C-04` |
| **R2** | **Unit board + targeted mobile push** (assigned clinician's device) | `urgent` / URG | assigned nurse/physician | soft (device push, ack expected) | **PT10M** ack → climb to R3 | `severity-model` tier 2; `CAT-C-03` |
| **R3** | **Interruptive RRT web push + audible** (page to on-call RRT rotation, < 5 s) | `critical` / CRIT | RRT rotation + charge nurse | yes (mandatory ack, audible) | **PT2M** ack → re-page **backup tier** (louder, second RRT member / attending) | `severity-model` tier 1; `CAT-C-02`; `PER-C-06` (RRT push PT5S) |

**Climb law.** Promotion is one rung on each breached ack-SLA (`raised → escalated`, `severity-model` transitions L130–131). A band **enters** at its rung and **cannot enter below it**; suppression/budget can delay a *repeat* firing but never lower the entry rung. Aggregation is **MAX-severity-wins** (`severity-model` L63–70, `CON-0182`/`P0-10`): a bed already at R3 is never pulled down to R1 by a later `watch` — the ladder only ratchets upward until a human acts.

**Manual overrides (bounded, audited).**
- **Escalar agora** — a clinician skips the timer and promotes now (e.g. Ana wants the RRT immediately). Always allowed; audited (`INV-1`, `CON-0066`).
- **Adiar** (defer/snooze) — allowed for `normal`/`watch` **only**, time-boxed, audited; **barred for `urgent`/`critical`** (a strict-ladder guarantee, not a preference).

---

## 3. Layout & surfaces

### 3.1 The Escalation Rail (the differentiator)
A compact, dockable **Radix vertical rail** — right-edge of the unit board, or a full-height "Roteamento" panel — that renders every *active* alert as one row, **grouped into the four rungs** (R3 top, R0 bottom). Each row carries, left→right:
- **Severity token** — `clinical.*` color + domain icon + severity shape (§5), never color alone.
- **Bed + patient initials + the triggering parameter** printed inline (`PER-ANA-02`, `PER-C-04`) — e.g. `Leito 7 · qSOFA 2 · Lactato 4.1` — so *which* signal fired is read without opening anything.
- **Countdown to next climb** — a token-scaled ring + a **numeric** label (`02:41` monospace, `ADR-0006-01` tabular figures) showing ack-SLA remaining; turns to the next-higher band color as it approaches breach.
- **Current rung → next rung** micro-indicator (`R2 → R3`), so the climb is legible before it happens.
- **One-click actions**: **Aceitar** (ack, stops the clock), **Atribuir** (assign), **Escalar agora**.

Rows **physically rise** between rung groups as timers breach (`motion.*` token, GPU transform only). The rail is the human-readable face of the state machine: you can watch an alert climb.

### 3.2 Dashboard chip (R0, the everywhere surface)
A **Radix HoverCard/Popover** count-badge in the app header (canonical count-badge primitive, `ADR-C-06` — one implementation, not the legacy two, `DES-3-01`/`DES-5-02`). It shows per-band counts (`crítico N · urgente N · alerta N`) and the **single nearest-to-breach countdown** for the signed-in clinician's patients. Opening it drops the Escalation Rail scoped to **"Meus pacientes"**. This is where `normal`/INFO advisories live and quietly coalesce — they never leave R0 on their own.

### 3.3 Unit board integration (R1/R2)
Each bed on the shared board (the mission-critical grid) carries its **worst active severity token** plus a **mini countdown ring** when an alert on that bed is climbing. `watch` and `urgent` live here ambiently; a bed at R2 shows the ring filling toward its R3 promotion. Board state is driven by the **same one channel** as the chip and the rail (`ADR-C-13`, `DES-C-05`), fixing the legacy grid-lags-the-bell defect (`ADR-0017-01`, `DES-6-02`). On ack the tile flips to **ASSISTIDO** (`assistido===true` override, `DES-2-03`), desaturated, ring stopped.

### 3.4 RRT web push + response card (R3)
The **< 5 s web push** (`PER-RAFAEL-01`, `PER-C-06`; deliver stage 2 s < 5 s budget, `budgets/latency.yaml` L79) lands Rafael on a **response card**: severity token, `leito/setor` location, triggering parameter, latest vitals + 24 h trend (`PER-RAFAEL-02`), and two 1-tap actions — **Aceitar** (ack, stops the R3 clock, prevents backup re-page) and **A caminho** (en route). Outcome documentation < 1 min (`PER-RAFAEL-03`) runs through the config-driven form engine (`DES-3-03`), off this surface.

### 3.5 Per-patient budget meter
On every patient chip and bed-detail: a small **token-scaled meter** — `alertas não-críticos hoje: 2/3` — reflecting the per-patient non-critical budget (`false_positive_budget.target_max_per_patient_day: 3`, `CON-0088`/`PER-C-02`; `rate_limit "4/24h/patient"`, alert schema). When spent, further `normal`/`watch` firings for that patient **coalesce into the patient's R0 digest** instead of badging the board — they are logged, never dropped. `urgent`/`critical` **bypass the meter entirely** (patient-safety carve-out). The meter is a governor, never a gate.

---

## 4. Interactions & the escalation state machine

Lifecycle maps 1:1 to `severity-model` L109–133 (`raised → acknowledged → acting → resolved → expired → escalated`) and the data-model status/resolution enums (`DM-VOCAB-04/05`):

1. **Aceitar (1-click ack, `PER-ANA-03`/`PER-C-05`).** `raised → acknowledged`; **stops the ack-SLA clock**, halting the climb; board tile → ASSISTIDO. This is the primary "catch." The action-window clock (`critical` PT5M / `urgent` PT30M / `watch` PT2H, `CON-0062..64`) then runs toward `acknowledged → escalated` if intervention stalls.
2. **Atribuir (assign).** Routes ownership to a clinician/role; the countdown and push now follow *their* chip/device.
3. **Escalar agora (manual climb).** Human promotion up a rung without waiting for the timer.
4. **Iniciar conduta (acting).** `acknowledged → acting`, resumes the action-window clock.
5. **Resolver.** Sets resolution `true_positive | false_positive | intervention_done` — feeds PPV/response analytics (`ppv_analytics`, `VIS-7.1-02/03/04`).
6. **Adiar (defer).** `normal`/`watch` only, bounded + audited; barred above.

Every transition writes an **immutable append-only audit row** (`INV-1`, `CON-0066`; LGPD + CFM 2.299/2021, `VIS-C-07`).

**Suppression (deterministic, tier-scoped).** Repeat firings of the same `dedup_key` within `cooldown` (alert schema) **collapse into the existing rail row** with a firing count + "visto há Xs" — the countdown does **not** reset on a suppressed repeat, so suppression can never hide a climbing alert. `maintenance_window_aware`: during a known procedure/turnover window, R1/R2 channels are muted but the alert still logs to R0. **Suppression can silence a channel; it can never lower a band or suppress `critical`.**

---

## 5. Severity encoding — never color alone (`ADR-0013-01`, `ADR-0014-01`, WCAG 1.4.1)

Promoted from the legacy `statusTrilha` table into contrast-checked `clinical.*` tokens, structurally separate from tenant `brand.*` (`ADR-C-08`, `DES-C-01`). Hex is **not invented here** — final re-derived values need clinical sign-off (`ADR-0013` open question, "red bed = crisis" muscle memory).

| `clinical.*` | Catalog sev / SLA (`LEGEND-SEV`) | statusTrilha (verbatim, `DES-2-02`) | Color token | Icon | Shape | Entry rung |
|---|---|---|---|---|---|---|
| `critical` | CRIT · ação < 5 min | **VERMELHO** | `clinical.severity.critical` | alert-octagon | octagon | R3 |
| `urgent` | URG · ação < 30 min | **LARANJA** | `clinical.severity.urgent` | exclamation | triangle | R2 |
| `watch` | WARN · ação < 2 h | **AMARELO** | `clinical.severity.watch` | eye | rounded-square | R1 |
| `normal` | INFO · ação < 6 h | **NEUTRO** | `clinical.severity.normal` | check-circle | circle | R0 |
| *attended* | — | **ASSISTIDO** | `clinical.assisted` | ring + check | ring | (motion stilled) |

Countdown rings use named `motion.*` tokens (pending the token pass, `ADR-0006-01` open question — no literal ms invented). Every rung row and push also carries a **text severity label**, so the ladder is legible to color-vision-deficient staff, at distance, and to screen readers.

---

## 6. States (exhaustive)

**Alert lifecycle:** `raised` · `acknowledged` · `acting` · `resolved` · `expired` · `escalated` (`severity-model` L109).
**Timer states (per row):** `contando` (counting) · `próximo do limite` (breach-imminent, color shifts to next band) · `estourado → escalonado` (breached, climbed) · `pausado` (acked/assisted).
**Rung/channel states:** on-rung R0–R3 · `suprimido` (cooldown, muted with firing count) · `agrupado no orçamento` (budget-coalesced digest) · `silenciado (manutenção)` (maintenance-muted, still logged) · `escalonado` (climbed) · `re-paginado (reserva)` (backup tier paged after R3 breach).
**Realtime states (whole surface):** `ao vivo` · `reconectando` (shared backoff, `ADR-C-12`) · `defasado` (last-updated timestamp + freshness veil, fixing silent-staleness `ADR-0017-01`) · `offline`. All from the ONE channel (`ADR-C-13`).
**Loading:** content-shaped skeleton rail (`ADR-0016-01`) — never the legacy full-viewport blocking `FadeLoading` (`DES-5-07`); staff keep triaging other rows while one loads.
**Partial failure:** a row that fails to hydrate shows inline error + retry — not a screen-wide `Modal.error` (`ADR-C-11`, `DES-5-07`).
**Empty:** no active alerts → calm "tudo estável" empty state, not an error.
**Push-delivery failure (R3):** at-least-once retry+backoff (`CON-0071`); on repeated failure, audible board fallback + staleness watchdog paged (`INV-5`, `CON-0070`) so a dropped web push can never fail silently.

---

## 7. Accessibility (WCAG 2.2 AA — `ADR-C-04`)

- Severity by **color + icon + shape + text** on every rung row, board badge, chip, and push (§5); never color alone.
- **Countdown timers are textual**, not just a ring — the numeric `MM:SS` is the source of truth; the ring is redundant decoration. `prefers-reduced-motion` removes the ring animation and the climb transition, leaving the static numeric timer and an instantaneous rung change.
- **Live regions:** `aria-live="assertive"` for a **new `critical`** and for any **SLA breach / climb**; `polite` for lower-severity arrivals and de-escalations. Each announcement names bed, patient, severity, rung change, and triggering parameter.
- **Keyboard:** the rail is a roving-tabindex list; every row action (Aceitar, Atribuir, Escalar agora, Adiar) is reachable with a visible `focus-visible` ring; Enter opens the bed's detail, Esc returns.
- **Contrast:** all `clinical.*` and timer-label tokens contrast-checked over the neumorphic **dark** surface *and* the light overlay before ship (`ADR-C-04`); legibility never depends on the severity glow. `prefers-contrast` flattens elevation to a solid high-contrast border.
- **Audible R3 cue** is paired with the visible assertive announcement (not the only channel), and is user-mutable per session without muting the visual page.

---

## 8. How each persona succeeds

**Dr. Rafael — Resposta Rápida / RRT (`PER-RAFAEL`) — the anchor.** Rafael sits at the top rung and receives **only what has earned R3**: `critical` alerts directly, plus `urgent` alerts that aged out unacked (climbed R2→R3). His web push lands in < 5 s (`PER-RAFAEL-01`/`PER-C-06`, deliver 2 s < 5 s, `latency.yaml`) with a response card showing latest vitals + 24 h trend + `leito/setor` (`PER-RAFAEL-02`). **Aceitar** stops the R3 clock and pre-empts the backup re-page; **A caminho** signals en route; outcome doc < 1 min via the form engine (`PER-RAFAEL-03`). Because the ladder is strict, his device is never touched by `watch`/`normal` noise — every page he gets is, by construction, a true top-tier event.

**Enf. Ana — Enfermeira de UTI (`PER-ANA`) — the catcher.** Ana lives at R1/R2 on the board and her chip. Scores are auto-computed and printed (`PER-ANA-01`, zero manual calc); the row **names the deranged parameter** (`PER-ANA-02`/`PER-C-04`). Her single most valuable move is **Aceitar** — one inline click (`PER-ANA-03`/`PER-C-05`) that stops the climb and flips the bed to ASSISTIDO. She sees the countdown, so she knows *how long* until an alert reaches Rafael — and she can **Escalar agora** if she wants the RRT before the timer. She is the human whose action keeps alerts off the top rung.

**Dr. Carlos — Intensivista (`PER-CARLOS`).** Carlos does not want to be paged for noise. The strict ladder guarantees he only sees `watch`/`urgent` at the chip and board — never a page unless something crosses into `critical` or ages out — directly serving his < 3 FP/patient-day pain (`PER-C-02`, 200 alerts/day/80% FP today). His chip shows the ladder position and countdown of each alert so he re-triages between procedures at a glance; scores land < 30 s after collection via the one channel (`PER-C-01`, `VIS-C-09`). He trusts the system precisely because the escalation is *deterministic and visible* — a missed `urgent` will not go silent, it will climb.

**Dra. Fernanda — Coordenadora de UTI (`PER-FERNANDA`).** For Fernanda the ladder **is** the quality instrument. A "Roteamento" overview gives her live counts per rung, **mean time-to-ack per band**, and — the number she reports upward — the **escalation-breach rate** (how many alerts climbed because nobody acked in the SLA). These are her time-to-action and alarm-fatigue KPIs made continuous, not retrospective (`PER-FERNANDA-01/02`, `VIS-7.1-03/04`). She reads the ladder to spot a unit that is systematically letting alerts climb (staffing signal) and exports the routing/response snapshot to hospital quality tooling (`PER-FERNANDA-03`/`PER-C-08`).

---

## 9. Risks

- **R1 — Shift-change page storm.** Timer-driven promotion can fire many R2→R3 climbs at once when a cohort of `urgent` alerts ages out simultaneously (e.g. handover gap). *Mitigation:* per-patient budget coalescing at R0/R1, jittered escalation timing, a charge-nurse batch view; residual real — the strict clock does not care that everyone is in handover.
- **R2 — The ladder amplifies upstream mis-tiering.** Deterministic routing is only as correct as the severity assignment; a band-mislabeled alert is *reliably* mis-routed. *Mitigation:* MAX-severity aggregation (`severity-model` L63), ADOPT-CORRECTED catalog severities, clinical sign-off on band mapping. This is the honest cost of strictness vs a context-aware concept.
- **R3 — RRT top-rung overload / single-device risk.** Funneling every `critical` + aged-out `urgent` to one RRT device can swamp it. *Mitigation:* R3 targets an **on-call rotation/role**, not a person, with a backup tier on breach; needs rotation config + staffing sign-off.
- **R4 — Web-push reliability threatens the < 5 s SLA.** Browser/OS push throttling can miss the R3 budget. *Mitigation:* at-least-once retry+backoff (`CON-0071`), audible board fallback, staleness watchdog (`INV-5`, `CON-0070`); web push is never the *only* R3 channel.
- **R5 — Clock-watching / false-ack gaming.** Visible countdowns can incentivize acking to stop the clock without acting. *Mitigation:* the `acknowledged → acting → resolved` action-window timers resume after ack, and false-acks surface in PPV analytics (`ppv_analytics`); residual behavioral risk.
- **R6 — Strictness under-serves clinical nuance.** A human wanting to "watch a trending-up but still-`watch` patient more closely" has only Escalar agora (over-pages) — the strict ladder has no soft middle. A context-aware suppression-first concept would beat Concept A here; this is the deliberate cost of the stance.
- **R7 — Snooze-as-silence on lower rungs.** Even with `urgent`/`critical` barred, repeated `Adiar` on `watch`/`normal` could hide a slow deterioration. *Mitigation:* defer is time-boxed + audited (`INV-1`) and cannot stop a band from *re-entering* at its rung if the predicate re-fires.
- **R8 — A second surface competes with the board.** The Escalation Rail is one more thing to watch. *Mitigation:* it is a **lens over the same one channel** (`ADR-C-13`), docks into the board, and never holds independent state; it is not a parallel truth. Divergence cost: this concept invests in an explicit routing surface a board-only concept would not build.
