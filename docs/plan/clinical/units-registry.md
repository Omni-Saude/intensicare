# Canonical Units Registry — IntensiCare v2

This document is the human-readable face of the single **canonical units registry** that every
domain spec and every alert input in IntensiCare v2 is mechanically validated against. The audit
proved that the legacy system's most dangerous defect class is **unit chaos** — the same number
meaning wildly different clinical severities depending on which unit an ingesting site happened to
use. This registry ends that ambiguity by fixing one canonical unit per parameter and forcing every
other unit to be normalized **at the edge, once**, before any clinical logic touches it.

The machine-readable source of truth is `docs/plan/_work/units/registry.yaml`. This markdown never
overrides it; where they could ever disagree, the YAML wins. The mission-mandated canonicals are LAW
(`docs/plan/_work/constraints/ledger.yaml` **CON-SEED-12**, reinforced by **CON-0060 / SYS-C-04**):
lactate `mmol/L`; FiO2 `fraction` 0–1 (percent display-only); vasopressor dosing `mcg/kg/min` (ml/h
is an edge input requiring the conversion service); temperature `°C`; creatinine `mg/dL`;
electrolytes per vision §3.6.

PT-BR clinical vocabulary (e.g. *balanço hídrico*, *bastonetes*, *diurese*, *noradrenalina*,
*débito urinário*, *frequência cardíaca*) is preserved verbatim, accents included.

---

## 1. Principles

1. **Canonical at every computation and API boundary.** Each parameter has exactly one
   `canonical_unit`. Every score formula, alert predicate, stored value, and API field carries that
   unit and no other. There is no "it depends on the site" — the site-dependence is resolved *before*
   the value enters the system.

2. **Edge normalization with explicit conversions.** Alternate units are accepted **only at the
   ingestion edge** and converted immediately. Two mechanisms:
   - **`aliases`** — synonym spellings that are numerically identical to the canonical unit
     (factor 1.0), e.g. `mEq/L` for a monovalent ion's `mmol/L`, `irpm` for `rpm`. Normalized by
     relabeling, no arithmetic.
   - **`edge_conversions`** — units needing a numeric factor, e.g. lactate `mg/dL → mmol/L ×0.111`.
     A conversion with `factor: null` is **not a fixed factor** and requires a service (temperature
     `°F` is affine; vasopressor `mL/h` needs drug concentration + weight).
   After the edge, an alias or foreign unit must never reappear.

3. **Display transforms are presentation-only.** A `display_transform` reshapes a value for the
   clinician's eyes without ever mutating the stored/compared canonical value. FiO2 is the archetype:
   stored and compared as `fraction` 0.21–1.0, shown as `%` by multiplying by 100. The transform is a
   one-way projection at render time, never a round-trip through storage.

4. **Unit mismatch is a BUILD-TIME error, not a runtime surprise.** In the alert-definition schema,
   an input whose declared `unit` is neither the parameter's `canonical_unit` nor a declared alias
   **fails the build**. Legacy failures happened silently at runtime (FiO2 40 compared to 0.4; lactate
   30 mg/dL treated as 30 mmol/L). v2 refuses to compile such a definition. Every alert input's `unit`
   must resolve into this registry (per `CONTRACTS.md` §Alert entry schema).

5. **Provenance duty.** Every canonical choice and every conversion factor carries `refs` — a
   published guideline, a `RULE-<CLUSTER>-<NNN>` catalog ID, a `SYS-`/`P0-` escalation, or a vision §.
   No number is invented; molar-mass-derived factors name the analyte's molecular weight. This mirrors
   `CONTRACTS.md` rule 3 (zero silent invention).

---

## 2. The registry by category

Tables are grouped exactly as in the YAML. **Canonical** is the only unit that crosses a computation
or API boundary. **Edge inputs** are accepted then converted; **1:1 aliases** are relabeled only.

### 2.1 Blood gases & oxygenation

