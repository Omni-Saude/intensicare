# Electrolyte-Emergency Domain — IntensiCare v2 Clinical Specification

> Vision §3.6 ("Emergências Eletrolíticas", priority **P3**, Fase 2a). Severe K⁺/Na⁺/Mg²⁺/Ca²⁺
> disturbances are potentially fatal within minutes to hours; automated critical-value detection reduces
> time-to-correction and prevents arrhythmias, seizures, and cardiac arrest (VIS-3.6-01). One of the
> Fase-2a §6.1 primary outcomes is a **50% reduction in cardiac arrest from electrolyte disturbance**.
>
> Scope of this spec: the six electrolyte alerts (`ALERT-ELY-*`), their unit-checked trigger logic, the
> evidence anchor for every threshold, the paired-condition and cross-domain interfaces, and the
> RATIFY-pending phosphate design. Severity uses ONLY `normal | watch | urgent | critical`
> (legacy CRIT→critical, URG→urgent, WARN→watch, INFO→normal).

---

## 1. Clinical scope

**In scope** — critical-value detection and staging for the five vision §3.6 ions plus phosphate:

| Ion | Alert | Bands | Reconciles |
|-----|-------|-------|-----------|
| K⁺ | `ALERT-ELY-POTASSIUM-01` | hyper crit >6.5 / urgent >6.0 / watch; hypo crit <2.5 / urgent <3.0 / watch | ELY-001, ELY-002 |
| Na⁺ (absolute) | `ALERT-ELY-SODIUM-01` | hyper crit >160 / urgent >155 / watch; hypo crit <120 / urgent <125 / watch | ELY-003(a,b), ELY-004 |
| Na⁺ (rate) | `ALERT-ELY-SODIUM-CORRECTION-02` | crit >10 mmol/L/24h / urgent >8 | ELY-003(c) |
| Ca²⁺ (ionized) | `ALERT-ELY-CALCIUM-01` | hypo crit <0.80 / urgent <0.90; hyper crit >1.60 / urgent >1.45 | ELY-005 |
| Mg²⁺ | `ALERT-ELY-MAGNESIUM-01` | crit <0.5 / urgent <0.7 / watch <0.9+cofactor | ELY-006 |
| PO₄ | `ALERT-ELY-PHOSPHATE-01` | hypo crit <1.0 / urgent <1.5; hyper watch >7.0 (pending RAT-ELY-01) | *(new)* |

**Out of scope** (handled by neighbouring domains): fluid-balance titration and diuresis trend
(→ AKI domain, `RULE-EQUILIBRIO-001`/`003`); nephrotoxic-drug substitution and opioid clearance
(→ AKI / pharmaco, `RULE-EQUILIBRIO-002` criteria 5-8); QTc-prolonging drug combinations themselves
(→ pharmaco `DDX-001` — this domain **feeds** it the electrolyte contribution but does not own the drug list).

**Design law — fewer, richer alerts.** The vision §3.6 table lists nine alert rows and the legacy catalog
six `ELY-*` entries, each with two-to-three internal severity bands. This spec folds them into **six per-ion
severity-scaling alerts** (one severity output that scales with the band), which is the primary lever for the
fleet PPV ≥ 0.60 and ignored-rate ≤ 10% targets (VIS-7.1-02/04). Every threshold below is objective (a lab
number against a guideline cut), so per-alert PPV is high; the residual false-positive source is **pre-analytic**
(hemolysis for K⁺, tourniquet/pH for ionized Ca²⁺, hyperglycemia pseudo-hyponatremia for Na⁺) and is called out
per alert.

---

## 2. Typed, unit-checked inputs

Every unit below is the **canonical unit** from `_work/units/registry.yaml`; a non-canonical/non-alias unit on
any input is a build-time error (registry law). The registry is the single source of truth for the electrolyte
mg/dL↔mmol/L conversions (Brazilian labs vary), and it explicitly forbids propagating the legacy
`RULE-EQUILIBRIO-004` potassium `mg/dl` mislabel (CON-0159 / CLU-EQUILIBRIO-C-01).

