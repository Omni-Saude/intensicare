# Pharmaco-Interaction Domain — IntensiCare v2 Clinical Specification

**Guild:** Clinical (pharmaco-interaction domain designer) · **Vision ref:** §3.7 (Interações Medicamentosas,
priority **P6**) · **Platform:** AMH Data Platform consumer (ADR-001) · **Legacy clusters:** `prescricao` (41 rules,
home-care MAR/pharmacist forms), `equilibrio` (4 rules, nephrotoxic-substitution + Na/K protocols), `antimicrobiano`
(3 rules, stewardship trilha).

ICU patients receive on average **12–20 simultaneous medications**; serious drug interactions (contraindications, QTc
prolongation, serotonin syndrome) account for **5–10 % of ICU adverse events** (VIS-3.7-01). This domain detects the
four high-consequence interaction classes named in the vision — **QTc-prolonging combinations, serotonergic
combinations, nephrotoxic stacking, CNS-depression stacking** — plus **therapeutic duplication**, **withdrawal on
abrupt discontinuation**, **renal-dose mismatch**, and adapts the legacy **antimicrobial-stewardship timers** as
stewardship alerts. The interaction knowledge base is **declarative and versioned** (§3).

All outputs are **advisory, physician-owned** (VIS-C-01, VIS-C-08), recorded to the prontuário at **NGS Level 2**
(VIS-C-07). **No automatic diagnosis** — every alert is a de-prescribe / adjust / investigate prompt, never a
diagnosis (VIS-C-01, keeps the SaMD Classe II classification, VIS-C-02).

---

## 1. Clinical scope

**In scope (8 alerts, §4).**

1. **QTc-prolonging combinations** → Torsades risk (`ALERT-PHARMACO-QTC-01`, critical) — with K⁺/Mg²⁺ amplification
   handed to the correlation engine (vision §4.1 "QTc + K⁺/Mg²⁺", VIS-4-03).
2. **Serotonergic combinations** → serotonin syndrome (`ALERT-PHARMACO-SEROTONIN-02`, urgent).
3. **CNS-depression stacking** → synergistic respiratory depression (`ALERT-PHARMACO-CNS-DEPRESSION-03`, critical).
4. **Therapeutic duplication** (`ALERT-PHARMACO-DUP-04`, watch).
5. **Withdrawal syndrome** on abrupt BZD/opioid discontinuation (`ALERT-PHARMACO-WITHDRAWAL-05`, watch).
6. **Renal-dose mismatch** for renally-cleared antimicrobials (`ALERT-PHARMACO-RENALADJ-06`, urgent).
7. **Antimicrobial-stewardship review** — duration / de-escalation timers adapted from the legacy `antimicrobiano`
   trilha (`ALERT-PHARMACO-STEWARDSHIP-07`, watch).
8. **CVC dwell + fever** — catheter-source workup with candidemia branch (`ALERT-PHARMACO-CVC-FEVER-08`, urgent).

**Out of scope / delegated.**
- **Nephrotoxic-stacking *firing alert*** → the **AKI** domain. This domain maintains the versioned nephrotoxic KB
  (§3.5) and emits `pharmaco.nephrotoxic_burden.changed`, but the patient-facing alert
  (`ALERT-AKI-NEPHROTOXIN-03`, catalog **AKI-005**) is owned by AKI so the "nefrotoxicidade aditiva" signal is a
  **single** push, not two (alarm-fatigue hygiene). Legacy `RULE-EQUILIBRIO-002`'s nephrotoxic-substitution content
  (Cefepime→Tazocin, Vancomicina→Linezolida, morphine avoidance under impaired clearance) feeds §3.5 and the
  renal-dose reasoning (§3.6) as decision-support vocabulary.
- **Hyperkalemia rescue (K > 6) and hypernatremia (Na > 160) correction protocols** → the **electrolyte** domain
  (`RULE-EQUILIBRIO-004` ADOPT-CORRECTED → `electrolyte.md#hyperkalemia-rescue-protocol`; `RULE-EQUILIBRIO-002`
  hypernatremia → `electrolyte.md#hypernatremia-na160-correction`). This domain only *consumes* K⁺/Mg²⁺ as QTc
  substrate.
- **Weight-based sedative *dosing* / overdose thresholds** → **neuro-sedation** domain (§7 open question there; the
  units registry has no weight-indexed *sedative* dose parameter). This domain consumes only the *presence* of CNS
  depressants (boolean/count), never a sedative infusion rate.
