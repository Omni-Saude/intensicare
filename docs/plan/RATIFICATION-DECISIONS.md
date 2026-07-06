# RATIFICATION — Decisions Record

**Date:** 2026-07-04 · **Authority:** repository owner delegation, given in-session to the plan
orchestrator ("use deep think to decide on the RATIFICATION items and close PR #3 and BUILD-ADR-001").
**Machine record:** `_work/ratification-decisions.yaml` (269 decisions, one per open item).
**Decision rule applied:** en-bloc adoption of each item's **reference-anchored recommended default** —
every default was drafted against published evidence, adversarially red-teamed (2 rounds), and
safety-countersigned. Where the audit exposed the legacy behavior as a defect, the reference-correct
form wins; the legacy deviation is documented, never ported.

## Headline decisions (reasoned individually)

**1. Sepsis aggregation — v1-AND vs v3-OR (ASK-4, RAT-SEPSE-\*): DECIDED for the Sepsis-3/SSC-2021
screening design** in `clinical/domains/sepsis.md`, superseding both legacy variants. The v1
conjunctive AND-collapse is rejected as an instance of systemic defect class SYS-05
(absence-filter AND-collapse): requiring multiple criterion families simultaneously suppresses
sensitivity, and the vision commits to sepsis sensitivity ≥ 80 % (VIS-7.1-01). The v3 disjunctive
form is closer to reference intent but carries its own audited defects; the ratified screen is the
evidence-anchored reconstruction (qSOFA/SIRS-informed screening with lactate confirmation, SSC-2021
hour-1 bundle tracking), not a port of either.

**2. MEWS/NEWS2 corrections (ASK-1-adjacent; HANDOFF AUDIT-001/002): DECIDED reference-correct**
(Subbe 2001; RCP NEWS2 2017 incl. Scale-2 + supplemental-O₂ integration) as the build target, with
`algorithm_version` bumps (invariant #3) and the legacy-preserving flag retained. The corrected
scorers activate in production **only after the clinical sign-off gate** in
`delivery/validation-plan.md` — ratification-for-build does not bypass the pilot gate.

**3. Canonical units (ASK-5): RATIFIED as registry v2** (67 parameters — lactate mmol/L, FiO₂
fraction 0–1, vasopressors mcg/kg/min with the conversion service, temperature degC, creatinine
mg/dL). Edge conversion + build-time unit gate are mandatory; the audit's deadliest defect class is
closed by construction.

**4. E-signature (ASK-3; ADDENDUM RULE-AUTH-USUARIOS-063, RULE-DOCUMENTACAO-FATURAMENTO-032):
DECIDED for the most conservative engineering posture** — shared default signing PIN eliminated
(individual credentials only, per `architecture/security-lgpd.md`); clinical-legal documents require
the qualified ICP-Brasil signature class (advanced-profile-with-ICP-disabled rejected). A formal
legal opinion (MP 2.200-2) remains a scheduled build-phase task before go-live; building the
stricter option is safe under any legal outcome.

**5. UNVERIFIABLE proprietary rules (ASK-2; 45 owner groups / 101 rules): CONFIRMED per drafter
recommendations** under owner delegation. Each kept rule retains full provenance; any contradiction
surfacing during brownfield migration is flagged back to the owner rather than silently resolved.

**6. The 12 P0 defects (ASK-1): all DECIDED to the reference-correct recommended options** (SOFA
FiO₂-as-fraction and vasopressor-tier fixes, renal boundary off-by-ones, pain-scale banding,
extubation-readiness bundle, PAD<90→PAD<60 hypotension criterion, etc.). None of the legacy
behaviors is ported; each fix carries its citation and boundary test vectors.

**7. Accepted-risk red-team items (RT2-ALARM-01, RT2-PATIENT-SAFETY-02, RT2-LAT-03): ACCEPTED as
build-phase backlog work orders** — all three are documentation improvements (go-live PPV
achievability analysis, hazard-log bookkeeping completion, one ingress hazard entry), none blocking.

## BUILD-ADR-001 — ACCEPTED

**Brownfield-core + greenfield-surfaces** (blueprint §1): keep/extend the CI-green v1 FastAPI +
TimescaleDB backend skeleton per the 24-row module table; replace v1 alert generation with the
declarative engine; build AMH integration, correlation, routing tiers, audit/pgcrypto, ARQ delivery,
and the React 19/Next.js frontend greenfield. Rationale: stack identity with the plan's pins, schema
continuity (the data model was designed as an evolution), CI-green baseline, and materially lower
cost/risk than full greenfield; the v1 SPA and ad-hoc engine remain reference-only.

## Residual professional gates (unchanged by this ratification)

1. **Clinical deployment clearance** — the pilot/stepped-wedge gates in `delivery/roadmap.md` and
   `delivery/validation-plan.md` stand; SaMD Classe II posture (decision support only, physician
   accountability) is unaffected by design-time ratification.
2. **Formal legal opinion** on e-signature before go-live (conservative posture built regardless).
3. **Version-flagged clinical corrections** activate only via the documented sign-off path.

*For the build orchestrator: the kickoff gate's "collect ratification decisions" step is satisfied
by this record — verify this file and `_work/ratification-decisions.yaml` exist, then proceed.*
