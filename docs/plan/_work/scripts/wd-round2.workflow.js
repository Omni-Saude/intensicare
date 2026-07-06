export const meta = {
  name: 'wd-adversarial-round2',
  description: 'Phase D adversarial round: lens attackers + completeness critic, then adjudication',
  phases: [{ title: 'Attack' }, { title: 'Adjudicate' }],
}

const N = 2
const REGRESSION = true

const FINDINGS_SCHEMA = {
  type: 'object', required: ['artifact', 'n_findings'],
  properties: { artifact: { type: 'string' }, n_findings: { type: 'number' }, notes: { type: 'string' } },
}

const COMMON = `Repo: /Users/familia/intensicare (cwd). Round ${N} adversarial review of the IntensiCare v2 build plan (docs/plan/**, deliverable docs + _work machine artifacts). Read docs/plan/_work/schemas/CONTRACTS.md first.
Your findings MUST be concrete and falsifiable. Write docs/plan/_work/redteam/round-${N}/<your-lens>.yaml:
{round: ${N}, lens: <lens>, findings: [{finding_id: RT${N}-<LENS>-NN, severity: critical|major|minor,
  claim: <specific defect>, falsifiable_check: <exact steps/files/values an adjudicator can walk to confirm or refute>,
  owning_doc: <the docs/plan file that must change>, proposed_fix: <concrete>}]}
Cap 10 ranked findings; do NOT pad — an empty list is legitimate. Severity critical = plausible patient harm or a DoD line broken; major = design defect needing fix before ratification; minor = polish.` +
  (REGRESSION ? `\nTHIS IS A REGRESSION ROUND: first read docs/plan/_work/redteam/round-${N - 1}/adjudicated.yaml — re-test every finding marked fixed (verify the fix actually landed in the owning doc and holds); only then hunt residual/new issues in the areas the fixes touched.` : '')

const LENSES = [
  { lens: 'patient-safety', model: 'fable', p: `${COMMON}
Lens: PATIENT-SAFETY failure modes. Attack the clinical designs as an intensivist adversary: walk alert trigger logic + test vectors against edge cases (boundary values, missing inputs, stale data, unit edge cases); hunt suppression paths that could mask a real deterioration (dedup keys too broad, cooldowns spanning re-deterioration, budget suppression leakage into urgent/critical); correlation logic that could delay member alerts; lifecycle dead-ends (alert stuck acknowledged, escalation loops); hazard-log mitigations without an owning spec section (read docs/plan/_work/safety/hazard-log.yaml and spot-check 10 mitigations' spec_refs); the 12 P0 legacy defects — is each verifiably designed OUT (not re-imported) in the new specs?` },
  { lens: 'alarm-fatigue', model: 'opus', p: `${COMMON}
Lens: ALARM-FATIGUE blowout. Stress the PPV/volume accounting: per-alert est_volume realism against ICU epidemiology (sepsis screen firing rates, electrolyte panel frequencies); double-counting across overlapping alerts (same physiology firing 3 domains simultaneously — is cross-domain dedup specified anywhere?); the correlation engine's net-suppression claims; per-severity delivery load on ONE nurse's shift (severity-model tiers × volumes); the coordinator tuning loop — can a noisy alert actually be fixed within governance guardrails; PER-CARLOS-02 (<3 FP/patient-day) arithmetic under worst-case (initial deployment, untuned thresholds ×3 volume).` },
  { lens: 'latency-feasibility', model: 'opus', p: `${COMMON}
Lens: LATENCY/ARCHITECTURE feasibility. Attack the p95 budget: Athena poll cadence vs micro-batch domains' claimed latencies (cold query planning, Gold partition lag, concurrent poll load at 90 beds×multi-hospital); the 9s owned pipeline under alert-storm (>500/min vision target) — queue depths, DB write amplification on hypertables, WebSocket fan-out; dead-man switch blind spots (who watches the watcher); Alternative-B trigger criteria measurable in practice?; NRT path's MLLP dependency vs ADR-001 no-own-ingestion (is the operational vitals feed properly reconciled with the platform constraint — read system-architecture.md's story vs alert-engine.md).` },
  { lens: 'platform-adoption', model: 'opus', p: `${COMMON}
Lens: three sub-lenses, cap 4 findings each. (a) LGPD/security breach paths: PHI in alert payloads over push channels, threshold-config audit gaps, role model deny-by-default holes, pgcrypto column coverage vs PHI inventory, the shared-PIN countermeasure completeness. (b) AMH-dependency fragility: Gold schema breaking-change handling, MPI unavailability, FHIR enrichment outage degradation, freshness SLO breach behavior (does every consumer degrade visibly per the staleness spec?). (c) Clinical-workflow rejection: walk each persona's shift through the specs — where would Enf. Ana or Dr. Carlos abandon the tool (extra clicks vs promised 1-click, monitor-wall legibility at 4m, RRT push actionability), PT-BR vocabulary fidelity in forms.` },
]

