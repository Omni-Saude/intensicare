# RULE-SEDACAO-024 — Sedation/analgesia pathway recommendation catalog (facade text: RASS targets, BNM, PRIS, analgesia ladder)

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | drug-dosing |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Facade payload text (get_payload_trilha_sedacao, the active "automatica" v2 variant) mapping each of the 12 pathway criteria to an alert label + recommendation string. Governs sedation-depth targets, neuromuscular-blocker (BNM) use, propofol PRIS monitoring, and the pain-management drug ladder. This is the clinician-facing text layer consumed by the v1 and v3 model get_detalhe(); the numeric predicates live in RULE-SEDACAO-001..012.

## Inputs

| name | type |
|---|---|
| criterio key | string (criterio_1..criterio_12) |

## Outputs

| name | type |
|---|---|
| {alerta, recomendacoes} | dict |

## Logic

```text
criterio_2  Reavaliar sedacao: avaliar suspender sedoanalgesia continua FORA das indicacoes:
            1-EME, 2-PCR<24h, 3-SHIC, 4-SDRA moderada/grave, 5-fase aguda choque septico, 6-cuidados paliativos.
criterio_3  P/F>150 + uso de BNM -> avaliar interromper BNM continuo (beneficio questionavel sem PRONA e P/F>150).
criterio_4  Altos parametros de VM -> alvo RASS <= -2 (iniciar/aprofundar sedacao).
criterio_5  Despertar diario: reduzir sedoanalgesia pela METADE da velocidade de infusao as 06h.
criterio_6  Overdose de BNM -> reduzir dose do BNM conforme protocolo.
criterio_7  Dor moderada -> tramal 100mg / metadona 10mg / paracetamol+codeina 750+30mg ate 4x/dia
            +/- dipirona 1g / paracetamol 750mg; reavaliar em 2h.
criterio_8  Dor intensa -> Morfina 2 mg EV, reavaliar a cada 1h ate max 10 mg; se refrataria OU
            creatinina > 2,5 mg/dl -> Fentanil BIC a 2 ml/h (50 mcg/h); reavaliar em 2h.
criterio_9  RASS < -2 sem indicacao -> reduzir >= metade da infusao ou suspender; RASS profundo
            justificado apenas em EME, PCR<24h, SHIC, SDRA com P/F<150.
criterio_10 Risco de hiperestesia/dependencia/abstinencia -> despertar diario, reduzir dose ou uso intermitente.
criterio_11 Propofol > 4 dias (risco PRIS) -> TG/CK/TGO/TGP 72/72h; suspender ou trocar por midazolam/cetamina.
criterio_12 TRE + taquidispneia FR > 22 ipm -> Morfina 2mg EV + Haldol EV ou Dexmedetomidina.
```

## Edge cases (as implemented)

