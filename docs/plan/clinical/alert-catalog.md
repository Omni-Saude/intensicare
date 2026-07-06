# Alert Catalog — IntensiCare v2

Every alert: typed unit-checked inputs, evidence citation, severity (`normal|watch|urgent|critical`), suppression spec, PPV budget, required response, and ≥3 test vectors. Machine source: `docs/plan/_work/alerts/<domain>.yaml` — this file is generated (`build_alert_catalog.py`); edit the YAML, not this file.

## sepsis (6 alerts)

<a id="alert-sepsis-screen-01"></a>
### ALERT-SEPSIS-SCREEN-01 — Triagem de sepse — SIRS/qSOFA com suspeita de infecção

**Severity** urgent · **Evidence** Bone RC et al. ACCP/SCCM Consensus, Chest 1992;101(6):1644-1655 (SIRS); Seymour CW et al. JAMA 2016;315(8):762-774 (qSOFA); Singer M et al. JAMA 2016;315(8):801-810 (Sepsis-3); Levy MM et al. Crit Care Med 2003;31(4):1250-1256 (SCCM/ESICM/ACCP/ATS/SIS); SIRS tachycardia HR>90 correction; Evans L et al. Surviving Sepsis Campaign 2021, Crit Care Med 2021;49(11):e1063-e1143 (infection-source screening) · **Rules** RULE-SEPSE-027, RULE-SEPSE-028, RULE-SEPSE-034, RULE-SEPSE-035, RULE-SEPSE-038, RULE-SEPSE-039, RULE-SEPSE-045, RULE-SEPSE-048, RULE-SEPSE-049, RULE-SEPSE-051, RULE-SEPSE-054, RULE-SEPSE-067, RULE-SEPSE-099 · **PPV target** 0.6 · **Est. volume** 7/100 beds/day

```yaml alert-spec
alert_id: ALERT-SEPSIS-SCREEN-01
name: Triagem de sepse — SIRS/qSOFA com suspeita de infecção
severity: urgent
trigger:
  logic: infection_present AND ( qsofa >= 2 points OR sirs_count >= 2 ) where infection_present := (cultura_positiva
    OR atb_iniciado_ultimas_24h OR suspeita_infeccao_documentada); qsofa counts {frequencia_respiratoria
    >= 22 rpm, pressao_arterial_sistolica <= 100 mmHg, glasgow < 15 points}; sirs_count counts (>=2 of
    4) {(temperatura > 38.0 degC OR temperatura < 36.0 degC), frequencia_cardiaca > 90 bpm, (frequencia_respiratoria
    > 20 rpm OR paco2_arterial < 32 mmHg), (leucocitos > 12 10^3/uL OR leucocitos < 4 10^3/uL OR bastonetes
    > 10 percent)}. PENDING RAT-SEPSE-02 — recommended default is OR-within published sets, AND-gated
    by infection; branch A (v1 maiores>=3 AND menores>=4) and branch B (v3 OR-all) both specified in domain
    doc §6.
  window: PT6H
inputs:
- name: temperatura
  type: quantity
  unit: degC
  source: AMH Gold Observation LOINC 8310-5
  staleness_max: PT6H
- name: frequencia_cardiaca
  type: quantity
  unit: bpm
  source: AMH Gold Observation LOINC 8867-4
  staleness_max: PT1H
- name: frequencia_respiratoria
  type: quantity
  unit: rpm
  source: AMH Gold Observation LOINC 9279-1
  staleness_max: PT1H
- name: pressao_arterial_sistolica
  type: quantity
  unit: mmHg
  source: AMH Gold Observation LOINC 8480-6
  staleness_max: PT1H
- name: glasgow
  type: quantity
  unit: points
  source: AMH Gold Observation LOINC 9269-2
  staleness_max: PT8H
- name: leucocitos
  type: quantity
  unit: 10^3/uL
  source: AMH Gold lab_result LOINC 6690-2
  staleness_max: PT24H
- name: bastonetes
  type: quantity
  unit: percent
  source: AMH Gold lab_result LOINC 35332-6
  staleness_max: PT24H
- name: paco2_arterial
  type: quantity
  unit: mmHg
  source: AMH Gold blood gas LOINC 2019-8
  staleness_max: PT6H
- name: qsofa
  type: quantity
  unit: points
  source: clinical-scoring domain (derived)
  staleness_max: PT1H
- name: cultura_positiva
  type: boolean
  unit: boolean
  source: AMH Gold DiagnosticReport (microbiology)
  staleness_max: PT72H
- name: atb_iniciado_ultimas_24h
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration (antimicrobial)
  staleness_max: PT24H
- name: suspeita_infeccao_documentada
  type: boolean
  unit: boolean
  source: AMH Gold Condition (SNOMED, suspeita de infecção)
  staleness_max: PT24H
evidence:
- citation: Bone RC et al. ACCP/SCCM Consensus, Chest 1992;101(6):1644-1655 (SIRS)
  rule_refs:
  - RULE-SEPSE-027
  - RULE-SEPSE-028
  - RULE-SEPSE-034
  - RULE-SEPSE-038
  - RULE-SEPSE-039
  - RULE-SEPSE-049
  - RULE-SEPSE-051
- citation: Seymour CW et al. JAMA 2016;315(8):762-774 (qSOFA); Singer M et al. JAMA 2016;315(8):801-810
    (Sepsis-3)
  rule_refs:
  - RULE-SEPSE-045
  - RULE-SEPSE-054
- citation: Levy MM et al. Crit Care Med 2003;31(4):1250-1256 (SCCM/ESICM/ACCP/ATS/SIS); SIRS tachycardia
    HR>90 correction
  rule_refs:
  - RULE-SEPSE-035
  - RULE-SEPSE-048
- citation: Evans L et al. Surviving Sepsis Campaign 2021, Crit Care Med 2021;49(11):e1063-e1143 (infection-source
    screening)
  rule_refs:
  - RULE-SEPSE-067
  - RULE-SEPSE-099
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT6H
  rate_limit: 2/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 7
  rationale: SIRS alone has low specificity (fires in pancreatitis/trauma/post-op without infection —
    CAT-SEP-001 Lim); the infection gate (cultura OR atb<24h OR suspeita documentada) is what lifts PPV
    to the 0.60 fleet floor. Rejecting the ungated v3 OR-all branch (which collapses PPV) and the v1 AND-of-large-groups
    branch (which misses the vision's >=80% early-detection target, VIS-7.1-01) keeps this the single
    richest screening alert rather than one alert per criterion. ~30% sepsis incidence over ICU turnover
    yields ~7 screen-positives/100 beds/day; 6h cooldown + 2/24h rate limit prevents re-fire on the same
    episode.
response:
  required: avaliação médica beira-leito + considerar abertura de protocolo de sepse
  ack_sla: PT30M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    qsofa: 2
    frequencia_respiratoria: 24
    pressao_arterial_sistolica: 96
    glasgow: 14
    suspeita_infeccao_documentada: true
  expected: fire
  note: qSOFA>=2 (RR>=22 + SBP<=100 + GCS<15) with documented infection suspicion
- id: TV-2
  kind: fire
  inputs:
    temperatura: 38.6
    frequencia_cardiaca: 112
    leucocitos: 15.2
    qsofa: 0
    atb_iniciado_ultimas_24h: true
  expected: fire
  note: 3 SIRS criteria (fever+tachycardia+leukocytosis) with antimicrobial started <24h
- id: TV-3
  kind: no-fire
  inputs:
    temperatura: 38.6
    frequencia_cardiaca: 112
    leucocitos: 15.2
    qsofa: 0
    cultura_positiva: false
    atb_iniciado_ultimas_24h: false
    suspeita_infeccao_documentada: false
  expected: no-fire
  note: 3 SIRS criteria but NO infection evidence — infection gate suppresses (PPV protection)
- id: TV-4
  kind: boundary
  inputs:
    frequencia_cardiaca: 90
    temperatura: 37.4
    frequencia_respiratoria: 20
    leucocitos: 12.0
    suspeita_infeccao_documentada: true
  expected: no-fire
  note: 'exact-threshold boundary: HR=90 (not >90), RR=20 (not >20), WBC=12.0 (not >12) => sirs_count
    0; infection present but no criterion met'
- id: TV-5
  kind: boundary
  inputs:
    frequencia_cardiaca: 91
    temperatura: 38.1
    frequencia_respiratoria: 20
    leucocitos: 12.0
    qsofa: 0
    cultura_positiva: true
  expected: fire
  note: 'boundary: HR=91 (>90) + temp=38.1 (>38.0) => sirs_count=2 with positive culture'
reconciliation:
- existing_id: SEP-001
  status: changed
  note: 'vs alert-catalog.md SEP-001 ''SIRS positivo com suspeita de infecção'' (URG/P1): legacy required
    a strict conjunction of all four SIRS clauses AND >=2 SIRS AND infection. v2 changes the aggregation
    to the reconciled recommended default — OR-within published SIRS(>=2/4) and qSOFA(>=2/3) sets, AND-gated
    by infection — resolving the v1-AND vs v3-OR dispute (pending RAT-SEPSE-02); SIRS tachycardia corrected
    110/100->90 bpm. Same urgent severity and infection gate; logic changed, not merely aligned.'
```

<a id="alert-sepsis-organ-02"></a>
### ALERT-SEPSIS-ORGAN-02 — qSOFA >=2 com lactato elevado ou em elevação

**Severity** critical · **Evidence** Singer M et al. JAMA 2016;315(8):801-810 (Sepsis-3); Seymour CW et al. JAMA 2016;315(8):762-774 (qSOFA); Evans L et al. SSC 2021, Crit Care Med 2021;49(11):e1063-e1143 (lactate >2 mmol/L hypoperfusion); Vincent JL et al. SOFA score, Intensive Care Med 1996;22:707-710 (coag <100 10^3/uL; liver >2 mg/dL); Hernandez G et al. ANDROMEDA-SHOCK, JAMA 2019;321(7):654-664 (capillary refill >3 s) · **Rules** RULE-SEPSE-012, RULE-SEPSE-013, RULE-SEPSE-022, RULE-SEPSE-030, RULE-SEPSE-042, RULE-SEPSE-045, RULE-SEPSE-046, RULE-SEPSE-050, RULE-SEPSE-052, RULE-SEPSE-054 · **PPV target** 0.72 · **Est. volume** 3/100 beds/day

```yaml alert-spec
alert_id: ALERT-SEPSIS-ORGAN-02
name: qSOFA >=2 com lactato elevado ou em elevação
severity: critical
trigger:
  logic: 'qsofa >= 2 points AND ( lactato_arterial > 2 mmol/L OR delta_lactato > 0.5 mmol/L per hour over
    PT6H ); supporting organ-dysfunction inputs (any reinforces, none required): plaquetas < 100 10^3/uL,
    bilirubina > 2 mg/dL, tempo_enchimento_capilar > 3 s. Lactate anchor corrected from legacy >=3 (RULE-SEPSE-013)
    / >=2.5 (RULE-SEPSE-050) to SSC-2021 >2 mmol/L.'
  window: PT6H
inputs:
- name: qsofa
  type: quantity
  unit: points
  source: clinical-scoring domain (derived; RR>=22, SBP<=100, GCS<15)
  staleness_max: PT1H
- name: lactato_arterial
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result LOINC 2524-7
  staleness_max: PT4H
- name: lactato_arterial_anterior
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result LOINC 2524-7 (prior result, 6h lookback)
  staleness_max: PT6H
- name: plaquetas
  type: quantity
  unit: 10^3/uL
  source: AMH Gold lab_result LOINC 777-3
  staleness_max: PT24H
- name: bilirubina
  type: quantity
  unit: mg/dL
  source: AMH Gold lab_result LOINC 1975-2
  staleness_max: PT24H
- name: tempo_enchimento_capilar
  type: quantity
  unit: s
  source: AMH Gold Observation (TEC bedside)
  staleness_max: PT6H
evidence:
- citation: Singer M et al. JAMA 2016;315(8):801-810 (Sepsis-3); Seymour CW et al. JAMA 2016;315(8):762-774
    (qSOFA)
  rule_refs:
  - RULE-SEPSE-045
  - RULE-SEPSE-054
- citation: Evans L et al. SSC 2021, Crit Care Med 2021;49(11):e1063-e1143 (lactate >2 mmol/L hypoperfusion)
  rule_refs:
  - RULE-SEPSE-013
  - RULE-SEPSE-050
- citation: Vincent JL et al. SOFA score, Intensive Care Med 1996;22:707-710 (coag <100 10^3/uL; liver
    >2 mg/dL)
  rule_refs:
  - RULE-SEPSE-012
  - RULE-SEPSE-052
  - RULE-SEPSE-046
- citation: Hernandez G et al. ANDROMEDA-SHOCK, JAMA 2019;321(7):654-664 (capillary refill >3 s)
  rule_refs:
  - RULE-SEPSE-022
  - RULE-SEPSE-030
  - RULE-SEPSE-042
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT4H
  rate_limit: 3/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.72
  est_volume_per_100_beds_day: 3
  rationale: Requiring BOTH qSOFA>=2 (organ dysfunction) AND lactate elevation/trend is far more specific
    than screening; qSOFA>=2 already selects a high-mortality subset (Seymour 2016). Lactate can rise
    from hepatopathy/epinephrine/metformin (CAT-SEP-002 Lim) so PPV target is set at 0.72 not higher.
    Estimated ~3/100 beds/day. Kept as one critical alert (not split by supporting criterion) to avoid
    alarm-fatigue; thrombocytopenia/bilirubin/CRT only reinforce, never independently fire.
response:
  required: avaliação médica imediata beira-leito + iniciar bundle hora-1 (lactato, culturas, ATB, cristaloide)
  ack_sla: PT15M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    qsofa: 2
    lactato_arterial: 2.4
  expected: fire
  note: qSOFA>=2 with lactate>2 mmol/L (SSC hypoperfusion)
- id: TV-2
  kind: no-fire
  inputs:
    qsofa: 2
    lactato_arterial: 1.8
    lactato_arterial_anterior: 1.2
  expected: no-fire
  note: qSOFA>=2 but lactate<2 and trend 0.6 mmol/L over 6h = 0.1 mmol/L/h < 0.5/h — neither lactate branch
    met
- id: TV-3
  kind: no-fire
  inputs:
    qsofa: 1
    lactato_arterial: 5.0
  expected: no-fire
  note: high lactate but qSOFA<2 — qSOFA gate not met (this alert requires organ dysfunction; isolated
    hyperlactatemia routes to SHOCK-03 if >=4)
- id: TV-4
  kind: boundary
  inputs:
    qsofa: 2
    lactato_arterial: 2.0
  expected: no-fire
  note: 'boundary exact-threshold: lactate=2.0 is NOT >2 (strict); 2.0-2.0 band excluded, matches SSC
    >2 mmol/L anchor'
- id: TV-5
  kind: boundary
  inputs:
    qsofa: 2
    lactato_arterial: 2.01
  expected: fire
  note: 'boundary: lactate just above 2 mmol/L fires'
- id: TV-6
  kind: fire
  inputs:
    qsofa: 2
    lactato_arterial: 1.9
    lactato_arterial_anterior: 1.0
  expected: fire
  note: delta 0.9 mmol/L over 1h lookback = 0.9 mmol/L/h > 0.5/h trend fires even with current lactate
    <2
reconciliation:
- existing_id: SEP-002
  status: extended
  note: 'vs alert-catalog.md SEP-002 ''qSOFA positivo com lactato elevado ou em elevação'' (CRIT/P1):
    carried forward with the lactate anchor corrected to SSC-2021 >2 mmol/L (legacy variants used >=3
    / >=2.5) and altered mentation widened GCS<=13 -> GCS<15. SEP-002''s embedded ''choque séptico iminente''
    escalation (lactate>=4 / refractory hypotension) is extended out into the standalone critical alert
    ALERT-SEPSIS-SHOCK-03 because its response differs; delta-lactato trend (>0.5 mmol/L/h) retained here.'
```

<a id="alert-sepsis-shock-03"></a>
### ALERT-SEPSIS-SHOCK-03 — Choque séptico iminente

**Severity** critical · **Evidence** Evans L et al. SSC 2021, Crit Care Med 2021;49(11):e1063-e1143 (hour-1 bundle; lactate >=4 mmol/L; MAP >=65); Singer M et al. JAMA 2016;315(8):801-810 (Sepsis-3 shock: vasopressor-requiring hypotension MAP<65) · **Rules** RULE-SEPSE-010, RULE-SEPSE-011, RULE-SEPSE-061, RULE-SEPSE-065 · **PPV target** 0.82 · **Est. volume** 1/100 beds/day

```yaml alert-spec
alert_id: ALERT-SEPSIS-SHOCK-03
name: Choque séptico iminente
severity: critical
trigger:
  logic: "lactato_arterial >= 4 mmol/L OR ( pressao_arterial_media < 65 mmHg\n     AND ( fluid_bolus_given\
    \ OR dose_vasopressor > 0 mcg/kg/min ) );\nMAP anchor from Sepsis-3 (RULE-SEPSE-011 VERIFIED reference);\
    \ vasopressor already canonical mcg/kg/min from hemodynamics (mL/h NOT convertible without concentration+weight,\
    \ SYS-C-04). Emits sepsis.shock.detected and hands lactate-clearance targeting to the hemodynamics\
    \ domain."
  window: PT1H
inputs:
- name: lactato_arterial
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result LOINC 2524-7
  staleness_max: PT4H
- name: pressao_arterial_media
  type: quantity
  unit: mmHg
  source: AMH Gold Observation LOINC 8478-0
  staleness_max: PT1H
- name: dose_vasopressor
  type: quantity
  unit: mcg/kg/min
  source: hemodynamics domain (MedicationAdministration, already converted)
  staleness_max: PT1H
- name: fluid_bolus_given
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration (30 mL/kg crystalloid, 6h lookback)
  staleness_max: PT6H
evidence:
- citation: Evans L et al. SSC 2021, Crit Care Med 2021;49(11):e1063-e1143 (hour-1 bundle; lactate >=4
    mmol/L; MAP >=65)
  rule_refs:
  - RULE-SEPSE-061
  - RULE-SEPSE-065
- citation: 'Singer M et al. JAMA 2016;315(8):801-810 (Sepsis-3 shock: vasopressor-requiring hypotension
    MAP<65)'
  rule_refs:
  - RULE-SEPSE-011
  - RULE-SEPSE-010
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT2H
  rate_limit: 6/24h/patient
  maintenance_window_aware: false
ppv_budget:
  target_ppv: 0.82
  est_volume_per_100_beds_day: 1
  rationale: Lactate >=4 mmol/L or vasopressor/fluid-refractory MAP<65 is a narrow, high-mortality (>80%
    for unrecognized shock, VIS-3.4-01) definition — highest PPV in the domain. Kept separate from ORGAN-02
    as a first-class critical alert (vs SEP-002's embedded flag) because the response differs (immediate
    shock management, not just bundle start). maintenance_window_aware:false — a life-threatening alert
    must never be suppressed by a maintenance window. Estimated ~1/100 beds/day.
response:
  required: ativação de equipe de resposta rápida + manejo de choque (vasopressor precoce, ressuscitação
    volêmica dirigida)
  ack_sla: PT5M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    lactato_arterial: 4.2
  expected: fire
  note: lactate >=4 mmol/L (SSC septic-shock hour-1 marker)
- id: TV-2
  kind: fire
  inputs:
    pressao_arterial_media: 58
    dose_vasopressor: 0.2
    lactato_arterial: 3.1
  expected: fire
  note: MAP<65 on active vasopressor despite lactate<4 — refractory hypotension branch
- id: TV-3
  kind: no-fire
  inputs:
    pressao_arterial_media: 58
    dose_vasopressor: 0
    fluid_bolus_given: false
    lactato_arterial: 2.5
  expected: no-fire
  note: MAP<65 but no fluid bolus and no vasopressor yet — not refractory; hypotension routes to ORGAN-02/SCREEN-01
- id: TV-4
  kind: boundary
  inputs:
    lactato_arterial: 4.0
    pressao_arterial_media: 70
  expected: fire
  note: 'boundary exact-threshold: lactate=4.0 is >=4 (inclusive) => fires'
- id: TV-5
  kind: boundary
  inputs:
    pressao_arterial_media: 65
    dose_vasopressor: 0.3
    lactato_arterial: 3.0
  expected: no-fire
  note: 'boundary: MAP=65 is NOT <65 (strict); refractory branch not met'
reconciliation:
- existing_id: null
  status: extended
  note: No standalone catalog SEP-* id existed for this. Promotes the 'choque séptico iminente' escalation
    embedded inside legacy SEP-002 (elevate to CRIT when lactate>=4 mmol/L or refractory MAP<65) into
    a standalone critical alert with a distinct rapid-response workflow and a 5-min ack SLA; sourced from
    vision VIS-3.1-04 plus SEP-002's embedded flag (the formal SEP-002 existing_id is recorded once, under
    ALERT-SEPSIS-ORGAN-02).
```

<a id="alert-sepsis-bundle-overdue-04"></a>
### ALERT-SEPSIS-BUNDLE-OVERDUE-04 — Item do bundle hora-1 em atraso

**Severity** urgent · **Evidence** Levy MM, Evans LE, Rhodes A. Surviving Sepsis Campaign Bundle: 2018 update. Crit Care Med 2018;46:997-1000 (hour-1 bundle timers); Evans L et al. SSC 2021, Crit Care Med 2021;49(11):e1063-e1143 (7-item hour-1 bundle content); Automation/lifecycle re-implementation (event-driven, AMH Gold via Athena; dead-code bug corrections) · **Rules** RULE-SEPSE-069, RULE-SEPSE-070, RULE-SEPSE-071, RULE-SEPSE-075, RULE-SEPSE-076, RULE-SEPSE-078, RULE-SEPSE-079, RULE-SEPSE-080, RULE-SEPSE-081, RULE-SEPSE-095, RULE-SEPSE-096 · **PPV target** 0.85 · **Est. volume** 3/100 beds/day

```yaml alert-spec
alert_id: ALERT-SEPSIS-BUNDLE-OVERDUE-04
name: Item do bundle hora-1 em atraso
severity: urgent
trigger:
  logic: 'protocol_active AND item.checked == false AND now > item.due_at where item.due_at = protocol_accept_time
    + (PT1H if item.pacote == ''primeira_hora'' else PT3H); 7-item SSC bundle (RULE-SEPSE-076/096 item
    set + PT-BR pacote vocabulary verbatim). Auto-checks (RULE-SEPSE-078/079/080/081 ADAPT, event-driven
    vs AMH Gold) mark items done from CPOE (24h) / ADEP (4h) before the timer fires. Corrected bugs: dispatch
    string solicitacao_exame->solicitacao_exames (RULE-SEPSE-079), overdue flag field unified (RULE-SEPSE-095).'
  window: PT3H
inputs:
- name: protocol_active
  type: boolean
  unit: boolean
  source: IntensiCare operational state (TimescaleDB, sepsis protocol lifecycle)
  staleness_max: PT1H
- name: item_checked
  type: boolean
  unit: boolean
  source: IntensiCare operational state (bundle item check-off)
  staleness_max: PT1H
- name: protocol_accept_time
  type: quantity
  unit: s
  source: IntensiCare operational state (protocol acceptance timestamp)
  staleness_max: PT6H
- name: item_pacote
  type: enum
  unit: enum
  source: bundle item catalog (enum {primeira_hora, reavaliacao})
  staleness_max: PT6H
evidence:
- citation: 'Levy MM, Evans LE, Rhodes A. Surviving Sepsis Campaign Bundle: 2018 update. Crit Care Med
    2018;46:997-1000 (hour-1 bundle timers)'
  rule_refs:
  - RULE-SEPSE-069
  - RULE-SEPSE-070
- citation: Evans L et al. SSC 2021, Crit Care Med 2021;49(11):e1063-e1143 (7-item hour-1 bundle content)
  rule_refs:
  - RULE-SEPSE-076
  - RULE-SEPSE-096
- citation: Automation/lifecycle re-implementation (event-driven, AMH Gold via Athena; dead-code bug corrections)
  rule_refs:
  - RULE-SEPSE-078
  - RULE-SEPSE-079
  - RULE-SEPSE-080
  - RULE-SEPSE-081
  - RULE-SEPSE-095
  - RULE-SEPSE-071
  - RULE-SEPSE-075
suppression:
  dedup_key: patient_id+protocol_id+item_name
  cooldown: PT1H
  rate_limit: 7/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.85
  est_volume_per_100_beds_day: 3
  rationale: Deterministic compliance timer (not a physiological prediction) so PPV is high by construction
    — it fires only when a clinician-accepted protocol has a genuinely uncompleted item past its SSC deadline.
    Auto-checks against CPOE/ADEP suppress the common false-positive (item done but not manually checked).
    dedup per item prevents one protocol from emitting a storm; ~3/100 beds/day given sepsis protocol
    incidence. This single overdue alert replaces per-item legacy flags.
response:
  required: completar item do bundle hora-1 pendente (documentar no prontuário NGS-2)
  ack_sla: PT15M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    protocol_active: true
    item_checked: false
    item_pacote: primeira_hora
    minutes_since_accept: 75
  expected: fire
  note: primeira_hora item still unchecked 75 min after accept (due at 60 min)
- id: TV-2
  kind: no-fire
  inputs:
    protocol_active: true
    item_checked: true
    item_pacote: primeira_hora
    minutes_since_accept: 75
  expected: no-fire
  note: item already checked (or auto-checked from CPOE/ADEP) — no overdue
- id: TV-3
  kind: no-fire
  inputs:
    protocol_active: true
    item_checked: false
    item_pacote: reavaliacao
    minutes_since_accept: 120
  expected: no-fire
  note: reavaliacao item due at 180 min, only 120 elapsed — not yet overdue (also within 2h reveal-delay)
- id: TV-4
  kind: boundary
  inputs:
    protocol_active: true
    item_checked: false
    item_pacote: primeira_hora
    minutes_since_accept: 60
  expected: no-fire
  note: 'boundary exact-threshold: at exactly 60 min due_at is reached but now > due_at is strict — not
    yet overdue'
- id: TV-5
  kind: boundary
  inputs:
    protocol_active: true
    item_checked: false
    item_pacote: reavaliacao
    minutes_since_accept: 181
  expected: fire
  note: 'boundary: reavaliacao item 1 min past the 180 min deadline fires'
reconciliation:
- existing_id: null
  status: new
  note: No catalog SEP-* alert covers hour-1 bundle compliance tracking; rebuilt from the legacy interactive-bundle
    rules (RULE-SEPSE-069/070/076/096 ADOPT; auto-check bugs corrected RULE-SEPSE-079/095) into a single
    deterministic overdue-item timer, replacing per-item legacy flags.
```

<a id="alert-sepsis-pct-rising-05"></a>
### ALERT-SEPSIS-PCT-RISING-05 — Procalcitonina em elevação — possível falha terapêutica

**Severity** watch · **Evidence** Schuetz P et al. Lancet Infect Dis 2018;18(1):95-107 (procalcitonin-guided antibiotic therapy); PROGRESS/Jensen JU et al. Am J Respir Crit Care Med 2011 (treatment-failure trend) · **Rules** — · **PPV target** 0.58 · **Est. volume** 1/100 beds/day

```yaml alert-spec
alert_id: ALERT-SEPSIS-PCT-RISING-05
name: Procalcitonina em elevação — possível falha terapêutica
severity: watch
trigger:
  logic: procalcitonina > procalcitonina_anterior AND delta_pct > 0.25 ng/mL over PT24H AND atb_ativa_horas
    >= 48; no legacy RULE-SEPSE-* covers PCT — cites guidelines directly (Schuetz 2018).
  window: PT24H
inputs:
- name: procalcitonina
  type: quantity
  unit: ng/mL
  source: AMH Gold lab_result LOINC 33959-8
  staleness_max: PT48H
- name: procalcitonina_anterior
  type: quantity
  unit: ng/mL
  source: AMH Gold lab_result LOINC 33959-8 (prior result, 24h lookback)
  staleness_max: PT48H
- name: atb_ativa_horas
  type: quantity
  unit: count
  source: AMH Gold MedicationRequest/MedicationAdministration (active antimicrobial duration, hours)
  staleness_max: PT24H
evidence:
- citation: Schuetz P et al. Lancet Infect Dis 2018;18(1):95-107 (procalcitonin-guided antibiotic therapy);
    PROGRESS/Jensen JU et al. Am J Respir Crit Care Med 2011 (treatment-failure trend)
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT24H
  rate_limit: 1/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.58
  est_volume_per_100_beds_day: 1
  rationale: PCT can rise from major post-op/trauma/burns/medullary thyroid carcinoma without infection
    (CAT-SEP-003 Lim), so PPV is set just below the fleet floor (0.58) and severity is only WATCH (advisory
    trend, not a deterioration alarm) to stay within the <=10% ignored-rate budget. Requires >=48h of
    active antimicrobial so it only fires when a treatment-failure question is clinically meaningful;
    degrades gracefully to insufficient-data when no PCT present (P2 availability). ~1/100 beds/day.
response:
  required: reavaliar cobertura antimicrobiana e controle de foco (avaliação médica)
  ack_sla: PT2H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    procalcitonina: 1.2
    procalcitonina_anterior: 0.8
    atb_ativa_horas: 60
  expected: fire
  note: PCT rising, delta 0.4 > 0.25 ng/mL, ATB active >=48h
- id: TV-2
  kind: no-fire
  inputs:
    procalcitonina: 1.2
    procalcitonina_anterior: 0.8
    atb_ativa_horas: 24
  expected: no-fire
  note: rising but ATB active only 24h (<48h) — too early to call failure
- id: TV-3
  kind: no-fire
  inputs:
    procalcitonina: 0.9
    procalcitonina_anterior: 1.5
    atb_ativa_horas: 72
  expected: no-fire
  note: PCT falling — responding to therapy, no alert
- id: TV-4
  kind: boundary
  inputs:
    procalcitonina: 1.05
    procalcitonina_anterior: 0.8
    atb_ativa_horas: 48
  expected: no-fire
  note: 'boundary exact-threshold: delta=0.25 is NOT >0.25 (strict); ATB=48 exactly meets >=48'
- id: TV-5
  kind: boundary
  inputs:
    procalcitonina: 1.06
    procalcitonina_anterior: 0.8
    atb_ativa_horas: 48
  expected: fire
  note: 'boundary: delta 0.26 > 0.25 with ATB exactly 48h fires'
reconciliation:
- existing_id: SEP-003
  status: changed
  note: 'vs alert-catalog.md SEP-003 ''Procalcitonina — orientação para antibioticoterapia'' (INFO(a)/URG(b),
    P2): legacy bundled two sub-triggers (3a de-escalation, 3b treatment-failure) in one entry. v2 splits
    them into two severity-appropriate alerts: the 3b treatment-failure branch is changed here (severity
    lowered URG->watch, a trend not a deterioration alarm) as ALERT-SEPSIS-PCT-RISING-05; thresholds (delta>0.25
    ng/mL/24h, ATB>=48h) unchanged. The 3a de-escalation branch becomes ALERT-SEPSIS-PCT-DEESC-06 (see
    its own reconciliation note).'
```

<a id="alert-sepsis-pct-deesc-06"></a>
### ALERT-SEPSIS-PCT-DEESC-06 — Desmame antimicrobiano guiado por procalcitonina

**Severity** normal · **Evidence** Schuetz P et al. Cochrane Database Syst Rev 2017;10:CD007498 (procalcitonin to guide antibiotics); PROGRESS/Jensen JU et al. 2011 (de-escalation); Evans L et al. SSC 2021, Crit Care Med 2021;49(11):e1063-e1143 (antimicrobial stewardship / de-escalation) · **Rules** RULE-SEPSE-062 · **PPV target** 0.65 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-SEPSIS-PCT-DEESC-06
name: Desmame antimicrobiano guiado por procalcitonina
severity: normal
trigger:
  logic: ( procalcitonina < 0.25 ng/mL OR (pico_pct - procalcitonina)/pico_pct > 0.80 ) AND atb_ativa_horas
    >= 48 AND NOT ( screen_positive OR organ_dysfunction OR septic_shock_imminent ); stability gate references
    SCREEN-01/ORGAN-02/SHOCK-03 states so de-escalation is never suggested for an unstable patient. Cites
    guidelines directly (Schuetz Cochrane 2017; PROGRESS).
  window: PT48H
inputs:
- name: procalcitonina
  type: quantity
  unit: ng/mL
  source: AMH Gold lab_result LOINC 33959-8
  staleness_max: PT48H
- name: pico_pct
  type: quantity
  unit: ng/mL
  source: AMH Gold lab_result LOINC 33959-8 (peak value this episode)
  staleness_max: PT7D
- name: atb_ativa_horas
  type: quantity
  unit: count
  source: AMH Gold MedicationRequest/MedicationAdministration (active antimicrobial duration, hours)
  staleness_max: PT24H
- name: patient_unstable
  type: boolean
  unit: boolean
  source: sepsis domain (SCREEN-01/ORGAN-02/SHOCK-03 active-state)
  staleness_max: PT6H
evidence:
- citation: Schuetz P et al. Cochrane Database Syst Rev 2017;10:CD007498 (procalcitonin to guide antibiotics);
    PROGRESS/Jensen JU et al. 2011 (de-escalation)
  rule_refs: []
- citation: Evans L et al. SSC 2021, Crit Care Med 2021;49(11):e1063-e1143 (antimicrobial stewardship
    / de-escalation)
  rule_refs:
  - RULE-SEPSE-062
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT24H
  rate_limit: 1/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.65
  est_volume_per_100_beds_day: 2
  rationale: Stewardship prompt (normal severity — informational, <6h action window) so it does not consume
    the deterioration-alarm attention budget; the stability gate (NOT screen_positive/organ_dysfunction/shock)
    removes the dangerous false-positive of suggesting de-escalation in an actively septic patient, keeping
    PPV at 0.65. ~2/100 beds/day. Kept as a single normal-severity alert rather than a channel of stewardship
    nudges to respect the fewer-richer-alerts principle.
response:
  required: considerar suspensão/estreitamento do antimicrobiano (decisão médica, stewardship)
  ack_sla: PT6H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    procalcitonina: 0.18
    atb_ativa_horas: 60
    patient_unstable: false
  expected: fire
  note: PCT <0.25 ng/mL, ATB >=48h, patient stable
- id: TV-2
  kind: fire
  inputs:
    procalcitonina: 0.9
    pico_pct: 6.0
    atb_ativa_horas: 72
    patient_unstable: false
  expected: fire
  note: '>85% drop from peak (6.0->0.9 = 85%) with stable patient'
- id: TV-3
  kind: no-fire
  inputs:
    procalcitonina: 0.18
    atb_ativa_horas: 60
    patient_unstable: true
  expected: no-fire
  note: PCT low but patient still meets screen/organ/shock — stability gate suppresses de-escalation
- id: TV-4
  kind: boundary
  inputs:
    procalcitonina: 0.25
    atb_ativa_horas: 60
    patient_unstable: false
  expected: no-fire
  note: 'boundary exact-threshold: PCT=0.25 is NOT <0.25 (strict); and no peak-drop supplied'
- id: TV-5
  kind: boundary
  inputs:
    procalcitonina: 0.24
    atb_ativa_horas: 48
    patient_unstable: false
  expected: fire
  note: 'boundary: PCT 0.24 <0.25 with ATB exactly 48h and stable fires'
reconciliation:
- existing_id: null
  status: extended
  note: Operationalizes the de-escalation branch (3a) of legacy catalog SEP-003 (PCT<0.25 ng/mL OR >80%
    drop from peak, + 48h stable ATB); the formal SEP-003 existing_id is recorded once, under ALERT-SEPSIS-PCT-RISING-05,
    to avoid double-mapping the same catalog entry. Extended here with an explicit stability gate wired
    to SCREEN-01/ORGAN-02/SHOCK-03 active states so de-escalation is never suggested for an actively septic
    patient; thresholds unchanged.
