# BACKEND_FRONTEND_GAP_MAP.md — IntensiCare

> **Auditoria de Gap Frontend↔Backend**
> **Data:** 2026-07-07
> **Agente:** Niemeyer (System Architect)
> **Risk Level:** L1 (read-only analysis)
> **Status:** ✅ COMPLETO — 4 fases executadas

---

## Resumo Executivo

A auditoria cruzou **1,029 regras clínicas** do legado (27 clusters YAML) contra o backend `src/intensicare/` (12 domain services, 11 API routers, 28 endpoints) e o frontend `frontend-v2/` (13 páginas, 23 funções API). 

**Resultado: 96% dos domínios clínicos têm gaps significativos.** Apenas 1 domínio (sinais-vitais) está completamente integrado. O produto está funcional como plataforma de alertas genéricos, mas **não entrega valor clínico específico** em 12 domínios críticos que estão completamente ausentes do backend e frontend.

### Números-Chave

| Métrica | Valor |
|---------|-------|
| Domínios analisados | 27 |
| Regras do legado | 1,029 |
| **Gaps BLOCKER** | **12 domínios (270 regras)** |
| **Gaps MAJOR** | **11 domínios (604 regras)** |
| Gaps MINOR | 3 domínios (111 regras) |
| Completamente integrado | 1 domínio (44 regras) |
| Endpoints backend não consumidos | 6 |
| Features frontend mockadas | 4 |
| Esforço total estimado | **55-75 semanas-dev** |

---

## 1. Matriz de Cobertura por Domínio (27 domínios)

### 🔴 BLOCKER — Zero Backend + Zero Frontend (12 domínios, 270 regras)

| # | Domínio | Regras | Service | API | Frontend | Esforço |
|---|---------|--------|---------|-----|----------|---------|
| 1 | **trilhas-engine** | 18 | — | — | — | XL |
| 2 | **balanco-hidrico** | 64 | domain_fluid_balance.py ⚠️ | — | — | XL |
| 3 | **prescricao** | 43 | — | — | — | XL |
| 4 | **documentacao-faturamento** | 40 | — | — | — | XL |
| 5 | **estabilidade** | 27 | — | — | — | XL |
| 6 | **ventilacao** | 27 | domain_respiratory.py ⚠️ | — | — | XL |
| 7 | **eficiencia** | 12 | — | — | — | XL |
| 8 | **piora-clinica** | 13 | — | — | — | XL |
| 9 | **nutricao** | 11 | — | — | — | L |
| 10 | **profilaxia** | 8 | — | — | — | L |
| 11 | **equilibrio** | 4 | domain_fluid_balance.py ⚠️ | — | — | L |
| 12 | **antimicrobiano** | 3 | — | — | — | L |

> ⚠️ = Domain service existe mas cobre apenas aspecto parcial (ex: fluid_balance cobre I/O mas não pathway Equilibrio)

### ⚠️ MAJOR — Backend Existe, Frontend Parcial/Ausente (11 domínios, 604 regras)

| # | Domínio | Regras | Service | API | Frontend | Esforço |
|---|---------|--------|---------|-----|----------|---------|
| 13 | **sepse** | 101 | domain_sepsis.py ✅ | alerts API (genérico) | alert-triage (genérico) | L |
| 14 | **evolucoes** | 81 | — | — | — | XL |
| 15 | **movimentacao-adt** | 74 | domain_movimentacao.py ✅ | — | — | XL |
| 16 | **auth-usuarios** | 68 | — | auth API ✅ | login/register/admin ✅ | M |
| 17 | **tenancy-organizacao** | 53 | domain_tenancy.py ✅ | — | — | L |
| 18 | **formularios-clinicos** | 49 | — | clinical-forms API ✅ | clinical-forms page ✅ | XL |
| 19 | **comunicacao** | 47 | domain_comunicacao.py ✅ | — | — | L |
| 20 | **auditoria-logs** | 37 | — | — | — | L |
| 21 | **cadastros-ui** | 35 | — | — | — | L |
| 22 | **indicadores-etl** | 31 | — | dashboard API ✅ | dashboard page ✅ | L |
| 23 | **sedacao** | 28 | domain_pharmaco_delirium.py ✅ | clinical-forms API ✅ | clinical-forms page ✅ | L |