| Parameter | Quantity | Canonical | Edge inputs → canonical | 1:1 aliases | Notes |
|---|---|---|---|---|---|
| `fio2` | inspired O2 fraction | **`fraction`** | `percent` ×0.01; `%` ×0.01 | — | **LAW.** Display ×100 → %. The single most dangerous legacy unit. |
| `pao2` | arterial pO2 | `mmHg` | `kPa` ×7.50062 | `torr` | Brazilian ABG in mmHg. |
| `paco2` | arterial pCO2 | `mmHg` | `kPa` ×7.50062 | `torr` | Drives NEWS2 Scale 2. |
| `spo2` | peripheral O2 sat | `percent` | `fraction` ×100 | `%` | Stays percent; ≠ FiO2. |
| `relacao_pao2_fio2` | P/F ratio | `ratio` | — (computed) | `P/F` | = PaO2(mmHg) / FiO2(**fraction**). |
| `relacao_spo2_fio2` | S/F ratio | `ratio` | — (computed) | `S/F` | = SpO2(%) / FiO2(**fraction**). |
| `ph_arterial` | acidity | `pH` | — | `pH` | Comma-decimal edge hazard (`7,15`). |
| `bicarbonato` | HCO3⁻ | `mmol/L` | — | `mEq/L` (monovalent) | Bicarbonate stewardship gate. |
| `lactato_arterial` | lactate | **`mmol/L`** | `mg/dL` ×0.111 (÷9.01) | `mM` | **LAW.** ~9x legacy chaos (SYS-03). |

### 2.2 Ventilation — airway pressures & volumes

| Parameter | Quantity | Canonical | Edge inputs → canonical | Notes |
|---|---|---|---|---|
| `peep` | PEEP | `cmH2O` | `mbar` ×1.01972 | Bounds diverge 0–40 vs 5–18 across forms (RATIFY). |
| `pressao_plato` | plateau pressure | `cmH2O` | `mbar` ×1.01972 | >30 cmH2O lung-protection cutoff. |
| `pressao_inspiratoria` | peak pressure (PINS) | `cmH2O` | `mbar` ×1.01972 | Bounds 0–30 vs 5–40 (RATIFY). |
| `volume_corrente` | tidal volume (absolute) | `mL` | `L` ×1000 | Legacy flagged absolute >500 mL — not lung-protective. |
| `volume_corrente_pbw` | tidal volume / PBW | `mL/kg` | — | Indexed to **predicted** body weight (height+sex), not `peso`. ARDSNet ≤6. |

### 2.3 Hemodynamics — pressures, rates, vasopressor dosing

| Parameter | Quantity | Canonical | Edge inputs → canonical | Notes |
|---|---|---|---|---|
| `pressao_arterial_sistolica` | SBP (PAS) | `mmHg` | `kPa` ×7.50062 | Feeds shock index. |
| `pressao_arterial_diastolica` | DBP (PAD) | `mmHg` | `kPa` ×7.50062 | RULE-SEPSE-043 PAD<90 is a threshold bug, unit fine. |
| `pressao_arterial_media` | MAP (PAM) | `mmHg` | `kPa` ×7.50062 | Legacy PAMValidator disabled (dead) — RATIFY + validate. |
| `dose_vasopressor` | weight-indexed vasopressor rate | **`mcg/kg/min`** | `mcg/kg/h` ÷60; `mg/kg/min` ×1000; **`mL/h` → service (factor null)** | **LAW.** norepinephrine/epinephrine/dopamine/dobutamine/phenylephrine. |
| `dose_vasopressina` | vasopressin (fixed-rate) | `U/min` | `U/h` ÷60 | **Not** weight-indexed; kept separate so it is never coerced into mcg/kg/min. |
| `indice_choque` | shock index | `ratio` | — (computed) | = HR(bpm) / SBP(mmHg); modified = HR/MAP. |
| `tempo_enchimento_capilar` | capillary refill (TEC) | `s` | — | ANDROMEDA-SHOCK normal ≤3s; unify the 3 legacy encodings. |