- **Vasopressor dosing** → **hemodynamics** domain (the ml/h→mcg/kg/min conversion service, SYS-C-04). No pharmaco
  alert consumes a vasopressor dose, so the SYS-02 dose-unit hazard does not touch this domain.
- **Medication-administration write-path / MAR UI** (dose check-off, suspension state machine, schedule generation) —
  the bulk of the `prescricao` cluster (RULE-PRESCRICAO-002/003/008/010/020/021 …) is **RETIRE** (home-care MAR
  plumbing with no v2 read-only analog, ADR-001 C-01). Only the pharmacist controlled *vocabularies* and antibiotic
  course-tracking survive (§3.7, RULE-PRESCRICAO-019/027/037/038/039).

**Legacy-aggregator reconciliation (three clusters → one design).** The legacy `antimicrobiano` trilha aggregated
5 of 12 criteria into a `VERMELHO/AMARELO/NEUTRO` enum (`RULE-ANTIMICROBIANO-001`), coexisting with a dead
weighted-count path (`RULE-ANTIMICROBIANO-002`). Neither is ported: `RULE-ANTIMICROBIANO-001` is **SUPERSEDE**d by the
unified `normal|watch|urgent|critical` scale and `RULE-ANTIMICROBIANO-002` is **RETIRE**d (dead code, `criterios == 3`
falls through both branches — CLU-ANTIMICROBIANO-C-02). The 12-criterion stewardship catalog (`RULE-ANTIMICROBIANO-003`,
**VERIFIED** vs IDSA/SSC-2021) is **ADAPT**ed into §4.7–4.8 with its dose tables migrated from S3 PNG to versioned
inline lookups (§3.6, CON-0139). PT-BR vocabularies `VERMELHO/AMARELO/NEUTRO`, `criterio_N`,
`payload_trilha_antimicrobiano`, `PAC`, `COVID-19` are preserved verbatim (CON-0136 / CLU-ANTIMICROBIANO-C-01).

---

## 2. Typed, unit-checked inputs

Every input unit is the canonical from `_work/units/registry.yaml`, **except `crcl` (mL/min)**, which is **missing**
from the registry and used as the **mission canonical** pending its addition (§7, OQ-PHARMACO-01). Drug presence is
represented as a **`boolean`** flag or a **`count`** over the versioned KB (§3), never as a raw dose — this keeps the
domain clear of the SYS-02 vasopressor and sedative dose-unit hazards.

| Input (PT-BR param) | Quantity | Unit (canonical) | Source | Staleness max |
|---|---|---|---|---|
| `qtc` | corrected_qt_interval | `ms` | Observation LOINC 44974-4 (Bazett/Fridericia) | PT24H |
| `delta_qtc` | corrected_qt_interval | `ms` | derived (qtc − prior qtc, same formula/lead) | PT24H |
| `qt_prolonging_drug_count` | dimensionless | `count` | derived from MedicationRequest ∩ CredibleMeds Known-Risk KB (§3.1) | PT12H |
| `serotonergic_agent_count` | dimensionless | `count` | derived from MedicationRequest ∩ serotonergic KB (§3.2) | PT12H |
| `cns_depressant_count` | dimensionless | `count` | derived from MedicationRequest ∩ CNS-depressant KB (§3.3) | PT6H |
| `same_class_active_count` | dimensionless | `count` | derived count within a duplication-flagged class (§3.4) | PT12H |
| `potassio` | serum_potassium | `mmol/L` | electrolyte domain / lab_result LOINC 6298-4 | PT12H |
| `magnesio` | serum_magnesium | `mmol/L` | electrolyte domain / lab_result LOINC 19123-9 | PT12H |
| `frequencia_respiratoria` | respiratory_rate | `rpm` | Observation LOINC 9279-1 / monitor | PT1H |
| `spo2` | peripheral_oxygen_saturation | `percent` | Observation LOINC 2708-6 / monitor | PT1H |
| `frequencia_cardiaca` | heart_rate | `bpm` | Observation LOINC 8867-4 / monitor | PT4H |
| `pressao_arterial_sistolica` | systolic_blood_pressure | `mmHg` | Observation LOINC 8480-6 / monitor | PT4H |
| `temperatura` | body_temperature | `degC` | Observation LOINC 8310-5 / monitor | PT6H |
| `rass` | richmond_agitation_sedation_scale | `points` (−5..+4) | neuro-sedation / Observation LOINC 75826-6 | PT4H |
| `creatinina` | serum_creatinine | `mg/dL` | lab_result LOINC 2160-0 | PT24H |
| `crcl` | creatinine_clearance | **`mL/min`** *(missing from registry — §7)* | derived Cockcroft-Gault (creatinina+peso+idade+sex) | PT24H |
| `idade` | age | `years` | Patient (MPI demographics) | static |
| `peso` | body_weight | `kg` | Observation LOINC 29463-7 (validated; SYS-09) | P7D |
| `clonus` / `hiperreflexia` / `sudorese` | dimensionless | `boolean` | Observation / nursing exam | PT12H |
| `antimicrobiano_duracao_gt_7d` / `cvc_dwell_gt_7d` / `bzd_continuo_gt_7d` | dimensionless | `boolean` | derived elapsed-exposure flags (§7 note on time-duration primitives) | PT12H |
| `indicacao_combinacao_documentada` / `suspensao_abrupta` / `de_escalonamento_disponivel` | dimensionless | `boolean` | Condition / care-plan / sepsis domain | PT24H |

