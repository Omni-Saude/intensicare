# Sepsis Domain — IntensiCare v2 Clinical Specification

**Guild:** Clinical (sepsis domain designer) · **Vision ref:** §3.1 (Sepse / Infecção, priority P1) ·
**Platform:** AMH Data Platform consumer (ADR-001) · **Legacy cluster:** `sepse` (99 rules, 4 pathway generations).

This document reconciles the legacy's four sepsis screening variants — **v1** (automatic, AND-aggregation),
**v3** (automatic, OR-aggregation), the **manual** `_REGRAS` 20-criteria pathway, and the **homecare** pathway —
plus the SSC hour-1 **interactive bundle** frontend, into **one** evidence-anchored design:
a **Sepsis-3 + SIRS screening layer** feeding a **SSC-2021 hour-1 bundle tracker**. Every threshold below cites a
guideline/paper and/or a `RULE-SEPSE-*` catalog ID. Disputed aggregation and P0/P1 defects are designed to the
reference-anchored **recommended default** and marked **pending RAT-SEPSE-\***; the ratification committee decides.

---

## 1. Clinical scope

**In scope.** Adult ICU (UTI) sepsis and septic shock, per Sepsis-3 (Singer 2016) and the Surviving Sepsis
Campaign 2021 (Evans 2021):

1. **Screening / triage** — detect a patient with *suspected or confirmed infection + evolving organ
   dysfunction*, early enough to start the hour-1 bundle (<1h from identification; vision VIS-3.1-01 cites a
   25–30% mortality reduction).
2. **Organ-dysfunction / hypoperfusion escalation** — qSOFA ≥2 with lactate elevation or trend.
3. **Septic shock** — vasopressor-requiring hypotension and/or lactate ≥4 mmol/L despite fluids.
4. **Hour-1 bundle compliance tracking** — the 7-item SSC checklist with 1h/3h timers and CPOE/ADEP auto-checks.
5. **Antimicrobial stewardship (procalcitonin)** — de-escalation and treatment-failure trends.

**Out of scope / delegated.** Definitive AKI staging (KDIGO) → **aki** domain; ARDS staging → **respiratory**
domain; lactate-clearance resuscitation targeting and vasopressor unit conversion → **hemodynamics** domain
(this domain *consumes* their outputs and *emits* correlation events). Automatic diagnosis is forbidden — all
outputs are advisory, physician-owned (VIS-C-01, VIS-C-08), recorded to the prontuário at NGS Level 2 (VIS-C-07).

**Reconciliation summary (four variants → one design).** The legacy variants disagree on aggregation
(AND vs OR), group boundaries (7/9/11 majors), strict-vs-inclusive comparisons, and units (lactate mg/dL vs
mmol/L). None of the two-axis "≥N majors AND ≥M minors" schemes has an external validation anchor
(RULE-SEPSE-001 / -004 verdict UNVERIFIABLE). We therefore **do not port any institutional aggregation
verbatim**. The v2 screening layer is rebuilt on the two *published* anchors the vision itself keeps —
**SIRS ≥2 of 4 + infection** (SEP-001) and **qSOFA ≥2 of 3** (SEP-002, Sepsis-3) — with the legacy criteria
carried forward only where they were VERIFIED or corrected to the reference (see §3). All four variants'
divergent behaviour is captured in the RATIFY table (§6).

---

## 2. Typed, unit-checked inputs

Every input unit is the canonical from `_work/units/registry.yaml`. Lactate is **mmol/L only** (mission law;
SYS-03). Weight-indexed quantities require a validated `peso` (SYS-09: legacy weight-parse inflated weight ~10×).

