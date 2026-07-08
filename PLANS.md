# PLANS.md — Sprint 5-8 Core Critical Backend

> **Orquestrador:** Parreira  
> **Data:** 2026-07-07  
> **Baseline:** PROMPT_SPRINT_5_8.md  
> **Contratos:** docs/contracts/{pathways,ventilation,stability,deterioration}-openapi.yaml (1,127 linhas)  
> **Test baseline:** 265 domain tests pass (PYTHONPATH=src), migration head: 0031

---

## Task Envelope

| Campo | Valor |
|-------|-------|
| **Goal** | Implementar 4 domain services: trilhas-engine, ventilacao, estabilidade, piora-clinica |
| **Context** | IntensiCare backend: Python 3.12, FastAPI, SQLAlchemy async, PostgreSQL 16 + TimescaleDB. Contratos Niemeyer existentes. domain_respiratory.py (1,035L) e domain_hemo.py (931L) existem como base. |
| **Constraints** | OpenAPI contracts, audit trail, JWT auth, {items, total}, Alembic per model |
| **Done When** | 4 services + 4 API routers + models + migrations + tests pass + gatekeepers GO |
| **Risk Level** | L2 — novos endpoints + tabelas, migration conflicts em ondas paralelas |
| **Scope** | Apenas backend. NÃO: frontend, contratos (Niemeyer), domínios existentes (exceto expandir domain_respiratory.py) |

---

## Waves

### Wave 1: Models + Schemas (3 agents parallel)
| Agent | Scope | Files |
|-------|-------|-------|
| A1 | pathways model + schema | `models/pathway.py` + `schemas/pathways.py` |
| A2 | stability model + schema | `models/stability.py` + `schemas/stability.py` |
| A3 | deterioration model + schema | `models/deterioration.py` + `schemas/deterioration.py` |

### Wave 2: Domain Services (3 agents parallel)
| Agent | Scope | Files |
|-------|-------|-------|
| B1 | trilhas-engine domain service | `services/domain_trilhas_engine.py` |
| B2 | ventilacao domain service | `services/domain_ventilacao.py` (expande domain_respiratory.py) |
| B3 | estabilidade + piora-clinica | `services/domain_estabilidade.py` + `services/domain_piora_clinica.py` |

### Wave 3: API Routers (3 agents parallel)
| Agent | Scope | Files |
|-------|-------|-------|
| C1 | pathways router (6 endpoints) | `api/v1/pathways.py` |
| C2 | ventilation router (2 endpoints) | `api/v1/ventilation.py` |
| C3 | stability + deterioration (4 endpoints) + wiring | `api/v1/stability.py` + `api/v1/deterioration.py` + `main.py` + `__init__.py` |

### Wave 4: Migration + Tests (3 agents parallel)
| Agent | Scope | Files |
|-------|-------|-------|
| D1 | migration (pathways + stability + deterioration) | `alembic/versions/0032_*.py` |
| D2 | tests: pathways + ventilation | `tests/test_domain_trilhas_engine.py` + `tests/test_domain_ventilacao.py` |
| D3 | tests: stability + deterioration | `tests/test_domain_estabilidade.py` + `tests/test_domain_piora_clinica.py` |

### Wave 5: Verification + Gatekeepers
- Verify: PYTHONPATH=src python3 -m pytest new tests
- Gatekeeper: production-validator
- Gatekeeper: security-manager
- Wire schemas/__init__.py + models/__init__.py (if not done in Wave 3)

---

## Dependencies
```
Wave 1 (Models+Schemas) → Wave 2 (Services) → Wave 3 (API Routers) → Wave 4 (Migration+Tests) → Wave 5 (Gates)
```

## Rollback
- Each wave committed separately (`wave-N:` prefix)
- Revert: `git revert <commit>` per wave
- Migration rollback: `alembic downgrade -1`

## Notes
- ventilacao has NO model (per metrics table) — uses existing data from vital_sign/lab_result
- domain_ventilacao.py expands domain_respiratory.py (which already has FiO2 helpers, SpO2/FiO2 bands)
- domain_estabilidade.py wraps domain_hemo.py stability evaluators
- All API routers follow antimicrobial.py pattern: `router = APIRouter(prefix="/api/v1")`, `Depends(get_current_user)`, `{items, total}`
