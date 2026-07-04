# IntensiCare Legacy Rule Catalog

The canonical, versioned knowledge base of every business and clinical rule extracted from the two legacy IntensiCare platforms. The rebuild implements from THESE documents — the legacy code should not need to be consulted again.

| | |
|---|---|
| Audited backend | `Dev-Infra-Grupo-AMH/ahlabs-trilhas` @ `8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f` (master) |
| Audited frontend | `Dev-Infra-Grupo-AMH/trilhas-frontend` @ `f9656be2660ec2048ce6240b4ac418b7fe7d5a5b` (master) |
| Audit date | 2026-07-03/04 |
| Rules | **959** (from 1,030 raw extractions incl. 12 post-sweep gap rules, deduplicated with full provenance) |
| Extraction status | 719 OK · 164 DISCREPANCY · 76 AMBIGUOUS |
| Verification verdicts | 73 VERIFIED · 104 DISCREPANCY · 102 UNVERIFIABLE · 680 not-applicable (non-formula) |

**Escalations:** every DISCREPANCY / AMBIGUOUS / UNVERIFIABLE item is ranked by clinical risk in [ESCALATIONS.md](ESCALATIONS.md). Nothing in this catalog was silently corrected — legacy behavior is preserved verbatim, including its defects.

**Audit method & statistics:** [AUDIT-REPORT.md](AUDIT-REPORT.md). Machine-readable reconciled catalogs (the source of truth for these docs): [extraction/phase2/catalog/](extraction/phase2/catalog/). Verification worksheets: [extraction/phase3-verification/](extraction/phase3-verification/). Raw single-pass extraction findings: [extraction/phase1/](extraction/phase1/). Scope & inventory: [INVENTORY.md](INVENTORY.md).

## How to read an entry

Each rule lives in `docs/rules/<category>/<RULE-ID>-<slug>.md`:

- **Field table** — category, type (`formula | threshold | decision-tree | workflow | validation | eligibility | scoring`), extraction status, verification verdict, confidence, owning cluster.
- **Rule** — plain-language statement of the behavior.
- **Inputs / Outputs** — names, types, units, valid ranges as implemented.
- **Logic** — exact pseudocode reproducing the implementation: operator directions, coefficients, boundaries (`>=` vs `>`), order of operations. Reimplementable without reading legacy code.
- **Edge cases** — boundary/null/rounding/timezone handling AS IMPLEMENTED (bugs included).
- **Divergence** — present when two legacy implementations of the same rule disagree (backend vs frontend, facade text vs model predicate, v1 vs v3).
- **Verification** — verdict against the authoritative published reference (with citation and test-vector trace), or `Not applicable` for non-formula rules, or `UNVERIFIABLE` for proprietary internal rules (flagged for owner review — not presumed wrong).
- **Provenance** — every implementation site as `repo : path : lines @ commit` plus the provisional extraction IDs merged into this rule and cross-references to related rules.

Statuses: `OK` (faithful, internally consistent), `DISCREPANCY` (implementations disagree with each other or with a published reference — see ESCALATIONS), `AMBIGUOUS` (intent could not be pinned down; best interpretation + evidence recorded).

## Taxonomy and index

### clinical-scoring (65 rules)

Clinical scores and scales (SOFA components, RASS, Glasgow, sepsis criteria aggregations, pain/behavioral scales)

| Rule | Name | Status | Verdict |
|---|---|---|---|
| [RULE-BALANCO-HIDRICO-019](clinical-scoring/RULE-BALANCO-HIDRICO-019-fluid-balance-pain-scale-conditional-nrs-0-10-bps-3-12.md) | Fluid-balance pain-scale conditional (NRS 0-10 / BPS 3-12) | AMBIGUOUS | VERIFIED |
| [RULE-BALANCO-HIDRICO-059](clinical-scoring/RULE-BALANCO-HIDRICO-059-fluid-balance-consciousness-level-enum-avdi-like.md) | Fluid-balance consciousness level enum (AVDI-like) | OK | UNVERIFIABLE |
| [RULE-CLINICAL-SCORING-001](clinical-scoring/RULE-CLINICAL-SCORING-001-sofa-total-score-sum-of-six-organ-sub-scores.md) | SOFA total score (sum of six organ sub-scores) | OK | VERIFIED |
| [RULE-CLINICAL-SCORING-002](clinical-scoring/RULE-CLINICAL-SCORING-002-sofa-respiratory-sub-score-pao2-fio2.md) | SOFA respiratory sub-score (PaO2/FiO2) | DISCREPANCY | DISCREPANCY (high) |
| [RULE-CLINICAL-SCORING-003](clinical-scoring/RULE-CLINICAL-SCORING-003-sofa-coagulation-sub-score-platelets.md) | SOFA coagulation sub-score (platelets) | OK | VERIFIED |
| [RULE-CLINICAL-SCORING-004](clinical-scoring/RULE-CLINICAL-SCORING-004-sofa-liver-sub-score-bilirubin.md) | SOFA liver sub-score (bilirubin) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-CLINICAL-SCORING-005](clinical-scoring/RULE-CLINICAL-SCORING-005-sofa-cardiovascular-sub-score-vasopressors-map.md) | SOFA cardiovascular sub-score (vasopressors/MAP) | DISCREPANCY | DISCREPANCY (high) |
| [RULE-CLINICAL-SCORING-006](clinical-scoring/RULE-CLINICAL-SCORING-006-sofa-cns-sub-score-glasgow.md) | SOFA CNS sub-score (Glasgow) | OK | VERIFIED |
| [RULE-CLINICAL-SCORING-007](clinical-scoring/RULE-CLINICAL-SCORING-007-sofa-renal-sub-score-creatinine-urine-output.md) | SOFA renal sub-score (creatinine/urine output) | DISCREPANCY | DISCREPANCY (high) |
| [RULE-CLINICAL-SCORING-011](clinical-scoring/RULE-CLINICAL-SCORING-011-sofa-attribute-sourcing-from-prontuario-model-save.md) | SOFA attribute sourcing from prontuario (model.save) | OK | VERIFIED |
| [RULE-CLINICAL-SCORING-012](clinical-scoring/RULE-CLINICAL-SCORING-012-sofa-score-input-assembly-first-movimentacao.md) | SOFA score input assembly (first movimentacao) | OK | VERIFIED |
| [RULE-CLINICAL-SCORING-013](clinical-scoring/RULE-CLINICAL-SCORING-013-glasgow-coma-scale-valid-range-3-15.md) | Glasgow Coma Scale valid range (3-15) | OK | VERIFIED |
| [RULE-CLINICAL-SCORING-014](clinical-scoring/RULE-CLINICAL-SCORING-014-rass-richmond-agitation-sedation-scale-enumeration.md) | RASS (Richmond Agitation-Sedation Scale) enumeration | DISCREPANCY | DISCREPANCY (low) |
| [RULE-CLINICAL-SCORING-015](clinical-scoring/RULE-CLINICAL-SCORING-015-escala-de-dor-numerica-faixa-valida-0-10.md) | Escala de Dor numerica - faixa valida (0-10) | OK | VERIFIED |
| [RULE-CLINICAL-SCORING-016](clinical-scoring/RULE-CLINICAL-SCORING-016-sinais-de-dor-escala-comportamental-faixa-valida-3-12.md) | Sinais de Dor (escala comportamental) - faixa valida (3-12) | OK | VERIFIED |
| [RULE-CLINICAL-SCORING-017](clinical-scoring/RULE-CLINICAL-SCORING-017-sdra-ards-severity-enumeration.md) | SDRA (ARDS) severity enumeration | AMBIGUOUS | VERIFIED |
| [RULE-CLINICAL-SCORING-018](clinical-scoring/RULE-CLINICAL-SCORING-018-fois-functional-oral-intake-scale-enumeration.md) | FOIS (Functional Oral Intake Scale) enumeration | OK | VERIFIED |
| [RULE-EFICIENCIA-010](clinical-scoring/RULE-EFICIENCIA-010-eficiencia-v3-criterio-7-delirium-agitation-risk-bundle-defi.md) | Eficiencia v3 criterio_7 - delirium/agitation risk bundle (defined, unwired, crashes) | DISCREPANCY | DISCREPANCY |
| [RULE-EVOLUCOES-001](clinical-scoring/RULE-EVOLUCOES-001-medical-record-clinical-parameter-panel-with-pre-computed-so.md) | Medical-record clinical parameter panel with pre-computed SOFA score | AMBIGUOUS | UNVERIFIABLE |
| [RULE-EVOLUCOES-002](clinical-scoring/RULE-EVOLUCOES-002-sofa-score-display-threshold.md) | SOFA score display threshold | OK | UNVERIFIABLE |
| [RULE-EVOLUCOES-003](clinical-scoring/RULE-EVOLUCOES-003-rass-field-type-mismatch-across-models.md) | RASS field type mismatch across models | DISCREPANCY | DISCREPANCY (low) |
| [RULE-EVOLUCOES-004](clinical-scoring/RULE-EVOLUCOES-004-cardiac-arrest-occurrence-tracking-shape.md) | Cardiac-arrest occurrence tracking shape | OK | UNVERIFIABLE |
| [RULE-FORMULARIOS-CLINICOS-001](clinical-scoring/RULE-FORMULARIOS-CLINICOS-001-pressure-injury-lpp-npuap-staging-enum.md) | Pressure-injury (LPP) NPUAP staging enum | OK | VERIFIED |
| [RULE-FORMULARIOS-CLINICOS-002](clinical-scoring/RULE-FORMULARIOS-CLINICOS-002-pressure-injury-lpp-staging-wound-bed-composite-assessment-n.md) | Pressure-injury (LPP) staging + wound-bed composite assessment (nursing / dietitian FE form) | DISCREPANCY | DISCREPANCY (low) |
| [RULE-FORMULARIOS-CLINICOS-003](clinical-scoring/RULE-FORMULARIOS-CLINICOS-003-nursing-technician-tecenfermagem-tegumentary-lpp-list-varian.md) | Nursing-technician (TecEnfermagem) tegumentary LPP list variant | DISCREPANCY | DISCREPANCY (low) |
| [RULE-INDICADORES-ETL-012](clinical-scoring/RULE-INDICADORES-ETL-012-get-microindicadores-icu-micro-indicator-boolean-mapping-dva.md) | get_microindicadores — ICU micro-indicator boolean mapping, DVA mapped to a drug-specific 'nora | AMBIGUOUS | DISCREPANCY (moderate) |
| [RULE-MOVIMENTACAO-ADT-002](clinical-scoring/RULE-MOVIMENTACAO-ADT-002-bed-movimentacao-micro-indicators-payload-vm-noradrenalina-s.md) | Bed/movimentacao micro-indicators payload (VM / noradrenalina / sedacao / LOS) | DISCREPANCY | UNVERIFIABLE |
| [RULE-MOVIMENTACAO-ADT-003](clinical-scoring/RULE-MOVIMENTACAO-ADT-003-expected-mortality-score-mortalidade-esperada-surfaced-witho.md) | Expected-mortality score (mortalidade_esperada) surfaced without formula | AMBIGUOUS | UNVERIFIABLE |
| [RULE-MOVIMENTACAO-ADT-004](clinical-scoring/RULE-MOVIMENTACAO-ADT-004-bed-level-assistencial-information-clinical-panel-vitals-neu.md) | Bed-level assistencial information clinical panel (vitals / neuro scores / labs) | OK | VERIFIED |
| [RULE-NUTRICAO-002](clinical-scoring/RULE-NUTRICAO-002-fois-functional-oral-intake-scale-enum-of-7-levels.md) | FOIS (Functional Oral Intake Scale) - enum of 7 levels | OK | VERIFIED |
| [RULE-OPERACIONAL-INFRA-012](clinical-scoring/RULE-OPERACIONAL-INFRA-012-popular-banco-rass-enum-values-synthetic-data.md) | popular_banco RASS enum values (synthetic data) | OK | VERIFIED |
| [RULE-PIORA-CLINICA-001](clinical-scoring/RULE-PIORA-CLINICA-001-piora-clinica-criterio-1-frequencia-respiratoria-graded-sub.md) | Piora Clinica criterio_1 - Frequencia respiratoria (graded sub-score) | OK | UNVERIFIABLE |
| [RULE-PIORA-CLINICA-002](clinical-scoring/RULE-PIORA-CLINICA-002-piora-clinica-criterio-2-temperatura-axilar-graded-sub-score.md) | Piora Clinica criterio_2 - Temperatura axilar (graded sub-score) | DISCREPANCY | DISCREPANCY (low) |
| [RULE-PIORA-CLINICA-003](clinical-scoring/RULE-PIORA-CLINICA-003-piora-clinica-criterio-3-pressao-arterial-sistolica-pas-grad.md) | Piora Clinica criterio_3 - Pressao arterial sistolica (PAS) (graded sub-score) | OK | UNVERIFIABLE |
| [RULE-PIORA-CLINICA-004](clinical-scoring/RULE-PIORA-CLINICA-004-piora-clinica-criterio-4-frequencia-cardiaca-fc-graded-sub-s.md) | Piora Clinica criterio_4 - Frequencia cardiaca (FC) (graded sub-score) | DISCREPANCY | DISCREPANCY (low) |
| [RULE-PIORA-CLINICA-005](clinical-scoring/RULE-PIORA-CLINICA-005-piora-clinica-criterio-5-nivel-de-consciencia-graded-sub-sco.md) | Piora Clinica criterio_5 - Nivel de consciencia (graded sub-score) | OK | UNVERIFIABLE |
| [RULE-PIORA-CLINICA-006](clinical-scoring/RULE-PIORA-CLINICA-006-piora-clinica-criterio-6-dor-escala-numerica-0-10-graded-sub.md) | Piora Clinica criterio_6 - Dor (escala numerica 0-10) (graded sub-score) | DISCREPANCY | DISCREPANCY (high) |
| [RULE-PIORA-CLINICA-007](clinical-scoring/RULE-PIORA-CLINICA-007-piora-clinica-criterio-7-dor-escala-comportamental-3-12-grad.md) | Piora Clinica criterio_7 - Dor (escala comportamental 3-12) (graded sub-score) | DISCREPANCY | DISCREPANCY (high) |
| [RULE-PIORA-CLINICA-008](clinical-scoring/RULE-PIORA-CLINICA-008-piora-clinica-criterio-8-sato2-paciente-regular-nao-dpoc-gra.md) | Piora Clinica criterio_8 - SatO2 (paciente regular / nao-DPOC) (graded sub-score) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-PIORA-CLINICA-009](clinical-scoring/RULE-PIORA-CLINICA-009-piora-clinica-criterio-9-sato2-paciente-dpoc-copd-graded-sub.md) | Piora Clinica criterio_9 - SatO2 (paciente DPOC/COPD) (graded sub-score) | OK | DISCREPANCY (moderate) |
| [RULE-SEDACAO-001](clinical-scoring/RULE-SEDACAO-001-sedacao-v3-criterio-7-moderate-pain-analog-4-6-bps-7-9-two-c.md) | Sedacao v3 criterio_7 - moderate pain (analog 4-6 / BPS 7-9), two consecutive | OK | VERIFIED |
| [RULE-SEDACAO-002](clinical-scoring/RULE-SEDACAO-002-sedacao-v3-criterio-8-severe-pain-analog-7-10-bps-10-12-two.md) | Sedacao v3 criterio_8 - severe pain (analog 7-10 / BPS 10-12), two consecutive | OK | VERIFIED |
| [RULE-SEDACAO-003](clinical-scoring/RULE-SEDACAO-003-sedacao-v3-criterio-9-deep-sedation-rass-3-5-defined-unwired.md) | Sedacao v3 criterio_9 - deep sedation RASS -3..-5 (defined, unwired) | DISCREPANCY | DISCREPANCY |
| [RULE-SEDACAO-004](clinical-scoring/RULE-SEDACAO-004-sedacao-v3-criterio-12-weaning-readiness-defined-unwired-bad.md) | Sedacao v3 criterio_12 - weaning readiness (defined, unwired, bad thresholds) | DISCREPANCY | DISCREPANCY |
| [RULE-SEPSE-001](clinical-scoring/RULE-SEPSE-001-sepse-v1-alert-maiores-menores-dual-threshold.md) | SEPSE v1 alert maiores/menores dual threshold | OK | UNVERIFIABLE |
| [RULE-SEPSE-002](clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md) | SEPSE v3 alert maiores/menores (OR thresholds) + risk message | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-SEPSE-005](clinical-scoring/RULE-SEPSE-005-sepse-hierarquia-de-nivel-de-consciencia.md) | Sepse - Hierarquia de nivel de consciencia | OK | UNVERIFIABLE |
| [RULE-SEPSE-027](clinical-scoring/RULE-SEPSE-027-sepse-criterio-1-febre-fever.md) | Sepse criterio_1 - Febre (fever) | OK | VERIFIED |
| [RULE-SEPSE-028](clinical-scoring/RULE-SEPSE-028-sepse-criterio-2-taquipneia-dessaturacao-sob-o2.md) | Sepse criterio_2 - Taquipneia / dessaturacao sob O2 | OK | VERIFIED |
| [RULE-SEPSE-029](clinical-scoring/RULE-SEPSE-029-sepse-criterio-3-escalonamento-de-suporte-ventilatorio.md) | Sepse criterio_3 - Escalonamento de suporte ventilatorio | OK | UNVERIFIABLE |
| [RULE-SEPSE-030](clinical-scoring/RULE-SEPSE-030-sepse-criterio-4-tempo-de-enchimento-capilar-5s.md) | Sepse criterio_4 - Tempo de enchimento capilar > 5s | OK | DISCREPANCY (low) |
| [RULE-SEPSE-031](clinical-scoring/RULE-SEPSE-031-sepse-criterio-5-hipotensao.md) | Sepse criterio_5 - Hipotensao | OK | VERIFIED |
| [RULE-SEPSE-032](clinical-scoring/RULE-SEPSE-032-sepse-criterio-6-oliguria-sonda-ou-dessaturacao.md) | Sepse criterio_6 - Oliguria (sonda) ou dessaturacao | OK | DISCREPANCY (moderate) |
| [RULE-SEPSE-033](clinical-scoring/RULE-SEPSE-033-sepse-criterio-7-variacao-do-nivel-de-consciencia.md) | Sepse criterio_7 - Variacao do nivel de consciencia | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-SEPSE-034](clinical-scoring/RULE-SEPSE-034-sepse-criterio-8-hipotermia.md) | Sepse criterio_8 - Hipotermia | OK | VERIFIED |
| [RULE-SEPSE-035](clinical-scoring/RULE-SEPSE-035-sepse-criterio-9-taquicardia.md) | Sepse criterio_9 - Taquicardia | OK | DISCREPANCY (low) |
| [RULE-SEPSE-036](clinical-scoring/RULE-SEPSE-036-sepse-criterio-10-dispositivo-invasivo-com-permanencia-7-dia.md) | Sepse criterio_10 - Dispositivo invasivo com permanencia > 7 dias | OK | UNVERIFIABLE |
| [RULE-SEPSE-037](clinical-scoring/RULE-SEPSE-037-sepse-criterio-11-placeholder-sempre-false.md) | Sepse criterio_11 - Placeholder (sempre False) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-SINAIS-VITAIS-011](clinical-scoring/RULE-SINAIS-VITAIS-011-glasgowvalidator-glasgow-coma-scale-range-zero-exempted.md) | GlasgowValidator — Glasgow Coma Scale range, zero exempted | OK | VERIFIED |
| [RULE-TENANCY-ORGANIZACAO-005](clinical-scoring/RULE-TENANCY-ORGANIZACAO-005-establishment-macro-indicator-aggregate-sum-avg-rounded-to-2.md) | Establishment macro-indicator aggregate (sum/avg rounded to 2 decimals) | OK | UNVERIFIABLE |
| [RULE-TENANCY-ORGANIZACAO-006](clinical-scoring/RULE-TENANCY-ORGANIZACAO-006-sector-macro-indicator-single-record-fetch-with-silent-failu.md) | Sector macro-indicator single-record fetch with silent failure | DISCREPANCY | UNVERIFIABLE |
| [RULE-TENANCY-ORGANIZACAO-015](clinical-scoring/RULE-TENANCY-ORGANIZACAO-015-monthly-total-intervention-count-for-sector-indicators.md) | Monthly total intervention count for sector indicators | OK | UNVERIFIABLE |
| [RULE-TENANCY-ORGANIZACAO-038](clinical-scoring/RULE-TENANCY-ORGANIZACAO-038-sector-clinical-indicator-aggregation-across-care-pathways-i.md) | Sector clinical indicator aggregation across care pathways (indicadores action) | OK | UNVERIFIABLE |
| [RULE-TENANCY-ORGANIZACAO-041](clinical-scoring/RULE-TENANCY-ORGANIZACAO-041-company-wide-indicadores-action-scopes-to-user-s-establishme.md) | Company-wide indicadores action scopes to user's establishments/sectors | OK | UNVERIFIABLE |
| [RULE-TENANCY-ORGANIZACAO-042](clinical-scoring/RULE-TENANCY-ORGANIZACAO-042-establishment-indicadores-action-scopes-movimentacoes-and-se.md) | Establishment indicadores action scopes movimentacoes and setores to the requesting user | OK | UNVERIFIABLE |

### drug-dosing (29 rules)

Drug dosing, titration and substitution rules (vasopressors, sedation, VTE prophylaxis, insulin, antimicrobials)

