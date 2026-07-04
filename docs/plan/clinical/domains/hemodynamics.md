# Hemodynamics Domain — IntensiCare v2 Clinical Specification

**Guild:** Clinical (hemodynamics domain designer) · **Vision ref:** §3.4 (Instabilidade Hemodinâmica, priority P4) ·
**Platform:** AMH Data Platform consumer (ADR-001) + local TimescaleDB invasive-monitor streaming ·
**Legacy cluster:** `estabilidade` (26 rules, 3 parallel shock pathways) with inputs from `equilibrio` (fluid balance)
and `antimicrobiano` (stewardship, delegated out).

This document reconciles the legacy's **three parallel shock pathways** — **v3 `estabilidade`** (criterio_1-13,
RULE-ESTABILIDADE-001..016), the **manual** pathway (C1-C6, RULE-ESTABILIDADE-017..023), and the
**`estabilizacao`/trilha2 v1** pathway (RULE-ESTABILIDADE-024/025) — plus the four catalog **HEMO-\*** alerts, into
**one** evidence-anchored design: a **shock-index screening layer**, a **lactate-clearance resuscitation-response**
alert, a **vasopressor escalation → refractory-shock ladder** (all dosing in canonical **mcg/kg/min** via the
unit-conversion service specified in [§4](#vasopressor-unit-conversion-service)), a **fluid-non-responsiveness**
overload guard, and a **vasoactive-medication × blood-pressure conflict** safety alert. Every threshold cites a
guideline/paper and/or a `RULE-ESTABILIDADE-*` catalog ID. Disputed logic and P0/P1 defects are designed to the
reference-anchored **recommended default** and marked **pending RAT-ESTABILIDADE-\***; the ratification committee decides.

> **This domain owns the audit's #1 finding.** SYS-02 / CON-0060 / RULE-ESTABILIDADE-016 vs -024: the legacy
> encoded the *same* vasopressor cutoff as a raw mL volume, an mL/h rate, mcg/kg/min, and mcg/kg/h — a 60× and an
> unconvertible drift on one number. The [vasopressor unit-conversion service](#vasopressor-unit-conversion-service)
> is the definitive engineering resolution: canonical `mcg/kg/min`, explicit `mL/h` conversion requiring drug
> concentration + patient weight, and a **loud reject** of anything unconvertible.

---

## 1. Clinical scope

**In scope.** Adult ICU (UTI) circulatory shock and hemodynamic instability, per Sepsis-3 (Singer 2016), the
Surviving Sepsis Campaign 2021 (Evans 2021), SEPSISPAM (Asfar 2014), ANDROMEDA-SHOCK (Hernandez 2019), and SCCM 2024
vasopressor guidance:

1. **Shock-index screening** — occult hypoperfusion via classic (HR/SBP) and modified (HR/MAP) shock index, corroborated by a perfusion marker.
2. **Lactate-clearance resuscitation targeting** — inadequate clearance (<10% at 2h) or persistence (>2 mmol/L at 6h) under active resuscitation. **Owned here** per orchestrator mandate; sepsis hands off via `sepsis.shock.detected`.
3. **Vasopressor escalation** — >50% norepinephrine-equivalent dose rise in 2h, or a second vasoactive agent.
4. **Refractory shock** — MAP <65 mmHg sustained >30 min on maximal (norepinephrine-equivalent >1.0 mcg/kg/min) vasopressor.
5. **Fluid non-responsiveness / overload risk** — dynamic indices (PPV/SVV) or a fluid-challenge fallback with a positive 24h balance.
6. **Vasoactive-medication × blood-pressure conflict** — scheduled antihypertensive co-existing with hypotension/vasopressor, or uncontrolled hypertension off any pressor.

**Out of scope / delegated.** Definitive **sepsis screening** (SIRS/qSOFA, hour-1 bundle) → **sepsis** domain (this
domain consumes `sepsis.shock.detected`); **AKI** staging and the disputed **fluid-balance** sign/window
(RULE-ESTABILIDADE-001, RATIFY) → **aki/equilibrio**; **SOFA cardiovascular** sub-score computation → **clinical-scoring**
(this domain *provides* it the canonical `dose_vasopressor`); **bicarbonate stewardship** (RULE-ESTABILIDADE-011,
ADOPT-CORRECTED) → **electrolyte** domain; **antimicrobial stewardship** (antimicrobiano cluster) → **pharmaco**.
Automatic diagnosis is forbidden — all outputs are advisory, physician-owned (VIS-C-01, VIS-C-08), recorded to the
prontuário at NGS Level 2 (VIS-C-07).

**Reconciliation summary (three pathways → one design).** The three pathways overlap in intent but disagree on
thresholds and, critically, **units** (nora in mL/h in v3, mcg/kg/min in RULE-016, mcg/kg/h in RULE-024 for the same
`>0.5` cutoff — CLU-ESTABILIDADE-05). Of v3's 13 criteria, only 7/10/12/13 ever feed an alert; criterio_1-6/8/9/11 are
**dead code** (CLU-ESTABILIDADE-02, CON-0162 forbids porting them as live behaviour without re-wiring). We therefore
**do not port any pathway verbatim**. The v2 design keeps the VERIFIED clinical concepts (shock index, hypoperfusion,
vasopressor escalation), rebuilds them on published anchors, routes every unit through the conversion service, and
sends the unconvertible-facade and institutional-list disputes to RATIFY (§6). The duplicate `estabilizacao`/trilha2
tiering shell (RULE-ESTABILIDADE-025) is **RETIRED** (CLU-ESTABILIDADE-19) rather than carried as a third parallel
implementation.

---

## 2. Typed, unit-checked inputs

Every input unit is the canonical from `_work/units/registry.yaml`. **Vasopressor dosing is `mcg/kg/min` only**
(mission law; SYS-02/CON-0060) — `mL/h` is an EDGE input that MUST pass through
[§4](#vasopressor-unit-conversion-service) first. **Lactate is `mmol/L` only** (SYS-03). Weight-indexed dosing
requires a validated `peso` (SYS-09: legacy weight-parse inflated weight ~10×).

| Input (PT-BR param) | Quantity | Unit (canonical) | Source | Staleness max |
|---|---|---|---|---|
| `frequencia_cardiaca` | heart_rate | `bpm` | local TimescaleDB (invasive monitor) / Observation LOINC 8867-4 | PT15M |
| `pressao_arterial_sistolica` | systolic_blood_pressure | `mmHg` | local TimescaleDB (arterial line) / Observation LOINC 8480-6 | PT15M |
| `pressao_arterial_diastolica` | diastolic_blood_pressure | `mmHg` | local TimescaleDB / Observation LOINC 8462-4 | PT6H |
| `pressao_arterial_media` | mean_arterial_pressure | `mmHg` | local TimescaleDB (arterial line) / Observation LOINC 8478-0 | PT15M |
| `indice_choque` | shock_index | `ratio` | derived = HR/SBP (this domain) | PT15M |
| `lactato_arterial` | lactate | `mmol/L` | AMH Gold lab_result LOINC 2524-7 | PT4H |
| `tempo_enchimento_capilar` | capillary_refill_time | `s` | AMH Gold Observation (TEC bedside) | PT6H |
| `dose_vasopressor` | weight_indexed_vasopressor_rate | `mcg/kg/min` | **conversion service** (§4) from MedicationAdministration | PT1H |
| `dose_vasopressina` | fixed_rate_vasopressin_dose | `U/min` | conversion service (§4; fixed-rate, NOT weight-indexed) | PT1H |
| `dose_adrenalina` / `dose_dobutamina` | weight_indexed_vasopressor_rate | `mcg/kg/min` | conversion service (§4) | PT1H |
| `taxa_infusao` | volumetric_infusion_rate | `mL/h` | MedicationAdministration dose.rate (**EDGE only**) | PT1H |
| `concentracao_farmaco` | drug_concentration | `mg/mL` | MedicationAdministration / medication master | PT7D |
| `peso` | body_weight | `kg` | AMH Gold Observation LOINC 29463-7 (validated) | PT7D |
| `ppv` | pulse_pressure_variation | `percent` | local TimescaleDB (advanced hemodynamic monitor) | PT1H |
| `svv` | stroke_volume_variation | `percent` | local TimescaleDB (advanced hemodynamic monitor) | PT1H |
| `delta_sv_pos_fluid` | stroke_volume_change | `percent` | derived (post fluid challenge) | PT2H |
| `balanco_hidrico_24h` | fluid_balance | `mL` | aki/equilibrio (recomputed from source rows) | PT6H |
| `hidrocortisona_ativa` | (presence) | `boolean` | AMH Gold MedicationAdministration | PT6H |
| `antihipertensivo_agendado_ativo` | (presence) | `boolean` | AMH Gold MedicationRequest (full class list) | PT12H |

**Unit hazards carried from the audit (all handled at the edge / conversion service, never in clinical logic):**
- **Vasopressor** — canonical `mcg/kg/min`; `mL/h` is a pump rate, **not** a dose, and is **not convertible without
  concentration + weight** (SYS-C-04/CON-0060). `mcg/kg/h → mcg/kg/min` is a fixed `/60` (SYS-02 60× drift,
  RULE-016 vs -024). See [§4](#vasopressor-unit-conversion-service). A dosing predicate consuming `mL/h` directly is a **build-time error**.
- **Lactate** — `mg/dL → mmol/L ×0.111` (SYS-03; legacy RULE-ESTABILIDADE-005/020 disagreed mg/dL vs mmol/L ~9×). A bare lactate number with no unit is a build-time error.
- **Weight** — comma-decimal parse (`70,5 → 705 kg`, SYS-09) inflates every weight-indexed dose ~10×. The conversion service refuses to run on an unvalidated `peso`.
- **Vasopressin** — `U/min`, a **fixed rate**, NOT weight-indexed and NOT expressible in mcg/kg/min; kept as a separate parameter so it is never coerced.

> **Open unit note.** `ppv`, `svv`, and `stroke_volume_change` are consumed in the canonical `percent` primitive
> (which exists in the registry), but they are **not yet named parameters** in `_work/units/registry.yaml`. Their unit
> is unambiguous (`percent`); this is flagged as an open question (§7) for the units engineer to add the named
> parameters. No non-registry unit is used.

---

## 3. Trigger / staging logic

Severity uses **only** `normal | watch | urgent | critical`. Each criterion cites its legacy rule and disposition;
RATIFY criteria are *designed to the recommended default* and flagged. Alert IDs and full test vectors are in
`_work/alerts/hemodynamics.yaml`.

### 3.1 Shock index — `ALERT-HEMO-SHOCK-INDEX-01` (severity: watch)

```
shock_index_positive :=
    ( indice_choque > 0.9                      # classic SI = HR/SBP; Rady 1994
      OR frequencia_cardiaca / pressao_arterial_media > 1.3 )   # modified SI; Liu 2012
    sustained > PT15M
    AND ( lactato_arterial > 2 mmol/L OR tempo_enchimento_capilar > 3 s )   # perfusion corroborator
```

**Corrections / decisions.** Legacy RULE-ESTABILIDADE-002 (ADAPT, VERIFIED but dead code) used the more *sensitive*
`SI>0.7 OR MSI>0.9` cutoffs; v2 adopts the vision/catalog-anchored `SI>0.9 / MSI>1.3` for specificity, and adds the
mandatory **perfusion corroborator** (RULE-ESTABILIDADE-003, ADAPT — lactate ≥2 / CRT >3 s, ANDROMEDA-SHOCK) so an
isolated tachycardia does not fire. PT-BR display `'Indice de choque positivo'` preserved verbatim (CLU-ESTABILIDADE-20).
One watch alert covers vision VIS-3.4-02 (classic) + VIS-3.4-03 (modified).

### 3.2 Lactate clearance — `ALERT-HEMO-LACTATE-CLEARANCE-02` (severity: critical)

```
lactate_clearance_inadequate :=
    active_resuscitation                                 # fluid bolus OR vasopressor>0 OR sepsis.shock.detected in PT6H
    AND lactato_inicial >= 2 mmol/L
    AND ( clearance_lactato_2h < 10 percent              # (inicial - 2h)/inicial*100; Jones 2010 JAMA
          OR lactato_6h > 2 mmol/L )                     # persistence after resuscitation; SSC-2021
```

Owned here per the orchestrator mandate. `active_resuscitation` is the PPV gate (fires only when the clearance
question is clinically live). Lactate is `mmol/L` only (SYS-03). Delegated in from sepsis `ALERT-SEPSIS-SHOCK-03`,
which emits `sepsis.shock.detected` and hands off resuscitation targeting.

### 3.3 Vasopressor escalation — `ALERT-HEMO-VASO-ESCALATION-03` (severity: urgent)

```
vasopressor_escalating :=
    dose_vasopressor > 0 mcg/kg/min
    AND ( dose_vasopressor > 1.5 * dose_vasopressor_2h_atras      # >50% increase in PT2H; SCCM 2024 / SSC 2021
          OR second_vasopressor_started_2h )                      # vasopressina/adrenalina/dobutamina added while NE active
```

**All doses are canonical `mcg/kg/min` from the [conversion service](#vasopressor-unit-conversion-service).** The
`>50%` / second-agent **trend** logic is SCCM-2024-anchored and **unit-safe** — it compares two canonical rates, so it
is immune to the SYS-02 drift. Draws on the vasopressor-ladder tiering shell (RULE-ESTABILIDADE-014, ADOPT — see
[§3.7](#shock-alert-tiering)), the initiation-window lookback (RULE-ESTABILIDADE-018, ADOPT — see
[§3.8](#vasopressor-initiation-window)), and the start-time default (RULE-ESTABILIDADE-026, ADOPT — see
[§3.9](#vasopressor-start-time-default)). The disputed **absolute** ladder cutoffs (`>0.5`, `>1.5 mcg/kg/min`, the
FC>130 bpm dobutamine-stop) are **pending RAT-ESTABILIDADE-08** (P0, RULE-ESTABILIDADE-016) and are **not** used as a
firing threshold here.

<a id="high-dose-noradrenaline-without-adjuncts"></a>
**High-dose noradrenaline without adjuncts (RULE-ESTABILIDADE-019, ADOPT-CORRECTED).** The manual pathway flagged
noradrenaline volume strict `>21 mL` without vasopressin/hydrocortisone; the governing `_REGRAS` spec says inclusive
`>=21 mL`. v2 adopts the **reference-correct inclusive boundary** but re-expresses it through the conversion service
as a `mcg/kg/min` adjunct-recommendation rung (add vasopressin + hydrocortisone), surfaced as an **enrichment** on
VASO-ESCALATION-03 and REFRACTORY-SHOCK-04 rather than a separate alert (ESC-P2-080).

### 3.4 Refractory shock — `ALERT-HEMO-REFRACTORY-SHOCK-04` (severity: critical)

```
refractory_shock :=
    pressao_arterial_media < 65 mmHg sustained > PT30M
    AND dose_vasopressor > 1.0 mcg/kg/min                # norepinephrine-equivalent, canonical
```

The `>1.0 mcg/kg/min` "maximal vasopressor" cutoff is the reference-anchored **recommended default** (vision
VIS-3.4-06; SEPSISPAM Asfar 2014) **pending RAT-ESTABILIDADE-08** (the disputed mcg/kg/min ladder). Enrichment (does
not gate firing): flags absence of `dose_vasopressina` / `hidrocortisona_ativa` and recommends adjunct rescue
(RULE-ESTABILIDADE-019). PT-BR display
`'Noradrenalina >0,5mcg/kg/min, associar corticoide e vasopressina'` preserved verbatim (CLU-ESTABILIDADE-20).

### 3.5 Fluid non-responsiveness — `ALERT-HEMO-FLUID-NONRESPONSIVE-05` (severity: watch)

```
fluid_non_responsive :=
    ( ( ppv < 10 percent OR svv < 10 percent ) AND delta_sv_pos_fluid < 10 percent
      AND balanco_hidrico_24h > 3000 mL )
    OR ( fluid_challenge_realizado AND delta_map_pos_fluid < 5 mmHg
         AND delta_lactato_pos_fluid < 5 percent AND balanco_hidrico_24h > 3000 mL )   # fallback (no PPV/SVV)
```

Dynamic PPV/SVV is the reference standard (Marik 2013) but LOW availability (DATA-AVAIL-09), so a clinical
fluid-challenge fallback path is provided. `balanco_hidrico_24h` is **recomputed from source rows** (never a mutable
running total; avoids the SYS-10 `criado_em__day` month-agnostic window bug) and uses the **positive-gain sign only**
— the disputed legacy `-2000 mL` sign convention (RULE-ESTABILIDADE-001) is RATIFY (RAT-ESTABILIDADE-01) and is
**not** used here.

### 3.6 Vasoactive-medication × BP conflict — `ALERT-HEMO-ANTIHTN-CONFLICT-06` (severity: watch)

Folds three legacy medication-safety rules into one alert with a per-branch dedup key.

<a id="recurrent-hypotension-antihypertensive-conflict"></a>
**Branch A — recurrent-hypotension / antihypertensive conflict (RULE-ESTABILIDADE-012, ADAPT).**
```
deprescribe :=
    antihipertensivo_agendado_ativo
    AND ( recurrent_hypotension OR dose_vasopressor > 0 mcg/kg/min )
recurrent_hypotension := >=2 of last PT24H readings with
    ( pressao_arterial_sistolica < 90 mmHg OR pressao_arterial_diastolica < 60 mmHg )   # corrected AND->OR
```
The legacy ANDed `PAS<90` with `PAD<60` in the same record where the docstring said OR (ESC-P3-104); v2 corrects the
boolean logic. Shares the antihypertensive drug-list conflict semantics of the manual pathway
[§3.6-C5](#antihypertensive-adequate-pressure-conflict).

<a id="recurrent-hypertension-off-vasopressor"></a>
**Branch B — uncontrolled hypertension off vasopressor (RULE-ESTABILIDADE-013, ADAPT).**
```
uncontrolled_htn_off_pressor :=
    dose_vasopressor == 0 mcg/kg/min
    AND recurrent_hypertension
    AND NOT permissive_htn_indication                       # e.g. AVCi / I64 permissive-HTN window
recurrent_hypertension := >=2 of last PT24H readings with
    ( pressao_arterial_sistolica > 155 mmHg OR pressao_arterial_diastolica > 90 mmHg )   # corrected AND->OR
```
Three legacy bugs corrected (ESC-P3-105): (1) `PAS>155` ANDed with `PAD>90` where OR was documented; (2) an exact
`count()==2` replaced with "≥2 of the last readings"; (3) the `I64/AVCi` exclusion that filtered dict **KEYS not
values** (permanently vacuous) rebuilt to test the actual diagnosis, so the permissive-hypertension exclusion now
works.

<a id="antihypertensive-adequate-pressure-conflict"></a>
**Manual C5 — antihypertensive with adequate pressure/vasopressor (RULE-ESTABILIDADE-021, ADOPT).** The manual
pathway's generic conflict trigger (`noradrenaline present OR PAS>90` while an antihypertensive is scheduled) is
adopted as the semantic root of Branch A; no external cutoff, so plain ADOPT.

**Institutional disputes NOT ported.** The antihypertensive **drug-list completeness** (legacy checked 16 of 18 drugs,
omitting anlodipino/metoprolol — RULE-ESTABILIDADE-010, UNVERIFIABLE) and the **`noradrenaline == 50 mL` exact-equality**
manual C6 (implausible for a continuous infusion — RULE-ESTABILIDADE-022, UNVERIFIABLE) are **pending
RAT-ESTABILIDADE-06 / RAT-ESTABILIDADE-10** (CON-0164). The recommended default is the **full drug-class list** and a
**threshold (not equality)** comparison.

### 3.7 Shock-alert tiering — `shock-alert-tiering` {#shock-alert-tiering}

The three-tier VERMELHO/AMARELO/NEUTRO aggregation shell (RULE-ESTABILIDADE-014, ADOPT — byte-identical
`calcular_alerta`/`_v2`, code-verified) is the canonical mechanism that maps the v3 criteria to a severity. In v2 it
is re-expressed on the `normal|watch|urgent|critical` scale and driven only by the resolved feeder alerts above (the
dead criteria 1-6/8/9/11 are **not** wired in, CON-0162). VERMELHO→`critical`/`urgent`, AMARELO→`watch`, NEUTRO→`normal`.

<a id="manual-pathway-alert-tiering"></a>
**Manual-pathway tiering (RULE-ESTABILIDADE-023, ADAPT).** The manual count-to-color aggregator (`n≥3` VERMELHO,
`n>0` AMARELO) is carried, but its **payload/alert desync** is corrected: `criterio_6` counted toward the alert while
being invisible in `get_payload`'s `1..5` iteration, letting an unseen criterion silently drive the color. v2 renders
every counted criterion (no hidden driver).

### 3.8 Vasopressor initiation window — `vasopressor-initiation-window` {#vasopressor-initiation-window}

The "noradrenaline started in the last 24h" temporal lookback (RULE-ESTABILIDADE-018, ADOPT — purely structural,
no clinical anchor) is the initiation-window check feeding VASO-ESCALATION-03 and the manual pathway.

### 3.9 Vasopressor start-time default — `vasopressor-start-time-default` {#vasopressor-start-time-default}

Defaulting an unset noradrenaline/cardiac-arrest `horario_inicio` to save-time (RULE-ESTABILIDADE-026, ADOPT) underpins
the "started in last 24h" temporal criteria; adopted as the timing model's default.

---

## 4. Vasopressor unit-conversion service {#vasopressor-unit-conversion-service}

> **This section is the definitive resolution of the audit's #1 finding (SYS-02 / CON-0060 / SYS-C-04 / CON-0163).**
> The legacy encoded the *same* vasopressor cutoff four incompatible ways — raw mL volume, mL/h rate, mcg/kg/min, and
> mcg/kg/h — a 60× drift (RULE-ESTABILIDADE-016 `mcg/kg/min` vs -024 `mcg/kg/h`) and an unconvertible mL/h-vs-rate
> confusion (RULE-ESTABILIDADE-007/008/009 predicates in mL/h narrated by an -016 facade in mcg/kg/min).

**Canonical.** Every weight-indexed vasopressor/inotrope (norepinephrine, epinephrine, dopamine, dobutamine,
phenylephrine) is stored and compared **only** in `mcg/kg/min`. Vasopressin is stored **only** in `U/min` (fixed rate,
never weight-indexed, never coerced into mcg/kg/min).

**Conversion contract.**

| Edge input | To canonical | Rule |
|---|---|---|
| `mcg/kg/h` | `mcg/kg/min` | **fixed** `÷ 60` (both weight-indexed; kills the SYS-02 60× RULE-016-vs-024 drift) |
| `mg/kg/min` | `mcg/kg/min` | **fixed** `× 1000` |
| `mL/h` (`taxa_infusao`) | `mcg/kg/min` | **NOT a fixed factor** — requires `concentracao_farmaco` (mg/mL) **and** `peso` (kg): |
| `U/h` (vasopressin) | `U/min` | **fixed** `÷ 60` (fixed-rate, stays in U/min) |
| `gtt/min` | `mL/h` | drip-set dependent (macro 20 gtt/mL, micro 60 gtt/mL); resolve per device, then convert as mL/h |

**The mL/h → mcg/kg/min formula (the only correct path):**

```
dose_mcg_kg_min =
    ( taxa_infusao[mL/h] * concentracao_farmaco[mg/mL] * 1000[mcg/mg] )
    / ( peso[kg] * 60[min/h] )
```

*Dimensional check:* `(mL/h · mg/mL · mcg/mg) / (kg · min/h) = (mg/h · mcg/mg) / (kg·min/h) = mcg/h / (kg·min/h)
= mcg/(kg·min)`. ✓

*Worked example (the SYS-02 trap made safe):* norepinephrine 4 mg in 250 mL (`concentracao_farmaco = 0.016 mg/mL`),
running at `taxa_infusao = 10 mL/h`, patient `peso = 70 kg`:
`(10 · 0.016 · 1000) / (70 · 60) = 160 / 4200 = 0.038 mcg/kg/min`. The legacy "`>10 mL/h`" predicate would have
treated the same infusion as if `10` were a dose — it is **not**; the true dose depends entirely on concentration and
weight, which is exactly why a fixed factor is forbidden.

**Rejection rules (reject loudly, never guess).**
1. An `mL/h` rate with **missing `concentracao_farmaco`** OR **missing/invalid `peso`** → **REJECT**; emit
   `hemodynamics.vasopressor_dose.canonical` with `conversion_status: rejected_missing_inputs`. No dosing predicate
   may run on the unconverted value. A dosing alert that consumes `mL/h` directly is a **build-time error** in the
   alert-definition schema.
2. A `peso` that fails the SYS-09 decimal-separator validation (e.g. a `705 kg` parse from `70,5`) → **REJECT** the
   weight; do not convert. Every weight-indexed dose depends on a validated `peso`.
3. A vasopressin value presented in `mcg/kg/min` (category error) → **REJECT**; vasopressin is `U/min` only.
4. A drug whose infusion `concentracao_farmaco` cannot be resolved from the medication master → **REJECT** (do not
   assume a "standard" dilution silently); surface for pharmacy confirmation.

**Provenance emitted.** The service emits `hemodynamics.vasopressor_dose.canonical` carrying the canonical dose **and
its provenance** (`source_rate_mL_h`, `drug_concentration_mg_mL`, `body_weight_kg`, `conversion_status`) so every
dose is 100% auditable (VIS-C-13) and the SOFA cardiovascular sub-score (clinical-scoring, P0-02
RULE-CLINICAL-SCORING-005) and pharmaco consume one authoritative number. **The clinical *cutoffs* that operate on the
canonical dose (>0.5, >1.0, >1.5 mcg/kg/min) remain a RATIFY decision (RAT-ESTABILIDADE-08); this service resolves the
*unit*, not the disputed *threshold*.**

---

## 5. Evidence citations for every threshold

| Threshold | Value | Evidence (guideline/paper) | Legacy rule(s) & disposition |
|---|---|---|---|
| Classic shock index | HR/SBP > 0.9 | Rady 1994 (Ann Emerg Med); Cannon 2011 | RULE-ESTABILIDADE-002 **ADAPT** (legacy >0.7, re-wired) |
| Modified shock index | HR/MAP > 1.3 | Liu 2012 (Crit Care) | RULE-ESTABILIDADE-002 ADAPT (legacy MSI>0.9) |
| Perfusion corroborator | lactate >2 mmol/L OR CRT >3 s | Singer 2016 (Sepsis-3); Hernandez 2019 (ANDROMEDA-SHOCK) | RULE-ESTABILIDADE-003 **ADAPT** (VERIFIED, re-wired) |
| Lactate clearance | <10% at 2h | Jones 2010 (JAMA); Jansen 2010 | — (design-new on ADOPT lactate; HEMO-002) |
| Lactate persistence | >2 mmol/L at 6h | Evans 2021 (SSC lactate-guided resuscitation) | RULE-ESTABILIDADE-020 **ADOPT-CORRECTED** (legacy ≥2.5 → >2) |
| Vasopressor escalation | dose +50% in 2h OR 2nd agent | SCCM 2024; Evans 2021 (SSC) | RULE-ESTABILIDADE-014/018/026 ADOPT |
| High-dose NE w/o adjuncts | NE ≥21 mL (→ mcg/kg/min via §4) + no vasopressin/HC | Evans 2021 (SSC vasopressin+HC) | RULE-ESTABILIDADE-019 **ADOPT-CORRECTED** (>21 → ≥21 mL) |
| Refractory-shock MAP | MAP < 65 mmHg > 30 min | Asfar 2014 (SEPSISPAM); Singer 2016 | RULE-ESTABILIDADE-016 → **RAT-ESTABILIDADE-08** (P0) |
| "Maximal" vasopressor | NE-equiv > 1.0 mcg/kg/min | vision VIS-3.4-06; SCCM 2024 | RULE-ESTABILIDADE-016 → **RAT-ESTABILIDADE-08** (recommended default) |
| Fluid non-responsiveness | PPV/SVV <10% + ΔSV <10% + BH 24h >3000 mL | Marik 2013; Monnet 2016 | — (HEMO-004; BH sign RULE-ESTABILIDADE-001 → RAT) |
| Fluid-challenge fallback | ΔMAP <5 mmHg + Δlactate <5% | Monnet 2016 | — (HEMO-004 alt path) |
| Recurrent hypotension | ≥2 readings SBP<90 OR DBP<60 mmHg | institutional (no external anchor) | RULE-ESTABILIDADE-012 **ADAPT** (AND→OR) |
| Recurrent hypertension | ≥2 readings SBP>155 OR DBP>90 mmHg | institutional | RULE-ESTABILIDADE-013 **ADAPT** (AND→OR, vacuous-exclusion fix) |
| Antihypertensive conflict | scheduled antihypertensive + adequate BP/pressor | institutional | RULE-ESTABILIDADE-021 ADOPT; RULE-010/022 → **RAT** |
| Vasopressor unit | mcg/kg/min (mL/h → §4; mcg/kg/h ÷60) | mission law CON-SEED-12/CON-0060 | RULE-ESTABILIDADE-016/024 → **RAT-ESTABILIDADE-08/11** |

---

## 6. RATIFY design points (designed to recommended default; committee decides)

Per CONTRACTS §Precedence and the escalations brief, **no P0/P1/UNVERIFIABLE rule is silently resolved.** Each below
is built to a reference-anchored *recommended default* and flagged pending the named RAT anchor.

| RAT anchor | Band | Dispute | **Recommended default (reference-anchored)** |
|---|---|---|---|
| **RAT-ESTABILIDADE-08** (RULE-ESTABILIDADE-016; also -007/-008/-009) | **P0** | Vasopressor **ladder unit/threshold**: facade `mcg/kg/min` (>0.5, >1.5) + FC>130 dobutamine-stop over v3 `mL/h` predicates — not interconvertible (CON-0060) | **Unit resolved by §4 (canonical mcg/kg/min).** Threshold recommended default: refractory `>1.0 mcg/kg/min` + MAP<65 (SEPSISPAM/SSC); committee ratifies the exact ladder cutoffs and the FC>130 rung. |
| **RAT-ESTABILIDADE-11** (RULE-ESTABILIDADE-024) | P1 | trilha2 labels the same `>0.5` cutoff `mcg/kg/H` vs -016 `mcg/kg/MIN` (60×); key gap skips criteria 8-9 | **Canonicalize to mcg/kg/min via §4** (`mcg/kg/h ÷ 60`); **retire the duplicate estabilizacao pathway** (RULE-ESTABILIDADE-025 RETIRE), do not carry a third dosing text. |
| **RAT-ESTABILIDADE-03** (RULE-ESTABILIDADE-007) | P1 | WIRED VERMELHO high-dose-NE-without-adjuncts fires on `mL/h` while facade asserts `mcg/kg/min` | Fire on canonical `mcg/kg/min` (via §4) with vasopressin/hydrocortisone absence; recommended adjunct rung on VASO-ESCALATION-03 / REFRACTORY-SHOCK-04. |
| **RAT-ESTABILIDADE-04** (RULE-ESTABILIDADE-008) | P1 | Refractory triple-therapy gate (`nora>70 mL/h AND vaso>5 mL/h`) narrated by an -016 `mcg/kg/min` facade | Canonicalize both to `mcg/kg/min`; committee ratifies the triple-therapy escalation thresholds. |
| **RAT-ESTABILIDADE-05** (RULE-ESTABILIDADE-009) | P1 | Dobutamine + high-NE predicate never checks the FC>130 bpm its facade displays | Ratify which condition governs (dose co-occurrence vs tachycardia); default = check **both** (dose AND FC>130) before firing the inotrope rung. |
| **RAT-ESTABILIDADE-02** (RULE-ESTABILIDADE-005) | P1 | Occult-shock criterion: docstring says **absence** of noradrenaline, code checks **presence** | Default = **absence** of vasopressor for "occult shock" ('Lactato >2mmol/L sem DVA e VM. Choque oculto?' preserved verbatim); committee confirms. |
| **RAT-ESTABILIDADE-07** (RULE-ESTABILIDADE-015) | P1 | Facade text (lactate>2, ScVO2<70, ΔPCO2>6, pH<7.15/BIC<16) asserts conditions the v3 predicates never test | Single source of truth = the **reference-correct predicate**; discard drifted facade text. Bicarbonate stewardship delegated to electrolyte (RULE-011 ADOPT-CORRECTED, pH≥7.15). |
| **RAT-ESTABILIDADE-01** (RULE-ESTABILIDADE-001) | P1 | Fluid-balance criterion: code inverts the −2000 mL sign to +2000, sums ALL history (not a 6h/4h window), swaps Ringer-bolus for a lactate test | FLUID-NONRESPONSIVE-05 uses the unambiguous **+3000 mL 24h gain** (recomputed from source rows); the −2000 mL negative-balance criterion is committee-decided. 'BH acumulado negativo em mais de 2000ml' preserved verbatim. |
| **RAT-ESTABILIDADE-06** (RULE-ESTABILIDADE-010) | UNVERIFIABLE | Antihypertensive-conflict drug list checks 16 of 18 drugs (omits anlodipino, metoprolol) | Default = **full drug-class list**; committee ratifies the institutional list (CON-0164). |
| **RAT-ESTABILIDADE-09** (RULE-ESTABILIDADE-017) | P1 | Manual C1 uses CRT strict `>5 s` vs ANDROMEDA-SHOCK `>3 s` (matches v3 RULE-003) | Default = **`>3 s`** (ANDROMEDA-SHOCK); the 3-5 s gap where hypoperfusion went unflagged is closed. |
| **RAT-ESTABILIDADE-10** (RULE-ESTABILIDADE-022) | UNVERIFIABLE | Manual C6 fires only when `noradrenaline == 50 mL` exactly (implausible for continuous infusion) | Default = a **threshold** (`≥`/`>`) comparison, canonicalized via §4; committee ratifies the intended cutoff (CON-0164). |

---

## 7. Interactions with other domains

- **Hemodynamics ↔ Sepsis** (vision §3.4; §3.1). Consumes `sepsis.shock.detected` (SHOCK-03 hands off lactate-clearance
  targeting + the vasopressor conversion). Emits `hemodynamics.shock.refractory` and `hemodynamics.lactate_clearance.inadequate`
  back to sepsis. Provides the canonical `dose_vasopressor` and `indice_choque` that sepsis consumes.
- **Hemodynamics + Respiratory** (vision VIS-4-03 correlation #2: "SDRA + choque"). `hemodynamics.shock.refractory` is
  consumed by the correlation engine alongside the respiratory ARDS-severity events.
- **Hemodynamics → Clinical-scoring** (P0-02, RULE-CLINICAL-SCORING-005). The conversion service ([§4](#vasopressor-unit-conversion-service))
  is the **sole source** of the canonical `mcg/kg/min` vasopressor rate the SOFA cardiovascular sub-score needs —
  fixing the legacy raw-mL-volume defect at the source.
- **Hemodynamics → Pharmaco** (drug/vasopressor dosing). `hemodynamics.vasopressor_dose.canonical` (incl. the
  `rejected_missing_inputs` variant) is the authoritative dose feed; pharmaco never re-derives from mL/h.
- **Hemodynamics ↔ AKI / Equilibrio.** Consumes `balanco_hidrico_24h` (recomputed) for FLUID-NONRESPONSIVE-05; emits
  `hemodynamics.fluid.non_responsive` for de-resuscitation stewardship. Hypotension (`hemodynamics.shock.refractory`)
  is a renal-perfusion input the aki domain may consume. The −2000 mL fluid-balance sign (RULE-ESTABILIDADE-001) is a
  shared RATIFY point (RAT-ESTABILIDADE-01).
- **Hemodynamics → Early-warning-scores.** Shock index (RULE-ESTABILIDADE-002) is shared cluster-wide
  (CLU-ESTABILIDADE-19); its computation is provided here and consumed by the early-warning-scores shock-index-with-
  vasopressor-absence criterion.
- **Governance / correlation.** The text-vs-predicate drift (RULE-ESTABILIDADE-015/016/024) and the institutional
  thresholds (RULE-010/022) feed the RATIFY queue; the correlation engine reasons over the emitted shock/lactate events.

---

## 8. Open questions

1. **PPV/SVV/stroke-volume parameters** are consumed in the canonical `percent` primitive (registry-valid) but are not
   yet **named parameters** in `_work/units/registry.yaml`. Requesting the units engineer add `pulse_pressure_variation`,
   `stroke_volume_variation`, and `stroke_volume` (mL) / `stroke_volume_change` (percent). No non-registry unit is used.
2. **Δ-baseline lookback** for `dose_vasopressor_2h_atras`, `clearance_lactato_2h`, and the post-fluid deltas — vision
   does not name the prior-value timestamp source (vision open question). Design assumes a 2h (vasopressor), 2h/6h
   (lactate) lookback against the same analyte/parameter's most-recent prior value; confirm the exact field mechanics
   with the data-model guild.
3. **Standard vasopressor concentrations** — the conversion service ([§4](#vasopressor-unit-conversion-service))
   rejects an unresolved `concentracao_farmaco` rather than assuming a house dilution. The medication master must
   carry per-drug infusion concentrations; the pharmacy/formulary owner should confirm coverage before build.
4. **Continuous-BP freshness path.** Shock-index / refractory-shock alerts assume the local TimescaleDB invasive-monitor
   stream (VIS-4.2-04 "contínuo"), which can meet the <30 s SLO (VIS-C-09); lactate (AMH Gold via Athena) is batch-bound
   (P95 <30 min, ADR001-F-02). Confirm the local streaming channel is provisioned for hemodynamics (ADR-001 Alternativa B).
5. All RATIFY anchors (§6) require a single canonical `RATIFICATION.md#rat-estabilidade-*` registry (per the shard
   dispositions) before build; the P0 RAT-ESTABILIDADE-08 (vasopressor ladder) gates any vasopressor **threshold**
   going live, though the **unit** is already resolved by §4.

---

```yaml domain-inputs
domain: hemodynamics
inputs:
  - {name: frequencia_cardiaca, type: quantity, unit: "bpm", source: "local TimescaleDB (invasive monitor) / AMH Gold Observation LOINC 8867-4"}
  - {name: pressao_arterial_sistolica, type: quantity, unit: "mmHg", source: "local TimescaleDB (arterial line) / AMH Gold Observation LOINC 8480-6"}
  - {name: pressao_arterial_diastolica, type: quantity, unit: "mmHg", source: "local TimescaleDB / AMH Gold Observation LOINC 8462-4"}
  - {name: pressao_arterial_media, type: quantity, unit: "mmHg", source: "local TimescaleDB (arterial line) / AMH Gold Observation LOINC 8478-0"}
  - {name: indice_choque, type: quantity, unit: "ratio", source: "hemodynamics domain (derived = HR/SBP)"}
  - {name: lactato_arterial, type: quantity, unit: "mmol/L", source: "AMH Gold lab_result LOINC 2524-7"}
  - {name: tempo_enchimento_capilar, type: quantity, unit: "s", source: "AMH Gold Observation (TEC bedside)"}
  - {name: dose_vasopressor, type: quantity, unit: "mcg/kg/min", source: "hemodynamics conversion service (§4) from MedicationAdministration"}
  - {name: dose_vasopressina, type: quantity, unit: "U/min", source: "hemodynamics conversion service (§4; fixed-rate)"}
  - {name: dose_adrenalina, type: quantity, unit: "mcg/kg/min", source: "hemodynamics conversion service (§4)"}
  - {name: dose_dobutamina, type: quantity, unit: "mcg/kg/min", source: "hemodynamics conversion service (§4)"}
  - {name: taxa_infusao, type: quantity, unit: "mL/h", source: "MedicationAdministration dose.rate (EDGE only; converted in §4)"}
  - {name: concentracao_farmaco, type: quantity, unit: "mg/mL", source: "MedicationAdministration / medication master"}
  - {name: peso, type: quantity, unit: "kg", source: "AMH Gold Observation LOINC 29463-7 (validated)"}
  - {name: ppv, type: quantity, unit: "percent", source: "local TimescaleDB (advanced hemodynamic monitor)"}
  - {name: svv, type: quantity, unit: "percent", source: "local TimescaleDB (advanced hemodynamic monitor)"}
  - {name: delta_sv_pos_fluid, type: quantity, unit: "percent", source: "hemodynamics domain (post fluid challenge)"}
  - {name: delta_map_pos_fluid, type: quantity, unit: "mmHg", source: "hemodynamics domain (post fluid challenge)"}
  - {name: delta_lactato_pos_fluid, type: quantity, unit: "percent", source: "hemodynamics domain (post fluid challenge)"}
  - {name: balanco_hidrico_24h, type: quantity, unit: "mL", source: "aki/equilibrio domain (recomputed from source rows)"}
  - {name: hidrocortisona_ativa, type: boolean, unit: "boolean", source: "AMH Gold MedicationAdministration (hydrocortisone)"}
  - {name: antihipertensivo_agendado_ativo, type: boolean, unit: "boolean", source: "AMH Gold MedicationRequest (scheduled antihypertensive, full class list)"}
  - {name: permissive_htn_indication, type: boolean, unit: "boolean", source: "AMH Gold Condition (AVCi/I64 permissive-HTN window)"}
  - {name: fluid_bolus_given, type: boolean, unit: "boolean", source: "AMH Gold MedicationAdministration (crystalloid bolus)"}
  - {name: fluid_challenge_realizado, type: boolean, unit: "boolean", source: "AMH Gold MedicationAdministration (500 mL crystalloid over 30 min)"}
alerts:
  - ALERT-HEMO-SHOCK-INDEX-01
  - ALERT-HEMO-LACTATE-CLEARANCE-02
  - ALERT-HEMO-VASO-ESCALATION-03
  - ALERT-HEMO-REFRACTORY-SHOCK-04
  - ALERT-HEMO-FLUID-NONRESPONSIVE-05
  - ALERT-HEMO-ANTIHTN-CONFLICT-06
rule_refs:
  - RULE-ESTABILIDADE-001
  - RULE-ESTABILIDADE-002
  - RULE-ESTABILIDADE-003
  - RULE-ESTABILIDADE-005
  - RULE-ESTABILIDADE-007
  - RULE-ESTABILIDADE-008
  - RULE-ESTABILIDADE-009
  - RULE-ESTABILIDADE-010
  - RULE-ESTABILIDADE-011
  - RULE-ESTABILIDADE-012
  - RULE-ESTABILIDADE-013
  - RULE-ESTABILIDADE-014
  - RULE-ESTABILIDADE-015
  - RULE-ESTABILIDADE-016
  - RULE-ESTABILIDADE-017
  - RULE-ESTABILIDADE-018
  - RULE-ESTABILIDADE-019
  - RULE-ESTABILIDADE-020
  - RULE-ESTABILIDADE-021
  - RULE-ESTABILIDADE-022
  - RULE-ESTABILIDADE-023
  - RULE-ESTABILIDADE-024
  - RULE-ESTABILIDADE-025
  - RULE-ESTABILIDADE-026
  - RULE-CLINICAL-SCORING-005
interfaces:
  emits_events:
    - hemodynamics.shock_index.elevated
    - hemodynamics.lactate_clearance.inadequate
    - hemodynamics.vasopressor.escalating
    - hemodynamics.shock.refractory
    - hemodynamics.fluid.non_responsive
    - hemodynamics.vasopressor_dose.canonical
  consumes:
    - {quantity: lactate, unit: "mmol/L", source: "AMH Gold lab_result LOINC 2524-7"}
    - {quantity: fluid_balance, unit: "mL", source: "aki/equilibrio domain"}
    - {quantity: septic_shock_flag, unit: "boolean", source: "sepsis domain (sepsis.shock.detected)"}
    - {quantity: volumetric_infusion_rate, unit: "mL/h", source: "AMH Gold MedicationAdministration (EDGE, converted in §4)"}
    - {quantity: drug_concentration, unit: "mg/mL", source: "AMH Gold MedicationAdministration / medication master"}
    - {quantity: body_weight, unit: "kg", source: "AMH Gold Observation LOINC 29463-7"}
```
