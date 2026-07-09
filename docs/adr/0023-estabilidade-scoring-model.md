# 0023. Estabilidade scoring model: threshold-based vs ML-based vs hybrid

Status: accepted
Date: 2026-07-07
Depends on: ADR-001 (AMH Data Platform consumer), ADR 0020 (trilhas-engine architecture), ADR 0022 (ventilação service architecture)

## Context and Problem Statement

The hemodynamic stability ("estabilidade") domain is the most rule-dense clinical surveillance domain in IntensiCare. The legacy platform encoded 26 rules (`RULE-ESTABILIDADE-001..026`) across three parallel and mutually inconsistent shock pathways:

1. **v3 `estabilidade`** — 13 criteria (`criterio_1..13`), of which only 7/10/12/13 ever fed an alert; criteria 1-6/8/9/11 are dead code (CLU-ESTABILIDADE-02, CON-0162).
2. **Manual pathway** — 6 criteria (C1-C6, RULE-ESTABILIDADE-017..023) with count-to-color aggregation.
3. **`estabilizacao`/trilha2 v1** — a duplicate tiering shell (RULE-ESTABILIDADE-024/025) with the same vasopressor cutoff encoded in incompatible units.

The v2 rebuild consolidates these into one evidence-anchored design in `domain_hemo.py` (931 lines, 6 alert evaluators): shock-index screening, lactate-clearance resuscitation targeting, vasopressor escalation, refractory shock, fluid non-responsiveness, and vasoactive-medication × BP conflict. All vasopressor dosing is canonical `mcg/kg/min` via the conversion service (§4 of the hemodynamics clinical spec). Every threshold cites a guideline or paper (Rady 1994, Singer 2016/Sepsis-3, Evans 2021/SSC, Asfar 2014/SEPSISPAM, Hernandez 2019/ANDROMEDA-SHOCK, SCCM 2024).

However, the current implementation is **purely threshold-based**: each of the 6 alerts fires when clinical inputs cross hardcoded, clinically-anchored cutoffs (SI > 0.9, lactate <10% clearance at 2h, vasopressor >50% increase in 2h, MAP <65 mmHg sustained >30 min, etc.). The 27 hemodynamic criteria collectively represent a rich clinical signal that a machine-learning model could potentially exploit — detecting deterioration earlier, personalizing thresholds to patient subpopulations, or identifying patterns invisible to univariate rules.

The question is: **should the estabilidade scoring model remain purely threshold-based (the current clinically-validated approach), adopt a machine-learning model, or pursue a hybrid architecture?** This is not a theoretical question — the clinical safety context (ICU hemodynamic instability is life-threatening in minutes) means any model that cannot explain *why* it fired is a patient-safety risk.

### Decision Drivers

- **VIS-C-01 / VIS-C-08:** all outputs are advisory, physician-owned. Automatic diagnosis is forbidden. Every alert must display the rationale — which specific parameter triggered it and at what threshold (`CON-0090`/`PER-C-04`).
- **Auditability:** every alert must stamp the exact `definition_version` that fired it (INV-3). The alert engine's Gate C (facade==predicate) requires that rendered rationale is generated from the same AST the engine evaluates — a black-box ML model cannot satisfy this without post-hoc explainability.
- **Regulatory:** the platform targets NGS Level 2 (clinical decision support, not autonomous action — VIS-C-07). Brazilian CFM Resolution 2.147/2016 and ANVISA RDC 657/2022 require traceable clinical rationale. An ML model used for clinical decision support must be registrable as software as a medical device (SaMD) under ANVISA — a threshold-based rules engine is substantially easier to register.
- **Data availability and quality:** the legacy's #1 audit finding (SYS-02/CON-0060) was vasopressor dose encoded four incompatible ways. Lactate was encoded in mg/dL vs mmol/L (~9× drift). Weight parsing inflated values ~10× (SYS-09). Any ML model trained on legacy data inherits these systemic unit errors unless the training pipeline includes the same edge normalization the threshold engine already enforces.
- **RATIFY backlog:** 10 RATIFY anchors remain unresolved (RAT-ESTABILIDADE-01..11), including the disputed vasopressor ladder thresholds (P0, RAT-ESTABILIDADE-08). A threshold-based model makes these disputes explicit and resolvable by a clinical committee; an ML model would obscure them inside learned weights.
- **Sub-30s latency:** critical alerts (refractory shock, vasopressor escalation) must deliver in <5s on the NRT path (VIS-C-09, IMP-2.2-03). ML inference latency must fit within this budget.
- **Evolving evidence:** hemodynamic thresholds change as guidelines update (e.g., SEPSISPAM 2014 → SSC 2021 → SCCM 2024). A threshold engine can update a single rule; an ML model requires retraining and revalidation on new data.