| Rule | Name | Status | Verdict |
|---|---|---|---|
| [RULE-BALANCO-HIDRICO-056](drug-dosing/RULE-BALANCO-HIDRICO-056-drugs-hydration-in-bi-vocabulary.md) | Drugs/hydration-in-BI vocabulary | OK | UNVERIFIABLE |
| [RULE-BALANCO-HIDRICO-057](drug-dosing/RULE-BALANCO-HIDRICO-057-antibiotic-vocabulary-fluid-balance.md) | Antibiotic vocabulary (fluid balance) | OK | UNVERIFIABLE |
| [RULE-BALANCO-HIDRICO-058](drug-dosing/RULE-BALANCO-HIDRICO-058-electrolyte-replacement-vocabulary.md) | Electrolyte replacement vocabulary | OK | UNVERIFIABLE |
| [RULE-EQUILIBRIO-002](drug-dosing/RULE-EQUILIBRIO-002-renal-function-drug-substitution-morphine-avoidance-and-hype.md) | Renal-function drug substitution, morphine avoidance, and hypernatremia (Na>160) correction (cr | OK | VERIFIED |
| [RULE-EQUILIBRIO-004](drug-dosing/RULE-EQUILIBRIO-004-severe-hyperkalemia-k-6-rescue-protocol-with-4h-reassessment.md) | Severe hyperkalemia (K>6) rescue protocol with 4h reassessment (criterio 9) | OK | DISCREPANCY (low) |
| [RULE-ESTABILIDADE-010](drug-dosing/RULE-ESTABILIDADE-010-estabilidade-v3-criterio-10-antihypertensive-with-active-vas.md) | Estabilidade v3 criterio_10 - antihypertensive with active vasopressor (VERMELHO, wired) | DISCREPANCY | UNVERIFIABLE |
| [RULE-ESTABILIDADE-016](drug-dosing/RULE-ESTABILIDADE-016-estabilidade-facade-alert-text-vasopressor-inotrope-escalati.md) | Estabilidade facade alert-text - vasopressor/inotrope escalation ladder (criteria 7-9) | DISCREPANCY | DISCREPANCY (high) |
| [RULE-FORMULARIOS-CLINICOS-014](drug-dosing/RULE-FORMULARIOS-CLINICOS-014-nursing-technician-high-cost-drug-antibiotic-list-and-other.md) | Nursing-technician high-cost drug/antibiotic list and other info | OK | UNVERIFIABLE |
| [RULE-FORMULARIOS-CLINICOS-042](drug-dosing/RULE-FORMULARIOS-CLINICOS-042-vasopressor-inotrope-sedative-dosing-capture-movimentacao.md) | Vasopressor / inotrope / sedative dosing capture (movimentacao) | OK | UNVERIFIABLE |
| [RULE-PROFILAXIA-001](drug-dosing/RULE-PROFILAXIA-001-prophylaxis-v1-hyperglycemia-subcutaneous-insulin-nph-slidin.md) | Prophylaxis v1 - hyperglycemia subcutaneous insulin NPH sliding regimen | OK | VERIFIED |
| [RULE-PROFILAXIA-002](drug-dosing/RULE-PROFILAXIA-002-prophylaxis-v1-vte-anticoagulation-dosing-by-renal-function.md) | Prophylaxis v1 - VTE anticoagulation dosing by renal function and BMI | OK | VERIFIED |
| [RULE-SEDACAO-005](drug-dosing/RULE-SEDACAO-005-sedacao-v3-criterio-1-excessive-continuous-sedation-infusion.md) | Sedacao v3 criterio_1 - excessive continuous sedation infusion | OK | UNVERIFIABLE |
| [RULE-SEDACAO-006](drug-dosing/RULE-SEDACAO-006-sedacao-v3-criterio-2-sedation-despite-adequate-oxygenation.md) | Sedacao v3 criterio_2 - sedation despite adequate oxygenation (defined, unwired) | OK | VERIFIED |
| [RULE-SEDACAO-007](drug-dosing/RULE-SEDACAO-007-sedacao-v3-criterio-3-neuromuscular-blockade-with-p-f-150-de.md) | Sedacao v3 criterio_3 - neuromuscular blockade with P/F>150 (defined, unwired) | OK | VERIFIED |
| [RULE-SEDACAO-008](drug-dosing/RULE-SEDACAO-008-sedacao-v3-criterio-4-undersedation-on-invasive-vent-defined.md) | Sedacao v3 criterio_4 - undersedation on invasive vent (defined, unwired) | AMBIGUOUS | DISCREPANCY (low) |
| [RULE-SEDACAO-009](drug-dosing/RULE-SEDACAO-009-sedacao-v3-criterio-5-no-morning-sedation-reduction-1-2.md) | Sedacao v3 criterio_5 - no morning sedation reduction (>=1/2) | AMBIGUOUS | DISCREPANCY (moderate) |
| [RULE-SEDACAO-010](drug-dosing/RULE-SEDACAO-010-sedacao-v3-criterio-6-high-dose-neuromuscular-blockade-defin.md) | Sedacao v3 criterio_6 - high-dose neuromuscular blockade (defined, unwired) | OK | UNVERIFIABLE |
| [RULE-SEDACAO-011](drug-dosing/RULE-SEDACAO-011-sedacao-v3-criterio-10-prolonged-sedation-96h-defined-unwire.md) | Sedacao v3 criterio_10 - prolonged sedation >96h (defined, unwired) | DISCREPANCY | DISCREPANCY |
| [RULE-SEDACAO-012](drug-dosing/RULE-SEDACAO-012-sedacao-v3-criterio-11-prolonged-propofol-without-safety-lab.md) | Sedacao v3 criterio_11 - prolonged propofol without safety labs (defined, unwired) | OK | VERIFIED |
| [RULE-SEDACAO-013](drug-dosing/RULE-SEDACAO-013-sedacao-v3-active-sedative-detection-set-sedativo-em-uso.md) | Sedacao v3 active-sedative detection (set_sedativo_em_uso) | OK | UNVERIFIABLE |
| [RULE-SEDACAO-024](drug-dosing/RULE-SEDACAO-024-sedation-analgesia-pathway-recommendation-catalog-facade-tex.md) | Sedation/analgesia pathway recommendation catalog (facade text: RASS targets, BNM, PRIS, analge | OK | VERIFIED |
| [RULE-SEDACAO-025](drug-dosing/RULE-SEDACAO-025-sedative-specific-reduction-recommendation-criterio-1-free-t.md) | Sedative-specific reduction recommendation (criterio_1 free text by active drug) | OK | UNVERIFIABLE |
| [RULE-SEDACAO-026](drug-dosing/RULE-SEDACAO-026-sedative-drug-enumeration-sedativo-nome-sedativo-choices.md) | Sedative drug enumeration (Sedativo.nome_sedativo choices) | OK | UNVERIFIABLE |
| [RULE-SEPSE-061](drug-dosing/RULE-SEPSE-061-sepse-volume-expansion-expansao-volemica-decision-and-dosing.md) | SEPSE volume expansion (expansao volemica) decision and dosing | OK | DISCREPANCY (low) |
| [RULE-SEPSE-065](drug-dosing/RULE-SEPSE-065-sepse-vasoactive-drug-escalation-thresholds-and-shock-index.md) | SEPSE vasoactive-drug escalation thresholds and shock index | OK | VERIFIED |
| [RULE-SINAIS-VITAIS-029](drug-dosing/RULE-SINAIS-VITAIS-029-dobutaminavalidator-dobutamine-dose-range-no-zero-exemption.md) | DobutaminaValidator — dobutamine dose range, no zero exemption | OK | UNVERIFIABLE |
| [RULE-SINAIS-VITAIS-030](drug-dosing/RULE-SINAIS-VITAIS-030-noradrenalinavalidator-norepinephrine-dose-range-no-zero-exe.md) | NoradrenalinaValidator — norepinephrine dose range, no zero exemption | OK | UNVERIFIABLE |
| [RULE-SINAIS-VITAIS-031](drug-dosing/RULE-SINAIS-VITAIS-031-sedativovalidator-sedative-dose-range-no-zero-exemption.md) | SedativoValidator — sedative dose range, no zero exemption | DISCREPANCY | DISCREPANCY |
| [RULE-TRILHAS-ENGINE-017](drug-dosing/RULE-TRILHAS-ENGINE-017-per-criterion-drug-dosing-reference-image.md) | Per-criterion drug-dosing reference image | OK | UNVERIFIABLE |

### physiological-calculation (47 rules)

Physiological formulas (fluid balance, P/F ratio, age, anthropometrics, 24h aggregations)

| Rule | Name | Status | Verdict |
|---|---|---|---|
| [RULE-BALANCO-HIDRICO-001](physiological-calculation/RULE-BALANCO-HIDRICO-001-balanco-hidrico-acumulado-cumulative-fluid-balance.md) | Balanco Hidrico acumulado (cumulative fluid balance) | OK | VERIFIED |
| [RULE-BALANCO-HIDRICO-002](physiological-calculation/RULE-BALANCO-HIDRICO-002-balanco-hidrico-ganhos-daily-intake-total.md) | Balanco Hidrico ganhos (daily intake total) | OK | VERIFIED |
| [RULE-BALANCO-HIDRICO-003](physiological-calculation/RULE-BALANCO-HIDRICO-003-balanco-hidrico-perdas-daily-output-total.md) | Balanco Hidrico perdas (daily output total) | OK | VERIFIED |
| [RULE-BALANCO-HIDRICO-004](physiological-calculation/RULE-BALANCO-HIDRICO-004-balanco-hidrico-diurno-day-shift-balance-07-00-19-00.md) | Balanco Hidrico diurno (day-shift balance 07:00-19:00) | OK | UNVERIFIABLE |
| [RULE-BALANCO-HIDRICO-005](physiological-calculation/RULE-BALANCO-HIDRICO-005-balanco-hidrico-noturno-night-shift-balance-by-subtraction.md) | Balanco Hidrico noturno (night-shift balance by subtraction) | OK | UNVERIFIABLE |
| [RULE-BALANCO-HIDRICO-006](physiological-calculation/RULE-BALANCO-HIDRICO-006-24h-fluid-balance-intake-minus-output-over-the-07-00-07-00-n.md) | 24h fluid balance = intake minus output over the 07:00-07:00 nursing day | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-BALANCO-HIDRICO-007](physiological-calculation/RULE-BALANCO-HIDRICO-007-ganhos-fluid-intake-summed-over-the-07-00-07-00-nursing-day.md) | Ganhos (fluid intake) summed over the 07:00-07:00 nursing day | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-BALANCO-HIDRICO-008](physiological-calculation/RULE-BALANCO-HIDRICO-008-diureses-urine-output-summed-over-the-07-00-07-00-nursing-da.md) | Diureses (urine output) summed over the 07:00-07:00 nursing day | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-BALANCO-HIDRICO-009](physiological-calculation/RULE-BALANCO-HIDRICO-009-evacuacoes-bowel-movements-summed-over-the-07-00-07-00-nursi.md) | Evacuacoes (bowel movements) summed over the 07:00-07:00 nursing day | DISCREPANCY | DISCREPANCY (low) |
| [RULE-BALANCO-HIDRICO-010](physiological-calculation/RULE-BALANCO-HIDRICO-010-maximum-temperature-over-the-07-00-07-00-nursing-day.md) | Maximum temperature over the 07:00-07:00 nursing day | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-BALANCO-HIDRICO-011](physiological-calculation/RULE-BALANCO-HIDRICO-011-maximum-hgt-capillary-blood-glucose-over-the-07-00-07-00-nur.md) | Maximum HGT (capillary blood glucose) over the 07:00-07:00 nursing day | DISCREPANCY | DISCREPANCY (low) |
| [RULE-BALANCO-HIDRICO-012](physiological-calculation/RULE-BALANCO-HIDRICO-012-formulario-agregacoes-de-24h-evolucao-incl-balanco-hidrico.md) | Formulario - agregacoes de 24h (evolucao) incl. balanco hidrico | AMBIGUOUS | UNVERIFIABLE |
| [RULE-BALANCO-HIDRICO-013](physiological-calculation/RULE-BALANCO-HIDRICO-013-fluid-balance-visao-geral-2-hour-time-bucketing-08-00-start.md) | Fluid-balance visao-geral 2-hour time-bucketing (08:00-start day, view facade + utils impl) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-BALANCO-HIDRICO-014](physiological-calculation/RULE-BALANCO-HIDRICO-014-fluid-balance-24h-accrual-on-intake-entrada.md) | Fluid balance 24h accrual on intake (entrada) | OK | VERIFIED |
| [RULE-BALANCO-HIDRICO-015](physiological-calculation/RULE-BALANCO-HIDRICO-015-fluid-balance-24h-accrual-on-output-saida.md) | Fluid balance 24h accrual on output (saida) | OK | VERIFIED |
| [RULE-BALANCO-HIDRICO-016](physiological-calculation/RULE-BALANCO-HIDRICO-016-tempo-criacao-horas-desde-a-criacao-shared-helper.md) | tempo_criacao - horas desde a criacao (shared helper) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-BALANCO-HIDRICO-017](physiological-calculation/RULE-BALANCO-HIDRICO-017-sinaisvitais-anterior-leitura-anterior-de-sinais-vitais.md) | SinaisVitais.anterior - leitura anterior de sinais vitais | OK | UNVERIFIABLE |
| [RULE-BALANCO-HIDRICO-018](physiological-calculation/RULE-BALANCO-HIDRICO-018-blood-pressure-display-composition-systolic-diastolic.md) | Blood-pressure display composition (systolic/diastolic) | OK | UNVERIFIABLE |
| [RULE-BALANCO-HIDRICO-020](physiological-calculation/RULE-BALANCO-HIDRICO-020-default-volume-for-enteral-diet-intake-entry.md) | Default volume for enteral diet intake entry | OK | UNVERIFIABLE |
| [RULE-BALANCO-HIDRICO-021](physiological-calculation/RULE-BALANCO-HIDRICO-021-default-volume-for-spontaneous-presence-output.md) | Default volume for spontaneous presence output | OK | UNVERIFIABLE |
| [RULE-BALANCO-HIDRICO-022](physiological-calculation/RULE-BALANCO-HIDRICO-022-presence-level-to-volume-mapping-for-evacuacao-vomito-output.md) | Presence-level to volume mapping for evacuacao/vomito outputs | DISCREPANCY | DISCREPANCY |
| [RULE-BALANCO-HIDRICO-023](physiological-calculation/RULE-BALANCO-HIDRICO-023-default-clinical-day-cutoff-07-00-for-balanco-hidrico.md) | Default clinical-day cutoff (07:00) for balanco hidrico | OK | UNVERIFIABLE |
| [RULE-BALANCO-HIDRICO-024](physiological-calculation/RULE-BALANCO-HIDRICO-024-fixed-clinical-shift-window-for-fluid-balance-07-00-07-00.md) | Fixed clinical shift window for fluid balance (07:00-07:00) | OK | UNVERIFIABLE |
| [RULE-BALANCO-HIDRICO-028](physiological-calculation/RULE-BALANCO-HIDRICO-028-medical-evolution-24h-indicator-gate-vs-value-source-mismatc.md) | Medical-evolution 24h-indicator gate vs value source mismatch | AMBIGUOUS | UNVERIFIABLE |
| [RULE-BALANCO-HIDRICO-038](physiological-calculation/RULE-BALANCO-HIDRICO-038-entrada-soft-delete-adjusts-24h-fluid-balance-and-logs-audit.md) | Entrada soft-delete adjusts 24h fluid balance and logs audit action | OK | VERIFIED |
| [RULE-BALANCO-HIDRICO-039](physiological-calculation/RULE-BALANCO-HIDRICO-039-saida-soft-delete-adjusts-24h-fluid-balance-and-logs-audit-a.md) | Saida soft-delete adjusts 24h fluid balance and logs audit action | OK | VERIFIED |
| [RULE-CLINICAL-SCORING-008](physiological-calculation/RULE-CLINICAL-SCORING-008-pao2-fio2-ratio-relacao-po2-fio2.md) | PaO2/FiO2 ratio (relacao PO2/FiO2) | DISCREPANCY | DISCREPANCY (high) |
| [RULE-CLINICAL-SCORING-009](physiological-calculation/RULE-CLINICAL-SCORING-009-mean-arterial-pressure-pam-from-pas-pad.md) | Mean arterial pressure (PAM) from PAS/PAD | OK | VERIFIED |
| [RULE-CLINICAL-SCORING-010](physiological-calculation/RULE-CLINICAL-SCORING-010-patient-age-from-birthdate-integer-days-365.md) | Patient age from birthdate (integer days // 365) | DISCREPANCY | DISCREPANCY (low) |
| [RULE-ESTABILIDADE-001](physiological-calculation/RULE-ESTABILIDADE-001-estabilidade-v3-criterio-5-vasopressor-with-negative-cumulat.md) | Estabilidade v3 criterio_5 - vasopressor with negative cumulative fluid balance | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-ESTABILIDADE-002](physiological-calculation/RULE-ESTABILIDADE-002-estabilidade-v3-criterio-6-shock-index-with-beta-blocker-vas.md) | Estabilidade v3 criterio_6 - shock index with beta-blocker/vasopressor absence | OK | VERIFIED (low) |
| [RULE-INDICADORES-ETL-003](physiological-calculation/RULE-INDICADORES-ETL-003-tlp-standardized-letality-percentage-conversion.md) | TLP (standardized letality) percentage conversion | OK | VERIFIED |
| [RULE-INDICADORES-ETL-004](physiological-calculation/RULE-INDICADORES-ETL-004-sedation-use-indicator-representation-assistenciais-vs-contr.md) | Sedation-use indicator representation (assistenciais vs controle-infeccao) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-INDICADORES-ETL-010](physiological-calculation/RULE-INDICADORES-ETL-010-sector-dashboard-dual-y-axis-toggle.md) | Sector dashboard dual y-axis toggle | OK | UNVERIFIABLE |
| [RULE-MOVIMENTACAO-ADT-001](physiological-calculation/RULE-MOVIMENTACAO-ADT-001-length-of-stay-tempo-de-permanencia-dias-de-internacao.md) | Length-of-stay (tempo de permanencia / dias de internacao) | OK | UNVERIFIABLE |
| [RULE-MOVIMENTACAO-ADT-005](physiological-calculation/RULE-MOVIMENTACAO-ADT-005-bed-micro-indicator-lookup-key-nr-atendimento-bed-name-as-cd.md) | Bed micro-indicator lookup key: nr_atendimento + bed name as CD_UNIDADE | OK | UNVERIFIABLE |
| [RULE-NUTRICAO-001](physiological-calculation/RULE-NUTRICAO-001-bmi-imc-auto-calculation.md) | BMI (IMC) auto-calculation | OK | VERIFIED |
| [RULE-PRESCRICAO-001](physiological-calculation/RULE-PRESCRICAO-001-ml-medications-capture-exported-quantity-for-fluid-balance-b.md) | ml medications capture exported quantity for fluid balance (balanco hidrico) | OK | UNVERIFIABLE |
| [RULE-SEPSE-006](physiological-calculation/RULE-SEPSE-006-sepse-v3-assistencial-info-snapshot-diurese-bh-aggregation.md) | SEPSE v3 assistencial info snapshot (diurese/BH aggregation) | OK | UNVERIFIABLE |
| [RULE-SEPSE-014](physiological-calculation/RULE-SEPSE-014-sepse-v3-criterio-8-oliguria-without-vasopressor-dialysis.md) | SEPSE v3 criterio_8 - oliguria without vasopressor/dialysis | DISCREPANCY | DISCREPANCY (high) |
| [RULE-TENANCY-ORGANIZACAO-001](physiological-calculation/RULE-TENANCY-ORGANIZACAO-001-establishment-occupancy-percentage-formula.md) | Establishment occupancy percentage formula | OK | VERIFIED |
| [RULE-TENANCY-ORGANIZACAO-002](physiological-calculation/RULE-TENANCY-ORGANIZACAO-002-sector-occupancy-percentage-formula.md) | Sector occupancy percentage formula | OK | VERIFIED |
| [RULE-TENANCY-ORGANIZACAO-003](physiological-calculation/RULE-TENANCY-ORGANIZACAO-003-establishment-bed-total-ativo-scoped-vs-occupied-bed-total-n.md) | Establishment bed total (ativo-scoped) vs occupied-bed total (no ativo scoping) | DISCREPANCY | DISCREPANCY (low) |
| [RULE-TENANCY-ORGANIZACAO-004](physiological-calculation/RULE-TENANCY-ORGANIZACAO-004-sector-active-bed-total-vs-occupied-bed-total-use-inconsiste.md) | Sector active-bed total vs. occupied-bed total use inconsistent ativo scoping | DISCREPANCY | DISCREPANCY (low) |
| [RULE-TENANCY-ORGANIZACAO-012](physiological-calculation/RULE-TENANCY-ORGANIZACAO-012-sector-bed-totals-active-beds-only.md) | Sector bed totals (active beds only) | OK | UNVERIFIABLE |
| [RULE-VENTILACAO-001](physiological-calculation/RULE-VENTILACAO-001-predicted-body-weight-and-protective-tidal-volume-vc-4-5-6-m.md) | Predicted body weight and protective tidal volume (VC 4/5/6 ml/kg) | OK | VERIFIED |
| [RULE-VENTILACAO-002](physiological-calculation/RULE-VENTILACAO-002-days-on-mechanical-ventilation-buscar-dias-com-ventilacao-me.md) | Days on mechanical ventilation (buscar_dias_com_ventilacao_mecanica) | OK | UNVERIFIABLE |

### alert-threshold (116 rules)

Alert triggers and severity classification (criterion thresholds, alert color assignment, rollups)

| Rule | Name | Status | Verdict |
|---|---|---|---|
| [RULE-ALERTAS-001](alert-threshold/RULE-ALERTAS-001-count-triggered-criteria-contar-qtd-criterios-alerta.md) | Count triggered criteria (contar_qtd_criterios_alerta) | OK | UNVERIFIABLE |
| [RULE-ALERTAS-002](alert-threshold/RULE-ALERTAS-002-aggregate-alert-counts-across-movimentacoes.md) | Aggregate alert counts across movimentacoes | OK | UNVERIFIABLE |
| [RULE-ALERTAS-003](alert-threshold/RULE-ALERTAS-003-criteria-count-alert-color-mapping-define-tipo-alerta-per-mo.md) | Criteria-count -> alert color mapping (define_tipo_alerta) + per-model _CRITERIOS_ALERTA thresh | DISCREPANCY | — |
| [RULE-ALERTAS-004](alert-threshold/RULE-ALERTAS-004-single-criterion-alert-flag-esta-alerta.md) | Single-criterion alert flag (esta_alerta) | OK | — |
| [RULE-ALERTAS-005](alert-threshold/RULE-ALERTAS-005-bed-level-alert-rollup-util-define-tipo-alerta-leito-dead-co.md) | Bed-level alert rollup util (define_tipo_alerta_leito) - DEAD/commented-out | OK | — |
| [RULE-ALERTAS-006](alert-threshold/RULE-ALERTAS-006-bed-alert-color-aggregation-get-alerta-leito-with-sepse-lara.md) | Bed alert color aggregation (get_alerta_leito, with sepse LARANJA override) | OK | — |
| [RULE-ALERTAS-007](alert-threshold/RULE-ALERTAS-007-automatic-bed-alert-ignoring-attendance-alerta-nao-assistido.md) | Automatic-bed alert ignoring attendance (alerta_nao_assistido) | OK | — |
| [RULE-ALERTAS-008](alert-threshold/RULE-ALERTAS-008-homecare-bed-alert-ignoring-attendance-pioraclinica-sepse.md) | Homecare-bed alert ignoring attendance (PioraClinica + Sepse) | OK | — |
| [RULE-ALERTAS-009](alert-threshold/RULE-ALERTAS-009-bed-attended-assistido-determination.md) | Bed 'attended' (assistido) determination | OK | — |
| [RULE-ALERTAS-010](alert-threshold/RULE-ALERTAS-010-automatic-bed-payload-alert-attendance-flag.md) | Automatic-bed payload alert + attendance flag | OK | — |
| [RULE-ALERTAS-011](alert-threshold/RULE-ALERTAS-011-assistido-overrides-alerta-status-color-precedence-frontend.md) | Assistido-overrides-alerta status color precedence (frontend render) | OK | — |
| [RULE-ALERTAS-012](alert-threshold/RULE-ALERTAS-012-conteudo-trilha-criterios-red-alert-content-extraction-for-m.md) | conteudo_trilha_criterios - RED-alert content extraction for manual-trilha movimentacao | OK | — |
| [RULE-ALERTAS-013](alert-threshold/RULE-ALERTAS-013-conteudo-trilha-automatica-criterios-red-alert-content-extra.md) | conteudo_trilha_automatica_criterios - RED-alert content extraction for automatic pathways | OK | — |
| [RULE-ALERTAS-014](alert-threshold/RULE-ALERTAS-014-conteudo-observacao-criterios-tipo-dependent-whitelist-filte.md) | conteudo_observacao_criterios - tipo-dependent whitelist filter on RED-alert criteria, with a d | AMBIGUOUS | — |
| [RULE-ALERTAS-015](alert-threshold/RULE-ALERTAS-015-conteudo-trilha-homecare-criterios-red-alert-content-extract.md) | conteudo_trilha_homecare_criterios - RED-alert content extraction for homecare pathways | OK | — |
| [RULE-ALERTAS-016](alert-threshold/RULE-ALERTAS-016-bed-observation-dispatch-with-vermelho-de-duplication-enviar.md) | Bed observation dispatch with VERMELHO de-duplication (enviar_observacao_leito) | OK | — |
| [RULE-ALERTAS-025](alert-threshold/RULE-ALERTAS-025-semantic-status-color-tokens-success-info-warning-danger-err.md) | Semantic status color tokens (success/info/warning/danger/error) | AMBIGUOUS | — |
| [RULE-ALERTAS-027](alert-threshold/RULE-ALERTAS-027-sector-gender-automatic-alert-rollup-get-total-generos-e-ale.md) | Sector gender + automatic-alert rollup (get_total_generos_e_alertas_automaticos) | OK | — |
| [RULE-ALERTAS-028](alert-threshold/RULE-ALERTAS-028-sector-automatic-alert-count-keyed-on-alerta-nao-assistido-g.md) | Sector automatic-alert count keyed on alerta_nao_assistido (get_total_alertas_automaticos) | OK | — |
| [RULE-ALERTAS-029](alert-threshold/RULE-ALERTAS-029-sector-assisted-bed-counts-get-total-assistidos-automatica-h.md) | Sector assisted-bed counts (get_total_assistidos_automatica / _homecare) | OK | — |
| [RULE-ANTIMICROBIANO-001](alert-threshold/RULE-ANTIMICROBIANO-001-antimicrobiano-alert-color-active-calcular-alerta-v2.md) | Antimicrobiano alert color (active - calcular_alerta_v2) | OK | — |
| [RULE-ANTIMICROBIANO-002](alert-threshold/RULE-ANTIMICROBIANO-002-antimicrobiano-alert-color-legacy-unused-calcular-alerta.md) | Antimicrobiano alert color (legacy unused - calcular_alerta) | AMBIGUOUS | — |
| [RULE-BALANCO-HIDRICO-025](alert-threshold/RULE-BALANCO-HIDRICO-025-fluid-balance-overview-cell-visibility-threshold-grid-vs-mob.md) | Fluid-balance overview cell visibility threshold (grid vs mobile mismatch) | DISCREPANCY | — |
| [RULE-COMUNICACAO-004](alert-threshold/RULE-COMUNICACAO-004-send-qtd-mensagens-to-firebase-per-user-unread-message-count.md) | send_qtd_mensagens_to_firebase — per-user unread-message counter fanout | OK | — |
| [RULE-COMUNICACAO-005](alert-threshold/RULE-COMUNICACAO-005-reduzir-qtd-mensageiro-eligibility-to-decrement-an-observati.md) | reduzir_qtd (mensageiro) — eligibility to decrement an observation's unread badge | OK | — |
| [RULE-COMUNICACAO-006](alert-threshold/RULE-COMUNICACAO-006-firebase-unread-count-decrement-when-an-observation-checagem.md) | Firebase unread-count decrement when an observation checagem is checked off | OK | — |
| [RULE-COMUNICACAO-007](alert-threshold/RULE-COMUNICACAO-007-firebase-message-count-notification-suppressed-for-reply-mes.md) | Firebase message-count notification suppressed for reply messages | OK | — |
| [RULE-COMUNICACAO-008](alert-threshold/RULE-COMUNICACAO-008-chat-message-retention-window-48h-default-96h-when-filtering.md) | Chat message retention window - 48h default, 96h when filtering by leito | OK | — |
| [RULE-COMUNICACAO-009](alert-threshold/RULE-COMUNICACAO-009-popup-notification-throttled-to-one-per-2-seconds.md) | Popup notification throttled to one per 2 seconds | OK | — |
| [RULE-COMUNICACAO-010](alert-threshold/RULE-COMUNICACAO-010-notification-alert-color-only-applied-for-leito-type-message.md) | Notification alert color only applied for leito-type messages | OK | — |
| [RULE-COMUNICACAO-020](alert-threshold/RULE-COMUNICACAO-020-real-time-notifications-filter-out-the-current-user-s-own-me.md) | Real-time notifications filter out the current user's own messages | OK | — |
| [RULE-COMUNICACAO-046](alert-threshold/RULE-COMUNICACAO-046-unread-counter-decrement-eligibility-predicate-reduzir-qtd.md) | Unread-counter decrement eligibility predicate (reduzir_qtd) | OK | — |
| [RULE-EFICIENCIA-001](alert-threshold/RULE-EFICIENCIA-001-eficiencia-v3-alert-aggregation-calcular-alerta-v2-wired.md) | Eficiencia v3 alert aggregation (calcular_alerta_v2, wired) | OK | — |
| [RULE-EFICIENCIA-005](alert-threshold/RULE-EFICIENCIA-005-eficiencia-v3-criterio-9-coma-without-sedation-defined-unwir.md) | Eficiencia v3 criterio_9 - coma without sedation (defined, unwired) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-EFICIENCIA-006](alert-threshold/RULE-EFICIENCIA-006-eficiencia-v3-criterio-10-mechanical-restraint-without-agita.md) | Eficiencia v3 criterio_10 - mechanical restraint without agitation (AMARELO, wired) | AMBIGUOUS | DISCREPANCY (moderate) |
| [RULE-EFICIENCIA-012](alert-threshold/RULE-EFICIENCIA-012-eficiencia-active-alert-text-payload-catalog-get-payload-tri.md) | Eficiencia active alert-text payload catalog (get_payload_trilha_eficiencia / eficiencia_automa | OK | VERIFIED |
| [RULE-EQUILIBRIO-001](alert-threshold/RULE-EQUILIBRIO-001-fluid-balance-positive-fluid-balance-and-maintenance-fluid-l.md) | Fluid balance - positive fluid balance and maintenance-fluid limits (criteria 1-4) | OK | — |
| [RULE-EQUILIBRIO-003](alert-threshold/RULE-EQUILIBRIO-003-equilibrio-trilha-alert-color-aggregation-v1-trilhaequilibri.md) | Equilibrio trilha alert-color aggregation (v1, TrilhaEquilibrioModel.calcular_alerta) | OK | — |
| [RULE-ESTABILIDADE-003](alert-threshold/RULE-ESTABILIDADE-003-estabilidade-v3-criterio-1-hypoperfusion-on-vasopressor.md) | Estabilidade v3 criterio_1 - hypoperfusion on vasopressor | OK | VERIFIED |
| [RULE-ESTABILIDADE-005](alert-threshold/RULE-ESTABILIDADE-005-estabilidade-v3-criterio-3-lactate-elevation-with-sepsis-the.md) | Estabilidade v3 criterio_3 - lactate elevation with sepsis therapy | AMBIGUOUS | DISCREPANCY (moderate) |
| [RULE-ESTABILIDADE-006](alert-threshold/RULE-ESTABILIDADE-006-estabilidade-v3-criterio-4-persistent-shock-on-low-dose-vaso.md) | Estabilidade v3 criterio_4 - persistent shock on low-dose vasopressor | OK | VERIFIED |
| [RULE-ESTABILIDADE-007](alert-threshold/RULE-ESTABILIDADE-007-estabilidade-v3-criterio-7-high-dose-noradrenaline-without-a.md) | Estabilidade v3 criterio_7 - high-dose noradrenaline without adjuncts (VERMELHO, wired) | OK | DISCREPANCY (moderate) |
| [RULE-ESTABILIDADE-008](alert-threshold/RULE-ESTABILIDADE-008-estabilidade-v3-criterio-8-refractory-shock-triple-therapy.md) | Estabilidade v3 criterio_8 - refractory shock triple therapy | OK | DISCREPANCY (moderate) |
| [RULE-ESTABILIDADE-009](alert-threshold/RULE-ESTABILIDADE-009-estabilidade-v3-criterio-9-dobutamine-with-high-dose-noradre.md) | Estabilidade v3 criterio_9 - dobutamine with high-dose noradrenaline | OK | DISCREPANCY (moderate) |
| [RULE-ESTABILIDADE-011](alert-threshold/RULE-ESTABILIDADE-011-estabilidade-v3-criterio-11-bicarbonate-despite-compensated.md) | Estabilidade v3 criterio_11 - bicarbonate despite compensated acidosis | OK | DISCREPANCY (low) |
| [RULE-ESTABILIDADE-012](alert-threshold/RULE-ESTABILIDADE-012-estabilidade-v3-criterio-12-antihypertensive-with-recurrent.md) | Estabilidade v3 criterio_12 - antihypertensive with recurrent hypotension (AMARELO, wired) | DISCREPANCY | — |
| [RULE-ESTABILIDADE-013](alert-threshold/RULE-ESTABILIDADE-013-estabilidade-v3-criterio-13-recurrent-hypertension-off-vasop.md) | Estabilidade v3 criterio_13 - recurrent hypertension off vasopressor (AMARELO, wired) | DISCREPANCY | — |
| [RULE-ESTABILIDADE-014](alert-threshold/RULE-ESTABILIDADE-014-estabilidade-v3-alert-level-calcular-alerta-calcular-alerta.md) | Estabilidade v3 alert level (calcular_alerta == calcular_alerta_v2) | OK | — |
| [RULE-ESTABILIDADE-015](alert-threshold/RULE-ESTABILIDADE-015-estabilidade-facade-alert-text-perfusion-shock-triggers-bica.md) | Estabilidade facade alert-text - perfusion/shock triggers & bicarbonate (criteria 1-6, 11) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-ESTABILIDADE-023](alert-threshold/RULE-ESTABILIDADE-023-estabilidade-manual-pathway-alert-level.md) | Estabilidade manual pathway alert level | OK | — |
| [RULE-ESTABILIDADE-025](alert-threshold/RULE-ESTABILIDADE-025-estabilizacao-v1-alert-with-criterio-6-combination-clause.md) | Estabilizacao v1 alert with criterio_6 combination clause | OK | — |
| [RULE-FORMULARIOS-CLINICOS-004](alert-threshold/RULE-FORMULARIOS-CLINICOS-004-peri-wound-edema-classification-4-cm-threshold-enum-backend.md) | Peri-wound edema classification - 4 cm threshold enum (backend canonical) | DISCREPANCY | DISCREPANCY (low) |
| [RULE-FORMULARIOS-CLINICOS-005](alert-threshold/RULE-FORMULARIOS-CLINICOS-005-nursing-cardiovascular-assessment-enums-with-capillary-refil.md) | Nursing cardiovascular assessment enums with capillary-refill (TEC) > 5 s alert | OK | DISCREPANCY (low) |
| [RULE-FORMULARIOS-CLINICOS-006](alert-threshold/RULE-FORMULARIOS-CLINICOS-006-nursing-technician-diet-block-ranges-subset.md) | Nursing-technician diet block ranges (subset) | OK | — |
| [RULE-INDICADORES-ETL-001](alert-threshold/RULE-INDICADORES-ETL-001-sector-alert-share-percentage-formula.md) | Sector alert-share percentage formula | OK | UNVERIFIABLE |
| [RULE-INDICADORES-ETL-002](alert-threshold/RULE-INDICADORES-ETL-002-sector-assisted-share-percentage-formula.md) | Sector assisted-share percentage formula | OK | UNVERIFIABLE |
| [RULE-INDICADORES-ETL-005](alert-threshold/RULE-INDICADORES-ETL-005-bed-occupancy-percentage-color-thresholds.md) | Bed-occupancy percentage color thresholds | OK | — |
| [RULE-INDICADORES-ETL-006](alert-threshold/RULE-INDICADORES-ETL-006-sector-level-aggregate-alert-color-decision-tree.md) | Sector-level aggregate alert-color decision tree | OK | — |
| [RULE-INDICADORES-ETL-007](alert-threshold/RULE-INDICADORES-ETL-007-dashboard-alert-count-4th-severity-level-inconsistent-with-3.md) | Dashboard alert-count 4th severity level inconsistent with 3-level Alerta elsewhere | DISCREPANCY | — |
| [RULE-MOVIMENTACAO-ADT-012](alert-threshold/RULE-MOVIMENTACAO-ADT-012-bed-movimentacao-alert-aggregation-new-alert-notification.md) | Bed/movimentacao alert aggregation + new-alert notification | OK | — |
| [RULE-MOVIMENTACAO-ADT-014](alert-threshold/RULE-MOVIMENTACAO-ADT-014-bed-trilha-alert-severity-levels-amarelo-neutro-vermelho.md) | Bed/trilha alert severity levels (AMARELO\|NEUTRO\|VERMELHO) | OK | — |
| [RULE-MOVIMENTACAO-ADT-015](alert-threshold/RULE-MOVIMENTACAO-ADT-015-overdue-protocol-item-indicator-on-trilha-chip.md) | Overdue-protocol-item indicator on trilha chip | OK | — |
| [RULE-MOVIMENTACAO-ADT-016](alert-threshold/RULE-MOVIMENTACAO-ADT-016-invasive-procedures-alert-indicator.md) | Invasive-procedures alert indicator | OK | — |
| [RULE-NUTRICAO-004](alert-threshold/RULE-NUTRICAO-004-nutrition-alert-computation-calcular-alerta-amarelo-branch-u.md) | Nutrition alert computation (calcular_alerta) - AMARELO branch unreachable | DISCREPANCY | — |
| [RULE-NUTRICAO-005](alert-threshold/RULE-NUTRICAO-005-nutrition-therapy-assessment-block-frontend-diet-routes-acce.md) | Nutrition-therapy assessment block (frontend) - diet routes, acceptance, ranges and prophylaxis | OK | DISCREPANCY (low) |
| [RULE-PIORA-CLINICA-010](alert-threshold/RULE-PIORA-CLINICA-010-piora-clinica-calculo-do-alerta-soma-agregada-gatilho-por-cr.md) | Piora Clinica - Calculo do alerta (soma agregada + gatilho por criterio) | DISCREPANCY | DISCREPANCY (high) |
| [RULE-PIORA-CLINICA-011](alert-threshold/RULE-PIORA-CLINICA-011-piora-clinica-payload-de-alertas-recomendacoes-intervencoes.md) | Piora Clinica - Payload de alertas/recomendacoes/intervencoes por (criterio, codigo de severida | AMBIGUOUS | UNVERIFIABLE |
| [RULE-PRESCRICAO-002](alert-threshold/RULE-PRESCRICAO-002-dose-level-medication-suspension-check-get-suspenso.md) | Dose-level medication suspension check (get_suspenso) | DISCREPANCY | — |
| [RULE-PRESCRICAO-003](alert-threshold/RULE-PRESCRICAO-003-continuous-prescription-order-level-suspension-flag-now-base.md) | Continuous-prescription (order-level) suspension flag - now-based | DISCREPANCY | — |
| [RULE-PROFILAXIA-003](alert-threshold/RULE-PROFILAXIA-003-prophylaxis-v1-alert-aggregation-amarelo-vermelho-scoring.md) | Prophylaxis v1 alert aggregation (amarelo/vermelho scoring) | OK | — |
| [RULE-PROFILAXIA-004](alert-threshold/RULE-PROFILAXIA-004-prophylaxis-v3-alert-aggregation-amarelo-vermelho-scoring.md) | Prophylaxis v3 alert aggregation (amarelo/vermelho scoring) | OK | — |
| [RULE-SEDACAO-014](alert-threshold/RULE-SEDACAO-014-sedacao-v3-alert-calcular-alerta-v2-used-legacy-calcular-ale.md) | Sedacao v3 alert (calcular_alerta_v2 used; legacy calcular_alerta present but unused) | OK | — |
| [RULE-SEDACAO-021](alert-threshold/RULE-SEDACAO-021-sedation-manual-pathway-alert-level-count-of-criteria.md) | Sedation manual pathway alert level (count of criteria) | OK | — |
| [RULE-SEDACAO-023](alert-threshold/RULE-SEDACAO-023-sedacao-v1-alert-trilhasedacaomodel-calcular-alerta.md) | Sedacao v1 alert (TrilhaSedacaoModel.calcular_alerta) | OK | — |
| [RULE-SEPSE-003](alert-threshold/RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md) | Sepse - Classificacao de alerta (maiores/menores) | DISCREPANCY | DISCREPANCY (low) |
| [RULE-SEPSE-004](alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md) | Sepsis pathway alert (major/minor two-axis threshold) | OK | UNVERIFIABLE |
| [RULE-SEPSE-007](alert-threshold/RULE-SEPSE-007-sepse-v3-criterio-1-fever-without-vasopressor.md) | SEPSE v3 criterio_1 - fever without vasopressor | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-SEPSE-008](alert-threshold/RULE-SEPSE-008-sepse-v3-criterio-2-tachypnea-hypoxemia-without-vasopressor.md) | SEPSE v3 criterio_2 - tachypnea/hypoxemia without vasopressor or invasive vent | OK | VERIFIED (low) |
| [RULE-SEPSE-009](alert-threshold/RULE-SEPSE-009-sepse-v3-criterio-3-respiratory-failure-prescription.md) | SEPSE v3 criterio_3 - respiratory failure prescription | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-SEPSE-010](alert-threshold/RULE-SEPSE-010-sepse-v3-criterio-4-newly-started-vasopressor.md) | SEPSE v3 criterio_4 - newly started vasopressor | OK | VERIFIED |
| [RULE-SEPSE-011](alert-threshold/RULE-SEPSE-011-sepse-v3-criterio-5-hypotension-without-vasopressor.md) | SEPSE v3 criterio_5 - hypotension without vasopressor | OK | VERIFIED |
| [RULE-SEPSE-012](alert-threshold/RULE-SEPSE-012-sepse-v3-criterio-6-thrombocytopenia-without-vasopressor.md) | SEPSE v3 criterio_6 - thrombocytopenia without vasopressor | OK | VERIFIED |
| [RULE-SEPSE-013](alert-threshold/RULE-SEPSE-013-sepse-v3-criterio-7-hyperlactatemia-without-vasopressor.md) | SEPSE v3 criterio_7 - hyperlactatemia without vasopressor | OK | DISCREPANCY (low) |
| [RULE-SEPSE-015](alert-threshold/RULE-SEPSE-015-sepse-v3-criterio-9-acute-kidney-injury-without-vasopressor.md) | SEPSE v3 criterio_9 - acute kidney injury without vasopressor/dialysis | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-SEPSE-016](alert-threshold/RULE-SEPSE-016-sepse-v3-criterio-10-acute-encephalopathy-delirium.md) | SEPSE v3 criterio_10 - acute encephalopathy/delirium | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-SEPSE-017](alert-threshold/RULE-SEPSE-017-sepse-v3-criterio-11-hyperbilirubinemia-jaundice-incomplete.md) | SEPSE v3 criterio_11 - hyperbilirubinemia/jaundice (incomplete) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-SEPSE-018](alert-threshold/RULE-SEPSE-018-sepse-v3-criterio-12-hypothermia-minor.md) | SEPSE v3 criterio_12 - hypothermia (minor) | OK | VERIFIED |
| [RULE-SEPSE-019](alert-threshold/RULE-SEPSE-019-sepse-v3-criterio-13-tachycardia-minor-wrong-column.md) | SEPSE v3 criterio_13 - tachycardia (minor, wrong column) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-SEPSE-020](alert-threshold/RULE-SEPSE-020-sepse-v3-criterio-14-respiratory-alkalosis-hypoxemia-spontan.md) | SEPSE v3 criterio_14 - respiratory alkalosis/hypoxemia spontaneous vent (minor) | OK | DISCREPANCY (moderate) |
| [RULE-SEPSE-021](alert-threshold/RULE-SEPSE-021-sepse-v3-criterio-15-leukocytosis-leukopenia-bandemia-crp-mi.md) | SEPSE v3 criterio_15 - leukocytosis/leukopenia/bandemia/CRP (minor) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-SEPSE-022](alert-threshold/RULE-SEPSE-022-sepse-v3-criterio-16-prolonged-capillary-refill-minor-new-on.md) | SEPSE v3 criterio_16 - prolonged capillary refill (minor, new onset) | OK | VERIFIED |
| [RULE-SEPSE-023](alert-threshold/RULE-SEPSE-023-sepse-v3-criterio-17-enteral-tube-with-adequate-gcs-minor.md) | SEPSE v3 criterio_17 - enteral tube with adequate GCS (minor) | OK | UNVERIFIABLE |
| [RULE-SEPSE-024](alert-threshold/RULE-SEPSE-024-sepse-v3-criterio-18-central-line-7-days-minor.md) | SEPSE v3 criterio_18 - central line > 7 days (minor) | OK | UNVERIFIABLE |
| [RULE-SEPSE-025](alert-threshold/RULE-SEPSE-025-sepse-v3-criterio-19-femoral-central-line-5-days-minor.md) | SEPSE v3 criterio_19 - femoral central line > 5 days (minor) | OK | UNVERIFIABLE |
| [RULE-SEPSE-026](alert-threshold/RULE-SEPSE-026-sepse-v3-criterio-20-recent-abdominal-surgery-minor.md) | SEPSE v3 criterio_20 - recent abdominal surgery (minor) | OK | UNVERIFIABLE |
| [RULE-SEPSE-058](alert-threshold/RULE-SEPSE-058-sepse-v3-automatica-trigger-threshold-table-20-criteria.md) | Sepse v3 automatica - trigger threshold table (20 criteria) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-SEPSE-062](alert-threshold/RULE-SEPSE-062-sepse-reassessment-lab-thresholds-bicarbonate-dobutamine-tra.md) | SEPSE reassessment lab thresholds (bicarbonate, dobutamine, transfusion) | OK | VERIFIED |
| [RULE-SEPSE-095](alert-threshold/RULE-SEPSE-095-sepsis-protocol-item-first-hour-delay-alert.md) | Sepsis protocol item first-hour delay alert | DISCREPANCY | — |
| [RULE-SINAIS-VITAIS-001](alert-threshold/RULE-SINAIS-VITAIS-001-blood-pressure-and-heart-rate-plausible-ranges-movimentacao.md) | Blood-pressure and heart-rate plausible ranges (movimentacao form) | OK | — |
| [RULE-SINAIS-VITAIS-002](alert-threshold/RULE-SINAIS-VITAIS-002-blood-gas-and-laboratory-plausible-ranges-movimentacao-form.md) | Blood-gas and laboratory plausible ranges (movimentacao form) | OK | — |
| [RULE-SINAIS-VITAIS-003](alert-threshold/RULE-SINAIS-VITAIS-003-urine-output-and-temperature-plausible-ranges-movimentacao-f.md) | Urine-output and temperature plausible ranges (movimentacao form) | OK | — |
| [RULE-SINAIS-VITAIS-004](alert-threshold/RULE-SINAIS-VITAIS-004-capillary-refill-time-tec-range-and-5s-threshold-inconsisten.md) | Capillary refill time (TEC) range and >5s threshold — inconsistent encodings | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-SINAIS-VITAIS-005](alert-threshold/RULE-SINAIS-VITAIS-005-physician-form-vital-sign-ranges-partial-hr-fr-temp-spo2-unb.md) | Physician-form vital-sign ranges (partial) — HR/FR/temp/SpO2 unbounded | DISCREPANCY | — |
| [RULE-TENANCY-ORGANIZACAO-007](alert-threshold/RULE-TENANCY-ORGANIZACAO-007-establishment-unread-message-count-sums-across-all-sectors-n.md) | Establishment unread message count sums across ALL sectors, not just user's own | AMBIGUOUS | UNVERIFIABLE |
| [RULE-TENANCY-ORGANIZACAO-008](alert-threshold/RULE-TENANCY-ORGANIZACAO-008-sector-unread-message-count-via-firestore.md) | Sector unread message count via Firestore | OK | UNVERIFIABLE |
| [RULE-TENANCY-ORGANIZACAO-011](alert-threshold/RULE-TENANCY-ORGANIZACAO-011-sector-alert-counts-merge-manual-movement-alerts-with-automa.md) | Sector alert counts merge manual movement alerts with automatic-pathway alerts | OK | UNVERIFIABLE |
| [RULE-TENANCY-ORGANIZACAO-035](alert-threshold/RULE-TENANCY-ORGANIZACAO-035-sector-total-alert-counts-branch-by-tipo.md) | Sector total alert counts branch by tipo | OK | — |
| [RULE-TRILHAS-ENGINE-004](alert-threshold/RULE-TRILHAS-ENGINE-004-pathway-alert-status-color-precedence.md) | Pathway alert-status color precedence | OK | — |
| [RULE-TRILHAS-ENGINE-008](alert-threshold/RULE-TRILHAS-ENGINE-008-pathway-overdue-item-alert.md) | Pathway overdue-item alert | OK | — |
| [RULE-VENTILACAO-014](alert-threshold/RULE-VENTILACAO-014-ventilation-pathway-alert-count-special-criterion-override-t.md) | Ventilation pathway alert (count + special-criterion override) - trilha_manual | OK | — |
| [RULE-VENTILACAO-015](alert-threshold/RULE-VENTILACAO-015-ventilacao-v1-alert-used-calcular-alerta-v2-trilha-automatic.md) | Ventilacao v1 alert (used - calcular_alerta_v2, trilha_automatica) | OK | — |
| [RULE-VENTILACAO-016](alert-threshold/RULE-VENTILACAO-016-ventilacao-v1-alert-unused-legacy-calcular-alerta-trilha-aut.md) | Ventilacao v1 alert (unused legacy - calcular_alerta, trilha_automatica) | AMBIGUOUS | — |
| [RULE-VENTILACAO-018](alert-threshold/RULE-VENTILACAO-018-ventilator-parameter-validation-ranges-movimentacao-form.md) | Ventilator parameter validation ranges (movimentacao form) | OK | — |
| [RULE-VENTILACAO-021](alert-threshold/RULE-VENTILACAO-021-supplemental-o2-flow-valid-range-1-15-l-min-homecare.md) | Supplemental O2 flow valid range 1-15 L/min (homecare) | OK | — |
| [RULE-VENTILACAO-022](alert-threshold/RULE-VENTILACAO-022-peep-pressao-expiratoria-pulmonar-valid-range-5-18-homecare.md) | PEEP (pressao expiratoria pulmonar) valid range 5-18 (homecare) | OK | — |
| [RULE-VENTILACAO-023](alert-threshold/RULE-VENTILACAO-023-inspiratory-pressure-valid-range-5-40-homecare.md) | Inspiratory pressure valid range 5-40 (homecare) | OK | — |