> **Vasopressor conversion service (cross-reference).** `mL/h` is a **pump rate, not a clinical
> dose**. Converting `mL/h → mcg/kg/min` is **not** a fixed multiplication — it needs the drug
> concentration (`concentracao_farmaco`, mg/mL) and the patient weight (`peso`, kg). That conversion
> lives in the hemodynamics designer's spec, not here:
> **`clinical/domains/hemodynamics.md#vasopressor-unit-conversion-service`**. Per **SYS-C-04 /
> CON-0060**, any code that assumes a constant `mL/h ↔ mcg/kg/min` factor is wrong; the registry
> encodes this by giving the `mL/h` edge conversion `factor: null` with a pointer to that service.

### 2.4 Labs — electrolytes (vision §3.6 canonicals)

Brazilian labs vary between `mg/dL` and `mmol/L`; **valence matters** — `mEq/L` equals `mmol/L` only
for *monovalent* ions (K⁺, Na⁺, Cl⁻, HCO3⁻). For *divalent* ions (Ca²⁺, Mg²⁺) `mEq/L = 0.5 × mmol/L`.

| Parameter | Quantity | Canonical | Edge inputs → canonical | 1:1 aliases | Notes |
|---|---|---|---|---|---|
| `potassio` | K⁺ | `mmol/L` | `mg/dL` ×0.2558 (⚠ suspected mislabel) | `mEq/L` | RULE-EQUILIBRIO-004 mislabels K⁺ as `mg/dl` — ADOPT-CORRECTED, never propagate. |
| `sodio` | Na⁺ | `mmol/L` | `mg/dL` ×0.435 (⚠ suspected mislabel) | `mEq/L` | Δ-Na correction ≤10 mmol/L/24h (CON-0061). |
| `magnesio` | Mg²⁺ | `mmol/L` | `mg/dL` ×0.4114; **`mEq/L` ×0.5** | — | Divalent — `mEq/L` is **not** 1:1. Vision cross-check: 0.5 mmol/L = 1.2 mg/dL. |
| `calcio_ionizado` | ionized Ca²⁺ | `mmol/L` | `mg/dL` ×0.2495; `mEq/L` ×0.5 | — | Vision §3.6 primary Ca measure. |
| `calcio_total` | total Ca (corrected) | `mg/dL` | `mmol/L` ×4.008; `mEq/L` ×2.004 | — | Albumin-corrected surrogate; prefer ionized. |
| `fosfato` | PO4 / phosphorus | `mg/dL` | `mmol/L` ×3.097 | — | Not in vision numeric table; Brazilian-lab convention (confirm w/ committee). |
| `cloreto` | Cl⁻ | `mmol/L` | — | `mEq/L` | Anion-gap / replacement vocab. |

### 2.5 Labs — chemistry, hematology, inflammatory

| Parameter | Quantity | Canonical | Edge inputs → canonical | Notes |
|---|---|---|---|---|
| `creatinina` | creatinine | **`mg/dL`** | `µmol/L` ×0.0113 (÷88.42) | **LAW.** SOFA-renal & KDIGO bands in mg/dL. |
| `clearance_creatinina` | creatinine clearance (CrCl) | `mL/min` | — | Cockcroft-Gault, **absolute** (not BSA-normalized); **drug dosing** (vision §3.7, CrCl<30). |
| `taxa_filtracao_glomerular` | eGFR (CKD-EPI) | `mL/min/1.73m2` | — | KDIGO CKD/AKI staging; BSA-normalized; **not** interchangeable with CrCl for dosing. |
| `glicemia` | glucose / HGT | `mg/dL` | `mmol/L` ×18.016 | Brazilian HGT is mg/dL. |
| `hemoglobina` | hemoglobin | `g/dL` | `g/L` ×0.1; `mmol/L` ×1.611 | **Audit:** legacy `mg/dl` label is a **1000x** error — reject mg/dL. |
| `plaquetas` | platelets | `10^3/uL` | `/uL` ÷1000; `/mm^3` ÷1000 | `10^3/uL` == `10^9/L`; matches SOFA numbers directly. |
| `bilirubina` | total bilirubin | `mg/dL` | `µmol/L` ×0.05848 (÷17.1) | SOFA-liver bands; SYS-07 boundary gaps are threshold bugs. |
| `leucocitos` | WBC / leukograma | `10^3/uL` | `/uL` ÷1000; `/mm^3` ÷1000 | SIRS >12 or <4 (×10³/µL). |
| `bastonetes` | band neutrophils | `percent` | `fraction` ×100 | SIRS >10% immature forms. |
| `proteina_c_reativa` | CRP (PCR) | `mg/L` | `mg/dL` ×10 | Brazilian `mg/dL` is a frequent silent **10x** error. |
| `procalcitonina` | PCT | `ng/mL` | — | `ng/mL` == `µg/L`; vision §3.1 PCT >0.5, <0.25. |

