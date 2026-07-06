# Screen Spec — Alert Triage & Lifecycle

**Owner:** alerting-ux-specialist · **Status:** draft for reconciliation barriers **C2** (severity + lifecycle UX) and **C3** (latency + PPV) · **Authority precedence:** ADR-001 ≻ vision ≻ directive ≻ audit (CONTRACTS §5).

This spec defines the end-to-end alert UI: how an alert is **raised**, **acknowledged** (one-tap, audited), **acted on** (structured one-click outcome), and **resolved** (with true/false-positive feedback that feeds PPV analytics); how it is **routed** by severity from a dashboard chip → unit board → mobile push to the RRT in <5s; how every alert always shows **why** it fired; and the **alarm-fatigue analytics** surface for coordinators. It renders the machinery already specified in `architecture/alert-engine.md` (lifecycle §9, severity §3, suppression §5, delivery §7) and `_work/platform/severity-model.yaml`. It invents no clinical content — cutoffs live in the alert catalog and units registry.

Every claim cites a source: a ledger constraint (`CON-*`), a brief fact (`VIS-*`, `CAT-*`, `DM-*`, `PER-*`, `DES-*`, `ADR-*`), a user story (`US-*`), or an invariant (`INV-*`).

---

## 0. Design-system frame (what this screen is built from)

- **Home surface is the bed-grid command center**; alerts surface as tiles/chips that drill down into a managed **drawer/overlay stack** with Esc/back + focus-trapping (`ADR-0009`, `ADR-0010`). No modal-routing; the drawer stack manager replaces the legacy 4-deep uncoordinated `DrawerBuilder` nesting (`DES-4-04`).
- **Dark-first "quiet ICU" aesthetic** with a symmetric token-driven light theme (`ADR-0002`/`ADR-0003`). Neumorphic elevation is a governed token pair with WCAG contrast verification in both themes (`ADR-0007`/`CON-0037`).
- **Severity color is `clinical.*`, structurally separate from tenant `brand.*`** (`CON-0041`/`CON-0049`/`DES-C-01`). Rebranding a tenant must never change what a severity color means. Severity is **always triple-encoded — color + icon + shape** (`CON-SEED-11`) so it survives colour-blindness/greyscale (WCAG 1.4.1). The two legacy severity bugs are **fixed, not ported**: toast/icon color derives from the alert's actual severity (never hardcoded amber, `DES-5-03`), and each criterion is colored by *its own* value (never a hardcoded `VERMELHO`, `CON-0042`/`ADR-C-09`).
- **One realtime push channel** (WebSocket + SSE fallback, shared reconnect/backoff) feeds alerts, bed grid, and presence (`ADR-0017`/`CON-0045`/`CON-0046`/`DES-C-05`). The bed board **never polls** — a red alert reaches the grid and the toast through the same latency class so they cannot disagree about one event (the legacy `tempo_atualizacao` polling gap, `DES-6-02`).
- **Abnormal-value flagging is a first-class service** (`ADR-0014`/`CON-0054`/`DES-C-06`): vitals/labs/fluid-balance/SOFA bands drive critical-value highlighting — the legacy "no flagging anywhere" gap (`DES-5-04`) is closed here.
- **Route permission is deny-by-default, enforced server-side** ahead of shell render, and the API independently authorizes every request (`CON-0038`/`CON-0047`/`DES-C-08`). The client guard is UX/defense-in-depth only.

---

## 1. Severity-tiered routing — dashboard chip → unit board → RRT push

One canonical four-band scale drives every routing decision (`severity-model.yaml`; alert-engine §3). Encoding and delivery tier are fixed per band; **tenant branding cannot alter them**.