| Input (PT-BR param) | Quantity | Unit (canonical) | Source | Staleness max |
|---|---|---|---|---|
| `temperatura` | body_temperature | `degC` | AMH Gold Observation LOINC 8310-5 | PT6H |
| `frequencia_cardiaca` | heart_rate | `bpm` | Observation LOINC 8867-4 | PT1H |
| `frequencia_respiratoria` | respiratory_rate | `rpm` | Observation LOINC 9279-1 | PT1H |
| `pressao_arterial_sistolica` | systolic_blood_pressure | `mmHg` | Observation LOINC 8480-6 | PT1H |
| `pressao_arterial_diastolica` | diastolic_blood_pressure | `mmHg` | Observation LOINC 8462-4 | PT1H |
| `pressao_arterial_media` | mean_arterial_pressure | `mmHg` | Observation LOINC 8478-0 | PT1H |
| `glasgow` | glasgow_coma_scale | `points` | Observation LOINC 9269-2 | PT8H |
| `leucocitos` | white_blood_cell_count | `10^3/uL` | lab_result LOINC 6690-2 | PT24H |
| `bastonetes` | band_neutrophils_fraction | `percent` | lab_result LOINC 35332-6 | PT24H |
| `plaquetas` | platelet_count | `10^3/uL` | lab_result LOINC 777-3 | PT24H |
| `bilirubina` | total_bilirubin | `mg/dL` | lab_result LOINC 1975-2 | PT24H |
| `creatinina` | serum_creatinine | `mg/dL` | lab_result LOINC 2160-0 | PT24H |
| `lactato_arterial` | lactate | `mmol/L` | lab_result LOINC 2524-7 | PT4H |
| `procalcitonina` | procalcitonin | `ng/mL` | lab_result LOINC 33959-8 | PT48H |
| `proteina_c_reativa` | c_reactive_protein | `mg/L` | lab_result LOINC 1988-5 | PT24H |
| `tempo_enchimento_capilar` | capillary_refill_time | `s` | Observation (TEC, bedside) | PT6H |
| `debito_urinario_horario` | urine_output_rate_indexed | `mL/kg/h` | derived (aki domain), needs `peso` | PT6H |
| `saturacao_o2` | peripheral_oxygen_saturation | `percent` | Observation LOINC 2708-6 | PT1H |
| `paco2_arterial` | arterial_partial_pressure_co2 | `mmHg` | blood gas LOINC 2019-8 | PT6H |
| `relacao_pao2_fio2` | pf_ratio | `ratio` | derived (respiratory domain; FiO2 fraction!) | PT6H |
| `dose_vasopressor` | weight_indexed_vasopressor_rate | `mcg/kg/min` | MedicationAdministration (hemodynamics) | PT1H |
| `qsofa` | quick_sofa | `points` | derived (this domain) | PT1H |
| `cam_icu` | delirium_assessment | `enum {positivo,negativo,nao_avaliavel}` | Observation | PT12H |
| `peso` | body_weight | `kg` | Observation LOINC 29463-7 | PT7D |
| `indice_choque` | shock_index | `ratio` | derived = HR/SBP | PT1H |

**Unit hazards carried from the audit (all handled at the edge normalizer, never in clinical logic):**
- **Lactate** — `mg/dL → mmol/L ×0.111`. Legacy mixed both for the same concept (SYS-03; RULE-SEPSE-013/050/059/061). A bare lactate number with no unit is a build-time error.
- **Weight** — comma-decimal parse (`70,5 → 705 kg`) inflated `mL/kg/h` ~10× and masked oliguria (SYS-09; P0-08 / RULE-SEPSE-014). `debito_urinario_horario` is never computed without a validated `peso`.
- **FiO2** — canonical fraction 0.21–1.0; the `relacao_pao2_fio2` used by minor-criterion C12 (RULE-SEPSE-020) is ~100× wrong if FiO2 arrives as percent (SYS-01/P0-07). Normalized upstream in the respiratory domain.
- **Vasopressor** — canonical `mcg/kg/min`; `mL/h` is **not** convertible without concentration + weight (SYS-C-04). SHOCK-03 consumes the already-converted rate from hemodynamics.

---

## 3. Trigger / staging logic

Severity uses **only** `normal | watch | urgent | critical`. Each criterion below is a carried-forward legacy
rule with an explicit disposition; RATIFY criteria are *designed to the recommended default* and flagged.

### 3.1 Screening layer — `ALERT-SEPSIS-SCREEN-01` (severity: urgent)

**Recommended default aggregation (pending RAT-SEPSE-01/02/03):**

