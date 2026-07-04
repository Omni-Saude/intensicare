# RULE-EFICIENCIA-004 — Eficiencia v3 criterio_5 - platelet transfusion at Plt>25000 (VERMELHO, wired)

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: moderate |
| Confidence | high |
| Cluster | eficiencia |

## Rule
Intended - platelet concentrate ("Concentrado de plaquetas com filtro") prescribed in the last 6h AND platelets>25000 AND absence of Melena / Enterorragia / AVC / TCE AND absence of a CVC / double-lumen dialysis catheter prescription in the last 4h. Feeds the VERMELHO alert.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| cpoe.concentrado_plaquetas, cpoe.cateter_duplo_hemod, cpoe.cateter_venoso_central | | | |
| evolucao platelets / enf_aspecto_intestinais / diagnostico_1..4 | | | |

## Outputs
| Name | Type | Unit |
|---|---|---|
| criterio_5 | boolean | |

## Logic
```text
cpoe_6hrs = cpoe_leito.filter(dt_atualizacao_cpoe__gte = now() - timedelta(hours=6))
cpoe_4hrs = cpoe_leito.filter(dt_atualizacao_cpoe__gte = now() - timedelta(hours=6))   # BUG: 6h, not 4h
return all([
  cpoe_6hrs.exclude(concentrado_plaquetas=0).exists(),
  handlers.get_number(getattr(ultima_cpoe, "diurna_plaquetas", 0)) > 25000,   # WRONG MODEL FIELD
  all([
    not getattr(ultima_evolucao, "enf_aspecto_intestinais") in ["Melena", "Enterorragia"],
    not list(filter(lambda x: x.startswith("I64"),
                    vars(ultima_evolucao).fromkeys(("diagnostico_1".."diagnostico_4")))),
    not cpoe_4hrs.exclude(cateter_duplo_hemod=0, cateter_venoso_central=0).exists(),
  ]),
]) if (ultimo_balanco and ultima_cpoe and ultima_evolucao and cpoe_6hrs) else False
```

## Edge cases (as implemented)
Platelet threshold reads ultima_cpoe.diurna_plaquetas, which does NOT exist on the CPOE model (diurna_plaquetas lives on evolucao) -> getattr default 0 -> ">25000" is always False -> this VERMELHO criterion never fires. The cpoe_4hrs window is defined with hours=6 (copy-paste of cpoe_6hrs), so the intended 4h catheter window is actually 6h. I64 (AVC) exclusion inert (fromkeys None-values bug).

## Divergence
Platelet value pulled from wrong model field (ultima_cpoe.diurna_plaquetas, absent -> always 0) so the sole wired VERMELHO trigger is permanently False; 4h CVC/CDL window mistakenly set to 6h; I64 exclusion inert. Facade text (RULE-EFICIENCIA-012) states the intended Plq>25000 rule.

## Verification
- Verdict: DISCREPANCY (impact: moderate)
- Reference: Kaufman RM, Djulbegovic B, Gernsheimer T, et al. Platelet Transfusion: A Clinical Practice Guideline From the AABB. Ann Intern Med. 2015;162(3):205-213. Prophylactic threshold 10x10^9/L (10,000/uL) for therapy-induced hypoproliferative thrombocytopenia; transfuse for elective CVC placement at <20,000/uL; no prophylactic indication above these thresholds absent procedure or active bleeding. (https://www.acpjournals.org/doi/10.7326/M14-1589)
- Test vectors: 3/4 match
- The 25,000/uL operational cutoff itself is reasonable and consistent with AABB 2015 (well above the 10k prophylactic and 20k pre-CVC thresholds). The DISCREPANCY is implementation: the platelet value is read from ultima_cpoe.diurna_plaquetas, a field that does not exist on the CPOE model (it lives on evolucao), so getattr returns 0 and `0 > 25000` is permanently False. This is the SOLE wired VERMELHO trigger in the efficiency track (per RULE-EFICIENCIA-001), so the entire red/high-priority alert tier never fires - a silent missed-alert for genuinely unjustified prophylactic platelet transfusions. Secondary defects: the intended 4h CVC/dialysis-catheter exclusion window is copy-pasted as 6h; the AVC (I64) exclusion is inert (fromkeys None-values). Missed advisory alert rather than a wrong order -> moderate.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/models/trilhas_v3/trilha_eficiencia.py | 561-617 | 8166c07e | primary |
| ahlabs-trilhas | core/facade/trilha_eficiencia.py | 127-134 | 8166c07e | duplicate |
- Merged from: RULE-eficiencia-BE-03-085
- Related rules: RULE-EFICIENCIA-001, RULE-EFICIENCIA-012

## Notes
Wired (VERMELHO via calcular_alerta_v2) but permanently False due to the wrong-field bug. Facade alert label "Reavaliar indicacao de transfusao de plaquetas para Plq> 25.000."

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