### 2.6 Neuro & clinical scores (dimensionless points / enum)

| Parameter | Quantity | Canonical | Range / states | Notes |
|---|---|---|---|---|
| `glasgow` | GCS | `points` | 3–15 (int) | qSOFA uses GCS<15; use `≤` at low end. |
| `rass` | RASS | `points` | −5..+4 (signed) | Never discard sign (P0-10 read only first char). |
| `cam_icu` | delirium (CAM-ICU) | `enum` | positivo/negativo/nao_avaliavel | Not numeric. |
| `mews` | MEWS | `points` | aggregate | Phase-1 implemented. |
| `news2` | NEWS2 | `points` | aggregate (incl. Scale 2) | Phase-1 implemented. |
| `sofa` | SOFA | `points` | 0–24 | **Corrupted if any input unit is wrong** (FiO2 fraction, vasopressor mcg/kg/min…). |
| `qsofa` | qSOFA | `points` | 0–3 | RR≥22, SBP≤100, GCS<15. |
| `escala_dor_numerica` | pain NRS (EVA) | `points` | 0–10 (capped) | SYS-06: `7 <= dor > 10` suppresses severe band. |
| `escala_dor_comportamental` | pain BPS | `points` | 3–12 (capped) | SYS-06: `10 <= sinais > 12` suppresses severe band. |

### 2.7 Vitals, fluids, anthropometrics, temporal

| Parameter | Quantity | Canonical | Edge inputs → canonical | Notes |
|---|---|---|---|---|
| `temperatura` | body temperature | **`°C`** | `°F` → (°F−32)×5/9 (**affine, null**); `K` → K−273.15 | **LAW.** Store DECIMAL(4,1). |
| `frequencia_cardiaca` | HR (FC) | `bpm` | — | Physician form was unbounded (accept-then-reject). |
| `frequencia_respiratoria` | RR (FR) | `rpm` | — | `irpm` is a 1:1 alias. |
| `debito_urinario` | urine output (volume) | `mL` | `L` ×1000 | Absolute KDIGO totals. |
| `debito_urinario_horario` | urine output (rate) | `mL/kg/h` | — | Weight-indexed; **SYS-09** weight bug makes oliguria invisible. |
| `balanco_hidrico` | fluid balance (BH) | `mL` | `L` ×1000 | Signed; SYS-10 window bug; recompute from source rows. |
| `peso` | body weight | `kg` | `g` ÷1000; `lb` ×0.453592 | **SYS-09:** edge parser must keep comma/dot decimals (`70,5`≠705). |
| `altura` | body height | `cm` | `m` ×100 | Needed (with sex) for PBW; comma-decimal hazard (`1,70`). |
| `idade` | age | `years` | `months` ÷12 | Delirium risk age>65; inclusion age≥18. |
| `qtc` | corrected QT | `ms` | `s` ×1000 | Torsades risk QTc>500 ms. |
| `intervalo_tempo` | elapsed duration | `h` | `min` ÷60; `s` ÷3600; `d` ×24 | Numeric inputs in `h`; trigger windows use ISO-8601 `PT*H`; legacy `.seconds` wraps at 24h (RULE-BALANCO-HIDRICO-016). |