```

## aki (3 alerts)

<a id="alert-aki-kdigo-stage-01"></a>
### ALERT-AKI-KDIGO-STAGE-01 — Lesão renal aguda — estadiamento KDIGO

**Severity** watch · **Evidence** KDIGO 2012 Clinical Practice Guideline for AKI, Kidney Int Suppl 2012;2(1):1-138 (staging §2.1) · **Rules** RULE-BALANCO-HIDRICO-001, RULE-BALANCO-HIDRICO-003, RULE-BALANCO-HIDRICO-014, RULE-BALANCO-HIDRICO-038, RULE-SINAIS-VITAIS-025 · **PPV target** 0.75 · **Est. volume** 5/100 beds/day

```yaml alert-spec
alert_id: ALERT-AKI-KDIGO-STAGE-01
name: Lesão renal aguda — estadiamento KDIGO
severity: watch
trigger:
  logic: 'kdigo_stage >= 1, where kdigo_stage = max(stage_cr, stage_uo). stage_cr = 3 if (creatinina >=
    3.0*creatinina_basal) OR (creatinina >= 4.0 mg/dL AND delta_cr_48h >= 0.5 mg/dL) OR terapia_renal_substitutiva;
    = 2 if creatinina >= 2.0*creatinina_basal; = 1 if delta_cr_48h >= 0.3 mg/dL OR (creatinina >= 1.5*creatinina_basal
    within 7d); else 0. stage_uo = 3 if debito_urinario_horario(24h) < 0.3 mL/kg/h OR anuria(12h); = 2
    if debito_urinario_horario(12h) < 0.5 mL/kg/h; = 1 if debito_urinario_horario(6h) < 0.5 mL/kg/h; else
    0. delta_cr_48h = creatinina - min(creatinina over trailing rolling 48h). Severity output = watch(stage
    1) | urgent(stage 2) | critical(stage 3).

    '
  window: PT48H
inputs:
- name: creatinina
  type: quantity
  unit: mg/dL
  source: AMH Gold lab_result (LOINC 2160-0)
  staleness_max: PT24H
- name: creatinina_basal
  type: quantity
  unit: mg/dL
  source: derived baseline resolver (known > 7d-min > MDRD eGFR 75)
  staleness_max: PT30D
- name: debito_urinario_horario
  type: quantity
  unit: mL/kg/h
  source: derived rolling 6/12/24h window (requires validated peso)
  staleness_max: PT6H
- name: debito_urinario
  type: quantity
  unit: mL
  source: AMH Gold Observation (LOINC 9187-6) / fluid-balance saida rows
  staleness_max: PT6H
- name: peso
  type: quantity
  unit: kg
  source: AMH Gold Observation (LOINC 29463-7)
  staleness_max: PT7D
- name: terapia_renal_substitutiva
  type: boolean
  unit: boolean
  source: AMH Gold Procedure / MedicationAdministration (RRT active)
  staleness_max: PT24H
evidence:
- citation: KDIGO 2012 Clinical Practice Guideline for AKI, Kidney Int Suppl 2012;2(1):1-138 (staging
    §2.1)
  rule_refs:
  - RULE-SINAIS-VITAIS-025
  - RULE-BALANCO-HIDRICO-001
  - RULE-BALANCO-HIDRICO-003
  - RULE-BALANCO-HIDRICO-014
  - RULE-BALANCO-HIDRICO-038
suppression:
  dedup_key: patient_id+alert_id+kdigo_stage
  cooldown: PT12H
  rate_limit: 3/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.75
  est_volume_per_100_beds_day: 5
  rationale: 'AKI incidence 30-60% of ICU patients (VIS-3.2-01); a 100-bed ICU generates ~4-6 new-or-escalating
    KDIGO stage transitions/day. KDIGO staging is an objective definition (Cr/UO vs a resolved baseline),
    so true-positive rate is high; the ~25% non-actionable share is dominated by MDRD-estimated baselines
    over-diagnosing known-CKD patients (surfaced via baseline_source) and transient pre-renal oliguria
    that self-corrects. Folding three stage alerts into one stage-scaling alert (dedup on kdigo_stage)
    is the key volume/PPV control vs the legacy three-alert design; supports the >=0.60 fleet PPV and
    <=10% ignored targets (VIS-7.1-02/04).

    '
response:
  required: avaliação médica; revisar nefrotóxicos, volemia e dosagem renal; considerar nefrologia se
    estágio >=2
  ack_sla: PT30M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    creatinina: 1.6
    creatinina_basal: 1.0
    debito_urinario_horario: 0.9
  expected: fire
  note: Cr 1.6 = 1.6x baseline (>=1.5x) -> stage 1 -> watch
- id: TV-2
  kind: fire
  inputs:
    creatinina: 2.2
    creatinina_basal: 1.0
    debito_urinario_horario: 0.9
  expected: fire
  note: Cr 2.2x baseline -> stage 2 -> urgent
- id: TV-3
  kind: fire
  inputs:
    creatinina: 1.0
    creatinina_basal: 1.0
    debito_urinario_horario: 0.25
    peso: 70
  expected: fire
  note: UO 0.25 mL/kg/h over 24h < 0.3 -> stage_uo 3 -> critical (max of axes)
- id: TV-4
  kind: no-fire
  inputs:
    creatinina: 1.1
    creatinina_basal: 1.0
    debito_urinario_horario: 0.9
  expected: no-fire
  note: Cr 1.1x baseline (<1.5x), delta 0.1<0.3, UO normal -> stage 0
- id: TV-5
  kind: boundary
  inputs:
    creatinina: 1.5
    creatinina_basal: 1.0
    debito_urinario_horario: 0.5
    peso: 70
  expected: fire
  note: Cr exactly 1.5x baseline -> stage 1 (>=1.5x inclusive); UO exactly 0.5 does NOT fire (<0.5 strict)
    so stage from Cr axis only
- id: TV-6
  kind: boundary
  inputs:
    creatinina: 1.29
    creatinina_basal: 1.0
    debito_urinario_horario: 0.5
    peso: 70
  expected: no-fire
  note: delta 0.29<0.3, 1.29x<1.5x, UO exactly 0.5 not <0.5 -> stage 0; guards the 0.3 rise and <0.5 UO
    boundaries
- id: TV-7
  kind: fire
  inputs:
    creatinina: 4.2
    creatinina_basal: 3.9
    delta_cr_48h: 0.6
    terapia_renal_substitutiva: false
  expected: fire
  note: Cr 4.2>=4.0 with acute rise 0.6>=0.5 -> stage 3 -> critical even though only ~1.08x baseline
reconciliation:
- existing_id: AKI-001
  status: changed
  note: 'vs docs/clinical/alert-catalog.md: KDIGO stage 1 (WARN) folded into stage-scaling alert; UO window
    changed from 07:00-07:00 nursing day to KDIGO rolling 6h; baseline resolver made explicit.'
- existing_id: AKI-002
  status: changed
  note: 'vs alert-catalog.md: KDIGO stage 2 (URG) folded in; UO rolling 12h replaces nursing-day window;
    severity = urgent branch.'
- existing_id: AKI-003
  status: changed
  note: 'vs alert-catalog.md: KDIGO stage 3 (CRIT) folded in; adds RRT-initiation and anuria(12h) to critical
    branch; UO rolling 24h; severity = critical branch.'
```

<a id="alert-aki-progression-02"></a>
### ALERT-AKI-PROGRESSION-02 — Progressão de LRA — mudança de estágio KDIGO em 24h

**Severity** urgent · **Evidence** KDIGO 2012 (staging is dynamic; stage progression is a deterioration signal), Kidney Int Suppl 2012;2(1):1-138 · **Rules** RULE-BALANCO-HIDRICO-003, RULE-SINAIS-VITAIS-025 · **PPV target** 0.7 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-AKI-PROGRESSION-02
name: Progressão de LRA — mudança de estágio KDIGO em 24h
severity: urgent
trigger:
  logic: 'kdigo_stage_now > kdigo_stage_24h_ago AND kdigo_stage_24h_ago is not null. Severity = urgent,
    escalated to critical if kdigo_stage_now == 3. A worsening trajectory outranks a static stage of equal
    value.

    '
  window: PT24H
inputs:
- name: creatinina
  type: quantity
  unit: mg/dL
  source: AMH Gold lab_result (LOINC 2160-0)
  staleness_max: PT24H
- name: creatinina_basal
  type: quantity
  unit: mg/dL
  source: derived baseline resolver
  staleness_max: PT30D
- name: debito_urinario_horario
  type: quantity
  unit: mL/kg/h
  source: derived rolling window (requires validated peso)
  staleness_max: PT6H
- name: peso
  type: quantity
  unit: kg
  source: AMH Gold Observation (LOINC 29463-7)
  staleness_max: PT7D
evidence:
- citation: KDIGO 2012 (staging is dynamic; stage progression is a deterioration signal), Kidney Int Suppl
    2012;2(1):1-138
  rule_refs:
  - RULE-SINAIS-VITAIS-025
  - RULE-BALANCO-HIDRICO-003
suppression:
  dedup_key: patient_id+alert_id+kdigo_stage_now
  cooldown: PT12H
  rate_limit: 2/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.7
  est_volume_per_100_beds_day: 2
  rationale: 'Stage progression is rarer than a static stage: only patients already in AKI who worsen
    within 24h (~1-2/100-beds/day). PPV is slightly below the staging alert because a single spurious
    creatinine spike or a transiently mis-resolved baseline can register a false step-up; dedup on the
    newly-reached stage prevents oscillation re-fires. Fires infrequently and carries a clear deterioration
    meaning, so it is alarm-fatigue-efficient (few, high-signal).

    '
response:
  required: reavaliação médica imediata; investigar causa da progressão (nefrotoxina, hipoperfusão, obstrução)
  ack_sla: PT30M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    kdigo_stage_now: 2
    kdigo_stage_24h_ago: 1
  expected: fire
  note: stage 1 -> 2 within 24h -> urgent
- id: TV-2
  kind: fire
  inputs:
    kdigo_stage_now: 3
    kdigo_stage_24h_ago: 1
  expected: fire
  note: stage 1 -> 3 -> critical (new stage == 3)
- id: TV-3
  kind: no-fire
  inputs:
    kdigo_stage_now: 2
    kdigo_stage_24h_ago: 2
  expected: no-fire
  note: no increase (static stage 2) -> staging alert owns this, not progression
- id: TV-4
  kind: boundary
  inputs:
    kdigo_stage_now: 1
    kdigo_stage_24h_ago: null
  expected: no-fire
  note: no prior stage (null) -> first detection is the staging alert's job, not progression; guards the
    null-baseline boundary
- id: TV-5
  kind: no-fire
  inputs:
    kdigo_stage_now: 1
    kdigo_stage_24h_ago: 2
  expected: no-fire
  note: improving (2 -> 1) -> no progression alert (direction guard; not the inverted legacy bug)
reconciliation:
- existing_id: AKI-004
  status: extended
  note: 'vs alert-catalog.md: AKI-004 ''Progressão AKI'' aligned; extended with severity escalation to
    critical when new stage is 3 and explicit null-prior-stage guard.'
```

<a id="alert-aki-nephrotoxin-03"></a>
### ALERT-AKI-NEPHROTOXIN-03 — Risco de nefrotoxicidade aditiva com creatinina em elevação

**Severity** watch · **Evidence** KDIGO Drug-Induced AKI 2023 (Kidney Int); Rybak MJ et al. Am J Health Syst Pharm 2020;77(11):835-864 (vancomycin/AKI); vision AIN Consensus 2020 · **Rules** RULE-ANTIMICROBIANO-003, RULE-SINAIS-VITAIS-025 · **PPV target** 0.6 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-AKI-NEPHROTOXIN-03
name: Risco de nefrotoxicidade aditiva com creatinina em elevação
severity: watch
trigger:
  logic: 'rising_cr AND nephrotoxic_combo, where rising_cr = creatinina > creatinina_basal + 0.2 mg/dL
    (sub-stage-1 upward trend); nephrotoxic_combo = (vancomicina_ativa AND aminoglicosideo_ativo) OR (vancomicina_ativa
    AND contraste_iodado) OR (aminoglicosideo_ativo AND aine_ativo) OR (ieca_bra_ativo AND hipovolemia).

    '
  window: PT72H
inputs:
- name: creatinina
  type: quantity
  unit: mg/dL
  source: AMH Gold lab_result (LOINC 2160-0)
  staleness_max: PT24H
- name: creatinina_basal
  type: quantity
  unit: mg/dL
  source: derived baseline resolver
  staleness_max: PT30D
- name: vancomicina_ativa
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration
  staleness_max: PT24H
- name: aminoglicosideo_ativo
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration
  staleness_max: PT24H
- name: contraste_iodado
  type: boolean
  unit: boolean
  source: AMH Gold Procedure (last 72h)
  staleness_max: PT72H
- name: aine_ativo
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration
  staleness_max: PT24H
- name: ieca_bra_ativo
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration
  staleness_max: PT24H
- name: hipovolemia
  type: boolean
  unit: boolean
  source: hemodynamics domain (net-negative balance / volume depletion)
  staleness_max: PT6H
evidence:
- citation: KDIGO Drug-Induced AKI 2023 (Kidney Int); Rybak MJ et al. Am J Health Syst Pharm 2020;77(11):835-864
    (vancomycin/AKI); vision AIN Consensus 2020
  rule_refs:
  - RULE-ANTIMICROBIANO-003
  - RULE-SINAIS-VITAIS-025
suppression:
  dedup_key: patient_id+alert_id+active_nephrotoxin_set
  cooldown: PT24H
  rate_limit: 1/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 2
  rationale: 'Nephrotoxic combinations are common in the ICU, but the rising_cr gate (Cr > baseline +
    0.2 mg/dL) restricts firing to patients with an actual early renal signal, keeping volume to ~1-2/100-beds/day
    and PPV at the fleet floor of 0.60. The gate is precisely the dedup boundary with the pharmaco-interaction
    DDX-003 combination alert (which fires pre-injury): without a moving marker this alert stays silent,
    avoiding a duplicate. It is intentionally the lowest-severity AKI alert (watch) because the intent
    is pre-emptive drug withdrawal, not resuscitation.

    '
response:
  required: revisar e suspender/ajustar nefrotóxicos; corrigir volemia; monitorar creatinina seriada
  ack_sla: PT2H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    creatinina: 1.3
    creatinina_basal: 1.0
    vancomicina_ativa: true
    aminoglicosideo_ativo: true
  expected: fire
  note: rising_cr (1.3 > 1.0+0.2) AND vanco+aminoglycoside -> watch
- id: TV-2
  kind: fire
  inputs:
    creatinina: 1.4
    creatinina_basal: 1.0
    ieca_bra_ativo: true
    hipovolemia: true
  expected: fire
  note: rising_cr AND ACEi/ARB + volume depletion branch
- id: TV-3
  kind: no-fire
  inputs:
    creatinina: 1.15
    creatinina_basal: 1.0
    vancomicina_ativa: true
    aminoglicosideo_ativo: true
  expected: no-fire
  note: combo present but Cr 1.15 <= baseline+0.2 -> no renal signal -> owned by pharmaco DDX-003, not
    this alert
- id: TV-4
  kind: boundary
  inputs:
    creatinina: 1.2
    creatinina_basal: 1.0
    vancomicina_ativa: true
    aminoglicosideo_ativo: true
  expected: no-fire
  note: Cr exactly baseline+0.2 (1.2) is NOT > 0.2 rise (strict) -> no-fire; guards the +0.2 threshold
- id: TV-5
  kind: no-fire
  inputs:
    creatinina: 1.5
    creatinina_basal: 1.0
    vancomicina_ativa: true
    aminoglicosideo_ativo: false
    contraste_iodado: false
  expected: no-fire
  note: rising_cr true but only vancomycin alone (no second nephrotoxin) -> combo false -> no-fire
reconciliation:
- existing_id: AKI-005
  status: extended
  note: 'vs alert-catalog.md: AKI-005 ''Risco de AKI por nefrotoxicidade aditiva'' aligned; extended with
    an explicit active_nephrotoxin_set dedup key and an explicit boundary with pharmaco DDX-003 (this
    alert requires rising_cr; DDX-003 fires pre-injury).'
```

## respiratory (5 alerts)

<a id="alert-resp-ards-staging-01"></a>
### ALERT-RESP-ARDS-STAGING-01 — SDRA — vigilância e estadiamento de Berlin (S/F e P/F)

**Severity** urgent · **Evidence** ARDS Definition Task Force. JAMA 2012;307(23):2526-2533 (Berlin Definition); Rice TW et al. Chest 2007;132(2):410-417 (SpO2/FiO2 surrogate); ARDS Network (ARMA). NEJM 2000;342:1301-1308 (lung-protective ≤6 mL/kg PBW); Amato MB et al. NEJM 2015;372:747 (plateau/driving pressure ≤30 cmH2O) · **Rules** RULE-VENTILACAO-001, RULE-VENTILACAO-017 · **PPV target** 0.65 · **Est. volume** 7/100 beds/day

```yaml alert-spec
alert_id: ALERT-RESP-ARDS-STAGING-01
name: SDRA — vigilância e estadiamento de Berlin (S/F e P/F)
severity: urgent
trigger:
  logic: "ards_gate := on_mechanical_ventilation_or_cpap AND peep >= 5 cmH2O AND infiltrado_bilateral\
    \ == true AND edema_cardiogenico_excluido == true. FiO2 is a FRACTION. S/F = saturacao_o2(percent\
    \ numeric) / fio2(fraction); P/F = pao2(mmHg) / fio2(fraction). stage(leve, WATCH)     := ards_gate\
    \ AND ((relacao_spo2_fio2 <= 315 AND relacao_spo2_fio2 > 235)\n                          OR (pf_available\
    \ AND relacao_pao2_fio2 <= 300 AND relacao_pao2_fio2 > 200));\nstage(moderada, URGENT):= ards_gate\
    \ AND ((relacao_spo2_fio2 <= 235 AND relacao_spo2_fio2 > 148)\n                          OR (pf_available\
    \ AND relacao_pao2_fio2 <= 200 AND relacao_pao2_fio2 > 100));\nstage(grave, CRITICAL) := ards_gate\
    \ AND (relacao_spo2_fio2 <= 148 OR (pf_available AND relacao_pao2_fio2 <= 100)). When ABG present,\
    \ P/F is authoritative and overrides the S/F band (S/F overestimates when SpO2>97%). Embedded lung-protective\
    \ companion (pending RAT-VENTILACAO-02): flag volume_corrente_pbw > 6 mL/kg-PBW OR pressao_plato >\
    \ 30 cmH2O."
  window: PT6H
inputs:
- name: saturacao_o2
  type: quantity
  unit: percent
  source: AMH Gold Observation LOINC 2708-6
  staleness_max: PT15M
- name: fio2
  type: quantity
  unit: fraction
  source: AMH Gold Observation LOINC 19935-6 / ventilator OBX
  staleness_max: PT15M
- name: pao2
  type: quantity
  unit: mmHg
  source: AMH Gold blood gas LOINC 2703-7 (optional)
  staleness_max: PT6H
- name: peep
  type: quantity
  unit: cmH2O
  source: ventilator OBX / Observation LOINC 20077-4
  staleness_max: PT1H
- name: infiltrado_bilateral
  type: boolean
  unit: boolean
  source: imaging DiagnosticReport (CXR/CT)
  staleness_max: PT24H
- name: edema_cardiogenico_excluido
  type: boolean
  unit: boolean
  source: clinical assessment (Berlin qualifier)
  staleness_max: PT24H
- name: volume_corrente_pbw
  type: quantity
  unit: mL/kg
  source: derived = VT / PBW(altura, sex)
  staleness_max: PT1H
- name: pressao_plato
  type: quantity
  unit: cmH2O
  source: ventilator OBX (optional)
  staleness_max: PT1H
evidence:
- citation: ARDS Definition Task Force. JAMA 2012;307(23):2526-2533 (Berlin Definition)
  rule_refs:
  - RULE-VENTILACAO-017
- citation: Rice TW et al. Chest 2007;132(2):410-417 (SpO2/FiO2 surrogate)
  rule_refs: []
- citation: ARDS Network (ARMA). NEJM 2000;342:1301-1308 (lung-protective ≤6 mL/kg PBW)
  rule_refs:
  - RULE-VENTILACAO-001
- citation: Amato MB et al. NEJM 2015;372:747 (plateau/driving pressure ≤30 cmH2O)
  rule_refs: []
ratify_pending:
- anchor: RAT-VENTILACAO-02
  rule: RULE-VENTILACAO-003
  band: P1
  note: 'lung-protective VT: recommended default >6 mL/kg-PBW replaces legacy absolute >500 mL'
- anchor: RAT-VENTILACAO-03
  rule: RULE-VENTILACAO-004
  band: P1
  note: PEEP/FiO2 table adequacy (FiO2 fraction, restore PEEP>0 guard) — captured not fired until ratified
- anchor: RAT-VENTILACAO-04
  rule: RULE-VENTILACAO-005
  band: P1
  note: severe PEEP/FiO2 table (FiO2 fraction) — captured not fired until ratified
suppression:
  dedup_key: patient_id+alert_id+stage
  cooldown: PT6H
  rate_limit: 3/24h/patient
  maintenance_window_aware: true
  note: Re-fires only on a stage ESCALATION (leve->moderada->grave) within the cooldown; a de-escalation
    or a same-stage re-read is suppressed. Degrades to 'insufficient data' if FiO2/SpO2 stale or Berlin
    qualifiers absent.
ppv_budget:
  target_ppv: 0.65
  est_volume_per_100_beds_day: 7
  rationale: '~40 of 100 ICU beds ventilated; ARDS prevalence ~23% of ventilated (~9 patients). Gating
    on VM + PEEP>=5 + bilateral infiltrates + cardiogenic exclusion, staged with escalation-only re-fire,
    yields ~7 firings/day (mostly initial staging + true escalations). The Berlin qualifier gate is the
    PPV lever: an ungated S/F band alone would flood the channel with atelectasis/effusion desaturations.
    Target 0.65 > fleet floor 0.60.'
response:
  required: avaliação médica beira-leito; considerar ventilação protetora e (se P/F<150) prona (PROSEVA)
  ack_sla: PT30M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    saturacao_o2: 90
    fio2: 0.6
    peep: 8
    infiltrado_bilateral: true
    edema_cardiogenico_excluido: true
  expected: fire
  note: S/F = 90/0.60 = 150 -> moderada (URGENT); gate satisfied
- id: TV-2
  kind: fire
  inputs:
    saturacao_o2: 88
    fio2: 0.9
    peep: 12
    infiltrado_bilateral: true
    edema_cardiogenico_excluido: true
  expected: fire
  note: S/F = 88/0.90 = 97.8 <=148 -> grave (CRITICAL)
- id: TV-3
  kind: boundary
  inputs:
    saturacao_o2: 94.5
    fio2: 0.3
    peep: 5
    infiltrado_bilateral: true
    edema_cardiogenico_excluido: true
  expected: no-fire
  note: 'S/F = 94.5/0.30 = 315 exactly; leve requires S/F<=315 AND >235 -> 315 is <=315 so FIRES leve.
    Boundary: at S/F=316 (94.8/0.30) no-fire. Documented exact-threshold at 315.'
- id: TV-4
  kind: no-fire
  inputs:
    saturacao_o2: 90
    fio2: 0.6
    peep: 8
    infiltrado_bilateral: false
    edema_cardiogenico_excluido: true
  expected: no-fire
  note: S/F=150 but no bilateral infiltrates -> Berlin gate fails -> suppressed
- id: TV-5
  kind: no-fire
  inputs:
    saturacao_o2: 97
    fio2: 0.21
    peep: 5
    infiltrado_bilateral: true
    edema_cardiogenico_excluido: true
  expected: no-fire
  note: S/F = 97/0.21 = 462 > 315 -> no ARDS band
- id: TV-6
  kind: fire
  inputs:
    saturacao_o2: 92
    fio2: 0.5
    pao2: 75
    peep: 10
    infiltrado_bilateral: true
    edema_cardiogenico_excluido: true
  expected: fire
  note: 'ABG present: P/F = 75/0.50 = 150 -> moderada; P/F authoritative overrides S/F=184'
reconciliation:
- existing_id: RESP-001
  status: changed
  note: vs docs/clinical/alert-catalog.md — mild ARDS (S/F<=315, WARN) folded as the WATCH tier of the
    staged alert; no longer a standalone channel.
- existing_id: RESP-002
  status: extended
  note: moderate (S/F<=235, URG) and severe/002b (S/F<=148, CRIT) consolidated into one staged alert with
    URGENT/CRITICAL tiers; adds Berlin qualifiers (PEEP>=5, infiltrates, cardiac exclusion) and lung-protective
    companion.
```

<a id="alert-resp-deterioration-02"></a>
### ALERT-RESP-DETERIORATION-02 — Deterioração ventilatória — tendência S/F e demanda de FiO2

**Severity** urgent · **Evidence** Rice TW et al. Chest 2017 (SpO2/FiO2 trend; vision VIS-3.3-05); catalog RESP-003 (deterioração ventilatória — tendência SpO2/FiO2) · **Rules** RULE-VENTILACAO-017 · **PPV target** 0.6 · **Est. volume** 6/100 beds/day

```yaml alert-spec
alert_id: ALERT-RESP-DETERIORATION-02
name: Deterioração ventilatória — tendência S/F e demanda de FiO2
severity: urgent
trigger:
  logic: ventilatory_deterioration := (delta_sf_ratio_6h <= -0.20 * relacao_spo2_fio2_6h_ago) OR (fio2_atual
    > 1.30 * fio2_6h_ago AND saturacao_o2_atual <= saturacao_o2_6h_ago). FiO2 is a FRACTION throughout.
    Requires persistence across >=2 consecutive S/F samples; excludes readings within a documented airway-maintenance
    event (suction/turn).
  window: PT6H
inputs:
- name: relacao_spo2_fio2
  type: quantity
  unit: ratio
  source: derived = SpO2 / FiO2(fraction); 6h lookback
  staleness_max: PT15M
- name: fio2
  type: quantity
  unit: fraction
  source: ventilator OBX / Observation LOINC 19935-6; 6h lookback
  staleness_max: PT15M
- name: saturacao_o2
  type: quantity
  unit: percent
  source: AMH Gold Observation LOINC 2708-6; 6h lookback
  staleness_max: PT15M
evidence:
- citation: Rice TW et al. Chest 2017 (SpO2/FiO2 trend; vision VIS-3.3-05)
  rule_refs: []
- citation: catalog RESP-003 (deterioração ventilatória — tendência SpO2/FiO2)
  rule_refs:
  - RULE-VENTILACAO-017
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT4H
  rate_limit: 4/24h/patient
  maintenance_window_aware: true
  note: 'Transient desaturation guard: fall must persist >=2 samples; airway-maintenance readings excluded
    to protect PPV.'
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 6
  rationale: Trend alerts are intrinsically noisier than static bands (suctioning, turning, transient
    shunt). The >=2-sample persistence requirement and airway-event exclusion cut the raw ~12/day of >20%
    S/F dips to ~6 actionable firings across ~40 ventilated beds. Target sits at the fleet floor 0.60
    — the persistence guard is what keeps it there.
response:
  required: reavaliação ventilatória beira-leito; investigar causa (secreção, pneumotórax, progressão
    SDRA)
  ack_sla: PT30M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    relacao_spo2_fio2: 180
    relacao_spo2_fio2_6h_ago: 240
  expected: fire
  note: ΔS/F = -60 = -25% of 240 (<= -20%) -> fire (2 samples confirm)
- id: TV-2
  kind: fire
  inputs:
    fio2: 0.7
    fio2_6h_ago: 0.5
    saturacao_o2: 92
    saturacao_o2_6h_ago: 94
  expected: fire
  note: FiO2 0.70 > 1.30*0.50=0.65 AND SpO2 not improved -> escalating O2 demand
- id: TV-3
  kind: boundary
  inputs:
    relacao_spo2_fio2: 192
    relacao_spo2_fio2_6h_ago: 240
  expected: no-fire
  note: ΔS/F = -48 = exactly -20% of 240; rule is <= -20% so -20% FIRES. At -19.9% (S/F 192.2) no-fire.
    Documented exact -20% boundary.
- id: TV-4
  kind: no-fire
  inputs:
    fio2: 0.6
    fio2_6h_ago: 0.5
    saturacao_o2: 97
    saturacao_o2_6h_ago: 93
  expected: no-fire
  note: FiO2 up but SpO2 improved (97>93) -> not deterioration; and 0.60 < 0.65 threshold
reconciliation:
- existing_id: RESP-003
  status: extended
  note: vs alert-catalog.md — same S/F/FiO2 trend logic; adds >=2-sample persistence + airway-maintenance
    exclusion for alarm-fatigue; FiO2 explicitly fraction.
```

<a id="alert-resp-asynchrony-03"></a>
### ALERT-RESP-ASYNCHRONY-03 — Assincronia paciente-ventilador

**Severity** watch · **Evidence** Thille AW et al. Intensive Care Med 2016 (patient-ventilator asynchrony; vision VIS-3.3-06); Amato MB et al. NEJM 2015;372:747 (plateau ≤30 cmH2O) · **Rules** RULE-VENTILACAO-017 · **PPV target** 0.6 · **Est. volume** 4/100 beds/day

```yaml alert-spec
alert_id: ALERT-RESP-ASYNCHRONY-03
name: Assincronia paciente-ventilador
severity: watch
trigger:
  logic: ventilator_asynchrony := on_mechanical_ventilation AND frequencia_respiratoria > frequencia_respiratoria_programada
    AND (pressao_plato present AND pressao_plato > 30 cmH2O). Degrades to 'insufficient data' when plateau
    absent — does NOT fire on RR criterion alone.
  window: PT1H
inputs:
- name: frequencia_respiratoria
  type: quantity
  unit: rpm
  source: AMH Gold Observation LOINC 9279-1 (spontaneous)
  staleness_max: PT1H
- name: frequencia_respiratoria_programada
  type: quantity
  unit: rpm
  source: ventilator OBX (set RR; see domain OQ-1)
  staleness_max: PT1H
- name: pressao_plato
  type: quantity
  unit: cmH2O
  source: ventilator OBX (optional)
  staleness_max: PT1H
evidence:
- citation: Thille AW et al. Intensive Care Med 2016 (patient-ventilator asynchrony; vision VIS-3.3-06)
  rule_refs: []
- citation: Amato MB et al. NEJM 2015;372:747 (plateau ≤30 cmH2O)
  rule_refs:
  - RULE-VENTILACAO-017
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT8H
  rate_limit: 2/24h/patient
  maintenance_window_aware: true
  note: Titration prompt; long cooldown avoids repeat firing while settings/sedation are being adjusted.
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 4
  rationale: Requires both spontaneous-RR-above-set-RR AND plateau>30 (Média ventilator availability,
    so many patients lack plateau and are excluded). Across ~40 ventilated beds with an 8h cooldown, ~4
    firings/day. Watch severity keeps it out of the high-acuity channel; the plateau conjunction is what
    lifts PPV to the 0.60 floor.
response:
  required: ajuste de ventilação/sedação-analgesia; avaliar modo e trigger
  ack_sla: PT2H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    frequencia_respiratoria: 32
    frequencia_respiratoria_programada: 16
    pressao_plato: 34
  expected: fire
  note: spont RR 32 > set 16 AND plateau 34 > 30 -> fire
- id: TV-2
  kind: no-fire
  inputs:
    frequencia_respiratoria: 32
    frequencia_respiratoria_programada: 16
    pressao_plato: 26
  expected: no-fire
  note: RR high but plateau 26 <= 30 -> no fire
- id: TV-3
  kind: boundary
  inputs:
    frequencia_respiratoria: 17
    frequencia_respiratoria_programada: 16
    pressao_plato: 31
  expected: fire
  note: spont RR 17 > set 16 (strict >) AND plateau 31 > 30 -> fire; at RR 16==16 no-fire. Documented
    RR strict-inequality boundary.
- id: TV-4
  kind: no-fire
  inputs:
    frequencia_respiratoria: 32
    frequencia_respiratoria_programada: 16
    pressao_plato: null
  expected: no-fire
  note: plateau absent -> insufficient data, no fire on RR alone
reconciliation:
- existing_id: null
  status: new
  note: No catalog RESP-* for asynchrony; net-new from vision VIS-3.3-06 (Assincronia ventilatória).
```

<a id="alert-resp-weaning-ready-04"></a>
### ALERT-RESP-WEANING-READY-04 — Prontidão para desmame / extubação

**Severity** normal · **Evidence** Boles JM et al. Eur Respir J 2007;29:1033-1056 (ERS/ATS weaning consensus; catalog RESP-004); Yang KL, Tobin MJ. NEJM 1991;324:1445-1450 (RSBI <105); Sessler CN et al. AJRCCM 2002 (RASS); Teasdale G. 1974 (GCS) · **Rules** RULE-VENTILACAO-007, RULE-VENTILACAO-017 · **PPV target** 0.7 · **Est. volume** 3/100 beds/day

```yaml alert-spec
alert_id: ALERT-RESP-WEANING-READY-04
name: Prontidão para desmame / extubação
severity: normal
trigger:
  logic: 'weaning_ready := ALL sustained >= 2h: relacao_spo2_fio2 > 315 (S/F; ~P/F>300) AND peep <= 8
    cmH2O AND fio2 <= 0.40 (FRACTION; pending RAT-VENTILACAO-06 / P0) AND (indice_respiracao_rapida_superficial
    < 105 if present) AND rass >= -2 AND glasgow > 8 AND dose_vasopressor <= 0.2 mcg/kg/min AND dias_em_ventilacao_mecanica
    >= 1 (pending RAT-VENTILACAO-01). Controlled-mode check uses modalidade_ventilatoria (corrects legacy
    C4 dispositivo/modalidade mismatch).'
  window: PT2H
inputs:
- name: relacao_spo2_fio2
  type: quantity
  unit: ratio
  source: derived = SpO2 / FiO2(fraction)
  staleness_max: PT15M
- name: peep
  type: quantity
  unit: cmH2O
  source: ventilator OBX / Observation LOINC 20077-4
  staleness_max: PT1H
- name: fio2
  type: quantity
  unit: fraction
  source: ventilator OBX / Observation LOINC 19935-6
  staleness_max: PT15M
- name: indice_respiracao_rapida_superficial
  type: quantity
  unit: ratio
  source: derived = RR / VT(L) (RSBI)
  staleness_max: PT1H
- name: rass
  type: quantity
  unit: points
  source: sedacao domain, Observation LOINC 75826-6
  staleness_max: PT4H
- name: glasgow
  type: quantity
  unit: points
  source: AMH Gold Observation LOINC 9269-2
  staleness_max: PT8H
- name: dose_vasopressor
  type: quantity
  unit: mcg/kg/min
  source: hemodynamics domain (MedicationAdministration)
  staleness_max: PT1H
- name: dias_em_ventilacao_mecanica
  type: quantity
  unit: count
  source: derived (see domain OQ-2)
  staleness_max: PT1H
evidence:
- citation: Boles JM et al. Eur Respir J 2007;29:1033-1056 (ERS/ATS weaning consensus; catalog RESP-004)
  rule_refs:
  - RULE-VENTILACAO-017
- citation: Yang KL, Tobin MJ. NEJM 1991;324:1445-1450 (RSBI <105)
  rule_refs: []
- citation: Sessler CN et al. AJRCCM 2002 (RASS); Teasdale G. 1974 (GCS)
  rule_refs:
  - RULE-VENTILACAO-007
ratify_pending:
- anchor: RAT-VENTILACAO-06
  rule: RULE-VENTILACAO-011
  band: P0
  note: extubation-readiness FiO2 fraction (<=0.40); mission-law number, committee confirms the alert-forcing
    bundle
- anchor: RAT-VENTILACAO-01
  rule: RULE-VENTILACAO-002
  band: UNVERIFIABLE
  note: 'days-on-VM primitive: whole elapsed days, no abs() on future timestamps'
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT12H
  rate_limit: 2/24h/patient
  maintenance_window_aware: true
  note: Positive opportunity prompt; long cooldown so a persistently-ready patient does not re-nag once
    an SBT is planned.
ppv_budget:
  target_ppv: 0.7
  est_volume_per_100_beds_day: 3
  rationale: Fires when a ventilated patient first meets ALL readiness criteria sustained 2h — a genuine
    SBT opportunity. Across ~40 ventilated beds, ~3/day become newly ready. 'PPV' here = truly SBT-eligible;
    the conjunctive bundle (oxygenation + low support + arousal + no high vasopressor) makes it specific,
    so target 0.70. Normal severity, so it never competes with deterioration alerts for attention.
response:
  required: considerar teste de respiração espontânea (TRE/SBT) e avaliação de extubação
  ack_sla: PT6H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    relacao_spo2_fio2: 350
    peep: 5
    fio2: 0.3
    indice_respiracao_rapida_superficial: 80
    rass: -1
    glasgow: 14
    dose_vasopressor: 0.0
    dias_em_ventilacao_mecanica: 3
  expected: fire
  note: all criteria met, sustained 2h -> ready