| Input | Type | Canonical unit | Source (AMH Gold via Athena, ADR-001-C-01) |
|-------|------|----------------|--------------------------------------------|
| `potassio` | quantity | `mmol/L` (== mEq/L, monovalent) | lab_result LOINC 6298-4 |
| `sodio` | quantity | `mmol/L` (== mEq/L) | lab_result LOINC 2951-2 |
| `magnesio` | quantity | `mmol/L` (mEq/L ≠ 1:1, factor 0.5 — divalent) | lab_result LOINC 19123-9 |
| `calcio_ionizado` | quantity | `mmol/L` | lab_result LOINC 1994-3 |
| `calcio_total` | quantity | `mg/dL` | lab_result LOINC 17861-6 |
| `fosfato` | quantity | `mg/dL` *(pending RAT-ELY-01)* | lab_result LOINC 2777-1 |
| `albumina` | quantity | `g/dL` *(see open question OQ-1)* | lab_result LOINC 1751-7 |
| `glicemia` | quantity | `mg/dL` | lab_result (glucose) |
| `creatinina` | quantity | `mg/dL` | lab_result LOINC 2160-0 |
| `qtc` | quantity | `ms` | Observation ECG QTc LOINC 44974-4 |
| `delta_k_24h` | quantity | `mmol/L` (trailing 24h delta) | derived from serial results |
| `delta_na_24h_trailing` | quantity | `mmol/L` (trailing: `sodio_atual − sodio_24h_atras`) | derived — **`ALERT-ELY-SODIUM-01` only** |
| `correcao_na_24h_from_nadir` | quantity | `mmol/L` (from nadir: `sodio_atual − sodio_nadir_24h`) | derived — **`ALERT-ELY-SODIUM-CORRECTION-02` only** |
| `digoxina_ativa` | boolean | `boolean` | MedicationAdministration |
| `medicamento_hipercalemiante_ativo` | boolean | `boolean` | MedicationAdministration (list below) |
| `furosemida_dose_alta` | boolean | `boolean` | MedicationAdministration |
| `ckd_moderada_grave` | boolean | `boolean` | Condition / eGFR<60 |

Hyperkalemiant drug list (preserved verbatim from ELY-001, PT-BR): **espironolactona, eplerenona, IECA,
BRA/ARA II, trimetoprim-sulfametoxazol, heparina prolongada, succinilcolina**.

> **Osmolality caveat (prose-only).** Plasma osmolality (LOINC 2692-2) distinguishes true hypotonic
> hyponatremia from pseudo-/translocational hyponatremia. It is *not* a typed input here because `mOsm/kg` is
> absent from the units registry (OQ-2); instead the sodium alert applies a **glucose correction** for the most
> common ICU confounder (hyperglycemia). Adding osmolality is a future enhancement gated on registering the unit.

---

## 3. Trigger / staging logic (evidence-anchored)

Each alert emits ONE severity that scales with the worst band. Boundary discipline: bands use strict `>`/`<`,
so a value **exactly on** a threshold falls to the next-lower band (verified by the boundary test vectors in
`_work/alerts/electrolyte.yaml`).

### 3.1 Potassium — `ALERT-ELY-POTASSIUM-01`

```
HYPER: critical  potassio > 6.5 mmol/L
       urgent    potassio > 6.0 mmol/L (<= 6.5)
       watch     potassio > 5.5 mmol/L AND delta_k_24h > 0.5 mmol/L
                 AND (ckd_moderada_grave OR medicamento_hipercalemiante_ativo OR digoxina_ativa)
HYPO:  critical  potassio < 2.5 mmol/L
       urgent    potassio < 3.0 mmol/L (>= 2.5)
       watch     potassio < 3.5 mmol/L AND (qtc > 500 ms OR furosemida_dose_alta
                 OR digoxina_ativa OR magnesio < 0.7 mmol/L)
PAIRED (digoxin): digoxina_ativa AND (potassio > 6.0 OR potassio < 3.0)
                 -> digoxin_toxicity_context = true
```

