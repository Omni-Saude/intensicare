# RULE-PIORA-CLINICA-003 — Piora Clinica criterio_3 - Pressao arterial sistolica (PAS) (graded sub-score)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | scoring |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | piora-clinica |

## Rule
Graded systolic blood-pressure sub-score. Full +/- grading present (only criterion with all six bands).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| sinais_vitais.pas | float | mmHg | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_3 | enum | — |

## Logic
```text
pontuacao = "0"
pas = sinais_vitais.pas
if pas:
    if   131 <= pas <= 149: pontuacao = "1+"
    elif 150 <= pas <= 189: pontuacao = "2+"
    elif        pas >  189: pontuacao = "3+"
    elif 100 <= pas <= 109: pontuacao = "1-"
    elif  81 <= pas <=  99: pontuacao = "2-"
    elif        pas <=  80: pontuacao = "3-"
return pontuacao
```

## Edge cases (as implemented)
Gap 110..130 -> "0". pas == 0 falsy -> "0". Boundaries inclusive as shown; pas == 80 -> "3-" (predicate uses <= 80).

## Divergence
Label-vs-code boundary mismatch at PAS = 80. Facade RULE-PIORA-CLINICA-011 describes the 3- (hipotensao grave) band as "PAS <80 mmHg", whereas this predicate uses `pas <= 80`. So PAS = 80 scores 3- in code but is described as excluded by the facade label text. Code is authoritative (the label is a non-executable descriptive string); recorded as an AMBIGUOUS label imprecision on the facade rule, this predicate stays OK.

## Verification
- Verdict: UNVERIFIABLE
- Reference: Royal College of Physicians NEWS2 (2017) systolic-BP band as family anchor. Piora-clinica PAS bands are a distinct proprietary scale (it scores hypertension, which NEWS2 does not until >=220).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/piora_clinica.py | 113-129 | 8166c07e | primary |
- Merged from: RULE-piora-BE-06-003
- Related rules: RULE-PIORA-CLINICA-010, RULE-PIORA-CLINICA-011

## Notes
Other facade thresholds match this code exactly: 2- "PAS 81-99mmHg", 2+ "PAS 150-189 mmHg", 3+ "PAS >189 mmHg". Only the 3- lower-bound description (<80 vs <=80) diverges.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