- id: TV-2
  kind: no-fire
  inputs:
    relacao_spo2_fio2: 350
    peep: 5
    fio2: 0.3
    indice_respiracao_rapida_superficial: 120
    rass: -1
    glasgow: 14
    dose_vasopressor: 0.0
    dias_em_ventilacao_mecanica: 3
  expected: no-fire
  note: RSBI 120 >= 105 -> not ready (rapid shallow breathing)
- id: TV-3
  kind: boundary
  inputs:
    relacao_spo2_fio2: 316
    peep: 8
    fio2: 0.4
    indice_respiracao_rapida_superficial: 104
    rass: -2
    glasgow: 9
    dose_vasopressor: 0.2
    dias_em_ventilacao_mecanica: 1
  expected: fire
  note: every criterion at its exact boundary (S/F>315 so 316 ok; PEEP<=8; FiO2<=0.40; RSBI<105; RASS>=-2;
    GCS>8 so 9 ok; vaso<=0.2; days>=1) -> fire
- id: TV-4
  kind: no-fire
  inputs:
    relacao_spo2_fio2: 350
    peep: 5
    fio2: 0.3
    indice_respiracao_rapida_superficial: 80
    rass: -4
    glasgow: 6
    dose_vasopressor: 0.0
    dias_em_ventilacao_mecanica: 3
  expected: no-fire
  note: RASS -4 (< -2) deep sedation AND GCS 6 (<=8) -> not arousable
- id: TV-5
  kind: no-fire
  inputs:
    relacao_spo2_fio2: 350
    peep: 5
    fio2: 0.3
    indice_respiracao_rapida_superficial: 80
    rass: -1
    glasgow: 14
    dose_vasopressor: 0.5
    dias_em_ventilacao_mecanica: 3
  expected: no-fire
  note: vasopressor 0.5 > 0.2 mcg/kg/min -> hemodynamically unfit for weaning
reconciliation:
- existing_id: RESP-004
  status: extended
  note: vs alert-catalog.md — RESP-004 readiness bundle (INFO->normal); adds RULE-VENTILACAO-007 arousal
    disjunct (RASS/GCS), corrected FiO2 fraction (RAT-VENTILACAO-06), modalidade-field controlled-mode
    fix, days-on-VM floor (RAT-VENTILACAO-01).
```

<a id="alert-resp-prolonged-intub-05"></a>
### ALERT-RESP-PROLONGED-INTUB-05 — Intubação prolongada — avaliar traqueostomia

**Severity** watch · **Evidence** Young D et al. JAMA 2013;309(20):2121-2129 (TracMan; tracheostomy timing); AAO-HNS COVID-19 tracheostomy guidelines 2020 (defer to >=14 days) · **Rules** RULE-VENTILACAO-008 · **PPV target** 0.75 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-RESP-PROLONGED-INTUB-05
name: Intubação prolongada — avaliar traqueostomia
severity: watch
trigger:
  logic: 'prolonged_intubation := dispositivo_via_aerea == "TOT" AND dias_em_ventilacao_mecanica > 10.
    COVID companion (pending RAT-VENTILACAO-05): if covid19_ativo == true, use threshold dias_em_ventilacao_mecanica
    >= 14 (AAO-HNS 2020 recommended default) instead of >10.'
  window: P1D
inputs:
- name: dispositivo_via_aerea
  type: enum
  unit: enum
  source: clinical form / EMR (see domain §6)
  staleness_max: PT12H
- name: dias_em_ventilacao_mecanica
  type: quantity
  unit: count
  source: derived (see domain OQ-2 / RAT-VENTILACAO-01)
  staleness_max: PT1H
- name: covid19_ativo
  type: boolean
  unit: boolean
  source: Condition (COVID-19)
  staleness_max: PT7D
evidence:
- citation: Young D et al. JAMA 2013;309(20):2121-2129 (TracMan; tracheostomy timing)
  rule_refs:
  - RULE-VENTILACAO-008
- citation: AAO-HNS COVID-19 tracheostomy guidelines 2020 (defer to >=14 days)
  rule_refs: []
ratify_pending:
- anchor: RAT-VENTILACAO-05
  rule: RULE-VENTILACAO-009
  band: P1
  note: 'COVID tracheostomy timing: code >10d vs facade/guideline >14d; recommended default >=14d for
    active COVID'
- anchor: RAT-VENTILACAO-01
  rule: RULE-VENTILACAO-002
  band: UNVERIFIABLE
  note: days-on-VM primitive correction
suppression:
  dedup_key: patient_id+alert_id
  cooldown: P3D
  rate_limit: 1/admission/patient
  maintenance_window_aware: true
  note: Fires once at the threshold crossing per admission; deduped so the trach discussion is prompted
    a single time.
ppv_budget:
  target_ppv: 0.75
  est_volume_per_100_beds_day: 2
  rationale: Deterministic duration trigger (TOT + >10 days), fired once per admission. Across a 100-bed
    ICU with typical VM durations, ~1-2 patients/day cross day 10 still orotracheally intubated. High
    actionability (multidisciplinary trach-timing decision) gives target 0.75; the once-per-admission
    dedup keeps volume minimal.
response:
  required: discussão multidisciplinar de traqueostomia (timing, elegibilidade)
  ack_sla: PT12H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    dispositivo_via_aerea: TOT
    dias_em_ventilacao_mecanica: 12
    covid19_ativo: false
  expected: fire
  note: TOT 12 days > 10 (non-COVID) -> fire
- id: TV-2
  kind: no-fire
  inputs:
    dispositivo_via_aerea: TQT
    dias_em_ventilacao_mecanica: 20
    covid19_ativo: false
  expected: no-fire
  note: already tracheostomized (TQT) -> excluded from the intubation timer
- id: TV-3
  kind: boundary
  inputs:
    dispositivo_via_aerea: TOT
    dias_em_ventilacao_mecanica: 10
    covid19_ativo: false
  expected: no-fire
  note: exactly 10 days; rule is strict >10 so day 10 no-fire, day 11 fires. Documented day-10 boundary.
- id: TV-4
  kind: no-fire
  inputs:
    dispositivo_via_aerea: TOT
    dias_em_ventilacao_mecanica: 12
    covid19_ativo: true
  expected: no-fire
  note: active COVID uses >=14d threshold (RAT-VENTILACAO-05); 12 < 14 -> deferred, no-fire
- id: TV-5
  kind: fire
  inputs:
    dispositivo_via_aerea: TOT
    dias_em_ventilacao_mecanica: 14
    covid19_ativo: true
  expected: fire
  note: active COVID at 14 days (>=14) -> fire
reconciliation:
- existing_id: null
  status: new
  note: No catalog RESP-* for tracheostomy timing; net-new to the respiratory alert set from legacy RULE-VENTILACAO-008
    (ADOPT) + -009 (RATIFY).
```

## hemodynamics (6 alerts)

<a id="alert-hemo-shock-index-01"></a>
### ALERT-HEMO-SHOCK-INDEX-01 — Índice de choque elevado — hipoperfusão oculta

**Severity** watch · **Evidence** Rady MY et al. Ann Emerg Med 1994;24(4):685-693 (shock index vs isolated vital signs); Liu YC et al. Crit Care 2012;16:R150 (modified shock index HR/MAP >1.3); Cannon CM et al. West J Emerg Med 2011;12(4):459-464; Hernandez G et al. ANDROMEDA-SHOCK, JAMA 2019;321(7):654-664 (capillary refill >3 s as perfusion target); Singer M et al. JAMA 2016;315(8):801-810 (lactate >2 mmol/L hypoperfusion) · **Rules** RULE-ESTABILIDADE-002, RULE-ESTABILIDADE-003 · **PPV target** 0.6 · **Est. volume** 5/100 beds/day

```yaml alert-spec
alert_id: ALERT-HEMO-SHOCK-INDEX-01
name: Índice de choque elevado — hipoperfusão oculta
severity: watch
trigger:
  logic: ( indice_choque > 0.9 ratio OR ( frequencia_cardiaca / pressao_arterial_media ) > 1.3 ratio )
    sustained > PT15M AND ( lactato_arterial > 2 mmol/L OR tempo_enchimento_capilar > 3 s ); indice_choque
    := frequencia_cardiaca(bpm) / pressao_arterial_sistolica(mmHg) (classic SI, Rady 1994); modified SI
    := frequencia_cardiaca / pressao_arterial_media (Liu 2012). The perfusion corroborator (lactate>2
    OR TEC>3s) is what lifts PPV above the 0.60 fleet floor — isolated shock index has low specificity.
    Legacy RULE-ESTABILIDADE-002 used the more sensitive SI>0.7 / MSI>0.9 cutoffs; v2 adopts the vision/catalog-anchored
    SI>0.9 / MSI>1.3 (higher specificity). PT-BR display vocabulary 'Indice de choque positivo' preserved
    verbatim (CLU-ESTABILIDADE-20).
  window: PT15M
inputs:
- name: frequencia_cardiaca
  type: quantity
  unit: bpm
  source: local TimescaleDB (invasive/multiparameter monitor, continuous) / AMH Gold Observation LOINC
    8867-4
  staleness_max: PT15M
- name: pressao_arterial_sistolica
  type: quantity
  unit: mmHg
  source: local TimescaleDB (invasive arterial line, continuous) / AMH Gold Observation LOINC 8480-6
  staleness_max: PT15M
- name: pressao_arterial_media
  type: quantity
  unit: mmHg
  source: local TimescaleDB (invasive arterial line, continuous) / AMH Gold Observation LOINC 8478-0
  staleness_max: PT15M
- name: indice_choque
  type: quantity
  unit: ratio
  source: hemodynamics domain (derived = HR/SBP)
  staleness_max: PT15M
- name: lactato_arterial
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result LOINC 2524-7
  staleness_max: PT4H
- name: tempo_enchimento_capilar
  type: quantity
  unit: s
  source: AMH Gold Observation (TEC bedside)
  staleness_max: PT6H
evidence:
- citation: Rady MY et al. Ann Emerg Med 1994;24(4):685-693 (shock index vs isolated vital signs)
  rule_refs:
  - RULE-ESTABILIDADE-002
- citation: Liu YC et al. Crit Care 2012;16:R150 (modified shock index HR/MAP >1.3); Cannon CM et al.
    West J Emerg Med 2011;12(4):459-464
  rule_refs: []
- citation: Hernandez G et al. ANDROMEDA-SHOCK, JAMA 2019;321(7):654-664 (capillary refill >3 s as perfusion
    target); Singer M et al. JAMA 2016;315(8):801-810 (lactate >2 mmol/L hypoperfusion)
  rule_refs:
  - RULE-ESTABILIDADE-003
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT2H
  rate_limit: 3/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 5
  rationale: Isolated shock index is a sensitive but low-specificity early marker (fires in pain/fever/anxiety/pacing/
    beta-blockade without shock). Requiring the elevated index to be SUSTAINED >15 min AND corroborated
    by a perfusion marker (lactate>2 mmol/L OR capillary refill>3 s) is what pulls PPV to the 0.60 fleet
    floor; it also lets one watch-severity alert replace the two separate vision alerts (classic + modified
    SI). Kept at WATCH (early trend, not immediate life threat) to protect the deterioration-alarm attention
    budget. ~5/100 beds/day given ICU tachycardia/hypotension prevalence; 2h cooldown prevents re-fire
    on the same episode.
response:
  required: avaliação de perfusão à beira-leito (lactato, TEC, diurese) e reavaliação volêmica
  ack_sla: PT2H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    frequencia_cardiaca: 120
    pressao_arterial_sistolica: 100
    indice_choque: 1.2
    lactato_arterial: 3.1
  expected: fire
  note: SI=1.2 (>0.9) sustained with lactate>2 mmol/L — corroborated occult hypoperfusion
- id: TV-2
  kind: fire
  inputs:
    frequencia_cardiaca: 110
    pressao_arterial_media: 78
    lactato_arterial: 1.5
    tempo_enchimento_capilar: 4.0
  expected: fire
  note: modified SI=110/78=1.41 (>1.3) with capillary refill 4 s (>3 s) — MSI branch + TEC corroborator
- id: TV-3
  kind: no-fire
  inputs:
    frequencia_cardiaca: 120
    pressao_arterial_sistolica: 100
    indice_choque: 1.2
    lactato_arterial: 1.4
    tempo_enchimento_capilar: 2.0
  expected: no-fire
  note: SI elevated but NO perfusion corroborator (lactate<2 and TEC<3s) — suppressed for PPV protection
- id: TV-4
  kind: boundary
  inputs:
    frequencia_cardiaca: 90
    pressao_arterial_sistolica: 100
    indice_choque: 0.9
    lactato_arterial: 3.0
  expected: no-fire
  note: 'boundary exact-threshold: SI=0.90 is NOT >0.9 (strict); index band not met even with high lactate'
- id: TV-5
  kind: boundary
  inputs:
    frequencia_cardiaca: 91
    pressao_arterial_sistolica: 100
    indice_choque: 0.91
    lactato_arterial: 2.01
  expected: fire
  note: 'boundary: SI=0.91 (>0.9) with lactate 2.01 (>2) both just above threshold — fires'
reconciliation:
- existing_id: HEMO-001
  status: changed
  note: 'vs alert-catalog.md HEMO-001 ''Shock Index > 0,9 — hipoperfusão oculta'' (URG/P2): legacy fired
    on SI>0.9 OR MSI>1.3 sustained >15 min with no corroborator. v2 changes it by adding a mandatory perfusion
    corroborator (lactato>2 mmol/L OR TEC>3 s) to lift PPV to the 0.60 floor and defeat the pain/pacing/beta-blockade
    false-positive flood, and lowers severity URG->watch (early trend, not immediate threat). Both classic
    and modified SI retained as OR branches; thresholds 0.9/1.3 kept.'
```

<a id="alert-hemo-lactate-clearance-02"></a>
### ALERT-HEMO-LACTATE-CLEARANCE-02 — Clearance de lactato inadequado

**Severity** critical · **Evidence** Jones AE et al. JAMA 2010;303(8):739-746 (lactate clearance >=10% at 2h non-inferior to ScvO2); Jansen TC et al. Am J Respir Crit Care Med 2010;182(6):752-761 (lactate-guided therapy); Evans L et al. SSC 2021, Crit Care Med 2021;49(11):e1063-e1143 (lactate-guided resuscitation, remeasure within 2-4h); Singer M et al. JAMA 2016 (lactate >2 mmol/L) · **Rules** RULE-ESTABILIDADE-003, RULE-ESTABILIDADE-020 · **PPV target** 0.7 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-HEMO-LACTATE-CLEARANCE-02
name: Clearance de lactato inadequado
severity: critical
trigger:
  logic: "active_resuscitation AND lactato_inicial >= 2 mmol/L AND ( clearance_lactato_2h < 10 percent\n\
    \      OR lactato_6h > 2 mmol/L );\nclearance_lactato_2h := (lactato_inicial - lactato_2h) / lactato_inicial\
    \ * 100 (Jones 2010 JAMA); active_resuscitation := fluid_bolus_given OR dose_vasopressor > 0 mcg/kg/min\
    \ OR sepsis.shock.detected received in the last PT6H. Lactate is mmol/L ONLY (mission law, SYS-03);\
    \ a lactate value with no unit is a build-time error. Anchored to Jones 2010 (10% 2-hour clearance)\
    \ and SSC-2021 lactate-guided resuscitation."
  window: PT6H
inputs:
- name: lactato_inicial
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result LOINC 2524-7 (resuscitation baseline)
  staleness_max: PT6H
- name: lactato_2h
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result LOINC 2524-7 (2h repeat)
  staleness_max: PT4H
- name: lactato_6h
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result LOINC 2524-7 (6h repeat)
  staleness_max: PT4H
- name: clearance_lactato_2h
  type: quantity
  unit: percent
  source: hemodynamics domain (derived = (inicial-2h)/inicial*100)
  staleness_max: PT4H
- name: dose_vasopressor
  type: quantity
  unit: mcg/kg/min
  source: hemodynamics domain (conversion service, mL/h->mcg/kg/min)
  staleness_max: PT1H
- name: fluid_bolus_given
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration (crystalloid bolus, 6h lookback)
  staleness_max: PT6H
evidence:
- citation: Jones AE et al. JAMA 2010;303(8):739-746 (lactate clearance >=10% at 2h non-inferior to ScvO2);
    Jansen TC et al. Am J Respir Crit Care Med 2010;182(6):752-761 (lactate-guided therapy)
  rule_refs: []
- citation: Evans L et al. SSC 2021, Crit Care Med 2021;49(11):e1063-e1143 (lactate-guided resuscitation,
    remeasure within 2-4h); Singer M et al. JAMA 2016 (lactate >2 mmol/L)
  rule_refs:
  - RULE-ESTABILIDADE-020
  - RULE-ESTABILIDADE-003
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT2H
  rate_limit: 4/24h/patient
  maintenance_window_aware: false
ppv_budget:
  target_ppv: 0.7
  est_volume_per_100_beds_day: 2
  rationale: Gated on ACTIVE resuscitation (fluid bolus / vasopressor / a received sepsis.shock.detected
    event), so it fires only when the clearance question is clinically live — this is what keeps PPV high
    despite lactate's known non-shock confounders (hepatopathy, epinephrine, metformin, seizures). Lactate
    can fail to clear for non-perfusion reasons, so PPV is targeted 0.70 not higher. maintenance_window_aware:false
    — a critical resuscitation-failure signal must never be muted by a maintenance window. ~2/100 beds/day
    (shock incidence x resuscitation subset). One critical alert covering both the 2h-clearance and 6h-persistence
    branches.
response:
  required: reavaliação imediata da ressuscitação (fonte de choque, volemia, vasopressor) + medir lactato
    seriado
  ack_sla: PT5M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    lactato_inicial: 4.0
    lactato_2h: 3.8
    clearance_lactato_2h: 5.0
    fluid_bolus_given: true
  expected: fire
  note: baseline>=2, clearance 5% (<10%) at 2h during active resuscitation
- id: TV-2
  kind: fire
  inputs:
    lactato_inicial: 3.0
    lactato_6h: 2.6
    dose_vasopressor: 0.2
  expected: fire
  note: lactate persistently >2 mmol/L at 6h despite active vasopressor resuscitation (persistence branch)
- id: TV-3
  kind: no-fire
  inputs:
    lactato_inicial: 4.0
    lactato_2h: 2.8
    clearance_lactato_2h: 30.0
    lactato_6h: 1.8
    fluid_bolus_given: true
  expected: no-fire
  note: clearance 30% (>=10%) and 6h lactate <2 — adequate resuscitation response
- id: TV-4
  kind: no-fire
  inputs:
    lactato_inicial: 4.0
    lactato_2h: 3.8
    clearance_lactato_2h: 5.0
    dose_vasopressor: 0
    fluid_bolus_given: false
  expected: no-fire
  note: poor clearance but NO active resuscitation — gate not met (not a resuscitation-failure context)
- id: TV-5
  kind: boundary
  inputs:
    lactato_inicial: 2.0
    lactato_2h: 1.8
    clearance_lactato_2h: 10.0
    lactato_6h: 2.0
    fluid_bolus_given: true
  expected: no-fire
  note: 'boundary exact-threshold: clearance=10.0 is NOT <10 (strict) AND lactato_6h=2.0 is NOT >2 (strict)
    — both branches excluded'
- id: TV-6
  kind: boundary
  inputs:
    lactato_inicial: 2.0
    lactato_2h: 1.82
    clearance_lactato_2h: 9.0
    fluid_bolus_given: true
  expected: fire
  note: 'boundary: baseline exactly 2.0 (>=2 inclusive) with clearance 9% (<10) fires'
reconciliation:
- existing_id: HEMO-002
  status: aligned
  note: 'vs alert-catalog.md HEMO-002 ''Clearance de lactato < 10% em 2h'' (CRIT/P2): carried forward
    essentially unchanged — baseline lactate>=2 mmol/L AND (2h clearance<10% OR 6h lactate>2 mmol/L after
    resuscitation). v2 makes the implicit ''após ressuscitação ativa'' condition an explicit active_resuscitation
    gate and pins lactate to canonical mmol/L; severity critical and the Jones 2010 anchor are unchanged.'
```

<a id="alert-hemo-vaso-escalation-03"></a>
### ALERT-HEMO-VASO-ESCALATION-03 — Escalonamento de vasopressor

**Severity** urgent · **Evidence** SCCM/Society of Critical Care Medicine 2024 Adult Vasopressor Guidance; Evans L et al. SSC 2021, Crit Care Med 2021;49(11):e1063-e1143 (vasopressor escalation, add vasopressin then epinephrine); Vasopressor-adjunct escalation rung (high-dose NE without vasopressin/hydrocortisone), reference-corrected inclusive boundary + mcg/kg/min canonicalization · **Rules** RULE-ESTABILIDADE-014, RULE-ESTABILIDADE-018, RULE-ESTABILIDADE-019, RULE-ESTABILIDADE-026 · **PPV target** 0.75 · **Est. volume** 3/100 beds/day

```yaml alert-spec
alert_id: ALERT-HEMO-VASO-ESCALATION-03
name: Escalonamento de vasopressor
severity: urgent
trigger:
  logic: "dose_vasopressor > 0 mcg/kg/min AND ( dose_vasopressor > 1.5 * dose_vasopressor_2h_atras   \
    \  # >50% increase in PT2H\n      OR second_vasopressor_started_2h );                    # 2nd agent\
    \ added while NE active\nsecond_vasopressor_started_2h := any of {dose_vasopressina > 0 U/min, dose_adrenalina\
    \ > 0 mcg/kg/min, dose_dobutamina > 0 mcg/kg/min} newly started within PT2H while norepinephrine already\
    \ active. ALL weight-indexed doses are canonical mcg/kg/min produced by #vasopressor-unit-conversion-service\
    \ from an edge mL/h rate + concentracao_farmaco + peso (mL/h is NOT convertible without both; SYS-C-04\
    \ / CON-0060). Vasopressin is U/min (fixed-rate, never coerced to mcg/kg/min). The >50%/2nd-agent\
    \ TREND logic is SCCM-2024 anchored and unit-safe; the disputed ABSOLUTE ladder cutoffs (>0.5, >1.5\
    \ mcg/kg/min) are pending RAT-ESTABILIDADE-08 (P0, RULE-ESTABILIDADE-016) and NOT used as a firing\
    \ threshold here."
  window: PT2H
inputs:
- name: dose_vasopressor
  type: quantity
  unit: mcg/kg/min
  source: hemodynamics conversion service (MedicationAdministration mL/h + concentracao_farmaco + peso)
  staleness_max: PT1H
- name: dose_vasopressor_2h_atras
  type: quantity
  unit: mcg/kg/min
  source: hemodynamics conversion service (prior value, 2h lookback)
  staleness_max: PT2H
- name: dose_vasopressina
  type: quantity
  unit: U/min
  source: hemodynamics conversion service (MedicationAdministration; fixed-rate, NOT weight-indexed)
  staleness_max: PT1H
- name: dose_adrenalina
  type: quantity
  unit: mcg/kg/min
  source: hemodynamics conversion service (MedicationAdministration mL/h + concentracao + peso)
  staleness_max: PT1H
- name: dose_dobutamina
  type: quantity
  unit: mcg/kg/min
  source: hemodynamics conversion service (MedicationAdministration mL/h + concentracao + peso)
  staleness_max: PT1H
evidence:
- citation: SCCM/Society of Critical Care Medicine 2024 Adult Vasopressor Guidance; Evans L et al. SSC
    2021, Crit Care Med 2021;49(11):e1063-e1143 (vasopressor escalation, add vasopressin then epinephrine)
  rule_refs:
  - RULE-ESTABILIDADE-014
  - RULE-ESTABILIDADE-018
  - RULE-ESTABILIDADE-026
- citation: Vasopressor-adjunct escalation rung (high-dose NE without vasopressin/hydrocortisone), reference-corrected
    inclusive boundary + mcg/kg/min canonicalization
  rule_refs:
  - RULE-ESTABILIDADE-019
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT2H
  rate_limit: 4/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.75
  est_volume_per_100_beds_day: 3
  rationale: A dose-trend / second-agent alert is deterministic (a genuine >50% rate rise or a newly-added
    second vasoactive drug), so PPV is high by construction; the only false positives are transient titration
    blips, damped by the PT2H window and 2h cooldown. It is unit-SAFE because it compares canonical mcg/kg/min
    values from the conversion service — the exact defect (SYS-02, mL/h vs mcg/kg/min vs mcg/kg/h 60x
    drift) this domain owns. Kept URGENT (rapid escalation warrants action <30 min but is not itself the
    imminent-death event — that is REFRACTORY-SHOCK-04). One alert covers both 003a (dose rise) and 003b
    (2nd agent).
response:
  required: reavaliação médica do choque e da estratégia vasoativa (fonte, volemia, adjuvantes vasopressina/hidrocortisona)
  ack_sla: PT30M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    dose_vasopressor: 0.35
    dose_vasopressor_2h_atras: 0.2
  expected: fire
  note: NE 0.20->0.35 mcg/kg/min = 75% increase (>50%) in 2h
- id: TV-2
  kind: fire
  inputs:
    dose_vasopressor: 0.3
    dose_vasopressor_2h_atras: 0.28
    dose_vasopressina: 0.03
  expected: fire
  note: vasopressin (0.03 U/min, fixed-rate) newly added while NE active — 2nd-agent branch
- id: TV-3
  kind: no-fire
  inputs:
    dose_vasopressor: 0.22
    dose_vasopressor_2h_atras: 0.2
  expected: no-fire
  note: NE 0.20->0.22 = 10% increase (<50%), no 2nd agent — normal titration
- id: TV-4
  kind: no-fire
  inputs:
    dose_vasopressor: 0
    dose_vasopressor_2h_atras: 0
    dose_dobutamina: 5.0
  expected: no-fire
  note: dobutamine present but NO active norepinephrine (dose_vasopressor=0) — gate not met (inotrope-only,
    not vasopressor escalation)
- id: TV-5
  kind: boundary
  inputs:
    dose_vasopressor: 0.3
    dose_vasopressor_2h_atras: 0.2
  expected: no-fire
  note: 'boundary exact-threshold: 0.30 = exactly 1.5x0.20 = exactly 50% increase, NOT >50% (strict) —
    no fire'
- id: TV-6
  kind: boundary
  inputs:
    dose_vasopressor: 0.301
    dose_vasopressor_2h_atras: 0.2
  expected: fire
  note: 'boundary: 0.301 just above 1.5x0.20 (>50%) fires'
reconciliation:
- existing_id: HEMO-003
  status: changed
  note: 'vs alert-catalog.md HEMO-003 ''Escalonamento de vasopressor'' (CRIT/P2): legacy bundled three
    triggers (003a dose +50% in 2h, 003b 2nd agent added, 003c refractory NE>1.0 mcg/kg/min + MAP<65 >30
    min). v2 splits them: 003a+003b become this alert (severity urgent); 003c is promoted to the standalone
    ALERT-HEMO-REFRACTORY-SHOCK-04 (see its own reconciliation note). Changed because all dosing is now
    canonical mcg/kg/min from the vasopressor unit-conversion service (the audit''s #1 finding, SYS-02/CON-0060
    — legacy mixed mL, mL/h, mcg/kg/min, mcg/kg/h).'
```

<a id="alert-hemo-refractory-shock-04"></a>
### ALERT-HEMO-REFRACTORY-SHOCK-04 — Choque refratário — hipotensão sob vasopressor máximo

**Severity** critical · **Evidence** Asfar P et al. SEPSISPAM, N Engl J Med 2014;370(17):1583-1593 (MAP target in septic shock); Evans L et al. SSC 2021, Crit Care Med 2021;49(11):e1063-e1143 (refractory shock, MAP>=65, add vasopressin/hydrocortisone); SCCM 2024 Adult Vasopressor Guidance (high-dose refractory shock); high-dose-NE-without-adjuncts rung reference-corrected to inclusive boundary + mcg/kg/min · **Rules** RULE-ESTABILIDADE-019 · **PPV target** 0.8 · **Est. volume** 1/100 beds/day

```yaml alert-spec
alert_id: ALERT-HEMO-REFRACTORY-SHOCK-04
name: Choque refratário — hipotensão sob vasopressor máximo
severity: critical
trigger:
  logic: 'pressao_arterial_media < 65 mmHg sustained > PT30M AND dose_vasopressor > 1.0 mcg/kg/min;                       #
    norepinephrine-equivalent, canonical the >1.0 mcg/kg/min ''maximal vasopressor'' cutoff is the reference-anchored
    RECOMMENDED DEFAULT (vision VIS-3.4-06; SEPSISPAM Asfar 2014) pending RAT-ESTABILIDADE-08 (P0, RULE-ESTABILIDADE-016
    disputed ladder). dose_vasopressor is canonical mcg/kg/min from #vasopressor-unit-conversion-service
    (mL/h NOT convertible without concentration+weight; SYS-C-04). Enrichment (does not gate firing):
    flags absence of adjuncts (vasopressina/hidrocortisona) per the high-dose-NE-without-adjuncts rung
    (RULE-ESTABILIDADE-019). PT-BR display ''Noradrenalina >0,5mcg/kg/min, associar corticoide e vasopressina''
    preserved (CLU-ESTABILIDADE-20).'
  window: PT30M
inputs:
- name: pressao_arterial_media
  type: quantity
  unit: mmHg
  source: local TimescaleDB (invasive arterial line, continuous) / AMH Gold Observation LOINC 8478-0
  staleness_max: PT15M
- name: dose_vasopressor
  type: quantity
  unit: mcg/kg/min
  source: hemodynamics conversion service (MedicationAdministration mL/h + concentracao_farmaco + peso)
  staleness_max: PT1H
- name: dose_vasopressina
  type: quantity
  unit: U/min
  source: hemodynamics conversion service (MedicationAdministration; adjunct-presence enrichment)
  staleness_max: PT1H
- name: hidrocortisona_ativa
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration (hydrocortisone; adjunct-presence enrichment)
  staleness_max: PT6H
evidence:
- citation: Asfar P et al. SEPSISPAM, N Engl J Med 2014;370(17):1583-1593 (MAP target in septic shock);
    Evans L et al. SSC 2021, Crit Care Med 2021;49(11):e1063-e1143 (refractory shock, MAP>=65, add vasopressin/hydrocortisone)
  rule_refs: []
- citation: SCCM 2024 Adult Vasopressor Guidance (high-dose refractory shock); high-dose-NE-without-adjuncts
    rung reference-corrected to inclusive boundary + mcg/kg/min
  rule_refs:
  - RULE-ESTABILIDADE-019
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT1H
  rate_limit: 6/24h/patient
  maintenance_window_aware: false
ppv_budget:
  target_ppv: 0.8
  est_volume_per_100_beds_day: 1
  rationale: Narrow, high-mortality definition (MAP<65 sustained >30 min on >1.0 mcg/kg/min norepinephrine-equivalent)
    — unrecognized shock carries >80% mortality (VIS-3.4-01), so this is the domain's highest-PPV alert.
    The 30-min sustain window rejects transient dips; the high absolute-dose gate rejects the merely-hypotensive.
    maintenance_window_aware:false — never mute a refractory-shock alarm. ~1/100 beds/day. Kept separate
    from VASO-ESCALATION-03 because the response differs (immediate refractory-shock management + adjunct
    rescue, not just escalation review). The adjunct-absence flag enriches the response text without adding
    an alert.
response:
  required: 'ativação de resposta rápida — manejo de choque refratário: confirmar volemia, associar vasopressina
    + hidrocortisona se ausentes, considerar segunda linha (adrenalina)'
  ack_sla: PT5M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    pressao_arterial_media: 58
    dose_vasopressor: 1.4
    dose_vasopressina: 0
    hidrocortisona_ativa: false
  expected: fire
  note: MAP 58 (<65) sustained >30 min on NE 1.4 mcg/kg/min (>1.0); adjuncts absent -> rescue recommended
- id: TV-2
  kind: no-fire
  inputs:
    pressao_arterial_media: 58
    dose_vasopressor: 0.4
  expected: no-fire
  note: MAP<65 but NE 0.4 mcg/kg/min (<=1.0) — hypotensive but not on MAXIMAL vasopressor; routes to VASO-ESCALATION-03
    if rising
- id: TV-3
  kind: no-fire
  inputs:
    pressao_arterial_media: 72
    dose_vasopressor: 1.5
  expected: no-fire
  note: high-dose NE but MAP 72 (>=65) — pressure target met, not refractory
- id: TV-4
  kind: boundary
  inputs:
    pressao_arterial_media: 65
    dose_vasopressor: 1.5
  expected: no-fire
  note: 'boundary exact-threshold: MAP=65 is NOT <65 (strict) — target met'
- id: TV-5
  kind: boundary
  inputs:
    pressao_arterial_media: 64
    dose_vasopressor: 1.0
  expected: no-fire
  note: 'boundary: dose=1.0 is NOT >1.0 (strict); MAP<65 but not on maximal dose per recommended-default
    cutoff (pending RAT-ESTABILIDADE-08)'
- id: TV-6
  kind: boundary
  inputs:
    pressao_arterial_media: 64
    dose_vasopressor: 1.01
  expected: fire
  note: 'boundary: MAP 64 (<65) with dose 1.01 (>1.0) both just past threshold — fires'
reconciliation:
- existing_id: null
  status: extended
  note: 'Promotes the refractory-shock sub-trigger (003c: NE>1.0 mcg/kg/min AND MAP<65 for >30 min) embedded
    inside legacy catalog HEMO-003 (the formal HEMO-003 existing_id is recorded once, under ALERT-HEMO-VASO-ESCALATION-03)
    into a standalone critical alert with a 5-min ack SLA and rapid-response workflow, extended with an
    adjunct-absence enrichment (recommend vasopressin+hydrocortisone when missing, RULE-ESTABILIDADE-019).
    The >1.0 mcg/kg/min ''maximal vasopressor'' cutoff is the recommended default pending RAT-ESTABILIDADE-08
    (P0 mcg/kg/min ladder).'
```

<a id="alert-hemo-fluid-nonresponsive-05"></a>
### ALERT-HEMO-FLUID-NONRESPONSIVE-05 — Não responsivo a fluidos — risco de sobrecarga

**Severity** watch · **Evidence** Marik PE et al. Crit Care Med 2013;41(7):1774-1781 (dynamic predictors of fluid responsiveness; PPV/SVV); Monnet X et al. Intensive Care Med 2016;42(12):1935-1947 (functional hemodynamic monitoring) · **Rules** — · **PPV target** 0.6 · **Est. volume** 1/100 beds/day

```yaml alert-spec
alert_id: ALERT-HEMO-FLUID-NONRESPONSIVE-05
name: Não responsivo a fluidos — risco de sobrecarga
severity: watch
trigger:
  logic: "( ( ppv < 10 percent OR svv < 10 percent ) AND delta_sv_pos_fluid < 10 percent\n  AND balanco_hidrico_24h\
    \ > 3000 mL )\nOR ( fluid_challenge_realizado AND delta_map_pos_fluid < 5 mmHg AND delta_lactato_pos_fluid\
    \ < 5 percent\n     AND balanco_hidrico_24h > 3000 mL );                    # fallback when PPV/SVV\
    \ unavailable\nbalanco_hidrico_24h is recomputed from source rows (never a mutable running total;\
    \ SYS-10 window bug). Sign convention: positive = net fluid gain (the legacy -2000 mL fluid-balance\
    \ sign is disputed and RATIFY, RAT-ESTABILIDADE-01 / RULE-ESTABILIDADE-001 — NOT used here; this alert\
    \ uses the unambiguous +3000 mL gain)."
  window: PT24H
inputs:
- name: ppv
  type: quantity
  unit: percent
  source: 'local TimescaleDB (advanced hemodynamic monitor: pulse pressure variation)'
  staleness_max: PT1H
- name: svv
  type: quantity
  unit: percent
  source: 'local TimescaleDB (advanced hemodynamic monitor: stroke volume variation)'
  staleness_max: PT1H
- name: delta_sv_pos_fluid
  type: quantity
  unit: percent
  source: hemodynamics domain (stroke-volume change after fluid challenge)
  staleness_max: PT2H
- name: delta_map_pos_fluid
  type: quantity
  unit: mmHg
  source: hemodynamics domain (MAP change after 500 mL crystalloid over 30 min)
  staleness_max: PT2H