> **FiO2 / lactate / vasopressor hazards do not apply here** — this domain consumes none of them at a computation
> boundary. The only cross-domain numeric inputs (K⁺, Mg²⁺, creatinina) arrive already in their registry canonicals.

---

## 3. Declarative, versioned interaction knowledge base

The interaction logic is data, not code: each list below is a **versioned lookup table** (a Gold-adjacent operational
config in the pharmaco service, ADR-001 C-03/C-13, alert versioning 100 % auditable) mapping RxNorm/ATC drug identity
to an interaction class. **A drug enters an alert only via KB membership**, so adding/removing a drug is a KB version
bump, never a code change (VIS-C-13 auditability). KB entries carry `{added_in_version, source_ref}`.

### 3.1 QT-prolonging drugs — CredibleMeds *Known Risk of TdP*
`amiodarona, azitromicina, ciprofloxacino, claritromicina, cloroquina, clorpromazina, citalopram, droperidol,
escitalopram, haloperidol, hidroxicloroquina, levofloxacino, metadona, moxifloxacino, ondansetrona, quinidina,
sotalol` — source: **CredibleMeds QTdrugs List** (Known Risk); Tisdale JE et al. *Circ Cardiovasc Qual Outcomes*
2013;6(4):479-487. Verbatim from catalog DDX-001.

### 3.2 Serotonergic agents
ISRS (`sertralina, fluoxetina, citalopram, escitalopram, paroxetina`), ISRSN (`venlafaxina, duloxetina`), `linezolida,
fentanil, ondansetrona, metoclopramida, tramadol, azul de metileno, erva de São João (Hypericum)` — source: Boyer EW,
Shannon M. *NEJM* 2005;352(11):1112-1120; Hunter criteria (Isbister GK, *J Clin Psychiatry* 2004). Verbatim from DDX-002.

### 3.3 CNS depressants
opioides (`morfina, fentanil, metadona, tramadol, codeína`), benzodiazepínicos (`midazolam, diazepam, lorazepam,
clonazepam`), gabapentinoides (`gabapentina, pregabalina`), antipsicóticos sedativos (`quetiapina, olanzapina,
clorpromazina`), barbitúricos (`fenobarbital, tiopental`), anti-histamínicos sedativos (`difenidramina, hidroxizina`)
— source: Overdyk FJ et al. *Anesth Analg* 2016;122(2):412-418. Verbatim from DDX-003.

### 3.4 Therapeutic-duplication classes (flagged `alerta_duplicidade`)
`IBP` (omeprazol+pantoprazol), `anticoagulante_dose_plena` (enoxaparina+HNF plena), `antiagregante` (AAS+clopidogrel
sem indicação dupla), `antiemetico` (ondansetrona+granisetrona), `antipsicotico` (haloperidol+quetiapina+olanzapina),
`benzodiazepinico` (midazolam contínuo+diazepam SOS), `AINE` (ibuprofeno+cetorolaco) — source: **ISMP Guidelines for
Preventing Duplicate Therapy 2023**. Verbatim from DDX-004.

### 3.5 Additive-nephrotoxic set (feeds AKI, §5)
`vancomicina, aminoglicosídeo, AINE, IECA/BRA, contraste iodado (<72h)` — source: **KDIGO Drug-Induced AKI 2023**;
`RULE-EQUILIBRIO-002` substitution recs (Cefepime→Tazocin, Vancomicina→Linezolida, morphine avoidance). The *firing*
combination logic lives in AKI (catalog AKI-005); this KB is the shared drug-identity source.

