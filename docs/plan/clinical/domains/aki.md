# Acute Kidney Injury (AKI) Domain — IntensiCare v2 Clinical Specification

**Guild:** Clinical (AKI domain designer) · **Vision ref:** §3.2 (AKI / KDIGO, priority P2) ·
**Platform:** AMH Data Platform consumer (ADR-001) · **Legacy source clusters:** `balanco-hidrico`
(urine-output & fluid-balance aggregation, 62 rules), `clinical-scoring` (SOFA renal sub-score),
`sinais-vitais` (creatinine validation), `sepse` (oliguria criterion), `antimicrobiano` (renal dose adjustment).

AKI has **no dedicated legacy rule cluster** — its logic was scattered across the fluid-balance nursing-day
aggregators, the SOFA renal sub-score, and a broken sepsis oliguria criterion. This document assembles those
fragments into **one evidence-anchored KDIGO 2012 staging engine**: a baseline-creatinine resolver, a
rolling urine-output windowing engine (replacing the legacy 07:00–07:00 nursing day), and an additive
nephrotoxin-exposure detector. Every threshold cites KDIGO 2012 (and/or the vision, the alert-catalog AKI-*
entries, and a `RULE-*` catalog ID). P0/P1/UNVERIFIABLE legacy defects are designed to the **reference-anchored
recommended default** and flagged **pending RAT-\***; the ratification committee decides.

---

## 1. Clinical scope

**In scope.** Adult ICU (UTI) acute kidney injury, staged by the **KDIGO 2012 Clinical Practice Guideline**
(Kidney Int Suppl 2012;2(1):1–138). Vision VIS-3.2-01: AKI occurs in 30–60 % of ICU patients and carries a
6.5× mortality increase; early KDIGO staging enables intervention at reversible stages. The trial primary
outcome is *time-to-recognition of AKI KDIGO ≥1* (goal −6 h, VIS-6.1-02) and *incidence of AKI KDIGO ≥2*
(VIS-6.2-03).

1. **KDIGO staging** — compute the current KDIGO stage (1/2/3) from the *worst* of the serum-creatinine
   criterion and the urine-output criterion, against a resolved baseline creatinine.
2. **AKI progression** — detect a stage increase within a rolling 24 h window (early deterioration signal).
3. **Additive nephrotoxicity** — detect a rising-creatinine trend under a nephrotoxic-drug combination,
   *before* the patient reaches KDIGO stage 1, so exposure can be withdrawn while injury is still reversible.

**Out of scope / delegated.**
- **Fluid-balance intake/output ledger, cumulative balance, and the vasopressor unit-conversion service** →
  **hemodynamics** domain (this domain *consumes* the fluid-balance aggregates and volume-status flag).
- **SOFA renal sub-score** (an organ-dysfunction *score* component) → **clinical-scoring** domain; AKI staging
  is a *diagnostic stage*, not a SOFA point. They share the creatinine and urine-output inputs (§5).
- **Drug–drug additive-nephrotoxicity *combination* alerting (pre-injury, no renal marker)** → **pharmaco-interaction**
  domain (vision §3.7 / DDX-003). This domain owns only the **nephrotoxin-exposure + rising-renal-marker** signal
  (vision §3.2 / AKI-005); the boundary is drawn in §5 to avoid a duplicate alert.
- **Electrolyte consequences of AKI** (hyperkalemia, metabolic acidosis) → **electrolytes** domain, which
  *consumes* the AKI stage as risk context.

Automatic diagnosis is forbidden — all outputs are advisory, physician-owned (VIS-C-01, VIS-C-08), and recorded
to the prontuário at NGS Level 2 (VIS-C-07). Every alert is versioned and auditable (VIS-C-13).

**Severity scale.** This domain uses **only** `normal | watch | urgent | critical`. The legacy alert-catalog
CRIT/URG/WARN/INFO map is: **CRIT → critical, URG → urgent, WARN → watch, INFO → normal**. KDIGO severity
scales with the computed stage: **stage 1 → watch, stage 2 → urgent, stage 3 → critical** (aligned with catalog
AKI-001 WARN / AKI-002 URG / AKI-003 CRIT).

---

## 2. Typed, unit-checked inputs

