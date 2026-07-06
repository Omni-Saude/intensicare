# Screen Spec — Alert Routing & Notification Delivery

**Owner:** alerting-ux-specialist · **Status:** draft for reconciliation barriers **C2** (severity + lifecycle UX) and **C3** (latency + PPV) · **Authority precedence:** ADR-001 ≻ vision ≻ directive ≻ audit (CONTRACTS §5).

This spec defines **how a fired alert reaches the right human at the right loudness, and how that decision is escalated and audited** — the routing and notification half of the alert system. It is the synthesis of the **alert-routing** panel: **winner Concept A** ("A Escada de Escalonamento" — the severity→channel escalation ladder with timer-driven climbs), strengthened with **role/shift-aware delivery grafted from Concept B**, and with the **salvageable suppression ideas from the SAFETY-VETOED Concept C grafted ONLY onto the normal/watch tiers** under one non-negotiable invariant: **critical and urgent alerts are never budget-suppressed** (`score-clinical-safety-officer-c.yaml` veto; HAZ-025/HAZ-026).

It renders the machinery already specified in `architecture/alert-engine.md` (suppression §5, delivery/dead-man §7, lifecycle §9, severity §3) and is bound by `_work/platform/severity-model.yaml` — **its delivery tiers and ack-SLAs are LAW**. It interlocks with `design/screens/alert-triage.md` (raise→ack→act→resolve lifecycle UI) and `design/screens/admin-config.md` (governance queue, threshold tuning). It invents **no** clinical content — cutoffs live in the alert catalog and units registry.

Every claim cites a source: a ledger constraint (`CON-*`), a brief fact (`VIS-*`, `CAT-*`, `DM-*`, `PER-*`, `DES-*`, `ADR-*`), a user story (`US-*`), a journey moment (`MOT-*`), a hazard (`HAZ-*`), or an invariant (`INV-*`). PT-BR clinical vocabulary is preserved verbatim (`CON-0183`/`DM-C-01`).

---

## 0. Design frame + inherited LAW (non-negotiable)

- **Severity model is LAW** (`severity-model.yaml`; alert-engine §3). Four canonical `clinical.*` bands `{normal, watch, urgent, critical}` with **fixed delivery tiers + ack/action SLAs** (§1). Routing may change *loudness within the tier guarantee*; it may **never** lower a recorded band or violate a band's SLA. Aggregation is **MAX-severity-wins, never last-writer-wins** — a VERMELHO is never overwritten by a later AMARELO (`CON-0182`/`P0-10`/HAZ-010).
- **One realtime channel** feeds chip + unit board + RRT push identically, with shared reconnect/backoff (`ADR-C-13`/`CON-0045`/`CON-0046`/`DES-C-05`). The routing fan-out is **server-side into recipient queues**, not a second socket; the bed board **never polls** (`ADR-0017`/`DES-6-02`). Chip, board, and page can never disagree about one event.
- **Severity is always triple-encoded — color + icon + shape + text** (`CON-SEED-11`, WCAG 1.4.1); never color alone. `clinical.*` tokens are structurally separate from tenant `brand.*` (`CON-0041`/`ADR-C-08`/`DES-C-01`) — rebranding can never change what a severity color *means*, nor which tier it routes to.
- **Deny-by-default, server-enforced** route/recipient permission ahead of shell render; the API independently authorizes every dispatch (`CON-0038`/`CON-0047`/`ADR-C-05`/`ADR-C-14`). The client renders only what the server already authorized.
- **Advisory + auditable.** Every routed alert is written to the prontuário at NGS Level 2 (`VIS-C-07`); routing suggests *who acts and how loudly*, never the clinical decision — the physician remains responsible (`VIS-C-08`). **Every delivery decision is an immutable audit row** (§8; `INV-1`/`CON-0066`; LGPD + CFM 2.299/2021).
- **PHI-free notifications (lock-screen safety).** The web-push page is **pre-authentication** and can surface on a lock screen or a wrong/roamed device, so it carries **no PHI and nothing patient-identifying** — **severity band + opaque deep-link token only** (NO score, trend, location, vitals, or name; bed+unit+time alone re-identifies the ICU patient). All clinical content renders **only inside the authenticated PWA after the responder taps through** (`CON-0038`/`CON-0047` deny-by-default; security-lgpd I11 / REQ-INV-4-S3; LGPD Art. 46; HAZ-034). §5.1 specifies the mechanics and the **dispatch-vs-content-load** latency split.
- **Web only.** Delivery is the responsive web app + PWA web push; a native app is WON'T (product-spec §4). §5 specifies the PWA mechanics.

---

## 1. The severity→channel ladder (the spine)

Routing is a **four-rung ladder** every alert occupies and can only **ascend**. Severity decides the **entry rung**; the band's **ack-SLA** decides **when it climbs** (§2). The three brief-named surfaces — **dashboard chip → unit board → web push RRT <5s** — are literally the rungs, extended to the four canonical bands. This table is the concept; the tiers and SLAs are copied verbatim from `severity-model.yaml` (LAW).