- **>6.5 crit / >6.0 urgent** — UKKA 2023 acute-hyperkalaemia guideline; vision VIS-3.6-02. (`ELY-001a/b`)
- **<2.5 crit / <3.0 urgent** — Clase CM et al. *BMJ* 2020 (KDIGO dyskalemia conference); vision VIS-3.6-03. (`ELY-002a/b`)
- **Hyperkalemia rescue bundle** (critical response) — legacy `RULE-EQUILIBRIO-004`, **ADOPT-CORRECTED**: the
  bundle (gluconato de cálcio → solução polarizante insulina+glicose → beta-agonista salbutamol/fenoterol →
  furosemida; +4 h reavaliação com bicarbonato 8.4 % 1 mL/kg e Sorcal se K⁺ > 5.5 mmol/L) matches
  KDIGO/UpToDate content (KDIGO summary *Eur J Emerg Med* 2020;27(5):329-337, PMC7448835; Mount & Sterns,
  UpToDate). The legacy code labels potassium **`mg/dl`**; v2 uses **mmol/L (mEq/L) throughout and NEVER
  propagates the unit error** (CON-0159 / CLU-EQUILIBRIO-C-01, ESC-P2-066 band P2, clinical_impact low).
- **Digoxin pairing (paired condition):** hyperkalemia with active digoxin signals **digoxin toxicity** — IV
  calcium is given with caution (historical "stone-heart" concern) and digoxin-specific antibody considered;
  hypokalemia with digoxin potentiates toxic arrhythmia. Emitted as `digoxin_toxicity_context`.

### 3.2 Sodium (absolute) — `ALERT-ELY-SODIUM-01`

```
Glucose correction: sodio_corrigido = sodio + 0.024*(glicemia - 100)  when glicemia > 100 mg/dL
HYPER: critical  sodio > 160 mmol/L
       urgent    sodio > 155 mmol/L (<= 160)
       watch     sodio > 150 mmol/L AND delta_na_24h_trailing > 5 mmol/L (rising)
HYPO:  critical  sodio < 120 mmol/L
       urgent    sodio < 125 mmol/L (>= 120)
       watch     sodio < 130 mmol/L AND delta_na_24h_trailing <= -5 mmol/L (acute fall)
```

- **>160 crit / >155 urgent; <120 crit / <125 urgent** — ESICM/ESE/ERBP 2024 dysnatraemia consensus;
  vision VIS-3.6-04/05 (`ELY-003a/b`, `ELY-004a/b`).
- **Hypernatremia correction path** — `RULE-EQUILIBRIO-002` (**ADAPT**, verdict VERIFIED against
  Adrogué HJ & Madias NE, *NEJM* 2000;342:1493-1499; Sterns UpToDate): água filtrada 400 mL 6/6 h,
  NaCl 0.22 % 84 mL/h, hidroclorotiazida 25 mg. Legacy `get_detalhe()` **never surfaced** this rescue path
  (a genuine patient-safety UI gap) — v2 restores full visibility (CON-0161 / CLU-EQUILIBRIO-C-03).
- **Glucose correction** — corrects the most common ICU pseudo-hyponatremia confounder (hyperglycemia,
  ~1.6 mmol/L Na⁺ per 100 mg/dL glucose > 100); uses the registry `glicemia` (mg/dL) and `sodio` (mmol/L).

### 3.3 Sodium correction rate — `ALERT-ELY-SODIUM-CORRECTION-02` (safety)

```
critical  correcao_na_24h_from_nadir > 10 mmol/L in 24h    (exceeds osmotic-demyelination ceiling)
urgent    correcao_na_24h_from_nadir >  8 mmol/L in 24h     (approaching ceiling)
highest concern when the 24h nadir sodium < 130 mmol/L (chronic hyponatremia being corrected)
```

- **>10 crit / >8 urgent** — Sterns RH, *JASN* 2015;26(9):2110-2115; vision VIS-3.6-06; **CON-0061 / CAT-C-01**
  (MUST NOT correct hyponatremia faster than 8-10 mmol/L per 24 h — risco de mielinólise pontina / síndrome de
  desmielinização osmótica). Kept as a **separate** alert because its clinical action (stop/relower, DDAVP)
  differs from the absolute-value alert and its **absence** is what kills — it is the domain's safety net.
