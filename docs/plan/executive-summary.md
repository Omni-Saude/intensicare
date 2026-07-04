# IntensiCare v2 Build Plan — Executive Summary

**What this is.** The complete, implementable design for IntensiCare v2 — an AI-agent-era rebuild of
the clinical decision-support platform for Brazilian ICUs — as a consumer of the AMH Data Platform
(ADR-001: Athena/Gold reads, MPI identity, no own FHIR server, Gold write-back). Documents only; the
build executes from [delivery/build-orchestrator-blueprint.md](delivery/build-orchestrator-blueprint.md)
via [delivery/build-kickoff-prompt.md](delivery/build-kickoff-prompt.md).

**What was decided, by the numbers.**

| Corpus | Disposition |
|---|---|
| 959 legacy rules (27 clusters) | ADOPT 194 · ADOPT-CORRECTED 57 · ADAPT 209 · SUPERSEDE 66 · RETIRE 229 · **RATIFY 204** — 100 % coverage, zero silent drops (script-verified) |
| 351 escalation items | 12 P0 + 45 P1 committee-grade drafts · 45 UNVERIFIABLE owner groups · 56 AMBIGUOUS keep/retire · 3 ADDENDUM e-signature items · P2/P3 resolved by dispositions |
| 18 legacy design ADRs | dispositioned into the new design system (dark-first, governed neumorphic elevation, one realtime channel, schema-driven form engine) |
| 5 audit ratification asks | all answered or escalated in [RATIFICATION.md](RATIFICATION.md) |

**The new clinical surface.** 9 domain specs (7 Phase-2 domains + early-warning-scores +
correlation engine) define **50 evidence-anchored alerts with 266 executable test vectors**, every
input typed against a **67-parameter canonical units registry** (lactate mmol/L, FiO₂ fraction,
vasopressors mcg/kg/min with a conversion service — the audit's most dangerous defect class designed
out at build time). Fleet math holds the vision targets: volume-weighted PPV 0.665 (≥ 0.60), 1.37
alerts/patient-day, alarm-fatigue levers honestly attributed. Severity is one canonical scale
(`normal/watch/urgent/critical`, color+icon+shape) with a 9-transition audited lifecycle feeding PPV
analytics; the p95 ingest→alert budget decomposes to 9 s owned pipeline inside the 30 s ceiling.

**Safety posture.** ISO-14971 hazard log (34 hazards, 105 owned mitigations, 93 traced to spec
sections); two adversarial red-team rounds produced 39 CONFIRMED findings — 36 fixed in-plan
(including PHI-free lock-screen pushes, an independent dead-man watchdog path, correlation
break-through so folds can never mask a new critical alert, and build-time criterion-coverage /
band-partition gates), 3 accepted-risk items explicitly listed for ratification. The six
architectural invariants appear as testable `REQ-INV-*` requirements with owners and drills.

**What humans must decide** ([RATIFICATION.md](RATIFICATION.md)): the 12 P0 legacy defects (each
with options + reference-anchored recommended default), the sepsis v1-AND/v3-OR aggregation, the
MEWS/NEWS2 corrections (HANDOFF AUDIT-001/002), canonical-units confirmation, e-signature legal
review, 45 owner-confirmation groups for proprietary rules, and BUILD-ADR-001 below.

**How the build starts.** [BUILD-ADR-001](delivery/build-orchestrator-blueprint.md#1-build-adr-001--v10-mvp-codebase-disposition):
**brownfield-core + greenfield-surfaces** — keep/extend the CI-green v1 FastAPI+TimescaleDB backend
skeleton (24-row module table), replace v1 alert generation with the declarative engine, build AMH
integration, correlation, routing, and the React 19/Next.js frontend greenfield. 40 work orders
(WO-001..040), invariants first, domains in vision §5 order (P1 Sepse → P7 Delirium). A successor
orchestrator pastes [build-kickoff-prompt.md](delivery/build-kickoff-prompt.md) and executes.

**Verification.** Every claim above is mechanically checkable:
`python3 docs/plan/_work/scripts/gate_dod.py --phase E` re-runs the full definition-of-done suite;
per-gate JSON evidence ships in `_work/gates/`.