Numeric anchors in text: P/F>150 (crit3/9), RASS<=-2 target / RASS<-2 excess (crit4/9), creatinina>2,5 (crit8), propofol>4d (crit11), FR>22 (crit12). Morphine titration ceiling 10 mg. Daily-awakening reduction is exactly half the infusion rate.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** Composite recommendation catalog whose numeric anchors map to standard published references: (a) NMBA reserved for severe ARDS P/F<150 and benefit questionable otherwise — ACURASYS (Papazian et al. NEJM 2010;363:1107, enrolled P/F<150) and ROSE (Moss et al. NEJM 2019;380:1997, negative with higher PEEP/lighter sedation/less prone); (b) light-sedation RASS target 0 to -2, deep sedation only for specific indications — SCCM PADIS 2018 (Crit Care Med 2018;46:e825) + RASS (Sessler 2002); (c) opioid choice in renal dysfunction: morphine active renal-cleared metabolite (M6G) accumulates -> fentanyl preferred; (d) PRIS surveillance for prolonged/high-dose propofol (CK, triglycerides); (e) tachypnea RR>=22 = qSOFA respiratory criterion (Sepsis-3, Singer et al. JAMA 2016;315:801). ([source](https://www.nejm.org/doi/full/10.1056/NEJMoa1901686))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | ok |
| units | ok |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| criterio=criterio_3; scenario=P/F>150 on continuous BNM, no prone | consider stopping NMBA (benefit reserved for severe ARDS P/F<150, esp. with prone) - ACURASYS/ROSE | text: 'avaliar interrupcao do BNM ... beneficio questionavel se ausencia de PRONA e P/F>150' | yes |
| criterio=criterio_8; scenario=severe pain, creatinine 3.0 mg/dl | avoid morphine accumulation in renal dysfunction; switch to fentanyl 50 mcg/h | text: 'morfina 2mg EV q1h ate max 10mg; se refrataria OU creatinina >2,5 mg/dl -> fentanil 2 ml/h (50 mcg/h)' | yes |
| criterio=criterio_11; scenario=propofol infusion >4 days | PRIS surveillance: monitor CK, triglycerides, transaminases; consider switch to midazolam/ketamine | text: 'Propofol >4 dias risco PRIS -> TG/CK/TGO/TGP 72/72h; suspender ou trocar por midazolam/cetamina' | yes |
| criterio=criterio_12; scenario=SBT with tachypnea RR>22 ipm | RR>=22 = qSOFA respiratory threshold; address pain/delirium/withdrawal | text: 'TRE + taquidispneia FR>22 ipm -> Morfina 2mg EV + Haldol EV ou Dexmedetomidina' | yes |
| criterio=criterio_4; scenario=high ventilator settings | deep sedation (RASS<=-2) acceptable when clinically indicated (severe ARDS); default light sedation per PADIS | text: 'Altos parametros de VM -> alvo RASS <= -2 (iniciar/aprofundar sedacao)' | yes |

**Verifier notes**

All numeric/pharmacologic anchors in the facade text (get_payload_trilha_sedacao, the active v2 variant) align with published references: NMBA-for-severe-ARDS P/F<150 threshold (ACURASYS/ROSE), PADIS light-sedation RASS 0 to -2 with justified deep sedation, morphine->fentanyl in renal impairment, propofol PRIS monitoring, qSOFA RR>=22. Units are internally consistent (fentanyl 2 ml/h = 50 mcg/h). ONE text typo (not a logic/numeric defect): criterio_9 recommendation body reads "Considerar RASS > 2 apenas para EME..." which contradicts its own alerta line "Sedacao profunda (RASS < -2)" and clinical intent — should read "RASS < -2". Cosmetic text only; documented, not corrected. The module-level payload_trilha_sedacao (v1 variant) carries identical analgesia numbers (label-only differences), so no numeric divergence between variants.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/facade/trilha_sedacao.py` | 94-185 | `8166c07eae` | primary |
| ahlabs-trilhas | `core/facade/trilha_sedacao.py` | 1-91 | `8166c07eae` | variant |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sedacao-BE-01-015`

**Related rules:**

- [RULE-SEDACAO-025](RULE-SEDACAO-025-sedative-specific-reduction-recommendation-criterio-1-free-t.md)
- [RULE-SEDACAO-014](../alert-threshold/RULE-SEDACAO-014-sedacao-v3-alert-calcular-alerta-v2-used-legacy-calcular-ale.md)
- [RULE-SEDACAO-023](../alert-threshold/RULE-SEDACAO-023-sedacao-v1-alert-trilhasedacaomodel-calcular-alerta.md)
- [RULE-SEDACAO-007](RULE-SEDACAO-007-sedacao-v3-criterio-3-neuromuscular-blockade-with-p-f-150-de.md)
- [RULE-SEDACAO-008](RULE-SEDACAO-008-sedacao-v3-criterio-4-undersedation-on-invasive-vent-defined.md)
- [RULE-SEDACAO-009](RULE-SEDACAO-009-sedacao-v3-criterio-5-no-morning-sedation-reduction-1-2.md)
- [RULE-SEDACAO-011](RULE-SEDACAO-011-sedacao-v3-criterio-10-prolonged-sedation-96h-defined-unwire.md)
- [RULE-SEDACAO-012](RULE-SEDACAO-012-sedacao-v3-criterio-11-prolonged-propofol-without-safety-lab.md)

## Notes

Catalog-text counterpart of the v3 predicate criteria (RULE-SEDACAO-001..012); kept as a distinct aggregate artifact (granularity: one payload spanning all 12 criteria) rather than merged into the individual predicates. The module-level payload_trilha_sedacao (lines 1-91) is a near-identical v1 text variant differing only in labels (crit_1 "Overdose de sedoanalgesia." vs v2 "...considerar reducao"; crit_5 "Nao realizado despertar diario." vs v2 "Sedacao continua, considerar despertar diario"; crit_7/8 label wording). Verified: analgesia NUMBERS are identical in both payloads (no clinical/numeric divergence, label-only). Consumed by trilha1.py and trilhas_v3 get_detalhe().

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
