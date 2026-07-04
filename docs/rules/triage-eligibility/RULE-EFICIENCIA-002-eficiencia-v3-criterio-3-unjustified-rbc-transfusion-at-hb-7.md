# RULE-EFICIENCIA-002 — Eficiencia v3 criterio_3 - unjustified RBC transfusion at Hb>=7 (AMARELO, wired)

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | high |
| Cluster | eficiencia |

## Rule
Intended - Hb>=7 AND packed-RBC ("Concentrado de hemacias com filtro") prescribed AND absence of SCA / Melena / Enterorragia / AVC isquemico (I64) / AVC hemorragico / TCE. Feeds the AMARELO alert. Restrictive transfusion threshold (Hb>=7 in absence of active bleeding, acute brain injury or acute coronary syndrome).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| evolucao.diurna_hemoglobina | float | g/dL | |
| evolucao.enf_aspecto_intestinais | string | | Melena/Enterorragia |
| evolucao.diag_inter_1..5, diagnostico_1..4 | strings | | |
| cpoe.concentrado_hemacias | float | units | |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_3 | boolean | |

## Logic
```text
ultimo_balanco  = balancos_leito.first()
ultima_cpoe     = cpoe_leito.first()
ultima_evolucao = evolucao_leito.first()
return all([
  getattr(ultima_evolucao, "diurna_hemoglobina", 0) or 0 >= 7,   # precedence bug
  getattr(ultima_cpoe, "concentrado_hemacias", 0),
  all([
    not "SCA - Sindrome coronariana aguda"
        in vars(ultima_evolucao).fromkeys(("diag_inter_1".."diag_inter_5")).values(),
    not getattr(ultima_evolucao, "enf_aspecto_intestinais") in ["Melena", "Enterorragia"],
    not list(filter(lambda x: x.startswith("I64"),
                    vars(ultima_evolucao).fromkeys(("diagnostico_1".."diagnostico_4")))),
  ]),
]) if (ultimo_balanco and ultima_cpoe and ultima_evolucao) else False
```

## Edge cases (as implemented)
Operator precedence - `diurna_hemoglobina or 0 >= 7` parses as `diurna_hemoglobina or (0 >= 7)`, i.e. truthiness of the Hb value; the Hb>=7 threshold is NEVER actually applied (fires on any non-empty Hb plus an RBC order). fromkeys() builds a dict whose values are all None, so the SCA and I64 (AVC) exclusions are vacuously True (non-functional). Melena/ Enterorragia exclusion does work.

## Divergence
Code vs intent/facade: Hb>=7 threshold is defeated by operator precedence (any truthy Hb + RBC prescription satisfies it), and the SCA/AVC diagnosis exclusions are inert (fromkeys None-values bug). Facade text (RULE-EFICIENCIA-012) states the intended Hb>=7 rule.

## Verification
- Verdict: DISCREPANCY (impact: moderate)
- Reference: Carson JL, Guyatt G, Heddle NM, et al. Clinical Practice Guidelines From the AABB: Red Blood Cell Transfusion Thresholds and Storage. JAMA. 2016;316(19):2025-2035. Restrictive threshold - transfusion not indicated until Hb <7 g/dL for hemodynamically stable hospitalized adults incl. critically ill; explicit exceptions for acute coronary syndrome. Origin: Hebert PC, et al. TRICC trial, NEJM 1999;340:409-417. (https://transfusionontario.org/wp-content/uploads/2020/06/AABB_RBC_Carson_JAMA_2016.pdf)
- Test vectors: 2/4 match
- Intended threshold matches AABB 2016/TRICC. Two implemented defects vs reference: (1) operator-precedence bug `diurna_hemoglobina or 0 >= 7` parses as `diurna_hemoglobina or (0>=7)`, so the Hb>=7 gate is never applied - it fires on ANY non-zero Hb plus an RBC order, generating false-positive "reassess transfusion" AMARELO alerts on patients appropriately transfused below 7; (2) the ACS and AVC-ischemic (I64) exclusions - the exact guideline carve-outs - are inert because vars().fromkeys() builds a dict with all None values, so alerts are NOT suppressed for ACS/acute-brain-injury patients. Melena/Enterorragia exclusion is functional. Advisory alert (not an order) -> moderate, not high.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/models/trilhas_v3/trilha_eficiencia.py | 436-494 | 8166c07e | primary |
| ahlabs-trilhas | core/facade/trilha_eficiencia.py | 111-118 | 8166c07e | duplicate |
- Merged from: RULE-eficiencia-BE-03-083
- Related rules: RULE-EFICIENCIA-001, RULE-EFICIENCIA-003, RULE-EFICIENCIA-012

## Notes
Wired (AMARELO via calcular_alerta_v2). Facade alert label is "Reavaliar indicacao de transfusao de hemacias (Hb>7)" with recommendation body stating Hb>=7.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