### 2.8 Drug administration (edge inputs to the conversion service)

| Parameter | Quantity | Canonical | Edge inputs → canonical | Notes |
|---|---|---|---|---|
| `concentracao_farmaco` | drug concentration | `mg/mL` | `mcg/mL` ÷1000; `g/L` ×1; `mg/L` ÷1000 | Input #1 to the vasopressor conversion service. |
| `taxa_infusao` | volumetric infusion rate | `mL/h` **(edge-only)** | `mL/min` ×60; `gtt/min` → per drip set (null) | **Never a dosing predicate input** — convert to `dose_vasopressor` first. |

### 2.9 Dimensionless utility units

| Parameter | Canonical | Purpose |
|---|---|---|
| `fraction` | `fraction` | 0–1 primitive; canonical for FiO2 and proportions. Display ×100 → percent. |
| `percent` | `percent` | 0–100 primitive; canonical for SpO2/bands, display twin of fraction. |
| `points` | `points` | ordinal/integer scores; the range bound defeats SYS-06 band-suppression. |
| `boolean` | `boolean` | true/false presence flags. |
| `count` | `count` | non-negative integers (criteria met, drug count, beds); SYS-09 also hits bed counts. |
| `ratio` | `ratio` | P/F, S/F, shock index, RSBI — valid only when numerator & denominator are canonical. |

---

## 3. Legacy hazards this registry kills

Each canonical decision above exists to permanently close a verified legacy defect class. The four
unit-specific systemic escalations and their affected catalog rules:

### SYS-01 — FiO2 percent-vs-fraction (`fio2` → **`fraction`**, percent display-only)
Legacy `FiO2Validator` stored 21–100 (a percentage) while the P/F ratio and every consumer treated
FiO2 as a fraction 0.21–1.0, so with validator-conformant data the ratio ran **~100x too small** —
driving the SOFA respiratory sub-score to max and spuriously classifying severe ARDS, while
`fio2 < 0.4` fraction comparisons never fired on percentage data. Unit tests set `fio2=1` directly,
bypassing the validator and masking the defect.
*Killed by:* one canonical `fraction`, percent as an edge input **and** a display-only transform, and
`relacao_pao2_fio2` documented as requiring the fraction. *Affected rules:* RULE-CLINICAL-SCORING-002,
RULE-CLINICAL-SCORING-008, RULE-VENTILACAO-004, RULE-VENTILACAO-005, RULE-VENTILACAO-006,
RULE-VENTILACAO-011, RULE-SEDACAO-004, RULE-SEDACAO-016, RULE-SEPSE-020, RULE-EVOLUCOES-001,
RULE-TRILHAS-ENGINE-017. (P0-01, P0-07, P0-11.)

### SYS-02 — Vasopressor dose-unit chaos (`dose_vasopressor` → **`mcg/kg/min`**)
Noradrenaline/inotrope thresholds mixed a raw infusion **volume** (`ml`) or a **rate** (`ml/h`) with
the clinical-standard weight-based rate `mcg/kg/min` — and `ml/h → mcg/kg/min` is **not convertible**
without drug concentration and patient weight. Separately, the same `>0.5` noradrenaline cutoff was
labelled `mcg/kg/min` in RULE-ESTABILIDADE-016 but `mcg/kg/h` in RULE-ESTABILIDADE-024 — a **60x**
discrepancy on the same number.
*Killed by:* canonical `mcg/kg/min`; `mcg/kg/h` accepted at the edge with the fixed ÷60 factor;
`mL/h` given `factor: null` and routed to the conversion service
(`clinical/domains/hemodynamics.md#vasopressor-unit-conversion-service`); `taxa_infusao` (`mL/h`)
flagged edge-only and forbidden as a dosing-predicate input. *Affected rules (volume/rate):*
RULE-CLINICAL-SCORING-005, RULE-ESTABILIDADE-007/008/009/016/019, RULE-SEDACAO-005/010,
RULE-SINAIS-VITAIS-029, RULE-SEPSE-014; *(per-minute vs per-hour):* RULE-ESTABILIDADE-007/008/016/019/024,
RULE-SEDACAO-010, RULE-SINAIS-VITAIS-029, RULE-TRILHAS-ENGINE-017. (P0-02, P0-06; SYS-C-04 / CON-0060.)

