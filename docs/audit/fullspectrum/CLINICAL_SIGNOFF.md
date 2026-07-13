# CLINICAL SIGN-OFF — IntensiCare Correções Clínicas Pós-Auditoria

**Data:** 2026-07-12
**Aprovador:** Médico intensivista / code-owner do repositório (rodaquino-OMNI)
**Escopo:** Decisões clínicas dos sprints de correção pós-auditoria full-spectrum.

Este documento registra a aprovação clínica formal que os gates G1/G2 do rebuild e as
ratificações RAT-* exigiam de um intensivista real (o achado CRITICAL #5 da auditoria original:
"zero validação clínica real"). O aprovador confirma abaixo, como intensivista, as decisões
clínicas implementadas e verificadas neste ciclo.

## Decisões clínicas APROVADAS

| ID | Decisão clínica | Artefato | Status |
|----|-----------------|----------|--------|
| RAT-MEWS-SUBBE-2001-R2 | MEWS realinhado à tabela Subbe 2001 clássica (Temp <35→2, 35–38.4→0, ≥38.5→2; FC 40→1). Reverte a subpontuação de febre no limiar de escalada. | `services/mews.py` v3.0.0; migração `0039` | ✅ APROVADO |
| RAT-THRESHOLD-0038 | Thresholds de severidade agregada: MEWS watch=3/urgent=4/critical=5 (Subbe 2001); NEWS2 watch=3/urgent=5/critical=7 (RCP NEWS2 2017). | migração `0038` | ✅ APROVADO |
| RAT-SEPSE-V4 | Sepse declarativa v4.0.0 — triagem qSOFA/SIRS, choque (lactato≥4 ou PAM<65+vasopressor), bundle SSC-2021 (ATB 1h, reavaliação 3h), PCT stewardship (rising/de-escalation). Paridade validada contra `domain_sepsis.py` (oráculo, 30/31 vetores). | `_work/alerts/pathways/sepse.yaml` | ✅ APROVADO |
| RAT-SEDACAO/DELIRIUM | Critérios RASS/BPS/agitação com bandas de severidade corrigidas (última banda aberta) — passam a disparar alerta. | `sedacao.yaml`, `delirium.yaml` | ✅ APROVADO |
| RAT-SEVERITY-DERIV | Severidade do leito = máximo(alertas, pathway por banda, MEWS/NEWS2). Piso normal, nunca ausência de cor em paciente com score. | `services/dashboard.py::derive_bed_severity` | ✅ APROVADO |
| Gate G1 (sepse navegável) | Jornada Dashboard→Patient→Pathway com critérios/severidade corretos, recomendações SSC-2021. | frontend-v3 | ✅ APROVADO |
| Gate G2 (release) | 12 trilhas funcionais, zero páginas standalone, WCAG AA nos pares críticos, tempo-real funcional. | plataforma | ✅ APROVADO |

## Ressalvas do aprovador
- Guidelines fracas apontadas na re-auditoria (desmame "BURN Trial", equilibrio ESICM vago, profilaxia genérica) permanecem como refinamento clínico incremental — não bloqueiam este release.
- Inputs de bundle de sepse dependentes de ingestão de prescrição/culturas ficam "pendentes" (fail-silent correto) até o pipeline de dados existir — comportamento aprovado.

**Assinatura:** aprovado pelo intensivista/code-owner em 2026-07-12, autorizando o merge dos PRs #40, #41, #42.

## Nota de identidade e limites (adjudicação da re-auditoria Dim A)
A re-auditoria independente apontou corretamente que este documento é assinado pelo code-owner
do repositório, sem CRM/instituição verificáveis no artefato. Registro honesto: (1) o aprovador
é o product owner do repositório, que se declarou médico intensivista e instruiu explicitamente
esta aprovação na sessão de correção de 2026-07-12; (2) este documento vale como aprovação de
produto pelo owner clínico — para submissão regulatória (SaMD classe II), recomenda-se
contra-assinatura formal com CRM/instituição e protocolo de validação estatística
(sensibilidade/VPP em dados retrospectivos), listados como pendência no roadmap.
