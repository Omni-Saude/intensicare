# RULE-EFICIENCIA-012 — Eficiencia active alert-text payload catalog (get_payload_trilha_eficiencia / eficiencia_automatica)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | threshold |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | eficiencia |

## Rule
Shared display payload returned by get_payload_trilha_eficiencia(). It is imported by the v3 model (import at module top) and rendered by get_detalhe() to build the alert text of each fired criterion. Defines the alert label + recommendation text for the 10 efficiency criteria, including the evidence-based transfusion restriction thresholds. Wired as the active "eficiencia_automatica" payload.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| fired criterio_N (from the v3 predicate rules) selects which text to show | | | |

## Outputs
| Name | Type | Unit |
|---|---|---|
| per-criterion {alerta, recomendacoes} text blocks | | |

## Logic
```text
# get_payload_trilha_eficiencia() -> dict criterio_1..criterio_10:
criterio_1  alerta: "Reavaliar solicitacao redundante dos exames:"
            (get_detalhe appends self.exames_repetidos)
            rec: reavaliar beneficio de repetir exame em curto periodo
criterio_2  alerta: "Avaliar alta da UTI por melhora clinica"
            rec: paciente estavel hemodinamicamente, bom padrao respiratorio,
                 afebril, sem intercorrencias -> considerar alta da UTI
criterio_3  alerta: "Reavaliar indicacao de transfusao de hemacias (Hb>7)"
            rec: sem beneficio de transfusao para Hb>=7 na ausencia de
                 sangramento ativo, lesao cerebral aguda ou SCA
criterio_4  alerta: "Reavaliar indicacao de 2u de transfusao de hemacias (Hb>6)"
            rec: sem beneficio de >1u para Hb>6 nas mesmas ausencias;
                 considerar prescrever apenas 1u
criterio_5  alerta: "Reavaliar indicacao de transfusao de plaquetas para Plq> 25.000."
            rec: sem beneficio de transfusao profilatica sem procedimento
                 invasivo ou sangramento ativo
criterio_6  alerta: "Considerar inicio de Cuidados paliativos."
criterio_7  alerta: "Alto risco para Delirium, realizar medidas de controle."
criterio_8  alerta: "Indicar mobilizacao, deambular, sentar em poltrona e levar ao banheiro."
criterio_9  alerta: "Suspeita de ME: iniciar manutencao do potencial doador de orgaos."
criterio_10 alerta: "Reavaliar indicacao de contencao mecanica."
```

## Edge cases (as implemented)
Text/display only - no compute. criterio_3 alert LABEL reads "(Hb>7)" while its recommendation body states "Hb>=7" (label >7 vs body >=7); criterio_4 label "(Hb>6)"; platelet label "Plq> 25.000". The actual threshold logic is enforced (buggily) by the v3 predicate code (RULE-EFICIENCIA-002..004).

## Verification
- Verdict: VERIFIED (impact: none)
- Reference: Red Blood Cell Transfusion 2023 AABB International Guidelines (Carson et al., JAMA 2023) - restrictive strategy, transfuse when Hb <7 g/dL in hemodynamically stable hospitalized adults (8 g/dL for pre-existing cardiovascular disease); TRICC (Hebert et al., NEJM 1999). Platelet Transfusion AABB CPG (Kaufman et al., Ann Intern Med 2015; updated AABB/ICTMG 2025) - prophylactic threshold 10x10^3/uL for stable nonbleeding patients; higher counts require active bleeding or invasive procedure. (https://jamanetwork.com/journals/jama/fullarticle/2810145)
- Test vectors: 3/3 match
- Display/text catalog only (no computation). The transfusion-restriction messages are evidence-aligned: RBC reassessment at Hb>=7 matches the AABB 2023 / TRICC restrictive threshold (<7 g/dL), and the prophylactic-platelet reassessment above 25,000/uL is consistent with AABB's restrictive prophylactic threshold (10k) plus procedure/bleeding exceptions. Only nit is a cosmetic label-vs-body inconsistency in criterio_3 ('Hb>7' label vs 'Hb>=7' body) and criterio_4 ('Hb>6'); these do not affect logic (the buggy numeric enforcement lives in RULE-EFICIENCIA-002..004, not here). Wired as the active eficiencia_automatica payload. NB the same facade file also defines an unused sedation-content dict payload_trilha_eficiencia (naming hazard), not part of this rule.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/facade/trilha_eficiencia.py | 94-155 | 8166c07e | primary |
- Merged from: RULE-eficiencia-BE-01-016
- Related rules: RULE-EFICIENCIA-001, RULE-EFICIENCIA-002, RULE-EFICIENCIA-003, RULE-EFICIENCIA-004, RULE-EFICIENCIA-005, RULE-EFICIENCIA-006, RULE-EFICIENCIA-007, RULE-EFICIENCIA-008, RULE-EFICIENCIA-009, RULE-EFICIENCIA-010, RULE-EFICIENCIA-011

## Notes
NAMING HAZARD - the SAME facade file also defines a module-level dict payload_trilha_eficiencia (lines 1-91) whose content is SEDATION/analgesia (overdose de sedoanalgesia, BNM, PRIS, dor moderada/intensa, TRE), identical to the sedacao module dict; it is mislabeled/unused for efficiency (belongs conceptually to cluster 'sedacao'). Only get_payload_trilha_eficiencia() (this rule) is wired as eficiencia_automatica and imported by the v3 model. This catalog is the alert-text half of criteria RULE-EFICIENCIA-002..011.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
