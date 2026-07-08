# HANDOFF.md — Parreira (DevOps Team Orchestrator)

> **De:** Niemeyer (System Architect) → **Para:** parreira
> **Data:** 2026-07-07
> **Projeto:** IntensiCare — Backend Sprint: Novos Domínios + Correções de Gap
> **Risk Level:** L2 (novos endpoints, não afeta produção existente)
> **Contratos:** `docs/contracts/antimicrobial-openapi.yaml`, `docs/contracts/prophylaxis-openapi.yaml`

---

## Envelope de Missão

### Goal
Implementar **2 novos domain services** com APIs REST (Antimicrobiano Stewardship + Profilaxia Bundles), **corrigir 6 endpoints sem consumer**, **resolver 4 features mockadas** no frontend, e **corrigir 3 path discrepancies** identificados no gap audit.

### Context
O Sprint 1-2 (product-design-orchestrator) entregou o frontend para Sepse, Antimicrobiano e Profilaxia. O backend da Sepse já existe. Antimicrobiano e Profilaxia usam **mock data** — precisam de backend real.

O gap audit (`docs/audit/BACKEND_FRONTEND_GAP_MAP.md`) identificou gaps adicionais que precisam de correção:
- 6 endpoints backend sem consumidor frontend
- 4 features frontend mockadas (precisam de APIs reais)
- 3 path/schema mismatches

### Constraints
- Stack: Python 3.12, FastAPI, SQLAlchemy async, PostgreSQL 16 + TimescaleDB, Redis, ARQ
- Padrão existente: routers em `src/intensicare/api/v1/`, services em `src/intensicare/services/`, models em `src/intensicare/models/`
- Autenticação: JWT via `intensicare.auth.dependencies.get_current_user`
- Audit trail: toda mutação → `AuditTrail` (OBRIGATÓRIO)
- Formato de resposta: wrapping `{ items: [...], total: N }` (padrão AUDIT-007)
- Idempotência: endpoints POST devem suportar idempotency key
- Contratos: seguir `docs/contracts/*.yaml` EXATAMENTE

### Done When
- [ ] `domain_antimicrobiano.py` — 12 critérios, scoring VERMELHO/AMARELO/NEUTRO, endpoints REST conforme contrato
- [ ] `domain_profilaxia.py` — 5 bundles (20 critérios), scoring, endpoints REST conforme contrato
- [ ] `models/antimicrobial.py` — SQLAlchemy model para AntimicrobialAssessment
- [ ] `models/prophylaxis.py` — SQLAlchemy model para ProphylaxisBundle
- [ ] `api/v1/antimicrobial.py` — router com endpoints do contrato
- [ ] `api/v1/prophylaxis.py` — router com endpoints do contrato
- [ ] 4 features mockadas resolvidas (alert-routing API, handoff patient list API, clinical-forms patient lookup, SSE endpoint)
- [ ] 3 path discrepancies corrigidos (patients status/detail, vitals prefix, clinical-forms schema)
- [ ] Testes: `tests/test_domain_antimicrobiano.py`, `tests/test_domain_profilaxia.py`
- [ ] Migration: Alembic migration para novas tabelas
- [ ] `HANDOFF.yaml` atualizado com status

### Scope Boundary
- ✅ DENTRO: `src/intensicare/services/domain_antimicrobiano.py`, `domain_profilaxia.py`, models, API routers, migrations, testes
- ❌ FORA: `frontend-v2/`, `docs/rules/`, design tokens

---

## Tarefas (Ordem de Execução)

### BLOCO A — Novos Domínios (2 domain services)

#### A1. Antimicrobial Stewardship
| O que | Onde | Contrato |
|-------|------|----------|
| Model | `src/intensicare/models/antimicrobial.py` | Schema em `docs/contracts/antimicrobial-openapi.yaml` |
| Service | `src/intensicare/services/domain_antimicrobiano.py` | 12 critérios × 7 categorias, scoring 0-12 |
| API | `src/intensicare/api/v1/antimicrobial.py` | 4 endpoints (list, create, get, criteria catalog) |
| Test | `tests/test_domain_antimicrobiano.py` | Cobertura dos 12 critérios + scoring |

**Lógica de scoring:**
```
score = count(criteria where met == false)  // não-conformidades
severity = NEUTRO (0-3), AMARELO (4-7), VERMELHO (8-12)
```

#### A2. Prophylaxis Bundles
| O que | Onde | Contrato |
|-------|------|----------|
| Model | `src/intensicare/models/prophylaxis.py` | Schema em `docs/contracts/prophylaxis-openapi.yaml` |
| Service | `src/intensicare/services/domain_profilaxia.py` | 5 bundles, 20 critérios total |
| API | `src/intensicare/api/v1/prophylaxis.py` | 5 endpoints (list bundles, get bundle, update, criteria catalog × 5) |
| Test | `tests/test_domain_profilaxia.py` | Cobertura dos 5 bundles |