```
screen_positive :=
    infection_present
    AND (
        qsofa >= 2              # Sepsis-3 bedside anchor (Seymour 2016); RR>=22 rpm OR SBP<=100 mmHg OR GCS<15
        OR sirs_count >= 2      # ACCP/SCCM SIRS anchor (Bone 1992): >=2 of the 4 SIRS criteria
    )

infection_present := cultura_positiva OR atb_iniciado_ultimas_24h OR suspeita_infeccao_documentada
                                        # RULE-SEPSE-067 (ADOPT), gates PPV; SEP-001

sirs_criteria (>=2 of 4, each ADOPT / ADOPT-CORRECTED):
  - temperatura > 38.0 degC OR temperatura < 36.0 degC         # RULE-SEPSE-027/018/034 ADOPT (Bone 1992)
  - frequencia_cardiaca > 90 bpm                               # RULE-SEPSE-035/048 ADOPT-CORRECTED (legacy 110/100 -> 90)
  - frequencia_respiratoria > 20 rpm OR paco2_arterial < 32 mmHg  # RULE-SEPSE-028/039/049 ADOPT (Bone 1992)
  - leucocitos > 12 (10^3/uL) OR leucocitos < 4 OR bastonetes > 10 percent  # RULE-SEPSE-051 ADOPT
```

**Why this default is reference-anchored.** SIRS is *defined* as a count-to-threshold-2 of 4 (an OR-of-4-to-≥2),
and qSOFA as ≥2 of 3 — neither is a conjunction of two large groups. The legacy **v1** "≥3 majors AND ≥4 minors"
(RULE-SEPSE-001) has no published anchor and would badly miss the vision's ≥80% early-detection target
(VIS-7.1-01); the **v3** OR-of-everything (RULE-SEPSE-002) floods the alert channel and collapses PPV below the
0.60 fleet floor. The reference-anchored middle is: **OR *within* the published criteria sets, AND-gated by
infection**. The infection gate is what protects PPV — an ungated SIRS-OR screen is exactly the alarm-fatigue
failure mode. **Both disputed branches (v1-AND, v3-OR) are fully specified in §6 RAT-SEPSE-02**; this default is
provisional pending that ratification.

The manual pathway's 20 PT-BR criterion descriptions (RULE-SEPSE-099, ADOPT-CORRECTED — fixes the
`criterio8`-vs-`criterio_8` key typo that silently dropped one description) are preserved verbatim as the
display vocabulary for a positive screen. Homecare-specific dead branches (RULE-SEPSE-003 `menores==4`,
unreachable because criterio_11/RULE-SEPSE-037 is hard-coded `False`) are **superseded**, not ported.

### 3.2 Organ-dysfunction / hypoperfusion — `ALERT-SEPSIS-ORGAN-02` (severity: critical)

```
organ_dysfunction :=
    qsofa >= 2                                   # Sepsis-3 (Seymour 2016); RULE-SEPSE-045/054 (GCS<15 ADOPT-CORRECTED)
    AND ( lactato_arterial > 2 mmol/L            # SSC-2021 hypoperfusion; RULE-SEPSE-013/050 ADOPT-CORRECTED (legacy >=3 / >=2.5 -> >2)
          OR delta_lactato > 0.5 mmol/L per hour ) # 6h lookback trend; SEP-002
```

**Corrections applied.** Legacy fired lactate at **≥3** (RULE-SEPSE-013) or **≥2.5** (RULE-SEPSE-050) mmol/L,
missing the 2.0–3.0 mmol/L hypoperfusion band. v2 uses the SSC-2021 / Sepsis-3 **>2 mmol/L** anchor.
Altered mentation widened from GCS≤13 to **GCS<15** to match qSOFA (RULE-SEPSE-054 ADOPT-CORRECTED).
Supporting organ-dysfunction inputs carried forward: thrombocytopenia <100 ×10³/µL (RULE-SEPSE-012/052 ADOPT,
SOFA-coag), hyperbilirubinemia >2 mg/dL (RULE-SEPSE-046 ADOPT, SOFA-liver), new-onset prolonged capillary refill
>3 s (RULE-SEPSE-022/030/042 ADOPT/ADOPT-CORRECTED — legacy >5 s → ANDROMEDA-SHOCK >3 s).

### 3.3 Septic shock — `ALERT-SEPSIS-SHOCK-03` (severity: critical)