### 🟡 MINOR — Cobertura Quase Completa (3 domínios, 111 regras)

| # | Domínio | Regras | Service | API | Frontend | Esforço |
|---|---------|--------|---------|-----|----------|---------|
| 24 | **operacional-infra** | 64 | domain_operacional.py ✅ | health API ✅ | — | S |
| 25 | **alertas** | 29 | domain_alertas.py ✅ | alerts API ✅ | alert-triage/routing ✅ | S |
| 26 | **clinical-scoring** | 18 | sofa/mews/news2 ✅ | dashboard API ✅ | dashboard page ✅ | M |

### 🟢 NONE — Totalmente Integrado (1 domínio, 44 regras)

| # | Domínio | Regras | Service | API | Frontend | Esforço |
|---|---------|--------|---------|-----|----------|---------|
| 27 | **sinais-vitais** | 44 | vitals.py ✅ | vitals API ✅ | patient dashboard ✅ | — |

---

## 2. Top 10 Gaps por Severidade (Ordenado para Ação)

| # | Severidade | Domínio | Regras | Esforço | Ação Recomendada |
|---|-----------|---------|--------|---------|-----------------|
| 1 | 🔴 BLOCKER | **trilhas-engine** | 18 | XL | Projetar engine de care pathways — o core differentiator do produto. Motor de elegibilidade, transições de estado, protocolos interativos. Impacto: diferenciação competitiva zero sem isso. |
| 2 | 🔴 BLOCKER | **balanco-hidrico** | 64 | XL | Expor domain_fluid_balance.py via API REST dedicada + dashboard de balanço hídrico com gráficos de I/O. |
| 3 | 🔴 BLOCKER | **prescricao** | 43 | XL | Módulo completo de prescrição: domain_prescricao.py, API REST, interface de administração de medicamentos. |
| 4 | ⚠️ MAJOR | **sepse** | 101 | L | Criar dashboard dedicado de sepse com visualização de critérios maiores/menores e timeline de confirmação (lactato, culturas). Backend já robusto — falta UI específica. |
| 5 | 🔴 BLOCKER | **documentacao-faturamento** | 40 | XL | Módulo Glosa Zero: 16 critérios de correção, motor de regras, API REST. |
| 6 | 🔴 BLOCKER | **ventilacao** | 27 | XL | Expor domain_respiratory.py via API + painel de parâmetros ventilatoriais com gráficos de tendência. |
| 7 | 🔴 BLOCKER | **estabilidade** | 27 | XL | Domain + API + dashboard de estabilidade hemodinâmica com 27 critérios. |
| 8 | ⚠️ MAJOR | **movimentacao-adt** | 74 | XL | Módulo de movimentação de pacientes (admissão/transferência/alta) com domain_movimentacao.py e UI. |
| 9 | ⚠️ MAJOR | **evolucoes** | 81 | XL | Motor de evoluções clínicas com templates, versionamento e timeline do paciente. |
| 10 | 🔴 BLOCKER | **piora-clinica** | 13 | XL | Sistema de detecção de piora clínica com 13 critérios de pontuação graduada. |

---

## 3. Endpoints Não Consumidos (Backend → Frontend)

Dos 28 endpoints REST expostos, **6 não têm consumidor frontend**:

| # | Endpoint | Método | Arquivo | Notas |
|---|----------|--------|---------|-------|
| 1 | `/api/v1/alerts/{id}/trace` | GET | api/v1/alerts.py:236 | Backend retorna trace completo do alerta; útil para debugging clínico |
| 2 | `/vitals` | POST | api/vitals.py:20 | Ingestão de sinais vitais — esperado (HL7/FHIR, não UI) |
| 3 | `/patients/{mpi_id}/status` | GET | api/patients.py:19 | Frontend usa `/detail` em vez de `/status` — schemas diferentes |
| 4 | `/api/v1/thresholds/{id}` | GET | api/thresholds.py:88 | Fetch de threshold único — sem consumer |
| 5 | `/api/v1/thresholds/{id}` | DELETE | api/thresholds.py:218 | Delete de threshold — sem consumer |
| 6 | `presence.updated` (WS) | Event | api/v1/ws.py:232 | Evento de presença documentado mas sem subscriber frontend |

