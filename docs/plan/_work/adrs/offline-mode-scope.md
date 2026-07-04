# ADR-DRAFT: Offline / degraded-mode scope

Status: **draft, pending ratification**
Date: 2026-07-04
Author: frontend-architect (v2 design phase)

## Context and Problem Statement

The legacy codebase includes an offline-sync mechanism used by the `trilha_homecare` pathway
(`docs/plan/_work/briefs/clusters/operacional-infra.json`, `CLU-OPERACIONAL-INFRA-07`): a scheduled
sync process that queues writes made while offline and later reconciles them against the server. The
audit found this mechanism was single-tenant-hardcoded — `RULE-OPERACIONAL-INFRA-021` unconditionally
sets `request.empresa = Empresa.objects.get(whitelabel='homecare')` regardless of the actual
requesting tenant — and separately documented a timestamp-labeling corruption defect in the same sync
path (`operacional-infra.json` §time-window-bugs). It was never generalized beyond the homecare
bed-type, and the audit's own summary flags it explicitly as "requires v2 redesign," not
"port as-is."

IntensiCare v2 is a clinical decision-support platform classified as SaMD Class II
(`VIS-C-01`/`VIS-C-02`) whose alerts and scores are explicitly advisory, not autonomous
(`VIS-C-01`: "Alertas inteligentes que não realizam diagnóstico automático nem substituem julgamento
clínico"). The frontend must decide what happens when a client loses connectivity to the API and/or
the realtime channel (§ADR `realtime-channel-consolidation.md`): does it queue writes for later
replay (as the legacy homecare path did), or does it degrade to read-only?

## Decision Drivers

- Patient-safety risk of write-conflict/staleness: a clinical action (alert disposition, vitals entry,
  RRT outcome) recorded against a local, possibly-stale view of patient state while offline can
  conflict with actions taken by other staff in the interim, or be applied against data that has since
  changed materially (e.g., the patient was discharged, transferred, or a newer, contradicting alert
  fired).
- `VIS-C-08`: "O médico continua sendo responsável pela decisão clínica final" (the physician remains
  responsible for the final clinical decision) — a queued, delayed write applied without the
  clinician re-confirming current patient state at time-of-application weakens that responsibility
  chain.
- `CON-0047`/`ADR-C-14`: the backend independently enforces authorization on every request; an offline
  write queue that replays later must still pass that enforcement at replay time, against
  potentially-changed state — a nontrivial conflict-resolution problem the legacy attempt did not
  solve well (per the documented defects above).
- The legacy offline mechanism was scoped to exactly one tenant/bed-type by hardcoding, was not
  audited for correctness beyond that scope, and carries at least one confirmed data-corruption
  defect (timestamp labeling) — there is no working reference implementation to generalize from.
- `PER-C-05`/`PER-C-07`: alert acknowledgment and outcome documentation have tight interaction-latency
  budgets (1 click, <1 minute) that assume an online, responsive backend; designing a queued-write
  UX that still meets those budgets while being honest about "this hasn't actually saved yet" is
  substantial, unbudgeted UX/engineering work.
- Users do need *some* continuity when connectivity drops mid-shift — a clinician mid-round should not
  lose access to already-loaded patient data just because a hospital Wi-Fi AP handed off badly.

## Considered Options

1. **Full offline support with a write queue and conflict resolution**, generalizing/rebuilding the
   legacy homecare mechanism for all tenants and bed types. Rejected: no clean legacy reference to
   build from (single-tenant-hardcoded, has a documented corruption bug); conflict-resolution
   semantics for clinical writes against a mission-critical, life-safety system are a large,
   unscoped design problem; increases the surface area for a v2 SaMD Class II submission without a
   clear clinical-safety case for the benefit.
2. **No degraded mode at all — hard-fail to an error/offline screen** when connectivity drops.
   Rejected: too brittle for real ICU network conditions (Wi-Fi handoffs, brief backend restarts);
   a clinician mid-round loses access to data they already legitimately fetched, for no safety
   benefit.
3. **Read-only degraded mode with explicit staleness banners; no offline writes.** Chosen. Already-
   fetched data (via the TanStack Query cache and service-worker cache, `component-library.md` §10)
   remains visible when connectivity is lost, clearly marked with `StalenessBanner`
   (`component-library.md` §5.7) and a `ConnectionStatusIndicator` (§5.13) state. All mutating actions
   (acknowledge alert, submit a form, log an RRT outcome) are disabled or explicitly blocked with a
   "reconnecting to save" state — never silently queued.

## Decision Outcome

Adopt **Option 3**. IntensiCare v2 supports a **read-only degraded mode**:

- On realtime-channel or API disconnection, previously-fetched data remains visible, annotated with
  its age via `StalenessBanner`.
- No write action (alert disposition, form submission, RRT outcome documentation, threshold change)
  is queued locally for later replay. Mutating UI is disabled during a confirmed disconnection, with
  a visible reason ("Sem conexão — reconectando…") rather than a silently-accepted, silently-queued
  action.
- The legacy `trilha_homecare` offline-sync mechanism is **retired**: it is not ported, not
  generalized to other tenants, and not used as a starting implementation for v2's degraded-mode
  read path. Its documented defects (single-tenant hardcoding, timestamp corruption,
  `RULE-OPERACIONAL-INFRA-021/022`) are dispositioned as `NOT_APPLICABLE` for v2 per the cluster
  brief, consistent with this ADR.
- Reconnection triggers an automatic refetch of any view the user is currently looking at (never a
  blind resume-from-cache) before re-enabling mutating controls, so a clinician's next action is
  always taken against confirmed-current server state.

### Consequences

**Good:**
- Eliminates an entire class of clinical-safety risk (stale/conflicting offline writes) rather than
  attempting to engineer around it.
- Matches the SaMD Class II advisory-only posture (`VIS-C-01`) and preserves the unambiguous
  physician-responsibility chain (`VIS-C-08`) — no action is ever "applied later" without the
  clinician's contemporaneous confirmation.
- Reuses infrastructure already required elsewhere (TanStack Query cache, service worker for PWA
  precache, `StalenessBanner`/`ConnectionStatusIndicator` from the realtime-consolidation work) —
  no new offline-sync subsystem to build, test, or carry as SaMD-submission surface area.
- Removes a documented legacy defect class (single-tenant hardcoding, timestamp corruption) from v2's
  scope entirely rather than inheriting it.

**Bad:**
- Clinicians on genuinely unreliable networks lose the ability to record actions in the moment during
  an outage; they must wait for reconnection or fall back to a non-digital process (paper, verbal
  handoff) for the duration — an operational cost, not a technical one, that should be communicated
  in staff training/rollout materials.
- No continuity path exists for the RRT mobile flow (§10 of `component-library.md`) if a responder
  loses connectivity mid-attendance beyond the already-loaded patient screen remaining readable; the
  outcome-documentation step (`US-28`) cannot be completed until connectivity returns.
- This decision forecloses a "queue and sync" UX some clinical stakeholders may expect from consumer
  mobile-app conventions; it must be explained clearly during clinical/UX validation, not assumed
  self-evident.

## Open questions for ratification

1. Whether a narrow, explicitly-scoped exception should exist for RRT outcome documentation only
   (e.g., a short client-side grace buffer of a few seconds during a network blip, not a durable
   offline queue) — flagged for clinical/UX validation, not decided here.
2. Staleness-threshold values (how old is "stale enough to bar action on" vs. "stale but still
   informative") per data class (vitals vs. alerts vs. occupancy) — a clinical-content decision, not
   an architecture one.
3. Whether this ADR needs explicit sign-off from the regulatory/LGPD track given its interaction with
   `VIS-C-01`/`VIS-C-02`/`VIS-C-08` — recommended before this draft is finalized to "accepted".
