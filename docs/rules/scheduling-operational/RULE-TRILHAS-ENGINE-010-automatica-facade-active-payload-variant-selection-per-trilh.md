# RULE-TRILHAS-ENGINE-010 — Automatica facade — active payload variant selection per trilha

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
The facade __init__ binds each trilha's "_automatica" alert payload to a SPECIFIC variant. For several trilhas two variants coexist (module dict vs get_ function, or v1 vs v3) and this mapping determines which one the automatic engine actually serves.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| trilha name | string |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| bound payload symbol | reference |  |

## Logic
```text
payload_sepse_automatica       = payload_trilha_sepse            (variant B, 27 criteria)
payload_sepse_automatica_v3    = get_payload_trilha_sepse()      (variant C, 20 criteria + thresholds)
payload_sedacao_automatica     = get_payload_trilha_sedacao()    (v2 fn, NOT the module dict)
payload_eficiencia_automatica  = get_payload_trilha_eficiencia() (efficiency fn, NOT the sedation module dict)
payload_estabilidade_automatica= get_payload_trilha_estabilidade()
payload_trilha_profilaxia_automatica = payload_trilha_profilaxia (v1 module dict, NOT the v3 fn)
payload_equilibrio_automatica  = payload_trilha_equilibrio
payload_ventilacao_automatica  = payload_trilha_ventilacao
payload_antimicrobiano_automatica = payload_trilha_antimicrobiano
payload_nutricao_automatica    = payload_trilha_nutricao
payload_glosa_zero_automatica  = payload_trilha_glosa_zero
# estabilizacao is NOT re-exported here; imported directly by trilha2 model
# from trilha_automatica.facade.estabilizacao
```

## Edge cases (as implemented)
"from .equilibrio import payload_equilibrio_automatica" appears twice (lines 2 and 7) — a harmless duplicate import. estabilizacao_automatica is intentionally absent from __init__.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/facade/__init__.py` | 1-12 | `8166c07e` | primary |

- Merged from: `RULE-config-BE-01-021`
- Related rules: RULE-TRILHAS-ENGINE-001, RULE-TRILHAS-ENGINE-009

## Notes
Load-bearing wiring: choosing get_ vs module payloads changes which criterion set and which thresholds are active. Cross-ref the sepse/sedacao/eficiencia/profilaxia variant payload rules (in their own clusters). This facade only selects between existing variants; it does not merge them.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
