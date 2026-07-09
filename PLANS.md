# PLANS.md — Trilhas Engine M2+M3+M4

> **Orquestrador:** Parreira | **Data:** 2026-07-09
> **Fontes:** PROMPT_TRILHAS_ENGINE.md + FORENSICS_FINAL_VERDICT_V2.md
> **Pré-requisito:** M1 completo (schema + CI gates + ventilacao.yaml)

## Envelope

| Campo | Valor |
|-------|-------|
| **Goal** | Migrar Trilhas Engine para rule engine declarativo (ADR-0020), M2+M3+M4 |
| **Risk** | L2 |
| **Constraints** | Sem breaking changes API, AST parser seguro (sem eval), CI gates PASS |
| **Scope** | trilhas_*.py, _work/alerts/pathways/*.yaml, pathways.py, domain_trilhas_engine.py |

## RECON Findings

- PATHWAY_SEEDS: 4 pathways (Ventilação, Sepse, Desmame, Nutrição) como list[dict]
- PathwayStore: state machine in-memory (791L) — será substituído
- 6 API endpoints em pathways.py — devem manter contrato
- ADR-0020 existe (20114 bytes)
- M1 artifacts: schema, validate_alerts.py, CI workflow, 20 testes

## Wave 1 — M2: Compiler + YAML (paralelo)

### Agent M2a: PredicateCompiler (3 arquivos)
| # | File | Action |
|---|------|--------|
| 1 | `trilhas_compiler.py` | CREATE — PredicateCompiler com AST parser seguro |
| 2 | `test_trilhas_compiler.py` | CREATE — testes do compilador |
| 3 | `trilhas_definitions.py` | MODIFY — catalog functions → YAML loader |

### Agent M2b: YAML Migration (3 arquivos)
| # | File | Action |
|---|------|--------|
| 1 | `_work/alerts/pathways/sepse.yaml` | CREATE — migrado de PATHWAY_SEEDS[1] |
| 2 | `_work/alerts/pathways/desmame.yaml` | CREATE — migrado de PATHWAY_SEEDS[2] |
| 3 | `_work/alerts/pathways/nutricao.yaml` | CREATE — migrado de PATHWAY_SEEDS[3] |

### Verificação Wave 1
```bash
python scripts/validate_alerts.py --gate A --defs _work/alerts/pathways/
python scripts/validate_alerts.py --gate B --defs _work/alerts/pathways/
pytest tests/test_trilhas_compiler.py -v
```

## Wave 2 — M3: Evaluator + Engine (depende de Wave 1)

### Agent M3: Evaluator + Engine (3-4 arquivos)
| # | File | Action |
|---|------|--------|
| 1 | `trilhas_evaluator.py` | CREATE — Stateless evaluator |
| 2 | `trilhas_engine.py` | CREATE — NOVO TrilhasEngine (substitui domain_trilhas_engine.py) |
| 3 | `test_trilhas_evaluator.py` | CREATE — testes do evaluator |

### Verificação Wave 2
```bash
python scripts/validate_alerts.py --gate C --defs _work/alerts/pathways/
pytest tests/test_trilhas_evaluator.py -v
```

## Wave 3 — M4: API Adapter + Cleanup (depende de Wave 2)

### Agent M4: Adapter + Cleanup (4-5 arquivos)
| # | File | Action |
|---|------|--------|
| 1 | `pathways.py` | MODIFY — adapter para novo engine |
| 2 | `trilhas_state.py` | MODIFY — isolar como deprecated |
| 3 | `domain_trilhas_engine.py` | MODIFY — thin wrapper |
| 4 | `test_domain_trilhas_engine.py` | MODIFY — atualizar contrato |
| 5 | `docs/adr/0020-trilhas-engine-architecture.md` | MODIFY — status "implemented" |

### Verificação Wave 3
```bash
pytest tests/test_domain_trilhas_engine.py -v
pytest tests/ -k "pathway" -v
```

## Gates Finais
- GATE-SEC: security scan
- GATE-PROD: production readiness