### triage-eligibility (57 rules)

Eligibility and triage predicates (pathway inclusion, bed classification, protocol eligibility)

| Rule | Name | Status | Verdict |
|---|---|---|---|
| [RULE-AUTH-USUARIOS-020](triage-eligibility/RULE-AUTH-USUARIOS-020-permission-string-ssr-route-guard-validateroute-incl-dead-co.md) | Permission-string SSR route guard (validateRoute), incl. dead-code token check | DISCREPANCY | — |
| [RULE-AUTH-USUARIOS-021](triage-eligibility/RULE-AUTH-USUARIOS-021-bed-management-page-reuses-access-group-permission.md) | Bed-management page reuses access-group permission | DISCREPANCY | — |
| [RULE-AUTH-USUARIOS-022](triage-eligibility/RULE-AUTH-USUARIOS-022-automatica-only-shortcuts-not-enforced-server-side.md) | Automatica-only shortcuts not enforced server-side | DISCREPANCY | — |
| [RULE-AUTH-USUARIOS-023](triage-eligibility/RULE-AUTH-USUARIOS-023-redirect-authenticated-user-away-from-login-page.md) | Redirect authenticated user away from login page | OK | — |
| [RULE-AUTH-USUARIOS-025](triage-eligibility/RULE-AUTH-USUARIOS-025-professional-profile-self-or-permission-access-gate.md) | Professional profile self-or-permission access gate | OK | — |
| [RULE-AUTH-USUARIOS-026](triage-eligibility/RULE-AUTH-USUARIOS-026-homecare-only-gestao-de-pacientes-tab.md) | Homecare-only "Gestão de Pacientes" tab | OK | — |
| [RULE-AUTH-USUARIOS-030](triage-eligibility/RULE-AUTH-USUARIOS-030-external-sso-fallback-with-auto-provisioning.md) | External SSO fallback with auto-provisioning | DISCREPANCY | — |
| [RULE-BALANCO-HIDRICO-034](triage-eligibility/RULE-BALANCO-HIDRICO-034-fluid-balance-action-authorization-manage-delete-permissions.md) | Fluid-balance action authorization (manage / delete permissions) | OK | — |
| [RULE-COMUNICACAO-016](triage-eligibility/RULE-COMUNICACAO-016-video-call-join-gated-on-detected-video-input-device.md) | Video-call join gated on detected video input device | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-014](triage-eligibility/RULE-DOCUMENTACAO-FATURAMENTO-014-double-gated-evolution-report-access.md) | Double-gated evolution report access | AMBIGUOUS | — |
| [RULE-EFICIENCIA-002](triage-eligibility/RULE-EFICIENCIA-002-eficiencia-v3-criterio-3-unjustified-rbc-transfusion-at-hb-7.md) | Eficiencia v3 criterio_3 - unjustified RBC transfusion at Hb>=7 (AMARELO, wired) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-EFICIENCIA-003](triage-eligibility/RULE-EFICIENCIA-003-eficiencia-v3-criterio-4-rbc-transfusion-at-hb-6-7-2-units-d.md) | Eficiencia v3 criterio_4 - RBC transfusion at Hb 6-7, 2 units (defined, unwired) | DISCREPANCY | DISCREPANCY (low) |
| [RULE-EFICIENCIA-004](triage-eligibility/RULE-EFICIENCIA-004-eficiencia-v3-criterio-5-platelet-transfusion-at-plt-25000-v.md) | Eficiencia v3 criterio_5 - platelet transfusion at Plt>25000 (VERMELHO, wired) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-EFICIENCIA-008](triage-eligibility/RULE-EFICIENCIA-008-eficiencia-v3-criterio-2-icu-discharge-readiness-defined-unw.md) | Eficiencia v3 criterio_2 - ICU discharge readiness (defined, unwired) | DISCREPANCY | DISCREPANCY |
| [RULE-EFICIENCIA-009](triage-eligibility/RULE-EFICIENCIA-009-eficiencia-v3-criterio-6-frailty-palliative-appropriateness.md) | Eficiencia v3 criterio_6 - frailty / palliative-appropriateness (defined, unwired) | OK | UNVERIFIABLE |
| [RULE-EFICIENCIA-011](triage-eligibility/RULE-EFICIENCIA-011-eficiencia-v3-criterio-8-low-support-step-down-readiness-def.md) | Eficiencia v3 criterio_8 - low-support step-down readiness (defined, unwired) | DISCREPANCY | DISCREPANCY |
| [RULE-EVOLUCOES-019](triage-eligibility/RULE-EVOLUCOES-019-author-only-edit-inactivate-re-sign-eligibility.md) | Author-only edit / inactivate / re-sign eligibility | OK | — |
| [RULE-FORMULARIOS-CLINICOS-007](triage-eligibility/RULE-FORMULARIOS-CLINICOS-007-home-care-incident-triage-urgency-grade-and-symptom-classifi.md) | Home-care incident triage - urgency grade and symptom classification | OK | — |
| [RULE-FORMULARIOS-CLINICOS-008](triage-eligibility/RULE-FORMULARIOS-CLINICOS-008-physiotherapy-early-mobilization-eligibility-flags.md) | Physiotherapy early-mobilization eligibility flags | OK | — |
| [RULE-MOVIMENTACAO-ADT-020](triage-eligibility/RULE-MOVIMENTACAO-ADT-020-bed-patient-resolution-and-auto-creation.md) | Bed patient resolution and auto-creation | OK | — |
| [RULE-MOVIMENTACAO-ADT-021](triage-eligibility/RULE-MOVIMENTACAO-ADT-021-homecare-vs-automatica-bed-classification-and-tenant-routing.md) | Homecare vs automatica bed classification and tenant routing | OK | — |
| [RULE-MOVIMENTACAO-ADT-025](triage-eligibility/RULE-MOVIMENTACAO-ADT-025-bed-eligibility-for-manual-movimentacao-admission.md) | Bed eligibility for manual movimentacao (admission) | OK | — |
| [RULE-NUTRICAO-006](triage-eligibility/RULE-NUTRICAO-006-stress-ulcer-nutrition-prophylaxis-indication-enum.md) | Stress-ulcer / nutrition prophylaxis indication enum | OK | DISCREPANCY (low) |
| [RULE-OPERACIONAL-INFRA-013](triage-eligibility/RULE-OPERACIONAL-INFRA-013-popular-banco-sdra-ards-severity-enum-synthetic-data.md) | popular_banco SDRA (ARDS) severity enum (synthetic data) | OK | VERIFIED |
| [RULE-PRESCRICAO-016](triage-eligibility/RULE-PRESCRICAO-016-add-new-horario-button-eligibility.md) | Add-new-horario button eligibility | OK | — |
| [RULE-PRESCRICAO-017](triage-eligibility/RULE-PRESCRICAO-017-only-the-checking-user-may-revert-a-check.md) | Only the checking user may revert a check | OK | — |
| [RULE-PRESCRICAO-018](triage-eligibility/RULE-PRESCRICAO-018-can-manage-prescricao-gates-all-administration-controls.md) | can_manage_prescricao gates all administration controls | OK | — |
| [RULE-SEPSE-038](triage-eligibility/RULE-SEPSE-038-sepsis-c1-major-fever.md) | Sepsis C1 (major) - fever | OK | VERIFIED |
| [RULE-SEPSE-039](triage-eligibility/RULE-SEPSE-039-sepsis-c2-major-spontaneous-respiratory-distress.md) | Sepsis C2 (major) - spontaneous respiratory distress | OK | VERIFIED |
| [RULE-SEPSE-040](triage-eligibility/RULE-SEPSE-040-sepsis-c3-major-recent-start-of-mechanical-ventilation.md) | Sepsis C3 (major) - recent start of mechanical ventilation | OK | UNVERIFIABLE |
| [RULE-SEPSE-041](triage-eligibility/RULE-SEPSE-041-sepsis-c4-major-noradrenaline-started-in-last-24h.md) | Sepsis C4 (major) - noradrenaline started in last 24h | OK | UNVERIFIABLE |
| [RULE-SEPSE-042](triage-eligibility/RULE-SEPSE-042-sepsis-c5-major-slow-capillary-refill.md) | Sepsis C5 (major) - slow capillary refill | OK | DISCREPANCY (low) |
| [RULE-SEPSE-043](triage-eligibility/RULE-SEPSE-043-sepsis-c6-major-hypotension-pas-90-or-pad-90-in-24h.md) | Sepsis C6 (major) - hypotension (PAS<90 or PAD<90 in 24h) | DISCREPANCY | DISCREPANCY (high) |
| [RULE-SEPSE-044](triage-eligibility/RULE-SEPSE-044-sepsis-c7-major-oliguria-or-rising-creatinine.md) | Sepsis C7 (major) - oliguria or rising creatinine | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-SEPSE-045](triage-eligibility/RULE-SEPSE-045-sepsis-c8-major-glasgow-drop-or-delirium.md) | Sepsis C8 (major) - Glasgow drop or delirium | OK | VERIFIED |
| [RULE-SEPSE-046](triage-eligibility/RULE-SEPSE-046-sepsis-c9-major-hyperbilirubinemia.md) | Sepsis C9 (major) - hyperbilirubinemia | OK | VERIFIED |
| [RULE-SEPSE-047](triage-eligibility/RULE-SEPSE-047-sepsis-c10-minor-hypothermia-in-last-24h.md) | Sepsis C10 (minor) - hypothermia in last 24h | OK | VERIFIED |
| [RULE-SEPSE-048](triage-eligibility/RULE-SEPSE-048-sepsis-c11-minor-tachycardia.md) | Sepsis C11 (minor) - tachycardia | AMBIGUOUS | DISCREPANCY (low) |
| [RULE-SEPSE-049](triage-eligibility/RULE-SEPSE-049-sepsis-c12-minor-hypocapnia-or-poor-oxygenation.md) | Sepsis C12 (minor) - hypocapnia or poor oxygenation | OK | VERIFIED |
| [RULE-SEPSE-050](triage-eligibility/RULE-SEPSE-050-sepsis-c13-minor-elevated-arterial-lactate.md) | Sepsis C13 (minor) - elevated arterial lactate | OK | DISCREPANCY (low) |
| [RULE-SEPSE-051](triage-eligibility/RULE-SEPSE-051-sepsis-c14-minor-leukocytosis-in-last-24h.md) | Sepsis C14 (minor) - leukocytosis in last 24h | OK | VERIFIED (low) |
| [RULE-SEPSE-052](triage-eligibility/RULE-SEPSE-052-sepsis-c15-minor-thrombocytopenia-in-last-24h.md) | Sepsis C15 (minor) - thrombocytopenia in last 24h | OK | VERIFIED (low) |
| [RULE-SEPSE-053](triage-eligibility/RULE-SEPSE-053-sepsis-c16-minor-poor-oral-intake-with-preserved-consciousne.md) | Sepsis C16 (minor) - poor oral intake with preserved consciousness | OK | UNVERIFIABLE |
| [RULE-SEPSE-054](triage-eligibility/RULE-SEPSE-054-sepsis-c17-minor-depressed-consciousness-in-last-12h.md) | Sepsis C17 (minor) - depressed consciousness in last 12h | OK | DISCREPANCY (low) |
| [RULE-SEPSE-055](triage-eligibility/RULE-SEPSE-055-sepsis-c18-minor-central-line-7-days.md) | Sepsis C18 (minor) - central line > 7 days | OK | UNVERIFIABLE |
| [RULE-SEPSE-056](triage-eligibility/RULE-SEPSE-056-sepsis-c19-minor-femoral-central-line-5-days.md) | Sepsis C19 (minor) - femoral central line > 5 days | OK | UNVERIFIABLE |
| [RULE-SEPSE-057](triage-eligibility/RULE-SEPSE-057-sepsis-c20-minor-recent-abdominal-surgery.md) | Sepsis C20 (minor) - recent abdominal surgery | OK | UNVERIFIABLE |
| [RULE-SEPSE-066](triage-eligibility/RULE-SEPSE-066-sepsis-pathway-disabled-legacy-criteria-v-old-27-vs-current.md) | Sepsis pathway - disabled/legacy criteria (v-old 27 vs current 20) | AMBIGUOUS | — |
| [RULE-SEPSE-067](triage-eligibility/RULE-SEPSE-067-sepsis-infection-source-screening-flags-movimentacao.md) | Sepsis / infection-source screening flags (movimentacao) | OK | — |
| [RULE-SEPSE-099](triage-eligibility/RULE-SEPSE-099-manual-sepsis-pathway-active-criteria-descriptions-regras-20.md) | Manual sepsis pathway active criteria descriptions (_REGRAS, 20 criteria) with criterio_8 key-t | DISCREPANCY | — |
| [RULE-TENANCY-ORGANIZACAO-025](triage-eligibility/RULE-TENANCY-ORGANIZACAO-025-homecare-only-dashboard-shortcuts-feed-relatorio-de-evolucao.md) | Homecare-only dashboard shortcuts (Feed / Relatório de Evolução) | OK | — |
| [RULE-TENANCY-ORGANIZACAO-026](triage-eligibility/RULE-TENANCY-ORGANIZACAO-026-manual-type-gates-estabelecimento-creation.md) | Manual-type gates estabelecimento creation | OK | — |
| [RULE-TENANCY-ORGANIZACAO-027](triage-eligibility/RULE-TENANCY-ORGANIZACAO-027-manual-type-gates-leito-creation.md) | Manual-type gates leito creation | OK | — |
| [RULE-TENANCY-ORGANIZACAO-028](triage-eligibility/RULE-TENANCY-ORGANIZACAO-028-manual-type-gates-setor-creation-and-editing.md) | Manual-type gates setor creation and editing | OK | — |
| [RULE-TRILHAS-ENGINE-005](triage-eligibility/RULE-TRILHAS-ENGINE-005-interactive-care-pathway-eligibility-sepse-profilaxia.md) | Interactive care-pathway eligibility (Sepse / Profilaxia) | OK | — |
| [RULE-TRILHAS-ENGINE-006](triage-eligibility/RULE-TRILHAS-ENGINE-006-interactive-pathway-restricted-to-automatic-bed-type.md) | Interactive pathway restricted to automatic bed type | OK | — |
| [RULE-TRILHAS-ENGINE-007](triage-eligibility/RULE-TRILHAS-ENGINE-007-mark-pathway-assisted-eligibility-and-own-record-authorizati.md) | Mark-pathway-assisted eligibility and own-record authorization | OK | — |

### care-pathway (211 rules)

Care-pathway steps, state machines, recommendation payloads, and workflow triggers

