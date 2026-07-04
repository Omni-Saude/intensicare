# RULE-VENTILACAO-017 — Ventilation/weaning facade protocol (ventilacao_automatica) - protective settings, PEEP/FiO2, tracheostomy timing, PRONA, O2 targets

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Ventilation pathway facade (= ventilacao_automatica): lung-protective ventilation, PEEP/FiO2 table titration, spontaneous-breathing readiness, tracheostomy timing, PRONA indication, oxygen-target de-escalation.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| peso ideal (kg) | | | |
| P/F ratio | | | |
| TOT dwell time (days) | | | |
| idade (years) | | | |
| SatO2 (%) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| alerta + recomendacoes (string) | | |

## Logic

```text
criterio_1 VM nao protetora -> VC 4 ml/kg do peso ideal, acidose respiratoria permissiva.
criterio_2 titulacao PEEP inadequada p/ SDRA leve-moderada -> tabela PEEPxFiO2 (SDRA mod/grave;
           se COVID -> tabela SDRA leve, PEEP baixa).
criterio_3 titulacao PEEP p/ P/F < 150 -> tabela PEEPxFiO2 SDRA mod/grave (PEEP alta);
           COVID -> tabela SDRA leve (PEEP baixa).
criterio_4 bom nivel de consciencia + baixos parametros -> teste de prontidao -> TRE.
criterio_5 dependente de VM por TOT > 10 dias sem progressao -> solicitar Traqueostomia.
criterio_6 COVID-19 dependente de VM > 14 dias sem progressao -> Traqueostomia.
criterio_7 SDRA moderada-grave -> PRONA 16 a 20h (tecnica envelope), RASS -4 a -5, +/- BNM continuo.
criterio_8/9 oportunidade de TRE -> se DPOC/ICC/falha de extubacao previa/idade > 75 anos ->
           VNI facilitadora por ate 2h imediatamente apos extubacao.
criterio_10 reducao de O2: algoritmo 1 SatO2 > 96% -> reduzir O2 (evitar hiperoxia);
           algoritmo 2 DPOC com SatO2 > 92% -> reduzir para manter 88-92%.
```

## Edge cases (as implemented)

Cutoffs: VC 4 ml/kg ideal weight; P/F<150; TOT>10d (14d if COVID); age>75; SatO2>96% general de-escalation; DPOC target band 88-92%. PRONA duration 16-20h, RASS -4 to -5. VNI <=2h.

## Verification

- Verdict: VERIFIED (clinical impact: none)
- Reference: Composite protocol facade. Anchors: (1) ARDSNet - ARDS Network NEJM 2000;342:1301-8 (lung-protective VT 6 mL/kg PBW, reducible to 5 then 4, permissive hypercapnia); (2) PROSEVA - Guerin C et al. NEJM 2013;368:2159-68 (prone if PaO2/FiO2 <150 with FiO2>=0.6/PEEP>=5; sessions >=16 h/day; deep sedation RASS -4/-5 +/- NMB); (3) ERS/ATS weaning consensus (Boles 2007, SBT/TRE readiness); (4) BTS 2017 oxygen guideline (SpO2 94-98% general, 88-92% COPD; avoid hyperoxia); (5) tracheostomy-timing literature (~10-14 days for prolonged intubation); (6) high-risk-extubation VNI (COPD/CHF/prior failure/advanced age).

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/facade/trilha_ventilacao.py` | 1-104 | `8166c07e` | primary |

- Merged from: RULE-ventilacao-BE-01-018
- Related rules: RULE-VENTILACAO-003, RULE-VENTILACAO-004, RULE-VENTILACAO-005, RULE-VENTILACAO-007, RULE-VENTILACAO-008, RULE-VENTILACAO-009, RULE-VENTILACAO-010, RULE-VENTILACAO-011, RULE-VENTILACAO-013, RULE-VENTILACAO-001

## Notes

Human-readable protocol facade (ventilacao_automatica variant) that the trilha_manual criteria (C1..C10) implement. PEEPxFiO2 tables referenced but not defined in this payload (external protocol). NOTE the variant divergence: facade criterio_6 COVID trach at ">14 dias" vs trilha_manual C6 code (RULE-VENTILACAO-009) at ">10 dias". Strong published ARDS/PRONA/O2-target anchors -> verify=true.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