### 3.6 Renally-cleared antimicrobials + **versioned inline renal-dose table** (replaces S3 PNG, CON-0139)
Renally-cleared (require CrCl-based dose/interval): `vancomicina, meropenem, imipenem, piperacilina-tazobactam,
cefepime, aciclovir, fluconazol (CrCl<50), oseltamivir` (catalog DDX-006). **No-renal-adjust EXCEPTION KB**
(CON-0139 / CLU-ANTIMICROBIANO-C-04): `Polimixina B, Linezolida, Oxacilina, Tigeciclina, Clindamicina`. The legacy
weight (criterio_3) and renal (criterio_4) dose tables were **external S3 PNG images, not version-controlled**
(`RULE-ANTIMICROBIANO-003`, ADAPT); v2 migrates them to a versioned inline lookup keyed by `{drug, crcl_band}`.
Source: Rybak MJ et al. *Am J Health Syst Pharm* 2020;77(11):835-864; Matzke GR et al. *Kidney Int* 2011;80(11):1122-1137.

### 3.7 Antimicrobial-stewardship criteria + broad-spectrum KB (`RULE-ANTIMICROBIANO-003`, ADAPT)
The 12-criterion stewardship catalog (duração >7d; espectro-estreito+internação>48h; ajuste peso/renal; CVC>7d+febre
38.3 °C; equinocandina empírica para candidemia; solicitação de culturas; de-escalonamento por PCR<100 em PAC/COVID-19)
is preserved verbatim (CON-0138 / CLU-ANTIMICROBIANO-C-03). **Recommended default (RAT-ANTIMICROBIANO-02):** surface
every clinically-actionable criterion consolidated into §4.7 (stewardship review) and §4.8 (CVC), **not** the legacy
`get_detalhe()` 3,4,5,6,8 subset. The candidemia workup **duality** — `criterio_9` (full bacterial+fungal) vs
`criterio_10` (fungi-only) — is preserved as distinct branches (CON-0140 / CLU-ANTIMICROBIANO-C-05), carried as the
advisory branch of §4.8 pending **RAT-ANTIMICROBIANO-03**. Pharmacist controlled vocabularies (medication
reconciliation `RULE-PRESCRICAO-019` ADOPT; antibiotic course tracking `RULE-PRESCRICAO-027` ADOPT-CORRECTED;
33-option intervention vocab `RULE-PRESCRICAO-039` ADAPT, typos corrected; prophylaxis `RULE-PRESCRICAO-038` ADAPT;
risk assessment `RULE-PRESCRICAO-037` ADOPT-CORRECTED) are shared clinical-form assets, referenced here for the
stewardship documentation surface.

---

## 4. Alerts — trigger / staging logic with evidence

Every threshold cites a guideline/paper and/or a `RULE-*` catalog ID. Full test vectors, suppression, and PPV budgets
are in `_work/alerts/pharmaco-interaction.yaml`. Severity uses **only** `normal|watch|urgent|critical`.

### 4.1 `ALERT-PHARMACO-QTC-01` — Prolongamento de QTc → Torsades (critical)
`qtc > 500 ms AND ( qt_prolonging_drug_count >= 2 OR (delta_qtc > 60 ms AND qt_prolonging_drug_count >= 1) )`.
**Evidence:** Tisdale 2013 (QTc risk score); CredibleMeds Known-Risk; vision §3.7 (VIS-3.7-02: QTc>500 or Δ>60 +
≥2 Known-Risk drugs). Lower substrate band (QTc>500 + 1 drug + K⁺<3.5 / Mg²⁺<0.7) is **not** a second push — emitted
as `drug.qtc.prolonged` and amplified by the correlation engine (§5). Boundary: QTc = 500 is *not* >500.

### 4.2 `ALERT-PHARMACO-SEROTONIN-02` — Síndrome serotoninérgica (urgent)
`serotonergic_agent_count >= 2 AND (clonus OR hipertermia_sem_infeccao OR hiperreflexia)`. **Evidence:** Boyer &
Shannon 2005; Hunter criteria (Isbister 2004); vision §3.7 (VIS-3.7-03). Asymptomatic ≥3-agent case (DDX-002b) →
`drug.serotonergic_load.high` surveillance event, not a push (PPV protection).