## Considered Options

### Option 1: Threshold-based — purely rule-driven, clinically anchored (current architecture)

All 27 hemodynamic criteria are evaluated as explicit, auditable threshold rules. Each rule cites its evidence anchor (guideline/paper), declares its trigger predicate (a composable boolean expression in the alert-definition YAML schema), and renders its firing rationale from the same AST the engine evaluates. This is what `domain_hemo.py` currently implements for the 6 consolidated alerts. Clinicians see exactly which parameter crossed which threshold, with the evidence citation, and can dispute/escalate via the RATIFY queue.

- **Pros:**
  - **Full auditability and explainability.** Every firing answers "what triggered it, at what threshold, per what guideline." Satisfies VIS-C-01, INV-3, and Gate C (facade==predicate) by construction.
  - **Regulatory simplicity.** A deterministic rules engine fits the SaMD Class I/II registration pathway under ANVISA RDC 657/2022 without the additional validation burden of an ML model.
  - **Directly addressable RATIFY queue.** Every disputed threshold (RAT-ESTABILIDADE-01..11) is an explicit, reviewable number in the YAML definition. A clinical committee can change a threshold and deploy without retraining.
  - **Guideline-responsive.** When SCCM publishes updated vasopressor guidance, the threshold changes in one YAML file, mints a new `definition_version`, and ships. No model retraining.
  - **CI-enforced correctness.** Build-time gates (band-partition, criterion-coverage, unit-check) make threshold errors un-shippable. The SYS-01..08 defect classes are eliminated at the source.
  - **Proven.** The current domain_hemo.py evaluators pass 34 test vectors from `_work/alerts/hemodynamics.yaml`. Every criterion is exercised by at least one can-fire vector.
  - **Zero inference latency.** Threshold evaluation is a set of float comparisons — microseconds, not milliseconds.

- **Cons:**
  - **Univariate, brittle at population edges.** A fixed SI > 0.9 threshold fires identically for a 25-year-old athlete and an 85-year-old with chronic tachycardia. No personalization to patient baseline, comorbidities, or temporal trends beyond the explicitly coded ones (e.g., the 2h vasopressor escalation window).
  - **Cannot detect novel patterns.** The rules only fire on what they're programmed to look for. A complex multi-parameter deterioration pattern (e.g., slowly rising lactate + gradually dropping MAP + increasing FiO₂ demand, none individually crossing their threshold but collectively predictive of imminent shock) goes undetected.
  - **Threshold maintenance burden.** Every new guideline or institutional protocol change requires a human to translate it into a YAML predicate, write test vectors, and go through RATIFY. This is slow and labor-intensive compared to a model that learns from data.
  - **No continuous risk score.** The current model produces discrete alert bands (watch/urgent/critical), not a continuous hemodynamic instability probability. A continuous score would enable trend visualization and earlier warning.

### Option 2: ML-based — learned model for hemodynamic instability prediction

Replace or augment the threshold rules with a machine-learning model trained on historical AMH Gold data (vitals, labs, medication administration, outcomes). The model outputs a continuous hemodynamic instability risk score (0-1) and/or classifies patients into stability tiers. Could use gradient-boosted trees (XGBoost/LightGBM — interpretable via SHAP), a lightweight neural network, or a survival-analysis model predicting time-to-decompensation.

- **Pros:**
  - **Earlier detection.** ML models can identify subtle multi-parameter patterns that precede threshold crossings — potentially detecting deterioration hours before a single parameter crosses its threshold.
  - **Personalization.** A model can learn patient-specific baselines and adjust risk based on age, comorbidities, chronic medication, and admission context.
  - **Continuous risk score.** A 0-1 probability enables graded visualization (risk trendlines, "probability of decompensation in next 2h") that threshold-based discrete bands cannot express.
  - **Reduced threshold-maintenance burden.** The model learns from outcomes data; new evidence is incorporated by retraining on updated datasets, not by hand-authoring YAML predicates.
  - **Cross-domain signal integration.** An ML model can naturally consume inputs from respiratory, renal, and sepsis domains without explicit correlation-engine rules.