Every input unit is the canonical from `_work/units/registry.yaml`. Weight-indexed urine output requires a
**validated `peso`** — SYS-09 / P0-08: the legacy weight-parse stripped the decimal separator
(`70,5 → 705 kg`), inflating weight ~10× and making `mL/kg/h` ~10× too small, silently **masking oliguria**.
`debito_urinario_horario` is never computed without a validated `peso`.

| Input (PT-BR param) | Quantity | Unit (canonical) | Source | Staleness max |
|---|---|---|---|---|
| `creatinina` | serum_creatinine | `mg/dL` | AMH Gold lab_result LOINC 2160-0 | PT24H |
| `creatinina_basal` | serum_creatinine | `mg/dL` | derived (baseline resolver, §3.1) | — |
| `debito_urinario_horario` | urine_output_rate_indexed | `mL/kg/h` | derived (rolling window, §3.2; requires `peso`) | PT6H |
| `debito_urinario` | urine_output_volume | `mL` | AMH Gold Observation LOINC 9187-6 / fluid-balance source rows | PT6H |
| `peso` | body_weight | `kg` | AMH Gold Observation LOINC 29463-7 | PT7D |
| `idade` | age | `years` | AMH Gold Patient (MPI) | PT30D |
| `balanco_hidrico` | fluid_balance | `mL` | hemodynamics domain (cumulative, signed) | PT6H |
| `terapia_renal_substitutiva` | dimensionless | `boolean` | AMH Gold Procedure / MedicationAdministration (RRT active) | PT24H |
| `vancomicina_ativa` | dimensionless | `boolean` | AMH Gold MedicationAdministration | PT24H |
| `aminoglicosideo_ativo` | dimensionless | `boolean` | AMH Gold MedicationAdministration | PT24H |
| `contraste_iodado` | dimensionless | `boolean` | AMH Gold Procedure (last 72 h) | PT72H |
| `aine_ativo` | dimensionless | `boolean` | AMH Gold MedicationAdministration | PT24H |
| `ieca_bra_ativo` | dimensionless | `boolean` | AMH Gold MedicationAdministration | PT24H |
| `hipovolemia` | dimensionless | `boolean` | derived (hemodynamics: net-negative balance / clinical volume depletion) | PT6H |

**Unit hazards carried from the audit (handled at the edge normalizer, never in clinical logic):**
- **Creatinine** — canonical `mg/dL` (mission law). `µmol/L → mg/dL ×0.0113`. All KDIGO cutoffs (≥0.3 rise,
  1.5/2.0/3.0× baseline, ≥4.0) and the SOFA renal bands are mg/dL. Validator bound 0–20 mg/dL
  (RULE-SINAIS-VITAIS-025 ADOPT).
- **Weight** — comma-decimal parse (`70,5 → 705 kg`) inflated `mL/kg/h` ~10× and masked oliguria
  (SYS-09; P0-08 / RULE-SEPSE-014). Every weight-indexed threshold requires a validated `peso`.
- **Urine-output windowing** — the legacy 07:00–07:00 nursing-day aggregators use a **month-agnostic
  `criado_em__day`** filter that breaks across month boundaries and an unsatisfiable second predicate that
  silently drops 00:00–07:00 rows (SYS-10; CON-0141; RULE-BALANCO-HIDRICO-006/008). v2 **replaces** the
  nursing-day window with KDIGO's clinically-defined **rolling 6 h / 12 h / 24 h** windows recomputed from
  source rows (§3.2), never a mutable running total (CON-0145).
- **µmol/L back-conversion** — the MDRD baseline back-calculation returns `mg/dL` directly; never mix SI units
  mid-computation.

All units required by this domain **exist** in `_work/units/registry.yaml`; **no new unit is requested**
(see Open Question 4 re: the `debito_urinario_horario` LOINC binding).

---

## 3. KDIGO staging engine

Severity uses **only** `normal | watch | urgent | critical`. Logic below is the reference-anchored recommended
default; RATIFY-dependent legacy behaviour is designed to the KDIGO reference and flagged.

### 3.1 Baseline-creatinine resolver (documented hierarchy)

KDIGO staging is a **change** detector — it needs a reference baseline. The vision/catalog baseline
("menor valor 3 meses / admissão", AKI-001) is generalized to the standard KDIGO-recommended hierarchy
(KDIGO 2012 §2.2.1 / Appendix; ADQI):

