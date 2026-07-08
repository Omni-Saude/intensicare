# PROMPT.md — Parreira (Sprint 5-8 Core Critical Backend)

> **De:** Niemeyer → **Para:** parreira
> **Data:** 2026-07-07
> **Contratos:** `docs/contracts/` (Niemeyer produz em paralelo)
> **Baseline:** `docs/audit/PLANS_SPRINT_5_8.md`

---

## Mission

Implementar **4 novos domain services** para os domínios críticos do IntensiCare: **trilhas-engine** (care pathway engine), **ventilacao** (parâmetros ventilatorios), **estabilidade** (hemodinâmica), **piora-clinica** (deterioração clínica). Estes 4 domínios são o **core do produto** — sem eles, a plataforma é genérica.

## Context

O gap audit revelou que `trilhas-engine` é o maior BLOCKER: 18 regras de care pathways do legado, ZERO implementação no novo backend. Os outros 3 domínios têm regras extraídas mas sem serviços.

Stack: Python 3.12, FastAPI, SQLAlchemy async, PostgreSQL 16 + TimescaleDB, Redis, ARQ.

## Domínios

### 1. Trilhas-Engine (18 regras) — ⭐ PRIORIDADE MÁXIMA
**O que é:** Motor de care pathways (protocolos clínicos interativos). Elegibilidade por tipo de leito, transições de estado, critérios de entrada/saída, tracking de adesão.

**Arquivos:**
- `services/domain_trilhas_engine.py` — motor de pathways
- `models/pathway.py` — SQLAlchemy models (Pathway, PathwayState, PathwayCriteria, PatientPathway)
- `api/v1/pathways.py` — REST endpoints

**Endpoints (sugeridos):**
- `GET /api/v1/pathways` — listar pathways disponíveis
- `GET /api/v1/pathways/{id}` — detalhe do pathway com critérios
- `POST /api/v1/patients/{mpi_id}/pathways` — inscrever paciente em pathway
- `GET /api/v1/patients/{mpi_id}/pathways` — pathways ativos do paciente
- `PUT /api/v1/patients/{mpi_id}/pathways/{id}/criteria` — atualizar critérios
- `GET /api/v1/patients/{mpi_id}/pathways/{id}/progress` — progresso e status

### 2. Ventilacao (27 regras)
**Service:** Expandir `domain_respiratory.py` existente ou criar `domain_ventilacao.py`
**Endpoints:** `GET /api/v1/patients/{mpi_id}/ventilation` — parâmetros atuais + tendência
**Dados:** modo ventilatório, FiO₂, PEEP, VC, FR, Pplat, driving pressure, PaO₂/FiO₂

### 3. Estabilidade (27 regras)
**Service:** `services/domain_estabilidade.py` — 27 critérios hemodinâmicos
**Endpoints:** `GET /api/v1/patients/{mpi_id}/stability` — status + critérios

### 4. Piora-Clinica (13 regras)
**Service:** `services/domain_piora_clinica.py` — scoring graduado (0, 1+, 1-, 3+, 3-)
**Endpoints:** `GET /api/v1/patients/{mpi_id}/deterioration` — score + tendência

## Regras

- Stack e padrões: seguir contratos OpenAPI (Niemeyer), audit trail obrigatório, JWT auth, resposta `{ items: [], total: N }`
- Testes: `tests/test_domain_trilhas_engine.py` etc.
- Migrations: Alembic para cada modelo novo

## Métricas

| Domínio | Service | Model | API | Tests |
|---------|---------|-------|-----|-------|
| trilhas-engine | ✅ | ✅ | 6 endpoints | ✅ |
| ventilacao | ✅ | — | 1 endpoint | ✅ |
| estabilidade | ✅ | ✅ | 1 endpoint | ✅ |
| piora-clinica | ✅ | ✅ | 1 endpoint | ✅ |