- **Baseline MUST be the 24 h nadir, never the trailing delta (deterministic-baseline law).** This alert consumes
  **`correcao_na_24h_from_nadir` = `sodio_atual − sodio_nadir_24h`**, a **distinct named quantity** from the
  **`delta_na_24h_trailing` = `sodio_atual − sodio_24h_atras`** that `ALERT-ELY-SODIUM-01` uses. The two MUST NOT
  be collapsed into one shared `delta_na_24h` value: an over-rapid rise off the 24 h nadir is the
  osmotic-demyelination hazard **even when the trailing 24 h delta is flat or negative**. Worked case — Na
  **140 → 120 → 132**: the from-nadir correction is **+12** (120 → 132) and fires **critical**, while the trailing
  delta is **−8** (132 − 140), a net fall that would silently miss the overcorrection. Sharing one name is exactly
  the **HAZ-031** deterministic-baseline violation that hands this safety net the wrong baseline and can miss an
  ODS-range correction (**HAZ-032**).

### 3.4 Ionized calcium — `ALERT-ELY-CALCIUM-01`

```
corrected_total_Ca = calcio_total + 0.8*(4.0 - albumina[g/dL])     (fallback only)
HYPO:  critical  calcio_ionizado < 0.80 mmol/L
                 OR (ionized unavailable AND corrected_total_Ca < 7.0 mg/dL)
       urgent    calcio_ionizado < 0.90 mmol/L (>= 0.80)
HYPER: critical  calcio_ionizado > 1.60 mmol/L
                 OR (ionized unavailable AND corrected_total_Ca > 14.0 mg/dL)
       urgent    calcio_ionizado > 1.45 mmol/L (<= 1.60)
QTc: hypocalcemia prolongs QTc -> emit qtc_risk when qtc > 500 ms
```

- **Hyper crit >1.60 / urgent >1.45** — Mousseaux C et al., *Nephrol Dial Transplant* 2022; vision VIS-3.6-07.
- **Hypo crit <0.80 / urgent <0.90** — Cooper MS et al., *Intensive Care Med* 2022; vision VIS-3.6-08.
- **Ionized-primary / corrected-total-fallback + albumin correction** — preserved verbatim from `ELY-005`
  (corrected total Ca > 14 mg/dL crit-high, < 7.0 mg/dL crit-low). Ionized is preferred whenever present
  because the corrected-total surrogate is albumin- and pH-dependent (lower reliability → lower PPV).

### 3.5 Magnesium — `ALERT-ELY-MAGNESIUM-01`

```
critical  magnesio < 0.5 mmol/L  (1.2 mg/dL)
urgent    magnesio < 0.7 mmol/L  (1.7 mg/dL) (>= 0.5)
watch     magnesio < 0.9 mmol/L AND (potassio < 3.5 mmol/L OR qtc > 500 ms)
```

- **<0.5 crit / <0.7 urgent** — Hansen BA & Bruserud Ø, *Intensive Care Med Exp* 2018;6:21; vision VIS-3.6-09.
- **Severity CONFLICT recorded** (CONTRACTS rule 5, never resolved silently): vision VIS-3.6-09 labels
  <0.5 **critical** / <0.7 **urgent**, whereas the legacy catalog `ELY-006` labels <0.5 URG / <0.7 WARN.
  Precedence (vision ≻ audit-legacy) resolves to the **vision** severities; see §6. The watch cofactor band
  (Mg exacerbates hypokalemia and prolongs QTc) is preserved and is the main feed to the pharmaco QTc correlation.

### 3.6 Phosphate — `ALERT-ELY-PHOSPHATE-01` (thresholds pending RAT-ELY-01)

```
HYPO:  critical  fosfato < 1.0 mg/dL   (weaning failure, resp-muscle weakness, rhabdomyolysis)
       urgent    fosfato < 1.5 mg/dL (>= 1.0)
HYPER: watch     fosfato > 7.0 mg/dL   (AKI / tumor-lysis marker -> routes to AKI review)
```