| Rule | Name | Status | Verdict |
|---|---|---|---|
| [RULE-ALERTAS-017](care-pathway/RULE-ALERTAS-017-assist-action-trilha-resolution-dual-movimentacao-leito-mode.md) | Assist-action trilha resolution: dual Movimentacao/Leito mode with per-tipo selection strategy | OK | — |
| [RULE-ALERTAS-018](care-pathway/RULE-ALERTAS-018-mensageiro-enviar-observacao-hardcoded-red-level-system-aler.md) | Mensageiro.enviar_observacao - hardcoded RED-level system alert + system-user auto-provisioning | OK | — |
| [RULE-ALERTAS-019](care-pathway/RULE-ALERTAS-019-mensageiro-enviar-observacao-automatica-e-homecare-hardcoded.md) | Mensageiro.enviar_observacao_automatica_e_homecare - hardcoded RED alert with tipo-dependent pa | OK | — |
| [RULE-ALERTAS-020](care-pathway/RULE-ALERTAS-020-neutro-alert-resets-assistido-flag-on-save-shared-behavior.md) | NEUTRO alert resets assistido flag on save (shared behavior) | OK | — |
| [RULE-ALERTAS-021](care-pathway/RULE-ALERTAS-021-trilha-care-pathway-model-mapping-per-bed-type-with-v3-model.md) | Trilha (care-pathway) model mapping per bed type, with v3 model migration | OK | — |
| [RULE-ALERTAS-022](care-pathway/RULE-ALERTAS-022-marking-a-trilha-as-assistido-bulk-update-for-v3-models-inst.md) | Marking a trilha as assistido - bulk update for v3 models, instance save for legacy | OK | — |
| [RULE-ALERTAS-023](care-pathway/RULE-ALERTAS-023-assistidopor-audit-snapshot-created-only-when-marking-as-ass.md) | AssistidoPor audit snapshot created only when marking as assistido=True | OK | — |
| [RULE-ALERTAS-024](care-pathway/RULE-ALERTAS-024-care-pathway-trilha-status-severity-color-palette-statustril.md) | Care-pathway (trilha) status severity color palette (statusTrilha) | OK | — |
| [RULE-ANTIMICROBIANO-003](care-pathway/RULE-ANTIMICROBIANO-003-antimicrobial-stewardship-criteria-catalog-12-criteria-durat.md) | Antimicrobial stewardship criteria catalog (12 criteria: duration, spectrum, weight/renal dose, | OK | VERIFIED |
| [RULE-AUTH-USUARIOS-016](care-pathway/RULE-AUTH-USUARIOS-016-permission-gate-for-rejecting-closing-sepse-protocol.md) | Permission gate for rejecting/closing SEPSE protocol | OK | — |
| [RULE-AUTH-USUARIOS-038](care-pathway/RULE-AUTH-USUARIOS-038-user-creation-links-to-current-empresa-and-syncs-setores-gru.md) | User creation links to current empresa and syncs setores/grupos | OK | — |
| [RULE-AUTH-USUARIOS-039](care-pathway/RULE-AUTH-USUARIOS-039-user-update-performs-diff-based-setor-sync-scoped-to-current.md) | User update performs diff-based setor sync scoped to current empresa | OK | — |
| [RULE-AUTH-USUARIOS-040](care-pathway/RULE-AUTH-USUARIOS-040-user-deletion-is-a-soft-delete-is-active-flag.md) | User deletion is a soft-delete (is_active flag) | OK | — |
| [RULE-AUTH-USUARIOS-060](care-pathway/RULE-AUTH-USUARIOS-060-company-monitoring-modality-enumeration-duplicate-of-leitoti.md) | Company monitoring-modality enumeration (duplicate of LeitoTipo) | OK | — |
| [RULE-BALANCO-HIDRICO-026](care-pathway/RULE-BALANCO-HIDRICO-026-balanco-hidrico-sub-record-delete-authorization-can-delete-e.md) | Balanco-hidrico sub-record delete authorization (can_delete) - Entrada/Saida/SinaisVitais | DISCREPANCY | — |
| [RULE-BALANCO-HIDRICO-027](care-pathway/RULE-BALANCO-HIDRICO-027-07-00-shift-boundary-assigns-pre-07-00-entries-to-previous-d.md) | 07:00 shift boundary assigns pre-07:00 entries to previous day's balanco | OK | — |
| [RULE-BALANCO-HIDRICO-029](care-pathway/RULE-BALANCO-HIDRICO-029-fluid-balance-intake-type-decision-tree.md) | Fluid-balance intake type decision tree | OK | — |
| [RULE-BALANCO-HIDRICO-030](care-pathway/RULE-BALANCO-HIDRICO-030-oral-diet-acceptance-conditional-volume.md) | Oral-diet acceptance conditional volume | OK | — |
| [RULE-BALANCO-HIDRICO-031](care-pathway/RULE-BALANCO-HIDRICO-031-fluid-balance-output-type-decision-tree.md) | Fluid-balance output type decision tree | OK | — |
| [RULE-BALANCO-HIDRICO-032](care-pathway/RULE-BALANCO-HIDRICO-032-fluid-balance-vital-sign-ventilation-conditional.md) | Fluid-balance vital-sign ventilation conditional | OK | — |
| [RULE-BALANCO-HIDRICO-033](care-pathway/RULE-BALANCO-HIDRICO-033-balanco-hidrico-sub-record-digital-signature-eligibility-can.md) | Balanco-hidrico sub-record digital-signature eligibility (can_assinar) - Entrada/Saida/SinaisVi | OK | — |
| [RULE-BALANCO-HIDRICO-035](care-pathway/RULE-BALANCO-HIDRICO-035-list-endpoint-required-day-auto-create-with-mismatched-day-v.md) | List endpoint required-day + auto-create with mismatched day value | DISCREPANCY | — |
| [RULE-BALANCO-HIDRICO-036](care-pathway/RULE-BALANCO-HIDRICO-036-balanco-hidrico-auto-provisioning-no-direct-write-endpoints.md) | Balanco hidrico auto-provisioning, no direct write endpoints | OK | — |
| [RULE-BALANCO-HIDRICO-041](care-pathway/RULE-BALANCO-HIDRICO-041-fluid-balance-balanco-hidrico-row-type-label-resolution-and.md) | Fluid-balance (balanco hidrico) row type-label resolution and signature-date format | OK | — |
| [RULE-BALANCO-HIDRICO-042](care-pathway/RULE-BALANCO-HIDRICO-042-fluid-balance-record-signature-eligibility.md) | Fluid-balance record signature eligibility | OK | — |
| [RULE-BALANCO-HIDRICO-043](care-pathway/RULE-BALANCO-HIDRICO-043-saida-record-sign-posts-to-the-entrada-route-bug.md) | Saida record sign posts to the "entrada" route (bug) | DISCREPANCY | — |
| [RULE-BALANCO-HIDRICO-044](care-pathway/RULE-BALANCO-HIDRICO-044-fluid-balance-module-navigation-state-routes.md) | Fluid-balance module navigation/state routes | OK | — |
| [RULE-BALANCO-HIDRICO-045](care-pathway/RULE-BALANCO-HIDRICO-045-fluid-balance-record-signing-deletion-lifecycle.md) | Fluid-balance record signing/deletion lifecycle | AMBIGUOUS | — |
| [RULE-COMUNICACAO-003](care-pathway/RULE-COMUNICACAO-003-acaohomecare-balanco-hidrico-method-reference-bug.md) | AcaoHomecare balanco_hidrico method-reference bug | DISCREPANCY | UNVERIFIABLE |
| [RULE-COMUNICACAO-011](care-pathway/RULE-COMUNICACAO-011-notification-click-through-decision-tree.md) | Notification click-through decision tree | OK | — |
| [RULE-COMUNICACAO-013](care-pathway/RULE-COMUNICACAO-013-observation-dual-mode-movimentacao-leito-resolution.md) | Observation dual-mode movimentacao/leito resolution | OK | — |
| [RULE-COMUNICACAO-014](care-pathway/RULE-COMUNICACAO-014-protocol-checklist-item-toggle-authorization.md) | Protocol-checklist item toggle authorization | OK | — |
| [RULE-COMUNICACAO-022](care-pathway/RULE-COMUNICACAO-022-auto-select-first-sector-conversation.md) | Auto-select first sector conversation | OK | — |
| [RULE-COMUNICACAO-023](care-pathway/RULE-COMUNICACAO-023-unread-message-badge-sourced-from-firestore-reset-on-open.md) | Unread-message badge sourced from Firestore, reset on open | OK | — |
| [RULE-COMUNICACAO-024](care-pathway/RULE-COMUNICACAO-024-websocket-driven-feed-auto-refresh-policy.md) | WebSocket-driven feed auto-refresh policy | OK | — |
| [RULE-COMUNICACAO-026](care-pathway/RULE-COMUNICACAO-026-hardcoded-neutral-alert-mock-pathways-in-feed-drawer.md) | Hardcoded neutral-alert mock pathways in feed drawer | DISCREPANCY | — |
| [RULE-COMUNICACAO-027](care-pathway/RULE-COMUNICACAO-027-reaction-hard-delete-override.md) | Reaction hard-delete override | OK | — |
| [RULE-COMUNICACAO-028](care-pathway/RULE-COMUNICACAO-028-online-call-roster-filtered-to-users-currently-in-call.md) | Online-call roster filtered to users currently in call | OK | — |
| [RULE-COMUNICACAO-032](care-pathway/RULE-COMUNICACAO-032-real-time-telemedicine-dependency-stack-agora-rtc-firebase-w.md) | Real-time telemedicine dependency stack (Agora RTC + Firebase + websocket) | OK | — |
| [RULE-COMUNICACAO-040](care-pathway/RULE-COMUNICACAO-040-conditional-rendering-of-trilha-criteria-checklist-in-send-o.md) | Conditional rendering of trilha-criteria checklist in send-observation modal | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-001](care-pathway/RULE-DOCUMENTACAO-FATURAMENTO-001-prescricao-pdf-display-date-formatting.md) | Prescricao PDF display date formatting | OK | VERIFIED |
| [RULE-DOCUMENTACAO-FATURAMENTO-004](care-pathway/RULE-DOCUMENTACAO-FATURAMENTO-004-signed-vs-unsigned-balanco-hidrico-pdf-template-selection.md) | Signed vs unsigned balanco hidrico PDF template selection | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-005](care-pathway/RULE-DOCUMENTACAO-FATURAMENTO-005-pdf-report-dt-entrada-lookup-admission-date.md) | PDF report dt_entrada lookup (admission date) | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-018](care-pathway/RULE-DOCUMENTACAO-FATURAMENTO-018-pdf-report-filename-pattern.md) | PDF report filename pattern | OK | — |
| [RULE-ESTABILIDADE-004](care-pathway/RULE-ESTABILIDADE-004-estabilidade-v3-criterio-2-new-vasopressor-missing-sepsis-wo.md) | Estabilidade v3 criterio_2 - new vasopressor missing sepsis work-up | OK | VERIFIED (low) |
| [RULE-ESTABILIDADE-017](care-pathway/RULE-ESTABILIDADE-017-estabilidade-manual-c1-slow-capillary-refill-on-noradrenalin.md) | Estabilidade manual C1 - slow capillary refill on noradrenaline | OK | DISCREPANCY (moderate) |
| [RULE-ESTABILIDADE-018](care-pathway/RULE-ESTABILIDADE-018-estabilidade-manual-c2-noradrenaline-started-in-last-24h.md) | Estabilidade manual C2 - noradrenaline started in last 24h | OK | — |
| [RULE-ESTABILIDADE-019](care-pathway/RULE-ESTABILIDADE-019-estabilidade-manual-c3-high-noradrenaline-without-rescue-the.md) | Estabilidade manual C3 - high noradrenaline without rescue therapy | DISCREPANCY | DISCREPANCY (low) |
| [RULE-ESTABILIDADE-020](care-pathway/RULE-ESTABILIDADE-020-estabilidade-manual-c4-elevated-arterial-lactate.md) | Estabilidade manual C4 - elevated arterial lactate | OK | DISCREPANCY (low) |
| [RULE-ESTABILIDADE-021](care-pathway/RULE-ESTABILIDADE-021-estabilidade-manual-c5-antihypertensive-with-adequate-pressu.md) | Estabilidade manual C5 - antihypertensive with adequate pressure/noradrenaline | OK | — |
| [RULE-ESTABILIDADE-022](care-pathway/RULE-ESTABILIDADE-022-estabilidade-manual-c6-dobutamine-with-exact-noradrenaline-5.md) | Estabilidade manual C6 - dobutamine with exact noradrenaline 50 | DISCREPANCY | UNVERIFIABLE |
| [RULE-ESTABILIDADE-024](care-pathway/RULE-ESTABILIDADE-024-estabilizacao-trilha2-shock-work-up-vasopressor-escalation-t.md) | Estabilizacao (trilha2) - shock work-up & vasopressor escalation text catalog | AMBIGUOUS | DISCREPANCY (moderate) |
| [RULE-EVOLUCOES-007](care-pathway/RULE-EVOLUCOES-007-form-visibility-rule-own-draft-or-released.md) | Form visibility rule - own draft or released | OK | — |
| [RULE-EVOLUCOES-008](care-pathway/RULE-EVOLUCOES-008-signed-pdf-takes-precedence-over-draft-pdf.md) | Signed PDF takes precedence over draft PDF | OK | — |
| [RULE-EVOLUCOES-009](care-pathway/RULE-EVOLUCOES-009-evolution-release-liberar-gated-by-registered-evolution-type.md) | Evolution release (liberar) gated by registered evolution type | OK | — |
| [RULE-EVOLUCOES-011](care-pathway/RULE-EVOLUCOES-011-evolution-release-eligibility-composite-check-can-liberar.md) | Evolution release eligibility composite check (can_liberar) | AMBIGUOUS | — |
| [RULE-EVOLUCOES-013](care-pathway/RULE-EVOLUCOES-013-conditional-pdf-rendering-of-assessment-sections-based-on-fi.md) | Conditional PDF rendering of assessment sections based on filled fields | OK | — |
| [RULE-EVOLUCOES-014](care-pathway/RULE-EVOLUCOES-014-medical-evolution-displays-most-recent-vital-signs-at-before.md) | Medical evolution displays most recent vital signs at/before its own creation time | OK | — |
| [RULE-EVOLUCOES-015](care-pathway/RULE-EVOLUCOES-015-nutritionist-pdf-displays-pressure-injury-lpp-records-from-t.md) | Nutritionist PDF displays pressure-injury (LPP) records from the latest nursing evolution | OK | — |
| [RULE-EVOLUCOES-016](care-pathway/RULE-EVOLUCOES-016-get-base-evolucao-context-admission-date-included-only-if-ta.md) | get_base_evolucao_context — admission date included only if Tasy micro-indicators exist for the | OK | — |
| [RULE-EVOLUCOES-017](care-pathway/RULE-EVOLUCOES-017-medico-form-bundles-vital-signs-creation-tied-to-daily-balan.md) | Medico form bundles vital-signs creation tied to daily balanco hidrico | AMBIGUOUS | — |
| [RULE-EVOLUCOES-020](care-pathway/RULE-EVOLUCOES-020-evolucao-drawer-ok-button-gating.md) | Evolução drawer OK-button gating | OK | — |
| [RULE-EVOLUCOES-021](care-pathway/RULE-EVOLUCOES-021-conditional-sub-fields-driven-by-selected-option-conditions.md) | Conditional sub-fields driven by selected option (conditions map) | OK | — |
| [RULE-EVOLUCOES-024](care-pathway/RULE-EVOLUCOES-024-criar-sepse-evolucao-get-ultimos-sinais-vitais-sepsis-note-a.md) | criar_sepse_evolucao / get_ultimos_sinais_vitais — sepsis note auto-linked to most recent vital | OK | — |
| [RULE-EVOLUCOES-025](care-pathway/RULE-EVOLUCOES-025-evolution-signing-workflow-and-signature-date-assignment.md) | Evolution signing workflow and signature-date assignment | DISCREPANCY | — |
| [RULE-EVOLUCOES-026](care-pathway/RULE-EVOLUCOES-026-auto-sign-and-release-on-create-when-status-is-liberado.md) | Auto sign-and-release on create when status is "liberado" | OK | — |
| [RULE-EVOLUCOES-027](care-pathway/RULE-EVOLUCOES-027-auto-sign-and-release-on-update-when-status-is-liberado-gate.md) | Auto sign-and-release on update when status is "liberado", gated by edit-eligibility | OK | — |
| [RULE-EVOLUCOES-028](care-pathway/RULE-EVOLUCOES-028-form-manage-data-required-identifiers-and-content-wrapping.md) | Form manage_data - required identifiers and content wrapping | OK | — |
| [RULE-EVOLUCOES-029](care-pathway/RULE-EVOLUCOES-029-anterior-indicadores-aggregation-previous-form-vitals-24h-in.md) | anterior_indicadores aggregation (previous form/vitals/24h indicators) | DISCREPANCY | — |
| [RULE-EVOLUCOES-030](care-pathway/RULE-EVOLUCOES-030-form-destroy-does-not-call-validar-inativacao-dead-validatio.md) | Form destroy() does not call validar_inativacao (dead validation) | DISCREPANCY | — |
| [RULE-EVOLUCOES-031](care-pathway/RULE-EVOLUCOES-031-medico-form-content-composition.md) | Medico form content composition | OK | — |
| [RULE-EVOLUCOES-032](care-pathway/RULE-EVOLUCOES-032-enfermagem-form-content-composition.md) | Enfermagem form content composition | OK | — |
| [RULE-EVOLUCOES-033](care-pathway/RULE-EVOLUCOES-033-tecnico-de-enfermagem-form-content-composition.md) | Tecnico de enfermagem form content composition | OK | — |
| [RULE-EVOLUCOES-034](care-pathway/RULE-EVOLUCOES-034-fisioterapeuta-form-content-composition.md) | Fisioterapeuta form content composition | OK | — |
| [RULE-EVOLUCOES-035](care-pathway/RULE-EVOLUCOES-035-farmaceutico-clinico-form-content-composition.md) | Farmaceutico clinico form content composition | OK | — |
| [RULE-EVOLUCOES-036](care-pathway/RULE-EVOLUCOES-036-fonoaudiologo-form-content-composition.md) | Fonoaudiologo form content composition | OK | — |
| [RULE-EVOLUCOES-037](care-pathway/RULE-EVOLUCOES-037-musicoterapeuta-form-content-composition.md) | Musicoterapeuta form content composition | OK | — |
| [RULE-EVOLUCOES-038](care-pathway/RULE-EVOLUCOES-038-nutricionista-form-content-composition.md) | Nutricionista form content composition | OK | — |
| [RULE-EVOLUCOES-039](care-pathway/RULE-EVOLUCOES-039-psicologo-form-content-composition.md) | Psicologo form content composition | OK | — |
| [RULE-EVOLUCOES-040](care-pathway/RULE-EVOLUCOES-040-terapeuta-form-content-composition.md) | Terapeuta form content composition | OK | — |
| [RULE-EVOLUCOES-041](care-pathway/RULE-EVOLUCOES-041-intercorrencia-form-content-composition.md) | Intercorrencia form content composition | OK | — |
| [RULE-EVOLUCOES-042](care-pathway/RULE-EVOLUCOES-042-evolution-progress-note-lifecycle-status.md) | Evolution/progress-note lifecycle status | OK | — |
| [RULE-EVOLUCOES-043](care-pathway/RULE-EVOLUCOES-043-evolution-status-state-machine-salvo-liberado-inativo.md) | Evolution status state machine (salvo / liberado / inativo) | OK | — |
| [RULE-EVOLUCOES-044](care-pathway/RULE-EVOLUCOES-044-liberar-assinar-sets-status-liberado-and-assinar-true.md) | Liberar/assinar sets status=liberado and assinar=true | OK | — |
| [RULE-EVOLUCOES-045](care-pathway/RULE-EVOLUCOES-045-evolucao-save-vs-save-and-release-workflow.md) | Evolução save-vs-save-and-release workflow | OK | — |
| [RULE-EVOLUCOES-046](care-pathway/RULE-EVOLUCOES-046-new-evolution-prefilled-from-last-form-dt-registro-defaults.md) | New evolution prefilled from last form; dt_registro defaults to now | OK | — |
| [RULE-EVOLUCOES-047](care-pathway/RULE-EVOLUCOES-047-previous-form-indicators-carry-forward-endpoint.md) | Previous-form-indicators carry-forward endpoint | OK | — |
| [RULE-EVOLUCOES-055](care-pathway/RULE-EVOLUCOES-055-cannot-inactivate-a-released-liberado-form-validation-rule-d.md) | Cannot inactivate a released (liberado) form - validation rule defined | OK | — |
| [RULE-FORMULARIOS-CLINICOS-009](care-pathway/RULE-FORMULARIOS-CLINICOS-009-home-care-incident-intervention-conduct-with-conditional-spe.md) | Home-care incident intervention/conduct with conditional specific-intervention | OK | — |
| [RULE-FORMULARIOS-CLINICOS-015](care-pathway/RULE-FORMULARIOS-CLINICOS-015-home-care-incident-disposition-outcome-enum.md) | Home-care incident disposition/outcome enum | OK | — |
| [RULE-FORMULARIOS-CLINICOS-016](care-pathway/RULE-FORMULARIOS-CLINICOS-016-physiotherapy-conduct-enums-respiratory-motor-techniques.md) | Physiotherapy conduct enums (respiratory & motor techniques) | OK | — |
| [RULE-FORMULARIOS-CLINICOS-017](care-pathway/RULE-FORMULARIOS-CLINICOS-017-intercorrencia-clinical-incident-complication-domain-concept.md) | Intercorrencia (clinical incident/complication) domain-concept icon | AMBIGUOUS | — |
| [RULE-FORMULARIOS-CLINICOS-037](care-pathway/RULE-FORMULARIOS-CLINICOS-037-multidisciplinary-care-team-discipline-icon-taxonomy.md) | Multidisciplinary care-team discipline icon taxonomy | AMBIGUOUS | — |
| [RULE-FORMULARIOS-CLINICOS-038](care-pathway/RULE-FORMULARIOS-CLINICOS-038-terapeuta-icon-is-a-byte-identical-duplicate-of-psicologo-ic.md) | Terapeuta icon is a byte-identical duplicate of Psicologo icon | DISCREPANCY | — |
| [RULE-INDICADORES-ETL-011](care-pathway/RULE-INDICADORES-ETL-011-get-procedimentos-invasivos-invasive-procedure-code-lookup.md) | get_procedimentos_invasivos — invasive-procedure code lookup | OK | — |
| [RULE-INDICADORES-ETL-015](care-pathway/RULE-INDICADORES-ETL-015-etl-schema-v1-tasy-to-trilha-sync-with-assistido-reset.md) | etl_schema (v1) — Tasy-to-Trilha sync with assistido reset | OK | — |
| [RULE-INDICADORES-ETL-016](care-pathway/RULE-INDICADORES-ETL-016-novo-etl-schema-v2-tasy-to-trilha-sync-criterio-modified-fla.md) | novo_etl_schema (v2) — Tasy-to-Trilha sync, criterio-modified flag overwritten instead of OR-ac | DISCREPANCY | — |
| [RULE-MOVIMENTACAO-ADT-011](care-pathway/RULE-MOVIMENTACAO-ADT-011-bed-assistido-flag-delegated-to-a-model-property-leito-seria.md) | Bed 'assistido' flag delegated to a model property (leito serializer) | AMBIGUOUS | UNVERIFIABLE |
| [RULE-MOVIMENTACAO-ADT-017](care-pathway/RULE-MOVIMENTACAO-ADT-017-trilha-care-pathway-click-routing.md) | Trilha (care-pathway) click routing | OK | — |
| [RULE-MOVIMENTACAO-ADT-018](care-pathway/RULE-MOVIMENTACAO-ADT-018-bed-trilhas-selection-branches-by-tipo-automatica-homecare-o.md) | Bed trilhas selection branches by tipo (automatica/homecare only) | OK | — |
| [RULE-MOVIMENTACAO-ADT-022](care-pathway/RULE-MOVIMENTACAO-ADT-022-bed-destroy-blocked-while-it-has-an-active-occupation.md) | Bed destroy() blocked while it has an active occupation | OK | — |
| [RULE-MOVIMENTACAO-ADT-023](care-pathway/RULE-MOVIMENTACAO-ADT-023-bed-action-button-eligibility-by-bed-type-and-permission.md) | Bed action-button eligibility by bed type and permission | OK | — |
| [RULE-MOVIMENTACAO-ADT-031](care-pathway/RULE-MOVIMENTACAO-ADT-031-discharge-baixa-only-the-current-movimentacao-can-be-closed.md) | Discharge (baixa) - only the current movimentacao can be closed; frees the bed | OK | — |
| [RULE-MOVIMENTACAO-ADT-032](care-pathway/RULE-MOVIMENTACAO-ADT-032-first-movimentacao-admission-occupies-the-bed.md) | First movimentacao - admission occupies the bed | OK | — |
| [RULE-MOVIMENTACAO-ADT-033](care-pathway/RULE-MOVIMENTACAO-ADT-033-first-admission-primeira-movimentacao-viewset-forced-fields.md) | First admission (Primeira Movimentacao) viewset - forced fields and downstream workflow | OK | — |
| [RULE-MOVIMENTACAO-ADT-034](care-pathway/RULE-MOVIMENTACAO-ADT-034-new-movimentacao-carry-forward-of-clinical-data-from-previou.md) | New movimentacao - carry-forward of clinical data from previous | OK | — |
| [RULE-MOVIMENTACAO-ADT-035](care-pathway/RULE-MOVIMENTACAO-ADT-035-new-movimentacao-viewset-carries-forward-patient-and-bed-fro.md) | New movimentacao viewset carries forward patient and bed from the previous record | OK | — |
| [RULE-MOVIMENTACAO-ADT-036](care-pathway/RULE-MOVIMENTACAO-ADT-036-homecare-bed-trilhas-list-is-a-static-fixed-template-not-per.md) | Homecare bed 'trilhas' list is a static fixed template, not per-patient data | DISCREPANCY | — |
| [RULE-MOVIMENTACAO-ADT-037](care-pathway/RULE-MOVIMENTACAO-ADT-037-automatic-pathway-bed-trilhas-only-populate-when-the-bed-is.md) | Automatic-pathway bed trilhas only populate when the bed is occupied | OK | — |
| [RULE-MOVIMENTACAO-ADT-038](care-pathway/RULE-MOVIMENTACAO-ADT-038-trilha-recompute-orchestration-on-prontuario-data-update.md) | Trilha recompute orchestration on prontuario data update | OK | — |
| [RULE-MOVIMENTACAO-ADT-042](care-pathway/RULE-MOVIMENTACAO-ADT-042-patient-user-sector-link-diff-sync-vinculo-bulk-action.md) | Patient-user-sector link diff-sync (vinculo bulk action) | OK | — |
| [RULE-MOVIMENTACAO-ADT-044](care-pathway/RULE-MOVIMENTACAO-ADT-044-default-active-sector-selection-for-patient-management.md) | Default active sector selection for patient management | OK | — |
| [RULE-MOVIMENTACAO-ADT-045](care-pathway/RULE-MOVIMENTACAO-ADT-045-pre-selection-of-already-linked-patients.md) | Pre-selection of already-linked patients | OK | — |
| [RULE-MOVIMENTACAO-ADT-046](care-pathway/RULE-MOVIMENTACAO-ADT-046-assistido-attend-to-action-on-a-bed-s-care-pathway-frontend.md) | Assistido (attend-to) action on a bed's care pathway (frontend endpoint) | OK | — |
| [RULE-MOVIMENTACAO-ADT-047](care-pathway/RULE-MOVIMENTACAO-ADT-047-cardiorespiratory-arrest-capture-nullable-group.md) | Cardiorespiratory arrest capture (nullable group) | OK | — |
| [RULE-MOVIMENTACAO-ADT-052](care-pathway/RULE-MOVIMENTACAO-ADT-052-bed-company-monitoring-modality-enumeration-manual-automatic.md) | Bed/company monitoring-modality enumeration (manual\|automatica\|homecare) | OK | — |
| [RULE-MOVIMENTACAO-ADT-063](care-pathway/RULE-MOVIMENTACAO-ADT-063-movimentacao-chronic-condition-pathway-flags.md) | Movimentacao chronic-condition / pathway flags | OK | — |
| [RULE-NUTRICAO-003](care-pathway/RULE-NUTRICAO-003-nutrition-therapy-pathway-payload-trilha-nutricao-tolerance.md) | Nutrition-therapy pathway (payload_trilha_nutricao) - tolerance, gastric-residual and contraind | OK | DISCREPANCY (moderate) |
| [RULE-NUTRICAO-007](care-pathway/RULE-NUTRICAO-007-dietitian-daily-objectives-conditional-prescribed-volumes.md) | Dietitian daily-objectives conditional prescribed volumes | OK | — |
| [RULE-OPERACIONAL-INFRA-003](care-pathway/RULE-OPERACIONAL-INFRA-003-offline-prescriptions-grouped-by-day-keyed-by-patient-atendi.md) | Offline prescriptions grouped by day, keyed by patient atendimento number | OK | UNVERIFIABLE |
| [RULE-OPERACIONAL-INFRA-019](care-pathway/RULE-OPERACIONAL-INFRA-019-offline-water-balance-shows-the-last-2-records-for-an-occupi.md) | Offline water balance shows the last 2 records for an occupied bed; a QTD attribute is defined  | DISCREPANCY | — |
| [RULE-PIORA-CLINICA-012](care-pathway/RULE-PIORA-CLINICA-012-vital-signs-entry-auto-creates-clinical-worsening-pioraclini.md) | Vital signs entry auto-creates clinical-worsening (PioraClinica) record | OK | — |
| [RULE-PRESCRICAO-008](care-pathway/RULE-PRESCRICAO-008-prescription-horario-administration-cancellation-reschedule.md) | Prescription horario administration/cancellation/reschedule state machine | OK | — |
| [RULE-PRESCRICAO-009](care-pathway/RULE-PRESCRICAO-009-medication-administration-status-checkbox-icon-and-actor-lab.md) | Medication administration status -> checkbox icon and actor label (decision tree) | OK | — |
| [RULE-PRESCRICAO-010](care-pathway/RULE-PRESCRICAO-010-continuous-prescription-prescricaocontinua-daily-generation.md) | Continuous-prescription (PrescricaoContinua) daily generation eligibility | OK | — |
| [RULE-PRESCRICAO-011](care-pathway/RULE-PRESCRICAO-011-prescription-time-slot-horario-visual-status-priority.md) | Prescription time-slot (horario) visual status priority | OK | — |
| [RULE-PRESCRICAO-012](care-pathway/RULE-PRESCRICAO-012-horario-persistence-routing-post-patch-delete.md) | Horario persistence routing (POST / PATCH / DELETE) | OK | — |
| [RULE-PRESCRICAO-013](care-pathway/RULE-PRESCRICAO-013-save-vs-save-and-check-vs-update-time-decision-when-hour-edi.md) | Save vs Save-and-check vs Update-time decision when hour edited | OK | — |
| [RULE-PRESCRICAO-014](care-pathway/RULE-PRESCRICAO-014-delete-authorization-for-a-scheduled-dose-get-can-delete.md) | Delete authorization for a scheduled dose (get_can_delete) | DISCREPANCY | — |
| [RULE-PRESCRICAO-015](care-pathway/RULE-PRESCRICAO-015-delete-horario-only-when-can-delete.md) | Delete horario only when can_delete | OK | — |
| [RULE-PRESCRICAO-019](care-pathway/RULE-PRESCRICAO-019-medication-reconciliation-logic.md) | Medication reconciliation logic | OK | — |
| [RULE-PRESCRICAO-023](care-pathway/RULE-PRESCRICAO-023-suspended-horario-blocks-all-administration-actions.md) | Suspended horario blocks all administration actions | OK | — |
| [RULE-PRESCRICAO-024](care-pathway/RULE-PRESCRICAO-024-quick-administered-check-without-reason.md) | Quick "administered" check without reason | OK | — |
| [RULE-PRESCRICAO-025](care-pathway/RULE-PRESCRICAO-025-administration-check-form-value-construction.md) | Administration-check form value construction | OK | — |
| [RULE-PRESCRICAO-026](care-pathway/RULE-PRESCRICAO-026-revert-administration-check-requires-justification.md) | Revert administration check requires justification | OK | — |
| [RULE-PRESCRICAO-028](care-pathway/RULE-PRESCRICAO-028-prescription-dose-administration-cancellation-lifecycle.md) | Prescription-dose administration/cancellation lifecycle | AMBIGUOUS | — |
| [RULE-PRESCRICAO-030](care-pathway/RULE-PRESCRICAO-030-not-administered-reason-enum-with-outros-free-text-requireme.md) | Not-administered reason enum with "outros" free-text requirement | OK | — |
| [RULE-PRESCRICAO-031](care-pathway/RULE-PRESCRICAO-031-add-new-horario-requires-a-time-hh-mm.md) | Add-new-horario requires a time (HH:mm) | OK | — |
| [RULE-PRESCRICAO-038](care-pathway/RULE-PRESCRICAO-038-pharmacist-prophylaxis-checklist.md) | Pharmacist prophylaxis checklist | OK | — |
| [RULE-PROFILAXIA-005](care-pathway/RULE-PROFILAXIA-005-prophylaxis-v3-criterio-1-gi-stress-ulcer-lamgd-prophylaxis.md) | Prophylaxis v3 criterio_1 - GI stress-ulcer (LAMGD) prophylaxis indicated but absent (AMARELO) | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-PROFILAXIA-006](care-pathway/RULE-PROFILAXIA-006-prophylaxis-v3-criterio-9-invasive-device-prescribed-vermelh.md) | Prophylaxis v3 criterio_9 - invasive device prescribed (VERMELHO) | OK | — |
| [RULE-PROFILAXIA-007](care-pathway/RULE-PROFILAXIA-007-prophylaxis-v1-lamgd-stress-ulcer-prophylaxis-mobilization-i.md) | Prophylaxis v1 - LAMGD (stress-ulcer) prophylaxis, mobilization & invasive-device catalog | OK | — |
| [RULE-PROFILAXIA-008](care-pathway/RULE-PROFILAXIA-008-prophylaxis-v3-reduced-active-criteria-set-facade-lamgd-inse.md) | Prophylaxis v3 - reduced active criteria set facade (LAMGD + insertion bundle only) | AMBIGUOUS | — |
| [RULE-SEDACAO-015](care-pathway/RULE-SEDACAO-015-sedation-manual-c1-sedoanalgesia-overdose-any-sedative-15-ml.md) | Sedation manual C1 - sedoanalgesia overdose (any sedative >15 ml) | OK | — |
| [RULE-SEDACAO-016](care-pathway/RULE-SEDACAO-016-sedation-manual-c2-deep-rass-with-low-fio2-peep.md) | Sedation manual C2 - deep RASS with low FiO2/PEEP | DISCREPANCY | DISCREPANCY |
| [RULE-SEDACAO-017](care-pathway/RULE-SEDACAO-017-sedation-manual-c3-good-oxygenation-on-sedation.md) | Sedation manual C3 - good oxygenation on sedation | OK | VERIFIED |
| [RULE-SEDACAO-018](care-pathway/RULE-SEDACAO-018-sedation-manual-c4-sedation-justified-by-severity.md) | Sedation manual C4 - sedation justified by severity | AMBIGUOUS | UNVERIFIABLE |
| [RULE-SEDACAO-019](care-pathway/RULE-SEDACAO-019-sedation-manual-c5-poor-oxygenation-with-light-absent-sedati.md) | Sedation manual C5 - poor oxygenation with light/absent sedation | OK | UNVERIFIABLE |
| [RULE-SEDACAO-020](care-pathway/RULE-SEDACAO-020-sedation-manual-c6-severity-without-sedation.md) | Sedation manual C6 - severity without sedation | OK | UNVERIFIABLE |
| [RULE-SEDACAO-022](care-pathway/RULE-SEDACAO-022-cardiac-arrest-within-last-24h-pcr-24h-helper-manual-model.md) | Cardiac arrest within last 24h (PCR-24h helper, manual model) | AMBIGUOUS | — |
| [RULE-SEPSE-059](care-pathway/RULE-SEPSE-059-sepse-automatica-variant-b-27-criterion-alert-catalog-global.md) | Sepse automatica variant B - 27-criterion alert catalog + global recommendation | OK | DISCREPANCY (low) |
| [RULE-SEPSE-060](care-pathway/RULE-SEPSE-060-sepse-pathway-variant-a-11-criterion-catalog-meropenem-1500m.md) | Sepse pathway variant A - 11-criterion catalog + Meropenem/1500ml recommendation | AMBIGUOUS | DISCREPANCY (moderate) |
| [RULE-SEPSE-063](care-pathway/RULE-SEPSE-063-sepse-hemodynamic-status-decision-intubation-rass-2-fluid-ch.md) | SEPSE hemodynamic-status decision (intubation RASS-2, fluid challenge) | OK | VERIFIED |
| [RULE-SEPSE-064](care-pathway/RULE-SEPSE-064-sepse-invasive-devices-decision-early-ne-central-access-cvc.md) | SEPSE invasive-devices decision (early NE, central access, CVC replacement) | OK | — |
| [RULE-SEPSE-071](care-pathway/RULE-SEPSE-071-sepse-v3-interactive-protocol-creation-gate-can-criar-novo-p.md) | SEPSE v3 interactive-protocol creation gate (can_criar_novo_protocolo) | OK | — |
| [RULE-SEPSE-072](care-pathway/RULE-SEPSE-072-sepse-protocol-acceptance-workflow-and-orange-alert.md) | SEPSE protocol acceptance workflow and orange alert | OK | — |
| [RULE-SEPSE-073](care-pathway/RULE-SEPSE-073-sepse-protocol-rejection-workflow-and-neutral-alert.md) | SEPSE protocol rejection workflow and neutral alert | DISCREPANCY | — |
| [RULE-SEPSE-074](care-pathway/RULE-SEPSE-074-sepse-protocol-closure-accepted-encerrado-workflow.md) | SEPSE protocol closure (accepted -> encerrado) workflow | OK | — |
| [RULE-SEPSE-075](care-pathway/RULE-SEPSE-075-sepse-item-check-uncheck-and-protocol-completion-state-machi.md) | SEPSE item check / uncheck and protocol completion state machine | OK | — |
| [RULE-SEPSE-076](care-pathway/RULE-SEPSE-076-sepse-interactive-protocol-bundle-hour-1-vs-reassessment-ite.md) | SEPSE interactive protocol bundle (hour-1 vs reassessment items) | OK | — |
| [RULE-SEPSE-077](care-pathway/RULE-SEPSE-077-sepse-item-checker-auto-attribution.md) | SEPSE item checker auto-attribution | OK | — |
| [RULE-SEPSE-078](care-pathway/RULE-SEPSE-078-sepsis-first-hour-auto-check-guard.md) | Sepsis first-hour auto-check guard | OK | — |
| [RULE-SEPSE-079](care-pathway/RULE-SEPSE-079-sepsis-1h-bundle-exam-solicitation-auto-check.md) | Sepsis 1h bundle - exam solicitation auto-check | DISCREPANCY | — |
| [RULE-SEPSE-080](care-pathway/RULE-SEPSE-080-sepsis-1h-bundle-antimicrobial-escalation-auto-check-24h-win.md) | Sepsis 1h bundle - antimicrobial escalation auto-check (24h window) | OK | — |
| [RULE-SEPSE-081](care-pathway/RULE-SEPSE-081-sepsis-1h-bundle-volume-expansion-auto-check-4h-window.md) | Sepsis 1h bundle - volume expansion auto-check (4h window) | OK | — |
| [RULE-SEPSE-082](care-pathway/RULE-SEPSE-082-vital-signs-entry-auto-creates-sepsis-screening-sepse-record.md) | Vital signs entry auto-creates sepsis-screening (Sepse) record linked to latest evolution | OK | — |
| [RULE-SEPSE-083](care-pathway/RULE-SEPSE-083-interactive-sepsis-trail-filtered-by-bed.md) | Interactive sepsis trail filtered by bed | OK | — |
| [RULE-SEPSE-084](care-pathway/RULE-SEPSE-084-active-sepsis-care-pathway-selection.md) | Active sepsis care-pathway selection | OK | — |
| [RULE-SEPSE-085](care-pathway/RULE-SEPSE-085-interactive-sepsis-pathway-completion-transition.md) | Interactive sepsis pathway completion transition | OK | — |
| [RULE-SEPSE-086](care-pathway/RULE-SEPSE-086-historical-sepsis-pathway-instances-filtered-by-aceito-false.md) | Historical sepsis pathway instances filtered by aceito=false | AMBIGUOUS | — |
| [RULE-SEPSE-087](care-pathway/RULE-SEPSE-087-sepsis-page-back-navigation-preserves-drawer-context.md) | Sepsis page "back" navigation preserves drawer context | OK | — |
| [RULE-SEPSE-089](care-pathway/RULE-SEPSE-089-current-protocol-tab-requires-non-empty-checklist-items.md) | Current protocol tab requires non-empty checklist items | OK | — |
| [RULE-SEPSE-090](care-pathway/RULE-SEPSE-090-sepsis-protocol-lifecycle-state-display.md) | Sepsis protocol lifecycle state display | OK | — |
| [RULE-SEPSE-091](care-pathway/RULE-SEPSE-091-sepsis-protocol-item-conditional-visibility-and-expandabilit.md) | Sepsis protocol item conditional visibility and expandability | OK | — |
| [RULE-SEPSE-092](care-pathway/RULE-SEPSE-092-sepsis-protocol-item-check-off-workflow.md) | Sepsis protocol item check-off workflow | OK | — |
| [RULE-SEPSE-093](care-pathway/RULE-SEPSE-093-sepsis-pathway-dual-completion-flags.md) | Sepsis-pathway dual completion flags | AMBIGUOUS | — |
| [RULE-SEPSE-094](care-pathway/RULE-SEPSE-094-sepsis-pathway-accept-discard-workflow.md) | Sepsis-pathway accept/discard workflow | OK | — |
| [RULE-SEPSE-096](care-pathway/RULE-SEPSE-096-sepsis-interactive-bundle-step-and-package-enums.md) | Sepsis interactive bundle step and package enums | OK | — |
| [RULE-SEPSE-097](care-pathway/RULE-SEPSE-097-sepsis-protocol-refusal-permission.md) | Sepsis protocol refusal permission | OK | — |
| [RULE-SINAIS-VITAIS-007](care-pathway/RULE-SINAIS-VITAIS-007-sinaisvitais-soft-delete-logs-audit-action-no-balance-adjust.md) | SinaisVitais soft-delete logs audit action (no balance adjustment) | OK | — |
| [RULE-TENANCY-ORGANIZACAO-016](care-pathway/RULE-TENANCY-ORGANIZACAO-016-processing-mode-tipo-enumeration-for-company-bed-sector-esta.md) | Processing-mode (tipo) enumeration for company/bed/sector/establishment | OK | — |
| [RULE-TENANCY-ORGANIZACAO-030](care-pathway/RULE-TENANCY-ORGANIZACAO-030-establishment-total-assisted-patients-branches-by-tipo.md) | Establishment total assisted patients branches by tipo | OK | — |
| [RULE-TENANCY-ORGANIZACAO-032](care-pathway/RULE-TENANCY-ORGANIZACAO-032-establishment-destroy-blocked-while-any-bed-has-an-active-oc.md) | Establishment destroy() blocked while any bed has an active occupation | OK | — |
| [RULE-TENANCY-ORGANIZACAO-036](care-pathway/RULE-TENANCY-ORGANIZACAO-036-sector-total-assisted-patient-count-branches-by-tipo-manual.md) | Sector total assisted-patient count branches by tipo (manual/automatica/homecare) | OK | — |
| [RULE-TENANCY-ORGANIZACAO-037](care-pathway/RULE-TENANCY-ORGANIZACAO-037-sector-destroy-blocked-while-any-bed-has-an-active-occupatio.md) | Sector destroy() blocked while any bed has an active occupation | DISCREPANCY | — |
| [RULE-TRILHAS-ENGINE-001](care-pathway/RULE-TRILHAS-ENGINE-001-automatic-bed-pathway-composition-v3-v2-model-sets.md) | Automatic-bed pathway composition (v3 + v2 model sets) | DISCREPANCY | — |
| [RULE-TRILHAS-ENGINE-002](care-pathway/RULE-TRILHAS-ENGINE-002-homecare-bed-pathway-composition.md) | Homecare-bed pathway composition | OK | — |
| [RULE-TRILHAS-ENGINE-003](care-pathway/RULE-TRILHAS-ENGINE-003-get-trilha-leito-type-dispatch.md) | get_trilha leito-type dispatch | AMBIGUOUS | — |
| [RULE-TRILHAS-ENGINE-009](care-pathway/RULE-TRILHAS-ENGINE-009-care-pathway-catalog-and-criteria-counts.md) | Care-pathway catalog and criteria counts | OK | — |
| [RULE-TRILHAS-ENGINE-011](care-pathway/RULE-TRILHAS-ENGINE-011-manual-pathway-set-created-per-movimentacao-estabilidade-sed.md) | Manual pathway set created per movimentacao (Estabilidade/Sedacao/Sepse/Ventilacao) | OK | — |
| [RULE-TRILHAS-ENGINE-012](care-pathway/RULE-TRILHAS-ENGINE-012-atualizartrilhasv3-v3-care-pathway-bootstrap-and-bed-re-link.md) | AtualizarTrilhasV3 — v3 care-pathway bootstrap and bed re-linking | AMBIGUOUS | — |
| [RULE-TRILHAS-ENGINE-013](care-pathway/RULE-TRILHAS-ENGINE-013-trilha-name-humanization-6-char-prefix-split.md) | Trilha name humanization (6-char prefix split) | AMBIGUOUS | — |
| [RULE-TRILHAS-ENGINE-014](care-pathway/RULE-TRILHAS-ENGINE-014-accept-interactive-protocol-workflow.md) | Accept interactive protocol workflow | OK | — |
| [RULE-TRILHAS-ENGINE-015](care-pathway/RULE-TRILHAS-ENGINE-015-refuse-interactive-protocol-workflow-justification-required.md) | Refuse interactive protocol workflow (justification required) | AMBIGUOUS | — |
| [RULE-TRILHAS-ENGINE-016](care-pathway/RULE-TRILHAS-ENGINE-016-criterion-recommendations-and-interventions-rendering.md) | Criterion recommendations and interventions rendering | OK | — |
| [RULE-TRILHAS-ENGINE-018](care-pathway/RULE-TRILHAS-ENGINE-018-care-pathway-type-enumeration-assistidochoices-vs-observacao.md) | Care-pathway type enumeration (AssistidoChoices vs ObservacaoChoices — label drift) | DISCREPANCY | — |
| [RULE-VENTILACAO-003](care-pathway/RULE-VENTILACAO-003-ventilation-c1-high-inspiratory-pressure-or-tidal-volume.md) | Ventilation C1 - high inspiratory pressure or tidal volume | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-VENTILACAO-004](care-pathway/RULE-VENTILACAO-004-ventilation-c2-fio2xpeep-mismatch-with-moderate-hypoxemia.md) | Ventilation C2 - FiO2xPEEP mismatch with moderate hypoxemia | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-VENTILACAO-005](care-pathway/RULE-VENTILACAO-005-ventilation-c3-fio2xpeep-mismatch-with-severe-hypoxemia.md) | Ventilation C3 - FiO2xPEEP mismatch with severe hypoxemia | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-VENTILACAO-006](care-pathway/RULE-VENTILACAO-006-ventilation-c2-c3-previous-version-fio2-peep-table-peep-old.md) | Ventilation C2/C3 previous-version FiO2->PEEP table (peep_old_table) | AMBIGUOUS | DISCREPANCY |
| [RULE-VENTILACAO-007](care-pathway/RULE-VENTILACAO-007-ventilation-c4-weaning-readiness-consciousness.md) | Ventilation C4 - weaning readiness / consciousness | DISCREPANCY | DISCREPANCY (low) |
| [RULE-VENTILACAO-008](care-pathway/RULE-VENTILACAO-008-ventilation-c5-prolonged-intubation-10-days-tot.md) | Ventilation C5 - prolonged intubation (>10 days TOT) | OK | VERIFIED |
| [RULE-VENTILACAO-009](care-pathway/RULE-VENTILACAO-009-ventilation-c6-prolonged-intubation-with-covid-19.md) | Ventilation C6 - prolonged intubation with COVID-19 | DISCREPANCY | DISCREPANCY (moderate) |
| [RULE-VENTILACAO-010](care-pathway/RULE-VENTILACAO-010-ventilation-c7-severe-hypoxemia-early-in-admission.md) | Ventilation C7 - severe hypoxemia early in admission | OK | VERIFIED |
| [RULE-VENTILACAO-011](care-pathway/RULE-VENTILACAO-011-ventilation-c8-extubation-readiness-bundle.md) | Ventilation C8 - extubation-readiness bundle | DISCREPANCY | DISCREPANCY (high) |
| [RULE-VENTILACAO-012](care-pathway/RULE-VENTILACAO-012-ventilation-c9-shock-without-ventilation.md) | Ventilation C9 - shock without ventilation | OK | DISCREPANCY (low) |
| [RULE-VENTILACAO-013](care-pathway/RULE-VENTILACAO-013-ventilation-c10-adequate-oxygenation-incl-copd-target.md) | Ventilation C10 - adequate oxygenation (incl. COPD target) | OK | VERIFIED |
| [RULE-VENTILACAO-017](care-pathway/RULE-VENTILACAO-017-ventilation-weaning-facade-protocol-ventilacao-automatica-pr.md) | Ventilation/weaning facade protocol (ventilacao_automatica) - protective settings, PEEP/FiO2, t | OK | VERIFIED |
| [RULE-VENTILACAO-019](care-pathway/RULE-VENTILACAO-019-physician-respiratory-assessment-ventilation-decision-tree-f.md) | Physician respiratory-assessment ventilation decision tree (FormularioMedico) | OK | — |
| [RULE-VENTILACAO-020](care-pathway/RULE-VENTILACAO-020-physiotherapy-ventilation-decision-tree-with-divergent-press.md) | Physiotherapy ventilation decision tree with divergent pressure ranges | DISCREPANCY | — |
| [RULE-VENTILACAO-024](care-pathway/RULE-VENTILACAO-024-ventilation-mode-string-classification-lists-get-ventilacao.md) | Ventilation-mode string classification lists (get_ventilacao) | DISCREPANCY | — |