### 4.3 `ALERT-PHARMACO-CNS-DEPRESSION-03` — Depressão respiratória sinérgica (critical)
`cns_depressant_count >= 2 AND (frequencia_respiratoria < 10 rpm OR spo2 < 90 %) AND ventilacao_mecanica_controlada
== false`. **Evidence:** Overdyk 2016; Lee 2015; vision §3.7 (VIS-3.7-05). The controlled-ventilation suppression gate
is an added PPV lever (a controlled set-rate is not spontaneous depression). Boundary: RR = 10 is *not* <10.

### 4.4 `ALERT-PHARMACO-DUP-04` — Duplicidade terapêutica (watch)
`same_class_active_count >= 2` for a duplication-flagged class (§3.4) `AND indicacao_combinacao_documentada == false`.
**Evidence:** ISMP 2023; Maviglia 2006; vision §3.7 (VIS-3.7-06). Documented dual-therapy (DAPT post-stent) suppresses.

### 4.5 `ALERT-PHARMACO-WITHDRAWAL-05` — Síndrome de abstinência (watch)
`(bzd_continuo_gt_7d OR opioide_continuo_gt_7d) AND suspensao_abrupta AND (fc>100 OR pas>160 OR temp>38.0 OR sudorese
OR rass>+1)`. **Evidence:** Devlin PADIS 2018; Korak-Leiter 2005; vision §3.7 (VIS-3.7-07). Exposure gate sourced from
neuro-sedation `neurosed.prolonged_sedation.flagged` (§5). Boundary: exactly 7 d → `gt_7d` flag false.

### 4.6 `ALERT-PHARMACO-RENALADJ-06` — Antimicrobiano sem ajuste renal (urgent)
`antimicrobiano_eliminacao_renal_ativo AND crcl < 30 mL/min AND dose_excede_ajuste_renal AND drug NOT IN exception KB`.
**Evidence:** Rybak 2020; Matzke 2011; KDIGO DIKI 2023; vision §3.7 (VIS-3.7-08); `RULE-ANTIMICROBIANO-003` (ADAPT,
versioned dose table §3.6). Boundary: CrCl = 30 is *not* <30. `crcl` unit is `mL/min` (missing from registry — §7).

### 4.7 `ALERT-PHARMACO-STEWARDSHIP-07` — Revisão de antimicrobiano (watch) — *adapted stewardship timer*
`antimicrobiano_ativo AND ( antimicrobiano_duracao_gt_7d OR (espectro_amplo AND NOT cultura_solicitada_48h) OR
de_escalonamento_disponivel )`. **Evidence:** SSC-2021 (Evans 2021); Schuetz Cochrane 2017 (PCT de-escalation);
IDSA/SHEA Stewardship 2016; `RULE-ANTIMICROBIANO-003` (ADAPT); `RULE-PRESCRICAO-027` (antibiotic course tracking,
ADOPT-CORRECTED). **Recommended default (pending RAT-ANTIMICROBIANO-01/02):** duration is a *soft* de-escalation
nudge at >7 d, reset on documented spectrum change; all actionable criteria surfaced.

### 4.8 `ALERT-PHARMACO-CVC-FEVER-08` — CVC >7 d com febre (urgent) — *adapted stewardship timer*
`cvc_dwell_gt_7d AND temperatura >= 38.3 degC` (IDSA fever). **Evidence:** Mermel LA et al. *Clin Infect Dis*
2009;49(1):1-45 (IDSA CRBSI); Pappas PG et al. *Clin Infect Dis* 2016;62(4):e1-e50 (candidemia empiric echinocandin);
`RULE-ANTIMICROBIANO-003` (ADAPT). Advisory carries the candidemia workup **duality** (criterio_9 full / criterio_10
fungi-only) preserved distinct (CON-0140, pending RAT-ANTIMICROBIANO-03). Boundary: temp = 38.3 fires (inclusive).

---

## 5. Interactions with other domains

- **Electrolyte (K⁺/Mg²⁺) — QTc amplification (vision §4.1 "QTc + K⁺/Mg²⁺", VIS-4-03).** This domain emits
  `drug.qtc.prolonged`; the **correlation engine** joins it with the electrolyte domain's
  `electrolyte.hypokalemia.detected` / `electrolyte.hypomagnesemia.detected` within PT24H to raise the single
  amplified `correlation.qtc_electrolyte.detected` (critical), so the QTc-substrate + electrolyte case is one alert,
  not two WARN pushes. Hypokalemia/hypomagnesemia correction itself is the electrolyte domain's.
