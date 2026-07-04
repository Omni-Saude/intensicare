# Regulatory Plan — IntensiCare v2 (ANVISA SaMD Classe II)

**Owner:** regulatory-samd-specialist · **Status:** draft dossier-inputs for the delivery barrier · **Standard frame:** ANVISA RDC 657/2022 (SaMD) · RDC 16/2013 (BPF) · LGPD (Lei 13.709/2018) · Resolução CFM 2.299/2021 · ISO 14971 (risk management) · ISO 27001 / SBIS-CFM (security & interoperability).

**Authority precedence** (CONTRACTS §5): `ADR-001 ≻ vision ≻ directive ≻ audit`. Every requirement below is traced to a vision constraint (`VIS-C-NN`), a security/LGPD constraint in the ledger (`CON-00NN`), a hazard (`HAZ-0NN`, `docs/plan/_work/safety/hazard-log.yaml`), an audit finding (`AUDIT-00N`), or a review-queue item (`RQ-N` / `T-N`).

> **The load-bearing regulatory posture.** (1) IntensiCare is a **Classe II SaMD decision-support** system: it computes scores and raises advisory alerts, it **never** issues an autonomous diagnosis and **never** replaces clinical judgment (`VIS-C-01`, `VIS-C-08`). The moment the software would auto-diagnose or auto-treat, it exits Classe II — so that boundary is a *design invariant*, not a disclaimer. (2) The **physician remains the responsible decision-maker** under CFM; every alert is written to the patient's prontuário at NGS Level 2 with a transparent, reconstructable rationale (`VIS-C-07`, `VIS-C-13`, `HAZ-034`). (3) Health data is **sensitive personal data**; processing is purpose-bound to clinical decision support, a **RIPD is mandatory**, and PHI is encrypted at rest under the AMH per-tenant KMS (`VIS-C-05`, `VIS-C-06`, `CON-0069`/`CON-0103`).

---

## 0. Scope of this document

This plan collects the **dossier inputs** the ANVISA cadastro, the LGPD RIPD, and the SBIS/ISO certification packages will draw on. It does **not** substitute for the external ANVISA regulatory consultancy (`RQ-1`) or the DPO-led RIPD (`RQ-2`) — both are named blockers in the review queue. It gives those workstreams a single, traceable source: intended use, classification rationale, clinical-evaluation design, the LGPD/CFM action lists, the certification trajectory, and the ISO 14971 hazard linkage.

**Regulatory perimeter.** IntensiCare is a *consumer* of the AMH Data Platform. It inherits the platform's IAM Identity Center SSO, per-tenant KMS and Lake Formation ABAC (`ADR001-C-07`); the SaMD device boundary and this dossier cover **only** IntensiCare's own software: the scoring/alert engine, the REST/WebSocket API, the MLLP listener, and the operational PostgreSQL/TimescaleDB store. Where a control lives in the platform, this plan cites the inheritance rather than re-claiming it.

---

## 1. Intended-Use Statement (ANVISA dossier input — mandatory)

*(This section is the canonical `Declaração de Uso Pretendido` seed; the medical director countersigns the final PT-BR version — `RQ-6`. Portuguese labelling and IFU are mandatory: `VIS-C-04`.)*

**Product.** IntensiCare — software de suporte à decisão clínica para Unidades de Terapia Intensiva (UTI) adulto em hospitais brasileiros.

**Intended purpose.** IntensiCare ingests vital signs, laboratory results and EMR data (via HL7 v2 and FHIR R4 from the AMH Data Platform), computes validated early-warning and organ-dysfunction scores (MEWS, NEWS2, SOFA, qSOFA) and, in Phase 2, evidence-based clinical alerts across seven monitoring domains (sepsis, AKI, respiratory failure, hemodynamic instability, delirium, electrolyte emergencies, drug–drug interactions). Its output is an **advisory alert with a transparent rationale**, surfaced to the ICU care team and recorded in the patient chart.