```
creatinina_basal :=
  1. known_baseline    — the LOWEST creatinina in the pre-admission window [7 d … 365 d before admission].
                         Preferred: a documented stable outpatient value. (catalog AKI-001: "menor valor 3 meses")
  2. else min_7d       — the LOWEST creatinina in the rolling prior 7 days (KDIGO reference-change window).
  3. else mdrd_backcalc — solve the 4-variable MDRD equation for creatinine assuming a baseline
                         eGFR = 75 mL/min/1.73 m^2 (KDIGO 2012 recommended surrogate when no prior SCr exists);
                         requires idade + sex. FLAGGED lower-confidence: back-calculated baselines
                         systematically over-diagnose AKI in patients with true CKD -> stage carries a
                         `baseline_source: mdrd_estimated` provenance field, and the alert text says so.
```

**Rationale.** Options 1–2 are the KDIGO-preferred measured baselines; option 3 is the KDIGO-sanctioned
fallback but is the weakest (it assumes normal premorbid function). Surfacing `baseline_source` is what keeps
this advisory and auditable (VIS-C-13) and lets the physician discount an MDRD-estimated stage in a known-CKD
patient. **The choice of pre-admission lookback bound (90 d vs 365 d) and whether MDRD-estimated baselines may
fire a critical alert are pending `RAT-AKI-01`** (§6).

### 3.2 Urine-output rolling-window engine (replaces the 07:00–07:00 nursing day)

KDIGO defines oliguria over **rolling** windows measured back from *now*, not over a fixed nursing shift.
The legacy `balanco-hidrico` urine total (RULE-BALANCO-HIDRICO-008, P1 → RATIFY) computed diuresis over the
buggy 07:00–07:00 window. **We ADAPT the intent (sum urine output over a clinical window, weight-index it) and
fix the mechanism**: recompute `debito_urinario_horario` from source `saida` rows (tipo ∈ {diurese_espontanea,
diurese_sonda}) over trailing **rolling** windows, recomputed on every new reading (CON-0145 recompute-from-source,
CON-0141 no month-agnostic filter):

```
debito_urinario_horario(W) := ( sum of urine-output volume (mL) over trailing window W )
                              / ( peso (kg) * W_hours )              # requires a validated peso (SYS-09)

anuria(W) := total urine-output volume over trailing window W ~= 0 mL
```

```
stage_uo :=
  3 if  debito_urinario_horario(rolling 24h) < 0.3 mL/kg/h
        OR anuria(rolling 12h)                                   # KDIGO st.3 UO; catalog AKI-003
  2 if  debito_urinario_horario(rolling 12h) < 0.5 mL/kg/h       # KDIGO st.2 UO; catalog AKI-002
  1 if  debito_urinario_horario(rolling 6h)  < 0.5 mL/kg/h       # KDIGO st.1 UO; catalog AKI-001
  0 otherwise
```

The 07:00–07:00 nursing-day boundary is an **institutional convention with no KDIGO basis** (CON-0147,
CLU-BALANCO-HIDRICO-C-07) — its ratification (`RAT-BALANCO-HIDRICO-01/03/05`) governs the *fluid-balance
reporting* surface but **does not block AKI staging**, because KDIGO's rolling windows are guideline-defined and
supersede the shift convention for this purpose (a vision-mandated mechanism replacing an unanchored one).

### 3.3 Creatinine staging

```
delta_cr_48h := creatinina - min(creatinina over trailing rolling 48h)   # KDIGO acute-rise window

stage_cr :=
  3 if  creatinina >= 3.0 * creatinina_basal                                   # KDIGO st.3
        OR ( creatinina >= 4.0 mg/dL AND delta_cr_48h >= 0.5 mg/dL )           # catalog AKI-003 / vision VIS-3.2-04
        OR terapia_renal_substitutiva                                          # RRT initiation = st.3
  2 if  creatinina >= 2.0 * creatinina_basal                                   # KDIGO st.2 (catalog AKI-002)
  1 if  delta_cr_48h >= 0.3 mg/dL                                              # KDIGO st.1 absolute rise
        OR creatinina >= 1.5 * creatinina_basal (within rolling 7d)            # KDIGO st.1 relative rise
  0 otherwise
```

