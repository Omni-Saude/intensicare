# RULE-PIORA-CLINICA-001 — Piora Clinica criterio_1 - Frequencia respiratoria (graded sub-score)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | scoring |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | piora-clinica |

## Rule
Graded respiratory-rate sub-score for the clinical-deterioration ("piora clinica") track-and-trigger scale. Returns a signed grade string ("+" = high deviation, "-" = low deviation) used both to sum the aggregate score and to fire per-criterion alerts.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| sinais_vitais.frequencia_respiratoria | int | breaths/min | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_1 | enum | — |

## Logic
```text
pontuacao = "0"
fr = sinais_vitais.frequencia_respiratoria
if fr:
    if   19 <= fr <= 22: pontuacao = "1+"
    elif  9 <= fr <= 11: pontuacao = "1-"
    elif       fr <  9 : pontuacao = "3-"
    elif       fr > 22 : pontuacao = "3+"
return pontuacao
```

## Edge cases (as implemented)
fr in 12..18 -> "0" (normal). fr == 0 is falsy -> "0". No 2+/2- band exists for FR (magnitude jumps 1 -> 3). Boundaries inclusive at 19,22 and 9,11.

## Verification
- Verdict: UNVERIFIABLE
- Reference: Royal College of Physicians. National Early Warning Score (NEWS) 2 (2017). Respiratory-rate band is the closest published track-and-trigger anchor; piora-clinica is a distinct proprietary instrument with its own cutoffs.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/piora_clinica.py | 83-95 | 8166c07e | primary |
- Merged from: RULE-piora-BE-06-001
- Related rules: RULE-PIORA-CLINICA-010, RULE-PIORA-CLINICA-011

## Notes
Grade magnitude (1/3) feeds the soma in RULE-PIORA-CLINICA-010; sign (+/-) feeds the per-criterion color trigger. Facade RULE-PIORA-CLINICA-011 only labels the 3+ (taquipneia grave) and 3- (bradipneia) outcomes for this criterion.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
