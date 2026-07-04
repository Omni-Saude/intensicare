# RATIFICATION — Open Human Decisions, IntensiCare v2 Build Plan

Every item below requires a decision by the clinical committee, product owner, or legal
counsel. Each carries a concrete question, options, and the plan's recommended default —
the design proceeds on the recommended default and marks the affected specs `pending RAT-*`.

**Standing policy (locked at Phase 0, ratify or amend):** rules escalated at bands
P0, P1, or UNVERIFIABLE-owner-review are never silently adopted — each is dispositioned
`RATIFY` and listed here. P2/P3 were decided by the disposition pass citing the escalation;
AMBIGUOUS rules were kept (RATIFY) or retired per clinical value.

## The five audit ratification asks

<a id="ask-1"></a>
### ASK-1 — Ratification ask 1: Clinical committee review of all P0 and P1 findings (57 items) — for each, rule whether th

Ratification ask 1: Clinical committee review of all P0 and P1 findings (57 items) — for each, rule whether the legacy behavior is intended (carry forward) or a defect (change). Start with the 12 P0 items in ESCALATIONS.md.

*Source: AUDIT-REPORT.md §8, item 1*

**Answered by this plan:** see the corresponding sections below (P0/P1 committee queue, UNVERIFIABLE owner queue, e-signature items, sepsis aggregation item, and the canonical units registry `clinical/units-registry.md`).

<a id="ask-2"></a>
### ASK-2 — Ratification ask 2: Owner confirmation of the 101 UNVERIFIABLE owner-review rules (plus the 102 UNVERIFIABLE v

Ratification ask 2: Owner confirmation of the 101 UNVERIFIABLE owner-review rules (plus the 102 UNVERIFIABLE verification verdicts they derive from) — proprietary logic whose intent only the product/clinical owner can confirm.

*Source: AUDIT-REPORT.md §8, item 2*

**Answered by this plan:** see the corresponding sections below (P0/P1 committee queue, UNVERIFIABLE owner queue, e-signature items, sepsis aggregation item, and the canonical units registry `clinical/units-registry.md`).

<a id="ask-3"></a>
### ASK-3 — Ratification ask 3: Legal review of the e-signature findings — the shared default signing PIN (RULE-AUTH-USUAR

Ratification ask 3: Legal review of the e-signature findings — the shared default signing PIN (RULE-AUTH-USUARIOS-063) and the default CryptoCubo signature profile (advanced, ICP-Brasil disabled; RULE-DOCUMENTACAO-FATURAMENTO-032) against MP 2.200-2 / ICP-Brasil e-signature norms.

*Source: AUDIT-REPORT.md §8, item 3*

**Answered by this plan:** see the corresponding sections below (P0/P1 committee queue, UNVERIFIABLE owner queue, e-signature items, sepsis aggregation item, and the canonical units registry `clinical/units-registry.md`).

<a id="ask-4"></a>
### ASK-4 — Ratification ask 4: Decision on v1-vs-v3 sepsis aggregation — whether the new platform adopts v1 AND-logic or 

Ratification ask 4: Decision on v1-vs-v3 sepsis aggregation — whether the new platform adopts v1 AND-logic or v3 OR-logic as the canonical sepsis screen (RULE-SEPSE-001 / RULE-SEPSE-002).

*Source: AUDIT-REPORT.md §8, item 4*

**Answered by this plan:** see the corresponding sections below (P0/P1 committee queue, UNVERIFIABLE owner queue, e-signature items, sepsis aggregation item, and the canonical units registry `clinical/units-registry.md`).

<a id="ask-5"></a>
### ASK-5 — Ratification ask 5: Canonical unit decisions before any reimplementation — a single ratified convention for Fi

Ratification ask 5: Canonical unit decisions before any reimplementation — a single ratified convention for FiO2 (fraction vs percentage), lactate (mg/dL vs mmol/L), and vasopressor dosing (mcg/kg/min vs ml/h vs raw ml), resolving cross-cutting issues 1-3 once rather than rule-by-rule.

*Source: AUDIT-REPORT.md §8, item 5*

**Answered by this plan:** see the corresponding sections below (P0/P1 committee queue, UNVERIFIABLE owner queue, e-signature items, sepsis aggregation item, and the canonical units registry `clinical/units-registry.md`).

## P0 — high clinical impact (committee review first) (12 items)

<a id="rat-clinical-scoring-01"></a>
### RAT-CLINICAL-SCORING-01 — RULE-CLINICAL-SCORING-002: SOFA respiratory sub-score (PaO2/FiO2)

> UNIT DISCREPANCY: thresholds are the standard P/F cutoffs which require FiO2 as a fraction (0.21-1.0), but the DadosProntuario FiO2Validator stores 21-100 (percentage). With a percentage FiO2 the ratio is ~100x too small vs standard P/F. Tests set attributes directly (fio2=1) bypassing the validator. See RULE-008. Same bilirubin-style strict-upper-

**Question.** For the SOFA respiratory sub-score (PaO2/FiO2), in what unit must FiO2 be supplied to the ratio, and must the 3- and 4-point bands be gated on active respiratory support?

**Options.**

- **A** — Reproduce legacy verbatim: divide PaO2 by FiO2 as stored by DadosProntuario.FiO2Validator (percentage 21-100), apply bands 400/300/200/100 unconditionally with no respiratory-support gate. *(risk: High — a percentage FiO2 makes the ratio ~100x too small, driving virtually every ventilated patient to the maximum 4 respiratory points and inflating total SOFA; also over-scores spontaneously breathing patients.)*
- **B** — Normalize FiO2 to a fraction 0.21-1.0 before dividing (convert any 21-100 percentage input by /100), keep the reference cutoffs 400/300/200/100, and gate the 3- and 4-point bands on documented respiratory support (mechanical ventilation / CPAP) per the SOFA definition. *(risk: Low — reproduces the validated 1996 SOFA respiratory scoring; correct oxygenation banding with no systematic upward bias.)*
- **C** — Normalize FiO2 to a fraction but omit the respiratory-support gate on the 3/4-point bands. *(risk: Moderate — fixes the ~100x unit defect but still over-scores a spontaneously breathing patient with a low ratio (bands 3-4 should require support).)*

**Recommended default.** B — Vincent JL et al., Intensive Care Med 1996;22(7):707-710 defines the SOFA respiration component on PaO2/FiO2 with PaO2 in mmHg and FiO2 as a FRACTION (0.21-1.0): >=400=0, 300-399=1, 200-299=2, 100-199=3 (with respiratory support), <100=4 (with respiratory support). The legacy cutoffs are correct but assume a fraction while the persisted FiO2 is a percentage (21-100), and the 3/4 bands are applied without the support gate. Option B is the reference-correct behavior.

**Disposition note.** RATIFY the reference-correct SOFA respiratory sub-score: FiO2 normalized to fraction 0.21-1.0, cutoffs 400/300/200/100, and the 3- and 4-point bands gated on active respiratory support. Do NOT port the percentage-FiO2 defect (RULE-CLINICAL-SCORING-002 / shared unit defect RULE-CLINICAL-SCORING-008). Legacy tests set fio2=1 directly and mask the runtime bug. Downstream: this sub-score feeds SOFA total (RULE-CLINICAL-SCORING-001).

<a id="rat-clinical-scoring-03"></a>
### RAT-CLINICAL-SCORING-03 — RULE-CLINICAL-SCORING-005: SOFA cardiovascular sub-score (vasopressors/MAP)

> DISCREPANCY: standard SOFA cardiovascular uses vasopressor RATES in mcg/kg/min (norepi >0.1=4, <=0.1=3; dopamine/epinephrine tiers; dobutamine any=2; MAP<70=1). Here noradrenaline is a raw ml volume (Noradrenalina.quantidade) with cutoff 10, and dobutamine is any>0=2. MAP<70=1 matches standard. Non-standard dosing units.

**Question.** For the SOFA cardiovascular sub-score, must vasopressor dosing be evaluated as an infusion RATE in mcg/kg/min (with the standard norepinephrine/dopamine/epinephrine/dobutamine tiers), rather than the legacy raw Noradrenalina.quantidade ml volume split at 10?

**Options.**

- **A** — Reproduce legacy verbatim: noradrenalina as a raw ml volume (Noradrenalina.quantidade) with >10=4 / 0<=10=3, dobutamina any>0=2, pam<70=1, pam>=70=0. *(risk: High — a raw ml volume is not comparable to a mcg/kg/min rate; any patient on noradrenaline is auto-tiered to >=3 points regardless of true dose, and dopamine/epinephrine are ignored, materially mis-scoring shock severity.)*
- **B** — Score cardiovascular on vasopressor RATE in mcg/kg/min per Vincent 1996: MAP>=70=0; MAP<70=1; dopamine<=5 OR dobutamine any dose=2; dopamine>5 OR epinephrine<=0.1 OR norepinephrine<=0.1=3; dopamine>15 OR epinephrine>0.1 OR norepinephrine>0.1=4. *(risk: Low — reproduces the validated SOFA cardiovascular tiers; requires the platform to capture/derive infusion rate (mcg/kg/min) with drug concentration and patient weight.)*
- **C** — Keep MAP bands (>=70=0, <70=1) and dobutamine-any=2 from legacy (which match reference) but replace the noradrenaline ml split with the mcg/kg/min norepinephrine tiers and add dopamine/epinephrine tiers. *(risk: Low — functionally converges with Option B; documents that only the vasopressor-rate handling changes while MAP/dobutamine bands are already reference-concordant.)*

**Recommended default.** B — Vincent JL et al., Intensive Care Med 1996 scores SOFA cardiovascular on vasopressor doses in mcg/kg/min sustained >=1h. MAP<70=1 and dobutamine-any=2 already match; the defect is that noradrenaline is read as a raw ml VOLUME (Noradrenalina.quantidade) split at 10 and dopamine/epinephrine are absent. Option B (equivalently C) restores the reference rate-based tiers.

**Disposition note.** RATIFY the rate-based (mcg/kg/min) SOFA cardiovascular tiers per Vincent 1996; preserve the MAP bands and dobutamine-any=2 already correct in legacy. Do NOT port the raw-ml Noradrenalina.quantidade cutoff of 10. Preserve PT-BR field vocabulary verbatim (Noradrenalina.quantidade, pam, dobutamina). Requires infusion-rate capture (concentration + weight) upstream.

<a id="rat-clinical-scoring-04"></a>
### RAT-CLINICAL-SCORING-04 — RULE-CLINICAL-SCORING-007: SOFA renal sub-score (creatinine/urine output)

> DISCREPANCY vs standard SOFA renal (Cr mg/dL): <1.2=0, 1.2-1.9=1, 2.0-3.4=2, 3.5-4.9=3, >=5.0=4; urine <500=3, <200=4. Here the '2 points' band is 2.0-4.0 (standard 2.0-3.4) and '>5' is strict leaving a dead gap at (4.9,5.0]. Reproduce VERBATIM.

**Question.** For the SOFA renal sub-score, must the creatinine bands use the standard boundaries with an inclusive top band (>=5.0 mg/dL = 4) instead of the legacy strict >5 that leaves a dead gap at (4.9, 5.0]?

**Options.**

- **A** — Reproduce legacy verbatim: creatinine >5=4, 3.5-4.9=3, 2.0-4.0=2, 1.2-1.9=1, <1.2=0; urine <200=4, <500=3. *(risk: High — creatinine exactly 5.0 mg/dL (a common reported value denoting severe renal failure) falls through every branch to 0, a 4-point undercount that silently lowers total SOFA and can under-triage severe AKI.)*
- **B** — Use standard SOFA renal bands per Vincent 1996: creatinine <1.2=0, 1.2-1.9=1, 2.0-3.4=2, 3.5-4.9=3, >=5.0=4; urine output <500 mL/day=3, <200 mL/day=4 (inclusive top band, no dead gap). *(risk: Low — reproduces the validated 1996 SOFA renal scale with contiguous bands and correct handling of Cr=5.0.)*
- **C** — Patch only the top boundary to >=5.0 while leaving the nominal 2-point band written as 2.0-4.0. *(risk: Low — closes the Cr=5.0 undercount; the 2.0-4.0 vs 2.0-3.4 wording is practically inert because the 3.5-4.9 branch is evaluated first, but leaves a hairline reference gap at (3.4, 3.5).)*

**Recommended default.** B — Vincent JL et al., Intensive Care Med 1996;22(7):707-710 renal component (serum creatinine mg/dL OR urine output): <1.2=0, 1.2-1.9=1, 2.0-3.4=2, 3.5-4.9=3, >=5.0 (>440 umol/L)=4; urine <500=3, <200=4. The legacy strict >5 leaves a dead gap at (4.9,5.0] and the 2-point band is mis-stated as 2.0-4.0. Option B is fully reference-correct.

**Disposition note.** RATIFY standard SOFA renal bands with inclusive >=5.0=4 and 2.0-3.4=2; do NOT port the strict >5 dead gap at (4.9,5.0] nor the 2.0-4.0 band wording. Keep urine-output cutoffs (<200=4, <500=3). Note legacy open-low bound treated debito==0 as no-data; preserve intent that true anuria (0 mL) is captured via the <200 band. PT-BR: debito_urinario_24h, creatinina.

<a id="rat-piora-clinica-04"></a>
### RAT-PIORA-CLINICA-04 — RULE-PIORA-CLINICA-006: Piora Clinica criterio_6 - Dor (escala numerica 0-10) (graded sub-score)