### Features Mockadas no Frontend (Frontend → Backend)

| # | Feature | Arquivo | Substituir por |
|---|---------|---------|---------------|
| 1 | Alert Routing Rules (save/load) | app/alert-routing/page.tsx | `setTimeout` → endpoint REST de configuração de roteamento |
| 2 | Patient List (handoff) | app/handoff/page.tsx | `MOCK_PATIENTS` → GET /api/v1/patients |
| 3 | Clinical Forms — Patient Selector | app/clinical-forms/page.tsx | `MOCK_PATIENTS` → GET /api/v1/patients |
| 4 | SSE `/api/v1/events/stream` | lib/websocket.ts | Frontend espera SSE mas backend não implementa — WS funciona |

### Discrepâncias de Path

| # | Backend | Frontend | Issue |
|---|---------|----------|-------|
| D1 | `GET /patients/{mpi_id}/status` | `GET /api/v1/patients/{mpi_id}/detail` | Schemas diferentes (PatientStatusResponse vs PatientDetailResponse) |
| D2 | `POST /vitals` (sem prefix) | — | Inconsistência: vitals router sem prefixo `/api/v1` |
| D3 | `POST /api/clinical-forms` — `form_type` | Frontend envia `mpiId`/`formId` | Schema mismatch |

---

## 4. Ordem Recomendada de Implementação

### Sprint 1-2: Quick Wins (Esforço L, Alto Impacto Clínico)
1. **sepse** — Dashboard dedicado (back-end robusto, só falta UI)
2. **antimicrobiano** — 3 regras, módulo pequeno mas clinicamente relevante
3. **profilaxia** — 8 regras, bundles de prevenção

### Sprint 3-4: Domínios com Service Parcial (Esforço L-M)
4. **nutricao** — 11 regras, baixa complexidade
5. **equilibrio** — Expansão do domain_fluid_balance existente
6. **comunicacao** — domain_comunicacao.py já existe
7. **tenancy-organizacao** — domain_tenancy.py já existe
8. **auditoria-logs** — Modelo AuditTrail implementado, falta API de consulta

### Sprint 5-8: Domínios Complexos (Esforço XL)
9. **trilhas-engine** — O MAIS CRÍTICO. Care pathway engine é o produto.
10. **balanco-hidrico** — 64 regras, dashboard de I/O
11. **ventilacao** — 27 regras, parâmetros ventilatoriais
12. **estabilidade** — 27 regras, hemodinâmica

### Sprint 9-12: Módulos Grandes (Esforço XL)
13. **movimentacao-adt** — 74 regras
14. **prescricao** — 43 regras
15. **evolucoes** — 81 regras
16. **documentacao-faturamento** — 40 regras

### Backlog: Melhorias
17. **cadastros-ui** — 35 regras
18. **formularios-clinicos** — Expandir além de RASS/CAM-ICU
19. **indicadores-etl** — Portar fórmulas do legado
20. **eficiencia** — 12 regras, stewardship
21. **piora-clinica** — 13 regras

---

## 5. Estimativa de Esforço por Sprint

| Fase | Sprints | Domínios | Esforço Estimado |
|------|---------|----------|-----------------|
| Quick Wins | 1-2 | 3 (sepse, antimicrobiano, profilaxia) | 3-5 semanas-dev |
| Parciais | 3-4 | 5 (nutricao, equilibrio, comunicacao, tenancy, auditoria) | 8-12 semanas-dev |
| Críticos | 5-8 | 4 (trilhas-engine, balanco-hidrico, ventilacao, estabilidade) | 20-28 semanas-dev |
| Grandes | 9-12 | 4 (movimentacao, prescricao, evolucoes, documentacao) | 16-22 semanas-dev |
| Melhorias | Backlog | 7 restantes | 8-12 semanas-dev |
| **Total** | **~12 sprints** | **23 domínios (excluindo 4 já cobertos)** | **55-75 semanas-dev** |

