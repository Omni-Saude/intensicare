# RULE-PIORA-CLINICA-009 — Piora Clinica criterio_9 - SatO2 (paciente DPOC/COPD) (graded sub-score)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | scoring |
| Status | OK |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | high |
| Cluster | piora-clinica |

## Rule
Graded oxygen-saturation sub-score for a COPD (DPOC) patient, where high SpO2 is penalized (over-oxygenation risk).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| sinais_vitais.saturacao_o2 | float | percent | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_9 | enum | — |

## Logic
```text
pontuacao = "0"
sato2 = sinais_vitais.saturacao_o2
if sato2:
    if   sato2 == 94     : pontuacao = "1+"
    elif sato2 >  94     : pontuacao = "3+"
    elif 91 <= sato2 <= 93: pontuacao = "1-"
    elif 88 <= sato2 <= 90: pontuacao = "2-"
    elif      sato2 <= 80 : pontuacao = "3-"
return pontuacao
```

## Edge cases (as implemented)
Gap 81..87 -> "0". sato2 == 94 -> "1+", >94 -> "3+". sato2 == 88 -> "2-". <=80 -> "3-". sato2 == 0 falsy -> "0".

## Verification
- Verdict: DISCREPANCY (impact: moderate)
- Reference: NEWS2 (Royal College of Physicians, 2017) SpO2 Scale 2, for hypercapnic (type 2) respiratory failure / COPD, target 88-92%: <=83% = 3, 84-85% = 2, 86-87% = 1, 88-92% (or >=93% on air) = 0, 93-94% on oxygen = 1, 95-96% on oxygen = 2, >=97% on oxygen = 3. High saturation IS penalized (over-oxygenation is dangerous in these patients).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/piora_clinica.py | 205-219 | 8166c07e | primary |
- Merged from: RULE-piora-BE-06-009
- Related rules: RULE-PIORA-CLINICA-008, RULE-PIORA-CLINICA-010, RULE-PIORA-CLINICA-011

## Notes
Penalizing high SpO2 (>94 -> 3+) is intentional for COPD. Gap 81-87 scores 0. Shares saturacao_o2 with criterio_8 (both summed together; see RULE-PIORA-CLINICA-008). Facade RULE-PIORA-CLINICA-011 labels 3+ "hiperoxia", 2- "dessaturacao moderada", 3- "dessaturacao grave".

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