> *Cluster:* `piora-clinica` · *Category:* `clinical-scoring` · *Extraction:* DISCREPANCY · *Verification:* DISCREPANCY  **What the legacy does.** Graded numeric pain-scale (0-10 numeric rating scale) sub-score.  **Why it matters clinically.** Confirms the extraction DISCREPANCY. The severe-pain band `if 7 <= dor > 10` parses as (7 <= dor) AND (dor >

**Question.** For Piora Clinica criterio_6 (dor, escala numerica 0-10 / NRS), must the severe-pain band be corrected to 7 <= dor <= 10 -> 3+ so it actually fires?

**Options.**

- **A** — Reproduce legacy verbatim: severe band written `7 <= dor > 10` (parses as 7<=dor AND dor>10), which is unreachable because escala_dor is capped at 10, so pain 7,8,9,10 all score 0. *(risk: High — severe pain (NRS 7-10) never raises the 3+ (dor intensa) sub-score, silently suppressing the highest pain grade and any AMARELO/VERMELHO it should drive.)*
- **B** — Correct the compound-comparison typo to `7 <= dor <= 10 -> 3+`, keeping the mild 2-3 -> 1+ and moderate 4-6 -> 2+ bands. *(risk: Low — restores the intended NRS severe-pain band; higher score = worse, severe pain drives intervention as the reference requires.)*

**Recommended default.** B — Numeric Rating Scale (NRS 0-10) for pain intensity (Boonstra AM et al., Front Psychol 2016;7:1466): severe pain is the 7-10 band and is the grade that must drive intervention. The legacy `7 <= dor > 10` is a compound-comparison bug that makes 3+ unreachable; the reference-correct predicate is `7 <= dor <= 10`.

**Disposition note.** RATIFY the corrected severe-pain band `7 <= dor <= 10 -> 3+`. Do NOT port the buggy `7 <= dor > 10` compound comparison (unreachable). Preserve PT-BR labels verbatim: 2+ = 'dor moderada', 3+ = 'dor intensa' (facade RULE-PIORA-CLINICA-011). Feeds the aggregate alert RULE-PIORA-CLINICA-010.

<a id="rat-piora-clinica-05"></a>
### RAT-PIORA-CLINICA-05 — RULE-PIORA-CLINICA-007: Piora Clinica criterio_7 - Dor (escala comportamental 3-12) (graded sub-score)

> *Cluster:* `piora-clinica` · *Category:* `clinical-scoring` · *Extraction:* DISCREPANCY · *Verification:* DISCREPANCY  **What the legacy does.** Graded behavioral pain-scale (range 3-12) sub-score.  **Why it matters clinically.** Confirms the extraction DISCREPANCY, identical bug pattern to criterio_6. `if 10 <= sinais > 12` parses as (10 <= sinais

**Question.** For Piora Clinica criterio_7 (dor, escala comportamental / Behavioral Pain Scale 3-12), must the top band be corrected to 10 <= sinais <= 12 -> 3+ so it actually fires?

**Options.**

- **A** — Reproduce legacy verbatim: top band written `10 <= sinais > 12` (parses as 10<=sinais AND sinais>12), unreachable because sinais_dor is capped at 12, so BPS 10,11,12 score 0. *(risk: High — maximal behavioral pain (BPS 10-12) never raises the 3+ (dor intensa) sub-score, suppressing the highest pain grade for non-verbal/sedated patients who cannot self-report.)*
- **B** — Correct the compound-comparison typo to `10 <= sinais <= 12 -> 3+`, keeping 5-6 -> 1+ and 7-9 -> 2+. *(risk: Low — restores the intended BPS top band; BPS >5 (>=6) already indicates significant pain requiring analgesia, so the severe band must be reachable.)*

**Recommended default.** B — Behavioral Pain Scale (Payen JF et al., Crit Care Med 2001;29(12):2258-63): three domains each 1-4, total 3 (no pain) to 12 (maximal pain), higher = worse; score >5 indicates unacceptable pain requiring analgesia. Legacy `10 <= sinais > 12` is the identical compound-comparison bug as criterio_6; reference-correct predicate is `10 <= sinais <= 12`.

**Disposition note.** RATIFY the corrected top band `10 <= sinais <= 12 -> 3+`. Do NOT port the buggy `10 <= sinais > 12` compound comparison. Preserve PT-BR labels verbatim: 2+ = 'dor moderada', 3+ = 'dor intensa'. Same defect pattern as ESC-P0-004; feeds RULE-PIORA-CLINICA-010.

<a id="rat-estabilidade-08"></a>
### RAT-ESTABILIDADE-08 — RULE-ESTABILIDADE-016: Estabilidade facade alert-text - vasopressor/inotrope escalation ladder (criteria 7-9)

> Cross-implementation (facade text vs v3 predicate code): (a) UNITS — facade dosing is in noradrenaline mcg/kg/min (>0.5, >1.5) whereas the paired v3 predicates trigger on qt_vol_nora infusion volume in ml/h (RULE-007 >20 ml/h; RULE-008 >70 ml/h + vaso>5 ml/h), which are not convertible without concentration/weight; (b) criterio_9 text centres on FC

**Question.** For the Estabilidade vasopressor/inotrope escalation alert-text (criteria 7-9), must the displayed noradrenaline dose thresholds and the FC>130 tachycardia condition be driven by predicates measured in the SAME unit as the text (mcg/kg/min and actual FC), resolving the ml/h-vs-mcg/kg/min mismatch?

**Options.**

- **A** — Reproduce legacy verbatim: display text asserting noradrenaline >0.5 / >1.5 mcg/kg/min and FC>130 bpm, while the paired v3 predicates fire on qt_vol_nora infusion volume in ml/h (>20; >70 + vaso>5) and never read FC. *(risk: High — the alert shows a mcg/kg/min dose threshold the trigger never measured; for common dilutions the ml/h trigger fires ~6-7x below the displayed 0.5 mcg/kg/min, prompting corticosteroid/vasopressin escalation at a much lower actual dose, and the FC>130 advice fires independent of real heart rate.)*
- **B** — Align the trigger to the displayed clinical unit: evaluate noradrenaline as mcg/kg/min (add vasopressin when norepinephrine ~0.25-0.5 mcg/kg/min; IV hydrocortisone when norepinephrine/epinephrine >=0.25 mcg/kg/min for >=4h; epinephrine as second-line in refractory shock) and gate criterio_9 on actual FC>130 bpm. *(risk: Low — text and trigger share one unit (mcg/kg/min) and criterio_9 reads real FC; escalation prompts match SSC-2021. Requires infusion-rate derivation (concentration + weight) upstream.)*
- **C** — Keep ml/h predicates but rewrite the displayed text to state the ml/h thresholds actually evaluated and remove the mcg/kg/min and FC claims the code cannot verify. *(risk: Moderate — removes the misleading unit mismatch but abandons the guideline-anchored mcg/kg/min dosing and the physiologically sound FC>130 dobutamine-suspension advice; ml/h thresholds are not guideline-referenceable without concentration/weight.)*

**Recommended default.** B — Surviving Sepsis Campaign 2021 (Evans et al., Crit Care Med 2021): add vasopressin usually when norepinephrine 0.25-0.5 mcg/kg/min; IV hydrocortisone 200 mg/d when norepinephrine or epinephrine >=0.25 mcg/kg/min for >=4h; epinephrine as second-line in refractory shock. Tachycardia (FC>130 bpm) impairs LV filling/CO. The displayed mcg/kg/min doses are guideline-plausible; the defect is the unit mismatch to ml/h predicates and the unread FC. Option B makes the reference-correct dosing the actual trigger — the mcg/kg/min facade dosing is the target, the ml/h predicates are the defect to discard.

**Disposition note.** RATIFY unit-aligned escalation: noradrenaline evaluated in mcg/kg/min per SSC-2021 and criterio_9 gated on actual FC>130 bpm. Do NOT port the qt_vol_nora ml/h predicates (>20; >70 + vaso>5) that never verify the displayed mcg/kg/min or FC. Preserve PT-BR dosing regimens verbatim (Hidrocortisona 50 mg EV 6/6h; Vasopressina EV continua; Adrenalina diluicao institucional). Cross-pathway note: estabilizacao sibling RULE-ESTABILIDADE-024 labels the analogous threshold mcg/kg/H — reconcile units there too. Paired v3 predicates: RULE-ESTABILIDADE-007/008/009.

<a id="rat-clinical-scoring-05"></a>
### RAT-CLINICAL-SCORING-05 — RULE-CLINICAL-SCORING-008: PaO2/FiO2 ratio (relacao PO2/FiO2)

> UNIT DISCREPANCY: FiO2Validator restricts fio2 to 0 or 21..100 (a percentage), but every clinical threshold using this ratio (SOFA 400/300/200/100; ventilacao 150/200/250/300) and all tests (fio2=1 -> ratio=po2) treat fio2 as a fraction 0.21..1.0. Tests set attributes directly, bypassing the validator. With percentage FiO2 the ratio is ~100x too sm

**Question.** For the PaO2/FiO2 (P/F) ratio helper consumed by SOFA, ventilacao, sedacao and sepse, must FiO2 be canonicalized to a FRACTION (0.21-1.0) so every downstream threshold uses one consistent unit?

**Options.**

- **A** — Reproduce legacy verbatim: return po2/fio2 using whatever FiO2 unit reaches the property (validator stores 21-100 percent; some call sites pass fraction <0.4; the FiO2xPEEP table divides by 100), False sentinel on non-positive inputs. *(risk: High — internally inconsistent FiO2 units; if a validator-conformant percentage FiO2 reaches the helper the ratio is ~100x too small, driving SOFA respiratory to 4 points and spuriously classifying severe ARDS.)*
- **B** — Canonicalize FiO2 to a fraction 0.21-1.0 at a single boundary (normalize any 21-100 percentage by /100) before computing po2/fio2; keep the equation and the non-positive-input no-data guard; represent no-data as None rather than the False sentinel. *(risk: Low — one consistent unit across SOFA (400/300/200/100), ventilacao (150-300) and Berlin ARDS; eliminates the ~100x mis-scoring and the ambiguous False==0 numeric coercion.)*
- **C** — Canonicalize FiO2 to a fraction but retain the False (==0) no-data sentinel. *(risk: Low — fixes the unit inconsistency; retains a benign but easily-misused False==0 sentinel in numeric comparisons.)*

**Recommended default.** B — PaO2/FiO2 in every authoritative use (Vincent 1996 SOFA; Berlin Definition of ARDS, JAMA 2012;307:2526-2533) has PaO2 in mmHg and FiO2 as a FRACTION (0.21-1.0), e.g. P/F 300 = PaO2 150 at FiO2 0.5. The DadosProntuario.FiO2Validator stores a percentage (21-100) and the codebase is internally inconsistent. Option B canonicalizes to the reference fraction at one point, the reference-correct behavior; distinguishing no-data as None (Option B over C) is the safer secondary choice.

**Disposition note.** RATIFY a single FiO2-as-fraction canonicalization (0.21-1.0) for the shared P/F helper; do NOT port the percentage-vs-fraction inconsistency (validator 21-100 vs call sites <0.4 vs /100 in the FiO2xPEEP table). This helper feeds SOFA respiratory (RULE-CLINICAL-SCORING-002 / ESC-P0-001) and ventilacao/sedacao/sepse pathways; canonicalizing here fixes them consistently. Prefer None over the False sentinel for no-data.

<a id="rat-sepse-08"></a>
### RAT-SEPSE-08 — RULE-SEPSE-014: SEPSE v3 criterio_8 - oliguria without vasopressor/dialysis

> DISCREPANCY - (a) weight-parse strips the decimal separator inflating peso ~10x; (b) the "DRC em TRS" diagnosis gate is non-functional per RULE-systemic-BE-03-001 and also inverted (docstring wants ABSENCE of DRC, code has no `not`), so this whole all([]) is effectively always False. Same diurese formula appears (commented) in trilha_profilaxia.py 

**Question.** For SEPSE v3 criterio_8 (oliguria without vasopressor/dialysis), must the KDIGO urine-output criterion be made functional by fixing the always-empty 'DRC em TRS' diagnosis gate (and correcting its inverted sense) and the decimal-stripping weight parse?

**Options.**

- **A** — Reproduce legacy verbatim: all([...]) including the DRC gate list(filter(x=='DRC em TRS', vars(evolucao).fromkeys(diagnostico_1..4))) which always yields [] (dead code) and the weight parse that strips the decimal separator (peso '70,5' -> 705 kg). *(risk: High — the fromkeys bug forces the whole all([]) to False, so this safety-relevant AKI/oliguria criterion NEVER fires (permanent false-negative); if the gate were fixed, the ~10x weight inflation would then over-flag oliguria.)*
- **B** — Implement the reference-correct criterion: urine output <0.5 mL/kg/h over the last 6-12h (KDIGO Stage 1), ABSENCE of noradrenaline (12h), ABSENCE of hemodialysis, and ABSENCE of chronic dialysis-dependent renal disease ('DRC em TRS') using a real diagnosis membership test; parse weight as a true decimal (70,5 -> 70.5 kg). *(risk: Low — the KDIGO oliguria criterion fires correctly with an accurate mL/kg/h rate and a functioning exclusion for patients already on renal replacement therapy.)*

**Recommended default.** B — KDIGO AKI 2012 (Kidney Int Suppl 2012;2:1-138): urine output <0.5 mL/kg/h for 6-12h defines Stage 1 oliguria. The core threshold (<0.5 mL/kg/h) is correct in legacy, but (a) the 'DRC em TRS' gate uses vars(evolucao).fromkeys(...) which builds a dict keyed by field NAMES that can never equal 'DRC em TRS' (always [] -> falsy -> all([]) False, dead code) and is logically inverted vs the docstring's ABSENCE intent, and (b) the weight parse strips the decimal separator, inflating peso ~10x. Option B is the reference-correct, functional criterion.

**Disposition note.** RATIFY a functional KDIGO oliguria criterion: real 'DRC em TRS' diagnosis membership test with correct ABSENCE sense, decimal-preserving weight parse, and absence of noradrenaline (12h) / hemodialysis. Do NOT port the fromkeys dead-code gate (RULE-systemic-BE-03-001) nor the decimal-stripping peso parse. Preserve PT-BR vocabulary verbatim: 'DRC em TRS', diurese, qt_vol_espontanea/qt_vol_svd/qt_vol_cistostomia, diurna_terapia_hemo. Same diurese formula appears commented in trilha_profilaxia.py c8.

<a id="rat-eficiencia-03"></a>
### RAT-EFICIENCIA-03 — RULE-EFICIENCIA-005: Eficiencia v3 criterio_9 - coma without sedation (defined, unwired)

> GCS<13 implemented vs GCS<6 intended; sedative-absence uses an AND-combined filter (requires all sedatives present at once) rather than the intended OR/any across sedatives, so it almost never excludes.

**Question.** For Eficiencia v3 criterio_9 (coma without sedation -> suspected brain death / donor-potential), must the GCS threshold be the intended severe value (GCS<=5) and the sedative-absence test use OR/any across sedatives rather than the legacy GCS<13 with an AND-combined filter?

**Options.**

- **A** — Reproduce legacy verbatim: GCS<13 AND a single .filter() requiring ALL FIVE infusion sedatives simultaneously >0 (and both adep drugs >0) for the 'sedation present' test. *(risk: High if wired — GCS<13 labels many merely obtunded patients as brain-death suspects, and the AND-filter treats a patient on a single agent (e.g. propofol alone) as unsedated, so it could initiate donor-potential maintenance on a sedated/obtunded patient. Currently unwired (moderate live risk).)*
- **B** — Implement the intended trigger: GCS<=5 (GCS<6) not explained by sedation AND ABSENCE of ANY sedative (OR/any across cetamina/dexmedetomidina/propofol/tiopental/midazolam and adep fenitoina/fenobarbital) in the last 6h. *(risk: Low — matches OPO/NICE clinical triggers for brain-death evaluation / organ-donation referral; only genuinely comatose, unsedated patients are flagged.)*

**Recommended default.** B — NICE CG135 (Organ donation for transplantation) clinical trigger: GCS <=4 not explained by sedation (or intention to test brainstem death); GCS scale 3-15 (Teasdale & Jennett, Lancet 1974;2:81-84). The docstring intent (GCS<6, i.e. GCS<=5) matches this literature; the code's GCS<13 and AND-combined sedative filter are defects. Option B is reference-correct. Any deployment must remain gated behind clinical/organ-procurement review given the sensitivity of a brain-death-suspicion alert.

**Disposition note.** RATIFY the intended criterio_9: GCS<=5 (GCS<6) with an OR/any sedative-absence test across all agents over 6h. Do NOT port GCS<13 nor the AND-combined single-filter that requires all sedatives present at once. Rule is currently UNWIRED (calcular_criterio_9 commented out); ratification fixes the logic but wiring/enablement requires explicit clinical + organ-procurement governance. Preserve PT-BR: 'Suspeita de ME', qt_vol_cet/dex/pro/tiop/mid, adep fenitoina/fenobarbital.

<a id="rat-piora-clinica-08"></a>
### RAT-PIORA-CLINICA-08 — RULE-PIORA-CLINICA-010: Piora Clinica - Calculo do alerta (soma agregada + gatilho por criterio)

> *Cluster:* `piora-clinica` · *Category:* `alert-threshold` · *Extraction:* DISCREPANCY · *Verification:* DISCREPANCY  **What the legacy does.** Aggregates the 9 graded sub-scores (criterio_1..9) into a color alert. This is a MEWS/NEWS-style track-and-trigger: any single criterion at grade 2 (+/-) sets AMARELO and any at grade 3 (+/-) sets VERMELHO 

**Question.** For the Piora Clinica aggregate alert (calculo do alerta), must the track-and-trigger logic preserve the highest single-criterion severity (no downgrade), count every abnormal parameter in the aggregate (including sign), and use reachable aggregate bands per NEWS2/MEWS?

**Options.**

- **A** — Reproduce legacy verbatim: last-writer-wins overwrite of alerta/mensagem across criterio_1..9 (a later grade-2 can downgrade an earlier grade-3), soma using int(criterio[0]) (magnitude only, sign discarded), and soma bands 0-7/8-14/15-21 that only run when NO criterion reached grade 2/3 (so 15-21 is dead and only soma 8-9 reaches AMARELO). *(risk: High — a high-severity single parameter (VERMELHO) can be silently downgraded to AMARELO by a later lower-severity criterion, violating the core early-warning safety rule that a red-score parameter must always escalate.)*
- **B** — Implement NEWS2/MEWS-style two-tier logic: ANY single criterion at grade 3 forces VERMELHO regardless of aggregate (no overwrite/downgrade); ANY at grade 2 sets at least AMARELO; the aggregate sum (with every abnormal parameter contributing) drives graded bands, keeping the maximum severity across per-criterion and aggregate tiers. *(risk: Low — reproduces validated track-and-trigger escalation; a red-score parameter never downgraded, all abnormal parameters counted.)*

**Recommended default.** B — NEWS2 / MEWS track-and-trigger (Royal College of Physicians NEWS2, 2017; NICE MIB205): (a) ANY single parameter scoring 3 (red score) mandates urgent escalation regardless of aggregate, and (b) aggregate bands drive graded response. A high-severity single parameter must never be downgraded by others and every abnormal parameter must contribute to the aggregate. The legacy overwrite (last-writer-wins), magnitude-only sum, and unreachable 15-21 band all violate this. Option B is reference-correct.

**Disposition note.** RATIFY NEWS2/MEWS-correct aggregation: single-criterion grade-3 forces VERMELHO with no downgrade, grade-2 forces at least AMARELO, and the aggregate contributes every abnormal parameter with reachable bands. Do NOT port the last-writer-wins overwrite, the int(criterio[0]) sign-discarding sum, or the dead 15-21 sum band. Preserve PT-BR strings verbatim: 'Baixo/Moderado/Alto risco de piora clinica', NEUTRO/AMARELO/VERMELHO. Depends on corrected sub-scores incl. RULE-PIORA-CLINICA-006/007 (ESC-P0-004/005).

<a id="rat-ventilacao-06"></a>
### RAT-VENTILACAO-06 — RULE-VENTILACAO-011: Ventilation C8 - extubation-readiness bundle

> FiO2 treated as a FRACTION here (fio2 < 0.4), contrasting C2/C3 (RULE-VENTILACAO-004/005) which divide fio2 by 100 as a PERCENTAGE - FiO2 unit inconsistency within the same model.

**Question.** For Ventilation C8 (extubation-readiness bundle), must FiO2 be handled in one consistent unit (fraction) across the ventilacao model so the FiO2<0.4 readiness gate is not inconsistent with C2/C3 which treat FiO2 as a percentage (fio2/100)?

**Options.**

- **A** — Reproduce legacy verbatim: C8 tests fio2 < 0.4 as a FRACTION while C2/C3 (RULE-VENTILACAO-004/005) divide fio2 by 100 treating it as a PERCENTAGE within the same model. *(risk: High — inconsistent FiO2 units across criteria of one model; the same stored FiO2 value is interpreted differently, so either C8 or C2/C3 mis-evaluates the oxygenation gate and the readiness/mismatch flags become unreliable.)*
- **B** — Canonicalize FiO2 to a fraction 0.21-1.0 model-wide (via the shared P/F helper, ESC-P0-007), keep the C8 readiness thresholds (FiO2<=0.40, PEEP<=8, RR criterion, adequate oxygenation P/F, no/minimal vasopressors, adequate consciousness) per the international weaning consensus. *(risk: Low — one consistent FiO2 unit; C8 readiness gate matches the ERS/ATS weaning-screen criteria and is consistent with C2/C3.)*

**Recommended default.** B — Boles J-M et al., Eur Respir J 2007;29:1033-1056 (International Consensus Conference on weaning): readiness-to-wean/SBT screening uses FiO2 <=0.40 and PEEP <=8 cmH2O (FiO2 expressed as a fraction), adequate oxygenation (P/F >=150, some protocols >200), adequate consciousness, an RR criterion, and no/minimal vasopressors. C8's thresholds are correct; the defect is the FiO2 unit inconsistency vs C2/C3. Canonicalizing FiO2 to a fraction (Option B, aligned with ESC-P0-007) is reference-correct.

**Disposition note.** RATIFY C8 readiness thresholds with model-wide FiO2-as-fraction canonicalization; do NOT port the FiO2 unit inconsistency (C8 fraction <0.4 vs C2/C3 percentage /100). Resolve jointly with the shared P/F helper (RULE-CLINICAL-SCORING-008 / ESC-P0-007). Alert-forcing criterion (RULE-VENTILACAO-014). Preserve PT-BR: dias_vm, relacao_po2_fio2, noradrenalina.

<a id="rat-sepse-22"></a>
### RAT-SEPSE-22 — RULE-SEPSE-043: Sepsis C6 (major) - hypotension (PAS<90 or PAD<90 in 24h)

> DISCREPANCY: _REGRAS text says "PAS < 90 OU PAD < 60"; code compares PAD < 90 (not 60). _ANTIGAS_REGRAS also mentioned PAM<65. Test test_trilha_sepse.py:124-137 (pas=89 dominates).

**Question.** For Sepsis C6 major (hypotension), must the diastolic disjunct compare PAD < 60 (per _REGRAS and physiology) instead of the legacy PAD < 90?

**Options.**

- **A** — Reproduce legacy verbatim: fire if PAS < 90 OR PAD < 90 (within 24h). *(risk: High — a normal diastolic BP is ~60-80 mmHg, so PAD < 90 is satisfied by essentially every patient, making this MAJOR criterion nearly always True; it stops discriminating and pushes almost all patients toward the 2-major sepsis alert bar (false positives).)*
- **B** — Fire if PAS < 90 OR PAD < 60 (matching the _REGRAS specification and normal-diastolic physiology), retaining the 24h lookback for the diastolic value. *(risk: Low — restores specificity; the diastolic disjunct flags genuinely low diastolic pressure rather than every recorded value.)*
- **C** — Replace the diastolic disjunct entirely with a MAP-based hypotension trigger (MAP < 70 or MAP < 65) plus PAS < 90, per Sepsis-3/SSC and the _ANTIGAS_REGRAS PAM<65 note. *(risk: Low — diastolic BP is not a standard sepsis hypotension trigger; MAP<70 (Sepsis-3) or MAP<65 (SSC resuscitation target) is the guideline-canonical marker and would be the most reference-aligned choice, but changes the input from PAD to MAP.)*

**Recommended default.** B — Sepsis-3 / SSC 2021 (Singer et al., JAMA 2016;315(8):801-810; Evans et al. 2021): sepsis-related hypotension = SBP < 90 mmHg, MAP < 70 mmHg, or SBP drop > 40 mmHg from baseline; qSOFA uses SBP <=100. Diastolic BP is not a standard trigger, and when a low-diastolic threshold is used it is ~<60 mmHg (normal diastolic ~60-80). The legacy PAD < 90 is the documented DISCREPANCY vs _REGRAS ('PAS < 90 OU PAD < 60'). Option B restores the reference/spec-correct PAD < 60; Option C (MAP-based) is the most guideline-pure alternative if the platform captures MAP here.

**Disposition note.** RATIFY the diastolic threshold PAD < 60 (per _REGRAS) over the legacy PAD < 90 that renders C6 non-discriminating. Do NOT port PAD < 90. A committee may prefer the MAP-based trigger (MAP<70 Sepsis-3 / MAP<65 SSC, per _ANTIGAS_REGRAS PAM<65) as the most reference-canonical form (Option C) if MAP is available at this criterion. Preserve PT-BR: pas, pad_em_24hrs, PAM. Test test_trilha_sepse.py:124-137.


## P1 — moderate clinical impact (45 items)

<a id="rat-clinical-scoring-02"></a>
### RAT-CLINICAL-SCORING-02 — RULE-CLINICAL-SCORING-004: SOFA liver sub-score (bilirubin)

> *`clinical-scoring` · `clinical-scoring` · DISCREPANCY/DISCREPANCY*  - **Legacy:** SOFA organ-3 (liver) points from total bilirubin (mg/dL). - **Deviation:** DISCREPANCY vs standard SOFA (mg/dL): <1.2=0, 1.2-1.9=1, 2.0-5.9=2, 6.0-11.9=3, >=12=4. Implementation uses strict < at the upper bounds (1.9, 5.9, 11.9) instead of <=, creating dead gaps [1.9

**Question.** The legacy SOFA liver sub-score (total bilirubin, mg/dL) uses strict < at the upper band edges (1.9, 5.9, 11.9), creating dead gaps [1.9,2.0), [5.9,6.0), [11.9,12.0) that return None (no score). Should v2 close these gaps to the canonical inclusive SOFA bands?

**Options.**

- **A** — Adopt reference-correct inclusive bands per Vincent 1996 (<1.2=0; 1.2-1.9=1; 2.0-5.9=2; 6.0-11.9=3; >=12=4). *(risk: none - restores the validated standard scoring.)*
- **B** — Preserve the legacy strict-< bands verbatim. *(risk: bilirubin values in the gaps score None, undercounting total SOFA and delaying sepsis/mortality escalation.)*
- **C** — Retire the hepatic sub-score. *(risk: loses the liver organ-dysfunction dimension of SOFA.)*

**Recommended default.** A — SOFA is a validated ordinal score and the gap values are pure implementation artifacts of strict < with no clinical
justification. Adopting the canonical inclusive bands (Vincent JL et al., Intensive Care Med 1996) is unambiguous and
restores band continuity. Committee confirmation is required only because SOFA drives sepsis and mortality flags, so any
band change is clinically load-bearing.

<a id="rat-indicadores-etl-05"></a>
### RAT-INDICADORES-ETL-05 — RULE-INDICADORES-ETL-012: get_microindicadores — ICU micro-indicator boolean mapping, DVA mapped to a drug-specific 

> *`indicadores-etl` · `clinical-scoring` · AMBIGUOUS/DISCREPANCY*  - **Legacy:** If a micro_indicador record exists, builds a dict of ICU quality indicators: tempo_internacao (length of stay, passthrough), ventilacao_mecanica (VM=='S'), noradrenalina (DVA=='S'), sedacao (SEDACAO=='S'), hemodialise (HEMODIALISE=='S'), mortalidade_esperada (passthroug

**Question.** The ICU quality-indicator ETL (get_microindicadores) maps the generic source field DVA (droga vasoativa = any vasoactive drug) to an output key literally named "noradrenalina". Should v2 rename the indicator to a generic vasopressor label or keep the norepinephrine-specific key?

**Options.**

- **A** — Rename to a generic key (droga_vasoativa / uso_vasopressor) reflecting the DVA source semantics. *(risk: downstream dashboards keyed on "noradrenalina" must migrate; no bedside-alert impact.)*
- **B** — Keep the key "noradrenalina" but document that it means any vasoactive drug. *(risk: misleading label over-reports norepinephrine-specific use in ICU quality reporting.)*
- **C** — Split into drug-specific keys. *(risk: source carries only the binary DVA flag; disaggregation is impossible.)*

**Recommended default.** A — In standard Brazilian ICU terminology DVA = droga vasoativa, i.e. any vasoactive agent (noradrenalina, adrenalina,
vasopressina, dopamina, dobutamina, nitroprussiato...), so surfacing it as "noradrenalina" misrepresents the indicator.
This feeds ICU quality metrics rather than a bedside alert, so the fix is a naming/semantics decision for the data
owner, not a clinical-threshold change. Recommend the generic label with a downstream migration note.

<a id="rat-piora-clinica-06"></a>
### RAT-PIORA-CLINICA-06 — RULE-PIORA-CLINICA-008: Piora Clinica criterio_8 - SatO2 (paciente regular / nao-DPOC) (graded sub-score)

> *`piora-clinica` · `clinical-scoring` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Graded oxygen-saturation sub-score for a "regular" (non-COPD) patient. - **Clinical relevance:** Confirms the extraction DISCREPANCY. Two problems vs NEWS2 Scale 1: (1) sign inversion - a normal non-COPD saturation >96% yields a POSITIVE deterioration sub-score "2+" (la

**Question.** For non-COPD ("regular") patients the Piora Clinica SatO2 sub-score assigns a POSITIVE deterioration grade "2+" (labelled hiperoxia) to normal high saturations >96%, firing a false AMARELO. Should v2 align this sub- score with NEWS2 Scale 1 (SpO2 >=96% scores 0)?

**Options.**

- **A** — Adopt NEWS2 Scale 1 grading - penalize only low SpO2; normal/high saturation scores 0. *(risk: none; removes systematic false positives.)*
- **B** — Preserve the legacy hiperoxia penalty for SpO2 >96% in non-COPD patients. *(risk: false AMARELO on healthy oxygenation drives alert fatigue and erodes trust in the track-and-trigger.)*
- **C** — Retire the non-COPD SatO2 sub-score. *(risk: loses hypoxaemia detection in the aggregated deterioration score.)*

**Recommended default.** A — NEWS2 Scale 1 applies to patients without hypercapnic (type 2) respiratory failure risk; for them high SpO2 is not a
deterioration signal, so the "2+" hiperoxia band is a sign inversion. Aligning to NEWS2 Scale 1 removes the false
AMARELO on normal oxygenation while preserving low-SpO2 detection. Committee sign-off is required because it changes a
wired track-and-trigger sub-score that contributes to the aggregate color alert.

<a id="rat-piora-clinica-07"></a>
### RAT-PIORA-CLINICA-07 — RULE-PIORA-CLINICA-009: Piora Clinica criterio_9 - SatO2 (paciente DPOC/COPD) (graded sub-score)

> *`piora-clinica` · `clinical-scoring` · OK/DISCREPANCY*  - **Legacy:** Graded oxygen-saturation sub-score for a COPD (DPOC) patient, where high SpO2 is penalized (over-oxygenation risk). - **Clinical relevance:** Extraction status was OK (the design INTENT - penalizing high SpO2 in COPD, ==94 -> 1+, >94 -> 3+ "hiperoxia" - is verified against NEWS2

**Question.** The COPD (DPOC) SatO2 sub-score correctly penalizes over-oxygenation (intent verified against NEWS2 Scale 2), but its band edges diverge from Scale 2 and leave a dead gap 81-87% scoring 0 (sato2==94 -> 1+, >94 -> 3+, 91-93 -> 1-, 88-90 -> 2-, <=80 -> 3-). Should v2 adopt the exact NEWS2 Scale 2 bands?

**Options.**

- **A** — Adopt NEWS2 Scale 2 verbatim (<=83=3, 84-85=2, 86-87=1, 88-92=0, 93-94 on O2=1, 95-96=2, >=97=3). *(risk: none; closes the 81-87 gap and corrects both tails.)*
- **B** — Preserve the legacy COPD bands. *(risk: 81-87% (moderate hypoxaemia) scores 0 and misses deterioration; low- and high-end cutoffs deviate from guideline.)*
- **C** — Retire the COPD-specific scale and use a single SpO2 scale. *(risk: loses the clinically important over-oxygenation penalty for hypercapnic patients.)*

**Recommended default.** A — The design intent (penalize high SpO2 in COPD, target 88-92%) is verified correct against NEWS2 Scale 2 rationale; only
the numeric bands and the 81-87% coverage gap deviate. Adopting Scale 2 verbatim preserves the verified intent while
fixing the low-end grading and the dead zone. Committee confirmation is required because it retunes a wired sub-score
for the distinct DPOC population.

<a id="rat-sepse-02"></a>
### RAT-SEPSE-02 — RULE-SEPSE-002: SEPSE v3 alert maiores/menores (OR thresholds) + risk message

> *`sepse` · `clinical-scoring` · DISCREPANCY/DISCREPANCY*  - **Legacy:** SEPSE v3 alert from 11 major (criterio_1..11) and 9 minor (criterio_12..20) criteria; VERMELHO when either major>=3 OR minor>=4; AMARELO when major>=2 OR minor>=3. Also emits a risk message. - **Deviation:** v1 (RULE-SEPSE-001) requires maiores AND menores (>=3 AND >=4 -> VERME

**Question.** SEPSE v3 combines its 11 maiores and 9 menores criteria with OR (VERMELHO if maiores>=3 OR menores>=4; AMARELO if maiores>=2 OR menores>=3), whereas v1 used AND (maiores AND menores). Which aggregation logic should the v2 sepsis alert adopt?

**Options.**

- **A** — Adopt v3 OR aggregation. *(risk: higher sensitivity, more alerts / lower PPV; note menores>=4 is currently unreachable via ESC-P1-020.)*
- **B** — Adopt v1 AND aggregation (maiores AND menores). *(risk: lower sensitivity; may miss severe single-axis presentations.)*
- **C** — Retune thresholds with the committee (hybrid). *(risk: requires fresh PPV validation before deployment.)*

**Recommended default.** A — OR aggregation favours sensitivity, which suits a sepsis safety-net, but it materially changes alert volume and PPV
versus the v1 AND logic, making this a clinical/operational trade-off for the committee. There is a hard dependency:
RULE-SEPSE-037 (ESC-P1-020) leaves the menores==4 branch unreachable, so effective firing is driven by maiores; the two
must be ratified together. Recommend v3 OR paired with an explicit PPV budget review.

<a id="rat-sepse-20"></a>
### RAT-SEPSE-20 — RULE-SEPSE-032: Sepse criterio_6 - Oliguria (sonda) ou dessaturacao

> *`sepse` · `clinical-scoring` · OK/DISCREPANCY*  - **Legacy:** Major criterion 6 fires if the last fluid-output was catheter diuresis (diurese_sonda) with volume <= 100 recorded within the last 2 hours, OR patient on O2 support with SpO2 < 96%. - **Clinical relevance:** Oliguria branch_A diverges from the KDIGO/SSC definition on THREE audited dimen

**Question.** Sepse major criterio_6 fires oliguria as a fixed absolute diurese_sonda volume <=100 mL within the last 2h (plus an O2-support + SpO2<96% branch), diverging from the KDIGO/SSC weight- and time-normalized oliguria definition (<0.5 mL/kg/h over >=2h). Should v2 replace the fixed cutoff with the guideline definition?

**Options.**

- **A** — Adopt KDIGO/SSC weight-normalized oliguria (<0.5 mL/kg/h for >=2h) and set the desaturation branch to a NEWS2 target (SpO2 94-98%). *(risk: needs reliable weight and timed urine output; more inputs.)*
- **B** — Preserve the fixed <=100 mL / 2h absolute cutoff. *(risk: not body-weight adjusted; a null volume defaults to 0<=100 (spurious fire) and misclassifies across body sizes.)*
- **C** — Keep the absolute cutoff but fix only the null-default and recency bugs. *(risk: retains a non-standard, weight-agnostic threshold.)*

**Recommended default.** A — The fixed 100 mL rule is neither weight- nor rate-normalized, and the null-default plus the timedelta.seconds recency
bug can spuriously satisfy it for stale records. KDIGO AKI 2012 and SSC define oliguria as <0.5 mL/kg/h for >=2
consecutive hours, and NEWS2 sets the SpO2 target at 94-98%. Because this is a wired major sepsis criterion, retuning it
requires committee ratification and confirmation that patient weight and timed urine output are available.

<a id="rat-sepse-21"></a>
### RAT-SEPSE-21 — RULE-SEPSE-033: Sepse criterio_7 - Variacao do nivel de consciencia

> *`sepse` · `clinical-scoring` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Major criterion 7 compares previous vs current consciousness level via a numeric severity hierarchy and returns True when the PREVIOUS severity rank is greater than the current rank. - **Deviation:** DISCREPANCY: In hierarquia_consciencia higher number = worse (coma=6, acordado

**Question.** Sepse major criterio_7 returns True when the PREVIOUS consciousness severity rank is greater than the CURRENT one (previous worse than now, i.e. improvement), which is inverted versus the documented intent to detect worsening. Should v2 flip the comparison to fire on deterioration?

**Options.**

- **A** — Fire when current severity rank > previous (deterioration). *(risk: none; matches the clinical intent of the criterion.)*
- **B** — Preserve the legacy comparison (anterior > atual). *(risk: criterion fires on improvement and misses true deterioration - a safety-relevant inversion.)*
- **C** — Retire criterio_7. *(risk: loses the acute-encephalopathy axis of sepsis screening.)*

**Recommended default.** A — In hierarquia_consciencia a higher number is worse (coma=6, acordado=1), so returning previous>current fires when the
patient has improved - the opposite of the intended "variacao para pior". Correcting the comparison to current>previous
restores deterioration detection. Committee sign-off is required because it is a wired major criterion and the inversion
is safety-relevant.

<a id="rat-sepse-02"></a>
### RAT-SEPSE-02 — RULE-SEPSE-037: Sepse criterio_11 - Placeholder (sempre False)

> *`sepse` · `clinical-scoring` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Minor criterion 11 is hard-coded to always return False (unimplemented placeholder). - **Deviation:** DISCREPANCY/consequence: because criterio_11 is always False, the "menores" group (c8,c9,c10,c11) can hold at most 3 True values, so the alert condition `menores == 4` in RULE-

**Question.** Sepse minor criterio_11 is hard-coded to always return False, so the menores group (c8-c11) can reach at most 3 True and the alert branch menores==4 is unreachable. Should v2 implement criterio_11 or restructure the menores threshold?

**Options.**

- **A** — Implement criterio_11 per its intended clinical definition so menores==4 becomes reachable. *(risk: requires defining and validating the missing criterion.)*
- **B** — Lower the menores firing threshold to match the 3 implementable minors. *(risk: changes alert sensitivity; requires PPV revalidation.)*
- **C** — Preserve the always-False placeholder. *(risk: dead alert path; the menores axis under-counts by one, silently reducing sensitivity.)*

**Recommended default.** A — An always-False placeholder silently disables the menores==4 escalation, an unintended consequence rather than a
deliberate design choice. The committee must decide whether to supply the missing criterion (restoring the intended
4-of-4 semantics) or retune the threshold to the criteria that actually exist. This interacts directly with the v3 OR
aggregation (ESC-P1-017) and must be resolved jointly.

<a id="rat-sedacao-02"></a>
### RAT-SEDACAO-02 — RULE-SEDACAO-009: Sedacao v3 criterio_5 - no morning sedation reduction (>=1/2)

> *`sedacao` · `drug-dosing` · AMBIGUOUS/DISCREPANCY*  - **Legacy:** Sedative present at the latest balance AND no reduction of at least half between the 06:00 and 10:00 balances (for midazolam/propofol/cetamina/dexmedetomidina). Wired AMARELO criterion. - **Clinical relevance:** WIRED AMARELO criterion (calcular_alerta_v2 amarelo=[criterio_5, criter

**Question.** Wired AMARELO criterio_5 fires when a sedative is present at the latest balance AND there was no reduction of at least half between the 06:00 and 10:00 balances (midazolam/propofol/cetamina/dexmedetomidina). Should v2 ratify this daily sedation-reduction logic and its fixed 06:00->10:00 window?

**Options.**

- **A** — Ratify the >=50% morning-reduction rule with the fixed 06:00->10:00 comparison. *(risk: a rigid clock window may miss units whose sedation-hold schedule differs.)*
- **B** — Generalize to a daily sedation-interruption/reduction check independent of fixed clock times. *(risk: needs a defined reference balance pair to compare against.)*
- **C** — Retire the criterion. *(risk: loses an oversedation / daily-awakening stewardship prompt.)*

**Recommended default.** B — The clinical concept (daily sedation reduction / spontaneous awakening for ventilated patients, PADIS-aligned) is sound,
but hard-coding 06:00 and 10:00 assumes a single nursing schedule and the AMBIGUOUS status reflects unclear balance-pair
selection. The committee should confirm the target reduction fraction (>=50%) and the window policy. Recommend
generalizing the window while preserving the >=50% reduction intent, since it is a wired AMARELO criterion.

<a id="rat-balanco-hidrico-03"></a>
### RAT-BALANCO-HIDRICO-03 — RULE-BALANCO-HIDRICO-006: 24h fluid balance = intake minus output over the 07:00-07:00 nursing day

> *`balanco-hidrico` · `physiological-calculation` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Net fluid balance (balanco hidrico) for an attendance over the 07:00-07:00 nursing day, computed as total Entrada intake minus total Saida output. Unlike the other helpers, missing sums default to 0 (not None), so this always returns a number. - **Deviation:*

**Question.** The 24h balanco hidrico (intake minus output) over the 07:00-07:00 nursing day is computed with a defective window (month-agnostic __day filter, an unsatisfiable second-queryset branch, and a 0-sum coerced to None). Should v2 ratify a corrected 07:00-07:00 windowing that preserves the nursing-day semantics?

**Options.**

- **A** — Adopt a timezone-aware 07:00->07:00 window (fixing month boundaries and the dead qs2 branch); keep balance = intake - output with 0 as a real value. *(risk: none clinical; totals change only where the old window mis-bucketed records.)*
- **B** — Preserve the legacy window verbatim. *(risk: month-boundary days drop records and net-zero balance is silently None, breaking downstream displays.)*
- **C** — Redefine the nursing day (e.g., calendar midnight). *(risk: departs from the established ICU 07:00 handover convention.)*

**Recommended default.** A — The 07:00-07:00 nursing-day intent is clinically correct; only the windowing mechanism is buggy (the shared BE-09
defect), so this is an ADAPT-style correction that preserves clinical semantics. Because net balance drives fluid-
management decisions, the committee must ratify the day-boundary definition and the 0-vs-None convention. Recommend the
corrected window with 0 treated as a valid balance value.

<a id="rat-balanco-hidrico-04"></a>
### RAT-BALANCO-HIDRICO-04 — RULE-BALANCO-HIDRICO-007: Ganhos (fluid intake) summed over the 07:00-07:00 nursing day

> *`balanco-hidrico` · `physiological-calculation` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Sum of all fluid-intake quantities (Entrada.quantidade, no type filter) for an attendance over the 07:00-07:00 nursing day. - **Deviation:** Same 07:00-07:00 window defect as RULE-BALANCO-HIDRICO-006: month-agnostic __day; else-branch qs2 unsatisfiable; 0-sum

**Question.** Ganhos (total fluid intake = Sum of Entrada.quantidade, no type filter) over the 07:00-07:00 nursing day shares the same defective window as the 24h balance (month-agnostic day, dead qs2 branch, 0-sum coerced to None). Should v2 ratify the corrected windowing while keeping the unfiltered intake sum?

**Options.**

- **A** — Adopt the corrected 07:00->07:00 window; keep Ganhos = Sum(Entrada. quantidade) unfiltered, with 0 as a real value. *(risk: none clinical; only mis-bucketed records change.)*
- **B** — Preserve the legacy window. *(risk: month-boundary intake is dropped and a genuine zero is reported as None in the balance numerator.)*
- **C** — Add a type filter to Entrada before summing. *(risk: could exclude legitimate intake sources not currently typed.)*

**Recommended default.** A — Ganhos is the intake numerator of the fluid balance and shares the same 07:00-07:00 window defect; the intent (sum all
Entrada over the nursing day) is correct. Correcting the window preserves clinical semantics while fixing month
boundaries and the None coercion. Committee ratification is warranted because intake feeds the wired balance used in
resuscitation decisions; recommend keeping the unfiltered Entrada sum.

<a id="rat-balanco-hidrico-05"></a>
### RAT-BALANCO-HIDRICO-05 — RULE-BALANCO-HIDRICO-008: Diureses (urine output) summed over the 07:00-07:00 nursing day

> *`balanco-hidrico` · `physiological-calculation` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Sum of urine-output quantities (Saida with tipo in {diurese_espontanea, diurese_sonda}) for an attendance over the 07:00-07:00 nursing day, using the same two-queryset window construction as evacuacoes. - **Deviation:** Same window defect as RULE-BALANCO-HIDR

**Question.** Diureses (urine output = Sum of Saida with tipo in {diurese_espontanea, diurese_sonda}) over the 07:00-07:00 nursing day uses the same defective two-queryset window. Should v2 ratify the corrected windowing and the two urine tipos included?

**Options.**

- **A** — Adopt the corrected 07:00->07:00 window; keep tipo in {diurese_espontanea, diurese_sonda}, with 0 as a real value. *(risk: none clinical; only mis-bucketed records change.)*
- **B** — Preserve the legacy window. *(risk: urine totals drop records at month boundaries and report None on a true zero, corrupting oliguria assessment.)*
- **C** — Broaden or narrow the set of urine tipos. *(risk: changes what counts as urine output; needs clinical definition.)*

**Recommended default.** A — Diureses is the urine-output measure feeding oliguria/AKI assessment and shares the same window defect; the two included
tipos (spontaneous and catheter diuresis) are clinically appropriate. Correcting the window preserves semantics while
fixing the boundary and None-coercion bugs. Committee ratification is required because urine output is clinically load-
bearing; recommend the corrected window with the existing two tipos.

<a id="rat-balanco-hidrico-06"></a>
### RAT-BALANCO-HIDRICO-06 — RULE-BALANCO-HIDRICO-010: Maximum temperature over the 07:00-07:00 nursing day

> *`balanco-hidrico` · `physiological-calculation` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Highest recorded body temperature (SinaisVitais.temperatura) for an attendance over the 07:00-07:00 nursing day. Takes the MAX of the per-window maxima. - **Deviation:** Same window defect as RULE-BALANCO-HIDRICO-006, but aggregate is Max not Sum: valores=[Ma

**Question.** Maximum body temperature over the 07:00-07:00 nursing day takes the MAX of per-window maxima using the same defective window construction. Should v2 ratify a corrected windowing that preserves the MAX aggregate?

**Options.**

- **A** — Adopt the corrected 07:00->07:00 window; keep Max(temperatura) with None-stripping. *(risk: none clinical; only mis-bucketed records change.)*
- **B** — Preserve the legacy window. *(risk: a peak temperature at a month boundary can be dropped, under-reporting fever.)*
- **C** — Change the aggregate (e.g., last value instead of max). *(risk: max is the clinically meaningful fever signal; a change loses it.)*

**Recommended default.** A — Unlike the fluid helpers this aggregate is a Max (peak fever), but it shares the identical 07:00-07:00 window defect.
Correcting the window preserves the MAX semantics while ensuring boundary- spanning peaks are not dropped. Committee
ratification is warranted because the daily temperature maximum feeds fever-based deterioration signals; recommend the
corrected window with the MAX aggregate retained.

<a id="rat-balanco-hidrico-08"></a>
### RAT-BALANCO-HIDRICO-08 — RULE-BALANCO-HIDRICO-013: Fluid-balance visao-geral 2-hour time-bucketing (08:00-start day, view facade + utils impl

> *`balanco-hidrico` · `physiological-calculation` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Builds the fluid-balance overview grid: for each distinct item name (nome) in a balanco, sum quantidade into twelve fixed 2-hour buckets. Bucket labels/edges start at 08:00 and wrap through 06:00-08:00, using America/Sao_Paulo local time. - **Deviation:** Buc

**Question.** The fluid-balance overview grid buckets quantities into twelve fixed 2-hour buckets starting at 08:00 (America/Sao_Paulo), but the [22:00,00:00] bucket becomes SQL BETWEEN 22:00:00 and 00:00:00 (a degenerate/empty range) so late-night entries are lost; the 08:00 anchor also differs from the 07:00-07:00 balance day. Should v2 ratify a corrected bucketing?

**Options.**

- **A** — Adopt corrected 2h buckets with a proper wrap of the 22:00-24:00 window, and confirm the 08:00 start + Sao_Paulo timezone. *(risk: none clinical; recovers currently-dropped late-night entries.)*
- **B** — Preserve the legacy bucketing. *(risk: 22:00-00:00 entries are silently excluded from the overview grid, under-displaying intake/output.)*
- **C** — Re-anchor the grid to the 07:00 nursing day to match the balance. *(risk: aligns display with the balance but changes long-standing bucket labels clinicians read.)*

**Recommended default.** A — The bucketing is a display grid, but the [22:00,00:00] BETWEEN range is a genuine defect that drops real late-night
entries. Correcting the wrap recovers those entries with no change to clinical semantics. The 08:00 grid anchor versus
the 07:00 balance day is a separate consistency question the committee should confirm; recommend fixing the wrap first
and keeping the 08:00 anchor unless the committee re-aligns it.

<a id="rat-balanco-hidrico-09"></a>
### RAT-BALANCO-HIDRICO-09 — RULE-BALANCO-HIDRICO-016: tempo_criacao - horas desde a criacao (shared helper)

> *`balanco-hidrico` · `physiological-calculation` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Hours elapsed since a record (Entrada/Saida/SinaisVitais) was created, used as the recency window guard in sepsis criteria. - **Deviation:** Uses timedelta.seconds (the seconds-within-a-day component, 0..86399) instead of total_seconds(); for any record older

**Question.** The shared helper tempo_criacao (hours since a record was created, used as the recency window guard in sepsis criteria) uses timedelta.seconds (0..86399, intra-day only) instead of total_seconds(), so any record older than 24h drops the day component and can spuriously pass "< N hours" checks. Should v2 ratify the total_seconds() correction?

**Options.**

- **A** — Adopt total_seconds() so recency windows are correct for records >24h old. *(risk: none; stale records stop spuriously satisfying recency gates in wired sepsis criteria.)*
- **B** — Preserve the legacy timedelta.seconds behavior. *(risk: records older than 24h can satisfy short recency windows (e.g., the 2h oliguria gate), firing on stale data.)*
- **C** — Remove the recency guard entirely. *(risk: criteria would ignore data staleness altogether.)*

**Recommended default.** A — This is a pure mechanism bug with cross-cutting impact: the helper gates recency in wired sepsis criteria (e.g.,
criterio_6's 2h window). Because the fix changes whether stale records satisfy recency gates in firing alerts, committee
ratification is warranted despite the change being a one-line primitive swap. total_seconds() is the unambiguous correct
elapsed-time primitive.

<a id="rat-estabilidade-01"></a>
### RAT-ESTABILIDADE-01 — RULE-ESTABILIDADE-001: Estabilidade v3 criterio_5 - vasopressor with negative cumulative fluid balance

> *`estabilidade` · `physiological-calculation` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Intended: noradrenaline started in last 6h AND cumulative fluid balance < -2000ml AND no >=500ml Ringer/saline bolus in last 4h. The code diverges substantially from this documented intent. Criterion is defined but UNWIRED (calcular_criterios does not call it). 

**Question.** Estabilidade criterio_5 (intended: noradrenaline started in last 6h AND cumulative fluid balance < -2000 mL AND no >=500 mL Ringer/saline bolus in last 4h) diverges substantially from its own docstring and is defined but UNWIRED. Should v2 implement the intended logic and wire it, or retire it?

**Options.**

- **A** — Implement the intended clinical predicate and wire the criterion. *(risk: requires ratifying the exact predicate and the ml/h vs mcg/kg/min dosing convention.)*
- **B** — Preserve the criterion as-is (unwired, inert). *(risk: no effect; a documented but non-functional safety concept.)*
- **C** — Retire the criterion. *(risk: loses the vasopressor-with-negative-balance under-resuscitation flag.)*

**Recommended default.** A — The intent - flag a vasopressor-dependent patient with a large negative fluid balance who has not received a recent
volume bolus - is clinically reasonable and consistent with SSC fluid-responsiveness thinking. The code deviates from
its docstring and never runs, so the committee must ratify the canonical predicate before wiring. The noradrenaline
dosing units (ml/h vs mcg/kg/min) must be resolved jointly with the estabilidade dosing decision (ESC-P0-006,
ESC-P1-032/033/034).

<a id="rat-indicadores-etl-03"></a>
### RAT-INDICADORES-ETL-03 — RULE-INDICADORES-ETL-004: Sedation-use indicator representation (assistenciais vs controle-infeccao)

> *`indicadores-etl` · `physiological-calculation` · DISCREPANCY/DISCREPANCY*  - **Legacy:** The two indicator viewsets present sedation differently. The assistance view plots taxa_uso_sedacao * 100 (a rate as percentage, labeled "Tx. sedacao"). The infection-control view plots the raw dias_sedacao field (days) under the same label "Tx. sedacao". - *

**Question.** The two indicator viewsets display sedation inconsistently under the same label "Tx. sedacao": the assistance view plots taxa_uso_sedacao * 100 (a rate as percentage) while the infection-control view plots the raw dias_sedacao field (days). Which representation should v2 standardize on?

**Options.**

- **A** — Standardize on the rate (taxa_uso_sedacao * 100, %) in both views. *(risk: infection-control view loses the absolute days-of-sedation figure.)*
- **B** — Standardize on days (dias_sedacao) in both views. *(risk: assistance view loses the normalized rate used for benchmarking.)*
- **C** — Keep both metrics but give them distinct, correct labels (e.g., "Tx. uso sedacao %" vs "Dias de sedacao"). *(risk: two labels to maintain, but each metric stays interpretable; no information lost.)*

**Recommended default.** C — Applying the same "Tx. sedacao" label to a percentage rate and to a raw day-count is a reporting-integrity defect, not a
clinical-threshold error. Both are legitimate ICU quality indicators serving different audiences (assistance vs
infection control). Recommend keeping both with distinct labels so neither signal is lost; this is a data-
owner/reporting decision with no bedside-alert impact.

<a id="rat-eficiencia-04"></a>
### RAT-EFICIENCIA-04 — RULE-EFICIENCIA-006: Eficiencia v3 criterio_10 - mechanical restraint without agitation (AMARELO, wired)

> *`eficiencia` · `alert-threshold` · AMBIGUOUS/DISCREPANCY*  - **Legacy:** Mechanical restraint prescribed AND GCS>12 AND (per docstring) absence of RASS>+1 AND absence of delirium. Code requires delirium PRESENT (truthy) and RASS not > 1. Feeds the AMARELO alert. - **Deviation:** Delirium clause checks presence of delirium, opposite of the document

**Question.** Wired AMARELO criterio_10 (mechanical restraint without agitation) checks for delirium PRESENT and RASS not > +1, but the docstring intends ABSENCE of delirium and absence of RASS > +1. Should v2 flip the delirium clause to match the documented intent?

**Options.**

- **A** — Correct to ABSENCE of delirium (flag restraint on a non-agitated, non- delirious patient = potential over-restraint). *(risk: none; restores the intended over-restraint safety flag.)*
- **B** — Preserve the legacy clause (delirium presence required). *(risk: fires only when delirium is present - the opposite population - so it never flags unjustified restraint.)*
- **C** — Retire the criterion. *(risk: loses the restraint-appropriateness quality/safety prompt.)*

**Recommended default.** A — The clinical intent is to flag physical restraint of a patient who is NOT agitated or delirious (ausencia de delirium),
an over-restraint quality and safety concern. The code inverts the delirium clause so it fires only when delirium is
present, targeting the wrong population. Correcting the clause restores intent; committee sign-off is required because
it is a wired AMARELO alert.

<a id="rat-estabilidade-02"></a>
### RAT-ESTABILIDADE-02 — RULE-ESTABILIDADE-005: Estabilidade v3 criterio_3 - lactate elevation with sepsis therapy

> *`estabilidade` · `alert-threshold` · AMBIGUOUS/DISCREPANCY*  - **Legacy:** Lactate >= 2 mmol/L AND antibiotic prescribed AND noradrenaline present in last 4h AND no mechanical ventilation in last 24h. The docstring documents ABSENCE of noradrenaline but the code checks PRESENCE. Defined but UNWIRED. - **Deviation:** Code checks noradrenaline PRESE

**Question.** Estabilidade criterio_3 (lactate >= 2 mmol/L AND antibiotic prescribed AND no mechanical ventilation in last 24h) checks noradrenaline PRESENCE, but its docstring documents ABSENCE of noradrenaline; the criterion is defined but UNWIRED. Which polarity should v2 adopt, and should it be wired?

**Options.**

- **A** — Adopt ABSENCE-of-noradrenaline (flag hyperlactatemia + sepsis therapy in a patient not yet on vasopressors) and wire it. *(risk: requires ratifying polarity and the ml/h dosing convention before enabling.)*
- **B** — Adopt the PRESENCE-of-noradrenaline logic as currently coded. *(risk: targets patients already on vasopressors, missing the earlier- escalation window the docstring intends.)*
- **C** — Retire the criterion. *(risk: loses an early septic-shock escalation prompt.)*

**Recommended default.** A — The docstring intent (elevated lactate with antibiotic but no vasopressor yet started) targets early septic shock before
vasopressor initiation, consistent with SSC hour-1 bundle timing. The code's presence check inverts this. Because the
criterion is unwired, the committee must ratify polarity and the ml/h dosing convention before enabling it. Recommend
the docstring (absence) form.

<a id="rat-estabilidade-03"></a>
### RAT-ESTABILIDADE-03 — RULE-ESTABILIDADE-007: Estabilidade v3 criterio_7 - high-dose noradrenaline without adjuncts (VERMELHO, wired)

> *`estabilidade` · `alert-threshold` · OK/DISCREPANCY*  - **Legacy:** Noradrenaline > 20ml/h in last 4h AND (no vasopressin recorded in balanco OR no hydrocortisone prescribed). WIRED (contributes to VERMELHO alert). - **Clinical relevance:** The CLINICAL CONCEPT (add vasopressin and/or hydrocortisone as adjuncts in high-dose vasopressor septic shoc

**Question.** Wired VERMELHO criterio_7 fires when noradrenaline > 20 ml/h in last 4h AND (no vasopressin recorded OR no hydrocortisone prescribed). The concept is guideline-concordant but the dose trigger is an infusion volume (ml/h), not weight-based mcg/kg/min. Should v2 ratify the ml/h threshold or convert to standard dosing units?

**Options.**

- **A** — Convert to weight-based mcg/kg/min (SSC adjunct-therapy range), requiring pump concentration + patient weight. *(risk: needs concentration and weight that the legacy system did not capture; data-capture change required.)*
- **B** — Ratify the legacy > 20 ml/h volume threshold as an institution- specific proxy, pending confirmation of the standard noradrenaline concentration. *(risk: valid only for the assumed infusion concentration; ambiguous if concentrations vary between units.)*
- **C** — Retire the criterion. *(risk: loses the high-dose-vasopressor-without-adjuncts VERMELHO flag.)*

**Recommended default.** B — The clinical concept - add vasopressin and/or hydrocortisone as adjuncts in high-dose vasopressor septic shock and flag
when either is absent - is verified consistent with SSC-2021. The only defect is units: ml/h is not convertible to
mcg/kg/min without pump concentration and patient weight, which the legacy system did not store. Committee must ratify
the institutional noradrenaline concentration that makes > 20 ml/h meaningful (or mandate mcg/kg/min capture); this
threshold recurs across estabilidade (ESC-P1-033/034/035, ESC-P0-006) and must be resolved consistently.

<a id="rat-estabilidade-04"></a>
### RAT-ESTABILIDADE-04 — RULE-ESTABILIDADE-008: Estabilidade v3 criterio_8 - refractory shock triple therapy

> *`estabilidade` · `alert-threshold` · OK/DISCREPANCY*  - **Legacy:** Noradrenaline > 70ml/h AND vasopressin > 5ml/h in last 4h AND absence of adrenaline in last 4h. Defined but UNWIRED. - **Clinical relevance:** Concept matches SSC-2021 escalation ladder (epinephrine as third agent for refractory shock on NE+vasopressin, gated by absence of adrenal

**Question.** Estabilidade criterio_8 (noradrenaline > 70 ml/h AND vasopressin > 5 ml/h in the SAME record in last 4h AND absence of adrenaline) encodes the SSC refractory-shock escalation (add epinephrine on NE + vasopressin) but uses ml/h dosing and is UNWIRED. Should v2 ratify the thresholds/units and wire it?

**Options.**

- **A** — Implement with weight-based mcg/kg/min thresholds and decouple the same-record AND requirement, then wire. *(risk: requires concentration + weight capture and threshold re-derivation.)*
- **B** — Ratify the legacy ml/h thresholds (> 70 nora, > 5 vaso) as institutional proxies and wire. *(risk: depends on the assumed infusion concentration; the same-record coupling may miss separately-charted infusions.)*
- **C** — Keep the criterion unwired. *(risk: refractory-shock triple-therapy escalation never surfaces.)*

**Recommended default.** B — The concept matches SSC-2021 (epinephrine as the third agent when MAP is inadequate on norepinephrine + vasopressin),
verified correct in the catalog. The ml/h thresholds depend on the institutional infusion concentration and are not
guideline numbers, and the same-record AND coupling (nora>70 AND vaso>5 co-occurring) is a modelling choice. The
committee must ratify the concentrations/units alongside criterio_7 and wire the criterion.

<a id="rat-estabilidade-05"></a>
### RAT-ESTABILIDADE-05 — RULE-ESTABILIDADE-009: Estabilidade v3 criterio_9 - dobutamine with high-dose noradrenaline

> *`estabilidade` · `alert-threshold` · OK/DISCREPANCY*  - **Legacy:** Noradrenaline > 50ml/h AND dobutamine > 10ml/h in last 4h. Defined but UNWIRED. - **Clinical relevance:** Two divergences from the paired facade recommendation (RULE-016 criterio_9): (1) the displayed advice is conditioned on FC >130 bpm (physiologically sound — suspend dobutamine

**Question.** Estabilidade criterio_9 (noradrenaline > 50 ml/h AND dobutamine > 10 ml/h in the SAME record, last 4h) is UNWIRED and diverges from its paired facade text, which conditions the recommendation on FC > 130 bpm (suspend dobutamine when tachycardia impairs filling). Should v2 add the tachycardia gate and reconcile dosing units?

**Options.**

- **A** — Implement with mcg/kg/min thresholds plus the FC > 130 bpm condition from the facade, and wire. *(risk: needs concentration + weight and confirmation of the FC gate.)*
- **B** — Ratify the legacy ml/h thresholds without the FC gate and wire. *(risk: predicate omits the physiologically-sound tachycardia condition shown in the clinician advice.)*
- **C** — Retire the criterion. *(risk: loses the dobutamine-with-high-dose-vasopressor prompt.)*

**Recommended default.** A — SSC-2021 supports adding dobutamine for septic cardiac dysfunction, and the facade's FC > 130 note is physiologically
sound (tachycardia shortens diastolic filling and can reduce cardiac output). The predicate omits the tachycardia
condition present in the displayed advice - an intent/implementation split - and uses non-standard ml/h units. The
committee must reconcile the FC gate and the dosing units before wiring, resolving units jointly with criterio_7 and
criterio_8.

<a id="rat-estabilidade-07"></a>
### RAT-ESTABILIDADE-07 — RULE-ESTABILIDADE-015: Estabilidade facade alert-text - perfusion/shock triggers & bicarbonate (criteria 1-6, 11)

> *`estabilidade` · `alert-threshold` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Recommendation / alert-text catalog (get_payload_trilha_estabilidade) rendered by the v3 model's get_detalhe for fired criteria. This capture covers the numeric-threshold criteria 1-6 (myocardiopathy/perfusion, out-of-protocol noradrenaline, occult shock, septic shock in 

**Question.** The estabilidade facade alert-text catalog (get_payload_trilha_estabilidade) renders clinician-facing recommendations for the numeric-threshold criteria 1-6 and 11 (myocardiopathy/perfusion, out-of-protocol noradrenaline, occult shock, septic shock in spontaneous ventilation, negative fluid balance, bicarbonate). Should v2 ratify this text and bind its thresholds to the reconciled v3 predicate code?

**Options.**

- **A** — Ratify the facade recommendation text and align its embedded thresholds to the corrected v3 predicates (single source of truth). *(risk: requires the estabilidade dosing-unit and bicarbonate-pH decisions to be settled first.)*
- **B** — Keep facade text and predicate code independent, as in legacy. *(risk: displayed thresholds drift from the thresholds that actually fire the alert, misleading clinicians.)*
- **C** — Retire the facade recommendation text. *(risk: alerts fire without actionable bedside guidance.)*

**Recommended default.** A — The facade renders the clinician-facing recommendation whose embedded thresholds (dosing, negative fluid balance,
bicarbonate pH) must match the predicates that actually fire the alert; legacy lets them drift. Binding the wording to a
single reconciled source prevents the displayed-vs- firing mismatch. This is the text counterpart of the estabilidade
dosing-unit and bicarbonate decisions (ESC-P0-006, ESC-P1-032/033/034, RULE-ESTABILIDADE-011), so it must be ratified
together with them.

<a id="rat-sepse-06"></a>
### RAT-SEPSE-06 — RULE-SEPSE-007: SEPSE v3 criterio_1 - fever without vasopressor

> *`sepse` · `alert-threshold` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Intended - absence of noradrenaline (6h) AND temperature > 38.2C in last 24h. - **Deviation:** DISCREPANCY - docstring specifies "ausencia de noradrenalina" but code omits the negation (uses qt_vol_nora__gt=0 presence). Temperature threshold 38.2C strict >. - **Clinical relevanc

**Question.** criterio_1 intends: ausencia de noradrenalina in the last 6h AND temperature > 38.2C in the last 24h.
The code omits the negation (uses qt_vol_nora__gt=0, i.e. PRESENCE) and applies a strict temperature
threshold of > 38.2C. Do we ratify the docstring-correct absence-of-noradrenaline gate together with
the 38.2C fever cutoff?

**Options.**

- **A** — Ratify docstring intent: ausencia de noradrenalina (6h) AND temperatura > 38.2C (24h)
- **B** — Preserve legacy code: noradrenaline PRESENCE (6h) AND temperatura > 38.2C (24h)
- **C** — Ratify the absence gate but revisit the 38.2C cutoff versus the >= 38.0/38.3C fever conventions

**Recommended default.** A — RATIFY: this is the recurring v3-sepsis inversion pattern — the docstring guards on ABSENCE of
noradrenaline (the criterion targets a not-yet-in-shock patient whose fever is an early sepsis flag),
but the code checks PRESENCE, which would only fire once vasopressors are already running and defeats
the early-screening intent. The negation must be restored. The 38.2C threshold is non-standard versus
common 38.0C/38.3C fever definitions, so option C's cutoff review is worth flagging, but neither the
inversion fix nor any cutoff change can be made by an agent: both alter live sepsis-screening volume
and require clinical-governance ratification. "ausencia de noradrenalina" preserved verbatim.

<a id="rat-sepse-07"></a>
### RAT-SEPSE-07 — RULE-SEPSE-009: SEPSE v3 criterio_3 - respiratory failure prescription

> *`sepse` · `alert-threshold` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Intended absence of noradrenaline (12h) AND prescription of invasive vent or intubation (24h). - **Deviation:** DISCREPANCY - missing negation on noradrenaline vs docstring. - **Clinical relevance:** Confirms the extraction DISCREPANCY. The noradrenaline gate is inverted vs the 

**Question.** criterio_3 intends: ausencia de noradrenalina in the last 12h AND a prescription for invasive
ventilation or intubation in the last 24h. The code is missing the negation on noradrenaline (uses
qt_vol_nora presence, per the docstring "ausencia"). Do we ratify the docstring-correct absence gate?

**Options.**

- **A** — Ratify docstring intent: ausencia de noradrenalina (12h) AND invasive-vent/intubation prescription (24h)
- **B** — Preserve legacy code with noradrenaline PRESENCE (12h)

**Recommended default.** A — RATIFY: same inverted-negation defect as the other v3 sepsis criteria. The criterion is meant to
catch new respiratory failure (fresh invasive-vent/intubation order) in a patient not yet on
vasopressors — an organ-dysfunction sepsis signal preceding shock. The PRESENCE gate inverts the
target population to patients already on noradrenaline, suppressing exactly the early cases the
screen exists to find. Restoring "ausencia de noradrenalina" is the reference-correct fix, but it
changes live sepsis-alert firing and so is a clinical-governance ratification, not an agent edit.
PT-BR term preserved verbatim.

<a id="rat-sepse-09"></a>
### RAT-SEPSE-09 — RULE-SEPSE-015: SEPSE v3 criterio_9 - acute kidney injury without vasopressor/dialysis

> *`sepse` · `alert-threshold` · DISCREPANCY/DISCREPANCY*  - **Legacy:** No noradrenaline (12h) AND no hemodialysis AND no "DRC em TRS" AND (creatinine>2 OR creatinine rise >0.5 over last 2 evolutions). - **Deviation:** DISCREPANCY - DRC exclusion always-true due to fromkeys bug (RULE-systemic-BE-03-001); remaining creatinine logic is sound. - **Clin

**Question.** criterio_9 intends: no noradrenaline (12h) AND no hemodialysis AND no "DRC em TRS" (chronic kidney
disease on renal replacement) AND (creatinine > 2 OR creatinine rise > 0.5 over the last 2 evolutions).
The DRC exclusion is always-true due to a dict fromkeys bug (RULE-systemic-BE-03-001); the creatinine
logic itself is sound. Do we ratify the intended AKI logic with a working DRC-on-dialysis exclusion?

**Options.**

- **A** — Ratify intended logic with a functioning DRC-em-TRS exclusion: no NE (12h) AND no hemodialysis AND NOT chronic-dialysis AND (creatinine > 2 OR delta creatinine > 0.5 over last 2 evolutions)
- **B** — Preserve the fromkeys-broken behaviour (DRC exclusion vacuously true) verbatim

**Recommended default.** A — RATIFY: the criterion screens for acute kidney injury as a sepsis organ-dysfunction signal, and the
exclusion of chronic dialysis / DRC-em-TRS patients is clinically essential — a stable ESRD patient
on maintenance dialysis has a chronically elevated creatinine that is NOT acute and would generate
false sepsis alerts. The fromkeys bug (RULE-systemic-BE-03-001) makes that guard vacuously true, so
the exclusion currently never applies; the creatinine > 2 / delta > 0.5 core is correct. Fixing the
exclusion removes false positives in the chronic-renal population, a change to live alerting that
must be ratified by clinical governance. PT-BR term "DRC em TRS" preserved verbatim.

<a id="rat-sepse-10"></a>
### RAT-SEPSE-10 — RULE-SEPSE-016: SEPSE v3 criterio_10 - acute encephalopathy/delirium

> *`sepse` · `alert-threshold` · DISCREPANCY/DISCREPANCY*  - **Legacy:** No noradrenaline (12h) AND no invasive vent AND no dementia AND (GCS drop >=2 over 48h OR delirium in 24h OR GCS<14), with no prior delirium beyond 24h. - **Deviation:** DISCREPANCY - GCS delta sign inverted vs docstring; dementia exclusion vacuously true (fromkeys bug). - **Cli

**Question.** criterio_10 intends: no noradrenaline (12h) AND no invasive ventilation AND no dementia AND (GCS drop
>= 2 over 48h OR delirium in 24h OR GCS < 14), with no prior delirium beyond 24h. Two defects: the GCS
delta sign is inverted versus the docstring, and the dementia exclusion is vacuously true (fromkeys
bug). Do we ratify the intended encephalopathy logic with a correct GCS-drop sign and a working
dementia exclusion?

**Options.**

- **A** — Ratify intended logic: no NE (12h) AND no invasive vent AND NOT dementia AND (GCS drop >= 2 over 48h OR delirium <24h OR GCS < 14), excluding patients with delirium already present beyond 24h; fix GCS-delta sign and dementia exclusion
- **B** — Preserve legacy code (inverted GCS delta, dementia exclusion vacuously true) verbatim

**Recommended default.** A — RATIFY: acute encephalopathy/delirium is a valid sepsis organ-dysfunction criterion, but both defects
corrupt it. An inverted GCS-delta sign makes the code look for a GCS IMPROVEMENT rather than the
intended acute >= 2-point DROP, so genuine neurological deterioration is missed. The vacuous dementia
exclusion (same fromkeys bug family) fails to filter baseline-cognitively-impaired patients, whose
chronic low GCS / confusion would generate false acute-encephalopathy alerts. The "no prior delirium
beyond 24h" guard correctly restricts to NEW delirium. Both corrections change live alerting on a
sensitive neurological signal and require clinical-governance ratification.

<a id="rat-sepse-11"></a>
### RAT-SEPSE-11 — RULE-SEPSE-017: SEPSE v3 criterio_11 - hyperbilirubinemia/jaundice (incomplete)

> *`sepse` · `alert-threshold` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Intended - no noradrenaline (12h) AND (bilirubin>2 OR jaundice present). - **Deviation:** DISCREPANCY - the "bilirubina > 2mg/dl" branch from the docstring is not implemented; only the jaundice (diurna_ictericia) truthiness is checked. criterio_11 counts as a MAJOR in v3 alert. 

**Question.** criterio_11 intends: no noradrenaline (12h) AND (bilirubin > 2 mg/dL OR jaundice present). The code
implements only the jaundice (diurna_ictericia) truthiness branch and omits the "bilirubina > 2mg/dl"
branch entirely. criterio_11 counts as a MAJOR in the v3 alert. Do we ratify the complete intended
logic including the bilirubin lab branch?

**Options.**

- **A** — Ratify complete intent: no NE (12h) AND (bilirubina > 2 mg/dL OR ictericia present); implement the missing bilirubin branch
- **B** — Preserve legacy jaundice-only behaviour (bilirubin branch absent) verbatim

**Recommended default.** A — RATIFY: hepatic dysfunction in sepsis is defined by bilirubin > 2 mg/dL (consistent with the SOFA
hepatic sub-score band), and jaundice alone is a subjective, later-appearing sign. Omitting the
quantitative bilirubin branch means the criterion misses lab-evident hepatic dysfunction before it is
clinically visible — and because criterio_11 is a MAJOR contributor to the v3 alert, that omission
materially lowers alert sensitivity. Implementing the > 2 mg/dL branch is the reference-correct
completion, but adding a MAJOR trigger path changes alert weighting and firing, so it must be
ratified by clinical governance. PT-BR term "ictericia" preserved.

<a id="rat-sepse-12"></a>
### RAT-SEPSE-12 — RULE-SEPSE-019: SEPSE v3 criterio_13 - tachycardia (minor, wrong column)

> *`sepse` · `alert-threshold` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Intended - no noradrenaline (6h) AND heart rate > 100 bpm in last 6h. - **Deviation:** DISCREPANCY - filters fr (frequencia respiratoria) instead of fc (frequencia cardiaca) despite docstring "Frequencia cardiaca > 100 bpm". - **Clinical relevance:** Extraction-flagged DISCREPAN

**Question.** criterio_13 intends: no noradrenaline (6h) AND frequencia cardiaca > 100 bpm in the last 6h. The code
filters balanco.fr (frequencia respiratoria) instead of fc (frequencia cardiaca), despite the
docstring "Frequencia cardiaca > 100 bpm". Do we ratify the intended heart-rate column?

**Options.**

- **A** — Ratify docstring intent: no NE (6h) AND frequencia cardiaca (fc) > 100 bpm (6h); use the correct fc column
- **B** — Preserve legacy code filtering frequencia respiratoria (fr) verbatim

**Recommended default.** A — RATIFY: this is an unambiguous wrong-column defect — the code reads fr (respiratory rate) where the
docstring and clinical intent specify fc (heart rate). A > 100 threshold on respiratory rate is
clinically nonsensical (it would essentially never fire, since RR > 100 is incompatible with life),
so the criterion is effectively dead as written; on the correct fc column, > 100 bpm is a standard
tachycardia cutoff. Repointing to fc revives a minor sepsis criterion and thereby changes alert
firing, so despite being an obvious typo it must be ratified by clinical governance before it goes
live. PT-BR terms "frequencia cardiaca" and "frequencia respiratoria" preserved verbatim.

<a id="rat-sepse-13"></a>
### RAT-SEPSE-13 — RULE-SEPSE-020: SEPSE v3 criterio_14 - respiratory alkalosis/hypoxemia spontaneous vent (minor)

> *`sepse` · `alert-threshold` · OK/DISCREPANCY*  - **Legacy:** No noradrenaline (6h) AND spontaneous ventilation AND (PaCO2<32 OR PaO2/FiO2<300). - **Clinical relevance:** Independent verdict overrides extraction status OK: the equation form and both cutoffs (PaCO2<32 mmHg, P/F<300) match the references, BUT two reference-relevant computation defect

**Question.** criterio_14: no noradrenaline (6h) AND spontaneous ventilation AND (PaCO2 < 32 OR PaO2/FiO2 < 300).
The independent verdict overrides the extraction OK: the equation form and both cutoffs (PaCO2 < 32
mmHg, P/F < 300) match references, BUT two reference-relevant computation defects exist (e.g. the
PaCO2 branch via handlers.get_number parsing/units). Do we ratify the cutoffs while correcting the
computation defects?

**Options.**

- **A** — Ratify the criterion form and cutoffs (PaCO2 < 32 mmHg, PaO2/FiO2 < 300) and correct the two computation defects (number-parsing / unit handling on the PaCO2 and P/F branches)
- **B** — Preserve the legacy computation (including the parsing/unit defects) verbatim

**Recommended default.** A — RATIFY: the clinical form is correct — respiratory alkalosis (PaCO2 < 32 mmHg) or hypoxemia
(PaO2/FiO2 < 300) in a spontaneously breathing, not-yet-vasopressed patient is a legitimate early
sepsis respiratory signal, and both cutoffs match the references. The problem is purely at the
computation layer: the get_number-based parsing/unit handling on the PaCO2 (and P/F) branch can
mis-evaluate the threshold. Note the P/F cutoff shares the SOFA respiratory FiO2 fraction-vs-percent
hazard flagged in ESC-P0-001/ESC-P0-008, so the unit convention must be reconciled there too.
Correcting a threshold computation on a live criterion is a clinical-governance ratification.

<a id="rat-sepse-14"></a>
### RAT-SEPSE-14 — RULE-SEPSE-021: SEPSE v3 criterio_15 - leukocytosis/leukopenia/bandemia/CRP (minor)

> *`sepse` · `alert-threshold` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Intended - no noradrenaline (6h) AND (leukocytes>12000 OR <4000 OR bands>10% OR PCR>100) in 24h. Parses leukocytes (strip . and ,) and bands (strip %) to float. - **Deviation:** DISCREPANCY - PCR>100 is AND-combined with the leukocyte/band clause; docstring lists all four as OR 

**Question.** criterio_15 intends: no noradrenaline (6h) AND (leukocytes > 12000 OR leukocytes < 4000 OR bands > 10%
OR PCR > 100) within 24h. The code AND-combines the PCR > 100 clause with the leukocyte/band clause,
whereas the docstring lists all four as OR alternatives. Do we ratify the all-OR intended logic?

**Options.**

- **A** — Ratify docstring intent: no NE (6h) AND (leukocytes > 12000 OR leukocytes < 4000 OR bands > 10% OR PCR > 100) - all four as OR alternatives
- **B** — Preserve legacy AND-combination of the PCR clause with the leukocyte/band clause verbatim

**Recommended default.** A — RATIFY: leukocytosis (> 12000), leukopenia (< 4000), bandemia (> 10%) and elevated CRP/PCR (> 100)
are independent SIRS/inflammatory markers — the intended logic fires if ANY one is met. The legacy
AND-coupling of PCR with the leukocyte/band clause requires an abnormal WBC/band AND a high CRP
simultaneously, sharply reducing sensitivity (a pure CRP rise, or an isolated leukopenia, would no
longer fire). Restoring the four-way OR is the reference-correct form, but it increases firing on a
minor criterion and therefore is a clinical-governance ratification. The leukocyte string-parsing
(strip . and ,) and band-percent parsing (strip %) are retained as-is.

<a id="rat-sepse-11"></a>
### RAT-SEPSE-11 — RULE-SEPSE-058: Sepse v3 automatica - trigger threshold table (20 criteria)

> *`sepse` · `alert-threshold` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Sepsis screening pathway variant "v3" (payload_sepse_automatica_v3). Each of 20 criteria, when flagged by the model layer, surfaces an alert whose label encodes the exact clinical threshold that defines that criterion. This payload documents the full threshold set for the v3 sep

**Question.** RULE-SEPSE-058 (payload_sepse_automatica_v3) is the alert-label catalog for the v3 sepsis engine:
each of the 20 criteria, when flagged, surfaces an alert whose label encodes the exact clinical
threshold defining that criterion. The DISCREPANCY is that these alert-label thresholds must stay
consistent with the underlying criterion predicates (RULE-SEPSE-007..021 etc.). Do we ratify the
threshold table as the reconciled single source of truth for the 20 v3 criteria?

**Options.**

- **A** — Ratify the 20-criteria threshold table, reconciled per-criterion against the corrected predicates from the individual RATIFY records (ESC-P1-036..043 and siblings), so every displayed label matches its firing logic
- **B** — Treat the label table as descriptive only and let each predicate carry its own threshold, accepting label/logic drift
- **C** — Preserve the v3 automatica label catalog verbatim without reconciliation

**Recommended default.** A — RATIFY: this payload is the umbrella threshold table for the entire v3 sepsis screen, and each label
is the human-readable promise of what a criterion means. Because the individual criteria carry
inverted-negation, wrong-column, incomplete-branch and unit defects (resolved in ESC-P1-036 through
ESC-P1-043), the label table can only be ratified as a set once those per-criterion corrections are
agreed — otherwise a displayed threshold will contradict the corrected predicate that fires it.
Reconciling 20 clinical thresholds across an entire sepsis pathway is squarely a clinical-governance
decision. This record therefore ratifies the table by reference to, and consistency with, its member
criterion RATIFY records rather than resolving each number independently here.

<a id="rat-sinais-vitais-01"></a>
### RAT-SINAIS-VITAIS-01 — RULE-SINAIS-VITAIS-004: Capillary refill time (TEC) range and >5s threshold — inconsistent encodings

> *`sinais-vitais` · `alert-threshold` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Capillary refill time (TEC) is captured three different ways across the frontend: as a number bounded 3-20 s (movimentacao), as a boolean ">5s?" (enfermagem), and as an exam checkbox "TEC > 5s" (physician). The numeric field's lower bound of 3s also conflicts with physio

**Question.** Capillary refill time (TEC) is captured three different ways across the frontend: a number bounded
3-20 s (movimentacao), a boolean ">5s?" (enfermagem), and an exam checkbox "TEC > 5s" (physician). The
numeric field's 3 s lower bound also conflicts with physiologically-normal refill (< 2-3 s), and the
> 5 s abnormal threshold disagrees with the ANDROMEDA-SHOCK CRT > 3 s definition used by the v3
counterpart. Do we ratify a single canonical TEC representation and abnormal threshold?

**Options.**

- **A** — Ratify one canonical numeric TEC in seconds with a physiological lower bound (allow < 3 s, e.g. range 0-20 s) and adopt the ANDROMEDA-SHOCK abnormal cutoff CRT > 3 s; migrate the boolean '>5s?' and checkbox 'TEC > 5s' capture points onto the canonical field
- **B** — Standardise all three capture points on the legacy > 5 s abnormal threshold and the 3-20 s numeric bound
- **C** — Preserve all three verbatim encodings (3-20 s numeric, boolean >5s, checkbox TEC>5s) with no unification

**Recommended default.** A — RATIFY: three incompatible encodings of the same vital across nursing, physician and movimentacao
forms make TEC un-computable as a single signal and force downstream rules to guess which field to
read. Two clinical issues compound it: (1) a numeric lower bound of 3 s cannot represent a normal
refill (< 2-3 s), so a normal patient is unrepresentable; (2) the > 5 s abnormal threshold contradicts
the validated ANDROMEDA-SHOCK peripheral-perfusion definition of CRT > 3 s that RULE-ESTABILIDADE-003
already uses, meaning the 3-5 s abnormal band is silently lost. Choosing the canonical representation,
the lower bound, and the abnormal cutoff (3 s vs 5 s) is a clinical-governance decision with data-model
migration implications, so it is ratified rather than resolved by an agent. PT-BR "TEC > 5s" preserved.

<a id="rat-estabilidade-09"></a>
### RAT-ESTABILIDADE-09 — RULE-ESTABILIDADE-017: Estabilidade manual C1 - slow capillary refill on noradrenaline

> *`estabilidade` · `care-pathway` · OK/DISCREPANCY*  - **Legacy:** Flags capillary refill time > 5s together with an active (persisted) noradrenaline record. - **Clinical relevance:** Manual C1 uses CRT strict > 5 s, whereas the validated septic-shock reference (ANDROMEDA-SHOCK) defines abnormal peripheral perfusion as CRT > 3 s (the v3 counterpart 

**Question.** For the manual estabilidade C1 criterion (slow capillary refill on a patient with an active noradrenaline record), should the abnormal capillary-refill-time threshold be CRT > 3 s (ANDROMEDA-SHOCK), harmonized with the v3 counterpart RULE-ESTABILIDADE-003, instead of the legacy strict CRT > 5 s?

**Options.**

- **A** — Ratify CRT > 3 s abnormal threshold (ANDROMEDA-SHOCK), aligning manual C1 with v3 RULE-ESTABILIDADE-003: flag on TEC > 3 s AND an active noradrenaline record. *(risk: Low - restores detection of the 3-5 s hypoperfusion band in a vasopressor-dependent patient; increases alert volume modestly but captures genuine hypoperfusion.)*
- **B** — Preserve the legacy strict CRT > 5 s. *(risk: Moderate - the 3-5 s abnormal band (genuine hypoperfusion on noradrenaline) is silently missed, delaying shock escalation; conservative (fewer alerts) but clinically under-sensitive.)*
- **C** — Adopt CRT >= 3 s (inclusive) so exactly 3 s also flags. *(risk: Moderate - ANDROMEDA defines > 3 s (exclusive) as abnormal and 3 s as the upper limit of normal, so >= 3 s would over-trigger at the boundary versus the validated definition.)*

**Recommended default.** A — ANDROMEDA-SHOCK (Hernandez G et al., JAMA 2019;321(7):654-664) defines abnormal peripheral perfusion as
capillary refill time > 3 s (distal phalanx, 10 s pressure), and the v3 counterpart RULE-ESTABILIDADE-003
already uses > 3 s. The manual pathway's strict > 5 s is therefore an internal inconsistency that silently
drops the 3-5 s hypoperfusion band in exactly the population - a patient already on noradrenaline - where
delayed escalation is most dangerous. Harmonizing on > 3 s is reference-correct and removes the manual-vs-v3
divergence. Because it raises live alert volume on the estabilidade pathway, clinical governance must ratify.

**Disposition note.** RATIFY the ANDROMEDA-SHOCK CRT > 3 s abnormal threshold for manual C1, harmonized with v3 RULE-ESTABILIDADE-003. Do NOT port the legacy strict > 5 s. The 3 s cutoff decided here must match the canonical TEC representation/lower bound ratified in ESC-P1-045 (RULE-SINAIS-VITAIS-004). PT-BR term 'TEC' / 'tempo de enchimento capilar' preserved verbatim.

<a id="rat-estabilidade-11"></a>
### RAT-ESTABILIDADE-11 — RULE-ESTABILIDADE-024: Estabilizacao (trilha2) - shock work-up & vasopressor escalation text catalog

> *`estabilidade` · `care-pathway` · AMBIGUOUS/DISCREPANCY*  - **Legacy:** Recommendation/alert-text catalog for the estabilizacao (trilha2) pathway. Criteria for malperfusion, noradrenaline initiation, high-dose noradrenaline, hyperlactatemia, antihypertensives in shock, and refractory shock with dobutamine, plus sparse criterio_7/10 stubs. - **Devi

**Question.** In the estabilizacao (trilha2) alert-text catalog, should the noradrenaline high-dose escalation threshold in criterio_3 be corrected to mcg/kg/min (aligned to SSC 2021 and the sibling estabilidade facade RULE-ESTABILIDADE-016), rather than the legacy clinician-facing label '> 0,5 mcg/kg/h'?

**Options.**

- **A** — Ratify the SSC-2021 per-minute unit (mcg/kg/min) for the displayed threshold and reconcile with RULE-ESTABILIDADE-016; also record the SSC corticosteroid trigger of norepinephrine >= 0.25 mcg/kg/min for review of the 0.5 value. *(risk: Low - the catalog performs no numeric comparison itself, so correcting the displayed unit removes a 60x clinician-facing error and aligns cross-pathway text without changing firing behaviour.)*
- **B** — Preserve the legacy '> 0,5 mcg/kg/h' text verbatim. *(risk: Moderate - a per-hour label on a per-minute drug rate is a 60x unit error that misleads bedside clinicians and, if ever reused against a real mcg/kg/min feed, would misclassify almost any noradrenaline exposure as 'high dose'.)*

**Recommended default.** A — SSC 2021 (Evans L et al., Crit Care Med 2021;49(11):e1063-e1143) doses vasopressors as a weight-based rate
per MINUTE (mcg/kg/min), gives hydrocortisone 200 mg/day as 50 mg IV q6h, and sets the corticosteroid trigger
at norepinephrine >= 0.25 mcg/kg/min for >= 4h. The recommendation CONTENT (hydrocortisone 50 mg q6h +
continuous vasopressin, dobutamine reduction at FC > 130, lactate/perfusion work-up) already matches the
guideline; the sole clinical defect is the '/h' unit on criterio_3, which contradicts the sibling facade
RULE-ESTABILIDADE-016 (mcg/kg/min) on the same 0.5 value (0.5 mcg/kg/min = 30 mcg/kg/h, a 60x discrepancy).
Correcting a clinician-facing dosing unit requires clinical-governance sign-off.

**Disposition note.** RATIFY the SSC-2021 per-minute vasopressor dosing unit (mcg/kg/min) for the criterio_3 displayed threshold; reconcile with RULE-ESTABILIDADE-016. Do NOT port the '/h' unit. Flag the 0.5 vs SSC 0.25 mcg/kg/min corticosteroid-trigger value for governance. Repair the non-clinical text defects (structural key gap missing criteria 8/9, empty criterio_7 and criterio_10 recomendacoes, stray smart-quote after 'vasopressina'). PT-BR clinical text preserved verbatim.

<a id="rat-nutricao-01"></a>
### RAT-NUTRICAO-01 — RULE-NUTRICAO-003: Nutrition-therapy pathway (payload_trilha_nutricao) - tolerance, gastric-residual and cont

> *`nutricao` · `care-pathway` · OK/DISCREPANCY*  - **Legacy:** Nutrition pathway (= nutricao / trilha6): per-criterion alert text and recommendations covering diet prescription, SNE need, tolerance/gastric-residual limits, diarrhea management, malperfusion feeding, prokinetics, GI bleed, NPT and hyperglycemia. Defined as the dict payload_trilha_nutr

**Question.** For the nutrition-therapy pathway text catalog, do we ratify the published clinical anchors it embeds - gastric-residual-volume hold at VRG > 500 mL/6h (ASPEN/SCCM 2016) and restrictive RBC transfusion at Hb < 7 g/dL in GI bleed (Villanueva 2013) - while flagging the site-specific noradrenaline 30 ml/h = 0,05 mcg/kg/min equivalence and the 'Hb < 7 AND plaquetas < 150000' transfusion conjunction for governance review?

**Options.**

- **A** — Ratify VRG > 500 mL/6h and restrictive Hb < 7 g/dL transfusion as reference-correct; record the noradrenaline 30 ml/h = 0,05 mcg/kg/min conversion as a site-specific open unit item; flag the plaquetas < 150000 conjunction as a possible over-restriction of indicated RBC transfusion. *(risk: Low - the two published anchors match guidelines; the open items are a dose-unit conversion and a compound-condition review, not changes to the core thresholds.)*
- **B** — Preserve all legacy nutrition text verbatim, including the ml/h vasopressor equivalence and the 'Hb < 7 AND plaquetas < 150000' conjunction, with no unit annotation. *(risk: Moderate - the ml/h equivalence is non-portable (concentration/weight dependent) and the platelet conjunction could delay a guideline-indicated RBC transfusion, since the restrictive threshold is Hb < 7 alone.)*
- **C** — Rewire all 10 criteria into the automatic alert (currently only criteria 4/7/10 surface via get_detalhe). *(risk: Moderate - expands live alerting substantially; a scope change requiring separate clinical-governance and PPV review.)*

**Recommended default.** A — The pathway embeds two published anchors that match reference. ASPEN/SCCM 2016 (McClave SA et al.) holds
enteral nutrition only for gastric residual volume > 500 mL, and Villanueva C et al. (NEJM 2013;368:11-21)
validate a restrictive RBC transfusion threshold of Hb < 7 g/dL in acute upper GI bleeding - both consistent
with the legacy VRG 500 mL/6h and Hb < 7 text. The residual concerns are (1) the noradrenaline
'30 ml/h = 0,05 mcg/kg/min' equivalence, a site-specific conversion depending on drug concentration and
patient weight that cannot be validated generically, and (2) the 'Hb < 7 AND plaquetas < 150000' conjunction,
stricter than the guideline (restrictive RBC transfusion is indicated at Hb < 7 irrespective of platelet
count) and thus a possible delay of indicated transfusion. Both are clinical-governance decisions.

**Disposition note.** RATIFY VRG > 500 mL/6h (ASPEN/SCCM 2016) and the restrictive Hb < 7 g/dL RBC-transfusion trigger (Villanueva 2013) as the reference-correct nutrition-pathway anchors. Open items for governance: (a) the noradrenaline 30 ml/h = 0,05 mcg/kg/min site-specific conversion, recorded as an open unit item like the estabilidade ml/h dosing (ESC-P1-032/ESC-P1-033); (b) the 'Hb < 7 AND plaquetas < 150000' transfusion conjunction, reviewed as a possible over-restriction. Note only criteria 4/7/10 are wired into the automatic alert (get_detalhe). PT-BR clinical vocabulary preserved verbatim, accents included.

<a id="rat-profilaxia-01"></a>
### RAT-PROFILAXIA-01 — RULE-PROFILAXIA-005: Prophylaxis v3 criterio_1 - GI stress-ulcer (LAMGD) prophylaxis indicated but absent (AMAR

> *`profilaxia` · `care-pathway` · DISCREPANCY/DISCREPANCY*  - **Legacy:** criterio_1 predicate: no PPI/cimetidine prescribed AND at least one stress-ulcer prophylaxis indication present (noradrenaline in balance; OR mechanical ventilation >48h; OR platelets <= 50000; OR no enteral/oral diet logged >24h; OR high-risk admission diagnosis). - **Deviati

**Question.** For the wired prophylaxis v3 criterio_1 (stress-ulcer prophylaxis indicated but absent -> AMARELO), do we ratify the reference-correct Cook-1994 indications - mechanical ventilation > 48h and coagulopathy at plaquetas < 50,000/mm3 - and restore the functionally inert high-risk admission-diagnosis branch (dict.fromkeys bug + string-concat bug), rather than preserve the legacy behaviour?

**Options.**

- **A** — Ratify the Cook-1994 indications: MV > 48h (fix the 50h window -> 48h), coagulopathy plaquetas < 50,000 (fix <= 50000 -> < 50000), diet-absence at 24h; and repair the admission-diagnosis branch so TCE/AVC/SEPSE/queimado/cirrose/HDA actually match (fix the dict.fromkeys None-values bug and the 'hemorragico'+'Grande queimado' string-concat fusion). *(risk: Low - restores an entire recognized indication class (ASPEN/ASHP additional SUP conditions) that currently can never raise the alert; increases the sensitivity of an advisory alert.)*
- **B** — Preserve the legacy verbatim (50h/26h windows, plaquetas <= 50000, inert diagnosis branch, string-concat bug). *(risk: Moderate - patients qualifying ONLY via admission diagnosis (TCE, queimado, SEPSE, cirrose, HDA) never get the AMARELO prophylaxis alert, giving under-detection; plus a boundary over-trigger at plaquetas exactly 50,000.)*

**Recommended default.** A — Cook DJ et al. (NEJM 1994;330:377-381, Canadian Critical Care Trials Group) established the two independent
risk factors for clinically important GI bleeding as mechanical ventilation > 48h (OR 15.6) and coagulopathy
= platelet count < 50,000/mm3 (OR 4.3); ASPEN/ASHP guidance adds TBI, extensive burns, sepsis, hepatic
failure and GI bleed as accepted indications. The legacy diverges: the MV window is 50h (not 48h) and diet
window 26h (not 24h), and plaquetas <= 50000 over-triggers by one boundary unit at exactly 50,000. The
material defect is that the entire high-risk-diagnosis OR-clause is INERT - dict.fromkeys iterates the literal
KEY NAMES not the field VALUES (systemic finding RULE-systemic-BE-03-001) - compounded by a Python
implicit-string-concat bug fusing two diagnoses into one unmatchable string. Restoring this branch and the
reference cutoffs raises sensitivity of a live AMARELO alert, so clinical governance must ratify.

**Disposition note.** RATIFY the Cook-1994 reference form: MV > 48h, coagulopathy plaquetas < 50,000/mm3 (strict), diet-absence 24h; repair the inert admission-diagnosis branch (dict.fromkeys None-values bug, systemic RULE-systemic-BE-03-001) and the 'Acidente vascular cerebral hemorragico'+'Grande queimado' string-concat fusion so all ASPEN/ASHP high-risk diagnoses match. Do NOT port the 50h/26h windows, plaquetas <= 50000, or the inert branch. Wired to AMARELO via calcular_alerta_v2 (action text RULE-PROFILAXIA-008). PT-BR admission-diagnosis strings preserved verbatim, accents included.

<a id="rat-sepse-12"></a>
### RAT-SEPSE-12 — RULE-SEPSE-060: Sepse pathway variant A - 11-criterion catalog + Meropenem/1500ml recommendation

> *`sepse` · `care-pathway` · AMBIGUOUS/DISCREPANCY*  - **Legacy:** Sepsis pathway variant A: nested {"criterios": {...}} structure with 11 qualitative alert flags and a single global recommendation naming a specific empiric antibiotic and fixed fluid bolus. Structure differs from variants B/C (criterios nested under a key). - **Clinical relevance:**

**Question.** For sepsis pathway variant A, do we ratify the SSC-2021 weight-based initial fluid resuscitation of 30 mL/kg crystalloid (replacing the legacy fixed 1500 mL Ringer Lactato bolus), treat the specific 'Meropenem 1 g EV' empiric-antibiotic naming as an antimicrobial-stewardship decision, and confirm this variant's wiring status (variant B appears to be the live consumer)?

**Options.**

- **A** — Ratify SSC-2021 weight-based 30 mL/kg crystalloid within 3h; defer 'Meropenem 1 g' to antimicrobial stewardship as an institutional empiric choice; confirm variant A wiring before any production use. *(risk: Low - weight-based dosing prevents under-resuscitation of heavier adults, and the antibiotic-agent choice is correctly deferred to stewardship.)*
- **B** — Preserve the fixed 1500 mL Ringer Lactato bolus and Meropenem 1 g verbatim. *(risk: Moderate - a fixed 1500 mL bolus equals 30 mL/kg only at ~50 kg and progressively under-resuscitates (600 mL short at 70 kg, 1500 mL short at 100 kg), delaying perfusion restoration in septic shock; a fixed empiric agent bypasses stewardship.)*
- **C** — Retire variant A as dead code (its consumer is not evident; core/facade/sepse.py aliases the 27-criterion variant B). *(risk: Low if confirmed unwired - but requires positive verification that no path consumes payload variant A before removal.)*

**Recommended default.** A — SSC 2021 (Evans L et al., Crit Care Med 2021;49(11):e1063-e1143) recommends at least 30 mL/kg IV crystalloid
within the first 3h of sepsis-induced hypoperfusion, guided by lactate remeasurement - a weight-based
construct; a fixed-volume bolus is not a guideline concept. The legacy fixed 1500 mL Ringer Lactato equals
30 mL/kg only at ~50 kg and under-resuscitates heavier adults (600 mL short at 70 kg, 1500 mL at 100 kg). The
empiric 'Meropenem 1 g EV' is an institutional choice; SSC recommends broad-spectrum coverage within 1h but
names no agent, so agent/dose belongs to antimicrobial stewardship. Because variant A's consumer is not
evident within scope (facade aliases the 27-criterion variant B, RULE-SEPSE-059), wiring must be confirmed
before the fluid change reaches patients. Weight-based dosing and stewardship deferral are ratified.

**Disposition note.** RATIFY SSC-2021 weight-based 30 mL/kg crystalloid within 3h as the reference-correct initial fluid resuscitation; defer the 'Meropenem 1 g EV' empiric-agent choice to antimicrobial stewardship. Do NOT port the fixed 1500 mL bolus. Verify variant A wiring (appears deprecated; variant B RULE-SEPSE-059 is the live 27-criterion consumer) - if confirmed dead code, RETIRE instead. Lactate remeasurement 'apos 3h' is SSC-concordant; cultures/imaging/catheter guidance retained. Related RULE-SEPSE-061 (volume-expansion dosing). PT-BR text preserved verbatim.

<a id="rat-ventilacao-02"></a>
### RAT-VENTILACAO-02 — RULE-VENTILACAO-003: Ventilation C1 - high inspiratory pressure or tidal volume

> *`ventilacao` · `care-pathway` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Flags inspiratory pressure > 16 OR tidal volume > 500 ml. Also a hard alert-forcing criterion. - **Deviation:** Current code: PINS>16 OR VC>500 ml (absolute). _ANTIGAS_REGRAS used "Pressao Controlada >15 OU Volume Corrente >6 ml/kg" (weight-based). Current version replaced wei

**Question.** For ventilation criterion C1 (high inspiratory pressure or tidal volume), do we ratify a weight-indexed tidal-volume limit of > 6 mL/kg predicted body weight (ARDSNet) in place of the legacy absolute > 500 mL, and align the pressure limit to the driving/plateau-pressure evidence rather than the legacy absolute > 16?

**Options.**

- **A** — Ratify tidal-volume limit at > 6 mL/kg predicted body weight (ARDSNet ARMA) and an evidence-based pressure limit (driving pressure > 15 cmH2O / plateau > 30 cmH2O); compute predicted body weight from height and sex. *(risk: Low - restores the validated lung-protective, weight-indexed target; an absolute 500 mL is unsafe because it over- or under-flags depending on patient size.)*
- **B** — Preserve the legacy absolute PINS > 16 OR VC > 500 mL. *(risk: Moderate - an absolute 500 mL flag ignores patient size, so a small patient ventilated at an injurious mL/kg is missed while a large patient at a safe mL/kg over-alerts; departs from ARDSNet.)*
- **C** — Restore the _ANTIGAS_REGRAS weight-based VC > 6 mL/kg but keep the pressure cutoff at the legacy > 16 (change only tidal volume). *(risk: Low-moderate - fixes tidal-volume weight-indexing but leaves an unreferenced absolute pressure cutoff.)*

**Recommended default.** A — Lung-protective ventilation is weight-indexed. ARDSNet ARMA (NEJM 2000;342:1301-1308) established a
tidal-volume target of <= 6 mL/kg PREDICTED body weight (computed from height and sex), and Amato MBP et al.
(NEJM 2015;372:747-755) identified driving pressure <= 15 cmH2O (with plateau <= 30 cmH2O) as the pressure
most associated with survival. The legacy replaced the original weight-based '> 6 mL/kg' (_ANTIGAS_REGRAS)
with an absolute '> 500 mL' and set pressure at an unreferenced absolute '> 16', so tidal-volume safety no
longer scales with the patient: 500 mL is ~10 mL/kg for a 50 kg woman but ~6 mL/kg for an 83 kg man.
Restoring PBW-indexed tidal volume and an evidence-based pressure limit is reference-correct. Because C1 is an
alert-forcing criterion (RULE-VENTILACAO-014), the change alters live alerting and requires ratification.

**Disposition note.** RATIFY weight-indexed tidal volume > 6 mL/kg predicted body weight (ARDSNet ARMA) and an evidence-based pressure limit (driving pressure > 15 cmH2O / plateau > 30 cmH2O, Amato 2015) for C1. Do NOT port the absolute VC > 500 mL or the unreferenced PINS > 16. Requires predicted-body-weight computation (height + sex) upstream. Alert-forcing criterion (RULE-VENTILACAO-014); coordinate with the automatica facade RULE-VENTILACAO-017. PT-BR field names (pressao_inspiratoria, volume_corrente) preserved.

<a id="rat-ventilacao-03"></a>
### RAT-VENTILACAO-03 — RULE-VENTILACAO-004: Ventilation C2 - FiO2xPEEP mismatch with moderate hypoxemia

> *`ventilacao` · `care-pathway` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Flags a PEEP value not matching the expected FiO2->PEEP table AND P/F ratio between 151 and 300. - **Deviation:** (1) Malformed guard: peep>0 requirement is dead code (inside `False and ...`), so PEEP>0 is NOT enforced. (2) FiO2 unit inconsistency: key = str(fio2/100)[0:3] ass

**Question.** For ventilation criterion C2 (PEEP/FiO2 mismatch with moderate hypoxemia), do we ratify (a) repairing the malformed guard so PEEP > 0 is actually enforced, and (b) a single canonical FiO2 unit (fraction 0.21-1.0) feeding the ARDSNet Lower-PEEP/Higher-FiO2 titration table, replacing the str(fio2/100) percentage-assumption that mis-keys fractional inputs to '0.0'?

**Options.**

- **A** — Ratify: enforce PEEP > 0 in the guard; normalize FiO2 to a fraction (0.21-1.0) before the table lookup; use the canonical ARDSNet Lower-PEEP/Higher-FiO2 allowed-PEEP table; keep the moderate-hypoxemia P/F window. *(risk: Low - the FiO2 key is computed correctly (fio2 = 1.0 -> '1.0', not '0.0'), the dead PEEP guard is repaired, and PEEP-mismatch detection matches the ARDSNet table.)*
- **B** — Preserve the legacy verbatim (dead PEEP > 0 guard inside 'False and ...'; str(fio2/100)[0:3] percentage key that maps fio2 = 1 to '0.0'). *(risk: High - fractional FiO2 is mis-keyed (a patient on FiO2 1.0 is scored against the '0.0' row), so PEEP-mismatch alerts fire against the wrong FiO2 band, and PEEP > 0 is never enforced.)*

**Recommended default.** A — The ARDSNet Lower-PEEP/Higher-FiO2 titration table (ARMA, NEJM 2000;342:1301) specifies allowed PEEP for each
FiO2 expressed as a FRACTION (0.3->5; 0.4->5,8; 0.5->8,10; ... 1.0->18,20,22,24), and Berlin (JAMA
2012;307:2526) grades P/F severity. The legacy has two reference-relevant computation defects: the guard's
'peep > 0' requirement is dead code (nested inside 'False and ...'), so PEEP presence is never enforced; and
the FiO2 key str(fio2/100)[0:3] assumes a percentage input, so a fractional FiO2 of 1.0 is mis-keyed to '0.0'
and scored against the wrong PEEP row - the shared FiO2 fraction-vs-percent hazard flagged in ESC-P0-001 /
RULE-CLINICAL-SCORING-008. Fixing the guard and standardizing FiO2 to a fraction is reference-correct; because
it changes a live ventilation alert, clinical governance must ratify and reconcile the unit convention.

**Disposition note.** RATIFY: enforce PEEP > 0 (repair the 'False and ...' dead-guard) and normalize FiO2 to a fraction (0.21-1.0) before the ARDSNet Lower-PEEP/Higher-FiO2 table lookup. Do NOT port str(fio2/100)[0:3] (mis-keys fractional FiO2 to '0.0'). The FiO2 fraction-vs-percent convention must be reconciled platform-wide with SOFA respiratory (ESC-P0-001, RULE-CLINICAL-SCORING-008) and sibling C3 (RULE-VENTILACAO-005, ESC-P1-053). C2 table = moderate-hypoxemia arm, distinct from the C3 severe arm.

<a id="rat-ventilacao-04"></a>
### RAT-VENTILACAO-04 — RULE-VENTILACAO-005: Ventilation C3 - FiO2xPEEP mismatch with severe hypoxemia

> *`ventilacao` · `care-pathway` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Flags a PEEP not matching the (different, severe) FiO2->PEEP table AND P/F ratio < 150. - **Deviation:** FiO2 unit inconsistency (fio2/100 percentage assumption vs fraction tests) as in C2 (RULE-VENTILACAO-004), but the guard is CORRECT here (ratio truthy AND peep>0). The C3 s

**Question.** For ventilation criterion C3 (PEEP/FiO2 mismatch with severe hypoxemia, P/F < 150), do we ratify a single canonical FiO2 unit (fraction 0.21-1.0) feeding the ARDSNet Higher-PEEP/Lower-FiO2 severe-arm titration table, replacing the str(fio2/100) percentage-assumption that mis-keys fractional FiO2 to '0.0' (the guard here is already correct)?

**Options.**

- **A** — Ratify: normalize FiO2 to a fraction before the severe-arm table lookup; retain the already-correct guard (P/F truthy AND PEEP > 0); keep the P/F < 150 window. *(risk: Low - corrects FiO2 keying so the severe-arm ARDSNet table is applied to the right FiO2 band; guard unchanged.)*
- **B** — Preserve the legacy str(fio2/100)[0:3] percentage key verbatim. *(risk: High - a fractional FiO2 of 1.0 mis-keys to '0.0' and is scored against the wrong PEEP row in the most severe hypoxemia patients (P/F < 150), producing incorrect PEEP-mismatch alerts exactly where ventilation errors are most dangerous.)*

**Recommended default.** A — The ARDSNet Higher-PEEP/Lower-FiO2 (ALVEOLI, NEJM 2004;351:327-336) severe-hypoxemia titration table
specifies allowed PEEP per FiO2 as a FRACTION (0.3->5-14; 0.4->14,16; 0.5->16,18; ... 0.8-1.0->22,24); P/F <
150 is the PROSEVA prone-positioning threshold (Guerin C et al., NEJM 2013;368:2159-2168) and Berlin 'severe'
ARDS is P/F < 100 (JAMA 2012;307:2526). C3's guard is already correct (P/F truthy AND PEEP > 0), so the sole
reference-relevant defect is the FiO2 key str(fio2/100)[0:3], which assumes a percentage and mis-keys a
fractional FiO2 of 1.0 to '0.0' - the same fraction-vs-percent hazard as C2 (ESC-P1-052) and SOFA respiratory
(ESC-P0-001). Standardizing FiO2 to a fraction is reference-correct; because it changes live alerting in
severe hypoxemia and shares the platform FiO2 unit convention, clinical governance must ratify.

**Disposition note.** RATIFY normalization of FiO2 to a fraction (0.21-1.0) before the ARDSNet Higher-PEEP/Lower-FiO2 severe-arm table lookup; retain the correct guard (P/F truthy AND PEEP > 0). Do NOT port str(fio2/100)[0:3]. Reconcile the FiO2 fraction-vs-percent convention platform-wide with C2 (RULE-VENTILACAO-004, ESC-P1-052) and SOFA respiratory (ESC-P0-001, RULE-CLINICAL-SCORING-008). C3 severe-arm table is distinct from the C2 moderate arm; P/F < 150 = PROSEVA prone threshold.

<a id="rat-ventilacao-05"></a>
### RAT-VENTILACAO-05 — RULE-VENTILACAO-009: Ventilation C6 - prolonged intubation with COVID-19

> *`ventilacao` · `care-pathway` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Flags TOT ventilation > 10 days AND COVID-19 diagnosis. - **Deviation:** Current code uses dias_vm > 10. _REGRAS text says ">10 dias TOT E COVID" but _ANTIGAS_REGRAS C5 said ">14 dias". The automatica facade (RULE-VENTILACAO-017 criterio_6) states ">14 dias" for COVID trach. V

**Question.** For ventilation criterion C6 (prolonged intubation with COVID-19 -> tracheostomy consideration), do we ratify the > 14-day intubation threshold from the COVID-19 tracheostomy guidelines and the automatica facade (RULE-VENTILACAO-017 criterio_6), resolving the divergence against the legacy manual code's > 10 days?

**Options.**

- **A** — Ratify > 14 days TOT with COVID-19 (COVID tracheostomy guidelines; matches facade RULE-VENTILACAO-017 criterio_6 and _ANTIGAS_REGRAS C5), replacing the manual code's > 10 days. *(risk: Low - aligns with guideline deferral of tracheostomy to >= 14 days in COVID (aerosol/viral-load risk) and removes the manual-vs-facade divergence; slightly fewer/later alerts.)*
- **B** — Preserve the legacy manual code's > 10 days. *(risk: Moderate - flags COVID tracheostomy consideration ~4 days earlier than guideline-recommended and contradicts the sibling automatica facade (> 14), producing inconsistent guidance across pathways.)*

**Recommended default.** A — International multidisciplinary COVID-19 tracheostomy guidance (AAO-HNS 2020; Br J Anaesth / Otolaryngol Head
Neck Surg systematic reviews) recommends deferring tracheostomy until at least 14 days of intubation (often
2-3 weeks) because of aerosolization and viral-load risk to staff. The legacy manual pathway codes dias_vm >
10, but the _REGRAS text, the deprecated _ANTIGAS_REGRAS C5, and the live automatica facade
RULE-VENTILACAO-017 criterio_6 all state > 14 days - so > 10 is both under-referenced and internally
inconsistent with the facade the same product ships. Ratifying > 14 days aligns the manual criterion with the
guideline and resolves the divergence. Because it changes when a live tracheostomy alert fires, ratify.

**Disposition note.** RATIFY > 14 days TOT intubation with COVID-19 (COVID-19 tracheostomy guidelines; consistent with automatica facade RULE-VENTILACAO-017 criterio_6). Do NOT port the manual code's > 10 days. Resolves the manual-vs-facade variant divergence in favour of the facade/guideline value. PT-BR device term 'tot' (tubo orotraqueal) preserved.

<a id="rat-eficiencia-01"></a>
### RAT-EFICIENCIA-01 — RULE-EFICIENCIA-002: Eficiencia v3 criterio_3 - unjustified RBC transfusion at Hb>=7 (AMARELO, wired)

> *`eficiencia` · `triage-eligibility` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Intended - Hb>=7 AND packed-RBC ("Concentrado de hemacias com filtro") prescribed AND absence of SCA / Melena / Enterorragia / AVC isquemico (I64) / AVC hemorragico / TCE. Feeds the AMARELO alert. Restrictive transfusion threshold (Hb>=7 in absence of active bleeding, ac

**Question.** For the wired efficiency criterion 3 (reassess RBC transfusion when Hb >= 7 without justification -> AMARELO), do we ratify the AABB-2016 restrictive threshold Hb >= 7 g/dL correctly applied (fixing the operator-precedence bug that currently defeats it) and restore the functionally inert SCA and AVC-isquemico (I64) exclusions?

**Options.**

- **A** — Ratify Hb >= 7 g/dL correctly evaluated (repair the 'diurna_hemoglobina or 0 >= 7' precedence bug) AND restore the SCA (acute coronary syndrome) and AVC-isquemico (I64) exclusions (fix the vars().fromkeys None-values bug); retain the working Melena/Enterorragia exclusion. *(risk: Low - the alert fires only when Hb is genuinely >= 7 without a bleeding/ACS/stroke carve-out, matching AABB 2016; eliminates false positives on patients appropriately transfused below 7 and correctly suppresses ACS/acute-brain-injury alerts.)*
- **B** — Preserve the legacy verbatim (precedence bug defeats the Hb >= 7 gate; SCA/I64 exclusions inert). *(risk: Moderate - fires on ANY non-zero Hb plus an RBC order, generating false 'reassess transfusion' AMARELO alerts on patients correctly transfused below 7, and fails to suppress alerts for the exact ACS/acute-brain-injury exceptions the guideline carves out (alert fatigue, second-guessing of indicated transfusions).)*

**Recommended default.** A — The AABB 2016 guideline (Carson JL et al., JAMA 2016;316(19):2025-2035), building on TRICC (Hebert PC et al.,
NEJM 1999;340:409-417), sets a restrictive RBC-transfusion threshold of Hb < 7 g/dL for hemodynamically
stable hospitalized adults including the critically ill, with explicit exceptions for acute coronary
syndrome. The intended criterion (flag transfusion at Hb >= 7 absent bleeding/ACS/acute-brain-injury) matches
the guideline, but two defects defeat it: the operator-precedence bug 'diurna_hemoglobina or 0 >= 7' parses as
'diurna_hemoglobina or (0 >= 7)', so the Hb >= 7 gate is never applied and the alert fires on any non-zero Hb
plus an RBC order; and the SCA/AVC-isquemico (I64) exclusions - the guideline's own carve-outs - are inert
because vars().fromkeys() yields all-None values (systemic RULE-systemic-BE-03-001). Wired AMARELO: ratify.

**Disposition note.** RATIFY correctly-evaluated Hb >= 7 g/dL (AABB 2016 restrictive threshold) with functioning SCA and AVC-isquemico (I64) exclusions. Do NOT port the 'diurna_hemoglobina or 0 >= 7' precedence bug (defeats the threshold) or the inert fromkeys exclusions (systemic RULE-systemic-BE-03-001). Retain the working Melena/Enterorragia exclusion. Wired to AMARELO via calcular_alerta_v2; facade label RULE-EFICIENCIA-012. PT-BR diagnosis strings preserved verbatim.

<a id="rat-eficiencia-02"></a>
### RAT-EFICIENCIA-02 — RULE-EFICIENCIA-004: Eficiencia v3 criterio_5 - platelet transfusion at Plt>25000 (VERMELHO, wired)

> *`eficiencia` · `triage-eligibility` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Intended - platelet concentrate ("Concentrado de plaquetas com filtro") prescribed in the last 6h AND platelets>25000 AND absence of Melena / Enterorragia / AVC / TCE AND absence of a CVC / double-lumen dialysis catheter prescription in the last 4h. Feeds the VERMELHO al

**Question.** For the wired efficiency criterion 5 (reassess prophylactic platelet transfusion at Plq > 25,000 -> VERMELHO), do we ratify the intended logic reading the platelet value from the correct model field (evolucao, not the non-existent cpoe.diurna_plaquetas that makes the sole VERMELHO trigger permanently False), with the intended 4h catheter-exclusion window and a functioning I64 exclusion?

**Options.**

- **A** — Ratify: read plaquetas from evolucao.diurna_plaquetas (the correct model field), apply the > 25,000 cutoff, restore the intended 4h CVC/CDL exclusion window (fix the 6h copy-paste), and repair the inert I64 (AVC) exclusion; retain the working Melena/Enterorragia exclusion. *(risk: Low - makes the VERMELHO trigger actually evaluable so genuinely unjustified prophylactic platelet transfusions are flagged; the 25,000 cutoff is consistent with AABB 2015 (well above the 10k prophylactic and 20k pre-procedure thresholds).)*
- **B** — Preserve the legacy verbatim (platelet value read from the non-existent cpoe.diurna_plaquetas -> always 0 -> criterion permanently False; 4h window is 6h; I64 exclusion inert). *(risk: High - the SOLE wired VERMELHO trigger in the efficiency track never fires, so genuinely unjustified prophylactic platelet transfusions are silently never surfaced (missed high-priority alert): an entire red tier is dead.)*

**Recommended default.** A — The AABB 2015 platelet-transfusion guideline (Kaufman RM et al., Ann Intern Med 2015;162(3):205-213) sets the
prophylactic threshold at 10x10^9/L (10,000/uL) and 20,000/uL before elective central-line placement, with no
prophylactic indication above these absent a procedure or active bleeding - so the legacy 25,000/uL cutoff is
clinically reasonable. The DISCREPANCY is purely implementation: the platelet value is read from
ultima_cpoe.diurna_plaquetas, a field that does NOT exist on the CPOE model (it lives on evolucao), so getattr
returns 0 and '0 > 25000' is permanently False. Because this is the SOLE wired VERMELHO trigger in the
efficiency track (RULE-EFICIENCIA-001), the entire red tier never fires - a silent missed alert. Secondary:
the 4h CVC/CDL exclusion is copy-pasted as 6h and the I64 exclusion is inert (RULE-systemic-BE-03-001). Ratify.

**Disposition note.** RATIFY reading plaquetas from evolucao.diurna_plaquetas (correct model field) with the > 25,000/uL cutoff (AABB 2015-consistent), the intended 4h CVC/CDL exclusion window (fix the 6h copy-paste), and a functioning I64 (AVC) exclusion. Do NOT port the wrong-field read (cpoe.diurna_plaquetas -> permanently 0/False) that silently kills the sole wired VERMELHO trigger. Retain the Melena/Enterorragia exclusion. Wired to VERMELHO via calcular_alerta_v2; facade label RULE-EFICIENCIA-012. PT-BR strings preserved.

<a id="rat-sepse-06"></a>
### RAT-SEPSE-06 — RULE-SEPSE-044: Sepsis C7 (major) - oliguria or rising creatinine

> *`sepse` · `triage-eligibility` · DISCREPANCY/DISCREPANCY*  - **Legacy:** Major criterion - 24h urine output <= 1200 ml OR (creatinine > 2 AND not on hemodialysis). - **Deviation:** DISCREPANCY: fixed 1200 mL/24h threshold rather than weight-based (<0.5 mL/kg/h). _ANTIGAS_REGRAS used the weight-based version. Also debito==0 evaluates falsy so true 

**Question.** For sepsis major criterion C7 (oliguria or rising creatinine), do we ratify a weight-based oliguria threshold (KDIGO urine output < 0.5 mL/kg/h) with correct anuria handling (a recorded urine output of 0 mL must flag, not be treated as falsy/absent), replacing the legacy fixed <= 1200 mL/24h that both over-triggers on normal output and silently excludes true anuria?

**Options.**

- **A** — Ratify weight-based oliguria KDIGO < 0.5 mL/kg/h (or the SOFA < 500 mL/day cut) AND fix anuria handling so a recorded urine output of 0 mL flags (do not treat 0 as falsy/missing); retain the creatinina > 2 mg/dL not-on-hemodialysis disjunct. *(risk: Low - removes false positives from the 1200 mL/24h over-trigger (1200 mL/24h is normal output) and, critically, removes the false negative that currently excludes true anuria - the sickest AKI patients.)*
- **B** — Preserve the legacy verbatim (fixed <= 1200 mL/24h; debito == 0 falsy so anuria excluded). *(risk: High - bidirectional error: a normal 1200 mL/24h output fires this MAJOR sepsis criterion (false positive), while true anuria (0 mL, the most severe AKI) is silently excluded from the oliguria disjunct (false negative in the sickest patients).)*
- **C** — Keep a fixed mL/24h threshold but lower it to the SOFA < 500 mL/day cut and fix anuria handling. *(risk: Low-moderate - corrects the direction of both errors but retains a non-weight-based cut that mis-scores very small or very large patients versus KDIGO.)*

**Recommended default.** A — The SOFA renal component (Vincent JL et al., Intensive Care Med 1996;22:707-710) scores urine output < 500
mL/day (3 pts) and < 200 mL/day (4 pts), and KDIGO 2012 defines oliguric AKI as urine output < 0.5 mL/kg/h
(~840 mL/24h for a 70 kg adult). The legacy fixed <= 1200 mL/24h sits far above both cuts, so a normal 1200
mL/24h output fires this MAJOR criterion (false positive); worse, debito_urinario_24h == 0 evaluates falsy, so
true anuria - the most severe AKI presentation - is EXCLUDED from the oliguria disjunct (false negative in the
sickest, mitigated only if creatinine is concurrently > 2). The creatinina > 2 mg/dL not-on-HD disjunct
correctly aligns with the SOFA 2-point renal cutoff. A weight-based KDIGO threshold with correct anuria
handling is reference-correct; _ANTIGAS_REGRAS already used the weight-based form. MAJOR criterion: ratify.

**Disposition note.** RATIFY weight-based oliguria (KDIGO < 0.5 mL/kg/h, or SOFA < 500 mL/day) with correct anuria handling (urine output 0 mL must flag, not be treated as falsy/missing); retain creatinina > 2 mg/dL not-on-hemodialysis. Do NOT port the fixed <= 1200 mL/24h threshold (over-triggers on normal output) or the debito == 0 falsy anuria exclusion (false negative in the sickest). Weight-based form requires patient-weight capture. MAJOR criterion feeding the RULE-SEPSE-004 two-axis alert. PT-BR field 'debito urinario' preserved verbatim.


## UNVERIFIABLE — proprietary rules requiring owner confirmation (grouped)

<a id="grp-adt-b-lookup-key"></a>
### GRP-ADT-B-LOOKUP-KEY — Confirm proprietary rule intent: the bed micro-indicator lookup key collapses nr_atendimento + bed name into a

**Member rules (1):** RULE-MOVIMENTACAO-ADT-005

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-adt-b-los"></a>
### GRP-ADT-B-LOS — Confirm proprietary rule intent: bed/movimentacao length-of-stay (tempo de permanencia) computed as an elapsed

**Member rules (1):** RULE-MOVIMENTACAO-ADT-001

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-adt-b-mortality-score"></a>
### GRP-ADT-B-MORTALITY-SCORE — Confirm proprietary rule intent: the expected-mortality score (mortalidade_esperada) is surfaced in the ADT pa

**Member rules (1):** RULE-MOVIMENTACAO-ADT-003

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** B

<a id="grp-adt-b-payload-shape"></a>
### GRP-ADT-B-PAYLOAD-SHAPE — Confirm proprietary rule intent / defect status: two ADT serializer payload-shape issues — the bed/movimentaca

**Member rules (2):** RULE-MOVIMENTACAO-ADT-002, RULE-MOVIMENTACAO-ADT-008

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-adt-b-serializer-delegation"></a>
### GRP-ADT-B-SERIALIZER-DELEGATION — Confirm proprietary rule intent: four ADT serializer/view behaviors with no clinical formula — the bed 'assist

**Member rules (4):** RULE-MOVIMENTACAO-ADT-011, RULE-MOVIMENTACAO-ADT-006, RULE-MOVIMENTACAO-ADT-007, RULE-MOVIMENTACAO-ADT-010

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-alert-b-counting"></a>
### GRP-ALERT-B-COUNTING — Confirm proprietary rule intent: two alert-counting utilities verified byte-for-byte against source — contar_q

**Member rules (2):** RULE-ALERTAS-001, RULE-ALERTAS-002

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-audit-b-date-range"></a>
### GRP-AUDIT-B-DATE-RANGE — Confirm proprietary rule intent: the audit-log date-range filter's start-of-day/ end-of-day boundary formula (

**Member rules (1):** RULE-AUDITORIA-LOGS-001

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-auth-b-payloads"></a>
### GRP-AUTH-B-PAYLOADS — Confirm proprietary rule intent: two access-control payload computations verified byte-faithful to source — th

**Member rules (2):** RULE-AUTH-USUARIOS-001, RULE-AUTH-USUARIOS-002

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-bh-data-sourcing"></a>
### GRP-BH-DATA-SOURCING — Confirm proprietary rule intent: fluid-balance data-sourcing edge cases — the active 24h formulario aggregatio

**Member rules (3):** RULE-BALANCO-HIDRICO-012, RULE-BALANCO-HIDRICO-017, RULE-BALANCO-HIDRICO-028

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-bh-default-volumes"></a>
### GRP-BH-DEFAULT-VOLUMES — Confirm proprietary rule intent: default charting volumes — enteral diet intake defaults to a fixed volume onl

**Member rules (2):** RULE-BALANCO-HIDRICO-020, RULE-BALANCO-HIDRICO-021

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-bh-display-composition"></a>
### GRP-BH-DISPLAY-COMPOSITION — Confirm proprietary rule intent: blood-pressure display composition (RULE-BALANCO-HIDRICO-018) — pas (systolic

**Member rules (1):** RULE-BALANCO-HIDRICO-018

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-bh-shift-window"></a>
### GRP-BH-SHIFT-WINDOW — Confirm proprietary rule intent: 07:00-anchored nursing-shift conventions for fluid balance — day-shift balanc

**Member rules (4):** RULE-BALANCO-HIDRICO-004, RULE-BALANCO-HIDRICO-005, RULE-BALANCO-HIDRICO-023, RULE-BALANCO-HIDRICO-024

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-bh-vocab"></a>
### GRP-BH-VOCAB — Confirm proprietary rule intent: fluid-balance vocabulary/enum lists — the AVDI-like consciousness-level selec

**Member rules (3):** RULE-BALANCO-HIDRICO-059, RULE-BALANCO-HIDRICO-056, RULE-BALANCO-HIDRICO-057

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-com-b-reaction-aggregation"></a>
### GRP-COM-B-REACTION-AGGREGATION — Confirm proprietary rule intent / defect status: three communication (reaction/ observation) behaviors — the A

**Member rules (3):** RULE-COMUNICACAO-003, RULE-COMUNICACAO-001, RULE-COMUNICACAO-002

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** B

<a id="grp-docfat-b-amhdocs"></a>
### GRP-DOCFAT-B-AMHDOCS — Confirm proprietary rule intent: two AMHDocs external-integration proxy behaviors — the file lookup that alway

**Member rules (2):** RULE-DOCUMENTACAO-FATURAMENTO-027, RULE-DOCUMENTACAO-FATURAMENTO-028

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-eff-b-frailty"></a>
### GRP-EFF-B-FRAILTY — Confirm proprietary rule intent: Eficiencia v3 criterio_6, frailty/palliative- appropriateness, defined but UN

**Member rules (1):** RULE-EFICIENCIA-009

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-est-b-drug-combination"></a>
### GRP-EST-B-DRUG-COMBINATION — Confirm proprietary rule intent: two Estabilidade drug-combination safety rules with facility-specific ml/h/mg

**Member rules (2):** RULE-ESTABILIDADE-010, RULE-ESTABILIDADE-022

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-etl-b-dashboard-proportions"></a>
### GRP-ETL-B-DASHBOARD-PROPORTIONS — Confirm proprietary rule intent: sector-dashboard proportion/formatting conventions — the dual-y-axis Chart.js

**Member rules (3):** RULE-INDICADORES-ETL-010, RULE-INDICADORES-ETL-001, RULE-INDICADORES-ETL-002

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-evol-b-data-shape"></a>
### GRP-EVOL-B-DATA-SHAPE — Confirm proprietary rule intent: two EVOLUCOES data-shape conventions — the cardiac-arrest occurrence flag typ

**Member rules (2):** RULE-EVOLUCOES-004, RULE-EVOLUCOES-005

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-evol-b-score-display"></a>
### GRP-EVOL-B-SCORE-DISPLAY — Confirm proprietary rule intent: the medical-record clinical panel surfaces a pre-computed, opaque escore_sofa

**Member rules (2):** RULE-EVOLUCOES-001, RULE-EVOLUCOES-002

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-form-b-capture"></a>
### GRP-FORM-B-CAPTURE — Confirm proprietary rule intent: two clinical-form capture conventions — the nursing-technician high-cost drug

**Member rules (2):** RULE-FORMULARIOS-CLINICOS-014, RULE-FORMULARIOS-CLINICOS-042

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-infra-b-duration-pagination"></a>
### GRP-INFRA-B-DURATION-PAGINATION — Confirm proprietary rule intent: internal duration/pagination arithmetic — length-of-stay computed via whole-d

**Member rules (3):** RULE-OPERACIONAL-INFRA-006, RULE-OPERACIONAL-INFRA-007, RULE-OPERACIONAL-INFRA-008

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-infra-offline-rx"></a>
### GRP-INFRA-OFFLINE-RX — Confirm proprietary rule intent: offline-prescription day-grouping/windowing/rollover — prescriptions grouped 

**Member rules (3):** RULE-OPERACIONAL-INFRA-003, RULE-OPERACIONAL-INFRA-004, RULE-OPERACIONAL-INFRA-005

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-infra-string-parse-utils"></a>
### GRP-INFRA-STRING-PARSE-UTILS — Confirm proprietary rule intent: internal string/parsing utility helpers — patient-name abbreviation with Port

**Member rules (4):** RULE-OPERACIONAL-INFRA-002, RULE-OPERACIONAL-INFRA-009, RULE-OPERACIONAL-INFRA-010, RULE-OPERACIONAL-INFRA-011

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-pc-b-consciousness-ladder"></a>
### GRP-PC-B-CONSCIOUSNESS-LADDER — Confirm proprietary rule intent: Piora Clinica criterio_5 consciousness graded sub-score, whose '+' (deteriora

**Member rules (1):** RULE-PIORA-CLINICA-005

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-pc-b-graded-bands"></a>
### GRP-PC-B-GRADED-BANDS — Confirm proprietary rule intent: Piora Clinica proprietary graded sub-score cutoffs with no authoritative exte

**Member rules (3):** RULE-PIORA-CLINICA-001, RULE-PIORA-CLINICA-003, RULE-PIORA-CLINICA-011

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-presc-b-fluid-export"></a>
### GRP-PRESC-B-FLUID-EXPORT — Confirm proprietary rule intent: ml-unit medications capture an exported quantity (qtd_exportada) for fluid-ba

**Member rules (1):** RULE-PRESCRICAO-001

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-sed-b-drug-vocab"></a>
### GRP-SED-B-DRUG-VOCAB — Confirm proprietary rule intent: sedation drug identification/vocabulary conventions — the active-sedative lab

**Member rules (3):** RULE-SEDACAO-013, RULE-SEDACAO-025, RULE-SEDACAO-026

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-sed-b-manual-composite"></a>
### GRP-SED-B-MANUAL-COMPOSITE — Confirm proprietary rule intent: three sedation-manual composite criteria (C4-C6) built on P/F ratio and RASS 

**Member rules (3):** RULE-SEDACAO-018, RULE-SEDACAO-019, RULE-SEDACAO-020

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-sed-b-volumetric-dosing"></a>
### GRP-SED-B-VOLUMETRIC-DOSING — Confirm proprietary rule intent: two sedation-pathway criteria expressed as fixed volumetric infusion-rate cut

**Member rules (2):** RULE-SEDACAO-005, RULE-SEDACAO-010

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-sepse-device-dwell"></a>
### GRP-SEPSE-DEVICE-DWELL — Confirm proprietary rule intent: invasive-device dwell-time infection-risk thresholds across sepsis criteria —

**Member rules (5):** RULE-SEPSE-036, RULE-SEPSE-024, RULE-SEPSE-055, RULE-SEPSE-025, RULE-SEPSE-056

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-sepse-dual-threshold"></a>
### GRP-SEPSE-DUAL-THRESHOLD — Confirm proprietary rule intent: sepsis dual-axis major/minor threshold aggregation (v1 RULE-SEPSE-001 and v3 

**Member rules (2):** RULE-SEPSE-001, RULE-SEPSE-004

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-sepse-internal-conventions"></a>
### GRP-SEPSE-INTERNAL-CONVENTIONS — Confirm proprietary rule intent: internal sepsis data conventions — the consciousness- level ordinal hierarchy

**Member rules (2):** RULE-SEPSE-005, RULE-SEPSE-006

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-sepse-major-timing"></a>
### GRP-SEPSE-MAJOR-TIMING — Confirm proprietary rule intent: major sepsis screening criteria keyed on recent escalation timing — respirato

**Member rules (3):** RULE-SEPSE-029, RULE-SEPSE-040, RULE-SEPSE-041

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-sepse-minor-gcs-gated"></a>
### GRP-SEPSE-MINOR-GCS-GATED — Confirm proprietary rule intent: minor sepsis criteria gated on preserved consciousness (GCS>=13) — enteral tu

**Member rules (2):** RULE-SEPSE-023, RULE-SEPSE-053

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-sepse-surgery-recency"></a>
### GRP-SEPSE-SURGERY-RECENCY — Confirm proprietary rule intent: "recent surgery" minor sepsis criterion in both the v3 automatic pathway (RUL

**Member rules (2):** RULE-SEPSE-026, RULE-SEPSE-057

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-sv-b-dose-validators"></a>
### GRP-SV-B-DOSE-VALIDATORS — Confirm proprietary rule intent: two input-capture dose-range validators with undocumented units — DobutaminaV

**Member rules (2):** RULE-SINAIS-VITAIS-029, RULE-SINAIS-VITAIS-030

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-ten-chat-ordering"></a>
### GRP-TEN-CHAT-ORDERING — Confirm proprietary rule intent: sector chat preview selects the first related Observacao without an explicit 

**Member rules (1):** RULE-TENANCY-ORGANIZACAO-014

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-ten-indicator-agg"></a>
### GRP-TEN-INDICATOR-AGG — Confirm proprietary rule intent: sector/establishment macro-indicator aggregation behaviors — establishment-le

**Member rules (4):** RULE-TENANCY-ORGANIZACAO-005, RULE-TENANCY-ORGANIZACAO-006, RULE-TENANCY-ORGANIZACAO-015, RULE-TENANCY-ORGANIZACAO-038

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-ten-merge-pattern"></a>
### GRP-TEN-MERGE-PATTERN — Confirm proprietary rule intent: sector counters that merge manual-movement records with automatic-pathway rec

**Member rules (2):** RULE-TENANCY-ORGANIZACAO-011, RULE-TENANCY-ORGANIZACAO-013

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-ten-messaging-counts"></a>
### GRP-TEN-MESSAGING-COUNTS — Confirm proprietary rule intent: unread-message counters — the establishment-level count sums unread messages 

**Member rules (2):** RULE-TENANCY-ORGANIZACAO-007, RULE-TENANCY-ORGANIZACAO-008

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-ten-scoping-todo"></a>
### GRP-TEN-SCOPING-TODO — Confirm proprietary rule intent: company-wide and establishment-level "indicadores" action access-scoping (RUL

**Member rules (2):** RULE-TENANCY-ORGANIZACAO-041, RULE-TENANCY-ORGANIZACAO-042

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

<a id="grp-ten-sector-display-count"></a>
### GRP-TEN-SECTOR-DISPLAY-COUNT — Confirm proprietary rule intent: sector display/counting utilities — active-beds-only totals (RULE-TENANCY-ORG

**Member rules (3):** RULE-TENANCY-ORGANIZACAO-012, RULE-TENANCY-ORGANIZACAO-009, RULE-TENANCY-ORGANIZACAO-010

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-trilha-b-dosing-image"></a>
### GRP-TRILHA-B-DOSING-IMAGE — Confirm proprietary rule intent: the per-criterion drug-dosing reference image UI feature (a 'Dosagens' modal 

**Member rules (1):** RULE-TRILHAS-ENGINE-017

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** A

<a id="grp-vent-b-duration"></a>
### GRP-VENT-B-DURATION — Confirm proprietary rule intent: days-on-mechanical-ventilation duration helper (buscar_dias_com_ventilacao_me

**Member rules (1):** RULE-VENTILACAO-002

- **A** — 
- **B** — 
- **C** — 

**Recommended default.** C

## ADDENDUM — Phase-6 security/compliance findings (3 items)

<a id="rat-sepse-add-01"></a>
### RAT-SEPSE-ADD-01 — RULE-SEPSE-099: Manual sepsis pathway active criteria descriptions (_REGRAS, 20 criteria) with criterio_8 

> *Cluster:* `sepse` · *Category:* `triage-eligibility` · *Extraction:* DISCREPANCY · *Verification:* NOT_APPLICABLE · *Suggested band:* P2 (low clinical impact)  - **Legacy:** The active `_REGRAS` dict on `TrilhaSepse` (manual sepsis pathway) defines `total_criterios=20` and the human-readable clinical description text for criteria `criterio_1`..`cr

**Question.** For the active manual sepsis pathway _REGRAS descriptions, do we ratify correcting the criterio_8 key-typo (line 114 reads 'criterio8' without the underscore, so descricao_criterio_8 always defaults to None and silently drops the Glasgow-decline/delirium criterion's clinical description text)?

**Options.**

- **A** — Ratify the fix: read _REGRAS.get('criterio_8') so descricao_criterio_8 carries the intended Glasgow-decline / delirium description text. *(risk: Low - restores the human-readable description for a functioning criterion; the boolean criterio_8 evaluation is unaffected, only its displayed/stored description text is corrected.)*
- **B** — Preserve the legacy 'criterio8' key-typo verbatim. *(risk: Moderate (display/traceability) - criterion 8 (acute Glasgow decline / delirium, a neurologic sepsis organ-dysfunction signal) fires with a blank description wherever descricao_criterio_8 is read/exposed, degrading clinician interpretability and audit traceability of why the criterion flagged.)*

**Recommended default.** A — RULE-SEPSE-099 documents a live, silent key-typo. On TrilhaSepse the active _REGRAS dict defines
total_criterios=20 and per-criterion description text, but line 114 looks up 'criterio8' (missing underscore)
instead of 'criterio_8', so descricao_criterio_8 always defaults to None. The boolean criterion still
functions, but its clinical description - the acute Glasgow-Coma-Scale drop of >= 2 points over 24h OR
delirium - is silently dropped wherever the description is displayed or persisted. Restoring the correct key is
an unambiguous reference-correct fix (the intended text is already present in _REGRAS) with no change to
firing logic; because it is part of the manual sepsis screen surfaced to clinicians, it is ratified with the
clinical committee for confirmation of the description wording. Verification is NOT_APPLICABLE (display rule).

**Disposition note.** RATIFY the criterio_8 key fix (_REGRAS.get('criterio_8') at line 114) so the Glasgow-decline/delirium description is no longer dropped. Do NOT port the 'criterio8' typo. No change to boolean firing logic (total_criterios=20 unchanged). Clinical committee to confirm the PT-BR description wording, preserved verbatim: 'Presenca de reducao numerica da escala de coma de Glasgow em dois pontos ou mais nas ultimas 24 horas (comparar com o ultimo checklist) OU presenca de delirium' (accents per source). _ANTIGAS_REGRAS (27 criteria) is deprecated/superseded; _REGRAS (20) is active. Related RULE-SEPSE-066.

<a id="rat-auth-usuarios-02"></a>
### RAT-AUTH-USUARIOS-02 — RULE-AUTH-USUARIOS-063: Shared default signing PIN (Usuario.pin defaults to settings.PIN_DEFAULT)

> *Cluster:* `auth-usuarios` · *Category:* `access-control` · *Extraction:* OK · *Verification:* NOT_APPLICABLE · *Priority:* HIGH (security/compliance review)  - **Legacy:** `Usuario.pin` ("PIN para assinar com o CryptoCubo") defaults to `settings.PIN_DEFAULT`, an env-configurable, deployment-wide value (`trilhas/settings.py:245`, `PIN_DEFAULT = os.

**Question.** For electronic signing of clinical documents, do we ratify requiring a unique per-user signing PIN - eliminating the org-wide shared default (Usuario.pin defaults to settings.PIN_DEFAULT) that is base64-encoded and submitted verbatim as the CryptoCubo signing credential - subject to legal review against MP 2.200-2 / ICP-Brasil signature-attribution requirements?

**Options.**

- **A** — Ratify eliminating the shared default: require each user to set a unique signing PIN (no deployment-wide default), enforce PIN rotation, and never fall back to settings.PIN_DEFAULT; refer to legal for confirmation against MP 2.200-2 / ICP-Brasil per-signatory attribution. *(risk: Low (security-positive) - restores per-user attributability of legally-binding electronic signatures on medical documents/prescriptions and aligns with e-signature integrity/non-repudiation requirements.)*
- **B** — Preserve the legacy shared settings.PIN_DEFAULT default. *(risk: High (legal/compliance) - any user whose PIN was never rotated signs medical/legal documents with an org-wide shared secret, so signatures are non-attributable to an individual signatory, undermining the legal validity and auditability of the signature and likely violating MP 2.200-2 / ICP-Brasil attribution requirements.)*

**Recommended default.** A — RULE-AUTH-USUARIOS-063 documents that Usuario.pin ('PIN para assinar com o CryptoCubo') defaults to
settings.PIN_DEFAULT (os.environ.get('PIN_DEFAULT'), a single deployment-wide value), and utils/cryptocubo.py
base64-encodes that PIN and submits it verbatim as the live signing credential. Every user created without an
explicit PIN inherits the same shared secret, making electronic signatures on clinical documents and
prescriptions non-attributable to an individual signatory. Under Brazil's MP 2.200-2/2001 (ICP-Brasil), a
legally valid electronic signature must be uniquely bound to and controlled by its signatory; a shared default
PIN defeats that binding and the non-repudiation it confers. This is audit ratification ask #3 (e-signature
legal review): the reference-correct default is a unique, rotated, per-user PIN with no shared fallback.

**Disposition note.** RATIFY a unique per-user signing PIN with enforced rotation and NO deployment-wide settings.PIN_DEFAULT fallback; refer to legal/compliance for confirmation against MP 2.200-2 / ICP-Brasil signatory-attribution and non-repudiation requirements (audit ratification ask #3, e-signature legal review). Do NOT port the shared default. Couple with RULE-DOCUMENTACAO-FATURAMENTO-032 (ESC-ADDENDUM-351, signature profile) and RULE-AUTH-USUARIOS-031 (password hashing). Note: if PIN_DEFAULT is unset the default is None, triggering the downstream .encode() crash path. Verification NOT_APPLICABLE (non-formula access-control rule). PT-BR field label preserved verbatim.

<a id="rat-documentacao-faturamento-add-01"></a>
### RAT-DOCUMENTACAO-FATURAMENTO-ADD-01 — RULE-DOCUMENTACAO-FATURAMENTO-032: Default electronic-signature configuration for CryptoCubo document signing

> *Cluster:* `documentacao-faturamento` · *Category:* `data-validation` · *Extraction:* OK · *Verification:* NOT_APPLICABLE · *Priority:* HIGH (security/compliance review)  - **Legacy:** `DocumentosCryptocubo.__init__` hardcodes the default electronic-signature configuration used to legally sign clinical documents (evolutions/forms) through the Crypt

**Question.** For the CryptoCubo electronic-signature defaults used to legally sign clinical documents, do we ratify the required signature profile - specifically whether signatures must use a 'qualified' / ICP-Brasil-enabled profile (icpbr=True) rather than the legacy default of tipo='advanced' with icpbr=False (ICP-Brasil root chain disabled) - subject to legal review under MP 2.200-2 / ICP-Brasil?

**Options.**

- **A** — Ratify a legally-reviewed signature profile: escalate the default to 'qualified' with ICP-Brasil enabled (icpbr=True) where the document type legally requires a qualified signature, per legal determination under MP 2.200-2 / ICP-Brasil; make the profile explicit rather than an unreviewed keyword default. *(risk: Low (compliance-positive) - ensures clinical/legal documents carry the signature strength the law requires and that ICP-Brasil validation is applied.)*
- **B** — Preserve the legacy defaults (tipo='advanced', perfil='adrb', icpbr=False). *(risk: High (legal/compliance) - every document signed on this path uses an 'advanced' (not 'qualified') signature with the ICP-Brasil root chain disabled, potentially failing the legal-validity/evidentiary bar for clinical records under MP 2.200-2 / ICP-Brasil and exposing signed evolutions/prescriptions to challenge.)*

**Recommended default.** A — RULE-DOCUMENTACAO-FATURAMENTO-032 documents that DocumentosCryptocubo.__init__ hardcodes the signature
defaults tipo='advanced' (NOT 'qualified'), formato='pdf', perfil='adrb', icpbr=False (ICP-Brasil root chain
off), and interpolates them into the CryptoCubo sign/verify URLs - so unless a caller overrides them, every
clinical document (evolutions/forms) is signed with an advanced, non-ICP-Brasil signature. Under MP
2.200-2/2001, a 'qualified' signature backed by an ICP-Brasil certificate carries a legal presumption of
authenticity that an 'advanced' signature with the root chain disabled does not; the required strength depends
on the legal classification of each document type. This is audit ratification ask #3 (e-signature legal
review): the reference-correct behaviour is a legally-determined, explicit profile, ratified with legal.

**Disposition note.** RATIFY a legal-review-determined CryptoCubo signature profile: escalate to 'qualified' / ICP-Brasil-enabled (icpbr=True) where the document class legally requires it under MP 2.200-2 / ICP-Brasil, and make the profile explicit rather than an unreviewed keyword default (audit ratification ask #3, e-signature legal review). Do NOT port tipo='advanced'/icpbr=False as an unreviewed default. Couple with RULE-AUTH-USUARIOS-063 (ESC-ADDENDUM-350, per-user signing PIN): signature strength and signatory attribution together determine legal validity. Verification NOT_APPLICABLE (non-formula data-validation rule). Config values preserved verbatim.


## AMBIGUOUS extractions — keep-vs-retire recommendations

| Item | Rule | Drafter recommendation | Disposition |
|---|---|---|---|
| ESC-AMBIGUOUS-293 | RULE-ALERTAS-014 | RATIFY: The disabled 'Risco para SEPSE: realizar abertura do Protocolo Institucional' fixed messag | RATIFY |
| ESC-AMBIGUOUS-294 | RULE-ALERTAS-025 | RETIRE-RECOMMENDED: Purely a UI color-token vocabulary (success/info/warning/danger/error) with no clinical lo | RETIRE |
| ESC-AMBIGUOUS-295 | RULE-ANTIMICROBIANO-002 | RETIRE-RECOMMENDED: Extraction explicitly notes this alert-color logic is legacy and unused (dead calcular_ale | RETIRE |
| ESC-AMBIGUOUS-296 | RULE-VENTILACAO-016 | RETIRE-RECOMMENDED: Ventilacao v1 alert coloring is unused legacy code (superseded by v3 trilha_automatica). N | RETIRE |
| ESC-AMBIGUOUS-297 | RULE-BALANCO-HIDRICO-045 | RATIFY: Encodes the recurring 'sign to finalize, soft-delete not hard-delete' medical-legal record | RATIFY |
| ESC-AMBIGUOUS-298 | RULE-EVOLUCOES-011 | RATIFY: can_liberar gates release of a clinical evolution note on tipo+liberar+cpf+nr_atendimento  | RETIRE |
| ESC-AMBIGUOUS-299 | RULE-EVOLUCOES-017 | RATIFY: Physician-form vitals submission auto-creates/attaches a daily balanco_hidrico record via  | RATIFY |
| ESC-AMBIGUOUS-300 | RULE-FORMULARIOS-CLINICOS-017 | RETIRE-RECOMMENDED: A cosmetic icon assignment for the 'intercorrencia' concept in the UI; carries no clinical | RETIRE |
| ESC-AMBIGUOUS-301 | RULE-FORMULARIOS-CLINICOS-037 | RETIRE-RECOMMENDED: Discipline-to-icon mapping for the multidisciplinary care team is pure UI iconography with | RATIFY |
| ESC-AMBIGUOUS-302 | RULE-PRESCRICAO-028 | RATIFY: Medication administration/cancellation lifecycle (administrado/suspenso/motivo_nao_adminis | RETIRE |
| ESC-AMBIGUOUS-303 | RULE-PROFILAXIA-008 | RATIFY: The active v3 prophylaxis facade fires on only 2 of the original 9 criteria (LAMGD + inser | RATIFY |
| ESC-AMBIGUOUS-304 | RULE-SEDACAO-022 | RATIFY: Defines 'cardiac arrest within last 24h' as timedelta.days==0 (a rolling <24h window, not  | RATIFY |
| ESC-AMBIGUOUS-305 | RULE-SEPSE-086 | RETIRE-RECOMMENDED: A frontend history-tab query filter ({aceito: false}) whose semantics ('pending review' vs | RETIRE |
| ESC-AMBIGUOUS-306 | RULE-SEPSE-093 | RATIFY: Two distinct sepsis-pathway completion flags (finalizado vs. concluida) with no code disti | RATIFY |
| ESC-AMBIGUOUS-307 | RULE-TRILHAS-ENGINE-003 | RETIRE-RECOMMENDED: get_trilha's 'automatica' branch picks a pathway record with no explicit ordering (impleme | RATIFY |
| ESC-AMBIGUOUS-308 | RULE-TRILHAS-ENGINE-012 | RATIFY: v3 pathway bootstrap re-fetches pathway instances via .first() with no nr_atendimento filt | RATIFY |
| ESC-AMBIGUOUS-309 | RULE-TRILHAS-ENGINE-013 | RETIRE-RECOMMENDED: A cosmetic display-name humanizer (hardcoded 6-char 'trilha' prefix split). Pure UI string | RETIRE |
| ESC-AMBIGUOUS-310 | RULE-TRILHAS-ENGINE-015 | RATIFY: Requiring a mandatory free-text justification (motivo_descartado) to refuse a care-pathway | RATIFY |
| ESC-AMBIGUOUS-311 | RULE-DOCUMENTACAO-FATURAMENTO-014 | RETIRE-RECOMMENDED: A double permission-gate (SSR cookie check + client hook re-check) on the evolution report | RATIFY |
| ESC-AMBIGUOUS-312 | RULE-SEPSE-066 | RATIFY: Documents 7 sepsis criteria (invasive-device duration, recent abdominal surgery, early ant | RETIRE |
| ESC-AMBIGUOUS-313 | RULE-AUDITORIA-LOGS-025 | RETIRE-RECOMMENDED: A UUID-in-path display normalization not applied to the underlying route-aggregation stats | RETIRE |
| ESC-AMBIGUOUS-314 | RULE-AUDITORIA-LOGS-028 | RETIRE-RECOMMENDED: Authenticated-user attribution on audit log entries is generic infrastructure logging beha | RETIRE |
| ESC-AMBIGUOUS-315 | RULE-AUDITORIA-LOGS-032 | RETIRE-RECOMMENDED: An is_html content-sniffing heuristic with broad false-positive risk is a technical loggin | RETIRE |
| ESC-AMBIGUOUS-316 | RULE-AUDITORIA-LOGS-034 | RETIRE-RECOMMENDED: A country->region->city cascading filter bug (city not re-scoped by country) in an admin l | RETIRE |
| ESC-AMBIGUOUS-317 | RULE-AUTH-USUARIOS-056 | RETIRE-RECOMMENDED: exceto_metodo literally misspells PATCH as PATH across write viewsets — an obvious legacy  | RETIRE |
| ESC-AMBIGUOUS-318 | RULE-BALANCO-HIDRICO-062 | RETIRE-RECOMMENDED: Extraction notes this day-scoped fluid-balance filter is unused. No live behavior depends  | RETIRE |
| ESC-AMBIGUOUS-319 | RULE-CADASTROS-UI-001 | RETIRE-RECOMMENDED: FilterLeitos sends a tri-state occupancy filter as a literal string rather than a structur | RETIRE |
| ESC-AMBIGUOUS-320 | RULE-CADASTROS-UI-005 | RETIRE-RECOMMENDED: New-user password auto-filled from the user's own CPF is a security anti-pattern (predicta | RATIFY |
| ESC-AMBIGUOUS-321 | RULE-CADASTROS-UI-006 | RATIFY: Every user's electronic-signature PIN defaults to the same hardcoded literal ('Homecare@Vi | RATIFY |
| ESC-AMBIGUOUS-322 | RULE-COMUNICACAO-041 | RETIRE-RECOMMENDED: Observation setor_id is always forced from the URL rather than from payload — a request-bi | RATIFY |
| ESC-AMBIGUOUS-323 | RULE-COMUNICACAO-045 | RETIRE-RECOMMENDED: FilePicker only reconciles its local file list on removal (a UI state-sync bug in file upl | RATIFY |
| ESC-AMBIGUOUS-324 | RULE-DOCUMENTACAO-FATURAMENTO-017 | RETIRE-RECOMMENDED: Default sort order for a bed-file listing UI is a cosmetic presentation choice, not a clin | RETIRE |
| ESC-AMBIGUOUS-325 | RULE-DOCUMENTACAO-FATURAMENTO-024 | RATIFY: Cross-references a Trilhas-vs-CPOE prescription-item signature-inconsistency record used f | RETIRE |
| ESC-AMBIGUOUS-326 | RULE-EVOLUCOES-018 | RETIRE-RECOMMENDED: A company-wide evolutions queryset filter with a possible instance-vs-id type mismatch is  | RETIRE |
| ESC-AMBIGUOUS-327 | RULE-EVOLUCOES-022 | RETIRE-RECOMMENDED: A single-checkbox form 'conditions' key mismatch is a frontend form-wiring bug with no cli | RETIRE |
| ESC-AMBIGUOUS-328 | RULE-EVOLUCOES-048 | RETIRE-RECOMMENDED: Dual query-parameter encoding on an evolution-report fetch endpoint is an HTTP/request-plu | RETIRE |
| ESC-AMBIGUOUS-329 | RULE-EVOLUCOES-074 | RATIFY: Form-group 'annulment' (soft-void rather than delete, via anulavel/isAnnulled) is inferred | RATIFY |
| ESC-AMBIGUOUS-330 | RULE-FORMULARIOS-CLINICOS-039 | RETIRE-RECOMMENDED: Binary Masculino/Feminino iconography is a cosmetic UI choice, not a clinical rule or thre | RATIFY |
| ESC-AMBIGUOUS-331 | RULE-MOVIMENTACAO-ADT-048 | RETIRE-RECOMMENDED: A fixed 3-second minimum loading-spinner on the bed camera page is a cosmetic UX timing ch | RETIRE |
| ESC-AMBIGUOUS-332 | RULE-MOVIMENTACAO-ADT-049 | RETIRE-RECOMMENDED: Test/temporary-bed exclusion uses AND semantics (all three substrings must match) where th | RETIRE |
| ESC-AMBIGUOUS-333 | RULE-MOVIMENTACAO-ADT-058 | RETIRE-RECOMMENDED: Extraction itself flags this as unverifiable — the observed 400 is fully explained by a co | RETIRE |
| ESC-AMBIGUOUS-334 | RULE-OPERACIONAL-INFRA-017 | RETIRE-RECOMMENDED: ParanoiaMixin's admin-path hard-delete vs. cascading soft-delete split is a Django ORM/inf | RATIFY |
| ESC-AMBIGUOUS-335 | RULE-OPERACIONAL-INFRA-037 | RETIRE-RECOMMENDED: ListChoiceField's context-dependent serialization switch is a DRF serializer implementatio | RATIFY |
| ESC-AMBIGUOUS-336 | RULE-PRESCRICAO-036 | RATIFY: A validator preventing any alteration to a dose's 'administrado' status once set is unused | RATIFY |
| ESC-AMBIGUOUS-337 | RULE-SEPSE-068 | RATIFY: The urea input field (key 'ureia_maior_50_24hrs') is stored as an unbounded raw number des | RATIFY |
| ESC-AMBIGUOUS-338 | RULE-SEPSE-098 | RATIFY: Sepsis-checklist signers uniquely capture a CPF (unlike Prescricao/BalancoHidrico/Chat 'ch | RATIFY |
| ESC-AMBIGUOUS-339 | RULE-SINAIS-VITAIS-033 | RATIFY: SpO2 validation (21-100, no zero exemption) is defined but its enforcement is commented ou | RATIFY |
| ESC-AMBIGUOUS-340 | RULE-TENANCY-ORGANIZACAO-020 | RETIRE-RECOMMENDED: LeitoMiddleware's missing cross-tenant consistency check (unlike the sibling Empresa/Estab | RETIRE |
| ESC-AMBIGUOUS-341 | RULE-OPERACIONAL-INFRA-040 | RETIRE-RECOMMENDED: Per-environment deploy scripts with asymmetric env-file loading are pure DevOps/CI plumbin | RATIFY |
| ESC-AMBIGUOUS-342 | RULE-OPERACIONAL-INFRA-059 | RETIRE-RECOMMENDED: A per-company dashboard auto-refresh interval is an operational UI configuration knob, not | RATIFY |
| ESC-AMBIGUOUS-343 | RULE-AUDITORIA-LOGS-021 | RETIRE-RECOMMENDED: A soft-delete mixin present on the log model but never exercised is unused legacy infrastr | RETIRE |
| ESC-AMBIGUOUS-344 | RULE-AUDITORIA-LOGS-022 | RETIRE-RECOMMENDED: Log dashboard access control (authenticated-only, no staff/ownership check) is an access-c | RATIFY |
| ESC-AMBIGUOUS-345 | RULE-AUTH-USUARIOS-045 | RETIRE-RECOMMENDED: A backend-vs-frontend type mismatch on user access-role codes (proprietario/usuario/monito | RATIFY |
| ESC-AMBIGUOUS-346 | RULE-AUTH-USUARIOS-047 | RETIRE-RECOMMENDED: A dormant read/read-write access-level enumeration with no active enforcement path is unus | RETIRE |
| ESC-AMBIGUOUS-347 | RULE-DOCUMENTACAO-FATURAMENTO-015 | RETIRE-RECOMMENDED: Auto-posting a released evolution to the Tasy EMR (billing lancamento code 501) is exactly | RETIRE |
| ESC-AMBIGUOUS-348 | RULE-FORMULARIOS-CLINICOS-040 | RETIRE-RECOMMENDED: Duplicate route registration for the enfermagem (nursing) form is a routing-configuration  | RETIRE |

## Additional RATIFY dispositions (not escalation-driven) (43)

| Ref | Rule | Why |
|---|---|---|
| <a id="rat-alertas-03"></a>RAT-ALERTAS-03 | RULE-ALERTAS-014 | A disabled sepsis-protocol prompt message and an automatica-only whitelist filter that can silently drop RED-a |
| <a id="rat-auditoria-logs-02"></a>RAT-AUDITORIA-LOGS-02 | RULE-AUDITORIA-LOGS-022 | Any authenticated user, not just staff, can browse every other user's IP, geolocation, and request/response bo |
| <a id="rat-auth-usuarios-01"></a>RAT-AUTH-USUARIOS-01 | RULE-AUTH-USUARIOS-045 | The 'm' (monitor) access code is defined and labeled on the backend but never mutated or enforced by any in-sc |
| <a id="rat-balanco-hidrico-17"></a>RAT-BALANCO-HIDRICO-17 | RULE-BALANCO-HIDRICO-045 | Status AMBIGUOUS with escalation band AMBIGUOUS: the ativo/data_assinatura/deletado_por/can_delete/can_assinar |
| <a id="rat-cadastros-ui-01"></a>RAT-CADASTROS-UI-01 | RULE-CADASTROS-UI-005 | Whether defaulting a brand-new user's password to their own semi-public CPF digits was an intentional convenie |
| <a id="rat-cadastros-ui-02"></a>RAT-CADASTROS-UI-02 | RULE-CADASTROS-UI-006 | A shared hardcoded 'signature PIN' literal ('Homecare@Vidaconecta') applied to every user could be either an i |
| <a id="rat-clinical-scoring-06"></a>RAT-CLINICAL-SCORING-06 | RULE-CLINICAL-SCORING-014 | Whether trilha_homecare's divergent RASS labels (-1 Sonolento, -4 Sedacao Intensa, -5 Nao desperta, and omissi |
| <a id="rat-comunicacao-01"></a>RAT-COMUNICACAO-01 | RULE-COMUNICACAO-026 | Hardcoded trilhasMock with fixed NEUTRO alert state is flagged DISCREPANCY and its escalation band is P3, but  |
| <a id="rat-comunicacao-02"></a>RAT-COMUNICACAO-02 | RULE-COMUNICACAO-027 | The reaction hard-delete override is an explicit deviation from the platform's dominant soft-delete convention |
| <a id="rat-comunicacao-03"></a>RAT-COMUNICACAO-03 | RULE-COMUNICACAO-034 | Both the homecare-bed-type guard and the unoccupied-bed guard for feed actions are confirmed entirely unenforc |
| <a id="rat-comunicacao-04"></a>RAT-COMUNICACAO-04 | RULE-COMUNICACAO-035 | The acaoDict (8 keys, including PT-BR verbatim labels Criar/Alterar/Editar/Inativar/Assinar/Liberar/Administra |
| <a id="rat-comunicacao-05"></a>RAT-COMUNICACAO-05 | RULE-COMUNICACAO-041 | Status AMBIGUOUS with escalation band AMBIGUOUS: the intended validation message for a missing setor__pk never |
| <a id="rat-comunicacao-06"></a>RAT-COMUNICACAO-06 | RULE-COMUNICACAO-045 | Status AMBIGUOUS with escalation band AMBIGUOUS: the cluster brief itself cannot determine whether the removal |
| <a id="rat-documentacao-faturamento-01"></a>RAT-DOCUMENTACAO-FATURAMENTO-01 | RULE-DOCUMENTACAO-FATURAMENTO-014 | Whether the client-side re-check of can_access_relatorio_evolucao is deliberate defense-in-depth (useEffective |
| <a id="rat-evolucoes-05"></a>RAT-EVOLUCOES-05 | RULE-EVOLUCOES-017 | Bundling vital-signs creation with an auto-created-or-looked-up daily BalancoHidrico via a `.get_pk` call that |
| <a id="rat-evolucoes-01"></a>RAT-EVOLUCOES-01 | RULE-EVOLUCOES-074 | The anulavel/nullifiers type shapes strongly suggest a medical-legal audit-trail pattern (void rather than del |
| <a id="rat-formularios-clinicos-01"></a>RAT-FORMULARIOS-CLINICOS-01 | RULE-FORMULARIOS-CLINICOS-037 | The escalation itself flags this as AMBIGUOUS because the icon-derived 10-discipline list cannot be confirmed  |
| <a id="rat-formularios-clinicos-02"></a>RAT-FORMULARIOS-CLINICOS-02 | RULE-FORMULARIOS-CLINICOS-039 | The Masculino/Feminino-only icon pairing cannot itself prove the v2 data model restricts gender/sex to a stric |
| <a id="rat-nutricao-02"></a>RAT-NUTRICAO-02 | RULE-NUTRICAO-006 | The vm_mais_72h stress-ulcer eligibility option sets a 72h ventilation threshold against ESC-P2-086, but ASHP  |
| <a id="rat-operacional-infra-11"></a>RAT-OPERACIONAL-INFRA-11 | RULE-OPERACIONAL-INFRA-017 | ParanoiaMixin.delete defaults admin-UI-path deletions to a REAL hard cascading delete unless soft_delete=True  |
| <a id="rat-operacional-infra-01"></a>RAT-OPERACIONAL-INFRA-01 | RULE-OPERACIONAL-INFRA-032 | Escalation band P3 on an internal off-by-one (peep 41 vs 40) in a seed-data generator, not enforced production |
| <a id="rat-operacional-infra-02"></a>RAT-OPERACIONAL-INFRA-02 | RULE-OPERACIONAL-INFRA-036 | Escalation band P3 flags that custom_exception_handler's flatten_errors uses collections.MutableMapping, which |
| <a id="rat-operacional-infra-03"></a>RAT-OPERACIONAL-INFRA-03 | RULE-OPERACIONAL-INFRA-037 | AMBIGUOUS band on ListChoiceField.to_representation: the intent behind switching label-vs-raw-value representa |
| <a id="rat-operacional-infra-04"></a>RAT-OPERACIONAL-INFRA-04 | RULE-OPERACIONAL-INFRA-040 | AMBIGUOUS band on whether prod's missing env-cmd wrapper reflects intentional reliance on Next's native .env.p |
| <a id="rat-operacional-infra-05"></a>RAT-OPERACIONAL-INFRA-05 | RULE-OPERACIONAL-INFRA-047 | Escalation band P3 on a real duplicate-beat-daemon bug (demo/homol-old uwsgi configs run both a standalone Cel |
| <a id="rat-operacional-infra-06"></a>RAT-OPERACIONAL-INFRA-06 | RULE-OPERACIONAL-INFRA-056 | Escalation band P3 on a systemic vars().fromkeys() misuse across multiple pathway files (trilha_sepse, trilha_ |
| <a id="rat-operacional-infra-07"></a>RAT-OPERACIONAL-INFRA-07 | RULE-OPERACIONAL-INFRA-059 | AMBIGUOUS band on the per-company tempo_atualizacao auto-refresh interval field: neither its unit (seconds vs  |
| <a id="rat-prescricao-01"></a>RAT-PRESCRICAO-01 | RULE-PRESCRICAO-036 | validar_alteracao_dado encodes a real once-set-cannot-be-altered immutability rule for administration status b |
| <a id="rat-profilaxia-02"></a>RAT-PROFILAXIA-02 | RULE-PROFILAXIA-008 | The v3 facade's AMBIGUOUS status (ESC-AMBIGUOUS-303) and its dead SEPSE-threshold comment block make it unclea |
| <a id="rat-sedacao-05"></a>RAT-SEDACAO-05 | RULE-SEDACAO-014 | This is the production-wired v3 alert aggregator (VERMELHO if c1 or c8, else AMARELO if c5 or c7), one of thre |
| <a id="rat-sedacao-09"></a>RAT-SEDACAO-09 | RULE-SEDACAO-021 | Manual-pathway alert aggregator (>=3 of 6 criteria -> VERMELHO, 1-2 -> AMARELO) is a second of the three non-r |
| <a id="rat-sedacao-10"></a>RAT-SEDACAO-10 | RULE-SEDACAO-022 | PCR-24h helper implements 'last 24h' as a rolling timedelta.days==0 window (true only while elapsed time keeps |
| <a id="rat-sepse-01"></a>RAT-SEPSE-01 | RULE-SEPSE-068 | AMBIGUOUS-band escalation on a live sepsis-criterion input: the ureia field name implies a >50mg/dL-in-24h boo |
| <a id="rat-sepse-02"></a>RAT-SEPSE-02 | RULE-SEPSE-093 | AMBIGUOUS-band escalation ESC-AMBIGUOUS-306: whether 'finalizado' means any session end and 'concluida' means  |
| <a id="rat-sepse-03"></a>RAT-SEPSE-03 | RULE-SEPSE-098 | AMBIGUOUS-band escalation ESC-AMBIGUOUS-338: sepsis checklist check-off actors uniquely carry a CPF field abse |
| <a id="rat-sinais-vitais-02"></a>RAT-SINAIS-VITAIS-02 | RULE-SINAIS-VITAIS-020 | PAMValidator's 0-200 bound is dead code: the model field and its import are commented out so MAP is never stor |
| <a id="rat-sinais-vitais-05"></a>RAT-SINAIS-VITAIS-05 | RULE-SINAIS-VITAIS-031 | 'Sedativo' aggregates an entire drug class (midazolam, propofol, dexmedetomidine, fentanyl) under one unit-les |
| <a id="rat-sinais-vitais-06"></a>RAT-SINAIS-VITAIS-06 | RULE-SINAIS-VITAIS-033 | SatO2Validator is both internally inconsistent (no zero exemption unlike the structurally identical FiO2Valida |
| <a id="rat-tenancy-organizacao-01"></a>RAT-TENANCY-ORGANIZACAO-01 | RULE-TENANCY-ORGANIZACAO-037 | Escalation band P3 flags this deletion-guard error-message defect; the underlying delete-while-occupied safety |
| <a id="rat-tenancy-organizacao-05"></a>RAT-TENANCY-ORGANIZACAO-05 | RULE-TENANCY-ORGANIZACAO-049 | Escalation band P3 flags this silent-data-loss defect (non-string logo values dropped without client feedback) |
| <a id="rat-trilhas-engine-01"></a>RAT-TRILHAS-ENGINE-01 | RULE-TRILHAS-ENGINE-003 | The 'automatica' branch's reliance on implicit default queryset ordering (vs the explicit -criado_em ordering  |
| <a id="rat-trilhas-engine-02"></a>RAT-TRILHAS-ENGINE-02 | RULE-TRILHAS-ENGINE-012 | Whether v3 pathway records are meant to be scoped per-encounter (nr_atendimento) or per-patient-lifetime canno |
| <a id="rat-trilhas-engine-03"></a>RAT-TRILHAS-ENGINE-03 | RULE-TRILHAS-ENGINE-015 | The refuse workflow's required-justification requirement is clinically sound, but its aceito field is submitte |
