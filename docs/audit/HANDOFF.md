# HANDOFF.md — Contract for Downstream Agents and Teams

> **Gerado por:** Niemeyer (System Architect)
> **Data:** 2026-07-07
> **Projeto:** IntensiCare — Auditoria de Gap Frontend↔Backend

---

## backend_frontend_gap_audit

### Escopo
Auditoria completa de cobertura backend↔frontend do IntensiCare v2. 27 domínios clínicos (1,029 regras do legado) cruzados contra `src/intensicare/` (12 services, 11 APIs, 28 endpoints) e `frontend-v2/` (13 páginas, 23 funções API).

### Resultado
- **12 BLOCKER** — zero implementação backend e frontend
- **11 MAJOR** — backend existe, frontend parcial/ausente
- **3 MINOR** — cobertura quase completa
- **1 NONE** — totalmente integrado (sinais-vitais)
- **6 endpoints** backend sem consumidor frontend
- **4 features** frontend mockadas
- **Esforço total:** 55-75 semanas-dev

### Artefatos
| Artefato | Path |
|----------|------|
| Relatório Consolidado | `docs/audit/BACKEND_FRONTEND_GAP_MAP.md` |
| RECON Territory Map | `docs/audit/RECON_MAP.md` |
| GAP Clínico Core | `docs/audit/GAP_DOMAIN_clinico_core.yaml` |
| GAP Cuidados+Admin | `docs/audit/GAP_DOMAIN_cuidados_admin.yaml` |
| GAP Infra+Gov | `docs/audit/GAP_DOMAIN_infra_gov.yaml` |
| Endpoint Coverage | `docs/audit/ENDPOINT_COVERAGE_MATRIX.md` |

### Próximos Passos (Ordem Recomendada)

#### Sprint 1-2 — Quick Wins
- [ ] **sepse**: Criar dashboard dedicado (backend robusto, só falta UI)
- [ ] **antimicrobiano**: Domain service + API + UI (3 regras)
- [ ] **profilaxia**: Domain service + API + UI (8 regras)

#### Sprint 3-4 — Domínios Parciais
- [ ] **nutricao**: 11 regras
- [ ] **equilibrio**: Expandir domain_fluid_balance.py
- [ ] **comunicacao**: API para domain_comunicacao.py
- [ ] **tenancy-organizacao**: API para domain_tenancy.py
- [ ] **auditoria-logs**: API de consulta de audit trail

#### Sprint 5-8 — Core Crítico
- [ ] **trilhas-engine**: Care pathway engine (O MAIS CRÍTICO)
- [ ] **balanco-hidrico**: API + dashboard de I/O
- [ ] **ventilacao**: API + painel de parâmetros ventilatoriais
- [ ] **estabilidade**: API + dashboard hemodinâmico

#### Correções Imediatas
- [ ] Corrigir schema mismatch em `POST /api/clinical-forms`
- [ ] Unificar `/patients/{id}/status` vs `/detail`
- [ ] Implementar SSE `/api/v1/events/stream` ou remover do frontend
- [ ] Substituir `MOCK_PATIENTS` em handoff e clinical-forms por API real

### Contatos
- **Arquiteto:** Niemeyer (System Architect Agent)
- **DevOps:** parreira (para planejamento de infra dos novos serviços)
- **Product:** Roadmap disponível no relatório consolidado

### Definition of Done (Arquitetural)
- [ ] ADR criado para cada novo domínio BLOCKER antes da implementação
- [ ] Contratos OpenAPI definidos para novos endpoints
- [ ] Testes de contrato (contract tests) entre novos endpoints e frontend
- [ ] Audit trail registrado em todas as mutações
- [ ] Thresholds configuráveis por tenant/unit para novos alertas