- **No vision numeric anchor.** Vision §3.6 VIS-3.6-10 lists PO₄ as *required data* but gives **no** alert band,
  and the units registry flags `fosfato` canonical mg/dL as an open committee item. These bands are therefore
  **designed to the recommended default and marked pending RAT-ELY-01** (§6). Anchor for the default: Geerse DA
  et al., *Crit Care* 2010;14:R147 (severe hypophosphatemia < 0.32 mmol/L ≈ < 1.0 mg/dL → weaning failure /
  rhabdomyolysis). Hyperphosphatemia is capped at **watch** (a marker, not a bedside emergency) to limit fatigue.

---

## 4. Evidence citations — every threshold

| Threshold | Value | Evidence |
|-----------|-------|----------|
| Hyperkalemia crit / urgent | K⁺ >6.5 / >6.0 mmol/L | UKKA 2023 (VIS-3.6-02) |
| Hyperkalemia rescue trigger | K⁺ >6 mmol/L bundle; reassess K⁺ >5.5 @+4h | `RULE-EQUILIBRIO-004` (ADOPT-CORRECTED, mEq/L); KDIGO *Eur J Emerg Med* 2020;27(5):329-337 |
| Hypokalemia crit / urgent | K⁺ <2.5 / <3.0 mmol/L | Clase CM *BMJ* 2020; UKKA (VIS-3.6-03) |
| Hypernatremia crit / urgent | Na⁺ >160 / >155 mmol/L | ESICM 2024 (VIS-3.6-04) |
| Hypernatremia correction | água filtrada / NaCl 0.22 % / HCTZ | `RULE-EQUILIBRIO-002` (ADAPT, VERIFIED); Adrogué-Madias *NEJM* 2000 |
| Hyponatremia crit / urgent | Na⁺ <120 / <125 mmol/L | ESICM 2024 (VIS-3.6-05) |
| Na⁺ correction rate crit / urgent | Δ >10 / >8 mmol/L/24h | Sterns *JASN* 2015 (VIS-3.6-06); CON-0061 / CAT-C-01 |
| Hypercalcemia crit / urgent | iCa >1.60 / >1.45 mmol/L | Mousseaux *NDT* 2022 (VIS-3.6-07) |
| Hypocalcemia crit / urgent | iCa <0.80 / <0.90 mmol/L | Cooper *ICM* 2022 (VIS-3.6-08) |
| Corrected-total-Ca fallback | >14 / <7.0 mg/dL | `ELY-005` (vision §3.6 corrected-Ca) |
| Hypomagnesemia crit / urgent | Mg²⁺ <0.5 / <0.7 mmol/L | Hansen *ICM Exp* 2018 (VIS-3.6-09) |
| Hypophosphatemia crit / urgent | PO₄ <1.0 / <1.5 mg/dL | Geerse *Crit Care* 2010 — **pending RAT-ELY-01** |
| Hyperphosphatemia watch | PO₄ >7.0 mg/dL | designed default — **pending RAT-ELY-01** |

Response-time SLOs by severity (CON-0062/63/64/65): critical <5 min, urgent <30 min, watch <2 h, normal <6 h.

---

## 5. Interactions with other domains

- **Pharmaco-interaction (drug) domain — vision correlation #3 "Drug + Electrolyte — QTc + K⁺/Mg²⁺" (VIS-4-03).**
  This domain **owns the electrolyte contribution** to Torsades risk and emits `electrolyte.qtc_risk.electrolyte`
  (hypokalemia K<3.5, hypomagnesemia Mg<0.9, hypocalcemia) which `DDX-001` consumes alongside its
  CredibleMeds drug list and QTc. The drug list itself stays in pharmaco; this domain never duplicates it.
- **Pharmaco (bidirectional, hyperkalemia).** The pharmaco/med layer supplies the boolean
  `medicamento_hipercalemiante_ativo` and `digoxina_ativa`; this domain consumes them to gate the potassium
  watch band and the digoxin-toxicity pairing, then emits `electrolyte.dyskalemia.detected` back with the
  digoxin context so the drug domain can flag the offending agent.