- **AKI — nephrotoxic stacking feed.** `pharmaco.nephrotoxic_burden.changed` (§3.5 KB) is consumed by AKI, which
  raises `ALERT-AKI-NEPHROTOXIN-03` (catalog AKI-005) when a rising-creatinine trend coincides with the additive
  combination. This domain intentionally raises **no** nephrotoxic push (avoids duplicate alarm; alarm-fatigue budget
  VIS-7.1-04).
- **Neuro-sedation — withdrawal exposure.** Consumes `neurosed.prolonged_sedation.flagged` (>7 d / >96 h continuous
  sedative/BZD/opioid) as the exposure gate for `ALERT-PHARMACO-WITHDRAWAL-05` (catalog DDX-005). Reuses the
  neuro-sedation prolonged-exposure computation rather than recomputing it.
- **Sepsis — antimicrobial de-escalation.** Consumes the sepsis/procalcitonin de-escalation signal (PCT<0.25 ng/mL or
  >80 % drop; PCR<100 mg/L CAP) to drive the de-escalation branch of `ALERT-PHARMACO-STEWARDSHIP-07`.
- **Respiratory — controlled-ventilation gate.** Consumes ventilator mode to suppress `ALERT-PHARMACO-CNS-DEPRESSION-03`
  under controlled mechanical ventilation.

---

## 6. RATIFY-pending decisions (designed to the recommended default, marked *pending RAT-\**)

Escalation policy (SYS-C-03, CONTRACTS §Precedence): P0/P1/UNVERIFIABLE/disputed items are **not** resolved by agents.
Each below is designed to a reference-anchored **recommended default**; the ratification committee decides.

| RAT id | Rule(s) | Question | Recommended default (designed here) |
|---|---|---|---|
| **RAT-ANTIMICROBIANO-01** | RULE-ANTIMICROBIANO-003 | Antibiotic duration >7 d: hard stop vs decision-support? Reset on spectrum change? | **Soft de-escalation-review nudge** at >7 d (watch), **reset on documented spectrum change**; never an auto-stop (VIS-C-01). Drives STEWARDSHIP-07. |
| **RAT-ANTIMICROBIANO-02** | RULE-ANTIMICROBIANO-003 | Surface all 12 stewardship criteria or the legacy 3,4,5,6,8 subset (CLU-ANTIMICROBIANO-C-03)? | **Surface all clinically-actionable criteria**, consolidated into STEWARDSHIP-07 + CVC-FEVER-08; legacy `get_detalhe()` subset discarded. |
| **RAT-ANTIMICROBIANO-03** | RULE-ANTIMICROBIANO-003 | Candidemia workup duality criterio_9 (full) vs criterio_10 (fungi-only) — same `alerta` label (CLU-ANTIMICROBIANO-C-05)? | **Preserve both as distinct advisory branches** of CVC-FEVER-08; do not collapse the differing workup scopes. |
| **RAT-PRESCRICAO-01** | RULE-PRESCRICAO-001, -036 | Is a mandatory ml-quantity capture / once-set-immutable administration-status invariant needed in v2 (UNVERIFIABLE / AMBIGUOUS)? | **Out of pharmaco-alert scope** (governance/clinical-forms); the antibiotic course-tracking form (RULE-PRESCRICAO-027) is the only prescricao surface this domain uses. Committee owns the immutability invariant. |

**Systemic-hazard note.** No P0 rule falls in this domain's own dispositions. The shared SYS-01 (FiO2), SYS-02
(vasopressor), SYS-03 (lactate), and SYS-09 (weight) hazards do **not** touch any pharmaco predicate — this domain
consumes only drug presence (boolean/count), QTc (ms), K⁺/Mg²⁺/creatinina (registry canonicals), and vitals. The one
weight-dependent value, CrCl (Cockcroft-Gault), inherits the SYS-09 `peso` guard via the validated `peso` input.

---

## 7. Open questions

1. **`crcl` (creatinine clearance) unit missing from `_work/units/registry.yaml`** (OQ-PHARMACO-01). Renal-dose
   mismatch (§4.6) and stewardship renal-adjust reasoning need Cockcroft-Gault CrCl. **Mission canonical assumed:
   `mL/min`** (non-indexed Cockcroft-Gault, matching vision §3.7 "CrCl < 30 mL/min"). eGFR variants (CKD-EPI,
   mL/min/1.73m²) are *not* interchangeable for drug dosing — the registry entry, when added, must distinguish
   `creatinine_clearance` (mL/min, Cockcroft-Gault, for dosing) from indexed eGFR. Flagged per CONTRACTS "use the
   mission canonical + open question" rule.
