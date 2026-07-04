# RULE-PIORA-CLINICA-011 — Piora Clinica - Payload de alertas/recomendacoes/intervencoes por (criterio, codigo de severidade)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | workflow |
| Status | AMBIGUOUS |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | piora-clinica |

## Rule
Facade payload (payload_trilha_piora_clinica) mapping each (criterio_1..9, severity-code) pair to a UI alert label, clinical recomendacoes, and clinical intervencoes. Severity codes: "2" = moderate (AMARELO), "3" = high/alto (VERMELHO); trailing "+" = high-value deviation, "-" = low-value deviation. Several labels embed explicit vital-sign thresholds (temperature, blood pressure) and the interventions carry the actionable clinical protocol (fluid challenge, antipyretic route, sepsis-protocol trigger).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| criterio index (1-9) | int | — | 1-9 |
| severity code | enum | — | 2+,2-,3+,3- |

## Outputs
| Name | Type | Unit |
|---|---|---|
| alerta | string | — |
| recomendacoes | list[string] | — |
| intervencoes | list[string] | — |

## Logic
```text
# payload_trilha_piora_clinica[criterio_key][severity_code] -> {alerta, recomendacoes, intervencoes}
criterio_1 (freq. respiratoria): 3+ = "taquipneia grave" (ALTO); 3- = "bradipneia" (ALTO).
criterio_2 (temperatura):        2+ = "febre baixa"  TAX 38 - 38,2C (MODERADO);
                                 3+ = "febre alta"   TAX >38,2C     (ALTO);
                                 3- = "hipotermia"   TAX <35C       (ALTO).
criterio_3 (pressao arterial):   2- = "hipotensao"          PAS 81-99 mmHg  (MODERADO);
                                 2+ = "hipertensao moderada" PAS 150-189 mmHg (MODERADO);
                                 3- = "hipotensao grave"    PAS <80 mmHg    (ALTO);   # code uses pas<=80
                                 3+ = "hipertensao grave"   PAS >189 mmHg   (ALTO).
criterio_4 (freq. cardiaca):     2+ taquicardia moderada; 3+ taquicardia grave; 3- bradicardia.
criterio_5 (consciencia):        2+ reage/responde ao estimulo tatil; 2- agitacao/confusao;
                                 3- convulsao; 3+ nao responde/reage.
criterio_6 (dor - escala numerica):     2+ dor moderada; 3+ dor intensa.
criterio_7 (dor - escala comportamental): 2+ dor moderada; 3+ dor intensa.
criterio_8 (saturacao, regular): 2- dessaturacao moderada; 2+ hiperoxia; 3- dessaturacao grave.
criterio_9 (saturacao, DPOC):    2- dessaturacao moderada; 3+ hiperoxia; 3- dessaturacao grave.
# Only criterio_1..3 carry non-empty recomendacoes/intervencoes; criterio_4..9 are label-only.
# Interventions include: escalate to Pronto Atendimento on new motor deficit / pupillary change
# / chest pain; fluid challenge Ringer Lactato 500ml (PAS 81-99) or 1000ml (PAS<80); antipyretic
# enteral (VO/SNE/GTT) for febre baixa, IV antipyretic for febre alta; open SEPSE protocol on
# organ dysfunction; enteral antihypertensive reassessed at 1h.
```

## Edge cases (as implemented)
criterio_4 through criterio_9 have EMPTY recomendacoes and intervencoes (label only). AMBIGUOUS labelling: criterio_8/criterio_9 saturation sub-levels use "Alto risco" wording even for the grade-2 codes (2-/2+), which are nominally "Moderado" - reproduced verbatim, treat labels as authoritative. criterio_1 3+ (taquipneia grave) intervencoes text erroneously says "causa base da bradipnea" (copy-paste from the 3- bradipneia entry) - verbatim.

## Divergence
Facade-label vs predicate-code divergence for criterio_3 grade 3-: the label reads "hipotenso (PAS <80 mmHg)" but the scoring predicate RULE-PIORA-CLINICA-003 uses `pas <= 80`, so PAS = 80 scores 3- in code but is described as excluded by the label. Boundary-only, documentation-level (the label string does not execute); code is authoritative. All other embedded thresholds match the predicates (TAX 38-38.2 / >38.2 / <35; PAS 81-99 / 150-189 / >189).

## Verification
- Verdict: UNVERIFIABLE
- Reference: Composite anchors (no single authoritative source governs the exact payload text). (1) Evans L, et al. Surviving Sepsis Campaign: International Guidelines for Management of Sepsis and Septic Shock 2021. Crit Care Med 2021;49(11):e1063-e1143 — >=30 mL/kg IV crystalloid within first 3h for sepsis-induced hypoperfusion (weak rec), balanced crystalloid preferred, open sepsis pathway on organ dysfunction (Sepsis-3). (2) Standard fluid-challenge practice: ~500 mL crystalloid bolus triggered by hypotension (LITFL / Messina et al. Ann Intensive Care systematic review 2022).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/facade/piora_clinica.py | 1-262 | 8166c07e | primary |
| ahlabs-trilhas | trilha_homecare/facade/piora_clinica.py | 1-3 | 8166c07e | duplicate |
- Merged from: RULE-piora-BE-01-004
- Related rules: RULE-PIORA-CLINICA-001, RULE-PIORA-CLINICA-002, RULE-PIORA-CLINICA-003, RULE-PIORA-CLINICA-004, RULE-PIORA-CLINICA-005, RULE-PIORA-CLINICA-006, RULE-PIORA-CLINICA-007, RULE-PIORA-CLINICA-008, RULE-PIORA-CLINICA-009, RULE-PIORA-CLINICA-010

## Notes
Phase-1 typed this "scoring"; reclassified to type=workflow because it is the action/label payload layer (recommendations + interventions), not a computation. Status upgraded OK -> AMBIGUOUS for the saturation "Alto risco"/grade-2 wording inconsistency plus the PAS <80 label imprecision. trilha_homecare/facade/piora_clinica.py exposes the SAME object via `payload_piora_clinica_homecare = payload_trilha_piora_clinica` (alias, byte-identical, no divergence). Consumed by trilha_homecare/models/piora_clinica.py get_detalhe(), which surfaces only criterio_1..3. verify=true: embedded vital-sign thresholds plus interventions (Ringer fluid-resuscitation volumes, SEPSE-protocol trigger on organ dysfunction) have plausible published clinical anchors (Surviving Sepsis Campaign / early-warning escalation).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
