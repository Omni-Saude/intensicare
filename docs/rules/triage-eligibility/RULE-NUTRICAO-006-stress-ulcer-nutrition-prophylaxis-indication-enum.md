# RULE-NUTRICAO-006 — Stress-ulcer / nutrition prophylaxis indication enum

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | eligibility |
| Status | OK |
| Verification | DISCREPANCY (impact: low) |
| Confidence | high |
| Cluster | nutricao |

## Rule
Enumerated indications for stress-ulcer / nutritional prophylaxis on the terapia_nutricional model, including a threshold-bearing option "mechanical ventilation for more than 72h".

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| indicacao_profilaxia | enum |  | dva|tce|avc|queimado|jejum_prolongado|nao_indicado|terapeutico|vm_mais_72h |

## Outputs
| Name | Type | Unit |
|---|---|---|
| prophylaxis indication | string |  |

## Logic
```text
indicacao_profilaxia (value, label):
  dva              -> DVA (vasoactive drugs)
  tce              -> TCE (traumatic brain injury)
  avc              -> AVC (stroke)
  queimado         -> Queimado (burn)
  jejum_prolongado -> Jejum Prolongado (prolonged fasting)
  nao_indicado     -> Nao indicado (not indicated)
  terapeutico      -> Terapeutico (therapeutic)
  vm_mais_72h      -> VM por mais de 72hs (mechanical ventilation > 72 hours)
```

## Edge cases (as implemented)
The value vm_mais_72h encodes a 72-hour ventilation threshold as an eligibility category (categorical label, not a computed threshold).

## Verification
- Verdict: DISCREPANCY (impact: low)
- Reference: ASHP Therapeutic Guidelines on Stress Ulcer Prophylaxis (1999): mechanical ventilation >48h and coagulopathy are the two primary independent SUP indications; SCCM/ASHP 2024 update revises MV-alone recommendation.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/choices/terapia_nutricional.py | 10-21 | 8166c07e | primary |

- Merged from: RULE-nutri-BE-06-002
- Related rules: RULE-NUTRICAO-005

## Notes
Verified against source lines 10-21 (TerapiaNutricionalChoices.indicacao_profilaxia). The identical 8-value enum (and the aceitacao enum in the same class) is replicated verbatim in the frontend forms (RULE-NUTRICAO-005) -> backend/frontend copies match exactly, no divergence. Kept separate from the frontend block to preserve backend-model granularity. verify:true: encodes a clinical prophylaxis eligibility threshold (VM>72h) with a plausible published anchor (stress-ulcer prophylaxis guidance; classic SUP indication is mechanical ventilation, often cited >48h, whereas this uses >72h).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