2. **Time-duration primitives** (`h` / `d`) are used only inside *derived boolean* exposure flags
   (`*_gt_7d`, dwell days) — no numeric clinical threshold uses a raw time unit at a computation boundary, consistent
   with the sibling neuro-sedation domain's use of `h`. Confirm whether the registry should add explicit `h`/`d`.
3. **QTc data availability (DATA-AVAIL-07, Média).** Automatic QTc computation varies by ECG algorithm; the recommended
   default fires only on a *measured* QTc, never on a drug list alone. Confirm the QTc source/formula (Bazett vs
   Fridericia) the AMH Gold Observation carries, and the `delta_qtc` prior-value lookback mechanics (mirrors the vision
   Δ-lactate/Δ-PCT lookback open question).
4. **Medication-administration real-time availability (DATA-AVAIL-06 / VIS-5.1-06, Baixa).** P6 is the lowest
   data-availability domain: administration events are not always real-time. All alerts here degrade gracefully on
   `MedicationRequest` (order) when `MedicationAdministration` lags; confirm the order-vs-administration precedence
   with the data-model guild.
5. **PRIS / candidemia value thresholds.** CVC-FEVER-08's candidemia branch is advisory only; if the committee wants
   value-based candidemia risk scoring (e.g. Candida score), the required inputs are not in the registry today.
6. **`RULE-PRESCRICAO-036` immutability call-site** is unconfirmed outside its partition (RAT-PRESCRICAO-01); it does
   not gate any pharmaco alert.

---