- name: delta_lactato_pos_fluid
  type: quantity
  unit: percent
  source: hemodynamics domain (lactate change after fluid challenge)
  staleness_max: PT4H
- name: balanco_hidrico_24h
  type: quantity
  unit: mL
  source: aki/equilibrio domain (recomputed from source rows; consumed here)
  staleness_max: PT6H
- name: fluid_challenge_realizado
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration (500 mL crystalloid over 30 min)
  staleness_max: PT6H
evidence:
- citation: Marik PE et al. Crit Care Med 2013;41(7):1774-1781 (dynamic predictors of fluid responsiveness;
    PPV/SVV); Monnet X et al. Intensive Care Med 2016;42(12):1935-1947 (functional hemodynamic monitoring)
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT12H
  rate_limit: 1/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 1
  rationale: Dynamic non-responsiveness indices (PPV/SVV) are the reference-standard predictors, but availability
    is LOW (invasive monitor + specific software; DATA-AVAIL-09) so this alert degrades to the clinical
    fluid- challenge fallback. Requiring BOTH non-response AND a positive 24h balance >3000 mL targets
    the true overload-risk patient and holds PPV at the 0.60 floor. WATCH severity (a de-resuscitation/stewardship
    prompt, <2h action, not a life threat) and a 12h cooldown keep it well within the ignored-rate budget.
    ~1/100 beds/day (limited by monitor availability). One alert, two evidence-graded input paths.
response:
  required: reavaliar estratégia de fluidos — considerar restrição/de-ressuscitação; evitar novo bolus
    se não responsivo
  ack_sla: PT2H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    ppv: 6
    delta_sv_pos_fluid: 4
    balanco_hidrico_24h: 3800
  expected: fire
  note: PPV 6% (<10) + SV change 4% (<10) after challenge + 24h balance +3800 mL — non-responsive, overloaded
- id: TV-2
  kind: fire
  inputs:
    fluid_challenge_realizado: true
    delta_map_pos_fluid: 3
    delta_lactato_pos_fluid: 2
    balanco_hidrico_24h: 3500
  expected: fire
  note: 'fallback path: fluid challenge with MAP change 3 mmHg (<5) and lactate change 2% (<5), positive
    balance'
- id: TV-3
  kind: no-fire
  inputs:
    ppv: 15
    delta_sv_pos_fluid: 18
    balanco_hidrico_24h: 3800
  expected: no-fire
  note: PPV 15% (>=10) and SV rose 18% (>=10) — patient IS fluid-responsive, no overload alert
- id: TV-4
  kind: no-fire
  inputs:
    ppv: 6
    delta_sv_pos_fluid: 4
    balanco_hidrico_24h: 1500
  expected: no-fire
  note: non-responsive but 24h balance only +1500 mL (<=3000) — not yet an overload-risk picture
- id: TV-5
  kind: boundary
  inputs:
    ppv: 10
    delta_sv_pos_fluid: 9
    balanco_hidrico_24h: 3000
  expected: no-fire
  note: 'boundary exact-threshold: PPV=10 is NOT <10 (strict) AND balance=3000 is NOT >3000 (strict) —
    both fail'
reconciliation:
- existing_id: HEMO-004
  status: aligned
  note: 'vs alert-catalog.md HEMO-004 ''Não responsivo a fluidos — risco de sobrecarga'' (WARN/P3): carried
    forward — (PPV<10% OR SVV<10%) AND deltaSV<10% AND 24h balance >3000 mL positive, with the clinical
    fluid-challenge fallback (deltaMAP<5 mmHg, deltalactato<5%) when PPV/SVV unavailable. Severity WARN
    maps to watch; Marik 2013 anchor unchanged. 24h balance is recomputed from source rows (SYS-10 window-bug
    avoidance), positive-gain sign only.'
```

<a id="alert-hemo-antihtn-conflict-06"></a>
### ALERT-HEMO-ANTIHTN-CONFLICT-06 — Conflito anti-hipertensivo × pressão arterial / vasopressor

**Severity** watch · **Evidence** Institutional medication-safety pathway (antihypertensive vs vasopressor/BP conflict), boolean-logic corrected AND->OR and vacuous-exclusion fix; no external guideline cutoff (governance) · **Rules** RULE-ESTABILIDADE-012, RULE-ESTABILIDADE-013, RULE-ESTABILIDADE-021 · **PPV target** 0.62 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-HEMO-ANTIHTN-CONFLICT-06
name: Conflito anti-hipertensivo × pressão arterial / vasopressor
severity: watch
trigger:
  logic: "(A) deprescribe: antihipertensivo_agendado_ativo\n    AND ( recurrent_hypotension OR dose_vasopressor\
    \ > 0 mcg/kg/min )\nOR (B) uncontrolled_htn_off_pressor: dose_vasopressor == 0 mcg/kg/min\n    AND\
    \ recurrent_hypertension\n    AND NOT permissive_htn_indication;\nrecurrent_hypotension := >=2 of\
    \ the last readings in PT24H with (pressao_arterial_sistolica < 90 mmHg OR pressao_arterial_diastolica\
    \ < 60 mmHg)  [corrected AND->OR, RULE-ESTABILIDADE-012 ADAPT]; recurrent_hypertension := >=2 of the\
    \ last readings in PT24H with (pressao_arterial_sistolica > 155 mmHg OR pressao_arterial_diastolica\
    \ > 90 mmHg)  [corrected AND->OR + count==2->last-2 + fixed vacuous I64/AVCi exclusion that filtered\
    \ dict KEYS not values, RULE-ESTABILIDADE-013 ADAPT]; antihipertensivo_agendado_ativo uses the FULL\
    \ scheduled-antihypertensive list (recommended default; legacy 16-of-18 gap RULE-010 and the nora==50-mL\
    \ exact-equality RULE-022 are pending RAT-ESTABILIDADE-06/10 and NOT used as the firing predicate).\
    \ PT-BR display vocabulary preserved verbatim (CLU-ESTABILIDADE-20)."
  window: PT24H
inputs:
- name: pressao_arterial_sistolica
  type: quantity
  unit: mmHg
  source: AMH Gold Observation LOINC 8480-6 (serial)
  staleness_max: PT6H
- name: pressao_arterial_diastolica
  type: quantity
  unit: mmHg
  source: AMH Gold Observation LOINC 8462-4 (serial)
  staleness_max: PT6H
- name: dose_vasopressor
  type: quantity
  unit: mcg/kg/min
  source: hemodynamics conversion service (MedicationAdministration)
  staleness_max: PT1H
- name: antihipertensivo_agendado_ativo
  type: boolean
  unit: boolean
  source: AMH Gold MedicationRequest (scheduled antihypertensive; full class list)
  staleness_max: PT12H
- name: permissive_htn_indication
  type: boolean
  unit: boolean
  source: AMH Gold Condition (e.g. AVCi/I64 permissive-hypertension window)
  staleness_max: PT24H
evidence:
- citation: Institutional medication-safety pathway (antihypertensive vs vasopressor/BP conflict), boolean-logic
    corrected AND->OR and vacuous-exclusion fix; no external guideline cutoff (governance)
  rule_refs:
  - RULE-ESTABILIDADE-012
  - RULE-ESTABILIDADE-013
  - RULE-ESTABILIDADE-021
suppression:
  dedup_key: patient_id+alert_id+branch
  cooldown: PT8H
  rate_limit: 2/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.62
  est_volume_per_100_beds_day: 2
  rationale: Deterministic medication-safety check (a scheduled antihypertensive co-existing with hypotension/vasopressor,
    or uncontrolled hypertension off any pressor), so PPV is driven by data quality not physiology; requiring
    >=2 confirming readings damps single-reading artefact. Folding the three legacy medication-conflict
    rules (012/013/021) into ONE alert with a branch dedup key (rather than three separate alerts) directly
    serves the fewer-richer-alerts principle. WATCH severity keeps it off the deterioration-alarm channel.
    ~2/100 beds/day. The disputed institutional drug-list completeness and equality-vs-threshold bugs
    are handled by ratification, not silently ported.
response:
  required: revisar prescrição de anti-hipertensivo à luz da PA/vasopressor atual (suspender se hipotenso/em
    DVA; tratar se HAS não controlada sem indicação permissiva)
  ack_sla: PT2H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    antihipertensivo_agendado_ativo: true
    dose_vasopressor: 0.15
    pressao_arterial_sistolica: 88
  expected: fire
  note: 'branch A: scheduled antihypertensive active while patient on vasopressor — should hold antihypertensive'
- id: TV-2
  kind: fire
  inputs:
    antihipertensivo_agendado_ativo: true
    dose_vasopressor: 0
    pressao_arterial_sistolica: 82
    pressao_arterial_diastolica: 55
  expected: fire
  note: 'branch A: recurrent hypotension (SBP<90 OR DBP<60 on >=2 readings) with active antihypertensive'
- id: TV-3
  kind: fire
  inputs:
    dose_vasopressor: 0
    antihipertensivo_agendado_ativo: false
    pressao_arterial_sistolica: 168
    pressao_arterial_diastolica: 98
    permissive_htn_indication: false
  expected: fire
  note: 'branch B: recurrent uncontrolled hypertension off any vasopressor, no permissive-HTN indication'
- id: TV-4
  kind: no-fire
  inputs:
    dose_vasopressor: 0
    antihipertensivo_agendado_ativo: false
    pressao_arterial_sistolica: 168
    pressao_arterial_diastolica: 98
    permissive_htn_indication: true
  expected: no-fire
  note: recurrent HTN but AVCi/I64 permissive-hypertension window active — exclusion correctly suppresses
    (fixes legacy vacuous key-filter)
- id: TV-5
  kind: no-fire
  inputs:
    antihipertensivo_agendado_ativo: false
    dose_vasopressor: 0.15
    pressao_arterial_sistolica: 88
  expected: no-fire
  note: hypotensive on vasopressor but NO scheduled antihypertensive active — nothing to deprescribe
- id: TV-6
  kind: boundary
  inputs:
    antihipertensivo_agendado_ativo: true
    dose_vasopressor: 0
    pressao_arterial_sistolica: 90
    pressao_arterial_diastolica: 60
  expected: no-fire
  note: 'boundary exact-threshold: SBP=90 is NOT <90 AND DBP=60 is NOT <60 (strict) — no hypotension reading,
    branch A not met'
reconciliation:
- existing_id: null
  status: new
  note: No catalog HEMO-* alert covers this; sourced from legacy estabilidade medication-safety rules
    RULE-ESTABILIDADE-012 (recurrent hypotension + antihypertensive, ADAPT), -013 (recurrent hypertension
    off pressor, ADAPT), -021 (antihypertensive with adequate pressure/vasopressor, ADOPT). Three medication-conflict
    branches folded into one watch alert (fewer-richer). The disputed drug-list completeness (RULE-010)
    and nora==50-mL exact-equality bug (RULE-022) are pending RAT-ESTABILIDADE-06/10, not ported.
```

## neuro-sedation (8 alerts)

<a id="alert-neurosed-oversed-01"></a>
### ALERT-NEUROSED-OVERSED-01 — Sedação profunda fora do alvo (RASS < -3 sem indicação)

**Severity** watch · **Evidence** Sessler CN et al. Am J Respir Crit Care Med 2002;166(10):1338-1344 (RASS); Devlin JW et al. Crit Care Med 2018;46(9):e825-e873 (PADIS light-sedation target) · **Rules** RULE-SEDACAO-003, RULE-SEDACAO-016 · **PPV target** 0.65 · **Est. volume** 4/100 beds/day

```yaml alert-spec
alert_id: ALERT-NEUROSED-OVERSED-01
name: Sedação profunda fora do alvo (RASS < -3 sem indicação)
severity: watch
trigger:
  logic: ventilacao_mecanica == true AND (rass >= -5 AND rass <= -3) AND indicacao_sedacao_profunda ==
    false AND sedacao_paliativa == false, sustained over >=2 consecutive RASS assessments (>=PT4H)
  window: PT4H
inputs:
- name: rass
  type: quantity
  unit: points
  source: AMH Gold Observation LOINC 75826-6 (signed -5..+4)
  staleness_max: PT4H
- name: ventilacao_mecanica
  type: boolean
  unit: boolean
  source: Procedure / device presence
  staleness_max: PT6H
- name: indicacao_sedacao_profunda
  type: boolean
  unit: boolean
  source: derived (SDRA grave/ECMO/BNM/HIC/EME)
  staleness_max: PT12H
- name: sedacao_paliativa
  type: boolean
  unit: boolean
  source: care-plan flag (diurna_sedoanalgesia_justificativas)
  staleness_max: PT24H
evidence:
- citation: Sessler CN et al. Am J Respir Crit Care Med 2002;166(10):1338-1344 (RASS)
  rule_refs:
  - RULE-SEDACAO-003
- citation: Devlin JW et al. Crit Care Med 2018;46(9):e825-e873 (PADIS light-sedation target)
  rule_refs:
  - RULE-SEDACAO-016
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT8H
  rate_limit: 3/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.65
  est_volume_per_100_beds_day: 4
  rationale: ~40% of a 100-bed ICU is ventilated; a minority are RASS<-3 off-target sustained >=4h with
    NO documented deep-sedation indication (the indication gate excludes intentional deep sedation for
    ARDS/ECMO/BNM/HIC/EME). >=2-consecutive requirement plus PT8H cooldown caps re-fires. Most fires are
    genuine over-sedation reducible by the team -> PPV ~0.65.
response:
  required: reavaliação da meta de sedação e titulação à faixa RASS 0 a -2
  ack_sla: PT2H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    rass: -4
    ventilacao_mecanica: true
    indicacao_sedacao_profunda: false
    sedacao_paliativa: false
    consecutive: 2
  expected: fire
  note: deep sedation, no indication, sustained
- id: TV-2
  kind: no-fire
  inputs:
    rass: -4
    ventilacao_mecanica: true
    indicacao_sedacao_profunda: true
    sedacao_paliativa: false
    consecutive: 2
  expected: no-fire
  note: deep sedation IS indicated (e.g. SDRA grave/BNM) -> suppressed
- id: TV-3
  kind: boundary
  inputs:
    rass: -3
    ventilacao_mecanica: true
    indicacao_sedacao_profunda: false
    sedacao_paliativa: false
    consecutive: 2
  expected: fire
  note: 'boundary: RASS exactly -3 is INSIDE the inclusive band (-5<=rass<=-3); fires. Corrects legacy
    unsatisfiable -3<=x<=-5 (RULE-SEDACAO-003)'
- id: TV-4
  kind: boundary
  inputs:
    rass: -2
    ventilacao_mecanica: true
    indicacao_sedacao_profunda: false
    sedacao_paliativa: false
    consecutive: 2
  expected: no-fire
  note: 'boundary: RASS -2 is the light-sedation target (0..-2); no fire'
- id: TV-5
  kind: no-fire
  inputs:
    rass: -4
    ventilacao_mecanica: true
    indicacao_sedacao_profunda: false
    sedacao_paliativa: false
    consecutive: 1
  expected: no-fire
  note: single assessment only; sustained-2 requirement not met
reconciliation:
  existing_id: DEL-001
  status: changed
  note: 'vs docs/clinical/alert-catalog.md DEL-001 ''Sedação fora da faixa alvo (RASS)'': DEL-001''s deep-sedation
    branch (RASS<-3) becomes this watch alert; its agitation branch (RASS>+1) is split into ALERT-NEUROSED-AGITATION-02
    with a distinct urgent severity/response.'
```

<a id="alert-neurosed-agitation-02"></a>
### ALERT-NEUROSED-AGITATION-02 — Agitação psicomotora — risco de remoção de dispositivos (RASS > +1)

**Severity** urgent · **Evidence** Sessler CN et al. Am J Respir Crit Care Med 2002 (RASS agitation band +2..+4); Ely EW et al. JAMA 2003;289(22):2983-2991 (RASS validity/reliability in ICU) · **Rules** — · **PPV target** 0.7 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-NEUROSED-AGITATION-02
name: Agitação psicomotora — risco de remoção de dispositivos (RASS > +1)
severity: urgent
trigger:
  logic: rass > +1 sustained over >=2 consecutive RASS assessments, OR any single rass >= +3
  window: PT4H
inputs:
- name: rass
  type: quantity
  unit: points
  source: AMH Gold Observation LOINC 75826-6 (signed -5..+4)
  staleness_max: PT4H
evidence:
- citation: Sessler CN et al. Am J Respir Crit Care Med 2002 (RASS agitation band +2..+4)
  rule_refs: []
- citation: Ely EW et al. JAMA 2003;289(22):2983-2991 (RASS validity/reliability in ICU)
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT2H
  rate_limit: 4/24h/patient
  maintenance_window_aware: false
ppv_budget:
  target_ppv: 0.7
  est_volume_per_100_beds_day: 2
  rationale: 'RASS>+1 sustained is uncommon (~2/100 beds/day) and directly actionable: agitation carries
    self-extubation / line-removal risk. Single RASS>=+3 (muito agitado/combativo) bypasses the sustained
    gate for immediate safety. maintenance_window_aware:false because agitation is never suppressible
    by a maintenance window. High PPV (~0.70) because RASS>+1 is a concrete observed state, not a trend
    inference.'
response:
  required: 'avaliação de segurança beira-leito: causa reversível (dor/delirium/hipóxia), proteção de
    dispositivos'
  ack_sla: PT15M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    rass: 2
    consecutive: 2
  expected: fire
  note: agitado, sustained
- id: TV-2
  kind: fire
  inputs:
    rass: 3
    consecutive: 1
  expected: fire
  note: muito agitado single reading -> immediate (bypasses sustained gate)
- id: TV-3
  kind: boundary
  inputs:
    rass: 1
    consecutive: 2
  expected: no-fire
  note: 'boundary: RASS +1 (inquieto) is NOT > +1; no fire'
- id: TV-4
  kind: no-fire
  inputs:
    rass: 2
    consecutive: 1
  expected: no-fire
  note: RASS +2 single reading; sustained-2 not met and not >=+3
reconciliation:
  existing_id: DEL-001
  status: changed
  note: 'vs DEL-001 (agitation branch): promoted from WARN to urgent and split into its own alert because
    self-extubation risk needs a <15min bedside response distinct from the watch-level over-sedation half
    (ALERT-NEUROSED-OVERSED-01).'
```

<a id="alert-neurosed-sat-03"></a>
### ALERT-NEUROSED-SAT-03 — Despertar diário (SAT) não realizado / candidato a redução de sedação

**Severity** watch · **Evidence** Kress JP et al. NEJM 2000;342(20):1471-1477 (daily interruption of sedation); Girard TD et al. Lancet 2008;371(9607):126-134 (ABC / SAT+SBT); Devlin JW et al. PADIS 2018 (sedation minimisation); ARDS Definition Task Force JAMA 2012 (P/F>200) · **Rules** RULE-SEDACAO-006, RULE-SEDACAO-011, RULE-SEDACAO-017 · **PPV target** 0.6 · **Est. volume** 3/100 beds/day

```yaml alert-spec
alert_id: ALERT-NEUROSED-SAT-03
name: Despertar diário (SAT) não realizado / candidato a redução de sedação
severity: watch
trigger:
  logic: ventilacao_mecanica == true AND sedativo_continuo_presente == true AND relacao_pao2_fio2 > 200
    AND fio2 < 0.50 AND indicacao_sedacao_profunda == false AND (reducao_sedacao_matinal_pct < 50 OR sedativo_continuo_gt_96h
    == true)
  window: PT24H
inputs:
- name: ventilacao_mecanica
  type: boolean
  unit: boolean
  source: Procedure / device presence
  staleness_max: PT6H
- name: sedativo_continuo_presente
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration (sedatives)
  staleness_max: PT4H
- name: relacao_pao2_fio2
  type: quantity
  unit: ratio
  source: respiratory domain (FiO2 fraction!)
  staleness_max: PT6H
- name: fio2
  type: quantity
  unit: fraction
  source: AMH Gold Observation LOINC 19935-6
  staleness_max: PT6H
- name: indicacao_sedacao_profunda
  type: boolean
  unit: boolean
  source: derived (SDRA grave/ECMO/BNM/HIC/EME)
  staleness_max: PT12H
- name: reducao_sedacao_matinal_pct
  type: quantity
  unit: percent
  source: derived (06:00-10:00 sedation dose delta)
  staleness_max: PT6H
- name: sedativo_continuo_gt_96h
  type: boolean
  unit: boolean
  source: derived from MedicationAdministration start (>96h)
  staleness_max: PT6H
evidence:
- citation: Kress JP et al. NEJM 2000;342(20):1471-1477 (daily interruption of sedation)
  rule_refs:
  - RULE-SEDACAO-006
- citation: Girard TD et al. Lancet 2008;371(9607):126-134 (ABC / SAT+SBT)
  rule_refs:
  - RULE-SEDACAO-017
- citation: Devlin JW et al. PADIS 2018 (sedation minimisation); ARDS Definition Task Force JAMA 2012
    (P/F>200)
  rule_refs:
  - RULE-SEDACAO-011
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT20H
  rate_limit: 1/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 3
  rationale: Evaluated once per morning window; rate_limit 1/24h/patient makes this at most 1 per ventilated-sedated
    patient/day. Oxygenation gate (P/F>200, FiO2<0.50) + indication-absence gate select true lightening
    candidates. ~3/100 beds/day. PPV floor 0.60 (some candidates have soft contraindications not captured
    as indication flags) — recommended-default reduction threshold pending RAT-SEDACAO-02.
response:
  required: considerar interrupção diária de sedação (SAT) e teste de respiração espontânea se elegível
  ack_sla: PT2H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    ventilacao_mecanica: true
    sedativo_continuo_presente: true
    relacao_pao2_fio2: 260
    fio2: 0.4
    indicacao_sedacao_profunda: false
    reducao_sedacao_matinal_pct: 20
  expected: fire
  note: adequate oxygenation, still sedated, morning reduction <50%
- id: TV-2
  kind: no-fire
  inputs:
    ventilacao_mecanica: true
    sedativo_continuo_presente: true
    relacao_pao2_fio2: 180
    fio2: 0.6
    indicacao_sedacao_profunda: false
    reducao_sedacao_matinal_pct: 10
  expected: no-fire
  note: P/F 180<200 and FiO2 0.60 -> not a lightening candidate (oxygenation gate fails)
- id: TV-3
  kind: boundary
  inputs:
    ventilacao_mecanica: true
    sedativo_continuo_presente: true
    relacao_pao2_fio2: 260
    fio2: 0.4
    indicacao_sedacao_profunda: false
    reducao_sedacao_matinal_pct: 50
  expected: no-fire
  note: 'boundary: exactly 50% reduction is COMPLIANT (>=50% passes); corrects RULE-SEDACAO-009 half-reduction
    bug (RAT-SEDACAO-02)'
- id: TV-4
  kind: boundary
  inputs:
    ventilacao_mecanica: true
    sedativo_continuo_presente: true
    relacao_pao2_fio2: 200
    fio2: 0.4
    indicacao_sedacao_profunda: false
    reducao_sedacao_matinal_pct: 20
  expected: no-fire
  note: 'boundary: P/F exactly 200 is NOT >200 (strict); no fire'
- id: TV-5
  kind: fire
  inputs:
    ventilacao_mecanica: true
    sedativo_continuo_presente: true
    relacao_pao2_fio2: 260
    fio2: 0.4
    indicacao_sedacao_profunda: false
    reducao_sedacao_matinal_pct: 70
    sedativo_continuo_gt_96h: true
  expected: fire
  note: reduction OK but >96h continuous sedation -> prolonged-sedation surveillance branch fires (RULE-SEDACAO-011)
reconciliation:
  existing_id: null
  status: new
  note: No DEL-* catalog alert covers SAT/daily-awakening; new alert consolidating RULE-SEDACAO-006/017
    (lightening candidate) + RULE-SEDACAO-011 (prolonged sedation) + RULE-SEDACAO-009 morning-reduction
    (pending RAT-SEDACAO-02).
```

<a id="alert-neurosed-delirium-04"></a>
### ALERT-NEUROSED-DELIRIUM-04 — Delirium — CAM-ICU positivo

**Severity** urgent · **Evidence** Ely EW et al. NEJM 2001;345(14):1013-1020 (CAM-ICU validity/reliability); Devlin JW et al. PADIS 2018 (delirium management bundle) · **Rules** — · **PPV target** 0.75 · **Est. volume** 5/100 beds/day

```yaml alert-spec
alert_id: ALERT-NEUROSED-DELIRIUM-04
name: Delirium — CAM-ICU positivo
severity: urgent
trigger:
  logic: cam_icu == positivo
  window: PT12H
inputs:
- name: cam_icu
  type: enum
  unit: enum
  source: 'AMH Gold Observation LOINC 8683-5/8684-3/8686-8 (CAM-ICU: {positivo,negativo,nao_avaliavel})'
  staleness_max: PT12H
evidence:
- citation: Ely EW et al. NEJM 2001;345(14):1013-1020 (CAM-ICU validity/reliability)
  rule_refs: []
- citation: Devlin JW et al. PADIS 2018 (delirium management bundle)
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT12H
  rate_limit: 2/24h/patient
  maintenance_window_aware: false
ppv_budget:
  target_ppv: 0.75
  est_volume_per_100_beds_day: 5
  rationale: Delirium prevalence in ventilated patients is 50-80% but CAM-ICU is assessed per shift; positive
    screens fire once per positive assessment (deduped). ~5/100 beds/day. CAM-ICU is a validated instrument
    -> a positive screen is a genuine, directly-actionable finding, PPV ~0.75. Not maintenance-suppressible.
response:
  required: 'abordagem PADIS: causas reversíveis, revisão de sedativos deliriogênicos, medidas não-farmacológicas'
  ack_sla: PT30M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    cam_icu: positivo
  expected: fire
  note: CAM-ICU positive
- id: TV-2
  kind: no-fire
  inputs:
    cam_icu: negativo
  expected: no-fire
  note: CAM-ICU negative
- id: TV-3
  kind: boundary
  inputs:
    cam_icu: nao_avaliavel
  expected: no-fire
  note: 'boundary: unassessable (RASS -4/-5 or language barrier) is NOT positive; no fire, but feeds SCREEN-GAP
    cadence clock'
reconciliation:
  existing_id: DEL-002
  status: aligned
  note: vs DEL-002 'Delirium — CAM-ICU positivo'; same trigger and evidence (Ely 2001). Severity mapped
    catalog URG -> urgent.
```

<a id="alert-neurosed-screen-gap-05"></a>
### ALERT-NEUROSED-SCREEN-GAP-05 — Rastreio de delirium em atraso / suspeita de delirium hipoativo

**Severity** watch · **Evidence** van den Boogaard M et al. BMJ 2014;348:g1173 (hypoactive delirium under-recognition / PRE-DELIRIC); Devlin JW et al. PADIS 2018 (routine delirium screening cadence) · **Rules** — · **PPV target** 0.55 · **Est. volume** 3/100 beds/day

```yaml alert-spec
alert_id: ALERT-NEUROSED-SCREEN-GAP-05
name: Rastreio de delirium em atraso / suspeita de delirium hipoativo
severity: watch
trigger:
  logic: (ventilacao_mecanica == true OR sedativo_continuo_presente == true) AND horas_desde_ultimo_cam_icu
    > 24 AND (rass >= -3 AND rass <= -1) AND sedativo_continuo_presente_ultimas_4h == false
  window: PT24H
inputs:
- name: horas_desde_ultimo_cam_icu
  type: quantity
  unit: h
  source: derived from last CAM-ICU Observation timestamp
  staleness_max: PT1H
- name: rass
  type: quantity
  unit: points
  source: AMH Gold Observation LOINC 75826-6
  staleness_max: PT4H
- name: ventilacao_mecanica
  type: boolean
  unit: boolean
  source: Procedure / device presence
  staleness_max: PT6H
- name: sedativo_continuo_presente
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration (sedatives)
  staleness_max: PT4H
evidence:
- citation: van den Boogaard M et al. BMJ 2014;348:g1173 (hypoactive delirium under-recognition / PRE-DELIRIC)
  rule_refs: []
- citation: Devlin JW et al. PADIS 2018 (routine delirium screening cadence)
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT24H
  rate_limit: 1/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.55
  est_volume_per_100_beds_day: 3
  rationale: A process/cadence alert (missing screening), inherently lower-yield than a positive screen.
    rate_limit 1/24h/patient bounds it to at most one nudge per patient/day. ~3/100 beds/day. PPV ~0.55
    (below fleet floor is acceptable for a screening-prompt class because the action cost is a single
    low-burden CAM-ICU assessment) — kept watch and heavily rate-limited so it cannot drive ignored-rate.
response:
  required: aplicar CAM-ICU; documentar avaliação de delirium hipoativo
  ack_sla: PT2H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    ventilacao_mecanica: true
    horas_desde_ultimo_cam_icu: 30
    rass: -2
    sedativo_continuo_presente_ultimas_4h: false
  expected: fire
  note: at-risk, no CAM-ICU in 30h, hypoactive window, no active sedation
- id: TV-2
  kind: no-fire
  inputs:
    ventilacao_mecanica: true
    horas_desde_ultimo_cam_icu: 30
    rass: -2
    sedativo_continuo_presente_ultimas_4h: true
  expected: no-fire
  note: reduced RASS explained by active sedation in last 4h -> not hypoactive suspicion (DEL-004)
- id: TV-3
  kind: boundary
  inputs:
    ventilacao_mecanica: true
    horas_desde_ultimo_cam_icu: 24
    rass: -2
    sedativo_continuo_presente_ultimas_4h: false
  expected: no-fire
  note: 'boundary: exactly 24h is NOT >24 (strict); no fire. Uses true rolling 24h window (RAT-SEDACAO-10),
    not calendar-day'
- id: TV-4
  kind: boundary
  inputs:
    ventilacao_mecanica: true
    horas_desde_ultimo_cam_icu: 30
    rass: 0
    sedativo_continuo_presente_ultimas_4h: false
  expected: no-fire
  note: 'boundary: RASS 0 outside the -1..-3 hypoactive window; no fire'
reconciliation:
  existing_id: DEL-004
  status: extended
  note: vs DEL-004 'Delirium hipoativo possivelmente não reconhecido'; adds an explicit >24h rolling cadence
    clock (true rolling window per RAT-SEDACAO-10) to the vision's 'no CAM-ICU record' condition. PT-BR
    alert text preserved verbatim.
```

<a id="alert-neurosed-iatro-06"></a>
### ALERT-NEUROSED-IATRO-06 — Risco de delirium iatrogênico — benzodiazepínico em idoso sedado

**Severity** watch · **Evidence** Devlin JW et al. PADIS 2018 (suggest non-benzodiazepine over benzodiazepine sedation to reduce delirium) · **Rules** — · **PPV target** 0.65 · **Est. volume** 1/100 beds/day

```yaml alert-spec
alert_id: ALERT-NEUROSED-IATRO-06
name: Risco de delirium iatrogênico — benzodiazepínico em idoso sedado
severity: watch
trigger:
  logic: benzodiazepinico_continuo == true AND idade > 65 AND rass <= -2 AND indicacao_sedacao_profunda
    == false
  window: PT8H
inputs:
- name: benzodiazepinico_continuo
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration (midazolam/diazepam/lorazepam)
  staleness_max: PT4H
- name: idade
  type: quantity
  unit: years
  source: MPI demographics (Patient)
  staleness_max: P30D
- name: rass
  type: quantity
  unit: points
  source: AMH Gold Observation LOINC 75826-6
  staleness_max: PT4H
- name: indicacao_sedacao_profunda
  type: boolean
  unit: boolean
  source: derived (SDRA grave/ECMO/BNM/HIC/EME)
  staleness_max: PT12H
evidence:
- citation: Devlin JW et al. PADIS 2018 (suggest non-benzodiazepine over benzodiazepine sedation to reduce
    delirium)
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT12H
  rate_limit: 1/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.65
  est_volume_per_100_beds_day: 1
  rationale: Narrow conjunction (BZD continuous infusion AND age>65 AND RASS<=-2 AND no deep-sed indication)
    selects a small, specific high-risk cohort (~1/100 beds/day). rate_limit 1/24h. PPV ~0.65 — the recommendation
    (consider dexmedetomidine/propofol substitution) is actionable whenever the conjunction holds; PADIS-anchored.
response:
  required: considerar sedativo não-benzodiazepínico (dexmedetomidina/propofol) se apropriado
  ack_sla: PT2H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    benzodiazepinico_continuo: true
    idade: 72
    rass: -3
    indicacao_sedacao_profunda: false
  expected: fire
  note: elderly, BZD infusion, sedated, no deep-sed indication
- id: TV-2
  kind: no-fire
  inputs:
    benzodiazepinico_continuo: false
    idade: 72
    rass: -3
    indicacao_sedacao_profunda: false
  expected: no-fire
  note: no continuous benzodiazepine
- id: TV-3
  kind: boundary
  inputs:
    benzodiazepinico_continuo: true
    idade: 65
    rass: -3
    indicacao_sedacao_profunda: false
  expected: no-fire
  note: 'boundary: age exactly 65 is NOT >65 (strict, per vision age>65); no fire'
- id: TV-4
  kind: boundary
  inputs:
    benzodiazepinico_continuo: true
    idade: 72
    rass: -2
    indicacao_sedacao_profunda: false
  expected: fire
  note: 'boundary: RASS exactly -2 satisfies rass<=-2; fires'
reconciliation:
  existing_id: DEL-003
  status: aligned
  note: vs DEL-003 'Risco de delirium iatrogênico — sedação inadequada'; same conjunction (BZD infusion
    + age>65 + RASS<=-2 + no deep-sed indication). Severity mapped catalog WARN -> watch.
```

<a id="alert-neurosed-pris-07"></a>
### ALERT-NEUROSED-PRIS-07 — Vigilância de síndrome de infusão de propofol (PRIS) — labs de segurança em falta

**Severity** watch · **Evidence** Mirrakhimov AE et al. Crit Care Res Pract 2015;2015:260385 (propofol infusion syndrome); Devlin JW et al. PADIS 2018 (propofol monitoring) · **Rules** RULE-SEDACAO-012 · **PPV target** 0.6 · **Est. volume** 1/100 beds/day

```yaml alert-spec
alert_id: ALERT-NEUROSED-PRIS-07
name: Vigilância de síndrome de infusão de propofol (PRIS) — labs de segurança em falta
severity: watch
trigger:
  logic: propofol_continuo_gt_96h == true AND (cpk_resultado_48h == false OR transaminases_resultado_48h
    == false OR triglicerides_resultado_48h == false)
  window: PT48H
inputs:
- name: propofol_continuo_gt_96h
  type: boolean
  unit: boolean
  source: derived from MedicationAdministration start (>96h continuous propofol)
  staleness_max: PT6H
- name: cpk_resultado_48h
  type: boolean
  unit: boolean
  source: AMH Gold lab_result presence (CPK) in 48h
  staleness_max: PT48H
- name: transaminases_resultado_48h
  type: boolean
  unit: boolean
  source: AMH Gold lab_result presence (TGO/AST + TGP/ALT) in 48h
  staleness_max: PT48H
- name: triglicerides_resultado_48h
  type: boolean
  unit: boolean
  source: AMH Gold lab_result presence (triglycerides) in 48h
  staleness_max: PT48H
evidence:
- citation: Mirrakhimov AE et al. Crit Care Res Pract 2015;2015:260385 (propofol infusion syndrome)
  rule_refs:
  - RULE-SEDACAO-012
- citation: Devlin JW et al. PADIS 2018 (propofol monitoring)
  rule_refs:
  - RULE-SEDACAO-012
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT24H
  rate_limit: 1/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 1
  rationale: Prolonged (>96h) continuous propofol is uncommon and the missing-safety-lab conjunction narrows
    further (~1/100 beds/day; rounds up from <1). rate_limit 1/24h. PPV ~0.60 — every fire is a concrete,
    cheap-to-close safety-lab gap (order CPK/transaminases/triglycerides + review lactate/pH); fixes the
    legacy 'trigliceres' typo that silently made the triglyceride leg inert (RULE-SEDACAO-012).
response:
  required: solicitar CPK, TGO/TGP, triglicérides; revisar lactato/pH; reavaliar dose e duração do propofol
  ack_sla: PT2H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    propofol_continuo_gt_96h: true
    cpk_resultado_48h: false
    transaminases_resultado_48h: true
    triglicerides_resultado_48h: true
  expected: fire
  note: '>96h propofol and CPK missing in 48h'