**Corrections & notes.** The SOFA renal sub-score (RULE-CLINICAL-SCORING-007, P0-03 → RATIFY) has a dead gap at
`(4.9, 5.0]` from a strict `>5` and a mis-widened `2.0–4.0` band; those are SOFA defects, **not** ported here —
KDIGO staging is multiplicative-vs-baseline, not the SOFA absolute bands. The vision/catalog "≥4.0 mg/dL with
acute increase ≥0.5" qualifier is adopted verbatim (VIS-3.2-04 / AKI-003); note that KDIGO 2012's own primary
text qualifies the ≥4.0 stage-3 by *any* AKI-defining rise (≥0.3/48 h or ≥1.5×/7 d) rather than ≥0.5 — recorded
as **Open Question 2** (the ≥0.5 is the AKIN/RIFLE legacy value the product carried).

### 3.4 Composite stage & the two staging alerts

```
kdigo_stage := max(stage_cr, stage_uo)     # KDIGO: the WORST of the two criteria (analogous to CON-0111,
                                           # SOFA-renal-is-max-not-sum; never sum the two axes)
```

- **`ALERT-AKI-KDIGO-STAGE-01`** — fires when `kdigo_stage >= 1`, with **severity scaling by stage**
  (1→watch, 2→urgent, 3→critical). One rich alert replaces catalog AKI-001/002/003; it carries `kdigo_stage`,
  which criterion drove it (`creatinine` vs `urine_output`), and `baseline_source` as fields. This consolidation
  is deliberate alarm-fatigue hygiene (fleet PPV ≥0.60, ignored ≤10 %, VIS-7.1-02/04): three near-duplicate
  stage alerts on the same patient become one escalating alert.
- **`ALERT-AKI-PROGRESSION-02`** — fires on a stage increase in a rolling 24 h window (catalog AKI-004):

```
progression := kdigo_stage_now > kdigo_stage_24h_ago AND kdigo_stage_24h_ago is not null
severity     := urgent  (critical if kdigo_stage_now == 3)     # a worsening trajectory outranks a static stage
```

### 3.5 Additive nephrotoxicity — `ALERT-AKI-NEPHROTOXIN-03` (watch)

Detects nephrotoxic exposure **with an early renal signal**, below KDIGO stage 1, so the offending agent can be
withdrawn while injury is reversible (catalog AKI-005; vision VIS-3.2-06). Nephrotoxin drug/exposure classes are
carried from the antimicrobial-stewardship renal-adjustment catalog (RULE-ANTIMICROBIANO-003 ADAPT):

```
rising_cr := creatinina > creatinina_basal + 0.2 mg/dL        # sub-stage-1 upward trend (catalog AKI-005)

nephrotoxic_combo :=
      ( vancomicina_ativa AND aminoglicosideo_ativo )
   OR ( vancomicina_ativa AND contraste_iodado )              # within 72 h
   OR ( aminoglicosideo_ativo AND aine_ativo )
   OR ( ieca_bra_ativo AND hipovolemia )                      # ACEi/ARB + volume depletion

fire := rising_cr AND nephrotoxic_combo
severity := watch
```

The concrete nephrotoxin drug list (vancomycin, aminoglycosides, iodinated contrast, NSAIDs, ACEi/ARB) is a
**facility formulary** — its exact membership and any additions (amphotericin B, calcineurin inhibitors, high-dose
acyclovir) are **pending `RAT-AKI-02`** (a formulary-vocabulary ruling analogous to the balanco-hidrico drug-list
RATIFYs, RAT-BALANCO-HIDRICO-18/19).

---

## 4. Evidence citations for every threshold