```
septic_shock_imminent :=
    lactato_arterial >= 4 mmol/L                 # SSC-2021 hour-1 bundle; vision "Choque séptico iminente"
    OR ( pressao_arterial_media < 65 mmHg        # Sepsis-3 shock MAP anchor; RULE-SEPSE-011/031 ADOPT
         AND ( fluid_bolus_given                  # 30 mL/kg crystalloid; RULE-SEPSE-061 ADOPT-CORRECTED
               OR dose_vasopressor > 0 mcg/kg/min ) )  # RULE-SEPSE-010/065 ADOPT (new/escalating vasopressor)
```

Vasopressor escalation guidance (RULE-SEPSE-065 ADOPT, SSC-2021): add vasopressin+hydrocortisone at
norepinephrine >0.3 mcg/kg/min; prefer epinephrine above 1.0 mcg/kg/min or shock index >0.7. **Lactate
clearance targeting and the mL/h→mcg/kg/min conversion are delegated to the hemodynamics domain** (SHOCK-03
emits `sepsis.shock.detected` and hands off). This alert extends SEP-002's embedded `choque séptico iminente`
flag into a first-class critical alert with a distinct response.

### 3.4 Hour-1 bundle tracker — `ALERT-SEPSIS-BUNDLE-OVERDUE-04` (severity: urgent)

The **7-item SSC hour-1 bundle** (RULE-SEPSE-076/096 ADOPT — item set and PT-BR `pacote` vocabulary carried
verbatim) with server timers (RULE-SEPSE-069 ADOPT: **1h** for `primeira_hora`, **3h** for `reavaliacao`;
2h reveal-delay RULE-SEPSE-070 ADOPT):

- `pacote: primeira_hora` — `solicitacao_exames` (culturas + lactato), `inicio_escalonamento_antimicrobiano`,
  `realizacao_expansao_volemica` (30 mL/kg Ringer Lactato; RULE-SEPSE-061 ADOPT-CORRECTED).
- `pacote: reavaliacao` — `status_hemodinamico` (RULE-SEPSE-063 ADOPT), `dispositivos_invasivos`
  (RULE-SEPSE-064 ADOPT), `drogas_vasoativas` (RULE-SEPSE-065 ADOPT), lab reassessment (RULE-SEPSE-062 ADOPT).

```
bundle_item_overdue :=
    protocol_active
    AND item.checked == false
    AND now > item.due_at            # due_at = protocol_accept_time + (PT1H if primeira_hora else PT3H)
```

Auto-checks (RULE-SEPSE-078/079/080/081 ADAPT — re-implemented event-driven against AMH Gold via Athena, not
legacy Django ORM): CPOE/ADEP lookback marks `inicio_escalonamento_antimicrobiano` (24h window) and
`realizacao_expansao_volemica` (4h window) done automatically. **Bugs corrected in adaptation:**
RULE-SEPSE-079 dead dispatch string `solicitacao_exame` → plural `solicitacao_exames`; RULE-SEPSE-095 overdue
flag field unified (backend `atraso_item_interativa` vs frontend `atraso_primeira_hora` never rendered).
Protocol lifecycle (accept/decline/close) is superseded by the v2 alert-lifecycle mechanism
(RULE-SEPSE-072/073/074 SUPERSEDE); decline requires a documented reason under a dedicated permission
(RULE-SEPSE-094/097 ADAPT). A 3-day cooldown after a concluded protocol prevents duplicate protocols
(RULE-SEPSE-071 ADAPT → alert suppression).

### 3.5 Procalcitonin stewardship — `ALERT-SEPSIS-PCT-RISING-05` (watch) & `ALERT-SEPSIS-PCT-DEESC-06` (normal)

No legacy `RULE-SEPSE-*` covers procalcitonin; these reconcile the vision/catalog **SEP-003** and cite guidelines
directly (Schuetz Cochrane 2017; Schuetz Lancet ID 2018; PROGRESS/Jensen).

```
pct_rising (treatment failure, watch) :=
    procalcitonina > procalcitonina_anterior
    AND delta_pct > 0.25 ng/mL in 24h
    AND atb_ativa >= 48h

pct_deescalation (stewardship, normal) :=
    ( procalcitonina < 0.25 ng/mL OR (pico_pct - procalcitonina)/pico_pct > 0.80 )
    AND atb_ativa >= 48h
    AND NOT (screen_positive OR organ_dysfunction OR septic_shock_imminent)   # only when clinically stable
```

---

## 4. Evidence citations for every threshold

