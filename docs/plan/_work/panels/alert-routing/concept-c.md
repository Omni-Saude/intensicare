# Concept C — Budget-Aware Alert Routing

**Panel:** severity-tiered alert routing (dashboard chip → unit board → web push RRT <5s)
**Designer:** C · **Deliberate stance:** *budget-aware-first* — per-patient alert **budgets** and
**smart suppression** are the primary organizing principle; the routing tier an alert reaches
(chip / board / push) is a **function of** severity floor **and** that patient's remaining budget
plus live suppression state. Severity alone never decides destination.

> Divergence note (for the panel): the other stances treat routing as severity-driven with
> suppression bolted on. Concept C inverts that — the **budget ledger is the router**. Severity sets
> a *floor*; the budget/suppression engine decides whether an alert climbs above it, collapses into a
> digest, or is held. This is the aggressive answer to Carlos's **<3 falsos positivos por
> paciente-dia** (PER-CARLOS-02) and to the alarm-fatigue target **25% → ≤10%** (VIS-7.1-04).

---

## 1. Fixed design authority (obeyed, not re-litigated)

- **Dark-first** default theme; light is a live, reload-free token-swap sibling (ADR-0002/0003).
- **Tokens only** for severity — `clinical.*` scale, structurally separate from tenant `brand.*`
  (ADR-C-08, DES-C-01). No raw severity hex in components.
- **Radix** primitives for every interactive overlay (chip popover, digest disclosure, ack menu,
  toast) — focus-trap + Esc/back handled once (ADR-0010 overlay-stack lesson).
- **One realtime channel** — chip, unit board, and RRT push are all fed by the *same* push
  transport and latency class so they can never visibly disagree about one event (ADR-C-13,
  DES-C-05). Budget/suppression state is computed **server-side** and pushed as a thin idempotent
  patch reconciled against the record (ADR-C-12) — the client never re-derives budget.
- **Severity = color + icon + shape**, never color alone; **WCAG 2.2 AA** in both themes (ADR-C-04).

Severity vocabulary is preserved verbatim from the catalog legend (LEGEND-SEV / CAT-C-02..05):
**CRIT** = risco iminente de vida, ação **<5 min** · **URG** = deterioração significativa, **<30 min**
· **WARN** = alteração relevante, **<2h** · **INFO** = tendência/risco, **<6h**. The acknowledged
override state keeps its legacy name **ASSISTIDO** (statusTrilha, DES-2-03).

---

## 2. The budget model (the spine of this concept)

### 2.1 Per-patient alert budget
Each patient carries a **rolling token-bucket budget** of *escalations* (not of alerts — every alert
is still recorded to the prontuário at NGS-2, VIS-C-07; the budget only governs how loudly it is
*routed*). Default allowance is derived directly from the persona SLO: **≤3 escalation tokens /
patient / 24h** for the WARN/INFO/repeat-URG band (PER-CARLOS-02). CRIT is **out of budget** — see
the hard floor in §2.4.

The budget is a **first-class visible object**, rendered as a **budget ring** around each patient
chip and aggregated on the unit board. State bands:

| Ring state | Meaning | Routing effect |
|---|---|---|
| `healthy` (≥2 tokens) | quiet patient | severity floor applies unchanged; may promote +1 tier on trend/correlation |
| `near` (1 token) | approaching noise ceiling | non-CRIT holds at chip tier; board shows amber budget mark |
| `depleted` (0 tokens) | budget spent this window | new WARN/INFO **collapse into a digest**, not pushed, still logged |
| `bypassed` | a CRIT or novel-critical fired | ring dims to neutral, CRIT routes at full floor regardless of tokens |

### 2.2 Smart suppression (what spends — or saves — a token)
Suppression runs *before* the router and reshapes the stream (all mechanisms sourced from the alert
schema `suppression:` block):

1. **Dedup + cooldown** — identical `dedup_key` (`patient_id+alert_id`) inside `cooldown` (e.g. PT6H
   for sepsis screen) does **not** spend a token; it increments a repeat-count on the existing chip.
2. **Rate-limit** — per-alert `rate_limit` (e.g. `4/24h/patient`) caps re-fires independent of budget.
3. **Severity supersession** — a higher-severity alert in the same domain **absorbs** the lower one
   (AKI-003 CRIT supersedes AKI-001 WARN, CAT-AKI-003 vs CAT-AKI-001); the two collapse into one
   chip, refunding the lower alert's token.
4. **Correlation collapse** — the three vision correlations (Sepse+AKI, Respiratória+Hemodinâmica,
   Drogas+Eletrólitos; VIS-4-03) merge co-firing alerts into **one correlated alert** carrying the
   higher severity — one token, one destination, instead of two.