| Threshold | Value | Evidence (guideline/paper) | Legacy rule(s) & disposition |
|---|---|---|---|
| Baseline resolver | known → 7 d min → MDRD (eGFR 75) | KDIGO 2012 §2.2.1 / Appendix; ADQI | catalog AKI-001 ("menor valor 3 meses"); pending RAT-AKI-01 |
| Stage 1 — absolute rise | ΔCr ≥ 0.3 mg/dL in 48 h | KDIGO 2012 (26.5 µmol/L) | catalog AKI-001; vision VIS-3.2-02 |
| Stage 1 — relative rise | Cr ≥ 1.5× baseline (7 d) | KDIGO 2012 | catalog AKI-001; vision VIS-3.2-02 |
| Stage 1 — urine output | < 0.5 mL/kg/h for 6 h | KDIGO 2012 | RULE-BALANCO-HIDRICO-008 (window ADAPT); catalog AKI-001 |
| Stage 2 — relative rise | Cr ≥ 2.0× baseline | KDIGO 2012 | catalog AKI-002; vision VIS-3.2-03 |
| Stage 2 — urine output | < 0.5 mL/kg/h for 12 h | KDIGO 2012 | RULE-BALANCO-HIDRICO-008 (ADAPT); catalog AKI-002 |
| Stage 3 — relative rise | Cr ≥ 3.0× baseline | KDIGO 2012 | catalog AKI-003; vision VIS-3.2-04 |
| Stage 3 — absolute | Cr ≥ 4.0 mg/dL + acute ↑ ≥ 0.5 mg/dL | KDIGO 2012; AKIN (≥0.5 qualifier) | catalog AKI-003; vision VIS-3.2-04 (Open Q2) |
| Stage 3 — urine output | < 0.3 mL/kg/h for 24 h OR anuria ≥ 12 h | KDIGO 2012 | RULE-BALANCO-HIDRICO-008 (ADAPT); catalog AKI-003 |
| Stage 3 — RRT | initiation of renal replacement therapy | KDIGO 2012 | catalog AKI-003 |
| Composite stage | max(stage_cr, stage_uo) | KDIGO 2012 (worst criterion) | CON-0111 (SOFA-renal-is-max analogue) |
| Progression | stage↑ within rolling 24 h | KDIGO 2012 (staging is dynamic) | catalog AKI-004 |
| Nephrotoxin rising Cr | Cr > baseline + 0.2 mg/dL | catalog AKI-005 | RULE-ANTIMICROBIANO-003 ADAPT |
| Nephrotoxin combos | vanco+aminoglycoside / vanco+contrast(72h) / aminoglycoside+NSAID / ACEi-ARB+hypovolemia | KDIGO Drug-Induced AKI 2023; Rybak 2020 (AJHP, vancomycin); vision AIN Consensus 2020 | catalog AKI-005; RULE-ANTIMICROBIANO-003 ADAPT |
| Creatinine plausibility bound | 0–20 mg/dL inclusive | (validation) | RULE-SINAIS-VITAIS-025 ADOPT |
| Urine-output aggregation | sum of source `saida` rows, recomputed | Malbrain 2018 (I&O); ADQI | RULE-BALANCO-HIDRICO-001/003 ADOPT; -014/-038 ADAPT (recompute-from-source) |

---

## 5. Interactions with other domains