**Intended user.** Licensed ICU clinicians — intensivist physicians and ICU nurses — and rapid-response teams. Not for patient/lay use; not for unsupervised operation.

**Intended clinical setting.** Adult ICU (UTI) of Brazilian hospitals; patients ≥ 18 years with expected stay > 24 h.

**Explicit boundaries of intended use** — the Classe II envelope (`VIS-C-01`, `VIS-C-08`):

| # | The system DOES | The system DOES NOT |
|---|-----------------|---------------------|
| 1 | Compute reference-validated scores and surface advisory alerts | Establish, confirm or exclude a diagnosis autonomously |
| 2 | Show the input values and score components that drove each alert | Prescribe, titrate, order or administer any therapy |
| 3 | Record every alert to the prontuário for the physician to act on | Close the loop / act on the patient without a clinician |
| 4 | Flag when a required input is missing or stale (no silent no-fire) | Replace the clinician's judgment or assume clinical accountability |

**Accountability statement (CFM).** IntensiCare is decision *support*. The attending physician remains solely responsible for every clinical decision (`VIS-C-08`; Resolução CFM 2.299/2021). Alerts are non-binding recommendations; acting on, deferring, or dismissing an alert is a documented physician act.

**Contraindications / limitations for the IFU.** Not validated for pediatric/neonatal ICU. Not a substitute for continuous bedside monitoring or for arterial blood-gas / laboratory confirmation. Alert firing depends on data availability and freshness; absence of an alert is **not** evidence of absence of risk (`HAZ-030`). Multi-domain correlation may add context or upgrade severity but never suppresses a constituent single-domain alert (`HAZ-027`).

---

## 2. SaMD Classification Rationale (RDC 657/2022 → Classe II)

**Determination.** IntensiCare is **Software como Dispositivo Médico (SaMD), Classe II**, requiring ANVISA **cadastro** (not full registro) (`VIS-C-02`). Confirmation of the class is a named external-consultancy deliverable (`RQ-1`).

**Rationale (IMDRF risk framing adopted by RDC 657/2022 — significance of information × state of the healthcare situation):**

| Axis | IntensiCare position | Effect on class |
|------|----------------------|-----------------|
| **Significance of the information to the clinical decision** | *Drives clinical management* — the alert informs, but does **not** diagnose or treat (informs, not "provides a diagnosis / triggers immediate action" in the auto sense) | Keeps below the top band |
| **State of the healthcare situation** | *Critical* — ICU deterioration, sepsis, shock | Raises the band |
| **Autonomy** | Advisory only; human-in-the-loop mandatory (`VIS-C-01`, `VIS-C-08`) | Caps at Classe II |

The combination *(informs a decision) × (critical situation) × (non-autonomous)* lands at **Classe II**. The audit and implementation plan both flag a **latent Classe III risk** if scope drifts toward autonomous diagnosis or ML-driven prediction that acts without a clinician (implementation-plan §5.1 risk; Phase 4 ML in vision §5.2). This plan therefore treats "no autonomous diagnosis" as a **classification-preserving design invariant** — a change that would auto-diagnose or auto-act is a regulatory-scope change requiring re-classification, not a feature toggle.