- **Cons:**
  - **Black-box — clinical safety risk.** A model that outputs "85% risk of refractory shock" without explaining *which parameters* drove that risk is unacceptable in an ICU context. Post-hoc explainability (SHAP/LIME) provides feature-importance approximations, not the deterministic "this parameter crossed this threshold per this guideline" that Gate C requires. A clinician cannot act on an unexplainable alert.
  - **Regulatory burden.** ANVISA classifies ML-based clinical decision support as SaMD Class III/IV depending on the clinical significance of the decision supported. Registration requires clinical validation studies, algorithm-change protocol documentation, and post-market surveillance — a 12-18 month regulatory timeline vs weeks for a threshold engine.
  - **Training data contamination.** The legacy AMH data carries the SYS-02/03/09 unit errors (vasopressor in mL/h vs mcg/kg/min, lactate in mg/dL vs mmol/L, weight ~10× inflation). Training an ML model on un-normalized data would bake these errors into the model weights — the model would learn that "noradrenaline > 10" means high dose when "10" could be mL/h, mcg/kg/min, or mcg/kg/h depending on which legacy pathway wrote the record.
  - **Distribution shift.** ICU protocols, vasopressor formulations, and monitoring equipment change over time. A model trained on 2020-2024 data may perform poorly on 2026 data — and the degradation may be silent (no explicit threshold to check).
  - **Inference latency.** An XGBoost model adds ~1-5 ms per prediction; a neural net adds ~10-50 ms. Well within the <30s budget, but adds complexity to the NRT hot path.
  - **Re-training overhead.** Every guideline change or new institutional protocol requires model retraining and revalidation — a weeks-to-months cycle vs a threshold change that ships in a day.
  - **Versioning mismatch with the alert engine.** The alert engine's `definition_version` stamps assume deterministic versioning (change a threshold → new version). An ML model's "version" is a training run, which is not directly comparable to a threshold change — making audit and reproducibility harder.

### Option 3: Hybrid — threshold-based primary, ML as enrichment/secondary (recommended)

Keep the threshold-based rules engine as the primary, clinically-auditable alerting pathway (producing the discrete watch/urgent/critical bands that drive notifications, bed-board status, and the audit trail). Add an ML-based enrichment layer that produces a continuous hemodynamic instability risk score (0-1) as an *advisory overlay* — displayed on the clinical dashboard alongside threshold-derived alerts but never the sole trigger for a critical notification. The ML model's output is treated as a decision-support signal, not a clinical decision.

