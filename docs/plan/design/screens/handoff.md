# Screen Spec — Shift Handoff (SBAR auto-summary from timeline deltas)

**Owner:** patient-timeline-designer · **Status:** draft for reconciliation barriers **C2** (SBAR content/review UX) and **C3** (shift-window correctness + audit) · **Authority precedence:** ADR-001 ≻ vision ≻ directive ≻ audit (CONTRACTS §5).

This spec defines the **shift-handoff SBAR auto-summary**: a per-patient Situation / Background / Assessment / Recommendation brief **generated deterministically from the patient timeline's events, scores, alerts, and responses over the shift window**. It is the **innovation mandate** of the timeline model — the panel's decision names *"since-last-handoff delta digest + SBAR as a deterministic projection of the stream"* as prime salvage material (`[salvage:B]`, decision.yaml; concept-b §2.4). SBAR here **costs the clinician nothing to author**: it *is* the timeline, re-projected, then reviewed and confirmed.

This screen **invents no clinical content** — every score, delta, alert, threshold, and response is projected from the timeline (`patient-timeline.md`) and the domain docs. It **generates no new number**: an SBAR line is a citation to a timeline event. Every claim cites a source: a ledger/constraint id (`CON-*`, `ADR-*`, `INV-*`), a brief fact (`VIS-*`, `PER-*`, `CAT-*`, `DM-*`), a persona criterion (`PER-C-*`), a user story (`US-*`), a journey moment (`MOT-*`), or a legacy rule id (`RULE-*`).