### SYS-03 — Lactate mg/dL vs mmol/L (`lactato_arterial` → **`mmol/L`**)
Sepsis/shock pathways and their facades disagreed on whether a lactate value was `mg/dL` or `mmol/L`
(~**9x** factor), so the same numeric cutoff denoted very different severities. Legacy
RULE-SEPSE-061 used `30 mg/dL` (≈ 3.3 mmol/L).
*Killed by:* canonical `mmol/L`; `mg/dL` accepted at the edge with the ×0.111 (÷9.01) factor; a bare
lactate number without a unit is a build-time error. *Affected rules:* RULE-EFICIENCIA-008,
RULE-ESTABILIDADE-005, RULE-ESTABILIDADE-020, RULE-SEPSE-013, RULE-SEPSE-050, RULE-SEPSE-058,
RULE-SEPSE-059, RULE-SEPSE-061, RULE-VENTILACAO-012.

### SYS-09 — Weight decimal-separator parse (`peso` → **`kg`**, comma-aware edge parser)
Legacy parsed weight with `float(''.join(re.findall(r'\d+', peso.replace(',', '.'))))`, which
**strips the decimal point entirely**: `'70,5'` / `'70.5' → 705 kg`. Every weight-normalized
threshold (`mL/kg/h` urine output, `mcg/kg` dosing, `mL/kg` PBW) then ran **~10x** off, and
bed/occupancy counts built on the same parser were likewise corrupted.
*Killed by:* canonical `kg` with an explicit edge-parser mandate to accept **both** comma and dot
decimals and **preserve** the separator; `debito_urinario_horario`, `volume_corrente_pbw`, and
`dose_vasopressor` all carry the SYS-09 provenance note; the `count` utility warns bed/occupancy
counts share the bug. *Affected rules:* RULE-CLINICAL-SCORING-002, RULE-SEPSE-014,
RULE-TENANCY-ORGANIZACAO-003, RULE-TENANCY-ORGANIZACAO-004, RULE-TENANCY-ORGANIZACAO-012. (P0-08.)

### Related unit mislabels also neutralized
- **Hemoglobin `mg/dl` → `g/dL`** (audit): the legacy label is a 1000x error; `mg/dL` is rejected as
  an alias for `hemoglobina`.
- **Potassium `mg/dl` → `mmol/L`** (RULE-EQUILIBRIO-004, CLU-EQUILIBRIO-C-01): K⁺ is physiologically
  `mEq/L` (= `mmol/L`); inbound `mg/dL` is treated as a suspected mislabel, flagged not silently
  converted.
- **CRP `mg/dL` → `mg/L`**: a routine Brazilian 10x edge input, normalized once.
- **Divalent `mEq/L` traps** (Ca²⁺, Mg²⁺): `mEq/L = 0.5 × mmol/L`, encoded as an edge factor, not a
  1:1 alias.

> These are **unit** decisions only. Whether a legacy *threshold* is correct (e.g. RULE-SEPSE-043
> comparing PAD<90) is a separate clinical/product-owner ratification (SYS-C-01..04, CON-0059);
> this registry fixes the units those thresholds are expressed in, so ratification argues about
> clinical intent rather than about arithmetic.

---

## 4. Machine registry pointer

```yaml units-registry-pointer
machine_registry: "docs/plan/_work/units/registry.yaml"
version: 2
```
