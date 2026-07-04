# RULE-EFICIENCIA-003 — Eficiencia v3 criterio_4 - RBC transfusion at Hb 6-7, 2 units (defined, unwired)

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: low |
| Confidence | high |
| Cluster | eficiencia |

## Rule
Intended - Hb strictly between 6 and 7 AND >=2 units packed RBC prescribed AND absence of SCA / Melena / Enterorragia / AVC / TCE. Reconsider giving a 2nd RBC unit. Defined but not computed (commented out in calcular_criterios).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| evolucao.diurna_hemoglobina | float | g/dL | |
| cpoe.concentrado_hemacias | float | units | |
| evolucao diagnosis / enf_aspecto_intestinais fields | | | |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_4 | boolean | |

## Logic
```text
return all([
  6 < handlers.get_number(getattr(ultima_evolucao, "diurna_hemoglobina")) < 7,
  handlers.get_number(getattr(ultima_cpoe, "concentrado_hemacias", 0)) >= 2,
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
Hb open interval (6,7). >=2 units required. The Hb threshold here is correctly parenthesized (unlike criterio_3). Diagnosis exclusions (SCA/AVC) are non-functional due to the fromkeys None-values bug; Melena/Enterorragia exclusion works. Unwired.

## Divergence
SCA/AVC diagnosis exclusions are inert (fromkeys None-values bug); Hb 6-7 and >=2-unit thresholds themselves are implemented correctly. Facade text (RULE-EFICIENCIA-012) labels this "Hb>6 / 2u"; v3 restricts the upper bound to Hb<7 because Hb>=7 is handled by criterio_3.

## Verification
- Verdict: DISCREPANCY (impact: low)
- Reference: Carson JL, et al. AABB RBC Transfusion Thresholds, JAMA 2016;316(19):2025-2035 (restrictive threshold, single-unit transfusion / reassess-after-each-unit practice). Single-unit policy reinforced by ISBT Patient Blood Management (Red Cell Restrictive Transfusion Thresholds and Single-Unit Transfusion). (https://www.isbtweb.org/isbt-working-parties/clinical-transfusion/resources/patient-blood-management-resources/4-red-cell-transfusion-tresholds.html)
- Test vectors: 3/4 match
- Core threshold dimensions (Hb open-interval 6-7, >=2 units) match the reference correctly - the Hb gate is properly parenthesized here. Only defect vs reference is the inert SCA/AVC(I64) diagnosis exclusion (same fromkeys None-values bug as criterio_3). Impact low because the rule is UNWIRED (calcular_criterio_4 commented out of calcular_criterios) so it never fires in production, and the defect only affects the ACS/AVC carve-out, not the primary threshold.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/models/trilhas_v3/trilha_eficiencia.py | 496-559 | 8166c07e | primary |
| ahlabs-trilhas | core/facade/trilha_eficiencia.py | 119-126 | 8166c07e | duplicate |
- Merged from: RULE-eficiencia-BE-03-084
- Related rules: RULE-EFICIENCIA-002, RULE-EFICIENCIA-012

## Notes
Unwired (calcular_criterio_4 commented out in calcular_criterios).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
