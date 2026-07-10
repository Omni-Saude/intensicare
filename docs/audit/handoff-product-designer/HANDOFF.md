# HANDOFF.md — Reconstrução do Frontend IntensiCare v3

**De:** Niemeyer (System Architect)  
**Para:** Product-Design-Orchestrator  
**Data:** 2026-07-09  
**Versão:** 2.0.0  
**Prioridade:** Crítica  
**Tipo:** Rebuild 100% novo de frontend  
**Princípio:** UX precede design. Jornada do intensivista é o fator organizador.  

---

## Envelope da Tarefa

| Campo | Valor |
|-------|-------|
| **Goal** | Construir frontend 100% novo, do zero, orientado à jornada do intensivista e às trilhas clínicas do backend. 6 páginas core. Trilha Sepse como MVP benchmark. |
| **Context** | IntensiCare: plataforma de alertas proativos para UTI. Backend: 9 trilhas YAML, motor de avaliação, alertas. Frontend v2: 33 páginas com erro de UX (domínios isolados). Arquit. correta: trilhas → scores → alertas. |
| **Constraints** | Next.js 15 + Tailwind + shadcn/ui + Recharts. Backend NÃO muda (spec canônica). NADA do v2 é copiado. CSP WebSocket. |
| **Done When** | 6 páginas 100% novas e funcionais. Jornada Dashboard → Patient → Pathway em ≤2 cliques. Trilha Sepse benchmark. 8 trilhas replicando padrão. Zero páginas standalone. |
| **Risk Level** | L2 (construção de novo frontend, sem alteração de backend) |
| **Architecture Scope** | FRONTEND APENAS. Backend é spec canônica — NÃO propor mudanças. |

---

## Princípios de UX (Leia Antes de Codar)

1. **Cada componente responde a uma pergunta da jornada.** "Este componente ajuda o intensivista a decidir?" Se não, não existe.
2. **Densidade com clareza.** UTI não é dashboard de marketing. Muita informação em pouco espaço, severidade codificada por cor E posição.
3. **≤2 cliques para qualquer informação crítica.** Dashboard → Patient → Pathway.
4. **Severidade é o atributo visual primário.** Cor (verde/âmbar/laranja/vermelho) + posição + movimento (pulsante se critical).
5. **Modo escuro como padrão.** UTI operate 24h. Luzes baixas à noite.

---

## Fases de Implementação

| Fase | Dias | O que construir | Critério de Done |
|------|------|----------------|------------------|
| **M0** | 2 | Projeto Next.js, sistema de design CSS, API client (tipos dos schemas), middleware auth, AppShell | `npm run build` passa, login funcional, API client cobre todos os endpoints |
| **M1** | 3 | Dashboard: BedGrid, BedCard, PathwayBadges, ScorePair, WebSocket | Grid de leitos com badges de trilhas coloridos |
| **M2** | 3 | Patient Detail: header, vitals, scores, ActivePathways, alerts | Todas as trilhas ativas visíveis em UMA tela |
| **M3** | 4 | Pathway View — Sepse: StateFlow, CriteriaList, Recommendations, TransitionHistory | Trilha sepse navegável com 7 critérios e recomendações SSC-2021 |
| **M4** | 3 | Alert Triage: FilterBar, AlertTable, QuickActions, AlertTrace | Alertas rastreáveis até critério/threshold |
| **M5** | 2 | Pathway Catalog: grid, YAML viewer, tester | 9 trilhas no catálogo |
| **M6** | 2 | Admin: usuários, thresholds, tenancy | CRUD funcional |
| **M7** | 6 | 8 trilhas restantes (sem código novo — só dados) | 9 trilhas com mesma experiência |
| **M8** | 3 | Integração: E2E, WCAG 2.1 AA, performance, responsividade, **substituição do v2** | Métricas de sucesso + v2 arquivado |

---

## Fontes de Verdade (ÚNICAS)

1. **Schemas OpenAPI:** `docs/contracts/pathways-openapi.yaml` — tipos TypeScript derivados daqui
2. **Definições YAML:** `_work/alerts/pathways/sepse.yaml` (e demais) — estrutura de dados
3. **Jornada do intensivista:** FRONTEND_REBUILD_PLAN.md § 1 — perguntas que cada página responde

---

## APIs para CONSUMIR

| Endpoint | Schema | Uso |
|----------|--------|-----|
| `GET /api/v1/dashboard` | `DashboardResponse` | M1 |
| `GET /api/v1/patients/{mpi_id}/detail` | `PatientDetailResponse` | M2 |
| `GET /api/v1/patients/{mpi_id}/pathways` | `{ items: PatientPathway[] }` | M2 |
| `GET /api/v1/patients/{mpi_id}/pathways/{pp_id}/progress` | `PathwayProgress` | M3, M7 |
| `GET /api/v1/pathways` | `{ items: Pathway[] }` | M5 |
| `GET /api/v1/pathways/{id}` | `Pathway` | M5 |
| `GET /api/v1/alerts` | `AlertListResponse` | M4 |
| `POST /api/v1/alerts/{id}/acknowledge` | `AlertInfo` | M4 |
| `POST /api/v1/alerts/{id}/escalate` | `AlertInfo` | M4 |
| `POST /api/v1/alerts/{id}/resolve` | `AlertInfo` | M4 |

---

## Pré-requisitos do Backend (validar antes do M0)

- [ ] JWT com claims `is_admin` e `role` OU endpoint `GET /api/v1/me`
- [ ] CSP permite WebSocket (`wss://` prod, `ws://localhost:8000` dev)
- [ ] `GET /patients/{mpi_id}/pathways` funcional (endpoint + dados)
- [ ] `GET /patients/{mpi_id}/pathways/{pp_id}/progress` funcional para sepse
- [ ] Endpoints 500 corrigidos (stability, ventilation)

---

## Decisões de Arquitetura

| ADR | Decisão |
|-----|---------|
| [ADR-0030](docs/adr/ADR-0030-frontend-pathway-architecture.md) | Arquitetura orientada a trilhas |
| [ADR-0031](docs/adr/ADR-0031-mvp-pathway-sepsis.md) | Sepse como MVP benchmark |
| [ADR-0032](docs/adr/ADR-0032-component-migration-strategy.md) | Construção 100% do zero — UX-first |
| [ADR-0033](docs/adr/ADR-0033-pathway-view-generic-pattern.md) | Pathway View genérico data-driven |
| [ADR-0034](docs/adr/ADR-0034-realtime-websocket-strategy.md) | WebSocket com fallback polling |

---

## Métricas de Sucesso

- Dashboard < 2s com 20+ pacientes
- Jornada Dashboard → Patient → Pathway ≤ 2 cliques
- Todas as trilhas de 1 paciente em 1 tela
- Zero páginas standalone de domínio
- 100% alertas rastreáveis
- WCAG 2.1 AA
- Responsivo tablet + desktop

---

## Contatos

| Área | Quem |
|------|------|
| Arquitetura | Niemeyer |
| Backend/DevOps | Parreira |
| Dúvidas clínicas | Rodrigo Aquino |

---

## Referências

- [FRONTEND_REBUILD_PLAN.md](FRONTEND_REBUILD_PLAN.md) — blueprint completo
- [PLANS.md](PLANS.md) — milestones e dependências
- [DESIGN_BRIEF.yaml](DESIGN_BRIEF.yaml) — especificações estruturadas
- [HANDOFF.yaml](HANDOFF.yaml) — estado canônico
- [PROMPT.md](PROMPT.md) — prompt standalone