**Companion regulatory obligations that ride with Classe II:**
- **BPF / RDC 16/2013** — Boas Práticas de Fabricação for the software lifecycle (`VIS-C-03`); satisfied through the DevOps quality gates (CI lint/type/coverage/security, versioned releases, ADR governance — implementation-plan §4, §7).
- **Portuguese labelling & IFU** — rotulagem e instruções de uso em português (`VIS-C-04`).
- **Algorithm auditability** — 100% versioned/auditable algorithms (`VIS-C-13`), enforced by the `algorithm_version` invariant (`AUDIT` invariant #3 PASS) and per-alert immutable input snapshot (`HAZ-034`).

**Pre-market gating.** No processing of real patient data until the three critical invariants close: audit trail (#1, `AUDIT-004`/`T1`), PHI encryption (#4, `AUDIT-005`/`T4`), and deep health check (#5, `AUDIT-006`/`T5`). These are patient-safety *and* regulatory prerequisites (LGPD Art. 46 for #4; SaMD lifecycle traceability for #1).

---

## 3. Clinical Evaluation Plan (aligned to vision §6)

The clinical evaluation supplies the SaMD clinical-evidence dossier and the SBIS/effectiveness claims. It has three tiers, mapped directly to vision §6 and the review-queue clinical-validation protocol (`RQ-4`).

### 3.1 Tier 0 — Analytical/algorithmic validation (pre-clinical, blocks go-live)

Verify each score/alert against its reference standard **before** any human-subjects study. This tier absorbs the audit findings and the hazard log's test-requirements:

| Scope | Reference | Acceptance | Trace |
|-------|-----------|------------|-------|
| MEWS boundary correctness | Subbe 2001 | All bands exact; low-threshold inflation fixed | `AUDIT-001` |
| NEWS2 Scale 2 + O₂ integration | RCP 2017 | 86–92% bands + supplemental-O₂ path correct | `AUDIT-002` |
| SOFA single risk-classification path | Vincent 1996 / Sepsis-3 | One deterministic risk label; boundary vectors at each band edge | `AUDIT-003`, `HAZ-001..003`, `HAZ-019` |
| Unit canonicalization (FiO₂ fraction, lactate mmol/L, vasopressor mcg/kg/min, weight decimal) | units-registry | Schema rejects non-canonical units at compute boundary | `HAZ-013..015`, `HAZ-021`, `HAZ-028` |
| Facade-text = firing-predicate | contract test | Displayed rationale rendered from the same predicate that fires | `HAZ-016`, `HAZ-034` |

Exit criterion: every score/alert has boundary + can-fire test vectors passing; no dead/unwired criterion (`HAZ-020`).

### 3.2 Tier 1 — Observational before-after study (vision §6.1)

- **Design:** 3-month control (conventional MEWS/NEWS) → 2-week washout/training → 3-month intervention (Phase 2 alerts active).
- **Sites/N:** 2 ICUs × 30 beds × 3 months ≈ 540 admissions/period; 80% power, α = 0.05 to detect a 20% reduction in time-to-antibiotic.
- **Primary outcomes:** time-to-antibiotic in sepsis (target −60 min); time-to-recognition of AKI KDIGO ≥1 (target −6 h); cardiac arrest from electrolyte disturbance (target −50%).
- **Secondary:** alert PPV, time-to-action, 28-day ICU mortality, ventilator-free days, ICU-free days, **alarm-fatigue rate** (≤10% goal, `HAZ-023`).
- **Analysis:** paired t / Mann-Whitney; χ²/Fisher; interrupted time-series; propensity-score adjustment (age, SAPS 3, comorbidities).

### 3.3 Tier 2 — Stepped-wedge cluster RCT (vision §6.2, level-1 evidence)

- **Design:** SW-CRT, 8 ICUs (4 hospitals × 2), 18 months, 4 transition steps; all clusters start control, all end intervention (`VIS-C-14` — no denial of benefit).
- **N:** ≈ 6,480 patients; power > 90%, α = 0.05, ICC = 0.02; detects 25% reduction in the composite primary.
- **Primary (hierarchical):** time-to-adequate-antibiotic; AKI KDIGO ≥2 incidence; serious adverse events from unrecognized electrolyte disturbance.
- **Analysis:** GLMM with random cluster effects; Gamma(log) for time-to-event, binomial for incidence; ITT + per-protocol sensitivity.
- **Ethics & registration (mandatory before execution):** CEP + CONEP approval; ReBEC + ClinicalTrials.gov registration; consent waiver with opt-out (institutional intervention); **independent DSMB meeting quarterly** (`VIS-C-15`, `VIS-C-16`).

### 3.4 Post-market clinical follow-up (PMCF)

Continuous monitoring feeds both ANVISA post-market surveillance and the hazard log's residual-risk closure: PPV per alert vs its budget, alarm-fatigue rate per unit, ingestion→alert latency p95 < 30 s (`VIS-C-09`, `HAZ-033`), delivery/ack rates (`HAZ-025`). Any post-market signal re-opens the relevant hazard.

---

## 4. LGPD / RIPD Action List

Health data = **dado pessoal sensível** (LGPD Art. 5º II); purpose bound to clinical decision support (Art. 6º I); **RIPD obrigatório** (`VIS-C-05`, `VIS-C-06`). The RIPD is a named blocker owned by the DPO/legal (`RQ-2`) and must precede any real-data processing.

| # | Action | Legal basis / control | Owner | Trace | Status |
|---|--------|-----------------------|-------|-------|:------:|
| L1 | Produce the **RIPD** (data-flow map: HL7/FHIR ingest → scoring → alert → prontuário) | Art. 38 RIPD; Art. 6 finality/necessity | DPO/legal | `RQ-2`, `VIS-C-06` | ❌ blocker |
| L2 | Record **legal basis**: proteção da vida/incolumidade (Art. 11 II "g" / Art. 7 VII); tutela da saúde | Art. 11 sensitive-data hypotheses | DPO | `VIS-C-05` | draft |
| L3 | **Encrypt PHI at rest** (nome, CPF, CNS, MRN, birth_date) — pgcrypto under per-tenant KMS data key | Art. 46; invariant #4 | security-lgpd | `CON-0069`/`CON-0103`, `AUDIT-005`, `T4` | ❌ pending |
| L4 | **Immutable audit trail** of every PHI read + mutating action | Art. 37 registro de operações; invariant #1 | security-lgpd | `CON-0066`/`CON-0097`, `AUDIT-004`, `T1` | ❌ pending |
| L5 | **7-year retention** in TimescaleDB with defined disposal | Art. 15–16; `VIS-C-12` | platform-ops | `VIS-C-12` | design |
| L6 | Data-subject rights path (access, correction, portability, info) via hospital as controller | Art. 18 | DPO | — | draft |
| L7 | **DPA / operator agreement** with each hospital (controller/operator roles) | Art. 39 | legal | implementation-plan risk #5 | draft |
| L8 | Deny-by-default access control; no legacy `ignorePermission=true`; no shared signing PIN | Art. 46 security-by-design | security-lgpd | `CON-0038`, security-lgpd §0 | design |
| L9 | Transit encryption (TLS) end-to-end; Caddy reverse proxy | Art. 46 | platform-ops | `T7` | pending |
| L10 | Data-breach response + ANPD notification runbook | Art. 48 | DPO/ops | — | to-do |
| L11 | Correct README/claims — remove HIPAA/GDPR, assert LGPD/SBIS | truthful-claims | docs | audit §4.1, implementation-plan §5.2 | ✅ done |

---

## 5. CFM Conformity Matrix

Resolução CFM 2.299/2021 (prontuário eletrônico, interoperabilidade) + the indelegable-medical-responsibility principle. Two obligations are load-bearing and both are already wired as design requirements in the hazard log (`HAZ-034`) and security architecture.

| CFM requirement | IntensiCare conformity | Design mechanism | Trace | Status |
|-----------------|------------------------|------------------|-------|:------:|
| **Alerts registered to the patient record** at NGS Level 2 | Every fired alert is written to the prontuário with rule_id + algorithm version + immutable input snapshot | Alert-persistence + audit trail | `VIS-C-07`, `HAZ-034`, `CON-0066` | design |
| **Physician remains responsible** — advisory-only, human-in-the-loop | No autonomous action; alerts are non-binding; ack/dismiss is a documented physician act | Intended-use invariant §1 | `VIS-C-08`, `VIS-C-01` | ✅ design invariant |
| **Score-component transparency** — clinician can see *why* an alert fired | UI shows the input values and individual score components; rationale is rendered from the same predicate that fires (no facade drift) | Score-detail view (US-04); facade=predicate contract test | `HAZ-016`, `HAZ-034`, audit §2 | design |
| **Reconstructability / recall** of any past alert | Any historical firing reconstructable by version + input snapshot; a defective rule version can identify and withdraw its alerts across affected patients | Versioned algorithms + recall mechanism | `VIS-C-13`, `HAZ-034`, invariant #3 | design |
| **Interoperability** (structured, standards-based) | FHIR R4 (via AMH DP) + HL7 v2 ingest | FHIR client / MLLP listener | implementation-plan §2.3 | ✅ functional |
| **Stale/missing-input transparency** — clinician not falsely reassured | Engine distinguishes "not evaluated (data missing)" from "evaluated, no fire"; UI discloses data coverage & data age | Missing-input + staleness handling | `HAZ-024`, `HAZ-030` | design |

---

## 6. SBIS / ISO-27001 Certification Trajectory

Certification sequence for the Brazilian market and the pre-launch security bar (implementation-plan §5.1, §5.3; review-queue `RQ-3`, `RQ-5`).

| Stage | Certification / gate | Purpose | Owner | Trace | Status |
|-------|----------------------|---------|-------|-------|:------:|
| Pre-launch (primary) | **SBIS-CFM** (S-RES / interoperability + security manual criteria) | Primary BR interoperability & EHR-security certification | architect | `RQ-3` | draft (Q4 2026) |
| Pre-launch | **External penetration test** | Independent security assurance before go-live | external firm | `RQ-5`, risk table | draft (Q4 2026) |
| Pre-launch (recommended) | **ISO/IEC 27001** ISMS | Formal information-security management system | security-lgpd | implementation-plan §5.1 | roadmap |
| Ongoing | Annual pentest + ANVISA/ANPD/CFM surveillance renewals | Post-market security & regulatory continuity | ops/DPO | implementation-plan §5.3 | roadmap |

**Dependencies.** SBIS interoperability criteria lean on the FHIR R4 client (functional). ISO 27001 and SBIS security criteria both depend on invariants #1/#4 (audit trail, encryption) and the deny-by-default access model already specified in the security-LGPD architecture — so L3/L4/L8 above are shared prerequisites, not separate work.

---

## 7. Hazard-Log Linkage (ISO 14971)

**Canonical hazard log:** `docs/plan/_work/safety/hazard-log.yaml` (34 hazards, HAZ-001…HAZ-034), owned by the clinical-safety-officer. *(The directive references `docs/plan/clinical/hazard-log.md`; the maintained artifact is the YAML above — this plan links the live source. If a Markdown mirror is later published under `docs/plan/clinical/`, it must be generated from the YAML, not authored independently.)*

The hazard log **is** the ISO 14971 risk-management file for the SaMD dossier. This regulatory plan does not restate it; it establishes the linkage the dossier needs:

- **Risk-management file → SaMD dossier.** The hazard log's hazard → hazardous-situation → harm → severity×probability → mitigations (each a testable design requirement with a named owner) → residual-risk structure is the ISO 14971 file ANVISA expects for a Classe II SaMD.
- **Residual-risk lifecycle gates certification.** `residual_risk` stays `null` and `status` stays `open` until mitigations are *verified present* in the reviewed specs and the clinical-safety-officer countersigns. No hazard may carry unresolved `open` status into go-live; this is the patient-safety VETO.
- **Directly regulatory hazards.** `HAZ-034` (non-auditable/unversioned algorithm; alert not recorded in prontuário) is the explicit SaMD/CFM compliance hazard — its mitigations *are* the §5 CFM matrix and `VIS-C-07`/`VIS-C-13`. `HAZ-032` (sodium-overcorrection → central pontine myelinolysis, catastrophic) and `HAZ-006`/`HAZ-028` (vasopressor unit chaos, catastrophic) are the highest-severity clinical hazards feeding the clinical-evaluation Tier-0 acceptance.
- **Class-preservation hazards.** The P0 defect hazards (`HAZ-001…012`) and the systemic classes (`HAZ-013…022`) are exactly the correctness failures that, if shipped, would both harm patients and invalidate the "validated decision support" basis of the Classe II claim. Each P0 is RATIFY-mandatory (`SYS-C-03`): a human clinical decision, never a silent adoption.
- **Post-market feedback.** §3.4 PMCF metrics re-open hazards on signal (alarm fatigue `HAZ-023`, delivery failure `HAZ-025`, latency `HAZ-033`), closing the ISO 14971 production-and-post-production loop.

---

## 8. Regulatory Review-Queue — folded in

The six mandatory pre-production regulatory artifacts from `docs/review-queue.md`, mapped to their home section here and their gating status. All six remain **blockers to real-patient data** until closed.

| RQ | Artifact | Owner | Covered in | Gating status |
|----|----------|-------|------------|:-------------:|
| `RQ-1` | ANVISA SaMD classification | external consultancy | §2 | 🔴 blocker — consultancy not engaged |
| `RQ-2` | LGPD RIPD | DPO/legal | §4 (L1) | 🔴 blocker — not produced |
| `RQ-3` | SBIS certification plan | architect | §6 | draft (Q4 2026) |
| `RQ-4` | Clinical validation protocol | clinical team | §3 | draft (Q3 2026) |
| `RQ-5` | Pentest report | external firm | §6 | draft (Q4 2026) |
| `RQ-6` | Intended-use statement | medical director | §1 | draft — needs medical-director sign-off |

**Immediate blockers (review-queue §🔴):** (1) engage ANVISA consultancy → `RQ-1`; (2) produce RIPD → `RQ-2`/`L1`; (3) implement `audit_trail` → `L4`/`T1`/`AUDIT-004`; (4) run a real-hospital HL7 pilot for clinical validation → Tier-1 §3.2. Technical prerequisites `T1`,`T4`,`T5` (audit trail, PHI encryption, deep health check) are the shared LGPD-and-SaMD gate.

---

## 9. Traceability summary

| Regulatory obligation | Primary source | Design/spec home |
|-----------------------|----------------|------------------|
| No autonomous diagnosis; advisory only | `VIS-C-01`, `VIS-C-08` | §1 intended use; §5 CFM matrix |
| SaMD Classe II / RDC 657/2022 cadastro | `VIS-C-02` | §2 |
| BPF RDC 16/2013 | `VIS-C-03` | §2; implementation-plan §4 |
| PT-BR labelling & IFU | `VIS-C-04` | §1 |
| Sensitive-data / purpose limitation | `VIS-C-05` | §4 (L2) |
| RIPD mandatory | `VIS-C-06` | §4 (L1) |
| Alert in prontuário NGS-2 | `VIS-C-07` | §5 |
| Physician responsibility | `VIS-C-08` | §1, §5 |
| Latency p95 < 30 s | `VIS-C-09` | §3.4; `HAZ-033` |
| 7-year retention | `VIS-C-12` | §4 (L5) |
| Algorithm 100% auditable | `VIS-C-13` | §2, §5; `HAZ-034` |
| Stepped-wedge ethics (no benefit denial, DSMB, CEP/CONEP/ReBEC) | `VIS-C-14/15/16` | §3.3 |
| Encryption at rest / audit trail (invariants #4/#1) | `CON-0069`/`CON-0103`, `CON-0066`/`CON-0097` | §4 (L3/L4) |
| ISO 14971 risk file | hazard-log.yaml (HAZ-001…034) | §7 |
| SBIS / ISO 27001 / pentest | implementation-plan §5; `RQ-3/5` | §6 |

---

*Compiled by the regulatory-samd-specialist as dossier inputs for the delivery barrier. External ANVISA consultancy (`RQ-1`) and DPO-led RIPD (`RQ-2`) remain the authoritative owners of formal classification and the impact report respectively; this plan feeds them a single traceable source. Not for real-patient data until the §8 blockers close.*