- id: TV-2
  kind: no-fire
  inputs:
    propofol_continuo_gt_96h: true
    cpk_resultado_48h: true
    transaminases_resultado_48h: true
    triglicerides_resultado_48h: true
  expected: no-fire
  note: all safety labs present in 48h -> surveillance satisfied
- id: TV-3
  kind: fire
  inputs:
    propofol_continuo_gt_96h: true
    cpk_resultado_48h: true
    transaminases_resultado_48h: true
    triglicerides_resultado_48h: false
  expected: fire
  note: triglyceride leg missing -> fires (this is the leg the legacy 'trigliceres' typo silently disabled)
- id: TV-4
  kind: boundary
  inputs:
    propofol_continuo_gt_96h: false
    cpk_resultado_48h: false
    transaminases_resultado_48h: false
    triglicerides_resultado_48h: false
  expected: no-fire
  note: 'boundary: propofol not yet >96h continuous; surveillance not triggered regardless of missing
    labs'
reconciliation:
  existing_id: null
  status: new
  note: No DEL-* catalog alert covers PRIS; new alert carrying RULE-SEDACAO-012 (ADOPT) forward with the
    'trigliceres' field-name typo corrected.
```

<a id="alert-neurosed-pain-08"></a>
### ALERT-NEUROSED-PAIN-08 — Dor não controlada (escala VISUAL/COMPORTAMENTAL, dois balanços consecutivos)

**Severity** urgent · **Evidence** Devlin JW et al. PADIS 2018 (pain assessment standard); Payen JF et al. Crit Care Med 2001;29(12):2258-2263 (Behavioral Pain Scale) · **Rules** RULE-SEDACAO-001, RULE-SEDACAO-002 · **PPV target** 0.6 · **Est. volume** 3/100 beds/day

```yaml alert-spec
alert_id: ALERT-NEUROSED-PAIN-08
name: Dor não controlada (escala VISUAL/COMPORTAMENTAL, dois balanços consecutivos)
severity: urgent
trigger:
  logic: 'Severity-scaling uncontrolled-pain alert; output = worst band, each confirmed on TWO consecutive
    fluid-balance records (built-in false-positive filter; RULE-SEDACAO-001/002). MODERATE (watch): (escala_dor_numerica
    4..6) OR (escala_dor_comportamental 7..9). SEVERE (urgent): (escala_dor_numerica >= 7) OR (escala_dor_comportamental
    >= 10) — RESTORED distinct urgent escalation for severe uncontrolled pain (NRS 7-10 / BPS 10-12).
    Scale maximums NRS 10 / BPS 12 MUST reach the severe->urgent band. Bands are expressed low <= x <=
    high, never the chained-comparison misparse ''7 <= dor > 10'' / ''10 <= sinais > 12'' that silently
    suppressed the severe grade (SYS-06 / P0-04 / P0-05). PENDING SAFETY-OFFICER RE-CHECK (R2).'
  window: PT12H
inputs:
- name: escala_dor_numerica
  type: quantity
  unit: points
  source: AMH Gold Observation (EVA/VISUAL 0-10)
  staleness_max: PT6H
- name: escala_dor_comportamental
  type: quantity
  unit: points
  source: AMH Gold Observation (BPS/COMPORTAMENTAL 3-12)
  staleness_max: PT6H
evidence:
- citation: Devlin JW et al. PADIS 2018 (pain assessment standard)
  rule_refs:
  - RULE-SEDACAO-001
- citation: Payen JF et al. Crit Care Med 2001;29(12):2258-2263 (Behavioral Pain Scale)
  rule_refs:
  - RULE-SEDACAO-002
suppression:
  dedup_key: patient_id+alert_id+band
  cooldown: PT6H
  rate_limit: 3/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 3
  rationale: The two-consecutive-balance confirmation is a built-in false-positive filter (a single spurious
    high score never fires), directly carried from RULE-SEDACAO-001/002. ~3/100 beds/day total; the SEVERE
    sub-band (NRS 7-10 / BPS 10-12) is the smaller fraction. PPV ~0.60 — uncontrolled pain confirmed on
    two balances is a genuine analgesia-titration prompt. The severe band now emits a DISTINCT URGENT
    escalation (ack <30min) instead of folding into watch — restoring the escalation lost when severe
    pain was collapsed to watch; moderate (NRS 4-6 / BPS 7-9) stays watch. Pending safety-officer re-check
    (R2).
response:
  required: reavaliar analgesia e titular; distinguir dor de agitação/delirium
  ack_sla: PT30M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    escala_dor_numerica: 6
    consecutive_balances: 2
    expected_severity: watch
  expected: fire
  note: 'MODERATE band: VISUAL 6 (4-6) on two consecutive balances -> watch'
- id: TV-2
  kind: no-fire
  inputs:
    escala_dor_numerica: 6
    consecutive_balances: 1
  expected: no-fire
  note: single balance only; two-consecutive confirmation not met
- id: TV-3
  kind: boundary
  inputs:
    escala_dor_numerica: 4
    consecutive_balances: 2
    expected_severity: watch
  expected: fire
  note: 'boundary: VISUAL exactly 4 is the moderate-band floor (>=4) -> watch'
- id: TV-4
  kind: boundary
  inputs:
    escala_dor_numerica: 3
    escala_dor_comportamental: 7
    consecutive_balances: 2
    expected_severity: watch
  expected: fire
  note: 'boundary: VISUAL 3 below floor but BPS exactly 7 meets the COMPORTAMENTAL moderate floor (7-9);
    OR-branch fires watch. Guards the chained-comparison severe-band suppression bug (SYS-06/P0-04/05)'
- id: TV-5
  kind: boundary
  inputs:
    escala_dor_numerica: 3
    escala_dor_comportamental: 6
    consecutive_balances: 2
  expected: no-fire
  note: 'boundary: VISUAL 3 and BPS 6 both below floors; no fire'
- id: TV-6
  kind: boundary
  inputs:
    escala_dor_numerica: 10
    consecutive_balances: 2
    expected_severity: urgent
  expected: fire
  note: 'SEVERE scale-maximum: NRS exactly 10 MUST fire URGENT on two consecutive assessments (restored
    distinct severe-pain escalation; was silently capped at watch). Directly satisfies HAZ-004 max-value
    requirement (P0-04 chained-comparison). Pending safety-officer re-check (R2)'
- id: TV-7
  kind: boundary
  inputs:
    escala_dor_comportamental: 12
    consecutive_balances: 2
    expected_severity: urgent
  expected: fire
  note: 'SEVERE scale-maximum: BPS exactly 12 MUST fire URGENT (non-communicative/sedated patients, the
    population BPS exists for). Satisfies HAZ-005 max-value requirement (P0-05). Pending safety-officer
    re-check (R2)'
- id: TV-8
  kind: boundary
  inputs:
    escala_dor_numerica: 7
    consecutive_balances: 2
    expected_severity: urgent
  expected: fire
  note: 'boundary: NRS exactly 7 is the SEVERE-band floor (>=7) -> urgent, distinct from the moderate
    watch band (4-6)'
- id: TV-9
  kind: boundary
  inputs:
    escala_dor_comportamental: 10
    consecutive_balances: 2
    expected_severity: urgent
  expected: fire
  note: 'boundary: BPS exactly 10 is the SEVERE-band floor (>=10) -> urgent; guards the BPS 9/10 moderate-severe
    edge'
reconciliation:
  existing_id: null
  status: new
  note: No DEL-* catalog alert covers pain (analgesia pillar); new alert carrying RULE-SEDACAO-001 (moderate)
    and RULE-SEDACAO-002 (severe) ADOPT forward with the two-consecutive-balance confirmation preserved.
    The severe band (RULE-SEDACAO-002, NRS 7-10 / BPS 10-12) now outputs a DISTINCT URGENT escalation
    (restored; previously folded to watch) — reinstating the domain's flagged single genuine clinical
    loss. Pending safety-officer re-check (R2).
```

## electrolyte (6 alerts)

<a id="alert-ely-potassium-01"></a>
### ALERT-ELY-POTASSIUM-01 — Distúrbio grave do potássio — hipercalemia/hipocalemia

**Severity** critical · **Evidence** UK Kidney Association (UKKA) 2023 Clinical Practice Guideline: Treatment of Acute Hyperkalaemia in Adults (crit >6.5, urgent >6.0 mmol/L) — vision §3.6 VIS-3.6-02; Clase CM et al. Potassium homeostasis and management of dyskalemia. BMJ 2020 (KDIGO conference) — hyper/hypo bands; hypoK crit <2.5, urgent <3.0 mmol/L per vision §3.6 VIS-3.6-03; KDIGO hyperkalaemia conference summary, Eur J Emerg Med 2020;27(5):329-337 (PMC7448835); Mount DB, Sterns RH — Treatment of hyperkalemia (UpToDate) — rescue bundle basis for RULE-EQUILIBRIO-004 · **Rules** RULE-EQUILIBRIO-004 · **PPV target** 0.88 · **Est. volume** 3/100 beds/day

```yaml alert-spec
alert_id: ALERT-ELY-POTASSIUM-01
name: Distúrbio grave do potássio — hipercalemia/hipocalemia
severity: critical
trigger:
  logic: 'Dyskalemia; output severity = worst band across the hyper and hypo axes. HYPER: critical if
    potassio > 6.5 mmol/L; urgent if potassio > 6.0 mmol/L (and <= 6.5); watch if potassio > 5.5 mmol/L
    AND delta_k_24h > 0.5 mmol/L AND (ckd_moderada_grave OR medicamento_hipercalemiante_ativo OR digoxina_ativa).
    HYPO: critical if potassio < 2.5 mmol/L; urgent if potassio < 3.0 mmol/L (and >= 2.5); watch if potassio
    < 3.5 mmol/L AND (qtc > 500 ms OR furosemida_dose_alta OR digoxina_ativa OR magnesio < 0.7 mmol/L).
    DIGOXIN pairing (paired-condition escalation): if digoxina_ativa AND (potassio > 6.0 OR potassio <
    3.0), attach digoxin_toxicity_context=true — hyperkalemia with digoxin signals digoxin toxicity (calcium
    given with caution / consider digoxin-specific antibody); hypokalemia with digoxin potentiates toxic
    arrhythmia.

    '
  window: PT24H
inputs:
- name: potassio
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result (LOINC 6298-4)
  staleness_max: PT12H
- name: delta_k_24h
  type: quantity
  unit: mmol/L
  source: derived (potassio_atual - potassio_24h_atras)
  staleness_max: PT24H
- name: magnesio
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result (LOINC 19123-9)
  staleness_max: PT24H
- name: qtc
  type: quantity
  unit: ms
  source: AMH Gold Observation ECG QTc (LOINC 44974-4)
  staleness_max: PT24H
- name: digoxina_ativa
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration (digoxina ativa)
  staleness_max: PT24H
- name: medicamento_hipercalemiante_ativo
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration (espironolactona/eplerenona/IECA/BRA/TMP-SMX/heparina prolongada/succinilcolina)
  staleness_max: PT24H
- name: ckd_moderada_grave
  type: boolean
  unit: boolean
  source: AMH Gold Condition / eGFR<60 (CKD estágio >=3)
  staleness_max: PT30D
- name: furosemida_dose_alta
  type: boolean
  unit: boolean
  source: AMH Gold MedicationAdministration (furosemida dose alta)
  staleness_max: PT24H
evidence:
- citation: 'UK Kidney Association (UKKA) 2023 Clinical Practice Guideline: Treatment of Acute Hyperkalaemia
    in Adults (crit >6.5, urgent >6.0 mmol/L) — vision §3.6 VIS-3.6-02'
  rule_refs:
  - RULE-EQUILIBRIO-004
- citation: Clase CM et al. Potassium homeostasis and management of dyskalemia. BMJ 2020 (KDIGO conference)
    — hyper/hypo bands; hypoK crit <2.5, urgent <3.0 mmol/L per vision §3.6 VIS-3.6-03
  rule_refs: []
- citation: KDIGO hyperkalaemia conference summary, Eur J Emerg Med 2020;27(5):329-337 (PMC7448835); Mount
    DB, Sterns RH — Treatment of hyperkalemia (UpToDate) — rescue bundle basis for RULE-EQUILIBRIO-004
  rule_refs:
  - RULE-EQUILIBRIO-004
suppression:
  dedup_key: patient_id+alert_id+direction+band
  cooldown: PT6H
  rate_limit: 4/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.88
  est_volume_per_100_beds_day: 3
  rationale: 'Severe dyskalemia at these bands is objective and clinically actionable; a 100-bed ICU (CKD,
    diuretics, RRT, refeeding) yields ~3 critical/urgent potassium events/day. The dominant false positive
    is pre-analytic pseudo-hyperkalemia from a hemolyzed or K-EDTA-contaminated sample, mitigated by dedup
    on band and by the watch-band cofactor gate (trend + risk factor), which suppresses isolated mild
    values. Digoxin/QTc context raises signal without adding volume. Comfortably above the >=0.60 fleet
    PPV and supports <=10% ignored (VIS-7.1-02/04).

    '
response:
  required: 'avaliação médica beira-leito imediata. Hipercalemia crítica: bundle de resgate (RULE-EQUILIBRIO-004,
    corrigido para mEq/L, NUNCA mg/dl): gluconato de cálcio (estabilização de membrana), solução polarizante
    (insulina+glicose), beta-agonista (salbutamol/fenoterol), furosemida; reavaliação em +4h com bicarbonato
    de sódio 8.4% 1 mL/kg e resina de troca (Sorcal) se K+ ainda > 5.5 mmol/L. Se digoxina ativa: cálcio
    com cautela e considerar anticorpo antidigoxina. Hipocalemia crítica: reposição de potássio E correção
    concomitante de magnésio (hipomagnesemia perpetua hipocalemia refratária).

    '
  ack_sla: PT5M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    potassio: 7.0
  expected: fire
  note: K+ 7.0 > 6.5 -> critical hyperkalemia
- id: TV-2
  kind: fire
  inputs:
    potassio: 2.2
  expected: fire
  note: K+ 2.2 < 2.5 -> critical hypokalemia
- id: TV-3
  kind: boundary
  inputs:
    potassio: 6.5
  expected: fire
  note: K+ exactly 6.5 is NOT > 6.5 (critical) but IS > 6.0 -> urgent; guards the 6.5/6.0 band edge
- id: TV-4
  kind: boundary
  inputs:
    potassio: 5.5
    delta_k_24h: 0.8
    ckd_moderada_grave: true
  expected: no-fire
  note: K+ exactly 5.5 is NOT > 5.5 -> watch band does not open even with trend+CKD; guards the 5.5 floor
- id: TV-5
  kind: fire
  inputs:
    potassio: 6.8
    digoxina_ativa: true
  expected: fire
  note: critical hyperkalemia + digoxin -> digoxin_toxicity_context; calcium with caution (paired condition)
- id: TV-6
  kind: no-fire
  inputs:
    potassio: 4.5
  expected: no-fire
  note: normokalemia -> no-fire
- id: TV-7
  kind: fire
  inputs:
    potassio: 3.2
    qtc: 520
  expected: fire
  note: K+ 3.2 < 3.5 AND QTc 520 > 500 -> watch; emits qtc_risk_electrolyte to pharmaco (Torsades)
reconciliation:
- existing_id: ELY-001
  status: changed
  note: 'vs docs/clinical/alert-catalog.md: hyperkalemia ELY-001 (a/b/c bands) folded into a per-ion scaling
    alert; adds explicit digoxin-toxicity pairing; rescue bundle adopts RULE-EQUILIBRIO-004 corrected
    to mEq/L (CON-0159 / CLU-EQUILIBRIO-C-01, never propagate the legacy mg/dl mislabel).'