- **Pros:**
  - **Preserves clinical safety and auditability.** The threshold-based primary pathway continues to satisfy VIS-C-01, INV-3, and Gate C exactly as today. The ML enrichment is non-blocking: if the ML model is unavailable, the threshold alerts still fire.
  - **Adds early-warning capability.** The ML risk score can surface deterioration risk before any single parameter crosses its threshold — displayed as a trend-line on the hemodynamic dashboard, with a configurable "elevated risk" advisory flag.
  - **Regulatory path is the simpler one.** The threshold engine is the SaMD Class I/II device; the ML enrichment is classified as a non-device clinical decision support tool (per ANVISA's current guidance on "software that supports clinical decisions without replacing clinical judgment") — pending formal regulatory consultation.
  - **ML can learn from cleaner data.** The ML training pipeline can consume the same canonical-unit-normalized data that the threshold engine already enforces — `domain_hemo.py`'s vasopressor conversion service produces clean `mcg/kg/min` values, lactate in `mmol/L`, validated `peso` — giving the ML model a clean foundation that the legacy never had.
  - **Incremental adoption.** Start with threshold-only as the MVP (already built). Add the ML enrichment layer in a subsequent phase, once the data pipeline is clean, the regulatory pathway is confirmed, and clinical validation data is available.
  - **Explainability via reference to thresholds.** The ML score can be annotated with SHAP values showing which features contributed most, and those features can be cross-referenced to the nearest threshold rule — e.g., "ML risk 0.78, driven by rising vasopressor dose (currently 0.3 mcg/kg/min, escalation threshold 0.5) and dropping MAP (currently 68 mmHg, refractory threshold 65)."

- **Cons:**
  - **Two systems to maintain.** Threshold rules + ML model + the integration between them — more components, more operational surface, more testing.
  - **Potential for conflicting signals.** The ML model may show "high risk" while all threshold rules are normal (or vice versa). This must be handled in the UX — the dashboard must present both signals without confusing clinicians. The design principle: threshold alerts are *actionable* (they demand a response); ML risk is *advisory* (it suggests closer monitoring).
  - **ML still requires regulatory attention.** Even as a non-device advisory tool, the ML model's validation, performance monitoring, and update protocol must be documented for the hospital's clinical governance committee.
  - **Training data timeline.** The ML model requires a clean, normalized dataset with sufficient outcomes (decompensation events). Building this dataset — cleaning the AMH Gold history, running it through the conversion service, annotating outcomes — is a non-trivial data-engineering project.
  - **The RATIFY backlog is not resolved by ML.** The 10 disputed threshold anchors are clinical questions (what is the correct vasopressor ladder?), not statistical ones. Adding ML does not answer them.

### Option 4: ML-primary with threshold safety net

The ML model is the primary alerting mechanism; threshold rules serve only as a safety net — firing if the ML model is silent but a known-dangerous threshold is crossed (e.g., MAP < 55 mmHg sustained regardless of ML risk score). The ML model's output classification (watch/urgent/critical) drives notifications.

- **Pros:**
  - Maximizes early-detection potential — the ML model sees everything, and thresholds only catch what the model misses.
  - Continuous risk score is the primary signal, not an enrichment.

- **Cons:**
  - **Regulatory non-starter for NGS Level 2.** An ML-primary clinical alerting system in a Brazilian ICU almost certainly requires SaMD Class III/IV registration, including a clinical trial demonstrating non-inferiority to standard care. This is a multi-year, multi-million-real regulatory program — disproportionate to IntensiCare's current stage.
  - **The "safety net" pattern is fragile.** If the ML model and threshold rules disagree, which one governs? A "model says normal, threshold says critical" scenario must resolve to the threshold (patient safety trumps ML) — but then the model is effectively not primary for the most important alerts.
  - All the ML cons from Option 2 apply, magnified by being in the primary path.

## Decision Outcome

Recommend **Option 3** (hybrid: threshold-based primary, ML as enrichment/secondary), with the threshold engine as the **MVP delivery** and the ML enrichment deferred to a post-MVP phase contingent on (a) clean, normalized training data availability, (b) regulatory pathway confirmation with ANVISA, and (c) clinical validation with partner ICUs.

The threshold-based primary pathway is already built and tested (`domain_hemo.py`, 34 test vectors, 6 consolidated alerts, canonical mcg/kg/min dosing via the conversion service). It satisfies every current requirement: auditability (INV-3, Gate C), regulatory simplicity (Class I/II SaMD), CI-enforced correctness, and the RATIFY queue for disputed thresholds. There is no clinical or regulatory reason to delay the MVP for an ML model that would add months of data engineering, model validation, and regulatory uncertainty.

The ML enrichment layer is the right medium-term investment: it adds genuine clinical value (earlier warning, personalized risk, continuous scoring) without compromising the safety and auditability of the primary threshold pathway. It can be developed in parallel with the MVP's clinical deployment, using the clean, canonical-unit-normalized data pipeline the threshold engine already enforces.

Option 1 (threshold-only) is the MVP baseline. Option 3 is the target architecture. Option 2 (ML-primary) and Option 4 (ML-primary with safety net) are rejected — ML-primary alerting in a Brazilian ICU context requires a disproportionate regulatory burden for uncertain clinical benefit.

### MVP delivery (Option 1 baseline — this sprint)

The 6 consolidated hemodynamic alerts in `domain_hemo.py` are the MVP:

| Alert ID | Clinical scope | Severity | Evidence anchor |
|---|---|---|---|
| `ALERT-HEMO-SHOCK-INDEX-01` | Shock index with perfusion corroborator | watch | Rady 1994, ANDROMEDA-SHOCK 2019 |
| `ALERT-HEMO-LACTATE-CLEARANCE-02` | Inadequate lactate clearance under resuscitation | critical | Jones 2010 JAMA, SSC 2021 |
| `ALERT-HEMO-VASO-ESCALATION-03` | >50% vasopressor increase or second agent added | urgent | SCCM 2024, SSC 2021 |
| `ALERT-HEMO-REFRACTORY-SHOCK-04` | MAP <65 sustained on maximal vasopressor | critical | SEPSISPAM 2014, VIS-3.4-06 |
| `ALERT-HEMO-FLUID-NONRESPONSIVE-05` | Fluid non-responsiveness with positive 24h balance | watch | Marik 2013, Monnet 2016 |
| `ALERT-HEMO-ANTIHTN-CONFLICT-06` | Antihypertensive × hypotension/vasopressor conflict | watch | Institutional, RULE-ESTABILIDADE-012/021 |

All dosing is canonical `mcg/kg/min` via the conversion service. All thresholds are declared in `_work/alerts/hemodynamics.yaml` and subject to CI build-time gates. The 10 unresolved RATIFY anchors are flagged as committee decisions (RAT-ESTABILIDADE-01..11) and ship with recommended defaults per the hemodynamics clinical spec §6.

### Post-MVP enrichment (Option 3 — target architecture)

1. **Data foundation (Phase 1):** build a clean, normalized training dataset from AMH Gold history. Pipe all relevant inputs (vitals, labs, vasopressor doses, fluid balance, outcomes) through the same edge-normalization layer the threshold engine uses — no raw mL/h, no un-validated weight, no mg/dL lactate. Annotate decompensation events (refractory shock, escalation to second vasopressor, lactate non-clearance) as training labels.

2. **Model development (Phase 2):** train an interpretable model (gradient-boosted trees — XGBoost or LightGBM) to predict hemodynamic decompensation in the next 2-6 hours. Use SHAP for feature-importance explainability. Publish model performance metrics (AUROC, sensitivity at fixed specificity, lead time vs threshold crossing) for clinical review.

3. **Integration (Phase 3):** deploy the ML model as a micro-batch enrichment — runs at the same cadence as the hemodynamic micro-batch runner, consumes the same normalized inputs, and emits `hemodynamics.ml_risk_score` as a non-alerting event. The clinical dashboard renders the ML risk score as a trend-line alongside threshold alerts, with SHAP feature-importance annotations.

4. **Regulatory (Phase 4):** submit the threshold engine for SaMD Class I/II registration. Submit the ML enrichment for regulatory consultation as a non-device CDS tool. Conduct a clinical validation study in partner ICUs comparing ML-augmented vs threshold-only monitoring.

### Consequences

**Good (MVP — threshold engine):**

- The 6 consolidated alerts ship with full auditability, CI-enforced correctness, and canonical unit safety — closing the legacy's SYS-02/03/09 defect classes at the source.
- Every alert is explainable: "MAP < 65 mmHg for >30 min on norepinephrine > 1.0 mcg/kg/min per SEPSISPAM 2014."
- The RATIFY queue is transparent: every disputed threshold is an explicit number in a YAML file, reviewable by the clinical committee.
- Zero ML infrastructure, zero model training, zero regulatory uncertainty — ships on the current sprint timeline.

**Bad (MVP):**

- No early-warning beyond explicit threshold crossings. A patient trending toward shock but not yet crossing any threshold is invisible.
- No personalization. The same SI > 0.9 threshold applies to all patients regardless of baseline physiology.
- No continuous risk score. The discrete watch/urgent/critical bands are coarse-grained.

**Good (post-MVP ML enrichment):**

- Earlier detection of deterioration via multi-parameter pattern recognition.
- Continuous risk score enables trend visualization and risk-stratified monitoring.
- Clean training data: the canonical-unit pipeline eliminates the legacy data-quality problems.

**Bad (post-MVP ML enrichment):**

- Two systems to maintain and integrate.
- Regulatory consultation required, even for advisory use.
- Training data engineering is a non-trivial project.
- The RATIFY backlog is not resolved by ML — the clinical threshold disputes remain committee decisions.

### Open questions

1. **Regulatory classification of the ML enrichment layer** — whether ANVISA classifies an advisory-only ML risk score as a non-device CDS tool or requires SaMD registration. This gates the Phase 2 timeline and should be resolved via formal regulatory consultation before model development begins.
2. **Clinical validation endpoint** — what constitutes an acceptable ML model? AUROC > 0.85? Lead time > 2h before threshold crossing? Sensitivity > 90% at fixed 80% specificity? These metrics should be defined with the clinical committee before training.
3. **Feature set** — which parameters beyond the threshold engine's 19 inputs should the ML model consume? Demographics, comorbidities, chronic medications, admission diagnosis, time since ICU admission, mechanical ventilation status, sedation level (RASS)? Each additional feature increases the regulatory surface.
4. **Outcome labels** — what defines a "hemodynamic decompensation event" for training? Escalation to second vasopressor? MAP < 60 mmHg for >15 min? Lactate > 4 mmol/L? Clinical committee must standardize this definition.
5. **Model update cadence** — how often does the ML model retrain? Quarterly on new AMH Gold data? On every guideline change? What is the protocol for detecting and responding to model drift?