**Lógica de status:**
```
bundle.status = complete (100%), partial (>0% <100%), pending (0%), na (not applicable)
overall = all_complete (todos 100%), partial, all_pending (todos 0%)
```

### BLOCO B — Correções de Gap (6 endpoints + 4 mocks)

#### B1. Endpoints sem Consumer → Expor ou Deprecated
| Endpoint | Ação |
|----------|------|
| `GET /api/v1/alerts/{id}/trace` | ✅ Já existe. Documentar para frontend usar. |
| `POST /vitals` | ✅ Já existe. É HL7/FHIR — OK não ter consumer UI. |
| `GET /patients/{mpi_id}/status` | Corrigir: adicionar endpoint `/api/v1/patients/{mpi_id}/detail` com PatientDetailResponse OU unificar |
| `GET /api/v1/thresholds/{id}` | Adicionar função `fetchThreshold(id)` no `lib/api.ts` OU manter só list |
| `DELETE /api/v1/thresholds/{id}` | Adicionar `deleteThreshold(id)` no frontend OU manter admin-only |
| `presence.updated` (WS) | Adicionar subscriber no frontend OU deprecated do backend |

#### B2. Features Mockadas → APIs Reais
| Mock | Solução |
|------|---------|
| Alert Routing (save/load) | Criar `POST/GET /api/v1/alert-routing` com modelo de regras de roteamento |
| Handoff patient list | Usar `GET /api/v1/dashboard` (já existe) em vez de `MOCK_PATIENTS` |
| Clinical Forms patient selector | Usar `GET /api/v1/dashboard` (já existe) em vez de `MOCK_PATIENTS` |
| SSE `/api/v1/events/stream` | Implementar SSE endpoint no backend OU remover fallback do frontend |

#### B3. Path/Schema Mismatches
| Discrepancy | Correção |
|-------------|----------|
| `GET /patients/{id}/status` vs `/detail` | Unificar: manter `/api/v1/patients/{mpi_id}/detail` com PatientDetailResponse, deprecated `/status` |
| `POST /vitals` sem prefix `/api/v1` | Adicionar prefixo `/api/v1` ao router de vitals |
| `POST /api/clinical-forms` schema mismatch | Frontend envia `mpiId`/`formId`; backend espera `form_type`. Alinhar contrato. |

### BLOCO C — Migrations + CI
| Tarefa | Detalhe |
|--------|---------|
| Alembic migration | `alembic revision --autogenerate -m "add antimicrobial and prophylaxis tables"` |
| CI pipeline | Adicionar novos testes ao `pytest` suite |
| Health check | Atualizar `api/v1/health.py` para incluir novas tabelas no DB check |

---

## Regras de Ouro (Agentic-Loop — DevOps)

1. **PLANS.md antes de codar.** Milestones de ≤3 arquivos. Rollback por milestone.
2. **Delegate com skills pré-carregadas.** Carregar `tdd-london-swarm`, `ops-cicd-github`, `security-manager`, `production-validator` antes de cada `delegate_task`.
3. **Verificar cada milestone.** `pytest`, `alembic upgrade head`, health check. Agente DIFERENTE cross-valida.
4. **Gatekeeper ≠ implementador.** `security-manager` + `production-validator` independentes.
5. **NUNCA deployar sem migration.** Alembic primeiro, deploy depois.
6. **Audit trail obrigatório.** Toda mutação → `AuditTrail(model, action, user_id, details)`.
7. **Estado no filesystem.** `HANDOFF.yaml`, `PLANS.md`, `RUNBOOK.md`.

## Anti-Patterns (DevOps)
- ❌ Alterar schema de tabela existente sem migration
- ❌ Endpoint sem audit trail
- ❌ Pular testes
- ❌ Deploy sem gatekeeper
- ❌ Hardcoded secrets (usar `intensicare.core.secrets`)
- ❌ Ignorar contratos OpenAPI — seguir EXATAMENTE

---

## Métricas de Sucesso

| Métrica | Target |
|---------|--------|
| Novos domain services | 2 (antimicrobiano + profilaxia) |
| Novos endpoints REST | 9 (4 antimicrobial + 5 prophylaxis) |
| Mocked features resolvidas | 4 → APIs reais |
| Path mismatches corrigidos | 3 |
| Testes | `pytest` passa com ≥80% coverage nos novos services |
| Migration | `alembic upgrade head` sem erros |
| Contratos | Endpoints conformam 100% com OpenAPI specs |
