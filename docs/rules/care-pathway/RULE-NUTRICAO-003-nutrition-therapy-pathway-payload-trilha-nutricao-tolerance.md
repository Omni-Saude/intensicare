# RULE-NUTRICAO-003 — Nutrition-therapy pathway (payload_trilha_nutricao) - tolerance, gastric-residual and contraindication thresholds

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | DISCREPANCY (impact: moderate) |
| Confidence | high |
| Cluster | nutricao |

## Rule
Nutrition pathway (= nutricao / trilha6): per-criterion alert text and recommendations covering diet prescription, SNE need, tolerance/gastric-residual limits, diarrhea management, malperfusion feeding, prokinetics, GI bleed, NPT and hyperglycemia. Defined as the dict payload_trilha_nutricao and consumed by the nutrition alert model (RULE-NUTRICAO-004) via get_detalhe for criteria [4,7,10].

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| volume residual gastrico (VRG) | float | ml/6h |  |
| numero de evacuacoes | int | count/24h |  |
| noradrenalina rate | float | ml/h |  |
| Hb / plaquetas | float |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| alerta + recomendacoes | string |  |

## Logic
```text
criterio_1 sem dieta prescrita -> prescrever dieta ou "Dieta Zero" justificada. Do NOT suspend
  nutrition merely for: vomito, diarreia, reducao de RHA, exames (com TOT), VRG < 500ml/6h,
  DVA, prona, pancreatite aguda grave, encefalopatia hepatica, varizes esofagicas, pre-traqueo.
  Consider Fonoaudiologia for altered consciousness / elderly starting oral diet.
criterio_2 necessidade de SNE -> passar SNE, iniciar infusao apos conferir posicionamento.
criterio_3 dieta interrompida sem justificativa -> checar contraindicacoes: perfusao muito
  reduzida (enchimento capilar/lactato aumentados), noradrenalina > 30 ml/h (= 0,05 mcg/kg/min),
  melena/hematemese/enterorragia, cirurgia media/grande porte pendente, VRG > 500 ml nas ultimas 6h.
criterio_4 diarreia >= 5 evacuacoes OR >= 3 "liquidas" em 24h -> Saccharomyces boulardii,
  loperamida (se sem febre/distensao); nao suspender/reduzir dieta por diarreia; se >48h com
  febre/piora -> pesquisar toxina A/B C. difficile + precaucao de contato + Metronidazol 500 mg 8/8h.
criterio_5 intolerancia (VRG aumentado pela SNE aberta) -> procineticos; se VRG > 500 ml nas
  ultimas 6h, interromper infusao de dieta por 2h e reavaliar reinicio.
criterio_6 dieta em paciente mal perfundido -> procineticos + infundir dieta a 30 ml/h (trofismo);
  considerar parecer de infectologia.
criterio_7 VM sem procineticos -> iniciar metoclopramida/bromoprida/domperidona/simeticona.
criterio_8 hemorragia digestiva -> Dieta Zero, suspender heparina profilatica/AAS/clopidogrel,
  EDA, omeprazol 40 mg EV 12/12h; hemotransfusao SO se Hb < 7 E plaquetas < 150000. Para pacientes
  estaveis, otimizar profilaxia mecanica de TEV (deambulacao, cicloergometro, CPI, sedestacao).
criterio_9 NPT -> acesso venoso profundo dedicado + reposicao vitaminica programada
  (Acido folinico 24/24h, Complexo B 72/72h, Cianocobalamina, Vit K, Polivitaminico, Oligoelementos, Tiamina);
  considerar parecer de Nutrologia.
criterio_10 hiperglicemia em paciente instavel -> Insulina em BIC (protocolo de controle glicemico UTI).
```

## Edge cases (as implemented)
Gastric residual cutoff 500 ml/6h (interrupt infusion for 2h). "Do not suspend" list uses VRG < 500ml/6h; interruption trigger uses VRG > 500ml/last 6h. Diarrhea cutoff >=5 total OR >=3 liquid stools / 24h. Vasopressor feeding contraindication noradrenaline >30 ml/h equated to 0,05 mcg/kg/min. GI-bleed transfusion trigger Hb<7 AND platelets<150000.

## Verification
- Verdict: DISCREPANCY (impact: moderate)
- Reference: McClave SA et al. ASPEN/SCCM Guidelines for Provision and Assessment of Nutrition Support Therapy in the Adult Critically Ill Patient (2016) - hold EN only for GRV >500 mL. Villanueva C et al. NEJM 2013;368:11-21 - restrictive RBC transfusion at Hb <7 g/dL in acute upper GI bleed.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/facade/trilha_nutricao.py | 1-87 | 8166c07e | primary |

- Merged from: RULE-nutricao-BE-01-017
- Related rules: RULE-NUTRICAO-004, RULE-NUTRICAO-005

## Notes
Verified against source lines 1-87 (dict payload_trilha_nutricao). trilha_automatica/facade/nutricao.py aliases this exact dict as payload_nutricao_automatica, imported by trilha6.py:7 and consumed by TrilhaNutricaoModel.get_detalhe (RULE-NUTRICAO-004) for criteria [4,7,10] only -- so of the 10 criteria, only 4/7/10 currently surface in the automatic alert detail. verify:true because the pathway embeds published clinical anchors worth checking: transfusion trigger (Hb<7), vasopressor dose equivalence (noradrenaline 30 ml/h = 0,05 mcg/kg/min) and the 500 ml/6h gastric-residual cutoff.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
