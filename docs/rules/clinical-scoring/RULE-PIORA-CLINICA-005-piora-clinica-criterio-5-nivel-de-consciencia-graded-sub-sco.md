# RULE-PIORA-CLINICA-005 — Piora Clinica criterio_5 - Nivel de consciencia (graded sub-score)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | scoring |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | piora-clinica |

## Rule
Graded consciousness sub-score mapped from the consciousness enum.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| sinais_vitais.nv_consciencia | enum | — | acordado|sonolencia|agitacao|reage_verbal|reage_tatil|coma|convulsao |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_5 | enum | — |

## Logic
```text
pontuacao = "0"
consciencia = sinais_vitais.nv_consciencia
if consciencia:
    if   consciencia == "reage_verbal": pontuacao = "1+"
    elif consciencia == "reage_tatil" : pontuacao = "2+"
    elif consciencia == "coma"        : pontuacao = "3+"
    elif consciencia == "sonolencia"  : pontuacao = "1-"
    elif consciencia == "agitacao"    : pontuacao = "2-"
    elif consciencia == "convulsao"   : pontuacao = "3-"
return pontuacao
```

## Edge cases (as implemented)
The value "acordado" (alert) and any unmapped value yield "0".

## Verification
- Verdict: UNVERIFIABLE
- Reference: Royal College of Physicians NEWS2 (2017) consciousness assessment (ACVPU: Alert / new Confusion / Voice / Pain / Unresponsive). Piora-clinica uses a proprietary consciousness enum mapped to a graded +/- sub-score rather than the NEWS2 binary (Alert=0, any CVPU=3).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/piora_clinica.py | 149-165 | 8166c07e | primary |
- Merged from: RULE-piora-BE-06-005
- Related rules: RULE-PIORA-CLINICA-010, RULE-PIORA-CLINICA-011

## Notes
Uses BalancoChoices.consciencia() enum values. Facade RULE-PIORA-CLINICA-011 labels: 2+ "Reage/responde ao estimulo tatil", 2- "Agitacao ou confusao", 3- "convulsao", 3+ "nao responde/reage".

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