- **AKI domain.** Consumes `aki.stage.detected` as context (CKD/AKI raises the pre-test probability of
  hyperkalemia, hyperphosphatemia, and hypocalcemia); routes `electrolyte.phosphate.disturbance`
  (hyperphosphatemia) to AKI / tumor-lysis review. Fluid-balance and nephrotoxic-substitution criteria of the
  shared `equilibrio` legacy trilha live in the **AKI** domain, not here.
- **Neuro-sedation.** Severe hyponatremia and hypocalcemia can cause seizures/altered mental status; the
  dysnatremia/calcium events are available as context for delirium/seizure work-up (consumer-side, no coupling).
- **Correlation Engine (Fase 2d).** All six per-ion events are correlation-ready (carry `mpi_id`, band,
  severity, `detected_at`); the QTc composite is the first wired cross-domain correlation.

---

## 6. RATIFY-pending & conflict handling (designed to recommended default)

Per CONTRACTS, items an agent cannot decide are **designed to the recommended default and marked pending a
ratification**, not silently resolved.

- **RAT-ELY-01 — phosphate canonical unit + numeric bands.** Vision §3.6 gives no PO₄ alert band and the units
  registry flags `fosfato` mg/dL as an open committee item. `ALERT-ELY-PHOSPHATE-01` is designed to the
  recommended default (hypo crit <1.0 / urgent <1.5 mg/dL; hyper watch >7.0 mg/dL, capped at watch) with the
  lowest PPV budget in the domain (0.65) and is the first drop candidate if its ignored-rate approaches 10 %.
  The committee ratifies the canonical unit and confirms/tightens the <1.0 mg/dL critical cut.
- **Magnesium severity conflict (recorded, not silently resolved).** vision VIS-3.6-09 (critical/urgent) vs
  legacy `ELY-006` (URG/WARN). Resolved to **vision** by precedence (vision ≻ audit-legacy, CONTRACTS rule 5);
  documented here and in the `ALERT-ELY-MAGNESIUM-01` reconciliation note. If a clinician review prefers the
  legacy softer severities, this becomes a formal RATIFY item.
- **Hyperkalemia unit-mislabel (ADOPT-CORRECTED, not RATIFY).** `RULE-EQUILIBRIO-004` labels K⁺ `mg/dl`;
  the reference-correct form uses mmol/L (mEq/L). Corrected here, never propagated (CON-0159); the clinical
  content of the bundle is adopted with citation (verified well per the escalation, ESC-P2-066 band P2).

*No P0 escalation lands in this domain* (P0-01..12 are scoring / sepse / estabilidade / ventilacao / piora),
so there is no mandatory-RATIFY rule; the only pending decisions are RAT-ELY-01 and the recorded Mg conflict.

---

## 7. Open questions

- **OQ-1 (albumina unit).** The units registry has no `albumina` parameter; the corrected-total-Ca fallback
  needs it. This spec uses the mission canonical **`g/dL`** (Brazilian lab convention, consistent with
  `hemoglobina`). Registry owner to add an `albumina` parameter (canonical g/dL; edge conversion g/L ×0.1).
- **OQ-2 (osmolality unit).** `mOsm/kg` is absent from the registry, so plasma osmolality is not a typed input
  (glucose correction is used instead). Register `osmolalidade` (canonical mOsm/kg) to enable
  pseudo/translocational-hyponatremia discrimination.
- **OQ-3 (delta baselines).** vision open question: which field/timestamp anchors `delta_k_24h`,
  `delta_na_24h_trailing` (trailing `sodio_atual − sodio_24h_atras`) and `correcao_na_24h_from_nadir`
  (the sodium 24 h nadir). The two sodium baselines are **distinct quantities** and MUST resolve separately
  (§3.3, HAZ-031). This spec assumes serial `lab_result` rows in AMH Gold with per-analyte timestamps;
  the exact lookback resolver is a downstream data-model decision (mirrors the AKI baseline resolver).

---