> ⚠️ Estimativas assumem 2-3 devs fullstack. Trilhas-engine sozinho pode consumir 8-12 semanas de um time dedicado.

---

## 6. Riscos e Recomendações

### Riscos Críticos
| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| **Trilhas-engine é o core differentiator** e está completamente ausente | Perda de valor do produto — a plataforma atual é "genérica" sem care pathways | Priorizar como Sprint 5-8; design review com clinicians antes de implementar |
| **12 domínios BLOCKER** sem qualquer implementação | Time pode levar 3-6 meses para cobrir só os críticos | Sequenciar por impacto clínico, não por contagem de regras |
| **Modelo de severidade diferente** (watch/urgent/critical vs VERMELHO/AMARELO/NEUTRO) | Migração de legado pode causar falsos positivos/negativos | Mapear equivalência e rodar validação com dados históricos |
| **Schema mismatch** em clinical-forms e patients | Integração quebrada em produção | Corrigir antes de adicionar novas features |

### Recomendações Estratégicas
1. **NÃO implementar todos os 27 domínios.** Priorizar por valor clínico: sepse, trilhas-engine, ventilacao, balanco-hidrico.
2. **Criar ADRs** para cada domínio BLOCKER antes de implementar — documentar decisões de arquitetura.
3. **Estabelecer baseline de contratos** (OpenAPI) para novos endpoints antes do desenvolvimento.
4. **Corrigir os 4 mocks do frontend** em paralelo com novos desenvolvimentos.
5. **Unificar schema** de pacientes: decidir entre `/status` e `/detail` e deprecated o não usado.

---

## 7. Artefatos Gerados

| Artefato | Localização | Descrição |
|----------|-------------|-----------|
| RECON_MAP.md | `docs/audit/RECON_MAP.md` | Baseline do território — 27 clusters, 12 services, 11 APIs, 13 páginas |
| GAP_DOMAIN_clinico_core.yaml | `docs/audit/GAP_DOMAIN_clinico_core.yaml` | Análise de 9 domínios clínicos (641 linhas) |
| GAP_DOMAIN_cuidados_admin.yaml | `docs/audit/GAP_DOMAIN_cuidados_admin.yaml` | Análise de 9 domínios de cuidados/admin (327 linhas) |
| GAP_DOMAIN_infra_gov.yaml | `docs/audit/GAP_DOMAIN_infra_gov.yaml` | Análise de 9 domínios de infra/governança (499 linhas) |
| ENDPOINT_COVERAGE_MATRIX.md | `docs/audit/ENDPOINT_COVERAGE_MATRIX.md` | Matriz 28×23 endpoints ↔ consumidores |
| **BACKEND_FRONTEND_GAP_MAP.md** | `docs/audit/BACKEND_FRONTEND_GAP_MAP.md` | **Este relatório — consolidação final** |
| HANDOFF.md | `docs/audit/HANDOFF.md` | Handoff package para times downstream |

---

## 8. Governança

### Autoavaliação (Architecture Evaluation Loop)

| Dimensão | Score (1-5) | Evidência |
|----------|-------------|-----------|
| **Cobertura** | 5 | 27/27 domínios analisados com evidência de arquivo:linha |
| **Precisão** | 4 | Cross-validation confirmou claims críticas (trilhas-engine = zero hits); pequenas variações entre subagentes em classificação |
| **Acionabilidade** | 5 | Todo gap tem ação específica + esforço + ordem de prioridade |
| **Security Awareness** | 4 | Modelo de auth, admin-only endpoints, e audit trail identificados; LGPD/HIPAA não profundamente analisados (fora do scope L1) |
| **Governance Readiness** | 5 | HANDOFF.md, ADRs sugeridos, baseline de contratos recomendada |

**Score Médio:** 4.6/5.0

### Gate: GO ✅

O relatório está completo, verificável e acionável. Pode ser consumido por:
- **parreira** (DevOps) — para planejar infra de novos serviços
- **Coding agents** — para implementar domínios na ordem recomendada
- **Product team** — para priorização de roadmap
- **QA agents** — para planejar testes de integração nos novos endpoints
