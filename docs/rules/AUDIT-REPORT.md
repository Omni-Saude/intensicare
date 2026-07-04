# IntensiCare Legacy Rule-Extraction Audit — Final Report

**For:** engineering and clinical leadership ratifying the audit and building the new platform from it.
**Audit dates:** 2026-07-03 (evening) → 2026-07-04 (early morning).
**Method:** static analysis only, over read-only clones of two pinned legacy snapshots. No legacy code was executed and no legacy repository was written to.

| | |
|---|---|
| Audited backend | `Dev-Infra-Grupo-AMH/ahlabs-trilhas` @ `8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f` (master) — 608 files (519 `.py`), Django + DRF |
| Audited frontend | `Dev-Infra-Grupo-AMH/trilhas-frontend` @ `f9656be2660ec2048ce6240b4ac418b7fe7d5a5b` (master) — 681 files, Next.js + TypeScript |

---

## 1. Executive summary

Two legacy IntensiCare ("trilhas") platforms — an automated/manual/homecare ICU care-pathway backend and its clinical frontend — were audited end to end at the two commits above. The audit's deliverable is a rebuild specification: **the new platform should implement from these documents, not from the legacy code.**

What was produced:

- A **959-rule catalog** with full provenance — every rule carries its implementation sites as `repo:path:lines @ commit`, the provisional extraction IDs merged into it, reimplementable pseudocode, edge cases as-implemented, and (where two legacy implementations disagree) an explicit divergence block. Index: [README.md](README.md). Machine-readable source of truth: [extraction/phase2/catalog/](extraction/phase2/catalog/).
- A **351-item escalation queue** ([ESCALATIONS.md](ESCALATIONS.md)), every DISCREPANCY / AMBIGUOUS / UNVERIFIABLE item ranked by clinical risk, including **12 P0 (high-impact) findings**.
- **18 ADRs** ([../adr/README.md](../adr/README.md)) plus a full **design-system inventory** ([../design/design-system-inventory.md](../design/design-system-inventory.md)) from the frontend design audit.

Headline numbers:

- **File coverage:** 1,289 / 1,289 files examined and dispositioned (100%).
- **Extraction status of the 959 rules:** 719 OK · 164 DISCREPANCY · 76 AMBIGUOUS.
- **Verification verdicts:** 73 VERIFIED · 104 DISCREPANCY · 102 UNVERIFIABLE · 680 not-applicable (non-formula).
- **Escalations:** 351 items — P0 12 / P1 45 / P2 35 / P3 99 / UNVERIFIABLE-owner-review 101 / AMBIGUOUS 56 / Phase-6 addendum 3.
- **Adversarial phase:** 0 of 73 VERIFIED verdicts refuted; 54 of 54 fidelity spot-checks faithful; 12 residual gap rules found and remediated.