Companion surfaces: **patient-timeline.md** is the source object (its §5 what-changed digest is what SBAR-A projects); **alert-triage.md** owns the alert lifecycle and — critically — the **RRT desfecho outcome form**, which is a *separate structured write instrument*, not this SBAR (§8, reinforcing patient-timeline must_fix #7).

---

## 0. Design-system frame

- **Dark-first token-driven default** with a symmetric light theme; the print/read view (§6) uses the light token set (`ADR-0002-01`/`ADR-0003`). No pure `#FFF`/`#000` large surface (`A11Y-REQ-23`).
- **Radix `Dialog`** hosts the SBAR preview/review overlay on the managed `OverlayStack` (Esc closes only the topmost, focus-trapped, depth ≤ 2 — `ADR-0010-01`/`A11Y-REQ-07/08`); the print view is a landmark-structured document (§6, §7).
- **ONE realtime channel** (`lib/realtime`, `ADR-0017-01`): SBAR is a **snapshot projection at generation time** with an explicit data-cutoff stamp (§7) — it never silently live-mutates a confirmed section (loud, not silent, MOT-17 failure mode).
- **Severity is `clinical.severity.*`, triple-encoded color + icon + shape + text** off the live value via `lib/severity` (`CON-SEED-11`/`ADR-0013-01`); tabular clinical values use the monospace token (`DES-2-05`).
- **Every generation and every section confirmation writes an immutable `audit_trail` row** (`INV-1`/`CON-0066`; LGPD + CFM 1.821/07). The generator carries an auditable `algorithm_version` so a historical SBAR is reproducible (`VIS-C-13`).
- **Advisory posture** — SBAR is decision support, physician/nurse owns the handoff; it **structures, never replaces**, the verbal exchange (`VIS-C-01`/`VIS-C-08`, MOT-17, product-spec §6 open validation).

---

## 1. What the SBAR is here — a deterministic projection, not a hand-authored form

Because the timeline is already a chronological narrative of change decomposed to the component level (`patient-timeline.md`), the SBAR is a **deterministic query over that same stream** — the strongest argument for the salvaged event-stream reading (`[salvage:B]`). Two consequences:

- **Zero re-transcription** (`US-24`, MOT-17): the nurse does not assemble the summary; the generator drafts all four sections from timeline data, and each SBAR line **deep-links back to its source timeline event** for verification.
- **Reproducible.** Regenerating for the same patient + window + data yields the same draft (deterministic projection) — the property Fernanda's quality lens depends on (`PER-FERNANDA-02`). The generator's `algorithm_version` is stamped on every generated SBAR.

Access: a **`SBAR ▸ handoff`** control on the patient rail (`patient-timeline.md` §1) and a batch **"Passagem de plantão"** entry that generates one SBAR per patient in the nurse's assignment (4–5 patients, `US-24`, MOT-17). Role defaults: Ana → oncoming nurse, Carlos → night physician.

---

## 2. Shift-window semantics — done CORRECTLY (the legacy 07:00 bugs designed out)

The shift boundary is the load-bearing correctness requirement. The legacy fluid-balance module implemented the same 07:00 nursing-day windowing that a handoff needs, and it was **broken in three named ways**. v2 preserves the clinical convention (`RULE-BALANCO-HIDRICO-027`: *"o turno vigente 7:00 as 7:00"* — a real institutional 12 h/shift convention) but **replaces the buggy mechanism** — the canonical CONTRACTS §5 **ADAPT** disposition ("07:00–07:00 shift windows with month-boundary bugs → correct temporal windowing, same clinical semantics").

### 2.1 The correct v2 windowing

- Shifts are **half-open intervals of absolute, timezone-aware instants** in the unit's local timezone, computed with proper calendar/date arithmetic (a date/tz library), **never** day-of-month integer comparisons and **never** lexicographic `"HH:MM"` string compares:
  - **Day shift** `D(d) = [d 07:00, d 19:00)`  · **Night shift** `N(d) = [d 19:00, (d+1) 07:00)`.
  - The **07:00–07:00 nursing day** used for 24 h aggregation = `D(d) ∪ N(d) = [d 07:00, (d+1) 07:00)`.
- An event is assigned to a window by its **clinical timestamp** (`recorded_at` / lab `collected_at`), **never** `ingested_at` (`DM-C-08`/`amh-freshness.yaml`). The half-open `[start, end)` interval guarantees an event lands in **exactly one** window — an event exactly at 07:00 belongs to the *starting* window; an event just before 07:00 belongs to the *previous* window (preserving `RULE-BALANCO-HIDRICO-027`'s clinical intent "pre-07:00 entries belong to the previous day", now via instant comparison, not a string compare).
- The **"since last handoff" anchor** = the window immediately preceding the current one. If none exists (fresh admission mid-shift), an **explicit empty state** renders (*"sem plantão anterior registrado"*) — **never** a `.get()`-style exception.
- **DST safety.** A shift crossing a daylight-saving transition is 11 h or 13 h of wall-clock; the window is defined by its local 07:00/19:00 boundaries resolved to absolute instants by the tz library, so no data shifts window or is double-counted — a class of error the legacy naive arithmetic could not even represent.
- This is a **single, shared, unit-tested temporal-window function** (mirroring the bed-grid density-function pattern, `ADR-C-07`) with **named regression tests** for each legacy defect below — the bugs are named regression fixtures, not "nice to haves".

### 2.2 The `RULE-BALANCO-HIDRICO-006` family bugs explicitly avoided

| Legacy defect (source) | What it broke | v2 fix |
|---|---|---|
| **Month-agnostic `__day` match** — `criado_em__day == (ref−1d).day` matches **day-of-month only** (`RULE-BALANCO-HIDRICO-006` D1) | grossly mis-windows across month boundaries (e.g. Jul 31 → Aug 1) | absolute date arithmetic; no day-of-month compare |
| **Unsatisfiable `hour<7` predicate silently drops 00:00–07:00** — the `hour≥7` branch's `criado_em == horario_ref AND hour < 7` can never be true (`RULE-BALANCO-HIDRICO-006` D2), dropping ~7 h of the night-shift tail of both intake and output | the entire midnight-to-07:00 segment vanishes from the shift total → SBAR-A would omit overnight deltas (the exact MOT-17 "unacknowledged alert dies in the gap between shifts" failure) | the half-open `[19:00, 07:00)` night window **includes** the full midnight tail; that segment belongs to `N(d−1)` which spans midnight and is counted **exactly once**, never dropped |
| **Lexicographic `"HH:MM" < "07:00"` + `.get()` DoesNotExist** (`RULE-BALANCO-HIDRICO-027`) — string compare only valid for zero-padded 24 h strings; previous-day lookup throws if yesterday's record is missing | fragile boundary compare; a missing prior shift **crashes** the handoff | timezone-aware **instant** comparison (not strings); a missing prior window is an explicit empty state (§2.1) |

Result: the SBAR shift window **cannot silently drop the overnight tail, cannot mis-window across a month or DST boundary, and cannot crash on a missing prior shift** — the three ways the legacy 07:00 machinery failed. The clinical semantics (07:00-07:00 nursing day, 12 h shift, "pre-07:00 → previous day") are preserved verbatim; only the mechanism is corrected (ADAPT).

---

## 3. Content model — S / B / A / R auto-drafted from the timeline

Each section is **drafted** (not finalized) from the timeline over the shift window (§2). Every drafted line carries its **source-event deep-link**, its **prior-value + timestamp provenance** (inherited from the timeline delta rule, `patient-timeline.md` §4.3), and a **staleness flag** on any input past its `staleness_max`. Sections that map onto the alert catalog's advisory responses are framed advisory (`VIS-C-08`).

### 3.1 S — Situação (current state)
The always-on state surface, from the now-strip (`patient-timeline.md` §1): current **worst active acuity** glyph (`MAX` severity, `severity-model.yaml` aggregation), the **dominant score(s) + band + trend arrow** (MEWS/NEWS2, with qSOFA/SOFA when relevant), **active unacknowledged alerts**, and LOS + `MicroIndicadores` devices (noradrenalina, VM, sedação, hemodiálise). Answers "where is this patient **now**."

### 3.2 B — Background (the stay in brief)
Admission event + the stay's **pinned milestones**, auto-selected by event severity/kind: intubação / início de ventilação mecânica, início de vasopressor, início de TRS (hemodiálise), mudanças de estágio KDIGO, sepse pathway start. Devices and LOS. This is the compressed backstory an oncoming clinician needs before reading the deltas.

### 3.3 A — Avaliação (the since-last-handoff delta digest — the core)
The projection of `patient-timeline.md` §5, scoped to the shift window (`[salvage:B]`, the since-last-handoff delta digest anchored to shift markers, MOT-17):

- Every **band crossing** and **component-level what-changed delta** since the prior shift marker — *"NEWS2 6→8: SpO₂ 96 %→91 % (+2 pts); demais componentes inalterados"* — decomposed to the parameter, never a bald score delta (`PER-ANA-02`/`PER-C-04`), ranked by contribution to score change (`[salvage:A]`).
- The current dominant score's **decomposition rendered as prose** (concept C: the SBAR is a decomposition rendered as prose) — which component drove the number, with its points and reference band.
- Active **correlations** (the three `VIS-4-03` pairs) with their **member events + evidence citations** and folded member alerts (`patient-timeline.md` §7; correlation-engine §8) — advisory, co-occurrence not causation.
- **Gap events** surfaced as owed documentation (*"Sem gasometria há 6 h", "Sem RASS há 8 h"* — `[salvage:B]`), so absence of expected data crosses the handoff as a first-class item.

### 3.4 R — Recomendação (pending actions + safety flags)
The forward-looking close, projected from open lifecycle state:

- **Pending / unacked alerts** and **overdue reassessments** (e.g. CAM-ICU não registrado > 24 h `CAT-DEL-004`; RASS gap), so a watch-level item does not die between shifts (MOT-17 failure mode).
- **Safety flags** — including the **ΔNa⁺ overcorrection ceiling watch**: when serum sodium is approaching the **8–10 mmol/L / 24 h** correction ceiling (`CAT-C-01`), SBAR-R surfaces it explicitly (safety-officer-b must_fix on the salvaged SBAR, HAZ-032). Other catalog safety ceilings surface the same way.
- The **advisory responses** from the alert catalog (`response.required`, e.g. *"avaliação médica beira-leito"*, sepsis hour-1 bundle items) for still-open alerts — explicitly framed advisory (`VIS-C-08`); SBAR recommends documentation/attention, it does not order.

---

## 4. Nurse review-and-edit flow — 1-click confirm per section, audited

SBAR is **auto-drafted, human-confirmed** — it augments, never replaces, the verbal handoff (MOT-17; product-spec §6 flags SBAR clinical validation as an open question, so confirmation is mandatory before an SBAR structures a real handoff).

- Each of the four sections renders as a **reviewable draft** with a single **`Confirmar`** control (1 click per section, `PER-ANA-03` low-friction budget). The four confirms are **independent** — the nurse can confirm S, then B, then A, then R as she walks the oncoming nurse through each (a natural huddle rhythm, MOT-17).
- **Edit before confirm.** Any section is editable (add nuance, pin an item) before confirming. The generator's draft and the nurse's confirmed content are both captured; the **diff (auto-draft → confirmed)** is part of the audit record, so a later reviewer sees what the clinician changed and why the projection was insufficient (SBAR-projection-drift mitigation, concept-b risk 6).
- **Audited.** Each `Confirmar` writes an immutable `audit_trail` row: `actor`, `confirmed_at`, the **confirmed content snapshot**, the source **shift-window bounds** (§2), and the generator `algorithm_version` (`INV-1`/`CON-0066`; `VIS-C-13`). The **generation event itself** is logged (MOT-17 "handoff generation is logged"), feeding Fernanda's cadence/quality view (`PER-FERNANDA-02`).
- **Confirmation charts at NGS Level 2** where the SBAR becomes part of the prontuário (`VIS-C-07`), consistent with the alert-ack charting model.
- A persistent banner states *"SBAR estrutura, não substitui, a passagem verbal"* — the standard is a structuring aid, not an authority (`VIS-C-08`, MOT-17 failure mode "handoff replacing rather than structuring the verbal exchange").

---

## 5. States

- **Loading / generating** — content-shaped skeleton per section (`SkeletonLoader`, never a blocking spinner, `ADR-0016-01`); the generator runs the deterministic projection.
- **No prior shift (fresh admission mid-shift)** — SBAR-A shows the explicit *"sem plantão anterior registrado; primeira passagem desta internação"* empty state (§2.1), not an empty/broken section.
- **Sparse timeline** — sections render with what exists + explicit gap notes; SBAR never fabricates a milestone or a delta.
- **Stale inputs** — any drafted line built on a past-`staleness_max` input carries the staleness flag inherited from the timeline (§3), so the oncoming clinician sees which SBAR facts are old (data-freshness as a first-class state, MOT-01/MOT-17).
- **New critical event after generation** — a non-modal banner *"novo evento crítico desde a geração — regenerar?"* offers regeneration; a confirmed section is **never** silently rewritten (loud, not silent, `ADR-0017-01`).
- **Error / permission** — classified (validation/permission/server) to visual weight, no blocking-modal default (`A11Y-REQ-19`/`ADR-C-11`); permission-denied re-routes per deny-by-default (`ADR-C-05`); a patient the user cannot see never appears (`ADR-C-14`).

---

## 6. Print / read view

For the bedside/board huddle (MOT-17 "print/read mode for the huddle"):

- A **print/read view** renders the four confirmed (or draft, watermarked *"não confirmado"*) sections at per-patient one-screen density, as a landmark-structured document (§7). Light token set, AA contrast in the print stylesheet (`A11Y-REQ` 1.4.3), no pure white surface.
- **Data-cutoff stamp** — every print/read view carries *"gerado HH:MM · dados até HH:MM · turno [D/N] dd/mm 07:00–19:00"* so an oncoming clinician reading 18:40 data at 19:25 knows the cutoff (the MOT-17 "data cut at generation time without a stamp" failure, designed out).
- **Export** to hospital quality tools (`PER-C-08`/`PER-FERNANDA-03`, `US-30`) with **LGPD minimization** (`VIS-C-05`) and per-export audit logging — the export **pipeline** (schema versioning, minimization, audit) is `analytics-etl-lead`'s deliverable (`CON-0094`); this screen owns only the request/confirmation trigger and the print rendering.

---

## 7. Accessibility gate (binding — accessibility-standard.md §8)

- **A11Y-GATE-01** — Section text ≥ 4.5:1; any `critical`-scoped value carried into SBAR (a critical score, K⁺, lactate) ≥ 7:1 (`A11Y-REQ-01`). Monospace numerals (`DES-2-05`).
- **A11Y-GATE-02** — Severity glyphs, deep-link affordances, focus rings ≥ 3:1 non-text contrast, both themes and the print stylesheet.
- **A11Y-GATE-03** — Acuity/severity in every section is color + icon + text, never color alone (`A11Y-REQ-02`); "não confirmado" is a text/icon watermark, not a hue.
- **A11Y-GATE-05** — No animation > 3 Hz; the generation progress indicator honors `prefers-reduced-motion` (`A11Y-REQ-13/14`).
- **A11Y-GATE-07** — Every severity encoding derives from the live projected value via `lib/severity` — no hardcoded literal (§0).
- **A11Y-GATE-08** — The SBAR review `Dialog` on `OverlayStack`: Esc closes only itself; back matches Esc; `role="dialog"` + `aria-modal` + focus trap; initial focus on the first section's review region, focus restored to the `SBAR ▸ handoff` trigger on close; depth ≤ 2 (`A11Y-REQ-07..11`).
- **A11Y-GATE-09** — Generation-complete and "novo evento crítico desde a geração" announce via `aria-live="polite"` (a non-critical status), coalesced (`A11Y-REQ-16/17`); the SBAR document is a landmark-structured region (four labelled sections + headings), navigable by an AT user as a document (accessibility-standard §5.1).
- **A11Y-GATE-10** — Any alert/score named in SBAR follows severity → parameter+value+trend → location in its accessible name (`A11Y-REQ-18`, `PER-C-04`).
- **A11Y-GATE-11** — The `Confirmar` control and every primary action ≥ 44×44 (`A11Y-REQ-21`); deep-links / secondary controls ≥ 24×24 (`A11Y-REQ-20`).
- **A11Y-GATE-12** — No pure `#FFF`/`#000` large surface; embossed surfaces carrying clinical text pass a stated contrast check + `prefers-contrast: more` flat-shadow fallback (`A11Y-REQ-23/24`).
- **A11Y-GATE-13** — No drag interaction on this screen (state: none).
- **A11Y-GATE-14** — Confirmation charts to the prontuário via the same audited path as the alert ack (no separate PIN/e-signature step is introduced on this screen; if institutional policy later requires a signature, it inherits the accessible-authentication requirement `A11Y-REQ-25` from the shared signing redesign) — N/A as specified here.
- **A11Y-GATE-15** — Each section, `Confirmar` control, and deep-link exposes accessible name/role/state (4.1.2); the document uses semantic regions/headings, not bare `<div>`s.
- **A11Y-GATE-16** — If a nurse edits a section via the clinical form engine, no field re-asks information already captured in the same flow (3.3.7); SBAR content is pre-populated from the timeline, so redundant entry is structurally avoided.

---

## 8. Boundary — SBAR is a read projection, NOT the RRT desfecho  — reinforces patient-timeline must_fix #7

The SBAR is a **read** projection of the timeline for shift handoff. It is **explicitly not** the RRT outcome-documentation instrument. Rafael's `desfecho` (melhorou / transferido para UTI / óbito / permanece em observação) is a **separate structured write flow** — the `OutcomeDocumentationSheet` (`US-28`, owned by `alert-triage.md` §3), measured **form-open → save < 1 min** (`PER-RAFAEL-03`/`PER-C-07`, MOT-16). Mapping the desfecho onto an SBAR dialog would under-serve the < 1-minute structured-outcome instrument (ux-researcher-c must_fix). The two are distinct: SBAR reads the stream; the desfecho writes a structured outcome that then *becomes* a timeline event the next SBAR can project.

---

## 9. Traceability

| Constraint / story / criterion | Where addressed |
|---|---|
| `US-24` handoff summary (zero re-transcription) · MOT-17 19:00 SBAR | §1, §3 |
| `[salvage:B]` SBAR as deterministic projection + since-last-handoff digest | §1, §3.3 |
| **07:00/19:00 shift window correct**; `RULE-BALANCO-HIDRICO-006/027` bugs avoided (ADAPT) | §2 |
| `DM-C-08` window on clinical timestamp, not ingested_at | §2.1 |
| `PER-ANA-03` 1-click (per-section confirm) · `PER-C-05` low-friction | §4 |
| `INV-1`/`CON-0066` every confirm + generation audited · `VIS-C-13` versioned generator | §0, §4 |
| `VIS-C-07` NGS-2 charting on confirm · `VIS-C-08` advisory, structures-not-replaces | §4 |
| `PER-ANA-02`/`PER-C-04` component-level deltas · `[salvage:A]` ranked by contribution | §3.3 |
| `VIS-4-03` correlations (member events + evidence) | §3.3 |
| `CAT-C-01` ΔNa⁺ overcorrection ceiling in SBAR-R (HAZ-032) | §3.4 |
| `PER-FERNANDA-02/03`/`PER-C-08` cadence/quality + export · `VIS-C-05` LGPD minimization | §4, §6 |
| `PER-RAFAEL-03`/`PER-C-07` desfecho is a separate instrument (patient-timeline must_fix #7) | §8 |
| `ADR-0016-01` skeleton not spinner · `ADR-0017-01` loud staleness / no silent rewrite | §5 |

**Innovation-mandate note.** The SBAR-from-timeline-deltas is the timeline model's designated innovation (decision.yaml salvage): a standardized, reproducible, auditable handoff that costs the clinician nothing to author, with the 07:00 nursing-day window finally implemented **correctly** — the single most-cited legacy defect family (`RULE-BALANCO-HIDRICO-*`) designed out rather than ported.