```yaml domain-inputs
domain: pharmaco-interaction
inputs:
  - {name: qtc, type: quantity, unit: "ms", source: "AMH Gold Observation LOINC 44974-4 (QTc Bazett/Fridericia)"}
  - {name: delta_qtc, type: quantity, unit: "ms", source: "derived (qtc - prior qtc, same formula/lead)"}
  - {name: qt_prolonging_drug_count, type: quantity, unit: "count", source: "derived MedicationRequest ∩ CredibleMeds Known-Risk KB (§3.1)"}
  - {name: serotonergic_agent_count, type: quantity, unit: "count", source: "derived MedicationRequest ∩ serotonergic KB (§3.2)"}
  - {name: cns_depressant_count, type: quantity, unit: "count", source: "derived MedicationRequest ∩ CNS-depressant KB (§3.3)"}
  - {name: same_class_active_count, type: quantity, unit: "count", source: "derived count within duplication-flagged class (§3.4)"}
  - {name: duplicated_class, type: enum, unit: "enum", source: "derived therapeutic class (ATC) from MedicationRequest (§3.4)"}
  - {name: potassio, type: quantity, unit: "mmol/L", source: "electrolyte domain / AMH Gold lab_result LOINC 6298-4"}
  - {name: magnesio, type: quantity, unit: "mmol/L", source: "electrolyte domain / AMH Gold lab_result LOINC 19123-9"}
  - {name: frequencia_respiratoria, type: quantity, unit: "rpm", source: "AMH Gold Observation LOINC 9279-1 / monitor"}
  - {name: spo2, type: quantity, unit: "percent", source: "AMH Gold Observation LOINC 2708-6 / monitor"}
  - {name: frequencia_cardiaca, type: quantity, unit: "bpm", source: "AMH Gold Observation LOINC 8867-4 / monitor"}
  - {name: pressao_arterial_sistolica, type: quantity, unit: "mmHg", source: "AMH Gold Observation LOINC 8480-6 / monitor"}
  - {name: temperatura, type: quantity, unit: "degC", source: "AMH Gold Observation LOINC 8310-5 / monitor"}
  - {name: rass, type: quantity, unit: "points", source: "neuro-sedation / AMH Gold Observation LOINC 75826-6 (signed -5..+4)"}
  - {name: creatinina, type: quantity, unit: "mg/dL", source: "AMH Gold lab_result LOINC 2160-0"}
  - {name: crcl, type: quantity, unit: "mL/min", source: "derived Cockcroft-Gault; UNIT MISSING from registry — mission canonical mL/min (§7 OQ-PHARMACO-01)"}
  - {name: idade, type: quantity, unit: "years", source: "MPI demographics (Patient)"}
  - {name: peso, type: quantity, unit: "kg", source: "AMH Gold Observation LOINC 29463-7 (validated peso; SYS-09)"}
  - {name: clonus, type: boolean, unit: "boolean", source: "AMH Gold Observation / nursing exam"}
  - {name: hiperreflexia, type: boolean, unit: "boolean", source: "AMH Gold Observation / neuro exam"}
  - {name: hipertermia_sem_infeccao, type: boolean, unit: "boolean", source: "derived (temperatura >38.0 degC without infection source)"}
  - {name: sudorese, type: boolean, unit: "boolean", source: "AMH Gold Observation / nursing record"}
  - {name: ventilacao_mecanica_controlada, type: boolean, unit: "boolean", source: "Procedure / ventilator mode (controlled vs spontaneous)"}
  - {name: antimicrobiano_ativo, type: boolean, unit: "boolean", source: "AMH Gold MedicationRequest (active antimicrobial)"}
  - {name: antimicrobiano_eliminacao_renal_ativo, type: boolean, unit: "boolean", source: "derived: active drug ∩ renally-cleared KB (§3.6)"}
  - {name: dose_excede_ajuste_renal, type: boolean, unit: "boolean", source: "derived vs versioned renal-dose table (§3.6, CON-0139)"}
  - {name: espectro_amplo, type: boolean, unit: "boolean", source: "derived: active drug ∩ broad-spectrum KB (§3.7)"}
  - {name: cultura_solicitada_48h, type: boolean, unit: "boolean", source: "AMH Gold ServiceRequest/DiagnosticReport (culture <=48h)"}
  - {name: de_escalonamento_disponivel, type: boolean, unit: "boolean", source: "sepsis domain de-escalation signal (PCT/PCR) or positive culture"}
  - {name: antimicrobiano_duracao_gt_7d, type: boolean, unit: "boolean", source: "derived from MedicationAdministration start (>7d; reset on spectrum change)"}
  - {name: cvc_dwell_gt_7d, type: boolean, unit: "boolean", source: "derived: CVC insertion Procedure dwell >7d"}
  - {name: bzd_continuo_gt_7d, type: boolean, unit: "boolean", source: "derived / neurosed.prolonged_sedation.flagged (>7d continuous BZD)"}
  - {name: opioide_continuo_gt_7d, type: boolean, unit: "boolean", source: "derived (>7d continuous opioid)"}
  - {name: suspensao_abrupta, type: boolean, unit: "boolean", source: "derived: prior continuous agent absent from MAR, no taper order"}
  - {name: indicacao_combinacao_documentada, type: boolean, unit: "boolean", source: "AMH Gold Condition / care-plan (dual-therapy indication)"}
alerts:
  - ALERT-PHARMACO-QTC-01
  - ALERT-PHARMACO-SEROTONIN-02
  - ALERT-PHARMACO-CNS-DEPRESSION-03
  - ALERT-PHARMACO-DUP-04
  - ALERT-PHARMACO-WITHDRAWAL-05
  - ALERT-PHARMACO-RENALADJ-06
  - ALERT-PHARMACO-STEWARDSHIP-07
  - ALERT-PHARMACO-CVC-FEVER-08
rule_refs:
  - RULE-ANTIMICROBIANO-001
  - RULE-ANTIMICROBIANO-002
  - RULE-ANTIMICROBIANO-003
  - RULE-EQUILIBRIO-002
  - RULE-PRESCRICAO-019
  - RULE-PRESCRICAO-027
  - RULE-PRESCRICAO-037
  - RULE-PRESCRICAO-038
  - RULE-PRESCRICAO-039
interfaces:
  emits_events:
    - drug.qtc.prolonged
    - drug.serotonergic_load.high
    - drug.cns_depression.risk
    - drug.therapeutic_duplication.detected
    - drug.withdrawal.risk
    - drug.renal_dose.mismatch
    - drug.antimicrobial.stewardship_review
    - drug.cvc.dwell_fever
    - pharmaco.nephrotoxic_burden.changed
  consumes:
    - {quantity: serum_potassium, unit: "mmol/L", source: "electrolyte domain"}
    - {quantity: serum_magnesium, unit: "mmol/L", source: "electrolyte domain"}
    - {quantity: richmond_agitation_sedation_scale, unit: "points", source: "neuro-sedation domain"}
    - {quantity: creatinine_clearance, unit: "mL/min", source: "derived Cockcroft-Gault (unit missing from registry, §7)"}
```