**Scope boundaries.** Non-rule-bearing artifacts were checked and explicitly excluded: binary assets (fonts, images, GeoIP `.mmdb`), `yarn.lock`, generated Next.js type stubs, and uWSGI/Docker infra config (the latter checked for embedded constants, then excluded). Everything rule-bearing in both application layers is in scope. Detail: [INVENTORY.md](INVENTORY.md#explicitly-out-of-scope-non-rule-bearing).

**Core guarantee — zero silent corrections.** Nothing in this catalog was fixed. Every legacy behavior — including inverted predicates, unit mismatches, off-by-one boundaries, dead branches, and structurally-always-false guards — is preserved verbatim, exactly as the legacy system behaves. The audit's job was to *find and describe* faithfully; the decision to carry a behavior forward or change it is a human clinical/business decision, and each such decision is escalated in [ESCALATIONS.md](ESCALATIONS.md).

---

## 2. Methodology

A six-phase pipeline. Orchestration: **~215 agent runs** consuming **~23M subagent tokens**. Model routing was task-appropriate — **opus** for clinical extraction, reconciliation, verification, and adversarial review; **sonnet** for mechanical API/UI extraction, integration, and document writing.

**Phase 0 — Inventory & partition.** Both repos cloned read-only into an isolated scratchpad. All 1,289 files inventoried (608 backend, 681 frontend) and split into extraction partitions by module/scope. Scope, structure, and the partition map: [INVENTORY.md](INVENTORY.md).

**Phase 1 — Parallel extraction with per-file coverage accounting.** 22 partitions plus a coordination residue partition, extracted in parallel. Ground rule: file names, folder structure, and comments are treated as unreliable — every rule is derived from code *behavior*. Coverage of every file, including explicit "no rules found" verdicts, was recorded per partition. Result: **1,018 provisional rules**, 100% file coverage. Raw findings: [extraction/phase1/](extraction/phase1/) (22 partition YAMLs + `COORD.yaml`).

**Phase 2 — Cluster reconciliation.** The 1,018 provisional rules were reconciled into **27 domain clusters** ([extraction/phase2/catalog/](extraction/phase2/catalog/)): duplicates merged, **35 misrouted rules re-homed** to their correct cluster, and backend/frontend (and v1/v3, facade/model) divergences detected and recorded. Reconciliation itself surfaced *new* divergences not visible in single-file extraction (e.g., 7 in the sepsis cluster alone — facade-text-vs-model threshold disagreements). Every provisional ID was consumed **exactly once** (verified mechanically). Final IDs assigned. Output: **947 rules**.

**Phase 3 — Reference-based verification.** Every formula/threshold rule was verified against an authoritative published reference (SOFA, NEWS2/MEWS, Berlin/ARDS, SSC-2021, KDIGO, ERS/ATS weaning, etc.) with **≥3 hand-traced test vectors per rule**. Verdicts: VERIFIED (faithful to reference), DISCREPANCY (diverges), UNVERIFIABLE (proprietary internal logic, no published reference), or not-applicable (non-formula). Worksheets: [extraction/phase3-verification/](extraction/phase3-verification/).

**Phase 4 — Canonical documentation.** One Markdown document per rule under `docs/rules/<category>/`, plus the catalog index and the ranked escalation report.

**Phase 5 — Design audit.** Three parallel design inventories (tokens; component library & IA; clinical UX) over the pinned frontend commit, consolidated into the [design-system inventory](../design/design-system-inventory.md) and **18 ADRs**.

**Phase 6 — Adversarial phase.** Three independent attacks on the audit's own output: (a) a **coverage re-sweep** (8 sweepers) re-checked both repos against the catalog and found **12 residual gap rules**, all now remediated; (b) **every one of the 73 VERIFIED verdicts was attacked** to refute it — **0 refuted**; (c) **fidelity spot-checks** re-derived 54 catalog entries from source — **0 unfaithful**.

### 2.1 Anatomy of a rule document (what the rebuild team consumes)

Each rule lives at `docs/rules/<category>/<RULE-ID>-<slug>.md` and is written to be reimplementable **without reading legacy code**:

- **Field table** — category, rule type (`formula | threshold | decision-tree | workflow | validation | eligibility | scoring`), extraction status, verification verdict, confidence, owning cluster.
- **Rule / Inputs / Outputs** — plain-language behavior; input and output names, types, units, and valid ranges as implemented.
- **Logic** — exact pseudocode: operator directions, coefficients, boundaries (`>=` vs `>`), order of operations.
- **Edge cases** — boundary/null/rounding/timezone handling as implemented, bugs included.
- **Divergence** — present when two legacy implementations of the same rule disagree (backend vs frontend, facade text vs model predicate, v1 vs v3).
- **Verification** — verdict against the authoritative reference with citation and test-vector trace, or `Not applicable`, or `UNVERIFIABLE`.
- **Provenance** — every implementation site as `repo : path : lines @ commit`, the provisional extraction IDs merged in, and cross-references to related rules.

### 2.2 Clinical-safety ground rules

- **Verbatim preservation.** Legacy behavior is reproduced exactly, defects included. Reimplementation notes say "reproduce VERBATIM including the gaps" where a bug is load-bearing.
- **DISCREPANCY / AMBIGUOUS discipline.** DISCREPANCY = implementations disagree with each other or with a published reference. AMBIGUOUS = intent could not be pinned down from the source; the observed behavior plus the best-supported interpretation is recorded, and the ambiguity is escalated for a human ruling. Neither status is silently resolved.
- **UNVERIFIABLE ≠ wrong.** A rule marked UNVERIFIABLE is proprietary internal logic with no published reference to check against. It is flagged for owner/clinical-committee confirmation of *intent* — it is **not** presumed defective.

---

## 3. Coverage statistics

**File coverage.** 1,289 / 1,289 files dispositioned (608 backend + 681 frontend). Every file received a verdict — including explicit "no rules found" — recorded in Phase 1 and independently re-checked by the Phase 6 coverage sweep.

**Extraction → reconciliation accounting.**

| Stage | Count |
|---|---:|
| Phase 1 provisional extractions | 1,018 |
| → reconciled (dedup + re-home) in Phase 2 | 947 |
| Phase 6 gap rules added | +12 |
| **Final catalog** | **959** |

Every provisional ID was consumed exactly once during reconciliation (verified mechanically); the 12 gap rules are the only post-reconciliation additions, giving 1,030 raw extractions behind the 959 final rules.

**Reconciled clusters (27):** alertas, antimicrobiano, auditoria-logs, auth-usuarios, balanco-hidrico, cadastros-ui, clinical-scoring, comunicacao, documentacao-faturamento, eficiencia, equilibrio, estabilidade, evolucoes, formularios-clinicos, indicadores-etl, movimentacao-adt, nutricao, operacional-infra, piora-clinica, prescricao, profilaxia, sedacao, sepse, sinais-vitais, tenancy-organizacao, trilhas-engine, ventilacao.

**Catalog taxonomy (10 categories, 959 rules).** Clusters are the reconciliation grouping (by legacy domain); the taxonomy below is the cross-cutting clinical/administrative categorization used in [README.md](README.md).

| Category | Rules |
|---|---:|
| data-validation | 314 |
| care-pathway | 211 |
| alert-threshold | 116 |
| scheduling-operational | 66 |
| clinical-scoring | 65 |
| triage-eligibility | 57 |
| physiological-calculation | 47 |
| billing-administrative | 38 |
| drug-dosing | 29 |
| access-control | 16 |
| **Total** | **959** |

---

## 4. Verification statistics

279 rules were verification-eligible (had a checkable formula/threshold); the remaining 680 are non-formula and are marked not-applicable. A verdict is an assessment **against a published clinical reference**, not against intent — a rule that faithfully reproduces the legacy code can still land in any verdict:

- **VERIFIED** — the legacy formula/threshold matches the authoritative reference, confirmed by the hand-traced test vectors.
- **DISCREPANCY** — the legacy implementation diverges from the reference (wrong boundary, wrong unit, inverted predicate, missing band). The divergence is described exactly; the code is *not* corrected.
- **UNVERIFIABLE** — the rule is proprietary internal logic (e.g., an institutional risk band, an access-scoping rule) with no published reference to check against. Recorded verbatim and flagged for owner review of intent — not presumed wrong.
- **Not applicable** — the rule is non-formula (workflow, validation shape, data mapping, UI behavior); correctness is defined by the legacy behavior itself.

| Verdict | Count | % of 279 eligible | % of 959 catalog |
|---|---:|---:|---:|
| VERIFIED | 73 | 26.2% | 7.6% |
| DISCREPANCY | 104 | 37.3% | 10.8% |
| UNVERIFIABLE | 102 | 36.6% | 10.6% |
| Not applicable (non-formula) | 680 | — | 70.9% |
| **Total** | **959** | | **100%** |

Extraction status (independent of verification — measures internal consistency and cross-implementation agreement) across all 959: **719 OK (75.0%) · 164 DISCREPANCY (17.1%) · 76 AMBIGUOUS (7.9%)**.

**Adversarial results (Phase 6).** All 73 VERIFIED verdicts were attacked to break them: **0 refuted**. 54 catalog entries were re-derived from source for fidelity: **0 unfaithful**. The coverage re-sweep found 12 rules missed by earlier phases (all remediated), which is the audit's own measured miss rate for the extraction pass.

---

## 5. Escalation summary

Every rule requiring a human clinical or business decision before reimplementation is in [ESCALATIONS.md](ESCALATIONS.md), ranked by clinical impact. Each item appears in exactly one band (its highest applicable).

| Band | What it contains | Items |
|---|---|---:|
| P0 — High clinical impact | Verified divergences that can mis-score, mis-dose, or mis-triage a patient | 12 |
| P1 — Moderate clinical impact | Verified divergences with a real but bounded clinical effect | 45 |
| P2 — Low clinical impact | Verified divergences with minor clinical effect | 35 |
| P3 — No expected clinical impact | Real deviations (display/admin/dead-code) with no scored patient impact | 99 |
| UNVERIFIABLE — owner review | Proprietary logic with no published reference; confirm intent | 101 |
| AMBIGUOUS extractions | Intent could not be pinned down from the source | 56 |
| Addendum — Phase 6 gap findings | Post-report coverage-sweep escalations | 3 |
| **Total escalated** | | **351** |

Within the impact-scored bands (P0–P3), clinical categories are listed before administrative ones; the category composition is:

| Band | Category composition |
|---|---|
| P0 (12) | clinical-scoring 5 · physiological-calculation 2 · alert-threshold 2 · drug-dosing 1 · care-pathway 1 · triage-eligibility 1 |
| P1 (45) | alert-threshold 16 · clinical-scoring 8 · physiological-calculation 8 · care-pathway 9 · triage-eligibility 3 · drug-dosing 1 |
| P2 (35) | clinical-scoring 8 · triage-eligibility 6 · alert-threshold 6 · physiological-calculation 5 · care-pathway 5 · drug-dosing 3 · scheduling-operational 2 |
| P3 (99) | data-validation 43 · care-pathway 21 · alert-threshold 10 · clinical-scoring 5 · triage-eligibility 6 · scheduling-operational 6 · drug-dosing 3 · billing-administrative 3 · physiological-calculation 1 · access-control 1 |

### The 12 P0 (high clinical impact) findings

Verified divergences — extraction **and** verification agree — that can directly mis-score, mis-dose, or mis-triage a patient. All preserved verbatim in the catalog. Category mix: clinical-scoring 5, physiological-calculation 2, alert-threshold 2, drug-dosing 1, care-pathway 1, triage-eligibility 1.

| Rule | Category | The defect, in one line |
|---|---|---|
| [RULE-CLINICAL-SCORING-002](clinical-scoring/RULE-CLINICAL-SCORING-002-sofa-respiratory-sub-score-pao2-fio2.md) | clinical-scoring | SOFA respiratory: percentage FiO2 makes P/F ~100× too small (over-scores to 4); 3/4-point bands applied without the ventilation gate. |
| [RULE-CLINICAL-SCORING-005](clinical-scoring/RULE-CLINICAL-SCORING-005-sofa-cardiovascular-sub-score-vasopressors-map.md) | clinical-scoring | SOFA cardiovascular: noradrenaline read as raw ml volume (cutoff 10) instead of mcg/kg/min rate; dopamine/epinephrine omitted. |
| [RULE-CLINICAL-SCORING-007](clinical-scoring/RULE-CLINICAL-SCORING-007-sofa-renal-sub-score-creatinine-urine-output.md) | clinical-scoring | SOFA renal: strict `> 5` leaves a dead gap at `(4.9, 5.0]`, so creatinine exactly 5.0 scores 0 (4-point undercount at the top). |
| [RULE-PIORA-CLINICA-006](clinical-scoring/RULE-PIORA-CLINICA-006-piora-clinica-criterio-6-dor-escala-numerica-0-10-graded-sub.md) | clinical-scoring | `if 7 <= dor > 10` never fires: severe numeric pain (NRS 7–10) never triggers a red alert. |
| [RULE-PIORA-CLINICA-007](clinical-scoring/RULE-PIORA-CLINICA-007-piora-clinica-criterio-7-dor-escala-comportamental-3-12-grad.md) | clinical-scoring | Same misparse for behavioral pain (BPS 10–12) — maximal pain in sedated patients never fires a red alert. |
| [RULE-CLINICAL-SCORING-008](physiological-calculation/RULE-CLINICAL-SCORING-008-pao2-fio2-ratio-relacao-po2-fio2.md) | physiological-calculation | P/F ratio: validator stores FiO2 as percentage, all consumers assume fraction — the codebase is internally inconsistent on FiO2 units. |
| [RULE-SEPSE-014](physiological-calculation/RULE-SEPSE-014-sepse-v3-criterio-8-oliguria-without-vasopressor-dialysis.md) | physiological-calculation | Homecare sepsis oliguria: `fromkeys` diagnosis gate always false + weight parse ~10× inflated → criterion can never fire. |
| [RULE-EFICIENCIA-005](alert-threshold/RULE-EFICIENCIA-005-eficiencia-v3-criterio-9-coma-without-sedation-defined-unwir.md) | alert-threshold | Suspected-brain-death: GCS<13 instead of <6 and an AND-collapsed sedative-absence filter; also left unwired. |
| [RULE-PIORA-CLINICA-010](alert-threshold/RULE-PIORA-CLINICA-010-piora-clinica-calculo-do-alerta-soma-agregada-gatilho-por-cr.md) | alert-threshold | Last-writer-wins alert aggregation downgrades a red (VERMELHO) to yellow; magnitude-only sum makes the top band unreachable. |
| [RULE-VENTILACAO-011](care-pathway/RULE-VENTILACAO-011-ventilation-c8-extubation-readiness-bundle.md) | care-pathway | Extubation-readiness reads FiO2 as fraction (`<0.4`) while data is percentage → readiness alert never fires (weaning delayed). |
| [RULE-SEPSE-043](triage-eligibility/RULE-SEPSE-043-sepsis-c6-major-hypotension-pas-90-or-pad-90-in-24h.md) | triage-eligibility | Hypotension major criterion compares PAD `< 90` (rule text says `< 60`) → satisfied by nearly everyone, driving false sepsis alerts. |
| [RULE-ESTABILIDADE-016](drug-dosing/RULE-ESTABILIDADE-016-estabilidade-facade-alert-text-vasopressor-inotrope-escalati.md) | drug-dosing | Vasopressor escalation text in mcg/kg/min while paired predicates trigger on ml/h; a FC>130 criterion the predicate never checks. |

### Most consequential findings

- **Vasopressor unit mismatch between alert text and trigger** — [RULE-ESTABILIDADE-016](drug-dosing/RULE-ESTABILIDADE-016-estabilidade-facade-alert-text-vasopressor-inotrope-escalati.md): the clinician-facing escalation text states noradrenaline doses in **mcg/kg/min** while the paired v3 predicates trigger on infusion volume in **ml/h** (not convertible without concentration/weight), and a "FC > 130 bpm" criterion the predicate never evaluates — the displayed rationale and the firing condition diverge.
- **Sepsis aggregation divergence, v1 vs v3** — [RULE-SEPSE-001](clinical-scoring/RULE-SEPSE-001-sepse-v1-alert-maiores-menores-dual-threshold.md) requires major **AND** minor thresholds; [RULE-SEPSE-002](clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md) uses **OR** (and moves one criterion from minor to major) for the same nominal sepsis screen — materially more patients flagged under v3.
- **Homecare sepsis criteria neutralized by structural bugs** — [RULE-SEPSE-014](physiological-calculation/RULE-SEPSE-014-sepse-v3-criterio-8-oliguria-without-vasopressor-dialysis.md): a `vars(...).fromkeys(...)` diagnosis gate keys on field *names* (always false) and a weight parse strips the decimal separator (~10× inflation), so the oliguria criterion can never fire; the related [RULE-SEPSE-032](clinical-scoring/RULE-SEPSE-032-sepse-criterio-6-oliguria-sonda-ou-dessaturacao.md) uses an intra-day-only `.seconds` recency test that wraps past 24h.
- **Shared default signing PIN** — [RULE-AUTH-USUARIOS-063](access-control/RULE-AUTH-USUARIOS-063-shared-default-signing-pin-usuario-pin-defaults-to-settings.md): `Usuario.pin` defaults to a single deployment-wide `settings.PIN_DEFAULT`, base64-encoded and sent as the CryptoCubo e-signature credential — un-rotated PINs defeat per-user attribution of signed clinical documents. (Companion frontend finding: [RULE-CADASTROS-UI-006](data-validation/RULE-CADASTROS-UI-006-hardcoded-default-signature-pin-for-all-users.md).)

### Cross-cutting systemic issues

The escalations are not independent; a handful of root causes recur across clusters, each fixable (or ratifiable) once as a class (full affected-rule lists in [ESCALATIONS.md](ESCALATIONS.md#cross-cutting-systemic-issues)):

1. **FiO2 percent-vs-fraction inconsistency** — validator stores 21–100 (%) but P/F thresholds assume 0.21–1.0 (fraction); ~100× error on real data.
2. **Vasopressor dose-unit chaos** — ml / ml/h vs mcg/kg/min vs mcg/kg/h across predicates and facade text (incl. a 60× min-vs-hour label drift on the same `>0.5` cutoff).
3. **Lactate units** — mg/dL vs mmol/L (~9× factor) inconsistent across sepsis/shock pathways.
4. **Facade-text vs model-predicate drift** — displayed threshold/unit/criterion-number differs from what the predicate evaluates.
5. **v1-vs-v3 AND/OR aggregation divergence** — OR alternatives implemented as AND `.filter()` (and vice-versa); collapses confounder-exclusion guards.
6. **Chained-comparison misparse** — `if 7 <= dor > 10:` suppresses the most-severe pain/agitation band.
7. **Off-by-one / exclusive-range boundaries** — dead gaps at band edges (e.g., SOFA creatinine `(4.9, 5.0]`), undercounting at the top of the scale.
8. **Dead / unwired / unreachable criterion code** — criteria computed but never wired in, or gated behind structurally-always-false predicates.
9. **Weight decimal-separator parse** — `'70,5'` → `705` kg (~10× inflation) corrupting every weight-normalized threshold.
10. **Month-agnostic day-of-month date filtering** — `criado_em__day` matches day-number regardless of month, plus a timezone boundary defect at month-end, contaminating 07:00–07:00 balance/vitals windows.

---

## 6. Known gaps and limitations

Stated honestly, from the verified audit record:

- **Static analysis only.** The legacy code was never executed; all test vectors were **hand-traced** through the code. Behavior under real production data is inferred, not observed.
- **102 UNVERIFIABLE rules** are proprietary internal logic with no published reference; they require owner / clinical-committee confirmation of intent before reimplementation.
- **Fidelity spot-check sampled 54 / 959 entries** (all passed); extraction breadth was independently checked by the Phase 6 coverage sweep rather than by a full second extraction pass.
- **No legacy regression suite for the automated/homecare engines.** Legacy CI only tests `trilha_manual`; there is no regression coverage for the automated or homecare pathways (the `operacional-infra` cluster / `COORD-001` finding), so those engines' runtime behavior is the least externally corroborated.
- **Portuguese clinical vocabularies preserved verbatim, including source typos** (e.g., the `criterio8` key-typo in the addendum), flagged wherever matching logic depends on the exact string.

**Operational anomalies handled during the run** (none caused data loss or unverified output):

- 42 verification batches were lost to a session rate limit; the workflow **resumed from cache** and re-ran only the failed batches.
- 3 `estabilidade` verify agents and 6 doc writers reported failure at their final-report step, but their **on-disk output was complete and validated** — confirmed on disk, no re-run needed.
- Scratchpad catalogs were **condensed mid-Phase-4** by a concurrent process (verification blocks → pointer form); rule content was verified unaffected, and the rich versions preserved in git were used for the final merge — **no data loss**.
- 421 rule docs were written in a cosmetic template dialect and **normalized mechanically** (two token-level substitutions); content untouched.
- The first gap-remediation agent died on a network failure with zero durable output; the re-run was **redesigned to persist per-gap increments**.

---

## 7. Definition-of-done checklist

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Every file in both repos examined and dispositioned | Met — 1,289 / 1,289, re-checked by the Phase 6 sweep | [INVENTORY.md](INVENTORY.md) · [extraction/phase1/](extraction/phase1/) |
| 2 | Every rule reimplementable from the catalog alone, with full provenance (`repo:path:lines @ commit`) | Met — 959 documented rules; catalog is the source of truth for the rebuild | [README.md](README.md) · [extraction/phase2/catalog/](extraction/phase2/catalog/) |
| 3 | Every formula/threshold rule verified against an authoritative reference with ≥3 hand-traced test vectors, or explicitly UNVERIFIABLE / not-applicable | Met — 279 eligible verdicts (73 V / 104 D / 102 U); ≥3 vectors each | [extraction/phase3-verification/](extraction/phase3-verification/) |
| 4 | Zero silent corrections; every DISCREPANCY / AMBIGUOUS / UNVERIFIABLE escalated and clinically ranked | Met — 351 items ranked; nothing corrected in the catalog | [ESCALATIONS.md](ESCALATIONS.md) |
| 5 | Findings independently re-checked (coverage re-sweep, refutation of every VERIFIED verdict, fidelity spot-checks) | Met — 12 gaps found & remediated; 0/73 refuted; 54/54 faithful | [ESCALATIONS.md — Addendum](ESCALATIONS.md#addendum--phase-6-coverage-sweep-findings-gap-remediation) |

Design-audit track (Phase 5), delivered alongside the rule catalog: 18 ADRs ([../adr/README.md](../adr/README.md)) and the design-system inventory ([../design/design-system-inventory.md](../design/design-system-inventory.md)); all ADR outcomes are **proposed**, pending team ratification.

---

## 8. Ratification asks

The audit is complete; the following decisions are explicitly **out of scope for the audit** and require human ratification before reimplementation begins:

1. **Clinical committee review of all P0 and P1 findings** (57 items) — for each, rule whether the legacy behavior is intended (carry forward) or a defect (change). Start with the 12 P0 items in [ESCALATIONS.md](ESCALATIONS.md#p0--high-clinical-impact).
2. **Owner confirmation of the 101 UNVERIFIABLE owner-review rules** (plus the 102 UNVERIFIABLE verification verdicts they derive from) — proprietary logic whose *intent* only the product/clinical owner can confirm.
3. **Legal review of the e-signature findings** — the shared default signing PIN ([RULE-AUTH-USUARIOS-063](access-control/RULE-AUTH-USUARIOS-063-shared-default-signing-pin-usuario-pin-defaults-to-settings.md)) and the default CryptoCubo signature profile (`advanced`, ICP-Brasil disabled; [RULE-DOCUMENTACAO-FATURAMENTO-032](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-032-default-electronic-signature-configuration-for-cryptocubo-do.md)) against MP 2.200-2 / ICP-Brasil e-signature norms.
4. **Decision on v1-vs-v3 sepsis aggregation** — whether the new platform adopts v1 AND-logic or v3 OR-logic as the canonical sepsis screen ([RULE-SEPSE-001](clinical-scoring/RULE-SEPSE-001-sepse-v1-alert-maiores-menores-dual-threshold.md) / [RULE-SEPSE-002](clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)).
5. **Canonical unit decisions before any reimplementation** — a single ratified convention for **FiO2** (fraction vs percentage), **lactate** (mg/dL vs mmol/L), and **vasopressor dosing** (mcg/kg/min vs ml/h vs raw ml), resolving cross-cutting issues 1–3 above once rather than rule-by-rule.

---

*This report describes the audit; the catalog and escalation report are its deliverables. All source citations are `repo:path:line-range` at the two commits named on the cover. Legacy behavior is preserved verbatim throughout — the ratification decisions above are where legacy behavior is accepted or changed.*
