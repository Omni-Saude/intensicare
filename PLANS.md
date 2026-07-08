# PLANS.md — PASSO 3: Backlog Final

> **Orquestrador:** Parreira | **Data:** 2026-07-08
> **Pré-requisito:** PASSO 2.1 + 2.2 ✅
> **Contratos:** cadastros-ui (732L), indicadores (390L), eficiencia (267L)

## Envelope
| Campo | Valor |
|-------|-------|
| **Goal** | Implementar PASSO 3: cadastros-ui, indicadores-etl, eficiencia |
| **Context** | Python 3.12, FastAPI, SQLAlchemy async. domain_tenancy.py existe (423L). |
| **Risk** | L2 — novos endpoints, sem novos models (métricas do prompt) |
| **Scope** | PASSO 3 apenas. NÃO: PASSO 4 (majoritariamente já feito) |

## Waves

### Wave 1: Domain + Routers (3 agents parallel)
| Agent | Scope | Files |
|-------|-------|-------|
| A1 | cadastros-ui | `api/v1/registry.py` (6 endpoints) + extender `domain_tenancy.py` |
| A2 | indicadores-etl | `api/v1/indicators.py` (3 endpoints) |
| A3 | eficiencia | `domain_eficiencia.py` + `api/v1/efficiency.py` (1 endpoint) |

### Wave 2: Tests (3 agents parallel)
| Agent | Scope |
|-------|-------|
| B1 | tests/test_registry.py |
| B2 | tests/test_indicators.py |
| B3 | tests/test_domain_eficiencia.py |

### Wave 3: Wiring + Gatekeepers
- Wire new routers into main.py + __init__.py
- production-validator + security-manager