```yaml domain-inputs
domain: electrolyte
inputs:
  - {name: potassio, type: quantity, unit: "mmol/L", source: "AMH Gold lab_result LOINC 6298-4"}
  - {name: sodio, type: quantity, unit: "mmol/L", source: "AMH Gold lab_result LOINC 2951-2"}
  - {name: magnesio, type: quantity, unit: "mmol/L", source: "AMH Gold lab_result LOINC 19123-9"}
  - {name: calcio_ionizado, type: quantity, unit: "mmol/L", source: "AMH Gold lab_result LOINC 1994-3"}
  - {name: calcio_total, type: quantity, unit: "mg/dL", source: "AMH Gold lab_result LOINC 17861-6 (corrected-total fallback)"}
  - {name: fosfato, type: quantity, unit: "mg/dL", source: "AMH Gold lab_result LOINC 2777-1 (pending RAT-ELY-01)"}
  - {name: albumina, type: quantity, unit: "g/dL", source: "AMH Gold lab_result LOINC 1751-7 (OQ-1: not yet in units registry)"}
  - {name: glicemia, type: quantity, unit: "mg/dL", source: "AMH Gold lab_result (glucose-corrected sodium)"}
  - {name: creatinina, type: quantity, unit: "mg/dL", source: "AMH Gold lab_result LOINC 2160-0 (CKD / tumor-lysis context)"}
  - {name: qtc, type: quantity, unit: "ms", source: "AMH Gold Observation ECG QTc LOINC 44974-4"}
  - {name: delta_k_24h, type: quantity, unit: "mmol/L", source: "derived (potassio_atual - potassio_24h_atras)"}
  - {name: delta_na_24h_trailing, type: quantity, unit: "mmol/L", source: "derived (sodio_atual - sodio_24h_atras); ALERT-ELY-SODIUM-01 only — trailing 24h delta"}
  - {name: correcao_na_24h_from_nadir, type: quantity, unit: "mmol/L", source: "derived (sodio_atual - sodio_nadir_24h); ALERT-ELY-SODIUM-CORRECTION-02 only — MUST use the 24h nadir baseline (HAZ-031/HAZ-032)"}
  - {name: digoxina_ativa, type: boolean, unit: "boolean", source: "AMH Gold MedicationAdministration"}
  - {name: medicamento_hipercalemiante_ativo, type: boolean, unit: "boolean", source: "AMH Gold MedicationAdministration (espironolactona/eplerenona/IECA/BRA/TMP-SMX/heparina/succinilcolina)"}
  - {name: furosemida_dose_alta, type: boolean, unit: "boolean", source: "AMH Gold MedicationAdministration"}
  - {name: ckd_moderada_grave, type: boolean, unit: "boolean", source: "AMH Gold Condition / eGFR<60"}
alerts:
  - ALERT-ELY-POTASSIUM-01
  - ALERT-ELY-SODIUM-01
  - ALERT-ELY-SODIUM-CORRECTION-02
  - ALERT-ELY-CALCIUM-01
  - ALERT-ELY-MAGNESIUM-01
  - ALERT-ELY-PHOSPHATE-01
rule_refs:
  - RULE-EQUILIBRIO-002
  - RULE-EQUILIBRIO-004
interfaces:
  emits_events:
    - electrolyte.dyskalemia.detected
    - electrolyte.dysnatremia.detected
    - electrolyte.sodium_correction.hazard
    - electrolyte.calcium.disturbance
    - electrolyte.hypomagnesemia.detected
    - electrolyte.phosphate.disturbance
    - electrolyte.qtc_risk.electrolyte
  consumes:
    - {quantity: serum_potassium, unit: "mmol/L", source: "AMH Gold lab_result LOINC 6298-4"}
    - {quantity: serum_sodium, unit: "mmol/L", source: "AMH Gold lab_result LOINC 2951-2"}
    - {quantity: serum_magnesium, unit: "mmol/L", source: "AMH Gold lab_result LOINC 19123-9"}
    - {quantity: ionized_calcium, unit: "mmol/L", source: "AMH Gold lab_result LOINC 1994-3"}
    - {quantity: serum_phosphate, unit: "mg/dL", source: "AMH Gold lab_result LOINC 2777-1"}
    - {quantity: corrected_qt_interval, unit: "ms", source: "AMH Gold Observation LOINC 44974-4"}
    - {event: aki.stage.detected, source: "AKI domain (CKD/AKI context)"}
```