- **Sepsis ↔ AKI** (vision VIS-4-03: "sepse é #1 causa de AKI"; correlation-engine correlation #1). This domain
  **emits** `aki.stage.detected` (with stage + criterion) — the sepsis domain and correlation engine consume it
  for its renal organ-dysfunction input and the Sepsis+AKI correlation. Reciprocally, this domain **is the source**
  of `debito_urinario_horario` and `creatinina` that the sepsis domain declares it consumes from `aki`
  (sepsis.md §5); the broken sepsis oliguria criterion (RULE-SEPSE-014, P0-08 → RATIFY) is **superseded** by this
  domain's KDIGO UO engine. This domain **consumes** `sepsis.organ_dysfunction.detected` to raise pre-test AKI
  suspicion / prioritize (sepsis-associated AKI is the dominant ICU AKI etiology).
- **Hemodynamics ↔ AKI.** The fluid-balance intake/output ledger, cumulative balance, and volume-status flag
  live in the hemodynamics domain (RULE-BALANCO-HIDRICO-001/003 ADOPT; -014/015/038/039 ADAPT). This domain
  **consumes** `balanco_hidrico` (signed cumulative) and the derived `hipovolemia` flag for the ACEi/ARB
  nephrotoxin branch, and reuses the same recompute-from-source `saida` rows for the UO engine. AKI does **not**
  compute the fluid ledger; it re-aggregates urine `saida` into rolling KDIGO windows.
- **Clinical-scoring ↔ AKI.** The SOFA **renal sub-score** (RULE-CLINICAL-SCORING-007, RATIFY) shares the
  `creatinina` and `debito_urinario` inputs but is a *score component*, not a *stage* — kept separate. Both take
  the **max** of the creatinine and urine axes (CON-0111); this domain does not emit a SOFA point.
- **Pharmaco-interaction ↔ AKI (boundary drawn).** Vision §3.7 / DDX-003 "Nefrotoxicidade aditiva" alerts on a
  drug **combination** *before any renal marker moves*; **AKI-NEPHROTOXIN-03 requires a rising renal marker**
  (`rising_cr`). The pharmaco domain owns the pre-exposure combination warning; this domain owns the
  exposure-**with**-early-injury signal. The dedup boundary is the `rising_cr` gate — without it, this alert does
  not fire, preventing a duplicate of DDX-003.
- **Electrolytes ← AKI.** `aki.stage.detected` is consumed by the electrolytes domain as risk context for
  hyperkalemia (vision §3.6) — AKI is a leading driver of severe hyperkalemia.

---

## 6. RATIFY design points (designed to recommended default; committee decides)

Per CONTRACTS §Precedence and the escalations brief, **no P0/P1/UNVERIFIABLE rule is silently resolved.** Each
below is built to a reference-anchored *recommended default* and flagged pending the named RAT anchor.

| RAT anchor | Dispute | Legacy behaviour | **Recommended default (reference-anchored)** |
|---|---|---|---|
| **RAT-AKI-01** (baseline resolver) | Pre-admission lookback bound; may an MDRD-estimated baseline fire critical? | catalog AKI-001 says "menor valor 3 meses/admissão"; no MDRD fallback defined. | **known(7 d–365 d) → 7 d-min → MDRD(eGFR 75)** with `baseline_source` provenance; MDRD-estimated stages surfaced but flagged, committee decides the lookback bound and whether MDRD may escalate to critical. |
| **RAT-AKI-02** (nephrotoxin formulary) | Exact nephrotoxic-drug list membership | AKI-005 lists vanco/aminoglycoside/NSAID/contrast/ACEi-ARB; RULE-ANTIMICROBIANO-003 dose tables are external S3 PNGs, not versioned. | **The 5 vision classes as the default set**; migrate to a versioned inline formulary; additions (ampho B, calcineurin inhibitors, acyclovir) pending committee (analogous to RAT-BALANCO-HIDRICO-18/19). |
| **RAT-BALANCO-HIDRICO-03/05** (window, P1) | 07:00–07:00 nursing-day window has a month-agnostic `__day` bug (CON-0141) | RULE-BALANCO-HIDRICO-006/008 drop 00:00–07:00 rows, break across months. | **AKI uses KDIGO rolling 6/12/24 h windows** (guideline-anchored), *independent* of the nursing-day ratification; that RAT governs only fluid-balance *reporting*, not AKI staging. |
| **RAT-SEPSE-08 / P0-08** (RULE-SEPSE-014) | Sepsis oliguria criterion: weight-parse ~10× + always-False DRC gate | Legacy criterion effectively never fires. | **Superseded** by this domain's KDIGO UO engine with a validated `peso`; sepsis consumes the AKI UO output, does not re-implement oliguria. |
| **RAT-CLINICAL-SCORING-04 / P0-03** (RULE-CLINICAL-SCORING-007) | SOFA renal band gap `(4.9, 5.0]` + `2.0–4.0` mis-widening | SOFA renal undercounts at the top of the scale. | Owned by clinical-scoring (fix to `≥5.0`, `2.0–3.4`, **max** of Cr/UO axes); **not** ported into KDIGO staging, which is multiplicative-vs-baseline. |

---

## 7. Open questions

1. **Δ-baseline lookback mechanics** — the vision (open question) does not name the prior-value timestamp source
   for `delta_cr_48h` or the pre-admission baseline lookback. Design assumes the analyte's own trailing rolling
   48 h minimum (acute rise) and a 7 d–365 d pre-admission minimum (baseline); confirm the exact field mechanics
   with the data-model guild.
2. **Stage-3 ≥4.0 mg/dL qualifier** — vision VIS-3.2-04 / catalog AKI-003 require an "acute increase ≥0.5 mg/dL"
   (an AKIN/RIFLE value); KDIGO 2012's own text qualifies the ≥4.0 stage-3 by *any* AKI-defining rise (≥0.3/48 h
   or ≥1.5×/7 d). Designed to the product's ≥0.5; committee to confirm.
