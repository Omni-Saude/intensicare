# RULE-PIORA-CLINICA-004 — Piora Clinica criterio_4 - Frequencia cardiaca (FC) (graded sub-score)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | scoring |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: low |
| Confidence | high |
| Cluster | piora-clinica |

## Rule
Graded heart-rate sub-score.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| sinais_vitais.frequencia_cardiaca | int | bpm | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_4 | enum | — |

## Logic
```text
pontuacao = "0"
fc = sinais_vitais.frequencia_cardiaca
if fc:
    if   101 <= fc <= 120: pontuacao = "1+"
    elif 121 <= fc <= 130: pontuacao = "2+"
    elif        fc >  130: pontuacao = "3+"
    elif  50 <= fc <=  59: pontuacao = "1-"
    # elif 81 <= fc <= 99: pontuacao = "2-"   # commented out / disabled in source
    elif        fc <=  50: pontuacao = "3-"
return pontuacao
```

## Edge cases (as implemented)
Gap 60..100 -> "0". fc == 0 falsy -> "0". fc == 50 matches "50 <= fc <= 59" (1-) first, so 50 -> "1-" (never "3-") due to branch order.

## Verification
- Verdict: DISCREPANCY (impact: low)
- Reference: Royal College of Physicians NEWS2 (2017) pulse band as family anchor. The verdict targets INTERNAL defects (disabled 2- band and branch-order shadowing) independent of the external reference.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/piora_clinica.py | 131-147 | 8166c07e | primary |
- Merged from: RULE-piora-BE-06-004
- Related rules: RULE-PIORA-CLINICA-010, RULE-PIORA-CLINICA-011

## Notes
DISCREPANCY (internal, preserved verbatim): the low "2-" band (81 <= fc <= 99) is commented out in source, so mild bradycardia / normal-low HR never scores 2-; and fc == 50 resolves to "1-" not "3-" due to branch order. Facade RULE-PIORA-CLINICA-011 labels only 2+ (taquicardia moderada), 3+ (taquicardia grave), 3- (bradicardia), with empty recomendacoes/intervencoes.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