| Rung | Channel (surface) | Entry band | `severity-model` tier | Reach | Interruptive | Ack-SLA → climb | Action-SLA | Source |
|---|---|---|---|---|---|---|---|---|
| **R0** | **Dashboard chip** (in-app, per-clinician, silent) | `normal` / INFO / **NEUTRO** | Tier 4 | signed-in clinician | no | **none** — never auto-climbs (review < 6h) | PT6H | tier 4; `CON-0065`/`CAT-C-05` |
| **R1** | **Unit board badge** (shared grid, ambient, WS push) | `watch` / WARN / **AMARELO** | Tier 3 | whole unit, glanceable | no | **PT60M** unacked → climb to R2 | PT2H | tier 3; `CON-0064`/`CAT-C-04` |
| **R2** | **Unit board + targeted mobile push** (assigned clinician's device) | `urgent` / URG / **LARANJA** | Tier 2 | assigned nurse/physician | soft (push, ack expected) | **PT10M** unacked → climb to R3 | PT30M | tier 2; `CON-0063`/`CAT-C-03` |
| **R3** | **Interruptive RRT web push + audible** (page to on-call RRT rotation, **< 5 s**) | `critical` / CRIT / **VERMELHO** | Tier 1 | RRT rotation + charge nurse | yes (mandatory ack, audible) | **PT2M** unacked → re-page **backup tier** (louder) | PT5M | tier 1; `CON-0062`/`CAT-C-02`; `CON-0092`/`PER-C-06`/`PER-RAFAEL-01` |

**Encoding per rung** (never color alone; promoted from legacy `statusTrilha`, verbatim — `DES-2-02`):

| Band | Legacy | `clinical.*` token | Icon | Shape | Entry rung |
|---|---|---|---|---|---|
| `critical` | **VERMELHO** | `clinical.severity.critical` | alert-octagon | octagon | R3 |
| `urgent` | **LARANJA** | `clinical.severity.urgent` | exclamation | triangle | R2 |
| `watch` | **AMARELO** | `clinical.severity.watch` | eye | rounded-square | R1 |
| `normal` | **NEUTRO** | `clinical.severity.normal` | check-circle | circle | R0 |
| *attended* | **ASSISTIDO** | `clinical.status.attended` | person-check | additive corner badge — composited **alongside** the true severity color+icon+shape, **never replacing** it | (additive; climb stilled, severity unchanged) |

**Climb law (the four invariants of the spine):**

1. **Enter-at-rung, never below.** A band enters at its rung and can never be delivered below it. Suppression/budget (§4) may delay a *repeat* firing or quiet a *lower* channel, but can **never lower the entry rung** of `urgent`/`critical`.
2. **Ratchet upward only.** MAX-severity-wins: a bed at R3 is never pulled to R1 by a later `watch`; the ladder only ratchets up until a human acts (`CON-0182`/HAZ-010).
3. **Never silent — it gets louder.** An unacked alert is **promoted one rung on each ack-SLA breach** (§2). The clinician trusts that a missed alert will not go quiet; it will climb and reach the next tier (`MOT-17`/`MOT-18` trust question; HAZ-025).
4. **Critical is unconditional.** `critical` enters at R3, multicasts in parallel (§3.2), pages the RRT in **< 5 s**, is **never rate-limited/suppressed/maintenance-muted/budget-held** (`severity-model` L60 `rate_limited: false`), and is silenced only by human ack or class-resolution.

> **The Escalation Rail (differentiator).** A dockable Radix vertical rail — right edge of the unit board, or a full-height **"Roteamento"** panel — renders every *active* alert as one row grouped into the four rungs (R3 top). Each row carries: the `clinical.*` severity token; `Leito` + patient initials + the **triggering parameter inline** (`Leito 7 · qSOFA 2 · Lactato 4.1`, `PER-ANA-02`/`PER-C-04`); the **→ recipient + delivery-state + time-in-tier** annotation *(graft: B)*; a **countdown to next climb** (§2); a `R2 → R3` micro-indicator; and one-click **Aceitar / Atribuir / Escalar agora**. Rows physically rise between rung groups as timers breach (GPU transform, `motion.*` token). The rail is a **lens over the one channel**, never a parallel truth (`ADR-C-13`); it holds no independent state.

### 1.1 The three surfaces (one event, three views, one channel)

- **R0 — Dashboard chip.** A Radix HoverCard/Popover count-badge (canonical count-badge primitive, `ADR-C-06`; fixes the legacy dual implementation `DES-3-01`/`DES-5-02`) showing per-band counts (`crítico N · urgente N · alerta N`) and the single nearest-to-breach countdown for the signed-in clinician's patients. `normal`/INFO advisories live and quietly coalesce here (§4). Opening it drops the Escalation Rail scoped to **"Meus pacientes"**.
- **R1/R2 — Unit board.** Each bed tile carries its **worst active severity** as border + glow + status ball (preserved `CollapseCard`/`Ball`, `DES-3-05`/`DES-8-01`) plus a mini countdown ring when an alert on that bed is climbing. `watch`/`urgent` live here ambiently; on ack the tile gains the **ASSISTIDO** state — an **additive `clinical.status.attended` corner badge (`person-check` icon) composited *alongside* the unchanged severity color+icon+shape**, ring stopped (`DES-2-03`); the live severity is **never desaturated or masked** (a `critical` under response still reads `critical` — design-language.md §4, design-tokens.md §6.5). Same channel as chip and rail (`CON-0053`).
- **R3 — RRT web push.** `critical` (and aged-out `urgent`) pages the RRT physician's corporate smartphone in **< 5 s** (`CON-0092`/`PER-C-06`; deliver stage p95 2 s < 5 s, `budgets/latency.yaml` L69/L79). **The page itself is PHI-free** — severity band + a generic label ("novo alerta crítico") + an opaque deep-link token only; **no** score, trend, `Estabelecimento▸Setor▸Leito` location, vitals, or patient name on the lock screen (§0; I11 / REQ-INV-4-S3, security-lgpd §2.2/§7; §5.1). **One authenticated tap** (in-app OIDC, `MOT-14`) then opens the **en-route responder view**, whose clinical content is fetched **server-side post-authN**: latest vitals each with its own staleness timestamp, scores + 24 h trend (`PER-RAFAEL-02` — read as **post-auth completeness**), the *why* panel (`alert-triage §4`), and two 1-tap actions **Aceitar** / **A caminho**. Desfecho documentation < 1 min runs off this surface via the form engine (`alert-triage §3`; `PER-RAFAEL-03`).

### 1.2 The ladder faithfully amplifies upstream mis-tiering — gated on RATIFY *(must_fix MF-09)*

A deterministic ladder is only as correct as the severity assignment feeding it; a band-mislabeled alert is *reliably* mis-routed, and an over-firing criterion (e.g. the P0-12 / HAZ-012 sepsis PAD<90 "nearly always true" defect) would **flood R2/R3 and burn the top rung's trust**. Therefore: **upstream band assignment MUST clear the `SYS-C-03` RATIFY gates before the strict ladder ships** (score-clinical-safety-officer-a.yaml own-R2; all P0 rules carry disposition RATIFY — human clinical decision, hazard-log policy). The ladder's own protections — MAX-severity aggregation, ADOPT-CORRECTED catalog severities, and per-alert PPV budgets (HAZ-023) — reduce but do not remove this dependency. This is the honest cost of strictness (Concept A R2) and is a **ship-gate**, not a mitigation.

---

## 2. Escalation timers — ack-SLA breach drives the climb

Escalation is **timer-driven and visible**. Each active `watch`/`urgent`/`critical` alert runs its band's **ack-SLA clock** (from `severity-model` transitions L126–133). On breach it climbs one rung (`raised → escalated`, system+timer, audited). A **second** escalation fires on **action-SLA breach** once acknowledged-but-not-resolved (`acknowledged → escalated`).

| Band | Ack-SLA (raised → escalated) | Climb target | Action-SLA (acknowledged → escalated) | Source |
|---|---|---|---|---|
| `normal` | — (never climbs) | — | — | `CON-0065` |
| `watch` | **PT60M** unacked | R1 → **R2** (board + assigned-clinician push; **not** RRT) | PT2H | `severity-model` L30–33 |
| `urgent` | **PT10M** unacked | R2 → **R3** (RRT web push) | PT30M | `severity-model` L42–44 |
| `critical` | **PT2M** unacked | R3 → **re-page backup tier** (2nd RRT / attending, louder) | PT5M | `severity-model` L52–56 |

- **`watch` climbs to a clinician, never to the RRT.** An unacked `watch` promotes to R2 (assigned clinician's device) — this reconciles the band's base descriptor ("Tier 3 … no mobile page; no escalation", meaning it does not page *at raise*) with the lifecycle's `raised → escalated` transition (escalation exists on ack-window breach). Only `urgent` and `critical` ever reach R3/RRT.
- **Countdown is textual + redundant ring.** The numeric `MM:SS` (monospace tabular figures, `ADR-0006-01`) is the source of truth; the ring is decoration and is removed under `prefers-reduced-motion` (§10). The label shifts to the next-higher band color as it approaches breach.

### 2.1 One global fire-time clock — assignment can never extend a window *(graft: B; closes B's Repassar loophole)*

Concept B's recipient chain granted each hand-off a *fresh* Tier-1 timer, so serial hand-offs could stretch an `urgent`'s <30-min window unboundedly (score-clinical-safety-officer-b.yaml must_fix; HAZ-025). **Grafted correction:** there is **exactly one ack-SLA clock per alert, anchored to `created_at` (fire time), that NO reassignment resets.** `Atribuir`/`Repassar` re-point the *device* the push targets and re-annotate the rail; they do **not** restart, pause, or extend the countdown. A per-recipient sub-timer may drive *presence-widening* (§3.2) but is always bounded by, and never supersedes, the one global clock. This is contract-tested (§12).

### 2.2 Manual overrides (bounded, audited)

- **Escalar agora** — a clinician skips the timer and promotes now (e.g. Enf. Ana wants the RRT before the clock). Always allowed; audited (`INV-1`/`CON-0066`).
- **Adiar** (defer/snooze) — allowed for `normal`/`watch` **only**, time-boxed, audited; **barred for `urgent`/`critical`** (a strict-ladder guarantee, not a preference). Re-entry + governance semantics in §4.4 (MF-01, MF-05).

### 2.3 The PT10M urgent→R3 climb needs clinical sign-off *(must_fix MF-08)*

Paging the RRT at **10 min** unacked against `urgent`'s **30-min** action window (`CAT-C-03`) may systematically **over-page Rafael and train dismissal** (score-clinical-ux-researcher-a.yaml; `MOT-14` duplicate-dispatch trap). The PT10M ack→R3 climb is therefore held for **clinical sign-off at C3** against the 30-min action SLA; the shift-storm jitter (§7) and recipient-widening (§3) are the compensating controls. **Open question (C3):** confirm PT10M, or widen to COVERING first and reserve RRT for a later breach. Recorded, not silently resolved (CONTRACTS §5).

---

## 3. Role + shift-aware delivery — "who can act now" *(graft: Concept B)*

The ladder decides *loudness*; the **recipient resolver** decides *which human the rung's push addresses*. This is grafted from Concept B **only where it strengthens the ladder without complicating the tier guarantees** — the band still enters at its rung, the global clock still runs from fire-time, and **critical never depends on any of it** (§3.2).

### 3.1 The recipient chain

For every fired alert the server computes an ordered recipient chain **before** any surface lights up:

```
OWNER     = assigned clinician for this patient this shift        ← roster
            (bedside nurse for nursing-actionable; attending for physician alerts)
COVERING  = charge nurse / on-call intensivist for the setor      ← roster + on-call
RESPONDER = on-shift RRT physician (Rafael), hospital-wide         ← on-call, location-free
presence(role) = { at-workstation | on-unit-mobile | remote | scrubbed-in/busy | off-shift }  ← live presence
```

The rung a band enters is unchanged; the resolver fills in **to whom** each rung's push is addressed. R0/R1 are ambient (whole unit / signed-in clinician); R2 targets the OWNER's device; R3 targets the RESPONDER rotation.

### 3.1.1 The roster / on-call / RRT-rotation source — named + owned *(RT1-UX-01)*

The resolver's `← roster`, `← roster + on-call`, and `← on-call, location-free` inputs above were
previously "specified in no brief" — the model's top **unowned** dependency, so the anchor <5 s
targeted RRT dispatch could not ship. **v2 decision: the source is a local, tenant-scoped
`rrt_rotation` / on-call rotation table**, admin-maintained — **not** an external feed for MVP:

- **Mechanism (v2, owned).** A **local rotation table** (per `tenant_id`, scoped by `unit`/`setor` and
  by role OWNER / COVERING / RESPONDER) holds current + upcoming shift assignments and the RRT rotation.
  It is **admin-maintained** through the `admin-config.md` governance surface, and **every change is
  audited** (append-only, `INV-1` — the same versioned-config pattern as `threshold_config` and
  `alert_enablement`, `data-model.md` §4.5/§6). It is operational config, not clinical data.
- **Freshness SLA.** The rotation is **valid only for the shift it names** and MUST be refreshed
  **before each shift boundary**; the resolver treats a rotation whose active window has lapsed as
  **stale**. Freshness target: **the active RRT (RESPONDER) rotation entry is non-empty and current for
  the wall-clock shift, checked continuously** (dead-man below). Staleness never silences a page — it
  triggers **degrade-WIDER** (§3.2) and raises a coordinator flag.
- **Provably-non-empty RRT rotation — dead-man.** A **dead-man check** runs continuously over the
  RESPONDER/RRT rotation: an **empty *or* lapsed-window** active rotation **pages operations/coordinator
  *before* a critical needs the rung** (§5.3, MF-04), and R3 falls back to the **backup tier + audible
  board fallback** so no `critical` is ever sole-routed to an empty rotation. This is the
  persistence-backed form of §5.3's "provably non-empty at all times."
- **Future integration (ADR-deferred).** An **AMH staff-directory / on-call integration** (reading the
  authoritative hospital roster instead of a locally-maintained table) is recorded as a **future ADR** —
  desirable, but **not** an MVP dependency; the local table ships v2 so the ladder does not block on an
  unbuilt feed. When ratified, the directory becomes the table's upstream sync source.
- **Live presence stays open.** The rotation *source* is now owned; the **live-presence signal**
  (`at-workstation | on-unit-mobile | remote | scrubbed-in/busy | off-shift`) remains the one
  ratification-gated input (§3.2) — until it is reliable the resolver runs **shadow-mode with
  severity-broadcast live** and **narrowing stays gated** (open recon. 1). Rotation *membership* (who is
  on the RRT this shift) is **not** presence and ships with the table.

### 3.2 Safety rails on the resolver (tested invariants, not behaviors)

- **CRIT parallel multicast — never waits on an owner timer** *(salvage: B)*. `critical` fans out to owner chip **+** unit board **+** RRT web push **simultaneously** in the first wave; a <5-min window cannot afford a sequential owner-no-ack timer (score-clinical-safety-officer-b.yaml salvage; HAZ-025/HAZ-033; `MOT-14`).
- **Presence widens, never narrows.** If the OWNER is `scrubbed-in/busy`, `remote`, or `off-unit` at fire time, the resolver routes to COVERING (and, for CRIT, RESPONDER) **immediately in parallel** and marks the owner chip "notificado, indisponível". A busy-marked-available owner costs **at most the Tier-1 ack-SLA** before widening — never more (score-clinical-safety-officer-b.yaml must_fix; contract-tested).
- **Off-shift never resolves as OWNER; presence never gates CRIT** — encoded as tested invariants (score-clinical-ux-researcher-b.yaml must_fix; HAZ-025).
- **Degrade WIDER, never narrower** *(salvage: B)*. The **rotation source is now owned** — a local, audited `rrt_rotation` / on-call table (§3.1.1). What remains ratification-gated is the **live-presence signal**, which is specified in no brief. Until presence is reliable, the resolver runs in **shadow mode with severity-broadcast live** (owner/presence-unknown ⇒ route to unit board + on-call as if all present). A stale rotation **or** stale presence must **widen** reach, never silence a recipient (score-clinical-*-b.yaml must_fix; HAZ-025/HAZ-029). **Open dependency (C3):** live-presence signal — ratification-gated before any narrowing ships; the rotation table itself ships v2 (§3.1.1).
- **Day/night recipient reshaping** *(salvage: B)*. The same CRIT resolves to different humans at 10h vs 03h: by day OWNER=Carlos at a workstation; at night Carlos "cobre chamadas remotas" (`personas` flow) so he is `remote` → CRIT routes on-site RRT (Rafael) **primary** + a **remote awareness push** to Carlos, never assuming a remote attending can act now (`MOT-18`).

### 3.3 Recipient-level suppression — "is someone already acting?" *(salvage: B, scoped)*

The most surgical delivery-side fatigue lever (score-clinical-ux-researcher-b.yaml salvage; `MOT-13`; `VIS-7.1-04`): if a patient is **ASSISTIDO** or the OWNER is present and already acting, correlated **lower-tier repeats of the same `dedup_key`** are demoted to an ambient chip for *that recipient* — nobody re-summons a person already at the bedside. **Grafted only under three clamps** (score-clinical-safety-officer-b.yaml must_fix; HAZ-026):

1. It may demote **only same-`dedup_key` repeats/correlates**, and **only** for `normal`/`watch` channels — never `urgent`/`critical` delivery.
2. A **novel `alert_id`** (a new clinical problem) on the same patient **always notifies** — being at the bedside is not knowing the new K⁺ result.
3. A **class-crossing / severity upgrade** on the suppressed key re-fires and re-promotes regardless of ASSISTIDO (§4.3).

### 3.4 Accountability framing — coverage, not surveillance *(must_fix MF-03)*

The rail's `→ recipient + delivery-state + time-in-tier` annotation *(salvage: B; `MOT-05`)* and the countdowns must read as **coverage and hand-off, not clock-policing** — punitive framing kills disposition-feedback participation (score-clinical-ux-researcher-a.yaml MF; `MOT-08`/`MOT-09`). Requirements: labels frame the countdown as *tempo de cobertura até o próximo nível* (coverage-to-next-tier), not a performance clock; **individual attribution is visible to the coordinator role only**; the shared unit rail shows **role + delivery state, not performance scoring** (score-clinical-*-b.yaml MF; Concept B R6). **MM:SS bedside visibility MUST be validated with nurses** before v1 — flagged for usability sign-off (C2).

---

## 4. Per-patient alert budget + smart suppression — normal/watch ONLY *(graft: Concept C, vetoed)*

> ### ⛔ THE LOAD-BEARING INVARIANT
> **Critical and urgent alerts are NEVER budget-suppressed, budget-demoted, digest-held, rate-limited, or maintenance-muted. Budget and smart suppression touch `normal` and `watch` ONLY.**
>
> Concept C was **SAFETY-VETOED** because its router demoted `urgent` by one tier on budget-depleted patients, and budget depletion **correlates with acuity** — "the sickest patients fire the most alerts", so a new URG deterioration with a <30-min action window (`CAT-C-03`) on precisely the highest-risk patient would be delivered only to one clinician's non-interruptive chip, with no ack-SLA escalation to make it louder until the patient crossed into CRIT — peri-arrest. That is **HAZ-026** (suppression masking a real deterioration) + **HAZ-025** (no dead-man on unacked alerts) *as designed behavior* (`score-clinical-safety-officer-c.yaml` veto rationale; also `score-clinical-ux-researcher-c.yaml` safety=2). C's salvageable ideas are grafted below **only in forms that cannot suppress a critical or urgent alert.**

### 4.1 Per-patient budget (a governor on R0/R1, never a gate)

Each patient carries a **rolling budget of ≤ 3 escalation tokens / 24 h** for the `watch`/`normal` band (`false_positive_budget.target_max_per_patient_day: 3`, `CON-0088`/`PER-C-02`; per-alert `rate_limit 4/24h/patient`, alert schema). It is **not** a budget of alerts — every alert is still recorded to the prontuário at NGS-2 (`VIS-C-07`); the budget only governs how loudly a **non-critical, already-seen** signal is routed. Rendered as a small token-scaled **budget ring** with a **text label** (`2 restantes` / `limite atingido`, never color-only) on each patient chip and bed-detail.

| Ring state | Meaning | Routing effect (normal/watch only) |
|---|---|---|
| `healthy` (≥2) | quiet patient | severity floor unchanged |
| `near` (1) | approaching ceiling | new `normal` coalesces to R0 digest; board badge marks amber |
| `depleted` (0) | budget spent this window | new `normal`/`watch` **coalesce into the patient's R0 digest**, logged, never dropped |
| `bypassed` | a CRIT/URG or a **novel** band fired | ring dims to neutral; the alert routes at its full entry rung regardless of tokens |

**`urgent`/`critical` bypass the meter entirely** (`severity-model` L60; Concept A §3.5). The budget is a governor on the two lowest rungs; it is never a gate anywhere.

### 4.2 Smart suppression — what quiets a token *(salvage: C; upgrade-only)*

Runs **before** the router (alert-engine §5 order); every mechanism is **upgrade-only** and audited:

1. **Dedup + cooldown** — identical `dedup_key` (`mpi_id + alert_definition_id + criterion`) within cooldown **collapses into the existing rail row** with a `×N` recurrence count + "visto há Xs"; the **countdown does NOT reset** on a suppressed repeat, so suppression can never hide a climbing alert (score-clinical-*-a.yaml salvage; HAZ-026).
2. **Severity supersession with token refund** *(salvage: C)* — a higher-severity alert in the same domain **absorbs** the lower into one chip and **carries the HIGHER severity**, refunding the lower alert's token (HAZ-027-compliant since it upgrades, never downgrades).
3. **Correlation-collapse — upgrade-only** *(salvage: C)* — the three vision correlations (Sepse+AKI, Respiratória+Hemodinâmica, Drogas+Eletrólitos, `VIS-4-03`) merge co-firing alerts into **one correlated alert carrying the higher severity**, one token, one destination — and **every constituent remains individually inspectable and independently acknowledgeable** (`MOT-13`; HAZ-027; alert-triage §4/US-20). Correlation may only **ADD context or UPGRADE**; it may never drop a constituent below the severity it would fire on its own.

### 4.3 The hard clamps — universal invariants *(salvage: C)*

Encoded as tested invariants (not resolver behaviors), ratified with clinical sign-off (C's top risk; ADR-0014 severity-band RATIFY):

- **CRIT never demotes.** Budget only *dedups* a critical; it never withholds it.
- **Novel breakthrough — for EVERY band, not CRIT-only.** The **first fire of any band** (`normal`…`critical`) of a given `alert_id` on a patient **ignores budget and cooldown** (extends C's novel-CRIT carve-out to close the veto's novel-URG gap; `score-clinical-safety-officer-c.yaml` must_fix #3; `score-clinical-ux-researcher-c.yaml` "novel-urgent parity"; HAZ-026).
- **Class-crossing re-promotes and overrides ASSISTIDO** *(salvage: C)* — any suppressed/held alert whose value crosses into a higher band is instantly re-promoted (e.g. hipercalemia AMARELO→VERMELHO, `CAT-ELY-001`; delta-Na⁺ `CAT-C-01`/HAZ-032). **Acking can never mask a worsening trend.**
- **Nothing is silent** *(salvage: C)* — every held/collapsed alert is written to the prontuário (`VIS-C-07`) and is one click away in the digest with an auditable **reason code** (`deduped` / `superseded` / `budget-held` / `correlated`) — 100% auditable (`VIS-C-13`; §8).

### 4.4 Budget-held items must be *delivered*, not merely pull-able *(must_fix MF-02; C veto must_fix #4)*

"Logged and one click away" is **pull, not delivery** (`score-clinical-safety-officer-c.yaml` must_fix #4; HAZ-025). Two guarantees:

- **Forced digest flush.** A `watch` coalesced into the R0 digest is **force-flushed (pushed) to the OWNER before its action window (`PT2H`, `CON-0064`) elapses**, at a bounded fraction of that window (exact fraction **RATIFY at C3**) — so a held `watch` is *delivered*, never left to be discovered. `normal` (advisory, <6h) may remain digest-coalesced.
- **Re-promotion on worsening (MF-02).** A budget-coalesced digest item **re-promotes out of the digest on class-crossing OR on predicate re-fire at a higher band** — verified by **test vectors that a worsening signal can never remain coalesced** (decision.yaml MF; score-clinical-safety-officer-a.yaml MF; HAZ-026).

### 4.5 Adiar (defer) re-entry + governance *(must_fix MF-01, MF-05)*

- **Re-entry semantics (MF-01).** A deferred `watch`/`normal` whose predicate **re-fires re-enters at its rung** (defer never bars re-entry); defer is **time-boxed + audited** (`INV-1`). Verified by **test vectors** (a deferred watch whose predicate re-fires re-enters; HAZ-026).
- **Snooze-as-silence is a governed pattern (MF-05).** **Repeated `Adiar` on `watch`/`normal` feeds Fernanda's governance queue** (US-25 analytics in `admin-config.md`), **not just an audit row** — so snooze-as-silence surfaces as a *tunable pattern*, ranked by frequency (score-clinical-ux-researcher-a.yaml MF; `MOT-19`; Concept A R7).

### 4.6 Budget tuning is bounded + audited *(C veto must_fix #5)*

Per-patient budget overrides (e.g. tighten a known-CKD patient, loosen a fresh post-op) are **optional, default from severity, clamped to reference-derived safe ranges, rejected if out of range, and fully audited** — a mis-tuned tight budget is a tenant-config hazard (`score-clinical-safety-officer-c.yaml` must_fix #5; HAZ-029; governed via `admin-config.md`).

### 4.7 Budget as a coordinator noise diagnostic *(salvage: C, decoupled)*

Decoupled from routing, **unit-wide budget depletion is Fernanda's leading mis-tuning indicator** — a bed "loud but low-yield" (depleted, many holds) reads differently from one "critically escalating" — feeding the governance queue as telemetry (`MOT-19`/US-25; score-clinical-ux-researcher-c.yaml salvage). This is *diagnostic*, never a routing input.

---

## 5. Web-push PWA mechanics + delivery-failure fallback (dead-man interaction)

Delivery is the responsive web app + **PWA web push** (native app WON'T, product-spec §4; alert-triage §1.1).

### 5.1 PWA push mechanics

- **Transport.** Service Worker + Push API + VAPID; the RRT device holds a push subscription per authenticated session. `critical`/escalated-`urgent` fires a push whose **body is PHI-free and non-identifying** — a **severity band + a generic label ("novo alerta crítico") + an opaque deep-link token** only. It carries **no** score, trend, `Estabelecimento▸Setor▸Leito` location, vitals, or patient name, because a lock-screen preview is **pre-authentication** and bed+unit+time alone re-identifies the ICU patient (§0; I11 / REQ-INV-4-S3, security-lgpd §2.2/§3.3/§7; HAZ-034; LGPD Art. 46). The opaque token resolves the patient **server-side only after** the responder taps and the PWA completes in-app OIDC authN; the complete en-route card (`PER-RAFAEL-02` — **post-auth** completeness) then renders. This replaces the earlier "payload complete without unlock-then-navigate" with **"one authenticated tap to the complete card."**
- **Latency (dispatch vs content-load).** The **<5 s SLA is the *dispatch* budget — time to push *receipt*** (the interruptive page landing on the device): deliver-stage p95 **2 s < 5 s** (`budgets/latency.yaml` L69/L79; `CON-0092`/`PER-C-06`/`PER-RAFAEL-01`). Making the push PHI-free does **not** regress dispatch — the severity+token body is smaller and still arrives < 5 s. The clinical content now loads on a **separate, post-tap authenticated fetch** (deep-link → OIDC re-validate → server-side payload resolve), which adds a **content-load p95 *on top of*** the dispatch SLA, **not inside it**. Budget: an additional **≤ 2 s p95** for tap→complete-card (same deliver-class round-trip; the auth step is a warm-session token refresh, not a full login) — so **push-receipt p95 ≈ 2 s** and **tap-to-complete-card p95 ≈ 2 s more**, stated as an addition; the exact figure is **co-owned with latency-architecture and RATIFY at C3** (open recon. 5). Bed-board and push share the **one channel/latency class** (`ADR-C-13`) so they cannot disagree.
- **At-least-once + effectively-once UX.** ARQ native retry + exponential backoff on every notification (`INV-6`/`CON-0071`); each push carries the `dedup_key` + a monotonic `version`; the client dedups on it (`CON-0045`/`ADR-C-12`). Acking from the push marks ASSISTIDO on board + chip in the same instant.

### 5.2 Push-undeliverable is itself an escalation event *(salvage: B)*

A push not channel-acked within its budget is **never a silent no-op** — it is an **escalation event** (score-clinical-*-b.yaml salvage; HAZ-025; `MOT-14` delivery≠awareness). On repeated failure the router **degrades wider**: re-page the **backup tier**, raise the **audible board fallback**, and page the staleness watchdog. Exhausted retries route to a **DLQ that itself raises an operational alert** — no alert is ever silently dropped (`INV-6`; alert-engine §7.1).

### 5.3 Dead-man: the R3 rotation must be provably non-empty *(must_fix MF-04)*

An empty top rung is **silent non-delivery** (score-clinical-safety-officer-a.yaml MF; HAZ-025). Requirements:

- **R3 targets an on-call rotation/role, not a person** (Concept A R3) — the **owned local `rrt_rotation` table** (§3.1.1), with a **backup tier** on PT2M breach.
- **The rotation MUST be provably non-empty at all times**, enforced by a **dead-man alarm on an unstaffed *or stale* rotation** — an empty or lapsed-window R3 pages operations/coordinator *before* a critical needs it, and R3 falls back to backup tier + audible board so no `critical` is ever sole-routed to an empty rung. The check reads the **audited rotation table** (§3.1.1) against wall-clock shift and its **freshness SLA**; an empty *or* stale active window both trip the dead-man.
- **External watchdog** (`INV-5`/`CON-0070`, outside the ECS service) probes `/api/v1/health` every **≤ 30 s** (aligned to `VIS-C-09`); the **staleness watchdog** (alert-on-no-alerts per `(unit, domain)`) converts pipeline silence into a paged operational alert (alert-engine §7.2). Delivery receipts make delivery≠awareness observable.

---

## 6. Quiet-hours + maintenance-window semantics

Both reshape **ambient loudness for `normal`/`watch` only** and **never** suppress or delay a page. Interpreted narrowly for ICU safety (a tightening of alert-engine §5's maintenance carve-out, consistent with the veto):

- **Maintenance windows** (`maintenance_window_aware`, alert schema) — a known procedure, patient transport, turnover, or device recalibration. During the window, **R0/R1 ambient badges/audible cues for `normal`/`watch` are muted**, but the alert **still logs to R0 + the prontuário** (nothing silent). **`urgent` and `critical` are never maintenance-muted** (patient-safety carve-out; `severity-model` L60). A **class-crossing or novel** event breaks through the window (§4.3).
- **Quiet hours** (night reshaping, `MOT-18`) — modulate **presentation** of `normal`/`watch` (suppress non-critical audible chip sounds, prefer digest coalescing) and reshape **recipients** to the night roster (§3.2 day/night), while the wall board stays a calm-but-live ambient safety net ("silence = verified normal", `MOT-18`). Quiet hours **never** silence, delay, or demote any page, and **never** touch `urgent`/`critical`.
- Every window entry/exit and every mute decision is **audited** (§8) and disclosable.

---

## 7. Shift-change page-storm control *(must_fix MF-06, MF-07)*

Timer-driven promotion can fire **many R2→R3 climbs at once** when a cohort of `urgent` alerts ages out together — worst-case in the **handover window** `MOT-17` protects, the worst-case RRT flood (`MOT-14`), itself an alarm-fatigue + latency hazard (HAZ-023, HAZ-033). Two must_fix, both **shipping with v1, not later**:

- **MF-06 — jittered escalation + handover-aware batching, specified and load-tested.** Climb timers carry **per-alert jitter** so a synchronized cohort does not breach in lockstep; escalation is **handover-aware batched** across the roster-change boundary. This path is **load-tested** at the >500 alerts/min throughput target (`VIS-C-11`) for a synchronized R2→R3 cohort at handover (score-clinical-safety-officer-a.yaml MF; HAZ-023/HAZ-033).
- **MF-07 — charge-nurse batch triage view ships v1.** A **charge-nurse batch triage view** (the "Roteamento" rail filtered to the unit's climbing cohort, with bulk Aceitar/Atribuir) ships with v1 so a handover cohort can be triaged as a batch rather than as a page storm (score-clinical-ux-researcher-a.yaml MF; `MOT-17`/`MOT-14`).
- CRIT is exempt from batching/jitter — it always multicasts immediately (§3.2). Residual risk is real and acknowledged (Concept A R1): the strict clock does not care that everyone is in handover, so the jitter + batch view are the compensating controls, and the **escalation-breach rate** (§8) surfaces a unit systematically letting alerts climb at handover as a **staffing signal** for Fernanda.

---

## 8. Audit of every delivery decision — the reason-coded delivery ledger

**Every routing and delivery decision writes one immutable append-only `audit_trail` row** (`INV-1`/`CON-0066`; append-only + anti-mutation trigger; LGPD + CFM 2.299/2021, `VIS-C-07`; HAZ-034). This is the reason-coded suppression ledger *(salvage: C)* one click away from every alert (score-clinical-*-c.yaml salvage; `MOT-09` trust-through-transparency). The ledger records, per alert:

| Decision | Audited fields |
|---|---|
| **Entry + rung** | `alert_id`, `alert_definition_version`, entry rung, aggregated band (MAX-severity provenance) |
| **Recipient resolution** | OWNER/COVERING/RESPONDER resolved, each recipient's **presence state**, day/night reshape applied |
| **Each channel dispatch** | channel (chip/board/push), target device/role, timestamp, **delivery receipt or failure**, retry count, DLQ |
| **Each climb** | from-rung → to-rung, ack-SLA vs action-SLA trigger, breach timestamp, jitter applied |
| **Each hold/collapse** | reason code `deduped` / `superseded` / `budget-held` / `correlated`, refunded token, digest membership, **forced-flush timestamp** |
| **Each mute** | maintenance-window / quiet-hours entry+exit, band muted, break-through (class-crossing/novel) if any |
| **Each manual override** | `Escalar agora` / `Adiar` (+ time-box, re-entry) / `Atribuir` / `Repassar`, actor, timestamp |
| **Global clock** | `created_at` anchor, that no reassignment reset it (§2.1) |

- **Nothing is silent** *(salvage: C)*: every held alert is also written to the prontuário at NGS-2 and disclosable (`VIS-C-07`/`VIS-C-13`).
- The ledger **feeds PPV/response analytics** (co-owned, C3; alert-triage §5–6): `resolution` → PPV = TP/(TP+FP) (≥60%, `VIS-7.1-02`); `acknowledged_at − created_at` → time-to-recognition; `resolved_at − created_at` → time-to-action (≤15 min, `VIS-7.1-03`); expired-unacked/total → alarm-fatigue (≤10%, `VIS-7.1-04`); **escalation-breach rate** (alerts that climbed because nobody acked in SLA) is Fernanda's first-class continuous KPI *(salvage)* (score-clinical-*-a.yaml salvage; `PER-FERNANDA-02`/`MOT-19`). All flow to Gold `fact_alert` (`CON-0028`).
- A "não procede" disposition **NEVER silently disables an alert type** — it only feeds analytics + the governance queue (alert-triage §2.4/US-22 AC3; `MOT-09`).

---

## 9. States (exhaustive)

- **Lifecycle** (`severity-model` L109; alert-triage §2): `raised · acknowledged · acting · resolved · expired · escalated`.
- **Timer states (per row):** `contando` · `próximo do limite` (breach-imminent, color shifts to next band) · `estourado → escalonado` · `pausado` (acked/ASSISTIDO).
- **Rung/channel states:** on-rung R0–R3 · `suprimido` (cooldown, `×N` count) · `agrupado no orçamento` (budget-coalesced digest, normal/watch only) · `silenciado (manutenção)` / `silenciado (horário noturno)` (muted, still logged) · `escalonado` · `re-paginado (reserva)` (backup tier after R3 breach).
- **Recipient states** *(graft: B):* `entregue/não reconhecido` · `escalando (↑)` · **ASSISTIDO** (additive `clinical.status.attended` badge rendered alongside the unchanged severity — **never** a severity override or desaturation; timers stopped, lower-tier same-key demoted) · `dono indisponível` (presence widened) · `push não entregue → escalado`.
- **Realtime (whole surface):** `ao vivo` · `reconectando` (shared backoff, `ADR-C-12`) · `defasado` (last-updated stamp + freshness veil, fixing silent staleness `ADR-0017`) · `offline`. All from the ONE channel.
- **Loading:** content-shaped skeleton rail (`ADR-0016`), never a full-viewport blocking loader (`DES-5-07`); staff keep triaging other rows.
- **Partial failure:** an un-hydrated row shows inline error + retry, not a screen-wide `Modal.error` (`ADR-C-11`).
- **Empty:** "tudo estável" calm empty state, not an error.

---

## 10. Accessibility (WCAG 2.2 AA — `ADR-C-04`)

- Severity by **color + icon + shape + text** on every rung row, badge, chip, and push (§1); never color alone.
- **Countdowns are textual** `MM:SS`; the ring is redundant. `prefers-reduced-motion` removes the ring + climb animation, leaving the numeric timer and an instantaneous rung change.
- **Live regions:** `aria-live="assertive"` for a new `critical` and for **any SLA breach / climb**; `polite` for lower-severity arrivals and de-escalations. Each announcement names bed, patient, severity, **rung change**, recipient, and triggering parameter.
- **Keyboard:** the rail is a roving-tabindex list; **Aceitar / Atribuir / Escalar agora / Adiar** each reachable with a visible `focus-visible` ring; Enter opens bed detail, Esc returns.
- **Contrast:** all `clinical.*` + timer-label tokens contrast-checked over the neumorphic **dark** and light surfaces before ship; legibility never depends on the severity glow. `prefers-contrast` flattens elevation to a solid high-contrast border. Board severity legible **by shape + color at meters** for the night monitor-wall glance (`CON-SEED-11`; `MOT-18`).
- **Audible R3 cue** is paired with the visible assertive announcement (never the only channel) and is user-mutable per session without muting the visual page.

### 10.1 Accessibility gate (A11Y-GATE — per `accessibility-standard.md` §8) *(RT1-COMP-02)*

Per-ID check-off against the binding gate; each item is satisfied on this surface or marked **N/A**
with rationale. This subsection converts §10's prose into gate-ID citations — `accessibility-standard.md`
§8 treats a missing gate subsection as a back-to-owner completeness failure (equivalent to a missing
test-vector set).

- [x] **A11Y-GATE-01** (text/critical contrast, SC 1.4.3/1.4.6) — §10: all `clinical.*` + timer-label
      tokens contrast-checked over dark **and** light before ship; `critical` numerics on the rail /
      en-route card meet AAA 7:1 (`A11Y-REQ-01`). Tokens are consumed here, not defined.
- [x] **A11Y-GATE-02** (non-text contrast, SC 1.4.11) — §10: severity borders/glow, status ball,
      countdown ring, and `focus-visible` rings ≥ 3:1 against adjacent surfaces, in both themes.
- [x] **A11Y-GATE-03** (never color-alone) — §0 / §1: severity is **triple-encoded — color + icon +
      shape + text** on every rung row, badge, chip, and the PHI-free push severity band (§1 encoding
      table + §9 states).
- [ ] **A11Y-GATE-04** (palette CVD ΔE method) — **N/A**: this screen **defines no severity palette**;
      it consumes the ratified `clinical.*` tokens whose CVD/ΔE validation is owned by
      `accessibility-standard.md` §2.2 + `design-tokens.md`. No hex is proposed or edited here.
- [x] **A11Y-GATE-05** (≤ 3 Hz flash; reduced-motion) — §2.2 / §10: the countdown ring + the row-rise
      climb animation are decoration; **`prefers-reduced-motion` removes them**, leaving the numeric
      `MM:SS` and an instantaneous rung change. No pulsing/flashing severity treatment is used
      (`A11Y-REQ-13`) — a new `critical` uses a static high-contrast border + text, never a pulse.
- [x] **A11Y-GATE-06** (icon+shape distinct at smallest size) — §1 encoding table + §10: severity is
      legible **by shape + color at meters** for the night monitor-wall; icon+shape pairs differ for
      every band at the smallest rail-chip / badge render size.
- [x] **A11Y-GATE-07** (encoding from live severity, no hardcoded literal) — §0 MAX-severity
      aggregation + §1: every severity glyph derives from the alert's **current aggregated** band;
      **ASSISTIDO** is an additive badge composited *alongside* the true severity, **never** replacing
      or desaturating it (§1 / §9) — no hardcoded `'VERMELHO'`-style literal anywhere.
- [x] **A11Y-GATE-08** (overlay Esc/back/focus-trap/depth ≤ 2) — the **Escalation Rail is a non-modal
      inline panel** (no focus trap; roving-tabindex list, §10). Any **drawer it opens** (bed detail via
      Enter, §10) inherits the global overlay-stack contract (`A11Y-REQ-07..11`,
      `accessibility-standard.md` §3): Esc / back close only the topmost, `role="dialog"` + `aria-modal`,
      focus restored to the rail row; stack depth ≤ 2.
- [x] **A11Y-GATE-09** (aria-live per §5.1 + coalescing) — §10 live regions: `assertive` for a new
      `critical` and **any SLA breach / climb**, `polite` for lower-severity arrivals / de-escalations.
      **One live-region container per severity tier**, coalesced at ≥ ~1 announcement / 2 s under bursts
      (shift-storm §7 / handover cohort), stating count + latest (`A11Y-REQ-16/17`) — the **visual**
      page is never delayed, only the spoken narration is debounced.
- [x] **A11Y-GATE-10** (accessible-name order) — §10: each announcement follows **severity →
      triggering parameter + value + trend → location (bed/patient)** (`A11Y-REQ-18`), plus rung change +
      recipient; never severity/location alone.
- [x] **A11Y-GATE-11** (24 px floor / 44 px ack) — **Aceitar / Atribuir / Escalar agora / Adiar** and
      the 1-tap push actions **Aceitar / A caminho** meet the **44×44** floor (`CON-0091`/`PER-C-05`,
      `A11Y-REQ-21`); every other rail pointer target meets the 24×24 floor (`A11Y-REQ-20`).
- [x] **A11Y-GATE-12** (no pure #FFF/#000; prefers-contrast) — §10: `prefers-contrast` flattens the
      neumorphic elevation to a solid high-contrast border; legibility never depends on the severity
      glow; surfaces use the ADR-0002/0003 near-black/near-white, never pure `#FFF`/`#000`
      (`A11Y-REQ-23/24`).
- [ ] **A11Y-GATE-13** (drag alternative) — **N/A**: this screen has **no drag interactions**. Rail
      rows *animate* between rung groups on timer breach (system-driven, not user-draggable); all actions
      are click / tap / keyboard.
- [x] **A11Y-GATE-14** (accessible authentication) — **authentication is OIDC via IAM Identity Center
      (no PIN)**; the RRT push→tap flow completes **in-app OIDC authN** before any clinical content
      renders (§5.1), and any clinical e-signature / ack weight follows `accessibility-standard.md` §7 +
      `security-lgpd.md` §5.1 (no shared-PIN, a non-cognitive-only path, `A11Y-REQ-25`).
- [x] **A11Y-GATE-15** (custom-component name/role/state) — every custom primitive on the rail
      (severity chip, status **Ball**, countdown timer, budget ring, ASSISTIDO badge, rung rows) exposes
      an accessible name/role/state (§9 states + §10 roving-tabindex) — no bare `<div onClick>`
      (SC 4.1.2).
- [x] **A11Y-GATE-16** (form engine no redundant entry) — the **desfecho** documentation form off the
      en-route / triage surface (§1.1) runs on the schema-driven form engine, which MUST NOT re-ask data
      already captured earlier in the same flow (SC 3.3.7); binds `form-engine-designer` (`alert-triage §3`).

---

## 11. How each persona succeeds

- **Dr. Rafael — RRT (anchor).** Sits at R3, receives **only what earned R3** (critical direct + aged-out urgent), web push < 5 s (`PER-RAFAEL-01`/`CON-0092`) — a **PHI-free page** (severity + opaque token) that becomes a **complete en-route response card after one authenticated tap** (`PER-RAFAEL-02` = **post-auth** completeness, §5.1); **Aceitar** stops the R3 clock and pre-empts the backup re-page; **A caminho** signals en route; desfecho < 1 min (`PER-RAFAEL-03`). Never touched by `watch`/`normal` noise; day/night reshaping makes him primary at night (§3.2).
- **Enf. Ana — nurse (catcher).** Lives at R1/R2; auto-computed scores (`PER-ANA-01`); the row names the deranged parameter (`PER-ANA-02`/`PER-C-04`); one-click **Aceitar** stops the climb and flips the bed to ASSISTIDO (`PER-ANA-03`/`PER-C-05`); she sees the coverage countdown and can **Escalar agora**; her guaranteed backup is the COVERING chain (§3.1).
- **Dr. Carlos — intensivista.** The strict ladder + normal/watch budget keeps him at chip/board and never pages him unless something reaches `critical` or ages out — cutting his 200-alert/80%-FP load toward < 3 FP/patient-day (`PER-C-02`); presence widening covers him when he scrubs in; correlation-collapse gives him one story, not three (`MOT-13`).
- **Dra. Fernanda — coordenadora.** The delivery ledger **is** her quality instrument: live per-rung counts, mean time-to-ack per band, **escalation-breach rate**, budget-depletion noise diagnostic, and the snooze-as-silence governance pattern — continuous, exportable to hospital quality tooling (`PER-FERNANDA-02`/`PER-C-08`; `MOT-19`).

---

## 12. `must_fix` traceability *(decision.yaml — all MANDATORY)*

| # | must_fix (decision.yaml) | Addressed | Verification |
|---|---|---|---|
| **MF-01** | Adiar re-entry semantics verified by test vectors; defer time-boxed + audited (HAZ-026). | §2.2, **§4.5** | Test vectors: deferred watch predicate re-fires → re-enters at rung; defer expiry audited. |
| **MF-02** | Budget-coalesced R0 digest re-promotes on class-crossing or predicate re-fire at higher band; worsening never stays coalesced (HAZ-026). | **§4.4**, §4.3 | Test vectors: worsening signal can never remain coalesced. |
| **MF-03** | Countdown framing at bedside validated with nurses (coverage, not clock-policing) (MOT-08/09). | **§3.4**, §2, §10 | Nurse usability sign-off (C2); coordinator-only individual attribution. |
| **MF-04** | R3 rotation provably non-empty + dead-man alarm on unstaffed rotation (HAZ-025). | **§5.3** | Chaos test: kill rotation → dead-man alarm; watchdog ≤30s. |
| **MF-05** | Repeated Adiar feeds the governance queue (US-25), not just an audit row (MOT-19). | **§4.5** | Governance queue ranks snooze-as-silence patterns. |
| **MF-06** | Shift-change storm (own R1): jittered escalation + handover-aware batching specified + load-tested (HAZ-023/033). | **§7** | Load test at >500 alerts/min for synchronized handover cohort. |
| **MF-07** | Shift-change storm (their R1 / MOT-17): jittered/staggered climbs + charge-nurse batch triage view ship v1 (MOT-14). | **§7** | Charge-nurse batch view in v1 scope; jitter shipped. |
| **MF-08** | PT10M urgent→R3 climb needs clinical sign-off vs CAT-C-03's 30-min window (MOT-14). | **§2.3** | C3 clinical sign-off; open question recorded, not resolved. |
| **MF-09** | Upstream band assignment clears SYS-C-03 RATIFY before the strict ladder ships (own R2). | **§1.2** | Ship-gate: all P0/band rules RATIFY-dispositioned before ladder ships. |

**must_fix addressed = 9/9.**

---

## 13. Salvage register (grafted from Concepts B and C)

| Idea | From | Grafted at | Constraint on the graft |
|---|---|---|---|
| CRIT parallel multicast — never waits on an owner timer | **[salvage:b]** | §3.2 | universal; critical is presence-independent (HAZ-025/033). |
| Degrade WIDER, never narrower (roster/presence fallback) | **[salvage:b]** | §3.2 | shadow-mode default until roster/presence ratified. |
| Day/night recipient reshaping (Carlos remote → RRT primary + awareness push) | **[salvage:b]** | §3.2, §6 | never narrows reach; matches persona flow. |
| Recipient-level suppression ("is someone already acting?") | **[salvage:b]** | §3.3 | same-key repeats **only**, normal/watch **only**; novel + class-crossing always notify. |
| Push-undeliverable is an escalation event | **[salvage:b]** | §5.2 | failed push degrades wider; never a silent no-op (HAZ-025). |
| `→ recipient + delivery-state + time-in-tier` rail annotation | **[salvage:b]** | §1, §3.4 | role + state on shared rail; individual attribution coordinator-only. |
| One global fire-time clock (closes Repassar loophole) | **[salvage:b]** | §2.1 | reassignment never resets the ack-SLA clock. |
| Severity supersession with token refund | **[salvage:c]** | §4.2 | carries the HIGHER severity (HAZ-027). |
| Correlation-collapse — upgrade-only merging | **[salvage:c]** | §4.2 | constituents remain inspectable + independently ackable. |
| Class-crossing re-promotion overrides ASSISTIDO | **[salvage:c]** | §4.3 | acking can never mask a worsening trend. |
| Novel breakthrough + class-crossing clamps as universal invariants | **[salvage:c]** | §4.3 | novelty carve-out extended to **every band**, not CRIT-only. |
| Reason-coded suppression ledger, one click away | **[salvage:c]** | §8 | `deduped/superseded/budget-held/correlated` (HAZ-034; MOT-09). |
| "Nothing is silent" — held alerts charted + disclosable | **[salvage:c]** | §4.3, §8 | prontuário NGS-2 (VIS-C-07/13). |
| Budget ring as coordinator noise diagnostic | **[salvage:c]** | §4.7 | decoupled from routing; telemetry only. |
| Unit-wide depletion → governance queue mis-tuning indicator | **[salvage:c]** | §4.7, §8 | feeds US-25 (MOT-19). |
| Escalation-breach rate as continuous coordinator KPI | **[salvage:a]** | §8 | first-class time-to-action/fatigue signal (PER-FERNANDA-02). |
| Suppressed-repeat-does-not-reset-the-clock | **[salvage:a]** | §4.2 | suppression can never hide a climbing alert (HAZ-026). |

---

## 14. Constraints owned / discharged + open reconciliations

| Constraint / story | Barrier | Where |
|---|---|---|
| `severity-model` tiers + ack/action SLAs (LAW) | C2 | §0, §1, §2 |
| `CON-0092`/`PER-C-06`/`PER-RAFAEL-01` RRT push <5s | C3 | §1.1, §5.1 |
| `CON-0062..0065` action SLAs · `CON-0088`/`PER-C-02` <3 FP/patient-day | C3 | §1, §2, §4 |
| `CON-0182`/HAZ-010 never-downgrade (MAX-severity) | C3 | §1 |
| `INV-1`/`CON-0066` every decision audited · `VIS-C-07`/`VIS-C-13` nothing silent | B/C3 | §8, §4.3 |
| `INV-5`/`CON-0070` dead-man · `INV-6`/`CON-0071` at-least-once delivery | B/C3 | §5.2, §5.3 |
| `rrt_rotation` local roster/on-call/RRT-rotation source (owned, audited) — RT1-UX-01 | B/C3 | §3.1.1, §5.3 |
| PHI-free push payload (I11 / REQ-INV-4-S3; no PHI/locator pre-authN) — RT1-SEC-01 | B | §0, §1.1, §5.1 |
| `CON-0045/0046/0053`/`DES-C-05` one realtime channel | C3 | §0, §5.1 |
| `CON-SEED-11` triple-encoded severity · `CON-0041`/`ADR-C-08` clinical/brand decoupling | C2 | §0, §1, §10 |
| HAZ-025/026/027/029/034 routing-safety hazards | veto-gate | §3–§5, §8 |
| `SYS-C-03` band-assignment RATIFY before ladder ships | ship-gate | §1.2 |

**Open reconciliations (recorded, not resolved — CONTRACTS §5):**
1. **Live-presence signal** — required by §3.2, specified in no brief; degrade-wider shadow-mode is the default until ratified (C3, amh-integration + platform-reliability). **Resolved for the source half (RT1-UX-01):** the roster / on-call / RRT-rotation **source** is now owned — a local, tenant-scoped, admin-maintained, audited `rrt_rotation` table (§3.1.1), with an AMH staff-directory integration deferred to a future ADR; only **live presence** remains ratification-gated before any narrowing ships.
2. **PT10M urgent→R3 climb** vs the 30-min URG action window — clinical sign-off (C3; §2.3).
3. **Forced digest-flush fraction** of the watch PT2H window (§4.4) — clinical sign-off (C3).
4. **Status enum extension** `acting`/`escalated` (and delivery-only `info`/`normal` for Tier-4 advisory rows) — data-architect (C2), per `severity-model` + alert-triage reconciliation notes.

---

```yaml routing-ladder
# Machine-readable summary of the routing spine + invariants (this file is the source of truth).
version: 1
ladder:
  - {rung: R0, surface: dashboard-chip,        band: normal,   tier: 4, ack_sla: null,  climb_to: null, paging: false, rate_limited: true}
  - {rung: R1, surface: unit-board-badge,      band: watch,    tier: 3, ack_sla: PT60M, climb_to: R2,   paging: false, rate_limited: true}
  - {rung: R2, surface: board+targeted-push,   band: urgent,   tier: 2, ack_sla: PT10M, climb_to: R3,   paging: true,  rate_limited: true}
  - {rung: R3, surface: rrt-webpush+audible,   band: critical, tier: 1, ack_sla: PT2M,  climb_to: backup-tier, paging: true, rate_limited: false, rrt_push_sla: PT5S, phi_free_push: true, push_payload: severity-band+opaque-deeplink-token-only, dispatch_sla_measures: push-receipt, content_load_post_authn_p95: PT2S}
invariants:
  - id: INV-ROUTE-01
    text: "critical and urgent alerts are NEVER budget-suppressed, budget-demoted, digest-held, rate-limited, or maintenance/quiet-muted"
    source: [score-clinical-safety-officer-c.yaml#veto, HAZ-025, HAZ-026, severity-model.yaml#L60]
  - id: INV-ROUTE-02
    text: "budget + smart-suppression modulate normal/watch ONLY; the first fire of ANY band bypasses budget (novel breakthrough)"
    source: [score-clinical-safety-officer-c.yaml#must_fix-1-3, score-clinical-ux-researcher-c.yaml#novel-urgent-parity, HAZ-026]
  - id: INV-ROUTE-03
    text: "one ack-SLA clock per alert anchored to created_at; no reassignment (Atribuir/Repassar) resets, pauses, or extends it"
    source: [score-clinical-safety-officer-b.yaml#Repassar, HAZ-025]
  - id: INV-ROUTE-04
    text: "MAX-severity-wins; a band enters at its rung and can never be delivered below it; the ladder ratchets up only"
    source: [CON-0182, P0-10, HAZ-010, severity-model.yaml#L63-70]
  - id: INV-ROUTE-05
    text: "class-crossing / severity upgrade / novel alert_id re-promotes and overrides ASSISTIDO and all suppression"
    source: [HAZ-026, HAZ-027, CAT-ELY-001, CAT-C-01]
  - id: INV-ROUTE-06
    text: "critical multicasts to all tiers in parallel, never waits on an owner timer, never gated by presence"
    source: [score-clinical-safety-officer-b.yaml#salvage, HAZ-025, HAZ-033]
  - id: INV-ROUTE-07
    text: "no silent non-delivery: push-undeliverable escalates wider; R3 rotation provably non-empty w/ dead-man; every held alert charted + reason-coded"
    source: [INV-5, INV-6, CON-0070, CON-0071, HAZ-025, HAZ-034, VIS-C-07]
  - id: INV-ROUTE-08
    text: "every routing/delivery decision writes one immutable audit_trail row"
    source: [INV-1, CON-0066, VIS-C-07]
  - id: INV-ROUTE-09
    text: "the web-push page is PHI-free and non-identifying (severity band + opaque deep-link token only; NO score/trend/location/vitals/name on the lock screen); all clinical content renders only inside the authenticated PWA post-tap; the <5s SLA measures dispatch=push-receipt, and the post-tap authenticated content fetch adds a separate content-load p95 on top of (not inside) the dispatch SLA"
    source: [security-lgpd.md#I11, REQ-INV-4-S3, HAZ-034, LGPD-Art-46, MOT-14]
  - id: INV-ROUTE-10
    text: "the roster/on-call/RRT-rotation source is a local, tenant-scoped, admin-maintained, audited rrt_rotation table (v2); the active RRT rotation is provably non-empty via a dead-man on an empty-or-stale window; live-presence stays ratification-gated (narrowing gated) while the rotation table ships v2"
    source: [RT1-UX-01, INV-1, HAZ-025, admin-config.md#roster, data-model.md#4.5]
ship_gates:
  - "upstream band assignment clears SYS-C-03 RATIFY before the strict ladder ships (MF-09)"
  - "shift-change jitter + charge-nurse batch triage view ship with v1 (MF-06, MF-07)"
open_reconciliations: [live-presence-signal, amh-directory-roster-adr, rrt-push-content-load-p95, urgent-R3-PT10M-signoff, digest-flush-fraction, status-enum-acting-escalated-info]
```
