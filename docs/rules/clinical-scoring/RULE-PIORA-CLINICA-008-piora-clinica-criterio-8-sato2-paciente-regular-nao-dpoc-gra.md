# RULE-PIORA-CLINICA-008 — Piora Clinica criterio_8 - SatO2 (paciente regular / nao-DPOC) (graded sub-score)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | scoring |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | medium |
| Cluster | piora-clinica |

## Rule
Graded oxygen-saturation sub-score for a "regular" (non-COPD) patient.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| sinais_vitais.saturacao_o2 | float | percent | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_8 | enum | — |

## Logic
```text
pontuacao = "0"
sato2 = sinais_vitais.saturacao_o2
if sato2:
    if   sato2 >  96      : pontuacao = "2+"
    elif 91 <= sato2 <= 93: pontuacao = "1-"
    elif 88 <= sato2 <= 90: pontuacao = "2-"
    elif      sato2 <= 88 : pontuacao = "3-"
return pontuacao
```

## Edge cases (as implemented)
Gap 94..96 -> "0". sato2 == 88 resolves to "2-" (matches 88 <= sato2 <= 90 before sato2 <= 88). sato2 == 0 falsy -> "0".

## Verification
- Verdict: DISCREPANCY (impact: moderate)
- Reference: NEWS2 (Royal College of Physicians, 2017) SpO2 Scale 1 (default, non-hypercapnic patients): >=96% = 0, 94-95% = 1, 92-93% = 2, <=91% = 3. High saturation is NOT penalized on Scale 1; points accrue only for hypoxaemia (supplemental O2 scores separately +2, not the saturation value itself).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/piora_clinica.py | 191-203 | 8166c07e | primary |
- Merged from: RULE-piora-BE-06-008
- Related rules: RULE-PIORA-CLINICA-009, RULE-PIORA-CLINICA-010, RULE-PIORA-CLINICA-011

## Notes
DISCREPANCY (internal, preserved verbatim): sato2 > 96 (a normal/high saturation) yields a positive deterioration score "2+", clinically inverted for a regular patient. Structurally coupled to RULE-PIORA-CLINICA-009: BOTH read the SAME saturacao_o2 field and are BOTH summed into the aggregate with no mutual exclusivity between regular/DPOC pathways, effectively double-weighting SpO2. Facade RULE-PIORA-CLINICA-011 labels 2+ "hiperoxia", 2- "dessaturacao moderada", 3- "dessaturacao grave" (all prefixed "Alto risco" - see 011 note).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