- existing_id: ELY-002
  status: changed
  note: 'vs alert-catalog.md: hypokalemia ELY-002 (a/b/c bands) folded into the same potassium alert;
    the high-risk watch band (QTc>500 / high-dose furosemide / digoxin / Mg<0.7) is retained and now emits
    qtc_risk_electrolyte to the pharmaco domain for Torsades correlation (VIS-4-03 #3).'
```

<a id="alert-ely-sodium-01"></a>
### ALERT-ELY-SODIUM-01 — Distúrbio grave do sódio — hipernatremia/hiponatremia

**Severity** critical · **Evidence** Spasovski G et al. / ESICM-ESE-ERBP 2024 consensus on acute hyponatraemia and hypernatraemia (hyperNa crit >160, urgent >155; hypoNa crit <120, urgent <125 mmol/L) — vision §3.6 VIS-3.6-04/05; Adrogué HJ, Madias NE. N Engl J Med 2000;342:1493-1499 (dysnatremia water-deficit correction) — hypernatremia rescue path · **Rules** RULE-EQUILIBRIO-002 · **PPV target** 0.88 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-ELY-SODIUM-01
name: Distúrbio grave do sódio — hipernatremia/hiponatremia
severity: critical
trigger:
  logic: 'Dysnatremia (absolute value); output severity = worst band across the hyper and hypo axes. Optional
    glucose correction: sodio_corrigido = sodio + 0.024*(glicemia - 100 mg/dL) when glicemia > 100 (guards
    pseudo-hyponatremia of hyperglycemia); bands evaluate sodio_corrigido when glicemia available. HYPER:
    critical if sodio > 160 mmol/L; urgent if sodio > 155 mmol/L (and <= 160); watch if sodio > 150 mmol/L
    AND delta_na_24h_trailing > 5 mmol/L (rising). HYPO: critical if sodio < 120 mmol/L; urgent if sodio
    < 125 mmol/L (and >= 120); watch if sodio < 130 mmol/L AND delta_na_24h_trailing <= -5 mmol/L (acute
    fall). NOTE: delta_na_24h_trailing is the TRAILING 24h delta (sodio_atual - sodio_24h_atras) — a DISTINCT
    quantity from correcao_na_24h_from_nadir used by ALERT-ELY-SODIUM-CORRECTION-02. The RATE-of-correction
    (osmotic-demyelination) hazard is that SEPARATE alert and MUST NOT reuse this trailing value.

    '
  window: PT24H
inputs:
- name: sodio
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result (LOINC 2951-2)
  staleness_max: PT12H
- name: delta_na_24h_trailing
  type: quantity
  unit: mmol/L
  source: derived (sodio_atual - sodio_24h_atras; TRAILING 24h delta — DISTINCT from the from-nadir correction
    quantity used by ALERT-ELY-SODIUM-CORRECTION-02)
  staleness_max: PT24H
- name: glicemia
  type: quantity
  unit: mg/dL
  source: AMH Gold lab_result (glucose); optional glucose-correction context
  staleness_max: PT12H
- name: creatinina
  type: quantity
  unit: mg/dL
  source: AMH Gold lab_result (LOINC 2160-0); free-water/renal context
  staleness_max: PT24H
evidence:
- citation: Spasovski G et al. / ESICM-ESE-ERBP 2024 consensus on acute hyponatraemia and hypernatraemia
    (hyperNa crit >160, urgent >155; hypoNa crit <120, urgent <125 mmol/L) — vision §3.6 VIS-3.6-04/05
  rule_refs: []
- citation: Adrogué HJ, Madias NE. N Engl J Med 2000;342:1493-1499 (dysnatremia water-deficit correction)
    — hypernatremia rescue path
  rule_refs:
  - RULE-EQUILIBRIO-002
suppression:
  dedup_key: patient_id+alert_id+direction+band
  cooldown: PT8H
  rate_limit: 3/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.88
  est_volume_per_100_beds_day: 2
  rationale: 'Absolute severe dysnatremia at these bands is objective; ~2 critical/urgent sodium events/100-beds/day
    (free-water losses, SIADH, hyperosmolar states). Glucose correction removes the main clinical false
    positive (pseudo-hyponatremia of hyperglycemia). The watch bands require a trend cofactor (delta),
    so isolated borderline values do not fire. Well above the >=0.60 fleet floor.

    '
response:
  required: 'avaliação médica. Hipernatremia: corrigir déficit de água livre (RULE-EQUILIBRIO-002: água
    filtrada 400 mL 6/6h, NaCl 0.22% 84 mL/h, hidroclorotiazida 25 mg) sem baixar o sódio > 8-10 mmol/L/24h.
    Hiponatremia: tratar conforme sintomas/cronicidade e NÃO ultrapassar 8-10 mmol/L/24h de correção (ver
    ALERT-ELY-SODIUM-CORRECTION-02, risco de mielinólise pontina).

    '
  ack_sla: PT5M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    sodio: 162
  expected: fire
  note: Na+ 162 > 160 -> critical hypernatremia
- id: TV-2
  kind: fire
  inputs:
    sodio: 118
  expected: fire
  note: Na+ 118 < 120 -> critical hyponatremia
- id: TV-3
  kind: boundary
  inputs:
    sodio: 160
  expected: fire
  note: Na+ exactly 160 is NOT > 160 (critical) but IS > 155 -> urgent; guards 160/155 band edge
- id: TV-4
  kind: boundary
  inputs:
    sodio: 155
    delta_na_24h_trailing: 2
  expected: no-fire
  note: Na+ exactly 155 NOT > 155; watch needs >150 AND delta_na_24h_trailing>5 (trailing=2) -> no-fire;
    guards 155 edge
- id: TV-5
  kind: fire
  inputs:
    sodio: 156
  expected: fire
  note: Na+ 156 > 155 -> urgent hypernatremia
- id: TV-6
  kind: no-fire
  inputs:
    sodio: 140
  expected: no-fire
  note: normonatremia -> no-fire
- id: TV-7
  kind: fire
  inputs:
    sodio: 128
    delta_na_24h_trailing: -7
  expected: fire
  note: Na+ 128 < 130 AND acute trailing fall -7 -> watch (acute hyponatremia trend)
reconciliation:
- existing_id: ELY-003
  status: changed
  note: 'vs alert-catalog.md: hyponatremia ELY-003 absolute bands (a crit<120, b urgent<125) folded here;
    adds glucose-correction guard; the ELY-003c rapid-correction SAFETY band is split out to ALERT-ELY-SODIUM-CORRECTION-02.'
- existing_id: ELY-004
  status: changed
  note: 'vs alert-catalog.md: hypernatremia ELY-004 (a/b/c) folded here; restores the RULE-EQUILIBRIO-002
    Na>160 correction path that legacy get_detalhe() never surfaced (CON-0161 / CLU-EQUILIBRIO-C-03, ADAPT
    to restore visibility).'
```

<a id="alert-ely-sodium-correction-02"></a>
### ALERT-ELY-SODIUM-CORRECTION-02 — Velocidade de correção do sódio perigosa — risco de desmielinização osmótica

**Severity** critical · **Evidence** Sterns RH. Disorders of plasma sodium — overcorrection & osmotic demyelination. J Am Soc Nephrol 2015;26(9):2110-2115 (correction ceiling 8-10 mmol/L/24h) — vision §3.6 VIS-3.6-06; CON-0061 / CAT-C-01 · **Rules** RULE-EQUILIBRIO-002 · **PPV target** 0.8 · **Est. volume** 1/100 beds/day

```yaml alert-spec
alert_id: ALERT-ELY-SODIUM-CORRECTION-02
name: Velocidade de correção do sódio perigosa — risco de desmielinização osmótica
severity: critical
trigger:
  logic: 'Rate-of-change safety net (bidirectional, primarily guarding over-rapid UPWARD correction of
    chronic hyponatremia). correcao_na_24h_from_nadir is the signed correction measured FROM the 24h nadir
    sodium (sodio_atual - sodio_nadir_24h) — NOT the trailing sodio_atual - sodio_24h_atras (delta_na_24h_trailing)
    used by ALERT-ELY-SODIUM-01. This alert MUST use the from-nadir quantity: an over-rapid rise off the
    24h nadir is the osmotic-demyelination hazard even when the net trailing 24h delta is flat or negative
    (deterministic-baseline requirement, HAZ-031; reusing the trailing baseline can miss an ODS-range
    correction, HAZ-032). critical if correcao_na_24h_from_nadir > 10 mmol/L in 24h (exceeds the osmotic-demyelination
    safety ceiling); urgent if correcao_na_24h_from_nadir > 8 mmol/L in 24h (approaching the ceiling).
    Highest concern when the 24h nadir sodium was < 130 mmol/L (chronic hyponatremia being corrected).
    A rapid FALL is also flagged (abs value) but the canonical ODS risk is the rapid rise.

    '
  window: PT24H
inputs:
- name: sodio
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result (LOINC 2951-2)
  staleness_max: PT6H
- name: correcao_na_24h_from_nadir
  type: quantity
  unit: mmol/L
  source: derived (sodio_atual - sodio_nadir_24h; signed correction over 24h FROM the 24h nadir — DISTINCT
    from delta_na_24h_trailing; deterministic nadir baseline per HAZ-031)
  staleness_max: PT24H
evidence:
- citation: Sterns RH. Disorders of plasma sodium — overcorrection & osmotic demyelination. J Am Soc Nephrol
    2015;26(9):2110-2115 (correction ceiling 8-10 mmol/L/24h) — vision §3.6 VIS-3.6-06; CON-0061 / CAT-C-01
  rule_refs:
  - RULE-EQUILIBRIO-002
suppression:
  dedup_key: patient_id+alert_id+band
  cooldown: PT6H
  rate_limit: 3/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.8
  est_volume_per_100_beds_day: 1
  rationale: 'A low-volume (~1/100-beds/day), high-value safety net: the harm it prevents (central pontine
    myelinolysis / osmotic demyelination syndrome) is catastrophic and iatrogenic, so a slightly lower
    PPV than the absolute-value alerts is deliberately accepted — the cost of a missed overcorrection
    dwarfs the cost of an occasional false alarm. It is exactly the alert whose ABSENCE is dangerous,
    so it is preserved as its own alert rather than folded into ALERT-ELY-SODIUM-01.

    '
response:
  required: 'interromper/reduzir a reposição de sódio imediatamente; considerar re-abaixamento controlado
    do sódio (água livre / DDAVP) se sobrecorreção confirmada; consultar nefrologia. Correção alvo <=
    8-10 mmol/L/24h.

    '
  ack_sla: PT5M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    sodio: 130
    sodio_nadir_24h: 118
    correcao_na_24h_from_nadir: 12
  expected: fire
  note: Na+ rose from 24h nadir 118 -> 130 (+12) > 10 -> critical overcorrection (ODS risk)
- id: TV-2
  kind: fire
  inputs:
    sodio: 128
    sodio_nadir_24h: 119
    correcao_na_24h_from_nadir: 9
  expected: fire
  note: +9 mmol/L/24h from nadir > 8 -> urgent (approaching ceiling)
- id: TV-3
  kind: boundary
  inputs:
    sodio: 130
    sodio_nadir_24h: 120
    correcao_na_24h_from_nadir: 10
  expected: fire
  note: exactly +10 from nadir is NOT > 10 (critical) but IS > 8 -> urgent; guards the 10/8 band edge
- id: TV-4
  kind: boundary
  inputs:
    sodio: 126
    sodio_nadir_24h: 118
    correcao_na_24h_from_nadir: 8
  expected: no-fire
  note: exactly +8 from nadir is NOT > 8 -> no-fire; guards the 8 mmol/L/24h floor
- id: TV-5
  kind: no-fire
  inputs:
    sodio: 124
    sodio_nadir_24h: 120
    correcao_na_24h_from_nadir: 4
  expected: no-fire
  note: controlled +4 mmol/L/24h correction from nadir -> no-fire
- id: TV-6
  kind: fire
  inputs:
    sodio: 132
    sodio_nadir_24h: 120
    correcao_na_24h_from_nadir: 12
    delta_na_24h_trailing: -8
  expected: fire
  note: 'Na 140->120->132: correction FROM NADIR is +12 (120->132) > 10 -> critical ODS risk. The TRAILING
    delta (132-140 = -8) is a net FALL and would MISS it entirely. Proves CORRECTION-02 MUST use correcao_na_24h_from_nadir,
    never the trailing delta_na_24h_trailing (HAZ-031 deterministic baseline; HAZ-032 catastrophic-ODS
    miss).'
reconciliation:
- existing_id: ELY-003
  status: extended
  note: 'vs alert-catalog.md: extends ELY-003c (''correção rápida demais — ALERTA DE SEGURANÇA'', correcao_na_24h_from_nadir>10)
    into a dedicated bidirectional rate alert with an added urgent band at >8 mmol/L/24h per vision VIS-3.6-06;
    enforces CON-0061 / CAT-C-01.'
```

<a id="alert-ely-calcium-01"></a>
### ALERT-ELY-CALCIUM-01 — Distúrbio grave do cálcio iônico — hipocalcemia/hipercalcemia

**Severity** critical · **Evidence** Mousseaux C et al. Hypercalcaemia in the ICU. Nephrol Dial Transplant 2022 (ionized Ca crit >1.60, urgent >1.45 mmol/L) — vision §3.6 VIS-3.6-07; Cooper MS et al. Diagnosis and management of hypocalcaemia in the critically ill. Intensive Care Med 2022 (ionized Ca crit <0.80, urgent <0.90 mmol/L) — vision §3.6 VIS-3.6-08 · **Rules** — · **PPV target** 0.82 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-ELY-CALCIUM-01
name: Distúrbio grave do cálcio iônico — hipocalcemia/hipercalcemia
severity: critical
trigger:
  logic: 'Severe calcium disturbance. IONIZED calcium (calcio_ionizado) is the primary measure; corrected
    TOTAL calcium is the fallback only when ionized is unavailable. calcio_total_corrigido = calcio_total
    + 0.8*(4.0 - albumina), albumina in g/dL. HYPO critical: calcio_ionizado < 0.80 mmol/L OR (calcio_ionizado
    unavailable AND calcio_total_corrigido < 7.0 mg/dL); HYPO urgent: calcio_ionizado < 0.90 mmol/L (and
    >= 0.80); HYPER critical: calcio_ionizado > 1.60 mmol/L OR (unavailable AND calcio_total_corrigido
    > 14.0 mg/dL); HYPER urgent: calcio_ionizado > 1.45 mmol/L (and <= 1.60). QTc context: hypocalcemia
    prolongs QTc — emit qtc_risk_electrolyte to pharmaco when qtc > 500 ms.

    '
  window: PT24H
inputs:
- name: calcio_ionizado
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result (LOINC 1994-3)
  staleness_max: PT12H
- name: calcio_total
  type: quantity
  unit: mg/dL
  source: AMH Gold lab_result (LOINC 17861-6); fallback when ionized unavailable
  staleness_max: PT12H
- name: albumina
  type: quantity
  unit: g/dL
  source: AMH Gold lab_result (LOINC 1751-7); for corrected-total-Ca fallback
  staleness_max: PT24H
- name: qtc
  type: quantity
  unit: ms
  source: AMH Gold Observation ECG QTc (LOINC 44974-4)
  staleness_max: PT24H
evidence:
- citation: Mousseaux C et al. Hypercalcaemia in the ICU. Nephrol Dial Transplant 2022 (ionized Ca crit
    >1.60, urgent >1.45 mmol/L) — vision §3.6 VIS-3.6-07
  rule_refs: []
- citation: Cooper MS et al. Diagnosis and management of hypocalcaemia in the critically ill. Intensive
    Care Med 2022 (ionized Ca crit <0.80, urgent <0.90 mmol/L) — vision §3.6 VIS-3.6-08
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id+direction+band
  cooldown: PT8H
  rate_limit: 3/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.82
  est_volume_per_100_beds_day: 2
  rationale: 'Ionized calcium is an objective, frequently-measured ICU value; ~2 severe events/100-beds/day
    (citrate anticoagulation/CRRT, sepsis, massive transfusion, malignancy). PPV slightly below the K/Na
    alerts because the corrected-TOTAL fallback (albumin-dependent) is less reliable than a direct ionized
    measurement and pH/tourniquet artifacts shift ionized Ca; the alert prefers ionized whenever present.
    Still well above the >=0.60 fleet floor.

    '
response:
  required: 'avaliação médica. Hipocalcemia crítica: gluconato de cálcio IV (estabilização) e corrigir
    magnésio (hipomagnesemia causa hipocalcemia refratária). Hipercalcemia crítica: hidratação salina,
    considerar calcitonina/bisfosfonato, investigar causa (malignidade/hiperparatireoidismo).

    '
  ack_sla: PT5M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    calcio_ionizado: 0.72
  expected: fire
  note: iCa 0.72 < 0.80 -> critical hypocalcemia
- id: TV-2
  kind: fire
  inputs:
    calcio_ionizado: 1.7
  expected: fire
  note: iCa 1.70 > 1.60 -> critical hypercalcemia
- id: TV-3
  kind: boundary
  inputs:
    calcio_ionizado: 0.8
  expected: fire
  note: iCa exactly 0.80 is NOT < 0.80 (critical) but IS < 0.90 -> urgent; guards 0.80/0.90 edge
- id: TV-4
  kind: boundary
  inputs:
    calcio_ionizado: 0.9
  expected: no-fire
  note: iCa exactly 0.90 is NOT < 0.90 -> no-fire; guards the 0.90 urgent floor
- id: TV-5
  kind: fire
  inputs:
    calcio_ionizado: null
    calcio_total: 6.0
    albumina: 4.0
  expected: fire
  note: ionized unavailable; corrected total = 6.0 + 0.8*(4.0-4.0) = 6.0 < 7.0 -> critical (fallback path)
- id: TV-6
  kind: no-fire
  inputs:
    calcio_ionizado: 1.2
  expected: no-fire
  note: normal ionized calcium -> no-fire
- id: TV-7
  kind: fire
  inputs:
    calcio_ionizado: 0.85
    qtc: 510
  expected: fire
  note: iCa 0.85 < 0.90 -> urgent; QTc 510>500 -> emits qtc_risk_electrolyte to pharmaco
reconciliation:
- existing_id: ELY-005
  status: changed
  note: 'vs alert-catalog.md: ELY-005 ''Distúrbio grave do cálcio'' (hypo/hyper bands a/b/c) folded into
    one bidirectional scaling alert; ionized-primary / corrected-total-fallback logic preserved verbatim;
    adds explicit QTc emission to pharmaco for hypocalcemia.'
```

<a id="alert-ely-magnesium-01"></a>
### ALERT-ELY-MAGNESIUM-01 — Hipomagnesemia grave

**Severity** critical · **Evidence** Hansen BA, Bruserud Ø. Hypomagnesemia in critically ill patients. Intensive Care Med Exp 2018;6:21 (crit <0.5, urgent <0.7 mmol/L) — vision §3.6 VIS-3.6-09 · **Rules** — · **PPV target** 0.75 · **Est. volume** 1/100 beds/day

```yaml alert-spec
alert_id: ALERT-ELY-MAGNESIUM-01
name: Hipomagnesemia grave
severity: critical
trigger:
  logic: 'Hypomagnesemia; output severity by band. critical if magnesio < 0.5 mmol/L (1.2 mg/dL); urgent
    if magnesio < 0.7 mmol/L (1.7 mg/dL) (and >= 0.5); watch if magnesio < 0.9 mmol/L AND (potassio <
    3.5 mmol/L OR qtc > 500 ms) [hypomagnesemia exacerbates hypokalemia and prolongs QTc].

    '
  window: PT24H
inputs:
- name: magnesio
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result (LOINC 19123-9)
  staleness_max: PT24H
- name: potassio
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result (LOINC 6298-4)
  staleness_max: PT24H
- name: qtc
  type: quantity
  unit: ms
  source: AMH Gold Observation ECG QTc (LOINC 44974-4)
  staleness_max: PT24H
evidence:
- citation: Hansen BA, Bruserud Ø. Hypomagnesemia in critically ill patients. Intensive Care Med Exp 2018;6:21
    (crit <0.5, urgent <0.7 mmol/L) — vision §3.6 VIS-3.6-09
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id+band
  cooldown: PT12H
  rate_limit: 2/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.75
  est_volume_per_100_beds_day: 1
  rationale: 'Hypomagnesemia is common in the ICU (diuretics, PPIs, diarrhea, alcohol), so the watch band
    is gated by a cofactor (K<3.5 or QTc>500) to stay actionable rather than firing on every mildly low
    magnesium. The critical/urgent bands are objective. ~1 firing/100-beds/day. PPV is set at 0.75 — lower
    than the K/Na alerts because a mildly low magnesium alone is often clinically minor; the cofactor
    gate keeps the watch band above the >=0.60 fleet floor. Its main value is feeding the pharmaco QTc/Torsades
    correlation.

    '
response:
  required: 'reposição de magnésio (sulfato de magnésio IV); corrigir hipocalemia/hipocalcemia refratárias
    em conjunto (magnésio baixo perpetua ambas); monitorar QTc se em uso de drogas QT-prolongadoras.

    '
  ack_sla: PT30M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    magnesio: 0.42
  expected: fire
  note: Mg 0.42 < 0.5 -> critical
- id: TV-2
  kind: fire
  inputs:
    magnesio: 0.62
  expected: fire
  note: Mg 0.62 < 0.7 -> urgent
- id: TV-3
  kind: boundary
  inputs:
    magnesio: 0.5
  expected: fire
  note: Mg exactly 0.5 is NOT < 0.5 (critical) but IS < 0.7 -> urgent; guards 0.5/0.7 edge
- id: TV-4
  kind: boundary
  inputs:
    magnesio: 0.9
    potassio: 3.0
  expected: no-fire
  note: Mg exactly 0.9 is NOT < 0.9 -> watch does not open even with hypokalemia; guards the 0.9 ceiling
- id: TV-5
  kind: fire
  inputs:
    magnesio: 0.8
    potassio: 3.2
  expected: fire
  note: Mg 0.8 < 0.9 AND K 3.2 < 3.5 -> watch; emits qtc_risk_electrolyte / hypoK-perpetuation to pharmaco+potassium
- id: TV-6
  kind: no-fire
  inputs:
    magnesio: 1.0
  expected: no-fire
  note: normal magnesium -> no-fire
reconciliation:
- existing_id: ELY-006
  status: changed
  note: 'vs alert-catalog.md: ELY-006 ''Hipomagnesemia'' folded and SEVERITY RAISED — legacy labeled <0.5
    URG / <0.7 WARN, but vision VIS-3.6-09 labels <0.5 CRITICAL / <0.7 URGENT. CONFLICT RECORDED (CONTRACTS
    rule 5): vision > legacy-catalog precedence resolves to vision; documented in electrolyte.md §6. Watch
    cofactor band (K<3.5 or QTc>500) preserved.'
```

<a id="alert-ely-phosphate-01"></a>
### ALERT-ELY-PHOSPHATE-01 — Distúrbio grave do fosfato — hipofosfatemia/hiperfosfatemia

**Severity** critical · **Evidence** Geerse DA et al. Treatment of hypophosphatemia in the intensive care unit: a review. Crit Care 2010;14:R147 (severe <0.32 mmol/L ~ <1.0 mg/dL; weaning failure/rhabdo) — designed default pending RAT-ELY-01; IntensiCare units registry fosfato canonical mg/dL (Brazilian-lab-convention); vision §3.6 VIS-3.6-10 lists PO4 as required data with no numeric band · **Rules** — · **PPV target** 0.65 · **Est. volume** 1/100 beds/day

```yaml alert-spec
alert_id: ALERT-ELY-PHOSPHATE-01
name: Distúrbio grave do fosfato — hipofosfatemia/hiperfosfatemia
severity: critical
trigger:
  logic: 'Phosphate disturbance. THRESHOLDS PENDING RATIFICATION (pending RAT-ELY-01): vision §3.6 names
    PO4 as required data (VIS-3.6-10) but gives NO numeric alert band, and the units registry flags fosfato
    canonical mg/dL as an open committee item — so these bands are DESIGNED TO THE RECOMMENDED DEFAULT
    and must be ratified before go-live. HYPO critical: fosfato < 1.0 mg/dL (severe: respiratory-muscle
    weakness, failure to wean, rhabdomyolysis); HYPO urgent: fosfato < 1.5 mg/dL (and >= 1.0); HYPER watch:
    fosfato > 7.0 mg/dL (marker of AKI / tumor-lysis; routes to AKI + oncologic-emergency review, not
    itself a bedside emergency).

    '
  window: PT24H
inputs:
- name: fosfato
  type: quantity
  unit: mg/dL
  source: AMH Gold lab_result (LOINC 2777-1)
  staleness_max: PT24H
- name: calcio_ionizado
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result (LOINC 1994-3); Ca x PO4 product context for hyperphosphatemia
  staleness_max: PT24H
- name: creatinina
  type: quantity
  unit: mg/dL
  source: AMH Gold lab_result (LOINC 2160-0); AKI/tumor-lysis context
  staleness_max: PT24H
evidence:
- citation: 'Geerse DA et al. Treatment of hypophosphatemia in the intensive care unit: a review. Crit
    Care 2010;14:R147 (severe <0.32 mmol/L ~ <1.0 mg/dL; weaning failure/rhabdo) — designed default pending
    RAT-ELY-01'
  rule_refs: []
- citation: IntensiCare units registry fosfato canonical mg/dL (Brazilian-lab-convention); vision §3.6
    VIS-3.6-10 lists PO4 as required data with no numeric band
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id+direction+band
  cooldown: PT12H
  rate_limit: 2/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.65
  est_volume_per_100_beds_day: 1
  rationale: 'Lowest-PPV alert in the domain (0.65, just above the 0.60 fleet floor) precisely because
    its thresholds are unratified (RAT-ELY-01) and the hyperphosphatemia band is a MARKER (AKI/tumor-lysis)
    rather than a bedside emergency — hence capped at watch to limit fatigue. Volume ~1/100-beds/day.
    If post-go-live ignored-rate on this alert approaches 10%, the hyperphosphatemia band is the first
    candidate to drop; ratification should confirm or tighten the <1.0 mg/dL critical cut.

    '
response:
  required: 'Hipofosfatemia grave: repor fosfato (IV/enteral), sobretudo em paciente em desmame ventilatório
    ou com fraqueza muscular. Hiperfosfatemia: investigar lise tumoral / LRA, considerar quelante de fósforo
    se indicado; correlacionar com o domínio AKI.

    '
  ack_sla: PT30M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    fosfato: 0.6
  expected: fire
  note: PO4 0.6 < 1.0 -> critical hypophosphatemia
- id: TV-2
  kind: fire
  inputs:
    fosfato: 1.3
  expected: fire
  note: PO4 1.3 < 1.5 -> urgent
- id: TV-3
  kind: boundary
  inputs:
    fosfato: 1.0
  expected: fire
  note: PO4 exactly 1.0 is NOT < 1.0 (critical) but IS < 1.5 -> urgent; guards 1.0/1.5 edge
- id: TV-4
  kind: boundary
  inputs:
    fosfato: 1.5
  expected: no-fire
  note: PO4 exactly 1.5 is NOT < 1.5 -> no-fire; guards the 1.5 urgent floor
- id: TV-5
  kind: fire
  inputs:
    fosfato: 8.5
    creatinina: 3.0
  expected: fire
  note: PO4 8.5 > 7.0 -> watch hyperphosphatemia (tumor-lysis/AKI marker)
- id: TV-6
  kind: no-fire
  inputs:
    fosfato: 3.0
  expected: no-fire
  note: normal phosphate -> no-fire
reconciliation:
- existing_id: null
  status: new
  note: No ELY-* catalog alert exists for phosphate; vision §3.6 VIS-3.6-10 lists PO4 as required data
    only. New alert; thresholds designed to recommended default pending RAT-ELY-01 (canonical unit + numeric
    bands to be ratified by the clinical committee).
```

## pharmaco-interaction (8 alerts)

<a id="alert-pharmaco-qtc-01"></a>
### ALERT-PHARMACO-QTC-01 — Prolongamento de QTc — risco de Torsades de Pointes

**Severity** critical · **Evidence** Tisdale JE et al. Circ Cardiovasc Qual Outcomes 2013;6(4):479-487 (QTc risk score); CredibleMeds QTdrugs List (Known Risk of TdP); Drew BJ et al. J Am Coll Cardiol 2010;55(9):934-947 · **Rules** — · **PPV target** 0.72 · **Est. volume** 1/100 beds/day

```yaml alert-spec
alert_id: ALERT-PHARMACO-QTC-01
name: Prolongamento de QTc — risco de Torsades de Pointes
severity: critical
trigger:
  logic: "qtc > 500 AND ( qt_prolonging_drug_count >= 2\n                OR ( delta_qtc > 60 AND qt_prolonging_drug_count\
    \ >= 1 ) ),\nwhere qt_prolonging_drug_count counts ACTIVE drugs on the CredibleMeds Known-Risk (TdP)\
    \ list (declarative KB, domain-doc §3.1). The lower substrate band (qtc > 500 AND exactly 1 Known-Risk\
    \ drug AND (potassio < 3.5 OR magnesio < 0.7)) is NOT a standalone push here: it is emitted as event\
    \ drug.qtc.prolonged and AMPLIFIED to critical by the correlation engine (correlation.qtc_electrolyte.detected,\
    \ VIS-4-03 'QTc + K+/Mg2+') to avoid a second WARN push.\n"
  window: PT24H
inputs:
- name: qtc
  type: quantity
  unit: ms
  source: AMH Gold Observation LOINC 44974-4 (QTc Bazett/Fridericia)
  staleness_max: PT24H
- name: delta_qtc
  type: quantity
  unit: ms
  source: 'derived: qtc - prior qtc (same lead/formula)'
  staleness_max: PT24H
- name: qt_prolonging_drug_count
  type: quantity
  unit: count
  source: derived from AMH Gold MedicationRequest+MedicationAdministration matched to CredibleMeds Known-Risk
    KB (domain §3.1)
  staleness_max: PT12H
- name: potassio
  type: quantity
  unit: mmol/L
  source: electrolyte domain / AMH Gold lab_result LOINC 6298-4
  staleness_max: PT12H
- name: magnesio
  type: quantity
  unit: mmol/L
  source: electrolyte domain / AMH Gold lab_result LOINC 19123-9
  staleness_max: PT12H
evidence:
- citation: Tisdale JE et al. Circ Cardiovasc Qual Outcomes 2013;6(4):479-487 (QTc risk score)
  rule_refs: []
- citation: CredibleMeds QTdrugs List (Known Risk of TdP); Drew BJ et al. J Am Coll Cardiol 2010;55(9):934-947
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT12H
  rate_limit: 2/24h/patient
  maintenance_window_aware: false
ppv_budget:
  target_ppv: 0.72
  est_volume_per_100_beds_day: 1
  rationale: 'QTc is Média-availability (DATA-AVAIL-07: automatic QTc varies), and QTc>500 ms WITH >=2
    Known-Risk drugs (or a >60 ms jump + >=1 drug) is an uncommon, high-specificity Torsades substrate
    (~1/100 beds/day). The >=2-drug / delta gate excludes isolated single-drug prolongation (routed to
    the correlation engine instead), so nearly every push is an actionable de-prescribe/replace-drug +
    correct-electrolytes decision -> PPV ~0.72. maintenance_window_aware:false (arrhythmia substrate is
    never maintenance-suppressible).'
response:
  required: 'revisão farmacológica imediata: suspender/substituir droga(s) QT-prolongadora(s), corrigir
    K+/Mg2+, monitorização de ECG'
  ack_sla: PT15M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    qtc: 520
    qt_prolonging_drug_count: 2
    delta_qtc: 20
    potassio: 4.0
    magnesio: 0.9
  expected: fire
  note: QTc 520 + 2 Known-Risk drugs -> primary Torsades band
- id: TV-2
  kind: no-fire
  inputs:
    qtc: 520
    qt_prolonging_drug_count: 1
    delta_qtc: 10
    potassio: 4.0
    magnesio: 0.9
  expected: no-fire
  note: only 1 Known-Risk drug, no delta jump, normal K+/Mg2+ -> emits drug.qtc.prolonged event for correlation
    but no standalone push
- id: TV-3
  kind: boundary
  inputs:
    qtc: 500
    qt_prolonging_drug_count: 3
    delta_qtc: 0
    potassio: 4.0
    magnesio: 0.9
  expected: no-fire
  note: 'boundary: QTc exactly 500 is NOT >500 (strict, vision §3.7 ''QTc > 500 ms''); no fire'
- id: TV-4
  kind: boundary
  inputs:
    qtc: 501
    qt_prolonging_drug_count: 2
    delta_qtc: 0
    potassio: 4.0
    magnesio: 0.9
  expected: fire
  note: 'boundary: QTc 501 just over 500 with 2 drugs -> fire'
- id: TV-5
  kind: fire
  inputs:
    qtc: 510
    qt_prolonging_drug_count: 1
    delta_qtc: 65
    potassio: 4.0
    magnesio: 0.9
  expected: fire
  note: 'delta branch: +65 ms jump (>60) with >=1 Known-Risk drug started between ECGs -> fire'
reconciliation:
  existing_id: DDX-001
  status: extended
  note: 'vs docs/clinical/alert-catalog.md DDX-001 ''Risco de Torsades por prolongamento de QTc + múltiplas
    drogas''. Same principal trigger (QTc>500 + >=2 CredibleMeds Known-Risk). EXTENDED: DDX-001b (>=1
    drug + K<3.5/Mg<0.7) and DDX-001c (delta>60) are folded — 001c becomes the delta branch here; 001b
    is offloaded to the correlation engine (correlation.qtc_electrolyte.detected) so the K+/Mg2+ amplification
    is ONE critical alert, not a second WARN, protecting the alarm-fatigue budget.'
```

<a id="alert-pharmaco-serotonin-02"></a>
### ALERT-PHARMACO-SEROTONIN-02 — Síndrome serotoninérgica — múltiplos agentes com sinais clínicos

**Severity** urgent · **Evidence** Boyer EW, Shannon M. NEJM 2005;352(11):1112-1120 (serotonin syndrome); Isbister GK et al. J Clin Psychiatry 2004; Hunter Serotonin Toxicity Criteria (clonus/hyperreflexia/hyperthermia) · **Rules** — · **PPV target** 0.68 · **Est. volume** 1/100 beds/day

```yaml alert-spec
alert_id: ALERT-PHARMACO-SEROTONIN-02
name: Síndrome serotoninérgica — múltiplos agentes com sinais clínicos
severity: urgent
trigger:
  logic: "serotonergic_agent_count >= 2 AND ( clonus == true OR hipertermia_sem_infeccao == true\n   \
    \                                 OR hiperreflexia == true ),\nwhere serotonergic_agent_count counts\
    \ ACTIVE agents on the serotonergic KB (domain §3.2: ISRS, ISRSN, linezolida, fentanil, ondansetrona,\
    \ metoclopramida, tramadol, azul de metileno, Hypericum). The asymptomatic >=3-agent case (DDX-002b)\
    \ is NOT pushed: it is emitted as event drug.serotonergic_load.high (surveillance) to protect PPV\
    \ — a drug list alone under-discriminates.\n"
  window: PT24H
inputs:
- name: serotonergic_agent_count
  type: quantity
  unit: count
  source: derived from AMH Gold MedicationRequest+MedicationAdministration matched to serotonergic KB
    (domain §3.2)
  staleness_max: PT12H
- name: clonus
  type: boolean
  unit: boolean
  source: AMH Gold Observation / nursing exam (clonus documentado)
  staleness_max: PT12H
- name: hipertermia_sem_infeccao
  type: boolean
  unit: boolean
  source: derived (temperatura > 38.0 degC without documented infection source)
  staleness_max: PT6H
- name: hiperreflexia
  type: boolean
  unit: boolean
  source: AMH Gold Observation / neuro exam (hiperreflexia documentada)
  staleness_max: PT12H
evidence:
- citation: Boyer EW, Shannon M. NEJM 2005;352(11):1112-1120 (serotonin syndrome)
  rule_refs: []
- citation: Isbister GK et al. J Clin Psychiatry 2004; Hunter Serotonin Toxicity Criteria (clonus/hyperreflexia/hyperthermia)
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT8H
  rate_limit: 3/24h/patient
  maintenance_window_aware: false
ppv_budget:
  target_ppv: 0.68
  est_volume_per_100_beds_day: 1
  rationale: 'The symptom gate (>=1 Hunter-criterion sign: clonus / hyperthermia-without-infection / hyperreflexia)
    is what makes this specific — >=2 serotonergic agents is common (linezolid+fentanyl, SSRI+ondansetron)
    but co-occurrence WITH a positive sign is rare (~1/100 beds/day) and directly actionable (stop the
    combination). PPV ~0.68. Asymptomatic polypharmacy is demoted to an event, not a push.'
response:
  required: suspender agentes serotoninérgicos, medidas de suporte, considerar ciproeptadina se toxicidade
    estabelecida
  ack_sla: PT30M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    serotonergic_agent_count: 2
    clonus: true
    hipertermia_sem_infeccao: false
    hiperreflexia: false
  expected: fire
  note: 2 agents (e.g. linezolida + fentanil) + clonus
- id: TV-2
  kind: no-fire
  inputs:
    serotonergic_agent_count: 3
    clonus: false
    hipertermia_sem_infeccao: false
    hiperreflexia: false
  expected: no-fire
  note: 3 agents but asymptomatic (DDX-002b) -> event drug.serotonergic_load.high only, no push
- id: TV-3
  kind: boundary
  inputs:
    serotonergic_agent_count: 1
    clonus: true
    hipertermia_sem_infeccao: false
    hiperreflexia: false
  expected: no-fire
  note: 'boundary: only 1 serotonergic agent (>=2 required) -> clonus alone does not fire'
- id: TV-4
  kind: boundary
  inputs:
    serotonergic_agent_count: 2
    clonus: false
    hipertermia_sem_infeccao: false
    hiperreflexia: false
  expected: no-fire
  note: 'boundary: exactly 2 agents but NO clinical sign -> no fire (symptom gate not met)'
reconciliation:
  existing_id: DDX-002
  status: changed
  note: 'vs DDX-002 ''Risco de síndrome serotoninérgica — múltiplos agentes''. CHANGED: the symptomatic
    branch is kept verbatim (urgent). DDX-002b (>=3 agents asymptomatic, WARN) is demoted from a push
    to event drug.serotonergic_load.high — a bare polypharmacy count without a Hunter sign is below the
    PPV floor and would drive ignored-rate, so it becomes surveillance, not an alarm.'
```

<a id="alert-pharmaco-cns-depression-03"></a>
### ALERT-PHARMACO-CNS-DEPRESSION-03 — Depressão respiratória por sinergismo de depressores do SNC

**Severity** critical · **Evidence** Overdyk FJ et al. Anesth Analg 2016;122(2):412-418 (opioid-induced respiratory depression); Lee LA et al. Anesthesiology 2015;122(3):659-665 (postoperative opioid respiratory depression) · **Rules** — · **PPV target** 0.63 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-PHARMACO-CNS-DEPRESSION-03
name: Depressão respiratória por sinergismo de depressores do SNC
severity: critical
trigger:
  logic: 'cns_depressant_count >= 2 AND ( frequencia_respiratoria < 10 OR spo2 < 90 ) AND ventilacao_mecanica_controlada
    == false, where cns_depressant_count counts ACTIVE CNS-depressant-class drugs (domain §3.3: opioides,
    benzodiazepínicos, gabapentinoides, antipsicóticos sedativos, barbitúricos, anti-histamínicos sedativos).
    Controlled-mode ventilation is excluded because a set RR/controlled SpO2 is not a spontaneous respiratory-depression
    signal (PPV gate).

    '
  window: PT1H
inputs:
- name: cns_depressant_count
  type: quantity
  unit: count
  source: derived from AMH Gold MedicationRequest+MedicationAdministration matched to CNS-depressant KB
    (domain §3.3)
  staleness_max: PT6H
- name: frequencia_respiratoria
  type: quantity
  unit: rpm
  source: AMH Gold Observation LOINC 9279-1 / monitor HL7 ORU
  staleness_max: PT1H
- name: spo2
  type: quantity
  unit: percent
  source: AMH Gold Observation LOINC 2708-6 / monitor HL7 ORU
  staleness_max: PT1H
- name: ventilacao_mecanica_controlada
  type: boolean
  unit: boolean
  source: Procedure / ventilator mode (controlled vs spontaneous)
  staleness_max: PT6H
evidence:
- citation: Overdyk FJ et al. Anesth Analg 2016;122(2):412-418 (opioid-induced respiratory depression)
  rule_refs: []
- citation: Lee LA et al. Anesthesiology 2015;122(3):659-665 (postoperative opioid respiratory depression)
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT2H
  rate_limit: 4/24h/patient
  maintenance_window_aware: false
ppv_budget:
  target_ppv: 0.63
  est_volume_per_100_beds_day: 2
  rationale: 'The physiologic gate (RR<10 OR SpO2<90) plus the controlled-ventilation exclusion turns
    a common polypharmacy state into a specific event: a spontaneously-breathing patient on >=2 CNS depressants
    who IS hypoventilating/desaturating (~2/100 beds/day). PPV ~0.63 — some fires are transient desaturations,
    but each warrants a naloxone/flumazenil-readiness + dose-review response. Critical severity because
    respiratory depression is imminently life-threatening (CAT-C-02, <5 min).'
response:
  required: 'avaliação beira-leito imediata: via aérea, revisão/redução de depressores do SNC, antagonista
    (naloxona/flumazenil) se indicado'
  ack_sla: PT15M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    cns_depressant_count: 2
    frequencia_respiratoria: 8
    spo2: 96
    ventilacao_mecanica_controlada: false
  expected: fire
  note: opioide + BZD, RR 8 (<10), spontaneous
- id: TV-2
  kind: no-fire
  inputs:
    cns_depressant_count: 2
    frequencia_respiratoria: 14
    spo2: 96
    ventilacao_mecanica_controlada: false
  expected: no-fire
  note: 2 depressants but RR 14 and SpO2 96 -> no respiratory compromise
- id: TV-3
  kind: boundary
  inputs:
    cns_depressant_count: 2
    frequencia_respiratoria: 10
    spo2: 95
    ventilacao_mecanica_controlada: false
  expected: no-fire
  note: 'boundary: RR exactly 10 is NOT <10 (strict, catalog rr<10rpm); SpO2 95 ok -> no fire'
- id: TV-4
  kind: boundary
  inputs:
    cns_depressant_count: 2
    frequencia_respiratoria: 12
    spo2: 89
    ventilacao_mecanica_controlada: false
  expected: fire
  note: 'boundary: SpO2 89 is <90 -> OR-branch fires'
- id: TV-5
  kind: no-fire
  inputs:
    cns_depressant_count: 2
    frequencia_respiratoria: 8
    spo2: 92
    ventilacao_mecanica_controlada: true
  expected: no-fire
  note: RR 8 but on CONTROLLED ventilation -> set-rate, not spontaneous depression (suppression gate)
reconciliation:
  existing_id: DDX-003
  status: extended
  note: vs DDX-003 'Depressão respiratória por sinergismo de depressores SNC'. Same trigger (>=2 CNS depressants
    + RR<10/SpO2<90). EXTENDED with a controlled-mechanical-ventilation suppression gate (a controlled
    set-rate is not spontaneous respiratory depression) to lift PPV. DDX-003b (>=3 depressants without
    continuous SpO2 monitoring, WARN) is handled as a monitoring-gap event, not a second push.
```

<a id="alert-pharmaco-dup-04"></a>
### ALERT-PHARMACO-DUP-04 — Duplicidade terapêutica — 2+ fármacos da mesma classe

**Severity** watch · **Evidence** ISMP Guidelines for Preventing Duplicate Therapy 2023; Maviglia SM et al. J Am Med Inform Assoc 2006;13(6):658-661 (duplicate-medication alerting) · **Rules** — · **PPV target** 0.6 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-PHARMACO-DUP-04
name: Duplicidade terapêutica — 2+ fármacos da mesma classe
severity: watch
trigger:
  logic: 'same_class_active_count >= 2 for a class flagged in the duplication KB (domain §3.4) AND indicacao_combinacao_documentada
    == false, where duplicated_class is one of {IBP, anticoagulante_dose_plena, antiagregante, antiemetico,
    antipsicotico, benzodiazepinico, AINE}. Documented dual-therapy indications (e.g. DAPT after recent
    stent) suppress.

    '
  window: PT24H
inputs:
- name: duplicated_class
  type: enum
  unit: enum
  source: 'derived: therapeutic class from AMH Gold MedicationRequest (ATC mapping, duplication KB §3.4)'
  staleness_max: PT12H
- name: same_class_active_count
  type: quantity
  unit: count
  source: derived count of active drugs within duplicated_class
  staleness_max: PT12H
- name: indicacao_combinacao_documentada
  type: boolean
  unit: boolean
  source: AMH Gold Condition / care-plan (documented combination indication)
  staleness_max: PT24H
evidence:
- citation: ISMP Guidelines for Preventing Duplicate Therapy 2023
  rule_refs: []
- citation: Maviglia SM et al. J Am Med Inform Assoc 2006;13(6):658-661 (duplicate-medication alerting)
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id+duplicated_class
  cooldown: PT24H
  rate_limit: 2/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 2
  rationale: 'The documented-indication suppression gate is the PPV lever: unintentional same-class duplication
    (2 PPIs, 2 antiemetics) is the target; intentional combinations (DAPT, scheduled+PRN BZD) are excluded.
    Deduped per class and rate-limited to 2/24h. ~2/100 beds/day. PPV ~0.60 (at the floor by design for
    a watch-level reconciliation nudge whose action cost is a single med-review); kept watch so it cannot
    drive ignored-rate.'
response:
  required: 'reconciliação medicamentosa: revisar necessidade de manter ambos os fármacos da mesma classe'
  ack_sla: PT2H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    duplicated_class: IBP
    same_class_active_count: 2
    indicacao_combinacao_documentada: false
  expected: fire
  note: omeprazol + pantoprazol, no indication for both
- id: TV-2
  kind: no-fire
  inputs:
    duplicated_class: antiagregante
    same_class_active_count: 2
    indicacao_combinacao_documentada: true
  expected: no-fire
  note: AAS + clopidogrel WITH documented DAPT indication (recent stent) -> suppressed
- id: TV-3
  kind: boundary
  inputs:
    duplicated_class: IBP
    same_class_active_count: 1
    indicacao_combinacao_documentada: false
  expected: no-fire
  note: 'boundary: only 1 drug in class (>=2 required) -> no duplication'
- id: TV-4
  kind: no-fire
  inputs:
    duplicated_class: null
    same_class_active_count: 2
    indicacao_combinacao_documentada: false
  expected: no-fire
  note: 2 active drugs but in DIFFERENT classes (no class flagged for duplication) -> no fire
reconciliation:
  existing_id: DDX-004
  status: aligned
  note: vs DDX-004 'Duplicidade terapêutica — 2+ medicamentos da mesma classe'. Same trigger (>=2 same-class
    active + no documented combination indication + class marked alerta_duplicidade). Severity mapped
    catalog WARN -> watch. Class KB preserved (§3.4).
```

<a id="alert-pharmaco-withdrawal-05"></a>
### ALERT-PHARMACO-WITHDRAWAL-05 — Risco de síndrome de abstinência por suspensão abrupta

**Severity** watch · **Evidence** Devlin JW et al. Crit Care Med 2018;46(9):e825-e873 (PADIS — iatrogenic withdrawal); Korak-Leiter M et al. Intensive Care Med 2005;31(3):380-387 (BZD/opioid withdrawal after prolonged sedation) · **Rules** — · **PPV target** 0.6 · **Est. volume** 1/100 beds/day

```yaml alert-spec
alert_id: ALERT-PHARMACO-WITHDRAWAL-05
name: Risco de síndrome de abstinência por suspensão abrupta
severity: watch
trigger:
  logic: "( bzd_continuo_gt_7d == true OR opioide_continuo_gt_7d == true ) AND suspensao_abrupta == true\
    \ AND ( frequencia_cardiaca > 100 OR pressao_arterial_sistolica > 160 OR temperatura > 38.0\n    \
    \  OR sudorese == true OR rass > 1 ),\nwhere suspensao_abrupta = discontinuation of a >7-day continuous\
    \ BZD/opioid with NO documented taper. Consumes neuro-sedation event neurosed.prolonged_sedation.flagged\
    \ for the >7d exposure.\n"
  window: PT24H
inputs:
- name: bzd_continuo_gt_7d
  type: boolean
  unit: boolean
  source: derived from AMH Gold MedicationAdministration (continuous BZD start >7d); neurosed.prolonged_sedation.flagged
  staleness_max: PT12H
- name: opioide_continuo_gt_7d
  type: boolean
  unit: boolean
  source: derived from AMH Gold MedicationAdministration (continuous opioid start >7d)
  staleness_max: PT12H
- name: suspensao_abrupta
  type: boolean
  unit: boolean
  source: 'derived: prior continuous agent absent from current MAR with no taper order'
  staleness_max: PT12H
- name: frequencia_cardiaca
  type: quantity
  unit: bpm
  source: AMH Gold Observation LOINC 8867-4 / monitor
  staleness_max: PT4H
- name: pressao_arterial_sistolica
  type: quantity
  unit: mmHg
  source: AMH Gold Observation LOINC 8480-6 / monitor
  staleness_max: PT4H
- name: temperatura
  type: quantity
  unit: degC
  source: AMH Gold Observation LOINC 8310-5 / monitor
  staleness_max: PT6H
- name: rass
  type: quantity
  unit: points
  source: neuro-sedation domain / AMH Gold Observation LOINC 75826-6 (signed -5..+4)
  staleness_max: PT4H
- name: sudorese
  type: boolean
  unit: boolean
  source: AMH Gold Observation / nursing record (diaphoresis)
  staleness_max: PT6H
evidence:
- citation: Devlin JW et al. Crit Care Med 2018;46(9):e825-e873 (PADIS — iatrogenic withdrawal)
  rule_refs: []
- citation: Korak-Leiter M et al. Intensive Care Med 2005;31(3):380-387 (BZD/opioid withdrawal after prolonged
    sedation)
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT12H
  rate_limit: 2/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 1
  rationale: 'Narrow conjunction: >7d continuous BZD/opioid AND abrupt stop (no taper) AND >=1 new autonomic
    sign. The exposure gate (>7d) and taper-absence gate exclude short courses and planned weans; the
    autonomic-sign gate excludes stable discontinuations (~1/100 beds/day). PPV ~0.60 — a genuine prompt
    to reinstate + taper. Watch severity (evolving, not imminently lethal).'
response:
  required: considerar reintrodução com desmame gradual do agente; tratar sintomas autonômicos
  ack_sla: PT2H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    bzd_continuo_gt_7d: true
    opioide_continuo_gt_7d: false
    suspensao_abrupta: true
    frequencia_cardiaca: 112
    pressao_arterial_sistolica: 140
    temperatura: 37.4
    sudorese: false
    rass: 0
  expected: fire
  note: '>7d BZD, abrupt stop, new tachycardia HR 112'
- id: TV-2
  kind: no-fire
  inputs:
    bzd_continuo_gt_7d: true
    opioide_continuo_gt_7d: false
    suspensao_abrupta: true
    frequencia_cardiaca: 84
    pressao_arterial_sistolica: 130
    temperatura: 36.8
    sudorese: false
    rass: 0
  expected: no-fire
  note: abrupt stop but NO autonomic sign -> no fire
- id: TV-3
  kind: boundary
  inputs:
    bzd_continuo_gt_7d: false
    opioide_continuo_gt_7d: false
    suspensao_abrupta: true
    frequencia_cardiaca: 112
    pressao_arterial_sistolica: 170
    temperatura: 38.2
    sudorese: true
    rass: 2
  expected: no-fire
  note: 'boundary: neither agent was continuous >7d (exposure gate false) -> no fire regardless of signs'
- id: TV-4
  kind: no-fire
  inputs:
    bzd_continuo_gt_7d: true
    opioide_continuo_gt_7d: false
    suspensao_abrupta: false
    frequencia_cardiaca: 112
    pressao_arterial_sistolica: 170
    temperatura: 38.2
    sudorese: true
    rass: 2
  expected: no-fire
  note: documented taper (suspensao_abrupta false) -> planned wean, suppressed
reconciliation:
  existing_id: DDX-005
  status: aligned
  note: vs DDX-005 'Risco de síndrome de abstinência por suspensão abrupta'. Same trigger (>7d continuous
    BZD/opioid + abrupt stop + >=1 autonomic sign HR>100/SBP>160/temp>38.0/sudorese/RASS>+1). Severity
    WARN -> watch. Exposure gate sourced from neuro-sedation neurosed.prolonged_sedation.flagged (cross-domain
    reuse).
```

<a id="alert-pharmaco-renaladj-06"></a>
### ALERT-PHARMACO-RENALADJ-06 — Antimicrobiano de eliminação renal sem ajuste para CrCl

**Severity** urgent · **Evidence** Rybak MJ et al. Am J Health Syst Pharm 2020;77(11):835-864 (vancomycin therapeutic monitoring); Matzke GR et al. Kidney Int 2011;80(11):1122-1137 (drug dosing in AKI/CKD); KDIGO Drug-Induced AKI 2023 · **Rules** RULE-ANTIMICROBIANO-003 · **PPV target** 0.65 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-PHARMACO-RENALADJ-06
name: Antimicrobiano de eliminação renal sem ajuste para CrCl
severity: urgent
trigger:
  logic: 'antimicrobiano_eliminacao_renal_ativo == true AND clearance_creatinina < 30 AND dose_excede_ajuste_renal
    == true AND drug NOT IN renal-adjust-exception KB {Polimixina B, Linezolida, Oxacilina, Tigeciclina,
    Clindamicina}. dose_excede_ajuste_renal is computed against the VERSIONED inline renal-dose lookup
    table (domain §3.6, replacing the legacy S3 PNG per CON-0139 / RULE-ANTIMICROBIANO-003).

    '
  window: PT24H
inputs:
- name: antimicrobiano_eliminacao_renal_ativo
  type: boolean
  unit: boolean
  source: 'derived: active antimicrobial matched to renally-cleared KB (domain §3.6) from AMH Gold MedicationRequest'
  staleness_max: PT12H
- name: clearance_creatinina
  type: quantity
  unit: mL/min
  source: derived Cockcroft-Gault from creatinina (LOINC 2160-0) + peso + idade + sex; canonical mL/min
    per registry clearance_creatinina (display alias CrCl; dosing-only, distinct from taxa_filtracao_glomerular/eGFR)
  staleness_max: PT24H
- name: dose_excede_ajuste_renal
  type: boolean
  unit: boolean
  source: 'derived: prescribed dose > recommended dose for CrCl band per versioned renal-dose table (domain
    §3.6)'
  staleness_max: PT12H
evidence:
- citation: Rybak MJ et al. Am J Health Syst Pharm 2020;77(11):835-864 (vancomycin therapeutic monitoring)
  rule_refs:
  - RULE-ANTIMICROBIANO-003
- citation: Matzke GR et al. Kidney Int 2011;80(11):1122-1137 (drug dosing in AKI/CKD); KDIGO Drug-Induced
    AKI 2023
  rule_refs:
  - RULE-ANTIMICROBIANO-003
suppression:
  dedup_key: patient_id+alert_id+drug
  cooldown: PT12H
  rate_limit: 3/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.65
  est_volume_per_100_beds_day: 2
  rationale: CrCl<30 mL/min AND a prescribed dose that exceeds the versioned renal-adjust table AND the
    drug is not on the no-adjust exception list — a computable, high-specificity mismatch (~2/100 beds/day).
    The exception KB (Polimixina B/Linezolida/Oxacilina/Tigeciclina/Clindamicina) removes the classic
    false positives. PPV ~0.65. Urgent because sub/over-dosing a renally-cleared antimicrobial risks toxicity
    or treatment failure (raised from catalog WARN given the additive AKI feedback).
response:
  required: ajuste de dose/intervalo do antimicrobiano à função renal (CrCl); considerar dosagem sérica
    quando disponível
  ack_sla: PT30M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    antimicrobiano_eliminacao_renal_ativo: true
    clearance_creatinina: 20
    dose_excede_ajuste_renal: true
  expected: fire
  note: vancomicina, CrCl 20, dose above renal-adjusted target
- id: TV-2
  kind: no-fire
  inputs:
    antimicrobiano_eliminacao_renal_ativo: true
    clearance_creatinina: 20
    dose_excede_ajuste_renal: false
  expected: no-fire
  note: renally-cleared drug at CrCl 20 but dose ALREADY adjusted -> no fire
- id: TV-3
  kind: boundary
  inputs:
    antimicrobiano_eliminacao_renal_ativo: true
    clearance_creatinina: 30
    dose_excede_ajuste_renal: true
  expected: no-fire
  note: 'boundary: CrCl exactly 30 is NOT <30 (strict, vision §3.7 ''CrCl < 30 mL/min'') -> no fire'
- id: TV-4
  kind: no-fire
  inputs:
    antimicrobiano_eliminacao_renal_ativo: true
    clearance_creatinina: 20
    dose_excede_ajuste_renal: true
    drug: Linezolida
  expected: no-fire
  note: Linezolida is on the renal-adjust EXCEPTION KB (no renal adjustment needed) -> suppressed (CON-0139)
reconciliation:
  existing_id: DDX-006
  status: extended
  note: 'vs DDX-006 ''Antimicrobiano com clearance renal sem ajuste para CrCl''. Same trigger (renally-cleared
    antimicrobial + CrCl<30 + dose>recommended). EXTENDED: the dose comparison is now against a VERSIONED
    inline renal-dose table (replacing the legacy S3 PNG, CON-0139) and an explicit no-adjust exception
    KB (Polimixina B/Linezolida/Oxacilina/Tigeciclina/Clindamicina); severity WARN -> urgent.'
```

<a id="alert-pharmaco-stewardship-07"></a>
### ALERT-PHARMACO-STEWARDSHIP-07 — Revisão de antimicrobiano — duração / de-escalonamento (stewardship)

**Severity** watch · **Evidence** Surviving Sepsis Campaign 2021, Evans L et al. Intensive Care Med 2021;47:1181-1247 (antimicrobial duration/de-escalation); Schuetz P et al. Cochrane 2017 CD007498 (procalcitonin-guided antibiotic de-escalation); IDSA/SHEA Antimicrobial Stewardship 2016; Antibiotic course tracking form (start/end, renal/hepatic adjust note, positive-culture note) · **Rules** RULE-ANTIMICROBIANO-003, RULE-PRESCRICAO-027 · **PPV target** 0.6 · **Est. volume** 3/100 beds/day

```yaml alert-spec
alert_id: ALERT-PHARMACO-STEWARDSHIP-07
name: Revisão de antimicrobiano — duração / de-escalonamento (stewardship)
severity: watch
trigger:
  logic: "antimicrobiano_ativo == true AND ( antimicrobiano_duracao_gt_7d == true\n  OR ( espectro_amplo\
    \ == true AND cultura_solicitada_48h == false )\n  OR de_escalonamento_disponivel == true ),\nwhere\
    \ de_escalonamento_disponivel is set by the sepsis/procalcitonin de-escalation signal (PCT<0.25 ng/mL\
    \ OR >80% drop from peak, or PCR<100 mg/L CAP context) OR a positive culture enabling narrowing. Adapts\
    \ the legacy antimicrobial-stewardship timers (RULE-ANTIMICROBIANO-003, criteria: duração >7d, espectro-amplo+internação>48h,\
    \ solicitação de culturas). Recommended default per RAT-ANTIMICROBIANO-01/02 (duration is a soft de-escalation-review\
    \ nudge, reset on documented spectrum change; all clinically-actionable criteria surfaced, not the\
    \ legacy 3,4,5,6,8 subset).\n"
  window: P7D
inputs:
- name: antimicrobiano_ativo
  type: boolean
  unit: boolean
  source: AMH Gold MedicationRequest (active antimicrobial)
  staleness_max: PT12H
- name: antimicrobiano_duracao_gt_7d
  type: boolean
  unit: boolean
  source: derived from MedicationAdministration start (>7d continuous, reset on documented spectrum change)
  staleness_max: PT12H
- name: espectro_amplo
  type: boolean
  unit: boolean
  source: 'derived: active drug on broad-spectrum KB (domain §3.7)'
  staleness_max: PT12H
- name: cultura_solicitada_48h
  type: boolean
  unit: boolean
  source: AMH Gold ServiceRequest/DiagnosticReport (culture ordered within 48h of antimicrobial start)
  staleness_max: PT48H
- name: de_escalonamento_disponivel
  type: boolean
  unit: boolean
  source: sepsis domain de-escalation signal (PCT<0.25 / >80% drop; PCR<100 CAP) OR positive culture enabling
    narrowing
  staleness_max: PT24H
evidence:
- citation: Surviving Sepsis Campaign 2021, Evans L et al. Intensive Care Med 2021;47:1181-1247 (antimicrobial
    duration/de-escalation)
  rule_refs:
  - RULE-ANTIMICROBIANO-003
- citation: Schuetz P et al. Cochrane 2017 CD007498 (procalcitonin-guided antibiotic de-escalation); IDSA/SHEA
    Antimicrobial Stewardship 2016
  rule_refs:
  - RULE-ANTIMICROBIANO-003
- citation: Antibiotic course tracking form (start/end, renal/hepatic adjust note, positive-culture note)
  rule_refs:
  - RULE-PRESCRICAO-027
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT48H
  rate_limit: 1/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 3
  rationale: A stewardship-review nudge, not a deterioration alarm. Evaluated once per patient/day, deduped
    to 1 fire per 48h, so at most ~3/100 beds/day. The three OR-branches (>7d duration, broad-spectrum-without-cultures,
    active de-escalation opportunity) are each an actionable review prompt. PPV ~0.60 (floor is acceptable
    for a low-burden review class whose action cost is a single stewardship-round decision); watch severity
    + heavy dedup keep it off the ignored-rate driver list.
response:
  required: 'revisão de stewardship: reavaliar duração, de-escalonar por cultura/PCT, confirmar solicitação
    de culturas'
  ack_sla: PT6H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    antimicrobiano_ativo: true
    antimicrobiano_duracao_gt_7d: true
    espectro_amplo: false
    cultura_solicitada_48h: true
    de_escalonamento_disponivel: false
  expected: fire
  note: '>7d continuous antimicrobial -> duration-review branch'
- id: TV-2
  kind: no-fire
  inputs:
    antimicrobiano_ativo: true
    antimicrobiano_duracao_gt_7d: false
    espectro_amplo: true
    cultura_solicitada_48h: true
    de_escalonamento_disponivel: false
  expected: no-fire
  note: day 3, broad-spectrum but cultures WERE sent, no de-escalation signal -> no fire
- id: TV-3
  kind: boundary
  inputs:
    antimicrobiano_ativo: true
    antimicrobiano_duracao_gt_7d: false
    espectro_amplo: false
    cultura_solicitada_48h: true
    de_escalonamento_disponivel: false
  expected: no-fire
  note: 'boundary: exactly 7d -> gt_7d flag false (>7d strict, RAT-ANTIMICROBIANO-01) -> no fire until
    day 8'
- id: TV-4
  kind: fire
  inputs:
    antimicrobiano_ativo: true
    antimicrobiano_duracao_gt_7d: false
    espectro_amplo: true
    cultura_solicitada_48h: false
    de_escalonamento_disponivel: true
  expected: fire
  note: de-escalation available (PCT<0.25 / >80% drop) -> de-escalation branch fires
reconciliation:
  existing_id: null
  status: new
  note: No DDX-* catalog alert covers antimicrobial stewardship (the DDX group is drug-interaction; stewardship
    is the legacy antimicrobiano trilha). NEW alert adapting RULE-ANTIMICROBIANO-003 (ADAPT) + RULE-PRESCRICAO-027
    (antibiotic course tracking, ADOPT-CORRECTED). Legacy VERMELHO/AMARELO/NEUTRO aggregation is superseded
    (RULE-ANTIMICROBIANO-001 SUPERSEDE) by the normal|watch|urgent|critical scale.
```

<a id="alert-pharmaco-cvc-fever-08"></a>
### ALERT-PHARMACO-CVC-FEVER-08 — Cateter venoso central > 7 dias com febre — investigar foco de cateter

**Severity** urgent · **Evidence** Mermel LA et al. Clin Infect Dis 2009;49(1):1-45 (IDSA intravascular catheter-related infection; fever 38.3 degC); Pappas PG et al. Clin Infect Dis 2016;62(4):e1-e50 (IDSA candidiasis — empiric echinocandin) · **Rules** RULE-ANTIMICROBIANO-003 · **PPV target** 0.6 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-PHARMACO-CVC-FEVER-08
name: Cateter venoso central > 7 dias com febre — investigar foco de cateter
severity: urgent
trigger:
  logic: 'cvc_dwell_gt_7d == true AND temperatura >= 38.3, where cvc_dwell_gt_7d = central venous catheter
    dwell time > 7 days and 38.3 degC is the IDSA fever definition (RULE-ANTIMICROBIANO-003 criterio_8).
    Advisory text carries the candidemia empiric-echinocandin branch (criterio_9/10, preserved distinct
    per CON-0140 / RAT-ANTIMICROBIANO-03) when candidemia risk factors are present.

    '
  window: PT24H
inputs:
- name: cvc_dwell_gt_7d
  type: boolean
  unit: boolean
  source: 'derived: CVC insertion Procedure timestamp > 7d ago, still in situ'
  staleness_max: PT12H
- name: temperatura
  type: quantity
  unit: degC
  source: AMH Gold Observation LOINC 8310-5 / monitor
  staleness_max: PT6H
evidence:
- citation: Mermel LA et al. Clin Infect Dis 2009;49(1):1-45 (IDSA intravascular catheter-related infection;
    fever 38.3 degC)
  rule_refs:
  - RULE-ANTIMICROBIANO-003
- citation: Pappas PG et al. Clin Infect Dis 2016;62(4):e1-e50 (IDSA candidiasis — empiric echinocandin)
  rule_refs:
  - RULE-ANTIMICROBIANO-003
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT12H
  rate_limit: 2/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 2
  rationale: CVC dwell >7d is common in ICU, but the conjunction with a new fever >=38.3 degC (IDSA) narrows
    to a specific catheter-source-workup prompt (~2/100 beds/day). PPV ~0.60 — fever has many sources,
    but the recommended action (paired blood cultures + reassess line necessity/removal) is low-cost and
    high-value; the alert is a workup prompt, not an infection diagnosis (VIS-C-01). Urgent (deterioração
    significativa, <30 min).
response:
  required: coletar hemoculturas pareadas (2x), reavaliar necessidade/troca do CVC; considerar equinocandina
    empírica se fatores de risco para candidemia
  ack_sla: PT30M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    cvc_dwell_gt_7d: true
    temperatura: 38.6
  expected: fire
  note: CVC >7d + febre 38.6
- id: TV-2
  kind: no-fire
  inputs:
    cvc_dwell_gt_7d: true
    temperatura: 37.5
  expected: no-fire
  note: CVC >7d but afebrile (37.5) -> no fire
- id: TV-3
  kind: boundary
  inputs:
    cvc_dwell_gt_7d: true
    temperatura: 38.3
  expected: fire
  note: 'boundary: temp exactly 38.3 meets IDSA fever definition (>=38.3, inclusive) -> fire'
- id: TV-4
  kind: boundary
  inputs:
    cvc_dwell_gt_7d: false
    temperatura: 39.0
  expected: no-fire
  note: 'boundary: CVC dwell NOT >7d (e.g. exactly 7d / line just placed) -> catheter-source prompt not
    triggered by fever alone'
reconciliation:
  existing_id: null
  status: new
  note: No DDX-* catalog alert covers CVC-source workup (legacy antimicrobiano trilha criterio_8). NEW
    alert adapting RULE-ANTIMICROBIANO-003 (ADAPT); preserves the candidemia workup duality (criterio_9
    full / criterio_10 fungi-only) as an advisory branch per CON-0140 (pending RAT-ANTIMICROBIANO-03),
    not a separate push.
```

## early-warning-scores (4 alerts)

<a id="alert-ews-news2-deterioration-01"></a>
### ALERT-EWS-NEWS2-DETERIORATION-01 — Deterioração clínica — NEWS2 alto (novo cruzamento >=7 ou parâmetro vermelho)

**Severity** urgent · **Evidence** Royal College of Physicians. National Early Warning Score (NEWS) 2. London: RCP, 2017; Smith GB et al. Resuscitation 2013;84(4):465-470 (NEWS validation); Legacy proprietary EWS temperature contiguity fix carried into NEWS2 banding · **Rules** RULE-PIORA-CLINICA-002 · **PPV target** 0.62 · **Est. volume** 5/100 beds/day

```yaml alert-spec
alert_id: ALERT-EWS-NEWS2-DETERIORATION-01
name: Deterioração clínica — NEWS2 alto (novo cruzamento >=7 ou parâmetro vermelho)
severity: urgent
trigger:
  logic: edge_trigger := ( news2_score >= 7 AND news2_score_prev < 7 ) OR ( any_single_parameter_score
    == 3 AND that_parameter_was_not_red_at_prev_measurement ). news2_score is the RCP-2017 aggregate 0-20
    (RR<=8|>=25=3, 9-11=1, 12-20=0, 21-24=2; SpO2 Scale1 >=96=0/94-95=1/92-93=2/<=91=3 or Scale2 hypercapnic
    >=93=0/88-92=1/86-87=2/84-85=2/<=83=3; supplemental_o2 +2; SBP<=90|>=220=3/91-100=2/101-110=1/111-219=0;
    HR<=40|>=131=3/41-50=1/51-90=0/91-110=1/111-130=2; ACVPU A=0 else 3; temp<=35.0=3/35.1-36.0=1/36.1-38.0=0/38.1-39.0=1/>=39.1=2).
    Scale 2 selected only when hypercapnic==true. Edge-triggered on the transition, NOT on persistent
    high state.
  window: PT1H
inputs:
- name: frequencia_respiratoria
  type: quantity
  unit: rpm
  source: AMH Gold Observation LOINC 9279-1
  staleness_max: PT1H
- name: saturacao_o2
  type: quantity
  unit: percent
  source: AMH Gold Observation LOINC 2708-6
  staleness_max: PT1H
- name: supplemental_o2
  type: boolean
  unit: boolean
  source: AMH Gold Observation (O2 therapy flag)
  staleness_max: PT1H
- name: hypercapnic
  type: boolean
  unit: boolean
  source: clinical context (chronic type-2 resp failure flag; RATIFY source RAT-EWS-01)
  staleness_max: PT7D
- name: pressao_arterial_sistolica
  type: quantity
  unit: mmHg
  source: AMH Gold Observation LOINC 8480-6
  staleness_max: PT1H
- name: frequencia_cardiaca
  type: quantity
  unit: bpm
  source: AMH Gold Observation LOINC 8867-4
  staleness_max: PT1H
- name: nivel_consciencia
  type: enum
  unit: enum
  source: AMH Gold Observation (ACVPU; enum {A,C,V,P,U}) — see open question, not yet in registry
  staleness_max: PT4H
- name: temperatura
  type: quantity
  unit: degC
  source: AMH Gold Observation LOINC 8310-5
  staleness_max: PT6H
- name: news2
  type: quantity
  unit: points
  source: clinical-scoring domain (this domain, NEWS2-v1.0.0)
  staleness_max: PT1H
evidence:
- citation: 'Royal College of Physicians. National Early Warning Score (NEWS) 2. London: RCP, 2017'
  rule_refs: []
- citation: Smith GB et al. Resuscitation 2013;84(4):465-470 (NEWS validation)
  rule_refs: []
- citation: Legacy proprietary EWS temperature contiguity fix carried into NEWS2 banding
  rule_refs:
  - RULE-PIORA-CLINICA-002
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT4H
  rate_limit: 3/24h/patient
  maintenance_window_aware: true
  note: Edge-trigger + 4h cooldown suppress the ICU chronic-high-NEWS2 flood; re-arms only after the score
    drops below 7 and no red parameter persists.
ppv_budget:
  target_ppv: 0.62
  est_volume_per_100_beds_day: 5
  rationale: A static NEWS2>=7 alert in ICU would fire on nearly every ventilated/pressor patient (PPV
    <0.2). Edge-triggering on the upward crossing + 4h cooldown restricts firing to genuine acute deteriorations,
    lifting PPV to ~0.62 and holding volume near 5/100 beds/day. NEWS2>=7 carries a documented ~10x rise
    in in-hospital mortality/ICU-transfer odds (Smith 2013), so a true crossing is highly actionable.
response:
  required: avaliação médica beira-leito + reavaliação do conjunto de sinais vitais
  ack_sla: PT15M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    news2: 7
    news2_score_prev: 4
  expected: fire
  note: new upward crossing into high-risk band
- id: TV-2
  kind: no-fire
  inputs:
    news2: 6
    news2_score_prev: 5
  expected: no-fire
  note: medium band (5-6) — handled by TREND alert, not a static alert here
- id: TV-3
  kind: boundary
  inputs:
    news2: 7
    news2_score_prev: 7
  expected: no-fire
  note: boundary — persistent high (already >=7 at prior), edge-trigger suppressed to avoid chronic-high
    ICU flood
- id: TV-4
  kind: fire
  inputs:
    news2: 5
    frequencia_respiratoria: 25
    rr_param_score: 3
    rr_was_red_prev: false
  expected: fire
  note: new single red parameter (RR>=25 => 3) even though aggregate only 5
reconciliation:
- existing_id: null
  status: new
  note: No v1.0.0 counterpart — docs/clinical/alert-catalog.md is entirely Phase-2 clinical detectors
    (SEP/AKI/RESP/HEMO/DEL/ELY/DDX) and contains no MEWS/NEWS2/SOFA/qSOFA early-warning-score alert. This
    is the Phase-1 EWS continuity workhorse, superseding the legacy proprietary piora-clinica aggregate
    (RULE-PIORA-CLINICA-010, RATIFY) with the validated NHS NEWS2.
```

<a id="alert-ews-trend-rising-02"></a>
### ALERT-EWS-TREND-RISING-02 — Tendência de piora — escore de alerta precoce em elevação

**Severity** watch · **Evidence** Subbe CP et al. QJM 2001;94(10):521-526 (MEWS; trend of the aggregate score predicts deterioration); Royal College of Physicians. NEWS2, London: RCP, 2017 (recommends acting on the trend, not only the absolute value) · **Rules** — · **PPV target** 0.6 · **Est. volume** 6/100 beds/day

```yaml alert-spec
alert_id: ALERT-EWS-TREND-RISING-02
name: Tendência de piora — escore de alerta precoce em elevação
severity: watch
trigger:
  logic: rising := ( news2_score - news2_score_at_window_start >= 3 ) OR ( mews_score - mews_score_at_window_start
    >= 3 ), measured across >=2 consecutive scorings within the window (MEWS trend requires >=2 samples,
    MEWS-1-29). Direction 'increasing' per compute_trend (MEWS-1-31). Delta threshold is >=3 (not >=2)
    to hold PPV above the fleet floor. Fires once per sustained rise (not per intermediate sample).
  window: PT8H
inputs:
- name: news2
  type: quantity
  unit: points
  source: clinical-scoring domain (NEWS2-v1.0.0)
  staleness_max: PT4H
- name: mews
  type: quantity
  unit: points
  source: clinical-scoring domain (MEWS-v1.0.0)
  staleness_max: PT4H
evidence:
- citation: Subbe CP et al. QJM 2001;94(10):521-526 (MEWS; trend of the aggregate score predicts deterioration)
  rule_refs: []
- citation: 'Royal College of Physicians. NEWS2, London: RCP, 2017 (recommends acting on the trend, not
    only the absolute value)'
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT6H
  rate_limit: 2/24h/patient
  maintenance_window_aware: true
  note: One alert per sustained rising episode; cooldown prevents re-firing on each new sample within
    the same deterioration.
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 6
  rationale: A +3 rise across consecutive scorings is a stronger deterioration signal than any single
    static band and precedes the >=7 crossing, buying lead time toward the vision's <1h early-detection
    target (VIS-7.1-01). Requiring >=3 (not >=2) and >=2 consecutive samples suppresses measurement noise
    and single-artifact spikes, keeping PPV at ~0.60 and volume ~6/100 beds/day.