### billing-administrative (38 rules)

Billing, audit ("glosa zero"), documentation-compliance and reporting rules

| Rule | Name | Status | Verdict |
|---|---|---|---|
| [RULE-AUDITORIA-LOGS-005](billing-administrative/RULE-AUDITORIA-LOGS-005-log-retention-purge-threshold-2-weeks-hard-delete.md) | Log retention / purge threshold (2 weeks, hard delete) | OK | — |
| [RULE-AUDITORIA-LOGS-006](billing-administrative/RULE-AUDITORIA-LOGS-006-default-and-selectable-page-size-for-log-list.md) | Default and selectable page size for log list | OK | — |
| [RULE-AUDITORIA-LOGS-007](billing-administrative/RULE-AUDITORIA-LOGS-007-top-4-most-accessed-routes-limit.md) | Top-4 most-accessed-routes limit | OK | — |
| [RULE-AUDITORIA-LOGS-008](billing-administrative/RULE-AUDITORIA-LOGS-008-problematic-routes-selection-one-path-per-status-code-top-4.md) | 'Problematic routes' selection: one path per status code, top 4 | OK | — |
| [RULE-AUDITORIA-LOGS-016](billing-administrative/RULE-AUDITORIA-LOGS-016-request-response-log-capture-payload.md) | Request/response log-capture payload | OK | — |
| [RULE-AUDITORIA-LOGS-017](billing-administrative/RULE-AUDITORIA-LOGS-017-asynchronous-log-persistence-dispatch.md) | Asynchronous log persistence dispatch | OK | — |
| [RULE-AUDITORIA-LOGS-018](billing-administrative/RULE-AUDITORIA-LOGS-018-unconditional-what-gets-logged-predicate-every-response.md) | Unconditional what-gets-logged predicate (every response) | OK | — |
| [RULE-AUDITORIA-LOGS-019](billing-administrative/RULE-AUDITORIA-LOGS-019-client-ip-and-public-private-classification.md) | Client IP and public/private classification | OK | — |
| [RULE-AUDITORIA-LOGS-020](billing-administrative/RULE-AUDITORIA-LOGS-020-geolocation-enrichment-via-geoip2-async-stage.md) | Geolocation enrichment via GeoIP2 (async stage) | OK | — |
| [RULE-AUDITORIA-LOGS-021](billing-administrative/RULE-AUDITORIA-LOGS-021-soft-delete-mixin-present-but-not-exercised-for-logs.md) | Soft-delete mixin present but not exercised for logs | AMBIGUOUS | — |
| [RULE-AUDITORIA-LOGS-022](billing-administrative/RULE-AUDITORIA-LOGS-022-log-dashboard-access-control-authenticated-only-no-staff-own.md) | Log dashboard access control (authenticated-only, no staff/ownership check) | AMBIGUOUS | — |
| [RULE-AUDITORIA-LOGS-023](billing-administrative/RULE-AUDITORIA-LOGS-023-default-log-list-ordering-most-recent-first.md) | Default log list ordering (most recent first) | OK | — |
| [RULE-AUDITORIA-LOGS-033](billing-administrative/RULE-AUDITORIA-LOGS-033-log-field-exposure-scoping-logsimpleserializer-vs-logseriali.md) | Log field-exposure scoping (LogSimpleSerializer vs LogSerializer) | OK | — |
| [RULE-AUDITORIA-LOGS-036](billing-administrative/RULE-AUDITORIA-LOGS-036-history-skip-on-non-substantive-field-changes.md) | History-skip on non-substantive field changes | OK | — |
| [RULE-AUTH-USUARIOS-009](billing-administrative/RULE-AUTH-USUARIOS-009-scope-based-rbac-permission-dispatch.md) | Scope-based RBAC permission dispatch | OK | — |
| [RULE-AUTH-USUARIOS-032](billing-administrative/RULE-AUTH-USUARIOS-032-user-company-membership-grants-u-access-and-cascades-group-c.md) | User-company membership grants 'u' access and cascades group cleanup | OK | — |
| [RULE-AUTH-USUARIOS-033](billing-administrative/RULE-AUTH-USUARIOS-033-establishment-membership-auto-creates-company-membership-del.md) | Establishment membership auto-creates company membership; delete cleans groups | OK | — |
| [RULE-AUTH-USUARIOS-034](billing-administrative/RULE-AUTH-USUARIOS-034-sector-membership-auto-creates-establishment-membership-dele.md) | Sector membership auto-creates establishment membership; delete cleans groups | OK | — |
| [RULE-AUTH-USUARIOS-044](billing-administrative/RULE-AUTH-USUARIOS-044-clinical-administrative-role-cargo-enumeration-backend-model.md) | Clinical/administrative role (cargo) enumeration — backend model vs frontend copy | DISCREPANCY | — |
| [RULE-AUTH-USUARIOS-045](billing-administrative/RULE-AUTH-USUARIOS-045-user-access-role-codes-proprietario-usuario-monitor-backend.md) | User access-role codes (proprietario/usuario/monitor) — backend model vs frontend type | AMBIGUOUS | — |
| [RULE-AUTH-USUARIOS-046](billing-administrative/RULE-AUTH-USUARIOS-046-professional-council-conselho-and-state-of-council-enumerati.md) | Professional council (conselho) and state-of-council enumerations — backend model vs frontend c | OK | — |
| [RULE-AUTH-USUARIOS-047](billing-administrative/RULE-AUTH-USUARIOS-047-access-level-enumeration-read-vs-read-write-dormant.md) | Access-level enumeration (read vs read-write) — dormant | AMBIGUOUS | — |
| [RULE-AUTH-USUARIOS-049](billing-administrative/RULE-AUTH-USUARIOS-049-company-context-required-for-request.md) | Company-context required for request | OK | — |
| [RULE-BALANCO-HIDRICO-046](billing-administrative/RULE-BALANCO-HIDRICO-046-fluid-balance-pdf-export-with-optional-signatures.md) | Fluid-balance PDF export with optional signatures | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-002](billing-administrative/RULE-DOCUMENTACAO-FATURAMENTO-002-glosa-zero-automatic-alert-engine-16-criteria-billing-docume.md) | Glosa-Zero automatic alert engine — 16-criteria billing/documentation-compliance catalog, dual  | DISCREPANCY | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-015](billing-administrative/RULE-DOCUMENTACAO-FATURAMENTO-015-auto-post-released-evolution-to-tasy-lancamento-code-501.md) | Auto-post released evolution to Tasy (lancamento code 501) | AMBIGUOUS | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-019](billing-administrative/RULE-DOCUMENTACAO-FATURAMENTO-019-evolution-note-count-by-type-with-total-row.md) | Evolution-note count-by-type with Total row | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-020](billing-administrative/RULE-DOCUMENTACAO-FATURAMENTO-020-uploaded-medical-record-document-category-code-catalog-three.md) | Uploaded medical-record/document category code catalog — three divergent hand-maintained copies | DISCREPANCY | — |
| [RULE-EVOLUCOES-010](billing-administrative/RULE-EVOLUCOES-010-registered-evolution-types-eligible-for-tasy-release-and-the.md) | Registered evolution types eligible for Tasy release, and their integration codes | OK | — |
| [RULE-EVOLUCOES-012](billing-administrative/RULE-EVOLUCOES-012-amh-docs-category-code-mapping-per-evolution-type.md) | AMH Docs category-code mapping per evolution type | OK | — |
| [RULE-FORMULARIOS-CLINICOS-040](billing-administrative/RULE-FORMULARIOS-CLINICOS-040-duplicate-route-registration-for-enfermagem-form.md) | Duplicate route registration for enfermagem form | AMBIGUOUS | — |
| [RULE-INDICADORES-ETL-018](billing-administrative/RULE-INDICADORES-ETL-018-hierarchical-recursive-kpi-rollup.md) | Hierarchical recursive KPI rollup | OK | — |
| [RULE-INDICADORES-ETL-023](billing-administrative/RULE-INDICADORES-ETL-023-macro-indicator-kpi-shape.md) | Macro-indicator KPI shape | OK | — |
| [RULE-MOVIMENTACAO-ADT-026](billing-administrative/RULE-MOVIMENTACAO-ADT-026-bed-leito-default-type-is-manual.md) | Bed (leito) default type is manual | OK | — |
| [RULE-OPERACIONAL-INFRA-015](billing-administrative/RULE-OPERACIONAL-INFRA-015-exclude-entities-already-in-a-given-access-group.md) | Exclude entities already in a given access group | OK | — |
| [RULE-PRESCRICAO-006](billing-administrative/RULE-PRESCRICAO-006-offline-prescription-validity-days.md) | Offline prescription validity days | OK | — |
| [RULE-TENANCY-ORGANIZACAO-039](billing-administrative/RULE-TENANCY-ORGANIZACAO-039-company-owner-proprietario-access-lifecycle-on-save.md) | Company owner (proprietario) access lifecycle on save | OK | — |
| [RULE-TENANCY-ORGANIZACAO-047](billing-administrative/RULE-TENANCY-ORGANIZACAO-047-whitelabel-brand-enumeration-unique-per-company.md) | Whitelabel brand enumeration (unique per company) | OK | — |

### data-validation (314 rules)

Input validation: ranges, masks, required-if logic, controlled vocabularies, uniqueness