const CRITIC = `Repo: /Users/familia/intensicare (cwd). You are the completeness critic, round ${N}.
1. RUN the mechanical suite via Bash and record outcomes: python3 docs/plan/_work/scripts/gate_dod.py --phase D (it runs env/dispositions/escalations/alert-catalog/units/links/coverage/matrix — matrix may legitimately be missing pre-Phase-E; note it).
2. Semantic completeness hunt: any vision §3 table row without a corresponding alert or explicit exclusion rationale; any MoSCoW MUST story without a spec anchor; any hazard-log mitigation whose spec_ref is null/dangling; any RATIFY disposition whose recommended default is NOT reflected as the design default in its target doc; any screen state without keyboard/focus spec; any invariant REQ row whose Verification cell is untestable prose.
Write docs/plan/_work/redteam/round-${N}/completeness.yaml: {round: ${N}, lens: completeness, gate_summary: <one line per gate>, findings: [same schema, ids RT${N}-COMP-NN]}.
Return {artifact, n_findings, notes}.`

phase('Attack')
const results = await parallel([
  ...LENSES.map(l => () => agent(l.p, { label: `rt${N}:${l.lens}`, phase: 'Attack', model: l.model, effort: 'high', schema: FINDINGS_SCHEMA })),
  () => agent(CRITIC, { label: `rt${N}:completeness`, phase: 'Attack', model: 'sonnet', effort: 'high', schema: FINDINGS_SCHEMA }),
])

phase('Adjudicate')
const adj = await agent(`Repo: /Users/familia/intensicare (cwd). You are the round-${N} adjudicator. Read every findings file in docs/plan/_work/redteam/round-${N}/ (5 files). For EACH finding: dedupe across lenses (same defect = one canonical finding, note merged ids); then WALK its falsifiable_check yourself against the actual files — do not trust the claim. Verdict: CONFIRMED (check reproduces), PLAUSIBLE (cannot fully reproduce but cannot refute), REJECTED (check fails — say why). Re-grade severity if the walk warrants.
Write docs/plan/_work/redteam/round-${N}/adjudicated.yaml: {round: ${N}, findings: [{finding_id, merged_from: [], lens, severity, verdict, claim, owning_doc, proposed_fix, walk_note: <what you actually observed>}], counts: {confirmed_critical: X, confirmed_major: Y, plausible_critical: Z, rejected: W}}.
Also update docs/plan/_work/redteam/ledger.json: {"rounds": {"${N}": {"confirmed_critical": X, "confirmed_major": Y}}, "consecutive_clean": <computed: this round clean means confirmed_critical==0>, "unresolved_confirmed_critical": <X>} — read the prior ledger if it exists and preserve earlier rounds.
Return {artifact: "docs/plan/_work/redteam/round-${N}/adjudicated.yaml", n_findings: <total after dedupe>, notes: "confirmed_critical=X confirmed_major=Y plausible=Z rejected=W"}.`,
  { label: `rt${N}:adjudicator`, phase: 'Adjudicate', model: 'fable', effort: 'high', schema: FINDINGS_SCHEMA })

return { round: N, attackers: results.filter(Boolean).length, adjudication: adj && adj.notes }