response:
  required: reavaliação de enfermagem + aumentar frequência de aferição; escalonar se cruzar NEWS2>=7
  ack_sla: PT30M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    news2_score_at_window_start: 3
    news2: 7
  expected: fire
  note: delta +4 across window
- id: TV-2
  kind: no-fire
  inputs:
    news2_score_at_window_start: 5
    news2: 6
  expected: no-fire
  note: delta +1 below threshold
- id: TV-3
  kind: boundary
  inputs:
    news2_score_at_window_start: 4
    news2: 7
  expected: fire
  note: boundary — delta exactly +3 fires (>=3)
- id: TV-4
  kind: boundary
  inputs:
    mews_score_at_window_start: 4
    mews: 6
  expected: no-fire
  note: boundary — MEWS delta exactly +2, below +3 threshold, no-fire
reconciliation:
- existing_id: null
  status: new
  note: No v1.0.0 counterpart — no EWS-trend alert exists in the catalog. Absorbs the MEWS/NEWS2 medium-band
    and rising-trend signal so no static low-band snapshot alert is needed (deliberate alarm-fatigue design);
    MEWS itself keeps a computed score/event but no standalone alert, avoiding double-firing against ALERT-EWS-NEWS2-DETERIORATION-01.
```

<a id="alert-ews-sofa-acute-organ-dysfunction-03"></a>
### ALERT-EWS-SOFA-ACUTE-ORGAN-DYSFUNCTION-03 — Disfunção orgânica aguda — aumento de SOFA >=2

**Severity** urgent · **Evidence** Vincent JL et al. Intensive Care Med 1996;22(7):707-710 (SOFA); Singer M et al. JAMA 2016;315(8):801-810 (Sepsis-3: acute change in total SOFA >=2 = organ dysfunction); SOFA input assembly/sourcing adapted from legacy save-hook to deterministic compute service · **Rules** RULE-CLINICAL-SCORING-001, RULE-CLINICAL-SCORING-003, RULE-CLINICAL-SCORING-006, RULE-CLINICAL-SCORING-011, RULE-CLINICAL-SCORING-012 · **PPV target** 0.65 · **Est. volume** 4/100 beds/day

```yaml alert-spec
alert_id: ALERT-EWS-SOFA-ACUTE-ORGAN-DYSFUNCTION-03
name: Disfunção orgânica aguda — aumento de SOFA >=2
severity: urgent
trigger:
  logic: 'acute_organ_dysfunction := ( sofa_total - sofa_total_baseline_24h >= 2 ). sofa_total is the
    0-24 arithmetic sum of 6 sub-scores (RULE-CLINICAL-SCORING-001, ADOPT): respiration = P/F band with
    FiO2 as FRACTION (>=400=0/300-399=1/200-299=2/100-199=3(vent)/<100=4(vent)); coagulation platelets
    (>=150=0/100-149=1/50-99=2/20-49=3/<20=4); liver bilirubin mg/dL closed intervals (<1.2=0/1.2-1.9=1/2.0-5.9=2/6.0-11.9=3/>=12.0=4);
    cardiovascular vasopressor mcg/kg/min (MAP<70=1; dopa<=5=2/5.1-15=3/>15=4; norepi|epi<=0.1=3/>0.1=4;
    dobut any=2); CNS GCS (15=0/13-14=1/10-12=2/6-9=3/<6=4); renal = MAX(creatinine mg/dL band, urine-output
    band). A ΔSOFA>=2 is the Sepsis-3 organ-dysfunction definition (Singer 2016). SOFA sub-scores marked
    pending RAT-CLINICAL-SCORING-01..05 (P0 FiO2/vasopressor/renal/liver defects) are designed to the
    reference default.'
  window: PT24H
inputs:
- name: relacao_pao2_fio2
  type: quantity
  unit: ratio
  source: respiratory domain (pao2 mmHg / fio2 FRACTION 0.21-1.0)
  staleness_max: PT12H
- name: fio2
  type: quantity
  unit: fraction
  source: AMH Gold Observation LOINC 19935-6 (canonical fraction; percent is edge/display only)
  staleness_max: PT6H
- name: pao2
  type: quantity
  unit: mmHg
  source: AMH Gold blood gas LOINC 2703-7
  staleness_max: PT12H
- name: mechanical_ventilation
  type: boolean
  unit: boolean
  source: AMH Gold device/Procedure flag (gates SOFA-resp 3/4 bands, SOFA-C-02)
  staleness_max: PT6H
- name: plaquetas
  type: quantity
  unit: 10^3/uL
  source: AMH Gold lab_result LOINC 777-3
  staleness_max: PT24H
- name: bilirubina
  type: quantity
  unit: mg/dL
  source: AMH Gold lab_result LOINC 1975-2
  staleness_max: PT24H
- name: pressao_arterial_media
  type: quantity
  unit: mmHg
  source: AMH Gold Observation LOINC 8478-0
  staleness_max: PT1H
- name: dose_vasopressor
  type: quantity
  unit: mcg/kg/min
  source: hemodynamics domain conversion service (mL/h NOT convertible without concentration+peso, SYS-C-04)
  staleness_max: PT1H
- name: glasgow
  type: quantity
  unit: points
  source: AMH Gold Observation LOINC 9269-2
  staleness_max: PT8H
- name: creatinina
  type: quantity
  unit: mg/dL
  source: AMH Gold lab_result LOINC 2160-0 (via aki domain)
  staleness_max: PT24H
- name: debito_urinario
  type: quantity
  unit: mL
  source: aki domain (24h total; requires validated peso for rate form)
  staleness_max: PT24H
- name: peso
  type: quantity
  unit: kg
  source: AMH Gold Observation LOINC 29463-7 (validated parse; SYS-09)
  staleness_max: PT7D
- name: sofa
  type: quantity
  unit: points
  source: clinical-scoring domain (SOFA-v2.0.0)
  staleness_max: PT24H
evidence:
- citation: Vincent JL et al. Intensive Care Med 1996;22(7):707-710 (SOFA)
  rule_refs:
  - RULE-CLINICAL-SCORING-001
  - RULE-CLINICAL-SCORING-003
  - RULE-CLINICAL-SCORING-006
- citation: 'Singer M et al. JAMA 2016;315(8):801-810 (Sepsis-3: acute change in total SOFA >=2 = organ
    dysfunction)'
  rule_refs: []
- citation: SOFA input assembly/sourcing adapted from legacy save-hook to deterministic compute service
  rule_refs:
  - RULE-CLINICAL-SCORING-011
  - RULE-CLINICAL-SCORING-012
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT12H
  rate_limit: 2/24h/patient
  maintenance_window_aware: true
  note: SOFA is a daily organ-dysfunction score; 12h cooldown matches its measurement cadence and prevents
    re-firing on lab-batch jitter.
ppv_budget:
  target_ppv: 0.65
  est_volume_per_100_beds_day: 4
  rationale: ΔSOFA>=2 from a 24h baseline is the published Sepsis-3 organ-dysfunction anchor with strong
    association to mortality; an acute rise (not a static high SOFA) is what carries actionable PPV in
    ICU. Correct FiO2-fraction handling is essential — with percent FiO2 the respiratory sub-score is
    ~100x wrong (SYS-01), which would flood this alert with false organ dysfunction. Volume ~4/100 beds/day;
    PPV ~0.65.
response:
  required: avaliação médica; rastrear foco (sepse/SDRA/AKI) via correlation engine
  ack_sla: PT15M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    sofa: 6
    sofa_total_baseline_24h: 3
  expected: fire
  note: delta +3 acute organ dysfunction
- id: TV-2
  kind: no-fire
  inputs:
    sofa: 5
    sofa_total_baseline_24h: 4
  expected: no-fire
  note: delta +1 below Sepsis-3 anchor
- id: TV-3
  kind: boundary
  inputs:
    sofa: 4
    sofa_total_baseline_24h: 2
  expected: fire
  note: boundary — delta exactly +2 fires (Sepsis-3 >=2)
- id: TV-4
  kind: boundary
  inputs:
    pao2: 80
    fio2: 0.5
    mechanical_ventilation: true
    expected_pf_ratio: 160
    expected_resp_subscore: 3
  expected: fire
  note: 'FiO2-FRACTION correctness: P/F=80/0.5=160 => resp sub-score 3 on vent. If fio2 arrived as percent
    (50), P/F=1.6 would wrongly force sub-score 4 — the P0-01 defect this design fixes'
- id: TV-5
  kind: boundary
  inputs:
    creatinina: 5.0
    sofa: 4
    sofa_total_baseline_24h: 0
    expected_renal_subscore: 4
  expected: fire
  note: 'SOFA-renal boundary (HAZ-003/P0-03): creatinina exactly 5.0 mg/dL => renal sub-score 4 on the
    CLOSED >=5.0 edge, NOT 0. A re-introduced strict ''>5'' scores 0 here and MUST fail this vector. renal
    = MAX(cr band, urine band)'
- id: TV-6
  kind: boundary
  inputs:
    creatinina: 4.9
    sofa: 3
    sofa_total_baseline_24h: 0
    expected_renal_subscore: 3
  expected: fire
  note: 'SOFA-renal boundary (HAZ-019 dead gap): creatinina 4.9 mg/dL => renal sub-score 3 (3.5-4.9 band),
    one below the 5.0 edge; pins the (4.9,5.0] gap closed so 4.9 never falls through to 0/None'
- id: TV-7
  kind: boundary
  inputs:
    dose_vasopressor: 0.1
    vasopressor_agent: norepinephrine
    sofa: 3
    sofa_total_baseline_24h: 0
    expected_cardio_subscore: 3
  expected: fire
  note: 'SOFA-cardio boundary (HAZ-002/P0-02): norepinephrine exactly 0.10 mcg/kg/min => cardio sub-score
    3 (norepi <=0.1 = 3). Weight-indexed RATE via the conversion service, never a raw mL volume (SYS-C-04)'
- id: TV-8
  kind: boundary
  inputs:
    dose_vasopressor: 0.11
    vasopressor_agent: norepinephrine
    sofa: 4
    sofa_total_baseline_24h: 0
    expected_cardio_subscore: 4
  expected: fire
  note: 'SOFA-cardio boundary (HAZ-002/P0-02): norepinephrine 0.11 mcg/kg/min => cardio sub-score 4 (norepi
    >0.1 = 4); pins the 0.1 tier split so 0.10 vs 0.11 resolve 3 vs 4'
- id: TV-9
  kind: boundary
  inputs:
    bilirubina: 2.0
    sofa: 2
    sofa_total_baseline_24h: 0
    expected_liver_subscore: 2
  expected: fire
  note: 'SOFA-liver boundary (HAZ-019): bilirubina exactly 2.0 mg/dL => liver sub-score 2 (closed 2.0-5.9
    band), NOT 1; guards the [1.9,2.0) dead gap'
- id: TV-10
  kind: boundary
  inputs:
    bilirubina: 6.0
    sofa: 3
    sofa_total_baseline_24h: 0
    expected_liver_subscore: 3
  expected: fire
  note: 'SOFA-liver boundary (HAZ-019): bilirubina exactly 6.0 mg/dL => liver sub-score 3 (closed 6.0-11.9
    band); guards the [5.9,6.0) dead gap'
- id: TV-11
  kind: boundary
  inputs:
    bilirubina: 12.0
    sofa: 4
    sofa_total_baseline_24h: 0
    expected_liver_subscore: 4
  expected: fire
  note: 'SOFA-liver boundary (HAZ-019): bilirubina exactly 12.0 mg/dL => liver sub-score 4 (closed >=12.0);
    guards the [11.9,12.0) dead gap'
- id: TV-12
  kind: boundary
  inputs:
    pao2: 60
    fio2: 1.0
    mechanical_ventilation: true
    expected_pf_ratio: 60
    sofa: 4
    sofa_total_baseline_24h: 0
    expected_resp_subscore: 4
  expected: fire
  note: 'SOFA-resp boundary (HAZ-001/P0-01): P/F=60/1.0=60 (<100) on vent => resp sub-score 4; FiO2 is
    a FRACTION'
- id: TV-13
  kind: boundary
  inputs:
    pao2: 60
    fio2: 1.0
    mechanical_ventilation: false
    expected_pf_ratio: 60
    sofa: 2
    sofa_total_baseline_24h: 0
    expected_resp_subscore: 2
  expected: fire
  note: 'SOFA-resp VENTILATION GATE (HAZ-001 SOFA-C-02): identical P/F=60 but NOT ventilated CAPS resp
    sub-score at 2 — the 3/4 bands require mechanical ventilation. Pairs with TV-12 to prove the MV gate'
reconciliation:
- existing_id: null
  status: new
  note: 'No v1.0.0 counterpart — SOFA has no catalog alert. Distinct from catalog SEP-002 (qSOFA+lactato,
    owned by the sepsis domain, see sepsis.yaml reconciliation): this fires on delta-SOFA>=2 organ dysfunction
    and emits an event the sepsis/correlation domains consume; qSOFA is computed and emitted here but
    deliberately not alerted, avoiding a duplicate of the sepsis screen.'
```

<a id="alert-ews-discharge-readiness-04"></a>
### ALERT-EWS-DISCHARGE-READINESS-04 — Prontidão para alta/step-down da UTI

**Severity** normal · **Evidence** Carson JL et al. JAMA 2016;316(19):2025-2035 (AABB — restrictive/stability posture; facade intent RULE-EFICIENCIA-012); Singer M et al. JAMA 2016;315(8):801-810 (lactate <2 mmol/L as resolved-hypoperfusion stability marker) · **Rules** RULE-EFICIENCIA-001, RULE-EFICIENCIA-008 · **PPV target** 0.6 · **Est. volume** 8/100 beds/day

```yaml alert-spec
alert_id: ALERT-EWS-DISCHARGE-READINESS-04
name: Prontidão para alta/step-down da UTI
severity: normal
trigger:
  logic: 'discharge_ready := admitted_gt_24h AND glasgow >= 14 AND dose_vasopressor == 0 mcg/kg/min AND
    pressao_arterial_media >= 65 mmHg AND lactato_arterial < 2 mmol/L AND NOT mechanical_ventilation AND
    saturacao_o2 >= 92 percent on room air or low-flow O2 AND no_active_deterioration_alert (no EWS-01/-02/-03
    firing). Rebuilds RULE-EFICIENCIA-008 (ADAPT): corrects the wrong aggregate key (''temp''->''max_temp''),
    the truthiness GCS check (-> >=14), and the inverted TEC>5/lactate>2 requirement (-> absence of instability,
    lactate<2). Aggregation shape reuses RULE-EFICIENCIA-001 (ADAPT) count->enum but rewired so all sub-predicates
    actually reach the signal.'
  window: PT24H
inputs:
- name: glasgow
  type: quantity
  unit: points
  source: AMH Gold Observation LOINC 9269-2
  staleness_max: PT8H
- name: dose_vasopressor
  type: quantity
  unit: mcg/kg/min
  source: hemodynamics domain conversion service
  staleness_max: PT2H
- name: pressao_arterial_media
  type: quantity
  unit: mmHg
  source: AMH Gold Observation LOINC 8478-0
  staleness_max: PT2H
- name: lactato_arterial
  type: quantity
  unit: mmol/L
  source: AMH Gold lab_result LOINC 2524-7 (mmol/L only, SYS-03)
  staleness_max: PT6H
- name: mechanical_ventilation
  type: boolean
  unit: boolean
  source: AMH Gold device/Procedure flag
  staleness_max: PT2H
- name: saturacao_o2
  type: quantity
  unit: percent
  source: AMH Gold Observation LOINC 2708-6
  staleness_max: PT2H
evidence:
- citation: Carson JL et al. JAMA 2016;316(19):2025-2035 (AABB — restrictive/stability posture; facade
    intent RULE-EFICIENCIA-012)
  rule_refs:
  - RULE-EFICIENCIA-008
  - RULE-EFICIENCIA-001
- citation: Singer M et al. JAMA 2016;315(8):801-810 (lactate <2 mmol/L as resolved-hypoperfusion stability
    marker)
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT12H
  rate_limit: 2/24h/patient
  maintenance_window_aware: true
  note: Positive/efficiency signal; low cadence. Suppressed while any deterioration alert (EWS-01/-02/-03)
    is active for the same patient.
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 8
  rationale: A readiness signal (physician still owns the disposition, VIS-C-08) — 'PPV' here means the
    patient is genuinely step-down-eligible. Conjunctive gating (all stability criteria AND no active
    deterioration alert) keeps false-ready signals low; volume ~8/100 beds/day reflects the natural discharge
    cadence of a turning-over ICU. Low severity (normal, action <6h) keeps it off the acute channel.
response:
  required: revisão médica de elegibilidade para step-down; decisão de alta é do médico
  ack_sla: PT6H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    admitted_gt_24h: true
    glasgow: 15
    dose_vasopressor: 0
    pressao_arterial_media: 75
    lactato_arterial: 1.5
    mechanical_ventilation: false
    saturacao_o2: 96
    no_active_deterioration_alert: true
  expected: fire
  note: all stability criteria met
- id: TV-2
  kind: no-fire
  inputs:
    admitted_gt_24h: true
    glasgow: 15
    dose_vasopressor: 0.08
    pressao_arterial_media: 70
    lactato_arterial: 1.4
    mechanical_ventilation: false
    saturacao_o2: 96
    no_active_deterioration_alert: true
  expected: no-fire
  note: still on vasopressor — not ready