5. **Ack-driven quieting** — once ASSISTIDO, further same-key fires route to digest until the
   underlying state *changes class* (e.g. K⁺ crosses from URG-band into CRIT-band, CAT-ELY-001), at
   which point supersession re-promotes it. Acking to silence a *worsening* trend is impossible.
6. **Maintenance-window aware** — `maintenance_window_aware` alerts (lab draw, transport) are held,
   not spent.

### 2.3 The router
`destination = clamp( severity_floor ± budget_modulation )`, evaluated server-side:

- **Floor by severity:** INFO/WARN → **chip**; URG → **board**; CRIT → **push (RRT, <5s)** + board + chip.
- **Budget modulation (±1 tier):**
  - *Promote +1* when budget is `healthy` **and** the alert is on a worsening trend or is a
    correlation-collapsed alert (e.g. a healthy-budget URG sepsis-with-rising-lactato, CAT-SEP-002,
    can promote to push).
  - *Demote −1* when budget is `near`/`depleted` and severity ≤ URG → the alert lands one tier lower
    (URG→chip, WARN→digest). Never silent: it is still on the board's suppression ledger.
- **Hard clamps (§2.4)** bound the modulation so it can never harm.

### 2.4 The hard floor — the safety guarantee of this stance
Budget may only ever make the stream **quieter for non-critical, already-seen signals**. Encoded as
non-negotiable clamps:

- **CRIT never demotes.** A CRIT alert (CAT-C-02, <5 min) always reaches RRT push + board + chip
  regardless of token count; budget only *dedups* it, never withholds it.
- **Novel-critical always breaks through.** The *first* fire of any CRIT-band alert on a patient
  ignores budget and cooldown entirely.
- **Class-crossing re-promotes.** Any suppressed alert whose value crosses into a higher severity
  band is instantly re-promoted (e.g. hipercalemia WARN→CRIT, CAT-ELY-001; delta-Na⁺ safety alert
  ELY-003c, CAT-C-01).
- **Nothing is silent.** Every held/collapsed alert is written to the prontuário (VIS-C-07) and is
  one click away in the digest, with an auditable reason code (`deduped`, `superseded`,
  `budget-held`, `correlated`) — versioning 100% auditable (VIS-C-13).

---

## 3. Layout & the three routing tiers

### Tier 1 — Dashboard chip (ambient, per bed)
On each bed card sits a **patient alert chip**: severity `icon + shape + color` token, the **single
triggering parameter** in tabular-figures mono (e.g. `FR 24 rpm`, `K⁺ 6,7`), a **repeat-count**
badge, and the **budget ring** framing it. Neumorphic elevation-token pair marks it as a live
surface (ADR-0007). Radix `HoverCard`/`Popover` expands it to a **24h sparkline** (PER-CARLOS-03),
the full trigger logic, the suppression ledger for that patient, and a **1-click Ack** (PER-ANA-03).
INFO/WARN live and die here unless budget/trend promotes them.

### Tier 2 — Unit board (aggregate, coordinator + charge nurse)
A dense bed grid (shared unit-tested column-span function — no legacy dead-band, ADR-C-07) where
each bed shows its top chip. A left **acuity + noise rail** stacks, per bed, the severity of the top
active alert **and** the budget ring — so a bed that is *loud but low-yield* (depleted budget, many
holds) reads differently from a bed that is *critically escalating*. A unit-level header strip shows
live **KPIs**: mean **tempo até ação** per tier (VIS-7.1-03, goal ≤15 min), **alarm-fatigue rate**
(held ÷ fired, VIS-7.1-04), and **PPV** proxy (acked-actioned ÷ pushed, VIS-7.1-02). URG alerts
highlight the bed here; a bed's ring turning `depleted` is the coordinator's leading indicator of
noise. Exportable to hospital quality tools (PER-C-08).

### Tier 3 — Web push to RRT (<5s, mobile)
Only alerts the router sends to **push** reach Rafael's smartphone — by construction these are CRIT
(or budget-promoted URG on a worsening trend), i.e. the **high-PPV top of the stream**. The push
card carries **score + trend arrow + patient location + latest vitals** (PER-RAFAEL-01/02) and a
deep link that, on the same realtime channel, opens the patient with **outcome documentation in
<1 min** (PER-RAFAEL-03). Because push volume is budget-capped, the channel stays trustworthy —
Rafael is never trained to ignore it.

---

## 4. Interactions & states

- **Chip states:** `idle`/NEUTRO → `active` (severity icon+shape+color) → `acknowledged`/ASSISTIDO
  (blue override, statusTrilha ASSISTIDO always wins, DES-2-03) → `suppressed-digest` (collapsed
  `+N` count) → `stale` (data-staleness hatch when input older than `staleness_max`).