| Band | Encoding (color · icon · shape) | Delivery tier | Where it appears | Push / page |
|---|---|---|---|---|
| **normal** | green · check-circle · circle | **Tier 4** | bed-board/worklist advisory chip only | none — suppressible/coalescable into a digest (`severity-model` normal) |
| **watch** | amber · eye · rounded-square | **Tier 3** | dashboard chip + bed-board badge | WS push; no mobile page; ack expected < 60 min |
| **urgent** | orange · exclamation · triangle | **Tier 2** | dashboard chip + bed-board + mobile | WS push + **mobile push**; ack expected < 10 min; escalate on ack-SLA breach |
| **critical** | red · alert-octagon · octagon | **Tier 1** | interruptive everywhere + audible | WS push + **mobile page to RRT <5s** (`CON-0092`/`PER-C-06`) + bed-board + audible; **mandatory ack < 2 min**; **never rate-limited** (`severity-model` critical) |

### 1.1 The three routing surfaces (one event, three views, one channel)

1. **Dashboard chip (Dra. Fernanda / occupancy view, US-06/US-09).** A per-unit severity chip row: count of active alerts per band, highest-band color/icon/shape leading. Clicking a chip opens the unit's alert worklist filtered to that band. The chip updates over the **same push channel** as the board (`CON-0046`) — no separate poll.
2. **Unit bed board (Dr. Carlos / Enf. Ana, the core screen, `DES-4-03`).** Each bed tile carries its patient's **highest active severity** as border + glow + status ball (the preserved `CollapseCard`/`Ball` pattern, `DES-3-05`/`DES-8-01`) plus a `MicroIndicadores` row. A new alert lands on the tile in the same latency class as the toast (`CON-0053`). Carlos gets "~10 seconds of glance" (journey MOT-04) — the tile must read severity pre-attentively via shape+color+icon, not text.
3. **Mobile push to RRT (Dr. Rafael, US-08/US-27).** `critical` pages the RRT physician's corporate smartphone in **<5s** (`CON-0092`). The push is one tap to the **en-route patient screen** (US-27): location, latest vitals each with its own staleness timestamp, current scores + trend direction, and the triggering alert's *why* panel (§4). Delivered on the responsive web app (native app is WON'T, product-spec §4). Delivery is at-least-once with ARQ retry+backoff (`INV-6`/`CON-0071`) and client-side dedup on `dedup_key` for effectively-once UX (`CON-0045`).

### 1.2 Escalation routing

On **ack-SLA breach** (raised → not acknowledged within crit 2 min / urg 10 min / watch 60 min) the alert auto-**escalates**: it pages the next tier (RRT) and visibly changes state on the board and chip (`alert-engine §9`, transition `raised → escalated`). On **action-SLA breach** (acknowledged but not resolved within the band's action window `CON-0062..64`) it escalates again. Escalation is a system+timer transition, always audited (`INV-1`).

---

## 2. Alert lifecycle UI — raise → acknowledge → act → resolve

The screen renders the state machine from `alert-engine.md §9` / `severity-model.yaml lifecycle`. States: `raised → acknowledged → acting → resolved`, plus `escalated` and `expired`. **Every transition writes one immutable `audit_trail` row** (`INV-1`/`CON-0066`; LGPD + CFM 1.821/07). The three human actions each have a dedicated affordance sized to their SLA.

### 2.1 RAISE (system)

- The engine fires; suppression passes (§5 of alert-engine); a row is persisted stamped with the exact `definition_version_id` (`INV-3`, so the alert is reproducible for 7 years) and the triggering parameter payload (§4).
- The alert appears simultaneously on chip + board + (if urgent/critical) mobile, over the one channel.
- **Suppression is visible, never silent:** a duplicate inside cooldown increments a recurrence counter on the existing alert (`dedup`, alert-engine §5.1) shown as a "×N" badge; a coalesced low-tier alert appears inside a digest, not dropped. A `critical` alert is **never** suppressed or rate-limited (patient-safety carve-out).

### 2.2 ACKNOWLEDGE — one-tap, audited (`CON-0091`/`PER-C-05`, US-05)

- A single primary control **Reconhecer** on the alert surface (chip toast, board tile drawer, or mobile push). One tap moves `raised → acknowledged` and writes the audit row (`acknowledged_by`, `acknowledged_at`) — no confirm dialog, no form (`PER-ANA-03`: median click-path length = 1, product-spec PER-ANA-03).
- Acknowledged **≠** ignored (journey MOT-08): acknowledging stops the ack-SLA escalation timer and marks the alert as *seen*, feeding time-to-recognition (`acknowledged_at − created_at`, `DM-T-04`) but **not** the ignored/fatigue count.
- For `critical`, ack is **mandatory** and its absence within 2 min drives escalation (§1.2). The audible/interruptive state clears on ack.

### 2.3 ACT — structured one-click outcome documentation (Enf. Ana **US-12**)

- From the acknowledged alert, a **predefined action set** is loggable in a single interaction (`US-12 AC1`): the record captures user, timestamp, and the chosen action into the append-only audit trail (`IMP-C-01`). This moves `acknowledged → acting` (modeled as `acknowledged + intervention_started_at`, severity-model reconciliation note).
- The action set is **per-domain and per-alert**, sourced from the alert definition and the journey flows — e.g. for a sepsis bundle alert (SEP-002/US-13): *coleta de lactato, hemocultura, antibiótico, cristaloide 30 mL/kg, vasopressor* (journey MOT-11, CAT-SEP-002 evidence); antibiotic-time capture directly feeds the time-to-antibiotic outcome (VIS-6.1-02). Actions are **advisory documentation, never auto-ordered** (`VIS-C-01`/US-11 AC2) — the clinician remains responsible (`VIS-C-08`).
- Logged actions feed time-to-action measurement (`resolved_at − created_at`, target p50 ≤ 15 min, `VIS-7.1-03`).
- **US-12 is COULD/Fase 3** in the MoSCoW set (product-spec §2.3); the one-click *disposition* path (§2.4, US-22) ships Fase 2a and is the minimum instrumentation.

### 2.4 RESOLVE — true/false-positive feedback feeding PPV (US-22/US-23)

- Resolve moves `acting → resolved` (or `acknowledged → resolved` directly) and **requires a `resolution`** from the data-model enum `{true_positive, false_positive, intervention_done}` (`DM-VOCAB-05`). This is surfaced as the one-click disposition **procede / não procede** (`US-22`): *procede* → `true_positive`/`intervention_done`; *não procede* → `false_positive`.
- Disposition is **one interaction from the alert surface** (`PER-ANA-03`), recording user + timestamp + disposition in the append-only audit trail (`US-22 AC1`/`IMP-C-01`). An optional reason tag is one more *never-required* tap (journey MOT-09).
- **A "não procede" NEVER silently disables an alert type** (`US-22 AC3`/journey MOT-09) — it only feeds analytics (§6) and Fernanda's governance queue (US-25). This is the load-bearing safety rule that keeps clinicians participating without ever muting a live safety signal.
- The `resolution` is exactly what feeds **PPV = TP/(TP+FP)** (target ≥ 60%, `VIS-7.1-02`) and FP/patient-day (< 3, `PER-C-02`) per the `ppv-ledger-draft.yaml` method block. These flow to Gold `fact_alert` (`CON-0028`).

### 2.5 EXPIRE / auto-clear (system)

- If the triggering condition clears before ack, or the alert TTL lapses, the engine routes it to `expired` (stays within the data-model status enum, severity-model reconciliation). An expired-**unacked** alert is what feeds the alarm-fatigue "ignored" count (`VIS-7.1-04`); an expired-after-ack alert does not.

### 2.6 Lifecycle affordance summary

| Action | Control | Clicks | State move | Audited fields | SLA |
|---|---|---|---|---|---|
| Acknowledge | **Reconhecer** | 1 | raised → acknowledged | actor, ts | crit 2m / urg 10m / watch 60m |
| Act | predefined action chip | 1 | acknowledged → acting | actor, ts, action | — |
| Resolve | **procede / não procede** | 1 | acting/ack → resolved | actor, ts, resolution | crit <5m / urg <30m / watch <2h (`CON-0062..64`) |
| (optional) reason tag | tag picker | +1 (never required) | — | reason | — |

---

## 3. RRT desfecho documentation (Dr. Rafael, US-28) — <1 min

For an RRT attendance the *resolve* step is the **desfecho form** (US-28): structured options reflecting the persona flow (*melhorou, transferido para UTI, óbito, permanece em observação*, etc.) plus optional free text, completable in **<1 minuto** (`PER-C-07`/`PER-RAFAEL-03`). The desfecho record **links the alert(s) that dispatched the call** with user + timestamps in the audit trail, closing the time-to-action loop (`VIS-7.1-03`). `form_opened`/`form_saved` events are emitted so the <1 min criterion is continuously measured (`US-28 AC3`).

---

## 4. Every alert shows WHY (Enf. Ana **US-21** — MUST for every domain)

No alert is shippable without a non-empty explanation (`US-21 AC3`: an empty trigger payload is a build/test failure). The *why* panel is reachable in **≤ 2 taps** from any alert surface (`US-21 AC4`) and renders four blocks:

1. **Triggering parameters — values + trends.** Each parameter that fired: name, measured value **with canonical unit**, the threshold crossed, the observation window, and each input's **staleness** (`US-21 AC1`, CONTRACTS alert schema). Values are rendered through the abnormal-value flagging service (`CON-0054`) so an out-of-range number is colored/iconed by *its own* band (`CON-0042`). A mini-trend (sparkline / delta arrow) shows direction — e.g. lactato with its 6h delta (CAT-SEP-002), delta-Na over 24h (CAT-ELY-003), SpO₂/FiO₂ slope (CAT-RESP-003). Units are canonical at the boundary: lactate mmol/L, FiO₂ fraction 0–1 (percent display-only), vasopressor mcg/kg/min with conversion provenance (`CON-SEED-12`/`CON-0060`, US-16 AC5 / US-17 AC4).
2. **Evidence citation.** The guideline/paper backing the rule (e.g. Seymour 2016 JAMA for qSOFA, KDIGO 2012 for AKI, UKKA 2023 for hipercalemia) — displayed, not hidden (`US-13 AC*`). Known **limitations** from the catalog are surfaced as context, not suppressed (`US-13 AC5`: SIRS low specificity, qSOFA false-negatives under β-bloqueadores).
3. **Rule id + version.** The `alert_id` (e.g. `SEP-002`) and the exact `alert_definition_version` / `algorithm_version` that fired (`US-21 AC2`/`IMP-C-03`/`VIS-7.2-05`) — auditable end to end and reproducible for 7 years.
4. **Data-coverage note when partial.** When an alert depends on Média/Baixa-availability data (medication completeness `DATA-AVAIL-06/07`, PPV/SVV `DATA-AVAIL-09`, structured RASS/CAM-ICU `DATA-AVAIL-08`), the panel states the coverage and, where relevant, that a degraded alternate-trigger path was used and labeled (`US-16 AC4`/`US-18 AC5`).

For **correlated insights** (US-20) the why-panel additionally explains the *link*: which constituent alerts, which shared signals, and the time relation — correlation without explanation is not shippable (`US-20 AC3`). Constituent alerts remain individually inspectable inside the grouped insight (`US-20 AC2`).

---

## 5. Alarm-fatigue analytics surface (Dra. Fernanda, US-23)

A coordinator surface that manages alert noise as a quality metric, not an anecdote. All values are computed by the `ppv-ledger-draft.yaml` **method** block from lifecycle feedback; nothing here is hand-authored.

- **Per unit and per alert type** (`US-23 AC1`): **PPV** (confirmed dispositions / total, `VIS-7.1-02`), **taxa de alarm fatigue** (alertas ignorados / total, `VIS-7.1-04`), **alert burden** (alertas/paciente/dia, `VIS-6.2-04`), and **ack-time distribution vs. severity SLAs** (`CAT-C-02..05`).
- **Baselines vs. goals** rendered against actuals (`US-23 AC2`): PPV 35% → ≥ 60%; fatigue 25% → ≤ 10%; time-to-action 42 min → ≤ 15 min (`fleet_targets` in the ledger).
- **Threshold-change effect visible** (`US-23 AC3`): time-series with before/after markers keyed to `threshold_config` version + `alert_definition_version` (from US-25), so a tuning decision's impact is measurable.
- **Governance work queue** (`US-23 AC4`): alert types ranked by **lowest PPV × highest volume**. A type whose 30-day PPV < its `ppv_target` for 2 consecutive windows raises a **per-alert tuning recommendation** carrying measured PPV, volume, ack-time distribution, and a suggested threshold delta that hands off to the US-26 retrospective preview and the US-25 governed change workflow (`admin-config.md`). The recommendation **never disables** an alert — it proposes a tuning for human approval.
- **Reconciles exactly** with the weekly KPI report (US-29 AC3) for the same period, and exports to hospital quality tools respecting LGPD minimization (US-30/`PER-C-08`).

---

## 6. PPV / feedback measurement (how the loop closes)

The disposition/resolution captured in §2.4 and the desfecho in §3 are the sole inputs to fleet PPV. Per `ppv-ledger-draft.yaml`:

- **PPV = true_positive / (true_positive + false_positive)** — only *dispositioned* alerts count; a pending or ignored alert is excluded from the ratio so an un-triaged backlog cannot silently tank PPV.
- **Acknowledged-then-"não procede" is a false positive, not ignored**; only **never-acknowledged-until-expiry** counts as *ignored* (feeds `VIS-7.1-04`). This distinction is the reason the ack (§2.2) and disposition (§2.4) are separate one-click acts.
- All lifecycle timestamps + `resolution` write to `audit_trail` (`INV-1`) and flow to Gold `fact_alert` (`CON-0028`) for corporate analytics and the before-after / stepped-wedge study secondary outcomes (`VIS-6.1-03`).

---

## 7. Constraints this screen owns or discharges

| Constraint / story | Barrier | Where addressed |
|---|---|---|
| `PER-C-05`/`CON-0091` 1-click ack · `US-05`/`US-22` disposition | C2 | §2.2, §2.4 |
| `US-12` structured 1-click action | Fase 3 | §2.3 |
| `PER-C-07`/`CON-0093` RRT desfecho <1min · `US-28` | C2 | §3 |
| `PER-C-04`/`CON-0090` expose trigger · `US-21` why-panel | C3 | §4 |
| `CON-0092`/`PER-C-06` RRT push <5s · `US-08`/`US-27` | C3 | §1, §1.1 |
| `CON-SEED-11` triple-encoded severity · `CON-0041`/`CON-0049` decoupled clinical/brand color | C2 | §0, §1 |
| `CON-0042`/`ADR-C-09` fix (not port) the two severity color bugs | C2 | §0, §4 |
| `CON-0045/0046/0053`/`DES-C-05` one realtime channel, no board polling | C3 | §0, §1.1 |
| `CON-0054`/`DES-C-06` abnormal-value flagging | C3 | §0, §4 |
| `US-22 AC3` "não procede" never disables an alert | Fase 2a | §2.4, §5 |
| `VIS-7.1-02/04`/`PER-C-02` PPV/fatigue/FP-per-day analytics · `US-23` | C3 | §5, §6 |
| `INV-1`/`CON-0066` every transition audited · `INV-3` version stamping | B/C3 | §2, §4, §6 |

**Open reconciliations (→ C2 / data-architect):** add `acting` + `escalated` to the `status` enum (or model `acting` as acknowledged+`intervention_started_at`, `escalated` as a flag); add a delivery-only `info`/`normal` value to `alert.severity` if Tier-4 advisories are to be persisted as first-class PPV-analyzable rows (severity-model reconciliation).

---

## 8. Accessibility gate (required by `accessibility-standard.md §8`)

This is the alert-routing/lifecycle surface, so the AAA critical-value ceiling (`A11Y-REQ-01`) is load-bearing here: the `critical` alert card, the triggering vital in the why-panel (§4), and the mandatory-ack control are all AAA-scoped.

- [x] **A11Y-GATE-01** — Alert card/chip/toast text meets `SC 1.4.3` (4.5:1 / large 3:1); every `critical`-scoped element (critical alert card, the triggering vital in the §4 why-panel, the mandatory-ack control) meets `SC 1.4.6` (7:1) per `A11Y-REQ-01` (`design-tokens.md §6.2`; §1, §4).
- [x] **A11Y-GATE-02** — Severity border/glow/status ball, the why-panel abnormal-value icons, mini-trend chart marks, and focus rings meet `SC 1.4.11` (≥3:1 non-text) in both themes.
- [x] **A11Y-GATE-03** — Severity band, alert **resolution** (`procede`/`não procede` → true/false-positive), and the suppression `×N` state each carry a distinct icon **and** shape/text, never color alone (§0 triple-encoding, §2.1, §4); the two legacy color-only bugs are fixed-not-ported (§0).
- [x] **A11Y-GATE-04** — **N/A** — this screen introduces no new severity hex; it consumes the C2-validated `clinical.*` set (§0, §1); the §2.2 CVD/ΔE method is owned by `design-tokens.md`.
- [x] **A11Y-GATE-05** — No animation exceeds 3 Hz (`A11Y-REQ-13` seizure floor) — a raised `critical` uses a static high-contrast border/icon + a "NOVO" badge, never a >3 Hz pulse; `prefers-reduced-motion: reduce` collapses non-essential motion to instant (`A11Y-REQ-14`).
- [x] **A11Y-GATE-06** — Severity icon+shape pairs stay distinct at the smallest chip / tile status-ball size used, protecting the deuteranopia `watch↔critical` LOW-RISK pair (§2.3 of the standard).
- [x] **A11Y-GATE-07** — Every severity-colored/iconed/announced element (chip, tile border, toast, why-panel criterion) derives from the live severity value — no hardcoded literal — the exact fix for the hardcoded-amber-toast and literal-`'VERMELHO'`-panel bugs (`A11Y-REQ`, §0, §4).
- [x] **A11Y-GATE-08** — The drawer/overlay stack (board-tile drawer, why-panel, RRT desfecho form) — `Escape` closes only the topmost, back matches Esc, `role="dialog"`/`alertdialog` + `aria-modal` + focus trap, stated initial focus + exact restore, depth ≤2 (§0, `accessibility-standard §3`, `A11Y-REQ-07..11`).
- [x] **A11Y-GATE-09** — Live alert regions are named per the §5.1 severity table: `critical` `role="alert"` assertive (never forces focus), `urgent` assertive region, `watch` polite, `normal` off; one container per tier, coalesced ~1/2 s to prevent stomping (`A11Y-REQ-16/17`) — the visual alert paints immediately regardless.
- [x] **A11Y-GATE-10** — Every alert's accessible name follows severity → triggering parameter+value+trend → location (bed/patient) per `A11Y-REQ-18` — e.g. *"Crítico. Lactato 4.2, subindo. Leito 12."* — never *"Alerta. Leito 12."*; this is the §4 why-content read aloud.
- [x] **A11Y-GATE-11** — 24×24 floor platform-wide; the **Reconhecer** 1-click ack and every RRT mobile primary action meet 44×44 (`A11Y-REQ-21`; §1.1, §2.2).
- [x] **A11Y-GATE-12** — No pure `#FFFFFF`/`#000000` large surface (`A11Y-REQ-23`); embossed alert cards/tiles carrying clinical text pass the both-theme contrast check (`CON-0037`) and have a `prefers-contrast: more` flat fallback (`A11Y-REQ-24`).
- [x] **A11Y-GATE-13** — **N/A** — no drag interactions on this screen (ack, disposition, act are all tap/click; state: none).
- [x] **A11Y-GATE-14** — **N/A** — no authentication/e-signature step on this surface (ack/disposition chart via the audited lifecycle, not a PIN); if institutional e-signing is later required on resolve it inherits `A11Y-REQ-25` from the shared signing redesign.
- [x] **A11Y-GATE-15** — Every custom primitive (alert chip, severity ball, `Reconhecer` control, `procede`/`não procede` disposition control, why-panel, digest row) exposes an accessible name/role/state (`SC 4.1.2`) — no bare `<div onClick>`.
- [x] **A11Y-GATE-16** — The structured act (§2.3) and RRT desfecho (§3) forms use the clinical form engine; they pre-populate from the alert payload and do not re-ask a value already captured in the same flow (`SC 3.3.7`).
