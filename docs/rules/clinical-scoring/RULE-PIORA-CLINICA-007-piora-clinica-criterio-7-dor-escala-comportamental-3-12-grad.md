# RULE-PIORA-CLINICA-007 — Piora Clinica criterio_7 - Dor (escala comportamental 3-12) (graded sub-score)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | scoring |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: high |
| Confidence | high |
| Cluster | piora-clinica |

## Rule
Graded behavioral pain-scale (range 3-12) sub-score.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| sinais_vitais.sinais_dor | int | points (behavioral pain scale, 3-12) | 3-12 |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_7 | enum | — |

## Logic
```text
pontuacao = "0"
sinais = sinais_vitais.sinais_dor
if sinais:
    if   5  <= sinais <= 6 : pontuacao = "1+"
    elif 7  <= sinais <= 9 : pontuacao = "2+"
    elif 10 <= sinais >  12: pontuacao = "3+"   # buggy compound comparison, verbatim
return pontuacao
```

## Edge cases (as implemented)
`10 <= sinais > 12` == (10 <= sinais) AND (sinais > 12). sinais_dor is validator-capped at 12, so sinais > 12 is impossible and "3+" is UNREACHABLE; sinais 10,11,12 score "0". sinais 3,4 -> "0".

## Verification
- Verdict: DISCREPANCY (impact: high)
- Reference: Behavioral Pain Scale (BPS), Payen JF et al., Crit Care Med 2001;29(12):2258-63. Three domains (facial expression, upper-limb movement, ventilator compliance), each 1-4, total range 3 (no pain) to 12 (maximal pain), higher = worse; score >5 (>=6) commonly indicates significant/unacceptable pain requiring analgesia.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/piora_clinica.py | 179-189 | 8166c07e | primary |
- Merged from: RULE-piora-BE-06-007
- Related rules: RULE-PIORA-CLINICA-010, RULE-PIORA-CLINICA-011

## Notes
DISCREPANCY (internal, preserved verbatim): intended `10 <= sinais <= 12 -> 3+`; as written the highest behavioral-pain band never fires. Validator capping sinais_dor at 12 lives in a separate cluster (pain-scale validator RULE-pain-BE-06-002). Facade RULE-PIORA-CLINICA-011 labels 2+ "dor moderada", 3+ "dor intensa" (identical strings to criterio_6).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
