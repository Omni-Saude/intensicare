# RULE-PIORA-CLINICA-006 — Piora Clinica criterio_6 - Dor (escala numerica 0-10) (graded sub-score)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | scoring |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: high |
| Confidence | high |
| Cluster | piora-clinica |

## Rule
Graded numeric pain-scale (0-10 numeric rating scale) sub-score.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| sinais_vitais.escala_dor | int | points (0-10 numeric rating scale) | 0-10 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_6 | enum | — |

## Logic
```text
pontuacao = "0"
dor = sinais_vitais.escala_dor
if dor:
    if   2 <= dor <= 3 : pontuacao = "1+"
    elif 4 <= dor <= 6 : pontuacao = "2+"
    elif 7 <= dor >  10: pontuacao = "3+"     # buggy compound comparison, verbatim
return pontuacao
```

## Edge cases (as implemented)
`7 <= dor > 10` evaluates as (7 <= dor) AND (dor > 10). Since escala_dor is validator-capped at 10, dor > 10 is impossible, so "3+" is UNREACHABLE and severe pain 7,8,9,10 all score "0". dor == 0/1 -> "0".

## Verification
- Verdict: DISCREPANCY (impact: high)
- Reference: Numeric Rating Scale (NRS 0-10) for pain intensity. Standard cut-offs: mild 1-3/1-4, moderate 5-6, severe 7-10; higher = worse and severe is the band that must drive intervention. Boonstra AM et al., "Cut-Off Points for Mild, Moderate, and Severe Pain on the NRS for Pain in Patients with Chronic Musculoskeletal Pain," Front Psychol 2016;7:1466.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/piora_clinica.py | 167-177 | 8166c07e | primary |
- Merged from: RULE-piora-BE-06-006
- Related rules: RULE-PIORA-CLINICA-010, RULE-PIORA-CLINICA-011

## Notes
DISCREPANCY (internal, preserved verbatim): intended threshold was almost certainly `7 <= dor <= 10 -> 3+`; as written the severe-pain band never fires. Input validator that caps escala_dor at 10 lives in a separate cluster (captured there as the pain-scale validator RULE-pain-BE-06-001). Facade RULE-PIORA-CLINICA-011 labels 2+ "dor moderada", 3+ "dor intensa".

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