3. **`debito_urinario_horario` data availability** — catalog DATA-AVAIL-04 rates hourly urine output *Média*
   (fluid balance rarely automated). The UO criteria degrade to "creatinine-only staging (insufficient UO data)"
   when no timed `saida` rows exist in the window; the staging alert must not silently down-stage on missing UO.
4. **Urine-output LOINC binding** — catalog AKI-001 cites LOINC 9187-6 for `débito urinário`; the registry maps
   `debito_urinario` (mL absolute) and `debito_urinario_horario` (mL/kg/h derived). Confirm the AMH Gold
   Observation coding for timed urine volume vs the derived rate.

---

```yaml domain-inputs
domain: aki
inputs:
  - {name: creatinina, type: quantity, unit: "mg/dL", source: "AMH Gold lab_result LOINC 2160-0"}
  - {name: creatinina_basal, type: quantity, unit: "mg/dL", source: "derived (baseline resolver: known > 7d-min > MDRD)"}
  - {name: debito_urinario_horario, type: quantity, unit: "mL/kg/h", source: "derived (rolling 6/12/24h window; requires validated peso)"}
  - {name: debito_urinario, type: quantity, unit: "mL", source: "AMH Gold Observation LOINC 9187-6 / fluid-balance saida rows"}
  - {name: peso, type: quantity, unit: "kg", source: "AMH Gold Observation LOINC 29463-7"}
  - {name: idade, type: quantity, unit: "years", source: "AMH Gold Patient (MPI)"}
  - {name: balanco_hidrico, type: quantity, unit: "mL", source: "hemodynamics domain (cumulative signed)"}
  - {name: terapia_renal_substitutiva, type: boolean, unit: "boolean", source: "AMH Gold Procedure / MedicationAdministration (RRT active)"}
  - {name: vancomicina_ativa, type: boolean, unit: "boolean", source: "AMH Gold MedicationAdministration"}
  - {name: aminoglicosideo_ativo, type: boolean, unit: "boolean", source: "AMH Gold MedicationAdministration"}
  - {name: contraste_iodado, type: boolean, unit: "boolean", source: "AMH Gold Procedure (last 72h)"}
  - {name: aine_ativo, type: boolean, unit: "boolean", source: "AMH Gold MedicationAdministration"}
  - {name: ieca_bra_ativo, type: boolean, unit: "boolean", source: "AMH Gold MedicationAdministration"}
  - {name: hipovolemia, type: boolean, unit: "boolean", source: "hemodynamics domain (net-negative balance / volume depletion)"}
alerts:
  - ALERT-AKI-KDIGO-STAGE-01
  - ALERT-AKI-PROGRESSION-02
  - ALERT-AKI-NEPHROTOXIN-03
rule_refs:
  - RULE-CLINICAL-SCORING-007
  - RULE-SINAIS-VITAIS-025
  - RULE-BALANCO-HIDRICO-001
  - RULE-BALANCO-HIDRICO-003
  - RULE-BALANCO-HIDRICO-006
  - RULE-BALANCO-HIDRICO-008
  - RULE-BALANCO-HIDRICO-014
  - RULE-BALANCO-HIDRICO-015
  - RULE-BALANCO-HIDRICO-038
  - RULE-BALANCO-HIDRICO-039
  - RULE-SEPSE-014
  - RULE-ANTIMICROBIANO-003
interfaces:
  emits_events:
    - aki.stage.detected
    - aki.progression.detected
    - aki.nephrotoxin.exposure
  consumes:
    - {quantity: fluid_balance, unit: "mL", source: "hemodynamics domain"}
    - {quantity: urine_output_volume, unit: "mL", source: "hemodynamics domain (saida source rows)"}
    - {quantity: body_weight, unit: "kg", source: "AMH Gold Observation LOINC 29463-7"}
    - {quantity: serum_creatinine, unit: "mg/dL", source: "AMH Gold lab_result LOINC 2160-0"}
```
