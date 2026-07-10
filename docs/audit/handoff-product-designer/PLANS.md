# PLANS.md — Reconstrução do Frontend IntensiCare v3

**Gerado por:** Niemeyer (System Architect)  
**Data:** 2026-07-09  
**Fonte:** FRONTEND_REBUILD_HANDOFF.md (Parreira) + análise de evidência do repositório

---

## 1. Objetivo

Construir um novo frontend (v3) do zero, orientado a **trilhas clínicas (care pathways)**, com 6 páginas core. A trilha de **Sepse** serve como MVP/benchmark — as demais 8 trilhas replicam o padrão.

## 2. Milestones

| M# | Nome | Artefatos | Duração | Depende de |
|----|------|-----------|---------|------------|
| **M0** | Foundation | Projeto Next.js 15, Tailwind, shadcn/ui, tokens, lib/api.ts expandida, middleware | 2d | — |
| **M1** | Dashboard | BedGrid, PatientCard, WebSocket, filtro por unidade | 3d | M0 |
| **M2** | Patient Detail | PatientHeader, ActivePathways, VitalsChart, ScoreTimeline, AlertsList | 3d | M0 |
| **M3** | Pathway View — MVP (Sepse) | PathwayStateMachine, CriteriaPanel, CriteriaDetail, Recommendations, History | 4d | M2 |
| **M4** | Alert Triage | AlertTable, filtros, acknowledge/escalate/resolve, AlertTrace | 3d | M0 |
| **M5** | Pathway Catalog | Definições YAML, teste contra paciente | 2d | M0 |
| **M6** | Admin | Usuários, thresholds, tenancy, registro | 2d | M0 |
| **M7** | Trilhas restantes (8) | Renal, Resp, Ventilação, Equilíbrio, Nutrição, Profilaxia, Sedação, Delirium | 6d (0.75d cada) | M3 |
| **M8** | Integração, testes, polish, cleanup v2 | E2E, a11y, performance, responsividade, substituição do v2 | 3d | M1-M7 |

**Total estimado:** ~28 dias de desenvolvimento

## 3. Dependências entre Milestones

```
M0 (Foundation)
├── M1 (Dashboard) ─────────────────────────────────────────┐
├── M2 (Patient Detail) ──► M3 (Pathway MVP) ──► M7 (Demais)┐
├── M4 (Alert Triage) ───────────────────────────────────────┤
├── M5 (Pathway Catalog) ────────────────────────────────────┤
└── M6 (Admin) ──────────────────────────────────────────────┘
                                                              │
                                              M8 (Integração) ◄── todos
```

## 4. Riscos por Milestone

| Milestone | Risco | P×I | Mitigação |
|-----------|-------|-----|-----------|
| M0 | Endpoints 500/404 no backend | A×A | Corrigir antes de começar M0. Validar todos os endpoints das trilhas. |
| M2 | Patient Detail não mostra trilhas ativas (API `GET /patients/{mpi_id}/pathways` quebrada) | M×A | Testar endpoint no M0. Se não existir, priorizar criação. |
| M3 | Pathway View complexo demais (state machine visual) | A×M | Começar com versão simplificada: lista de estados + critérios. State machine visual é stretch. |
| M7 | 8 trilhas com nuances diferentes (cada YAML tem estrutura própria) | M×M | O M3 define o componente genérico. M7 é só configuração de dados. |
| M8 | A11y insuficiente para uso clínico real | M×A | WCAG 2.1 AA como critério de done desde o M0. |

## 5. Rollback por Milestone

| Milestone | Estratégia de Rollback |
|-----------|----------------------|
| M0 | Branch `feature/frontend-v3` isolada. Se falhar, descartar branch. |
| M1-M6 | Cada milestone é um PR contra `feature/frontend-v3`. Reverter PR. |
| M7 | Cada trilha é um commit separado. Reverter commit da trilha problemática. |
| M8 | Manter `frontend-v2` rodando em paralelo até M8 concluído. |

## 6. Approval Gates

| Gate | Quando | Quem | Critério |
|------|--------|------|----------|
| G0 | Após M0 | Arquiteto (Niemeyer) | Projeto compila, tokens carregam, middleware funcional, lib/api.ts cobre pathways |
| G1 | Após M3 (Pathway MVP) | Arquiteto + Médico | Trilha de sepse navegável: Dashboard → Patient → Pathway View com critérios visíveis |
| G2 | Após M8 | Arquiteto | Todas as 9 trilhas funcionais, zero páginas standalone, métricas de sucesso atingidas |

## 7. Ordem de Produção

1. `PLANS.md` ← **este arquivo**
2. `FRONTEND_REBUILD_PLAN.md` — blueprint completo
3. `docs/adr/ADR-0030-frontend-pathway-architecture.md`
4. `docs/adr/ADR-0031-mvp-pathway-sepsis.md`
5. `docs/adr/ADR-0032-component-migration-strategy.md`
6. `docs/adr/ADR-0033-pathway-view-generic-pattern.md`
7. `docs/adr/ADR-0034-realtime-websocket-strategy.md`
8. `HANDOFF.md` — envelope para Product-Design-Orchestrator
9. `DESIGN_BRIEF.yaml` — especificações estruturadas
10. `HANDOFF.yaml` — estado canônico
11. `PROMPT.md` — prompt standalone para o orchestrator

## 8. Estimativa de Esforço

**Tamanho:** XL (28 dias, 6 páginas, 9 trilhas, 5+ ADRs, handoff package completo)