- **Budget ring states:** `healthy` / `near` / `depleted` / `bypassed` (§2.1), each with a **text
  label** (`2 restantes` / `limite atingido`), never color-only.
- **Ack (1 click):** marks ASSISTIDO, logs responder + timestamp (feeds the tempo-até-ação KPI),
  and quiets repeats — but cannot mask a class-crossing worsening (§2.4).
- **Digest disclosure:** Radix `Collapsible` on the chip lists everything held for this patient with
  reason codes; opening it is the audit trail, satisfying "nothing silent".
- **Budget tuning:** Carlos can tighten a chronic patient's budget (e.g. known CKD on AKI-005
  nefrotoxicidade, CAT-AKI-005) to cut expected noise, or loosen a fresh post-op — a per-patient
  override, never required, defaulted from severity.

---

## 5. How each persona succeeds

**Dr. Carlos (intensivista).** The budget ring *is* his **<3 FP/paciente-dia** guardrail made
visible and enforced (PER-CARLOS-02). Noise from repeat/low-yield alerts is collapsed before it
reaches him; CRIT still always breaks through (§2.4) so specificity rises without losing
sensitivity. Chip → 24h sparkline gives his trend view (PER-CARLOS-03); the suppression ledger lets
him *see why* something was quieted (trust through transparency).

**Enf. Ana (enfermeira).** Every chip names the **exact triggering parameter** (PER-ANA-02) and
**Ack is one click** (PER-ANA-03, PER-C-05). She never hand-calculates a score (PER-ANA-01). The
budget ring explains *why the board is calm* for a stable patient, so silence reads as "handled",
not "broken".

**Dra. Fernanda (coordenadora).** The unit board's acuity+noise rail and live KPI strip give her a
real-time occupancy/acuity view (PER-FERNANDA-01) plus **tempo médio de resposta** and
**alarm-fatigue rate** as first-class, **exportable** quality indicators (PER-FERNANDA-02/03,
PER-C-08). Unit-wide budget depletion is her earliest signal that a protocol is mis-tuned.

**Dr. Rafael (RRT).** Push is budget-gated to the high-PPV top of the stream, so his **<5s** mobile
alert (PER-RAFAEL-01) is one he can trust and act on — carrying score, trend, location, and latest
vitals (PER-RAFAEL-02), with **outcome documentation <1 min** (PER-RAFAEL-03). One realtime channel
guarantees his push and the board agree (ADR-C-13).

---

## 6. Risks (with mitigations)

1. **[TOP, patient-safety] Budget suppresses a real deterioration.** *Mitigation:* the §2.4 hard
   floor — CRIT never demotes, novel-critical always breaks through, class-crossing re-promotes,
   budget touches only WARN/INFO/repeat-URG. This clamp is the load-bearing invariant; it must be
   ratified with clinical sign-off (ties to ADR-0014 severity-band ratification).
2. **Mis-tuned per-patient budgets.** *Mitigation:* tuning is optional; defaults come from severity;
   overrides are logged and auditable (VIS-C-13).
3. **Silent suppression → clinician distrust / regulatory gap.** *Mitigation:* nothing is silent —
   every hold is logged to the prontuário (VIS-C-07), shown in the digest with a reason code, and
   auditable.
4. **Cognitive load of a budget meter at the bedside (Ana).** *Mitigation:* the ring is ambient and
   labeled; nurses act on the chip, not the ledger — the budget is *explanatory*, never a task.
5. **Gaming — acking to silence.** *Mitigation:* ack quiets only same-class repeats; a worsening
   class-crossing re-fires and re-promotes regardless of ASSISTIDO.
6. **Budget state divergence across surfaces.** *Mitigation:* budget computed once server-side,
   pushed on the single channel as a thin patch (ADR-C-12/13) — no client re-derivation.

---

## 7. Alarm-fatigue impact & a11y

**Alarm-fatigue impact:** directly attacks VIS-7.1-04 (25%→≤10%) and PER-CARLOS-02 (<3 FP/patient-day)
by capping *escalation volume per patient* at the source — dedup, supersession, correlation-collapse,
and budget demotion shrink the pushed stream while the hard floor preserves sensitivity, so PPV
(VIS-7.1-02, →≥60%) rises rather than falls.

**A11y note:** severity is encoded redundantly as **color + icon + shape** and the budget ring
carries a **text label** (never color-only), meeting **WCAG 2.2 AA** contrast in both dark and light
themes over neumorphic surfaces (ADR-C-04); push and digest entries are fully text-labeled.
