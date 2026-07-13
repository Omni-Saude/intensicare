# PROMPT — Validação E2E em Browser Real da Plataforma IntensiCare
## Interações Clínicas Reais no Chrome → Bugs Verdadeiros → Fixes com Gates

**De:** Product Owner (médico intensivista / code-owner)
**Para:** Orquestrador Hive-Mind (agente rainha — coordena, NUNCA coda)
**Data:** 2026-07-13
**Tipo:** Operação de validação comportamental + correção. RODAR a plataforma, USAR a plataforma como um intensivista usaria, ACHAR bugs verdadeiros, CORRIGIR com excelência técnica.
**Predecessor:** ciclo de auditoria+correção full-spectrum (`docs/audit/fullspectrum/FULLSPECTRUM_VERDICT.md`, GO-WITH-ISSUES 79.25). Este prompt valida o comportamento REAL pós-merge.

---

## ═══════ ENVELOPE ═══════

| Campo | Valor |
|-------|-------|
| **Goal** | Subir a plataforma completa localmente, executar uma bateria de interações clínicas reais em Chrome (browser de verdade, não só curl/testes), capturar TODO comportamento divergente do esperado com evidência forense (pageerror, console, network, screenshot), classificar bug-verdadeiro vs ausência-de-dado vs artefato-de-ambiente, e corrigir os bugs verdadeiros via swarm com gates independentes. |
| **Context** | Repo: `/Users/familia/intensicare` (branch `main`, pós PRs #40-#43). Stack: FastAPI+TimescaleDB+Redis / Next.js 16. 12 trilhas YAML declarativas, motor persistente com avaliação automática na ingestão, WS real-time, CSP nonce, sessão via refresh-cookie HttpOnly, ABAC clínico, CDS Hooks, projeção de deterioração. |
| **Constraints** | Fixes SÓ para bugs verdadeiros confirmados (reproduzidos 2×). Main é protegido: todo fix vai por branch→PR→review do owner. Orquestrador não coda. Sem workarounds — causa raiz sempre. |
| **Done When** | Relatório de comportamento com matriz interação→resultado→evidência; todos os bugs verdadeiros com fix em PR verde (ou justificativa de adiamento); re-execução da bateria completa passando. |
| **Risk Level** | L2 — roda serviços locais, escreve em dev DB (namespace DEMO), cria PRs. Sem produção, sem cloud. |

---

## ═══════ FASE 0 — BOOT DO STACK (você, ~15 min) ═══════

Suba e VERIFIQUE cada camada. Comandos conhecidos-bons desta base:

```bash
# 1. Infra (docker já existente na máquina)