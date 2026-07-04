# RULE-PIORA-CLINICA-002 — Piora Clinica criterio_2 - Temperatura axilar (graded sub-score)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | scoring |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: low |
| Confidence | high |
| Cluster | piora-clinica |

## Rule
Graded axillary-temperature sub-score for the clinical-deterioration scale.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| sinais_vitais.temperatura | float | Celsius | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_2 | enum | — |

## Logic
```text
pontuacao = "0"
temperatura = sinais_vitais.temperatura
if temperatura:
    if   37.6 <= temperatura <= 37.9: pontuacao = "1+"
    elif 38   <= temperatura <= 38.2: pontuacao = "2+"
    elif         temperatura >  38.2: pontuacao = "3+"
    elif 35   <= temperatura <= 35.4: pontuacao = "1-"
    elif         temperatura <  35  : pontuacao = "3-"
return pontuacao
```

## Edge cases (as implemented)
Gap 35.5..37.5 -> "0". DISCREPANCY: half-open boundary gap 37.9 < t < 38.0 (e.g. 37.95) falls between the 1+ and 2+ bands and scores "0". No 2- band. temperatura == 0 falsy -> "0".

## Verification
- Verdict: DISCREPANCY (impact: low)
- Reference: Royal College of Physicians NEWS2 (2017) temperature band as family anchor. The verdict here targets an INTERNAL coverage discontinuity independent of any external reference.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/piora_clinica.py | 97-111 | 8166c07e | primary |
- Merged from: RULE-piora-BE-06-002
- Related rules: RULE-PIORA-CLINICA-010, RULE-PIORA-CLINICA-011

## Notes
DISCREPANCY is a coverage bug internal to the predicate (discontinuity in (37.9, 38.0)), not a cross-copy divergence. Facade label thresholds match this code: 2+ "TAX 38 - 38,2C", 3+ "TAX >38,2C", 3- "TAX<35C" (RULE-PIORA-CLINICA-011).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