- id: TV-3
  kind: boundary
  inputs:
    admitted_gt_24h: true
    glasgow: 14
    dose_vasopressor: 0
    pressao_arterial_media: 65
    lactato_arterial: 2.0
    mechanical_ventilation: false
    saturacao_o2: 92
    no_active_deterioration_alert: true
  expected: no-fire
  note: boundary — lactate exactly 2.0 fails the strict <2 mmol/L stability gate
- id: TV-4
  kind: boundary
  inputs:
    admitted_gt_24h: true
    glasgow: 14
    dose_vasopressor: 0
    pressao_arterial_media: 65
    lactato_arterial: 1.9
    mechanical_ventilation: false
    saturacao_o2: 92
    no_active_deterioration_alert: true
  expected: fire
  note: boundary — GCS=14, MAP=65, lactate 1.9 all just inside the gates => ready
reconciliation:
- existing_id: null
  status: new
  note: No v1.0.0 counterpart — no discharge/step-down readiness alert exists in the catalog. Rebuilt
    from legacy RULE-EFICIENCIA-008 (ADAPT, corrected aggregate key / truthiness-GCS / inverted-TEC bugs);
    efficiency signal, normal severity.
```

## correlation-engine (4 alerts)

<a id="alert-corr-sepsis-aki-01"></a>
### ALERT-CORR-SEPSIS-AKI-01 — Sepse com lesão renal aguda associada (SA-AKI)

**Severity** critical · **Evidence** Zarbock A et al. Sepsis-associated acute kidney injury: consensus report of the 28th ADQI workgroup. Nat Rev Nephrol 2023;19:401-417 (SA-AKI definition; sepsis-first temporal ordering); Bagshaw SM et al. Septic acute kidney injury in critically ill patients. Clin J Am Soc Nephrol 2007;2(3):431-439 (sepsis is the leading cause of ICU AKI); KDIGO Clinical Practice Guideline for AKI. Kidney Int Suppl 2012;2(1):1-138 (KDIGO stage-1 creatinine/urine-output anchors, inherited from AKI domain); Evans L et al. Surviving Sepsis Campaign 2021. Crit Care Med 2021;49(11):e1063-e1143 (sepsis organ-dysfunction thresholds); vision VIS-3.2-01 (AKI 6.5x mortality), VIS-4-03 · **Rules** — · **PPV target** 0.8 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-CORR-SEPSIS-AKI-01
name: Sepse com lesão renal aguda associada (SA-AKI)
severity: critical
trigger:
  logic: "sepsis_active AND aki_active AND causal_temporal_link where sepsis_active := (event sepsis.organ_dysfunction.detected\
    \ OR sepsis.shock.detected) seen within PT72H; aki_active := event aki.stage.detected with kdigo_stage\
    \ >= 1\n  (creatinina rise >= 0.3 mg/dL over PT48H OR creatinina >= 1.5x baseline OR\n   debito_urinario_horario\
    \ < 0.5 mL/kg/h for >= PT6H) seen within PT72H;\ncausal_temporal_link := aki_onset_at is within PT72H\
    \ AT OR AFTER sepsis_onset_at\n  (sepsis-first ordering; concurrent within the same evaluation tick\
    \ counts as linked).\nEscalation stays critical; the emitted event carries kdigo_stage so the UI escalates\
    \ the renal message when stage >= 2 or when the sepsis member was sepsis.shock.detected. Thresholds\
    \ inherited from the member domains (KDIGO-2012 stage-1 anchors; Sepsis-3), NOT re-derived."
  window: PT72H
inputs:
- name: sepsis_event
  type: enum
  unit: enum
  source: sepsis domain event {sepsis.organ_dysfunction.detected, sepsis.shock.detected} via Redis pub/sub
  staleness_max: PT72H
- name: kdigo_stage
  type: enum
  unit: enum
  source: aki domain event aki.stage.detected (ordinal 0-3; OQ-CORR-01 — not yet a units-registry parameter)
  staleness_max: PT72H
- name: creatinina
  type: quantity
  unit: mg/dL
  source: aki domain event aki.stage.detected (field creatinina_mg_dL, AMH Gold lab_result LOINC 2160-0)
  staleness_max: PT48H
- name: debito_urinario_horario
  type: quantity
  unit: mL/kg/h
  source: aki domain event aki.stage.detected (requires validated peso, SYS-09)
  staleness_max: PT12H
- name: lactato_arterial
  type: quantity
  unit: mmol/L
  source: sepsis domain event (field lactato_arterial_mmol_L, AMH Gold lab_result LOINC 2524-7)
  staleness_max: PT6H
- name: sepsis_onset_at
  type: quantity
  unit: s
  source: sepsis domain event detected_at (epoch seconds)
  staleness_max: PT72H
- name: aki_onset_at
  type: quantity
  unit: s
  source: aki domain event detected_at (epoch seconds)
  staleness_max: PT72H
evidence:
- citation: 'Zarbock A et al. Sepsis-associated acute kidney injury: consensus report of the 28th ADQI
    workgroup. Nat Rev Nephrol 2023;19:401-417 (SA-AKI definition; sepsis-first temporal ordering)'
  rule_refs: []
- citation: Bagshaw SM et al. Septic acute kidney injury in critically ill patients. Clin J Am Soc Nephrol
    2007;2(3):431-439 (sepsis is the leading cause of ICU AKI)
  rule_refs: []
- citation: KDIGO Clinical Practice Guideline for AKI. Kidney Int Suppl 2012;2(1):1-138 (KDIGO stage-1
    creatinine/urine-output anchors, inherited from AKI domain)
  rule_refs: []
- citation: Evans L et al. Surviving Sepsis Campaign 2021. Crit Care Med 2021;49(11):e1063-e1143 (sepsis
    organ-dysfunction thresholds); vision VIS-3.2-01 (AKI 6.5x mortality), VIS-4-03
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT12H
  rate_limit: 3/24h/patient
  maintenance_window_aware: false
  member_suppression: folds member sepsis.organ_dysfunction/shock alert + AKI stage alert (SEP-002/AKI-001..004)
    for the cooldown; members still logged to prontuário NGS-2
ppv_budget:
  target_ppv: 0.8
  est_volume_per_100_beds_day: 2
  rationale: 'Requiring BOTH an already-specific sepsis organ-dysfunction/shock event AND a KDIGO>=1 event,
    joined by sepsis-first temporal ordering, is strictly more specific than either member (each of which
    is already gated) — so PPV is high (~0.80) despite AKI''s many non-septic causes, because the sepsis
    member excludes them. Sepsis ~30% ICU incidence (VIS-3.1-01) and AKI 30-60% (VIS-3.2-01) co-occur
    in a smaller septic-AKI subset; estimated ~2/100 beds/day. This ONE critical alert REPLACES the separate
    sepsis and AKI pushes (net -1..-2 pushes/patient) — fewer, richer alerts. maintenance_window_aware
    false: a two-organ-failure alert must never be muted by a maintenance window.'
response:
  required: avaliação médica imediata beira-leito — controle de foco + reanimação dirigida com atenção
    à nefroproteção (evitar nefrotóxicos, revisar dose renal); registrar no prontuário NGS-2
  ack_sla: PT15M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    sepsis_event: sepsis.organ_dysfunction.detected
    sepsis_onset_at: 0
    aki_onset_at: 36000
    kdigo_stage: 1
    creatinina: 1.9
    lactato_arterial: 3.2
  expected: fire
  note: sepsis then AKI KDIGO-1 10h later — sepsis-first causal link within 72h fires
- id: TV-2
  kind: fire
  inputs:
    sepsis_event: sepsis.shock.detected
    sepsis_onset_at: 0
    aki_onset_at: 7200
    kdigo_stage: 2
    debito_urinario_horario: 0.28
  expected: fire
  note: septic shock + KDIGO-2 oliguria 2h later — most severe combined path
- id: TV-3
  kind: no-fire
  inputs:
    sepsis_event: null
    kdigo_stage: 2
    creatinina: 2.4
  expected: no-fire
  note: AKI present but NO sepsis member event — routes to AKI domain alert, not a correlation
- id: TV-4
  kind: no-fire
  inputs:
    sepsis_event: sepsis.organ_dysfunction.detected
    sepsis_onset_at: 0
    aki_onset_at: null
    kdigo_stage: 0
  expected: no-fire
  note: sepsis present but KDIGO-0 (no AKI) — routes to sepsis domain alert only
- id: TV-5
  kind: boundary
  inputs:
    sepsis_event: sepsis.organ_dysfunction.detected
    sepsis_onset_at: 0
    aki_onset_at: 259200
    kdigo_stage: 1
  expected: no-fire
  note: 'boundary exact-threshold: AKI onset exactly 72h (259200 s) after sepsis is the window edge but
    strict > sepsis_onset ordering holds; join uses within PT72H inclusive of edge -> set to just-outside
    (259201 s) semantics — at exactly 72h+epsilon the causal window has closed, no-fire'
- id: TV-6
  kind: boundary
  inputs:
    sepsis_event: sepsis.organ_dysfunction.detected
    sepsis_onset_at: 0
    aki_onset_at: 258000
    kdigo_stage: 1
    creatinina: 1.6
  expected: fire
  note: 'boundary: AKI onset ~71.7h after sepsis, inside the PT72H causal window -> fires'
reconciliation:
- existing_id: null
  status: new
  note: No v1.0.0 counterpart — the correlation engine is a new cross-domain layer; no catalog alert correlated
    sepsis and AKI. At runtime this suppresses (folds) the member alerts owned by the sepsis domain (ORGAN-02/SHOCK-03,
    successors of catalog SEP-002) and the AKI domain (KDIGO stage alerts, successors of catalog AKI-001..004)
    into one push; those members are not dropped, they remain owned by their domains and stay logged to
    prontuário NGS-2.
```

<a id="alert-corr-resp-hemo-02"></a>
### ALERT-CORR-RESP-HEMO-02 — Falência cardiopulmonar combinada (SDRA moderada/grave + choque)

**Severity** critical · **Evidence** ARDS Definition Task Force. Acute respiratory distress syndrome: the Berlin Definition. JAMA 2012;307(23):2526-2533 (moderate PaO2/FiO2 <=200); Asfar P et al. High versus low blood-pressure target in septic shock (SEPSISPAM). N Engl J Med 2014;370(17):1583-1593 (MAP target >=65 mmHg); Vieillard-Baron A et al. Acute cor pulmonale in ARDS. Intensive Care Med 2016;42(5):862-870 (ARDS+shock RV failure interaction — rationale for combined alert); vision VIS-3.3 (Berlin severity), VIS-3.4-01 (unrecognized shock mortality >80%), VIS-4-03 (SDRA + choque) · **Rules** — · **PPV target** 0.85 · **Est. volume** 1/100 beds/day

```yaml alert-spec
alert_id: ALERT-CORR-RESP-HEMO-02
name: Falência cardiopulmonar combinada (SDRA moderada/grave + choque)
severity: critical
trigger:
  logic: "ards_moderate_or_severe AND shock_active seen within PT6H of each other where ards_moderate_or_severe\
    \ := event respiratory.ards.detected with\n  (relacao_pao2_fio2 <= 200 ratio OR relacao_spo2_fio2\
    \ <= 235 ratio)   # Berlin moderate/severe\nAND shock_active := event hemodynamic.shock.detected\n\
    \  OR (pressao_arterial_media < 65 mmHg AND dose_vasopressor > 0 mcg/kg/min).\nBerlin moderate/severe\
    \ anchor (PaO2/FiO2 <= 200) inherited from the respiratory domain; FiO2 MUST be the canonical fraction\
    \ (SYS-01) or the ratio is ~100x wrong. MAP<65 and vasopressor already canonical mcg/kg/min from hemodynamics\
    \ (mL/h NOT convertible without concentration+weight, CON-0060/SYS-C-04)."
  window: PT6H
inputs:
- name: relacao_pao2_fio2
  type: quantity
  unit: ratio
  source: respiratory domain event respiratory.ards.detected (FiO2 canonical fraction, SYS-01)
  staleness_max: PT6H
- name: relacao_spo2_fio2
  type: quantity
  unit: ratio
  source: respiratory domain event respiratory.ards.detected (non-invasive surrogate)
  staleness_max: PT6H
- name: ards_severity
  type: enum
  unit: enum
  source: respiratory domain event field ards_severity {leve, moderada, grave}
  staleness_max: PT6H
- name: pressao_arterial_media
  type: quantity
  unit: mmHg
  source: hemodynamics domain event (AMH Gold Observation LOINC 8478-0)
  staleness_max: PT1H
- name: dose_vasopressor
  type: quantity
  unit: mcg/kg/min
  source: hemodynamics domain event (conversion service, CON-0060)
  staleness_max: PT1H
- name: shock_event
  type: boolean
  unit: boolean
  source: hemodynamics domain event hemodynamic.shock.detected presence
  staleness_max: PT6H
evidence:
- citation: 'ARDS Definition Task Force. Acute respiratory distress syndrome: the Berlin Definition. JAMA
    2012;307(23):2526-2533 (moderate PaO2/FiO2 <=200)'
  rule_refs: []
- citation: Asfar P et al. High versus low blood-pressure target in septic shock (SEPSISPAM). N Engl J
    Med 2014;370(17):1583-1593 (MAP target >=65 mmHg)
  rule_refs: []
- citation: Vieillard-Baron A et al. Acute cor pulmonale in ARDS. Intensive Care Med 2016;42(5):862-870
    (ARDS+shock RV failure interaction — rationale for combined alert)
  rule_refs: []
- citation: vision VIS-3.3 (Berlin severity), VIS-3.4-01 (unrecognized shock mortality >80%), VIS-4-03
    (SDRA + choque)
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT4H
  rate_limit: 4/24h/patient
  maintenance_window_aware: false
  member_suppression: folds member RESP-002 (SDRA moderada/grave) + HEMO-003 (escalonamento de vasopressor)
    pushes for the cooldown; members still logged to prontuário NGS-2
ppv_budget:
  target_ppv: 0.85
  est_volume_per_100_beds_day: 1
  rationale: 'The intersection of moderate/severe ARDS AND concurrent shock is narrow and carries the
    highest combined mortality (unrecognized shock >80%, VIS-3.4-01) — so PPV is the highest of the clinical
    correlations (~0.85). Both members are already specific detector events; requiring co-occurrence within
    6h excludes isolated respiratory or isolated circulatory failure. Estimated ~1/100 beds/day. This
    ONE critical alert REPLACES the separate ARDS and vasopressor-escalation pushes. maintenance_window_aware
    false: life-threatening two-organ failure.'
response:
  required: ativação de equipe de resposta rápida — ventilação protetora + manejo de choque simultâneos;
    avaliar disfunção de VD (ecocardiograma à beira-leito)
  ack_sla: PT5M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    relacao_pao2_fio2: 150
    ards_severity: moderada
    shock_event: true
  expected: fire
  note: moderate ARDS (P/F 150) + active shock event within 6h
- id: TV-2
  kind: fire
  inputs:
    relacao_pao2_fio2: 90
    ards_severity: grave
    pressao_arterial_media: 58
    dose_vasopressor: 0.25
  expected: fire
  note: severe ARDS + MAP<65 on vasopressor — refractory shock branch
- id: TV-3
  kind: no-fire
  inputs:
    relacao_pao2_fio2: 260
    ards_severity: leve
    shock_event: true
  expected: no-fire
  note: only MILD ARDS (P/F>200) + shock — mild ARDS excluded; routes to hemodynamic domain alert
- id: TV-4
  kind: no-fire
  inputs:
    relacao_pao2_fio2: 150
    ards_severity: moderada
    pressao_arterial_media: 78
    dose_vasopressor: 0
    shock_event: false
  expected: no-fire
  note: moderate ARDS but NO shock — routes to respiratory domain alert only
- id: TV-5
  kind: boundary
  inputs:
    relacao_pao2_fio2: 200
    ards_severity: moderada
    shock_event: true
  expected: fire
  note: 'boundary exact-threshold: P/F=200 is <=200 (inclusive, Berlin moderate) with shock -> fires'
- id: TV-6
  kind: boundary
  inputs:
    relacao_pao2_fio2: 201
    ards_severity: leve
    pressao_arterial_media: 65
    dose_vasopressor: 0.1
    shock_event: false
  expected: no-fire
  note: 'boundary: P/F=201 is NOT <=200 (mild), and MAP=65 is NOT <65 — neither gate met'
reconciliation:
- existing_id: null
  status: new
  note: No v1.0.0 counterpart — suppresses/folds the member alerts owned by the respiratory domain (SDRA
    moderada/grave, successor of catalog RESP-002) and the hemodynamics domain (ALERT-HEMO-VASO-ESCALATION-03
    / ALERT-HEMO-SHOCK-INDEX-01, successors of catalog HEMO-003/HEMO-001) when they co-occur within 6h.
    Members remain owned by their domains; none dropped.
```

<a id="alert-corr-qtc-elec-03"></a>
### ALERT-CORR-QTC-ELEC-03 — Substrato de Torsades amplificado — QTc prolongado + hipocalemia/hipomagnesemia

**Severity** critical · **Evidence** Drew BJ et al. Prevention of Torsade de Pointes in Hospital Settings: AHA/ACCF Scientific Statement. Circulation 2010;121(8):1047-1060 (QTc>500 + hypoK/hypoMg + QT drug = reversible TdP substrate); Tisdale JE et al. Development and validation of a risk score to predict QT prolongation. Circ Cardiovasc Qual Outcomes 2013;6(4):479-487 (QTc>500 ms; hypokalemia/loop-diuretic risk factors); CredibleMeds QTdrugs List (Known Risk of TdP); vision VIS-3.7-02 (QTc>500 + >=2 drugs), VIS-3.6-02 (K+ thresholds), VIS-3.6-09 (Mg2+ thresholds), VIS-4-03 · **Rules** — · **PPV target** 0.7 · **Est. volume** 1/100 beds/day

```yaml alert-spec
alert_id: ALERT-CORR-QTC-ELEC-03
name: Substrato de Torsades amplificado — QTc prolongado + hipocalemia/hipomagnesemia
severity: critical
trigger:
  logic: 'qtc > 500 ms AND qt_prolonging_drug_count >= 1                     # >=1 CredibleMeds Known-Risk
    drug active AND ( potassio < 3.5 mmol/L OR magnesio < 0.7 mmol/L ) joined within PT24H (QTc ECG, active-drug
    list, and electrolyte result all within the window). AMPLIFICATION rule: individually the QTc member
    (drug domain DDX-001b) and the electrolyte members (ELY-002c hipocalemia-tendência, ELY-006c hipomagnesemia-contexto)
    are WARN; their co-occurrence is the reversible-cause TdP substrate (Drew 2010 AHA/ACCF), so the correlation
    ESCALATES to critical and surfaces the correctable trigger (hold QT drug + repor K+/Mg2+).'
  window: PT24H
inputs:
- name: qtc
  type: quantity
  unit: ms
  source: drug-interaction domain event drug.qtc.prolonged (AMH Gold Observation LOINC 44974-4)
  staleness_max: PT24H
- name: qt_prolonging_drug_count
  type: quantity
  unit: count
  source: drug-interaction domain event (CredibleMeds Known-Risk active drug count)
  staleness_max: PT24H
- name: potassio
  type: quantity
  unit: mmol/L
  source: electrolyte domain event electrolyte.hypokalemia.detected (AMH Gold lab_result LOINC 6298-4)
  staleness_max: PT24H
- name: magnesio
  type: quantity
  unit: mmol/L
  source: electrolyte domain event electrolyte.hypomagnesemia.detected (AMH Gold lab_result LOINC 19123-9)
  staleness_max: PT24H
evidence:
- citation: 'Drew BJ et al. Prevention of Torsade de Pointes in Hospital Settings: AHA/ACCF Scientific
    Statement. Circulation 2010;121(8):1047-1060 (QTc>500 + hypoK/hypoMg + QT drug = reversible TdP substrate)'
  rule_refs: []
- citation: Tisdale JE et al. Development and validation of a risk score to predict QT prolongation. Circ
    Cardiovasc Qual Outcomes 2013;6(4):479-487 (QTc>500 ms; hypokalemia/loop-diuretic risk factors)
  rule_refs: []
- citation: CredibleMeds QTdrugs List (Known Risk of TdP); vision VIS-3.7-02 (QTc>500 + >=2 drugs), VIS-3.6-02
    (K+ thresholds), VIS-3.6-09 (Mg2+ thresholds), VIS-4-03
  rule_refs: []
suppression:
  dedup_key: patient_id+alert_id
  cooldown: PT8H
  rate_limit: 3/24h/patient
  maintenance_window_aware: false
  member_suppression: folds member DDX-001 QTc alert + ELY-002/ELY-006 electrolyte-context alerts for
    the cooldown; members still logged to prontuário NGS-2
ppv_budget:
  target_ppv: 0.7
  est_volume_per_100_beds_day: 1
  rationale: Three co-occurring predicates (QTc>500 ms, an active Known-Risk drug, and hypoK OR hypoMg)
    select the precise TdP substrate the vision names (QTc + K+/Mg2+); PPV ~0.70 (below the ARDS/sepsis
    correlations because QTc measurement/algorithm variance and asymptomatic prolongation remain, CAT-DDX-001).
    Set to critical by AMPLIFICATION — the whole point of the correlation is that neither WARN member
    alone conveys the arrhythmia risk. Estimated ~1/100 beds/day. This ONE alert replaces the QTc + electrolyte
    pushes, and its explainability lists the specific correctable drug + electrolyte so the action is
    one decision, not three separate WARNs to reconcile.
response:
  required: revisão médica/farmacêutica imediata — suspender/substituir fármaco prolongador de QT + repor
    K+/Mg2+; monitorização eletrocardiográfica contínua
  ack_sla: PT15M
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    qtc: 520
    qt_prolonging_drug_count: 1
    potassio: 3.1
  expected: fire
  note: QTc>500 + 1 QT drug + hypokalemia (K 3.1) — amplified critical
- id: TV-2
  kind: fire
  inputs:
    qtc: 540
    qt_prolonging_drug_count: 2
    magnesio: 0.55
  expected: fire
  note: QTc>500 + 2 QT drugs + hypomagnesemia (Mg 0.55) fires on the Mg branch
- id: TV-3
  kind: no-fire
  inputs:
    qtc: 520
    qt_prolonging_drug_count: 1
    potassio: 4.2
    magnesio: 0.9
  expected: no-fire
  note: QTc prolonged on a QT drug but normal K+ and Mg2+ — no electrolyte substrate; stays a WARN in
    the drug domain (DDX-001b), not amplified
- id: TV-4
  kind: no-fire
  inputs:
    qtc: 520
    qt_prolonging_drug_count: 0
    potassio: 3.0
  expected: no-fire
  note: QTc prolonged + hypokalemia but NO QT-prolonging drug active — routes to electrolyte domain (ELY-002c),
    correctable-drug arm absent
- id: TV-5
  kind: boundary
  inputs:
    qtc: 500
    qt_prolonging_drug_count: 1
    potassio: 3.0
  expected: no-fire
  note: 'boundary exact-threshold: QTc=500 is NOT >500 (strict), matches DDX-001 anchor -> no-fire'
- id: TV-6
  kind: boundary
  inputs:
    qtc: 501
    qt_prolonging_drug_count: 1
    potassio: 3.5
    magnesio: 0.7
  expected: no-fire
  note: 'boundary: QTc just >500 and a drug active, but K=3.5 is NOT <3.5 and Mg=0.7 is NOT <0.7 (both
    strict) — no electrolyte substrate'
- id: TV-7
  kind: boundary
  inputs:
    qtc: 501
    qt_prolonging_drug_count: 1
    potassio: 3.49
  expected: fire
  note: 'boundary: QTc 501>500, drug active, K 3.49<3.5 -> substrate complete, fires'
reconciliation:
- existing_id: null
  status: new
  note: No v1.0.0 counterpart — amplifies (escalates watch->critical) and folds the member alerts owned
    by the pharmaco-interaction domain (QTc/Torsades, successor of catalog DDX-001) and the electrolyte
    domain (hipocalemia/hipomagnesemia context arms, successors of catalog ELY-002/ELY-006). Members remain
    owned by their domains; none dropped.
```

<a id="alert-corr-exam-redund-04"></a>
### ALERT-CORR-EXAM-REDUND-04 — Solicitação redundante de exame (mesma classe dentro da janela de reavaliação)

**Severity** normal · **Evidence** RULE-EFICIENCIA-007 (ADAPT) — legacy redundant-exam-ordering intent; per-class window mechanism corrected; Halpern SD et al. An official ATS/ACCP/SCCM/AACN policy statement: Choosing Wisely in critical care. Crit Care Med 2014 (avoid repeated routine diagnostics without a new question) · **Rules** RULE-EFICIENCIA-007 · **PPV target** 0.6 · **Est. volume** 2/100 beds/day

```yaml alert-spec
alert_id: ALERT-CORR-EXAM-REDUND-04
name: Solicitação redundante de exame (mesma classe dentro da janela de reavaliação)
severity: normal
category: efficiency-stewardship
suppression_accounting: excluded
trigger:
  logic: "for a NEW exam order of exam_class C:\n  repeat := EXISTS a prior resulted/pending order of\
    \ the SAME class C whose result_at/order_at is\n  within C's class-specific reassessment window W(C)\n\
    \  where W(hemograma)=PT120H (5d), W(bioquimica_rotina)=PT168H (7d), W(rx_torax_rotina)=PT336H (14d),\n\
    \  W(marcadores_tireoide)=PT504H (21d), W(sorologias)=PT720H (30d);   # per-class, NOT summed\nfire\
    \ when repeat is true for that class. CORRECTED from RULE-EFICIENCIA-007's legacy defect that summed\
    \ positive window-hits ACROSS unrelated exam classes into one undifferentiated threshold; v2 evaluates\
    \ each class against its OWN window (ADAPT — same cost/burden intent, corrected mechanism)."
  window: PT720H
inputs:
- name: exam_class
  type: enum
  unit: enum
  source: AMH Gold ServiceRequest category (exam-class taxonomy)
  staleness_max: PT720H
- name: prior_order_within_window
  type: boolean
  unit: boolean
  source: AMH Gold ServiceRequest/DiagnosticReport (same-class prior order/result within W(class))
  staleness_max: PT720H
- name: hours_since_prior_same_class
  type: quantity
  unit: count
  source: derived (hours between prior same-class order/result and the new order)
  staleness_max: PT720H
evidence:
- citation: RULE-EFICIENCIA-007 (ADAPT) — legacy redundant-exam-ordering intent; per-class window mechanism
    corrected
  rule_refs:
  - RULE-EFICIENCIA-007
- citation: 'Halpern SD et al. An official ATS/ACCP/SCCM/AACN policy statement: Choosing Wisely in critical
    care. Crit Care Med 2014 (avoid repeated routine diagnostics without a new question)'
  rule_refs: []
suppression:
  dedup_key: patient_id+exam_class
  cooldown: PT24H
  rate_limit: 3/24h/patient
  maintenance_window_aware: true
ppv_budget:
  target_ppv: 0.6
  est_volume_per_100_beds_day: 2
  rationale: 'Deterministic order-history correlation (not a physiological prediction): it fires on a
    genuine same-class repeat within a clinically-set window, so PPV sits at the fleet floor (0.60) —
    the residual false positives are legitimately-justified repeats (a new clinical question), which the
    clinician dismisses in one tap. Severity normal (informational stewardship, <6h) keeps it OUT of the
    deterioration-alarm attention budget so it cannot erode the <=10% ignored-rate target of the critical
    alerts. Estimated ~2/100 beds/day. Per-class dedup + 24h cooldown prevent a busy-ordering storm.'
response:
  required: confirmar necessidade clínica do exame repetido ou cancelar (revisão do prescritor)
  ack_sla: PT6H
test_vectors:
- id: TV-1
  kind: fire
  inputs:
    exam_class: hemograma
    prior_order_within_window: true
    hours_since_prior_same_class: 48
  expected: fire
  note: hemograma re-ordered 48h after a prior one, inside the 5-day (120h) window
- id: TV-2
  kind: no-fire
  inputs:
    exam_class: hemograma
    prior_order_within_window: false
    hours_since_prior_same_class: 150
  expected: no-fire
  note: prior hemograma 150h ago (>120h window) — legitimately due, no redundancy
- id: TV-3
  kind: no-fire
  inputs:
    exam_class: rx_torax_rotina
    prior_order_within_window: false
    hours_since_prior_same_class: 200
  expected: no-fire
  note: CXR 200h (<336h window) but NO prior same-class order flagged — cross-class hits are NOT summed
    (the corrected behavior)
- id: TV-4
  kind: boundary
  inputs:
    exam_class: hemograma
    prior_order_within_window: true
    hours_since_prior_same_class: 120
  expected: no-fire
  note: 'boundary exact-threshold: prior exactly 120h (5d) ago is AT the window edge — window is strict
    ''< W'' so 120h is outside -> no-fire'
- id: TV-5
  kind: boundary
  inputs:
    exam_class: hemograma
    prior_order_within_window: true
    hours_since_prior_same_class: 119
  expected: fire
  note: 'boundary: prior 119h ago (<120h) is inside the window -> redundant, fires'
reconciliation:
- existing_id: null
  status: new
  note: No v1.0.0 counterpart — new efficiency correlation carried from legacy RULE-EFICIENCIA-007 (ADAPT);
    no catalog alert covered redundant diagnostic ordering. Standalone (no member alert to suppress);
    a stewardship signal, not a fold of existing deterioration alerts.
```

## Reconciliation vs docs/clinical/alert-catalog.md (v1.0.0)

| Existing | New alert | Status | Note |
|---|---|---|---|
| AKI-001 | ALERT-AKI-KDIGO-STAGE-01 | changed | vs docs/clinical/alert-catalog.md: KDIGO stage 1 (WARN) folded into stage-scaling alert; UO window c |
| AKI-002 | ALERT-AKI-KDIGO-STAGE-01 | changed | vs alert-catalog.md: KDIGO stage 2 (URG) folded in; UO rolling 12h replaces nursing-day window; seve |
| AKI-003 | ALERT-AKI-KDIGO-STAGE-01 | changed | vs alert-catalog.md: KDIGO stage 3 (CRIT) folded in; adds RRT-initiation and anuria(12h) to critical |
| AKI-004 | ALERT-AKI-PROGRESSION-02 | extended | vs alert-catalog.md: AKI-004 'Progressão AKI' aligned; extended with severity escalation to critical |
| AKI-005 | ALERT-AKI-NEPHROTOXIN-03 | extended | vs alert-catalog.md: AKI-005 'Risco de AKI por nefrotoxicidade aditiva' aligned; extended with an ex |
| DDX-001 | ALERT-PHARMACO-QTC-01 | extended | vs docs/clinical/alert-catalog.md DDX-001 'Risco de Torsades por prolongamento de QTc + múltiplas dr |
| DDX-002 | ALERT-PHARMACO-SEROTONIN-02 | changed | vs DDX-002 'Risco de síndrome serotoninérgica — múltiplos agentes'. CHANGED: the symptomatic branch  |
| DDX-003 | ALERT-PHARMACO-CNS-DEPRESSION-03 | extended | vs DDX-003 'Depressão respiratória por sinergismo de depressores SNC'. Same trigger (>=2 CNS depress |
| DDX-004 | ALERT-PHARMACO-DUP-04 | aligned | vs DDX-004 'Duplicidade terapêutica — 2+ medicamentos da mesma classe'. Same trigger (>=2 same-class |
| DDX-005 | ALERT-PHARMACO-WITHDRAWAL-05 | aligned | vs DDX-005 'Risco de síndrome de abstinência por suspensão abrupta'. Same trigger (>7d continuous BZ |
| DDX-006 | ALERT-PHARMACO-RENALADJ-06 | extended | vs DDX-006 'Antimicrobiano com clearance renal sem ajuste para CrCl'. Same trigger (renally-cleared  |
| DEL-001 | ALERT-NEUROSED-AGITATION-02 | changed | vs DEL-001 (agitation branch): promoted from WARN to urgent and split into its own alert because sel |
| DEL-001 | ALERT-NEUROSED-OVERSED-01 | changed | vs docs/clinical/alert-catalog.md DEL-001 'Sedação fora da faixa alvo (RASS)': DEL-001's deep-sedati |
| DEL-002 | ALERT-NEUROSED-DELIRIUM-04 | aligned | vs DEL-002 'Delirium — CAM-ICU positivo'; same trigger and evidence (Ely 2001). Severity mapped cata |
| DEL-003 | ALERT-NEUROSED-IATRO-06 | aligned | vs DEL-003 'Risco de delirium iatrogênico — sedação inadequada'; same conjunction (BZD infusion + ag |
| DEL-004 | ALERT-NEUROSED-SCREEN-GAP-05 | extended | vs DEL-004 'Delirium hipoativo possivelmente não reconhecido'; adds an explicit >24h rolling cadence |
| ELY-001 | ALERT-ELY-POTASSIUM-01 | changed | vs docs/clinical/alert-catalog.md: hyperkalemia ELY-001 (a/b/c bands) folded into a per-ion scaling  |
| ELY-002 | ALERT-ELY-POTASSIUM-01 | changed | vs alert-catalog.md: hypokalemia ELY-002 (a/b/c bands) folded into the same potassium alert; the hig |
| ELY-003 | ALERT-ELY-SODIUM-01 | changed | vs alert-catalog.md: hyponatremia ELY-003 absolute bands (a crit<120, b urgent<125) folded here; add |
| ELY-003 | ALERT-ELY-SODIUM-CORRECTION-02 | extended | vs alert-catalog.md: extends ELY-003c ('correção rápida demais — ALERTA DE SEGURANÇA', correcao_na_2 |
| ELY-004 | ALERT-ELY-SODIUM-01 | changed | vs alert-catalog.md: hypernatremia ELY-004 (a/b/c) folded here; restores the RULE-EQUILIBRIO-002 Na> |
| ELY-005 | ALERT-ELY-CALCIUM-01 | changed | vs alert-catalog.md: ELY-005 'Distúrbio grave do cálcio' (hypo/hyper bands a/b/c) folded into one bi |
| ELY-006 | ALERT-ELY-MAGNESIUM-01 | changed | vs alert-catalog.md: ELY-006 'Hipomagnesemia' folded and SEVERITY RAISED — legacy labeled <0.5 URG / |
| HEMO-001 | ALERT-HEMO-SHOCK-INDEX-01 | changed | vs alert-catalog.md HEMO-001 'Shock Index > 0,9 — hipoperfusão oculta' (URG/P2): legacy fired on SI> |
| HEMO-002 | ALERT-HEMO-LACTATE-CLEARANCE-02 | aligned | vs alert-catalog.md HEMO-002 'Clearance de lactato < 10% em 2h' (CRIT/P2): carried forward essential |
| HEMO-003 | ALERT-HEMO-VASO-ESCALATION-03 | changed | vs alert-catalog.md HEMO-003 'Escalonamento de vasopressor' (CRIT/P2): legacy bundled three triggers |
| HEMO-004 | ALERT-HEMO-FLUID-NONRESPONSIVE-05 | aligned | vs alert-catalog.md HEMO-004 'Não responsivo a fluidos — risco de sobrecarga' (WARN/P3): carried for |
| RESP-001 | ALERT-RESP-ARDS-STAGING-01 | changed | vs docs/clinical/alert-catalog.md — mild ARDS (S/F<=315, WARN) folded as the WATCH tier of the stage |
| RESP-002 | ALERT-RESP-ARDS-STAGING-01 | extended | moderate (S/F<=235, URG) and severe/002b (S/F<=148, CRIT) consolidated into one staged alert with UR |
| RESP-003 | ALERT-RESP-DETERIORATION-02 | extended | vs alert-catalog.md — same S/F/FiO2 trend logic; adds >=2-sample persistence + airway-maintenance ex |
| RESP-004 | ALERT-RESP-WEANING-READY-04 | extended | vs alert-catalog.md — RESP-004 readiness bundle (INFO->normal); adds RULE-VENTILACAO-007 arousal dis |
| SEP-001 | ALERT-SEPSIS-SCREEN-01 | changed | vs alert-catalog.md SEP-001 'SIRS positivo com suspeita de infecção' (URG/P1): legacy required a str |
| SEP-002 | ALERT-SEPSIS-ORGAN-02 | extended | vs alert-catalog.md SEP-002 'qSOFA positivo com lactato elevado ou em elevação' (CRIT/P1): carried f |
| SEP-003 | ALERT-SEPSIS-PCT-RISING-05 | changed | vs alert-catalog.md SEP-003 'Procalcitonina — orientação para antibioticoterapia' (INFO(a)/URG(b), P |