| Threshold | Value | Evidence (guideline/paper) | Legacy rule(s) & disposition |
|---|---|---|---|
| SIRS fever / hypothermia | >38.0 / <36.0 degC | Bone 1992 (ACCP/SCCM); Levy 2003 | RULE-SEPSE-027/038 (>38.3 major) ADOPT; -018/034/047 ADOPT |
| SIRS tachycardia | >90 bpm | Bone 1992 | RULE-SEPSE-035/048 **ADOPT-CORRECTED** (legacy 110/100) |
| SIRS tachypnea / hypocapnia | >20 rpm / PaCO2<32 mmHg | Bone 1992 | RULE-SEPSE-028/039/049 ADOPT |
| SIRS leukocytosis/leukopenia/bands | >12 / <4 ×10³/µL / >10% | Bone 1992; Levy 2003 | RULE-SEPSE-051 ADOPT |
| qSOFA | ≥2 of {RR≥22, SBP≤100, GCS<15} | Seymour 2016 JAMA; Singer 2016 (Sepsis-3) | RULE-SEPSE-045/054 ADOPT/ADOPT-CORRECTED |
| Lactate elevation | >2 mmol/L | Evans 2021 (SSC); Singer 2016 | RULE-SEPSE-013/050 **ADOPT-CORRECTED** (legacy ≥3 / ≥2.5) |
| Lactate trend | Δ>0.5 mmol/L/h (6h) | SEP-002 (catalog); Seymour 2016 | — (design-new trend on ADOPT lactate) |
| Septic-shock lactate | ≥4 mmol/L | Evans 2021 (SSC hour-1 bundle) | vision VIS-3.1-04 |
| Hypotension | SBP<90 OR PAD<60 OR MAP<65 mmHg | Singer 2016; Evans 2021 | RULE-SEPSE-011/031 ADOPT (RULE-SEPSE-043 PAD<90 bug → RAT) |
| Thrombocytopenia | <100 ×10³/µL | Vincent 1996 (SOFA-coag) | RULE-SEPSE-012/052 ADOPT |
| Hyperbilirubinemia | >2 mg/dL | Vincent 1996 (SOFA-liver) | RULE-SEPSE-046 ADOPT (RULE-SEPSE-017 missing branch → RAT) |
| Capillary refill | >3 s | Hernandez 2019 (ANDROMEDA-SHOCK) | RULE-SEPSE-022/030/042 ADOPT/**ADOPT-CORRECTED** (legacy >5 s) |
| Altered mentation | GCS<15 | Seymour 2016 (qSOFA); Vincent 1996 | RULE-SEPSE-054 **ADOPT-CORRECTED** (legacy ≤13) |
| Volume resuscitation | 30 mL/kg Ringer Lactato (20 for cardiac/renal) | Evans 2021 (SSC) | RULE-SEPSE-061 **ADOPT-CORRECTED** (lactate trigger 30 mg/dL → >2 mmol/L) |
| Vasopressor escalation | vasopressin+HC at NE>0.3; epi at NE>1.0 mcg/kg/min | Evans 2021 (SSC) | RULE-SEPSE-065 ADOPT |
| Restrictive transfusion | Hb>7 g/dL (do not transfuse above) | Evans 2021 (SSC) | RULE-SEPSE-062 ADOPT (Hb unit `g/dL`, not legacy mg/dl) |
| Bundle timers | 1h (primeira_hora) / 3h (reavaliacao) | Levy 2018 (SSC hour-1 bundle update) | RULE-SEPSE-069/070 ADOPT |
| Bundle item set | 7 items, `primeira_hora`/`reavaliacao` | Evans 2021; Levy 2018 | RULE-SEPSE-076/096 ADOPT |
| PCT rising | >baseline + Δ>0.25 ng/mL/24h | Schuetz 2018 Lancet ID | SEP-003b (catalog) |
| PCT de-escalation | <0.25 ng/mL OR >80% drop from peak + 48h stable | Schuetz 2017 Cochrane; PROGRESS | SEP-003a (catalog); vision VIS-3.1-06 |

---

## 5. Interactions with other domains

- **Sepsis + AKI** (vision VIS-4-03: "sepse é #1 causa de AKI"). SCREEN-01/ORGAN-02 emit
  `sepsis.organ_dysfunction.detected`; the **aki** domain consumes it to raise KDIGO suspicion. Reciprocally,
  this domain **consumes** `debito_urinario_horario` and `creatinina` from aki for the renal organ-dysfunction
  input — it does **not** stage AKI itself (legacy RULE-SEPSE-014/032/044 oliguria criteria → RAT, delegated).
- **Sepsis + hemodynamics** (vision VIS-3.4). SHOCK-03 hands off to hemodynamics for lactate-clearance
  resuscitation targeting, shock-index trending, and the `mL/h → mcg/kg/min` vasopressor conversion service
  (SYS-C-04). This domain consumes the already-canonical `dose_vasopressor` and `indice_choque`.
- **Sepsis → early-warning-scores.** The SIRS/qSOFA criteria and SOFA sub-score inputs are shared cluster-wide
  (CLU-SEPSE-17); SOFA/qSOFA computation lives in clinical-scoring, consumed here.
- **Sepsis + correlation engine.** Device-dwell / CLABSI-CAUTI infection-source flags (RULE-SEPSE-067 ADOPT;
  RULE-SEPSE-024/025/055/056 catheter-dwell → RAT) feed the correlation engine's infection-source reasoning.
- **Respiratory.** Consumes `relacao_pao2_fio2` (FiO2 fraction!) and `paco2_arterial` for the C12 oxygenation
  minor criterion; ARDS staging itself is the respiratory domain's.
- **Platform / experience.** Hour-1 bundle state machine and RBAC (RULE-SEPSE-072..098) are rebuilt on the v2
  alert-lifecycle + IAM model, not the retired Django/Tasy stack (ADR-001).

---

## 6. RATIFY design points (designed to recommended default; committee decides)

Per CONTRACTS §Precedence and the escalations brief, **no P0/P1/UNVERIFIABLE rule is silently resolved.** Each
below is built to a reference-anchored *recommended default* and flagged pending the named RAT anchor.

| RAT anchor | Dispute | Both branches | **Recommended default (reference-anchored)** |
|---|---|---|---|
| **RAT-SEPSE-02** (RULE-SEPSE-001/002/004/037) | Screening aggregation **v1-AND vs v3-OR** | **A (v1):** `maiores≥3 AND menores≥4` — high specificity, low sensitivity, fails the ≥80% early-detection target. **B (v3):** OR across all criteria — high sensitivity, PPV collapses below 0.60. | **Neither verbatim.** OR *within* published SIRS(≥2/4) and qSOFA(≥2/3) sets, **AND-gated by infection** (§3.1). Anchored to Bone 1992 + Seymour 2016; protects PPV via the infection gate. |
| **RAT-SEPSE-05 / P0-12** (RULE-SEPSE-043) | Hypotension: code `PAD<90` vs text `PAD<60` | `PAD<90` fires on nearly every patient (false-positive flood). | **`PAS<90 OR PAD<60 OR MAP<65 mmHg`** (Singer 2016; RULE-SEPSE-011 VERIFIED reference). |
| **RAT-SEPSE-08/20/06** (RULE-SEPSE-014/032/044) | Oliguria: fixed mL/24h + weight-parse ~10× bug | Legacy `<100 mL` / `≤1200 mL/24h`, weight inflated ~10× → criterion never fires. | **KDIGO `<0.5 mL/kg/h` for ≥6h**, computed only with a validated `peso`; delegated to aki domain. |
| **RAT-SEPSE-10/21** (RULE-SEPSE-016/033) | GCS/consciousness **direction inverted** (fires on improvement) | Legacy detects an *increase* / improvement. | **Fire on deterioration** (GCS decrease ≥2 or worsening consciousness rank); CON-0193 correction. |
| **RAT-SEPSE-11** (RULE-SEPSE-017/058) | Bilirubin major branch unimplemented; v3 label-vs-model drift | Jaundice-flag only / catalog labels disagree with model (e.g. plaquetopenia label <150 000 vs model <100 000). | **Add bilirubin >2 mg/dL** (SOFA-liver); use the **model** (reference-correct) thresholds, discard drifted labels. |
| **RAT-SEPSE-06/07** (RULE-SEPSE-007/009) | Vasopressor gate **presence vs absence** inversion | Code checks *presence* of noradrenaline where intent is *absence*. | **Absence** of vasopressor for the "spontaneous distress" criteria (docstring intent). |
| **RAT-SEPSE-14** (RULE-SEPSE-021) | CRP AND-combined vs OR-alternative | `PCR>100 AND WBC/bands` — far stricter than intended. | **OR-alternative**: CRP >100 mg/L as an independent minor branch (not a co-condition). |
| **RAT-SEPSE-12** (RULE-SEPSE-019/060) | Tachycardia wrong field (`fr` not `fc`); variant-A live? | Filters respiratory rate; near-never fires. Variant A (Meropenem 1g, 1500 mL fixed) wiring unclear. | **HR>90 bpm** on `frequencia_cardiaca`; treat **variant A as dead legacy**, use weight-based 30 mL/kg. |
| Catheter-dwell / eligibility (RULE-SEPSE-023/024/025/026/036/040/041/053/055/056/057) | Unanchored institutional dwell-time & eligibility cutoffs | Various fixed CVC/CDL/femoral dwell days, VM/vasopressor windows, oral-intake, recent-surgery flags. | **Retain infection-source *concept*, drop fixed cutoffs** pending committee; CDC/HICPAC discourages fixed catheter-replacement intervals. |
| Data-shape (RULE-SEPSE-068/093/098) | Urea threshold-vs-continuous; `finalizado`/`concluida` meaning; CPF signature | AMBIGUOUS — extractor best-guess. | Deferred to committee; bundle-compliance reporting and LGPD signature policy are product/legal decisions. |

---

## 7. Open questions

1. **RAT anchor numbering** is shard-local (sepse-p1 defines RAT-SEPSE-01..21; p2 re-uses RAT-SEPSE-01..12; p3
   RAT-SEPSE-01..03). This doc references anchors by their *rule pairing*; a single canonical RAT-SEPSE
   registry should be minted in `RATIFICATION.md` before build.
2. **Δ-baseline lookback** for `delta_lactato` and `delta_pct` — vision does not name the prior-value timestamp
   source (vision open question). Design assumes a 6h (lactate) / 24h (PCT) lookback against the same analyte's
   most-recent prior result; confirm the exact lookback field mechanics with the data-model guild.
3. **PCT LOINC / availability** — procalcitonin is P2 availability (catalog DATA-AVAIL); the PCT alerts degrade
   gracefully to "insufficient data" when no `procalcitonina` is present.
4. All units required by this domain **exist** in `_work/units/registry.yaml`; no new unit is requested.

---

```yaml domain-inputs
domain: sepsis
inputs:
  - {name: temperatura, type: quantity, unit: "degC", source: "AMH Gold Observation LOINC 8310-5"}
  - {name: frequencia_cardiaca, type: quantity, unit: "bpm", source: "AMH Gold Observation LOINC 8867-4"}
  - {name: frequencia_respiratoria, type: quantity, unit: "rpm", source: "AMH Gold Observation LOINC 9279-1"}
  - {name: pressao_arterial_sistolica, type: quantity, unit: "mmHg", source: "AMH Gold Observation LOINC 8480-6"}
  - {name: pressao_arterial_diastolica, type: quantity, unit: "mmHg", source: "AMH Gold Observation LOINC 8462-4"}
  - {name: pressao_arterial_media, type: quantity, unit: "mmHg", source: "AMH Gold Observation LOINC 8478-0"}
  - {name: glasgow, type: quantity, unit: "points", source: "AMH Gold Observation LOINC 9269-2"}
  - {name: leucocitos, type: quantity, unit: "10^3/uL", source: "AMH Gold lab_result LOINC 6690-2"}
  - {name: bastonetes, type: quantity, unit: "percent", source: "AMH Gold lab_result LOINC 35332-6"}
  - {name: plaquetas, type: quantity, unit: "10^3/uL", source: "AMH Gold lab_result LOINC 777-3"}
  - {name: bilirubina, type: quantity, unit: "mg/dL", source: "AMH Gold lab_result LOINC 1975-2"}
  - {name: creatinina, type: quantity, unit: "mg/dL", source: "AMH Gold lab_result LOINC 2160-0 (via aki domain)"}
  - {name: lactato_arterial, type: quantity, unit: "mmol/L", source: "AMH Gold lab_result LOINC 2524-7"}
  - {name: procalcitonina, type: quantity, unit: "ng/mL", source: "AMH Gold lab_result LOINC 33959-8"}
  - {name: proteina_c_reativa, type: quantity, unit: "mg/L", source: "AMH Gold lab_result LOINC 1988-5"}
  - {name: tempo_enchimento_capilar, type: quantity, unit: "s", source: "AMH Gold Observation (TEC bedside)"}
  - {name: debito_urinario_horario, type: quantity, unit: "mL/kg/h", source: "aki domain (requires validated peso)"}
  - {name: saturacao_o2, type: quantity, unit: "percent", source: "AMH Gold Observation LOINC 2708-6"}
  - {name: paco2_arterial, type: quantity, unit: "mmHg", source: "AMH Gold blood gas LOINC 2019-8"}
  - {name: relacao_pao2_fio2, type: quantity, unit: "ratio", source: "respiratory domain (FiO2 fraction)"}
  - {name: dose_vasopressor, type: quantity, unit: "mcg/kg/min", source: "hemodynamics domain (MedicationAdministration)"}
  - {name: qsofa, type: quantity, unit: "points", source: "clinical-scoring domain"}
  - {name: cam_icu, type: enum, unit: "enum", source: "AMH Gold Observation (delirium_assessment)"}
  - {name: peso, type: quantity, unit: "kg", source: "AMH Gold Observation LOINC 29463-7"}
  - {name: indice_choque, type: quantity, unit: "ratio", source: "hemodynamics domain (HR/SBP)"}
alerts:
  - ALERT-SEPSIS-SCREEN-01
  - ALERT-SEPSIS-ORGAN-02
  - ALERT-SEPSIS-SHOCK-03
  - ALERT-SEPSIS-BUNDLE-OVERDUE-04
  - ALERT-SEPSIS-PCT-RISING-05
  - ALERT-SEPSIS-PCT-DEESC-06
rule_refs:
  - RULE-SEPSE-008
  - RULE-SEPSE-010
  - RULE-SEPSE-011
  - RULE-SEPSE-012
  - RULE-SEPSE-013
  - RULE-SEPSE-018
  - RULE-SEPSE-022
  - RULE-SEPSE-027
  - RULE-SEPSE-028
  - RULE-SEPSE-030
  - RULE-SEPSE-031
  - RULE-SEPSE-034
  - RULE-SEPSE-035
  - RULE-SEPSE-038
  - RULE-SEPSE-039
  - RULE-SEPSE-042
  - RULE-SEPSE-045
  - RULE-SEPSE-046
  - RULE-SEPSE-047
  - RULE-SEPSE-048
  - RULE-SEPSE-049
  - RULE-SEPSE-050
  - RULE-SEPSE-051
  - RULE-SEPSE-052
  - RULE-SEPSE-054
  - RULE-SEPSE-059
  - RULE-SEPSE-061
  - RULE-SEPSE-062
  - RULE-SEPSE-063
  - RULE-SEPSE-064
  - RULE-SEPSE-065
  - RULE-SEPSE-067
  - RULE-SEPSE-069
  - RULE-SEPSE-070
  - RULE-SEPSE-071
  - RULE-SEPSE-075
  - RULE-SEPSE-076
  - RULE-SEPSE-077
  - RULE-SEPSE-078
  - RULE-SEPSE-079
  - RULE-SEPSE-080
  - RULE-SEPSE-081
  - RULE-SEPSE-082
  - RULE-SEPSE-090
  - RULE-SEPSE-094
  - RULE-SEPSE-095
  - RULE-SEPSE-096
  - RULE-SEPSE-099
interfaces:
  emits_events:
    - sepsis.screening.positive
    - sepsis.organ_dysfunction.detected
    - sepsis.shock.detected
    - sepsis.bundle.overdue
    - sepsis.pct.trend
  consumes:
    - {quantity: urine_output_rate_indexed, unit: "mL/kg/h", source: "aki domain"}
    - {quantity: serum_creatinine, unit: "mg/dL", source: "aki domain"}
    - {quantity: weight_indexed_vasopressor_rate, unit: "mcg/kg/min", source: "hemodynamics domain"}
    - {quantity: shock_index, unit: "ratio", source: "hemodynamics domain"}
    - {quantity: pf_ratio, unit: "ratio", source: "respiratory domain"}
    - {quantity: quick_sofa, unit: "points", source: "clinical-scoring domain"}
```