| Rule | Name | Status | Verdict |
|---|---|---|---|
| [RULE-ALERTAS-026](data-validation/RULE-ALERTAS-026-record-lifecycle-status-to-icon-color-mapping-handleiconbyst.md) | Record lifecycle status to icon/color mapping (handleIconByStatus) | OK | — |
| [RULE-AUDITORIA-LOGS-001](data-validation/RULE-AUDITORIA-LOGS-001-date-range-filter-boundary-formula-start-of-day-end-of-day.md) | Date-range filter boundary formula (start-of-day / end-of-day) | OK | UNVERIFIABLE |
| [RULE-AUDITORIA-LOGS-002](data-validation/RULE-AUDITORIA-LOGS-002-request-body-capture-get-vs-write-methods-json-fallback.md) | request_body capture (GET vs write methods, JSON fallback) | OK | — |
| [RULE-AUDITORIA-LOGS-003](data-validation/RULE-AUDITORIA-LOGS-003-response-body-capture-json-then-raw-text-fallback.md) | response_body capture (JSON then raw-text fallback) | OK | — |
| [RULE-AUDITORIA-LOGS-004](data-validation/RULE-AUDITORIA-LOGS-004-device-classification-from-user-agent-dispositivo.md) | Device classification from user agent (dispositivo) | OK | — |
| [RULE-AUDITORIA-LOGS-009](data-validation/RULE-AUDITORIA-LOGS-009-undesirable-status-codes-chart-exclude-is-a-no-op-and-instea.md) | 'Undesirable status codes' chart exclude is a no-op (AND instead of OR) | DISCREPANCY | — |
| [RULE-AUDITORIA-LOGS-010](data-validation/RULE-AUDITORIA-LOGS-010-status-code-badge-color-mapping-get-status-style-399-boundar.md) | Status-code badge color mapping (get_status_style) — 399 boundary bug | DISCREPANCY | — |
| [RULE-AUDITORIA-LOGS-011](data-validation/RULE-AUDITORIA-LOGS-011-http-method-badge-color-mapping-get-method-style.md) | HTTP method badge color mapping (get_method_style) | OK | — |
| [RULE-AUDITORIA-LOGS-012](data-validation/RULE-AUDITORIA-LOGS-012-device-icon-mapping-get-icon-missing-branches-for-tablet-ema.md) | Device icon mapping (get_icon) missing branches for tablet/email/touch_capable | DISCREPANCY | — |
| [RULE-AUDITORIA-LOGS-013](data-validation/RULE-AUDITORIA-LOGS-013-is-status-code-validity-check-599-boundary-unused-dead-code.md) | is_status_code validity check — 599 boundary, unused (dead code) | DISCREPANCY | — |
| [RULE-AUDITORIA-LOGS-014](data-validation/RULE-AUDITORIA-LOGS-014-pretty-json-double-encodes-string-typed-json-values-instead.md) | pretty_json double-encodes string-typed JSON values instead of formatting them | DISCREPANCY | — |
| [RULE-AUDITORIA-LOGS-015](data-validation/RULE-AUDITORIA-LOGS-015-log-detail-field-rendering-rules-skip-falsy-json-html-plain.md) | Log-detail field rendering rules (skip falsy, JSON/HTML/plain branching) | OK | — |
| [RULE-AUDITORIA-LOGS-024](data-validation/RULE-AUDITORIA-LOGS-024-dead-nested-duplicate-of-estadologview.md) | Dead nested duplicate of EstadoLogView | DISCREPANCY | — |
| [RULE-AUDITORIA-LOGS-025](data-validation/RULE-AUDITORIA-LOGS-025-uuid-in-path-anonymization-is-display-only-not-applied-to-ro.md) | UUID-in-path anonymization is display-only, not applied to route aggregation stats | AMBIGUOUS | — |
| [RULE-AUDITORIA-LOGS-026](data-validation/RULE-AUDITORIA-LOGS-026-logmodel-tag-html-table-helper-methods-are-dead-code.md) | LogModel *_tag() HTML-table helper methods are dead code | DISCREPANCY | — |
| [RULE-AUDITORIA-LOGS-027](data-validation/RULE-AUDITORIA-LOGS-027-request-meta-sanitization-for-log-storage.md) | request.META sanitization for log storage | OK | — |
| [RULE-AUDITORIA-LOGS-028](data-validation/RULE-AUDITORIA-LOGS-028-authenticated-user-attribution-on-log-entries.md) | Authenticated-user attribution on log entries | AMBIGUOUS | — |
| [RULE-AUDITORIA-LOGS-029](data-validation/RULE-AUDITORIA-LOGS-029-log-persistence-validation-gate.md) | Log persistence validation gate | OK | — |
| [RULE-AUDITORIA-LOGS-030](data-validation/RULE-AUDITORIA-LOGS-030-allowed-log-list-filter-fields-whitelist.md) | Allowed log-list filter fields whitelist | DISCREPANCY | — |
| [RULE-AUDITORIA-LOGS-031](data-validation/RULE-AUDITORIA-LOGS-031-geo-cascade-endpoints-use-a-narrower-filter-whitelist-than-t.md) | Geo cascade endpoints use a narrower filter whitelist than the main list (missing 'path') | DISCREPANCY | — |
| [RULE-AUDITORIA-LOGS-032](data-validation/RULE-AUDITORIA-LOGS-032-is-html-heuristic-broad-false-positive-risk.md) | is_html heuristic (broad false-positive risk) | AMBIGUOUS | — |
| [RULE-AUDITORIA-LOGS-034](data-validation/RULE-AUDITORIA-LOGS-034-country-region-city-cascading-filter-city-not-re-scoped-by-c.md) | Country -> region -> city cascading filter (city not re-scoped by country) | AMBIGUOUS | — |
| [RULE-AUDITORIA-LOGS-035](data-validation/RULE-AUDITORIA-LOGS-035-geolocalizacao-field-defaults-to-empty-dict-never-null-in-pr.md) | geolocalizacao field defaults to empty dict, never null in practice | OK | — |
| [RULE-AUTH-USUARIOS-001](data-validation/RULE-AUTH-USUARIOS-001-grupoacesso-permission-catalog-payload-computation.md) | GrupoAcesso permission catalog payload computation | OK | UNVERIFIABLE |
| [RULE-AUTH-USUARIOS-002](data-validation/RULE-AUTH-USUARIOS-002-user-cargos-roles-empresa-scoped-lookup.md) | User cargos (roles) empresa-scoped lookup | OK | UNVERIFIABLE |
| [RULE-AUTH-USUARIOS-010](data-validation/RULE-AUTH-USUARIOS-010-grupoacesso-hierarchical-scope-resolution.md) | GrupoAcesso hierarchical scope resolution | OK | — |
| [RULE-AUTH-USUARIOS-011](data-validation/RULE-AUTH-USUARIOS-011-permission-lookup-hierarchical-scope-resolution.md) | Permission lookup hierarchical scope resolution | OK | — |
| [RULE-AUTH-USUARIOS-012](data-validation/RULE-AUTH-USUARIOS-012-grupoacesso-usuarios-field-suppressed-on-list-destroy-action.md) | GrupoAcesso usuarios field suppressed on list/destroy actions | OK | — |
| [RULE-AUTH-USUARIOS-013](data-validation/RULE-AUTH-USUARIOS-013-user-representation-scopes-setores-list-to-current-empresa.md) | User representation scopes setores list to current empresa | OK | — |
| [RULE-AUTH-USUARIOS-014](data-validation/RULE-AUTH-USUARIOS-014-user-queryset-restricted-to-active-users-scoped-to-empresa.md) | User queryset restricted to active users scoped to empresa | OK | — |
| [RULE-AUTH-USUARIOS-015](data-validation/RULE-AUTH-USUARIOS-015-get-and-patch-bypass-can-manage-usuario-permission.md) | GET and PATCH bypass can_manage_usuario permission | OK | — |
| [RULE-AUTH-USUARIOS-017](data-validation/RULE-AUTH-USUARIOS-017-sector-card-click-and-audit-button-permission-gating.md) | Sector-card click and audit-button permission gating | OK | — |
| [RULE-AUTH-USUARIOS-018](data-validation/RULE-AUTH-USUARIOS-018-settings-gear-header-icon-visibility.md) | Settings-gear header icon visibility | OK | — |
| [RULE-AUTH-USUARIOS-019](data-validation/RULE-AUTH-USUARIOS-019-company-switch-dropdown-visibility.md) | Company-switch dropdown visibility | OK | — |
| [RULE-AUTH-USUARIOS-029](data-validation/RULE-AUTH-USUARIOS-029-login-cascade-local-auth-first-incl-http-202-status.md) | Login cascade - local auth first (incl. HTTP 202 status) | OK | — |
| [RULE-AUTH-USUARIOS-031](data-validation/RULE-AUTH-USUARIOS-031-auto-hash-plaintext-password-on-user-save.md) | Auto-hash plaintext password on user save | OK | — |
| [RULE-AUTH-USUARIOS-035](data-validation/RULE-AUTH-USUARIOS-035-grupoacesso-update-replaces-entire-permission-set.md) | GrupoAcesso update() replaces entire permission set | OK | — |
| [RULE-AUTH-USUARIOS-036](data-validation/RULE-AUTH-USUARIOS-036-grupoacesso-update-replaces-entire-usuarios-membership.md) | GrupoAcesso update() replaces entire usuarios membership | OK | — |
| [RULE-AUTH-USUARIOS-037](data-validation/RULE-AUTH-USUARIOS-037-full-permission-catalog-exposure.md) | Full permission catalog exposure | OK | — |
| [RULE-AUTH-USUARIOS-043](data-validation/RULE-AUTH-USUARIOS-043-api-key-name-uniqueness.md) | API key name uniqueness | OK | — |
| [RULE-AUTH-USUARIOS-048](data-validation/RULE-AUTH-USUARIOS-048-access-group-must-belong-to-exactly-one-scope-empresa-xor-es.md) | Access group must belong to exactly one scope (empresa XOR estabelecimento XOR setor) | OK | — |
| [RULE-AUTH-USUARIOS-050](data-validation/RULE-AUTH-USUARIOS-050-grupoacesso-incoming-permissoes-payload-rewrite.md) | GrupoAcesso incoming permissoes payload rewrite | OK | — |
| [RULE-AUTH-USUARIOS-051](data-validation/RULE-AUTH-USUARIOS-051-user-must-belong-to-a-group-s-scope-before-joining-that-acce.md) | User must belong to a group's scope before joining that access group | DISCREPANCY | — |
| [RULE-AUTH-USUARIOS-052](data-validation/RULE-AUTH-USUARIOS-052-loginserializer-required-field-validation-never-enforced.md) | LoginSerializer required-field validation never enforced | DISCREPANCY | — |
| [RULE-AUTH-USUARIOS-053](data-validation/RULE-AUTH-USUARIOS-053-user-payload-field-renames-with-empty-list-edge-case.md) | User payload field renames with empty-list edge case | DISCREPANCY | — |
| [RULE-AUTH-USUARIOS-054](data-validation/RULE-AUTH-USUARIOS-054-cpfvalidator-brazilian-cpf-check-digit-validation.md) | CPFValidator — Brazilian CPF check-digit validation | OK | — |
| [RULE-AUTH-USUARIOS-055](data-validation/RULE-AUTH-USUARIOS-055-username-normalization-before-login-submit.md) | Username normalization before login submit | OK | — |
| [RULE-AUTH-USUARIOS-056](data-validation/RULE-AUTH-USUARIOS-056-exceto-metodo-misspells-patch-as-path-across-write-viewsets.md) | exceto_metodo misspells PATCH as PATH across write viewsets | AMBIGUOUS | — |
| [RULE-AUTH-USUARIOS-062](data-validation/RULE-AUTH-USUARIOS-062-jwt-token-expiration-refresh-policy.md) | JWT token expiration/refresh policy | OK | — |
| [RULE-BALANCO-HIDRICO-040](data-validation/RULE-BALANCO-HIDRICO-040-entrada-saida-write-manage-data-payload-injection-balanco-id.md) | Entrada/Saida write manage_data payload injection (balanco id + assinar passthrough) | OK | — |
| [RULE-BALANCO-HIDRICO-047](data-validation/RULE-BALANCO-HIDRICO-047-entrada-always-marked-checado-on-creation.md) | Entrada always marked checado on creation | OK | — |
| [RULE-BALANCO-HIDRICO-048](data-validation/RULE-BALANCO-HIDRICO-048-entrada-saida-quantidade-fallback-to-zero-before-persist.md) | Entrada/Saida quantidade fallback to zero before persist | OK | — |
| [RULE-BALANCO-HIDRICO-049](data-validation/RULE-BALANCO-HIDRICO-049-entrada-saida-default-display-name-from-tipo.md) | Entrada/Saida default display name from tipo | OK | — |
| [RULE-BALANCO-HIDRICO-050](data-validation/RULE-BALANCO-HIDRICO-050-explicit-dia-parameter-parsing-validation-for-balanco-hidric.md) | Explicit 'dia' parameter parsing/validation for balanco hidrico | OK | — |
| [RULE-BALANCO-HIDRICO-051](data-validation/RULE-BALANCO-HIDRICO-051-entrada-saida-listing-includes-soft-deleted-records.md) | Entrada/Saida listing includes soft-deleted records | DISCREPANCY | — |
| [RULE-BALANCO-HIDRICO-052](data-validation/RULE-BALANCO-HIDRICO-052-vital-signs-field-set-and-units-sinais-vitais.md) | Vital-signs field set and units (sinais vitais) | OK | — |
| [RULE-BALANCO-HIDRICO-053](data-validation/RULE-BALANCO-HIDRICO-053-fluid-intake-output-field-set-and-volume-unit-entrada-saida.md) | Fluid intake/output field set and volume unit (entrada/saida) | OK | — |
| [RULE-BALANCO-HIDRICO-054](data-validation/RULE-BALANCO-HIDRICO-054-empty-state-for-fluid-balance-overview-tab.md) | Empty-state for fluid-balance overview tab | OK | — |
| [RULE-BALANCO-HIDRICO-055](data-validation/RULE-BALANCO-HIDRICO-055-iv-hydration-solution-vocabulary.md) | IV hydration solution vocabulary | OK | — |
| [RULE-BALANCO-HIDRICO-060](data-validation/RULE-BALANCO-HIDRICO-060-fluid-balance-complaint-conditional.md) | Fluid-balance complaint conditional | OK | — |
| [RULE-BALANCO-HIDRICO-061](data-validation/RULE-BALANCO-HIDRICO-061-required-hh-mm-24h-event-time-fluid-balance.md) | Required HH:MM 24h event-time (fluid balance) | DISCREPANCY | — |
| [RULE-BALANCO-HIDRICO-062](data-validation/RULE-BALANCO-HIDRICO-062-balanco-hidrico-day-filter-unused.md) | Balanco hidrico day filter (unused) | AMBIGUOUS | — |
| [RULE-CADASTROS-UI-001](data-validation/RULE-CADASTROS-UI-001-filterleitos-tri-state-occupancy-filter-sent-as-literal-stri.md) | FilterLeitos tri-state occupancy filter sent as literal string | AMBIGUOUS | — |
| [RULE-CADASTROS-UI-002](data-validation/RULE-CADASTROS-UI-002-leito-estabelecimento-name-and-code-locked-for-non-manual-co.md) | Leito/Estabelecimento name and code locked for non-manual companies | OK | — |
| [RULE-CADASTROS-UI-003](data-validation/RULE-CADASTROS-UI-003-delete-professional-action-gated-on-edit-mode-permission.md) | Delete-professional action gated on edit mode + permission | OK | — |
| [RULE-CADASTROS-UI-004](data-validation/RULE-CADASTROS-UI-004-camera-credential-fields-gated-on-can-manage-camera-permissi.md) | Camera credential fields gated on can_manage_camera permission | OK | — |
| [RULE-CADASTROS-UI-005](data-validation/RULE-CADASTROS-UI-005-new-user-password-auto-filled-from-cpf.md) | New-user password auto-filled from CPF | AMBIGUOUS | — |
| [RULE-CADASTROS-UI-006](data-validation/RULE-CADASTROS-UI-006-hardcoded-default-signature-pin-for-all-users.md) | Hardcoded default signature PIN for all users | AMBIGUOUS | — |
| [RULE-CADASTROS-UI-007](data-validation/RULE-CADASTROS-UI-007-group-edit-autosave-guards-partial-usuarios-updates.md) | Group-edit autosave guards partial "usuarios" updates | OK | — |
| [RULE-CADASTROS-UI-008](data-validation/RULE-CADASTROS-UI-008-company-tipo-only-settable-at-creation-hex-color-round-trip.md) | Company "tipo" only settable at creation; hex color round-trip | OK | — |
| [RULE-CADASTROS-UI-009](data-validation/RULE-CADASTROS-UI-009-cpf-input-mask-and-unformatting.md) | CPF input mask and unformatting | OK | — |
| [RULE-CADASTROS-UI-010](data-validation/RULE-CADASTROS-UI-010-formusuario-submit-value-normalization.md) | FormUsuario submit-value normalization | OK | — |
| [RULE-CADASTROS-UI-011](data-validation/RULE-CADASTROS-UI-011-formusuario-required-fields-only-enforced-in-modal-creation.md) | FormUsuario required fields only enforced in modal (creation) mode | OK | — |
| [RULE-CADASTROS-UI-012](data-validation/RULE-CADASTROS-UI-012-default-required-field-rule.md) | Default required-field rule | OK | — |
| [RULE-CADASTROS-UI-013](data-validation/RULE-CADASTROS-UI-013-email-format-validation.md) | Email format validation | OK | — |
| [RULE-CADASTROS-UI-014](data-validation/RULE-CADASTROS-UI-014-patient-sex-gender-code-labels.md) | Patient sex/gender code labels | OK | — |
| [RULE-CADASTROS-UI-015](data-validation/RULE-CADASTROS-UI-015-brazilian-federative-unit-uf-enumeration.md) | Brazilian federative-unit (UF) enumeration | OK | — |
| [RULE-CADASTROS-UI-016](data-validation/RULE-CADASTROS-UI-016-brazilian-document-and-number-formatting-masks.md) | Brazilian document and number formatting masks | OK | DISCREPANCY |
| [RULE-CADASTROS-UI-017](data-validation/RULE-CADASTROS-UI-017-length-heuristic-date-datetime-formatting.md) | Length-heuristic date/datetime formatting | OK | — |
| [RULE-CADASTROS-UI-018](data-validation/RULE-CADASTROS-UI-018-date-field-detection-convention-data-dt-key-prefixes.md) | Date-field detection convention (data_ / dt_ key prefixes) | OK | — |
| [RULE-CADASTROS-UI-019](data-validation/RULE-CADASTROS-UI-019-image-file-extension-whitelist.md) | Image-file extension whitelist | OK | — |
| [RULE-CADASTROS-UI-020](data-validation/RULE-CADASTROS-UI-020-single-image-or-pdf-file-constraint-on-avatar-logo-uploader.md) | Single image-or-PDF file constraint on avatar/logo uploader | OK | — |
| [RULE-COMUNICACAO-001](data-validation/RULE-COMUNICACAO-001-reaction-count-by-emoji-aggregation-sql-correct-vs-order-dep.md) | Reaction-count-by-emoji aggregation — SQL-correct vs order-dependent duplicate implementations | DISCREPANCY | UNVERIFIABLE |
| [RULE-COMUNICACAO-002](data-validation/RULE-COMUNICACAO-002-current-user-s-own-reaction-id-on-an-observation.md) | Current user's own reaction id on an observation | OK | UNVERIFIABLE |
| [RULE-COMUNICACAO-012](data-validation/RULE-COMUNICACAO-012-patient-snapshot-in-observation-branches-by-leito-type.md) | Patient snapshot in observation branches by leito type | OK | — |
| [RULE-COMUNICACAO-015](data-validation/RULE-COMUNICACAO-015-chat-reaction-removal-restricted-to-its-own-author.md) | Chat reaction removal restricted to its own author | OK | — |
| [RULE-COMUNICACAO-021](data-validation/RULE-COMUNICACAO-021-chat-message-list-pagination.md) | Chat message list pagination | OK | — |
| [RULE-COMUNICACAO-033](data-validation/RULE-COMUNICACAO-033-checado-por-id-always-forced-to-the-requesting-user.md) | checado_por_id always forced to the requesting user | OK | — |
| [RULE-COMUNICACAO-034](data-validation/RULE-COMUNICACAO-034-validacao-de-leito-para-acao-de-feed-homecare.md) | Validacao de leito para acao de feed homecare | DISCREPANCY | — |
| [RULE-COMUNICACAO-035](data-validation/RULE-COMUNICACAO-035-homecare-feed-action-type-vocabulary-acaodict-render-map-vs.md) | Homecare feed action-type vocabulary — acaoDict render map vs Feed.Acao TS union | DISCREPANCY | — |
| [RULE-COMUNICACAO-036](data-validation/RULE-COMUNICACAO-036-chat-feed-emoji-reaction-enumeration.md) | Chat/feed emoji-reaction enumeration | OK | — |
| [RULE-COMUNICACAO-038](data-validation/RULE-COMUNICACAO-038-reaction-usuario-observacao-always-server-injected.md) | Reaction usuario/observacao always server-injected | OK | — |
| [RULE-COMUNICACAO-039](data-validation/RULE-COMUNICACAO-039-message-scope-enumeration.md) | Message scope enumeration | OK | — |
| [RULE-COMUNICACAO-041](data-validation/RULE-COMUNICACAO-041-observation-setor-id-is-always-forced-from-the-url.md) | Observation setor_id is always forced from the URL | AMBIGUOUS | — |
| [RULE-COMUNICACAO-042](data-validation/RULE-COMUNICACAO-042-observation-responsavel-id-is-always-forced-to-the-authentic.md) | Observation responsavel_id is always forced to the authenticated user | OK | — |
| [RULE-COMUNICACAO-043](data-validation/RULE-COMUNICACAO-043-observation-reply-field-rename.md) | Observation reply field rename | OK | — |
| [RULE-COMUNICACAO-045](data-validation/RULE-COMUNICACAO-045-filepicker-only-reconciles-local-file-list-on-removal.md) | FilePicker only reconciles local file list on removal | AMBIGUOUS | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-003](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-003-combinar-documentos-all-or-nothing-pdf-validation-gate-befor.md) | combinar_documentos — all-or-nothing PDF validation gate before merge/upload | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-007](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-007-cryptocubo-get-formato-assinatura-signature-format-mapping.md) | Cryptocubo __get_formato_assinatura — signature-format mapping | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-008](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-008-cryptocubo-pin-alias-fallback-inconsistent-or-fallback-seman.md) | Cryptocubo PIN/ALIAS fallback — inconsistent 'or'-fallback semantics, unencoded fallback PIN | DISCREPANCY | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-009](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-009-cryptocubo-check-response-status-non-200-response-audit-logg.md) | Cryptocubo __check_response_status — non-200 response audit logging + hard failure | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-010](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-010-digital-signature-eligibility-user-must-have-cpf-and-pin.md) | Digital-signature eligibility - user must have CPF and PIN | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-011](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-011-bulk-download-button-requires-a-non-empty-selection.md) | Bulk-download button requires a non-empty selection | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-012](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-012-leito-file-send-requires-image-s-or-a-pdf-plus-category-obse.md) | Leito file-send requires image(s) or a PDF plus category/observation | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-013](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-013-leito-upload-tab-gated-on-can-upload-files-amhdocs-permissio.md) | Leito upload tab gated on can_upload_files_amhdocs permission | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-016](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-016-agrupar-pdfs-e-baixar-workflow-response-validation-chain.md) | "Agrupar PDFs e baixar" workflow response-validation chain | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-017](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-017-leito-arquivos-list-default-sort-order.md) | Leito arquivos list default sort order | AMBIGUOUS | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-021](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-021-pdf-export-base64-flag-uses-raw-truthy-string-check.md) | PDF export base64 flag uses raw truthy string check | DISCREPANCY | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-022](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-022-prescricao-pdf-export-has-no-explicit-validation-for-missing.md) | Prescricao PDF export has no explicit validation for missing 'dia' | DISCREPANCY | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-023](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-023-prescricao-pdf-export-unguarded-first-access-for-dt-entrada.md) | Prescricao PDF export - unguarded first() access for dt_entrada | DISCREPANCY | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-024](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-024-prescription-cpoe-signature-inconsistency-record.md) | Prescription/CPOE signature-inconsistency record | AMBIGUOUS | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-025](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-025-report-filter-date-prefix-formatting-convention.md) | Report filter date-prefix formatting convention | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-026](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-026-pdf-upload-mime-type-validation.md) | PDF upload MIME-type validation | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-027](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-027-amhdocs-external-file-lookup-keyed-by-bed-s-nr-atendimento.md) | AMHDocs external file lookup keyed by bed's nr_atendimento | OK | UNVERIFIABLE |
| [RULE-DOCUMENTACAO-FATURAMENTO-028](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-028-amhdocs-pagination-links-rewritten-to-proxy-s-own-url.md) | AMHDocs pagination links rewritten to proxy's own URL | OK | UNVERIFIABLE |
| [RULE-DOCUMENTACAO-FATURAMENTO-029](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-029-pdf-grouping-agrupar-pdf-requires-a-non-empty-array-of-ids.md) | PDF grouping (agrupar-pdf) requires a non-empty array of ids | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-030](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-030-pdf-grouping-response-status-code-decision-tree.md) | PDF grouping response status-code decision tree | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-031](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-031-arquivo-filter-end-date-must-not-precede-start-date.md) | Arquivo filter end-date must not precede start date | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-032](data-validation/RULE-DOCUMENTACAO-FATURAMENTO-032-default-electronic-signature-configuration-for-cryptocubo-do.md) | Default electronic-signature configuration for CryptoCubo document signing | OK | — |
| [RULE-ESTABILIDADE-026](data-validation/RULE-ESTABILIDADE-026-auto-start-time-default-now-for-noradrenaline-cardiac-arrest.md) | Auto start-time default (now) for noradrenaline & cardiac arrest | OK | — |
| [RULE-EVOLUCOES-005](data-validation/RULE-EVOLUCOES-005-company-evolutions-patient-name-resolved-by-attendance-numbe.md) | Company evolutions - patient name resolved by attendance number | OK | UNVERIFIABLE |
| [RULE-EVOLUCOES-006](data-validation/RULE-EVOLUCOES-006-leito-resolution-precedence-for-form-endpoints.md) | Leito resolution precedence for form endpoints | OK | — |
| [RULE-EVOLUCOES-018](data-validation/RULE-EVOLUCOES-018-company-wide-evolutions-queryset-filter-with-possible-instan.md) | Company-wide evolutions queryset filter with possible instance-vs-id type mismatch | AMBIGUOUS | — |
| [RULE-EVOLUCOES-022](data-validation/RULE-EVOLUCOES-022-single-checkbox-conditions-key-mismatch.md) | Single-checkbox conditions key mismatch | AMBIGUOUS | — |
| [RULE-EVOLUCOES-023](data-validation/RULE-EVOLUCOES-023-dynamic-clinical-form-field-type-vocabulary-declared-union-v.md) | Dynamic clinical-form field-type vocabulary (declared union vs render dispatch) | DISCREPANCY | — |
| [RULE-EVOLUCOES-048](data-validation/RULE-EVOLUCOES-048-dual-query-parameter-encoding-on-evolution-report-fetch.md) | Dual query-parameter encoding on evolution-report fetch | AMBIGUOUS | — |
| [RULE-EVOLUCOES-049](data-validation/RULE-EVOLUCOES-049-annullable-anulavel-group-nullification-on-submit.md) | Annullable (anulavel) group nullification on submit | OK | — |
| [RULE-EVOLUCOES-050](data-validation/RULE-EVOLUCOES-050-checkable-checavel-subgroup-toggle-and-null-on-disable.md) | Checkable (checavel) subgroup toggle and null-on-disable | OK | — |
| [RULE-EVOLUCOES-051](data-validation/RULE-EVOLUCOES-051-cannot-update-an-inactive-evolution.md) | Cannot update an inactive evolution | OK | — |
| [RULE-EVOLUCOES-052](data-validation/RULE-EVOLUCOES-052-only-the-original-author-can-edit-an-evolution.md) | Only the original author can edit an evolution | OK | — |
| [RULE-EVOLUCOES-053](data-validation/RULE-EVOLUCOES-053-cpf-required-to-release-an-evolution.md) | CPF required to release an evolution | OK | — |
| [RULE-EVOLUCOES-054](data-validation/RULE-EVOLUCOES-054-cpf-and-pin-required-to-sign-an-evolution.md) | CPF and PIN required to sign an evolution | OK | — |
| [RULE-EVOLUCOES-056](data-validation/RULE-EVOLUCOES-056-nutritionist-evolution-mandates-global-nutritional-therapy-a.md) | Nutritionist evolution mandates global, nutritional-therapy, and abdominal assessments | OK | — |
| [RULE-EVOLUCOES-057](data-validation/RULE-EVOLUCOES-057-dispositivos-invasivos-novo-declared-but-excluded-from-meta.md) | dispositivos_invasivos_novo declared but excluded from Meta.fields | DISCREPANCY | — |
| [RULE-EVOLUCOES-058](data-validation/RULE-EVOLUCOES-058-atualizar-campos-evolucao-required-id-field-per-sub-form-whe.md) | atualizar_campos_evolucao — required 'id' field per sub-form when updating an evolution | OK | — |
| [RULE-EVOLUCOES-059](data-validation/RULE-EVOLUCOES-059-registration-datetime-immutable-when-editing-a-past-evolutio.md) | Registration datetime immutable when editing a past evolution | OK | — |
| [RULE-EVOLUCOES-060](data-validation/RULE-EVOLUCOES-060-nutritional-assessment-numeric-coercion-on-load.md) | Nutritional-assessment numeric coercion on load | OK | — |
| [RULE-EVOLUCOES-061](data-validation/RULE-EVOLUCOES-061-ventilation-device-date-field-adapters-for-nursing-forms.md) | Ventilation/device date-field adapters for nursing forms | OK | — |
| [RULE-EVOLUCOES-062](data-validation/RULE-EVOLUCOES-062-pharmacist-evolution-form-key-naming-type-inconsistency.md) | Pharmacist evolution-form key naming/type inconsistency | DISCREPANCY | — |
| [RULE-EVOLUCOES-063](data-validation/RULE-EVOLUCOES-063-strip-ids-when-creating-a-new-evolucao.md) | Strip ids when creating a new evolucao | OK | — |
| [RULE-EVOLUCOES-064](data-validation/RULE-EVOLUCOES-064-field-read-only-disableall-conditions.md) | Field read-only (disableAll) conditions | OK | — |
| [RULE-EVOLUCOES-065](data-validation/RULE-EVOLUCOES-065-string-field-disable-condition-nullifier-lookup.md) | String field disable condition (nullifier lookup) | DISCREPANCY | — |
| [RULE-EVOLUCOES-066](data-validation/RULE-EVOLUCOES-066-numeric-field-inclusive-min-max-range-validation.md) | Numeric field inclusive min/max range validation | OK | — |
| [RULE-EVOLUCOES-067](data-validation/RULE-EVOLUCOES-067-interval-field-slider-bounds.md) | Interval field slider bounds | OK | — |
| [RULE-EVOLUCOES-068](data-validation/RULE-EVOLUCOES-068-multicheck-selection-count-min-max.md) | Multicheck selection-count min/max | OK | — |
| [RULE-EVOLUCOES-069](data-validation/RULE-EVOLUCOES-069-masked-field-regex-pattern-validation.md) | Masked field regex pattern validation | OK | — |
| [RULE-EVOLUCOES-070](data-validation/RULE-EVOLUCOES-070-repeatable-list-maximum-item-cap.md) | Repeatable list maximum item cap | OK | — |
| [RULE-EVOLUCOES-071](data-validation/RULE-EVOLUCOES-071-required-if-validation-for-text-date-extra-fields.md) | Required-if validation for text/date/extra fields | OK | — |
| [RULE-EVOLUCOES-072](data-validation/RULE-EVOLUCOES-072-dynamic-form-field-level-validation-constraints.md) | Dynamic-form field-level validation constraints | OK | — |
| [RULE-EVOLUCOES-073](data-validation/RULE-EVOLUCOES-073-dynamic-form-conditional-field-visibility.md) | Dynamic-form conditional field visibility | OK | — |
| [RULE-EVOLUCOES-074](data-validation/RULE-EVOLUCOES-074-form-group-annulment-soft-void-mechanic.md) | Form-group annulment (soft-void) mechanic | AMBIGUOUS | — |
| [RULE-EVOLUCOES-075](data-validation/RULE-EVOLUCOES-075-encounter-number-field-name-type-mismatch-across-models.md) | Encounter-number field name/type mismatch across models | DISCREPANCY | — |
| [RULE-EVOLUCOES-076](data-validation/RULE-EVOLUCOES-076-gender-code-enumeration.md) | Gender code enumeration | OK | — |
| [RULE-EVOLUCOES-077](data-validation/RULE-EVOLUCOES-077-relatorio-de-evolucao-filter-requires-professional-valid-dat.md) | Relatório de Evolução filter requires professional + valid date range | OK | — |
| [RULE-FORMULARIOS-CLINICOS-010](data-validation/RULE-FORMULARIOS-CLINICOS-010-physician-physical-exam-enums-and-conditional-reveals.md) | Physician physical-exam enums and conditional reveals | OK | — |
| [RULE-FORMULARIOS-CLINICOS-011](data-validation/RULE-FORMULARIOS-CLINICOS-011-nursing-global-assessment-enums-and-risk-conditionals.md) | Nursing global assessment enums and risk conditionals | OK | — |
| [RULE-FORMULARIOS-CLINICOS-012](data-validation/RULE-FORMULARIOS-CLINICOS-012-nursing-technician-respiratory-assessment-with-aspiration-co.md) | Nursing-technician respiratory assessment with aspiration conditional | OK | — |
| [RULE-FORMULARIOS-CLINICOS-013](data-validation/RULE-FORMULARIOS-CLINICOS-013-nursing-technician-genitourinary-with-diaper-change-conditio.md) | Nursing-technician genitourinary with diaper-change conditional | OK | — |
| [RULE-FORMULARIOS-CLINICOS-018](data-validation/RULE-FORMULARIOS-CLINICOS-018-pressure-injury-lpp-origin-classification-enum-tipo-lpp-back.md) | Pressure-injury (LPP) origin classification enum (tipo_lpp, backend serializer) | OK | — |
| [RULE-FORMULARIOS-CLINICOS-019](data-validation/RULE-FORMULARIOS-CLINICOS-019-other-lesion-non-pressure-assessment-list.md) | Other-lesion (non-pressure) assessment list | OK | — |
| [RULE-FORMULARIOS-CLINICOS-020](data-validation/RULE-FORMULARIOS-CLINICOS-020-anatomical-lesion-catheter-insertion-site-enumeration.md) | Anatomical lesion / catheter-insertion site enumeration | OK | — |
| [RULE-FORMULARIOS-CLINICOS-021](data-validation/RULE-FORMULARIOS-CLINICOS-021-home-care-chronic-diagnosis-catalog-backend-humanize-map-fro.md) | Home-care chronic-diagnosis catalog (backend humanize map + frontend physician multicheck) | DISCREPANCY | — |
| [RULE-FORMULARIOS-CLINICOS-022](data-validation/RULE-FORMULARIOS-CLINICOS-022-vascular-access-dressing-tracked-field-enum.md) | Vascular-access / dressing tracked-field enum | OK | — |
| [RULE-FORMULARIOS-CLINICOS-023](data-validation/RULE-FORMULARIOS-CLINICOS-023-physician-in-use-invasive-devices-vocabulary.md) | Physician in-use invasive devices vocabulary | OK | — |
| [RULE-FORMULARIOS-CLINICOS-024](data-validation/RULE-FORMULARIOS-CLINICOS-024-physician-in-use-equipment-vocabulary.md) | Physician in-use equipment vocabulary | OK | — |
| [RULE-FORMULARIOS-CLINICOS-025](data-validation/RULE-FORMULARIOS-CLINICOS-025-speech-therapy-global-assessment-enums.md) | Speech-therapy global assessment enums | OK | — |
| [RULE-FORMULARIOS-CLINICOS-026](data-validation/RULE-FORMULARIOS-CLINICOS-026-speech-therapy-orofacial-and-language-enums.md) | Speech-therapy orofacial and language enums | OK | — |
| [RULE-FORMULARIOS-CLINICOS-027](data-validation/RULE-FORMULARIOS-CLINICOS-027-music-therapy-global-assessment-enums.md) | Music-therapy global assessment enums | OK | — |
| [RULE-FORMULARIOS-CLINICOS-028](data-validation/RULE-FORMULARIOS-CLINICOS-028-intramusical-relations-assessment-enum.md) | Intramusical-relations assessment enum | OK | — |
| [RULE-FORMULARIOS-CLINICOS-029](data-validation/RULE-FORMULARIOS-CLINICOS-029-nursing-abdominal-assessment-enums.md) | Nursing abdominal assessment enums | OK | — |
| [RULE-FORMULARIOS-CLINICOS-030](data-validation/RULE-FORMULARIOS-CLINICOS-030-nursing-genitourinary-assessment-enums.md) | Nursing genitourinary assessment enums | OK | — |
| [RULE-FORMULARIOS-CLINICOS-031](data-validation/RULE-FORMULARIOS-CLINICOS-031-nursing-neurological-assessment-enums.md) | Nursing neurological assessment enums | OK | — |
| [RULE-FORMULARIOS-CLINICOS-032](data-validation/RULE-FORMULARIOS-CLINICOS-032-physiotherapy-neuro-cardio-respiratory-assessment-enums.md) | Physiotherapy neuro/cardio/respiratory assessment enums | OK | — |
| [RULE-FORMULARIOS-CLINICOS-033](data-validation/RULE-FORMULARIOS-CLINICOS-033-physiotherapy-motor-function-enums.md) | Physiotherapy motor-function enums | OK | — |
| [RULE-FORMULARIOS-CLINICOS-034](data-validation/RULE-FORMULARIOS-CLINICOS-034-psychology-global-assessment-enums.md) | Psychology global assessment enums | OK | — |
| [RULE-FORMULARIOS-CLINICOS-035](data-validation/RULE-FORMULARIOS-CLINICOS-035-psychological-assessment-enums.md) | Psychological-assessment enums | OK | — |
| [RULE-FORMULARIOS-CLINICOS-036](data-validation/RULE-FORMULARIOS-CLINICOS-036-nursing-technician-global-assessment-with-locomotion.md) | Nursing-technician global assessment with locomotion | OK | — |
| [RULE-FORMULARIOS-CLINICOS-039](data-validation/RULE-FORMULARIOS-CLINICOS-039-binary-gender-iconography-masculino-feminino.md) | Binary gender iconography (Masculino/Feminino) | AMBIGUOUS | — |
| [RULE-FORMULARIOS-CLINICOS-041](data-validation/RULE-FORMULARIOS-CLINICOS-041-optional-hh-mm-24h-exit-time-mask.md) | Optional HH:MM 24h exit-time mask | OK | — |
| [RULE-FORMULARIOS-CLINICOS-044](data-validation/RULE-FORMULARIOS-CLINICOS-044-pharmacist-evolution-neurological-and-cardiological-assessme.md) | Pharmacist evolution neurological and cardiological assessment vocabularies | OK | — |
| [RULE-FORMULARIOS-CLINICOS-045](data-validation/RULE-FORMULARIOS-CLINICOS-045-nursing-technician-evolution-neurological-assessment-vocabul.md) | Nursing-technician evolution neurological assessment vocabulary | OK | — |
| [RULE-INDICADORES-ETL-008](data-validation/RULE-INDICADORES-ETL-008-per-sector-dashboard-shortcut-visibility-by-empresa-type.md) | Per-sector dashboard shortcut visibility by empresa type | OK | — |
| [RULE-INDICADORES-ETL-009](data-validation/RULE-INDICADORES-ETL-009-unread-message-badge-display-and-cap.md) | Unread-message badge display and cap | OK | — |
| [RULE-INDICADORES-ETL-019](data-validation/RULE-INDICADORES-ETL-019-assistencial-indicators-endpoint-url-template-bug.md) | Assistencial-indicators endpoint URL template bug | DISCREPANCY | — |
| [RULE-INDICADORES-ETL-020](data-validation/RULE-INDICADORES-ETL-020-generic-indicator-create-always-stamps-server-side-usuario-i.md) | Generic indicator create always stamps server-side usuario_id and timestamp | OK | — |
| [RULE-INDICADORES-ETL-021](data-validation/RULE-INDICADORES-ETL-021-video-call-entry-indicator-has-a-fixed-tipo-and-unvalidated.md) | Video-call entry indicator has a fixed tipo and unvalidated setor_id | OK | — |
| [RULE-INDICADORES-ETL-022](data-validation/RULE-INDICADORES-ETL-022-macro-indicator-tile-display-filter.md) | Macro-indicator tile display filter | OK | — |
| [RULE-INDICADORES-ETL-024](data-validation/RULE-INDICADORES-ETL-024-clinical-indicator-null-vs-truthy-display-rule-informacoes-a.md) | Clinical indicator null-vs-truthy display rule (Informações Assistenciais) | OK | — |
| [RULE-INDICADORES-ETL-025](data-validation/RULE-INDICADORES-ETL-025-24h-indicator-numeric-type-display-filter.md) | 24h indicator numeric-type display filter | OK | — |
| [RULE-INDICADORES-ETL-026](data-validation/RULE-INDICADORES-ETL-026-micro-indicadores-icon-value-display-rule.md) | Micro-indicadores icon/value display rule | OK | — |
| [RULE-INDICADORES-ETL-027](data-validation/RULE-INDICADORES-ETL-027-indicador-tipo-enumeration-and-type-specific-payload-validat.md) | Indicador tipo enumeration and type-specific payload validation (backend enum/dispatch vs front | DISCREPANCY | — |
| [RULE-MOVIMENTACAO-ADT-006](data-validation/RULE-MOVIMENTACAO-ADT-006-bed-patient-snapshot-defaults-to-empty-dict-when-unassigned.md) | Bed patient snapshot defaults to empty dict when unassigned | OK | UNVERIFIABLE |
| [RULE-MOVIMENTACAO-ADT-007](data-validation/RULE-MOVIMENTACAO-ADT-007-patient-basic-name-age-computed-fields.md) | Patient basic name/age computed fields | OK | UNVERIFIABLE |
| [RULE-MOVIMENTACAO-ADT-008](data-validation/RULE-MOVIMENTACAO-ADT-008-precomputed-vinculo-lookup-dict-is-built-but-never-consumed.md) | Precomputed vinculo lookup dict is built but never consumed by the serializer | DISCREPANCY | UNVERIFIABLE |
| [RULE-MOVIMENTACAO-ADT-010](data-validation/RULE-MOVIMENTACAO-ADT-010-live-camera-rtsp-url-construction.md) | Live camera RTSP URL construction | OK | UNVERIFIABLE |
| [RULE-MOVIMENTACAO-ADT-019](data-validation/RULE-MOVIMENTACAO-ADT-019-bed-queryset-hierarchical-scope-resolution-setor-empresa-all.md) | Bed queryset hierarchical scope resolution (setor > empresa > all) | OK | — |
| [RULE-MOVIMENTACAO-ADT-027](data-validation/RULE-MOVIMENTACAO-ADT-027-bed-action-fields-expose-has-camera-only-on-retrieve.md) | Bed action_fields expose has_camera only on retrieve | OK | — |
| [RULE-MOVIMENTACAO-ADT-028](data-validation/RULE-MOVIMENTACAO-ADT-028-camera-enabled-bed-list-requires-a-non-empty-configured-ip.md) | Camera-enabled bed list requires a non-empty configured IP | OK | — |
| [RULE-MOVIMENTACAO-ADT-029](data-validation/RULE-MOVIMENTACAO-ADT-029-movimentacao-queryset-optionally-scoped-by-setor-ordered-by.md) | Movimentacao queryset optionally scoped by setor, ordered by most recent update | OK | — |
| [RULE-MOVIMENTACAO-ADT-030](data-validation/RULE-MOVIMENTACAO-ADT-030-sector-patient-list-restricted-to-currently-occupied-beds.md) | Sector patient list restricted to currently-occupied beds | OK | — |
| [RULE-MOVIMENTACAO-ADT-041](data-validation/RULE-MOVIMENTACAO-ADT-041-patient-creation-wrapper-cadastrarpaciente.md) | Patient creation wrapper (CadastrarPaciente) | OK | — |
| [RULE-MOVIMENTACAO-ADT-043](data-validation/RULE-MOVIMENTACAO-ADT-043-setorpacientevinculoviewset-forces-all-link-fields-from-the.md) | SetorPacienteVinculoViewSet forces all link fields from the URL and hard-deletes | OK | — |
| [RULE-MOVIMENTACAO-ADT-048](data-validation/RULE-MOVIMENTACAO-ADT-048-fixed-3-second-minimum-spinner-on-bed-camera-page.md) | Fixed 3-second minimum spinner on bed camera page | AMBIGUOUS | — |
| [RULE-MOVIMENTACAO-ADT-049](data-validation/RULE-MOVIMENTACAO-ADT-049-test-temporary-bed-exclusion-filter-and-semantics.md) | Test/temporary bed exclusion filter (AND semantics) | AMBIGUOUS | — |
| [RULE-MOVIMENTACAO-ADT-050](data-validation/RULE-MOVIMENTACAO-ADT-050-bed-occupancy-and-active-status-mapping-tasy-indicators.md) | Bed occupancy and active-status mapping (Tasy indicators) | OK | — |
| [RULE-MOVIMENTACAO-ADT-051](data-validation/RULE-MOVIMENTACAO-ADT-051-manual-occupied-bed-requires-a-movimentacao.md) | Manual occupied bed requires a movimentacao | OK | — |
| [RULE-MOVIMENTACAO-ADT-053](data-validation/RULE-MOVIMENTACAO-ADT-053-invasive-procedure-type-enumeration-10-values.md) | Invasive-procedure type enumeration (10 values) | OK | — |
| [RULE-MOVIMENTACAO-ADT-054](data-validation/RULE-MOVIMENTACAO-ADT-054-patient-gender-icon-mapping.md) | Patient gender icon mapping | OK | — |
| [RULE-MOVIMENTACAO-ADT-055](data-validation/RULE-MOVIMENTACAO-ADT-055-discharge-baixa-requires-both-exit-date-and-reason.md) | Discharge (baixa) requires BOTH exit date and reason | OK | — |
| [RULE-MOVIMENTACAO-ADT-056](data-validation/RULE-MOVIMENTACAO-ADT-056-movimentacao-requires-patient-unless-it-chains-a-prior-movim.md) | Movimentacao requires patient unless it chains a prior movimentacao | OK | — |
| [RULE-MOVIMENTACAO-ADT-057](data-validation/RULE-MOVIMENTACAO-ADT-057-movimentacao-data-entrada-absent-ok-empty-invalid-future-rej.md) | Movimentacao data_entrada - absent OK, empty invalid, future rejected | OK | — |
| [RULE-MOVIMENTACAO-ADT-058](data-validation/RULE-MOVIMENTACAO-ADT-058-automatic-type-bed-rejects-movimentacao-lacking-data-entrada.md) | Automatic-type bed rejects movimentacao lacking data_entrada | AMBIGUOUS | — |
| [RULE-MOVIMENTACAO-ADT-059](data-validation/RULE-MOVIMENTACAO-ADT-059-entry-date-must-not-be-in-the-future-datavalidation.md) | Entry date must not be in the future (DataValidation) | OK | — |
| [RULE-MOVIMENTACAO-ADT-060](data-validation/RULE-MOVIMENTACAO-ADT-060-birthdate-must-not-be-in-the-future-patient-payload-required.md) | Birthdate must not be in the future + patient payload required | OK | — |
| [RULE-MOVIMENTACAO-ADT-061](data-validation/RULE-MOVIMENTACAO-ADT-061-dados-prontuario-payload-required.md) | dados_prontuario payload required | OK | — |
| [RULE-MOVIMENTACAO-ADT-062](data-validation/RULE-MOVIMENTACAO-ADT-062-movimentacao-creation-composite-validation.md) | Movimentacao creation composite validation | OK | — |
| [RULE-MOVIMENTACAO-ADT-064](data-validation/RULE-MOVIMENTACAO-ADT-064-patient-registration-required-fields-and-identifiers.md) | Patient registration required fields and identifiers | OK | — |
| [RULE-MOVIMENTACAO-ADT-065](data-validation/RULE-MOVIMENTACAO-ADT-065-infopaciente-listing-scoped-by-encounter.md) | InfoPaciente listing scoped by encounter | OK | — |
| [RULE-MOVIMENTACAO-ADT-066](data-validation/RULE-MOVIMENTACAO-ADT-066-update-patient-list-button-disabled-check-uses-array-referen.md) | Update-patient-list button disabled check uses array reference equality | DISCREPANCY | — |
| [RULE-MOVIMENTACAO-ADT-067](data-validation/RULE-MOVIMENTACAO-ADT-067-bed-movement-prontuario-field-annulment-and-date-formatting.md) | Bed-movement prontuário field annulment and date formatting | OK | — |
| [RULE-MOVIMENTACAO-ADT-068](data-validation/RULE-MOVIMENTACAO-ADT-068-past-prontuario-date-field-hydration.md) | Past-prontuário date field hydration | OK | — |
| [RULE-MOVIMENTACAO-ADT-069](data-validation/RULE-MOVIMENTACAO-ADT-069-formprontuario-fields-have-no-bound-input-controls.md) | FormProntuario fields have no bound input controls | DISCREPANCY | — |
| [RULE-MOVIMENTACAO-ADT-070](data-validation/RULE-MOVIMENTACAO-ADT-070-filterocupacoes-todos-sentinel-and-occupancy-creation-type-f.md) | FilterOcupacoes "todos" sentinel and occupancy creation-type filter | OK | — |
| [RULE-NUTRICAO-008](data-validation/RULE-NUTRICAO-008-height-altura-range-validation-0-3-m.md) | Height (altura) range validation 0-3 m | OK | — |
| [RULE-NUTRICAO-009](data-validation/RULE-NUTRICAO-009-food-intolerance-aversion-enums-with-conditional-description.md) | Food intolerance / aversion enums with conditional description | OK | — |
| [RULE-NUTRICAO-010](data-validation/RULE-NUTRICAO-010-care-risk-riscos-assistenciais-checklist-with-allergy-detail.md) | Care-risk (riscos assistenciais) checklist with allergy detail | OK | — |
| [RULE-NUTRICAO-011](data-validation/RULE-NUTRICAO-011-dietitian-abdominal-assessment-enums-extended.md) | Dietitian abdominal assessment enums (extended) | OK | — |
| [RULE-OPERACIONAL-INFRA-002](data-validation/RULE-OPERACIONAL-INFRA-002-patient-name-abbreviation-with-connective-handling-nome-abre.md) | Patient name abbreviation with connective handling (nome_abreviado_paciente) | DISCREPANCY | UNVERIFIABLE |
| [RULE-OPERACIONAL-INFRA-009](data-validation/RULE-OPERACIONAL-INFRA-009-format-horario-normalize-hour-only-strings-to-hh-mm.md) | format_horario — normalize hour-only strings to HH:MM | OK | UNVERIFIABLE |
| [RULE-OPERACIONAL-INFRA-010](data-validation/RULE-OPERACIONAL-INFRA-010-parse-date-to-iso-multi-format-date-string-parser-with-fixed.md) | parse_date_to_iso — multi-format date string parser with fixed precedence | OK | UNVERIFIABLE |
| [RULE-OPERACIONAL-INFRA-011](data-validation/RULE-OPERACIONAL-INFRA-011-get-number-safe-numeric-coercion-with-zero-default.md) | get_number — safe numeric coercion with zero default | OK | UNVERIFIABLE |
| [RULE-OPERACIONAL-INFRA-017](data-validation/RULE-OPERACIONAL-INFRA-017-paranoiamixin-delete-restore-admin-path-hard-delete-vs-casca.md) | ParanoiaMixin.delete/restore — admin-path hard delete vs cascading soft delete | AMBIGUOUS | — |
| [RULE-OPERACIONAL-INFRA-018](data-validation/RULE-OPERACIONAL-INFRA-018-setupmodel-delete-overrides-paranoiamixin-delete-with-simple.md) | SetUpModel.delete — overrides ParanoiaMixin.delete with simpler soft-delete-only semantics (no  | DISCREPANCY | — |
| [RULE-OPERACIONAL-INFRA-020](data-validation/RULE-OPERACIONAL-INFRA-020-offline-evolution-forms-visible-if-authored-by-the-requestin.md) | Offline evolution forms visible if authored by the requesting user OR marked 'liberado' | OK | — |
| [RULE-OPERACIONAL-INFRA-021](data-validation/RULE-OPERACIONAL-INFRA-021-offline-endpoints-hardcode-empresa-lookup-to-whitelabel-home.md) | Offline endpoints hardcode empresa lookup to whitelabel='homecare' | DISCREPANCY | — |
| [RULE-OPERACIONAL-INFRA-022](data-validation/RULE-OPERACIONAL-INFRA-022-offline-bed-access-requires-user-membership-at-every-level-o.md) | Offline bed access requires user membership at every level of the ownership chain | OK | — |
| [RULE-OPERACIONAL-INFRA-023](data-validation/RULE-OPERACIONAL-INFRA-023-prescription-balance-offline-endpoints-only-include-currentl.md) | Prescription/balance offline endpoints only include currently-occupied homecare beds | OK | — |
| [RULE-OPERACIONAL-INFRA-024](data-validation/RULE-OPERACIONAL-INFRA-024-offline-horario-prescricao-deletion-capability-is-permission.md) | Offline horario-prescricao deletion capability is permission-gated | OK | — |
| [RULE-OPERACIONAL-INFRA-032](data-validation/RULE-OPERACIONAL-INFRA-032-popular-banco-valores-maximos-atributos-vital-sign-reference.md) | popular_banco valores_maximos_atributos — vital-sign reference ranges for synthetic data, PEEP  | DISCREPANCY | DISCREPANCY |
| [RULE-OPERACIONAL-INFRA-036](data-validation/RULE-OPERACIONAL-INFRA-036-custom-exception-handler-flatten-errors-drf-error-envelope-m.md) | custom_exception_handler / flatten_errors — DRF error envelope mapping with a Python 3.10+ inco | DISCREPANCY | — |
| [RULE-OPERACIONAL-INFRA-037](data-validation/RULE-OPERACIONAL-INFRA-037-listchoicefield-to-representation-context-dependent-represen.md) | ListChoiceField.to_representation — context-dependent representation switch | AMBIGUOUS | — |
| [RULE-OPERACIONAL-INFRA-043](data-validation/RULE-OPERACIONAL-INFRA-043-breadcrumb-hides-uuid-shaped-route-segments.md) | Breadcrumb hides UUID-shaped route segments | OK | — |
| [RULE-OPERACIONAL-INFRA-050](data-validation/RULE-OPERACIONAL-INFRA-050-next-image-remote-image-domain-whitelist.md) | next/image remote image domain whitelist | OK | — |
| [RULE-OPERACIONAL-INFRA-051](data-validation/RULE-OPERACIONAL-INFRA-051-uniqueness-constraints-across-org-hierarchy.md) | Uniqueness constraints across org hierarchy | OK | — |
| [RULE-OPERACIONAL-INFRA-053](data-validation/RULE-OPERACIONAL-INFRA-053-uniquetogethermanagermixin-save-composite-uniqueness-excludi.md) | UniqueTogetherManagerMixin.save — composite uniqueness excluding soft-deleted rows | OK | — |
| [RULE-OPERACIONAL-INFRA-054](data-validation/RULE-OPERACIONAL-INFRA-054-uniquemanagermixin-save-single-field-uniqueness-excluding-so.md) | UniqueManagerMixin.save — single-field uniqueness excluding soft-deleted rows | OK | — |
| [RULE-OPERACIONAL-INFRA-055](data-validation/RULE-OPERACIONAL-INFRA-055-popular-banco-gender-enum-synthetic-data.md) | popular_banco gender enum (synthetic data) | OK | — |
| [RULE-OPERACIONAL-INFRA-056](data-validation/RULE-OPERACIONAL-INFRA-056-diagnosis-list-checks-are-non-functional-vars-fromkeys-misus.md) | Diagnosis-list checks are non-functional (vars().fromkeys misuse) | DISCREPANCY | — |
| [RULE-OPERACIONAL-INFRA-057](data-validation/RULE-OPERACIONAL-INFRA-057-upload-to-model-type-based-storage-folder-convention.md) | upload_to — model-type-based storage folder convention | OK | — |
| [RULE-OPERACIONAL-INFRA-058](data-validation/RULE-OPERACIONAL-INFRA-058-verificar-setor-da-empresa-tenant-hierarchy-consistency-chec.md) | verificar_setor_da_empresa — tenant-hierarchy consistency check | OK | — |
| [RULE-OPERACIONAL-INFRA-060](data-validation/RULE-OPERACIONAL-INFRA-060-tasymodel-oracle-database-routing-reads-and-writes-forced-to.md) | TasyModel Oracle database routing (reads and writes forced to the 'oracle' connection) | OK | — |
| [RULE-OPERACIONAL-INFRA-061](data-validation/RULE-OPERACIONAL-INFRA-061-request-body-upload-size-cap-data-upload-max-memory-size-100.md) | Request-body upload size cap (DATA_UPLOAD_MAX_MEMORY_SIZE = 100 MiB) | OK | — |
| [RULE-PRESCRICAO-029](data-validation/RULE-PRESCRICAO-029-not-administered-reason-enum-motivo-nao-administrado.md) | Not-administered reason enum (motivo_nao_administrado) | DISCREPANCY | — |
| [RULE-PRESCRICAO-032](data-validation/RULE-PRESCRICAO-032-horario-de-prescricao-autor-padrao-sistema.md) | Horario de prescricao - autor padrao 'sistema' | OK | — |
| [RULE-PRESCRICAO-034](data-validation/RULE-PRESCRICAO-034-only-the-checking-user-may-cancel-a-scheduled-dose.md) | Only the checking user may cancel a scheduled dose | OK | — |
| [RULE-PRESCRICAO-035](data-validation/RULE-PRESCRICAO-035-non-administration-reason-validation-effectively-unreachable.md) | Non-administration reason validation (effectively unreachable guard) | DISCREPANCY | — |
| [RULE-PRESCRICAO-036](data-validation/RULE-PRESCRICAO-036-checagem-lock-cannot-alter-administration-status-once-set-un.md) | Checagem lock — cannot alter administration status once set (unused in this scope) | AMBIGUOUS | — |
| [RULE-PRESCRICAO-037](data-validation/RULE-PRESCRICAO-037-pharmacist-global-assessment-risks-with-dead-conditionals.md) | Pharmacist global assessment (risks with dead conditionals) | DISCREPANCY | — |
| [RULE-PRESCRICAO-039](data-validation/RULE-PRESCRICAO-039-pharmacist-intervention-vocabulary.md) | Pharmacist intervention vocabulary | OK | — |
| [RULE-PRESCRICAO-040](data-validation/RULE-PRESCRICAO-040-pharmacist-form-variable-file-naming-mismatch.md) | Pharmacist form variable/file naming mismatch | DISCREPANCY | — |
| [RULE-PRESCRICAO-041](data-validation/RULE-PRESCRICAO-041-prescricao-continua-day-filter.md) | Prescricao continua day filter | OK | — |
| [RULE-SEDACAO-027](data-validation/RULE-SEDACAO-027-unique-sedative-per-prontuario-dose-unit.md) | Unique sedative per prontuario + dose unit | OK | — |
| [RULE-SEPSE-068](data-validation/RULE-SEPSE-068-urea-field-encodes-an-unbounded-value-under-a-threshold-name.md) | Urea field encodes an unbounded value under a threshold name | AMBIGUOUS | — |
| [RULE-SEPSE-088](data-validation/RULE-SEPSE-088-empty-state-for-absent-sepsis-protocols.md) | Empty-state for absent sepsis protocols | OK | — |
| [RULE-SEPSE-098](data-validation/RULE-SEPSE-098-sepsis-checklist-signer-requires-cpf-unlike-other-checklist.md) | Sepsis-checklist signer requires CPF, unlike other checklist types | AMBIGUOUS | — |
| [RULE-SINAIS-VITAIS-006](data-validation/RULE-SINAIS-VITAIS-006-sinaisvitais-listing-includes-soft-deleted-records.md) | SinaisVitais listing includes soft-deleted records | DISCREPANCY | — |
| [RULE-SINAIS-VITAIS-008](data-validation/RULE-SINAIS-VITAIS-008-sinaisvitais-manage-data-payload-injection.md) | SinaisVitais manage_data payload injection | OK | — |
| [RULE-SINAIS-VITAIS-009](data-validation/RULE-SINAIS-VITAIS-009-porcentagemvalidator-generic-percentage-range.md) | PorcentagemValidator — generic percentage range | OK | — |
| [RULE-SINAIS-VITAIS-010](data-validation/RULE-SINAIS-VITAIS-010-fio2validator-inspired-oxygen-fraction-range-zero-exempted.md) | FiO2Validator — inspired oxygen fraction range, zero exempted | OK | — |
| [RULE-SINAIS-VITAIS-012](data-validation/RULE-SINAIS-VITAIS-012-peepvalidator-peep-range-no-zero-exemption.md) | PeepValidator — PEEP range, no zero exemption | OK | — |
| [RULE-SINAIS-VITAIS-013](data-validation/RULE-SINAIS-VITAIS-013-tecvalidator-capillary-refill-time-range-zero-exempted.md) | TecValidator — capillary refill time range, zero exempted | OK | — |
| [RULE-SINAIS-VITAIS-014](data-validation/RULE-SINAIS-VITAIS-014-po2validator-pao2-po2-range-no-zero-exemption.md) | Po2Validator — PaO2/PO2 range, no zero exemption | OK | — |
| [RULE-SINAIS-VITAIS-015](data-validation/RULE-SINAIS-VITAIS-015-frvalidator-respiratory-rate-range-no-zero-exemption.md) | FRValidator — respiratory rate range, no zero exemption | OK | — |
| [RULE-SINAIS-VITAIS-016](data-validation/RULE-SINAIS-VITAIS-016-lactatoarterialvalidator-arterial-lactate-range-no-zero-exem.md) | LactatoArterialValidator — arterial lactate range, no zero exemption | OK | — |
| [RULE-SINAIS-VITAIS-017](data-validation/RULE-SINAIS-VITAIS-017-volumecorrentevalidator-tidal-volume-range-no-zero-exemption.md) | VolumeCorrenteValidator — tidal volume range, no zero exemption | OK | — |
| [RULE-SINAIS-VITAIS-018](data-validation/RULE-SINAIS-VITAIS-018-pasvalidator-systolic-blood-pressure-range-zero-exempted.md) | PASValidator — systolic blood pressure range, zero exempted | OK | — |
| [RULE-SINAIS-VITAIS-019](data-validation/RULE-SINAIS-VITAIS-019-padvalidator-diastolic-blood-pressure-range-no-zero-exemptio.md) | PADValidator — diastolic blood pressure range, no zero exemption | OK | — |
| [RULE-SINAIS-VITAIS-020](data-validation/RULE-SINAIS-VITAIS-020-pamvalidator-mean-arterial-pressure-range-no-zero-exemption.md) | PAMValidator — mean arterial pressure range, no zero exemption (validator defined but disabled  | OK | — |
| [RULE-SINAIS-VITAIS-021](data-validation/RULE-SINAIS-VITAIS-021-debitourinario24hvalidator-24h-urine-output-range-no-zero-ex.md) | DebitoUrinario24hValidator — 24h urine output range, no zero exemption | OK | — |
| [RULE-SINAIS-VITAIS-022](data-validation/RULE-SINAIS-VITAIS-022-bilirrubinasvalidator-bilirubin-range-no-zero-exemption.md) | BilirrubinasValidator — bilirubin range, no zero exemption | OK | — |
| [RULE-SINAIS-VITAIS-023](data-validation/RULE-SINAIS-VITAIS-023-temperaturavalidator-body-temperature-range-zero-exempted.md) | TemperaturaValidator — body temperature range, zero exempted | OK | — |
| [RULE-SINAIS-VITAIS-024](data-validation/RULE-SINAIS-VITAIS-024-paco2validator-paco2-range-no-zero-exemption.md) | PaCO2Validator — PaCO2 range, no zero exemption | OK | — |
| [RULE-SINAIS-VITAIS-025](data-validation/RULE-SINAIS-VITAIS-025-creatininavalidator-creatinine-range-no-zero-exemption.md) | CreatininaValidator — creatinine range, no zero exemption | OK | — |
| [RULE-SINAIS-VITAIS-026](data-validation/RULE-SINAIS-VITAIS-026-leucocitosvalidator-leukocyte-count-range-no-zero-exemption.md) | LeucocitosValidator — leukocyte count range, no zero exemption | OK | — |
| [RULE-SINAIS-VITAIS-027](data-validation/RULE-SINAIS-VITAIS-027-frequenciacardiacavalidator-heart-rate-range-no-zero-exempti.md) | FrequenciaCardiacaValidator — heart rate range, no zero exemption | OK | — |
| [RULE-SINAIS-VITAIS-028](data-validation/RULE-SINAIS-VITAIS-028-plaquetasvalidator-platelet-count-range-no-zero-exemption.md) | PlaquetasValidator — platelet count range, no zero exemption | OK | — |
| [RULE-SINAIS-VITAIS-032](data-validation/RULE-SINAIS-VITAIS-032-pressaoinspiratoriavalidator-inspiratory-pressure-pins-range.md) | PressaoInspiratoriaValidator — inspiratory pressure (PINS) range, no zero exemption | OK | — |
| [RULE-SINAIS-VITAIS-033](data-validation/RULE-SINAIS-VITAIS-033-sato2validator-oxygen-saturation-range-no-zero-exemption-and.md) | SatO2Validator — oxygen saturation range, no zero exemption AND disabled on the model field | AMBIGUOUS | — |
| [RULE-TENANCY-ORGANIZACAO-009](data-validation/RULE-TENANCY-ORGANIZACAO-009-combined-setor-display-name.md) | Combined setor display name | OK | UNVERIFIABLE |
| [RULE-TENANCY-ORGANIZACAO-010](data-validation/RULE-TENANCY-ORGANIZACAO-010-atualizado-em-timestamp-floored-to-5-minute-buckets.md) | 'atualizado_em' timestamp floored to 5-minute buckets | OK | UNVERIFIABLE |
| [RULE-TENANCY-ORGANIZACAO-013](data-validation/RULE-TENANCY-ORGANIZACAO-013-sector-gender-counts-merge-manual-movements-with-automatic-p.md) | Sector gender counts merge manual movements with automatic-pathway beds | OK | UNVERIFIABLE |
| [RULE-TENANCY-ORGANIZACAO-014](data-validation/RULE-TENANCY-ORGANIZACAO-014-sector-chat-preview-picks-the-first-related-observation-with.md) | Sector chat preview picks the first related observation without explicit ordering | AMBIGUOUS | UNVERIFIABLE |
| [RULE-TENANCY-ORGANIZACAO-017](data-validation/RULE-TENANCY-ORGANIZACAO-017-empresamiddleware-path-based-empresa-tenant-resolution.md) | EmpresaMiddleware — path-based empresa (tenant) resolution | OK | — |
| [RULE-TENANCY-ORGANIZACAO-018](data-validation/RULE-TENANCY-ORGANIZACAO-018-estabelecimentomiddleware-path-based-estabelecimento-resolut.md) | EstabelecimentoMiddleware — path-based estabelecimento resolution + empresa cross-check | OK | — |
| [RULE-TENANCY-ORGANIZACAO-019](data-validation/RULE-TENANCY-ORGANIZACAO-019-setormiddleware-path-based-setor-resolution-dual-empresa-est.md) | SetorMiddleware — path-based setor resolution + dual empresa/estabelecimento cross-check | OK | — |
| [RULE-TENANCY-ORGANIZACAO-020](data-validation/RULE-TENANCY-ORGANIZACAO-020-leitomiddleware-path-based-leito-resolution-no-cross-tenant.md) | LeitoMiddleware — path-based leito resolution (no cross-tenant check) | AMBIGUOUS | — |
| [RULE-TENANCY-ORGANIZACAO-021](data-validation/RULE-TENANCY-ORGANIZACAO-021-sector-queryset-dual-non-exclusive-scoping-by-empresa-and-es.md) | Sector queryset dual (non-exclusive) scoping by empresa and estabelecimento | OK | — |
| [RULE-TENANCY-ORGANIZACAO-022](data-validation/RULE-TENANCY-ORGANIZACAO-022-establishment-queryset-optionally-scoped-to-parent-empresa.md) | Establishment queryset optionally scoped to parent empresa | OK | — |
| [RULE-TENANCY-ORGANIZACAO-023](data-validation/RULE-TENANCY-ORGANIZACAO-023-cascading-estabelecimento-then-setor-selection-gate.md) | Cascading estabelecimento-then-setor selection gate | OK | — |
| [RULE-TENANCY-ORGANIZACAO-024](data-validation/RULE-TENANCY-ORGANIZACAO-024-get-bypasses-can-manage-empresa-permission.md) | GET bypasses can_manage_empresa permission | OK | — |
| [RULE-TENANCY-ORGANIZACAO-029](data-validation/RULE-TENANCY-ORGANIZACAO-029-establishment-gender-alert-assisted-totals-branch-by-tipo-ma.md) | Establishment gender/alert/assisted totals branch by tipo (manual vs. other) | OK | — |
| [RULE-TENANCY-ORGANIZACAO-031](data-validation/RULE-TENANCY-ORGANIZACAO-031-establishment-action-fields-expose-camera-credentials-only-o.md) | Establishment action_fields expose camera credentials only on retrieve/partial_update | OK | — |
| [RULE-TENANCY-ORGANIZACAO-033](data-validation/RULE-TENANCY-ORGANIZACAO-033-establishment-chats-action-lists-only-sectors-the-user-belon.md) | Establishment chats action lists only sectors the user belongs to | OK | — |
| [RULE-TENANCY-ORGANIZACAO-034](data-validation/RULE-TENANCY-ORGANIZACAO-034-sector-patient-gender-totals-branch-by-tipo-manual-vs-automa.md) | Sector patient/gender totals branch by tipo (manual vs. automatic/homecare) | OK | — |
| [RULE-TENANCY-ORGANIZACAO-040](data-validation/RULE-TENANCY-ORGANIZACAO-040-company-logo-base64-conversion-on-update.md) | Company logo base64 conversion on update | OK | — |
| [RULE-TENANCY-ORGANIZACAO-045](data-validation/RULE-TENANCY-ORGANIZACAO-045-access-group-exactly-one-scope-constraint-three-xor.md) | Access-group exactly-one-scope constraint (three_xor) | OK | — |
| [RULE-TENANCY-ORGANIZACAO-046](data-validation/RULE-TENANCY-ORGANIZACAO-046-grupo-estabelecimento-scoped-member-search.md) | Grupo/estabelecimento-scoped member search | OK | — |
| [RULE-TENANCY-ORGANIZACAO-048](data-validation/RULE-TENANCY-ORGANIZACAO-048-company-field-constraints-primary-color-length-refresh-inter.md) | Company field constraints (primary color length, refresh interval) | OK | — |
| [RULE-TENANCY-ORGANIZACAO-049](data-validation/RULE-TENANCY-ORGANIZACAO-049-company-logo-field-rename-with-silent-drop-for-non-string-va.md) | Company logo field rename with silent drop for non-string values | DISCREPANCY | — |
| [RULE-TENANCY-ORGANIZACAO-050](data-validation/RULE-TENANCY-ORGANIZACAO-050-undefinedmiddleware-reject-literal-undefined-in-url-path.md) | UndefinedMiddleware — reject literal 'undefined' in URL path | OK | — |
| [RULE-TENANCY-ORGANIZACAO-051](data-validation/RULE-TENANCY-ORGANIZACAO-051-acaohomecare-tenant-scoping.md) | AcaoHomecare tenant scoping | OK | — |
| [RULE-TENANCY-ORGANIZACAO-052](data-validation/RULE-TENANCY-ORGANIZACAO-052-multi-tenant-data-scoping-by-sector-establishment.md) | Multi-tenant data scoping by sector/establishment | OK | — |
| [RULE-VENTILACAO-025](data-validation/RULE-VENTILACAO-025-ventilacaomecanica-ventilation-device-modality-enumerations.md) | VentilacaoMecanica ventilation / device / modality enumerations (backend model + frontend movim | DISCREPANCY | — |
| [RULE-VENTILACAO-026](data-validation/RULE-VENTILACAO-026-nursing-ventilation-secretion-assessment-enums-avaliacao-ven.md) | Nursing ventilation / secretion assessment enums (avaliacao_ventilacao) | OK | — |

### scheduling-operational (66 rules)

Scheduling cadences, shift boundaries (07:00), retention, deployment/runtime policies

| Rule | Name | Status | Verdict |
|---|---|---|---|
| [RULE-BALANCO-HIDRICO-037](scheduling-operational/RULE-BALANCO-HIDRICO-037-daily-fluid-balance-auto-creation-for-occupied-homecare-beds.md) | Daily fluid-balance auto-creation for occupied homecare beds | OK | — |
| [RULE-COMUNICACAO-017](scheduling-operational/RULE-COMUNICACAO-017-notification-fan-out-to-all-sector-users-on-creation.md) | Notification fan-out to all sector users on creation | OK | — |
| [RULE-COMUNICACAO-018](scheduling-operational/RULE-COMUNICACAO-018-record-interaction-indicator-on-first-notification-view.md) | Record interaction indicator on first notification view | OK | — |
| [RULE-COMUNICACAO-019](scheduling-operational/RULE-COMUNICACAO-019-observation-auto-creates-a-notification-and-routes-by-target.md) | Observation auto-creates a notification and routes by target | OK | — |
| [RULE-COMUNICACAO-025](scheduling-operational/RULE-COMUNICACAO-025-feed-pagination-thresholds.md) | Feed pagination thresholds | OK | — |
| [RULE-COMUNICACAO-029](scheduling-operational/RULE-COMUNICACAO-029-video-call-auto-leaves-on-route-change.md) | Video call auto-leaves on route change | OK | — |
| [RULE-COMUNICACAO-030](scheduling-operational/RULE-COMUNICACAO-030-single-join-guard-and-forced-reload-after-leaving-a-call.md) | Single-join guard and forced reload after leaving a call | OK | — |
| [RULE-COMUNICACAO-031](scheduling-operational/RULE-COMUNICACAO-031-video-call-room-exit-confirmation-guard.md) | Video-call room exit confirmation guard | OK | — |
| [RULE-COMUNICACAO-037](scheduling-operational/RULE-COMUNICACAO-037-one-reaction-per-user-per-observation-unread-counter-side-ef.md) | One reaction per user per observation + unread-counter side effect | OK | — |
| [RULE-COMUNICACAO-044](scheduling-operational/RULE-COMUNICACAO-044-video-call-online-presence-flag-derivation.md) | Video-call online-presence flag derivation | OK | — |
| [RULE-DOCUMENTACAO-FATURAMENTO-006](scheduling-operational/RULE-DOCUMENTACAO-FATURAMENTO-006-prescricao-pdf-export-priority-ordering-and-soft-delete-excl.md) | Prescricao PDF export - priority ordering and soft-delete exclusion | OK | — |
| [RULE-EFICIENCIA-007](scheduling-operational/RULE-EFICIENCIA-007-eficiencia-v3-criterio-1-repeated-exams-within-minimum-repea.md) | Eficiencia v3 criterio_1 - repeated exams within minimum-repeat windows (defined, unwired) | OK | — |
| [RULE-FORMULARIOS-CLINICOS-043](scheduling-operational/RULE-FORMULARIOS-CLINICOS-043-invasive-device-dressing-and-exchange-scheduling.md) | Invasive-device dressing and exchange scheduling | OK | — |
| [RULE-INDICADORES-ETL-013](scheduling-operational/RULE-INDICADORES-ETL-013-incremental-watermark-load-of-occupancy-indicators.md) | Incremental (watermark) load of occupancy indicators | OK | — |
| [RULE-INDICADORES-ETL-014](scheduling-operational/RULE-INDICADORES-ETL-014-macro-indicators-loaded-for-current-month-only.md) | Macro indicators loaded for current month only | OK | — |
| [RULE-INDICADORES-ETL-017](scheduling-operational/RULE-INDICADORES-ETL-017-sector-occupancy-dashboard-auto-reload-interval.md) | Sector occupancy dashboard auto-reload interval | OK | — |
| [RULE-MOVIMENTACAO-ADT-009](scheduling-operational/RULE-MOVIMENTACAO-ADT-009-fixed-3h-display-offset-for-prontuario-timestamps.md) | Fixed -3h display offset for prontuario timestamps | DISCREPANCY | DISCREPANCY (low) |
| [RULE-MOVIMENTACAO-ADT-013](scheduling-operational/RULE-MOVIMENTACAO-ADT-013-patient-assisted-resolution-across-pathways-movimentacao.md) | Patient 'assisted' resolution across pathways (movimentacao) | OK | — |
| [RULE-MOVIMENTACAO-ADT-024](scheduling-operational/RULE-MOVIMENTACAO-ADT-024-homecare-occupancy-access-filtering.md) | Homecare occupancy access filtering | OK | — |
| [RULE-MOVIMENTACAO-ADT-039](scheduling-operational/RULE-MOVIMENTACAO-ADT-039-prontuario-lookback-chain-buscar-ultimos-dados.md) | Prontuario lookback chain (buscar_ultimos_dados) | OK | — |
| [RULE-MOVIMENTACAO-ADT-040](scheduling-operational/RULE-MOVIMENTACAO-ADT-040-batch-recompute-of-current-movimentacoes-trilhas-celery-task.md) | Batch recompute of current movimentacoes' trilhas (Celery task) | OK | — |
| [RULE-OPERACIONAL-INFRA-001](scheduling-operational/RULE-OPERACIONAL-INFRA-001-round-timestamp-to-whole-hour-get-hora-cheia-justoclock.md) | Round timestamp to whole hour (get_hora_cheia / justOclock) | DISCREPANCY | DISCREPANCY (low) |
| [RULE-OPERACIONAL-INFRA-004](scheduling-operational/RULE-OPERACIONAL-INFRA-004-continuous-prescription-real-day-rolls-over-at-07-00-shift-b.md) | Continuous prescription 'real day' rolls over at 07:00 (shift boundary) | OK | UNVERIFIABLE |
| [RULE-OPERACIONAL-INFRA-005](scheduling-operational/RULE-OPERACIONAL-INFRA-005-offline-prescriptions-windowed-to-the-last-3-days-ordered-by.md) | Offline prescriptions windowed to the last 3 days, ordered by day then item-type priority | OK | UNVERIFIABLE |
| [RULE-OPERACIONAL-INFRA-006](scheduling-operational/RULE-OPERACIONAL-INFRA-006-length-of-stay-tempo-permanencia-computed-property.md) | Length of stay (TEMPO_PERMANENCIA) computed property | OK | UNVERIFIABLE |
| [RULE-OPERACIONAL-INFRA-007](scheduling-operational/RULE-OPERACIONAL-INFRA-007-pagination-page-count-and-default-page-size.md) | Pagination page-count and default page size | OK | UNVERIFIABLE |
| [RULE-OPERACIONAL-INFRA-008](scheduling-operational/RULE-OPERACIONAL-INFRA-008-minutes-elapsed-between-two-dates.md) | Minutes elapsed between two dates | OK | UNVERIFIABLE |
| [RULE-OPERACIONAL-INFRA-014](scheduling-operational/RULE-OPERACIONAL-INFRA-014-android-twa-digital-asset-links-restricted-to-a-single-homol.md) | Android TWA Digital Asset Links restricted to a single homol package | DISCREPANCY | — |
| [RULE-OPERACIONAL-INFRA-016](scheduling-operational/RULE-OPERACIONAL-INFRA-016-evolution-formulario-full-day-date-range-filter.md) | Evolution (Formulario) full-day date-range filter | OK | — |
| [RULE-OPERACIONAL-INFRA-025](scheduling-operational/RULE-OPERACIONAL-INFRA-025-per-queue-celery-worker-concurrency-assignment-serialize-pat.md) | Per-queue Celery worker concurrency assignment (serialize pathway-mutating queues) | OK | — |
| [RULE-OPERACIONAL-INFRA-026](scheduling-operational/RULE-OPERACIONAL-INFRA-026-start-sh-production-branch-references-a-uwsgi-ini-file-absen.md) | start.sh production branch references a uwsgi ini file absent from the repository | DISCREPANCY | — |
| [RULE-OPERACIONAL-INFRA-027](scheduling-operational/RULE-OPERACIONAL-INFRA-027-environment-classification-from-base-url.md) | Environment classification from base URL | OK | — |
| [RULE-OPERACIONAL-INFRA-028](scheduling-operational/RULE-OPERACIONAL-INFRA-028-pagination-control-disabled-when-everything-fits-on-one-page.md) | Pagination control disabled when everything fits on one page | OK | — |
| [RULE-OPERACIONAL-INFRA-029](scheduling-operational/RULE-OPERACIONAL-INFRA-029-shift-day-turno-calendar-date-assignment.md) | Shift-day (turno) calendar-date assignment | OK | — |
| [RULE-OPERACIONAL-INFRA-030](scheduling-operational/RULE-OPERACIONAL-INFRA-030-shared-default-search-result-limit-and-debounce-interval.md) | Shared default search-result limit and debounce interval | OK | — |
| [RULE-OPERACIONAL-INFRA-031](scheduling-operational/RULE-OPERACIONAL-INFRA-031-createsearchinput-overrides-configured-limit-to-5-on-empty-k.md) | CreateSearchInput overrides configured limit to 5 on empty keyword | DISCREPANCY | — |
| [RULE-OPERACIONAL-INFRA-033](scheduling-operational/RULE-OPERACIONAL-INFRA-033-tempo-atualizacao-trilhas-automatic-pathway-recalculation-ca.md) | TEMPO_ATUALIZACAO_TRILHAS — automatic pathway recalculation cadence | OK | — |
| [RULE-OPERACIONAL-INFRA-034](scheduling-operational/RULE-OPERACIONAL-INFRA-034-shift-turnover-virada-de-turno-cutoff-for-date-navigation.md) | Shift-turnover (virada de turno) cutoff for date navigation | OK | — |
| [RULE-OPERACIONAL-INFRA-035](scheduling-operational/RULE-OPERACIONAL-INFRA-035-data-7-as-7-7am-to-7am-shift-reporting-day-boundary.md) | data_7_as_7 — 7am-to-7am shift/reporting-day boundary | OK | — |
| [RULE-OPERACIONAL-INFRA-038](scheduling-operational/RULE-OPERACIONAL-INFRA-038-pwa-service-worker-generation-disabled-only-in-local-develop.md) | PWA service-worker generation disabled only in local development | OK | — |
| [RULE-OPERACIONAL-INFRA-039](scheduling-operational/RULE-OPERACIONAL-INFRA-039-pm2-multi-environment-process-configuration.md) | PM2 multi-environment process configuration | OK | — |
| [RULE-OPERACIONAL-INFRA-040](scheduling-operational/RULE-OPERACIONAL-INFRA-040-per-environment-deploy-script-workflow-with-asymmetric-env-f.md) | Per-environment deploy script workflow with asymmetric env-file loading | AMBIGUOUS | — |
| [RULE-OPERACIONAL-INFRA-041](scheduling-operational/RULE-OPERACIONAL-INFRA-041-environment-secret-files-excluded-from-version-control-per-d.md) | Environment secret files excluded from version control per deploy target | OK | — |
| [RULE-OPERACIONAL-INFRA-042](scheduling-operational/RULE-OPERACIONAL-INFRA-042-pwa-app-identity-and-installed-app-display-behavior.md) | PWA app identity and installed-app display behavior | OK | — |
| [RULE-OPERACIONAL-INFRA-044](scheduling-operational/RULE-OPERACIONAL-INFRA-044-assistido-flag-reset-1-minute-update-window.md) | Assistido flag reset - 1-minute update window | OK | — |
| [RULE-OPERACIONAL-INFRA-045](scheduling-operational/RULE-OPERACIONAL-INFRA-045-interactive-sepsis-overdue-item-auto-check-and-alert-message.md) | Interactive sepsis - overdue item auto-check and alert message | OK | — |
| [RULE-OPERACIONAL-INFRA-046](scheduling-operational/RULE-OPERACIONAL-INFRA-046-celery-queue-naming-convention-environment-namespaced-routin.md) | Celery queue naming convention — environment-namespaced routing keys | OK | — |
| [RULE-OPERACIONAL-INFRA-047](scheduling-operational/RULE-OPERACIONAL-INFRA-047-celery-beat-scheduler-databasescheduler-with-a-duplicate-bea.md) | Celery beat scheduler — DatabaseScheduler, with a duplicate-beat-daemon discrepancy in demo/leg | DISCREPANCY | — |
| [RULE-OPERACIONAL-INFRA-048](scheduling-operational/RULE-OPERACIONAL-INFRA-048-backend-ci-gate-covers-only-trilha-manual-tests.md) | Backend CI gate covers only trilha_manual tests | OK | — |
| [RULE-OPERACIONAL-INFRA-049](scheduling-operational/RULE-OPERACIONAL-INFRA-049-nursing-shift-day-window-07-00-07-00.md) | Nursing-shift day window 07:00-07:00 | OK | — |
| [RULE-OPERACIONAL-INFRA-052](scheduling-operational/RULE-OPERACIONAL-INFRA-052-observation-by-bed-includes-replies-to-that-bed.md) | Observation-by-bed includes replies to that bed | OK | — |
| [RULE-OPERACIONAL-INFRA-059](scheduling-operational/RULE-OPERACIONAL-INFRA-059-per-company-auto-refresh-interval-field.md) | Per-company auto-refresh interval field | AMBIGUOUS | — |
| [RULE-OPERACIONAL-INFRA-062](scheduling-operational/RULE-OPERACIONAL-INFRA-062-per-environment-uwsgi-worker-capacity-and-recycling-threshol.md) | Per-environment uWSGI worker capacity and recycling thresholds | OK | — |
| [RULE-PRESCRICAO-004](scheduling-operational/RULE-PRESCRICAO-004-prescription-day-boundary-rule-for-exporting-a-dose-quantity.md) | Prescription day-boundary rule for exporting a dose quantity into fluid balance | OK | — |
| [RULE-PRESCRICAO-005](scheduling-operational/RULE-PRESCRICAO-005-07-00-shift-boundary-reordering-of-scheduled-dose-times-for.md) | 07:00 shift-boundary reordering of scheduled dose times for display | OK | — |
| [RULE-PRESCRICAO-007](scheduling-operational/RULE-PRESCRICAO-007-prescription-item-type-priority-ordering-5-tier.md) | Prescription-item type priority ordering (5-tier) | DISCREPANCY | — |
| [RULE-PRESCRICAO-020](scheduling-operational/RULE-PRESCRICAO-020-geracao-de-horarios-a-partir-de-ds-horarios.md) | Geracao de horarios a partir de DS_HORARIOS | OK | — |
| [RULE-PRESCRICAO-021](scheduling-operational/RULE-PRESCRICAO-021-bulk-medication-administration-checkoff-multi-checagem.md) | Bulk medication-administration checkoff (multi_checagem) | OK | — |
| [RULE-PRESCRICAO-022](scheduling-operational/RULE-PRESCRICAO-022-horario-prescricao-manage-data-payload-injection.md) | Horario prescricao manage_data payload injection | OK | — |
| [RULE-PRESCRICAO-027](scheduling-operational/RULE-PRESCRICAO-027-antibiotic-course-tracking-list-with-malformed-field.md) | Antibiotic course tracking list (with malformed field) | DISCREPANCY | — |
| [RULE-PRESCRICAO-033](scheduling-operational/RULE-PRESCRICAO-033-horario-prescricao-scoped-to-parent-prescricao-continua.md) | Horario prescricao scoped to parent prescricao continua | OK | — |
| [RULE-SEPSE-069](scheduling-operational/RULE-SEPSE-069-bundle-item-overdue-atraso-item-interativa-time-windows.md) | Bundle item overdue (atraso_item_interativa) time windows | OK | VERIFIED |
| [RULE-SEPSE-070](scheduling-operational/RULE-SEPSE-070-bundle-item-visibility-exibir-reassessment-appears-after-2h.md) | Bundle item visibility (exibir) - reassessment appears after 2h | OK | — |
| [RULE-TENANCY-ORGANIZACAO-043](scheduling-operational/RULE-TENANCY-ORGANIZACAO-043-auto-refresh-polling-interval-driven-by-company-setting-empr.md) | Auto-refresh polling interval driven by company setting (empresa dashboard) | OK | — |
| [RULE-TENANCY-ORGANIZACAO-044](scheduling-operational/RULE-TENANCY-ORGANIZACAO-044-auto-refresh-polling-interval-driven-by-company-setting-esta.md) | Auto-refresh polling interval driven by company setting (estabelecimento dashboard) | OK | — |
| [RULE-TRILHAS-ENGINE-010](scheduling-operational/RULE-TRILHAS-ENGINE-010-automatica-facade-active-payload-variant-selection-per-trilh.md) | Automatica facade — active payload variant selection per trilha | OK | — |

### access-control (16 rules)

Authentication, authorization, permission cascades, tenancy scoping (taxonomy extension)

| Rule | Name | Status | Verdict |
|---|---|---|---|
| [RULE-AUTH-USUARIOS-003](access-control/RULE-AUTH-USUARIOS-003-super-admin-chatbot-permission-predicate.md) | Super-admin (chatbot) permission predicate | OK | — |
| [RULE-AUTH-USUARIOS-004](access-control/RULE-AUTH-USUARIOS-004-partner-required-permission-predicate.md) | Partner-required permission predicate | OK | — |
| [RULE-AUTH-USUARIOS-005](access-control/RULE-AUTH-USUARIOS-005-owner-organization-object-permission-predicate.md) | Owner-organization object permission predicate | OK | — |
| [RULE-AUTH-USUARIOS-006](access-control/RULE-AUTH-USUARIOS-006-authenticated-user-predicate-isauthenticated.md) | Authenticated-user predicate (IsAuthenticated) | OK | — |
| [RULE-AUTH-USUARIOS-007](access-control/RULE-AUTH-USUARIOS-007-empresa-read-vs-read-write-permissions-are-identical.md) | Empresa read vs read-write permissions are identical | DISCREPANCY | — |
| [RULE-AUTH-USUARIOS-008](access-control/RULE-AUTH-USUARIOS-008-hierarchical-permission-cascade-get-permissoes-empresa-estab.md) | Hierarchical permission cascade (get_permissoes_empresa/estabelecimento/setor) | OK | — |
| [RULE-AUTH-USUARIOS-024](access-control/RULE-AUTH-USUARIOS-024-post-login-company-selection-redirect-decision-tree.md) | Post-login company-selection redirect decision tree | OK | — |
| [RULE-AUTH-USUARIOS-027](access-control/RULE-AUTH-USUARIOS-027-admin-sidebar-menu-item-visibility-gating.md) | Admin sidebar menu-item visibility gating | OK | — |
| [RULE-AUTH-USUARIOS-028](access-control/RULE-AUTH-USUARIOS-028-per-professional-evolution-form-authoring-eligibility.md) | Per-professional evolution-form authoring eligibility | OK | — |
| [RULE-AUTH-USUARIOS-041](access-control/RULE-AUTH-USUARIOS-041-session-cookie-lifetimes-and-token-verify-refresh-workflow.md) | Session cookie lifetimes and token verify/refresh workflow | OK | — |
| [RULE-AUTH-USUARIOS-042](access-control/RULE-AUTH-USUARIOS-042-effective-permission-intersection-computation.md) | Effective-permission intersection computation | OK | — |
| [RULE-AUTH-USUARIOS-057](access-control/RULE-AUTH-USUARIOS-057-authorization-header-format.md) | Authorization header format | OK | — |
| [RULE-AUTH-USUARIOS-058](access-control/RULE-AUTH-USUARIOS-058-rbac-permission-catalog.md) | RBAC permission catalog | OK | — |
| [RULE-AUTH-USUARIOS-059](access-control/RULE-AUTH-USUARIOS-059-access-group-aggregates-the-full-permission-map.md) | Access group aggregates the full permission map | OK | — |
| [RULE-AUTH-USUARIOS-061](access-control/RULE-AUTH-USUARIOS-061-context-switch-destinations-exclude-bed-level.md) | Context-switch destinations exclude bed level | OK | — |
| [RULE-AUTH-USUARIOS-063](access-control/RULE-AUTH-USUARIOS-063-shared-default-signing-pin-usuario-pin-defaults-to-settings.md) | Shared default signing PIN (Usuario.pin defaults to settings.PIN_DEFAULT) | OK | — |

## Clusters

Rules were reconciled in 27 domain clusters (the `Cluster` field): `sepse` (99), `evolucoes` (77), `movimentacao-adt` (70), `auth-usuarios` (63), `balanco-hidrico` (62), `operacional-infra` (62), `tenancy-organizacao` (52), `comunicacao` (46), `formularios-clinicos` (45), `prescricao` (41), `auditoria-logs` (36), `sinais-vitais` (33), `documentacao-faturamento` (32), `alertas` (29), `indicadores-etl` (27), `sedacao` (27), `estabilidade` (26), `ventilacao` (26), `cadastros-ui` (20), `clinical-scoring` (18), `trilhas-engine` (18), `eficiencia` (12), `piora-clinica` (12), `nutricao` (11), `profilaxia` (8), `equilibrio` (4), `antimicrobiano` (3).
